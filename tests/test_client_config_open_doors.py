import json
import unittest
from pathlib import Path

from csuite.ghl.snapshots import SnapshotAssembler, validate_client_config

CLIENT_CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "config" / "clients" / "open_doors_financial_group.json"
)


class TestOpenDoorsFinancialGroupClientConfig(unittest.TestCase):
    """Proves the Coach Shonough / ODFG client configuration layer
    (docs/13) is a real, system-recognized config — not just a JSON file
    that looks plausible. It must pass the exact same gate real onboarding
    uses (validate_client_config / SnapshotAssembler) and assemble cleanly
    against the insurance_agency industry pack."""

    @classmethod
    def setUpClass(cls):
        with open(CLIENT_CONFIG_PATH, "r", encoding="utf-8") as fh:
            cls.client_config = json.load(fh)

    def test_all_twelve_required_fields_present(self):
        missing = validate_client_config(self.client_config)
        self.assertEqual(missing, [], f"client config is missing required fields: {missing}")

    def test_assembles_cleanly_against_insurance_agency_pack(self):
        assembler = SnapshotAssembler(industry="insurance_agency", client_config=self.client_config)
        assembled = assembler.assemble()
        self.assertEqual(assembled["industry_pack"]["industry"], "insurance_agency")
        self.assertIn("licensed_agent_recruiting_funnel", assembled["industry_pack"]["components"]["funnels"])
        self.assertIn("consumer_financial_education_funnel", assembled["industry_pack"]["components"]["funnels"])
        self.assertEqual(assembled["client_configuration"], self.client_config)

    def test_client_layer_never_leaks_into_shared_layers(self):
        assembler = SnapshotAssembler(industry="insurance_agency", client_config=self.client_config)
        assembled = assembler.assemble()
        self.assertNotIn("client_configuration", assembled["universal_core"])
        self.assertNotIn("client_configuration", assembled["industry_pack"])

    def test_recruiting_and_consumer_intent_segments_stay_distinct(self):
        segments = self.client_config["intent_segments"]
        self.assertIn("consumer", segments)
        self.assertIn("agent-licensed", segments)
        self.assertIn("agent-unlicensed", segments)
        # consumer and recruiting must never collapse into a single segment,
        # per insurance_pack.json's separation of consumer vs. recruiting funnels
        self.assertNotEqual(len(set(segments)), 1)

    def test_recruiting_no_earnings_claims_flag_is_set(self):
        # mirrors insurance_pack.json's compliance_review_controls: "no
        # guaranteed-earnings language permitted in recruiting funnels"
        self.assertTrue(self.client_config["disclosures"]["recruiting_no_earnings_claims"])

    def test_financial_education_content_requires_signoff(self):
        self.assertTrue(
            self.client_config["disclosures"]["financial_education_content_requires_compliance_signoff"]
        )


if __name__ == "__main__":
    unittest.main()
