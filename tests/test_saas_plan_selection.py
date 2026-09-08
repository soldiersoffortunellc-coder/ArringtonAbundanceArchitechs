import unittest

from csuite.ghl.snapshots import INDUSTRY_SNAPSHOT_IDS
import json
from pathlib import Path


class TestSaasPlanSelection(unittest.TestCase):
    def test_offer_ladder_has_four_configurable_tiers(self):
        config_path = Path(__file__).resolve().parents[1] / "config" / "offer_ladder.json"
        with open(config_path) as fh:
            config = json.load(fh)
        tier_ids = [t["id"] for t in config["tiers"]]
        self.assertEqual(
            tier_ids,
            ["starter_saas", "ai_growth_system", "ai_revenue_operating_system", "enterprise_agency_license"],
        )

    def test_every_tier_has_a_configurable_price_range(self):
        config_path = Path(__file__).resolve().parents[1] / "config" / "offer_ladder.json"
        with open(config_path) as fh:
            config = json.load(fh)
        for tier in config["tiers"]:
            self.assertIn("setup_fee", tier)
            self.assertIn("monthly_fee", tier)
            self.assertLessEqual(tier["monthly_fee"]["min"], tier["monthly_fee"]["max"])

    def test_supported_industries_have_a_plan_mapping(self):
        # every industry pack must map to a snapshot id usable during plan selection
        for industry in ("insurance_agency", "real_estate", "home_services"):
            self.assertIn(industry, INDUSTRY_SNAPSHOT_IDS)


if __name__ == "__main__":
    unittest.main()
