"""Common helpers - JSON state, mode, Ollama, 9Router, GPU, LLM, token estimation."""

import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx

from . import config

# ---------------------------------------------------------------------------
# Write helpers (cross-platform colored output)
# ---------------------------------------------------------------------------

# ANSI colors for terminals that support it (Linux/macOS, modern Windows Terminal)
_COLOR_MAP = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "gray": "\033[90m",
    "magenta": "\033[95m",
    "blue": "\033[94m",
    "white": "\033[97m",
    "reset": "\033[0m",
}


def _supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if platform.system() == "Windows":
        return (
            os.environ.get("WT_SESSION")
            or os.environ.get("TERM_PROGRAM") == "mintty"
            or os.environ.get("ConEmuANSI") == "ON"
            or os.environ.get("ANSICON")
            or os.environ.get("VSCODE_PID")
        )
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_USE_COLOR = _supports_color()


def _c(text: str, color: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{_COLOR_MAP.get(color, '')}{text}{_COLOR_MAP['reset']}"


def write_step(step: str, message: str):
    print(f"\n{_c(f'[{step}] {message}', 'cyan')}")


def write_ok(message: str):
    print(f"  {_c('[OK]', 'green')} {message}")


def write_skip(message: str):
    print(f"  {_c('[SKIP]', 'yellow')} {message}")


def write_fail(message: str):
    print(f"  {_c('[FAIL]', 'red')} {message}")


def write_info(message: str):
    print(f"  {_c('[..]', 'gray')} {message}")


# ---------------------------------------------------------------------------
# JSON state helpers
# ---------------------------------------------------------------------------

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Mode helpers
# ---------------------------------------------------------------------------

def get_llm_mode() -> str:
    state = read_json(config.LLM_MODE_FILE, default={"mode": "eco"})
    return state.get("mode", "eco") if state else "eco"


def get_work_mode() -> str:
    state = read_json(config.WORK_MODE_FILE, default={"mode": "build"})
    return state.get("mode", "build") if state else "build"


def get_llm_model() -> str:
    state = read_json(config.LLM_MODE_FILE, default={"model": ""})
    return state.get("model", "") if state else ""


# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

def test_ollama_running() -> bool:
    try:
        r = httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def start_ollama_service() -> bool:
    if test_ollama_running():
        return True
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=(platform.system() == "Windows"),
        )
        time.sleep(3)
        return test_ollama_running()
    except Exception:
        return False


def stop_ollama_models():
    if not test_ollama_running():
        return
    try:
        r = httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        data = r.json()
        for m in data.get("models", []):
            name = m.get("name", "")
            if name:
                subprocess.run(["ollama", "stop", name], capture_output=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 9Router helpers
# ---------------------------------------------------------------------------

def get_9router_pid() -> int | None:
    try:
        if config.ROUTER_PID_FILE.exists():
            pid_val = int(config.ROUTER_PID_FILE.read_text(encoding="utf-8").strip())
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid_val}", "/NH"],
                    capture_output=True, text=True, timeout=5,
                )
                if "node.exe" in result.stdout:
                    return pid_val
            else:
                try:
                    os.kill(pid_val, 0)
                    return pid_val
                except OSError:
                    return None
    except Exception:
        pass
    return None


def stop_9router():
    stop_headroom()
    existing_pid = get_9router_pid()
    if existing_pid:
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/PID", str(existing_pid), "/F"], capture_output=True)
            else:
                os.kill(existing_pid, 15)  # SIGTERM
            time.sleep(1)
        except Exception:
            pass

    # Fallback: kill process on router port
    try:
        router_port = config.ROUTER_PORT
        if platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if f":{router_port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = int(parts[4])
                        try:
                            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
                        except Exception:
                            pass
        else:
            # lsof + kill
            result = subprocess.run(
                ["lsof", "-ti", f":{router_port}"],
                capture_output=True, text=True, timeout=5,
            )
            for pid_str in result.stdout.strip().split("\n"):
                if pid_str.strip():
                    try:
                        os.kill(int(pid_str.strip()), 15)
                    except Exception:
                        pass
        time.sleep(1)
    except Exception:
        pass

    if config.ROUTER_PID_FILE.exists():
        config.ROUTER_PID_FILE.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Headroom proxy (context compression for 9Router)
