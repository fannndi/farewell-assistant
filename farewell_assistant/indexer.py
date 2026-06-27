"""Skill indexer — match project stack → ECC skills. Centralized in .farewell/."""

import json

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


def get_project_skills(project_code: str, project_name: str) -> list[str]:
    manifest_path = config.FAREWELL_DIR / "manifests" / f"{project_code}-{project_name}.json"
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data.get("skills", [])
    return []


def write_active_skills_manifest(project_code: str, project_name: str):
    skills = get_project_skills(project_code, project_name)
    if not skills:
        skills = _find_matching_skills([project_code.split("-")[0] if "-" in project_code else project_code]) + COMMON_SKILLS
        skills = sorted(set(skills))
    paths = [f"ecc/skills/{s}/SKILL.md" for s in skills if (config.ECC_DIR / "skills" / s / "SKILL.md").exists()]
    paths += [".farewell/custom-skills"]
    manifest = {"paths": paths, "project": f"{project_code}-{project_name}", "total": len(paths)}
    mf = config.STATE_DIR / "active-skills.json"
    mf.parent.mkdir(parents=True, exist_ok=True)
    tmp = mf.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp.replace(mf)
