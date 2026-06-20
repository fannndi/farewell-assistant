"""Project type detection from directory markers."""

import fnmatch
import re
from collections import OrderedDict
from pathlib import Path

from . import config
from .helpers import write_fail, write_info, write_ok, write_step
from .log import write_task_log

# ---------------------------------------------------------------------------
# Marker -> project type mapping (ordered by specificity)
# ---------------------------------------------------------------------------

MARKERS = OrderedDict({
    "pubspec.yaml":     ("Flutter",    "Flutter + Dart"),
    "go.mod":           ("Go",         "Go module"),
    "Cargo.toml":       ("Rust",       "Rust + Cargo"),
    "composer.json":    ("PHP/Laravel","PHP + Composer"),
    "Gemfile":          ("Ruby",       "Ruby + Bundler"),
    "requirements.txt": ("Python",     "Python + pip"),
    "pyproject.toml":   ("Python",     "Python + PEP 621"),
    "package.json":     ("Node",       "Node.js + npm"),
    "tsconfig.json":    ("TypeScript", "TypeScript"),
    "*.csproj":         (".NET",       "C# / .NET"),
    "*.vbproj":         (".NET",       "VB.NET / .NET"),
    "Pipfile":          ("Python",     "Python + Pipenv"),
    "mix.exs":          ("Elixir",     "Elixir + Mix"),
    "build.gradle":     ("Java/Kotlin","JVM + Gradle"),
    "build.gradle.kts": ("Java/Kotlin","JVM + Gradle KTS"),
    "pom.xml":          ("Java",       "Java + Maven"),
})

# ---------------------------------------------------------------------------
# Heuristics for sub-type refinement
# ---------------------------------------------------------------------------

def _file_contains(file_path: Path, pattern: str) -> bool:
    if not file_path.is_file():
        return False
    try:
        content = file_path.read_text(encoding="utf-8")
        return bool(re.search(pattern, content))
    except Exception:
        return False


def refine_node_type(root: Path) -> str:
    pkg = root / "package.json"
    if not pkg.is_file():
        return "Node.js"
    if _file_contains(pkg, r'"next"'):
        return "Next.js"
    if _file_contains(pkg, r'"nuxt"'):
        return "Nuxt"
    if _file_contains(pkg, r'"vue"'):
        return "Vue"
    if _file_contains(pkg, r'"react"'):
        return "React"
    if _file_contains(pkg, r'"express"'):
        return "Express"
    if _file_contains(pkg, r'"nestjs"'):
        return "NestJS"
    if _file_contains(pkg, r'"svelte"'):
        return "Svelte"
    return "Node.js"


def refine_php_type(root: Path) -> str:
    composer = root / "composer.json"
    if not composer.is_file():
        return "PHP"
    if _file_contains(composer, r'"laravel/framework"'):
        return "Laravel"
    if _file_contains(composer, r'"symfony/symfony"'):
        return "Symfony"
    return "PHP"


# ---------------------------------------------------------------------------
# Main Detection
# ---------------------------------------------------------------------------

def detect_project(path: str = "", emit_context: bool = False) -> dict:
    if not path:
        path = str(Path.cwd())

    root = Path(path)
    if not root.exists():
        write_fail("Path not found: " + path)
        return {"type": "unknown", "stack": "unknown"}

    write_step("DETECT", "Project type detection")
    write_info("Path: " + str(root))

    detected = None
    stack = None
    sub_type = None

    for marker, (ptype, pstack) in MARKERS.items():
        if marker.startswith("*"):
            # Glob pattern (e.g. *.csproj)
            matches = list(root.glob(marker))
            if matches:
                detected = ptype
                stack = pstack
                break
        else:
            file_path = root / marker
            if file_path.exists():
                detected = ptype
                stack = pstack
                if detected == "Node":
                    sub_type = refine_node_type(root)
                if detected == "PHP/Laravel":
                    sub_type = refine_php_type(root)
                break

    if not detected:
        supported = ", ".join(MARKERS.keys())
        write_fail("No project markers found in " + str(root))
        write_info("Supported markers: " + supported)
        write_task_log("DETECT", "Detect " + path, "fail", str(root))
        return {"type": "unknown", "stack": "unknown"}

    display_type = detected + " (" + sub_type + ")" if sub_type else detected
    write_ok("Type: " + display_type)
    write_ok("Stack: " + stack)

    if emit_context:
        import re as _re
        slug = root.name
        slug = _re.sub(r"[^a-z0-9-]", "-", slug.lower())
        slug = _re.sub(r"-+", "-", slug)
        ctx_dir = config.CONTEXT_DIR
        ctx_dir.mkdir(parents=True, exist_ok=True)
        ctx_file = ctx_dir / (slug + ".md")
        lines = [
            "# " + slug,
            "",
            "Type: " + display_type,
            "Path: " + str(root).replace("\\", "/"),
            "Stack: " + stack,
            "Focus: (describe current focus)",
            "Key files: (list important directories/files)",
        ]
        ctx_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        write_ok("Context template written: " + str(ctx_file))
        write_info("Edit it to add focus + key files, then register in projects/registry.json")

    write_task_log("DETECT", "Detect " + str(root) + " -> " + display_type, "success", str(root))
    return {"type": display_type, "stack": stack, "sub_type": sub_type}
