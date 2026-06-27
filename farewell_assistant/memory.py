"""Per-project session memory — save/load last context."""

import json
from datetime import datetime
from pathlib import Path
from . import config


MEMORY_DIR = config.FAREWELL_DIR / "memory"


def _mem_path(project_code: str, project_name: str) -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return MEMORY_DIR / f"{project_code}-{project_name}.json"


def save_session(project_code: str, project_name: str, summary: str, files: list[str] | None = None, user_msgs: int = 1):
    path = _mem_path(project_code, project_name)
    data = {"project_code": project_code, "project_name": project_name,
            "last_summary": summary, "files_touched": files or [],
            "user_messages": user_msgs, "updated_at": datetime.now().isoformat()}
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_session(project_code: str, project_name: str) -> dict:
    path = _mem_path(project_code, project_name)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_recent_context(project_code: str, project_name: str) -> str:
    mem = load_session(project_code, project_name)
    if not mem:
        return ""
    summary = mem.get("last_summary", "")
    files = mem.get("files_touched", [])
    msgs = mem.get("user_messages", 0)
    parts = []
    if summary:
        parts.append(f"Previous session: {summary}")
    if files:
        parts.append(f"Files worked on: {', '.join(files[:5])}")
    parts.append(f"Session had {msgs} user message(s)")
    return " | ".join(parts) if parts else ""
