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

# GGUF model config (llama-cpp-python)
GGUF_MODEL_NAME = "Qwen_Qwen3.5-0.8B-Q8_0.gguf"
GGUF_MODEL_PATH = MODELS_DIR / GGUF_MODEL_NAME
GGUF_N_CTX = 4096
GGUF_N_GPU_LAYERS = 99

ENRICHMENT = {
    "min_words": 2,
    "max_tokens": 150,
    "temperature": 0.1,
    "timeout": 25,
    "cache_ttl": 3600,
}
