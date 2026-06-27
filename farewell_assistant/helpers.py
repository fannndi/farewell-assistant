"""Common helpers — JSON state, project registry, colored output."""

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config

_COLOR_MAP = {
    "green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m",
    "cyan": "\033[96m", "gray": "\033[90m", "magenta": "\033[95m",
    "blue": "\033[94m", "white": "\033[97m", "reset": "\033[0m",
}

def _supports_color():
    if os.environ.get("NO_COLOR"): return False
    if platform.system() == "Windows":
        return (os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM") == "mintty"
                or os.environ.get("ConEmuANSI") == "ON" or os.environ.get("ANSICON")
                or os.environ.get("VSCODE_PID"))
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_USE_COLOR = _supports_color()

def _c(text: str, color: str) -> str:
    return f"{_COLOR_MAP.get(color, '')}{text}{_COLOR_MAP['reset']}" if _USE_COLOR else text

def write_step(step: str, message: str): print(f"\n{_c(f'[{step}] {message}', 'cyan')}")
def write_ok(message: str): print(f"  {_c('[OK]', 'green')} {message}")
def write_skip(message: str): print(f"  {_c('[SKIP]', 'yellow')} {message}")
def write_fail(message: str): print(f"  {_c('[FAIL]', 'red')} {message}")
def write_info(message: str): print(f"  {_c('[..]', 'gray')} {message}")

def read_json(path: Path, default=None):
    if not path.exists(): return default
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return default

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

def get_work_mode() -> str:
    state = read_json(config.WORK_MODE_FILE, default={"mode": "build"})
    return state.get("mode", "build") if state else "build"

def get_project_path(project_name: str, registry_file=None) -> str:
    file_to_read = registry_file or config.REGISTRY_FILE
    reg = read_json(file_to_read)
    if reg and reg.get("projects", {}).get(project_name, {}).get("path"):
        return reg["projects"][project_name]["path"]
    return str(config.ROOT_DIR)

def read_project_active(registry_file=None) -> str:
    file_to_read = registry_file or config.REGISTRY_FILE
    reg = read_json(file_to_read)
    return reg["active"] if reg and reg.get("active") else "farewell-assistant"

def read_project_code(project_name: str, registry_file=None) -> str:
    file_to_read = registry_file or config.REGISTRY_FILE
    reg = read_json(file_to_read)
    if reg and reg.get("projects", {}).get(project_name, {}).get("project_code"):
        return reg["projects"][project_name]["project_code"]
    return "???"

def list_registered_projects() -> list[dict]:
    reg = read_json(config.REGISTRY_FILE)
    if not reg: return []
    active = reg.get("active", "")
    projects = []
    for name, info in reg.get("projects", {}).items():
        projects.append({
            "code": info.get("project_code", "???"), "name": name,
            "type": info.get("type", "?"), "dominan": info.get("dominan", ""),
            "active": name == active,
        })
    return sorted(projects, key=lambda p: p["code"])

def get_next_project_code() -> str:
    reg = read_json(config.REGISTRY_FILE) or {}
    codes = [int(p.get("project_code", 0)) for p in reg.get("projects", {}).values()]
    next_val = max(codes) + 1 if codes else 1
    return f"{next_val:03d}"

def register_project(name: str, project_type: str, path: str, dominan: str = "") -> str:
    reg = read_json(config.REGISTRY_FILE) or {"projects": {}, "active": "", "_next_code": "001"}
    lower = name.lower().replace(" ", "-")
    existing = reg.get("projects", {}).get(lower, {})
    code = existing.get("project_code") or get_next_project_code()
    if not project_type:
        from pathlib import Path
        p = Path(path)
        if not p.exists(): return "unknown"
        files = [f.name.lower() for f in p.iterdir() if f.is_file()]
        if "package.json" in files: project_type = "node"
        elif any(f in files for f in ["pyproject.toml", "requirements.txt", "setup.py"]): project_type = "python"
        elif "cargo.toml" in files: project_type = "rust"
        elif "go.mod" in files: project_type = "go"
        elif "pubspec.yaml" in files: project_type = "flutter"
        elif "composer.json" in files: project_type = "php"
        else: project_type = "unknown"
    if not dominan:
        dominan = project_type.upper()
    reg["projects"][lower] = {
        "project_code": code, "type": project_type,
        "last_used": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "context_file": f"{lower}.md", "path": path,
        "dominan": dominan, "is_local": False,
    }
    reg["active"] = lower
    write_json(config.REGISTRY_FILE, reg)
    return code
