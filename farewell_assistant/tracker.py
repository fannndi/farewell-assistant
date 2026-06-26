"""Token tracker — read usage from 9Router SQLite + cost budget."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db():
    p = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if not p.exists():
        return None
    return sqlite3.connect(str(p))


def get_today_usage() -> dict:
    db = _db()
    if not db:
        return {"today": "0", "total": "0", "requests": 0, "today_input": 0, "today_output": 0}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cur = db.cursor()

    # Today from usageDaily
    cur.execute('SELECT data FROM usageDaily WHERE dateKey = ?', (today,))
    row = cur.fetchone()
    today_data = json.loads(row[0]) if row else {}

    # Total from usageHistory
    try:
        cur.execute('SELECT SUM(promptTokens), SUM(completionTokens) FROM usageHistory')
        total_row = cur.fetchone()
    except Exception:
        total_row = (0, 0)

    db.close()

    def fmt(n):
        if not n: return "0"
        n = int(n)
        if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        if n >= 1_000: return f"{n/1_000:.0f}K"
        return str(n)

    return {
        "today": fmt(today_data.get("promptTokens", 0) + today_data.get("completionTokens", 0)),
        "total": fmt((total_row[0] or 0) + (total_row[1] or 0)),
        "requests": today_data.get("requests", 0),
        "today_input": fmt(today_data.get("promptTokens", 0)),
        "today_output": fmt(today_data.get("completionTokens", 0)),
    }


def get_cost_status() -> dict:
    from .cost_tracker import get_cost_budget
    return get_cost_budget().status()


def sync_from_9router(limit: int = 500) -> int:
    """Sync recent usage from 9Router SQLite into CostBudget.
    Returns number of rows imported.
    """
    from .cost_tracker import get_cost_budget
    db = _db()
    if not db:
        return 0
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT model, promptTokens, completionTokens FROM usageHistory "
            "ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = [{"model": r[0], "prompt_tokens": r[1], "completion_tokens": r[2]} for r in cur.fetchall()]
        if rows:
            get_cost_budget().import_from_9router(rows)
        return len(rows)
    finally:
        db.close()
