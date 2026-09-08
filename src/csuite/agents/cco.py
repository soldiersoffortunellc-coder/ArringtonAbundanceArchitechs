"""Chief Client Officer (CCO) — the C-suite escalation point for client health, above the Client Success and Retention Director."""

from __future__ import annotations

from csuite.agents.base import BaseAgent


class CCOAgent(BaseAgent):
    name = "cco"
    title = "Chief Client Officer"
    mission = "Own the client experience end-to-end: escalate systemic retention risk and approve reputation-facing asks."
    kpis_owned = ["net_revenue_retention_signal", "clients_requiring_executive_intervention"]
    ghl_authority = []

    def run(self, context: dict):
        """
        context = {
            "client_success_report": <AgentReport.to_dict() from ClientSuccessRetentionDirectorAgent>,
            "high_risk_threshold": int,  # number of risk signals that triggers executive escalation
        }
        """
        report = self.new_report()
        cs_report = context.get("client_success_report", {})
        threshold = context.get("high_risk_threshold", 2)

        at_risk = cs_report.get("kpis", {}).get("clients_at_risk", [])
        needs_exec = [c for c in at_risk if len(c.get("risk_signals", [])) >= threshold]

        for c in needs_exec:
            report.escalations.append(
                f"EXECUTIVE ESCALATION: tenant '{c['tenant_id']}' has {len(c['risk_signals'])} concurrent "
                f"risk signals ({c['risk_signals']}) — requires CCO-level intervention plan, not just a team alert."
            )

        healthy = cs_report.get("kpis", {}).get("clients_healthy", [])
        total = len(at_risk) + len(healthy)
        report.kpis["clients_requiring_executive_intervention"] = [c["tenant_id"] for c in needs_exec]
        report.kpis["net_revenue_retention_signal"] = round(len(healthy) / total, 4) if total else None
        return report
