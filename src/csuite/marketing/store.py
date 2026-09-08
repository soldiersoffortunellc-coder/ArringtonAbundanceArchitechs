"""
CampaignStore — the in-memory repository for campaigns and everything
attached to them (briefs, script versions, compliance reviews, approval
records, video jobs, social posts). Mirrors the existing
csuite.platform.tenant.TenantRegistry pattern: no database exists in this
repo (see docs/13), so this is the same "registry object with public
methods a real store can later sit behind" convention already used
throughout the codebase.
"""

from __future__ import annotations

from csuite.marketing.campaign_state_machine import CampaignStateMachine
from csuite.marketing.models import (
    Campaign, CampaignBrief, ScriptVersion, ComplianceReview, ApprovalRecord,
    VideoGenerationJob, SocialPost,
)


class DuplicateCampaignError(Exception):
    pass


class CampaignStore:
    def __init__(self):
        self.campaigns: dict[str, Campaign] = {}
        self.state_machines: dict[str, CampaignStateMachine] = {}
        self.briefs: dict[str, CampaignBrief] = {}
        self.script_versions: dict[str, list[ScriptVersion]] = {}  # campaign_id -> versions
        self.compliance_reviews: dict[str, list[ComplianceReview]] = {}
        self.approval_records: dict[str, list[ApprovalRecord]] = {}
        self.video_jobs: dict[str, VideoGenerationJob] = {}
        self.social_posts: dict[str, list[SocialPost]] = {}
        self._published_content_hashes: set[tuple[str, str]] = set()  # (platform, content_hash)

    def add_campaign(self, campaign: Campaign) -> CampaignStateMachine:
        if campaign.campaign_id in self.campaigns:
            raise DuplicateCampaignError(f"Campaign '{campaign.campaign_id}' already exists.")
        self.campaigns[campaign.campaign_id] = campaign
        sm = CampaignStateMachine(campaign)
        self.state_machines[campaign.campaign_id] = sm
        return sm

    def get_campaign(self, campaign_id: str) -> Campaign:
        return self.campaigns[campaign_id]

    def get_state_machine(self, campaign_id: str) -> CampaignStateMachine:
        return self.state_machines[campaign_id]

    def add_brief(self, brief: CampaignBrief) -> None:
        self.briefs[brief.brief_id] = brief
        self.campaigns[brief.campaign_id].brief_id = brief.brief_id

    def add_script_version(self, version: ScriptVersion) -> None:
        self.script_versions.setdefault(version.campaign_id, []).append(version)
        self.campaigns[version.campaign_id].current_version_id = version.version_id

    def latest_script_version(self, campaign_id: str) -> ScriptVersion | None:
        versions = self.script_versions.get(campaign_id, [])
        return versions[-1] if versions else None

    def add_compliance_review(self, review: ComplianceReview) -> None:
        self.compliance_reviews.setdefault(review.campaign_id, []).append(review)

    def latest_compliance_review(self, campaign_id: str) -> ComplianceReview | None:
        reviews = self.compliance_reviews.get(campaign_id, [])
        return reviews[-1] if reviews else None

    def add_approval_record(self, record: ApprovalRecord) -> None:
        self.approval_records.setdefault(record.campaign_id, []).append(record)

    def add_video_job(self, job: VideoGenerationJob) -> None:
        self.video_jobs[job.job_id] = job

    def add_social_post(self, post: SocialPost) -> None:
        """Prevents duplicate publishing: refuses a second post with the same
        (platform, content_hash) pair that has already reached PUBLISHED or SCHEDULED."""
        key = (post.platform, post.content_hash)
        if post.content_hash and key in self._published_content_hashes:
            raise DuplicateCampaignError(
                f"A post with identical content already exists for platform '{post.platform}' "
                f"(content_hash={post.content_hash}). Refusing duplicate publish."
            )
        self.social_posts.setdefault(post.campaign_id, []).append(post)
        if post.content_hash and post.status in ("SCHEDULED", "PUBLISHED"):
            self._published_content_hashes.add(key)

    def mark_post_published(self, post: SocialPost) -> None:
        if post.content_hash:
            self._published_content_hashes.add((post.platform, post.content_hash))
