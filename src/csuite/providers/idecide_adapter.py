"""
IDecideAdapter — the interactive-presentation layer between marketing
campaigns and GHL pipelines. See docs/15-idecide-integration.md for the
full capability matrix; NO iDecide API has been confirmed from this
environment, so this adapter is built against the generic webhook +
link-token shape common to this class of tool and is dry-run/mock by
default like every other provider adapter here. Every method that would
touch a real iDecide account raises the same NotImplementedError path as
GHLAdapter's `_live_call` until credentials + a confirmed API exist.

Idempotency is mandatory here specifically because iDecide may re-fire the
completion webhook for the same session — `record_completion_event` refuses
to process a duplicate `event_id` twice.
"""

from __future__ import annotations

import uuid

from csuite.marketing.webhooks import IdempotencyStore
from csuite.providers.base import ProviderAdapterBase, ProviderAction


class IDecideAdapter(ProviderAdapterBase):
    provider_name = "idecide"

    def __init__(self, dry_run: bool = True, live_authorized: bool = False, idempotency_store: IdempotencyStore | None = None):
        super().__init__(dry_run=dry_run, live_authorized=live_authorized)
        self.idempotency_store = idempotency_store or IdempotencyStore()

    def create_personalized_link(
        self, *, presentation_id: str, version_id: str, contact_id: str,
        campaign_id: str | None, assigned_agent: str | None,
    ) -> ProviderAction:
        return self._dispatch(
            "create_personalized_link",
            {"presentation_id": presentation_id, "version_id": version_id, "contact_id": contact_id,
             "campaign_id": campaign_id, "assigned_agent": assigned_agent},
            {"link_id": f"idecide_link_{uuid.uuid4().hex[:12]}", "url": f"mock://idecide/{presentation_id}/{contact_id}"},
        )

    def record_started_event(self, *, session_id: str, link_id: str, contact_id: str) -> ProviderAction:
        return self._dispatch(
            "record_started_event", {"session_id": session_id, "link_id": link_id, "contact_id": contact_id},
            {"recorded": True},
        )

    def record_completion_event(self, event_id: str, payload: dict) -> ProviderAction:
        """Idempotent: a duplicate event_id is recorded as such and never double-processed downstream."""
        duplicate = self.idempotency_store.already_processed(event_id)
        if not duplicate:
            self.idempotency_store.mark_processed(event_id)
        return self._dispatch(
            "record_completion_event", {"event_id": event_id, "payload": payload},
            {"duplicate": duplicate, "processed": not duplicate},
        )

    def isolate_session_for_contact(self, session_id: str, requesting_contact_id: str, owning_contact_id: str) -> ProviderAction:
        """Cross-contact isolation guard: refuses to hand back session data for a contact that doesn't own it."""
        allowed = requesting_contact_id == owning_contact_id
        return self._dispatch(
            "isolate_session_for_contact",
            {"session_id": session_id, "requesting_contact_id": requesting_contact_id, "owning_contact_id": owning_contact_id},
            {"access_granted": allowed},
        )
