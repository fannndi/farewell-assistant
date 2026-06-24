from farewell_assistant.health import check_gpu, check_llm
from farewell_assistant import config
from pytest import MonkeyPatch
from pathlib import Path


class TestCheckGpu:
    def test_returns_dict(self):
        result = check_gpu()
        assert isinstance(result, dict)
        assert "available" in result


class TestCheckLlm:
    def test_returns_bool(self):
        result = check_llm()
        assert isinstance(result, bool)
