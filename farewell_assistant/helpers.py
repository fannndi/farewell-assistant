"""Common helpers — JSON state, GPU, project registry, colored output."""

import json
import os
import platform
import re
import subprocess
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

def get_gpu_info(fields: str = "utilization.gpu,memory.used,memory.total") -> dict:
    try:
        gpu_raw = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        if gpu_raw.returncode != 0 or not gpu_raw.stdout.strip():
            return {"available": False, "utilization": 0, "memory_used": 0, "memory_total": 0}
        field_list = [f.strip() for f in fields.split(",")]
        parts = [p.strip() for p in gpu_raw.stdout.strip().split(",")]
        result = {"available": True}
        for field, value in zip(field_list, parts):
            if field == "name": result["name"] = value
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

class ApiKeyConfig:
    __slots__ = ("api_key", "router_password", "combo_entries", "combo_models")
    def __init__(self, api_key, router_password, combo_entries, combo_models):
        self.api_key = api_key; self.router_password = router_password
        self.combo_entries = combo_entries; self.combo_models = combo_models
    def __iter__(self):
        return iter((self.api_key, self.combo_entries, self.combo_models))

def parse_api_key() -> ApiKeyConfig:
    api_key = None; router_password = ""; combo_entries = {}; combo_models = {}
    try:
        for line in Path("api-key.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k, v = line.split("=", 1); k, v = k.strip(), v.strip()
            if k == "NINEROUTER_API_KEY": api_key = v
            elif k == "9ROUTER_PASSWORD": router_password = v
            elif k.startswith("COMBO_"): combo_entries.setdefault(k.replace("COMBO_", ""), {})["combo"] = v
            elif k.startswith("MODELS_"): combo_models.setdefault(k.replace("MODELS_", ""), {})["models"] = [m.strip() for m in v.split(",") if m.strip()]
    except Exception: pass
    return ApiKeyConfig(api_key, router_password, combo_entries, combo_models)

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

def log_session(project: str = "", work_mode: str = ""):
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not project: project = read_project_active()
    if not work_mode: work_mode = get_work_mode()
    entry = f"""## {now}\n- **Project:** {project}\n- **Work Mode:** {work_mode.upper()}\n- **Turn:** 0\n---\n"""
    try:
        with open(config.SESSION_LOG_FILE, "a", encoding="utf-8") as f: f.write(entry)
        write_ok("Session logged")
    except Exception as e: write_skip(f"Session log failed: {e}")


