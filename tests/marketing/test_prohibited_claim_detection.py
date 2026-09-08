import unittest

from csuite.marketing.compliance import ComplianceEngine, RISK_PROHIBITED
from csuite.marketing.models import ScriptVersion


def _script(body):
    return ScriptVersion(
        version_id="v1", campaign_id="c1", version_number=1, hook="hook", body=body, cta_text="cta",
        platform_captions={}, hashtags={},
    )


class TestProhibitedClaimDetection(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceEngine()

    def test_guaranteed_returns_is_blocked(self):
        review = self.engine.review(_script("We offer guaranteed returns on every dollar."), platforms=["facebook"])
        self.assertEqual(review.risk_level, RISK_PROHIBITED)
        self.assertIn("guaranteed returns", review.blocked_phrases_found)

    def test_risk_free_wealth_is_blocked(self):
        review = self.engine.review(_script("This is risk-free wealth for your family."), platforms=["instagram"])
        self.assertEqual(review.risk_level, RISK_PROHIBITED)

    def test_instant_approval_is_blocked(self):
        review = self.engine.review(_script("Get instant approval today."), platforms=["tiktok"])
        self.assertEqual(review.risk_level, RISK_PROHIBITED)

    def test_tax_free_forever_is_blocked(self):
        review = self.engine.review(_script("Your money grows tax-free forever."), platforms=["youtube_shorts"])
        self.assertEqual(review.risk_level, RISK_PROHIBITED)

    def test_case_insensitive_matching(self):
        review = self.engine.review(_script("GUARANTEED APPROVAL for everyone!"), platforms=["facebook"])
        self.assertEqual(review.risk_level, RISK_PROHIBITED)

    def test_clean_script_is_not_blocked(self):
        review = self.engine.review(_script("Ownership beats income — build something that outlasts you."), platforms=["linkedin"])
        self.assertNotEqual(review.risk_level, RISK_PROHIBITED)
        self.assertEqual(review.blocked_phrases_found, [])


if __name__ == "__main__":
    unittest.main()
