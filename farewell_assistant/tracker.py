"""Token usage — read 9Router SQLite combo stats."""

import json
import os
import sqlite3
from pathlib import Path


def get_totals() -> dict:
    db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if not db.exists():
        return {"error": "9Router DB not found"}
    try:
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        combos = []
        total_models = 0
        for row in cur.fetchall():
            models = json.loads(row[2]) if row[2] else []
            cnt = len(models)
            if cnt:
                combos.append(row[0])
                total_models += cnt
        conn.close()
        return {"total_combos": len(combos), "total_models": total_models}
    except Exception as e:
        return {"error": str(e)}


def get_combo_details() -> dict:
    db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if not db.exists():
        return {"error": "9Router DB not found"}
    try:
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        combos = []
        for row in cur.fetchall():
            models = json.loads(row[2]) if row[2] else []
            if models:
                combos.append({"name": row[0], "kind": row[1] or "round-robin", "models": models})
        conn.close()
        return {"combos": combos, "total": len(combos)}
    except Exception as e:
        return {"error": str(e)}