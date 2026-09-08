import unittest

from csuite.orchestrator import RevenueOperatingSystem
from csuite.ghl.adapter import GHLAdapter


class TestAgentRoster(unittest.TestCase):
    def setUp(self):
        self.ros = RevenueOperatingSystem(adapter=GHLAdapter(dry_run=True))

    def test_at_least_five_c_suite_level_agents_exist(self):
        c_suite = [self.ros.ceo, self.ros.cro, self.ros.cmo, self.ros.coo, self.ros.cfo, self.ros.cto, self.ros.cco]
        self.assertGreaterEqual(len(c_suite), 5)
        titles = {a.title for a in c_suite}
        self.assertEqual(len(titles), len(c_suite), "every C-suite agent must have a distinct title")

    def test_every_c_suite_agent_has_a_mission_and_owned_kpis(self):
        c_suite = [self.ros.ceo, self.ros.cro, self.ros.cmo, self.ros.coo, self.ros.cfo, self.ros.cto, self.ros.cco]
        for agent in c_suite:
            self.assertTrue(agent.mission, f"{agent.name} has no mission")
            self.assertTrue(agent.kpis_owned, f"{agent.name} owns no KPIs")

    def test_cro_directs_six_revenue_subordinates(self):
        self.assertEqual(len(self.ros.cro.subordinates), 6)

    def test_full_roster_is_thirteen_task_oriented_agents(self):
        roster = self.ros.agent_roster()
        self.assertEqual(len(roster), 13)

    def test_run_cycle_produces_a_report_from_every_c_suite_agent(self):
        result = self.ros.run_cycle({})
        for key in ("ceo", "cro", "cmo", "coo", "cfo", "cto", "cco"):
            self.assertIn(key, result)
            self.assertIn("kpis", result[key])


if __name__ == "__main__":
    unittest.main()
