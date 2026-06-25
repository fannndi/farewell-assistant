"""Skill indexer — match project stack → ECC skills. Centralized in .farewell/."""

import json
from datetime import datetime
from pathlib import Path

from . import config

STACK_SKILLS = {
    "python": ["python-patterns", "python-testing", "fastapi-patterns", "django-patterns", "django-tdd", "django-security", "backend-patterns"],
    "flutter": ["dart-flutter-patterns", "compose-multiplatform-patterns", "flutter-dart-code-review"],
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

COMMON_SKILLS = ["git-workflow", "tdd-workflow", "coding-standards", "error-handling", "security-review", "verification-loop", "agent-self-evaluation", "accessibility"]


def _find_matching_skills(stack: list[str]) -> list[str]:
    matched = set()
    for s in stack:
        for keyword, skills in STACK_SKILLS.items():
            if keyword in s.lower():
                matched.update(skills)
    matched.update(COMMON_SKILLS)
    return sorted(matched)


def index_project(project_path: str, project_code: str, project_name: str, stack: list[str] | None = None) -> dict:
    if not stack:
        from .helpers import detect_type_from_path
        stack = [detect_type_from_path(project_path)]
        # Deep scan
        try:
            for f in Path(project_path).rglob("*"):
                if f.is_file():
                    n = f.name.lower()
                    if n == "manage.py": stack.append("django")
                    if "next.config" in n: stack.append("nextjs")
                    if "pubspec.yaml" in n: stack.append("dart")
                    if "cargo.toml" in n: stack.append("rust")
        except Exception: pass
        stack = list(dict.fromkeys(stack))

    matched = _find_matching_skills(stack)

    # Manifest path: .farewell/manifests/<code>-<name>.json
    manifests_dir = config.FAREWELL_DIR / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifests_dir / f"{project_code}-{project_name}.json"

    manifest = {
        "project": project_name,
        "code": project_code,
        "stack": stack,
        "skills": matched,
        "total": len(matched),
        "indexed_at": datetime.now().isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def get_project_skills(project_code: str, project_name: str) -> list[str]:
    manifest_path = config.FAREWELL_DIR / "manifests" / f"{project_code}-{project_name}.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data.get("skills", [])
    return []


def get_active_skills() -> list[str]:
    from .helpers import read_project_active, read_project_code
    active = read_project_active()
    code = read_project_code(active)
    return get_project_skills(code, active)
