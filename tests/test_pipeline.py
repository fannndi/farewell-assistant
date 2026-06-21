import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from farewell_assistant import config
from farewell_assistant.enrichment_pipeline import (
    clear_intent_cache,
    get_cached_intent,
    get_quick_intent,
    set_cached_intent,
    check_input_sufficiency,
)
from farewell_assistant.helpers import read_json
from farewell_assistant.intent_router import (
    invoke_intent_router,
    select_model_route,
    sync_turn_state,
    check_task_permission,
)
from farewell_assistant.skill_chain import get_skill_chain


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    state_dir = tmp_path / ".opencode"
    state_dir.mkdir()
    monkeypatch.setattr(config, "STATE_DIR", state_dir)
    clear_intent_cache()
    yield
    clear_intent_cache()


class TestQuickIntent:
    def test_fix_bug(self):
        r = get_quick_intent("fix bug auth token expiry")
        assert r["intent"] == "fix"
        assert r["confidence"] == 0.7

    def test_build_crud(self):
        r = get_quick_intent("bikin CRUD user dengan auth")
        assert r["intent"] == "build"
        assert r["confidence"] == 0.8

    def test_deploy_infra(self):
        r = get_quick_intent("deploy docker kubernetes cluster")
        assert r["intent"] == "deploy"
        assert r["domain"] == "infra"

    def test_review(self):
        r = get_quick_intent("review code security")
        assert r["intent"] == "review"

    def test_unknown(self):
        r = get_quick_intent("apa itu closure")
        assert r["intent"] == "ask"


class TestSkillChain:
    def test_build_web(self):
        chain = get_skill_chain("build", "web")
        assert len(chain) == 8
        assert chain[0]["name"] == "orch-add-feature"
        assert chain[-1]["name"] == "git-workflow"

    def test_build_mobile(self):
        chain = get_skill_chain("build", "mobile")
        assert len(chain) == 7
        assert chain[1]["name"] == "dart-flutter-patterns"

    def test_fix_general(self):
        chain = get_skill_chain("fix", "general")
        assert len(chain) == 3
        assert chain[0]["name"] == "search-first"

    def test_deploy(self):
        chain = get_skill_chain("deploy", "general")
        assert len(chain) == 4
        assert chain[0]["name"] == "production-audit"

    def test_unknown_fallback(self):
        chain = get_skill_chain("unknown", "general")
        assert chain[0]["name"] == "documentation-lookup"


class TestCheckTaskPermission:
    def test_blocks_build_in_plan(self):
        r = check_task_permission({"intent": "build"}, "plan")
        assert r["allowed"] is False
        assert "requires BUILD" in r["reason"]

    def test_allows_review_in_plan(self):
        r = check_task_permission({"intent": "review"}, "plan")
        assert r["allowed"] is True

    def test_allows_all_in_build(self):
        r = check_task_permission({"intent": "build"}, "build")
        assert r["allowed"] is True

    def test_allows_docs_in_plan(self):
        r = check_task_permission({"intent": "docs"}, "plan")
        assert r["allowed"] is True


class TestModelRoute:
    def test_low_complexity(self):
        r = select_model_route("low")
        assert r["primary"] == "Free"

    def test_high_secondary(self):
        r = select_model_route("high")
        assert r["secondary"] == "Emergency"

    def test_critical_primary(self):
        r = select_model_route("critical")
        assert r["primary"] == "Emergency"


