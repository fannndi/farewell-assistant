"""Centralized configuration."""

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
MODELS_DIR = ROOT_DIR / "models"
DATA_DIR = ROOT_DIR / "data"
STATE_DIR = ROOT_DIR / ".opencode"
LOG_DIR = STATE_DIR / "logs"
PROJECT_CONTEXT_DIR = DATA_DIR / "context"
PROJECT_SKILLS_DIR = DATA_DIR / "skills"
LLM_DIR = DATA_DIR / "llm"

REGISTRY_FILE = DATA_DIR / "registry.json"
SKILL_IDX_FILE = DATA_DIR / "skill-mode-index.json"
LLM_MODE_FILE = STATE_DIR / "llm-mode.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
COMBO_FILE = STATE_DIR / "combo.json"

LOG_FILE = ROOT_DIR / "logging.md"
SESSION_LOG_FILE = ROOT_DIR / "session-log.md"

# Offline execution paths
OFFLINE_DIR = STATE_DIR / "offline"
OFFLINE_TASK_FILE = OFFLINE_DIR / "task.json"
OFFLINE_RESULT_FILE = OFFLINE_DIR / "result.json"
OFFLINE_STATE_FILE = OFFLINE_DIR / "state.json"

# Dual-model config (online=0.8B enrichment, offline=2B execution)
MODEL_ONLINE_NAME = "Qwen_Qwen3.5-0.8B-Q8_0.gguf"
MODEL_ONLINE_PATH = MODELS_DIR / MODEL_ONLINE_NAME
MODEL_ONLINE_CTX = 4096
MODEL_ONLINE_VRAM = 1358

MODEL_OFFLINE_NAME = "Qwen3.5-2B-Q4_K_M.gguf"
MODEL_OFFLINE_PATH = MODELS_DIR / MODEL_OFFLINE_NAME
MODEL_OFFLINE_CTX = 16384
MODEL_OFFLINE_VRAM = 1500

GGUF_N_GPU_LAYERS = 99  # Vulkan GPU acceleration

ENRICHMENT = {
    "min_words": 2,
    "max_tokens": 150,
    "temperature": 0.1,
    "timeout": 25,
    "cache_ttl": 3600,
}

# Model definitions
MODEL_DEFS = {
    "online": {
        "label": "Online",
        "model_name": "qwen3.5-0.8b",
        "gguf_file": MODEL_ONLINE_NAME,
        "gguf_path": MODEL_ONLINE_PATH,
        "n_ctx": MODEL_ONLINE_CTX,
        "vram_mb": MODEL_ONLINE_VRAM,
        "description": "0.8B — enrichment only",
    },
    "offline": {
        "label": "Offline",
        "model_name": "qwen3.5-2b",
        "gguf_file": MODEL_OFFLINE_NAME,
        "gguf_path": MODEL_OFFLINE_PATH,
        "n_ctx": MODEL_OFFLINE_CTX,
        "vram_mb": MODEL_OFFLINE_VRAM,
        "description": "2B — enrichment + execution",
    },
}