# ---------------------------------------------------------------------------

def stop_headroom():
    """Kill headroom proxy process."""
    pid_file = config.HEADROOM_PID_FILE
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            else:
                os.kill(pid, 15)
            time.sleep(1)
        except Exception:
            pass
        pid_file.unlink(missing_ok=True)

    # Fallback: kill by port
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if f":{config.HEADROOM_PORT}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
        else:
            result = subprocess.run(
                ["lsof", "-ti", f":{config.HEADROOM_PORT}"],
                capture_output=True, text=True, timeout=5,
            )
            for pid_str in result.stdout.strip().split("\n"):
                if pid_str.strip():
                    try:
                        os.kill(int(pid_str.strip()), 15)
                    except Exception:
                        pass
    except Exception:
        pass

    if config.HEADROOM_PID_FILE.exists():
        config.HEADROOM_PID_FILE.unlink(missing_ok=True)


def start_headroom() -> bool:
    """Start headroom proxy for context compression."""
    import shutil

    headroom_bin = shutil.which("headroom")
    if not headroom_bin:
        write_skip("Headroom not installed, skipping")
        return False

    stop_headroom()

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_out = config.LOG_DIR / "headroom.log"

    try:
        proc = subprocess.Popen(
            ["headroom", "proxy", "--port", config.HEADROOM_PORT],
            stdout=open(log_out, "w"),
            stderr=subprocess.STDOUT,
            shell=(platform.system() == "Windows"),
        )
        if proc.pid:
            config.HEADROOM_PID_FILE.write_text(str(proc.pid), encoding="utf-8")

        # Quick health check
        time.sleep(3)
        try:
            r = httpx.get(f"http://localhost:{config.HEADROOM_PORT}/health", timeout=3)
            if r.status_code == 200:
                write_ok(f"Headroom proxy started (port {config.HEADROOM_PORT}, PID: {proc.pid})")
                return True
        except Exception:
            pass
        write_skip("Headroom proxy started but not reachable")
        return False
    except Exception as e:
        write_skip(f"Headroom proxy failed to start: {e}")
        return False


def start_9router() -> bool:
    standalone_js = config.ROUTER_DIR / ".next" / "standalone" / "server.js"
    if not standalone_js.exists():
        write_fail("9Router standalone build missing. Run: python -m farewell_assistant.cli start")
        return False

    stop_9router()

    # Ensure static assets present
    standalone_next = config.ROUTER_DIR / ".next" / "standalone" / ".next" / "static"
    static_source = config.ROUTER_DIR / ".next" / "static"
    if not standalone_next.exists() and static_source.exists():
        import shutil
        shutil.copytree(str(static_source), str(standalone_next))

    # Logs dir
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_out = config.LOG_DIR / "9router.log"
    log_err = config.LOG_DIR / "9router-error.log"

    env = os.environ.copy()
    env["PORT"] = config.ROUTER_PORT
    env["NODE_ENV"] = "production"
    home = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME", ""))
    if platform.system() == "Windows":
        env["DATA_DIR"] = str(home / "AppData" / "Roaming" / "9router")
    else:
        env["DATA_DIR"] = str(home / ".config" / "9router")
    env["INITIAL_PASSWORD"] = os.environ.get("9ROUTER_PASSWORD", "")

    cmd = ["node", ".next/standalone/server.js"]
    with open(log_out, "w") as fout, open(log_err, "w") as ferr:
        proc = subprocess.Popen(
            cmd,
            cwd=str(config.ROUTER_DIR),
            env=env,
            stdout=fout,
            stderr=ferr,
            shell=(platform.system() == "Windows"),
        )

    if proc and proc.pid:
        config.ROUTER_PID_FILE.write_text(str(proc.pid), encoding="utf-8")

    # Health-check with backoff
    waits = [2, 3, 5, 8, 12, 15]
    total = 0
    for w in waits:
        time.sleep(w)
        total += w
        try:
            r = httpx.get(f"{config.API_URL}/api/health", timeout=10)
            if r.status_code == 200:
                write_ok(f"9Router started ({total}s, PID: {proc.pid})")
                # Start headroom proxy after 9Router is healthy
                start_headroom()
                return True
        except Exception:
            pass

    write_fail(f"9Router not reachable after {total}s (see {log_err})")
    return False


