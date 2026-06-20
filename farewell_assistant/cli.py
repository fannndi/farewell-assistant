"""CLI entrypoint - argparse-based command dispatcher."""

import argparse
import sys

from . import config
from .detect_project import detect_project
from .helpers import get_llm_mode
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
    result = detect_project(args.path, emit_context=args.context)
    return result


def cmd_start(args):
    run_start()


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
    det_p.set_defaults(func=cmd_detect)

    # start
    start_p = subparsers.add_parser("start", help="Run startup sequence")
    start_p.set_defaults(func=cmd_start)

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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
