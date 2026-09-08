import unittest

from csuite.marketing.models import new_campaign, SocialPost
from csuite.marketing.store import CampaignStore, DuplicateCampaignError


class TestDuplicatePublishingPrevention(unittest.TestCase):
    def setUp(self):
        self.store = CampaignStore()
        self.campaign = new_campaign("open_doors_financial_group", "coach_rashon", "financial_education")
        self.store.add_campaign(self.campaign)

    def test_identical_content_on_same_platform_is_rejected(self):
        post1 = SocialPost(post_id="p1", campaign_id=self.campaign.campaign_id, platform="instagram",
                            caption="Same caption", status="SCHEDULED", content_hash="hash-abc")
        self.store.add_social_post(post1)

        post2 = SocialPost(post_id="p2", campaign_id=self.campaign.campaign_id, platform="instagram",
                            caption="Same caption", status="SCHEDULED", content_hash="hash-abc")
        with self.assertRaises(DuplicateCampaignError):
            self.store.add_social_post(post2)

    def test_same_content_on_different_platforms_is_allowed(self):
        post1 = SocialPost(post_id="p1", campaign_id=self.campaign.campaign_id, platform="instagram",
                            caption="Same caption", status="SCHEDULED", content_hash="hash-abc")
        post2 = SocialPost(post_id="p2", campaign_id=self.campaign.campaign_id, platform="tiktok",
                            caption="Same caption", status="SCHEDULED", content_hash="hash-abc")
        self.store.add_social_post(post1)
        self.store.add_social_post(post2)  # should not raise
        self.assertEqual(len(self.store.social_posts[self.campaign.campaign_id]), 2)

    def test_draft_posts_do_not_block_future_publishing(self):
        draft = SocialPost(post_id="p1", campaign_id=self.campaign.campaign_id, platform="instagram",
                            caption="Draft only", status="DRAFT", content_hash="hash-draft")
        self.store.add_social_post(draft)
        # a DRAFT (never scheduled/published) shouldn't lock the content hash
        scheduled = SocialPost(post_id="p2", campaign_id=self.campaign.campaign_id, platform="instagram",
                                caption="Draft only", status="SCHEDULED", content_hash="hash-draft")
        self.store.add_social_post(scheduled)  # should not raise


if __name__ == "__main__":
    unittest.main()
