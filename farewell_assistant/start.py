"""Startup — 9Router health check + start if needed."""
import os
import socket
import subprocess
import time
from pathlib import Path
from . import config
from .helpers import write_ok, write_skip
def _ensure_static_files(router_dir: Path):
    standalone = router_dir / ".next" / "standalone"
    if not standalone.exists():
        return
    src = router_dir / ".next" / "static"
    dst = standalone / "public" / "_next" / "static"
    if src.exists():
        dst.mkdir(parents=True, exist_ok=True)
        subprocess.run(["robocopy", str(src), str(dst), "/E", "/NJH", "/NJS", "/NDL", "/NP"],
                      capture_output=True, text=True, timeout=30)
def ensure_9router() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()
    if result == 0:
        write_ok("9Router is running (port 20128)")
        return True
    router_dir = config.ROUTER_DIR
    _ensure_static_files(router_dir)
    write_skip("9Router not running - starting...")
    standalone = router_dir / ".next" / "standalone"
    try:
        env_file = router_dir / ".env"
        data_dir = str(Path(os.environ.get("APPDATA", "")) / "9router")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DATA_DIR="): data_dir = line.split("=", 1)[1].strip(); break
        env = {"PORT": "20128", "NODE_ENV": "production", "DATA_DIR": data_dir, "INITIAL_PASSWORD": "123456"}
        node_cmd = ["node", str(standalone / "server.js")] if standalone.exists() else ["npx", "next", "start", "-p", "20128"]
        proc = subprocess.Popen(node_cmd, cwd=str(router_dir), env={**os.environ, **env},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            time.sleep(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1)
            try:
                if s.connect_ex(("127.0.0.1", 20128)) == 0:
                    write_ok(f"9Router started (PID: {proc.pid})")
                    pid_file = config.ROOT_DIR / ".opencode" / "9router.pid"
                    pid_file.parent.mkdir(parents=True, exist_ok=True); pid_file.write_text(str(proc.pid))
                    s.close(); return True
            finally: s.close()
        write_skip("9Router start timed out (30s)")
    except Exception as e: write_skip(f"9Router start failed: {e}")
    return False

