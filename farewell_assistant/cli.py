"""CLI entrypoint — minimal dispatcher (daily/workmode/project/self-heal)."""

import argparse
from . import config
from .workmode import switch_workmode


def cmd_workmode(args):
    switch_workmode(args.action)


def cmd_llm(args):
    from .llm_setup import handle_llm_setup
    handle_llm_setup(args.action)


def cmd_self_heal(args):
    from .self_heal import run_self_heal
    run_self_heal(args.file, args.project)


def cmd_project(args):
    from .helpers import list_registered_projects, read_json, write_json
    from . import config
    if args.action == "list":
        projects = list_registered_projects()
        if not projects: print("  No registered projects.\n  Register via data/registry.json"); return
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
                from .helpers import _c
                print(f"\n  {_c('[ACTIVE]', 'green')} {args.action}-{name}\n")
                return
        print(f"  Project code '{args.action}' not found.")


def cmd_daily(args):
    from .daily import show_daily_report
    from .start import ensure_9router
    from .log import write_task_log
    ensure_9router()
    show_daily_report()
    write_task_log("DAILY", "Daily report generated", "success")


def _get_team() -> str:
    import json as _json
    try:
        f = config.FAREWELL_DIR / "team.json"
        if f.exists():
            return _json.loads(f.read_text(encoding="utf-8")).get("team", "OFF")
    except Exception: pass
    return "OFF"


def cmd_self_improvement(args):
    from .self_improvement import run_self_improvement
    run_self_improvement(full=getattr(args, 'full', False))


def cmd_team(args):
    import json as _json
    from .helpers import _c, get_work_mode, read_project_active
    if args.status == "on":
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "ON"}), encoding="utf-8")
        _write_context_footer(read_project_active(), get_work_mode(), _get_session_num())
        print(f"\n  {_c('[TEAM]', 'green')} ON - professional mode\n")
    elif args.status == "off":
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "OFF"}), encoding="utf-8")
        _write_context_footer(read_project_active(), get_work_mode(), _get_session_num())
        print(f"\n  {_c('[TEAM]', 'yellow')} OFF - personal mode\n")
    else:
        print(f"  Team: {_get_team()}")


def _get_session_num() -> int:
    import json as _json
    f = config.FAREWELL_DIR / "session-counter.json"
    if f.exists():
        try: return _json.loads(f.read_text(encoding="utf-8")).get("n", 0)
        except: pass
    return 0


def _inc_session() -> int:
    import json as _json
    f = config.FAREWELL_DIR / "session-counter.json"
    n = _get_session_num() + 1
    f.write_text(_json.dumps({"n": n}), encoding="utf-8")
    return n


def _write_context_footer(project: str, mode: str, session: int = 1):
    from .helpers import read_project_code
    from .tracker import get_today_usage
    from .memory import get_last_session
    from .indexer import get_project_skills
    code = read_project_code(project)
    team = _get_team()
    usage = get_today_usage()
    last, last_team = get_last_session(code, project)
    skills = get_project_skills(code, project)
    sk = f" | Skills: {len(skills)}" if skills else ""
    prev = f" (prev: {last_team})" if last_team and last_team != team else ""
    last_line = f"\nLast: {last}" if last else ""
    ctx = f"""# State
Team: {team}{prev}
Project: {code}-{project}
Session: #{session}
Mode: {mode.upper()}{sk}
Tokens: {usage['today']} today ({usage['total']} total){last_line}
"""
    (config.STATE_DIR / "context.md").write_text(ctx, encoding="utf-8")


def cmd_save(args):
    from .helpers import read_project_code, read_project_active, get_work_mode, _c
    from .memory import save_session
    active = read_project_active()
    code = read_project_code(active)
    team = _get_team()
    summary = args.summary.strip() if args.summary else ""
    if not summary:
        print(f"\n  {_c('[SKIP]', 'yellow')} Empty summary - nothing saved.\n")
        return
    save_session(code, active, summary, team)
    print(f"\n  {_c('[SAVED]', 'green')} {code}-{active}: {summary[:60]}...\n")
    _write_context_footer(active, get_work_mode(), _get_session_num())


