"""
Chief Revenue Officer (CRO) — owns commercialization and revenue strategy.

Coordinates the six revenue subordinate agents and never represents modeled
revenue as a guaranteed outcome.
"""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.agents.revenue import (
    MarketOpportunityAnalystAgent,
    ProductizationDirectorAgent,
    SalesDirectorAgent,
    ClientOnboardingDirectorAgent,
    ClientSuccessRetentionDirectorAgent,
    RevenueOperationsAnalystAgent,
)


class CROAgent(BaseAgent):
    name = "cro"
    title = "Chief Revenue Officer"
    mission = (
        "Identify urgent, profitable industry problems; design offers, pricing, onboarding and expansion; "
        "coordinate marketing, sales, fulfillment, client success and finance agents; track revenue truthfully."
    )
    kpis_owned = ["contracted_revenue", "cash_collected", "mrr", "gross_margin", "cac", "retention", "churn"]
    ghl_authority = []  # the CRO directs subordinates; subordinates hold the actual GHL authority

    def __init__(self, *args, subordinates: dict[str, BaseAgent] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.subordinates = subordinates or {
            "market_opportunity_analyst": MarketOpportunityAnalystAgent(adapter=self.adapter, global_controls=self.global_controls),
            "productization_director": ProductizationDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "sales_director": SalesDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "client_onboarding_director": ClientOnboardingDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "client_success_retention_director": ClientSuccessRetentionDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "revenue_operations_analyst": RevenueOperationsAnalystAgent(adapter=self.adapter, global_controls=self.global_controls),
        }

    def run(self, context: dict):
        """
        context is a dict keyed by subordinate name, each value being that
        subordinate's own context dict (see each subordinate module for shape).
        """
        report = self.new_report()
        subordinate_reports = {}

        for sub_name, agent in self.subordinates.items():
            sub_context = context.get(sub_name, {})
            sub_report = agent.run(sub_context)
            subordinate_reports[sub_name] = sub_report.to_dict()
            report.directives_issued.extend(sub_report.directives_issued)
            report.escalations.extend(f"[{sub_name}] {e}" for e in sub_report.escalations)
            report.warnings.extend(f"[{sub_name}] {w}" for w in sub_report.warnings)

        report.decisions.append(
            f"Coordinated {len(self.subordinates)} revenue subordinate agents this cycle: "
            f"{', '.join(self.subordinates)}."
        )
        report.kpis["subordinate_reports"] = subordinate_reports

        rev_ops = subordinate_reports.get("revenue_operations_analyst", {}).get("kpis", {})
        for key in ("contracted_revenue", "cash_collected", "monthly_recurring_revenue", "gross_margin"):
            if key in rev_ops:
                report.kpis[key] = rev_ops[key]

        return report
