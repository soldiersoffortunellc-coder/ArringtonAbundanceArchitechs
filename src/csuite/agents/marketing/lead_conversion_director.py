"""Lead-Conversion Director — reports to the CMO."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from csuite.agents.base import BaseAgent
from csuite.marketing.models import LeadAttribution

CONFIG_ROOT = Path(__file__).resolve().parents[4] / "config" / "marketing"


def _load_pipeline(pipeline_key: str) -> dict:
    with open(CONFIG_ROOT / "pipelines" / f"{pipeline_key}.json", "r", encoding="utf-8") as fh:
        return json.load(fh)


class LeadConversionDirectorAgent(BaseAgent):
    name = "lead_conversion_director"
    title = "Lead-Conversion Director"
    mission = "Connect every campaign to the correct GHL destination (pipeline, calendar, workflow) and route leads by intent, location, license status, and lead score."
    kpis_owned = ["leads_routed", "attributions_recorded"]
    ghl_authority = ["tag_contact", "create_opportunity", "update_opportunity_stage"]

    def run(self, context: dict):
        """
        context = {
            "campaign_id": str, "location_id": str, "contact_id": str, "cta_key": str,
            "pipeline_key": str, "target_stage_key": str, "value": float,
            "routing_facts": {"license_status": ..., "experience": ..., "lead_score": ..., "requested_service": ...},
        }
        Every video/campaign must have a measurable campaign_id, CTA, conversion
        destination, and follow-up process — enforced by requiring pipeline_key/target_stage_key here.
        """
        self._guard()
        report = self.new_report()

        pipeline = _load_pipeline(context["pipeline_key"])
        stage = next((s for s in pipeline["stages"] if s["key"] == context["target_stage_key"]), None)
        if stage is None:
            report.escalations.append(f"'{context['target_stage_key']}' is not a valid stage in pipeline '{context['pipeline_key']}'.")
            return report

        destination_summary = f"{pipeline['pipeline_name']} -> {stage['name']}"

        if self.adapter is not None:
            tag_action = self.adapter.tag_contact(context["location_id"], context["contact_id"], f"campaign:{context['campaign_id']}")
            report.directives_issued.append(tag_action.action_id)
            opp_action = self.adapter.create_opportunity(context["location_id"], pipeline["pipeline_name"], stage["name"], context.get("value", 0))
            report.directives_issued.append(opp_action.action_id)

        attribution = LeadAttribution(
            attribution_id=str(uuid.uuid4()), campaign_id=context["campaign_id"], contact_id=context["contact_id"],
            cta_key=context["cta_key"], destination=destination_summary,
        )

        report.decisions.append(
            f"Routed contact {context['contact_id']} from campaign {context['campaign_id']} (CTA '{context['cta_key']}') "
            f"to {destination_summary} based on: {context.get('routing_facts', {})}."
        )
        report.kpis["leads_routed"] = 1
        report.kpis["attributions_recorded"] = 1
        report.kpis["lead_attribution"] = attribution
        report.kpis["ghl_destination_summary"] = destination_summary
        return report
