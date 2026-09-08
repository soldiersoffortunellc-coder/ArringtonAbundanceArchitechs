"""
SocialPlatformAdapter — used ONLY when GHL Social Planner cannot provide a
required publishing or analytics feature for a given platform. Not every
platform supports the same features via API; this module states, per
platform, what's assumed supported/unsupported so the Social Distribution
Director never assumes uniform capability. These flags are this system's
own configuration, not fetched from any platform — verify against each
platform's current developer terms before relying on them live.
"""

from __future__ import annotations

import uuid

from csuite.providers.base import ProviderAdapterBase, ProviderAction

PLATFORM_CAPABILITIES = {
    "facebook": {"publish_via_api": True, "native_analytics_via_api": True, "watch_time_available": True},
    "instagram": {"publish_via_api": True, "native_analytics_via_api": True, "watch_time_available": False},
    "tiktok": {"publish_via_api": "verify_current_tos", "native_analytics_via_api": "verify_current_tos", "watch_time_available": "verify_current_tos"},
    "youtube_shorts": {"publish_via_api": True, "native_analytics_via_api": True, "watch_time_available": True},
    "linkedin": {"publish_via_api": True, "native_analytics_via_api": "limited", "watch_time_available": False},
}


class UnsupportedPlatformFeatureError(Exception):
    pass


class SocialPlatformAdapter(ProviderAdapterBase):
    provider_name = "social_platform"

    def capabilities(self, platform: str) -> dict:
        if platform not in PLATFORM_CAPABILITIES:
            return {"publish_via_api": "unknown", "native_analytics_via_api": "unknown", "watch_time_available": "unknown"}
        return PLATFORM_CAPABILITIES[platform]

    def publish_post(self, *, platform: str, caption: str, media_ref: str) -> ProviderAction:
        caps = self.capabilities(platform)
        if caps.get("publish_via_api") is False:
            raise UnsupportedPlatformFeatureError(f"Publishing via API is not supported for '{platform}'. Use GHL Social Planner's UI path or the platform's own composer.")
        return self._dispatch(
            "publish_post", {"platform": platform, "caption": caption, "media_ref": media_ref},
            {"platform_post_id": f"post_{uuid.uuid4().hex[:12]}", "post_url": f"mock://{platform}/post/{uuid.uuid4().hex[:8]}"},
        )

    def fetch_analytics(self, platform: str, platform_post_id: str) -> ProviderAction:
        caps = self.capabilities(platform)
        if caps.get("native_analytics_via_api") is False:
            return self._dispatch(
                "fetch_analytics", {"platform": platform, "platform_post_id": platform_post_id},
                {"data_quality": "unavailable", "note": f"'{platform}' does not expose native analytics via API in this adapter's current config."},
            )
        return self._dispatch(
            "fetch_analytics", {"platform": platform, "platform_post_id": platform_post_id},
            {"data_quality": "estimated", "views": 0, "engagement": 0},
        )
