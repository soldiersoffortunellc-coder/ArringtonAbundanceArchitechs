import unittest

from csuite.platform.billing import BillingLedger
from csuite.agents.revenue.revenue_operations_analyst import RevenueOperationsAnalystAgent


class TestContractedVsCollected(unittest.TestCase):
    def test_contracted_and_collected_are_reported_as_distinct_fields(self):
        ledger = BillingLedger()
        ledger.record("t1", "contract_signed", 50000)
        ledger.record("t1", "payment_collected", 10000)

        agent = RevenueOperationsAnalystAgent(billing_ledger=ledger)
        report = agent.run({"funnel": {}, "scenario": "target"})

        self.assertEqual(report.kpis["contracted_revenue"], 50000)
        self.assertEqual(report.kpis["cash_collected"], 10000)
        self.assertNotEqual(report.kpis["contracted_revenue"], report.kpis["cash_collected"])
        # the two numbers must never be summed into one field anywhere in the report
        self.assertNotIn("total_revenue", report.kpis)

    def test_decision_narrative_explicitly_names_both_numbers(self):
        ledger = BillingLedger()
        ledger.record("t1", "contract_signed", 12345)
        ledger.record("t1", "payment_collected", 6789)
        agent = RevenueOperationsAnalystAgent(billing_ledger=ledger)
        report = agent.run({"funnel": {}, "scenario": "conservative"})
        narrative = " ".join(report.decisions)
        self.assertIn("12,345", narrative)
        self.assertIn("6,789", narrative)


if __name__ == "__main__":
    unittest.main()
