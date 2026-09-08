import unittest

from csuite.platform.billing import BillingLedger


class TestBillingEventHandling(unittest.TestCase):
    def setUp(self):
        self.ledger = BillingLedger()

    def test_records_multiple_event_types(self):
        self.ledger.record("t1", "contract_signed", 30500)
        self.ledger.record("t1", "invoice_sent", 20000)
        self.ledger.record("t1", "payment_collected", 20000)
        self.ledger.record("t1", "payment_collected", 3500, is_recurring=True)

        summary = self.ledger.summary()
        self.assertEqual(summary["contracted_revenue"], 30500)
        self.assertEqual(summary["invoiced_revenue"], 20000)
        self.assertEqual(summary["cash_collected"], 23500)
        self.assertEqual(summary["monthly_recurring_revenue"], 3500)

    def test_accounts_receivable_never_goes_negative(self):
        self.ledger.record("t1", "invoice_sent", 5000)
        self.ledger.record("t1", "payment_collected", 6000)  # overpayment / early renewal
        self.assertEqual(self.ledger.accounts_receivable(), 0.0)

    def test_refunds_reduce_net_cash_but_not_gross_collected(self):
        self.ledger.record("t1", "payment_collected", 1000)
        self.ledger.record("t1", "refund", 200)
        self.assertEqual(self.ledger.cash_collected(), 1000)
        self.assertEqual(self.ledger.net_cash_collected(), 800)


if __name__ == "__main__":
    unittest.main()
