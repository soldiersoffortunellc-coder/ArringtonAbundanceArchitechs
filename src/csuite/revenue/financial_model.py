"""
90-day revenue-planning model, owned by the Revenue Operations Analyst agent
(directed by the CRO). Backed by config/financial_scenarios.json.

IMPORTANT: every number produced here is a MODELED planning input, never a
guaranteed outcome. Every output dict is stamped accordingly.
"""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "financial_scenarios.json"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _segment_value(segment: dict, recurring_months: int) -> dict:
    clients = segment["clients"]
    setup_fee = segment["setup_fee"]
    monthly_fee = segment["monthly_fee"]
    setup_revenue = clients * setup_fee
    recurring_revenue = clients * monthly_fee * recurring_months
    return {
        "clients": clients,
        "setup_fee": setup_fee,
        "monthly_fee": monthly_fee,
        "setup_revenue": setup_revenue,
        "recurring_revenue": recurring_revenue,
        "modeled_value": setup_revenue + recurring_revenue,
    }


class FinancialModel:
    def __init__(self, config: dict | None = None):
        self.config = config or _load_config()
        self.recurring_months = self.config["recurring_months_modeled"]
        self.scenarios = self.config["scenarios"]

    def scenario(self, name: str) -> dict:
        if name not in self.scenarios:
            raise KeyError(f"Unknown scenario '{name}'. Known scenarios: {list(self.scenarios)}")
        raw = self.scenarios[name]
        premium = _segment_value(raw["premium"], self.recurring_months)
        standardized = _segment_value(raw["standardized"], self.recurring_months)
        combined = premium["modeled_value"] + standardized["modeled_value"]
        return {
            "scenario": name,
            "is_guaranteed": False,
            "recurring_months_modeled": self.recurring_months,
            "premium": premium,
            "standardized": standardized,
            "combined_modeled_90_day_value": combined,
        }

    def all_scenarios(self) -> dict:
        return {name: self.scenario(name) for name in self.scenarios}
