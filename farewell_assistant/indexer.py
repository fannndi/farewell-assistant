"""Skill indexer — match project stack → ECC skills, symlink to .farewell/."""

import json
import os
import platform
import subprocess
from pathlib import Path

from . import config
from .helpers import write_ok, write_skip, write_info, write_step

STACK_SKILLS: dict[str, list[str]] = {
    "python": [
        "python-patterns", "python-testing", "fastapi-patterns", "django-patterns",
        "django-tdd", "django-security", "backend-patterns",
    ],
    "flutter": [
        "dart-flutter-patterns", "compose-multiplatform-patterns", "flutter-dart-code-review",
    ],
    "dart": ["dart-flutter-patterns", "flutter-dart-code-review"],
    "react": ["react-patterns", "react-testing", "react-performance", "frontend-patterns"],
    "nextjs": ["react-patterns", "react-testing", "nextjs-turbopack", "frontend-patterns"],
    "vue": ["vue-patterns", "ui-to-vue"],
    "nodejs": ["nestjs-patterns", "prisma-patterns", "backend-patterns", "database-migrations"],
    "golang": ["golang-patterns", "golang-testing"],
    "rust": ["rust-patterns", "rust-testing"],
    "kotlin": ["kotlin-patterns", "kotlin-coroutines-flows", "kotlin-testing"],
    "swift": ["swiftui-patterns", "swift-concurrency-6-2", "swift-actor-persistence"],
    "database": ["postgres-patterns", "mysql-patterns", "database-migrations", "redis-patterns"],
    "docker": ["docker-patterns", "deployment-patterns"],
    "infra": ["kubernetes-patterns", "deployment-patterns", "docker-patterns"],
}

COMMON_SKILLS = [
    "git-workflow", "tdd-workflow", "coding-standards", "error-handling",
    "security-review", "verification-loop", "agent-self-evaluation",
    "accessibility",
]


def _find_matching_skills(stack: list[str]) -> list[str]:
    matched: set[str] = set()
    for s in stack:
        for keyword, skills in STACK_SKILLS.items():
            if keyword in s.lower():
                matched.update(skills)
    matched.update(COMMON_SKILLS)
    return sorted(matched)


def _make_symlink(target: Path, link: Path) -> bool:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists():
        return True
    try:
        if platform.system() == "Windows":
            r = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True, text=True, timeout=10,
            )
            return r.returncode == 0
        else:
            link.symlink_to(target, target_is_directory=True)
            return True
    except Exception:
        return False


def index_project(project_path: str, stack: list[str] | None = None, force: bool = False) -> dict:
    p = Path(project_path)
    if not p.is_dir():
        return {"ok": False, "error": "Path not found"}

    farewell_dir = p / ".farewell"
    skills_link_dir = farewell_dir / "skills"
    manifest_path = farewell_dir / "manifest.json"

    if manifest_path.exists() and not force:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        write_skip(f"Already indexed ({len(existing.get('skills',[]))} skills)")
        return {"ok": True, "skills": existing.get("skills", []), "stack": existing.get("stack", [])}

    # Detect stack if not provided
    if not stack:
        from .helpers import detect_type_from_path
        t = detect_type_from_path(str(p))
        stack = [t] if t != "unknown" else []
        # Deep scan for more specific frameworks
        try:
            for f in p.rglob("*"):
                if f.is_file():
                    n = f.name.lower()
                    if n == "manage.py": stack.append("django")
                    if "next.config" in n: stack.append("nextjs")
                    if "pubspec.yaml" in n: stack.append("dart")
                    if "cargo.toml" in n: stack.append("rust")
        except Exception: pass
        stack = list(dict.fromkeys(stack))  # dedupe

    matched = _find_matching_skills(stack)

    write_step("INDEX", f"Indexing {len(matched)} skills for {p.name} ({', '.join(stack)})")

    # Create symlinks
    linked = 0
    for skill in matched:
        src = config.ECC_DIR / "skills" / skill
        if src.is_dir():
            dst = skills_link_dir / skill
            if _make_symlink(src, dst):
                linked += 1

    manifest = {
        "project": p.name,
        "stack": stack,
        "skills": matched,
        "linked": linked,
        "total": len(matched),
        "indexed_at": __import__("datetime").datetime.now().isoformat(),
    }
    farewell_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_ok(f"{linked}/{len(matched)} skills indexed")
    return {"ok": True, "skills": matched, "stack": stack, "linked": linked}


def get_indexed_skills(project_path: str) -> list[str]:
    manifest = Path(project_path) / ".farewell" / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return data.get("skills", [])
    return []
