"""Full coverage for workmode — switch, show, permission, mode defs."""
from pathlib import Path
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.workmode import switch_workmode, show_mode_info, MODE_DEFS
from farewell_assistant.helpers import get_work_mode


class TestModeDefs:
    def test_plan_exists(self):
        assert "plan" in MODE_DEFS

    def test_build_exists(self):
        assert "build" in MODE_DEFS

    def test_plan_blocks_write(self):
        assert "write" in MODE_DEFS["plan"]["tools_blocked"]

    def test_build_allows_write(self):
        assert "write" in MODE_DEFS["build"]["tools_allowed"]

    def test_plan_groups(self):
        assert "audit" in MODE_DEFS["plan"]["groups"]

    def test_build_groups(self):
        assert "orchestration" in MODE_DEFS["build"]["groups"]


class TestSwitchWorkmode:
    def test_switch_to_plan(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "WORK_MODE_FILE", state_dir / "work-mode.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        (tmp_path / "skill-mode-index.json").write_text('{"plan": {"skills": {"audit": []}}}')
        switch_workmode("plan")
        assert get_work_mode() == "plan"

    def test_switch_to_build(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "WORK_MODE_FILE", state_dir / "work-mode.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        (tmp_path / "skill-mode-index.json").write_text('{"build": {"skills": {"coding": []}}}')
        switch_workmode("build")
        assert get_work_mode() == "build"

    def test_status_does_not_crash(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "WORK_MODE_FILE", state_dir / "work-mode.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        (tmp_path / "skill-mode-index.json").write_text('{"build": {"skills": {}}}')
        switch_workmode("status")
