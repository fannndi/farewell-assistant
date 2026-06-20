"""Structured task logging to logging.md + session state sync."""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config


def write_task_log(stage: str, action: str, result: str = "success", files: str = ""):
    """Append structured log entry to logging.md."""
    try:
        log_file = config.LOG_FILE
        if not log_file.exists():
            log_file.write_text("# Logging\n", encoding="utf-8")

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        files_part = f" | FILES: {files}" if files else ""
        entry = f"[{ts}] STAGE: {stage} | ACTION: {action} | RESULT: {result}{files_part}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sync_session_state():
    """Write session-state.json + initial context.md."""
    try:
        from .helpers import get_llm_mode, get_work_mode, get_skill_count

        mode = get_llm_mode()
        work = get_work_mode()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

        # Read registry for active project
        active = "farewell-assistant"
        kategori = "AUTOMATION"
        reg = _read_json(config.REGISTRY_FILE)
        if reg and reg.get("active"):
            active = reg["active"]
            if reg.get("projects", {}).get(active, {}).get("kategori"):
                kat_vals = set()
                for v in reg["projects"][active]["kategori"].values():
                    kat_vals.add(v)
                kategori = " - ".join(sorted(kat_vals))

        skill_count = get_skill_count(work)

        # Write session-state.json
        state = {
            "session": {
                "project": active,
                "mode": mode,
                "work": work.upper(),
                "kategori": kategori,
                "started": now,
                "last_save": now,
            },
            "metrics": {
                "tokens_input": 0,
                "tokens_output": 0,
                "sessions_count": 1,
            },
        }
        _write_json(config.STATE_DIR / "session-state.json", state)

        # context.md is managed by sync_turn_state (intent_router.py)
        # Only write initial context.md if it doesn't exist
        context_path = config.STATE_DIR / "context.md"
        if not context_path.exists():
            ctx = f"""# Session State

- **Project:** {active}
- **Kategori:** {kategori}
- **Mode:** {mode}
- **Work:** {work.upper()}
- **Started:** {now}
"""
            context_path.write_text(ctx, encoding="utf-8")
    except Exception:
        pass
