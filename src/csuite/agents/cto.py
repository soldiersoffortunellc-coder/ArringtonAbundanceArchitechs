"""Chief Technology Officer (CTO) — owns the GHL integration, snapshot technical config, and tenant isolation integrity."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.ghl.snapshots import validate_client_config
from csuite.platform.tenant import TenantRegistry, TenantIsolationError
from csuite.platform.usage_limits import UsageLimitTracker, UsageLimitExceededError


class CTOAgent(BaseAgent):
    name = "cto"
    title = "Chief Technology Officer"
    mission = "Own the GHL technical architecture: snapshot integrity, tenant isolation, credentials, and AI usage limits."
    kpis_owned = ["snapshot_validation_failures", "tenant_isolation_violations_blocked", "usage_over_cap_accounts"]
    ghl_authority = ["manage_ghl_integration", "manage_snapshot_technical_config"]

    def __init__(
        self,
        *args,
        tenant_registry: TenantRegistry | None = None,
        usage_tracker: UsageLimitTracker | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tenant_registry = tenant_registry or TenantRegistry()
        self.usage_tracker = usage_tracker or UsageLimitTracker()

    def run(self, context: dict):
        """
        context = {
            "pending_client_configs": [{"industry": str, "client_config": dict, "tenant_id": str}, ...],
            "usage_events": [{"tenant_id": str, "tier": str, "metric": str, "amount": int}, ...],
            "isolation_checks": [{"requesting_tenant_id": str, "owner_tenant_id": str, "key": str}, ...],
        }
        """
        report = self.new_report()

        validation_failures = []
        for pending in context.get("pending_client_configs", []):
            missing = validate_client_config(pending["client_config"])
            if missing:
                validation_failures.append({"tenant_id": pending["tenant_id"], "missing_fields": missing})
                report.escalations.append(
                    f"Tenant '{pending['tenant_id']}' snapshot cannot be validated — missing: {missing}"
                )
            else:
                report.decisions.append(f"Tenant '{pending['tenant_id']}' client configuration passed validation.")
        report.kpis["snapshot_validation_failures"] = validation_failures

        over_cap = []
        for event in context.get("usage_events", []):
            try:
                result = self.usage_tracker.record_usage(**event)
                if result["over_cap"]:
                    over_cap.append(result)
                    report.warnings.append(
                        f"Tenant '{result['tenant_id']}' is over its AI usage cap for '{result['metric']}' "
                        f"({result['usage']}/{result['cap']})."
                    )
            except UsageLimitExceededError as exc:
                report.escalations.append(str(exc))
        report.kpis["usage_over_cap_accounts"] = over_cap

        isolation_violations_blocked = 0
        for check in context.get("isolation_checks", []):
            try:
                self.tenant_registry.get_data(**check)
            except TenantIsolationError:
                isolation_violations_blocked += 1
        report.kpis["tenant_isolation_violations_blocked"] = isolation_violations_blocked

        return report
