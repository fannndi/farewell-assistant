"""Direct Nvidia API client — bypass 9Router for Nvidia models."""

import json
from pathlib import Path
from .helpers import write_ok, write_skip, write_info, write_fail, _c

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODELS = {
    "deepseek-ai/deepseek-v4-flash": "Nvidia Flash (40 RPM)",
    "deepseek-ai/deepseek-v4-pro": "Nvidia Pro (40 RPM)",
}


def _load_api_key() -> str | None:
    """Read NVIDIA_API_KEY from api-key.txt."""
    try:
        for line in Path("api-key.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "NVIDIA_API_KEY":
                return v.strip()
    except Exception:
        pass
    return None


def check_health() -> dict:
    """Check Nvidia API key validity and RPM status."""
    import urllib.request
    api_key = _load_api_key()
    if not api_key:
        return {"ok": False, "reason": "No NVIDIA_API_KEY in api-key.txt"}
    try:
        payload = json.dumps({
            "model": "deepseek-ai/deepseek-v4-flash",
            "messages": [{"role": "user", "content": "p"}],
            "max_tokens": 1
        }).encode()
        req = urllib.request.Request(
            f"{NVIDIA_BASE_URL}/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        r = urllib.request.urlopen(req, timeout=8)
        if r.status == 200:
            return {"ok": True, "reason": "valid"}
        return {"ok": False, "reason": f"HTTP {r.status}"}
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {"ok": True, "reason": "RPM limited"}
        return {"ok": False, "reason": f"HTTP {e.code}"}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def chat_completion(model: str, messages: list[dict], max_tokens: int = 4096) -> dict:
    """Direct Nvidia API call."""
    import urllib.request
    api_key = _load_api_key()
    if not api_key:
        return {"ok": False, "error": "No NVIDIA_API_KEY"}
    try:
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens
        }).encode()
        req = urllib.request.Request(
            f"{NVIDIA_BASE_URL}/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST"
        )
        r = urllib.request.urlopen(req, timeout=30)
        resp = json.loads(r.read())
        return {"ok": True, "content": resp.get("choices", [{}])[0].get("message", {}).get("content", "")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def ping_all() -> dict:
    """Ping all Nvidia models to check availability."""
    results = {}
    for model in NVIDIA_MODELS:
        ok = False
        reason = ""
        try:
            import urllib.request
            api_key = _load_api_key()
            if not api_key:
                reason = "No API key"
            else:
                payload = json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": "p"}],
                    "max_tokens": 1
                }).encode()
                req = urllib.request.Request(
                    f"{NVIDIA_BASE_URL}/chat/completions",
                    data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    method="POST"
                )
                r = urllib.request.urlopen(req, timeout=8)
                ok = r.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ok = True
                reason = "RPM ok"
            else:
                reason = f"HTTP {e.code}"
        except Exception as e:
            reason = str(e)
            if "timed out" in reason.lower() or "timeout" in reason.lower():
                ok = True
                reason = "RPM limited (timeout)"
        results[model] = {"ok": ok, "reason": reason}
    return results
