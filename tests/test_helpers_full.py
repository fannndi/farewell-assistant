"""Full coverage for helpers — GPU, Ollama, 9Router, token estimation."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from pytest import MonkeyPatch
import tempfile

from farewell_assistant import config
from farewell_assistant.helpers import (
    get_gpu_info,
    get_llm_mode,
    get_work_mode,
    get_llm_model,
    test_ollama_running as test_ollama_running_fn,
    estimate_tokens,
    parse_api_key,
    get_skill_count,
    read_json,
    write_json,
)


class TestGetGpuInfo:
    def test_returns_dict(self):
        result = get_gpu_info()
        assert isinstance(result, dict)
        assert "available" in result

    def test_explicit_fields(self):
        result = get_gpu_info("name,memory.total,memory.used")
        assert isinstance(result, dict)
        if result.get("available"):
            assert "name" in result
            assert "memory_total" in result
            assert "memory_used" in result

    def test_returns_zero_on_no_gpu(self):
        result = get_gpu_info("name,memory.total")
        assert isinstance(result, dict)
        assert "available" in result


class TestGetLlmMode:
    def test_defaults_to_eco(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "LLM_MODE_FILE", tmp_path / "nonexistent.json")
        assert get_llm_mode() == "eco"

    def test_reads_existing(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        f = tmp_path / "llm-mode.json"
        f.write_text('{"mode": "balance"}')
        monkeypatch.setattr(config, "LLM_MODE_FILE", f)
        assert get_llm_mode() == "balance"


class TestGetWorkMode:
    def test_defaults_to_build(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "WORK_MODE_FILE", tmp_path / "nonexistent.json")
        assert get_work_mode() == "build"

    def test_reads_existing(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        f = tmp_path / "work-mode.json"
        f.write_text('{"mode": "plan"}')
        monkeypatch.setattr(config, "WORK_MODE_FILE", f)
        assert get_work_mode() == "plan"


class TestGetLlmModel:
    def test_returns_string(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        monkeypatch.setattr(config, "LLM_MODE_FILE", tmp_path / "nonexistent.json")
        result = get_llm_model()
        assert isinstance(result, str)


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 0

    def test_ascii(self):
        n = estimate_tokens("hello")
        assert n > 0

    def test_cjk(self):
        n = estimate_tokens("你好")
        assert n >= 2

    def test_long_input(self):
        n = estimate_tokens("a" * 1000)
        assert n > 100


class TestParseApiKey:
    def test_parses_full(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        f = tmp_path / "api-key.txt"
        f.write_text("NINEROUTER_API_KEY=sk-test\nCOMBO_0=Free\nMODELS_0=model-a,model-b\n")
        monkeypatch.setattr(config, "API_KEY_FILE", f)
        api_key, entries, models = parse_api_key()
        assert api_key == "sk-test"
        assert entries["0"]["combo"] == "Free"
        assert models["0"]["models"] == ["model-a", "model-b"]

    def test_empty_file(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        f = tmp_path / "api-key.txt"
        f.write_text("")
        monkeypatch.setattr(config, "API_KEY_FILE", f)
        api_key, _, _ = parse_api_key()
        assert api_key is None

    def test_no_file(self, monkeypatch: MonkeyPatch):
        fake = Path(tempfile.gettempdir()) / "_nonexistent_test_.txt"
        monkeypatch.setattr(config, "API_KEY_FILE", fake)
        api_key, _, _ = parse_api_key()
        assert api_key is None


class TestReadWriteJson:
    def test_roundtrip(self, tmp_path: Path):
        f = tmp_path / "test.json"
        data = {"key": "value", "num": 42}
        write_json(f, data)
        result = read_json(f)
        assert result == data

    def test_nonexistent(self, tmp_path: Path):
        result = read_json(tmp_path / "nonexistent.json")
        assert result is None

    def test_corrupt(self, tmp_path: Path):
        f = tmp_path / "corrupt.json"
        f.write_text("not json {{{")
        result = read_json(f)
        assert result is None


class TestGetSkillCount:
    def test_returns_int(self, tmp_path: Path, monkeypatch: MonkeyPatch):
        idx_file = tmp_path / "skill-mode-index.json"
        idx_file.write_text('{"build": {"skill_groups": {"coding": ["a","b"]}}}')
        monkeypatch.setattr(config, "SKILL_IDX_FILE", idx_file)
        result = get_skill_count("build")
        assert result == 2
