"""Local Agent — offline execution loop using local GGUF model + subprocess.

Usage:
    py -m farewell_assistant.local_agent [task_file]
    
Reads .opencode/offline/task.json, executes steps, writes result.json.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Ensure we can import from package
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from farewell_assistant import config
from farewell_assistant.helpers import read_json, write_json, get_gpu_info


# ---------------------------------------------------------------------------
# Step executors
# ---------------------------------------------------------------------------

def _cmd_read_file(params: dict) -> dict:
    path = _resolve_path(params["path"])
    if not path.exists():
        return {"ok": False, "error": f"File not found: {params['path']}"}
    lines = params.get("lines")
    content = path.read_text(encoding="utf-8")
    if lines:
        parts = lines.split("-")
        try:
            start = int(parts[0]) - 1
            end = int(parts[1]) if len(parts) > 1 else start + 1
            lines_arr = content.splitlines(keepends=True)
            content = "".join(lines_arr[start:end])
        except (ValueError, IndexError):
            pass
    return {"ok": True, "content": content, "path": str(path), "size": len(content)}


def _cmd_write_file(params: dict) -> dict:
    path = _resolve_path(params["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(params["content"], encoding="utf-8")
    return {"ok": True, "path": str(path), "size": len(params["content"])}


def _cmd_edit_file(params: dict) -> dict:
    path = _resolve_path(params["path"])
    if not path.exists():
        return {"ok": False, "error": f"File not found: {params['path']}"}
    content = path.read_text(encoding="utf-8")
    old = params["old"]
    new = params.get("new", "")
    count = params.get("count", 1)
    if count == -1:
        new_content = content.replace(old, new)
    else:
        new_content = content.replace(old, new, count)
    if content == new_content:
        return {"ok": False, "error": f"old_string not found: {old[:50]}..."}
    path.write_text(new_content, encoding="utf-8")
    return {"ok": True, "path": str(path), "diff_size": len(new_content) - len(content)}


def _cmd_batch_edit(params: dict) -> dict:
    path = _resolve_path(params["path"])
    if not path.exists():
        return {"ok": False, "error": f"File not found: {params['path']}"}
    content = path.read_text(encoding="utf-8")
    changes = params["edits"]
    applied = 0
    for edit in changes:
        if edit["old"] in content:
            content = content.replace(edit["old"], edit.get("new", ""), 1)
            applied += 1
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": str(path), "applied": applied, "total": len(changes)}


def _cmd_run_command(params: dict) -> dict:
    cmd = params["cmd"]
    timeout = params.get("timeout", 30)
    try:
        start = time.monotonic()
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, shell=True,
        )
        elapsed = time.monotonic() - start
        return {
            "ok": r.returncode == 0,
            "returncode": r.returncode,
            "stdout": r.stdout[:2000],
            "stderr": r.stderr[:1000],
            "duration": round(elapsed, 2),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _cmd_search_code(params: dict) -> dict:
    pattern = params["pattern"]
    path = _resolve_path(params.get("path", "."))
    include = params.get("include", "*.py")
    try:
        r = subprocess.run(
            ["rg", "-n", pattern, "--include", include, str(path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            lines = [l for l in r.stdout.splitlines() if l.strip()]
            return {"ok": True, "matches": len(lines), "results": lines[:50]}
        return {"ok": True, "matches": 0, "results": []}
    except Exception:
        # fallback: Python grep
        matches = []
        for f in Path(path).rglob(include):
            if f.is_file():
                try:
                    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                        if re.search(pattern, line):
                            matches.append(f"{f}:{i}: {line.strip()[:120]}")
                except Exception:
                    pass
        return {"ok": True, "matches": len(matches), "results": matches[:50]}


def _cmd_ask_llm(params: dict) -> dict:
    """Ask the local LLM for code generation / analysis."""
    from farewell_assistant.models import invoke_llm
    prompt = params["prompt"]
    system = params.get("system", "You are a coding assistant.")
    max_tokens = params.get("max_tokens", 512)
    t0 = time.time()
    result = invoke_llm(prompt=prompt, system=system, max_tokens=max_tokens, temperature=0.2)
    elapsed = time.time() - t0
    if result:
        return {"ok": True, "response": result["response"], "tokens": result["tokens"], "duration": elapsed}
    return {"ok": False, "error": "LLM returned no response"}


_STEP_HANDLERS = {
    "read_file": _cmd_read_file,
    "write_file": _cmd_write_file,
    "edit_file": _cmd_edit_file,
    "batch_edit": _cmd_batch_edit,
    "run_command": _cmd_run_command,
    "search_code": _cmd_search_code,
    "ask_llm": _cmd_ask_llm,
}


# ---------------------------------------------------------------------------
# Path resolution — prevent escape from project
# ---------------------------------------------------------------------------

def _resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = ROOT / p
    # Safety: ensure within project
    try:
        p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        # Allow common system paths needed for commands
        if not any(str(p).startswith(str(ROOT)) for ROOT in [ROOT, Path("/tmp"), Path(os.environ.get("TEMP", "/tmp"))]):
            raise PermissionError(f"Path outside project: {p}")
    return p


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_local_agent(task_path: str | None = None) -> dict:
    """Execute offline task file. Returns result dict."""
    task_file = Path(task_path) if task_path else config.OFFLINE_TASK_FILE
    if not task_file.exists():
        return {"ok": False, "error": f"Task file not found: {task_file}"}

    task = read_json(task_file)
    if not task or "steps" not in task:
        return {"ok": False, "error": "Invalid task format: no steps"}

    # Write initial state
    tasks_dir = task_file.parent
    tasks_dir.mkdir(parents=True, exist_ok=True)
    state = {"status": "running", "current_step": 0, "total_steps": len(task["steps"])}
    write_json(config.OFFLINE_STATE_FILE, state)

    results = []
    failed = False

    for i, step in enumerate(task["steps"]):
        step_type = step.get("type", "")
        handler = _STEP_HANDLERS.get(step_type)

        # Snapshot GPU before
        gpu_before = get_gpu_info("name,utilization.gpu,memory.used,memory.total")

        if not handler:
            results.append({
                "step_id": step.get("id", i),
                "type": step_type,
                "ok": False,
                "error": f"Unknown step type: {step_type}",
            })
            failed = True
            break

        step_start = time.monotonic()
        try:
            step_result = handler(step.get("params", {}))
        except Exception as e:
            step_result = {"ok": False, "error": str(e)}

        step_time = time.monotonic() - step_start

        # Snapshot GPU after
        gpu_after = get_gpu_info("name,utilization.gpu,memory.used,memory.total")

        result_entry = {
            "step_id": step.get("id", i),
            "type": step_type,
            "params": step.get("params", {}),
            "ok": step_result["ok"],
            "result": step_result,
            "duration": round(step_time, 2),
            "gpu_before": gpu_before,
            "gpu_after": gpu_after,
        }
        results.append(result_entry)

        # Update state
        state["current_step"] = i + 1
        state["last_step"] = step.get("id", i)
        state["last_status"] = "ok" if step_result["ok"] else "fail"
        write_json(config.OFFLINE_STATE_FILE, state)

        if not step_result["ok"]:
            failed = True
            break

    # Capture final GPU
    gpu_final = get_gpu_info("name,utilization.gpu,memory.used,memory.total")

    final = {
        "ok": not failed,
        "plan": task.get("plan", ""),
        "total_steps": len(task["steps"]),
        "completed": len(results),
        "failed": failed,
        "results": results,
        "gpu": gpu_final,
        "total_duration": round(sum(r["duration"] for r in results), 2),
    }

    write_json(config.OFFLINE_RESULT_FILE, final)
    state["status"] = "completed" if not failed else "failed"
    write_json(config.OFFLINE_STATE_FILE, state)

    return final


def main():
    task_path = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_local_agent(task_path)
    if result["ok"]:
        print(f"[OK] {result['completed']}/{result['total_steps']} steps completed in {result['total_duration']}s")
    else:
        failed = [r for r in result.get("results", []) if not r["ok"]]
        for f in failed:
            print(f"[FAIL] Step {f['step_id']} ({f['type']}): {f['result'].get('error', 'unknown')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
