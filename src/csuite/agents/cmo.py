"""Chief Marketing Officer (CMO) — owns campaigns, funnels, content, and brand-facing GHL publishing (dry-run by default)."""

from __future__ import annotations

from csuite.agents.base import BaseAgent


class CMOAgent(BaseAgent):
    name = "cmo"
    title = "Chief Marketing Officer"
    mission = "Drive top-of-funnel demand across outbound, inbound, referral, webinar, and database-reactivation channels."
    kpis_owned = ["campaigns_published", "leads_generated_by_channel", "cost_per_lead"]
    ghl_authority = ["publish_campaign", "create_workflow"]

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
