import subprocess
import platform
from pathlib import Path
from . import config
from .helpers import write_info, write_ok, write_skip, write_step
from .log import write_task_log


def update_repo(repo_dir: Path, label: str, remote: str, branch: str) -> bool:
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        write_skip(f"{label}: .git not found in {repo_dir}")
        return False
    write_step(f"Updating {label} ({remote}/{branch})...")
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only", remote, branch],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            write_info(f"{label}: {result.stderr.strip()}")
            return False
        output = result.stdout.strip()
        if output:
            write_ok(f"{label}: {output.splitlines()[0]}")
            write_task_log("STAGE", f"update {label}", "success", str(repo_dir))
            return True
        write_skip(f"{label}: up to date")
        return False
    except Exception as e:
        write_info(f"{label}: error - {e}")
        return False


def run_update_check() -> dict:
    ecc_updated = update_repo(config.ECC_DIR, "ECC", "origin", "main")
    router_updated = update_repo(config.ROUTER_DIR, "9Router", "origin", "master")
    return {"ecc_updated": ecc_updated, "router_updated": router_updated}


def rebuild_9router_if_needed(was_updated: bool) -> bool:
    if not was_updated:
        write_skip("9Router build: not needed (no update)")
        return True
    use_shell = platform.system() == "Windows"
    node_modules = config.ROUTER_DIR / "node_modules"
    if not node_modules.exists():
        write_step("Installing 9Router dependencies...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(config.ROUTER_DIR),
                capture_output=True,
                text=True,
                shell=use_shell,
                check=True,
            )
            write_ok("Dependencies installed")
        except subprocess.CalledProcessError as e:
            write_info(f"npm install failed: {e.stderr.strip()}")
            return False
    write_step("Building 9Router...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(config.ROUTER_DIR),
            capture_output=True,
            text=True,
            shell=use_shell,
        )
        if result.returncode != 0:
            write_info(f"Build failed: {result.stderr.strip()}")
            write_task_log("STAGE", "rebuild 9Router", "fail", str(config.ROUTER_DIR))
            return False
        write_ok("9Router built successfully")
        write_task_log("STAGE", "rebuild 9Router", "success", str(config.ROUTER_DIR))
        return True
    except Exception as e:
        write_info(f"Build error: {e}")
        return False
