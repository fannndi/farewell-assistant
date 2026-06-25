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

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
