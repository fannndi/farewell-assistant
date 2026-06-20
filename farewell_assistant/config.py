"""Centralized configuration - URLs, paths, constants, model routes."""

import os
from pathlib import Path

# Resolve project root from this file's location
ROOT_DIR = Path(__file__).resolve().parent.parent

# -- URLs (configurable via env vars) --
OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")
ROUTER_PORT = os.environ.get("ROUTER_PORT", "20128")
OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}"
API_URL = f"http://localhost:{ROUTER_PORT}"

# -- Directories --
ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
OPENCODE_DIR = Path(os.environ.get("USERPROFILE") or os.environ.get("HOME", "")) / ".config" / "opencode"
OPENCODE_CFG = OPENCODE_DIR / "opencode.jsonc"
MODELS_DIR = ROOT_DIR / "models"

# -- Data (project data, context, registry, skills) --
DATA_DIR = ROOT_DIR / "data"
PROJECT_CODE_DIR = DATA_DIR / "Code"
PROJECT_CONTEXT_DIR = DATA_DIR / "context"
PROJECT_SESSION_DIR = DATA_DIR / "session"
PROJECT_MEMORY_DIR = DATA_DIR / "memory"
PROJECT_SKILLS_DIR = DATA_DIR / "skills"

# -- Index / Registry --
REGISTRY_FILE = DATA_DIR / "registry.json"
SKILL_IDX_FILE = DATA_DIR / "skill-mode-index.json"
CONTEXT_DIR = PROJECT_CONTEXT_DIR  # alias for context lookups

# -- State Files --
STATE_DIR = ROOT_DIR / ".opencode"
LOG_DIR = STATE_DIR / "logs"
ROUTER_PID_FILE = STATE_DIR / "9router.pid"
LLM_MODE_FILE = STATE_DIR / "llm-mode.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
COMBO_FILE = STATE_DIR / "combo.json"
API_KEY_FILE = ROOT_DIR / "api-key.txt"
PROFILE_SRC = ROOT_DIR / "profiles" / "combo" / "opencode.jsonc"
PROFILE_LOG_DIR = ROOT_DIR / "profiles" / "logs"

# -- Logging --
LOG_FILE = ROOT_DIR / "logging.md"

# -- Helpers --

# -- Scheduled Task (cross-platform) --
TASK_NAME = "FarewellAssistant-9Router"

# -- Model Routing by Complexity --
MODEL_ROUTES = {
    "low":      {"primary": "Free", "secondary": "Free",   "heavy": "Free"},
    "medium":   {"primary": "Free", "secondary": "Free",   "heavy": "Free"},
    "high":     {"primary": "Free", "secondary": "Emergency", "heavy": "Emergency"},
    "critical": {"primary": "Emergency", "secondary": "Emergency", "heavy": "Emergency"},
}

# -- Enrichment Settings --
ENRICHMENT = {
    "min_words": 3,
    "max_tokens": 150,
    "temperature": 0.1,
    "timeout": 45,
    "cache_ttl": 3600,
}
