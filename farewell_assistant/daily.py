"""Daily all-in-one — start 9Router + upstream ECC/Router + sync opencode + readiness check."""

import json
import os
import socket
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from . import config
from .helpers import _c, write_ok, write_skip, write_info, write_fail, write_step


def _db() -> Path | None:
    p = Path(os.environ.get("APPDATA", "")) / "9router" / "db" / "data.sqlite"
    return p if p.exists() else None


# ── Phase 1/4: Start 9Router ─────────────────────────────────────────────

def _ensure_9router() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("127.0.0.1", 20128))
    sock.close()
    if result == 0:
        return True

    write_skip("9Router not running - starting...")
    router_dir = config.ROUTER_DIR
    standalone = router_dir / ".next" / "standalone"

    # Ensure static files copied to standalone
    src = router_dir / ".next" / "static"
    dst = standalone / "public" / "_next" / "static"
    if src.exists() and dst.parent.parent.exists():
        dst.mkdir(parents=True, exist_ok=True)
        subprocess.run(["robocopy", str(src), str(dst), "/E", "/NJH", "/NJS", "/NDL", "/NP"],
                      capture_output=True, text=True, timeout=30)

    try:
        import time
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


# ── Phase 2/4: Upstream (ECC + 9Router) ──────────────────────────────────

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


# ── Phase 3/4: Sync opencode.jsonc ───────────────────────────────────────

def _load_db_combos() -> list[dict]:
    db = _db()
    if not db: return []
    conn = sqlite3.connect(str(db))
    cur = conn.execute("SELECT name, kind, models FROM combos")
    combos = []
    for row in cur.fetchall():
        if row[0].lower() == "nvidia": continue
        models = json.loads(row[2]) if row[2] else []
        if models:
            kind = row[1] or "round-robin"
            combos.append({"key": row[0], "name": f"{row[0]} ({len(models)} models, {kind})", "models": models})
    conn.close()
    return combos


def _nvidia_models() -> dict:
    return {
        "deepseek-ai/deepseek-v4-flash": {"name": "Nvidia Flash (40 RPM)"},
        "deepseek-ai/deepseek-v4-pro": {"name": "Nvidia Pro (40 RPM)"},
    }


def _sync_opencode():
    """Read template, substitute combo models, write to opencode.jsonc."""
    template = config.ROOT_DIR / "opencode.template.jsonc"
    output = config.ROOT_DIR / "opencode.jsonc"
    if not template.exists():
        return

    combos = _load_db_combos()
    model_entries = []
    for i, c in enumerate(combos):
        comma = "," if i < len(combos) - 1 else ""
        model_entries.append(f'        "{c["key"]}": {{ "name": "{c["name"]}" }}{comma}')
    models_json = "{\n" + "\n".join(model_entries) + "\n      }"

    content = template.read_text(encoding="utf-8")
    content = content.replace("${COMBO_MODELS}", models_json)
    tmp = output.with_suffix(".jsonc.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(output)


# ── Phase 4/4: Readiness check ───────────────────────────────────────────

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
        conn = sqlite3.connect(str(db))
        cur = conn.execute("SELECT name, kind, models FROM combos")
        combos = []
        for row in cur.fetchall():
            if row[0].lower() == "nvidia": continue
            models = json.loads(row[2]) if row[2] else []
            if models:
                combos.append({"name": row[0], "kind": row[1] or "-", "models": models})
        conn.close()
        return {"combos": combos, "total": len(combos)}
    except Exception as e:
        return {"error": str(e)}


def _check_nvidia() -> dict:
    try:
        from .nvidia import NVIDIA_API_KEY_FLASH, NVIDIA_MODELS, _load_api_key
    except:
        pass
    results = {}
    for model in ["deepseek-ai/deepseek-v4-flash", "deepseek-ai/deepseek-v4-pro"]:
        ok = False; reason = ""
        try:
            var = "NVIDIA_API_KEY_FLASH" if "flash" in model else "NVIDIA_API_KEY_PRO"
            api_key = None
            for line in Path("api-key.txt").read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == var: api_key = v.strip(); break
            if not api_key:
                reason = "No API key"
            else:
                payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "p"}], "max_tokens": 1}).encode()
                req = urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions",
                    data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
                r = urllib.request.urlopen(req, timeout=8)
                ok = r.status == 200
        except urllib.error.HTTPError as e:
            if e.code == 429: ok = True; reason = "RPM limited"
            else: reason = f"HTTP {e.code}"
        except Exception as e:
            if "timed out" in str(e).lower(): ok = True; reason = "RPM limited (timeout)"
            else: reason = str(e)
        results[model] = {"ok": ok, "reason": reason}
    return results


