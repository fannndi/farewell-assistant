"""Smoke tests for farewell-assistant v2 core."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_imports():
    from farewell_assistant import config, helpers, workmode, cli, org
    assert config.ROOT_DIR.exists()


def test_config_paths():
    from farewell_assistant import config
    assert str(config.ROOT_DIR).endswith("farewell-assistant")
    assert config.ECC_DIR.name == "ecc"
    assert config.STATE_DIR.name == ".opencode"


def test_json_io():
    from farewell_assistant.helpers import read_json, write_json
    tmp = Path(tempfile.gettempdir()) / "__test_fa.json"
    data = {"hello": "world", "num": 42}
    write_json(tmp, data)
    assert tmp.exists()
    loaded = read_json(tmp)
    assert loaded == data
    tmp.unlink(missing_ok=True)
    assert read_json(tmp / "nonexistent") is None


def test_workmode_default():
    from farewell_assistant.helpers import get_work_mode
    mode = get_work_mode()
    assert mode in ("plan", "build")


def test_colored_output():
    from farewell_assistant.helpers import _c
    result = _c("hello", "green")
    assert "hello" in result


def test_project_registry():
    from farewell_assistant.helpers import read_project_active, list_registered_projects
    projects = list_registered_projects()
    active = read_project_active()
    assert isinstance(projects, list)
    assert isinstance(active, str)
