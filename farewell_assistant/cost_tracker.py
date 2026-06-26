"""Cost & context budget tracker — observability layer over 9Router API calls."""

import json
import csv
from datetime import datetime, timezone
from pathlib import Path

from . import config


class ContextBudget:
    """Per-task context window budget — in-memory. Reset per task."""
    def __init__(self, context_window=1_000_000, warn_pct=0.75, stop_pct=0.95):
        self.total_tokens = 0
        self.context_window = context_window
        self.warn_threshold = int(context_window * warn_pct)
        self.stop_threshold = int(context_window * stop_pct)

    def add(self, total_tokens: int) -> str:
        self.total_tokens += total_tokens
        if self.total_tokens >= self.stop_threshold:
            return "stop"
        if self.total_tokens >= self.warn_threshold:
            return "warning"
        return "ok"

    def reset(self):
        self.total_tokens = 0

    def check(self) -> str:
        if self.total_tokens >= self.stop_threshold:
            return "stop"
        if self.total_tokens >= self.warn_threshold:
            return "warning"
        return "ok"

    def ratio(self) -> float:
        return self.total_tokens / self.context_window if self.context_window else 0

    def status(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "context_window": self.context_window,
            "ratio": self.ratio(),
            "state": "stop" if self.total_tokens >= self.stop_threshold
                     else "warning" if self.total_tokens >= self.warn_threshold
                     else "ok",
        }


