"""LLM configuration — single model Qwen3.5-0.8B."""

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

MODEL = "qwen3.5-0.8b"
HF_REPO = "bartowski/Qwen_Qwen3.5-0.8B-GGUF"
HF_FILE = "Qwen_Qwen3.5-0.8B-Q8_0.gguf"
SIZE_GB = 0.85


def get_gguf_path() -> Path | None:
    gguf = config.MODELS_DIR / HF_FILE
    return gguf if gguf.exists() else None


def set_llm_mode():
    state = {"mode": "on", "model": MODEL, "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")}
    write_json(config.LLM_MODE_FILE, state)
    try:
        from .enrichment_pipeline import clear_intent_cache
        clear_intent_cache()
    except Exception:
        pass
    sync_session_state()
    write_task_log("LLM", f"Set model: {MODEL}", "success")


def invoke_download_gguf() -> bool:
    out_dir = config.MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / HF_FILE
    if out_file.exists():
        write_skip(f"GGUF already exists: {HF_FILE}")
        return True
    url = f"https://huggingface.co/{HF_REPO}/resolve/main/{HF_FILE}"
    write_step("DOWNLOAD", f"Downloading {MODEL} ({HF_FILE}) ~{SIZE_GB}GB...")
    write_info(f"  URL: {url}")
    temp_file = Path(tempfile.gettempdir()) / HF_FILE
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
    write_step("STATUS", "GGUF Model...")
    gguf = get_gguf_path()
    if gguf:
        size_gb = round(gguf.stat().st_size / (1024 ** 3), 2)
        write_ok(f"{HF_FILE} ({size_gb} GB)")
    else:
        write_skip(f"{HF_FILE} not found")
    write_step("STATUS", "LLM Engine...")
    try:
        from llama_cpp import Llama
        write_ok("llama-cpp-python available")
    except ImportError:
        write_fail("llama-cpp-python not installed")


def invoke_remove():
    write_step("REMOVE", "Removing GGUF model...")
    gguf = get_gguf_path()
    if gguf:
        from .models import get_llm
        gguf.unlink()
        write_ok(f"Removed: {HF_FILE}")
    else:
        write_skip("No GGUF to remove")


def handle_llm_setup(action: str = "status", profile: str = ""):
    if action in ("pull", "download"):
        if invoke_download_gguf():
            set_llm_mode()
            write_ok(f"LLM ready: {MODEL}")
    elif action == "status":
        invoke_status()
    elif action == "list":
        write_step("MODEL", f"Active: {MODEL} ({HF_FILE}, ~{SIZE_GB}GB)")
        gguf = get_gguf_path()
        write_info(f"  GGUF: {'Downloaded' if gguf else 'Not downloaded'}")
    elif action == "remove":
        invoke_remove()
    else:
        write_step("LLM", f"Current model: {MODEL}")
        invoke_status()
