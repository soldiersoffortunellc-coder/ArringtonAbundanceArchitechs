import unittest

from csuite.platform.controls import GlobalControls, SystemPausedError, PublishingPausedError
from csuite.agents.marketing.ai_video_production_director import AIVideoProductionDirectorAgent
from csuite.agents.marketing.social_distribution_director import SocialDistributionDirectorAgent


class TestEmergencyPublishingPause(unittest.TestCase):
    def test_publishing_pause_is_distinct_from_full_system_pause(self):
        controls = GlobalControls()
        controls.pause_publishing("suspected compliance issue")
        self.assertTrue(controls.publishing_paused)
        self.assertFalse(controls.paused)  # full revenue-ops pause is untouched

    def test_guard_publishing_blocks_when_publishing_paused(self):
        controls = GlobalControls()
        controls.pause_publishing("emergency stop")
        with self.assertRaises(PublishingPausedError):
            controls.guard_publishing()

    def test_guard_publishing_also_blocked_by_full_system_pause(self):
        controls = GlobalControls()
        controls.pause("full system pause")
        with self.assertRaises(SystemPausedError):
            controls.guard_publishing()

    def test_video_production_director_honors_publishing_pause(self):
        controls = GlobalControls()
        controls.pause_publishing("kill switch engaged")
        agent = AIVideoProductionDirectorAgent(global_controls=controls)
        with self.assertRaises(PublishingPausedError):
            agent.run({"campaign_id": "c1", "version_id": "v1", "script_text": "hi", "consent_authorization_id": "consent_1"})

    def test_social_distribution_director_honors_publishing_pause(self):
        controls = GlobalControls()
        controls.pause_publishing("kill switch engaged")
        agent = SocialDistributionDirectorAgent(global_controls=controls)
        with self.assertRaises(PublishingPausedError):
            agent.run({"campaign_id": "c1", "platform_captions": {"instagram": "hi"}})

    def test_resume_publishing_clears_the_scoped_pause(self):
        controls = GlobalControls()
        controls.pause_publishing("temp")
        controls.resume_publishing()
        controls.guard_publishing()  # should not raise
        self.assertFalse(controls.publishing_paused)


if __name__ == "__main__":
    unittest.main()
