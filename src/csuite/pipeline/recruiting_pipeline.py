"""
Recruiting pipeline model for the Insurance Agency Revenue OS — tracks
candidates sourced from recruiting funnels (including the Meta/Facebook Lead
Ads recruiting funnel, see csuite.ghl.meta_recruiting) through licensing,
interview, and contracting into an active agent.

Kept separate from csuite.pipeline.sales_pipeline.SalesPipeline (rather than
generalized into one model) because a recruiting candidate and a sales
opportunity carry genuinely different fields (licensing_status vs deal
value) and different terminal-stage semantics (Active Agent / Disqualified
vs Closed Won / Closed Lost).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "pipelines" / "recruiting_pipeline.json"


class InvalidRecruitingStageError(Exception):
    pass


class DisqualificationReasonRequiredError(Exception):
    pass


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Candidate:
    candidate_id: str
    full_name: str
    source: str
    licensing_status: str
    stage: str
    disqualification_reason: str | None = None
    stage_history: list = field(default_factory=list)


class RecruitingPipeline:
    def __init__(self, config: dict | None = None):
        self.config = config or _load_config()
        self.stages: list[str] = self.config["stages"]
        self.terminal_stages: list[str] = self.config["terminal_stages"]
        self.disqualification_required_for: list[str] = self.config["disqualification_reason_required_for"]
        self.valid_disqualification_reasons: list[str] = self.config["disqualification_reasons"]
        self.candidates: dict[str, Candidate] = {}

    def add_candidate(self, full_name: str, source: str, licensing_status: str) -> Candidate:
        candidate = Candidate(
            candidate_id=str(uuid.uuid4()),
            full_name=full_name,
            source=source,
            licensing_status=licensing_status,
            stage=self.stages[0],
            stage_history=[self.stages[0]],
        )
        self.candidates[candidate.candidate_id] = candidate
        return candidate

    def move_stage(self, candidate_id: str, new_stage: str, disqualification_reason: str | None = None) -> Candidate:
        candidate = self.candidates[candidate_id]
        if new_stage not in self.stages:
            raise InvalidRecruitingStageError(f"'{new_stage}' is not a defined recruiting pipeline stage.")

        if new_stage in self.disqualification_required_for:
            if not disqualification_reason or disqualification_reason not in self.valid_disqualification_reasons:
                raise DisqualificationReasonRequiredError(
                    f"A valid disqualification_reason is required to move a candidate to '{new_stage}'. "
                    f"Valid reasons: {self.valid_disqualification_reasons}"
                )
            candidate.disqualification_reason = disqualification_reason

        candidate.stage = new_stage
        candidate.stage_history.append(new_stage)
        return candidate

    def by_stage(self) -> dict:
        buckets: dict[str, list[Candidate]] = {stage: [] for stage in self.stages}
        for candidate in self.candidates.values():
            buckets[candidate.stage].append(candidate)
        return buckets
