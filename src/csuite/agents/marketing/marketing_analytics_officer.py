"""Marketing Analytics Officer — reports to the CMO."""

from __future__ import annotations

import uuid

from csuite.agents.base import BaseAgent
from csuite.marketing.models import OptimizationRecommendation, PerformanceMetric
from csuite.providers.analytics_adapter import AnalyticsAdapter


class MarketingAnalyticsOfficerAgent(BaseAgent):
    name = "marketing_analytics_officer"
    title = "Marketing Analytics Officer"
    mission = "Track real performance data, generate weekly reports, and recommend future content based on evidence only — never inventing unavailable data."
    kpis_owned = ["metrics_collected", "recommendations_generated", "data_quality_breakdown"]
    ghl_authority = []

    def __init__(self, *args, analytics_adapter: AnalyticsAdapter | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.analytics_adapter = analytics_adapter or AnalyticsAdapter()

    def run(self, context: dict):
        """
        context = {
            "campaigns": [{"campaign_id": str, "platform": str, "platform_post_id": str}, ...],
            "top_performer_evidence": [{"campaign_id": str, "hook": str, "cta": str, "conversion_rate": float}, ...],
        }
        """
        report = self.new_report()
        metrics: list[PerformanceMetric] = []
        quality_breakdown: dict[str, int] = {}

        for camp in context.get("campaigns", []):
            platform_action = self.analytics_adapter.collect_platform_metrics(camp["platform"], camp.get("platform_post_id", ""))
            ghl_action = self.analytics_adapter.collect_ghl_conversion_metrics(camp["campaign_id"])

            for metric_name, m in platform_action.result.get("metrics", {}).items():
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()), campaign_id=camp["campaign_id"], platform=camp["platform"],
                    metric_name=metric_name, value=m["value"] or 0, data_quality=m["data_quality"],
                ))
                quality_breakdown[m["data_quality"]] = quality_breakdown.get(m["data_quality"], 0) + 1

            for metric_name, m in ghl_action.result.get("metrics", {}).items():
                metrics.append(PerformanceMetric(
                    metric_id=str(uuid.uuid4()), campaign_id=camp["campaign_id"], platform="ghl",
                    metric_name=metric_name, value=m["value"] or 0, data_quality=m["data_quality"],
                ))
                quality_breakdown[m["data_quality"]] = quality_breakdown.get(m["data_quality"], 0) + 1

        # Recommendations are generated ONLY from evidence explicitly passed in — never invented.
        recommendations = []
        evidence = context.get("top_performer_evidence", [])
        if evidence:
            best = max(evidence, key=lambda e: e.get("conversion_rate", 0))
            rec = OptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                based_on_campaign_ids=[e["campaign_id"] for e in evidence],
                recommendation=f"Favor hooks/CTAs similar to campaign {best['campaign_id']} (hook: '{best.get('hook', 'n/a')}', CTA: '{best.get('cta', 'n/a')}') — highest observed conversion rate ({best.get('conversion_rate', 0):.1%}).",
                evidence=f"Based on {len(evidence)} campaign(s) with reported conversion rates.",
            )
            recommendations.append(rec)
            report.decisions.append(f"Generated 1 optimization recommendation from {len(evidence)} campaign(s) of actual evidence — submitted for approval, not auto-applied.")
        else:
            report.warnings.append("No performance evidence supplied this cycle — no recommendations generated (never inventing unavailable data).")

        report.kpis["metrics_collected"] = len(metrics)
        report.kpis["data_quality_breakdown"] = quality_breakdown
        report.kpis["recommendations_generated"] = len(recommendations)
        report.kpis["metrics"] = metrics
        report.kpis["recommendations"] = recommendations
        return report
