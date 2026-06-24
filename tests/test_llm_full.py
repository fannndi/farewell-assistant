"""Full coverage for llm_setup — single model, always-on mode."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.llm_setup import MODEL, HF_FILE, HF_REPO, get_gguf_path, set_llm_mode, handle_llm_setup


class TestModel:
    def test_model_defined(self):
        assert MODEL == "qwen2.5-coder-1.5b"
        assert HF_FILE == "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
        assert "Qwen" in HF_REPO

    def test_get_gguf_path_returns_path_or_none(self):
        path = get_gguf_path()
        assert path is None or path.name == HF_FILE

    def test_get_gguf_path_found(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        gguf = tmp_path / HF_FILE
        gguf.write_text("dummy")
        monkeypatch.setattr(config, "MODELS_DIR", tmp_path)
        assert get_gguf_path() == gguf

    def test_set_llm_mode_writes_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_file = tmp_path / "llm-mode.json"
        monkeypatch.setattr(config, "LLM_MODE_FILE", state_file)
        from farewell_assistant.helpers import read_json
        set_llm_mode()
        state = read_json(state_file)
        assert state["mode"] == "on"
        assert state["model"] == MODEL

    def test_handle_status(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("farewell_assistant.llm_setup.invoke_status", lambda: None)
        handle_llm_setup("status")
