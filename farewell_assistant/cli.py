"""CLI entrypoint — minimal dispatcher (workmode/team/status/start/project/upstream/daily)."""

import argparse
from . import config
from .workmode import switch_workmode


def cmd_workmode(args):
    switch_workmode(args.action)


def _get_team() -> str:
    import json as _json
    try:
        f = config.FAREWELL_DIR / "team.json"
        if f.exists():
            return _json.loads(f.read_text(encoding="utf-8")).get("team", "OFF")
    except Exception: pass
    return "OFF"


def cmd_team(args):
    import json as _json
    from .helpers import _c, get_work_mode, read_project_active
    from .indexer import get_project_skills
    if args.status == "on":
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "ON"}), encoding="utf-8")
        _write_context_footer()
        print(f"\n  {_c('[TEAM]', 'green')} ON - professional mode\n")
    elif args.status == "off":
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "OFF"}), encoding="utf-8")
        _write_context_footer()
        print(f"\n  {_c('[TEAM]', 'yellow')} OFF - personal mode\n")
    else:
        print(f"  Team: {_get_team()}")


def cmd_upstream(args):
    from .upstream import run_upstream
    run_upstream()


def cmd_daily(args):
    from .daily import run_daily
    run_daily()


def cmd_sync(args):
    from .sync_opencode import sync_opencode
    sync_opencode()


def cmd_project(args):
    from .helpers import list_registered_projects, read_json, write_json, _c
    if args.action == "list":
        projects = list_registered_projects()
        if not projects: print("  No registered projects."); return
        print(); print("  === Registered Projects ===")
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print()
    else:
        reg = read_json(config.REGISTRY_FILE)
        if not reg: return
        for name, info in reg.get("projects", {}).items():
            if info.get("project_code") == args.action:
                reg["active"] = name
                write_json(config.REGISTRY_FILE, reg)
                _write_context_footer()
                print(f"\n  {_c('[ACTIVE]', 'green')} {args.action}-{name}\n")
                return
        print(f"  Project code '{args.action}' not found.")


def cmd_status(args):
    from .helpers import read_project_active, get_work_mode, _c, read_project_code
    from .indexer import get_project_skills
    active = read_project_active()
    mode = get_work_mode()
    code = read_project_code(active)
    team = _get_team()
    skills = get_project_skills(code, active)
    sk = f" | Skills: {len(skills)}" if skills else ""
    print(f"\n  {_c(f'Farewell: ON | {code}-{active} | {mode.upper()}{sk} | Team: {team}', 'cyan')}\n")


def cmd_start(args):
    from .start import ensure_9router
    ensure_9router()


def _write_context_footer(project: str | None = None, mode: str | None = None):
    from .helpers import read_project_code, read_project_active, get_work_mode
    from .indexer import get_project_skills
    if project is None:
        project = read_project_active()
    if mode is None:
        mode = get_work_mode()
    code = read_project_code(project)
    team = _get_team()
    skills = get_project_skills(code, project)
    sk = f" | Skills: {len(skills)}" if skills else ""
    ctx = f"""# State
Farewell: ON
Team: {team}
Project: {code}-{project}
Mode: {mode.upper()}{sk}
"""
    (config.STATE_DIR / "context.md").write_text(ctx, encoding="utf-8")


def main():
    _write_context_footer()
    parser = argparse.ArgumentParser(prog="farewell-assistant", description="Lightweight 9Router orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    wm_p = subparsers.add_parser("workmode", help="Switch work mode (plan/build)")
    wm_p.add_argument("action", nargs="?", default="status", choices=["plan", "build", "status"])
    wm_p.set_defaults(func=cmd_workmode)

    team_p = subparsers.add_parser("team", help="Set team mode: on / off / status")
    team_p.add_argument("status", nargs="?", default="status", choices=["on", "off", "status"])
    team_p.set_defaults(func=cmd_team)

    status_p = subparsers.add_parser("status", help="Show current state")
    status_p.set_defaults(func=cmd_status)

    start_p = subparsers.add_parser("start", help="Start 9Router if not running")
    start_p.set_defaults(func=cmd_start)

    proj_p = subparsers.add_parser("project", help="List or switch active project")
    proj_p.add_argument("action", nargs="?", default="list", help="Project code or 'list'")
    proj_p.set_defaults(func=cmd_project)

    up_p = subparsers.add_parser("upstream", help="Git pull ECC + 9Router")
    up_p.set_defaults(func=cmd_upstream)

    daily_p = subparsers.add_parser("daily", help="Daily readiness: 9Router health + ECC/GitHub updates + combo model ping")
    daily_p.set_defaults(func=cmd_daily)

    sync_p = subparsers.add_parser("sync", help="Sync 9Router combos + Nvidia to opencode.jsonc")
    sync_p.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
