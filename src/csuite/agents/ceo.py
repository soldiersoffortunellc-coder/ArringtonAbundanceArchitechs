"""
Chief Executive Officer (CEO) — the orchestrating agent. Reviews every other
C-suite agent's report each cycle, decides strategic focus, and holds the
one authority no one else does: engaging the global pause switch.
"""

from __future__ import annotations

from csuite.agents.base import BaseAgent


class CEOAgent(BaseAgent):
    name = "ceo"
    title = "Chief Executive Officer"
    mission = "Set strategic direction, resolve cross-functional conflicts, and protect the business from unauthorized risk."
    kpis_owned = ["90_day_target_progress_pct", "open_executive_escalations"]
    ghl_authority = []  # authorizes; does not itself issue GHL directives

    def run(self, context: dict):
        """
        context = {
            "csuite_reports": {"cro": <dict>, "cmo": <dict>, "coo": <dict>, "cfo": <dict>, "cto": <dict>, "cco": <dict>},
            "target_90_day_value": float,
        }
        """
        report = self.new_report()
        csuite_reports = context.get("csuite_reports", {})

        all_escalations = []
        for agent_name, agent_report in csuite_reports.items():
            for e in agent_report.get("escalations", []):
                all_escalations.append(f"[{agent_name.upper()}] {e}")

        report.escalations = all_escalations
        report.kpis["open_executive_escalations"] = len(all_escalations)

        cro_report = csuite_reports.get("cro", {})
        cash_collected = cro_report.get("kpis", {}).get("cash_collected")
        target = context.get("target_90_day_value")
        if cash_collected is not None and target:
            report.kpis["90_day_target_progress_pct"] = round(cash_collected / target, 4)
            report.decisions.append(
                f"Cash collected of ${cash_collected:,.2f} represents "
                f"{cash_collected / target:.1%} of the ${target:,.2f} modeled 90-day target "
                "(a planning benchmark, not a guarantee)."
            )

        if len(all_escalations) >= 3:
            report.decisions.append(
                f"{len(all_escalations)} open cross-functional escalations this cycle — "
                "convening C-suite review before approving new client acquisition volume."
            )

        return report
