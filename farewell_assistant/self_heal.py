import platform
import subprocess
from pathlib import Path


def _has_marker(root: Path, markers: list[str]) -> bool:
    for marker in markers:
        if (root / marker).exists():
            return True
    return False


def _run_check(command: list[str], check_pattern: str = None) -> tuple[bool, str]:
    use_shell = platform.system() == "Windows"
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            shell=use_shell,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        if not passed and check_pattern and check_pattern not in output:
            passed = True
        return passed, output.strip()
    except subprocess.TimeoutExpired:
        return False, "check timed out after 30s"
    except FileNotFoundError:
        return False, f"command not found: {command[0]}"
    except Exception as e:
        return False, str(e)


def self_heal(file_path: str, project_path: str = "") -> list[str]:
    path = Path(file_path)
    if not path.is_absolute():
        path = Path.cwd() / path

    ext = path.suffix.lower()
    root = Path(project_path) if project_path else path.parent
    issues: list[str] = []

    if ext in (".ts", ".tsx"):
        if not _has_marker(root, ["tsconfig.json", "package.json"]):
            return issues
        passed, output = _run_check(["npx", "tsc", "--noEmit"])
        if not passed:
            for line in output.splitlines():
                if line.strip():
                    issues.append(line.strip())

    elif ext == ".dart":
        if not _has_marker(root, ["pubspec.yaml"]):
            return issues
        passed, output = _run_check(["flutter", "analyze", str(path)])
        if not passed:
            for line in output.splitlines():
                if "error" in line.lower() or "warning" in line.lower():
                    issues.append(line.strip())

    elif ext == ".py":
        if not _has_marker(root, ["pyproject.toml", "requirements.txt", "Pipfile"]):
            return issues
        passed, output = _run_check(["ruff", "check", str(path)])
        if not passed:
            for line in output.splitlines():
                if line.strip():
                    issues.append(line.strip())

    return issues


def run_self_heal(file_path: str, project_path: str = ""):
    results = self_heal(file_path, project_path)
    if results:
        print(f"self_heal found {len(results)} issue(s) in {file_path}:")
        for issue in results:
            print(f"  {issue}")
    else:
        print(f"self_heal: {file_path} clean")
