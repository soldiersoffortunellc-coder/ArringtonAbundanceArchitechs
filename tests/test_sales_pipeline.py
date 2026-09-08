import unittest

from csuite.pipeline.sales_pipeline import SalesPipeline, LossReasonRequiredError, InvalidStageError


class TestSalesPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = SalesPipeline()

    def test_closed_lost_requires_a_valid_loss_reason(self):
        opp = self.pipeline.create_opportunity("Acme Co", "real_estate", "outbound", 5000)
        with self.assertRaises(LossReasonRequiredError):
            self.pipeline.move_stage(opp.opportunity_id, "Closed Lost")

    def test_closed_lost_with_invalid_reason_string_rejected(self):
        opp = self.pipeline.create_opportunity("Acme Co", "real_estate", "outbound", 5000)
        with self.assertRaises(LossReasonRequiredError):
            self.pipeline.move_stage(opp.opportunity_id, "Closed Lost", loss_reason="just because")

    def test_closed_lost_with_valid_reason_is_recorded(self):
        opp = self.pipeline.create_opportunity("Acme Co", "real_estate", "outbound", 5000)
        updated = self.pipeline.move_stage(opp.opportunity_id, "Closed Lost", loss_reason="no_budget")
        self.assertEqual(updated.loss_reason, "no_budget")
        self.assertEqual(updated.stage, "Closed Lost")

    def test_pipeline_value_excludes_terminal_stages(self):
        opp1 = self.pipeline.create_opportunity("Acme Co", "real_estate", "outbound", 5000)
        opp2 = self.pipeline.create_opportunity("Beta Co", "home_services", "referral", 3000)
        self.pipeline.move_stage(opp2.opportunity_id, "Closed Lost", loss_reason="bad_timing")
        self.assertEqual(self.pipeline.pipeline_value(), 5000)

    def test_invalid_stage_name_rejected(self):
        opp = self.pipeline.create_opportunity("Acme Co", "real_estate", "outbound", 5000)
        with self.assertRaises(InvalidStageError):
            self.pipeline.move_stage(opp.opportunity_id, "Made Up Stage")


if __name__ == "__main__":
    unittest.main()
