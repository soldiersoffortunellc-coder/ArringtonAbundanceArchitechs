import unittest

from csuite.providers.avatar_video_adapter import AvatarVideoAdapter, ConsentRequiredError
from csuite.providers.voice_adapter import VoiceAdapter, ConsentRequiredError as VoiceConsentRequiredError
from csuite.providers.base import ProviderLiveModeNotAuthorized


class TestProviderDryRunMocks(unittest.TestCase):
    def test_avatar_adapter_defaults_to_dry_run(self):
        adapter = AvatarVideoAdapter()
        self.assertTrue(adapter.dry_run)

    def test_avatar_adapter_live_mode_requires_authorization(self):
        with self.assertRaises(ProviderLiveModeNotAuthorized):
            AvatarVideoAdapter(dry_run=False)

    def test_avatar_adapter_refuses_job_without_consent(self):
        adapter = AvatarVideoAdapter()
        with self.assertRaises(ConsentRequiredError):
            adapter.submit_job(campaign_id="c1", version_id="v1", script_text="hi", consent_authorization_id=None)

    def test_avatar_adapter_submits_with_consent(self):
        # NOTE: unlike GHLAdapter, AvatarVideoAdapter's result.status carries the job's
        # lifecycle state (SUBMITTED/PROCESSING/...) rather than a SIMULATED/LIVE marker —
        # whether the call was simulated is tracked on the action itself (action.dry_run).
        adapter = AvatarVideoAdapter()
        action = adapter.submit_job(campaign_id="c1", version_id="v1", script_text="hi", consent_authorization_id="consent_1")
        self.assertTrue(action.dry_run)
        self.assertEqual(action.result["status"], "SUBMITTED")
        self.assertTrue(action.result.get("provider_job_id"))

    def test_retry_flow_dead_letters_after_max_attempts(self):
        adapter = AvatarVideoAdapter()
        action = adapter.retry_job("job_1", attempt=4, max_attempts=3)
        self.assertEqual(action.result["status"], "DEAD_LETTER")

    def test_retry_flow_retries_within_max_attempts(self):
        adapter = AvatarVideoAdapter()
        action = adapter.retry_job("job_1", attempt=2, max_attempts=3)
        self.assertEqual(action.result["status"], "RETRYING")

    def test_voice_adapter_requires_both_voice_id_and_consent(self):
        adapter = VoiceAdapter()
        with self.assertRaises(VoiceConsentRequiredError):
            adapter.generate_voice_clip(campaign_id="c1", script_text="hi", authorized_voice_id=None, consent_authorization_id="consent_1")
        with self.assertRaises(VoiceConsentRequiredError):
            adapter.generate_voice_clip(campaign_id="c1", script_text="hi", authorized_voice_id="voice_1", consent_authorization_id=None)

    def test_every_provider_action_is_recorded_in_the_audit_log(self):
        adapter = AvatarVideoAdapter()
        adapter.submit_job(campaign_id="c1", version_id="v1", script_text="hi", consent_authorization_id="consent_1")
        adapter.check_status("job_1")
        self.assertEqual(len(adapter.action_log()), 2)


if __name__ == "__main__":
    unittest.main()
