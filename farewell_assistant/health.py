import time
import httpx
from . import config
from .helpers import (
    get_9router_pid,
    get_gpu_info,
    test_ollama_running,
    start_9router,
    start_ollama_service,
    get_llm_mode,
    parse_api_key,
    write_info,
    write_skip,
)
from .log import write_task_log


def ensure_9router() -> bool:
    pid = get_9router_pid()
    if pid:
        return True
    write_info("9Router not running, attempting start...")
    ok = start_9router()
    if ok:
        write_task_log("HEALTH", "ensure_9router", "started", "9router")
    else:
        write_task_log("HEALTH", "ensure_9router", "fail", "9router")
    return ok


def ensure_ollama() -> bool:
    mode = get_llm_mode()
    if mode == "eco":
        write_skip("Ollama check skipped (eco mode)")
        return True
    if test_ollama_running():
        return True
    write_info("Ollama not running, attempting start...")
    ok = start_ollama_service()
    if ok:
        write_task_log("HEALTH", "ensure_ollama", "started", "ollama")
    else:
        write_task_log("HEALTH", "ensure_ollama", "fail", "ollama")
    return ok


def check_gpu() -> dict:
    return get_gpu_info("name,memory.total,temperature.gpu")


def ping_models() -> list:
    results = []
    api_key, combo_entries, combo_models = parse_api_key()
    if not api_key or not combo_entries:
        return results

    pid = get_9router_pid()
    if not pid:
        return results

    for idx, entry in sorted(combo_entries.items()):
        combo = entry.get("combo", "")
        models = combo_models.get(idx, {}).get("models", [])
        for model in models:
            result = {
                "combo": combo,
                "model": model,
                "ok": False,
                "code": 0,
                "time": 0.0,
                "err": "",
            }
            try:
                start = time.monotonic()
                r = httpx.post(
                    f"{config.API_URL}/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 1,
                    },
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10,
                )
                elapsed = round(time.monotonic() - start, 2)
                result["ok"] = r.status_code == 200
                result["code"] = r.status_code
                result["time"] = elapsed
                if r.status_code != 200:
                    result["err"] = r.text[:200]
            except Exception as e:
                result["err"] = str(e)[:200]
            results.append(result)
    return results


def check_standalone_build() -> bool:
    server_js = config.ROUTER_DIR / ".next" / "standalone" / "server.js"
    return server_js.exists()