def cmd_start_project(args):
    from .helpers import list_registered_projects, read_json, write_json, _c, read_project_code, get_work_mode
    from . import config

    if args.code == "list" or not args.code:
        projects = list_registered_projects()
        if not projects: print("  No registered projects."); return
        print(); print("  === Projects ===")
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print(); return

    reg = read_json(config.REGISTRY_FILE)
    if not reg: print("  No registry found."); return

    for name, info in reg.get("projects", {}).items():
        if info.get("project_code") == args.code:
            reg["active"] = name
            write_json(config.REGISTRY_FILE, reg)

            mode = get_work_mode().upper()
            _write_context_footer(name, mode)

            code = read_project_code(name)
            from .indexer import get_project_skills
            from .memory import get_last_session
            team = _get_team()
            skills = get_project_skills(code, name)
            _, prev_team = get_last_session(code, name)
            sess = _inc_session()
            sk = f" | Skills: {len(skills)}" if skills else ""
            prev = f" (prev: {prev_team})" if prev_team and prev_team != team else ""
            print(f"\n  {_c('[ACTIVE]', 'green')} {code}-{name}")
            print(f"  {_c(f'Farewell: ON | {code}-{name} | {mode} | Session: #{sess} | Team: {team}{prev}{sk}', 'cyan')}\n")
            _write_context_footer(name, mode, sess)
            return
    print(f"  Project code '{args.code}' not found.")


def cmd_setup_project(args):
    from .helpers import register_project, _c
    from .indexer import index_project
    from pathlib import Path

    path = Path(args.path)
    if not path.is_dir():
        print(f"  Path not found: {args.path}")
        return

    name = args.name or path.name
    code = register_project(name, "", str(path))

    result = index_project(str(path), code, name, stack=args.stack)

    sk = f" | Skills: {result.get('total', 0)}" if result else ""
    print(f"\n  {_c('[REGISTERED]', 'green')} {code}-{name} ({path.name}){sk}")
    print(f"  Active: {code}-{name}\n")


def main():
    parser = argparse.ArgumentParser(prog="farewell-assistant", description="Lightweight 9Router orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    wm_p = subparsers.add_parser("workmode", help="Switch or show work mode (plan/build)")
    wm_p.add_argument("action", nargs="?", default="status", choices=["plan", "build", "status"])
    wm_p.set_defaults(func=cmd_workmode)

    llm_p = subparsers.add_parser("llm", help="Show LLM/GPU status")
    llm_p.add_argument("action", nargs="?", default="status", choices=["status", "list"])
    llm_p.set_defaults(func=cmd_llm)

    sh_p = subparsers.add_parser("self-heal", help="Post-edit typecheck hook")
    sh_p.add_argument("--file", required=True, help="Edited file path")
    sh_p.add_argument("--project", default="", help="Project root path")
    sh_p.set_defaults(func=cmd_self_heal)

    proj_p = subparsers.add_parser("project", help="List or switch active project")
    proj_p.add_argument("action", nargs="?", default="list", help="Project code or 'list'")
    proj_p.set_defaults(func=cmd_project)

    daily_p = subparsers.add_parser("daily", help="Daily: 9Router health + system status")
    daily_p.set_defaults(func=cmd_daily)

    save_p = subparsers.add_parser("save", help="Save session summary to memory")
    save_p.add_argument("summary", help="Session summary text")
    save_p.set_defaults(func=cmd_save)

    si_p = subparsers.add_parser("self-improvement", help="Git pull ECC + 9Router")
    si_p.add_argument("--full", action="store_true", help="Run full audit")
    si_p.set_defaults(func=cmd_self_improvement)

    team_p = subparsers.add_parser("team", help="Set team mode: on / off / status")
    team_p.add_argument("status", nargs="?", default="status", choices=["on", "off", "status"])
    team_p.set_defaults(func=cmd_team)

    sp_p = subparsers.add_parser("start-project", help="Switch active project + show footer")
    sp_p.add_argument("code", nargs="?", default="list", help="Project code (001/002/003) or 'list'")
    sp_p.set_defaults(func=cmd_start_project)

    setup_p = subparsers.add_parser("setup-project", help="Register project from path + index skills")
    setup_p.add_argument("path", help="Path to project directory")
    setup_p.add_argument("--name", default="", help="Project name (default: dirname)")
    setup_p.add_argument("--stack", nargs="*", default=None, help="Force stack (e.g. python flutter react)")
    setup_p.add_argument("--reindex", action="store_true", help="Force re-index even if already indexed")
    setup_p.set_defaults(func=cmd_setup_project)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
