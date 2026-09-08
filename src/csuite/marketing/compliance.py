"""
ComplianceEngine — the logic behind the Marketing Compliance Officer agent.

Deterministic keyword/phrase scanning against config/marketing/
prohibited_claims.json and config/marketing/disclosure_requirements.json.
This is NOT a substitute for legal, tax, or regulatory review — it is a
first-pass filter that (a) blocks a fixed list of clearly unsupportable
phrases outright and (b) forces mandatory human approval for anything that
touches a regulated category, exactly as required. See
docs/13-media-marketing-audit-and-plan.md for why this is keyword-based
(no LLM is wired into this repo).
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from csuite.marketing.models import ComplianceReview, ScriptVersion

CONFIG_ROOT = Path(__file__).resolve().parents[3] / "config" / "marketing"

RISK_PROHIBITED = "PROHIBITED"
RISK_HIGH = "HIGH"
RISK_MEDIUM = "MEDIUM"
RISK_LOW = "LOW"

# Content that must ALWAYS get human approval regardless of compliance score,
# per the spec's explicit "Human Approval Rules" list.
ALWAYS_REQUIRE_HUMAN_APPROVAL_FLAGS = {
    "carrier_specific", "product_specific", "illustrated_or_projected_values",
    "interest_dividend_index_or_return_claims", "tax_statements", "investment_comparisons",
    "client_testimonials", "client_case_studies", "income_claims", "recruiting_income_claims",
    "guarantees", "health_related_claims", "legal_interpretations", "political_content",
    "crisis_communications",
}


def _load(name: str) -> dict:
    with open(CONFIG_ROOT / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


class ComplianceEngine:
    def __init__(self, prohibited_config: dict | None = None, disclosure_config: dict | None = None):
        self.prohibited_config = prohibited_config or _load("prohibited_claims.json")
        self.disclosure_config = disclosure_config or _load("disclosure_requirements.json")

    def _scan_text(self, text: str) -> tuple[list[str], list[str]]:
        lowered = text.lower()
        blocked_found = [p for p in self.prohibited_config["blocked_phrases"] if p in lowered]
        categories_found = [
            cat for cat, keywords in self.prohibited_config["claim_categories"].items()
            if any(kw in lowered for kw in keywords)
        ]
        return blocked_found, categories_found

    def required_disclosures(self, *, platforms: list[str], product: str | None, campaign_type: str | None) -> list[str]:
        disclosures = list(self.disclosure_config["by_platform"].get("all", []))
        for platform in platforms:
            disclosures.extend(self.disclosure_config["by_platform"].get(platform, []))
        if product:
            disclosures.extend(self.disclosure_config["by_product"].get(product, []))
        if campaign_type:
            disclosures.extend(self.disclosure_config["by_campaign_type"].get(campaign_type, []))
        # de-duplicate, preserve order
        seen = set()
        deduped = []
        for d in disclosures:
            if d not in seen:
                seen.add(d)
                deduped.append(d)
        return deduped

    def review(
        self,
        script: ScriptVersion,
        *,
        platforms: list[str],
        product: str | None = None,
        campaign_type: str | None = None,
        manual_flags: set[str] | None = None,
        is_ai_clone: bool = True,
        within_first_30_days: bool = False,
    ) -> ComplianceReview:
        """
        manual_flags: any of ALWAYS_REQUIRE_HUMAN_APPROVAL_FLAGS the caller
        knows to be true from context the text scan can't see (e.g. "this
        script includes an illustrated policy value table").
        """
        manual_flags = manual_flags or set()
        combined_text = " ".join([script.hook, script.body, script.cta_text, *script.platform_captions.values()])

        blocked_found, categories_found = self._scan_text(combined_text)

        if blocked_found:
            risk_level = RISK_PROHIBITED
        elif categories_found or manual_flags:
            risk_level = RISK_HIGH
        elif script.unresolved_fields:
            # NEEDS_INPUT content is not yet safe to auto-clear even if no keyword hit
            risk_level = RISK_MEDIUM
        else:
            risk_level = RISK_LOW

        requires_human_approval = (
            risk_level in (RISK_HIGH, RISK_PROHIBITED)
            or bool(manual_flags & ALWAYS_REQUIRE_HUMAN_APPROVAL_FLAGS)
            or any(c in self.prohibited_config["requires_human_approval_categories"] for c in categories_found)
            or (is_ai_clone and within_first_30_days)
        )

        review = ComplianceReview(
            review_id=str(uuid.uuid4()),
            campaign_id=script.campaign_id,
            version_id=script.version_id,
            risk_level=risk_level,
            detected_categories=categories_found,
            blocked_phrases_found=blocked_found,
            required_disclosures=self.required_disclosures(platforms=platforms, product=product, campaign_type=campaign_type),
            requires_human_approval=requires_human_approval,
        )
        return review
