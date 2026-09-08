"""Productization Director — reports to the CRO."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.ghl.snapshots import load_universal_core, load_industry_pack, INDUSTRY_SNAPSHOT_IDS, SnapshotError


class ProductizationDirectorAgent(BaseAgent):
    name = "productization_director"
    title = "Productization Director"
    mission = "Convert proven systems into standardized products; prevent unnecessary custom work."
    kpis_owned = ["snapshot_versions_current", "industries_productized", "avg_implementation_hours"]
    ghl_authority = []  # defines snapshots; actual apply is done by CTO/onboarding

    def run(self, context: dict):
        """
        context = {
            "implementation_hours_by_industry": {"insurance_agency": 12.5, ...}  # optional
        }
        """
        report = self.new_report()

        productized = []
        for industry in INDUSTRY_SNAPSHOT_IDS:
            try:
                pack = load_industry_pack(industry)
                productized.append({"industry": industry, "snapshot_id": pack["snapshot_id"], "version": pack["version"]})
            except SnapshotError as exc:
                report.warnings.append(str(exc))

        core = load_universal_core()
        report.decisions.append(
            f"Universal core snapshot '{core['snapshot_id']}' v{core['version']} is the single shared foundation "
            f"for all {len(productized)} productized industry packs."
        )
        report.kpis["universal_core_version"] = core["version"]
        report.kpis["industries_productized"] = productized

        hours = context.get("implementation_hours_by_industry", {})
        if hours:
            report.kpis["avg_implementation_hours"] = round(sum(hours.values()) / len(hours), 2)

        return report
