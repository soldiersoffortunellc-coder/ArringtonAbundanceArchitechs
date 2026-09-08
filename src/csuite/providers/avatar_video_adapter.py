"""
AvatarVideoAdapter — replaceable provider adapter for an authorized
digital-twin/avatar video platform (e.g. HeyGen). Mock/dry-run by default.

Never submit a job without a ConsentAuthorization reference — this adapter
refuses (ConsentRequiredError) rather than silently proceeding, per "Never
create or use another person's image, likeness, avatar, or voice without
documented authorization."

NOTE on `result["status"]`: unlike GHLAdapter (where the dispatch wrapper's
"status" field is reserved to mean SIMULATED/LIVE), here it intentionally
carries the video job's own lifecycle state (SUBMITTED / PROCESSING /
COMPLETED / RETRYING / DEAD_LETTER) since callers need that. Whether a call
was simulated is tracked separately on the action itself (`action.dry_run`).
"""

from __future__ import annotations

import uuid

from csuite.providers.base import ProviderAdapterBase, ProviderAction


class ConsentRequiredError(Exception):
    pass


class AvatarVideoAdapter(ProviderAdapterBase):
    provider_name = "avatar_video"

    def submit_job(
        self,
        *,
        campaign_id: str,
        version_id: str,
        script_text: str,
        consent_authorization_id: str | None,
        aspect_ratio: str = "9:16",
        scene_instructions: dict | None = None,
    ) -> ProviderAction:
        if not consent_authorization_id:
            raise ConsentRequiredError(
                "AvatarVideoAdapter.submit_job requires a consent_authorization_id — "
                "refusing to generate a likeness/voice video without documented authorization."
            )
        return self._dispatch(
            "submit_job",
            {
                "campaign_id": campaign_id, "version_id": version_id, "script_text": script_text,
                "consent_authorization_id": consent_authorization_id, "aspect_ratio": aspect_ratio,
                "scene_instructions": scene_instructions or {},
            },
            {"provider_job_id": f"avatar_job_{uuid.uuid4().hex[:12]}", "status": "SUBMITTED", "cost_estimate": None},
        )

    def check_status(self, provider_job_id: str) -> ProviderAction:
        return self._dispatch("check_status", {"provider_job_id": provider_job_id}, {"status": "PROCESSING"})

    def retrieve_video(self, provider_job_id: str) -> ProviderAction:
        return self._dispatch(
            "retrieve_video", {"provider_job_id": provider_job_id},
            {"status": "COMPLETED", "asset_url": f"mock://avatar-video/{provider_job_id}.mp4"},
        )

    def retry_job(self, provider_job_id: str, attempt: int, max_attempts: int) -> ProviderAction:
        if attempt > max_attempts:
            return self._dispatch(
                "retry_job", {"provider_job_id": provider_job_id, "attempt": attempt, "max_attempts": max_attempts},
                {"status": "DEAD_LETTER", "note": "Max retry attempts exhausted — routed for manual recovery."},
            )
        return self._dispatch(
            "retry_job", {"provider_job_id": provider_job_id, "attempt": attempt, "max_attempts": max_attempts},
            {"status": "RETRYING"},
        )

    def estimate_cost(self, script_text: str, aspect_ratio: str = "9:16") -> ProviderAction:
        # crude, provider-agnostic placeholder estimate (chars-based); replace with a real provider rate card.
        estimated = round(len(script_text) * 0.01, 2)
        return self._dispatch("estimate_cost", {"script_text": script_text, "aspect_ratio": aspect_ratio}, {"cost_estimate": estimated})