class TestCheckInputSufficiency:
    def test_research_sufficient(self):
        r = check_input_sufficiency("apa itu closure", {"intent": "research", "stack": []})
        assert r["sufficient"] is True

    def test_docs_sufficient(self):
        r = check_input_sufficiency("write documentation", {"intent": "docs", "stack": []})
        assert r["sufficient"] is True

    def test_ask_short_hold(self):
        r = check_input_sufficiency("hai", {"intent": "ask", "stack": []})
        assert r["sufficient"] is False

    def test_ask_detailed(self):
        r = check_input_sufficiency("apa itu closure di JavaScript?", {"intent": "ask", "stack": ["javascript"]})
        assert r["sufficient"] is True

    def test_fix_with_detail(self):
        r = check_input_sufficiency("fix bug token expired di middleware auth", {"intent": "fix", "stack": []})
        assert r["sufficient"] is True

    def test_fix_short(self):
        r = check_input_sufficiency("fix", {"intent": "fix", "stack": []})
        assert r["sufficient"] is False

    def test_deploy_with_detail(self):
        r = check_input_sufficiency("deploy docker kubernetes production", {"intent": "deploy", "stack": ["docker"]})
        assert r["sufficient"] is True

    def test_deploy_short(self):
        r = check_input_sufficiency("deploy", {"intent": "deploy", "stack": []})
        assert r["sufficient"] is False

    def test_build_always_sufficient(self):
        r = check_input_sufficiency(
            "bikin CRUD user",
            {"intent": "build", "stack": []},
        )
        assert r["sufficient"] is True

    def test_build_with_stack(self):
        r = check_input_sufficiency(
            "bikin CRUD user dengan React",
            {"intent": "build", "stack": ["react"]},
        )
        assert r["sufficient"] is True
        assert r.get("auto_detect_stack") is False

    def test_build_without_stack(self):
        r = check_input_sufficiency(
            "bikin CRUD user",
            {"intent": "build", "stack": []},
        )
        assert r["sufficient"] is True
        assert r.get("auto_detect_stack") is True


class TestCacheFunctions:
    def test_cache_miss(self):
        r = get_cached_intent("unique input xyz123")
        assert r is None

    def test_cache_roundtrip(self):
        test_input = "cache test roundtrip"
        test_intent = {"intent": "build", "confidence": 0.8}
        set_cached_intent(test_input, test_intent)
        r = get_cached_intent(test_input)
        assert r["intent"] == "build"
        assert r["confidence"] == 0.8

    def test_cache_clear(self):
        set_cached_intent("cache clear test", {"intent": "fix"})
        clear_intent_cache()
        r = get_cached_intent("cache clear test")
        assert r is None

    def test_cache_expiry(self):
        set_cached_intent("cache expiry test", {"intent": "docs"})
        # Manually set timestamp to past
        from farewell_assistant.enrichment_pipeline import _intent_cache, _hash_input
        key = _hash_input("cache expiry test")
        _intent_cache[key]["timestamp"] = 0
        r = get_cached_intent("cache expiry test")
        assert r is None

    def test_purge_expired_cache(self):
        from farewell_assistant.enrichment_pipeline import purge_expired_cache
        set_cached_intent("purge test", {"intent": "ask"})
        from farewell_assistant.enrichment_pipeline import _intent_cache, _hash_input
        key = _hash_input("purge test")
        _intent_cache[key]["timestamp"] = 0
        purge_expired_cache()
        r = get_cached_intent("purge test")
        assert r is None


class TestSyncTurnState:
    def test_writes_pipeline_result(self, tmp_path):
        result = {
            "success": True,
            "intent": {
                "intent": "build",
                "domain": "web",
                "complexity": "medium",
                "confidence": 0.95,
                "source": "structured",
                "stack": ["react"],
            },
            "skill_chain": [{"name": "step1", "desc": "first"}],
            "model_route": {"primary": "Free", "secondary": "Free", "heavy": "Free"},
            "needs_planning": False,
            "work_mode": "build",
            "profile": "eco",
            "turn": 1,
            "blocked": [],
            "chain_summary": "step1",
        }
        sync_turn_state(result, "test input")

        pipeline_path = config.STATE_DIR / "pipeline-result.json"
        assert pipeline_path.exists()
        data = json.loads(pipeline_path.read_text(encoding="utf-8"))
        assert data["intent"] == "build"
        assert data["domain"] == "web"
        assert data["input"] == "test input"
        assert data["turn"] == 1

    def test_writes_context_md(self):
        result = {
            "success": True,
            "intent": {
                "intent": "fix",
                "domain": "web",
                "complexity": "medium",
                "confidence": 0.9,
                "source": "quick",
                "stack": [],
            },
            "skill_chain": [{"name": "a", "desc": ""}],
            "model_route": {"primary": "Free", "secondary": "Free", "heavy": "Free"},
            "needs_planning": False,
            "work_mode": "build",
            "profile": "eco",
            "turn": 99,
            "blocked": [],
            "chain_summary": "a",
        }
        sync_turn_state(result, "test")

        ctx_path = config.STATE_DIR / "context.md"
        assert ctx_path.exists()
        content = ctx_path.read_text(encoding="utf-8")
        assert "Session State" in content
        assert "Turn State" in content
        assert "fix" in content
        assert "99" in content
