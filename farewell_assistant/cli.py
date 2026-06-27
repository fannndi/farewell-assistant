"""CLI entrypoint — minimal dispatcher (workmode/team/status/project/daily/cool)."""

import argparse, json as _json
from . import config
from .workmode import switch_workmode, set_models
from .indexer import write_active_skills_manifest
from .memory import get_recent_context, save_session

_CONTEXT_COUNTER = 0


def cmd_workmode(args):
    switch_workmode(args.action)


def _get_team() -> str:
    try:
        f = config.FAREWELL_DIR / "team.json"
        if f.exists():
            return _json.loads(f.read_text(encoding="utf-8")).get("team", "TIM")
    except Exception: pass
    return "TIM"


def cmd_team(args):
    from .helpers import _c
    status = args.status
    if status in ("on", "divisi"):
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "ON"}), encoding="utf-8")
        set_models("9router/Deepseek-GO-Flash", "9router/Free", "divisi")
        _write_context_footer()
        print(f"\n  {_c('[DIVISI]', 'green')} Ketua Divisi leading: ocg/deepseek-v4-flash\n")
    elif status in ("off", "tim"):
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "TIM"}), encoding="utf-8")
        set_models("9router/Ketua-Tim", "9router/Pekerja", "tim")
        _write_context_footer()
        print(f"\n  {_c('[TEAM]', 'yellow')} Ketua Tim leading: oc/deepseek-v4-flash-free + workers\n")
    elif status == "bawahan":
        (config.FAREWELL_DIR / "team.json").write_text(_json.dumps({"team": "BAWAHAN"}), encoding="utf-8")
        set_models("9router/Pekerja", "9router/Pekerja", "bawahan")
        _write_context_footer()
        print(f"\n  {_c('[KARYAWAN]', 'cyan')} Workers langsung tanpa leader\n")
    else:
        team = _get_team()
        if team == "ON": model = "ocg/deepseek-v4-flash"; tier = "Divisi"
        elif team == "TIM": model = "oc/deepseek-v4-flash-free"; tier = "Tim"
        else: model = "workers"; tier = "Bawahan"
        print(f"  Team: {team} ({tier}: {model})")


def cmd_daily(args):
    from .daily import run_daily
    run_daily()


def cmd_project(args):
    from .helpers import list_registered_projects, read_json, write_json, _c, read_project_code
    from .memory import save_session
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
                # Save memory for previous project
                old_active = reg.get("active", "farewell-assistant")
                old_code = read_project_code(old_active)
                save_session(old_code, old_active, f"switched to {args.action}-{name}")

                reg["active"] = name
                write_json(config.REGISTRY_FILE, reg)
                _write_context_footer()
                print(f"\n  {_c('[ACTIVE]', 'green')} {args.action}-{name}\n")
                return
        print(f"  Project code '{args.action}' not found.")


def cmd_cool(args):
    from .awesome_indexer import load_all_entries, get_recommended_projects_for_stack, get_project_info
    from .helpers import _c, read_project_active, read_project_code
    plugs, themes, ags, projs, res = load_all_entries()

    if args.action == "info" and args.query:
        for cat, entries in [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs), ("resource", res)]:
            for e in entries:
                if args.query.lower() in e.get("name", "").lower():
                    name = e.get("name", "")
                    print(f"\n  {_c(f'[{cat}] {name}', 'cyan')}")
                    print(f"  {e.get('tagline', '')}")
                    print(f"   {e.get('description', '')}")
                    print(f"   {e.get('repo', '')}")
                    if "installation" in e:
                        print(f"   install: {e['installation']}")
                    print()
                    return
        print(f"  '{args.query}' not found in awesome-opencode")

    elif args.action == "search" and args.query:
        q = args.query.lower()
        found = []
        for cat, entries in [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs), ("resource", res)]:
            for e in entries:
                if q in e.get("name", "").lower() or q in e.get("tagline", "").lower() or q in e.get("description", "").lower():
                    found.append((cat, e))
        found_count = len(found)
        print(f"\n  {_c(f'Found {found_count} in awesome-opencode for: {args.query}', 'cyan')}\n")
        for cat, e in found[:20]:
            print(f"  [{cat:>7}] {e.get('name')}")
            print(f"          {e.get('tagline', '')}")
            print(f"          {e.get('repo', '')}")
            print()

    elif args.action == "list":
        cat = args.category or "all"
        sources = [("plugin", plugs), ("theme", themes), ("agent", ags), ("project", projs), ("resource", res)]
        print()
        for label, entries in sources:
            if cat in ("all", label):
                print(f"  {_c(f'{label}s ({len(entries)})', 'cyan')}")
                for e in entries[:10]:
                    scope = ",".join(e.get("scope", ["global"])) if "scope" in e else ""
                    s = f" [{scope}]" if scope else ""
                    print(f"    - {e.get('name')}{s}")
                if len(entries) > 10:
                    print(f"    ... +{len(entries)-10} more")
                print()

    elif args.action == "recommend":
        active = read_project_active()
        code = read_project_code(active)
        from .indexer import get_project_skills
        skills = get_project_skills(code, active)
        stack = list(dict.fromkeys([s.split("-")[0] for s in skills if "-" in s]))
        if not stack:
            stack = [code.split("-")[0] if "-" in code else code]
        recs = get_recommended_projects_for_stack(stack)
        if recs:
            stack_str = ", ".join(stack[:3])
            print(f"\n  {_c(f'awesome recommendations for {code}-{active} (stack: {stack_str})', 'cyan')}\n")
            for r in recs[:10]:
                print(f"  - {r.get('name')}: {r.get('tagline', '')}")
                print(f"    {r.get('repo', '')}")
            print()
        else:
            print(f"\n  No recommendations for current project\n")

    elif args.action == "stats":
        print(f"\n  {_c('awesome-opencode stats', 'cyan')}")
        print(f"  plugins:  {len(plugs)}")
        print(f"  themes:   {len(themes)}")
        print(f"  agents:   {len(ags)}")
        print(f"  projects: {len(projs)}")
        print(f"  resources:{len(res)}")
        print(f"  total:    {len(plugs)+len(themes)+len(ags)+len(projs)+len(res)}\n")


