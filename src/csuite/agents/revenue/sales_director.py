"""Sales Director — reports to the CRO. Owns the sales pipeline."""

from __future__ import annotations

from csuite.agents.base import BaseAgent
from csuite.pipeline.sales_pipeline import SalesPipeline


class SalesDirectorAgent(BaseAgent):
    name = "sales_director"
    title = "Sales Director"
    mission = "Build campaigns, route opportunities, and track conversion by source and rep."
    kpis_owned = ["pipeline_value", "close_rate", "opportunities_by_stage"]
    ghl_authority = ["create_opportunity", "update_opportunity_stage", "publish_campaign"]

    def __init__(self, *args, pipeline: SalesPipeline | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline or SalesPipeline()

    def run(self, context: dict):
        """
        context = {
            "new_opportunities": [{"account_name": ..., "industry": ..., "source": ..., "value": ...}, ...],
            "stage_updates": [{"opportunity_id": ..., "new_stage": ..., "loss_reason": None}, ...],
        }
        """
        self._guard()
        report = self.new_report()

        for opp_input in context.get("new_opportunities", []):
            opp = self.pipeline.create_opportunity(**opp_input)
            report.decisions.append(f"Opened opportunity {opp.opportunity_id} for {opp.account_name} ({opp.industry}).")
            if self.adapter is not None:
                location_id = context.get("location_id", "unprovisioned")
                action = self.adapter.create_opportunity(location_id, "Revenue OS Sales Pipeline", opp.stage, opp.value)
                report.directives_issued.append(action.action_id)

        for update in context.get("stage_updates", []):
            opp = self.pipeline.move_stage(**update)
            report.decisions.append(f"Moved opportunity {opp.opportunity_id} to '{opp.stage}'.")
            if self.adapter is not None:
                action = self.adapter.update_opportunity_stage(opp.opportunity_id, opp.stage, opp.loss_reason)
                report.directives_issued.append(action.action_id)

        by_stage = self.pipeline.by_stage()
        report.kpis["opportunities_by_stage"] = {stage: len(opps) for stage, opps in by_stage.items()}
        report.kpis["pipeline_value"] = self.pipeline.pipeline_value()

        closed_won = len(by_stage.get("Closed Won", []))
        closed_lost = len(by_stage.get("Closed Lost", []))
        total_closed = closed_won + closed_lost
        report.kpis["close_rate"] = round(closed_won / total_closed, 4) if total_closed else None

        return report
