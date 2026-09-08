"""Social Distribution Director — reports to the CMO."""

from __future__ import annotations

import hashlib
import uuid

from csuite.agents.base import BaseAgent
from csuite.marketing.models import SocialPost
from csuite.marketing.store import CampaignStore, DuplicateCampaignError


def _content_hash(caption: str, media_ref: str | None) -> str:
    return hashlib.sha256(f"{caption}|{media_ref or ''}".encode("utf-8")).hexdigest()


class SocialDistributionDirectorAgent(BaseAgent):
    name = "social_distribution_director"
    title = "Social Distribution Director"
    mission = "Prepare approved content per platform for GHL Social Planner (or an authorized alternative), preventing duplicate publishing."
    kpis_owned = ["posts_scheduled", "duplicates_prevented", "posts_by_status"]
    ghl_authority = ["publish_campaign"]

    def __init__(self, *args, store: CampaignStore | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store or CampaignStore()

    def run(self, context: dict):
        """
        context = {
            "campaign_id": str, "platform_captions": {platform: caption}, "media_ref": str,
            "hashtags": {platform: [str]}, "scheduled_time": float | None, "location_id": str,
        }
        """
        if self.global_controls is not None:
            self.global_controls.guard_publishing()
        report = self.new_report()
        campaign_id = context["campaign_id"]
        media_ref = context.get("media_ref")
        location_id = context.get("location_id", "unprovisioned")

        scheduled = []
        duplicates_prevented = 0
        for platform, caption in context.get("platform_captions", {}).items():
            post = SocialPost(
                post_id=str(uuid.uuid4()), campaign_id=campaign_id, platform=platform, caption=caption,
                hashtags=context.get("hashtags", {}).get(platform, []),
                scheduled_time=context.get("scheduled_time"), status="SCHEDULED",
                content_hash=_content_hash(caption, media_ref),
            )
            try:
                self.store.add_social_post(post)
            except DuplicateCampaignError as exc:
                duplicates_prevented += 1
                report.warnings.append(str(exc))
                continue

            if self.adapter is not None:
                action = self.adapter.publish_campaign(location_id, f"{campaign_id}:{platform}")
                report.directives_issued.append(action.action_id)

            scheduled.append({"platform": platform, "post_id": post.post_id, "status": post.status})
            report.decisions.append(f"Scheduled post for campaign {campaign_id} on '{platform}' (post {post.post_id}).")

        report.kpis["posts_scheduled"] = scheduled
        report.kpis["duplicates_prevented"] = duplicates_prevented
        return report
