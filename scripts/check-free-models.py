import http.client, json
from _key import get_key

KEY = get_key()

conn = http.client.HTTPConnection("localhost", 20128, timeout=5)
conn.request("GET", "/v1/models", headers={"Authorization": f"Bearer {KEY}"})
res = conn.getresponse()
data = json.loads(res.read().decode())
print(f"Status: {res.status}")
for m in data.get("data", []):
    combo = m.get("combo", {}) or {}
    strat = combo.get("strategy", combo.get("fallbackStrategy", "-"))
    layers = len(combo.get("layers", []))
    owned = m.get("owned_by", "")
    kind = "(combo)" if owned == "combo" else ""
    print(f"  {m['id']:35s} {kind:8s} strat={strat:15s} layers={len(combo.get('layers', []))}")
