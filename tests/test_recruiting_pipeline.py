import unittest

from csuite.pipeline.recruiting_pipeline import (
    RecruitingPipeline,
    InvalidRecruitingStageError,
    DisqualificationReasonRequiredError,
)


class TestRecruitingPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = RecruitingPipeline()

    def test_new_candidate_starts_at_first_stage(self):
        candidate = self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        self.assertEqual(candidate.stage, "New Candidate (Meta Lead)")

    def test_disqualified_requires_a_valid_reason(self):
        candidate = self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        with self.assertRaises(DisqualificationReasonRequiredError):
            self.pipeline.move_stage(candidate.candidate_id, "Disqualified")

    def test_disqualified_with_invalid_reason_string_rejected(self):
        candidate = self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        with self.assertRaises(DisqualificationReasonRequiredError):
            self.pipeline.move_stage(candidate.candidate_id, "Disqualified", disqualification_reason="vibes")

    def test_disqualified_with_valid_reason_is_recorded(self):
        candidate = self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        updated = self.pipeline.move_stage(
            candidate.candidate_id, "Disqualified", disqualification_reason="non_responsive"
        )
        self.assertEqual(updated.disqualification_reason, "non_responsive")
        self.assertEqual(updated.stage, "Disqualified")

    def test_invalid_stage_name_rejected(self):
        candidate = self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        with self.assertRaises(InvalidRecruitingStageError):
            self.pipeline.move_stage(candidate.candidate_id, "Made Up Stage")

    def test_by_stage_buckets_all_defined_stages(self):
        self.pipeline.add_candidate("Jordan Lee", "meta_lead_ads", "unlicensed")
        buckets = self.pipeline.by_stage()
        self.assertIn("Active Agent", buckets)
        self.assertEqual(len(buckets["New Candidate (Meta Lead)"]), 1)


if __name__ == "__main__":
    unittest.main()
