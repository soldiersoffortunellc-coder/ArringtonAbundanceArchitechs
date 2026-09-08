"""AI usage-limit enforcement, backed by config/ai_usage_limits.json."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "ai_usage_limits.json"


class UsageLimitExceededError(Exception):
    pass


class UsageLimitTracker:
    def __init__(self, config: dict | None = None):
        if config is None:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                config = json.load(fh)
        self.limits_by_tier: dict = config["limits_by_tier"]
        self.hard_stop_multiplier: float = config["hard_stop_multiplier"]
        self._usage: dict[str, dict[str, int]] = {}  # tenant_id -> {metric: count}

    def record_usage(self, tenant_id: str, tier: str, metric: str, amount: int = 1) -> dict:
        if tier not in self.limits_by_tier:
            raise KeyError(f"Unknown plan tier '{tier}'.")
        limit_key = f"{metric}_per_month"
        if limit_key not in self.limits_by_tier[tier]:
            raise KeyError(f"Tier '{tier}' has no limit configured for metric '{metric}'.")

        cap = self.limits_by_tier[tier][limit_key]
        hard_stop = cap * self.hard_stop_multiplier

        tenant_usage = self._usage.setdefault(tenant_id, {})
        current = tenant_usage.get(metric, 0) + amount

        if current > hard_stop:
            raise UsageLimitExceededError(
                f"Tenant '{tenant_id}' exceeded the hard stop for '{metric}' on tier '{tier}' "
                f"({current} > {hard_stop})."
            )

        tenant_usage[metric] = current
        return {
            "tenant_id": tenant_id,
            "metric": metric,
            "usage": current,
            "cap": cap,
            "over_cap": current > cap,
            "hard_stopped": False,
        }

    def usage_for(self, tenant_id: str) -> dict:
        return dict(self._usage.get(tenant_id, {}))
