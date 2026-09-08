"""Brand Voice & Content Strategist — reports to the CMO."""

from __future__ import annotations

import uuid

from csuite.agents.base import BaseAgent
from csuite.marketing.content_strategy import load_brand_profile
from csuite.marketing.models import ScriptVersion

PLATFORM_HASHTAG_STYLE = {
    "facebook": {"max_hashtags": 3}, "instagram": {"max_hashtags": 8}, "tiktok": {"max_hashtags": 5},
    "youtube_shorts": {"max_hashtags": 3}, "linkedin": {"max_hashtags": 3},
}


class BrandVoiceContentStrategistAgent(BaseAgent):
    name = "brand_voice_content_strategist"
    title = "Brand Voice & Content Strategist"
    mission = "Structure Coach Rashon's authentic voice into hooks, scripts, captions, and platform-adapted variants — never fabricating facts, credentials, results, or testimonials."
    kpis_owned = ["scripts_drafted", "unresolved_fields_count", "platforms_covered"]
    ghl_authority = []

    def run(self, context: dict):
        """
        context = {
            "campaign_id": str, "brand_id": str, "platforms": [str],
            "key_messages": [str],   # facts the requester actually supplied — never invented
            "cta_text": str, "hook_override": str | None, "version_number": int,
        }
        Never fabricates: any hook/body content not traceable to key_messages or the
        brand's voice_profile.recurring_themes is marked NEEDS_INPUT rather than invented.
        """
        report = self.new_report()
        brand = load_brand_profile(context["brand_id"])
        key_messages = context.get("key_messages", [])
        unresolved = []

        if key_messages:
            body = " ".join(key_messages)
        else:
            body = "NEEDS_INPUT: no key messages were supplied for this brief."
            unresolved.append("body")

        hook = context.get("hook_override") or (key_messages[0] if key_messages else None)
        if not hook:
            hook = "NEEDS_INPUT: no hook was supplied or derivable from key messages."
            unresolved.append("hook")

        cta_text = context.get("cta_text")
        approved_ctas = brand.get("approved_ctas", [])
        if cta_text and approved_ctas and cta_text not in approved_ctas:
            report.warnings.append(f"CTA '{cta_text}' is not in this brand's approved_ctas list {approved_ctas} — flagging for brand review.")
        elif not cta_text:
            cta_text = "NEEDS_INPUT: no CTA supplied."
            unresolved.append("cta_text")

        platforms = context.get("platforms", [])
        platform_captions = {}
        hashtags = {}
        for platform in platforms:
            style = PLATFORM_HASHTAG_STYLE.get(platform, {"max_hashtags": 3})
            platform_captions[platform] = f"{hook}\n\n{body}\n\n{cta_text}"
            hashtags[platform] = []  # never invented — populated only from an approved hashtag list if supplied
            if "approved_hashtags" in context:
                hashtags[platform] = context["approved_hashtags"][: style["max_hashtags"]]

        script = ScriptVersion(
            version_id=str(uuid.uuid4()),
            campaign_id=context["campaign_id"],
            version_number=context.get("version_number", 1),
            hook=hook, body=body, cta_text=cta_text,
            platform_captions=platform_captions, hashtags=hashtags,
            unresolved_fields=unresolved,
        )

        report.decisions.append(
            f"Drafted script v{script.version_number} for campaign {context['campaign_id']} "
            f"across {len(platforms)} platform(s); {len(unresolved)} field(s) need human input."
        )
        report.kpis["scripts_drafted"] = 1
        report.kpis["unresolved_fields_count"] = len(unresolved)
        report.kpis["platforms_covered"] = platforms
        report.kpis["script_version"] = script
        return report
