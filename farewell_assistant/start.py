"""Startup orchestrator — pipeline prime + daily report."""

import os
import time
from pathlib import Path

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
    write_step("1/3", "Pipeline Prime")
    _prime_pipeline()
    write_step("2/3", "9Router Health")
    _ensure_9router()
    write_step("3/3", "Health Check")
    _run_self_heal_check(project_root=config.ROOT_DIR)
    sync_session_state()
    duration = round(time.monotonic() - start, 1)
    write_task_log("START", f"Boot completed ({duration}s)", "success")
    write_step("Ready", f"Ready ({duration}s)")
    return True


def run_daily() -> bool:
    """Daily session start: pipeline prime + 9router + git pull + comprehensive report."""
    from .daily import show_daily_report, save_session_memory, git_pull_self, get_last_commits
    from .intent_router import _reset_turn_count

    _reset_turn_count()

    # Pipeline prime
    _prime_pipeline()

    # 9Router health check + start if needed
    _ensure_9router()

    # Git pull self
    changes = git_pull_self()
    if changes:
        write_ok(f"Git pull: {len(changes)} change(s)")

    # Log session
    try:
        from .helpers import log_session
        log_session()
    except Exception:
        pass

    # Save memory for next daily
    commits = get_last_commits(3)
    save_session_memory(0, commits, [])

    # Show report
    show_daily_report()

    return True


def _prime_pipeline():
    """Prime the intent pipeline with 'session start'."""
    try:
        result = invoke_intent_router("session start", force=True)
        if result.get("success"):
            i = result.get("intent", {})
            write_ok(f"Pipeline primed: {i.get('intent', '?')}/{i.get('domain', '?')}/{i.get('complexity', '?')}")
        else:
            write_ok("Pipeline primed (startup)")
    except Exception as e:
        write_skip("Pipeline skip: " + str(e))


def _ensure_9router():
    """Check if 9Router is running on port 20128; start if not."""
    import socket
    import subprocess

    # Check via socket (fast)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()

    if result == 0:
        write_ok("9Router is running (port 20128)")
        return

    # Not running — try to start
    write_skip("9Router not running — starting...")
    router_dir = config.ROUTER_DIR
    standalone = router_dir / ".next" / "standalone"

    try:
        # Read DATA_DIR from .env file, fallback to default
        env_file = router_dir / ".env"
        data_dir = str(Path(os.environ.get("APPDATA", "")) / "9router")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DATA_DIR="):
                    data_dir = line.split("=", 1)[1].strip()
                    break

        env = {
            "PORT": "20128",
            "NODE_ENV": "production",
            "DATA_DIR": data_dir,
        }
        if standalone.exists():
            node_cmd = ["node", str(standalone / "server.js")]
        else:
            node_cmd = ["npx", "next", "start", "-p", "20128"]

        proc = subprocess.Popen(
            node_cmd,
            cwd=str(router_dir),
            env={**os.environ, **env},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait up to 30s for port to open
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            time.sleep(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                if s.connect_ex(("127.0.0.1", 20128)) == 0:
                    write_ok(f"9Router started (PID: {proc.pid})")
                    # Save PID
                    pid_file = config.ROOT_DIR / ".opencode" / "9router.pid"
                    pid_file.parent.mkdir(parents=True, exist_ok=True)
                    pid_file.write_text(str(proc.pid))
                    s.close()
                    return
            finally:
                s.close()

        write_skip("9Router start timed out (30s) — check logs")
    except Exception as e:
        write_skip(f"9Router start failed: {e}")


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
