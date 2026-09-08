"""
Content pillar / content mix config loader, and GHL-marketing-config
validation (which PLACEHOLDER values are still unfilled). Owned by the CMO
and the Brand Voice & Content Strategist agent.
"""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_ROOT = Path(__file__).resolve().parents[3] / "config" / "marketing"


def _load(name: str) -> dict:
    with open(CONFIG_ROOT / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_content_pillars() -> list[dict]:
    return _load("content_pillars.json")["pillars"]


def load_content_mix() -> dict:
    return _load("content_mix.json")


def cross_brand_mixing_requires_approval() -> bool:
    return _load("content_pillars.json")["cross_brand_mixing_requires_approval"]


def load_brand_profile(brand_id: str) -> dict:
    path = CONFIG_ROOT / "brand_profiles" / f"{brand_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No brand profile found for '{brand_id}' at {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_placeholders(obj, path: str = "") -> list[str]:
    """Recursively finds every string value containing 'PLACEHOLDER' — used to
    validate that a GHL marketing config (or field map, or pipeline mapping)
    has been filled in with real IDs before it's trusted for live use."""
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.extend(find_placeholders(value, f"{path}.{key}" if path else key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found.extend(find_placeholders(value, f"{path}[{i}]"))
    elif isinstance(obj, str) and "PLACEHOLDER" in obj:
        found.append(path)
    return found


def validate_ghl_marketing_config(config: dict) -> list[str]:
    """Returns the dotted-path list of every field still holding a PLACEHOLDER value."""
    return find_placeholders(config)


def content_mix_balance_check(planned_counts: dict) -> dict:
    """
    planned_counts = {"ai_clone": int, "authentic_live": int, "education": int,
                       "recruiting": int, "leadership_motivation": int,
                       "community_impact": int, "direct_promotion": int}
    Returns each configured ratio's target share vs. actual share, so the
    CMO/content calendar can see drift without the percentages ever being
    hard-coded into this function.
    """
    mix = load_content_mix()
    production_total = planned_counts.get("ai_clone", 0) + planned_counts.get("authentic_live", 0)
    topic_total = sum(
        planned_counts.get(k, 0)
        for k in ("education", "recruiting", "leadership_motivation", "community_impact", "direct_promotion")
    )

    def _share(count, total):
        return round(count / total, 4) if total else None

    return {
        "production_mix": {
            "ai_clone_target": mix["production_mix"]["ai_clone_content_pct"],
            "ai_clone_actual": _share(planned_counts.get("ai_clone", 0), production_total),
            "authentic_live_target": mix["production_mix"]["authentic_live_recorded_pct"],
            "authentic_live_actual": _share(planned_counts.get("authentic_live", 0), production_total),
        },
        "topic_mix": {
            "education_target": mix["topic_mix"]["education_pct"],
            "education_actual": _share(planned_counts.get("education", 0), topic_total),
            "recruiting_target": mix["topic_mix"]["recruiting_pct"],
            "recruiting_actual": _share(planned_counts.get("recruiting", 0), topic_total),
            "leadership_and_motivation_target": mix["topic_mix"]["leadership_and_motivation_pct"],
            "leadership_and_motivation_actual": _share(planned_counts.get("leadership_motivation", 0), topic_total),
            "community_impact_target": mix["topic_mix"]["community_impact_pct"],
            "community_impact_actual": _share(planned_counts.get("community_impact", 0), topic_total),
            "direct_promotion_target": mix["topic_mix"]["direct_promotion_pct"],
            "direct_promotion_actual": _share(planned_counts.get("direct_promotion", 0), topic_total),
        },
    }
