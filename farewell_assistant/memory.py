"""Session memory — save/load per project. Centralized in .farewell/memory/."""

from datetime import datetime, timezone
from pathlib import Path

from . import config


def save_session(project_code: str, project_name: str, summary: str, team: str = ""):
    config.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    p = config.MEMORY_DIR / f"{project_code}-{project_name}.md"
    header = f"# {project_code}-{project_name}\n\n" if not p.exists() else ""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tag = f" [Team: {team}]" if team else ""
    with open(p, "a", encoding="utf-8") as f:
        if header:
            f.write(header)
        f.write(f"## {date}\n- {summary.strip()}{tag}\n")


def get_last_session(project_code: str, project_name: str) -> tuple[str, str]:
    p = config.MEMORY_DIR / f"{project_code}-{project_name}.md"
    if not p.exists():
        return ("", "")
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    for line in reversed(lines):
        if line.startswith("- ") or line.startswith("* "):
            text = line[2:].strip()
            team = ""
            if "[Team: " in text and text.endswith("]"):
                idx = text.index("[Team: ")
                team = text[idx + 7:-1]
                text = text[:idx].strip()
            return (text, team)
    return ("", "")
