import subprocess
from unittest.mock import patch, MagicMock

from farewell_assistant.health import ensure_9router, ensure_ollama, check_gpu
from farewell_assistant import config
from pytest import MonkeyPatch
from pathlib import Path


class TestCheckGpu:
    def test_returns_dict(self):
        result = check_gpu()
        assert isinstance(result, dict)
        assert "available" in result


class TestEnsureOllama:
    def test_returns_true_when_already_running(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("farewell_assistant.helpers.test_ollama_running", lambda: True)
        assert ensure_ollama() is True

    def test_returns_true_eco_mode(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("farewell_assistant.helpers.get_llm_mode", lambda: "eco")
        assert ensure_ollama() is True
