"""
Chief Marketing Officer (CMO) — owns campaigns, funnels, content, and
brand-facing GHL publishing (dry-run by default), AND — as of the AI Media
& Marketing Division — owns the complete AI-clone marketing-video pipeline
through 6 subordinate agents (mirrors how CROAgent directs its 6 revenue
subordinates; see docs/13-media-marketing-audit-and-plan.md).

The original `run()` method below is UNCHANGED from before the Media &
Marketing Division existed — nothing that already depends on it breaks.
`run_media_division()` is the new, additive entry point for the AI-clone
video pipeline; it coordinates the subordinates and NEVER itself approves
or publishes anything — every campaign it touches must clear
MarketingComplianceOfficer + the human ApprovalQueue gate first.
"""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.agents.marketing import (
    BrandVoiceContentStrategistAgent,
    AIVideoProductionDirectorAgent,
    MarketingComplianceOfficerAgent,
    SocialDistributionDirectorAgent,
    LeadConversionDirectorAgent,
    MarketingAnalyticsOfficerAgent,
)


class CMOAgent(BaseAgent):
    name = "cmo"
    title = "Chief Marketing Officer"
    mission = "Drive top-of-funnel demand across outbound, inbound, referral, webinar, and database-reactivation channels; own the complete AI Media & Marketing Division; never publish without satisfying every approval requirement."
    kpis_owned = ["campaigns_published", "leads_generated_by_channel", "cost_per_lead"]
    ghl_authority = ["publish_campaign", "create_workflow"]

    def __init__(self, *args, subordinates: dict[str, BaseAgent] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.subordinates = subordinates or {
            "brand_voice_content_strategist": BrandVoiceContentStrategistAgent(adapter=self.adapter, global_controls=self.global_controls),
            "ai_video_production_director": AIVideoProductionDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "marketing_compliance_officer": MarketingComplianceOfficerAgent(adapter=self.adapter, global_controls=self.global_controls),
            "social_distribution_director": SocialDistributionDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "lead_conversion_director": LeadConversionDirectorAgent(adapter=self.adapter, global_controls=self.global_controls),
            "marketing_analytics_officer": MarketingAnalyticsOfficerAgent(adapter=self.adapter, global_controls=self.global_controls),
        }

    def run_media_division(self, context: dict):
        """
        context is a dict keyed by subordinate name, each value being that
        subordinate's own context dict (see each subordinate module for shape).
        Only runs the subordinates a caller actually supplies context for —
        this lets a caller drive one campaign through one or two stages of
        the pipeline per cycle (e.g. just brand_voice_content_strategist +
        marketing_compliance_officer) rather than forcing every subordinate
        to act on every cycle.
        """
        report = self.new_report()
        subordinate_reports = {}

        for sub_name, sub_context in context.items():
            if sub_name not in self.subordinates:
                report.warnings.append(f"Unknown media-division subordinate '{sub_name}' — ignored.")
                continue
            agent = self.subordinates[sub_name]
            sub_report = agent.run(sub_context)
            subordinate_reports[sub_name] = sub_report
            report.directives_issued.extend(sub_report.directives_issued)
            report.escalations.extend(f"[{sub_name}] {e}" for e in sub_report.escalations)
            report.warnings.extend(f"[{sub_name}] {w}" for w in sub_report.warnings)

        report.decisions.append(
            f"Ran {len(subordinate_reports)} media-division subordinate(s) this cycle: {', '.join(subordinate_reports)}."
        )
        report.kpis["subordinate_reports"] = {name: r.to_dict() for name, r in subordinate_reports.items()}
        # raw (non-serialized) reports are also kept, since several subordinates
        # return live objects (ScriptVersion, ComplianceReview, ...) in their kpis
        # that a caller chaining stages together needs, not just the dict view.
        report.kpis["subordinate_reports_raw"] = subordinate_reports
        return report

    def run(self, context: dict):
        """
        context = {
            "location_id": str,
            "campaigns": [{"name": str, "channel": str}, ...],
            "leads_by_channel": {"outbound": int, "referral": int, ...},  # optional, reported facts
        }
        """
        self._guard()
        report = self.new_report()
        location_id = context.get("location_id", "unprovisioned")

        published = []
        for campaign in context.get("campaigns", []):
            if self.adapter is not None:
                action = self.adapter.publish_campaign(location_id, campaign["name"])
                report.directives_issued.append(action.action_id)
            published.append(campaign["name"])
            report.decisions.append(f"Published campaign '{campaign['name']}' on channel '{campaign.get('channel', 'unspecified')}' (dry-run unless live-authorized).")

        report.kpis["campaigns_published"] = published
        leads_by_channel = context.get("leads_by_channel", {})
        report.kpis["leads_generated_by_channel"] = leads_by_channel
        report.kpis["total_leads_generated"] = sum(leads_by_channel.values()) if leads_by_channel else 0
        return report
