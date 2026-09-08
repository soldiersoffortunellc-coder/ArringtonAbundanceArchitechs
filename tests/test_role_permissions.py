import unittest

from csuite.platform.permissions import PermissionRegistry, PermissionDeniedError


class TestRolePermissions(unittest.TestCase):
    def setUp(self):
        self.registry = PermissionRegistry()

    def test_owner_can_do_anything(self):
        self.assertTrue(self.registry.can("owner", "authorize_live_mode"))
        self.assertTrue(self.registry.can("owner", "manage_api_credentials"))

    def test_sales_rep_cannot_authorize_live_mode(self):
        self.assertFalse(self.registry.can("sales_rep", "authorize_live_mode"))
        with self.assertRaises(PermissionDeniedError):
            self.registry.require("sales_rep", "authorize_live_mode")

    def test_client_admin_cannot_view_other_clients_reports(self):
        self.assertFalse(self.registry.can("client_admin", "view_all"))

    def test_cfo_agent_can_manage_billing_dry_run(self):
        self.assertTrue(self.registry.can("cfo_agent", "manage_billing_dry_run"))

    def test_unknown_role_can_do_nothing(self):
        self.assertFalse(self.registry.can("nonexistent_role", "view_own_dashboard"))


if __name__ == "__main__":
    unittest.main()
