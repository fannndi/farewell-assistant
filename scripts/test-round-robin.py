"""Test Free combo Round Robin — 5 requests with different messages."""
import http.client, json

KEY = "sk-5aeb03e2d6fefe6e-oedccr-a35926e4"

print("=== Same message (same session -> pinned model) ===")
for i in range(5):
    conn = http.client.HTTPConnection("localhost", 20128, timeout=30)
    body = json.dumps({"model": "Free", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 200, "stream": False})
    conn.request("POST", "/v1/chat/completions", body, {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    r = conn.getresponse()
    d = json.loads(r.read().decode())
    print(f"  Req {i+1}: {d.get('model','?')}")

print("\n=== Different messages (different session -> rotates) ===")
msgs = ["ping", "hello", "test", "check", "verify"]
for i, msg in enumerate(msgs):
    conn = http.client.HTTPConnection("localhost", 20128, timeout=30)
    body = json.dumps({"model": "Free", "messages": [{"role": "user", "content": msg}], "max_tokens": 200, "stream": False})
    conn.request("POST", "/v1/chat/completions", body, {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    r = conn.getresponse()
    d = json.loads(r.read().decode())
    print(f"  Req {i+1} ({msg:8s}): {d.get('model','?')}")
