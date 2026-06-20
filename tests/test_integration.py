"""Integration tests for the full pipeline."""
import pytest
from pytest import MonkeyPatch
from pathlib import Path
from unittest.mock import patch

from farewell_assistant import config
from farewell_assistant.intent_router import invoke_intent_router, sync_turn_state, check_task_permission


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    state_dir = tmp_path / ".opencode"
    state_dir.mkdir()
    monkeypatch.setattr(config, "STATE_DIR", state_dir)
    monkeypatch.setattr(config, "REGISTRY_FILE", tmp_path / "data" / "registry.json")
    monkeypatch.setattr(config, "LOG_FILE", tmp_path / "logging.md")
    yield


class TestInvokeIntentRouter:
    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_build_intent(self, mock_enrich):
        result = invoke_intent_router("bikin CRUD user dengan auth JWT")
        assert result["success"] is True
        assert result["intent"]["intent"] == "build"
        assert result["intent"]["domain"] == "web"
        assert result["needs_planning"] is False
        assert len(result["skill_chain"]) == 8

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_fix_intent(self, mock_enrich):
        result = invoke_intent_router("fix bug auth token expired")
        assert result["success"] is True
        assert result["intent"]["intent"] == "fix"
        assert result["intent"]["domain"] == "web"

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_deploy_intent(self, mock_enrich):
        result = invoke_intent_router("deploy docker kubernetes production")
        assert result["success"] is True
        assert result["intent"]["intent"] == "deploy"
        assert result["model_route"]["primary"] == "Free"

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_blocked_in_plan_mode(self, mock_enrich):
        result = invoke_intent_router("bikin landing page", work_mode="plan")
        assert result["success"] is False
        assert "build" in result["reason"].lower()

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_turn_counter_increments(self, mock_enrich):
        result1 = invoke_intent_router("test input 1")
        result2 = invoke_intent_router("test input 2")
        assert result2["turn"] > result1["turn"]

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_pipeline_result_written(self, mock_enrich):
        invoke_intent_router("bikin CRUD user")
        pipeline_file = config.STATE_DIR / "pipeline-result.json"
        assert pipeline_file.exists()
        import json
        data = json.loads(pipeline_file.read_text(encoding="utf-8"))
        assert data["project"] == "farewell-assistant"
        assert data["work_mode"] == "build"

    @patch("farewell_assistant.enrichment_pipeline.invoke_structured_enrichment", return_value=None)
    def test_context_md_written_with_kategori(self, mock_enrich):
        # Create registry with kategori
        reg_file = config.REGISTRY_FILE
        reg_file.parent.mkdir(parents=True, exist_ok=True)
        reg_file.write_text(
            '{"active": "farewell-assistant", "projects": {"farewell-assistant": {"kategori": {"0": "AUTOMATION"}}}}',
            encoding="utf-8",
        )
        invoke_intent_router("test")
        ctx_file = config.STATE_DIR / "context.md"
        assert ctx_file.exists()
        content = ctx_file.read_text(encoding="utf-8")
        assert "Kategori" in content
