"""Check 9Router models — list all available models."""
import http.client, json

KEY = "sk-5aeb03e2d6fefe6e-oedccr-a35926e4"

conn = http.client.HTTPConnection("localhost", 20128, timeout=5)
conn.request("GET", "/v1/models", headers={"Authorization": "Bearer " + KEY})
res = conn.getresponse()
data = json.loads(res.read().decode())
print(f"Status: {res.status} | {len(data.get('data',[]))} models\n")
for m in data.get("data", []):
    combo = m.get("combo", {}) or {}
    strat = combo.get("strategy", combo.get("fallbackStrategy", "-"))
    layers = len(combo.get("layers", []))
    owned = m.get("owned_by", "")
    kind = "(combo)" if owned == "combo" else ""
    print(f"  {m['id']:30s} {kind:8s} strat={strat:15s} layers={layers}")
