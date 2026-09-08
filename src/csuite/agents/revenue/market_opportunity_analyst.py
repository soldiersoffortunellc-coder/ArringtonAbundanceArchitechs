"""Market Opportunity Analyst — reports to the CRO."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.revenue.scoring import OpportunityScorer


class MarketOpportunityAnalystAgent(BaseAgent):
    name = "market_opportunity_analyst"
    title = "Market Opportunity Analyst"
    mission = "Research and score industries; separate urgent problems from optional improvements."
    kpis_owned = ["vertical_normalized_score", "verticals_activated", "verticals_rejected"]
    ghl_authority = []  # research/analysis role — issues no direct GHL writes

    def __init__(self, *args, scorer: OpportunityScorer | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.scorer = scorer or OpportunityScorer()

    def run(self, context: dict):
        """
        context = {
            "vertical_scores": {
                "insurance_agency": {factor: score, ...},
                "real_estate": {...},
                "home_services": {...},
                ...
            }
        }
        """
        report = self.new_report()
        vertical_scores = context.get("vertical_scores", {})

        scored = []
        for industry, factor_scores in vertical_scores.items():
            vs = self.scorer.score(industry, factor_scores)
            scored.append(vs)
            report.decisions.append(f"{industry}: {vs.recommendation} (score={vs.normalized_score}/10)")

        ranked = self.scorer.rank(scored)
        report.kpis["ranked_verticals"] = [
            {"industry": v.industry, "score": v.normalized_score, "recommendation": v.recommendation}
            for v in ranked
        ]
        report.kpis["activate"] = [v.industry for v in ranked if v.recommendation == "ACTIVATE"]
        report.kpis["test"] = [v.industry for v in ranked if v.recommendation == "TEST"]
        report.kpis["pause"] = [v.industry for v in ranked if v.recommendation == "PAUSE"]
        report.kpis["reject"] = [v.industry for v in ranked if v.recommendation == "REJECT"]
        return report
