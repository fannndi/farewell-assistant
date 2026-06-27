"""Common helpers — JSON state, project registry, colored output."""

import json
import os
import platform
import sys
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

