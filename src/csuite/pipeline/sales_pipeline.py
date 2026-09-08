"""
Sales pipeline model, owned operationally by the Sales Director agent.
Enforces that a loss reason is always captured for every Closed Lost opportunity.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "sales_pipeline.json"


class InvalidStageError(Exception):
    pass


class LossReasonRequiredError(Exception):
    pass


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Opportunity:
    opportunity_id: str
    account_name: str
    industry: str
    source: str
    stage: str
    value: float = 0.0
    loss_reason: str | None = None
    stage_history: list = field(default_factory=list)


class SalesPipeline:
    def __init__(self, config: dict | None = None):
        self.config = config or _load_config()
        self.stages: list[str] = self.config["stages"]
        self.terminal_stages: list[str] = self.config["terminal_stages"]
        self.loss_reason_required_for: list[str] = self.config["loss_reason_required_for"]
        self.valid_loss_reasons: list[str] = self.config["loss_reasons"]
        self.opportunities: dict[str, Opportunity] = {}

    def create_opportunity(self, account_name: str, industry: str, source: str, value: float = 0.0) -> Opportunity:
        opp = Opportunity(
            opportunity_id=str(uuid.uuid4()),
            account_name=account_name,
            industry=industry,
            source=source,
            stage=self.stages[0],
            value=value,
            stage_history=[self.stages[0]],
        )
        self.opportunities[opp.opportunity_id] = opp
        return opp

    def move_stage(self, opportunity_id: str, new_stage: str, loss_reason: str | None = None) -> Opportunity:
        opp = self.opportunities[opportunity_id]
        if new_stage not in self.stages:
            raise InvalidStageError(f"'{new_stage}' is not a defined pipeline stage.")

        if new_stage in self.loss_reason_required_for:
            if not loss_reason or loss_reason not in self.valid_loss_reasons:
                raise LossReasonRequiredError(
                    f"A valid loss_reason is required to move an opportunity to '{new_stage}'. "
                    f"Valid reasons: {self.valid_loss_reasons}"
                )
            opp.loss_reason = loss_reason

        opp.stage = new_stage
        opp.stage_history.append(new_stage)
        return opp

    def pipeline_value(self) -> float:
        return sum(o.value for o in self.opportunities.values() if o.stage not in self.terminal_stages)

    def by_stage(self) -> dict:
        buckets: dict[str, list[Opportunity]] = {stage: [] for stage in self.stages}
        for opp in self.opportunities.values():
            buckets[opp.stage].append(opp)
        return buckets
