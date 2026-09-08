"""Revenue Operations Analyst — reports to the CRO. The single source of truth for revenue numbers."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.platform.billing import BillingLedger
from csuite.revenue.financial_model import FinancialModel


class RevenueOperationsAnalystAgent(BaseAgent):
    name = "revenue_operations_analyst"
    title = "Revenue Operations Analyst"
    mission = "Track every revenue, pipeline, and retention metric without conflating contracted and collected revenue."
    kpis_owned = [
        "leads_generated", "qualified_appointments", "show_rate", "proposal_rate", "close_rate",
        "setup_revenue", "monthly_recurring_revenue", "contracted_revenue", "cash_collected",
        "refunds", "gross_margin", "customer_acquisition_cost", "payback_period", "churn",
        "net_revenue_retention", "time_to_launch", "support_burden",
    ]
    ghl_authority = []

    def __init__(self, *args, billing_ledger: BillingLedger | None = None, financial_model: FinancialModel | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.billing_ledger = billing_ledger or BillingLedger()
        self.financial_model = financial_model or FinancialModel()

    def run(self, context: dict):
        """
        context = {
            "funnel": {"leads_generated": int, "qualified_appointments": int, "shows": int,
                       "proposals_sent": int, "closed_won": int, "closed_total": int},
            "scenario": "target" | "conservative" | "aggressive",
        }
        """
        report = self.new_report()
        funnel = context.get("funnel", {})

        leads = funnel.get("leads_generated", 0)
        appts = funnel.get("qualified_appointments", 0)
        shows = funnel.get("shows", 0)
        proposals = funnel.get("proposals_sent", 0)
        closed_won = funnel.get("closed_won", 0)
        closed_total = funnel.get("closed_total", 0)

        report.kpis["leads_generated"] = leads
        report.kpis["qualified_appointments"] = appts
        report.kpis["show_rate"] = round(shows / appts, 4) if appts else None
        report.kpis["proposal_rate"] = round(proposals / shows, 4) if shows else None
        report.kpis["close_rate"] = round(closed_won / closed_total, 4) if closed_total else None

        billing = self.billing_ledger.summary()
        report.kpis.update(billing)
        report.decisions.append(
            "Contracted revenue and cash collected are tracked as two separate figures "
            f"(${billing['contracted_revenue']:,.2f} contracted vs ${billing['cash_collected']:,.2f} collected) "
            "and must never be reported as one number."
        )

        scenario_name = context.get("scenario", "target")
        scenario = self.financial_model.scenario(scenario_name)
        report.kpis["modeled_90_day_scenario"] = scenario
        report.warnings.append(
            f"Scenario '{scenario_name}' combined modeled 90-day value of "
            f"${scenario['combined_modeled_90_day_value']:,.2f} is a planning input, not a guaranteed result."
        )

        return report
