"""CLI entrypoint — argparse-based command dispatcher."""

import argparse
import sys
from .intent_router import invoke_intent_router, show_intent_router_result
from .llm_setup import handle_llm_setup
from .workmode import switch_workmode


def cmd_route(args):
    context = args.context or ""
    result = invoke_intent_router(args.input, context, force=args.force)
    show_intent_router_result(result)
    return result


def cmd_workmode(args):
    switch_workmode(args.action)


def cmd_llm(args):
    handle_llm_setup(args.action)


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


def cmd_start_project(args):
    from .helpers import list_registered_projects, activate_project_by_code, read_json, write_json, _c
    from . import config

    if args.code == "list" or not args.code:
        projects = list_registered_projects()
        if not projects:
            print("  Tidak ada project terdaftar.")
            print("  Jalankan: py -m farewell_assistant.cli project <code> untuk register.")
            return
        print()
        print("  === Registered Projects ===")
        print()
        for p in projects:
            marker = " <- active" if p["active"] else ""
            print(f"  {p['code']} - {p['name']} ({p['type']}, {p['dominan']}){marker}")
        print()
        return

    # Activate by code
    code = args.code.strip()
    ok = activate_project_by_code(code)
    if not ok:
        return

    from .intent_router import _reset_turn_count, sync_turn_state
    from .helpers import get_work_mode, get_llm_model
    _reset_turn_count()

    reg = read_json(config.REGISTRY_FILE)
    active = reg.get("active", "?") if reg else "?"
    project_code = reg["projects"][active]["project_code"] if reg and reg.get("projects", {}).get(active) else ""
    work_mode = get_work_mode().upper()

    # Write pipeline-result.json + context.md (for plugin footer)
    result = {
        "success": True,
        "intent": {"intent": "ask", "domain": "general", "stack": [], "complexity": "low", "confidence": 0.6, "source": "quick"},
        "skill_chain": [],
        "model_route": {"primary": "Free", "secondary": "Free", "heavy": "Free"},
        "needs_planning": False,
        "work_mode": get_work_mode(),
        "profile": "on",
        "turn": 0,
        "blocked": [],
        "chain_summary": "",
        "task_warning": None,
    }
    sync_turn_state(result, "project switch")

    # Footer (matches plugin intent-router.js format)
    footer = f"Farewell: ON | Project: {project_code}-{active} | {work_mode} | Turn: 0 | Chain: - | 60% | LLM:{get_llm_model()}"
    print()
    print(f"  {_c('[ACTIVE]', 'green')} {project_code}-{active}")
    print(f"  {_c(footer, 'cyan')}")
    print()


def cmd_self_improvement(args):
    from .self_improvement import run_self_improvement
    run_self_improvement(full=getattr(args, 'full', False))


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

    sp_p = subparsers.add_parser("start-project", help="Switch project + prime pipeline (show footer)")
    sp_p.add_argument("code", nargs="?", default="list", help="Project code (001/002/003) or 'list'")
    sp_p.set_defaults(func=cmd_start_project)

    daily_p = subparsers.add_parser("daily", help="Daily report: pipeline prime + session log + system health")
    daily_p.set_defaults(func=cmd_daily)

    si_p = subparsers.add_parser("self-improvement", help="Git pull ECC + 9Router, cek dampak, update changelog")
    si_p.add_argument("--full", action="store_true", help="Run full audit (routing tests + red team + scorecard)")
    si_p.set_defaults(func=cmd_self_improvement)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
