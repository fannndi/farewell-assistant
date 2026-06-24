"""Startup orchestrator — pipeline prime + health check."""

import time

from . import config
from .helpers import write_ok, write_skip, write_step
from .intent_router import invoke_intent_router
from .log import sync_session_state, write_task_log


def run_start() -> bool:
    """Startup sequence. Returns True if pipeline primed."""
    start = time.monotonic()

    print()
    print("  =================================================")
    print("  farewell-assistant - Start")
    print("  =================================================")
    print()

    # Pipeline prime
    write_step("1/2", "Pipeline Prime")
    _prime_pipeline()

    # Health check
    write_step("2/2", "Health Check")
    _run_self_heal_check(project_root=config.ROOT_DIR)

    # Sync & log
    sync_session_state()
    duration = round(time.monotonic() - start, 1)
    write_task_log("START", f"Boot completed ({duration}s)", "success")
    write_step("Ready", f"Ready ({duration}s)")
    return True


def _prime_pipeline():
    """Prime the intent pipeline with 'session start'."""
    try:
        result = invoke_intent_router("session start", force=True)
        if result.get("success"):
            i = result.get("intent", {})
            write_ok(
                "Pipeline primed: "
                + i.get("intent", "?") + "/"
                + i.get("domain", "?") + "/"
                + i.get("complexity", "?")
            )
        else:
            write_ok("Pipeline primed (startup)")
    except Exception as e:
        write_skip("Pipeline skip: " + str(e))


def _run_self_heal_check(project_root):
    """Scan recently modified .py files for type errors."""
    try:
        py_files = [f for f in project_root.rglob("*.py")
                    if "ecc" not in str(f) and "9router" not in str(f)
                    and ".venv" not in str(f) and ".git" not in str(f)
                    and "__pycache__" not in str(f)]
        if not py_files:
            return
        from .self_heal import self_heal
        for f in py_files[:5]:
            issues = self_heal(str(f), str(project_root))
            if issues:
                write_skip(f"  self_heal({f.name}): {len(issues)} issue(s)")
    except Exception:
        pass
