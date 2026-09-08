import unittest

from csuite.platform.tenant import TenantRegistry, DuplicateTenantError


class TestDuplicateAccountPrevention(unittest.TestCase):
    def setUp(self):
        self.registry = TenantRegistry()

    def test_duplicate_tenant_id_rejected(self):
        self.registry.register("t1", "Acme Co", "real_estate")
        with self.assertRaises(DuplicateTenantError):
            self.registry.register("t1", "Someone Else Co", "home_services")

    def test_duplicate_client_name_rejected_case_and_whitespace_insensitive(self):
        self.registry.register("t1", "Acme Co", "real_estate")
        with self.assertRaises(DuplicateTenantError):
            self.registry.register("t2", "  ACME CO  ", "home_services")

    def test_duplicate_location_attachment_rejected(self):
        self.registry.register("t1", "Acme Co", "real_estate")
        self.registry.register("t2", "Other Co", "real_estate")
        self.registry.attach_location("t1", "loc_123")
        with self.assertRaises(DuplicateTenantError):
            self.registry.attach_location("t2", "loc_123")


if __name__ == "__main__":
    unittest.main()
