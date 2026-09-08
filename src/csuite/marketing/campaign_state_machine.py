"""
Campaign workflow state machine.

    IDEA -> BRIEF_CREATED -> SCRIPT_DRAFTED -> BRAND_REVIEW -> COMPLIANCE_REVIEW
    -> REVISION_REQUIRED or HUMAN_APPROVAL_REQUIRED -> APPROVED -> VIDEO_GENERATING
    -> VIDEO_REVIEW -> SCHEDULED -> PUBLISHED -> PERFORMANCE_TRACKING
    -> OPTIMIZATION_COMPLETE

Plus REJECTED, PAUSED, FAILED, CANCELED, ARCHIVED.

Unlike the (strictly linear) client-onboarding state machine
(csuite.onboarding.state_machine), this workflow has real branches —
compliance review can send content back for revision, human approval can
reject, video generation can fail and retry, and any active state can be
paused or canceled. So this is modeled as a directed transition graph
(state -> allowed next states) rather than a fixed ordered list, with the
same pause/resume side-state mechanism as the onboarding machine.

Every transition records the fields the spec requires: campaign_id,
timestamp, acting agent/user, previous_state, new_state, reason,
content_version, and an approval_record_id when applicable — as an
AuditEvent appended to Campaign.audit_trail. This is the campaign's
immutable audit trail.
"""

from __future__ import annotations

import time
import uuid

from csuite.marketing.models import AuditEvent, Campaign

TERMINAL_STATES = {"REJECTED", "CANCELED", "ARCHIVED"}

# Active (non-terminal, non-side) states that CAN be paused.
PAUSABLE_STATES = {
    "IDEA", "BRIEF_CREATED", "SCRIPT_DRAFTED", "BRAND_REVIEW", "COMPLIANCE_REVIEW",
    "REVISION_REQUIRED", "HUMAN_APPROVAL_REQUIRED", "APPROVED", "VIDEO_GENERATING",
    "VIDEO_REVIEW", "SCHEDULED", "PUBLISHED", "PERFORMANCE_TRACKING",
}

TRANSITIONS: dict[str, set[str]] = {
    "IDEA": {"BRIEF_CREATED", "CANCELED"},
    "BRIEF_CREATED": {"SCRIPT_DRAFTED", "CANCELED"},
    "SCRIPT_DRAFTED": {"BRAND_REVIEW", "CANCELED"},
    "BRAND_REVIEW": {"COMPLIANCE_REVIEW", "REVISION_REQUIRED", "CANCELED"},
    "COMPLIANCE_REVIEW": {"REVISION_REQUIRED", "HUMAN_APPROVAL_REQUIRED", "CANCELED"},
    "REVISION_REQUIRED": {"SCRIPT_DRAFTED", "CANCELED"},
    "HUMAN_APPROVAL_REQUIRED": {"APPROVED", "REJECTED", "REVISION_REQUIRED"},
    "APPROVED": {"VIDEO_GENERATING", "CANCELED"},
    "VIDEO_GENERATING": {"VIDEO_REVIEW", "FAILED"},
    "VIDEO_REVIEW": {"SCHEDULED", "REVISION_REQUIRED", "FAILED"},
    "SCHEDULED": {"PUBLISHED", "CANCELED", "FAILED"},
    "PUBLISHED": {"PERFORMANCE_TRACKING"},
    "PERFORMANCE_TRACKING": {"OPTIMIZATION_COMPLETE"},
    "OPTIMIZATION_COMPLETE": {"ARCHIVED"},
    "FAILED": {"VIDEO_GENERATING", "SCHEDULED", "CANCELED"},  # retry paths
}

ALL_STATES = set(TRANSITIONS) | {"REJECTED", "PAUSED", "CANCELED", "ARCHIVED"}

# States requiring mandatory human approval before they may reach APPROVED —
# per spec this is every path out of COMPLIANCE_REVIEW; kept as a named
# constant so callers/tests can assert the rule explicitly.
HUMAN_APPROVAL_GATE_STATES = {"HUMAN_APPROVAL_REQUIRED"}


class InvalidCampaignTransitionError(Exception):
    pass


class CampaignStateMachine:
    def __init__(self, campaign: Campaign):
        self.campaign = campaign
        self._pre_pause_state: str | None = None

    @property
    def state(self) -> str:
        return self.campaign.state

    def transition(
        self,
        new_state: str,
        *,
        actor: str,
        reason: str,
        content_version: str | None = None,
        approval_record_id: str | None = None,
    ) -> AuditEvent:
        if new_state not in ALL_STATES:
            raise InvalidCampaignTransitionError(f"'{new_state}' is not a known campaign state.")

        current = self.campaign.state

        if new_state == "PAUSED":
            if current not in PAUSABLE_STATES:
                raise InvalidCampaignTransitionError(f"Cannot pause a campaign in state '{current}'.")
            self._pre_pause_state = current
        elif current == "PAUSED":
            if new_state != self._pre_pause_state:
                raise InvalidCampaignTransitionError(
                    f"Campaign is PAUSED — must resume() back to '{self._pre_pause_state}' before any other transition."
                )
        elif current in TERMINAL_STATES:
            raise InvalidCampaignTransitionError(f"Campaign is in terminal state '{current}'; no further transitions allowed.")
        else:
            allowed = TRANSITIONS.get(current, set())
            if new_state not in allowed:
                raise InvalidCampaignTransitionError(
                    f"Cannot move campaign from '{current}' to '{new_state}'. Allowed: {sorted(allowed)}"
                )

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            campaign_id=self.campaign.campaign_id,
            timestamp=time.time(),
            actor=actor,
            previous_state=current,
            new_state=new_state,
            reason=reason,
            content_version=content_version,
            approval_record_id=approval_record_id,
        )
        self.campaign.audit_trail.append(event)
        self.campaign.state = new_state
        return event

    def resume(self, *, actor: str, reason: str) -> AuditEvent:
        if self.campaign.state != "PAUSED":
            raise InvalidCampaignTransitionError("Campaign is not PAUSED.")
        if self._pre_pause_state is None:
            raise InvalidCampaignTransitionError("No prior state recorded to resume to.")
        return self.transition(self._pre_pause_state, actor=actor, reason=reason)

    def is_terminal(self) -> bool:
        return self.campaign.state in TERMINAL_STATES

    def requires_human_approval_gate(self) -> bool:
        """True once compliance review has routed this campaign to the mandatory human-approval gate."""
        return self.campaign.state in HUMAN_APPROVAL_GATE_STATES
