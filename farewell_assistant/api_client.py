"""HTTP client for 9Router API, with cost/context budget tracking."""

import http.client
import json
from .helpers import parse_api_key
from .cost_tracker import log_api_call, get_cost_budget, get_context_budget


class BudgetExceeded(Exception):
    pass


def _extract_usage(response_body: dict) -> dict | None:
    usage = response_body.get("usage")
    if not usage or not isinstance(usage, dict):
        return None
    prompt_tokens = usage.get("prompt_tokens", 0) or 0
    completion_tokens = usage.get("completion_tokens", 0) or 0
    cache_hit = usage.get("prompt_cache_hit_tokens", 0) or 0
    miss = usage.get("prompt_cache_miss_tokens", 0) or 0
    if not miss and cache_hit:
        miss = max(0, prompt_tokens - cache_hit)
    if not cache_hit and usage.get("prompt_tokens_details"):
        cache_hit = usage["prompt_tokens_details"].get("cached_tokens", 0) or 0
        if not miss:
            miss = max(0, prompt_tokens - cache_hit)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cache_hit_tokens": cache_hit,
        "cache_miss_tokens": miss or max(0, prompt_tokens - cache_hit),
    }


def chat_completion(model: str, messages: list,
                    max_tokens: int = 4096,
                    stream: bool = False,
                    host: str = "localhost",
                    port: int = 20128,
                    **kwargs) -> dict:
    """Send chat completion to 9Router, track usage, enforce budgets.
    
    Returns {'response': dict, 'usage': dict, 'budget': dict}
    Raises BudgetExceeded if hard stop triggered.
    """
    ctx = get_context_budget()
    cst = get_cost_budget()

    if ctx.check() == "stop":
        raise BudgetExceeded("Context budget exceeded — summarize or truncate before continuing")
    if cst.check() == "stop":
        raise BudgetExceeded("Monthly cost budget exceeded — reset or top-up to continue")

    api_key = parse_api_key()
    body = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": stream,
        **kwargs,
    })
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    conn = http.client.HTTPConnection(host, port, timeout=120)
    try:
        conn.request("POST", "/v1/chat/completions", body, headers)
        resp = conn.getresponse()
        raw = resp.read().decode()
        resp_data = json.loads(raw)

        usage_data = _extract_usage(resp_data)
        budget_status = {}
        if usage_data:
            budget_status = log_api_call(
                model=model,
                prompt_tokens=usage_data["prompt_tokens"],
                completion_tokens=usage_data["completion_tokens"],
                cache_hit_tokens=usage_data["cache_hit_tokens"],
                cache_miss_tokens=usage_data["cache_miss_tokens"],
            )

        return {
            "response": resp_data,
            "usage": usage_data,
            "budget": budget_status,
        }
    finally:
        conn.close()
