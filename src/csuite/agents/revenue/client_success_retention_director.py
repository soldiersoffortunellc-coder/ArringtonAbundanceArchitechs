"""Client Success and Retention Director — reports to the CRO."""

from __future__ import annotations

from csuite.agents.base import BaseAgent

CHURN_RISK_THRESHOLDS = {
    "adoption_pct_low": 0.30,
    "appointments_last_30d_low": 3,
    "engagement_score_low": 0.40,
}


class ClientSuccessRetentionDirectorAgent(BaseAgent):
    name = "client_success_retention_director"
    title = "Client Success and Retention Director"
    mission = "Monitor adoption and results, trigger interventions on decline, manage renewal/expansion/referrals."
    kpis_owned = ["clients_at_risk", "clients_healthy", "expansion_opportunities"]
    ghl_authority = ["send_notification"]

    def run(self, context: dict):
        """
        context = {
            "client_health": [
                {"tenant_id", "adoption_pct", "appointments_last_30d", "engagement_score",
                 "failed_automations", "testimonial_permission_granted": bool}, ...
            ]
        }
        """
        self._guard()
        report = self.new_report()

        at_risk = []
        healthy = []
        expansion = []

        for record in context.get("client_health", []):
            risk_signals = []
            if record.get("adoption_pct", 1.0) < CHURN_RISK_THRESHOLDS["adoption_pct_low"]:
                risk_signals.append("low_adoption")
            if record.get("appointments_last_30d", 999) < CHURN_RISK_THRESHOLDS["appointments_last_30d_low"]:
                risk_signals.append("low_appointment_volume")
            if record.get("engagement_score", 1.0) < CHURN_RISK_THRESHOLDS["engagement_score_low"]:
                risk_signals.append("low_engagement")
            if record.get("failed_automations", 0) > 0:
                risk_signals.append("failed_automations")

            tenant_id = record["tenant_id"]
            if risk_signals:
                at_risk.append({"tenant_id": tenant_id, "risk_signals": risk_signals})
                report.escalations.append(f"Tenant '{tenant_id}' is at churn risk: {risk_signals}")
                if self.adapter is not None:
                    action = self.adapter.send_notification(
                        location_id=record.get("location_id", "unknown"),
                        channel="internal_alert",
                        to="client_success_team",
                        template="retention_intervention_trigger",
                    )
                    report.directives_issued.append(action.action_id)
            else:
                healthy.append(tenant_id)
                if record.get("engagement_score", 0) >= 0.8 and record.get("adoption_pct", 0) >= 0.8:
                    expansion.append(tenant_id)

            # testimonial/referral requests require explicit permission + compliance approval
            if record.get("testimonial_requested") and not record.get("testimonial_permission_granted"):
                report.warnings.append(
                    f"Tenant '{tenant_id}': testimonial requested but permission/compliance approval "
                    "not yet granted — request withheld."
                )

        report.kpis["clients_at_risk"] = at_risk
        report.kpis["clients_healthy"] = healthy
        report.kpis["expansion_opportunities"] = expansion
        return report
