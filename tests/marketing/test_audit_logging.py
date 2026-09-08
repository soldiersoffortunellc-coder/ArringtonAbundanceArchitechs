import unittest

from csuite.marketing.models import new_campaign
from csuite.marketing.campaign_state_machine import CampaignStateMachine


class TestAuditLogging(unittest.TestCase):
    def test_every_transition_records_all_required_fields(self):
        campaign = new_campaign("open_doors_financial_group", "coach_rashon", "leadership_development")
        sm = CampaignStateMachine(campaign)
        event = sm.transition("BRIEF_CREATED", actor="cmo_agent", reason="idea approved", content_version="v0", approval_record_id=None)

        self.assertEqual(event.campaign_id, campaign.campaign_id)
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(event.actor, "cmo_agent")
        self.assertEqual(event.previous_state, "IDEA")
        self.assertEqual(event.new_state, "BRIEF_CREATED")
        self.assertEqual(event.reason, "idea approved")
        self.assertEqual(event.content_version, "v0")
        self.assertIn(event, campaign.audit_trail)

    def test_audit_trail_is_append_only_and_ordered(self):
        campaign = new_campaign("open_doors_financial_group", "coach_rashon", "leadership_development")
        sm = CampaignStateMachine(campaign)
        sm.transition("BRIEF_CREATED", actor="a", reason="1")
        sm.transition("SCRIPT_DRAFTED", actor="b", reason="2")
        self.assertEqual(len(campaign.audit_trail), 2)
        self.assertEqual(campaign.audit_trail[0].new_state, "BRIEF_CREATED")
        self.assertEqual(campaign.audit_trail[1].new_state, "SCRIPT_DRAFTED")
        self.assertEqual(campaign.audit_trail[1].previous_state, "BRIEF_CREATED")


if __name__ == "__main__":
    unittest.main()
