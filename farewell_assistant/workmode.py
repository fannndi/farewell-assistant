"""Work mode — PLAN/BUILD switch. Writes work-mode.json + syncs default_agent + model in opencode.jsonc."""

import json
import re
from datetime import datetime, timezone
from . import config
from .helpers import read_json, write_json, write_ok, write_info, write_fail


OC_FILE = config.ROOT_DIR / "opencode.jsonc"


def _jsonc_strip_comments(text: str) -> str:
    return re.sub(r'//.*', '', text)


def _patch_jsonc_value(key: str, value: str, content: str) -> str:
    return re.sub(
        rf'("{re.escape(key)}"\s*:\s*)"[^"]*"',
        lambda m: f'{m.group(1)}"{value}"',
        content,
    )


def _switch_default_agent(target: str) -> bool:
    if not OC_FILE.exists():
        return False
    try:
        content = OC_FILE.read_text(encoding="utf-8")
        new_content = _patch_jsonc_value("default_agent", target, content)
        if new_content == content:
            return False
        tmp = OC_FILE.with_suffix(".jsonc.tmp")
        tmp.write_text(new_content, encoding="utf-8")
        tmp.replace(OC_FILE)
        return True
    except Exception:
        return False


def set_models(model_key: str, small_key: str):
    """JSONC-safe model swap — updates root + all agent-level model references."""
    if not OC_FILE.exists():
        return
    try:
        content = OC_FILE.read_text(encoding="utf-8")
        # Swap at root level
        content = _patch_jsonc_value("model", model_key, content)
        content = _patch_jsonc_value("small_model", small_key, content)
        # Swap at every agent level (all have "model": "...")
        # Use a broader approach: find all "model": "9router/..." references
        content = re.sub(
            r'("model"\s*:\s*)"9router/[^"]*"',
            lambda m: f'{m.group(1)}"{model_key}"',
            content,
        )
        # But restore small_model if it was also caught by the broad pattern
        content = _patch_jsonc_value("small_model", small_key, content)
        tmp = OC_FILE.with_suffix(".jsonc.tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(OC_FILE)
    except Exception:
        pass


def switch_workmode(action: str):
    current = read_json(config.WORK_MODE_FILE, {}).get("mode", "build")
    if action == "status":
        print(f"\n  Mode: {current.upper()}")
        return
    if action == current:
        write_info(f"Already in {action.upper()}")
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    write_json(config.WORK_MODE_FILE, {"mode": action, "updated_at": now})

    target = "team" if action == "plan" else "build"
    synced = _switch_default_agent(target)

    if synced:
        write_ok(f"Work mode set to {action.upper()} (agent: {target})")
    else:
        write_fail(f"Work mode set to {action.upper()} but default_agent sync FAILED — check opencode.jsonc")
