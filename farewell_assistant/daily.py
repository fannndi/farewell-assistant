"""Daily readiness check — 9Router health, ECC + GitHub updates, combo status."""

import json
import os
import socket
import subprocess
import urllib.request
from pathlib import Path
from . import config
from .helpers import _c, write_ok, write_skip, write_info, write_fail
from .nvidia import ping_all as _ping_nvidia, NVIDIA_MODELS


def _db() -> Path | None:
    p = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    return p if p.exists() else None


def _check_9router() -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()
    if result != 0:
        return {"running": False}
    try:
        r = urllib.request.urlopen("http://localhost:20128/api/version", timeout=3)
        data = json.loads(r.read())
        return {"running": True, "version": data.get("currentVersion")}
    except:
        return {"running": True, "version": None}


def _check_ecc() -> dict:
    try:
        r = subprocess.run(["git", "fetch", "origin", "main"], cwd=str(config.ECC_DIR),
                          capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            return {"updated": False, "reason": r.stderr.strip()[:100]}
        behind = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/main"],
                               cwd=str(config.ECC_DIR), capture_output=True, text=True, timeout=10)
        commits = int(behind.stdout.strip()) if behind.returncode == 0 and behind.stdout.strip() else 0
        return {"updated": commits > 0, "commits_behind": commits}
    except Exception as e:
        return {"updated": False, "reason": str(e)}


def _check_github_release() -> dict:
    try:
        url = "https://api.github.com/repos/decolua/9router/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "farewell-assistant"})
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read())
        return {"tag": data.get("tag_name", ""), "published": data.get("published_at", "")}
    except:
        return {"error": "GitHub unreachable"}


def _get_combos() -> dict:
    db = _db()
    if not db:
        return {"error": "DB not found"}
    try:
        import sqlite3
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        combos = []
        for row in cur.fetchall():
            name = row[0]
            if name.lower() == "nvidia":
                continue
            models = json.loads(row[2]) if row[2] else []
            if models:
                combos.append({"name": row[0], "kind": row[1] or "-", "models": models})
        conn.close()
        return {"combos": combos, "total": len(combos)}
    except Exception as e:
        return {"error": str(e)}


def _print_report(health, ecc, github, combos, nvidia):
    print(f"\n  {_c('='*40, 'cyan')}\n  {_c('Daily Readiness', 'cyan')}\n  {_c('='*40, 'cyan')}")

    if health["running"]:
        write_ok(f"9Router v{health['version'] or '?'} (port 20128)")
    else:
        write_fail("9Router NOT running")

    if ecc.get("commits_behind", 0) > 0:
        write_info(f"ECC: {ecc['commits_behind']} behind -- /upstream")
    else:
        write_ok("ECC: up to date")

    if "error" in github:
        write_fail(f"GitHub: {github['error']}")
    else:
        local = config.ROUTER_DIR / "package.json"
        local_ver = json.loads(local.read_text()).get("version") if local.exists() else None
        tag = github.get("tag", "").lstrip("v")
        if local_ver and tag != local_ver:
            write_info("GitHub: v{0} ({1}) -- update available!".format(tag, github["published"][:10]))
        else:
            write_ok("GitHub: {0}".format(github.get("tag", "?")))

    if "error" in nvidia:
        write_info("Nvidia: {0}".format(nvidia["error"]))
    else:
        ok_models = sum(1 for r in nvidia.values() if r.get("ok"))
        total = len(nvidia)
        if ok_models == total:
            write_ok("Nvidia (direct): {0}/{1} models, 40 RPM".format(ok_models, total))
        else:
            failed = [m for m, r in nvidia.items() if not r.get("ok")]
            write_info("Nvidia (direct): {0}/{1} models -- {2}".format(ok_models, total, ", ".join(failed[:3])))

    if "error" in combos:
        write_info("Combos: {0}".format(combos["error"]))
    else:
        total_models = sum(len(c["models"]) for c in combos["combos"])
        for c in combos["combos"]:
            models_str = ", ".join(c["models"][:4])
            if len(c["models"]) > 4:
                models_str += " +{0}".format(len(c["models"])-4)
            write_info("  {0:<20} ({1:<8}) <- {2}".format(c["name"], c["kind"] or "-", models_str))
        write_ok("{0} combos, {1} models".format(combos["total"], total_models))

    print(f"  {_c('='*40, 'cyan')}\n")


def run_daily():
    health = _check_9router()
    ecc = _check_ecc()
    github = _check_github_release()
    combos = _get_combos()
    nvidia = _ping_nvidia()
    _print_report(health, ecc, github, combos, nvidia)
