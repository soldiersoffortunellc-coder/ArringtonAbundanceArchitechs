"""AI Video Production Director — reports to the CMO."""

from __future__ import annotations

import uuid

from csuite.agents.base import BaseAgent
from csuite.marketing.models import VideoGenerationJob
from csuite.providers.avatar_video_adapter import AvatarVideoAdapter, ConsentRequiredError
from csuite.providers.base import ProviderAction


class AIVideoProductionDirectorAgent(BaseAgent):
    name = "ai_video_production_director"
    title = "AI Video Production Director"
    mission = "Convert approved scripts into structured, tracked video-generation jobs — never using a likeness/voice without documented authorization."
    kpis_owned = ["jobs_submitted", "jobs_failed", "jobs_completed", "total_cost_estimate"]
    ghl_authority = []

    def __init__(self, *args, avatar_adapter: AvatarVideoAdapter | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.avatar_adapter = avatar_adapter or AvatarVideoAdapter()

    def run(self, context: dict):
        """
        context = {
            "campaign_id": str, "version_id": str, "script_text": str,
            "consent_authorization_id": str | None, "aspect_ratio": "9:16",
            "scene_instructions": {...},  # captions, b-roll, branding, logo, background, music, CTA end card, disclosure overlays
        }
        """
        if self.global_controls is not None:
            self.global_controls.guard_publishing()  # video generation is a publishing-cost action — scoped kill switch applies
        report = self.new_report()

        try:
            action = self.avatar_adapter.submit_job(
                campaign_id=context["campaign_id"], version_id=context["version_id"],
                script_text=context["script_text"], consent_authorization_id=context.get("consent_authorization_id"),
                aspect_ratio=context.get("aspect_ratio", "9:16"), scene_instructions=context.get("scene_instructions"),
            )
        except ConsentRequiredError as exc:
            report.escalations.append(str(exc))
            report.kpis["jobs_submitted"] = 0
            return report

        job = VideoGenerationJob(
            job_id=str(uuid.uuid4()), campaign_id=context["campaign_id"], version_id=context["version_id"],
            provider=self.avatar_adapter.provider_name, provider_job_id=action.result.get("provider_job_id"),
            status=action.result.get("status", "SUBMITTED"),
        )
        report.directives_issued.append(action.action_id)
        report.decisions.append(f"Submitted video-generation job {job.job_id} (provider job {job.provider_job_id}) for campaign {job.campaign_id}.")
        report.kpis["jobs_submitted"] = 1
        report.kpis["video_job"] = job
        return report

    def handle_completion(self, job: VideoGenerationJob, normalized_event: dict) -> VideoGenerationJob:
        """Applies a normalized video-completion webhook event (see marketing.webhooks) to a tracked job."""
        job.status = normalized_event.get("status", job.status)
        job.final_asset_url = normalized_event.get("asset_url", job.final_asset_url)
        job.cost_actual = normalized_event.get("cost_actual", job.cost_actual)
        if job.status == "COMPLETED":
            import time
            job.completed_at = time.time()
        return job

    def retry(self, job: VideoGenerationJob) -> ProviderAction:
        job.attempts += 1
        action = self.avatar_adapter.retry_job(job.provider_job_id, job.attempts, job.max_attempts)
        job.status = action.result.get("status", job.status)
        return action
