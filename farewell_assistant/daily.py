"""Daily report — 9Router health + project status."""

import socket
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from . import config
from .helpers import _c, get_gpu_info, read_project_active, list_registered_projects
from .tracker import get_today_usage


def show_daily_report():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    active_project = read_project_active(config.REGISTRY_FILE)
    projects = list_registered_projects()
    import json as _json
    team = "OFF"
    try:
        oc = _json.loads((config.ROOT_DIR / "opencode.jsonc").read_text(encoding="utf-8"))
        m = oc.get("model", "")
        if "GO-Flash" in m or "Deepseek" in m: team = "ON"
    except Exception: pass

    skill_count = 0
    from .helpers import get_project_path
    p_path = get_project_path(active_project)
    manifest = Path(p_path) / ".farewell" / "manifest.json"
    if manifest.exists():
        try: skill_count = len(_json.loads(manifest.read_text(encoding="utf-8")).get("skills", []))
        except: pass

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

    usage = get_today_usage()
    router_icon = _c("[RUNNING]", "green") if router_up else _c("[STOPPED]", "red")
    print(f"\n  9Router  : {router_icon} (port 20128)")
    team_icon = _c("ON", "green") if team == "ON" else _c("OFF", "yellow")
    sk = f" | Skills: {skill_count}" if skill_count else ""
    print(f"  Team     : {team_icon}{sk}")
    print(f"  Tokens   : {_c('today', 'cyan')}={usage['today']} (in={usage['today_input']} out={usage['today_output']}) | {_c('total', 'gray')}={usage['total']}")
    print(f"  GPU      : {_c('[OK]', 'green') if gpu.get('available') else _c('[N/A]', 'yellow')} {gpu_str}")
    print(f"  Git      : {_c('[OK]', 'green') if git_status == 'up to date' else _c('[OUTDATED]', 'yellow')} {git_status}")
    print(f"  Project  : {active_project} ({len(projects)} registered)")

    print(f"\n  {_c(sep, 'gray')}\n")
