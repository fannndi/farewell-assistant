from pathlib import Path
import pytest
from pytest import MonkeyPatch
from farewell_assistant import config
from farewell_assistant.llm_setup import MODEL, HF_FILE, get_gguf_path


class TestLlmSetup:
    def test_model_defined(self):
        assert MODEL == "qwen2.5-coder-1.5b"
        assert HF_FILE == "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

    def test_get_gguf_path(self, monkeypatch: MonkeyPatch, tmp_path: Path):
        gguf = tmp_path / HF_FILE
        gguf.write_text("dummy")
        monkeypatch.setattr(config, "MODELS_DIR", tmp_path)
        assert get_gguf_path() == gguf

    def test_get_gguf_path_returns_path_or_none(self):
        path = get_gguf_path()
        assert path is None or path.name == HF_FILE
