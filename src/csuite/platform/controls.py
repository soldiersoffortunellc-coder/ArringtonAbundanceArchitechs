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


@dataclass
class GlobalControls:
    paused: bool = False
    pause_reason: str | None = None
    offboarded_tenants: list = field(default_factory=list)

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
