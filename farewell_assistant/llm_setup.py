"""LLM configuration - profiles, modes, GGUF download, Ollama import, GPU detection."""

import os
import platform
import shutil
import subprocess
from collections import OrderedDict
from pathlib import Path

from . import config
from .helpers import (
    get_gpu_info,
    get_llm_mode,
    read_json,
    start_ollama_service,
    stop_ollama_models,
    test_ollama_running,
    write_fail,
    write_info,
    write_json,
    write_ok,
    write_skip,
    write_step,
)
from .log import sync_session_state, write_task_log

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

PROFILES = OrderedDict({
    "hot": {
        "model": "qwen3.5-0.8b",
        "vram": "~600MB",
        "condition": "Outdoor, unplugged, high temp",
        "hf_repo": "unsloth/Qwen3.5-0.8B-GGUF",
        "hf_file": "Qwen3.5-0.8B-Q4_K_M.gguf",
        "modelfile": str(config.ROOT_DIR / "Modelfile.qwen3.5-0.8b"),
        "size_gb": 0.5,
    },
    "eco": {
        "model": "qwen2.5-coder-1.5b",
        "vram": "~1GB",
        "condition": "Indoor, unplugged",
        "hf_repo": "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "hf_file": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "modelfile": str(config.ROOT_DIR / "Modelfile.qwen2.5-coder-1.5b"),
        "size_gb": 1.0,
    },
    "balance": {
        "model": "qwen3.5-2b",
        "vram": "~1.4GB",
        "condition": "Indoor, plugged, AC",
        "hf_repo": "unsloth/Qwen3.5-2B-GGUF",
        "hf_file": "Qwen3.5-2B-Q4_K_M.gguf",
        "modelfile": str(config.ROOT_DIR / "Modelfile.qwen3.5-2b"),
        "size_gb": 1.4,
    },
    "performance": {
        "model": "qwen3.5-4b",
        "vram": "~2.5GB",
        "condition": "Indoor, plugged, fan active",
        "hf_repo": "unsloth/Qwen3.5-4B-GGUF",
        "hf_file": "Qwen3.5-4B-Q4_K_M.gguf",
        "modelfile": str(config.ROOT_DIR / "Modelfile.qwen3.5-4b"),
        "size_gb": 2.5,
    },
})

VRAM_MAP = OrderedDict({
    "hot": 600,
    "eco": 1024,
    "balance": 1433,
    "performance": 2560,
})

MODEL_MAP = OrderedDict({
    "eco": "qwen2.5-coder-1.5b",
    "on": "qwen2.5-coder-1.5b",
    "hot": "qwen3.5-0.8b",
    "balance": "qwen3.5-2b",
    "performance": "qwen3.5-4b",
})


# ---------------------------------------------------------------------------
# Set LLM Mode
# ---------------------------------------------------------------------------

def set_llm_mode(mode: str):
    state = read_json(config.LLM_MODE_FILE, default={})
    if state is None:
        state = {}
    state["mode"] = mode
    from datetime import datetime, timezone
    state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    model = MODEL_MAP.get(mode)
    if model:
        state["model"] = model
    write_json(config.LLM_MODE_FILE, state)
    try:
        sync_session_state()
    except Exception:
        pass
    write_task_log("LLM", "Set mode to " + mode, "success")


# ---------------------------------------------------------------------------
# GGUF Path
# ---------------------------------------------------------------------------

def get_gguf_path(profile_name: str) -> Path | None:
    p = PROFILES.get(profile_name)
    if not p:
        return None
    return config.MODELS_DIR / p["hf_file"]


# ---------------------------------------------------------------------------
# Modelfile Content
# ---------------------------------------------------------------------------

