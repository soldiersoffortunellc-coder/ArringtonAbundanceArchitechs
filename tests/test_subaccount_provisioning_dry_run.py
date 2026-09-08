import unittest

from csuite.ghl.adapter import GHLAdapter, LiveModeNotAuthorized
from csuite.ghl.provisioning import ProvisioningWorkflow
from csuite.platform.tenant import TenantRegistry

VALID_CLIENT_CONFIG = {
    "branding": {"logo_url": "x"}, "domain": "client.example.com", "phone_numbers": ["+15555550100"],
    "email": "hello@client.example.com", "calendars": ["c1"], "users": ["u1"], "services": ["s1"],
    "service_areas": ["TX"], "pricing": {"setup": 1000}, "disclosures": ["d1"],
    "integrations": ["i1"], "escalation_contacts": ["e1"],
}


class TestSubaccountProvisioningDryRun(unittest.TestCase):
    def test_default_adapter_is_dry_run(self):
        adapter = GHLAdapter()
        self.assertTrue(adapter.dry_run)

    def test_live_mode_requires_explicit_authorization(self):
        with self.assertRaises(LiveModeNotAuthorized):
            GHLAdapter(dry_run=False)

    def test_provisioning_creates_a_simulated_location_only(self):
        adapter = GHLAdapter(dry_run=True)
        workflow = ProvisioningWorkflow(adapter=adapter, tenant_registry=TenantRegistry())

        result = workflow.run(
            tenant_id="t1", client_name="Acme Co", industry="real_estate", plan_id="ai_growth_system",
            client_config=VALID_CLIENT_CONFIG, users=[{"email": "a@acme.com"}],
        )

        self.assertIsNone(result.blocked_reason)
        self.assertTrue(result.location_id.startswith("loc_"))
        self.assertEqual(result.state_machine.current_state, "LIVE")

        create_location_actions = [a for a in adapter.action_log() if a["kind"] == "create_location"]
        self.assertEqual(len(create_location_actions), 1)
        self.assertTrue(create_location_actions[0]["dry_run"])
        self.assertEqual(create_location_actions[0]["result"]["status"], "SIMULATED")


if __name__ == "__main__":
    unittest.main()