# ---------------------------------------------------------------------------
# API key parser (shared)
# ---------------------------------------------------------------------------

class ApiKeyConfig:
    """Parsed API key configuration."""
    __slots__ = ("api_key", "router_password", "combo_entries", "combo_models")

    def __init__(self, api_key: str | None, router_password: str, combo_entries: dict[str, dict], combo_models: dict[str, dict]):
        self.api_key = api_key
        self.router_password = router_password
        self.combo_entries = combo_entries
        self.combo_models = combo_models

    def __iter__(self):
        return iter((self.api_key, self.combo_entries, self.combo_models))


def parse_api_key() -> ApiKeyConfig:
    """Parse api-key.txt. Returns ApiKeyConfig with api_key, router_password, combo_entries, combo_models."""
    api_key = None
    router_password = ""
    combo_entries: dict[str, dict] = {}
    combo_models: dict[str, dict] = {}
    try:
        for line in config.API_KEY_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k == "NINEROUTER_API_KEY":
                api_key = v
            elif k == "9ROUTER_PASSWORD":
                router_password = v
            elif k.startswith("COMBO_"):
                idx = k.replace("COMBO_", "")
                combo_entries.setdefault(idx, {})["combo"] = v
            elif k.startswith("MODELS_"):
                idx = k.replace("MODELS_", "")
                combo_models.setdefault(idx, {})["models"] = [m.strip() for m in v.split(",") if m.strip()]
    except Exception as e:
        try:
            from .log import write_task_log
            write_task_log("PARSE_API_KEY", f"Parse error: {e}", "fail")
        except Exception:
            pass
    return ApiKeyConfig(api_key, router_password, combo_entries, combo_models)


# ---------------------------------------------------------------------------
# GPU helpers
# ---------------------------------------------------------------------------

def get_gpu_info(fields: str = "utilization.gpu,memory.used,memory.total") -> dict:
    try:
        gpu_raw = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if gpu_raw.returncode != 0 or not gpu_raw.stdout.strip():
            return {"available": False, "utilization": 0, "memory_used": 0, "memory_total": 0}

        # Parse by field order — nvidia-smi outputs values in same order as --query-gpu
        field_list = [f.strip() for f in fields.split(",")]
        parts = [p.strip() for p in gpu_raw.stdout.strip().split(",")]
        result = {"available": True}
        for field, value in zip(field_list, parts):
            if field == "name":
                result["name"] = value
            elif field == "memory.total":
                m = re.search(r"(\d+)", value)
                result["memory_total"] = int(m.group(1)) if m else 0
            elif field == "memory.used":
                m = re.search(r"(\d+)", value)
                result["memory_used"] = int(m.group(1)) if m else 0
            elif field == "temperature.gpu":
                m = re.search(r"(\d+)", value)
                result["temperature"] = int(m.group(1)) if m else 0
            elif field == "utilization.gpu":
                m = re.search(r"(\d+)", value)
                result["utilization"] = int(m.group(1)) if m else 0

        return result
    except Exception:
        return {"available": False, "utilization": 0, "memory_used": 0, "memory_total": 0}


