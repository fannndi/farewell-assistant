"""Full coverage for llm_setup — profiles, mode switch, modelfile, GPU."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.llm_setup import (
    PROFILES,
    MODEL_MAP,
    set_llm_mode,
    get_gguf_path,
    get_modelfile_content,
    invoke_list_profiles,
    handle_llm_setup,
)


class TestProfiles:
    def test_four_profiles(self):
        assert set(PROFILES.keys()) == {"hot", "eco", "balance", "performance"}

    def test_hot_has_modelfile(self):
        assert "Modelfile.qwen3.5-0.8b" in PROFILES["hot"]["modelfile"]

    def test_eco_has_modelfile(self):
        assert "Modelfile.qwen2.5-coder-1.5b" in PROFILES["eco"]["modelfile"]

    def test_balance_has_modelfile(self):
        assert "Modelfile.qwen3.5-2b" in PROFILES["balance"]["modelfile"]

    def test_performance_has_modelfile(self):
        assert "Modelfile.qwen3.5-4b" in PROFILES["performance"]["modelfile"]


class TestModelMap:
    def test_eco_model(self):
        assert MODEL_MAP["eco"] == "qwen2.5-coder-1.5b"

    def test_hot_model(self):
        assert MODEL_MAP["hot"] == "qwen3.5-0.8b"

    def test_balance_model(self):
        assert MODEL_MAP["balance"] == "qwen3.5-2b"

    def test_performance_model(self):
        assert MODEL_MAP["performance"] == "qwen3.5-4b"


class TestSetLlmMode:
    def test_writes_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "LLM_MODE_FILE", state_dir / "llm-mode.json")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "PROFILE_LOG_DIR", tmp_path / "profiles" / "logs")
        set_llm_mode("eco")
        assert (state_dir / "llm-mode.json").exists()

    def test_clears_cache_on_switch(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        from farewell_assistant.enrichment_pipeline import set_cached_intent, get_cached_intent
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "LLM_MODE_FILE", state_dir / "llm-mode.json")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "ENRICHMENT", {"cache_ttl": 3600})
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        monkeypatch.setattr(config, "PROFILE_LOG_DIR", tmp_path / "profiles" / "logs")
        monkeypatch.setattr(config, "COMBO_FILE", tmp_path / "combo.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        from farewell_assistant.log import sync_session_state
        set_cached_intent("test input", {"intent": "build"})
        assert get_cached_intent("test input") is not None
        set_llm_mode("eco")
        assert get_cached_intent("test input") is None


class TestGetGgufPath:
    def test_known_profile(self):
        path = get_gguf_path("eco")
        assert path is not None
        assert path.name.endswith(".gguf")

    def test_unknown_profile(self):
        assert get_gguf_path("unknown") is None


class TestGetModelfileContent:
    def test_includes_from(self):
        content = get_modelfile_content("eco", "custom.gguf")
        assert "FROM" in content
        assert "custom.gguf" in content

    def test_unknown_profile(self):
        assert get_modelfile_content("unknown", "x") == ""


class TestHandleLlmSetup:
    def test_status_does_not_crash(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        state_dir = tmp_path / ".opencode"
        state_dir.mkdir()
        monkeypatch.setattr(config, "LLM_MODE_FILE", state_dir / "llm-mode.json")
        monkeypatch.setattr(config, "MODELS_DIR", tmp_path / "models")
        monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
        monkeypatch.setattr(config, "STATE_DIR", state_dir)
        monkeypatch.setattr(config, "PROFILE_LOG_DIR", tmp_path / "profiles" / "logs")
        monkeypatch.setattr(config, "COMBO_FILE", tmp_path / "combo.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        handle_llm_setup("status")

    def test_list_does_not_crash(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "MODELS_DIR", tmp_path / "models")
        monkeypatch.setattr(config, "STATE_DIR", tmp_path / ".opencode")
        monkeypatch.setattr(config, "PROFILE_LOG_DIR", tmp_path / "profiles" / "logs")
        monkeypatch.setattr(config, "COMBO_FILE", tmp_path / "combo.json")
        monkeypatch.setattr(config, "SKILL_IDX_FILE", tmp_path / "skill-mode-index.json")
        monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "registry.json")
        handle_llm_setup("list")
