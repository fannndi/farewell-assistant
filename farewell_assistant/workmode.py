"""Work mode — PLAN/BUILD switch. Writes work-mode.json + syncs default_agent in opencode.jsonc."""

import re
from datetime import datetime, timezone
from . import config
from .helpers import read_json, write_json, write_ok, write_info, write_fail


OC_FILE = config.ROOT_DIR / "opencode.jsonc"


def _switch_default_agent(target: str) -> bool:
    """Change default_agent in opencode.jsonc preserving JSONC comments."""
    if not OC_FILE.exists():
        return False
    try:
        content = OC_FILE.read_text(encoding="utf-8")
        new_content = re.sub(
            r'("default_agent"\s*:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{target}"',
            content,
        )
        if new_content == content:
            return False
        tmp = OC_FILE.with_suffix(".jsonc.tmp")
        tmp.write_text(new_content, encoding="utf-8")
        tmp.replace(OC_FILE)
        return True
    except Exception:
        return False


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

    target = "plan-mode" if action == "plan" else "build"
    synced = _switch_default_agent(target)

    if synced:
        write_ok(f"Work mode set to {action.upper()} (agent: {target})")
    else:
        write_fail(f"Work mode set to {action.upper()} but default_agent sync FAILED — check opencode.jsonc")
