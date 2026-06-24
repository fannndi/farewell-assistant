"""Self-Improvement — git pull ECC + 9Router, cek dampak, update changelog."""

import subprocess
from pathlib import Path
from datetime import datetime, timezone

from . import config
from .helpers import _c, read_json, write_json, write_ok, write_skip, write_info, write_step


def git_pull(repo_dir: Path, remote: str = "origin", branch: str = "main") -> dict:
    """Git pull repo, return change summary."""
    git_dir = repo_dir / ".git"
    if not git_dir.exists():
        return {"updated": False, "reason": "not a git repo"}
    try:
        # Get commit count before pull
        before = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
        )
        before_count = int(before.stdout.strip()) if before.returncode == 0 and before.stdout.strip() else 0
        before_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
        ).stdout.strip()[:8]

        # Pull
        r = subprocess.run(
            ["git", "pull", "--ff-only", remote, branch],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            return {"updated": False, "reason": r.stderr.strip()[:200]}

        after_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
        ).stdout.strip()[:8]

        if before_sha == after_sha:
            return {"updated": False, "reason": "up to date"}

        # Get new commits
        log = subprocess.run(
            ["git", "log", f"{before_sha}..{after_sha}", "--oneline"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
        )
        new_commits = [l.strip() for l in log.stdout.strip().splitlines() if l.strip()] if log.returncode == 0 else []

        return {
            "updated": True,
            "before": before_sha,
            "after": after_sha,
            "new_commits": new_commits,
            "summary": f"{before_sha} -> {after_sha} ({len(new_commits)} commit(s))",
        }
    except Exception as e:
        return {"updated": False, "reason": str(e)}


def find_new_skills(ecc_dir: Path, whitelist: set) -> list[str]:
    """Find new skills in ecc/skills/ not yet in whitelist."""
    skills_dir = ecc_dir / "skills"
    data_skills = config.DATA_DIR / "skills"
    ecc_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()
    data_skills_set = {d.name for d in data_skills.iterdir() if d.is_dir()} if data_skills.exists() else set()
    all_skills = ecc_skills | data_skills_set
    return sorted(all_skills - whitelist)


def find_removed_skills(ecc_dir: Path, whitelist: set) -> list[str]:
    """Find whitelisted skills that no longer exist on disk."""
    skills_dir = ecc_dir / "skills"
    data_skills = config.DATA_DIR / "skills"
    ecc_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()} if skills_dir.exists() else set()
    data_skills_set = {d.name for d in data_skills.iterdir() if d.is_dir()} if data_skills.exists() else set()
    all_skills = ecc_skills | data_skills_set
    return sorted(whitelist - all_skills)


def find_chain_impact(missing_skills: list[str], chain_file: Path) -> list[str]:
    """Check which chains reference missing skills."""
    if not missing_skills or not chain_file.exists():
        return []
    try:
        content = chain_file.read_text(encoding="utf-8")
        impacted = []
        for skill in missing_skills:
            chain_key = None
            for line in content.splitlines():
                if f'"{skill}"' in line:
                    # Find parent chain
                    for prev in content.splitlines():
                        if '"' in prev and '": [' in prev:
                            chain_key = prev.split('"')[1]
                    impacted.append(f"{skill} -> chain '{chain_key}'")
                    break
        return impacted
    except Exception:
        return []


def update_changelog(changelog_file: Path, repo_label: str, update_info: dict):
    """Update CHANGELOG file with update info."""
    if not update_info.get("updated"):
        return
    try:
        if not changelog_file.exists():
            changelog_file.write_text(f"# CHANGELOG — {repo_label}\n\n", encoding="utf-8")
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        entry = f"## {ts}\n\n{update_info['summary']}\n\n"
        for c in update_info.get("new_commits", []):
            entry += f"- {c}\n"
        entry += "\n"
        with open(changelog_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def run_self_improvement() -> dict:
    """Main self-improvement routine."""
    print(f"\n  {_c('='*50, 'cyan')}")
    print(f"  {_c('Self-Improvement', 'cyan')}")
    print(f"  {_c('='*50, 'cyan')}\n")

    # Step 1: Git pull ECC
    write_step("1/4", "Git Pull ECC")
    ecc_update = git_pull(config.ECC_DIR, "origin", "main")
    if ecc_update.get("updated"):
        write_ok(f"ECC updated: {ecc_update['summary']}")
        for c in ecc_update.get("new_commits", [])[:5]:
            write_info(f"  {c}")
    else:
        write_info(ecc_update.get("reason", "no changes"))

    # Step 2: Git pull 9Router
    write_step("2/4", "Git Pull 9Router")
    router_update = git_pull(config.ROUTER_DIR, "origin", "master")
    if router_update.get("updated"):
        write_ok(f"9Router updated: {router_update['summary']}")
        for c in router_update.get("new_commits", [])[:5]:
            write_info(f"  {c}")
    else:
        write_info(router_update.get("reason", "no changes"))

    # Step 3: Analisis dampak
    write_step("3/4", "Analisis Dampak")

    whitelist_file = config.ROOT_DIR / "data" / "skill-whitelist.json"
    whitelist_data = read_json(whitelist_file, default={})
    whitelist_skills = set(whitelist_data.get("kept", []))

    new_skills = find_new_skills(config.ECC_DIR, whitelist_skills)
    removed_skills = find_removed_skills(config.ECC_DIR, whitelist_skills)
    chain_impacts = find_chain_impact(removed_skills, config.ROOT_DIR / "farewell_assistant" / "skill_chain.py")

    if new_skills:
        write_skip(f"New skills (not in whitelist): {len(new_skills)}")
        for s in new_skills[:10]:
            write_info(f"  {s}")
    if removed_skills:
        write_skip(f"Removed from disk: {len(removed_skills)}")
        for s in removed_skills[:10]:
            write_info(f"  {s}")
    if chain_impacts:
        write_skip("Chain impacts:")
        for i in chain_impacts[:5]:
            write_info(f"  {i}")

    if not new_skills and not removed_skills:
        write_ok("No impact on this project.")

    # Step 4: Update changelogs
    write_step("4/4", "Update Changelogs")
    update_changelog(config.ROOT_DIR / "CHANGELOG_ECC.md", "ECC", ecc_update)
    update_changelog(config.ROOT_DIR / "CHANGELOG_9ROUTER.md", "9Router", router_update)
    write_ok("Changelogs updated")

    result = {
        "success": True,
        "ecc": {"updated": ecc_update.get("updated", False), "summary": ecc_update.get("summary", "")},
        "router": {"updated": router_update.get("updated", False), "summary": router_update.get("summary", "")},
        "new_skills": new_skills[:20],
        "removed_skills": removed_skills[:20],
        "chain_impacts": chain_impacts[:10],
        "recommendations": [],
    }

    if new_skills:
        result["recommendations"].append(f"Pertimbangkan tambah {len(new_skills)} skill baru ke whitelist.")
    if removed_skills:
        result["recommendations"].append(f"Hapus {len(removed_skills)} skill dari whitelist yang sudah tidak ada di disk.")
    if chain_impacts:
        result["recommendations"].append(f"Update chain definitions: {len(chain_impacts)} impacted.")

    print(f"\n  {_c('='*50, 'cyan')}")
    if result["recommendations"]:
        for rec in result["recommendations"]:
            write_skip(rec)
    else:
        write_ok("No recommendations. System is up to date.")
    print(f"  {_c('='*50, 'cyan')}\n")

    return result
