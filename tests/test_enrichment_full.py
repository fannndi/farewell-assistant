"""Full coverage for enrichment pipeline — edge cases, all intents, cache."""
import time
from pathlib import Path
from pytest import MonkeyPatch

from farewell_assistant import config
from farewell_assistant.enrichment_pipeline import (
    clear_intent_cache,
    get_cached_intent,
    set_cached_intent,
    get_quick_intent,
    check_input_sufficiency,
    purge_expired_cache,
    _hash_input,
)


class TestHashInput:
    def test_consistency(self):
        assert _hash_input("test") == _hash_input("test")

    def test_case_insensitive(self):
        assert _hash_input("Hello") == _hash_input("hello")

    def test_whitespace_normalization(self):
        assert _hash_input("hello  world") == _hash_input("hello world")

    def test_different_inputs(self):
        assert _hash_input("hello") != _hash_input("world")


class TestCache:
    def test_miss(self):
        assert get_cached_intent("unique_xyz_999") is None

    def test_hit(self):
        set_cached_intent("cache_hit_test", {"intent": "build"})
        assert get_cached_intent("cache_hit_test")["intent"] == "build"

    def test_clear(self):
        set_cached_intent("cache_clear_test", {"intent": "fix"})
        clear_intent_cache()
        assert get_cached_intent("cache_clear_test") is None

    def test_expiry(self):
        set_cached_intent("cache_expiry_test", {"intent": "docs"})
        from farewell_assistant.enrichment_pipeline import _intent_cache, _hash_input
        key = _hash_input("cache_expiry_test")
        _intent_cache[key]["timestamp"] = 0
        assert get_cached_intent("cache_expiry_test") is None

    def test_purge_expired(self):
        set_cached_intent("purge_test", {"intent": "ask"})
        from farewell_assistant.enrichment_pipeline import _intent_cache, _hash_input
        key = _hash_input("purge_test")
        _intent_cache[key]["timestamp"] = 0
        purge_expired_cache()
        assert get_cached_intent("purge_test") is None

    def test_no_expiry_within_ttl(self):
        set_cached_intent("ttl_test", {"intent": "build"})
        assert get_cached_intent("ttl_test")["intent"] == "build"


class TestQuickIntent:
    def test_fix_bug(self):
        r = get_quick_intent("fix bug auth token expiry")
        assert r["intent"] == "fix"

    def test_fix_error(self):
        r = get_quick_intent("error pada login")
        assert r["intent"] == "fix"

    def test_fix_crash(self):
        r = get_quick_intent("crash server production")
        assert r["intent"] == "fix"

    def test_review_code(self):
        r = get_quick_intent("review code security")
        assert r["intent"] == "review"

    def test_review_audit(self):
        r = get_quick_intent("audit database performance")
        assert r["intent"] == "review"

    def test_deploy_docker(self):
        r = get_quick_intent("deploy docker kubernetes cluster")
        assert r["intent"] == "deploy"
        assert r["domain"] == "infra"

    def test_deploy_release(self):
        r = get_quick_intent("release version 2.0")
        assert r["intent"] == "deploy"

    def test_research(self):
        r = get_quick_intent("research react vs vue")
        assert r["intent"] == "research"

    def test_research_compare(self):
        r = get_quick_intent("compare fastapi and django")
        assert r["intent"] == "research"

    def test_docs(self):
        r = get_quick_intent("write documentation for API")
        assert r["intent"] == "docs"

    def test_docs_readme(self):
        r = get_quick_intent("update readme")
        assert r["intent"] == "docs"

    def test_build_crud(self):
        r = get_quick_intent("bikin CRUD user dengan auth")
        assert r["intent"] == "build"

    def test_build_create(self):
        r = get_quick_intent("create new feature")
        assert r["intent"] == "build"

    def test_build_make(self):
        r = get_quick_intent("make a simple page")
        assert r["intent"] == "build"

    def test_ask_closure(self):
        r = get_quick_intent("apa itu closure")
        assert r["intent"] == "ask"

    def test_domain_web(self):
        r = get_quick_intent("bikin CRUD user dengan React")
        assert r["domain"] == "web"

    def test_domain_flutter(self):
        r = get_quick_intent("bikin mobile app Flutter")
        assert r["domain"] == "mobile"

    def test_domain_infra(self):
        r = get_quick_intent("setup docker kubernetes")
        assert r["domain"] == "infra"

    def test_domain_data(self):
        r = get_quick_intent("optimize postgres query")
        assert r["domain"] == "data"

    def test_domain_ai_ml(self):
        r = get_quick_intent("train pytorch model")
        assert r["domain"] == "ai_ml"

    def test_domain_automation(self):
        r = get_quick_intent("automate powershell task")
        assert r["domain"] == "automation"

    def test_stack_python(self):
        r = get_quick_intent("fix bug in fastapi app")
        assert "python" in r["stack"]

    def test_stack_react(self):
        r = get_quick_intent("create react component")
        assert "react" in r["stack"]

    def test_stack_flutter(self):
        r = get_quick_intent("bikin mobile Flutter")
        assert "flutter" in r["stack"]


class TestInputSufficiency:
    def test_research_sufficient(self):
        r = check_input_sufficiency("apa itu closure", {"intent": "research"})
        assert r["sufficient"] is True

    def test_docs_sufficient(self):
        r = check_input_sufficiency("write documentation", {"intent": "docs"})
        assert r["sufficient"] is True

    def test_ask_short_hold(self):
        r = check_input_sufficiency("hai", {"intent": "ask"})
        assert r["sufficient"] is False

    def test_ask_detailed(self):
        r = check_input_sufficiency("apa itu closure di JavaScript?", {"intent": "ask", "stack": ["javascript"]})
        assert r["sufficient"] is True

    def test_fix_with_detail(self):
        r = check_input_sufficiency("fix bug token expired di middleware auth", {"intent": "fix"})
        assert r["sufficient"] is True

    def test_fix_short(self):
        r = check_input_sufficiency("fix", {"intent": "fix"})
        assert r["sufficient"] is False

    def test_deploy_with_detail(self):
        r = check_input_sufficiency("deploy docker kubernetes production", {"intent": "deploy"})
        assert r["sufficient"] is True

    def test_deploy_short(self):
        r = check_input_sufficiency("deploy", {"intent": "deploy"})
        assert r["sufficient"] is False

    def test_build_always_sufficient(self):
        r = check_input_sufficiency("bikin CRUD user", {"intent": "build", "stack": []})
        assert r["sufficient"] is True

    def test_build_with_stack(self):
        r = check_input_sufficiency("bikin CRUD dengan React", {"intent": "build", "stack": ["react"]})
        assert r["sufficient"] is True
        assert r.get("auto_detect_stack") is False

    def test_build_without_stack(self):
        r = check_input_sufficiency("bikin CRUD user", {"intent": "build", "stack": []})
        assert r["sufficient"] is True
        assert r.get("auto_detect_stack") is True

    def test_fix_review_deploy_sufficient(self):
        for intent in ("fix", "review", "deploy"):
            r = check_input_sufficiency(f"fix error in {intent} endpoint", {"intent": intent})
            assert r["sufficient"] is True
