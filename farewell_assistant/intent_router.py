"""Intent Router - Routes user intent to appropriate skill chain and model."""

from datetime import datetime, timezone

from . import config
from .helpers import get_work_mode, read_json, write_json, _c, read_project_active, detect_stack_from_path, validate_task_vs_project
from .enrichment_pipeline import (
    invoke_structured_enrichment,
    get_quick_intent,
    get_cached_intent,
    set_cached_intent,
    check_input_sufficiency,
)
from .skill_chain import get_skill_chain, test_skill_chain
from .log import write_task_log

# ---------------------------------------------------------------------------
# Turn Counter (persisted to .opencode/turn-count)
# ---------------------------------------------------------------------------

def _get_turn_count() -> int:
    path = config.STATE_DIR / "turn-count"
    try:
        if path.exists():
            return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        pass
    return 0


def _set_turn_count(count: int):
    path = config.STATE_DIR / "turn-count"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(count), encoding="utf-8")


def _reset_turn_count():
    _set_turn_count(0)


# ---------------------------------------------------------------------------
# Permission Check
# ---------------------------------------------------------------------------

def check_task_permission(intent: dict, work_mode: str) -> dict:
    if work_mode == "plan" and intent.get("intent") in ("build", "fix", "deploy"):
        return {"allowed": False, "reason": f"Intent '{intent['intent']}' requires BUILD mode. Current mode: PLAN"}
    return {"allowed": True}


def _get_project_info(project_name: str, registry_file=None) -> dict | None:
    """Get project info from registry."""
    file_to_read = registry_file or config.REGISTRY_FILE
    reg = read_json(file_to_read)
    if reg and reg.get("projects", {}).get(project_name):
        return reg["projects"][project_name]
    return None


# ---------------------------------------------------------------------------
# Skill-Level Permission (mode-based skill filtering)
# ---------------------------------------------------------------------------

def filter_chain_by_mode(chain: list[dict[str, str]], work_mode: str) -> list[dict[str, str]]:
    """Filter skill chain: remove EXCLUSIVE WRITE skills if in PLAN mode.
    Skills shared with plan groups or hybrid groups are kept."""
    if work_mode != "plan":
        return chain

    build_only = _get_build_only_skills()
    hybrid_skills = _get_hybrid_skills()
    filtered = []
    for step in chain:
        name = step["name"]
        if name in build_only:
            continue  # skip WRITE-only skills in PLAN mode
        step_copy = dict(step)
        if name in hybrid_skills:
            step_copy["mode_hint"] = "PLAN: analysis only"
        filtered.append(step_copy)
    return filtered


def _get_build_only_skills() -> set[str]:
    """Load skills EXCLUSIVE to build mode (not shared with plan or hybrid)."""
    try:
        idx = read_json(config.SKILL_IDX_FILE)
        if not idx:
            return set()
        build_skills = set()
        for group in idx.get("build", {}).get("skill_groups", {}).values():
            build_skills.update(group)
        plan_skills = set()
        for group in idx.get("plan", {}).get("skill_groups", {}).values():
            plan_skills.update(group)
        hybrid_skills = set()
        for group in idx.get("hybrid", {}).get("skill_groups", {}).values():
            hybrid_skills.update(group)
        return build_skills - plan_skills - hybrid_skills
    except Exception:
        return set()


def _get_hybrid_skills() -> set[str]:
    """Load HYBRID skill names from skill-mode-index."""
    try:
        idx = read_json(config.SKILL_IDX_FILE)
        if not idx:
            return set()
        skills = set()
        for group in idx.get("hybrid", {}).get("skill_groups", {}).values():
            skills.update(group)
        return skills
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# Model Route — single model, always on
# ---------------------------------------------------------------------------

def select_model_route(complexity: str) -> dict:
    return {"primary": "qwen2.5-coder-1.5b", "secondary": "qwen2.5-coder-1.5b", "heavy": "qwen2.5-coder-1.5b"}


# ---------------------------------------------------------------------------
# Persist Turn State to Context Files
# ---------------------------------------------------------------------------

