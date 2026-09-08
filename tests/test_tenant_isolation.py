import unittest

from csuite.platform.tenant import TenantRegistry, TenantIsolationError


class TestTenantIsolation(unittest.TestCase):
    def setUp(self):
        self.registry = TenantRegistry()
        self.registry.register("t1", "Acme Co", "real_estate")
        self.registry.register("t2", "Other Co", "home_services")
        self.registry.put_data("t1", "notes", "confidential acme notes")

    def test_tenant_can_read_its_own_data(self):
        value = self.registry.get_data("t1", "t1", "notes")
        self.assertEqual(value, "confidential acme notes")

    def test_tenant_cannot_read_another_tenants_data(self):
        with self.assertRaises(TenantIsolationError):
            self.registry.get_data("t2", "t1", "notes")

    def test_unknown_owner_key_returns_none_for_the_owner_itself(self):
        self.assertIsNone(self.registry.get_data("t1", "t1", "does_not_exist"))


if __name__ == "__main__":
    unittest.main()
