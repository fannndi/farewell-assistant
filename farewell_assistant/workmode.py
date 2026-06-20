"""Work mode management - Switch between plan/build modes."""

from datetime import datetime, timezone

from . import config
from .helpers import read_json, write_json, write_step, write_ok, write_info, get_work_mode
from .log import write_task_log, sync_session_state

MODE_DEFS = {
    "plan": {
        "label": "PLAN",
        "icon": "[P]",
        "tools_allowed": ["read", "bash"],
        "tools_blocked": ["write", "edit"],
        "groups": ["audit", "research", "explore", "planning"],
    },
    "build": {
        "label": "BUILD",
        "icon": "[B]",
        "tools_allowed": ["write", "edit", "bash", "read"],
        "tools_blocked": [],
        "groups": ["orchestration", "tdd_testing", "coding", "security", "deployment", "agent_eng"],
    },
}


def show_mode_info(mode: str):
    """Display mode details + skill groups."""
    idx = read_json(config.SKILL_IDX_FILE)
    if not idx:
        print("  skill-mode-index.json not found")
        return

    defn = MODE_DEFS.get(mode, MODE_DEFS["build"])
    mode_data = idx.get(mode, {})

    print()
    write_step("MODE", f"{defn['icon']} {defn['label']}")
    write_info(f"Description: {mode_data.get('description', '')}")
    write_info(f"Tools allowed: {', '.join(defn['tools_allowed'])}")
    if defn["tools_blocked"]:
        write_info(f"Tools blocked: {', '.join(defn['tools_blocked'])}")
    else:
        write_info("Tools blocked: none")

    print()
    write_step("SKILLS", "Groups loaded")
    total = 0
    groups = mode_data.get("skills", {})
    for group in defn["groups"]:
        skills = groups.get(group, [])
        count = len(skills) if isinstance(skills, list) else 0
        total += count
        write_ok(f"{group} - {count} skills")
        for s in (skills if isinstance(skills, list) else []):
            write_info(f"  {s}")

    print()
    write_step("TOTAL", f"{total} skills loaded")


def switch_workmode(action: str):
    """Switch or show work mode."""
    current = get_work_mode()

    if action == "status":
        write_step("STATUS", "Current work mode")
        write_ok(f"Mode: {current.upper()}")
        show_mode_info(current)
        return

    if action == current:
        write_info(f"Already in {action.upper()} mode. No change.")
        show_mode_info(action)
        return

    write_step("SWITCH", f"Changing {current.upper()} -> {action.upper()}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    state = {"mode": action, "updated_at": now}
    write_json(config.WORK_MODE_FILE, state)
    write_ok(f"Work mode set to {action.upper()}")
    show_mode_info(action)
    try:
        sync_session_state()
    except Exception:
        pass
    write_task_log("WORKMODE", f"Switch to {action.upper()}", "success")