def get_modelfile_content(profile_name: str, gguf_relative: str) -> str:
    p = PROFILES.get(profile_name)
    if not p:
        return ""

    template_path = Path(p["modelfile"])
    if template_path.is_file():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace(".gguf", gguf_relative)
        return content

    # Default Modelfile template (Ollama syntax uses double braces)
    # Build via concatenation to avoid f-string curly-brace escaping issues
    LBRACE = "{"
    RBRACE = "}"
    LS = LBRACE + LBRACE
    RS = RBRACE + RBRACE

    lines = [
        "FROM " + gguf_relative,
        'TEMPLATE "' + LS + " if .System " + RS + "<|im_start|>system",
        RS + LS + " end " + RS + LS + " if .Prompt " + RS + "<|im_start|>user",
        RS + LS + " end " + RS + "<|im_start|>assistant",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Download GGUF from HuggingFace
# ---------------------------------------------------------------------------

def invoke_download_gguf(profile_name: str) -> bool:
    p = PROFILES.get(profile_name)
    if not p:
        write_fail("Unknown profile '" + profile_name + "'")
        return False

    out_dir = config.MODELS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / p["hf_file"]
    if out_file.exists():
        write_skip("GGUF already exists: " + p["hf_file"])
        return True

    url = "https://huggingface.co/" + p["hf_repo"] + "/resolve/main/" + p["hf_file"]
    write_step("DOWNLOAD", "Downloading " + p["model"] + " (" + p["hf_file"] + ")...")
    write_info("  URL: " + url)
    write_info("  Size: ~" + str(p["size_gb"]) + "GB")

    temp_file = Path(tempfile.gettempdir()) / p["hf_file"]
    try:
        proc = subprocess.run(
            ["curl.exe", "-L", "-o", str(temp_file), url],
            shell=(platform.system() == "Windows"),
        )
        if proc.returncode != 0 or not temp_file.exists():
            write_fail("Download failed (exit code: " + str(proc.returncode) + ")")
            return False
    except Exception as e:
        write_fail("Download failed: " + str(e))
        return False

    shutil.move(str(temp_file), str(out_file))
    write_ok("Downloaded to " + str(out_file))
    return True


# ---------------------------------------------------------------------------
# Import to Ollama
# ---------------------------------------------------------------------------

def invoke_import_ollama(profile_name: str) -> bool:
    p = PROFILES.get(profile_name)
    if not p:
        write_fail("Unknown profile '" + profile_name + "'")
        return False

    gguf_path = get_gguf_path(profile_name)
    if not gguf_path or not gguf_path.exists():
        write_fail("GGUF not found: " + str(gguf_path))
        return False

    existing = subprocess.run(
        ["ollama", "list"],
        capture_output=True, text=True,
    )
    if p["model"] in existing.stdout:
        write_skip("Model '" + p["model"] + "' already exists in Ollama")
        return True

    write_step("IMPORT", "Importing " + p["model"] + " into Ollama...")

    gguf_relative = ".\\models\\" + p["hf_file"]
    modelfile_content = get_modelfile_content(profile_name, gguf_relative)

    modelfile_path = Path(tempfile.gettempdir()) / ("Modelfile." + p["model"])
    modelfile_path.write_text(modelfile_content, encoding="utf-8")

    proc = subprocess.run(
        ["ollama", "create", p["model"], "-f", str(modelfile_path)],
        shell=(platform.system() == "Windows"),
    )
    modelfile_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        write_fail("Import failed (exit code: " + str(proc.returncode) + ")")
        return False

    write_ok("Imported '" + p["model"] + "' into Ollama")
    return True


# ---------------------------------------------------------------------------
# Auto Mode Detection
# ---------------------------------------------------------------------------

def invoke_auto_mode():
    write_step("AUTO", "Detecting GPU hardware...")
    gpu_info = get_gpu_info("name,memory.total,temperature.gpu")

    if not gpu_info or (not gpu_info.get("name") and not gpu_info.get("memory_total")):
        write_fail("No GPU detected")
        write_step("AUTO", "Setting mode to eco (no LLM)...")
        set_llm_mode("eco")
        write_ok("[MODE] ECO - no LLM, zero GPU usage")
        return

    write_info("  GPU: " + str(gpu_info.get("name", "")))
    vram_mb = gpu_info.get("memory_total", 0)
    write_info("  VRAM: ~" + str(vram_mb) + "MB")

    temp = gpu_info.get("temperature")
    if temp:
        write_info("  Temp: " + str(temp) + "C")

    if vram_mb < 1024:
        recommendation = "hot"
        label = "HOT - qwen3.5-0.8b, ~600MB VRAM"
    elif vram_mb < 2048:
        recommendation = "balance"
        label = "BALANCE - qwen3.5-2b, ~1.4GB VRAM"
    else:
        recommendation = "performance"
        label = "PERFORMANCE - qwen3.5-4b, ~2.5GB VRAM"

    write_info("Recommendation: " + recommendation)
    response = input("  Switch to " + recommendation + " profile? [y/N] ")
    if response.lower() == "y":
        downloaded = invoke_download_gguf(recommendation)
        if not downloaded:
            return
        imported = invoke_import_ollama(recommendation)
        if not imported:
            return
        write_step("AUTO", "Setting mode to " + recommendation + "...")
        set_llm_mode(recommendation)
        write_ok("[MODE] " + label)
    else:
        write_skip("Skipped profile switch")


# ---------------------------------------------------------------------------
# List Profiles
# ---------------------------------------------------------------------------

def invoke_list_profiles():
    write_step("PROFILES", "LLM Profiles")
    write_info("")

    ollama_list = ""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True,
        )
        ollama_list = result.stdout
    except Exception:
        pass

    for name, p in PROFILES.items():
        gguf_path = get_gguf_path(name)
        gguf_status = "Downloaded" if gguf_path and gguf_path.exists() else "Not downloaded"
        ollama_status = "Loaded" if p["model"] in ollama_list else "Not loaded"

        write_ok(name + " | " + p["model"] + " | " + p["vram"] + " | " + p["condition"])
        write_info("  GGUF: " + gguf_status + "  |  Ollama: " + ollama_status)

    gpu = get_gpu_info()
    if gpu and gpu.get("available"):
        write_info("GPU: " + str(gpu.get("name", "unknown")))


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def invoke_status():
    write_step("STATUS", "GPU Information...")
    gpu = get_gpu_info("name,memory.total,temperature.gpu")
    if gpu and gpu.get("available"):
        write_info("  Name: " + str(gpu.get("name", "")))
        write_info("  VRAM: " + str(gpu.get("memory_total", 0)) + "MB")
        temp = gpu.get("temperature")
        if temp:
            write_info("  Temp: " + str(temp) + "C")
    else:
        write_skip("No GPU detected")

    write_step("STATUS", "Ollama Service...")
    if test_ollama_running():
        write_ok("Ollama is running")
    else:
        write_skip("Ollama is not running")

    write_step("STATUS", "Loaded Models...")
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                write_info("  " + line)
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
                write_info("  " + f.name + " (" + str(size_gb) + " GB)")
        else:
            write_skip("No GGUF files")
    else:
        write_skip("No models directory")


