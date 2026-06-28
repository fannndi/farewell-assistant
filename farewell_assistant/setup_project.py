"""Project analyzer — scan path → detect stack/type → register → write skill manifest."""

import json
from pathlib import Path
from datetime import date
from . import config
from .indexer import STACK_SKILLS, COMMON_SKILLS, _find_matching_skills

SIGNATURES = [
    ("pyproject.toml", "python"), ("setup.py", "python"), ("requirements.txt", "python"),
    ("Cargo.toml", "rust"), ("go.mod", "golang"),
    ("pubspec.yaml", "flutter"), ("package.json", "nodejs"),
    ("compose.yml", "docker"), ("Dockerfile", "docker"),
    ("kubernetes", "infra"), ("k8s", "infra"),
]

FRAMEWORK_HINTS = {
    "next.config": "nextjs", "nuxt.config": "vue",
    "vite.config": "react", "angular.json": "angular",
    "vue.config": "vue", "svelte.config": "svelte",
    "django": "django", "fastapi": "fastapi", "flask": "flask",
    "spring": "java", "pom.xml": "java", "build.gradle": "kotlin",
    "Podfile": "swift", "Package.swift": "swift",
}


def _probe_stack(path: Path) -> list[str]:
    hints = set()
    entries = list(path.iterdir()) if path.is_dir() else []

    # File-based detection — check root + 1 level deep
    for fname, stack_name in SIGNATURES:
        if fname.endswith("/"):  # directory check
            if any(e.is_dir() and e.name == fname.rstrip("/") for e in entries):
                hints.add(stack_name)
        else:
            if (path / fname).exists():
                hints.add(stack_name)
            else:
                # Check one level deep for monorepo structures
                for e in entries:
                    if e.is_dir() and (e / fname).exists():
                        hints.add(stack_name)
                        break

    # Framework hints from subdirs + file scans
    for e in entries:
        if e.is_dir():
            for hint, stack_name in FRAMEWORK_HINTS.items():
                if any(f.name.startswith(hint) for f in e.iterdir()):
                    hints.add(stack_name)
        elif e.is_file():
            for hint, stack_name in FRAMEWORK_HINTS.items():
                if e.name.startswith(hint):
                    hints.add(stack_name)

    # Deep scan common configs
    if (path / "supabase").is_dir() or any("supabase" in str(f) for f in path.rglob("supabase*")):
        hints.add("database")

    if not hints:
        hints.add("nodejs")

    return sorted(hints)


def _detect_type(stack: list[str]) -> str:
    priority = ["flutter", "nextjs", "react", "vue", "angular", "nodejs", "python", "golang", "rust", "kotlin", "swift"]
    for p in priority:
        if p in stack:
            return p
    return stack[0] if stack else "unknown"


def _detect_dominan(stack: list[str]) -> str:
    dom_map = {"flutter": "DART", "nextjs": "TYPESCRIPT", "react": "TYPESCRIPT",
               "vue": "JAVASCRIPT", "python": "PYTHON", "golang": "GOLANG",
               "rust": "RUST", "kotlin": "KOTLIN", "swift": "SWIFT", "nodejs": "NODE"}
    for s in stack:
        if s in dom_map:
            return dom_map[s]
    return "UNKNOWN"


def _project_name_from_path(path: Path) -> str:
    return path.resolve().name


def _next_project_code(reg: dict) -> str:
    existing = list(reg.get("projects", {}).keys()) if reg else []
    max_n = 0
    for name, info in (reg.get("projects", {}).items() if reg else {}).items():
        code = info.get("project_code", "")
        if code.isdigit():
            max_n = max(max_n, int(code))
    return f"{max_n + 1:03d}"


def analyze_and_register(path_str: str) -> dict:
    path = Path(path_str).resolve()
    if not path.is_dir():
        raise ValueError(f"Path not found or not a directory: {path}")

    stack = _probe_stack(path)
    ptype = _detect_type(stack)
    dominan = _detect_dominan(stack)
    name = _project_name_from_path(path)

    reg = config.REGISTRY_FILE
    data = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else {"active": "", "projects": {}}

    if name in data.get("projects", {}):
        code = data["projects"][name]["project_code"]
        action = "updated"
    else:
        code = _next_project_code(data)
        data.setdefault("projects", {})[name] = {}
        action = "registered"

    data["projects"][name] = {
        "project_code": code, "type": ptype,
        "last_used": date.today().isoformat(),
        "context_file": f"{name}.md",
        "path": str(path), "dominan": dominan, "is_local": False,
    }
    data["active"] = name

    reg.parent.mkdir(parents=True, exist_ok=True)
    tmp = reg.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(reg)

    # Write skill manifest
    skills = _find_matching_skills(stack)
    manifest_fname = f"{code}-{name}.json"
    manifest_path = config.FAREWELL_DIR / "manifests" / manifest_fname
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"stack": stack, "skills": skills, "project": f"{code}-{name}"}
    tmp2 = manifest_path.with_suffix(".json.tmp")
    tmp2.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp2.replace(manifest_path)

    return {"action": action, "code": code, "name": name, "type": ptype, "dominan": dominan, "stack": stack, "skills": skills, "path": str(path)}
