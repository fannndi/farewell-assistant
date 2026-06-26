"""Proof: Team ON vs Team OFF produce DIFFERENT model traffic.
Team ON  → Deepseek-GO-Flash → instructor model
Team OFF → Free Round Robin  → 5 free models rotating
"""
import http.client, json, sqlite3, os, time
from pathlib import Path

KEY_FILE = Path(__file__).resolve().parent.parent / "api-key.txt"
KEY = ""
for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
    if line.startswith("NINEROUTER_API_KEY="):
        KEY = line.split("=", 1)[1].strip()
        break

DB = os.path.join(os.environ.get("APPDATA", ""), "9router", "db", "data.sqlite")

def send(model, msg):
    conn = http.client.HTTPConnection("localhost", 20128, timeout=30)
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": msg}], "max_tokens": 200, "stream": False})
    conn.request("POST", "/v1/chat/completions", body, {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    r = conn.getresponse()
    d = json.loads(r.read().decode())
    return d.get("model", "?")

print("TEAM ON: Deepseek-GO-Flash (instructor)")
print("-" * 50)
on_models = []
for i in range(3):
    m = send("Deepseek-GO-Flash", f"ping-on {i}")
    on_models.append(m)
    print(f"  Req {i+1}: {m}")

time.sleep(1)

print("\nTEAM OFF: Free Round Robin (executors)")
print("-" * 50)
off_models = []
msgs = ["ping-a", "ping-b", "ping-c", "ping-d", "ping-e"]
for i, msg in enumerate(msgs):
    m = send("Free", f"ping-off-{msg}")
    off_models.append(m)
    print(f"  Req {i+1}: {m}")

time.sleep(1)

print("\n=== VERDICT ===")
on_unique = set(on_models)
off_unique = set(off_models)
print(f"  Team ON models:  {len(on_unique)} unique ({', '.join(on_unique)})")
print(f"  Team OFF models: {len(off_unique)} unique ({', '.join(off_unique)})")
if on_unique != off_unique:
    print("\n  [PASS] Team ON and OFF use DIFFERENT models.")
else:
    print("\n  [FAIL] Both use same models — something wrong.")
