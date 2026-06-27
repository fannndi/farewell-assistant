import os
import sqlite3
import json
from pathlib import Path

db_path = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
print("Database exists:", db_path.exists())

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

print("\nTables:")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(f"  {row[0]}")

print("\nCombos table:")
for row in cur.execute("SELECT name, kind, models FROM combos"):
    print(f"  name: {row[0]}, kind: {row[1]}, models: {row[2][:100]}...")

conn.close()