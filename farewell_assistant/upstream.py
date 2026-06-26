"""Upstream — git pull ECC + 9Router, analyze changelog, adaptive self-heal."""

import subprocess
from pathlib import Path
from . import config
from .helpers import _c, write_ok, write_skip, write_info, write_step, write_fail
from .log import write_task_log


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


def _get_changed_files(repo_dir: Path, before_sha: str, after_sha: str) -> list[str]:
    try:
        r = subprocess.run(["git", "diff", "--name-only", f"{before_sha}..{after_sha}"],
                          cwd=str(repo_dir), capture_output=True, text=True, timeout=15)
        if r.returncode != 0: return []
        return [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
    except Exception:
        return []


def _get_local_tag(repo_dir: Path) -> str | None:
    try:
        r = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=str(repo_dir),
                          capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


_CRITICAL_PATTERNS = [
    "main.py", "server.py", "src/", "config/",
    "router", "api/", ".env", "next.config",
    "package.json", "pyproject.toml",
]


def _categorize_ecc_changes(changed_files: list[str], project_skills: list[str]) -> dict:
    affected = set()
    for f in changed_files:
        parts = f.replace("\\", "/").split("/")
        if len(parts) >= 2 and parts[0] == "skills":
            skill_name = parts[1]
            if skill_name in project_skills:
                affected.add(skill_name)
    return {
        "affected": sorted(affected),
        "needs_reindex": len(affected) > 0,
    }


def _categorize_router_changes(changed_files: list[str]) -> dict:
    critical = []
    for f in changed_files:
        for pat in _CRITICAL_PATTERNS:
            if pat.lower() in f.lower().replace("\\", "/"):
                critical.append(f)
                break
    return {
        "critical": critical,
        "needs_verify": len(critical) > 0,
    }


def _status(d: dict) -> str:
    if d.get("updated"): return "updated"
    reason = d.get("reason", "")
    return "failed" if reason and reason != "up to date" else "up-to-date"


def run_upstream(full: bool = False) -> dict:
    print(f"\n  {_c('='*50, 'cyan')}\n  {_c('Upstream', 'cyan')}\n  {_c('='*50, 'cyan')}\n")

    heal_actions = []
    ecc_analysis = None
    router_analysis = None

    # ── Phase 1/3: Git Pull ECC ──
    write_step("1/3", "Git Pull ECC")
    ecc = git_pull(config.ECC_DIR, "origin", "main")
    if ecc.get("updated"):
        write_ok(f"ECC: {ecc['summary']}")
        for c in ecc.get("new_commits", [])[:5]:
            write_info(f"  {c}")
    elif ecc.get("reason") == "up to date":
        write_info("ECC: up to date")
    else:
        write_fail(f"ECC: {ecc.get('reason', 'unknown error')}")

    # ── Phase 2/3: Git Pull 9Router ──
    write_step("2/3", "Git Pull 9Router")
    router = git_pull(config.ROUTER_DIR, "origin", "master")
    if router.get("updated"):
        write_ok(f"9Router: {router['summary']}")
        for c in router.get("new_commits", [])[:5]:
            write_info(f"  {c}")
    elif router.get("reason") == "up to date":
        write_info("9Router: up to date")
    else:
        write_fail(f"9Router: {router.get('reason', 'unknown error')}")

    # ── Phase 3/3: Changelog Analysis & Self-Heal ──
    write_step("3/3", "Changelog Analysis & Self-Heal")

    # ECC analysis
    if ecc.get("updated"):
        files = _get_changed_files(config.ECC_DIR, ecc["before"], ecc["after"])
        from .helpers import read_project_active, read_project_code
        active = read_project_active()
        code = read_project_code(active)
        from .indexer import get_project_skills
        project_skills = get_project_skills(code, active)
        ecc_analysis = _categorize_ecc_changes(files, project_skills)
        if ecc_analysis["affected"]:
            write_info(f"ECC: {len(ecc_analysis['affected'])} affected skill(s): {', '.join(ecc_analysis['affected'][:5])}")
        else:
            write_info("ECC: no affected skills")
    else:
        write_info("ECC: no changes")

    # 9Router analysis
    if router.get("updated"):
        files = _get_changed_files(config.ROUTER_DIR, router["before"], router["after"])
        router_analysis = _categorize_router_changes(files)
        tag = _get_local_tag(config.ROUTER_DIR)
        tag_info = f" (tag: {tag})" if tag else ""
        if router_analysis["critical"]:
            write_info(f"9Router: {len(router_analysis['critical'])} critical file(s) changed{tag_info}")
        else:
            write_info(f"9Router: non-critical changes only{tag_info}")
    else:
        write_info("9Router: no changes")

    # Adaptive heal
    if ecc_analysis and ecc_analysis["needs_reindex"]:
        from .helpers import read_project_active, read_project_code, get_project_path
        from .indexer import index_project
        active = read_project_active()
        code = read_project_code(active)
        path = get_project_path(active)
        result = index_project(str(path), code, active)
        heal_actions.append(f"Re-indexed project skills ({result.get('total', 0)} matched)")

    if router_analysis and router_analysis["needs_verify"]:
        from .start import ensure_9router
        if ensure_9router():
            heal_actions.append("9Router health check passed (port 20128)")
        else:
            heal_actions.append("9Router health check FAILED — needs manual intervention")

    if heal_actions:
        for a in heal_actions:
            write_ok(a)
    else:
        write_info("No adaptations needed")

    print(f"\n  {_c('='*50, 'cyan')}\n")

    result = {"success": True, "ecc": ecc, "router": router, "heal_actions": heal_actions}
    write_task_log("UPSTREAM", f"ECC: {_status(ecc)}, Router: {_status(router)}, Heal: {len(heal_actions)} actions", "success")
    return result
