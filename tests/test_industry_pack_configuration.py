import unittest

from csuite.ghl.snapshots import load_industry_pack, load_universal_core, SnapshotError


class TestIndustryPackConfiguration(unittest.TestCase):
    def test_all_three_priority_industry_packs_load(self):
        for industry in ("insurance_agency", "real_estate", "home_services"):
            pack = load_industry_pack(industry)
            self.assertEqual(pack["layer"], "industry_pack")
            self.assertEqual(pack["extends"], "universal_core")
            self.assertIn("components", pack)

    def test_industry_pack_declares_the_problems_it_solves(self):
        pack = load_industry_pack("home_services")
        self.assertGreater(len(pack["problems_solved"]), 0)

    def test_universal_core_is_industry_agnostic(self):
        core = load_universal_core()
        self.assertNotIn("industry", core)

    def test_unsupported_industry_raises_snapshot_error(self):
        with self.assertRaises(SnapshotError):
            load_industry_pack("nonexistent_industry")


if __name__ == "__main__":
    unittest.main()
