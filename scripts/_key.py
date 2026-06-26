"""Shared helper — read 9Router API key."""
from pathlib import Path

def get_key():
    key_file = Path(__file__).resolve().parent.parent / "api-key.txt"
    for line in key_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("NINEROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""
