from pathlib import Path

import pytest
from pytest import MonkeyPatch

from farewell_assistant.detect_project import detect_project, refine_node_type, refine_php_type


class TestDetectProject:
    def test_node_project(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"name": "myapp"}')
        result = detect_project(str(tmp_path))
        assert "Node" in result["type"]

    def test_python_project(self, tmp_path: Path):
        (tmp_path / "requirements.txt").write_text("flask")
        result = detect_project(str(tmp_path))
        assert result["type"] == "Python"

    def test_unknown_project(self, tmp_path: Path):
        result = detect_project(str(tmp_path))
        assert result["type"] == "unknown"

    def test_nonexistent_path(self):
        result = detect_project("C:\\_nonexistent_path_test_")
        assert result["type"] == "unknown"


class TestRefineNodeType:
    def test_nextjs(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"next": "14.0.0"}}')
        assert refine_node_type(tmp_path) == "Next.js"

    def test_react(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"react": "18.0.0"}}')
        assert refine_node_type(tmp_path) == "React"

    def test_express(self, tmp_path: Path):
        (tmp_path / "package.json").write_text('{"dependencies": {"express": "4.0.0"}}')
        assert refine_node_type(tmp_path) == "Express"

    def test_no_package_json(self, tmp_path: Path):
        assert refine_node_type(tmp_path) == "Node.js"


class TestRefinePhpType:
    def test_laravel(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"require": {"laravel/framework": "10.0"}}')
        assert refine_php_type(tmp_path) == "Laravel"

    def test_sfony(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"require": {"symfony/symfony": "7.0"}}')
        assert refine_php_type(tmp_path) == "Symfony"

    def test_plain_php(self, tmp_path: Path):
        (tmp_path / "composer.json").write_text('{"require": {}}')
        assert refine_php_type(tmp_path) == "PHP"
