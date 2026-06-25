"""Work mode — PLAN/BUILD switch. Writes work-mode.json for OpenCode."""

from datetime import datetime, timezone
from . import config
from .helpers import read_json, write_json, write_ok, write_info, write_fail

def switch_workmode(action: str):
    current = read_json(config.WORK_MODE_FILE, {}).get("mode", "build")
    if action == "status":
        print(f"\n  Mode: {current.upper()}")
        return
    if action == current:
        write_info(f"Already in {action.upper()}")
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    write_json(config.WORK_MODE_FILE, {"mode": action, "updated_at": now})
    write_ok(f"Work mode set to {action.upper()}")
