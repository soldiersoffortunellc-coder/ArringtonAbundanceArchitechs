import unittest

from csuite.ghl.snapshots import SnapshotAssembler, MissingClientConfigurationError

VALID_CLIENT_CONFIG = {
    "branding": {"logo_url": "x"}, "domain": "client.example.com", "phone_numbers": ["+15555550100"],
    "email": "hello@client.example.com", "calendars": ["c1"], "users": ["u1"], "services": ["s1"],
    "service_areas": ["TX"], "pricing": {"setup": 1000}, "disclosures": ["d1"],
    "integrations": ["i1"], "escalation_contacts": ["e1"],
}


class TestSnapshotAssignment(unittest.TestCase):
    def test_correct_industry_pack_is_assigned(self):
        assembler = SnapshotAssembler(industry="real_estate", client_config=VALID_CLIENT_CONFIG)
        assembled = assembler.assemble()
        self.assertEqual(assembled["industry_pack"]["industry"], "real_estate")
        self.assertEqual(assembled["universal_core"]["snapshot_id"], "universal_core")

    def test_layers_stay_separated(self):
        assembler = SnapshotAssembler(industry="home_services", client_config=VALID_CLIENT_CONFIG)
        assembled = assembler.assemble()
        self.assertIn("universal_core", assembled)
        self.assertIn("industry_pack", assembled)
        self.assertIn("client_configuration", assembled)
        # the client layer must never leak into the universal or industry layers
        self.assertNotIn("client_configuration", assembled["universal_core"])
        self.assertNotIn("client_configuration", assembled["industry_pack"])

    def test_unknown_industry_raises(self):
        assembler = SnapshotAssembler(industry="astrology", client_config=VALID_CLIENT_CONFIG)
        with self.assertRaises(Exception):
            assembler.assemble()


if __name__ == "__main__":
    unittest.main()
