"""
Meta (Facebook/Instagram) Lead Ads -> Insurance Recruiting Pipeline router.

How this fits GHL's real integration model: GHL's native Facebook
integration (connected in the GHL UI, verified read-only here via
GHLAdapter.fb_get_integration / fb_get_page_lead_forms) is what actually
receives the ad platform's webhook and creates the contact — there is no
public API call that "ingests a lead" directly. What this module does is
the step after that: given the raw lead-form answers (however they reach
this system — a GHL workflow webhook, a periodic form-submission poll, etc.)
it maps them onto the candidate profile the insurance recruiting funnel
needs, tags/scores the resulting contact, opens a recruiting-pipeline
candidate at the right stage, and reports which funnel
(licensed_agent_recruiting_funnel vs licensing_interest_funnel, per
config/snapshots/insurance_pack.json) the candidate should be enrolled in.

Every GHL side effect goes through the same GHLAdapter every other agent
uses, so it inherits the same dry-run-by-default guarantee: nothing here
ever reaches a real GHL account unless the caller already built the adapter
with dry_run=False, live_authorized=True.
"""

from __future__ import annotations

import json
from pathlib import Path

from csuite.ghl.adapter import GHLAdapter
from csuite.pipeline.recruiting_pipeline import RecruitingPipeline

MAPPING_PATH = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "meta_lead_ads"
    / "insurance_recruiting_form_mapping.json"
)


class IncompleteMetaLeadError(Exception):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"Meta lead is missing required fields: {missing_fields}")


class DuplicateMetaLeadError(Exception):
    def __init__(self, fb_lead_id: str):
        self.fb_lead_id = fb_lead_id
        super().__init__(f"Meta lead '{fb_lead_id}' has already been ingested.")


class UnrecognizedLicensingStatusError(Exception):
    pass


def _load_mapping() -> dict:
    with open(MAPPING_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _first_present(raw_lead: dict, candidate_keys: list[str]) -> str | None:
    for key in candidate_keys:
        if raw_lead.get(key):
            return raw_lead[key]
    return None


class MetaRecruitingLeadRouter:
    """
    Maps raw Meta Lead Ads form answers onto the insurance recruiting funnel
    and drives both the local RecruitingPipeline model and the real/dry-run
    GHLAdapter side effects (tagging the contact, opening a candidate
    opportunity) from a single ingest_lead() call.
    """

    def __init__(
        self,
        adapter: GHLAdapter,
        pipeline: RecruitingPipeline | None = None,
        mapping: dict | None = None,
    ):
        self.adapter = adapter
        self.pipeline = pipeline or RecruitingPipeline()
        self.mapping = mapping or _load_mapping()
        self._seen_fb_lead_ids: set[str] = set()

    def _map_fields(self, raw_lead: dict) -> dict:
        mapped = {}
        for internal_field, source_keys in self.mapping["field_map"].items():
            mapped[internal_field] = _first_present(raw_lead, source_keys)
        return mapped

    def _normalize_licensing_status(self, raw_value: str | None) -> str:
        if raw_value is None:
            return "unknown"
        normalized = raw_value.strip().lower()
        for status, accepted_values in self.mapping["licensing_status_values"].items():
            if normalized in [v.lower() for v in accepted_values]:
                return status
        raise UnrecognizedLicensingStatusError(
            f"Licensing status '{raw_value}' does not match any known value in "
            f"{list(self.mapping['licensing_status_values'])}. Update the mapping file "
            "if the ad form's answer options changed."
        )

    def ingest_lead(self, location_id: str, raw_lead: dict) -> dict:
        """
        raw_lead: a flat dict of the Meta lead form's field answers, plus
        attribution fields (fb_lead_id, fb_form_id, fb_page_id, fb_ad_id,
        fb_campaign_name) and, when the contact already exists in GHL
        (the normal case, since GHL's Facebook integration creates it),
        ghl_contact_id.
        """
        fb_lead_id = raw_lead.get("fb_lead_id")
        if fb_lead_id and fb_lead_id in self._seen_fb_lead_ids:
            raise DuplicateMetaLeadError(fb_lead_id)

        mapped = self._map_fields(raw_lead)
        missing = [f for f in self.mapping["required_fields"] if not mapped.get(f)]
        if missing:
            raise IncompleteMetaLeadError(missing)

        licensing_status = self._normalize_licensing_status(mapped["licensing_status"])
        funnel = self.mapping["funnel_routing"].get(licensing_status, "licensing_interest_funnel")

        candidate = self.pipeline.add_candidate(
            full_name=mapped["full_name"],
            source="meta_lead_ads",
            licensing_status=licensing_status,
        )

        contact_id = raw_lead.get("ghl_contact_id", f"pending_fb_contact_{candidate.candidate_id[:8]}")
        actions = [
            self.adapter.tag_contact(location_id, contact_id, "meta-lead-source:facebook"),
            self.adapter.tag_contact(location_id, contact_id, f"recruiting-candidate:{licensing_status}"),
            self.adapter.create_opportunity(
                location_id,
                pipeline_name=self.pipeline.config["pipeline_name"],
                stage=candidate.stage,
                value=0.0,
            ),
        ]

        if fb_lead_id:
            self._seen_fb_lead_ids.add(fb_lead_id)

        return {
            "candidate_id": candidate.candidate_id,
            "contact_id": contact_id,
            "licensing_status": licensing_status,
            "routed_funnel": funnel,
            "stage": candidate.stage,
            "attribution": {k: raw_lead.get(k) for k in self.mapping["attribution_fields_captured"]},
            "action_ids": [a.action_id for a in actions],
        }
