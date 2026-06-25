"""Model loader — single GGUF instance via llama-cpp-python."""

import threading
import time

from . import config
from .helpers import estimate_tokens

_lock = threading.Lock()
_llama = None


def _unload():
    global _llama
    _llama = None


def get_llm():
    global _llama
    if _llama is not None:
        return _llama

    with _lock:
        if _llama is not None:
            return _llama
        gguf_path = config.GGUF_MODEL_PATH
        if not gguf_path.exists():
            return None
        try:
            from llama_cpp import Llama
            _llama = Llama(
                model_path=str(gguf_path),
                n_ctx=config.GGUF_N_CTX,
                n_gpu_layers=config.GGUF_N_GPU_LAYERS,
                verbose=False,
            )
            return _llama
        except Exception as e:
            try:
                from .log import write_task_log
                write_task_log("MODELS", f"Failed to load GGUF: {e}", "fail")
            except Exception:
                pass
            return None


def invoke_llm(
    prompt: str,
    system: str = "You are a helpful assistant.",
    model: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout_sec: int = 60,
) -> dict | None:
    llm = get_llm()
    if not llm:
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        start = time.monotonic()
        output = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        elapsed = time.monotonic() - start

        content = output["choices"][0]["message"]["content"]
        if content:
            tokens = output.get("usage", {}).get("completion_tokens") or estimate_tokens(content)
            tps = round(tokens / elapsed, 2) if elapsed > 0 else 0
            return {
                "response": content,
                "tokens": tokens,
                "duration": elapsed,
                "tokens_per_second": tps,
            }
    except Exception as e:
        try:
            from .log import write_task_log
            write_task_log("MODELS", f"invoke_llm failed: {e}", "fail")
        except Exception:
            pass
    return None
