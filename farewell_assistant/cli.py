"""CLI entrypoint — minimal dispatcher (daily/workmode/project/self-heal)."""

import argparse
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


def cmd_hermes(args):
    from .hermes import main as hermes_main
    hermes_main(args.action)


def _write_context_footer(project: str, mode: str):
    from .helpers import read_project_code, read_json
    from . import config
    from datetime import datetime, timezone
    code = read_project_code(project)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    ctx = f"""# Session
- Project: {code}-{project}
- Mode: {mode.upper()}
- Started: {now}

# Footer
Farewell: ON | {code}-{project} | {mode.upper()} | 9Router
"""
    (config.STATE_DIR / "context.md").write_text(ctx, encoding="utf-8")


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
            print(f"\n  {_c('[ACTIVE]', 'green')} {code}-{name}")
            print(f"  {_c(f'Farewell: ON | {code}-{name} | {mode}', 'cyan')}\n")
            return
    print(f"  Project code '{args.code}' not found.")


def cmd_setup_project(args):
    from .helpers import register_project, _c
    from pathlib import Path

    path = Path(args.path)
    if not path.is_dir():
        print(f"  Path not found: {args.path}")
        return

    name = args.name or path.name
    code = register_project(name, "", str(path))
    print(f"\n  {_c('[REGISTERED]', 'green')} {code}-{name} ({path.name})")
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

    hermes_p = subparsers.add_parser("hermes", help="Hermes Agent: install/config/launch/status")
    hermes_p.add_argument("action", nargs="?", default="status",
                          choices=["install", "config", "launch", "status"])
    hermes_p.set_defaults(func=cmd_hermes)

    sp_p = subparsers.add_parser("start-project", help="Switch active project + show footer")
    sp_p.add_argument("code", nargs="?", default="list", help="Project code (001/002/003) or 'list'")
    sp_p.set_defaults(func=cmd_start_project)

    setup_p = subparsers.add_parser("setup-project", help="Register existing project from path")
    setup_p.add_argument("path", help="Path to project directory")
    setup_p.add_argument("--name", default="", help="Project name (default: dirname)")
    setup_p.set_defaults(func=cmd_setup_project)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
