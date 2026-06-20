"""Cross-platform autostart manager — Scheduled Tasks (Windows), systemd user service (Linux)."""

import os
import platform
import subprocess
from pathlib import Path
from . import config
from .helpers import get_9router_pid, read_json, write_info, write_ok, write_skip, write_fail, write_step
from .log import write_task_log


def _get_task_name() -> str:
    return config.TASK_NAME


def _get_router_health() -> bool:
    import httpx
    try:
        r = httpx.get(f"{config.API_URL}/api/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _enable_windows() -> bool:
    name = _get_task_name()
    # Use Python CLI directly - finds py.exe or falls back to python
    py_cmd = "py -m farewell_assistant.cli start"
    cmd = [
        "schtasks", "/Create",
        "/SC", "ONLOGON",
        "/TN", name,
        "/TR", py_cmd,
        "/DELAY", "0000:30",
        "/IT",
        "/RL", "LIMITED",
        "/F",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
    except subprocess.CalledProcessError as e:
        write_fail(f"schtasks /Create failed: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        write_fail(f"schtasks /Create error: {e}")
        return False
    startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    vbs_path = startup_dir / "9router.vbs"
    if vbs_path.exists():
        try:
            vbs_path.unlink()
            write_ok("Removed stale VBS startup shortcut")
        except Exception:
            write_skip("Could not remove stale VBS (may need admin)")
    write_ok(f"Windows Scheduled Task '{name}' created")
    return True


def _enable_linux() -> bool:
    name = _get_task_name()
    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_dir.mkdir(parents=True, exist_ok=True)
    service_file = service_dir / f"{name}.service"
    # Use Python CLI directly
    service_content = f"""[Unit]
Description=Farewell Assistant 9Router
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=python3 -m farewell_assistant.cli start
Restart=on-failure
RestartSec=300
Environment=NODE_ENV=production

[Install]
WantedBy=default.target
"""
    try:
        service_file.write_text(service_content, encoding="utf-8")
    except Exception as e:
        write_fail(f"Failed to write service file: {e}")
        return False
    try:
        subprocess.run(
            ["systemctl", "--user", "daemon-reload"],
            check=True, capture_output=True, timeout=15,
        )
        subprocess.run(
            ["systemctl", "--user", "enable", name],
            check=True, capture_output=True, timeout=15,
        )
    except subprocess.CalledProcessError as e:
        write_fail(f"systemctl failed: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        write_fail(f"systemctl error: {e}")
        return False
    write_ok(f"systemd user service '{name}' enabled")
    return True


def _disable_windows() -> bool:
    name = _get_task_name()
    cmd = ["schtasks", "/Delete", "/TN", name, "/F"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=15)
    except subprocess.CalledProcessError as e:
        write_fail(f"schtasks /Delete failed: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        write_fail(f"schtasks /Delete error: {e}")
        return False
    write_ok(f"Windows Scheduled Task '{name}' deleted")
    return True


def _disable_linux() -> bool:
    name = _get_task_name()
    service_file = Path.home() / ".config" / "systemd" / "user" / f"{name}.service"
    try:
        subprocess.run(
            ["systemctl", "--user", "disable", name],
            check=True, capture_output=True, timeout=15,
        )
    except subprocess.CalledProcessError:
        pass
    try:
        if service_file.exists():
            service_file.unlink()
    except Exception as e:
        write_fail(f"Failed to remove service file: {e}")
        return False
    try:
        subprocess.run(
            ["systemctl", "--user", "daemon-reload"],
            check=True, capture_output=True, timeout=15,
        )
    except subprocess.CalledProcessError as e:
        write_fail(f"systemctl daemon-reload failed: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        write_fail(f"systemctl error: {e}")
        return False
    write_ok(f"systemd user service '{name}' disabled")
    return True


def enable_autostart() -> bool:
    system = platform.system()
    if system == "Windows":
        ok = _enable_windows()
    elif system == "Linux":
        ok = _enable_linux()
    else:
        write_fail(f"Unsupported platform: {system}")
        write_task_log("AUTOSTART_ENABLE", f"Unsupported platform {system}", "fail")
        return False
    result = "ok" if ok else "fail"
    write_task_log("AUTOSTART_ENABLE", f"Autostart enabled ({system})", result)
    return ok


def disable_autostart() -> bool:
    system = platform.system()
    if system == "Windows":
        ok = _disable_windows()
    elif system == "Linux":
        ok = _disable_linux()
    else:
        write_fail(f"Unsupported platform: {system}")
        write_task_log("AUTOSTART_DISABLE", f"Unsupported platform {system}", "fail")
        return False
    result = "ok" if ok else "fail"
    write_task_log("AUTOSTART_DISABLE", f"Autostart disabled ({system})", result)
    return ok


def show_status() -> dict:
    name = _get_task_name()
    system = platform.system()
    configured = False
    if system == "Windows":
        try:
            r = subprocess.run(
                ["schtasks", "/Query", "/TN", name, "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=10,
            )
            configured = r.returncode == 0 and name in r.stdout
        except Exception:
            configured = False
    elif system == "Linux":
        service_file = Path.home() / ".config" / "systemd" / "user" / f"{name}.service"
        configured = service_file.exists()
    standalone_js = config.ROUTER_DIR / ".next" / "standalone" / "server.js"
    router_alive = _get_router_health()
    pid = get_9router_pid()
    return {
        "platform": system,
        "autostart_configured": configured,
        "task_name": name,
        "router_running": router_alive,
        "router_pid": pid,
        "standalone_build": standalone_js.exists(),
    }
