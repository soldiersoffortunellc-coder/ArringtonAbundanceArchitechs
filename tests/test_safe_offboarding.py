import unittest

from csuite.platform.controls import GlobalControls
from csuite.platform.tenant import TenantRegistry


class TestSafeOffboarding(unittest.TestCase):
    def setUp(self):
        self.registry = TenantRegistry()
        self.registry.register("t1", "Acme Co", "real_estate")
        self.registry.attach_location("t1", "loc_123")
        self.registry.put_data("t1", "history", ["event1", "event2"])
        self.controls = GlobalControls()

    def test_offboarding_requires_explicit_confirmation(self):
        with self.assertRaises(ValueError):
            self.controls.safe_offboard(self.registry, "t1")

    def test_confirmed_offboarding_retains_data_and_marks_status(self):
        result = self.controls.safe_offboard(self.registry, "t1", confirm=True)
        self.assertEqual(result["status"], "OFFBOARDED")
        self.assertIn("history", result["retained_data_keys"])
        # data is retained, not destroyed
        self.assertEqual(self.registry.get_data("t1", "t1", "history"), ["event1", "event2"])
        self.assertIn("t1", self.controls.offboarded_tenants)


if __name__ == "__main__":
    unittest.main()
