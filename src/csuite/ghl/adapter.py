"""
GHLAdapter — the single choke point every agent uses to "direct" GoHighLevel.

Design intent (per operating rules):
  - Every integration defaults to dry_run=True. No agent may flip that from
    inside the system; only an explicit, human-driven construction of the
    adapter with dry_run=False and live_authorized=True enables real calls.
  - Live mode additionally requires an explicit `api_client` (a
    `GHLApiClient`, see api_client.py) to be supplied — there is no implicit
    credential lookup inside the adapter itself. `_live_call` dispatches
    each action kind to a real GHL API v2 call over that client where the
    public API supports it, and raises `GHLUnsupportedActionError` for the
    handful of actions GoHighLevel's public API does not expose (see
    docs/12-live-ghl-connection.md for exactly which is which).
  - Every action taken is recorded to `self.actions` (an in-memory audit log)
    so tests and the executive dashboard can verify exactly what the system
    *would have done* (dry-run) or *did* (live) to a real GHL account.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from csuite.ghl.api_client import GHLApiClient, GHLUnsupportedActionError


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
    explicitly by a human-driven caller (never inferred, never defaulted),
    AND an `api_client` instance (credentials come from environment
    variables read by GHLApiClient — never hardcoded, never passed as a
    plain string here). See docs/12-live-ghl-connection.md.
    """

    def __init__(
        self,
        dry_run: bool = True,
        live_authorized: bool = False,
        tenant_id: str | None = None,
        api_client: GHLApiClient | None = None,
    ):
        if not dry_run and not live_authorized:
            raise LiveModeNotAuthorized(
                "Refusing to construct a live GHLAdapter without live_authorized=True. "
                "Live/paid integrations must be explicitly authorized by the business owner."
            )
        if not dry_run and api_client is None:
            raise LiveModeNotAuthorized(
                "Refusing to construct a live GHLAdapter without an api_client. "
                "Pass GHLAdapter(dry_run=False, live_authorized=True, api_client=GHLApiClient()) "
                "once GHL_ACCESS_TOKEN is set. See docs/12-live-ghl-connection.md."
            )
        self.dry_run = dry_run
        self.live_authorized = live_authorized
        self.tenant_id = tenant_id
        self.api_client = api_client
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

    # Action kinds GoHighLevel's public API v2 does not (as of this writing)
    # expose a documented way to perform at runtime. These must be baked
    # into a snapshot at design time, or done through the GHL UI / SaaS
    # Configurator. Listed explicitly so a live call fails loudly and
    # specifically instead of hitting a guessed, possibly-wrong endpoint.
    _UNSUPPORTED_LIVE_ACTIONS = {
        "apply_snapshot": (
            "Applying a snapshot to an EXISTING location is a GHL UI/agency-console action, "
            "not a documented public API call. A snapshot can only be attached via the "
            "'snapshotId' field at location-CREATION time (see create_location). Build the "
            "snapshot inside GHL first and pass its real snapshot_id there."
        ),
        "create_pipeline": (
            "GoHighLevel's public API does not expose pipeline creation. Pipelines must be "
            "created once in the GHL UI (or shipped inside a snapshot) and then referenced by "
            "their real pipeline_id for opportunity operations."
        ),
        "create_workflow": (
            "GoHighLevel's public API does not expose workflow creation. Workflows must be "
            "built in the GHL UI (or shipped inside a snapshot); the API can only add contacts "
            "to an existing workflow, not define a new one."
        ),
        "publish_campaign": (
            "There is no generic public 'publish campaign' endpoint. Route this through the "
            "specific channel's real endpoint (e.g. Conversations API for a message blast, or "
            "Workflows for an automation) once that campaign exists inside GHL."
        ),
        "create_billing_event": (
            "Agency billing/subscription events are managed through GHL's SaaS Configurator, "
            "which has its own account-level setup and is not a generic billing-event endpoint. "
            "Wire this to the SaaS Configurator API specifically once that's configured."
        ),
    }

    def _live_call(self, kind: str, payload: dict) -> dict:
        if kind in self._UNSUPPORTED_LIVE_ACTIONS:
            raise GHLUnsupportedActionError(f"[{kind}] {self._UNSUPPORTED_LIVE_ACTIONS[kind]}")

        client = self.api_client

        if kind == "create_location":
            # Requires an agency-level OAuth token with the locations.write scope.
            # NOTE: GHL's create-location body needs more than these three fields in
            # practice (e.g. companyId, address/timezone, and optionally snapshotId to
            # apply a snapshot at creation time). This maps only the fields this system
            # tracks internally — extend the body per your agency's actual GHL account
            # requirements before relying on this in production.
            body = {
                "name": payload["client_name"],
                "customFields": [{"key": "industry_vertical", "value": payload["industry"]}],
            }
            return client.post("/locations/", json_body=body)

        if kind == "create_users":
            created = [client.post("/users/", json_body=u) for u in payload["users"]]
            return {"created": len(created), "users": created}

        if kind == "create_custom_fields":
            location_id = payload["location_id"]
            created = [
                client.post(f"/locations/{location_id}/customFields", json_body={"name": f})
                for f in payload["fields"]
            ]
            return {"created": len(created), "fields": created}

        if kind == "create_calendar":
            return client.post("/calendars/", json_body={
                "locationId": payload["location_id"],
                "name": payload["calendar_name"],
            })

        if kind == "tag_contact":
            return client.post(
                f"/contacts/{payload['contact_id']}/tags",
                json_body={"tags": [payload["tag"]]},
            )

        if kind == "create_opportunity":
            return client.post("/opportunities/", json_body={
                "locationId": payload["location_id"],
                "pipelineId": payload["pipeline_name"],  # caller must pass a real pipeline_id
                "name": payload.get("name", payload["pipeline_name"]),
                "status": payload["stage"],
                "monetaryValue": payload["value"],
            })

        if kind == "update_opportunity_stage":
            body = {"pipelineStageId": payload["new_stage"]}
            if payload.get("loss_reason"):
                body["status"] = "lost"
            return client.put(f"/opportunities/{payload['opportunity_id']}", json_body=body)

        if kind == "send_notification":
            return client.post("/conversations/messages", json_body={
                "locationId": payload["location_id"],
                "type": payload["channel"].upper(),
                "contactId": payload["to"],
                "message": payload["template"],
            })

        raise GHLUnsupportedActionError(
            f"'{kind}' has no live implementation wired up in GHLAdapter._live_call. "
            "Add it to api_client.py / adapter.py once you've confirmed the real endpoint."
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
