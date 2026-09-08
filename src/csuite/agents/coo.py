"""Chief Operating Officer (COO) — owns fulfillment capacity, snapshot release, and delivery quality."""

from __future__ import annotations

from csuite.agents.base import BaseAgent


class COOAgent(BaseAgent):
    name = "coo"
    title = "Chief Operating Officer"
    mission = "Protect implementation capacity, delivery quality, and time-to-launch across every active onboarding."
    kpis_owned = ["implementation_capacity_used_pct", "avg_time_to_launch_days", "qa_pass_rate"]
    ghl_authority = []  # approves releases; does not itself write to GHL

    def run(self, context: dict):
        """
        context = {
            "active_implementations": int,
            "max_capacity": int,
            "time_to_launch_days_by_client": [float, ...],
            "qa_results": [{"tenant_id": str, "passed": bool}, ...],
        }
        """
        report = self.new_report()

        active = context.get("active_implementations", 0)
        capacity = context.get("max_capacity", 0)
        utilization = round(active / capacity, 4) if capacity else None
        report.kpis["implementation_capacity_used_pct"] = utilization

        if utilization is not None and utilization >= 0.9:
            report.escalations.append(
                f"Implementation capacity at {utilization:.0%} — recommend adding fulfillment capacity "
                "before accepting more Closed Won deals."
            )

        durations = context.get("time_to_launch_days_by_client", [])
        report.kpis["avg_time_to_launch_days"] = round(sum(durations) / len(durations), 2) if durations else None

        qa_results = context.get("qa_results", [])
        passed = [r for r in qa_results if r.get("passed")]
        report.kpis["qa_pass_rate"] = round(len(passed) / len(qa_results), 4) if qa_results else None
        for r in qa_results:
            if not r.get("passed"):
                report.escalations.append(f"QA failed for tenant '{r.get('tenant_id')}' — launch blocked until resolved.")

        return report