# ---------------------------------------------------------------------------
# Token estimation (multi-language aware)
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    tokens = 0.0
    for ch in text:
        code = ord(ch)
        if (
            (0x4E00 <= code <= 0x9FFF)
            or (0x3040 <= code <= 0x309F)
            or (0x30A0 <= code <= 0x30FF)
            or (0xAC00 <= code <= 0xD7AF)
            or (0x3400 <= code <= 0x4DBF)
        ):
            tokens += 1
        elif code < 0x30 or (0x2000 <= code <= 0x206F):
            tokens += 0.5
        else:
            tokens += 0.25
    return max(1, int(tokens + 0.999))  # ceiling


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def invoke_llm(
    prompt: str,
    system: str = "You are a helpful assistant.",
    model: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout_sec: int = 60,
) -> dict | None:
    if not model:
        model = get_llm_model()
    if not model:
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": "5m",
        "think": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
            "num_gpu": 99,
        },
    }

    try:
        start = time.monotonic()
        r = httpx.post(
            f"{config.OLLAMA_URL}/api/chat",
            json=body,
            timeout=timeout_sec,
        )
        elapsed = time.monotonic() - start
        data = r.json()
        content = data.get("message", {}).get("content")
        if content:
            tokens = data.get("eval_count") or estimate_tokens(content)
            tps = round(tokens / elapsed, 2) if elapsed > 0 else 0
            return {
                "response": content,
                "tokens": tokens,
                "duration": elapsed,
                "tokens_per_second": tps,
            }
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Skill count
# ---------------------------------------------------------------------------

def get_skill_count(work_mode: str) -> int:
    count = 0
    idx = read_json(config.SKILL_IDX_FILE)
    if idx:
        mode_data = idx.get(work_mode, {})
        skills = mode_data.get("skills", {})
        if isinstance(skills, dict):
            for group in skills.values():
                if isinstance(group, list):
                    count += len(group)
    return count


# ---------------------------------------------------------------------------
# Session Log
# ---------------------------------------------------------------------------

