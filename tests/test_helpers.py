import tempfile
from pathlib import Path

import pytest
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.helpers import estimate_tokens, parse_api_key, _supports_color


class TestParseApiKey:
    def test_parses_full_config(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        key_file = tmp_path / "api-key.txt"
        key_file.write_text(
            "# comment\n"
            "NINEROUTER_API_KEY=sk-test\n"
            "COMBO_0=Free\n"
            "MODELS_0=model-a, model-b\n"
            "COMBO_1=Emergency\n"
            "MODELS_1=model-c\n"
        )
        monkeypatch.setattr(config, "API_KEY_FILE", key_file)
        api_key, entries, models = parse_api_key()
        assert api_key == "sk-test"
        assert entries["0"]["combo"] == "Free"
        assert entries["1"]["combo"] == "Emergency"
        assert models["0"]["models"] == ["model-a", "model-b"]
        assert models["1"]["models"] == ["model-c"]

    def test_empty_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        key_file = tmp_path / "api-key.txt"
        key_file.write_text("")
        monkeypatch.setattr(config, "API_KEY_FILE", key_file)
        api_key, _, _ = parse_api_key()
        assert api_key is None

    def test_no_file(self, monkeypatch: MonkeyPatch):
        fake = Path(tempfile.gettempdir()) / "_nonexistent_key_test_.txt"
        monkeypatch.setattr(config, "API_KEY_FILE", fake)
        api_key, _, _ = parse_api_key()
        assert api_key is None


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
        assert n == 3  # 11 chars * 0.25 = 2.75 -> ceil = 3

    def test_cjk(self):
        n = estimate_tokens("你好世界")
        assert n == 4  # 4 CJK chars * 1.0 = 4
