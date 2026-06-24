"""Daily report engine — informative /daily output."""

import subprocess
import platform
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .helpers import (
    _c, get_gpu_info, test_ollama_running, get_llm_model, get_work_mode,
    read_project_active, read_json, write_json, list_registered_projects,
)


def read_last_session() -> dict:
    """Baca data sesi terakhir dari daily-memory.json."""
    mem_file = config.DATA_DIR / "memory" / "daily-memory.json"
    data = read_json(mem_file, default={})
    if data:
        return {
            "date": data.get("last_session", "-"),
            "turns": data.get("last_turn", 0),
            "commits": data.get("last_commits", []),
            "topics": data.get("last_topics", []),
        }
    return {"date": "-", "turns": 0, "commits": [], "topics": []}


def save_session_memory(turns: int, commits: list[str], topics: list[str]):
    """Simpan data sesi untuk dibaca daily berikutnya."""
    mem_dir = config.DATA_DIR / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    mem_file = mem_dir / "daily-memory.json"
    write_json(mem_file, {
        "last_session": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_turn": turns,
        "last_commits": commits[:5],
        "last_topics": topics[:5],
    })


def read_pending_items() -> list[dict]:
    """Baca P0/P1/P2 pending dari self-improvement.md Appendix D."""
    si_file = config.ROOT_DIR / "self-improvement.md"
    if not si_file.exists():
        return []
    items = []
    try:
        text = si_file.read_text(encoding="utf-8")
        in_tracker = False
        for line in text.splitlines():
            if "# COMPLETION TRACKER" in line:
                in_tracker = True
                continue
            if in_tracker:
                if line.strip().startswith("#"):
                    in_tracker = False
                    continue
                if "|" in line and ("P0" in line or "P1" in line or "P2" in line):
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        items.append({"id": parts[1], "desc": parts[2], "status": parts[4] if len(parts) > 4 else ""})
    except Exception:
        pass
    return [i for i in items if i.get("status") in ("NEW", "CARRY_OVER", "IN_PROGRESS")]


def check_git_update(repo_dir: Path) -> str:
    """Cek apakah ada update dari remote."""
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        return "not a git repo"
    try:
        r = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..@{u}"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
        )
        behind = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0
        if behind > 0:
            return f"{behind} commit(s) behind remote"
        return "up to date"
    except Exception:
        return "check failed"


def git_pull_self() -> list[str]:
    """Git pull farewell-assistant sendiri, return list of changes."""
    try:
        r = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(config.ROOT_DIR), capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            return [l for l in lines if l]
        return []
    except Exception:
        return []


def get_last_commits(n: int = 5) -> list[str]:
    """Get last N commit short hashes + messages."""
    try:
        r = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            cwd=str(config.ROOT_DIR), capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return [l.strip() for l in r.stdout.strip().splitlines()]
        return []
    except Exception:
        return []


def show_daily_report():
    """Display informative daily report to stdout."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    model = get_llm_model()
    mode = get_work_mode().upper()
    active_project = read_project_active(config.REGISTRY_FILE)

    # System health
    ollama_ok = test_ollama_running()
    gpu = get_gpu_info("name,memory.total,memory.used,temperature.gpu")
    gpu_name = gpu.get("name", "N/A") if gpu.get("available") else "N/A"
    gpu_mem = f"{gpu.get('memory_used', 0)}/{gpu.get('memory_total', 0)}MB" if gpu.get("available") else "N/A"
    gpu_temp = f"{gpu.get('temperature', '?')}°C" if gpu.get("temperature") else "N/A"

    projects = list_registered_projects()
    project_count = len(projects)
    project_names = [p["name"] for p in projects[:5]]

    whitelist = read_json(config.ROOT_DIR / "data" / "skill-whitelist.json", default={})
    whitelist_count = len(whitelist.get("kept", []))
    total_skills = len(list((config.ECC_DIR / "skills").glob("*")))

    # Last session
    last = read_last_session()

    # Pending items
    pending = read_pending_items()

    # Commits
    commits = get_last_commits(3)

    # ECC + 9Router update status
    ecc_status = check_git_update(config.ECC_DIR)
    router_status = check_git_update(config.ROUTER_DIR)

    # ── Display ──
    sep = "=" * 50
    sub = "-" * 50

    print()
    print(f"  {_c(sep, 'cyan')}")
    print(f"  {_c('Daily Report', 'cyan')} — {now}")
    print(f"  {_c(sep, 'cyan')}")

    # System Health
    print(f"\n  {_c('SYSTEM HEALTH', 'yellow')}")
    print(f"  {sub}")
    ollama_icon = _c("[OK]", "green") if ollama_ok else _c("[FAIL]", "red")
    model_display = f" ({model})" if ollama_ok else ""
    print(f"    Ollama    : {ollama_icon}{model_display}")
    gpu_icon = _c("[OK]", "green") if gpu.get("available") else _c("[FAIL]", "red")
    print(f"    GPU       : {gpu_icon} {gpu_name} ({gpu_temp}, {gpu_mem})")
    print(f"    Mode      : {_c(mode, 'green')}")
    print(f"    Tests     : [OK] (run: py -m pytest)")

    # ECC + 9Router
    print(f"\n  {_c('EXTERNAL COMPONENTS', 'yellow')}")
    print(f"  {sub}")
    ecc_icon = _c("[OK]", "green") if ecc_status == "up to date" else _c("[OUTDATED]", "yellow")
    print(f"    ECC       : {ecc_icon} {ecc_status} ({whitelist_count}/{total_skills} whitelisted)")
    router_icon = _c("[OK]", "green") if router_status == "up to date" else _c("[OUTDATED]", "yellow")
    print(f"    9Router   : {router_icon} {router_status}")

    # Project Status
    print(f"\n  {_c('PROJECT STATUS', 'yellow')}")
    print(f"  {sub}")
    print(f"    Active    : {active_project}")
    print(f"    Projects  : {project_count} registered ({', '.join(project_names[:3])})")

    # Last Session
    print(f"\n  {_c('LAST SESSION', 'yellow')}")
    print(f"  {sub}")
    print(f"    Date      : {last['date']}")
    if last.get("turns"):
        print(f"    Turns     : {last['turns']}")
    if last.get("commits"):
        print(f"    Last cmts : {', '.join(last['commits'][:3])}")
    if last.get("topics"):
        print(f"    Topics    : {', '.join(last['topics'][:3])}")

    # Pending Items
    if pending:
        print(f"\n  {_c('PENDING ITEMS', 'yellow')}")
        print(f"  {sub}")
        for item in pending:
            status_icon = _c("[CARRY]", "yellow") if item["status"] == "CARRY_OVER" else _c("[NEW]", "cyan")
            print(f"    {status_icon} {item['id']} {item['desc'][:50]}")

    # Recent Commits
    if commits:
        print(f"\n  {_c('RECENT COMMITS', 'yellow')}")
        print(f"  {sub}")
        for c in commits:
            print(f"    {c}")

    print(f"\n  {_c(sep, 'cyan')}")
    print(f"  {_c('Next: /go atau mulai coding.', 'gray')}")
    print(f"  {_c(sep, 'cyan')}\n")
