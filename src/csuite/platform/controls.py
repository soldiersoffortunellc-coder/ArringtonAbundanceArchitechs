"""
Global pause switch and safe-offboarding routine.

The global pause is the emergency stop: when engaged, no agent may direct
any write action to GHL (messaging, publishing, billing, provisioning) for
any tenant. Safe offboarding is the controlled teardown of a single tenant
that preserves data and never destroys anything irreversibly without a
final confirmation flag.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from csuite.platform.tenant import TenantRegistry


class SystemPausedError(Exception):
    pass


class PublishingPausedError(Exception):
    """Raised by the Media & Marketing Division's scoped kill switch — distinct from SystemPausedError
    so publishing can be halted without pausing the whole Revenue OS, and vice versa."""


@dataclass
class GlobalControls:
    paused: bool = False
    pause_reason: str | None = None
    offboarded_tenants: list = field(default_factory=list)
    publishing_paused: bool = False
    publishing_pause_reason: str | None = None

    def pause(self, reason: str) -> None:
        self.paused = True
        self.pause_reason = reason

    def resume(self) -> None:
        self.paused = False
        self.pause_reason = None

    def guard(self) -> None:
        """Call at the top of any write-directing agent action."""
        if self.paused:
            raise SystemPausedError(f"System is globally paused: {self.pause_reason}")

    def pause_publishing(self, reason: str) -> None:
        """The Media & Marketing Division's own emergency stop: blocks every publish-directing
        agent action (social scheduling/publishing, video submission) without touching revenue
        operations. A full guard() pause also blocks publishing (it blocks everything); this is
        the narrower, publishing-only control requested alongside it."""
        self.publishing_paused = True
        self.publishing_pause_reason = reason

    def resume_publishing(self) -> None:
        self.publishing_paused = False
        self.publishing_pause_reason = None

    def guard_publishing(self) -> None:
        """Call at the top of any action that would submit a video job or schedule/publish a post."""
        self.guard()  # a full system pause also blocks publishing
        if self.publishing_paused:
            raise PublishingPausedError(f"Publishing is paused: {self.publishing_pause_reason}")

    def safe_offboard(self, tenant_registry: TenantRegistry, tenant_id: str, confirm: bool = False) -> dict:
        if not confirm:
            raise ValueError(
                "safe_offboard requires confirm=True — this is a deliberately non-default, "
                "explicit action to prevent accidental client teardown."
            )
        tenant = tenant_registry.get(tenant_id)
        # data is retained (not deleted) — offboarding suspends access, it does not destroy history.
        snapshot_of_data = dict(tenant.data)
        self.offboarded_tenants.append(tenant_id)
        return {
            "tenant_id": tenant_id,
            "location_id": tenant.location_id,
            "retained_data_keys": list(snapshot_of_data.keys()),
            "status": "OFFBOARDED",
        }
