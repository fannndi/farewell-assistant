from pathlib import Path

import pytest
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.llm_setup import PROFILES, get_gguf_path, get_modelfile_content


class TestLlmSetup:
    def test_profiles_defined(self):
        assert "hot" in PROFILES
        assert "eco" in PROFILES
        assert "balance" in PROFILES
        assert "performance" in PROFILES

    def test_get_gguf_path_returns_none_for_unknown(self):
        assert get_gguf_path("unknown") is None

    def test_get_modelfile_content_template(self):
        content = get_modelfile_content("eco", "custom.gguf")
        assert "FROM" in content
        assert "custom.gguf" in content

    def test_get_modelfile_content_unknown(self):
        assert get_modelfile_content("unknown", "x") == ""
