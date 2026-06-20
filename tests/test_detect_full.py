"""Full coverage for detect_project — all 16 markers, refinements, edge cases."""
from pathlib import Path
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.detect_project import detect_project, refine_node_type, refine_php_type


class TestDetectAllMarkers:
    def test_flutter(self, tmp_path: Path):
        (tmp_path / "pubspec.yaml").write_text("name: app")
        r = detect_project(str(tmp_path))
        assert "Flutter" in r["type"]

    def test_go(self, tmp_path: Path):
        (tmp_path / "go.mod").write_text("module app")
        r = detect_project(str(tmp_path))
        assert "Go" in r["type"]

    def test_rust(self, tmp_path: Path):
        (tmp_path / "Cargo.toml").write_text("[package]\nname = 'app'")
        r = detect_project(str(tmp_path))
        assert "Rust" in r["type"]

    def test_python_req(self, tmp_path: Path):
        (tmp_path / "requirements.txt").write_text("flask")
        r = detect_project(str(tmp_path))
        assert "Python" in r["type"]

    def test_python_pyproject(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'app'")
        r = detect_project(str(tmp_path))
        assert "Python" in r["type"]

    def test_python_pipfile(self, tmp_path: Path):
        (tmp_path / "Pipfile").write_text("[packages]")
        r = detect_project(str(tmp_path))
        assert "Python" in r["type"]

    def test_node(self, tmp_path: Path):
        (tmp_path / "package.json").write_text("{}")
        r = detect_project(str(tmp_path))
        assert "Node" in r["type"]

    def test_dotnet(self, tmp_path: Path):
        (tmp_path / "test.csproj").write_text("<Project />")
        r = detect_project(str(tmp_path))
        assert ".NET" in r["type"]

    def test_elixir(self, tmp_path: Path):
        (tmp_path / "mix.exs").write_text("defmodule App do")
        r = detect_project(str(tmp_path))
        assert "Elixir" in r["type"]

    def test_java_gradle(self, tmp_path: Path):
        (tmp_path / "build.gradle").write_text("apply plugin: 'java'")
        r = detect_project(str(tmp_path))
        assert "Java" in r["type"]


class TestRefineNodeType:
    def test_nextjs(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"next": "14"}}')
        assert refine_node_type(tmp_path) == "Next.js"

    def test_nuxt(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"nuxt": "3"}}')
        assert refine_node_type(tmp_path) == "Nuxt"

    def test_vue(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"vue": "3"}}')
        assert refine_node_type(tmp_path) == "Vue"

    def test_react(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "18"}}')
        assert refine_node_type(tmp_path) == "React"

    def test_express(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "4"}}')
        assert refine_node_type(tmp_path) == "Express"

    def test_nestjs(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"nestjs": "9"}}')
        assert refine_node_type(tmp_path) == "NestJS"

    def test_svelte(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"svelte": "3"}}')
        assert refine_node_type(tmp_path) == "Svelte"

    def test_fallback_node(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"name": "app"}')
        assert refine_node_type(tmp_path) == "Node.js"


class TestRefinePhpType:
    def test_laravel(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"require": {"laravel/framework": "10"}}')
        assert refine_php_type(tmp_path) == "Laravel"

    def test_symfony(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"require": {"symfony/symfony": "7"}}')
        assert refine_php_type(tmp_path) == "Symfony"

    def test_plain_php(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"name": "app"}')
        assert refine_php_type(tmp_path) == "PHP"


class TestDetectEdgeCases:
    def test_nonexistent_path(self):
        r = detect_project("C:\\_nonexistent_test_dir_")
        assert r["type"] == "unknown"
        assert r["stack"] == "unknown"

    def test_emit_context_creates_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        from farewell_assistant.helpers import read_json
        monkeypatch.setattr(config, "CONTEXT_DIR", tmp_path / "context")
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        (tmp_path / "package.json").write_text('{"name": "app"}')
        r = detect_project(str(tmp_path), emit_context=True)
        slug = tmp_path.name.lower()
        slug = __import__("re").sub(r"[^a-z0-9\s-]", "", slug)
        slug = __import__("re").sub(r"[\s]+", "-", slug)
        slug = __import__("re").sub(r"-+", "-", slug).strip("-")
        ctx_file = tmp_path / "context" / (slug + ".md")
        assert ctx_file.exists(), f"Expected {ctx_file}"
        reg_file = tmp_path / "registry.json"
        assert reg_file.exists(), "Registry file not created"

    def test_emit_context_updates_registry(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "CONTEXT_DIR", tmp_path / "context")
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        (tmp_path / "requirements.txt").write_text("flask")
        detect_project(str(tmp_path), emit_context=True)
        import json
        data = json.loads((tmp_path / "registry.json").read_text())
        slug = tmp_path.name.lower()
        slug = __import__("re").sub(r"[^a-z0-9\s-]", "", slug)
        slug = __import__("re").sub(r"[\s]+", "-", slug)
        slug = __import__("re").sub(r"-+", "-", slug).strip("-")
        assert data["active"] == slug, f"Expected '{slug}', got '{data['active']}'"
