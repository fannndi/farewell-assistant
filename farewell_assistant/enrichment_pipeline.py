"""Enrichment Pipeline - Structured intent classification via local LLM."""

import hashlib
import json
import re
import time

from . import config
from .helpers import get_llm_mode, get_llm_model, invoke_llm, read_json, write_json

# ---------------------------------------------------------------------------
# Intent Cache (per session, in-memory + disk persistence)
# ---------------------------------------------------------------------------

_CACHE_FILE = config.STATE_DIR / "intent-cache.json"

_intent_cache: dict[str, dict] = {}


def _load_cache():
    global _intent_cache
    try:
        data = read_json(_CACHE_FILE, default={})
        _intent_cache = data if isinstance(data, dict) else {}
    except Exception:
        _intent_cache = {}


def _save_cache():
    try:
        config.STATE_DIR.mkdir(parents=True, exist_ok=True)
        write_json(_CACHE_FILE, _intent_cache)
    except Exception:
        pass


def _hash_input(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.md5(normalized.encode()).hexdigest()


def get_cached_intent(text: str) -> dict | None:
    key = _hash_input(text)
    entry = _intent_cache.get(key)
    if not entry:
        return None
    ts = entry.get("timestamp", 0)
    ttl = config.ENRICHMENT.get("cache_ttl", 3600)
    if time.time() - ts > ttl:
        del _intent_cache[key]
        return None
    return entry.get("data")


def set_cached_intent(text: str, intent: dict):
    _intent_cache[_hash_input(text)] = {
        "data": intent,
        "timestamp": time.time(),
    }
    _save_cache()


def clear_intent_cache():
    _intent_cache.clear()
    if _CACHE_FILE.exists():
        _CACHE_FILE.unlink(missing_ok=True)


def purge_expired_cache():
    """Remove expired entries from cache."""
    now = time.time()
    ttl = config.ENRICHMENT.get("cache_ttl", 3600)
    expired = [k for k, v in _intent_cache.items() if now - v.get("timestamp", 0) > ttl]
    for k in expired:
        del _intent_cache[k]
    if expired:
        _save_cache()


# Load cache on import
_load_cache()


# ---------------------------------------------------------------------------
# Structured Enrichment via Local LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a structured intent classifier. Analyze user input and return ONLY valid JSON.

Return this exact schema (no markdown, no explanation, no code fences):
{
  "intent": "<build|fix|review|deploy|research|docs|ask>",
  "domain": "<web|mobile|infra|data|ai_ml|automation|general>",
  "stack": ["<detected framework or language>"],
  "complexity": "<low|medium|high|critical>",
  "confidence": <0.0 to 1.0>
}

Domain classification rules:
- web: APIs, REST endpoints, CRUD, frontend, backend, authentication, web frameworks (React, Django, FastAPI, Express, Laravel, NestJS)
- mobile: Flutter, Dart, iOS, Android, Swift, Kotlin, React Native
- infra: Docker, Kubernetes, CI/CD, deployment, server configuration, networking
- data: databases, SQL, migrations, ETL, data pipelines, PostgreSQL, MySQL, Redis
- ai_ml: machine learning, model training, inference, LLM, PyTorch, TensorFlow
- automation: PowerShell, scripts, task automation, scheduling, Windows automation
- general: programming concepts, generic questions, unclear domain

Stack detection: identify specific technologies mentioned (e.g., ["python", "fastapi"], ["flutter", "dart"])

Complexity rules:
- low: simple question, one-line fix, typo
- medium: feature implementation, bug fix
- high: architectural change, multi-file refactor, system design
- critical: security vulnerability, production down

Return ONLY the JSON object, nothing else.
"""

VALID_INTENTS = {"build", "fix", "review", "deploy", "research", "docs", "ask"}
VALID_DOMAINS = {"web", "mobile", "infra", "data", "ai_ml", "automation", "general"}
VALID_COMPLEXITY = {"low", "medium", "high", "critical"}


def invoke_structured_enrichment(text_input: str, context: str = "", force: bool = False) -> dict | None:
    """Structured intent classification via local LLM (JSON output).
    Skipped in eco/performance mode (performance is too slow for chat hook, use CLI instead)."""
    mode = get_llm_mode()
    if mode in ("eco", "performance") and not force:
        return None
    if len(text_input.split()) < 3 and not force:
        return None

    context_block = f"\nProject context: {context}\n" if context else ""
    prompt = f"User input: {text_input}{context_block}"

    model = get_llm_model()
    result = invoke_llm(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        model=model,
        max_tokens=config.ENRICHMENT["max_tokens"],
        temperature=config.ENRICHMENT["temperature"],
        timeout_sec=config.ENRICHMENT["timeout"],
    )
    if not result:
        return None

    response_text = result["response"].strip()

    # Strip markdown code fences if present
    response_text = re.sub(r"```json\s*", "", response_text)
    response_text = re.sub(r"```\s*$", "", response_text)
    response_text = response_text.strip()

    # Try parse JSON
    try:
        parsed = json.loads(response_text)
        intent = parsed.get("intent", "ask") if parsed.get("intent") in VALID_INTENTS else "ask"
        domain = parsed.get("domain", "general") if parsed.get("domain") in VALID_DOMAINS else "general"
        complexity = parsed.get("complexity", "medium") if parsed.get("complexity") in VALID_COMPLEXITY else "medium"
        stack = parsed.get("stack", [])
        if not isinstance(stack, list):
            stack = [stack] if stack else []
        # Strip angle brackets
        stack = [re.sub(r"^<|>$", "", s) for s in stack if s]
        confidence = max(0.0, min(1.0, float(parsed.get("confidence", 0.5) or 0.5)))

        return {
            "intent": intent,
            "domain": domain,
            "stack": stack,
            "complexity": complexity,
            "confidence": confidence,
            "source": "structured",
            "raw": parsed,
        }
    except (json.JSONDecodeError, ValueError):
        # JSON parse failed - try regex extraction fallback
        intent_match = re.search(r'"intent"\s*:\s*"(\w+)"', response_text)
        domain_match = re.search(r'"domain"\s*:\s*"(\w+)"', response_text)
        complexity_match = re.search(r'"complexity"\s*:\s*"(\w+)"', response_text)

        intent = intent_match.group(1) if intent_match and intent_match.group(1) in VALID_INTENTS else "ask"
        domain = domain_match.group(1) if domain_match and domain_match.group(1) in VALID_DOMAINS else "general"
        complexity = complexity_match.group(1) if complexity_match and complexity_match.group(1) in VALID_COMPLEXITY else "medium"

        return {
            "intent": intent,
            "domain": domain,
            "stack": [],
            "complexity": complexity,
            "confidence": 0.4,
            "source": "regex_fallback",
            "raw": response_text,
        }


# ---------------------------------------------------------------------------
# Quick Intent Fallback (no LLM, pattern-based)
# ---------------------------------------------------------------------------

_DOMAIN_PATTERNS: list[tuple[str, str]] = [
    (r"react|nextjs|next\.js|vue|angular|frontend|ui|css|html|api|rest|express|fastapi|django|laravel|spring|nest|crud|auth|jwt|backend|server|middleware|token|login|register", "web"),
    (r"flutter|dart|kotlin|android|ios|swift|compose|mobile|react.native", "mobile"),
    (r"docker|kubernetes|k8s|ci|cd|deploy|nginx|terraform|ansible|infra", "infra"),
    (r"postgres|mysql|redis|clickhouse|database|sql|etl|pipeline|data", "data"),
    (r"pytorch|tensorflow|llm|model|train|inference|ml|ai|gpu|cuda", "ai_ml"),
    (r"powershell|script|automate|task|schedule|windows|registry|env", "automation"),
]

_STACK_PATTERNS: list[tuple[str, str]] = [
    (r"python|fastapi|django|flask", "python"),
    (r"node|javascript|typescript|express|nest", "nodejs"),
    (r"react|nextjs|next\.js", "react"),
    (r"flutter|dart", "flutter"),
    (r"powershell|ps1", "powershell"),
    (r"go|golang", "golang"),
    (r"rust|cargo", "rust"),
    (r"php|laravel", "php"),
    (r"java|spring", "java"),
    (r"kotlin", "kotlin"),
    (r"swift|ios", "swift"),
]

_INTENT_PATTERNS: list[tuple[str, str, str | None]] = [
    (r"fix|bug|error|crash|broken|debug", "fix", None),
    (r"review|audit|check|inspect|scan", "review", None),
    (r"deploy|release|ship|publish|ci|cd", "deploy", "high"),
    (r"research|search|find|investigate|compare", "research", "low"),
    (r"write|document|readme|docs|guide", "docs", "low"),
]


def get_quick_intent(text_input: str) -> dict:
    """Pattern-based intent classification (no LLM). Detects multiple intents."""
    input_lower = text_input.lower().strip()
    domain = "general"
    stack: list[str] = []

    # Detect domain
    for pattern, d in _DOMAIN_PATTERNS:
        if re.search(pattern, input_lower):
            domain = d
            break

    # Detect stack
    for pattern, s in _STACK_PATTERNS:
        if re.search(pattern, input_lower):
            stack = [s]
            break

    # Detect intent — collect ALL matches for multi-intent warning
    matched_intents: list[str] = []
    for pattern, intent, fixed_complexity in _INTENT_PATTERNS:
        if re.search(pattern, input_lower):
            matched_intents.append(intent)

    # Also check build patterns
    if re.search(r"create|build|make|add|implement|bikin|buat|tambah", input_lower):
        matched_intents.append("build")

    if not matched_intents:
        return {"intent": "ask", "domain": domain, "stack": stack, "complexity": "low", "confidence": 0.6}

    # Primary = first match (backward compatible)
    primary = matched_intents[0]
    secondary = matched_intents[1:]

    # Complexity from primary
    if primary == "build":
        complexity = "medium"
        if re.search(r"simple|basic|quick|tipis", input_lower):
            complexity = "low"
        if re.search(r"full|complex|advanced|enterprise|sistem", input_lower):
            complexity = "high"
    else:
        # Get complexity from the matching pattern
        complexity = "medium"
        for pattern, intent, fixed_complexity in _INTENT_PATTERNS:
            if intent == primary and fixed_complexity:
                complexity = fixed_complexity
                break

    confidence = 0.8 if primary == "build" else 0.7
    result = {"intent": primary, "domain": domain, "stack": stack, "complexity": complexity, "confidence": confidence}
    if secondary:
        result["secondary_intents"] = secondary
    return result


# ---------------------------------------------------------------------------
# Input Sufficiency Check
# ---------------------------------------------------------------------------

def check_input_sufficiency(text_input: str, classified: dict | None) -> dict:
    """Check if user input has enough detail for precise execution."""
    input_lower = text_input.lower().strip()
    word_count = len(text_input.split())
    intent = classified.get("intent", "unknown") if classified else "unknown"
    domain = classified.get("domain", "general") if classified else "general"
    stack = classified.get("stack", []) if classified else []

    # Always sufficient: questions, research, docs
    if intent in ("research", "docs"):
        return {"sufficient": True}

    # HOLD: ask intent too short
    if intent == "ask" and word_count < 4:
        return {
            "sufficient": False,
            "reason": "Input terlalu singkat. Jelaskan lebih detail apa yang kamu butuhkan.",
            "missing": ["detail lebih lanjut"],
        }

    # Always sufficient: fix/review/deploy with enough detail
    if intent == "fix" and re.search(r"(bug|error|crash|broken|fix)\s+\w+\s+\w+", input_lower):
        return {"sufficient": True}
    if intent == "review" and re.search(r"(review|audit|check)\s+\w+\s+\w+", input_lower):
        return {"sufficient": True}
    if intent == "deploy" and re.search(r"(deploy|release)\s+\w+\s+\w+", input_lower):
        return {"sufficient": True}

    # BUILD intent — always sufficient, flag auto-detection
    if intent == "build":
        has_stack = bool(stack) and stack[0] != ""
        if not has_stack:
            has_stack_hint = bool(re.search(
                r"(react|vue|angular|next|nuxt|django|fastapi|laravel|spring|express|nest|"
                r"flutter|swift|kotlin|python|node|go|rust|php|java|typescript|javascript|"
                r"powershell|postgres|mysql|redis|docker|kubernetes|crud|auth|jwt|rest|graphql)",
                input_lower,
            ))
        return {"sufficient": True, "auto_detect_stack": not has_stack}

    # HOLD: fix/deploy too short
    if intent in ("fix", "deploy") and word_count < 3:
        return {
            "sufficient": False,
            "reason": f"Input terlalu singkat untuk '{intent}'. Jelaskan apa yang perlu di-{intent}.",
            "missing": ["detail lebih lanjut"],
        }

    return {"sufficient": True}
