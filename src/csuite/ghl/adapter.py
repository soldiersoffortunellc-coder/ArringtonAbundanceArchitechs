"""
GHLAdapter — the single choke point every agent uses to "direct" GoHighLevel.

Design intent (per operating rules):
  - Every integration defaults to dry_run=True. No agent may flip that from
    inside the system; only an explicit, human-driven construction of the
    adapter with dry_run=False and live_authorized=True enables real calls.
  - Even in "live" mode, this module does not embed an actual GHL HTTP client
    (no API base URL, no API key handling) because no credentials have been
    supplied and no authorization to spend/publish has been granted. The
    `_live_call` hook is the single place a real `requests`/GHL SDK call
    would be wired in later, once credentials exist (see
    docs/09-credentials-and-ghl-ids.md).
  - Every action taken is recorded to `self.actions` (an in-memory audit log)
    so tests and the executive dashboard can verify exactly what the system
    *would have done* to a real GHL account.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


class LiveModeNotAuthorized(RuntimeError):
    """Raised when code attempts a live (non-dry-run) action without explicit authorization."""


@dataclass
class GHLAction:
    action_id: str
    kind: str
    payload: dict
    dry_run: bool
    timestamp: float
    result: dict = field(default_factory=dict)


class GHLAdapter:
    """
    A directed, auditable interface onto GoHighLevel concepts:
    locations (subaccounts), snapshots, pipelines, custom fields, workflows,
    calendars, contacts/opportunities, billing events, and outbound messages.

    dry_run=True (default): every method logs the intended action and returns
    a simulated result. Nothing leaves the process.

    dry_run=False requires live_authorized=True, which itself must be passed
    explicitly by a human-driven caller (never inferred, never defaulted).
    Even then, `_live_call` is a stub — wiring a real GHL API client is future
    work gated on credentials being supplied (see docs/09).
    """

    def __init__(self, dry_run: bool = True, live_authorized: bool = False, tenant_id: str | None = None):
        if not dry_run and not live_authorized:
            raise LiveModeNotAuthorized(
                "Refusing to construct a live GHLAdapter without live_authorized=True. "
                "Live/paid integrations must be explicitly authorized by the business owner."
            )
        self.dry_run = dry_run
        self.live_authorized = live_authorized
        self.tenant_id = tenant_id
        self.actions: list[GHLAction] = []

    # ---- internal plumbing -------------------------------------------------

    def _record(self, kind: str, payload: dict, result: dict) -> GHLAction:
        action = GHLAction(
            action_id=str(uuid.uuid4()),
            kind=kind,
            payload=payload,
            dry_run=self.dry_run,
            timestamp=time.time(),
            result=result,
        )
        self.actions.append(action)
        return action

    def _live_call(self, kind: str, payload: dict) -> dict:  # pragma: no cover - future integration point
        raise NotImplementedError(
            "Live GHL API integration is not wired up yet. Supply credentials per "
            "docs/09-credentials-and-ghl-ids.md and implement the real HTTP call here."
        )

    def _dispatch(self, kind: str, payload: dict, simulated_result: dict) -> GHLAction:
        if self.dry_run:
            result = {"status": "SIMULATED", **simulated_result}
        else:
            result = self._live_call(kind, payload)
        return self._record(kind, payload, result)

    # ---- subaccount / location lifecycle -----------------------------------

    def create_location(self, client_name: str, industry: str, plan_id: str) -> GHLAction:
        return self._dispatch(
            "create_location",
            {"client_name": client_name, "industry": industry, "plan_id": plan_id},
            {"location_id": f"loc_{uuid.uuid4().hex[:12]}"},
        )

    def apply_snapshot(self, location_id: str, snapshot_id: str, version: str) -> GHLAction:
        return self._dispatch(
            "apply_snapshot",
            {"location_id": location_id, "snapshot_id": snapshot_id, "version": version},
            {"applied": True},
        )

    def create_users(self, location_id: str, users: list[dict]) -> GHLAction:
        return self._dispatch(
            "create_users",
            {"location_id": location_id, "users": users},
            {"created": len(users)},
        )

    # ---- structural configuration ------------------------------------------

    def create_pipeline(self, location_id: str, pipeline_name: str, stages: list[str]) -> GHLAction:
        return self._dispatch(
            "create_pipeline",
            {"location_id": location_id, "pipeline_name": pipeline_name, "stages": stages},
            {"pipeline_id": f"pipe_{uuid.uuid4().hex[:12]}"},
        )

    def create_custom_fields(self, location_id: str, fields: list[str]) -> GHLAction:
        return self._dispatch(
            "create_custom_fields",
            {"location_id": location_id, "fields": fields},
            {"created": len(fields)},
        )

    def create_calendar(self, location_id: str, calendar_name: str) -> GHLAction:
        return self._dispatch(
            "create_calendar",
            {"location_id": location_id, "calendar_name": calendar_name},
            {"calendar_id": f"cal_{uuid.uuid4().hex[:12]}"},
        )

    def create_workflow(self, location_id: str, workflow_name: str) -> GHLAction:
        return self._dispatch(
            "create_workflow",
            {"location_id": location_id, "workflow_name": workflow_name},
            {"workflow_id": f"wf_{uuid.uuid4().hex[:12]}"},
        )

    # ---- contacts / opportunities -------------------------------------------

    def tag_contact(self, location_id: str, contact_id: str, tag: str) -> GHLAction:
        return self._dispatch(
            "tag_contact",
            {"location_id": location_id, "contact_id": contact_id, "tag": tag},
            {"tagged": True},
        )

    def create_opportunity(self, location_id: str, pipeline_name: str, stage: str, value: float) -> GHLAction:
        return self._dispatch(
            "create_opportunity",
            {"location_id": location_id, "pipeline_name": pipeline_name, "stage": stage, "value": value},
            {"opportunity_id": f"opp_{uuid.uuid4().hex[:12]}"},
        )

    def update_opportunity_stage(self, opportunity_id: str, new_stage: str, loss_reason: str | None = None) -> GHLAction:
        return self._dispatch(
            "update_opportunity_stage",
            {"opportunity_id": opportunity_id, "new_stage": new_stage, "loss_reason": loss_reason},
            {"updated": True},
        )

    # ---- messaging / publishing (always dry-run unless explicitly live) ----

    def send_notification(self, location_id: str, channel: str, to: str, template: str) -> GHLAction:
        return self._dispatch(
            "send_notification",
            {"location_id": location_id, "channel": channel, "to": to, "template": template},
            {"sent": True},
        )

    def publish_campaign(self, location_id: str, campaign_name: str) -> GHLAction:
        return self._dispatch(
            "publish_campaign",
            {"location_id": location_id, "campaign_name": campaign_name},
            {"published": True},
        )

    # ---- billing --------------------------------------------------------------

    def create_billing_event(self, location_id: str, event_type: str, amount: float, currency: str = "USD") -> GHLAction:
        return self._dispatch(
            "create_billing_event",
            {"location_id": location_id, "event_type": event_type, "amount": amount, "currency": currency},
            {"billing_event_id": f"bill_{uuid.uuid4().hex[:12]}"},
        )

    # ---- introspection ----------------------------------------------------

    def action_log(self) -> list[dict]:
        return [
            {
                "action_id": a.action_id,
                "kind": a.kind,
                "payload": a.payload,
                "dry_run": a.dry_run,
                "timestamp": a.timestamp,
                "result": a.result,
            }
            for a in self.actions
        ]
