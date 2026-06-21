"""CLI entrypoint - argparse-based command dispatcher."""

import argparse
import sys

from . import config
from .detect_project import detect_project
from .intent_router import invoke_intent_router, show_intent_router_result
from .llm_setup import handle_llm_setup
from .start import run_start
from .workmode import switch_workmode


def cmd_route(args):
    context = args.context or ""
    result = invoke_intent_router(args.input, context, force=args.force)
    show_intent_router_result(result)
    return result


def cmd_workmode(args):
    switch_workmode(args.action)


def cmd_llm(args):
    handle_llm_setup(args.action, args.profile)


def cmd_detect(args):
    emit = args.context or args.register
    result = detect_project(args.path, emit_context=emit)
    return result


def cmd_start(args):
    run_start()


def cmd_daily(args):
    from .start import run_daily
    run_daily()


def cmd_autostart(args):
    from .autostart import enable_autostart, disable_autostart, show_status
    if args.action == "enable":
        enable_autostart()
    elif args.action == "disable":
        disable_autostart()
    else:
        show_status()


def cmd_self_heal(args):
    from .self_heal import run_self_heal
    run_self_heal(args.file, args.project)


def cmd_enrich_check(args):
    input_text = " ".join(args.args) if args.args else "apa itu closure"
    force = not input_text.startswith("_")
    result = invoke_intent_router(input_text, force=force)
    show_intent_router_result(result)


def cmd_project(args):
    from .helpers import list_registered_projects, activate_project_by_code
    if args.action == "list":
        projects = list_registered_projects()
        if not projects:
            print("  Tidak ada project terdaftar.")
            return
        print()
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print()
    else:
        # Try as code (001, 002, etc.)
        activate_project_by_code(args.action)


def cmd_setup_project(args):
    from .helpers import setup_project_from_url
    setup_project_from_url(args.url)


def cmd_start_project(args):
    from .helpers import list_registered_projects, activate_project_by_code
    if args.action:
        activate_project_by_code(args.action)
    else:
        projects = list_registered_projects()
        if not projects:
            print("  Tidak ada project terdaftar.")
            return
        print()
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print()
        print("  Pilih project: /start-project <code>")
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="farewell-assistant",
        description="Intent-Driven AI assistant orchestrator",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # route
    route_p = subparsers.add_parser("route", help="Run intent router on text input")
    route_p.add_argument("input", help="User input text to route")
    route_p.add_argument("--context", default="", help="Project context")
    route_p.add_argument("--force", action="store_true", help="Force enrichment")
    route_p.set_defaults(func=cmd_route)

    # workmode
    wm_p = subparsers.add_parser("workmode", help="Switch or show work mode")
    wm_p.add_argument("action", nargs="?", default="status",
                      choices=["plan", "build", "status"],
                      help="plan | build | status")
    wm_p.set_defaults(func=cmd_workmode)

    # llm
    llm_p = subparsers.add_parser("llm", help="LLM management")
    llm_p.add_argument("action", nargs="?", default="status",
                       choices=["eco", "on", "hot", "balance", "performance",
                                "list", "pull", "status", "remove", "auto"],
                       help="eco | on | hot | balance | performance | list | pull | status | remove | auto")
    llm_p.add_argument("--profile", default="", help="Profile name for pull action")
    llm_p.set_defaults(func=cmd_llm)

    # detect
    det_p = subparsers.add_parser("detect", help="Detect project type")
    det_p.add_argument("path", nargs="?", default="", help="Path to project directory")
    det_p.add_argument("--context", action="store_true", help="Emit context template")
    det_p.add_argument("--register", action="store_true", help="Register in registry and set active")
    det_p.set_defaults(func=cmd_detect)

    # start
    start_p = subparsers.add_parser("start", help="Run full startup sequence (legacy)")
    start_p.set_defaults(func=cmd_start)

    # daily (new: daily session start + log)
    daily_p = subparsers.add_parser("daily", help="Daily session start + log to session-log.md")
    daily_p.set_defaults(func=cmd_daily)

    # autostart
    as_p = subparsers.add_parser("autostart", help="Manage autostart (schtasks/systemd)")
    as_p.add_argument("action", nargs="?", default="status",
                      choices=["enable", "disable", "status"])
    as_p.set_defaults(func=cmd_autostart)

    # self-heal
    sh_p = subparsers.add_parser("self-heal", help="Post-edit typecheck hook")
    sh_p.add_argument("--file", required=True, help="Edited file path")
    sh_p.add_argument("--project", default="", help="Project root path")
    sh_p.set_defaults(func=cmd_self_heal)

    # enrich-check
    ec_p = subparsers.add_parser("enrich-check", help="Verify enrichment pipeline")
    ec_p.add_argument("args", nargs="*", help="Optional test input text")
    ec_p.set_defaults(func=cmd_enrich_check)

    # project
    proj_p = subparsers.add_parser("project", help="Switch active project")
    proj_p.add_argument("action", nargs="?", default="list",
                        help="Project code (001, 002, etc.) or 'list'")
    proj_p.set_defaults(func=cmd_project)

    # setup-project (clone + register)
    setup_p = subparsers.add_parser("setup-project", help="Clone project to TEMP/ and register")
    setup_p.add_argument("url", help="Git clone URL")
    setup_p.set_defaults(func=cmd_setup_project)

    # start-project (list + select)
    start_proj_p = subparsers.add_parser("start-project", help="List projects and activate one")
    start_proj_p.add_argument("action", nargs="?", default="",
                              help="Project code to activate (001, 002, etc.)")
    start_proj_p.set_defaults(func=cmd_start_project)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
