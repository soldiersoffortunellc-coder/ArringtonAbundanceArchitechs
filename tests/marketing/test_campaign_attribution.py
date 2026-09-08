import unittest

from csuite.agents.marketing.lead_conversion_director import LeadConversionDirectorAgent
from csuite.ghl.adapter import GHLAdapter


class TestCampaignAttribution(unittest.TestCase):
    def setUp(self):
        self.agent = LeadConversionDirectorAgent(adapter=GHLAdapter(dry_run=True))

    def test_every_lead_gets_a_measurable_campaign_id_cta_and_destination(self):
        report = self.agent.run({
            "campaign_id": "camp_1", "location_id": "loc_1", "contact_id": "contact_1",
            "cta_key": "book_a_call", "pipeline_key": "consumer_financial_education",
            "target_stage_key": "new_inquiry", "value": 0, "routing_facts": {"lead_score": 55},
        })
        attribution = report.kpis["lead_attribution"]
        self.assertEqual(attribution.campaign_id, "camp_1")
        self.assertEqual(attribution.cta_key, "book_a_call")
        self.assertIn("Consumer Financial Education", attribution.destination)
        self.assertIn("New Inquiry", attribution.destination)

    def test_invalid_stage_key_is_escalated_not_silently_dropped(self):
        report = self.agent.run({
            "campaign_id": "camp_1", "location_id": "loc_1", "contact_id": "contact_1",
            "cta_key": "book_a_call", "pipeline_key": "consumer_financial_education",
            "target_stage_key": "not_a_real_stage", "value": 0, "routing_facts": {},
        })
        self.assertTrue(report.escalations)
        self.assertNotIn("lead_attribution", report.kpis)

    def test_ghl_directives_are_issued_through_the_shared_adapter(self):
        report = self.agent.run({
            "campaign_id": "camp_1", "location_id": "loc_1", "contact_id": "contact_1",
            "cta_key": "apply_agency", "pipeline_key": "licensed_agent_recruiting",
            "target_stage_key": "new_lead", "value": 0, "routing_facts": {"license_status": "unlicensed"},
        })
        self.assertEqual(len(report.directives_issued), 2)  # tag_contact + create_opportunity


if __name__ == "__main__":
    unittest.main()
