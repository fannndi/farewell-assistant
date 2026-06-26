"""Centralized configuration — minimal. 9Router handle all models."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ECC_DIR = ROOT_DIR / "ecc"
ROUTER_DIR = ROOT_DIR / "9router"
STATE_DIR = ROOT_DIR / ".opencode"
FAREWELL_DIR = ROOT_DIR / ".farewell"
LOG_DIR = STATE_DIR / "logs"
PROJECT_CONTEXT_DIR = FAREWELL_DIR / "context"
PROJECT_SKILLS_DIR = FAREWELL_DIR / "custom-skills"
REGISTRY_FILE = FAREWELL_DIR / "registry.json"
WORK_MODE_FILE = STATE_DIR / "work-mode.json"
LOG_FILE = ROOT_DIR / "logging.md"
SESSION_LOG_FILE = ROOT_DIR / "session-log.md"
MEMORY_DIR = FAREWELL_DIR / "memory"
COST_BUDGET_FILE = FAREWELL_DIR / "cost-budget.json"
COST_LOG_FILE = FAREWELL_DIR / "cost-log.csv"
RATES_FILE = ROOT_DIR / "farewell_assistant" / "deepseek_rates.json"
