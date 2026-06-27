"""Centralized configuration — minimal paths."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
STATE_DIR = ROOT_DIR / ".opencode"
FAREWELL_DIR = ROOT_DIR / ".farewell"
REGISTRY_FILE = FAREWELL_DIR / "registry.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
PROJECT_CONTEXT_DIR = FAREWELL_DIR / "context"
LOG_FILE = ROOT_DIR / "logging.md"
