"""Daily readiness check — 9Router health, ECC + GitHub updates, combo model ping."""

import json
import os
import socket
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from . import config
from .helpers import _c, write_ok, write_skip, write_info, write_fail


def _check_9router() -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()
    if result != 0:
        return {"running": False, "version": None}
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
        published = data.get("published_at", "")
        return {"tag": data.get("tag_name", ""), "name": data.get("name", ""), "published": published}
    except Exception as e:
        return {"error": str(e)}


def _ping_model(model: str) -> tuple:
    try:
        payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "p"}], "max_tokens": 1}).encode()
        req = urllib.request.Request("http://localhost:20128/v1/chat/completions", data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        r = urllib.request.urlopen(req, timeout=8)
        return (True, "OK") if r.status == 200 else (False, f"HTTP {r.status}")
    except urllib.error.HTTPError as e:
        return (False, f"HTTP {e.code}")
    except Exception as e:
        return (False, str(e))


def _check_combo_models() -> dict:
    db = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    if not db.exists():
        return {"error": "DB not found"}
    try:
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        all_models = set()
        combos = []
        for row in cur.fetchall():
            models = json.loads(row[2]) if row[2] else []
            if models:
                combos.append({"name": row[0], "kind": row[1], "models": models})
                all_models.update(models)
        conn.close()
        if not all_models:
            return {"total": 0, "ok": 0, "details": {}, "combos": combos}
        results = {}
        for m in sorted(all_models):
            ok, reason = _ping_model(m)
            results[m] = {"ok": ok, "reason": reason}
        ok_count = sum(1 for r in results.values() if r["ok"])
        return {"total": len(all_models), "ok": ok_count, "details": results, "combos": combos}
    except Exception as e:
        return {"error": str(e)}


def _print_report(health, ecc, github, combo):
    print(f"\n  {_c('='*45, 'cyan')}\n  {_c('Daily Readiness Check', 'cyan')}\n  {_c('='*45, 'cyan')}")

    if health["running"]:
        write_ok(f"9Router running v{health['version'] or '?'} (port 20128)")
    else:
        write_fail("9Router NOT running")

    if ecc.get("commits_behind", 0) > 0:
        write_info(f"ECC: {ecc['commits_behind']} commit(s) behind — run /upstream")
    else:
        write_ok("ECC: up to date")

    if "error" in github:
        write_fail(f"GitHub: {github['error']}")
    else:
        local = config.ROUTER_DIR / "package.json"
        local_ver = json.loads(local.read_text()).get("version") if local.exists() else None
        tag = github.get("tag", "").lstrip("v")
        if local_ver and tag != local_ver:
            write_info(f"GitHub: v{tag} ({github['published'][:10]}) — UPDATE AVAILABLE! (local v{local_ver})")
        else:
            write_ok(f"GitHub: {github.get('tag', '?')} — up to date")

    if "error" in combo:
        write_fail(f"Combos: {combo['error']}")
    elif combo.get("total", 0) == 0:
        write_info("Combos: no combos found")
    elif combo["ok"] == combo["total"]:
        write_ok(f"Combos: {len(combo['combos'])} combos, {combo['ok']}/{combo['total']} models responsive")
    else:
        failed = [m for m, r in combo["details"].items() if not r["ok"]]
        write_fail(f"Combos: {combo['ok']}/{combo['total']} models responsive — {', '.join(failed[:5])}")

    print(f"  {_c('='*45, 'cyan')}\n")


def run_daily():
    health = _check_9router()
    ecc = _check_ecc()
    github = _check_github_release()
    combo = _check_combo_models()
    _print_report(health, ecc, github, combo)
