"""Structured task logging to logging.md."""

from datetime import datetime, timezone
from . import config

def write_task_log(stage: str, action: str, result: str = "success", files: str = ""):
    try:
        log_file = config.LOG_FILE
        if not log_file.exists():
            log_file.write_text("# Logging\n", encoding="utf-8")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
        files_part = f" | FILES: {files}" if files else ""
        entry = f"[{ts}] STAGE: {stage} | ACTION: {action} | RESULT: {result}{files_part}\n"
        with open(log_file, "a", encoding="utf-8") as f: f.write(entry)
    except Exception:
        import sys
        print(f"[LOGGING ERROR] {config.LOG_FILE}", file=sys.stderr)
