"""LLM configuration — dual-model download & status."""

import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from . import config
from .helpers import (
    get_gpu_info,
    read_json,
    write_fail,
    write_info,
    write_json,
    write_ok,
    write_skip,
    write_step,
)
from .log import sync_session_state, write_task_log
from .models import set_llm_mode, get_active_model_info


HF_REPOS = {
    "qwen3.5-0.8b": "bartowski/Qwen_Qwen3.5-0.8B-GGUF",
    "qwen3.5-2b": "unsloth/Qwen3.5-2B-GGUF",
}


def get_gguf_path(model_name: str = "") -> Path | None:
    info = get_active_model_info() if not model_name else config.MODEL_DEFS.get(model_name.split("-")[0] if "-" in model_name else model_name, config.MODEL_DEFS["online"])
    if model_name:
        # Find matching model def
        for key, md in config.MODEL_DEFS.items():
            if md["model_name"] == model_name or key == model_name:
                info = md
                break
    gguf = info["gguf_path"]
    return gguf if gguf.exists() else None


def invoke_download_gguf(llm_mode: str = "online") -> bool:
    model_def = config.MODEL_DEFS[llm_mode]
    out_dir = config.MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = model_def["gguf_path"]
    if out_file.exists():
        write_skip(f"GGUF already exists: {model_def['gguf_file']}")
        return True
    repo = HF_REPOS.get(model_def["model_name"])
    if not repo:
        write_fail(f"Unknown model: {model_def['model_name']}")
        return False
    url = f"https://huggingface.co/{repo}/resolve/main/{model_def['gguf_file']}"
    size_str = f"{model_def['vram_mb']/1024:.1f}GB"
    write_step("DOWNLOAD", f"Downloading {model_def['model_name']} ({model_def['gguf_file']}) ~{size_str}...")
    write_info(f"  URL: {url}")
    temp_file = Path(tempfile.gettempdir()) / model_def['gguf_file']
    try:
        proc = subprocess.run(["curl.exe", "-L", "-o", str(temp_file), url], shell=(platform.system() == "Windows"))
        if proc.returncode != 0 or not temp_file.exists():
            write_fail(f"Download failed (exit code: {proc.returncode})")
            return False
    except Exception as e:
        write_fail(f"Download failed: {e}")
        return False
    shutil.move(str(temp_file), str(out_file))
    write_ok(f"Downloaded to {out_file}")
    return True


def invoke_status():
    write_step("STATUS", "GPU Information...")
    gpu = get_gpu_info("name,memory.total,temperature.gpu")
    if gpu and gpu.get("available"):
        write_info(f"  Name: {gpu.get('name', '')}")
        write_info(f"  VRAM: {gpu.get('memory_total', 0)}MB")
        temp = gpu.get("temperature")
        if temp:
            write_info(f"  Temp: {temp}C")
    else:
        write_skip("No GPU detected")

    write_step("STATUS", "Models...")
    for mode_key, md in config.MODEL_DEFS.items():
        gguf = md["gguf_path"]
        if gguf.exists():
            size_gb = round(gguf.stat().st_size / (1024 ** 3), 2)
            active = "(active)" if md["model_name"] == get_active_model_info()["model_name"] else ""
            write_ok(f"  [{mode_key}] {md['model_name']} ({size_gb} GB) {active}")
        else:
            write_skip(f"  [{mode_key}] {md['model_name']} (not downloaded)")

    write_step("STATUS", "LLM Engine...")
    try:
        from llama_cpp import Llama
        write_ok("llama-cpp-python available")
    except ImportError:
        write_fail("llama-cpp-python not installed")


def invoke_remove(llm_mode: str = ""):
    write_step("REMOVE", "Removing GGUF model...")
    if llm_mode:
        targets = [config.MODEL_DEFS[llm_mode]]
    else:
        targets = list(config.MODEL_DEFS.values())
    for md in targets:
        gguf = md["gguf_path"]
        if gguf and gguf.exists():
            gguf.unlink()
            write_ok(f"Removed: {md['gguf_file']}")
        else:
            write_skip(f"Not found: {md['gguf_file']}")


def handle_llm_setup(action: str = "status", profile: str = ""):
    llm_mode = profile if profile in ("online", "offline") else "online"
    if action in ("pull", "download"):
        if invoke_download_gguf(llm_mode):
            set_llm_mode(llm_mode)
            model_name = config.MODEL_DEFS[llm_mode]["model_name"]
            write_ok(f"LLM ready: {model_name} ({llm_mode})")
    elif action == "status":
        invoke_status()
    elif action == "list":
        write_step("MODELS", "Available models:")
        for mode_key, md in config.MODEL_DEFS.items():
            gguf = md["gguf_path"]
            status = "Downloaded" if gguf.exists() else "Not downloaded"
            write_info(f"  [{mode_key}] {md['model_name']} ({md['description']}) — {status}")
    elif action == "remove":
        invoke_remove("online")
        invoke_remove("offline")
    else:
        write_step("LLM", "Usage: py -m farewell_assistant.cli llm [download|status|list|remove] [online|offline]")
        invoke_status()
