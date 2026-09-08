import os
import unittest
from unittest.mock import patch

from csuite.ghl.adapter import GHLAdapter, LiveModeNotAuthorized
from csuite.ghl.api_client import GHLApiClient, GHLCredentialsMissingError, GHLUnsupportedActionError


class TestGhlApiClientCredentials(unittest.TestCase):
    def test_missing_token_raises_clear_error_before_any_network_call(self):
        with patch.dict(os.environ, {}, clear=True):
            client = GHLApiClient()
            with self.assertRaises(GHLCredentialsMissingError):
                client._headers()

    def test_token_from_env_var_is_picked_up(self):
        with patch.dict(os.environ, {"GHL_ACCESS_TOKEN": "secret-token-value"}, clear=True):
            client = GHLApiClient()
            headers = client._headers()
            self.assertEqual(headers["Authorization"], "Bearer secret-token-value")
            self.assertEqual(headers["Version"], "2021-07-28")

    def test_explicit_token_overrides_env(self):
        with patch.dict(os.environ, {"GHL_ACCESS_TOKEN": "env-token"}, clear=True):
            client = GHLApiClient(access_token="explicit-token")
            self.assertEqual(client._headers()["Authorization"], "Bearer explicit-token")


class TestLiveAdapterConstructionGuards(unittest.TestCase):
    def test_live_adapter_requires_authorization(self):
        with self.assertRaises(LiveModeNotAuthorized):
            GHLAdapter(dry_run=False)

    def test_live_adapter_requires_an_api_client(self):
        with self.assertRaises(LiveModeNotAuthorized):
            GHLAdapter(dry_run=False, live_authorized=True)

    def test_live_adapter_constructs_with_authorization_and_client(self):
        client = GHLApiClient(access_token="t")
        adapter = GHLAdapter(dry_run=False, live_authorized=True, api_client=client)
        self.assertFalse(adapter.dry_run)
        self.assertIs(adapter.api_client, client)


class _RecordingApiClient:
    """A fake GHLApiClient that never touches the network — records calls instead."""

    def __init__(self):
        self.calls = []

    def post(self, path, json_body):
        self.calls.append(("POST", path, json_body))
        return {"id": "fake_id_123"}

    def put(self, path, json_body):
        self.calls.append(("PUT", path, json_body))
        return {"updated": True}

    def get(self, path, query=None):
        self.calls.append(("GET", path, query))
        return {}


class TestLiveCallDispatch(unittest.TestCase):
    def setUp(self):
        self.fake_client = _RecordingApiClient()
        self.adapter = GHLAdapter(dry_run=False, live_authorized=True, api_client=self.fake_client)

    def test_supported_action_dispatches_to_the_real_endpoint_shape(self):
        self.adapter.tag_contact("loc_1", "contact_1", "hot-lead")
        method, path, body = self.fake_client.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(path, "/contacts/contact_1/tags")
        self.assertEqual(body, {"tags": ["hot-lead"]})

    def test_create_opportunity_dispatches_correctly(self):
        self.adapter.create_opportunity("loc_1", "pipe_123", "Qualified", 5000)
        method, path, body = self.fake_client.calls[0]
        self.assertEqual(path, "/opportunities/")
        self.assertEqual(body["monetaryValue"], 5000)

    def test_unsupported_action_raises_with_actionable_guidance(self):
        with self.assertRaises(GHLUnsupportedActionError) as ctx:
            self.adapter.apply_snapshot("loc_1", "universal_core", "1.0.0")
        self.assertIn("snapshot", str(ctx.exception).lower())

    def test_every_unsupported_action_is_pre_declared(self):
        for kind in ("apply_snapshot", "create_pipeline", "create_workflow", "publish_campaign", "create_billing_event"):
            self.assertIn(kind, GHLAdapter._UNSUPPORTED_LIVE_ACTIONS)

    def test_live_actions_are_recorded_in_the_audit_log_like_dry_run_ones(self):
        self.adapter.tag_contact("loc_1", "contact_1", "hot-lead")
        log = self.adapter.action_log()
        self.assertEqual(len(log), 1)
        self.assertFalse(log[0]["dry_run"])


if __name__ == "__main__":
    unittest.main()
