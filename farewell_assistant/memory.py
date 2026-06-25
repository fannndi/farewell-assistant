"""Session memory — save/load per project. /save = checkpoint."""

from datetime import datetime, timezone
from pathlib import Path


def save_session(project_path: str, project_code: str, project_name: str, summary: str):
    mem_dir = Path(project_path) / ".farewell" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    p = mem_dir / f"{project_code}-{project_name}.md"
    header = f"# {project_code}-{project_name}\n\n" if not p.exists() else ""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(p, "a", encoding="utf-8") as f:
        if header:
            f.write(header)
        f.write(f"## {date}\n- {summary.strip()}\n")


def get_last_session(project_path: str, project_code: str, project_name: str) -> str:
    p = Path(project_path) / ".farewell" / "memory" / f"{project_code}-{project_name}.md"
    if not p.exists():
        return ""
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    for line in reversed(lines):
        if line.startswith("- ") or line.startswith("* "):
            return line[2:].strip()
    return ""
