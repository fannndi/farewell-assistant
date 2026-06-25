"""Centralized configuration — minimal. 9Router handle all models."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
DATA_DIR = ROOT_DIR / "data"
STATE_DIR = ROOT_DIR / ".opencode"
LOG_DIR = STATE_DIR / "logs"
PROJECT_CONTEXT_DIR = DATA_DIR / "context"
PROJECT_SKILLS_DIR = DATA_DIR / "skills"
REGISTRY_FILE = DATA_DIR / "registry.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
LOG_FILE = ROOT_DIR / "logging.md"
SESSION_LOG_FILE = ROOT_DIR / "session-log.md"
