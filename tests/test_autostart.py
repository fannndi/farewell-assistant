from pathlib import Path

import pytest
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.autostart import show_status


class TestAutostartStatus:
    def test_returns_dict(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "TASK_NAME", "FarewellAssistant-Test")
        result = show_status()
        assert "platform" in result
        assert "autostart_configured" in result
        assert "router_running" in result
        assert isinstance(result["autostart_configured"], bool)
