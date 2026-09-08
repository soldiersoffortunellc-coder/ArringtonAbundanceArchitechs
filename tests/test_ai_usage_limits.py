import unittest

from csuite.platform.usage_limits import UsageLimitTracker, UsageLimitExceededError


class TestAiUsageLimits(unittest.TestCase):
    def setUp(self):
        self.tracker = UsageLimitTracker()

    def test_usage_under_cap_is_not_flagged(self):
        result = self.tracker.record_usage("t1", "ai_growth_system", "ai_conversations", 100)
        self.assertFalse(result["over_cap"])

    def test_usage_over_cap_but_under_hard_stop_is_flagged_not_blocked(self):
        result = self.tracker.record_usage("t1", "ai_growth_system", "ai_conversations", 1600)
        self.assertTrue(result["over_cap"])  # cap is 1500

    def test_usage_beyond_hard_stop_raises(self):
        with self.assertRaises(UsageLimitExceededError):
            self.tracker.record_usage("t1", "ai_growth_system", "ai_conversations", 5000)  # hard stop = 1500*1.5=2250

    def test_starter_saas_tier_has_zero_ai_allowance(self):
        result = self.tracker.record_usage("t1", "starter_saas", "ai_conversations", 0)
        self.assertEqual(result["cap"], 0)

    def test_unknown_tier_raises_keyerror(self):
        with self.assertRaises(KeyError):
            self.tracker.record_usage("t1", "not_a_real_tier", "ai_conversations", 1)


if __name__ == "__main__":
    unittest.main()
