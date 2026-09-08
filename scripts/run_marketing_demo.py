#!/usr/bin/env python3
"""
Walks ONE sample campaign through the AI Media & Marketing Division
pipeline, in full dry-run/mock mode, and stops the moment it reaches
HUMAN_APPROVAL_REQUIRED — proving the mandatory approval gate concretely
rather than just asserting it in a test. Nothing is published, no video
provider is called live, no message is sent, and no GHL data is touched.

Usage:
    python3 scripts/run_marketing_demo.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from csuite.ghl.adapter import GHLAdapter  # noqa: E402
from csuite.marketing.models import new_campaign  # noqa: E402
from csuite.marketing.store import CampaignStore  # noqa: E402
from csuite.marketing.approval_queue import ApprovalQueue  # noqa: E402
from csuite.agents.marketing.brand_voice_content_strategist import BrandVoiceContentStrategistAgent  # noqa: E402
from csuite.agents.marketing.marketing_compliance_officer import MarketingComplianceOfficerAgent  # noqa: E402


def main() -> None:
    adapter = GHLAdapter(dry_run=True)
    store = CampaignStore()
    queue = ApprovalQueue(store)

    # 1. IDEA -> BRIEF_CREATED
    campaign = new_campaign("open_doors_financial_group", "coach_rashon", "leadership_development", is_ai_clone=True)
    sm = store.add_campaign(campaign)
    sm.transition("BRIEF_CREATED", actor="cmo_agent", reason="Weekly content calendar: leadership pillar slot")

    # 2. SCRIPT_DRAFTED — Brand Voice & Content Strategist
    bv_agent = BrandVoiceContentStrategistAgent(adapter=adapter)
    bv_report = bv_agent.run({
        "campaign_id": campaign.campaign_id,
        "brand_id": "coach_rashon",
        "platforms": ["instagram", "tiktok", "youtube_shorts"],
        "key_messages": ["Ownership beats income. Build something that outlasts you."],
        "cta_text": "DM WEALTH",
    })
    script = bv_report.kpis["script_version"]
    store.add_script_version(script)
    sm.transition("SCRIPT_DRAFTED", actor="brand_voice_content_strategist", reason="Initial draft complete", content_version=script.version_id)

    # 3. BRAND_REVIEW -> COMPLIANCE_REVIEW (CMO approves voice/pillar fit)
    sm.transition("BRAND_REVIEW", actor="cmo_agent", reason="Submitted for brand review")
    sm.transition("COMPLIANCE_REVIEW", actor="cmo_agent", reason="Brand review passed — voice and pillar fit confirmed", content_version=script.version_id)

    # 4. Marketing Compliance Officer review
    compliance_agent = MarketingComplianceOfficerAgent()
    compliance_report = compliance_agent.run({
        "script_version": script, "platforms": ["instagram", "tiktok", "youtube_shorts"],
        "campaign_type": "recruiting", "is_ai_clone": True, "within_first_30_days": True,
    })
    review = compliance_report.kpis["compliance_review"]
    store.add_compliance_review(review)

    # 5. Route per the mandatory gate: every AI-clone post in the first 30 days requires human approval,
    #    regardless of risk level — this demo NEVER auto-approves.
    if review.requires_human_approval:
        sm.transition("HUMAN_APPROVAL_REQUIRED", actor="marketing_compliance_officer", reason=f"risk={review.risk_level}; AI-clone within first 30 days", content_version=script.version_id)
    else:
        sm.transition("REVISION_REQUIRED", actor="marketing_compliance_officer", reason="compliance issue found", content_version=script.version_id)

    queue.enqueue(
        campaign, script, review,
        destination_summary="Licensed Agent Recruiting -> New Lead (pipeline_key=licensed_agent_recruiting, stage_key=new_lead)",
        agent_recommendations=["Lead with the ownership hook — matches Coach Rashon's recurring themes."],
    )

    print("=" * 70)
    print(f"Campaign {campaign.campaign_id} is now in state: {sm.state}")
    print("=" * 70)
    print(f"Risk level: {review.risk_level}")
    print(f"Requires human approval: {review.requires_human_approval}")
    print(f"Required disclosures: {review.required_disclosures}")
    print(f"Pending approval queue items: {len(queue.pending_items())}")
    print()
    print("This campaign STOPS here. No video was generated, nothing was scheduled")
    print("or published, and no GHL data was touched. To move it forward, an")
    print("'executive_approver' role must call ApprovalQueue.approve(...) —")
    print("see docs/16-media-marketing-setup-and-checklist.md.")
    print()
    print("Full audit trail:")
    for event in campaign.audit_trail:
        print(f"  {event.previous_state} -> {event.new_state}  (actor={event.actor}, reason='{event.reason}')")

    out_path = os.path.join(os.path.dirname(__file__), "..", "config", "marketing", "sample_campaigns", "sample_draft_campaign.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({
            "campaign_id": campaign.campaign_id,
            "state": sm.state,
            "business": campaign.business,
            "brand_id": campaign.brand_id,
            "pillar_id": campaign.pillar_id,
            "script": {"hook": script.hook, "body": script.body, "cta_text": script.cta_text, "unresolved_fields": script.unresolved_fields},
            "compliance_review": {"risk_level": review.risk_level, "requires_human_approval": review.requires_human_approval, "required_disclosures": review.required_disclosures},
            "audit_trail": [{"previous_state": e.previous_state, "new_state": e.new_state, "actor": e.actor, "reason": e.reason} for e in campaign.audit_trail],
        }, fh, indent=2)
    print(f"\nWrote sample campaign snapshot to {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
