"""
VoiceAdapter — optional, separate voice-generation provider (e.g.
ElevenLabs), used only when the avatar-video provider's built-in voice
isn't sufficient. Same consent requirement as AvatarVideoAdapter.
"""

from __future__ import annotations

import uuid

from csuite.providers.base import ProviderAdapterBase, ProviderAction


class ConsentRequiredError(Exception):
    pass


class VoiceAdapter(ProviderAdapterBase):
    provider_name = "voice"

    def generate_voice_clip(self, *, campaign_id: str, script_text: str, authorized_voice_id: str | None, consent_authorization_id: str | None) -> ProviderAction:
        if not consent_authorization_id or not authorized_voice_id:
            raise ConsentRequiredError(
                "VoiceAdapter.generate_voice_clip requires both an authorized_voice_id and a "
                "consent_authorization_id — refusing to synthesize a voice without documented authorization."
            )
        return self._dispatch(
            "generate_voice_clip",
            {"campaign_id": campaign_id, "script_text": script_text, "authorized_voice_id": authorized_voice_id,
             "consent_authorization_id": consent_authorization_id},
            {"clip_id": f"voice_clip_{uuid.uuid4().hex[:12]}", "status": "SUBMITTED"},
        )

    def check_status(self, clip_id: str) -> ProviderAction:
        return self._dispatch("check_status", {"clip_id": clip_id}, {"status": "PROCESSING"})
