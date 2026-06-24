"""LLM configuration — single-profile, always-on."""

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
    start_ollama_service,
    test_ollama_running,
    write_fail,
    write_info,
    write_json,
    write_ok,
    write_skip,
    write_step,
)
from .log import sync_session_state, write_task_log

MODEL = "qwen2.5-coder-1.5b"
HF_REPO = "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF"
HF_FILE = "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
SIZE_GB = 1.0


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


def invoke_import_ollama() -> bool:
    gguf_path = get_gguf_path()
    if not gguf_path:
        write_fail(f"GGUF not found: {HF_FILE}")
        return False
    existing = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if MODEL in existing.stdout:
        write_skip(f"Model '{MODEL}' already exists in Ollama")
        return True
    write_step("IMPORT", f"Importing {MODEL} into Ollama...")
    modelfile_path = Path(tempfile.gettempdir()) / f"Modelfile.{MODEL}"
    modelfile_path.write_text(f"FROM .\\models\\{HF_FILE}\n", encoding="utf-8")
    proc = subprocess.run(["ollama", "create", MODEL, "-f", str(modelfile_path)], shell=(platform.system() == "Windows"))
    modelfile_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        write_fail(f"Import failed (exit code: {proc.returncode})")
        return False
    write_ok(f"Imported '{MODEL}' into Ollama")
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
    write_step("STATUS", "Ollama Service...")
    write_ok("Ollama is running") if test_ollama_running() else write_skip("Ollama is not running")
    write_step("STATUS", "Loaded Models...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                write_info(f"  {line}")
        else:
            write_skip("No models loaded")
    except Exception:
        write_skip("No models loaded")
    write_step("STATUS", "GGUF Files...")
    model_dir = config.MODELS_DIR
    if model_dir.is_dir():
        ggufs = list(model_dir.glob("*.gguf"))
        if ggufs:
            for f in ggufs:
                size_gb = round(f.stat().st_size / (1024 ** 3), 2)
                write_info(f"  {f.name} ({size_gb} GB)")
        else:
            write_skip("No GGUF files")
    else:
        write_skip("No models directory")


def invoke_remove():
    write_step("REMOVE", "Removing Ollama models...")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        start = 1 if lines and "NAME" in lines[0] else 0
        for line in lines[start:]:
            model_name = line.split()[0] if line.split() else ""
            if model_name:
                subprocess.run(["ollama", "rm", model_name], capture_output=True)
                write_ok(f"Removed model: {model_name}")
    except Exception:
        pass


def handle_llm_setup(action: str = "status", profile: str = ""):
    if action in ("pull", "download"):
        if invoke_download_gguf():
            invoke_import_ollama()
            set_llm_mode()
            write_ok(f"LLM ready: {MODEL}")
    elif action == "status":
        invoke_status()
    elif action == "list":
        write_step("MODEL", f"Active: {MODEL} ({HF_FILE}, ~{SIZE_GB}GB)")
        gguf = get_gguf_path()
        write_info(f"  GGUF: {'Downloaded' if gguf else 'Not downloaded'}")
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            write_info(f"  Ollama: {'Loaded' if MODEL in result.stdout else 'Not loaded'}")
        except Exception:
            write_info("  Ollama: Not reachable")
    elif action == "remove":
        invoke_remove()
    else:
        write_step("LLM", f"Current model: {MODEL}")
        invoke_status()
