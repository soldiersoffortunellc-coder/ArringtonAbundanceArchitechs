import unittest

from csuite.platform.controls import GlobalControls, SystemPausedError
from csuite.agents.cmo import CMOAgent


class TestGlobalPause(unittest.TestCase):
    def test_guard_passes_when_not_paused(self):
        controls = GlobalControls()
        controls.guard()  # should not raise

    def test_guard_raises_when_paused(self):
        controls = GlobalControls()
        controls.pause("suspected billing anomaly")
        with self.assertRaises(SystemPausedError):
            controls.guard()

    def test_agent_write_action_is_blocked_while_paused(self):
        controls = GlobalControls()
        controls.pause("emergency stop")
        agent = CMOAgent(global_controls=controls)
        with self.assertRaises(SystemPausedError):
            agent.run({"campaigns": [{"name": "Should Not Publish", "channel": "outbound"}]})

    def test_resume_clears_pause(self):
        controls = GlobalControls()
        controls.pause("temporary")
        controls.resume()
        controls.guard()  # should not raise
        self.assertFalse(controls.paused)


if __name__ == "__main__":
    unittest.main()
