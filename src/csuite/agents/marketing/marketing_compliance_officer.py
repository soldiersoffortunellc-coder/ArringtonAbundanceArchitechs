"""Marketing Compliance Officer — reports to the CMO."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.marketing.compliance import ComplianceEngine, RISK_HIGH, RISK_PROHIBITED


class MarketingComplianceOfficerAgent(BaseAgent):
    name = "marketing_compliance_officer"
    title = "Marketing Compliance Officer"
    mission = "Review every script, caption, claim, and CTA; assign risk; block unsupported claims; require human approval for regulated content. Not legal, tax, or regulatory advice."
    kpis_owned = ["reviews_completed", "prohibited_blocked", "human_approval_required_count"]
    ghl_authority = []

    def __init__(self, *args, engine: ComplianceEngine | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine or ComplianceEngine()

    def run(self, context: dict):
        """
        context = {
            "script_version": ScriptVersion, "platforms": [str], "product": str | None,
            "campaign_type": str | None, "manual_flags": set[str], "is_ai_clone": bool,
            "within_first_30_days": bool,
        }
        """
        report = self.new_report()
        script = context["script_version"]

        review = self.engine.review(
            script, platforms=context.get("platforms", []), product=context.get("product"),
            campaign_type=context.get("campaign_type"), manual_flags=context.get("manual_flags"),
            is_ai_clone=context.get("is_ai_clone", True), within_first_30_days=context.get("within_first_30_days", False),
        )

        report.decisions.append(f"Compliance review for campaign {review.campaign_id}: risk={review.risk_level}, human_approval_required={review.requires_human_approval}.")
        if review.risk_level == RISK_PROHIBITED:
            report.escalations.append(f"BLOCKED — prohibited phrases found: {review.blocked_phrases_found}")
        elif review.risk_level == RISK_HIGH:
            report.escalations.append(f"HIGH risk — categories detected: {review.detected_categories}. Human approval required.")

        report.kpis["reviews_completed"] = 1
        report.kpis["prohibited_blocked"] = 1 if review.risk_level == RISK_PROHIBITED else 0
        report.kpis["human_approval_required_count"] = 1 if review.requires_human_approval else 0
        report.kpis["compliance_review"] = review
        return report
