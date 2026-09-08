"""
Domain models for the AI Media & Marketing Division.

No database or ORM exists anywhere in this repository (see
docs/13-media-marketing-audit-and-plan.md). Following the existing
convention (plain dataclasses + in-memory registries, e.g.
csuite.platform.tenant.TenantRegistry), every model here is a lightweight
dataclass. `CampaignStore` (store.py) is the in-memory repository; swapping
it for a real database later means changing that one file, not every
caller.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---- brand / voice / audience ---------------------------------------------

@dataclass
class BrandProfile:
    brand_id: str
    display_name: str
    verified_facts: dict = field(default_factory=dict)
    user_provided_unverified: dict = field(default_factory=dict)
    approved_ctas: list = field(default_factory=list)
    requires_compliance_review: bool = True
    raw: dict = field(default_factory=dict)  # full loaded JSON, for anything not modeled explicitly


@dataclass
class VoiceProfile:
    brand_id: str
    tone_descriptors: list = field(default_factory=list)
    recurring_themes: list = field(default_factory=list)
    explicit_non_goals: list = field(default_factory=list)


@dataclass
class AudienceProfile:
    audience_id: str
    business: str
    description: str
    pain_points: list = field(default_factory=list)
    desired_outcomes: list = field(default_factory=list)


@dataclass
class ContentPillar:
    pillar_id: str
    name: str
    business: str


# ---- campaign chain ---------------------------------------------------------

@dataclass
class CampaignBrief:
    brief_id: str
    campaign_id: str
    business: str
    brand_id: str
    pillar_id: str
    audience_id: str | None
    platform_targets: list  # e.g. ["instagram", "tiktok"]
    objective: str
    cta_key: str
    key_messages: list = field(default_factory=list)  # facts the requester explicitly supplied
    is_ai_clone: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class ScriptVersion:
    version_id: str
    campaign_id: str
    version_number: int
    hook: str
    body: str
    cta_text: str
    platform_captions: dict = field(default_factory=dict)  # platform -> caption text
    hashtags: dict = field(default_factory=dict)            # platform -> [hashtags]
    unresolved_fields: list = field(default_factory=list)   # NEEDS_INPUT markers
    created_at: float = field(default_factory=time.time)


@dataclass
class ComplianceReview:
    review_id: str
    campaign_id: str
    version_id: str
    risk_level: str  # LOW | MEDIUM | HIGH | PROHIBITED
    detected_categories: list = field(default_factory=list)
    blocked_phrases_found: list = field(default_factory=list)
    required_disclosures: list = field(default_factory=list)
    requires_human_approval: bool = False
    reviewed_at: float = field(default_factory=time.time)
    reviewer: str = "marketing_compliance_officer_agent"


@dataclass
class ApprovalRecord:
    approval_id: str
    campaign_id: str
    version_id: str
    decision: str  # APPROVED | REJECTED | REVISION_REQUESTED | PAUSED
    approver_role: str
    approver_id: str
    reason: str = ""
    decided_at: float = field(default_factory=time.time)


@dataclass
class VideoGenerationJob:
    job_id: str
    campaign_id: str
    version_id: str
    provider: str
    provider_job_id: str | None = None
    status: str = "PENDING"  # PENDING | SUBMITTED | PROCESSING | COMPLETED | FAILED | RETRYING
    attempts: int = 0
    max_attempts: int = 3
    cost_estimate: float | None = None
    cost_actual: float | None = None
    final_asset_url: str | None = None
    consent_authorization_id: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None


@dataclass
class MediaAsset:
    asset_id: str
    campaign_id: str
    kind: str  # video | thumbnail | caption_file | disclosure_overlay
    storage_ref: str
    created_at: float = field(default_factory=time.time)


@dataclass
class CTA:
    cta_key: str
    label: str
    conversion_destination: str  # e.g. "calendar:strategy_call" or "pipeline:licensed_agent_recruiting"


@dataclass
class GHLDestination:
    destination_id: str
    kind: str  # pipeline | calendar | form | funnel | workflow
    key: str
    ghl_id: str | None = None  # PLACEHOLDER until real config is supplied


@dataclass
class SocialPost:
    post_id: str
    campaign_id: str
    platform: str
    caption: str
    hashtags: list = field(default_factory=list)
    scheduled_time: float | None = None
    status: str = "DRAFT"  # DRAFT | SCHEDULED | PUBLISHED | FAILED | PAUSED | CANCELED
    platform_post_id: str | None = None
    post_url: str | None = None
    error_message: str | None = None
    content_hash: str | None = None


@dataclass
class PublishingJob:
    job_id: str
    post_id: str
    attempts: int = 0
    max_attempts: int = 3
    last_error: str | None = None


@dataclass
class LeadAttribution:
    attribution_id: str
    campaign_id: str
    contact_id: str
    cta_key: str
    destination: str
    created_at: float = field(default_factory=time.time)


@dataclass
class PerformanceMetric:
    metric_id: str
    campaign_id: str
    platform: str
    metric_name: str
    value: float
    data_quality: str = "available"  # available | estimated | delayed | incomplete | unavailable
    recorded_at: float = field(default_factory=time.time)


@dataclass
class OptimizationRecommendation:
    recommendation_id: str
    based_on_campaign_ids: list
    recommendation: str
    evidence: str
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL | APPROVED | REJECTED


@dataclass
class ProviderCredentialReference:
    provider: str
    env_var_name: str  # never the credential itself — just where to find it


@dataclass
class ConsentAuthorization:
    consent_id: str
    person_name: str
    scope: str  # e.g. "ai_clone_video_and_voice"
    authorized_by: str
    authorized_at: float = field(default_factory=time.time)
    revoked: bool = False


@dataclass
class AuditEvent:
    event_id: str
    campaign_id: str
    timestamp: float
    actor: str  # agent name or user id
    previous_state: str | None
    new_state: str
    reason: str
    content_version: str | None = None
    approval_record_id: str | None = None


@dataclass
class Campaign:
    campaign_id: str
    business: str
    brand_id: str
    pillar_id: str
    state: str = "IDEA"
    is_ai_clone: bool = True
    created_at: float = field(default_factory=time.time)
    brief_id: str | None = None
    current_version_id: str | None = None
    audit_trail: list = field(default_factory=list)  # list[AuditEvent]


def new_campaign(business: str, brand_id: str, pillar_id: str, is_ai_clone: bool = True) -> Campaign:
    return Campaign(campaign_id=_new_id("camp"), business=business, brand_id=brand_id, pillar_id=pillar_id, is_ai_clone=is_ai_clone)


# ---- iDecide models ---------------------------------------------------------

@dataclass
class IDecidePresentation:
    presentation_id: str
    presentation_type_id: str
    name: str
    business: str


@dataclass
class IDecidePresentationVersion:
    version_id: str
    presentation_id: str
    version_number: int
    compliance_approved: bool = False


@dataclass
class IDecidePersonalizedLink:
    link_id: str
    presentation_id: str
    version_id: str
    contact_id: str
    campaign_id: str | None
    assigned_agent: str | None
    url: str
    created_at: float = field(default_factory=time.time)


@dataclass
class IDecideViewerSession:
    session_id: str
    link_id: str
    contact_id: str
    started_at: float | None = None
    completed_at: float | None = None
    completion_count: int = 0


@dataclass
class IDecideViewerChoice:
    choice_id: str
    session_id: str
    viewer_path_key: str
    selected_at: float = field(default_factory=time.time)


@dataclass
class IDecideOutcome:
    outcome_id: str
    session_id: str
    final_cta: str | None
    final_outcome: str | None


@dataclass
class IDecideCompletionEvent:
    event_id: str  # provider event id — used for idempotency
    session_id: str
    raw_payload: dict
    processed: bool = False
    received_at: float = field(default_factory=time.time)


@dataclass
class IDecideCTASelection:
    selection_id: str
    session_id: str
    cta_key: str


@dataclass
class IDecideAgentAssignment:
    contact_id: str
    agent_id: str
    assigned_at: float = field(default_factory=time.time)


@dataclass
class IDecideCampaignMapping:
    campaign_id: str
    presentation_type_id: str


@dataclass
class IDecideGHLFieldMapping:
    field_key: str
    ghl_field_id: str  # PLACEHOLDER until real config supplied


@dataclass
class IDecideWorkflowMapping:
    workflow_key: str
    ghl_workflow_id: str  # PLACEHOLDER until real config supplied


@dataclass
class IDecideSubaccountConfiguration:
    location_id: str
    idecide_account_ref: str
    field_map_ref: str
    workflow_map_ref: str