# ── Report ────────────────────────────────────────────────────────────────

def _print_report(health, ecc, github, combos, nvidia, upstream_ecc, upstream_router):
    print(f"\n  {_c('='*40, 'cyan')}\n  {_c('Daily Readiness', 'cyan')}\n  {_c('='*40, 'cyan')}")

    if health["running"]:
        write_ok(f"9Router v{health['version'] or '?'} (port 20128)")
    else:
        write_fail("9Router NOT running")

    if ecc.get("commits_behind", 0) > 0:
        write_info(f"ECC: {ecc['commits_behind']} behind -- pulled now")
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


# ── Run all ───────────────────────────────────────────────────────────────

def run_daily():
    print(f"\n  {_c('='*40, 'cyan')}\n  {_c('Daily', 'cyan')}\n  {_c('='*40, 'cyan')}\n")

    # Phase 1: Start 9Router
    write_step("1/4", "Start 9Router")
    started = _ensure_9router()
    if not started:
        write_fail("9Router failed to start")

    # Phase 2: Upstream (ECC + 9Router + awesome-opencode)
    write_step("2/4", "Upstream ECC + 9Router + awesome-opencode")
    ecc_upstream = git_pull(config.ECC_DIR, "origin", "main")
    if ecc_upstream.get("updated"):
        write_ok("ECC: {0}".format(ecc_upstream["summary"]))
        for c in ecc_upstream.get("new_commits", [])[:5]:
            write_info("  {0}".format(c))
    elif ecc_upstream.get("reason") == "up to date":
        write_info("ECC: up to date")
    else:
        write_info("ECC: {0}".format(ecc_upstream.get("reason", "error")))

    awesome_upstream = git_pull(config.AWESOME_DIR, "origin", "main")
    if awesome_upstream.get("updated"):
        write_ok("awesome-opencode: {0}".format(awesome_upstream["summary"]))
        for c in awesome_upstream.get("new_commits", [])[:5]:
            write_info("  {0}".format(c))
    elif awesome_upstream.get("reason") == "up to date":
        write_info("awesome-opencode: up to date")
    else:
        write_info("awesome-opencode: {0}".format(awesome_upstream.get("reason", "error")))

    router_upstream = git_pull(config.ROUTER_DIR, "origin", "master")
    if router_upstream.get("updated"):
        write_ok("9Router: {0}".format(router_upstream["summary"]))
        for c in router_upstream.get("new_commits", [])[:5]:
            write_info("  {0}".format(c))
    elif router_upstream.get("reason") == "up to date":
        write_info("9Router: up to date")
    else:
        write_info("9Router: {0}".format(router_upstream.get("reason", "error")))

    # Phase 3: Sync opencode.jsonc
    write_step("3/4", "Sync opencode.jsonc + awesome-index")
    _sync_opencode()
    write_ok("opencode.jsonc synced")
    from .awesome_indexer import load_all_entries
    plugs, themes, ags, projs, res = load_all_entries()
    write_info("awesome: {0} plugins, {1} themes, {2} agents, {3} projects".format(len(plugs), len(themes), len(ags), len(projs)))

    # Phase 4: Readiness check
    write_step("4/4", "Readiness check")
    health = _check_9router()
    ecc = _check_ecc()
    github = _check_github_release()
    combos = _get_combos()
    nvidia = _check_nvidia()

    _print_report(health, ecc, github, combos, nvidia, ecc_upstream, router_upstream)
