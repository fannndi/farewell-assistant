import tempfile
from pathlib import Path
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.log import write_task_log


class TestWriteTaskLog:
    def test_creates_log_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        log_file = tmp_path / "logging.md"
        monkeypatch.setattr(config, "LOG_FILE", log_file)
        write_task_log("TEST", "test action", "success")
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "TEST" in content
        assert "test action" in content
        assert "success" in content

    def test_appends_to_existing(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        log_file = tmp_path / "logging.md"
        log_file.write_text("# Logging\n", encoding="utf-8")
        monkeypatch.setattr(config, "LOG_FILE", log_file)
        write_task_log("STEP1", "first")
        write_task_log("STEP2", "second")
        content = log_file.read_text(encoding="utf-8")
        assert "STEP1" in content
        assert "STEP2" in content
