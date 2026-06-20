from pathlib import Path
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.workmode import switch_workmode, MODE_DEFS


class TestSwitchWorkmode:
    def test_switch_to_plan(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "WORK_MODE_FILE", tmp_path / "work-mode.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "STATE_DIR", tmp_path)
        (tmp_path / "skill-mode-index.json").write_text(
            '{"plan": {"skills": {"audit": []}}}', encoding="utf-8"
        )
        switch_workmode("plan")
        state_file = tmp_path / "work-mode.json"
        assert state_file.exists()

    def test_mode_defs_complete(self):
        assert "plan" in MODE_DEFS
        assert "build" in MODE_DEFS
        assert "write" in MODE_DEFS["plan"]["tools_blocked"]
        assert "write" in MODE_DEFS["build"]["tools_allowed"]
