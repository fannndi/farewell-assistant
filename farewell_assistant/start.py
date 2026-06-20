"""Full startup orchestrator - combines bootstrap, update, health, pipeline."""

import json
import os
import subprocess
import time

from . import config
from .bootstrap import handle_first_run, bootstrap_check
from .update import run_update_check, rebuild_9router_if_needed
from .health import ensure_9router, ensure_ollama
from .helpers import (
    get_llm_mode, parse_api_key, read_json, write_info, write_ok, write_skip, write_step,
    log_session,
)
from .intent_router import invoke_intent_router
from .log import sync_session_state, write_task_log


def run_start() -> bool:
    """Full startup sequence. Returns True if all critical steps passed."""
    start = time.monotonic()

    print()
    print("  =================================================")
    print("  farewell-assistant - Start")
    print("  =================================================")
    print()

    # Step 1: Git pull self
    write_step("1/7", "Git Pull Self")
    try:
        import subprocess
        r = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True, text=True,
            cwd=str(config.ROOT_DIR),
        )
        if r.returncode == 0 and r.stdout.strip():
            write_ok("Git pull: " + r.stdout.strip())
        else:
            write_skip("Git: up to date")
    except Exception as e:
        write_info("Git pull: " + str(e))

    # Step 2: Bootstrap (first run)
    write_step("2/7", "Initial Bootstrap")
    if bootstrap_check():
        handle_first_run()
    else:
        write_skip("Initial already done")

    # Step 3: Update ECC + 9Router
    write_step("3/7", "Update Check")
    updates = run_update_check()
    if updates.get("router_updated"):
        rebuild_9router_if_needed(True)

    # Step 4: 9Router health
    write_step("4/7", "9Router Health")
    ensure_9router()

    # Step 5: Configuration (api-key.txt, combos)
    write_step("5/7", "Load Configuration")
    _handle_config()

    # Step 6: Pipeline prime
    write_step("6/7", "Pipeline + Launch")
    mode = get_llm_mode()
    if mode != "eco":
        ensure_ollama()

    _prime_pipeline()

    # Sync & log
    sync_session_state()
    duration = round(time.monotonic() - start, 1)
    write_task_log("START", f"Boot completed ({duration}s)", "success")
    write_step("7/7", "Ready")
    write_ok(f"Ready ({duration}s)")
    return True


def _handle_config():
    """Parse api-key.txt, load combos, generate profile."""
    api_key_file = config.API_KEY_FILE
    if not api_key_file.exists():
        write_skip("api-key.txt not found")
        return

    api_key_config = parse_api_key()
    api_key, combo_entries, combo_models = api_key_config

    if combo_entries:
        # Export env vars for 9Router startup
        if api_key:
            os.environ["NINEROUTER_API_KEY"] = api_key
        if api_key_config.router_password:
            os.environ["9ROUTER_PASSWORD"] = api_key_config.router_password

        write_ok("API keys loaded")
        # Check for new/changed combos
        cached = read_json(config.COMBO_FILE, default=[]) or []
        cached_map = {str(c.get("name", "")): c for c in cached if isinstance(c, dict)}
        for idx, entry in sorted(combo_entries.items()):
            if idx not in cached_map:
                combo_name = entry.get("combo", idx)
                write_ok(f"NEW combo: {idx} ({combo_name})")
        # Save combo cache
        save = []
        for idx in sorted(combo_entries.keys()):
            save.append({
                "name": idx,
                "combo": combo_entries[idx],
                "models": combo_models.get(idx, {}).get("models", []),
            })
        config.COMBO_FILE.parent.mkdir(parents=True, exist_ok=True)
        config.COMBO_FILE.write_text(json.dumps(save, indent=2, ensure_ascii=False), encoding="utf-8")
        write_ok("Combos saved")

        # Generate opencode profile
        _generate_profile(combo_entries, combo_models)
    else:
        write_skip("No COMBO_* entries")


def _generate_profile(combo_entries: dict, combo_models: dict):
    """Generate opencode.jsonc from template."""
    profile_src = config.PROFILE_SRC
    if not profile_src.exists():
        write_skip("Profile template not found")
        return

    try:
        content = profile_src.read_text(encoding="utf-8")
    except Exception:
        return

    sorted_indices = sorted(combo_entries.keys())
    combos = [combo_entries[i]["combo"] for i in sorted_indices if combo_entries[i].get("combo")]

    content = content.replace("{project}", str(config.ROOT_DIR).replace("\\", "/"))
    c0 = combos[0] if combos else ""
    c1 = combos[1] if len(combos) > 1 else c0
    content = content.replace("${COMBO_0}", c0)
    content = content.replace("${COMBO_1}", c1)

    # Build combo models JSON
    model_obj = {}
    for c in combos:
        model_obj[c] = {"name": c + " combo"}
    content = content.replace("${COMBO_MODELS}", json.dumps(model_obj, indent=2))

    # Context file
    context_slug = "farewell-assistant"
    reg = read_json(config.REGISTRY_FILE)
    if reg and reg.get("active"):
        context_slug = reg["active"]
    content = content.replace("{context_file}", context_slug)

    config.OPENCODE_DIR.mkdir(parents=True, exist_ok=True)
    config.OPENCODE_CFG.write_text(content, encoding="utf-8")
    write_ok("Profile applied")


def _prime_pipeline():
    """Prime the intent pipeline with 'session start'."""
    write_step("Pipeline", "Prime")
    try:
        result = invoke_intent_router("session start", force=True)
        if result.get("success"):
            i = result.get("intent", {})
            write_ok(
                "Pipeline primed: "
                + i.get("intent", "?") + "/"
                + i.get("domain", "?") + "/"
                + i.get("complexity", "?")
            )
        else:
            write_ok("Pipeline primed (startup)")
    except Exception as e:
        write_skip("Pipeline skip: " + str(e))


def run_daily() -> bool:
    """Daily session start: full startup + session-log."""
    print()
    print("  =================================================")
    print("  farewell-assistant - Daily")
    print("  =================================================")
    print()
    ok = run_start()
    # Log session after startup
    log_session()
    return ok