# ---------------------------------------------------------------------------
# Remove All
# ---------------------------------------------------------------------------

def invoke_remove():
    write_step("REMOVE", "Removing all Ollama models...")
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True,
        )
        lines = result.stdout.strip().splitlines()
        start = 1 if lines and "NAME" in lines[0] else 0
        for line in lines[start:]:
            model_name = line.split()[0] if line.split() else ""
            if model_name:
                subprocess.run(["ollama", "rm", model_name], capture_output=True)
                write_ok("Removed model: " + model_name)
    except Exception:
        pass

    write_step("REMOVE", "Removing all GGUF files...")
    model_dir = config.MODELS_DIR
    if model_dir.is_dir():
        for f in model_dir.glob("*.gguf"):
            f.unlink()
        write_ok("Removed GGUF files from " + str(model_dir))
    else:
        write_skip("No models directory")


# ---------------------------------------------------------------------------
# Main Dispatch
# ---------------------------------------------------------------------------

def _warmup_mode(mode: str):
    """Common: ensure Ollama running → warm up model → set mode."""
    if not test_ollama_running():
        start_ollama_service()
    model = MODEL_MAP[mode]
    write_step("LLM", "Warming up " + model + "...")
    subprocess.run(["ollama", "run", model, ""], capture_output=True)
    set_llm_mode(mode)
    write_ok("[MODE] " + mode.upper() + " - " + model)


def handle_llm_setup(action: str = "status", profile: str = ""):
    if action == "eco":
        write_step("LLM", "Setting mode to eco...")
        set_llm_mode("eco")
        stop_ollama_models()
        write_ok("[MODE] ECO - no LLM, zero GPU usage")

    elif action == "on":
        if not test_ollama_running():
            start_ollama_service()
        model = MODEL_MAP["on"]
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True,
            )
            if model not in result.stdout:
                write_step("LLM", "Pulling default model " + model + "...")
                subprocess.run(["ollama", "pull", model], capture_output=True)
        except Exception:
            pass
        set_llm_mode("on")
        write_ok("[MODE] ON - LLM active, GPU-enabled")

    elif action in ("hot", "balance", "performance"):
        _warmup_mode(action)

    elif action == "list":
        invoke_list_profiles()

    elif action == "pull":
        if profile:
            if profile not in PROFILES:
                write_fail("Unknown profile '" + profile + "'. Valid: " + ", ".join(PROFILES.keys()))
                return
            write_step("LLM", "Downloading GGUF for " + profile + "...")
            if not invoke_download_gguf(profile):
                return
            write_step("LLM", "Importing to Ollama...")
            if not invoke_import_ollama(profile):
                return
            write_ok("Profile '" + profile + "' ready")
        else:
            for name in PROFILES:
                write_step("LLM", "Processing profile: " + name)
                if invoke_download_gguf(name):
                    invoke_import_ollama(name)
            write_ok("All profiles processed")

    elif action == "status":
        invoke_status()

    elif action == "remove":
        invoke_remove()

    elif action == "auto":
        invoke_auto_mode()
