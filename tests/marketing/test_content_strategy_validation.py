import unittest

from csuite.marketing.content_strategy import (
    load_content_pillars, load_content_mix, cross_brand_mixing_requires_approval,
    validate_ghl_marketing_config, content_mix_balance_check, load_brand_profile,
)


class TestContentStrategyValidation(unittest.TestCase):
    def test_fifteen_content_pillars_are_configured(self):
        self.assertEqual(len(load_content_pillars()), 15)

    def test_content_mix_percentages_are_configurable_data_not_hardcoded(self):
        mix = load_content_mix()
        self.assertAlmostEqual(mix["production_mix"]["ai_clone_content_pct"], 0.70)
        self.assertAlmostEqual(
            sum(mix["topic_mix"].values()), 1.0, places=4,
        )

    def test_cross_brand_mixing_requires_approval_by_default(self):
        self.assertTrue(cross_brand_mixing_requires_approval())

    def test_placeholder_config_is_flagged_as_incomplete(self):
        config = {"agency_id": "PLACEHOLDER_AGENCY_ID", "location_id": "loc_real_123", "nested": {"x": "PLACEHOLDER"}}
        missing = validate_ghl_marketing_config(config)
        self.assertIn("agency_id", missing)
        self.assertIn("nested.x", missing)
        self.assertNotIn("location_id", missing)

    def test_fully_filled_config_has_no_placeholders(self):
        config = {"agency_id": "real_agency_1", "location_id": "real_loc_1"}
        self.assertEqual(validate_ghl_marketing_config(config), [])

    def test_content_mix_balance_check_reports_target_vs_actual(self):
        result = content_mix_balance_check({"ai_clone": 7, "authentic_live": 3, "education": 4, "recruiting": 3})
        self.assertEqual(result["production_mix"]["ai_clone_actual"], 0.7)
        self.assertEqual(result["production_mix"]["ai_clone_target"], 0.70)

    def test_brand_profile_separates_verified_from_unverified_facts(self):
        profile = load_brand_profile("coach_rashon")
        self.assertIn("verified_facts", profile)
        self.assertIn("user_provided_unverified", profile)
        # nothing invented: unverified fields must be explicitly marked NEEDS_INPUT
        for value in profile["user_provided_unverified"].values():
            self.assertIn("NEEDS_INPUT", value)


if __name__ == "__main__":
    unittest.main()
