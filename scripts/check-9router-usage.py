"""Check 9Router token usage from SQLite."""
import sqlite3, os, json
from datetime import datetime, timezone

DB = os.path.join(os.environ.get("APPDATA", ""), "9router", "db", "data.sqlite")

if not os.path.exists(DB):
    print(f"[FAIL] Database not found: {DB}")
    exit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Today's usage
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
cur.execute("SELECT data FROM usageDaily WHERE dateKey = ?", (today,))
row = cur.fetchone()

if row:
    data = json.loads(row[0])
    print(f"=== TODAY ({today}) ===")
    print(f"  Requests:     {data.get('requests', 0)}")
    print(f"  Prompt tokens:{data.get('promptTokens', 0):,}")
    print(f"  Output tokens:{data.get('completionTokens', 0):,}")
    print(f"  Cost:         ${data.get('cost', 0):.6f}")
    print()

    by_model = data.get("byModel", {})
    print(f"  By model ({len(by_model)}):")
    for model, info in sorted(by_model.items(), key=lambda x: -(x[1].get("count", 0) if isinstance(x[1], dict) else x[1])):
        if isinstance(info, dict):
            c = info.get("count", 0)
            t = info.get("totalTokens", info.get("promptTokens", 0) + info.get("completionTokens", 0))
            print(f"    {model:50s} {c:>6} req ({t:>10,} tok)")
        else:
            print(f"    {model:50s} {info:>6} req")

# Total all time
cur.execute("SELECT SUM(promptTokens), SUM(completionTokens) FROM usageHistory")
total = cur.fetchone()
print(f"\n=== ALL TIME ===")
print(f"  Total tokens: {(total[0] or 0) + (total[1] or 0):,}")
print(f"  Prompt:       {total[0] or 0:,}")
print(f"  Output:       {total[1] or 0:,}")

conn.close()
