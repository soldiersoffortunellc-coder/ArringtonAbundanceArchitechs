import unittest

from csuite.providers.idecide_adapter import IDecideAdapter
from csuite.marketing.lead_scoring import LeadScoringEngine


class TestIDecideIntegration(unittest.TestCase):
    def setUp(self):
        self.adapter = IDecideAdapter()

    def test_personalized_link_creation(self):
        action = self.adapter.create_personalized_link(
            presentation_id="pres_1", version_id="v1", contact_id="contact_1",
            campaign_id="camp_1", assigned_agent="agent_1",
        )
        self.assertIn("link_id", action.result)
        self.assertIn("url", action.result)

    def test_repeat_completion_events_are_idempotent(self):
        first = self.adapter.record_completion_event("evt_1", {"outcome": "book_a_call"})
        second = self.adapter.record_completion_event("evt_1", {"outcome": "book_a_call"})
        self.assertFalse(first.result["duplicate"])
        self.assertTrue(second.result["duplicate"])
        self.assertTrue(first.result["processed"])
        self.assertFalse(second.result["processed"])

    def test_cross_contact_isolation_blocks_wrong_contact(self):
        action = self.adapter.isolate_session_for_contact("session_1", requesting_contact_id="contact_B", owning_contact_id="contact_A")
        self.assertFalse(action.result["access_granted"])

    def test_cross_contact_isolation_allows_owning_contact(self):
        action = self.adapter.isolate_session_for_contact("session_1", requesting_contact_id="contact_A", owning_contact_id="contact_A")
        self.assertTrue(action.result["access_granted"])


class TestIDecideLeadScoring(unittest.TestCase):
    def setUp(self):
        self.engine = LeadScoringEngine()

    def test_scheduling_appointment_scores_high_intent(self):
        result = self.engine.score([
            "started_presentation", "completed_presentation",
            "selected_book_a_call", "selected_join_the_agency", "scheduled_appointment",
        ])  # 5 + 15 + 25 + 25 + 30 = 100
        self.assertEqual(result["classification"], "High Intent")

    def test_abandonment_is_penalized(self):
        result = self.engine.score(["started_presentation", "abandoned_before_cta"])
        self.assertEqual(result["score"], 0)  # clamped at floor

    def test_repeat_completion_is_recorded_but_not_auto_boosted(self):
        base = self.engine.score(["started_presentation", "completed_presentation"])
        with_repeat = self.engine.score(["started_presentation", "completed_presentation", "repeat_completion", "repeat_completion"])
        self.assertEqual(base["score"], with_repeat["score"])  # repeat_completion is worth 0 points by default
        self.assertEqual(with_repeat["repeat_completion_count"], 2)
        self.assertIsNotNone(with_repeat["repeat_completion_note"])

    def test_classification_thresholds_are_configurable_not_hardcoded_in_logic(self):
        custom_config = {
            "event_scores": {"completed_presentation": 100},
            "classifications": [{"min": 0, "max": 100, "label": "Everything Is Cold"}],
            "score_floor": 0, "score_ceiling": 100,
        }
        engine = LeadScoringEngine(config=custom_config)
        result = engine.score(["completed_presentation"])
        self.assertEqual(result["classification"], "Everything Is Cold")


if __name__ == "__main__":
    unittest.main()
