"""First-run setup: clone ECC, 9Router, npm install, build standalone."""

import platform
import subprocess

from . import config
from .helpers import write_info, write_ok, write_skip, write_step, write_fail
from .log import write_task_log


def bootstrap_check() -> bool:
    return not (
        config.COMBO_FILE.exists()
        and config.LLM_MODE_FILE.exists()
        and config.WORK_MODE_FILE.exists()
    )


def run_bootstrap() -> bool:
    use_shell = platform.system() == "Windows"

    # Clone ECC
    agents_md = config.ECC_DIR / "AGENTS.md"
    if not agents_md.exists():
        write_info("Cloning ECC...")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/affaan-m/ECC.git", str(config.ECC_DIR)],
                check=True, capture_output=True, text=True, timeout=120,
            )
            write_ok("ECC cloned")
        except subprocess.CalledProcessError as e:
            write_fail(f"ECC clone failed: {e.stderr.strip()}")
            return False
    else:
        write_skip("ECC already cloned")

    # Clone 9Router
    pkg_json = config.ROUTER_DIR / "package.json"
    if not pkg_json.exists():
        write_info("Cloning 9Router...")
        try:
            subprocess.run(
                ["git", "clone", "https://github.com/decolua/9router.git", str(config.ROUTER_DIR)],
                check=True, capture_output=True, text=True, timeout=120,
            )
            write_ok("9Router cloned")
        except subprocess.CalledProcessError as e:
            write_fail(f"9Router clone failed: {e.stderr.strip()}")
            return False
    else:
        write_skip("9Router already cloned")

    # npm install
    node_modules = config.ROUTER_DIR / "node_modules"
    if not node_modules.exists():
        write_info("npm install...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=str(config.ROUTER_DIR),
                check=True, capture_output=True, text=True, timeout=300,
                shell=use_shell,
            )
            write_ok("npm install complete")
        except subprocess.CalledProcessError as e:
            write_fail(f"npm install failed: {e.stderr.strip()}")
            return False
    else:
        write_skip("npm already installed")

    # npm run build (standalone)
    standalone_js = config.ROUTER_DIR / ".next" / "standalone" / "server.js"
    if not standalone_js.exists():
        write_info("Building 9Router standalone...")
        try:
            subprocess.run(
                ["npm", "run", "build"],
                cwd=str(config.ROUTER_DIR),
                check=True, capture_output=True, text=True, timeout=600,
                shell=use_shell,
            )
            write_ok("9Router build complete")
        except subprocess.CalledProcessError as e:
            write_fail(f"9Router build failed: {e.stderr.strip()}")
            return False
    else:
        write_skip("9Router already built")

    return True


def handle_first_run() -> bool:
    write_step("BOOTSTRAP", "First-run setup")
    result = run_bootstrap()
    if result:
        # Ask LLM setup — download all 4 models
        try:
            import sys
            if sys.stdin.isatty():
                response = input("\n  Setup LLM? Download all 4 models? [y/N] ").strip().lower()
                if response == "y":
                    from .llm_setup import handle_llm_setup
                    write_step("LLM", "Downloading all 4 profiles...")
                    handle_llm_setup("pull")
                    from .llm_setup import set_llm_mode
                    set_llm_mode("eco")
                    write_ok("LLM setup complete — eco mode (default)")
        except Exception:
            pass
        write_ok("Bootstrap complete")
        write_task_log("bootstrap", "first-run setup", result="success")
    else:
        write_fail("Bootstrap failed")
        write_task_log("bootstrap", "first-run setup", result="fail")
    return result