def cmd_status(args):
    from .helpers import read_project_active, get_work_mode, _c, read_project_code
    from .indexer import get_project_skills
    from .awesome_indexer import load_all_entries
    active = read_project_active()
    mode = get_work_mode()
    code = read_project_code(active)
    team = _get_team()
    if team == "ON": tier = "Divisi"
    elif team == "TIM": tier = "Tim"
    else: tier = "Bawahan"
    skills = get_project_skills(code, active)
    sk = f" | Skills: {len(skills)}" if skills else ""
    plugs, themes, ags, projs, res = load_all_entries()
    ao = f" | awesome: {len(plugs)}p/{len(ags)}a/{len(projs)}pr"
    print(f"\n  {_c(f'Farewell: ON | {code}-{active} | {mode.upper()}{sk} | {tier}{ao}', 'cyan')}\n")


def _write_context_footer(project: str | None = None, mode: str | None = None):
    from .helpers import read_project_code, read_project_active, get_work_mode
    from .indexer import get_project_skills
    from .awesome_indexer import get_recommended_projects_for_stack
    if project is None:
        project = read_project_active()
    if mode is None:
        mode = get_work_mode()
    code = read_project_code(project)
    team = _get_team()
    if team == "ON": tier = "Divisi"
    elif team == "TIM": tier = "Tim"
    else: tier = "Bawahan"
    skills = get_project_skills(code, project)
    sk = f" | Skills: {len(skills)}" if skills else ""

    # Write active skills manifest (filtered)
    write_active_skills_manifest(code, project)

    # Memory context
    mem_ctx = get_recent_context(code, project)

    # Awesome recommendations
    stack = list(dict.fromkeys([s.split("-")[0] for s in skills if "-" in s]))
    if stack:
        recs = get_recommended_projects_for_stack(stack)
        recs_str = "\n".join(f"  - {r.get('name')}: {r.get('tagline', '')}" for r in recs[:3])
        recs_block = f"\n\n# Awesome Recommendations\n{recs_str}" if recs_str else ""
    else:
        recs_block = ""

    global _CONTEXT_COUNTER
    _CONTEXT_COUNTER += 1
    ctx = f"""# State
Farewell: ON
Tier: {tier}
Project: {code}-{project}
Mode: {mode.upper()}{sk}
{mem_ctx}{recs_block}
"""
    (config.STATE_DIR / "context.md").write_text(ctx, encoding="utf-8")

    if _CONTEXT_COUNTER % 5 == 0 and mode != "plan":
        save_session(code, project, f"Mode: {mode.upper()} | Skills: {len(skills)}", list(skills[:5]), 0)


def main():
    _write_context_footer()
    parser = argparse.ArgumentParser(prog="farewell-assistant", description="Lightweight 9Router orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    wm_p = subparsers.add_parser("workmode", help="Switch work mode (plan/build)")
    wm_p.add_argument("action", nargs="?", default="status", choices=["plan", "build", "status"])
    wm_p.set_defaults(func=cmd_workmode)

    team_p = subparsers.add_parser("team", help="Switch Divisi / Tim / Bawahan / status")
    team_p.add_argument("status", nargs="?", default="status", choices=["on", "off", "divisi", "tim", "bawahan", "status"])
    team_p.set_defaults(func=cmd_team)

    status_p = subparsers.add_parser("status", help="Show current state")
    status_p.set_defaults(func=cmd_status)

    daily_p = subparsers.add_parser("daily", help="Daily all-in-one: start 9Router + upstream + sync + readiness check")
    daily_p.set_defaults(func=cmd_daily)

    proj_p = subparsers.add_parser("project", help="List or switch active project")
    proj_p.add_argument("action", nargs="?", default="list", help="Project code or 'list'")
    proj_p.set_defaults(func=cmd_project)

    cool_p = subparsers.add_parser("cool", help="awesome-opencode: list / search / info / recommend / stats")
    cool_p.add_argument("action", nargs="?", default="stats", choices=["list", "search", "info", "recommend", "stats"])
    cool_p.add_argument("query", nargs="?", default="")
    cool_p.add_argument("-c", "--category", default="all", help="Filter: plugin, theme, agent, project, resource")
    cool_p.set_defaults(func=cmd_cool)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        import sys; sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()