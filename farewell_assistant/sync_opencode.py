"""Sync 9Router combos + Nvidia → opencode.jsonc models."""

import json
import os
import re
from pathlib import Path
from . import config


def _load_db() -> list[dict]:
    """Read combos from 9Router SQLite."""
    import sqlite3
    db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if not db.exists():
        return []
    conn = sqlite3.connect(str(db))
    cur = conn.execute("SELECT name, kind, models FROM combos")
    combos = []
    for row in cur.fetchall():
        if row[0].lower() == "nvidia":
            continue
        models = json.loads(row[2]) if row[2] else []
        if models:
            total = len(models)
            kind = row[1] or "round-robin"
            combos.append({
                "key": row[0],
                "name": f"{row[0]} ({total} models, {kind})",
                "models": models
            })
    conn.close()
    return combos


def _nvidia_models() -> dict:
    """Nvidia provider model definitions."""
    return {
        "deepseek-ai/deepseek-v4-flash": {"name": "Nvidia Flash (40 RPM)"},
        "deepseek-ai/deepseek-v4-pro": {"name": "Nvidia Pro (40 RPM)"},
    }


def _generate_provider_block(combos: list[dict]) -> str:
    """Generate the provider section JSON string."""
    lines = []
    lines.append('    "9router": {')
    lines.append('      "npm": "@ai-sdk/openai-compatible",')
    lines.append('      "name": "Local 9Router",')
    lines.append('      "env": ["NINEROUTER_API_KEY"],')
    lines.append('      "options": {')
    lines.append('        "baseURL": "http://localhost:20128/v1",')
    lines.append('        "apiKey": "{env:NINEROUTER_API_KEY}"')
    lines.append('      },')
    lines.append('      "models": {')
    for i, c in enumerate(combos):
        comma = "," if i < len(combos) - 1 else ""
        lines.append(f'        "{c["key"]}": {{ "name": "{c["name"]}" }}{comma}')
    lines.append('      }')
    lines.append('    },')
    lines.append('    "nvidia": {')
    lines.append('      "npm": "@ai-sdk/openai-compatible",')
    lines.append('      "name": "Nvidia Direct",')
    lines.append('      "env": ["NVIDIA_API_KEY"],')
    lines.append('      "options": {')
    lines.append('        "baseURL": "https://integrate.api.nvidia.com/v1",')
    lines.append('        "apiKey": "{env:NVIDIA_API_KEY}"')
    lines.append('      },')
    lines.append('      "models": {')
    lines.append('        "deepseek-ai/deepseek-v4-flash": { "name": "Nvidia Flash (40 RPM)" },')
    lines.append('        "deepseek-ai/deepseek-v4-pro": { "name": "Nvidia Pro (40 RPM)" }')
    lines.append('      }')
    lines.append('    }')
    return "\n".join(lines)


def sync_opencode():
    """Update opencode.jsonc provider section with combos + Nvidia."""
    combos = _load_db()
    new_provider = _generate_provider_block(combos)

    path = config.ROOT_DIR / "opencode.jsonc"
    content = path.read_text(encoding="utf-8")

    # Find provider section start and end
    # Match from "provider": { to the next key after the closing }
    start = content.find('"provider"')
    if start == -1:
        print("  [FAIL] Could not find 'provider' in opencode.jsonc")
        return False

    # Find the opening brace after "provider":
    brace_start = content.find('{', start)
    if brace_start == -1:
        print("  [FAIL] Could not find provider block")
        return False

    # Find the matching closing brace
    depth = 0
    brace_end = -1
    for i in range(brace_start, len(content)):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    if brace_end == -1:
        print("  [FAIL] Could not close provider block")
        return False

    new_section = f'"provider": {{\n{new_provider}\n  }}'
    new_content = content[:start] + new_section + content[brace_end + 1:]

    tmp = path.with_suffix(".jsonc.tmp")
    tmp.write_text(new_content, encoding="utf-8")
    tmp.replace(path)

    from .helpers import write_ok
    write_ok(f"opencode.jsonc synced: {len(combos)} combos + Nvidia")
    return True
