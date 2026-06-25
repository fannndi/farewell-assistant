import time
from . import config
from .helpers import get_gpu_info, write_info, write_skip
from .log import write_task_log


def check_gpu() -> dict:
    return get_gpu_info("name,memory.total,temperature.gpu")


def check_llm() -> bool:
    return config.GGUF_MODEL_PATH.exists()


def ping_model() -> list:
    results = []
    from .helpers import invoke_llm
    start = time.monotonic()
    r = invoke_llm("ping", max_tokens=1, timeout_sec=10)
    elapsed = round(time.monotonic() - start, 2)
    results.append({"ok": bool(r), "time": elapsed, "err": "" if r else "no response"})
    return results
