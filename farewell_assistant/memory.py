"""Session memory — save/load per project. /save = checkpoint."""

from datetime import datetime, timezone
from pathlib import Path

from . import config


def _file(project_code: str, project_name: str) -> Path:
    config.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    return config.MEMORY_DIR / f"{project_code}-{project_name}.md"


def save_session(project_code: str, project_name: str, summary: str):
    p = _file(project_code, project_name)
    header = f"# {project_code}-{project_name}\n\n" if not p.exists() else ""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(p, "a", encoding="utf-8") as f:
        if header:
            f.write(header)
        f.write(f"## {date}\n- {summary.strip()}\n")
    return True


def get_last_session(project_code: str, project_name: str) -> str:
    p = _file(project_code, project_name)
    if not p.exists():
        return ""
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    for line in reversed(lines):
        if line.startswith("- ") or line.startswith("* "):
            return line[2:].strip()
    return ""
