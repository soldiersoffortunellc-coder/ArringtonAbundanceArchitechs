import unittest

from csuite.revenue.financial_model import FinancialModel


class TestRevenueCalculations(unittest.TestCase):
    def setUp(self):
        self.model = FinancialModel()

    def test_target_scenario_matches_specified_modeled_values(self):
        scenario = self.model.scenario("target")
        self.assertEqual(scenario["premium"]["modeled_value"], 762500)
        self.assertEqual(scenario["standardized"]["modeled_value"], 274550)
        self.assertEqual(scenario["combined_modeled_90_day_value"], 1037050)

    def test_every_scenario_is_explicitly_flagged_as_not_guaranteed(self):
        for name, scenario in self.model.all_scenarios().items():
            self.assertFalse(scenario["is_guaranteed"], f"scenario '{name}' must not claim to be guaranteed")

    def test_conservative_is_lower_than_target_is_lower_than_aggressive(self):
        all_scenarios = self.model.all_scenarios()
        conservative = all_scenarios["conservative"]["combined_modeled_90_day_value"]
        target = all_scenarios["target"]["combined_modeled_90_day_value"]
        aggressive = all_scenarios["aggressive"]["combined_modeled_90_day_value"]
        self.assertLess(conservative, target)
        self.assertLess(target, aggressive)

    def test_unknown_scenario_raises(self):
        with self.assertRaises(KeyError):
            self.model.scenario("moonshot")


if __name__ == "__main__":
    unittest.main()