def _load_rates(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


class CostBudget:
    """Persistent monthly cost budget — survives restarts."""
    def __init__(self, rates_path=None, storage_path=None, log_path=None):
        self.rates_path = rates_path or config.RATES_FILE
        self.storage_path = storage_path or config.COST_BUDGET_FILE
        self.log_path = log_path or config.COST_LOG_FILE
        self.rates = _load_rates(self.rates_path)
        self._ensure_log_header()
        self.data = self._load()

    def _ensure_log_header(self):
        try:
            p = Path(self.log_path)
            if not p.exists():
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow([
                        "timestamp", "model", "prompt_tokens",
                        "completion_tokens", "cache_hit_tokens",
                        "cache_miss_tokens", "request_cost",
                        "running_monthly_cost",
                    ])
        except Exception:
            pass

    def _load(self) -> dict:
        p = Path(self.storage_path)
        if not p.exists():
            return self._default_data()
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("month") != _current_month():
                return self._default_data()
            return d
        except Exception:
            return self._default_data()

    def _default_data(self) -> dict:
        return {
            "month": _current_month(),
            "cumulative_cost": 0.0,
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "by_model": {},
        }

    def _save(self):
        try:
            p = Path(self.storage_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(p.suffix + ".tmp")
            tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(p)
        except Exception:
            pass

    def _get_rate(self, model: str) -> dict:
        models = self.rates.get("models", {})
        if model in models:
            return models[model]
        ml = model.lower()
        for key, val in models.items():
            kl = key.lower()
            if kl in ml or ml in kl:
                return val
        if "flash" in ml:
            return models.get("deepseek-v4-flash", {"input": 0.14, "output": 0.28, "cache_hit": 0.0028})
        if "pro" in ml:
            return models.get("deepseek-v4-pro", {"input": 0.435, "output": 0.87, "cache_hit": 0.003625})
        return {"input": 0.14, "output": 0.28, "cache_hit": 0.0028}

    def _calc_cost(self, model: str, prompt_tokens: int, completion_tokens: int,
                   cache_hit_tokens: int) -> float:
        rate = self._get_rate(model)
        non_cached = max(0, prompt_tokens - cache_hit_tokens)
        cost = 0.0
        cost += non_cached * (rate.get("input", 0.14) / 1_000_000)
        cost += cache_hit_tokens * (rate.get("cache_hit", rate.get("input", 0.14)) / 1_000_000)
        cost += completion_tokens * (rate.get("output", 0.28) / 1_000_000)
        return cost

    def add(self, model: str, prompt_tokens: int, completion_tokens: int,
            cache_hit_tokens: int = 0, cache_miss_tokens: int = 0) -> str:
        request_cost = self._calc_cost(model, prompt_tokens, completion_tokens, cache_hit_tokens)
        self.data["cumulative_cost"] = round(self.data["cumulative_cost"] + request_cost, 6)
        self.data["total_requests"] += 1
        self.data["total_prompt_tokens"] += prompt_tokens
        self.data["total_completion_tokens"] += completion_tokens

        by_model = self.data["by_model"]
        if model not in by_model:
            by_model[model] = {"requests": 0, "cost": 0.0, "prompt_tokens": 0, "completion_tokens": 0}
        by_model[model]["requests"] += 1
        by_model[model]["cost"] = round(by_model[model]["cost"] + request_cost, 6)
        by_model[model]["prompt_tokens"] += prompt_tokens
        by_model[model]["completion_tokens"] += completion_tokens

        self._log_entry(model, prompt_tokens, completion_tokens,
                        cache_hit_tokens, cache_miss_tokens, request_cost)
        self._save()
        return self.check()

    def _log_entry(self, model: str, prompt_tokens: int, completion_tokens: int,
                   cache_hit_tokens: int, cache_miss_tokens: int, request_cost: float):
        try:
            p = Path(self.log_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([
                    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
                    model, prompt_tokens, completion_tokens,
                    cache_hit_tokens, cache_miss_tokens,
                    f"{request_cost:.6f}",
                    f"{self.data['cumulative_cost']:.6f}",
                ])
        except Exception:
            pass

    def check(self) -> str:
        monthly_budget = self.rates.get("thresholds", {}).get("monthly_budget_usd", 10.0)
        if monthly_budget <= 0:
            return "ok"
        ratio = self.data["cumulative_cost"] / monthly_budget
        stop_pct = self.rates.get("thresholds", {}).get("monthly_stop_pct", 1.0)
        warn_pct = self.rates.get("thresholds", {}).get("monthly_warning_pct", 0.80)
        if ratio >= stop_pct:
            return "stop"
        if ratio >= warn_pct:
            return "warning"
        return "ok"

    def status(self) -> dict:
        monthly_budget = self.rates.get("thresholds", {}).get("monthly_budget_usd", 10.0)
        ratio = self.data["cumulative_cost"] / monthly_budget if monthly_budget > 0 else 0
        return {
            "month": self.data["month"],
            "cumulative_cost": self.data["cumulative_cost"],
            "monthly_budget": monthly_budget,
            "ratio": round(ratio, 4),
            "total_requests": self.data["total_requests"],
            "total_prompt_tokens": self.data["total_prompt_tokens"],
            "total_completion_tokens": self.data["total_completion_tokens"],
            "by_model": self.data["by_model"],
            "state": self.check(),
        }

    def reset(self):
        self.data = self._default_data()
        self._save()

    def import_from_9router(self, rows: list[dict]):
        """Bulk import usage history from 9Router SQLite for catch-up sync."""
        for row in rows:
            model = row.get("model", "unknown")
            prompt_tokens = row.get("prompt_tokens", 0) or 0
            completion_tokens = row.get("completion_tokens", 0) or 0
            self.add(model, prompt_tokens, completion_tokens)


_context_budget = None
_cost_budget = None


def get_context_budget() -> ContextBudget:
    global _context_budget
    if _context_budget is None:
        rates = _load_rates(config.RATES_FILE)
        t = rates.get("thresholds", {})
        _context_budget = ContextBudget(
            context_window=t.get("context_window", 1_000_000),
            warn_pct=t.get("context_warning_pct", 0.75),
            stop_pct=t.get("context_stop_pct", 0.95),
        )
    return _context_budget


def get_cost_budget() -> CostBudget:
    global _cost_budget
    if _cost_budget is None:
        _cost_budget = CostBudget()
    return _cost_budget


def log_api_call(model: str, prompt_tokens: int, completion_tokens: int,
                 cache_hit_tokens: int = 0, cache_miss_tokens: int = 0) -> dict:
    ctx = get_context_budget()
    cst = get_cost_budget()
    total_tokens = prompt_tokens + completion_tokens
    ctx_state = ctx.add(total_tokens)
    cst_state = cst.add(model, prompt_tokens, completion_tokens, cache_hit_tokens, cache_miss_tokens)
    return {
        "context_state": ctx_state,
        "cost_state": cst_state,
        "overall": "stop" if "stop" in (ctx_state, cst_state)
                  else "warning" if "warning" in (ctx_state, cst_state)
                  else "ok",
        "context": ctx.status(),
        "cost": cst.status(),
    }
