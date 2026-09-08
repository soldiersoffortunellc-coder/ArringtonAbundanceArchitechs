import unittest

from csuite.marketing.compliance import ComplianceEngine
from csuite.marketing.models import ScriptVersion


def _script(**overrides):
    base = dict(
        version_id="v1", campaign_id="c1", version_number=1,
        hook="Ownership beats income.", body="Building your own agency changes your family tree.",
        cta_text="DM WEALTH", platform_captions={}, hashtags={},
    )
    base.update(overrides)
    return ScriptVersion(**base)


class TestHumanApprovalEnforcement(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceEngine()

    def test_low_risk_clean_script_does_not_require_approval_outside_first_30_days(self):
        review = self.engine.review(_script(), platforms=["instagram"], campaign_type="recruiting", is_ai_clone=False)
        self.assertEqual(review.risk_level, "LOW")
        self.assertFalse(review.requires_human_approval)

    def test_every_ai_clone_post_in_first_30_days_requires_approval_even_if_low_risk(self):
        review = self.engine.review(_script(), platforms=["instagram"], is_ai_clone=True, within_first_30_days=True)
        self.assertEqual(review.risk_level, "LOW")
        self.assertTrue(review.requires_human_approval)

    def test_insurance_claim_keywords_force_high_risk_and_approval(self):
        review = self.engine.review(_script(body="This policy's premium covers the death benefit fully."), platforms=["facebook"])
        self.assertEqual(review.risk_level, "HIGH")
        self.assertTrue(review.requires_human_approval)
        self.assertIn("insurance", review.detected_categories)

    def test_manual_flags_force_approval_for_context_the_text_scan_cant_see(self):
        review = self.engine.review(_script(), platforms=["facebook"], manual_flags={"client_testimonials"})
        self.assertTrue(review.requires_human_approval)

    def test_testimonial_income_and_guarantee_categories_all_gate_approval(self):
        for text, expected_category in [
            ("As told to me by a client, this changed everything.", "testimonials"),
            ("You could earn $10k a month with override income.", "recruiting_income"),
            ("This is a guarantee you can count on.", "guarantees"),
        ]:
            review = self.engine.review(_script(body=text), platforms=["tiktok"])
            self.assertIn(expected_category, review.detected_categories)
            self.assertTrue(review.requires_human_approval)


if __name__ == "__main__":
    unittest.main()
