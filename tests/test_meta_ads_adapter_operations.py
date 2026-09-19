import unittest

from csuite.ghl.adapter import GHLAdapter


class TestMetaAdsAdapterOperations(unittest.TestCase):
    def setUp(self):
        self.adapter = GHLAdapter(dry_run=True)

    def test_fb_get_integration_is_simulated_in_dry_run(self):
        action = self.adapter.fb_get_integration("loc_1")
        self.assertTrue(action.dry_run)
        self.assertEqual(action.result["status"], "SIMULATED")
        self.assertEqual(action.kind, "fb_get_integration")

    def test_fb_get_page_lead_forms_is_simulated_in_dry_run(self):
        action = self.adapter.fb_get_page_lead_forms("loc_1", page_id="page_xyz")
        self.assertTrue(action.dry_run)
        self.assertEqual(action.payload["page_id"], "page_xyz")
        self.assertEqual(action.result["status"], "SIMULATED")

    def test_meta_ads_actions_are_recorded_in_the_audit_log(self):
        self.adapter.fb_get_integration("loc_1")
        self.adapter.fb_get_page_lead_forms("loc_1", page_id="page_xyz")
        kinds = [a["kind"] for a in self.adapter.action_log()]
        self.assertIn("fb_get_integration", kinds)
        self.assertIn("fb_get_page_lead_forms", kinds)


if __name__ == "__main__":
    unittest.main()
