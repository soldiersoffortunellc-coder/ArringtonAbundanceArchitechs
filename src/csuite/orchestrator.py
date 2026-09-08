"""
The C-Suite Operating System orchestrator: wires all agents together
(7 C-suite agents + 6 revenue subordinates under the CRO + 6 media/marketing
subordinates under the CMO — 19 agents total) around one shared GHLAdapter,
TenantRegistry, GlobalControls, and the AI Media & Marketing Division's own
provider adapters, and runs one "operating cycle" — the unit of work the
whole system performs on a recurring cadence (e.g. daily).

Class name kept as `RevenueOperatingSystem` (unchanged) even though it now
also drives the Media & Marketing Division — renaming it would be a
cosmetic, non-additive change to every existing caller/test for no
functional benefit (see docs/13-media-marketing-audit-and-plan.md's
non-destructive-change rule).
"""

from __future__ import annotations

from csuite.ghl.adapter import GHLAdapter
from csuite.platform.tenant import TenantRegistry
from csuite.platform.controls import GlobalControls
from csuite.platform.usage_limits import UsageLimitTracker
from csuite.platform.permissions import PermissionRegistry
from csuite.agents.ceo import CEOAgent
from csuite.agents.cro import CROAgent
from csuite.agents.cmo import CMOAgent
from csuite.agents.coo import COOAgent
from csuite.agents.cfo import CFOAgent
from csuite.agents.cto import CTOAgent
from csuite.agents.cco import CCOAgent
from csuite.marketing.store import CampaignStore
from csuite.marketing.approval_queue import ApprovalQueue
from csuite.providers.avatar_video_adapter import AvatarVideoAdapter
from csuite.providers.voice_adapter import VoiceAdapter
from csuite.providers.social_platform_adapter import SocialPlatformAdapter
from csuite.providers.storage_adapter import StorageAdapter
from csuite.providers.analytics_adapter import AnalyticsAdapter
from csuite.providers.idecide_adapter import IDecideAdapter


class RevenueOperatingSystem:
    """
    The full white-label AI Revenue Operating System, as a single object
    graph. Everything defaults to dry-run: the GHLAdapter constructed here
    never touches a real GHL account unless the caller passes an adapter
    they built with dry_run=False, live_authorized=True. The Media &
    Marketing Division's provider adapters (avatar video, voice, social
    platform, storage, analytics, iDecide) follow the identical
    dry-run-by-default convention — see src/csuite/providers/base.py.
    """

    def __init__(self, adapter: GHLAdapter | None = None):
        self.adapter = adapter or GHLAdapter(dry_run=True)
        self.tenant_registry = TenantRegistry()
        self.global_controls = GlobalControls()
        self.usage_tracker = UsageLimitTracker()
        self.permissions = PermissionRegistry()

        # AI Media & Marketing Division infrastructure
        self.campaign_store = CampaignStore()
        self.approval_queue = ApprovalQueue(self.campaign_store, self.permissions)
        self.avatar_video_adapter = AvatarVideoAdapter()
        self.voice_adapter = VoiceAdapter()
        self.social_platform_adapter = SocialPlatformAdapter()
        self.storage_adapter = StorageAdapter()
        self.analytics_adapter = AnalyticsAdapter()
        self.idecide_adapter = IDecideAdapter()

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

        # give media-division subordinates the shared provider adapters/store
        self.cmo.subordinates["ai_video_production_director"].avatar_adapter = self.avatar_video_adapter
        self.cmo.subordinates["social_distribution_director"].store = self.campaign_store
        self.cmo.subordinates["marketing_analytics_officer"].analytics_adapter = self.analytics_adapter

    def agent_roster(self) -> list[dict]:
        agents = [self.ceo, self.cro, self.cmo, self.coo, self.cfo, self.cto, self.cco]
        roster = [{"name": a.name, "title": a.title, "mission": a.mission, "kpis_owned": a.kpis_owned} for a in agents]
        for sub_name, sub in self.cro.subordinates.items():
            roster.append({"name": sub.name, "title": sub.title, "mission": sub.mission, "kpis_owned": sub.kpis_owned, "reports_to": "cro"})
        for sub_name, sub in self.cmo.subordinates.items():
            roster.append({"name": sub.name, "title": sub.title, "mission": sub.mission, "kpis_owned": sub.kpis_owned, "reports_to": "cmo"})
        return roster

    def run_media_division(self, context: dict) -> dict:
        """Passthrough to CMOAgent.run_media_division — see that method for the context shape."""
        report = self.cmo.run_media_division(context)
        return report.to_dict()

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
