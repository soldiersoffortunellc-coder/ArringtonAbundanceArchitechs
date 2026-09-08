"""
Tests for Open Doors Financial OS v1's Phase 1/2 scripts. Synthetic only —
no real network call is ever made; GHLApiClient.get is mocked for the
success/failure paths. This is exactly the kind of destructive-logic-free,
synthetic testing Phase 12 requires: no real GHL account is touched.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import ghl_connection_test as conn_test  # noqa: E402
import ghl_discovery as discovery  # noqa: E402
from csuite.ghl.api_client import GHLApiError  # noqa: E402

REQUIRED_ENV = {
    "GHL_LOCATION_ID": "loc_test_123",
    "GHL_PRIVATE_INTEGRATION_TOKEN": "pit_test_value",
    "GHL_API_VERSION": "2021-07-28",
}


class TestConnectionTestMissingCredentials(unittest.TestCase):
    def test_all_missing_reports_fail_with_exact_var_names(self):
        with patch.dict(os.environ, {}, clear=True):
            report = conn_test.run_connection_test()
        self.assertEqual(report["connection_status"], "FAIL")
        self.assertEqual(
            set(report["missing_env_vars"]),
            {"GHL_LOCATION_ID", "GHL_PRIVATE_INTEGRATION_TOKEN", "GHL_API_VERSION"},
        )

    def test_partial_missing_identifies_only_the_missing_ones(self):
        with patch.dict(os.environ, {"GHL_LOCATION_ID": "loc_1"}, clear=True):
            report = conn_test.run_connection_test()
        self.assertEqual(report["missing_env_vars"], ["GHL_PRIVATE_INTEGRATION_TOKEN", "GHL_API_VERSION"])

    def test_report_never_contains_the_token_value(self):
        with patch.dict(os.environ, {**REQUIRED_ENV, "GHL_PRIVATE_INTEGRATION_TOKEN": "super-secret-value"}, clear=True):
            with patch.object(conn_test.GHLApiClient, "get", side_effect=Exception("network unreachable")):
                report = conn_test.run_connection_test()
        report_text = str(report)
        self.assertNotIn("super-secret-value", report_text)
        self.assertEqual(report["env_vars"]["GHL_PRIVATE_INTEGRATION_TOKEN"], "SET")


class TestConnectionTestMockedNetwork(unittest.TestCase):
    def test_successful_connection_reports_pass(self):
        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            with patch.object(conn_test.GHLApiClient, "get", return_value={"location": {"id": "loc_test_123", "name": "Open Doors Financial Group"}}):
                report = conn_test.run_connection_test()
        self.assertEqual(report["connection_status"], "PASS")
        self.assertTrue(report["location_resolved"])
        self.assertEqual(report["location_name"], "Open Doors Financial Group")

    def test_401_reports_fail_with_scope_hint_not_generic_error(self):
        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            with patch.object(conn_test.GHLApiClient, "get", side_effect=GHLApiError(401, "GET", "https://x/locations/loc_test_123", "Unauthorized")):
                report = conn_test.run_connection_test()
        self.assertEqual(report["connection_status"], "FAIL")
        self.assertEqual(report["http_status"], 401)
        self.assertIn("scope", report["error"].lower())

    def test_404_reports_fail_location_not_found(self):
        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            with patch.object(conn_test.GHLApiClient, "get", side_effect=GHLApiError(404, "GET", "https://x/locations/loc_test_123", "Not Found")):
                report = conn_test.run_connection_test()
        self.assertEqual(report["connection_status"], "FAIL")
        self.assertEqual(report["http_status"], 404)


class TestDiscoveryBlockedOnConnectionFailure(unittest.TestCase):
    def test_discovery_is_blocked_when_connection_fails_and_makes_no_calls(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(discovery.GHLApiClient, "get") as mock_get:
                report = discovery.run_discovery()
        mock_get.assert_not_called()
        self.assertIsNotNone(report["blocked_reason"])
        for task in report["tasks"].values():
            self.assertEqual(task["status"], "BLOCKED")

    def test_discovery_proceeds_task_by_task_when_connected(self):
        def fake_get(path, query=None):
            if path == f"/locations/{REQUIRED_ENV['GHL_LOCATION_ID']}":
                return {"location": {"id": "loc_test_123", "name": "Open Doors Financial Group"}}
            if path == "/opportunities/pipelines":
                return {"pipelines": [{"name": "01 | Insurance Sales"}]}
            raise GHLApiError(404, "GET", path, "not found in this mock")

        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            with patch.object(discovery.GHLApiClient, "get", side_effect=fake_get):
                report = discovery.run_discovery()

        self.assertEqual(report["connection"]["status"], "PASS")
        self.assertEqual(report["tasks"]["pipelines"]["status"], "ACCESSIBLE")
        # a task that 404s in the mock is reported, not crashed on
        self.assertIn(report["tasks"]["tags"]["status"], ("NOT_ACCESSIBLE", "ERROR"))

    def test_one_task_failure_does_not_stop_the_rest(self):
        def fake_get(path, query=None):
            if "locations/" in path:
                return {"location": {"id": "loc_test_123"}}
            if path == "/calendars/":
                return {"calendars": [{"name": "Insurance Discovery"}]}
            raise GHLApiError(500, "GET", path, "server error")

        with patch.dict(os.environ, REQUIRED_ENV, clear=True):
            with patch.object(discovery.GHLApiClient, "get", side_effect=fake_get):
                report = discovery.run_discovery()

        self.assertEqual(report["tasks"]["calendars"]["status"], "ACCESSIBLE")
        self.assertEqual(report["tasks"]["pipelines"]["status"], "ERROR")
        self.assertEqual(len(report["tasks"]), len(discovery.DISCOVERY_TASKS))


if __name__ == "__main__":
    unittest.main()
