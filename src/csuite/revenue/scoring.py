"""
Market opportunity scoring model, owned by the Market Opportunity Analyst
agent. Twelve weighted factors, each scored 1-10 by the analyst (human or
upstream research agent), producing a single comparable score per industry
vertical so the CRO can rank/activate/pause/reject verticals.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FACTORS = [
    "pain_urgency",
    "financial_impact",
    "ability_to_pay",
    "ease_of_reaching_decision_makers",
    "sales_cycle_length",          # scored such that 10 = short/fast cycle
    "repeatability",
    "ghl_compatibility",
    "ai_automation_potential",
    "compliance_complexity",       # scored such that 10 = low complexity
    "retention_potential",
    "expansion_revenue",
    "referral_potential",
]

DEFAULT_WEIGHTS: dict[str, float] = {factor: 1.0 for factor in FACTORS}

RECOMMENDATION_THRESHOLDS = {
    "activate": 7.5,
    "test": 6.0,
    "pause": 4.0,
    # anything below "pause" threshold -> reject
}


@dataclass
class VerticalScore:
    industry: str
    scores: dict
    weights: dict
    weighted_total: float
    max_possible: float
    normalized_score: float  # 0-10 scale
    recommendation: str
    notes: list = field(default_factory=list)


class OpportunityScorer:
    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or dict(DEFAULT_WEIGHTS)
        missing = set(FACTORS) - set(self.weights)
        if missing:
            raise ValueError(f"Weights missing for factors: {missing}")

    def score(self, industry: str, scores: dict[str, float], notes: list[str] | None = None) -> VerticalScore:
        missing = set(FACTORS) - set(scores)
        if missing:
            raise ValueError(f"Scores missing for factors: {missing}")
        for factor, value in scores.items():
            if not (0 <= value <= 10):
                raise ValueError(f"Score for '{factor}' must be between 0 and 10 (got {value}).")

        weighted_total = sum(scores[f] * self.weights[f] for f in FACTORS)
        max_possible = sum(10 * self.weights[f] for f in FACTORS)
        normalized = (weighted_total / max_possible) * 10 if max_possible else 0.0

        if normalized >= RECOMMENDATION_THRESHOLDS["activate"]:
            recommendation = "ACTIVATE"
        elif normalized >= RECOMMENDATION_THRESHOLDS["test"]:
            recommendation = "TEST"
        elif normalized >= RECOMMENDATION_THRESHOLDS["pause"]:
            recommendation = "PAUSE"
        else:
            recommendation = "REJECT"

        return VerticalScore(
            industry=industry,
            scores=dict(scores),
            weights=dict(self.weights),
            weighted_total=weighted_total,
            max_possible=max_possible,
            normalized_score=round(normalized, 2),
            recommendation=recommendation,
            notes=notes or [],
        )

    def rank(self, scored_verticals: list[VerticalScore]) -> list[VerticalScore]:
        return sorted(scored_verticals, key=lambda v: v.normalized_score, reverse=True)
