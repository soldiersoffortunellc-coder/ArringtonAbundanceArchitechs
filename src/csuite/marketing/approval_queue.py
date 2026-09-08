"""
Executive approval queue — the backend for the human-in-the-loop gate.

"An API request succeeding does not mean a campaign has been approved."
This module is why: every mutating action is RBAC-gated through the
existing PermissionRegistry (config/role_permissions.json), and approving
an item does nothing but append an ApprovalRecord and attempt the campaign
state transition — if the campaign isn't actually sitting in
HUMAN_APPROVAL_REQUIRED, the state-machine transition itself refuses it, so
a permission check succeeding is never confused with a valid approval.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from csuite.marketing.models import ApprovalRecord, Campaign, ComplianceReview, ScriptVersion
from csuite.marketing.store import CampaignStore
from csuite.platform.permissions import PermissionRegistry, PermissionDeniedError


@dataclass
class ApprovalQueueItem:
    """Every field the approval interface is required to display."""
    campaign_id: str
    version_id: str
    script: ScriptVersion
    compliance_review: ComplianceReview
    video_asset_url: str | None
    destination_summary: str
    agent_recommendations: list
    scheduled_publishing_time: float | None
    enqueued_at: float = field(default_factory=time.time)


class ApprovalQueue:
    def __init__(self, store: CampaignStore, permissions: PermissionRegistry | None = None):
        self.store = store
        self.permissions = permissions or PermissionRegistry()
        self._items: dict[str, ApprovalQueueItem] = {}  # campaign_id -> item

    def enqueue(
        self,
        campaign: Campaign,
        script: ScriptVersion,
        compliance_review: ComplianceReview,
        *,
        video_asset_url: str | None = None,
        destination_summary: str = "unassigned",
        agent_recommendations: list | None = None,
        scheduled_publishing_time: float | None = None,
    ) -> ApprovalQueueItem:
        item = ApprovalQueueItem(
            campaign_id=campaign.campaign_id,
            version_id=script.version_id,
            script=script,
            compliance_review=compliance_review,
            video_asset_url=video_asset_url,
            destination_summary=destination_summary,
            agent_recommendations=agent_recommendations or [],
            scheduled_publishing_time=scheduled_publishing_time,
        )
        self._items[campaign.campaign_id] = item
        return item

    def pending_items(self) -> list[ApprovalQueueItem]:
        return [
            item for item in self._items.values()
            if self.store.get_campaign(item.campaign_id).state == "HUMAN_APPROVAL_REQUIRED"
        ]

    def _record_and_transition(self, campaign_id: str, decision: str, new_state: str, role: str, actor_id: str, reason: str) -> ApprovalRecord:
        item = self._items[campaign_id]
        record = ApprovalRecord(
            approval_id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            version_id=item.version_id,
            decision=decision,
            approver_role=role,
            approver_id=actor_id,
            reason=reason,
        )
        self.store.add_approval_record(record)
        sm = self.store.get_state_machine(campaign_id)
        sm.transition(
            new_state, actor=f"{role}:{actor_id}", reason=reason,
            content_version=item.version_id, approval_record_id=record.approval_id,
        )
        return record

    def approve(self, campaign_id: str, *, role: str, actor_id: str, reason: str = "") -> ApprovalRecord:
        self.permissions.require(role, "approve_campaign_content")
        return self._record_and_transition(campaign_id, "APPROVED", "APPROVED", role, actor_id, reason)

    def reject(self, campaign_id: str, *, role: str, actor_id: str, reason: str) -> ApprovalRecord:
        self.permissions.require(role, "reject_campaign_content")
        return self._record_and_transition(campaign_id, "REJECTED", "REJECTED", role, actor_id, reason)

    def request_revision(self, campaign_id: str, *, role: str, actor_id: str, reason: str) -> ApprovalRecord:
        self.permissions.require(role, "request_campaign_revision")
        return self._record_and_transition(campaign_id, "REVISION_REQUESTED", "REVISION_REQUIRED", role, actor_id, reason)

    def pause_campaign(self, campaign_id: str, *, role: str, actor_id: str, reason: str) -> ApprovalRecord:
        self.permissions.require(role, "pause_campaign")
        return self._record_and_transition(campaign_id, "PAUSED", "PAUSED", role, actor_id, reason)
