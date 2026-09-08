"""Chief Financial Officer (CFO) — owns margin controls, billing integrity, and pricing discipline."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.revenue.margin import ClientProfitability
from csuite.platform.billing import BillingLedger


class CFOAgent(BaseAgent):
    name = "cfo"
    title = "Chief Financial Officer"
    mission = "Protect gross margin per account and keep contracted, invoiced, and collected revenue clearly separated."
    kpis_owned = ["accounts_below_margin", "average_gross_margin_pct", "accounts_receivable"]
    ghl_authority = ["create_billing_event"]

    def __init__(self, *args, profitability: ClientProfitability | None = None, billing_ledger: BillingLedger | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profitability = profitability or ClientProfitability()
        self.billing_ledger = billing_ledger or BillingLedger()

    def run(self, context: dict):
        """
        context = {
            "accounts": [ {tenant_id, setup_revenue, monthly_revenue, software_cost, ai_usage_cost,
                            phone_cost, email_cost, sms_cost, integration_cost, labor_hours,
                            hourly_labor_rate, onboarding_cost, support_cost}, ... ],
            "billing_events": [ {tenant_id, event_type, amount, is_recurring}, ... ],
        }
        """
        self._guard()
        report = self.new_report()

        margin_results = []
        below_margin = []
        for account in context.get("accounts", []):
            result = self.profitability.compute(**account)
            margin_results.append(result)
            if result["below_required_margin"]:
                below_margin.append(result["tenant_id"])
                report.escalations.append(result["alert"].message)

        report.kpis["accounts_below_margin"] = below_margin
        if margin_results:
            report.kpis["average_gross_margin_pct"] = round(
                sum(r["gross_margin_pct"] for r in margin_results) / len(margin_results), 4
            )

        for event in context.get("billing_events", []):
            self.billing_ledger.record(**event)
            if self.adapter is not None:
                action = self.adapter.create_billing_event(
                    location_id=event.get("location_id", "unknown"),
                    event_type=event["event_type"],
                    amount=event["amount"],
                )
                report.directives_issued.append(action.action_id)

        billing_summary = self.billing_ledger.summary()
        report.kpis.update(billing_summary)
        report.decisions.append(
            f"Accounts receivable stands at ${billing_summary['accounts_receivable']:,.2f} "
            f"(invoiced ${billing_summary['invoiced_revenue']:,.2f} minus collected ${billing_summary['cash_collected']:,.2f})."
        )

        return report
