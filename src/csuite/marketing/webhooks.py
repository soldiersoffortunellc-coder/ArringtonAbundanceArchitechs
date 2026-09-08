"""
Inbound webhook handling: signature verification, idempotency, and
normalization for the three genuinely code-shaped operational workflows
(video-provider completion, iDecide completion, comment/DM keyword
capture). See config/marketing/workflow_blueprints.json for how these fit
alongside the GHL-UI-only workflow blueprints.

SECURITY MODEL — every payload here is UNTRUSTED EXTERNAL INPUT:
  - Social comments, DMs, and any text inside a webhook payload are treated
    as DATA ONLY. Nothing in this module ever evaluates, executes, or
    formats that text as an instruction, a prompt, or code. It is sanitized
    and stored as a plain string; keyword matching is a literal substring
    check against a configured allow-list, not a language-model call.
  - Signature verification uses HMAC-SHA256 over the raw payload bytes
    compared with `hmac.compare_digest` (constant-time). The exact header
    name / signing scheme differs per provider (GHL, an avatar-video
    provider, iDecide) and must be confirmed against that provider's actual
    docs before going live — this module implements the verification
    primitive correctly; wiring the right header name per provider is a
    configuration step, not a code change.
  - Idempotency: every handler requires an event id and refuses to process
    the same one twice (IdempotencyStore), because a provider (iDecide
    explicitly, per its own spec) may re-fire a completion webhook.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from dataclasses import dataclass, field


class WebhookSignatureError(Exception):
    pass


class WebhookPayloadError(Exception):
    pass


_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MAX_SANITIZED_TEXT_LENGTH = 2000


def sanitize_untrusted_text(text: str) -> str:
    """Strips control characters and truncates. Never evaluated, never executed, never used as a prompt."""
    if not isinstance(text, str):
        raise WebhookPayloadError(f"Expected a string, got {type(text).__name__}.")
    cleaned = _CONTROL_CHARS_RE.sub("", text)
    return cleaned[:MAX_SANITIZED_TEXT_LENGTH]


def verify_signature(payload_bytes: bytes, provided_signature: str, secret: str) -> bool:
    if not secret:
        raise WebhookSignatureError("No webhook secret configured — refusing to accept an unsigned webhook.")
    expected = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided_signature or "")


class IdempotencyStore:
    """In-memory dedupe of processed webhook event ids. Swap for a real store in production (see docs/13)."""

    def __init__(self):
        self._seen: dict[str, float] = {}

    def already_processed(self, event_id: str) -> bool:
        return event_id in self._seen

    def mark_processed(self, event_id: str) -> None:
        self._seen[event_id] = time.time()


@dataclass
class NormalizedWebhookEvent:
    event_type: str
    event_id: str
    duplicate: bool
    data: dict = field(default_factory=dict)


class WebhookEventProcessor:
    def __init__(self, idempotency_store: IdempotencyStore | None = None, keyword_allowlist: list[str] | None = None):
        self.idempotency_store = idempotency_store or IdempotencyStore()
        self.keyword_allowlist = keyword_allowlist or ["AGENT", "WEALTH"]

    def _check_idempotency(self, event_id: str) -> bool:
        """Returns True if this is a duplicate (already processed)."""
        if not event_id:
            raise WebhookPayloadError("Webhook payload is missing an event id — cannot guarantee idempotency.")
        duplicate = self.idempotency_store.already_processed(event_id)
        if not duplicate:
            self.idempotency_store.mark_processed(event_id)
        return duplicate

    def handle_video_completion(self, payload: dict, *, signature: str | None = None, secret: str | None = None, raw_bytes: bytes | None = None) -> NormalizedWebhookEvent:
        if secret:
            if raw_bytes is None:
                raise WebhookSignatureError("raw_bytes required to verify a signed webhook.")
            if not verify_signature(raw_bytes, signature or "", secret):
                raise WebhookSignatureError("Video-provider webhook signature verification failed.")

        event_id = str(payload.get("event_id") or payload.get("job_id") or "")
        duplicate = self._check_idempotency(event_id)

        return NormalizedWebhookEvent(
            event_type="video_completion",
            event_id=event_id,
            duplicate=duplicate,
            data={
                "provider_job_id": payload.get("job_id"),
                "status": payload.get("status"),
                "asset_url": payload.get("asset_url"),
                "cost_actual": payload.get("cost"),
                "error": payload.get("error"),
            },
        )

    def handle_idecide_completion(self, payload: dict, *, signature: str | None = None, secret: str | None = None, raw_bytes: bytes | None = None) -> NormalizedWebhookEvent:
        if secret:
            if raw_bytes is None:
                raise WebhookSignatureError("raw_bytes required to verify a signed webhook.")
            if not verify_signature(raw_bytes, signature or "", secret):
                raise WebhookSignatureError("iDecide webhook signature verification failed.")

        event_id = str(payload.get("event_id") or "")
        duplicate = self._check_idempotency(event_id)

        return NormalizedWebhookEvent(
            event_type="idecide_completion",
            event_id=event_id,
            duplicate=duplicate,
            data={
                "session_id": payload.get("session_id"),
                "contact_id": payload.get("contact_id"),
                "final_cta": payload.get("final_cta"),
                "final_outcome": payload.get("final_outcome"),
                "viewer_choices": list(payload.get("viewer_choices", [])),
                "slides_viewed": payload.get("slides_viewed"),
                "completed_at": payload.get("completed_at"),
            },
        )

    def handle_comment_dm_capture(self, payload: dict, *, signature: str | None = None, secret: str | None = None, raw_bytes: bytes | None = None) -> NormalizedWebhookEvent:
        """
        Social comments and DMs are the highest-risk inbound surface for
        prompt injection — the sanitized text below is NEVER interpreted as
        an instruction, only matched against a literal keyword allow-list.
        """
        if secret:
            if raw_bytes is None:
                raise WebhookSignatureError("raw_bytes required to verify a signed webhook.")
            if not verify_signature(raw_bytes, signature or "", secret):
                raise WebhookSignatureError("Platform webhook signature verification failed.")

        event_id = str(payload.get("event_id") or "")
        duplicate = self._check_idempotency(event_id)

        raw_text = payload.get("text", "")
        sanitized = sanitize_untrusted_text(raw_text) if raw_text else ""
        matched_keyword = next(
            (kw for kw in self.keyword_allowlist if kw.lower() in sanitized.lower()),
            None,
        )

        return NormalizedWebhookEvent(
            event_type="comment_dm_capture",
            event_id=event_id,
            duplicate=duplicate,
            data={
                "platform": payload.get("platform"),
                "contact_ref": payload.get("contact_ref"),
                "sanitized_text": sanitized,
                "matched_keyword": matched_keyword,
            },
        )
