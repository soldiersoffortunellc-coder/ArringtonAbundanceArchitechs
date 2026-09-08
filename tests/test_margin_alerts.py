import unittest

from csuite.revenue.margin import ClientProfitability


class TestMarginAlerts(unittest.TestCase):
    def setUp(self):
        self.calc = ClientProfitability(required_margin_pct=0.50)

    def test_healthy_account_raises_no_alert(self):
        result = self.calc.compute(
            tenant_id="t1", setup_revenue=20000, monthly_revenue=3500,
            software_cost=100, ai_usage_cost=100, phone_cost=50, email_cost=10, sms_cost=20,
            integration_cost=200, labor_hours=20, hourly_labor_rate=65,
            onboarding_cost=300, support_cost=100,
        )
        self.assertFalse(result["below_required_margin"])
        self.assertIsNone(result["alert"])

    def test_thin_margin_account_triggers_alert(self):
        result = self.calc.compute(
            tenant_id="t2", setup_revenue=2500, monthly_revenue=997,
            software_cost=300, ai_usage_cost=400, phone_cost=80, email_cost=30, sms_cost=60,
            integration_cost=200, labor_hours=30, hourly_labor_rate=65,
            onboarding_cost=400, support_cost=200,
        )
        self.assertTrue(result["below_required_margin"])
        self.assertIsNotNone(result["alert"])
        self.assertIn("t2", result["alert"].message)

    def test_max_acceptable_cac_is_computed(self):
        result = self.calc.compute(
            tenant_id="t3", setup_revenue=10000, monthly_revenue=2500,
            software_cost=0, ai_usage_cost=0, phone_cost=0, email_cost=0, sms_cost=0,
            integration_cost=0, labor_hours=0, hourly_labor_rate=0,
            onboarding_cost=0, support_cost=0,
        )
        # 10000 + (2500*3)*0.5 = 13750
        self.assertEqual(result["max_acceptable_acquisition_cost"], 13750.0)


if __name__ == "__main__":
    unittest.main()
