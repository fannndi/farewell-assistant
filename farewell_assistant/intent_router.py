"""Intent Router - Routes user intent to appropriate skill chain and model."""

import json
from datetime import datetime, timezone

from . import config
from .helpers import get_llm_mode, get_work_mode, read_json, write_json, _c
from .enrichment_pipeline import (
    invoke_structured_enrichment,
    get_quick_intent,
    get_cached_intent,
    set_cached_intent,
    check_input_sufficiency,
)
from .skill_chain import get_skill_chain
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


# ---------------------------------------------------------------------------
# Permission Check
# ---------------------------------------------------------------------------

def check_task_permission(intent: dict, work_mode: str) -> dict:
    if work_mode == "plan" and intent.get("intent") in ("build", "fix", "deploy"):
        return {"allowed": False, "reason": f"Intent '{intent['intent']}' requires BUILD mode. Current mode: PLAN"}
    return {"allowed": True}


# ---------------------------------------------------------------------------
# Model Route Selection
# ---------------------------------------------------------------------------

def select_model_route(complexity: str, profile: str) -> dict:
    route = config.MODEL_ROUTES.get(complexity, config.MODEL_ROUTES["medium"])
    return route


# ---------------------------------------------------------------------------
# Persist Turn State to Context Files
# ---------------------------------------------------------------------------

def sync_turn_state(result: dict, user_input: str = ""):
    """Write pipeline-result.json + context.md."""
    state_dir = config.STATE_DIR

    # Read registry for active project + kategori
    active = "farewell-assistant"
    kategori = "AUTOMATION"
    try:
        reg = read_json(config.REGISTRY_FILE)
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
    pipeline_data = {"timestamp": now, "input": user_input, "turn": result.get("turn", 0)}

    if result.get("success"):
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
        })
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
    mode = get_llm_mode()
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

    context_content = f"""# Session State

- **Project:** {active}
- **Kategori:** {kategori}
- **Mode:** {mode}
- **Work:** {work}
- **Started:** {session_started}

# Turn State

- **Intent:** {intent_display}
- **Complexity:** {complexity_display}
- **Confidence:** {confidence_display}
- **Stack:** {stack_display}
- **Chain:** {chain_display}
- **Model:** {model_display}
- **Planning:** {planning_display}
- **Turn:** {turn_count}
"""
    (state_dir / "context.md").write_text(context_content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main Router Function
# ---------------------------------------------------------------------------

def invoke_intent_router(
    text_input: str,
    context: str = "",
    work_mode: str = "",
    active_profile: str = "",
    force: bool = False,
) -> dict:
    """Route user intent to skill chain + model selection."""
    if not work_mode:
        work_mode = get_work_mode()
    if not active_profile:
        active_profile = get_llm_mode()

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
    chain = get_skill_chain(classified["intent"], classified["domain"])

    # Step 4: Select model route
    model_route = select_model_route(classified["complexity"], active_profile)

    # Step 5: Determine if planning phase needed
    needs_planning = classified["complexity"] in ("high", "critical") and classified["intent"] == "build"

    # Step 6: Build blocked intents list
    blocked = ["build", "fix", "deploy"] if work_mode == "plan" else []

    # Step 7: Chain summary
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
