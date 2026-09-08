"""
The Revenue Operating System orchestrator: wires all 13 agents together
(7 C-suite + 6 revenue subordinates under the CRO) around one shared
GHLAdapter, TenantRegistry, and GlobalControls instance, and runs one
"operating cycle" — the unit of work the whole system performs on a
recurring cadence (e.g. daily).
"""

from __future__ import annotations

from csuite.ghl.adapter import GHLAdapter
from csuite.platform.tenant import TenantRegistry
from csuite.platform.controls import GlobalControls
from csuite.platform.usage_limits import UsageLimitTracker
from csuite.agents.ceo import CEOAgent
from csuite.agents.cro import CROAgent
from csuite.agents.cmo import CMOAgent
from csuite.agents.coo import COOAgent
from csuite.agents.cfo import CFOAgent
from csuite.agents.cto import CTOAgent
from csuite.agents.cco import CCOAgent


class RevenueOperatingSystem:
    """
    The full white-label AI Revenue Operating System, as a single object
    graph. Everything defaults to dry-run: the GHLAdapter constructed here
    never touches a real GHL account unless the caller passes an adapter
    they built with dry_run=False, live_authorized=True.
    """

    def __init__(self, adapter: GHLAdapter | None = None):
        self.adapter = adapter or GHLAdapter(dry_run=True)
        self.tenant_registry = TenantRegistry()
        self.global_controls = GlobalControls()
        self.usage_tracker = UsageLimitTracker()

        common = {"adapter": self.adapter, "global_controls": self.global_controls}

        self.cro = CROAgent(**common)
        self.cmo = CMOAgent(**common)
        self.coo = COOAgent(**common)
        self.cfo = CFOAgent(**common)
        self.cto = CTOAgent(tenant_registry=self.tenant_registry, usage_tracker=self.usage_tracker, **common)
        self.cco = CCOAgent(**common)
        self.ceo = CEOAgent(**common)

        # give onboarding-related subordinates the shared tenant registry
        self.cro.subordinates["client_onboarding_director"].tenant_registry = self.tenant_registry

    def agent_roster(self) -> list[dict]:
        agents = [self.ceo, self.cro, self.cmo, self.coo, self.cfo, self.cto, self.cco]
        roster = [{"name": a.name, "title": a.title, "mission": a.mission, "kpis_owned": a.kpis_owned} for a in agents]
        for sub_name, sub in self.cro.subordinates.items():
            roster.append({"name": sub.name, "title": sub.title, "mission": sub.mission, "kpis_owned": sub.kpis_owned, "reports_to": "cro"})
        return roster

    def run_cycle(self, context: dict) -> dict:
        """
        context = {
            "cro": {...per-subordinate context, see agents/cro.py...},
            "cmo": {...},
            "coo": {...},
            "cfo": {...},
            "cto": {...},
            "cco_high_risk_threshold": int,
            "target_90_day_value": float,
        }
        """
        cro_report = self.cro.run(context.get("cro", {}))
        cmo_report = self.cmo.run(context.get("cmo", {}))
        coo_report = self.coo.run(context.get("coo", {}))
        cfo_report = self.cfo.run(context.get("cfo", {}))
        cto_report = self.cto.run(context.get("cto", {}))

        client_success_report = cro_report.kpis.get("subordinate_reports", {}).get("client_success_retention_director", {})
        cco_report = self.cco.run({
            "client_success_report": client_success_report,
            "high_risk_threshold": context.get("cco_high_risk_threshold", 2),
        })

        csuite_reports = {
            "cro": cro_report.to_dict(),
            "cmo": cmo_report.to_dict(),
            "coo": coo_report.to_dict(),
            "cfo": cfo_report.to_dict(),
            "cto": cto_report.to_dict(),
            "cco": cco_report.to_dict(),
        }

        ceo_report = self.ceo.run({
            "csuite_reports": csuite_reports,
            "target_90_day_value": context.get("target_90_day_value"),
        })

        return {
            "ceo": ceo_report.to_dict(),
            **csuite_reports,
            "ghl_action_log": self.adapter.action_log(),
        }
