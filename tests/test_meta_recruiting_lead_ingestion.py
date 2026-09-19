import unittest

from csuite.ghl.adapter import GHLAdapter
from csuite.ghl.meta_recruiting import (
    MetaRecruitingLeadRouter,
    IncompleteMetaLeadError,
    DuplicateMetaLeadError,
    UnrecognizedLicensingStatusError,
)

LICENSED_LEAD = {
    "fb_lead_id": "fb_lead_001",
    "fb_form_id": "form_abc",
    "fb_page_id": "page_xyz",
    "fb_ad_id": "ad_1",
    "fb_campaign_name": "Q3 Agent Recruiting",
    "full_name": "Jordan Lee",
    "phone_number": "+15555550100",
    "email": "jordan@example.com",
    "are_you_currently_licensed?": "Yes",
}

UNLICENSED_LEAD = {
    "fb_lead_id": "fb_lead_002",
    "full_name": "Casey Kim",
    "phone_number": "+15555550101",
    "are_you_currently_licensed?": "No",
}


class TestMetaRecruitingLeadIngestion(unittest.TestCase):
    def setUp(self):
        self.adapter = GHLAdapter(dry_run=True)
        self.router = MetaRecruitingLeadRouter(self.adapter)

    def test_licensed_lead_routes_to_licensed_agent_funnel(self):
        result = self.router.ingest_lead("loc_1", LICENSED_LEAD)
        self.assertEqual(result["licensing_status"], "licensed")
        self.assertEqual(result["routed_funnel"], "licensed_agent_recruiting_funnel")
        self.assertEqual(result["stage"], "New Candidate (Meta Lead)")
        self.assertEqual(len(result["action_ids"]), 3)

    def test_unlicensed_lead_routes_to_licensing_interest_funnel(self):
        result = self.router.ingest_lead("loc_1", UNLICENSED_LEAD)
        self.assertEqual(result["licensing_status"], "unlicensed")
        self.assertEqual(result["routed_funnel"], "licensing_interest_funnel")

    def test_missing_required_field_raises(self):
        incomplete = {"fb_lead_id": "fb_lead_003", "full_name": "No Phone"}
        with self.assertRaises(IncompleteMetaLeadError) as ctx:
            self.router.ingest_lead("loc_1", incomplete)
        self.assertIn("phone", ctx.exception.missing_fields)
        self.assertIn("licensing_status", ctx.exception.missing_fields)

    def test_duplicate_fb_lead_id_rejected(self):
        self.router.ingest_lead("loc_1", LICENSED_LEAD)
        with self.assertRaises(DuplicateMetaLeadError):
            self.router.ingest_lead("loc_1", LICENSED_LEAD)

    def test_unrecognized_licensing_answer_raises(self):
        weird = {**LICENSED_LEAD, "fb_lead_id": "fb_lead_004", "are_you_currently_licensed?": "maybe soon"}
        with self.assertRaises(UnrecognizedLicensingStatusError):
            self.router.ingest_lead("loc_1", weird)

    def test_dry_run_actions_are_simulated_not_live(self):
        result = self.router.ingest_lead("loc_1", LICENSED_LEAD)
        log = self.adapter.action_log()
        relevant = [a for a in log if a["action_id"] in result["action_ids"]]
        self.assertTrue(all(a["dry_run"] for a in relevant))
        self.assertTrue(all(a["result"]["status"] == "SIMULATED" for a in relevant))

    def test_attribution_fields_are_captured(self):
        result = self.router.ingest_lead("loc_1", LICENSED_LEAD)
        self.assertEqual(result["attribution"]["fb_lead_id"], "fb_lead_001")
        self.assertEqual(result["attribution"]["fb_campaign_name"], "Q3 Agent Recruiting")


if __name__ == "__main__":
    unittest.main()
