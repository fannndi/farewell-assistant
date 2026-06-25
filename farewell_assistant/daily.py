"""Daily report — 9Router health + project status."""

import socket
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from . import config
from .helpers import _c, get_gpu_info, read_project_active, list_registered_projects


def show_daily_report():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    active_project = read_project_active(config.REGISTRY_FILE)
    projects = list_registered_projects()
    import json as _json

    combo = "9Router"
    try:
        oc = _json.loads((config.ROOT_DIR / "opencode.jsonc").read_text(encoding="utf-8"))
        m = oc.get("model", "")
        if m.startswith("9router/"): combo = m.split("/", 1)[1]
    except Exception:
        pass

    # 9Router health
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    router_up = sock.connect_ex(("127.0.0.1", 20128)) == 0
    sock.close()

    # GPU
    gpu = get_gpu_info("name,memory.total,memory.used,temperature.gpu")
    gpu_str = f"{gpu.get('name', 'N/A')} ({gpu.get('temperature', '?')}C, {gpu.get('memory_used', 0)}/{gpu.get('memory_total', 0)}MB)" if gpu.get("available") else "N/A"

    # Git status
    git_status = "up to date"
    try:
        r = subprocess.run(["git", "rev-list", "--count", "HEAD..@{u}"], cwd=str(config.ROOT_DIR),
                          capture_output=True, text=True, timeout=10)
        behind = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0
        if behind > 0: git_status = f"{behind} commit(s) behind"
    except Exception:
        git_status = "check failed"

    sep = "=" * 50
    print(f"\n  {_c(sep, 'cyan')}")
    print(f"  {_c('Daily Report', 'cyan')} - {now}")
    print(f"  {_c(sep, 'cyan')}")

    router_icon = _c("[RUNNING]", "green") if router_up else _c("[STOPPED]", "red")
    print(f"\n  9Router  : {router_icon} (port 20128)")
    print(f"  Combo    : {_c(combo, 'cyan')} (instructor)")
    print(f"  GPU      : {_c('[OK]', 'green') if gpu.get('available') else _c('[N/A]', 'yellow')} {gpu_str}")
    print(f"  Git      : {_c('[OK]', 'green') if git_status == 'up to date' else _c('[OUTDATED]', 'yellow')} {git_status}")
    print(f"  Project  : {active_project} ({len(projects)} registered)")

    print(f"\n  {_c(sep, 'gray')}\n")
