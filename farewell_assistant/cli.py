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
    import json
    registry = config.REGISTRY_FILE
    if not registry.exists():
        print("  Registry not found: " + str(registry))
        return
    data = json.loads(registry.read_text(encoding="utf-8"))
    projects = data.get("projects", {})
    if args.action == "list":
        active = data.get("active", "")
        for name, info in projects.items():
            marker = " *" if name == active else ""
            print(f"  {name}{marker}  ({info.get('type', 'unknown')}, {info.get('dominan', '')})")
        print(f"\n  Active: {active}")
    elif args.action in projects:
        data["active"] = args.action
        registry.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Active project: {args.action}")
    else:
        print(f"  Unknown project '{args.action}'. Use 'project list' to see available.")


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

    # enrich-check
    ec_p = subparsers.add_parser("enrich-check", help="Verify enrichment pipeline")
    ec_p.add_argument("args", nargs="*", help="Optional test input text")
    ec_p.set_defaults(func=cmd_enrich_check)

    # project
    proj_p = subparsers.add_parser("project", help="Switch active project")
    proj_p.add_argument("action", nargs="?", default="list",
                        help="Project name or 'list'")
    proj_p.set_defaults(func=cmd_project)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
