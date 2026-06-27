"""Cache-hit ratio logger — reads 9Router SQLite, no source patches needed."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db_path() -> Path | None:
    p = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    return p if p.exists() else None


def get_recent_requests(hours: int = 24) -> list[dict]:
    db = _db_path()
    if not db:
        return []
    try:
        conn = sqlite3.connect(str(db))
        cur = conn.execute(
            "SELECT timestamp, provider, model, connectionId, data FROM requestDetails WHERE datetime(timestamp) >= datetime('now', ?)",
            (f"-{hours} hours",),
        )
        rows = []
        for row in cur.fetchall():
            item = {"timestamp": row[0], "provider": row[1], "model": row[2], "connectionId": row[3]}
            try:
                item.update(json.loads(row[4]).get("tokens", {}))
            except Exception:
                pass
            rows.append(item)
        conn.close()
        return rows
    except Exception:
        return []


def print_cache_report(rows: list[dict]):
    if not rows:
        print("  No request data available.")
        return
    total = len(rows)
    providers = {}
    for r in rows:
        prov = r.get("provider", "?")
        if prov not in providers:
            providers[prov] = {"requests": 0, "prompt": 0, "completion": 0, "cached": 0}
        providers[prov]["requests"] += 1
        providers[prov]["prompt"] += r.get("prompt_tokens", 0)
        providers[prov]["completion"] += r.get("completion_tokens", 0)
        providers[prov]["cached"] += r.get("cached_tokens", 0)

    print(f"\n  Cache Report — {len(rows)} requests (last 24h)")
    print(f"  {'Provider':<20} {'Req':>5} {'Cached':>8} {'Ratio':>7}")
    print(f"  {'-'*20} {'-'*5} {'-'*8} {'-'*7}")
    for prov, d in sorted(providers.items()):
        ratio = d["cached"] / max(d["prompt"], 1)
        print(f"  {prov:<20} {d['requests']:>5} {d['cached']:>8} {ratio:>6.1%}")
