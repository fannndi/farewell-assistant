"""Self-Improvement — git pull ECC + 9Router, cek dampak."""

import subprocess
from pathlib import Path
from datetime import datetime, timezone
from . import config
from .helpers import _c, read_json, write_ok, write_skip, write_info, write_step


def git_pull(repo_dir: Path, remote: str = "origin", branch: str = "main") -> dict:
    git_dir = repo_dir / ".git"
    if not git_dir.exists(): return {"updated": False, "reason": "not a git repo"}
    try:
        before_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                                    capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        r = subprocess.run(["git", "pull", "--ff-only", remote, branch], cwd=str(repo_dir),
                          capture_output=True, text=True, timeout=60)
        if r.returncode != 0: return {"updated": False, "reason": r.stderr.strip()[:200]}
        after_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir),
                                   capture_output=True, text=True, timeout=10).stdout.strip()[:8]
        if before_sha == after_sha: return {"updated": False, "reason": "up to date"}
        log = subprocess.run(["git", "log", f"{before_sha}..{after_sha}", "--oneline"], cwd=str(repo_dir),
                            capture_output=True, text=True, timeout=10)
        new_commits = [l.strip() for l in log.stdout.strip().splitlines() if l.strip()] if log.returncode == 0 else []
        return {"updated": True, "before": before_sha, "after": after_sha,
                "new_commits": new_commits, "summary": f"{before_sha} -> {after_sha} ({len(new_commits)} commit(s))"}
    except Exception as e: return {"updated": False, "reason": str(e)}


def run_self_improvement(full: bool = False) -> dict:
    print(f"\n  {_c('='*50, 'cyan')}\n  {_c('Self-Improvement', 'cyan')}\n  {_c('='*50, 'cyan')}\n")

    write_step("1/2", "Git Pull ECC")
    ecc = git_pull(config.ECC_DIR, "origin", "main")
    if ecc.get("updated"):
        write_ok(f"ECC: {ecc['summary']}")
        for c in ecc.get("new_commits", [])[:5]: write_info(f"  {c}")
    else: write_info(ecc.get("reason", "no changes"))

    write_step("2/2", "Git Pull 9Router")
    router = git_pull(config.ROUTER_DIR, "origin", "master")
    if router.get("updated"):
        write_ok(f"9Router: {router['summary']}")
        for c in router.get("new_commits", [])[:5]: write_info(f"  {c}")
    else: write_info(router.get("reason", "no changes"))

    print(f"\n  {_c('='*50, 'cyan')}\n")
    return {"success": True, "ecc": ecc, "router": router}
