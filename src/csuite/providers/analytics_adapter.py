"""
AnalyticsAdapter — collects and normalizes platform + GHL conversion data
WITHOUT pretending unlike measurements are identical. Every metric this
adapter returns carries a `data_quality` tag: "available", "estimated",
"delayed", "incomplete", or "unavailable" — the Marketing Analytics
Officer agent must surface that tag, never silently drop it.
"""

from __future__ import annotations

from csuite.providers.base import ProviderAdapterBase, ProviderAction
from csuite.providers.social_platform_adapter import PLATFORM_CAPABILITIES


class AnalyticsAdapter(ProviderAdapterBase):
    provider_name = "analytics"

    def collect_platform_metrics(self, platform: str, platform_post_id: str) -> ProviderAction:
        caps = PLATFORM_CAPABILITIES.get(platform, {})
        if caps.get("native_analytics_via_api") is False:
            return self._dispatch(
                "collect_platform_metrics", {"platform": platform, "platform_post_id": platform_post_id},
                {"data_quality": "unavailable", "metrics": {}},
            )
        watch_time_quality = "available" if caps.get("watch_time_available") is True else "unavailable"
        return self._dispatch(
            "collect_platform_metrics", {"platform": platform, "platform_post_id": platform_post_id},
            {
                "data_quality": "estimated",
                "metrics": {
                    "views": {"value": 0, "data_quality": "estimated"},
                    "engagement": {"value": 0, "data_quality": "estimated"},
                    "comments": {"value": 0, "data_quality": "estimated"},
                    "watch_time": {"value": None, "data_quality": watch_time_quality},
                },
            },
        )

    def collect_ghl_conversion_metrics(self, campaign_id: str) -> ProviderAction:
        return self._dispatch(
            "collect_ghl_conversion_metrics", {"campaign_id": campaign_id},
            {
                "data_quality": "available",
                "metrics": {
                    "leads": {"value": 0, "data_quality": "available"},
                    "appointments": {"value": 0, "data_quality": "available"},
                    "show_rate": {"value": None, "data_quality": "incomplete"},
                    "recruits": {"value": 0, "data_quality": "available"},
                    "applications": {"value": 0, "data_quality": "available"},
                    "issued_business": {"value": 0, "data_quality": "delayed"},
                    "revenue": {"value": None, "data_quality": "unavailable", "note": "Not connected until legally and technically appropriate — see docs/16."},
                },
            },
        )
