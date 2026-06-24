import time
import httpx
from . import config
from .helpers import get_gpu_info, test_ollama_running, start_ollama_service, write_info, write_skip
from .log import write_task_log


def ensure_ollama() -> bool:
    if test_ollama_running():
        return True
    write_info("Ollama not running, attempting start...")
    ok = start_ollama_service()
    write_task_log("HEALTH", "ensure_ollama", "started" if ok else "fail", "ollama")
    return ok


def check_gpu() -> dict:
    return get_gpu_info("name,memory.total,temperature.gpu")


def ping_model() -> list:
    results = []
    from .helpers import invoke_llm
    start = time.monotonic()
    r = invoke_llm("ping", max_tokens=1, timeout_sec=10)
    elapsed = round(time.monotonic() - start, 2)
    results.append({"ok": bool(r), "time": elapsed, "err": "" if r else "no response"})
    return results
