"""9Router diagnostic — check combo config, usage, and settings.

Usage:
  py scripts/9router-diagnostic.py [--fix]

Without --fix: read-only check.
With --fix: ensure Free combo has round-robin + stickyLimit=1.
"""

import sqlite3, os, json, sys

DB = os.path.join(os.environ.get("APPDATA", ""), "9router", "db", "data.sqlite")

def db():
    if not os.path.exists(DB):
        print(f"[FAIL] Database not found: {DB}")
        return None
    return sqlite3.connect(DB)


def check():
    conn = db()
    if not conn: return
    cur = conn.cursor()

    # Combos
    cur.execute("SELECT name, kind, models FROM combos")
    print("=== COMBOS ===")
    for r in cur.fetchall():
        models = json.loads(r[2]) if isinstance(r[2], str) else r[2]
        print(f"  {r[0]:25s} kind={r[1] or '-':15s} models={len(models)}")

    # Settings
    cur.execute("SELECT data FROM settings LIMIT 1")
    data = json.loads(cur.fetchone()[0])
    print(f"\n=== SETTINGS ===")
    print(f"  comboStrategy:           {data.get('comboStrategy')}")
    print(f"  fallbackStrategy:       {data.get('fallbackStrategy')}")
    print(f"  comboStickyRoundRobin:  {data.get('comboStickyRoundRobinLimit')}")
    for name, strat in data.get("comboStrategies", {}).items():
        print(f"  comboStrategies.{name}: {json.dumps(strat)}")

    # Usage today
    today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT data FROM usageDaily WHERE dateKey = ?", (today,))
    row = cur.fetchone()
    if row:
        d = json.loads(row[0])
        by_model = d.get("byModel", {})
        total_req = sum(v.get("count", 0) if isinstance(v, dict) else v for v in by_model.values())
        print(f"\n=== TODAY ({today}) ===")
        print(f"  Total requests: {total_req}")
        for m, info in sorted(by_model.items(), key=lambda x: -(x[1].get("count", 0) if isinstance(x[1], dict) else x[1])):
            c = info.get("count", 0) if isinstance(info, dict) else info
            print(f"  {m:50s} {c:>6} req")
    conn.close()


def fix():
    conn = db()
    if not conn: return
    cur = conn.cursor()

    cur.execute("SELECT data FROM settings LIMIT 1")
    data = json.loads(cur.fetchone()[0])

    # Ensure Free combo has round-robin strategy
    if "comboStrategies" not in data:
        data["comboStrategies"] = {}
    data["comboStrategies"]["Free"] = {
        "fallbackStrategy": "round-robin",
        "stickyRoundRobinLimit": 1
    }
    data["comboStickyRoundRobinLimit"] = 1
    data["comboStrategy"] = "round-robin"

    cur.execute("UPDATE settings SET data = ?", (json.dumps(data),))
    conn.commit()
    conn.close()
    print("[OK] Free combo strategy set to round-robin + stickyLimit=1")


if __name__ == "__main__":
    if "--fix" in sys.argv:
        check()
        print()
        fix()
    else:
        check()
