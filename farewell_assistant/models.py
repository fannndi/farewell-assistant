"""Model Manager — dual-model (online 0.8B / offline 2B), single-loaded."""

import threading
import time
from pathlib import Path

from . import config
from .helpers import read_json, write_json, estimate_tokens

_lock = threading.Lock()
_current_model = None
_current_mode = None
_llama = None


def get_active_model_info() -> dict:
    """Return model def for current LLM mode (online/offline)."""
    state = read_json(config.LLM_MODE_FILE, default={"llm_mode": "online"})
    llm_mode = state.get("llm_mode", "online")
    return config.MODEL_DEFS.get(llm_mode, config.MODEL_DEFS["online"])


def set_llm_mode(llm_mode: str) -> bool:
    """Switch LLM mode (online/offline). Unloads current model, sets mode."""
    if llm_mode not in ("online", "offline"):
        return False
    state = read_json(config.LLM_MODE_FILE, default={"mode": "on", "model": "qwen3.5-0.8b"})
    model_def = config.MODEL_DEFS[llm_mode]
    state["llm_mode"] = llm_mode
    state["model"] = model_def["model_name"]
    write_json(config.LLM_MODE_FILE, state)
    _unload()
    return True


def _unload():
    """Unload current model from memory."""
    global _llama, _current_model, _current_mode
    _llama = None
    _current_model = None
    _current_mode = None


def get_llm():
    """Get current LLM instance (load if needed)."""
    global _llama, _current_model, _current_mode
    if _llama is not None:
        return _llama

    with _lock:
        if _llama is not None:
            return _llama
        model_info = get_active_model_info()
        gguf_path = model_info["gguf_path"]
        if not gguf_path.exists():
            return None
        try:
            from llama_cpp import Llama
            _llama = Llama(
                model_path=str(gguf_path),
                n_ctx=model_info["n_ctx"],
                n_gpu_layers=model_info["n_gpu_layers"],
                verbose=False,
            )
            _current_model = model_info["model_name"]
            _current_mode = model_info["label"]  # "Online" or "Offline"
            return _llama
        except Exception as e:
            try:
                from .log import write_task_log
                write_task_log("MODELS", f"Failed to load {model_info['gguf_file']}: {e}", "fail")
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
    """Call current LLM with given prompt."""
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


def get_current_llm_label() -> str:
    """Return current LLM mode label: 'Online' or 'Offline'."""
    model_info = get_active_model_info()
    return model_info["label"]