def log_session(project: str = "", llm_mode: str = "", work_mode: str = ""):
    """Append daily session entry to session-log.md."""
    from datetime import datetime, timezone
    config.SESSION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not project:
        project = read_project_active()
    if not llm_mode:
        llm_mode = get_llm_mode()
    if not work_mode:
        work_mode = get_work_mode()

    entry = f"""## {now}

- **Project:** {project}
- **LLM Mode:** {llm_mode}
- **Work Mode:** {work_mode.upper()}
- **Turn:** 0
---
"""
    try:
        with open(config.SESSION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        write_ok("Session logged")
    except Exception as e:
        write_skip(f"Session log failed: {e}")


# ---------------------------------------------------------------------------
# Project Registry
# ---------------------------------------------------------------------------

def read_project_active() -> str:
    """Get active project name from registry."""
    reg = read_json(config.REGISTRY_FILE)
    if reg and reg.get("active"):
        return reg["active"]
    return "farewell-assistant"


def read_project_code(project_name: str) -> str:
    """Get project code by name."""
    reg = read_json(config.REGISTRY_FILE)
    if reg and reg.get("projects", {}).get(project_name, {}).get("project_code"):
        return reg["projects"][project_name]["project_code"]
    return "???"


def get_next_project_code() -> str:
    """Auto-increment project code (001, 002, ...)."""
    reg = read_json(config.REGISTRY_FILE)
    next_code = reg.get("_next_code", "001") if reg else "001"
    val = int(next_code) if next_code.isdigit() else 0
    code = f"{val:03d}"
    # Increment for next time
    if reg:
        reg["_next_code"] = f"{val + 1:03d}"
    return code


def register_project(name: str, project_type: str, path: str, dominan: str = ""):
    """Register project in registry with auto code."""
    code = get_next_project_code()
    reg = read_json(config.REGISTRY_FILE) or {"projects": {}, "active": "", "_next_code": "001"}

    # Detect type and dominan from path
    if not project_type:
        project_type = detect_type_from_path(path)
    if not dominan:
        dominan = project_type.upper()

    lower = name.lower().replace(" ", "-")
    reg["projects"][lower] = {
        "project_code": code,
        "type": project_type,
        "last_used": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "context_file": f"{lower}.md",
        "path": path,
        "dominan": dominan,
        "is_local": False,
    }
    reg["active"] = lower
    write_json(config.REGISTRY_FILE, reg)
    return code


def detect_type_from_path(path: str) -> str:
    """Simple project type detection from files in path."""
    import glob
    p = Path(path)
    if not p.exists():
        return "unknown"
    files = [f.name.lower() for f in p.iterdir() if f.is_file()]
    if "package.json" in files: return "node"
    if "pyproject.toml" in files or "requirements.txt" in files or "setup.py" in files: return "python"
    if "cargo.toml" in files: return "rust"
    if "pom.xml" in files or "build.gradle" in files or "build.gradle.kts" in files: return "java"
    if "go.mod" in files: return "go"
    if "pubspec.yaml" in files: return "flutter"
    if "composer.json" in files: return "php"
    if "*.csproj" in glob.glob(os.path.join(path, "*.csproj")): return "dotnet"
    return "unknown"


def detect_stack_from_path(path: str, max_depth: int = 2) -> list[str]:
    """Detect stack/frameworks from project files. Works in eco mode (no LLM)."""
    p = Path(path)
    if not p.exists():
        return []
    stack = []
    # Check root files
    try:
        for f in p.iterdir():
            if f.is_file():
                name = f.name.lower()
                if name == "pyproject.toml" or name == "requirements.txt":
                    stack.append("python")
                elif name == "package.json":
                    stack.append("node")
                elif name == "cargo.toml":
                    stack.append("rust")
                elif name == "go.mod":
                    stack.append("go")
                elif name == "pubspec.yaml":
                    stack.append("flutter")
                elif name == "composer.json":
                    stack.append("php")
                elif name == "pom.xml" or name == "build.gradle" or name == "build.gradle.kts":
                    stack.append("java")
                elif name == "sln" or name.endswith(".sln"):
                    stack.append("dotnet")
    except PermissionError:
        pass
    # Deep scan for framework detection (limited depth)
    if max_depth > 0:
        try:
            for f in p.rglob("*"):
                if f.is_file() and len(str(f)) < 200:
                    name = f.name.lower()
                    rel = str(f.relative_to(p)).lower()
                    # Python frameworks
                    if name == "manage.py" and "django" not in stack:
                        stack.append("django")
                    if name == "main.py" and "fastapi" not in stack:
                        # Check content for FastAPI/Flask
                        try:
                            content = f.read_text(encoding="utf-8", errors="ignore")[:500]
                            if "fastapi" in content.lower():
                                stack.append("fastapi")
                            elif "flask" in content.lower():
                                stack.append("flask")
                        except Exception:
                            pass
                    # Node frameworks
                    if "next.config" in name:
                        stack.append("nextjs")
                    if "nuxt.config" in name:
                        stack.append("nuxt")
                    if "angular.json" in name:
                        stack.append("angular")
                    if "vue.config" in name or "vite.config" in name:
                        stack.append("vue")
                    # Mobile
                    if "android" in rel and "app" in rel and name == "build.gradle.kts":
                        stack.append("android")
                    if "ios" in rel and name == "podfile":
                        stack.append("ios")
                    # Database
                    if name == "prisma" and rel.endswith("schema.prisma"):
                        stack.append("prisma")
                    if name == "docker-compose.yml" or name == "docker-compose.yaml":
                        stack.append("docker")
                    if name == "kubernetes.yml" or "k8s" in rel:
                        stack.append("kubernetes")
        except Exception:
            pass
    # Deduplicate
    seen = set()
    result = []
    for s in stack:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result


def validate_task_vs_project(intent: str, project_type: str, project_stack: list[str]) -> str | None:
    """Check if task intent matches project type. Returns warning or None."""
    if not project_stack:
        return None
    type_stack_set = set(project_stack)
    # Web/backend tasks on non-web projects
    web_tasks = {"build", "fix"}
    web_domains = {"node", "python", "django", "fastapi", "flask", "nextjs", "vue", "angular", "nuxt", "laravel", "php"}
    rust_tasks = {"build", "fix"}
    mobile_tasks = {"build", "fix"}
    # Check for mismatch
    if intent in web_tasks and not (type_stack_set & web_domains) and "unknown" not in type_stack_set:
        project_types = ", ".join(sorted(type_stack_set))
        return f"Warning: Task '{intent}' is web/backend oriented but project is {project_types}. Are you working in the right project?"
    if intent in rust_tasks and "rust" in type_stack_set:
        return None  # Rust project, rust task = ok
    if intent in mobile_tasks and "flutter" in type_stack_set:
        return None  # Flutter project, mobile task = ok
    return None


def clone_project(url: str, temp_dir: str | None = None) -> str | None:
    """Clone git repo to TEMP/, return project name or None."""
    import urllib.parse
    if not temp_dir:
        temp_dir = str(config.TEMP_DIR)
    name = os.path.basename(url)
    if name.endswith(".git"):
        name = name[:-4]
    dest = os.path.join(temp_dir, name)
    # Skip if already exists
    if os.path.exists(dest):
        write_skip(f"Already exists: {dest}")
        return name
    write_step("Clone", f"Cloning {url}...")
    result = subprocess.run(
        ["git", "clone", url, dest],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        write_fail(f"Clone failed: {result.stderr[:200]}")
        return None
    write_ok(f"Cloned to {dest}")
    return name


def setup_project_from_url(url: str) -> dict:
    """Clone + detect + register. Returns {name, code, error}."""
    name = clone_project(url)
    if not name:
        return {"error": "Clone failed"}
    dest = os.path.join(str(config.TEMP_DIR), name)
    project_type = detect_type_from_path(dest)
    code = register_project(name, project_type, dest)
    write_ok(f"{name} terdaftar dengan code project {code}")
    return {"name": name, "code": code}


def activate_project_by_code(code: str) -> bool:
    """Activate a registered project by its code."""
    reg = read_json(config.REGISTRY_FILE)
    if not reg:
        return False
    for proj_name, proj_data in reg.get("projects", {}).items():
        if proj_data.get("project_code") == code:
            reg["active"] = proj_name
            write_json(config.REGISTRY_FILE, reg)
            write_ok(f"Active project: {code}-{proj_name}")
            # Force pipeline refresh for new project context
            _refresh_project_context(proj_name)
            return True
    write_fail(f"Project code {code} tidak ditemukan")
    return False


def _refresh_project_context(project_name: str):
    """Update context.md to reflect active project."""
    from .intent_router import sync_turn_state
    result = {
        "success": True,
        "intent": {"intent": "ask", "domain": "general", "stack": [], "complexity": "low", "confidence": 0.6},
        "skill_chain": [],
        "model_route": {"primary": "Free", "secondary": "Free", "heavy": "Free"},
        "needs_planning": False,
        "work_mode": get_work_mode(),
        "profile": get_llm_mode(),
        "turn": 0,
        "blocked": [],
        "chain_summary": "",
        "task_warning": None,
    }
    try:
        sync_turn_state(result, "project switch")
    except Exception:
        pass


def list_registered_projects() -> list[dict]:
    """Return list of {code, name, type, active}."""
    reg = read_json(config.REGISTRY_FILE)
    if not reg:
        return []
    active = reg.get("active", "")
    projects = []
    for name, info in reg.get("projects", {}).items():
        projects.append({
            "code": info.get("project_code", "???"),
            "name": name,
            "type": info.get("type", "?"),
            "dominan": info.get("dominan", ""),
            "active": name == active,
        })
    return sorted(projects, key=lambda p: p["code"])
