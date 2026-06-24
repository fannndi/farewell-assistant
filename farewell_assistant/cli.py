"""CLI entrypoint — argparse-based command dispatcher."""

import argparse
import sys
from .intent_router import invoke_intent_router, show_intent_router_result
from .llm_setup import handle_llm_setup
from .workmode import switch_workmode
from .helpers import write_ok, write_skip, write_step
from .models import set_llm_mode, get_active_model_info


def cmd_route(args):
    context = args.context or ""
    result = invoke_intent_router(args.input, context, force=args.force)
    show_intent_router_result(result)
    return result


def cmd_workmode(args):
    switch_workmode(args.action)


def cmd_llm(args):
    handle_llm_setup(args.action, args.profile)


def cmd_offline(args):
    if args.action == "on":
        set_llm_mode("offline")
        info = get_active_model_info()
        write_step("OFFLINE", "Offline mode ON")
        write_ok(f"Model: {info['model_name']} ({info['description']})")
        write_ok("Cloud AI akan mendelegasikan eksekusi ke local LLM")
    elif args.action == "off":
        set_llm_mode("online")
        info = get_active_model_info()
        write_step("OFFLINE", "Offline mode OFF")
        write_ok(f"Model: {info['model_name']} ({info['description']})")
        write_ok("Cloud AI akan mengeksekusi langsung")
    else:
        info = get_active_model_info()
        mode = "ON" if info["label"] == "Offline" else "OFF"
        write_step("OFFLINE", f"Status: {mode}")
        write_ok(f"Model lokal: {info['model_name']} ({info['gguf_file']})")
        write_ok(f"Role: {info['description']}")
        from .health import check_llm
        write_ok("GGUF tersedia" if check_llm() else "GGUF tidak ditemukan")


def cmd_self_heal(args):
    from .self_heal import run_self_heal
    run_self_heal(args.file, args.project)


def cmd_enrich_check(args):
    input_text = " ".join(args.args) if args.args else "apa itu closure"
    result = invoke_intent_router(input_text, force=not input_text.startswith("_"))
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
        activate_project_by_code(args.action)


def cmd_daily(args):
    from .start import run_daily
    run_daily()


def cmd_self_improvement(args):
    from .self_improvement import run_self_improvement
    run_self_improvement()


def main():
    parser = argparse.ArgumentParser(prog="farewell-assistant", description="Intent-Driven AI assistant orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    route_p = subparsers.add_parser("route", help="Run intent router on text input")
    route_p.add_argument("input", help="User input text to route")
    route_p.add_argument("--context", default="", help="Project context")
    route_p.add_argument("--force", action="store_true", help="Force enrichment")
    route_p.set_defaults(func=cmd_route)

    wm_p = subparsers.add_parser("workmode", help="Switch or show work mode")
    wm_p.add_argument("action", nargs="?", default="status", choices=["plan", "build", "status"])
    wm_p.set_defaults(func=cmd_workmode)

    llm_p = subparsers.add_parser("llm", help="LLM management")
    llm_p.add_argument("action", nargs="?", default="status",
                       choices=["status", "list", "pull", "download", "remove"])
    llm_p.set_defaults(func=cmd_llm)

    off_p = subparsers.add_parser("offline", help="Offline mode: delegate execution to local LLM")
    off_p.add_argument("action", nargs="?", default="status", choices=["on", "off", "status"])
    off_p.set_defaults(func=cmd_offline)

    sh_p = subparsers.add_parser("self-heal", help="Post-edit typecheck hook")
    sh_p.add_argument("--file", required=True, help="Edited file path")
    sh_p.add_argument("--project", default="", help="Project root path")
    sh_p.set_defaults(func=cmd_self_heal)

    ec_p = subparsers.add_parser("enrich-check", help="Verify enrichment pipeline")
    ec_p.add_argument("args", nargs="*", help="Optional test input text")
    ec_p.set_defaults(func=cmd_enrich_check)

    proj_p = subparsers.add_parser("project", help="Switch active project")
    proj_p.add_argument("action", nargs="?", default="list", help="Project code or 'list'")
    proj_p.set_defaults(func=cmd_project)

    daily_p = subparsers.add_parser("daily", help="Daily report: pipeline prime + session log + system health")
    daily_p.set_defaults(func=cmd_daily)

    si_p = subparsers.add_parser("self-improvement", help="Git pull ECC + 9Router, cek dampak, update changelog")
    si_p.set_defaults(func=cmd_self_improvement)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
