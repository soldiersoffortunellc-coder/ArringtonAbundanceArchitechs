"""
Client profitability controls: per-account margin calculation and alerting,
owned by the CFO agent / Revenue Operations Analyst.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MarginAlert:
    tenant_id: str
    gross_margin_pct: float
    required_margin_pct: float
    message: str


class ClientProfitability:
    def __init__(self, required_margin_pct: float = 0.50):
        self.required_margin_pct = required_margin_pct

    def compute(
        self,
        *,
        tenant_id: str,
        setup_revenue: float,
        monthly_revenue: float,
        software_cost: float,
        ai_usage_cost: float,
        phone_cost: float,
        email_cost: float,
        sms_cost: float,
        integration_cost: float,
        labor_hours: float,
        hourly_labor_rate: float,
        onboarding_cost: float,
        support_cost: float,
    ) -> dict:
        labor_cost = labor_hours * hourly_labor_rate
        monthly_direct_cost = software_cost + ai_usage_cost + phone_cost + email_cost + sms_cost + support_cost
        one_time_cost = integration_cost + labor_cost + onboarding_cost

        total_revenue = setup_revenue + monthly_revenue
        total_cost = one_time_cost + monthly_direct_cost
        gross_profit = total_revenue - total_cost
        gross_margin_pct = (gross_profit / total_revenue) if total_revenue else 0.0

        break_even_point = one_time_cost / monthly_revenue if monthly_revenue else float("inf")
        max_acceptable_cac = setup_revenue + (monthly_revenue * 3) * self.required_margin_pct

        below_required = gross_margin_pct < self.required_margin_pct
        alert = None
        if below_required:
            alert = MarginAlert(
                tenant_id=tenant_id,
                gross_margin_pct=gross_margin_pct,
                required_margin_pct=self.required_margin_pct,
                message=(
                    f"Tenant '{tenant_id}' gross margin {gross_margin_pct:.1%} is below the required "
                    f"{self.required_margin_pct:.1%} threshold."
                ),
            )

        return {
            "tenant_id": tenant_id,
            "setup_revenue": setup_revenue,
            "monthly_revenue": monthly_revenue,
            "one_time_cost": one_time_cost,
            "monthly_direct_cost": monthly_direct_cost,
            "gross_profit": gross_profit,
            "gross_margin_pct": gross_margin_pct,
            "break_even_point_months": break_even_point,
            "max_acceptable_acquisition_cost": max_acceptable_cac,
            "below_required_margin": below_required,
            "alert": alert,
        }
