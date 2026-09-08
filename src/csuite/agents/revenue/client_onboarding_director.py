"""Client Onboarding Director — reports to the CRO. Owns provisioning + the onboarding state machine."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.ghl.provisioning import ProvisioningWorkflow
from csuite.platform.tenant import TenantRegistry


class ClientOnboardingDirectorAgent(BaseAgent):
    name = "client_onboarding_director"
    title = "Client Onboarding Director"
    mission = "Configure the client's system, run QA, train the client, and obtain launch approval."
    kpis_owned = ["time_to_launch", "onboarding_blocked_count", "onboarding_live_count"]
    ghl_authority = ["create_location", "apply_snapshot", "create_users"]

    def __init__(self, *args, tenant_registry: TenantRegistry | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant_registry = tenant_registry or TenantRegistry()

    def run(self, context: dict):
        """
        context = {
            "new_clients": [
                {"tenant_id", "client_name", "industry", "plan_id", "client_config", "users"},
                ...
            ]
        }
        """
        self._guard()
        report = self.new_report()
        workflow = ProvisioningWorkflow(adapter=self.adapter, tenant_registry=self.tenant_registry)

        live_count = 0
        blocked_count = 0
        for client in context.get("new_clients", []):
            result = workflow.run(**client)
            report.directives_issued.extend(a["action_id"] for a in result.ghl_actions)
            if result.blocked_reason:
                blocked_count += 1
                report.escalations.append(
                    f"Tenant '{result.tenant_id}' is BLOCKED during onboarding: {result.blocked_reason}"
                )
            else:
                live_count += 1
                report.decisions.append(
                    f"Tenant '{result.tenant_id}' provisioned end-to-end and is now "
                    f"'{result.state_machine.current_state}' at location '{result.location_id}'."
                )

        report.kpis["onboarding_live_count"] = live_count
        report.kpis["onboarding_blocked_count"] = blocked_count
        return report
