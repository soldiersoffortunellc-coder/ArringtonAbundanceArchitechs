import unittest

from csuite.marketing.models import new_campaign, ScriptVersion, ComplianceReview
from csuite.marketing.store import CampaignStore
from csuite.marketing.approval_queue import ApprovalQueue
from csuite.platform.permissions import PermissionDeniedError


def _prep_campaign_at_human_approval_required(store: CampaignStore):
    campaign = new_campaign("open_doors_financial_group", "open_doors_financial_group", "life_insurance_education")
    sm = store.add_campaign(campaign)
    for state in ("BRIEF_CREATED", "SCRIPT_DRAFTED", "BRAND_REVIEW", "COMPLIANCE_REVIEW", "HUMAN_APPROVAL_REQUIRED"):
        sm.transition(state, actor="test", reason="progressing")

    script = ScriptVersion(version_id="v1", campaign_id=campaign.campaign_id, version_number=1,
                            hook="h", body="b", cta_text="c", platform_captions={}, hashtags={})
    store.add_script_version(script)
    review = ComplianceReview(review_id="r1", campaign_id=campaign.campaign_id, version_id="v1", risk_level="HIGH", requires_human_approval=True)
    store.add_compliance_review(review)
    return campaign, script, review


class TestApprovalQueue(unittest.TestCase):
    def setUp(self):
        self.store = CampaignStore()
        self.queue = ApprovalQueue(self.store)

    def test_enqueued_item_carries_every_required_display_field(self):
        campaign, script, review = _prep_campaign_at_human_approval_required(self.store)
        item = self.queue.enqueue(
            campaign, script, review, video_asset_url="mock://video.mp4",
            destination_summary="Consumer Financial Education -> New Inquiry",
            agent_recommendations=["Lead with the hook variant"], scheduled_publishing_time=1234.0,
        )
        self.assertEqual(item.campaign_id, campaign.campaign_id)
        self.assertEqual(item.script, script)
        self.assertEqual(item.compliance_review, review)
        self.assertIsNotNone(item.video_asset_url)
        self.assertIsNotNone(item.destination_summary)
        self.assertTrue(item.agent_recommendations)
        self.assertIsNotNone(item.scheduled_publishing_time)

    def test_content_operator_cannot_approve(self):
        campaign, script, review = _prep_campaign_at_human_approval_required(self.store)
        self.queue.enqueue(campaign, script, review)
        with self.assertRaises(PermissionDeniedError):
            self.queue.approve(campaign.campaign_id, role="content_operator", actor_id="u1")

    def test_executive_approver_can_approve(self):
        campaign, script, review = _prep_campaign_at_human_approval_required(self.store)
        self.queue.enqueue(campaign, script, review)
        record = self.queue.approve(campaign.campaign_id, role="executive_approver", actor_id="u1", reason="looks good")
        self.assertEqual(record.decision, "APPROVED")
        self.assertEqual(self.store.get_campaign(campaign.campaign_id).state, "APPROVED")

    def test_compliance_reviewer_can_reject_but_not_approve(self):
        campaign, script, review = _prep_campaign_at_human_approval_required(self.store)
        self.queue.enqueue(campaign, script, review)
        with self.assertRaises(PermissionDeniedError):
            self.queue.approve(campaign.campaign_id, role="compliance_reviewer", actor_id="u2")
        record = self.queue.reject(campaign.campaign_id, role="compliance_reviewer", actor_id="u2", reason="unsupported claim")
        self.assertEqual(record.decision, "REJECTED")

    def test_approval_only_transitions_a_campaign_actually_awaiting_approval(self):
        """An API call succeeding does not mean a campaign has been approved: approving a
        campaign NOT sitting in HUMAN_APPROVAL_REQUIRED must fail at the state-machine level."""
        campaign = new_campaign("open_doors_financial_group", "coach_rashon", "leadership_development")
        self.store.add_campaign(campaign)  # still in IDEA
        script = ScriptVersion(version_id="v1", campaign_id=campaign.campaign_id, version_number=1,
                                hook="h", body="b", cta_text="c", platform_captions={}, hashtags={})
        review = ComplianceReview(review_id="r1", campaign_id=campaign.campaign_id, version_id="v1", risk_level="LOW")
        self.queue.enqueue(campaign, script, review)
        with self.assertRaises(Exception):
            self.queue.approve(campaign.campaign_id, role="executive_approver", actor_id="u1")

    def test_pending_items_only_lists_campaigns_awaiting_approval(self):
        campaign, script, review = _prep_campaign_at_human_approval_required(self.store)
        self.queue.enqueue(campaign, script, review)
        self.assertEqual(len(self.queue.pending_items()), 1)
        self.queue.approve(campaign.campaign_id, role="executive_approver", actor_id="u1")
        self.assertEqual(len(self.queue.pending_items()), 0)


if __name__ == "__main__":
    unittest.main()
