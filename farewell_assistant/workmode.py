"""Work mode — PLAN/BUILD switch. Writes work-mode.json + syncs default_agent + model in opencode.jsonc."""

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


def set_models(model_key: str, small_key: str, tier: str = "divisi"):
    """JSONC-safe model swap — updates root + agent-level models per team tier."""
    if not OC_FILE.exists():
        return
    try:
        content = OC_FILE.read_text(encoding="utf-8")

        # Step 1: Set all AGENT models (indented lines) to model_key
        content = re.sub(
            r'(\s{4,}"model"\s*:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{model_key}"',
            content,
        )

        # Step 2: Set ROOT model (first occurrence, minimal indent)
        content = re.sub(
            r'^(\s*"model"\s*:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{model_key}"',
            content, count=1, flags=re.MULTILINE,
        )

        content = re.sub(
            r'^(\s*"small_model"\s*:\s*)"[^"]*"',
            lambda m: f'{m.group(1)}"{small_key}"',
            content, count=1, flags=re.MULTILINE,
        )
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
