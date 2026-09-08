import unittest

from csuite.marketing.models import new_campaign
from csuite.marketing.campaign_state_machine import CampaignStateMachine, InvalidCampaignTransitionError


class TestCampaignStateTransitions(unittest.TestCase):
    def setUp(self):
        self.campaign = new_campaign("open_doors_financial_group", "coach_rashon", "financial_education")
        self.sm = CampaignStateMachine(self.campaign)

    def test_starts_in_idea(self):
        self.assertEqual(self.sm.state, "IDEA")

    def test_full_happy_path_to_optimization_complete(self):
        path = [
            "BRIEF_CREATED", "SCRIPT_DRAFTED", "BRAND_REVIEW", "COMPLIANCE_REVIEW",
            "HUMAN_APPROVAL_REQUIRED", "APPROVED", "VIDEO_GENERATING", "VIDEO_REVIEW",
            "SCHEDULED", "PUBLISHED", "PERFORMANCE_TRACKING", "OPTIMIZATION_COMPLETE", "ARCHIVED",
        ]
        for state in path:
            self.sm.transition(state, actor="test", reason="progressing")
        self.assertEqual(self.sm.state, "ARCHIVED")
        self.assertTrue(self.sm.is_terminal())

    def test_cannot_skip_states(self):
        with self.assertRaises(InvalidCampaignTransitionError):
            self.sm.transition("APPROVED", actor="test", reason="skip ahead")

    def test_compliance_review_can_route_to_revision_required(self):
        self.sm.transition("BRIEF_CREATED", actor="t", reason="r")
        self.sm.transition("SCRIPT_DRAFTED", actor="t", reason="r")
        self.sm.transition("BRAND_REVIEW", actor="t", reason="r")
        self.sm.transition("COMPLIANCE_REVIEW", actor="t", reason="r")
        self.sm.transition("REVISION_REQUIRED", actor="t", reason="flagged claim")
        self.assertEqual(self.sm.state, "REVISION_REQUIRED")
        # revision loops back to redrafting, not forward
        self.sm.transition("SCRIPT_DRAFTED", actor="t", reason="revised")
        self.assertEqual(self.sm.state, "SCRIPT_DRAFTED")

    def test_human_approval_required_can_reject(self):
        for state in ("BRIEF_CREATED", "SCRIPT_DRAFTED", "BRAND_REVIEW", "COMPLIANCE_REVIEW", "HUMAN_APPROVAL_REQUIRED"):
            self.sm.transition(state, actor="t", reason="r")
        self.sm.transition("REJECTED", actor="human_approver", reason="not approved")
        self.assertTrue(self.sm.is_terminal())
        with self.assertRaises(InvalidCampaignTransitionError):
            self.sm.transition("APPROVED", actor="t", reason="cannot revive a rejected campaign")

    def test_pause_and_resume_returns_to_prior_state(self):
        self.sm.transition("BRIEF_CREATED", actor="t", reason="r")
        self.sm.transition("SCRIPT_DRAFTED", actor="t", reason="r")
        self.sm.transition("PAUSED", actor="owner", reason="emergency pause")
        self.assertEqual(self.sm.state, "PAUSED")
        self.sm.resume(actor="owner", reason="resuming")
        self.assertEqual(self.sm.state, "SCRIPT_DRAFTED")

    def test_cannot_transition_out_of_paused_except_to_resume_state(self):
        self.sm.transition("BRIEF_CREATED", actor="t", reason="r")
        self.sm.transition("PAUSED", actor="owner", reason="pause")
        with self.assertRaises(InvalidCampaignTransitionError):
            self.sm.transition("CANCELED", actor="t", reason="cannot skip past paused")

    def test_failed_video_generation_can_retry(self):
        for state in ("BRIEF_CREATED", "SCRIPT_DRAFTED", "BRAND_REVIEW", "COMPLIANCE_REVIEW",
                      "HUMAN_APPROVAL_REQUIRED", "APPROVED", "VIDEO_GENERATING"):
            self.sm.transition(state, actor="t", reason="r")
        self.sm.transition("FAILED", actor="ai_video_production_director", reason="provider timeout")
        self.sm.transition("VIDEO_GENERATING", actor="ai_video_production_director", reason="retry")
        self.assertEqual(self.sm.state, "VIDEO_GENERATING")

    def test_terminal_state_blocks_further_transitions(self):
        self.sm.transition("CANCELED", actor="t", reason="canceled early")
        with self.assertRaises(InvalidCampaignTransitionError):
            self.sm.transition("BRIEF_CREATED", actor="t", reason="cannot revive")


if __name__ == "__main__":
    unittest.main()
