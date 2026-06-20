from farewell_assistant.bootstrap import bootstrap_check
from farewell_assistant import config
from pathlib import Path
from pytest import MonkeyPatch


class TestBootstrapCheck:
    def test_returns_true_when_no_state(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "COMBO_FILE", tmp_path / "combo.json")
        monkeypatch.setattr(config, "LLM_MODE_FILE", tmp_path / "llm-mode.json")
        monkeypatch.setattr(config, "WORK_MODE_FILE", tmp_path / "work-mode.json")
        assert bootstrap_check() is True

    def test_returns_false_when_state_exists(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "COMBO_FILE", tmp_path / "combo.json")
        monkeypatch.setattr(config, "LLM_MODE_FILE", tmp_path / "llm-mode.json")
        monkeypatch.setattr(config, "WORK_MODE_FILE", tmp_path / "work-mode.json")
        (tmp_path / "combo.json").write_text("[]")
        (tmp_path / "llm-mode.json").write_text("{}")
        (tmp_path / "work-mode.json").write_text("{}")
        assert bootstrap_check() is False
