import tempfile
from pathlib import Path
import pytest
from pytest import MonkeyPatch
from farewell_assistant import config
from farewell_assistant.helpers import estimate_tokens, _supports_color


class TestSupportsColor:
    def test_no_color_env(self, monkeypatch: MonkeyPatch):
        monkeypatch.setenv("NO_COLOR", "1")
        assert _supports_color() is False

    def test_default_false(self, monkeypatch: MonkeyPatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setenv("WT_SESSION", "")
        monkeypatch.setenv("TERM_PROGRAM", "")
        monkeypatch.setenv("ConEmuANSI", "")
        monkeypatch.setenv("ANSICON", "")
        monkeypatch.setenv("VSCODE_PID", "")
        assert not _supports_color()


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 0

    def test_ascii(self):
        n = estimate_tokens("hello world")
        assert n == 3

    def test_cjk(self):
        n = estimate_tokens("你好世界")
        assert n == 4