def sync_turn_state(result: dict, user_input: str = ""):
    """Write pipeline-result.json + context.md."""
    state_dir = config.STATE_DIR
    # Read registry for active project + kategori
    reg_file = config.REGISTRY_FILE
    
    active = "farewell-assistant"
    kategori = "AUTOMATION"
    try:
        reg = read_json(reg_file)
        if reg and reg.get("active"):
            active = reg["active"]
            if reg.get("projects", {}).get(active, {}).get("kategori"):
                kat_vals = set()
                for v in reg["projects"][active]["kategori"].values():
                    kat_vals.add(v)
                kategori = " > ".join(sorted(kat_vals))
    except Exception:
        pass

    # 1. Write pipeline-result.json
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    # Get project code from registry
    project_code = ""
    try:
        reg = read_json(reg_file)
        if reg and reg.get("active") and reg.get("projects", {}).get(reg["active"], {}).get("project_code"):
            project_code = reg["projects"][reg["active"]]["project_code"]
    except Exception:
        pass
    pipeline_data = {"timestamp": now, "input": user_input, "turn": result.get("turn", 0), "project_code": project_code}

    from .helpers import get_llm_mode as _get_llm_mode

    if result.get("success"):
        secondary = result["intent"].get("secondary_intents")
        pipeline_data.update({
            "project": active,
            "intent": result["intent"]["intent"],
            "domain": result["intent"]["domain"],
            "stack": result["intent"].get("stack", []),
            "complexity": result["intent"]["complexity"],
            "confidence": result["intent"]["confidence"],
            "source": result["intent"].get("source", ""),
            "needs_planning": result.get("needs_planning", False),
            "model_primary": result["model_route"]["primary"],
            "model_heavy": result["model_route"]["heavy"],
            "chain": [s["name"] for s in result.get("skill_chain", [])],
            "chain_summary": result.get("chain_summary", ""),
            "blocked": result.get("blocked", []),
            "work_mode": result.get("work_mode", ""),
            "profile": result.get("profile", ""),
            "task_warning": result.get("task_warning"),
        })
        if secondary:
            pipeline_data["secondary_intents"] = secondary
        if result.get("post_steps"):
            pipeline_data["post_steps"] = result["post_steps"]
        if result.get("degraded"):
            pipeline_data["degraded"] = result["degraded"]
    else:
        pipeline_data.update({
            "project": active,
            "blocked": True,
            "hold": result.get("hold", False),
            "reason": result.get("reason", ""),
            "intent": result.get("intent", {}).get("intent", ""),
        })
        if result.get("missing"):
            pipeline_data["missing"] = result["missing"]

    write_json(state_dir / "pipeline-result.json", pipeline_data)

    # 2. Update context.md
    mode = "on"
    work = get_work_mode().upper()

    # Build chain display
    if result.get("success"):
        chain_display = result.get("chain_summary", "")
        intent_display = result["intent"]["intent"]
        complexity_display = result["intent"]["complexity"]
        confidence_pct = round(result["intent"]["confidence"] * 100)
        source = result["intent"].get("source", "")
        confidence_display = f"{confidence_pct}%({source})"
        stack_display = ", ".join(result["intent"].get("stack", [])) or "-"
        planning_display = "yes" if result.get("needs_planning") else "no"
        blocked_display = ", ".join(result.get("blocked", [])) if result.get("blocked") else "none"
        model_display = f"{result['model_route']['primary']}/{result['model_route']['heavy']}"
    else:
        chain_display = ""
        intent_display = "BLOCKED"
        complexity_display = ""
        confidence_display = ""
        stack_display = ""
        planning_display = ""
        blocked_display = result.get("reason", "")
        model_display = ""

    turn_count = result.get("turn", 0)

    # Read session start time
    session_started = ""
    try:
        ss = read_json(config.STATE_DIR / "session-state.json")
        if ss and ss.get("session", {}).get("started"):
            session_started = ss["session"]["started"]
    except Exception:
        pass

    # Read project info for richer context
    project_type = ""
    project_dominan = ""
    project_stack = ""
    project_path = ""
    try:
        reg = read_json(reg_file)
        if reg and reg.get("active") and reg.get("projects", {}).get(reg["active"]):
            p = reg["projects"][reg["active"]]
            project_type = p.get("type", "")
            project_dominan = p.get("dominan", "")
            project_path = p.get("path", "")
    except Exception:
        pass

    # Chain step details
    chain_steps = ""
    if result.get("success") and result.get("skill_chain"):
        steps = []
        for i, s in enumerate(result["skill_chain"], 1):
            mode_hint = s.get("mode_hint", "")
            hint = f" ({mode_hint})" if mode_hint else ""
            steps.append(f"    {i}. {s['name']}{hint} — {s['desc']}")
        chain_steps = "\n" + "\n".join(steps)

    context_content = f"""# Session State

- **Project:** {active}
- **Project Type:** {project_type}
- **Project Stack:** {project_dominan}
- **Kategori:** {kategori}
- **Mode:** {mode}
- **Work:** {work}
- **Started:** {session_started}

# Turn State

- **Turn:** {turn_count}
- **Input:** {result.get("input", "")}
- **Intent:** {intent_display}
- **Domain:** {result.get("intent", {}).get("domain", "") if result.get("success") else ""}
- **Complexity:** {complexity_display}
- **Confidence:** {confidence_display}
- **Stack:** {stack_display}
- **Chain:** {chain_display}
- **Chain Steps:** {chain_steps if chain_steps else "-"}
- **Model:** {model_display}
- **Planning:** {planning_display}
- **Blocked:** {blocked_display}

# AI Instructions

Analisis input user berdasarkan context di atas. Gunakan Chain Steps sebagai panduan skill yang harus di-load. Jika blocked, informasikan user untuk switch mode.
"""
    (state_dir / "context.md").write_text(context_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main Router Function
# ---------------------------------------------------------------------------

def invoke_intent_router(
    text_input: str,
    context: str = "",
    work_mode: str = "",
    active_profile: str = "on",
    force: bool = False,
) -> dict:
    """Route user intent to skill chain + model."""
    if not work_mode:
        work_mode = get_work_mode()

    # Increment turn counter
    turn_count = _get_turn_count() + 1
    _set_turn_count(turn_count)

    # Step 1: Classify intent
    classified = get_cached_intent(text_input)
    if not classified:
        structured = invoke_structured_enrichment(text_input, context, force=force)
        quick = get_quick_intent(text_input)
        if structured:
            classified = structured
            if structured["confidence"] < 0.5 and quick["confidence"] >= 0.8:
                classified = quick
                classified["source"] = "quick"
        else:
            classified = quick
            classified["source"] = "quick"

        # Eco mode fallback: file-based stack detection when enrichment disabled
        if not classified.get("stack") or classified["stack"] == ["-"]:
            active_project = read_project_active(config.REGISTRY_FILE)
            if active_project:
                import os as _os
                project_info = _get_project_info(active_project)
                if project_info and project_info.get("path"):
                    project_path = project_info["path"].replace("$ROOT", str(config.ROOT_DIR))
                    if _os.path.isdir(project_path):
                        file_stack = detect_stack_from_path(project_path)
                        if file_stack:
                            classified["stack"] = file_stack

        set_cached_intent(text_input, classified)

    # Step 2: Check permissions
    permission = check_task_permission(classified, work_mode)
    if not permission["allowed"]:
        result = {"success": False, "reason": permission["reason"], "intent": classified, "turn": turn_count}
        sync_turn_state(result, text_input)
        return result

    # Step 2.5: Check input sufficiency
    sufficiency = check_input_sufficiency(text_input, classified)
    if not sufficiency["sufficient"]:
        result = {
            "success": False,
            "hold": True,
            "reason": sufficiency["reason"],
            "missing": sufficiency.get("missing"),
            "intent": classified,
            "turn": turn_count,
        }
        sync_turn_state(result, text_input)
        return result

    # Step 3: Build skill chain
    # Refactor override — if input contains "refactor", route to fix_refactor chain
    if "refactor" in text_input.lower() and classified["intent"] == "fix":
        chain, chain_degraded = get_skill_chain("fix_refactor", classified["domain"])
    else:
        chain, chain_degraded = get_skill_chain(classified["intent"], classified["domain"])

    # Step 3.2: Project-task validation
    task_warning = None
    active_project = read_project_active(config.REGISTRY_FILE)
    if active_project:
        project_info = _get_project_info(active_project, config.REGISTRY_FILE)
        if project_info:
            project_type = project_info.get("type", "unknown")
            project_stack = project_info.get("dominan", "").split("+") if project_info.get("dominan") else []
            task_warning = validate_task_vs_project(classified["intent"], project_type, project_stack)

    # Step 3.3: Remind eksekutor to run self-heal after build/fix edits
    self_heal_hint = None
    post_steps = []
    if classified["intent"] in ("build", "fix"):
        self_heal_hint = "Setelah mengedit file, jalankan: py -m farewell_assistant.cli self-heal --file <path>"
        post_steps.append("self-heal")

    # Step 3.5: Filter chain by work mode (remove WRITE skills in PLAN mode)
    chain = filter_chain_by_mode(chain, work_mode)

    # Step 3.7: Validate chain skills exist on disk
    degraded = chain_degraded
    if chain:
        chain_check = test_skill_chain(chain)
        if chain_check["missing"]:
            write_task_log("CHAIN", f"Missing skills: {chain_check['missing']}", "warn")
            total = chain_check["total_count"]
            missing_count = len(chain_check["missing"])
            if missing_count > total * 0.5:
                result = {
                    "success": False,
                    "reason": f"Chain rusak: {missing_count}/{total} skill hilang. Missing: {', '.join(chain_check['missing'])}",
                    "intent": classified,
                    "turn": turn_count,
                }
                sync_turn_state(result, text_input)
                return result
            chain = [s for s in chain if s["name"] not in chain_check["missing"]]
            degraded = f"Stripped {missing_count} missing skills dari chain"

    # Step 4: Select model route
    model_route = select_model_route(classified["complexity"])

    # Step 5: Determine if planning phase needed
    needs_planning = classified["complexity"] in ("high", "critical") and classified["intent"] == "build"

    # Step 6: Build blocked intents list
    blocked = ["build", "fix", "deploy"] if work_mode == "plan" else []

    # Step 7: Chain summary + post-steps
    chain_summary = " → ".join(s["name"] for s in chain)

    result = {
        "success": True,
        "intent": classified,
        "skill_chain": chain,
        "model_route": model_route,
        "needs_planning": needs_planning,
        "work_mode": work_mode,
        "profile": active_profile,
        "turn": turn_count,
        "blocked": blocked,
        "chain_summary": chain_summary,
        "task_warning": task_warning,
        "self_heal_hint": self_heal_hint,
        "post_steps": post_steps if post_steps else None,
        "degraded": degraded,
    }

    # Persist to context files
    sync_turn_state(result, text_input)

    return result


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def show_intent_router_result(result: dict):
    if not result.get("success"):
        print(f"\n  {_c('[BLOCKED]', 'red')} {result['reason']}")
        print(f"  Switch to BUILD mode: /workmode build\n")
        return

    intent = result["intent"]
    chain = result["skill_chain"]
    model = result["model_route"]

    print(f"\n  {'='*50}")
    print(f"  {_c('Intent Router', 'cyan')}")
    print(f"  {'='*50}\n")
    print(f"  Intent:       {intent['intent']}")
    print(f"  Domain:       {intent['domain']}")
    complexity_color = "yellow" if intent["complexity"] == "high" else ("cyan" if intent["complexity"] == "medium" else "green")
    print(f"  Complexity:   {_c(intent['complexity'], complexity_color)}")
    print(f"  Confidence:   {round(intent['confidence'] * 100)}%")
    print(f"  Source:       {intent.get('source', '')}")
    if intent.get("stack"):
        print(f"  Stack:        {', '.join(intent['stack'])}")
    print()
    print(f"  Model:        Free={model['primary']} / Emergency={model['secondary']}")
    print(f"  Planning:     {result['needs_planning']}")
    print()
    print(f"  Skill Chain ({len(chain)} steps):")
    for i, step in enumerate(chain, 1):
        print(f"    {i}. {_c(step['name'], 'cyan')}")
        print(f"       {step['desc']}")
    print(f"\n  {'='*50}\n")
