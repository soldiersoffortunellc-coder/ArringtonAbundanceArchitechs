"""
Shared base for every non-GHL provider adapter (avatar video, voice,
social platform, storage, analytics, iDecide) — the exact same dry-run /
audit-log / live-authorization convention as csuite.ghl.adapter.GHLAdapter,
so every external integration in this system behaves identically.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


class ProviderLiveModeNotAuthorized(RuntimeError):
    """Raised when a provider adapter is asked to go live without explicit authorization."""


@dataclass
class ProviderAction:
    action_id: str
    kind: str
    payload: dict
    dry_run: bool
    timestamp: float
    result: dict = field(default_factory=dict)


class ProviderAdapterBase:
    """dry_run=True (default) — every action is simulated and logged. dry_run=False requires
    live_authorized=True, exactly like GHLAdapter."""

    provider_name = "unknown_provider"

    def __init__(self, dry_run: bool = True, live_authorized: bool = False):
        if not dry_run and not live_authorized:
            raise ProviderLiveModeNotAuthorized(
                f"Refusing to construct a live {self.provider_name} adapter without live_authorized=True."
            )
        self.dry_run = dry_run
        self.live_authorized = live_authorized
        self.actions: list[ProviderAction] = []

    def _record(self, kind: str, payload: dict, result: dict) -> ProviderAction:
        action = ProviderAction(
            action_id=str(uuid.uuid4()), kind=kind, payload=payload,
            dry_run=self.dry_run, timestamp=time.time(), result=result,
        )
        self.actions.append(action)
        return action

    def _live_call(self, kind: str, payload: dict) -> dict:
        raise NotImplementedError(
            f"Live {self.provider_name} integration is not wired up — this is a mock/dry-run-only "
            "adapter until a real provider SDK/API client is added and credentials are supplied."
        )

    def _dispatch(self, kind: str, payload: dict, simulated_result: dict) -> ProviderAction:
        result = {"status": "SIMULATED", **simulated_result} if self.dry_run else self._live_call(kind, payload)
        return self._record(kind, payload, result)

    def action_log(self) -> list[dict]:
        return [
            {"action_id": a.action_id, "kind": a.kind, "payload": a.payload, "dry_run": a.dry_run,
             "timestamp": a.timestamp, "result": a.result}
            for a in self.actions
        ]
