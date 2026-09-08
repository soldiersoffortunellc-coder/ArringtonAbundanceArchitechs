import unittest

from csuite.ghl.snapshots import SnapshotAssembler, MissingClientConfigurationError, validate_client_config


class TestMissingConfiguration(unittest.TestCase):
    def test_empty_client_config_lists_every_required_field(self):
        missing = validate_client_config({})
        self.assertIn("domain", missing)
        self.assertIn("escalation_contacts", missing)
        self.assertEqual(len(missing), 12)

    def test_assemble_raises_with_missing_fields_named(self):
        assembler = SnapshotAssembler(industry="real_estate", client_config={"domain": "x.com"})
        with self.assertRaises(MissingClientConfigurationError) as ctx:
            assembler.assemble()
        self.assertIn("branding", ctx.exception.missing_fields)
        self.assertNotIn("domain", ctx.exception.missing_fields)


if __name__ == "__main__":
    unittest.main()
