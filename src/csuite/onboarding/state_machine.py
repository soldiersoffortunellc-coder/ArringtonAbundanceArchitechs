"""
Client Onboarding State Machine.

Enforces the exact forward-only primary path plus side-states defined in
config/onboarding_states.json. Owned operationally by the Client Onboarding
Director agent.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "onboarding_states.json"


class InvalidTransitionError(Exception):
    pass


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


class OnboardingStateMachine:
    def __init__(self, tenant_id: str, config: dict | None = None):
        self.tenant_id = tenant_id
        self.config = config or _load_config()
        self.primary_path: list[str] = self.config["primary_path"]
        self.side_states: list[str] = self.config["side_states"]
        self.side_state_entry_allowed_from: dict = self.config["side_state_entry_allowed_from"]

        self.current_state: str | None = None
        self._pre_side_state: str | None = None
        self.history: list[dict] = []

    def _record(self, state: str) -> None:
        self.history.append({"state": state, "timestamp": time.time()})

    def transition(self, target_state: str) -> None:
        all_states = set(self.primary_path) | set(self.side_states)
        if target_state not in all_states:
            raise InvalidTransitionError(f"'{target_state}' is not a known onboarding state.")

        if target_state in self.side_states:
            self._enter_side_state(target_state)
            return

        # target is a primary-path state
        if self.current_state is None:
            if target_state != self.primary_path[0]:
                raise InvalidTransitionError(
                    f"Onboarding must start at '{self.primary_path[0]}', not '{target_state}'."
                )
            self.current_state = target_state
            self._record(target_state)
            return

        if self.current_state in self.side_states:
            raise InvalidTransitionError(
                f"Cannot move directly from side-state '{self.current_state}' to '{target_state}'. "
                "Call resume() first."
            )

        current_index = self.primary_path.index(self.current_state)
        target_index = self.primary_path.index(target_state)
        if target_index != current_index + 1:
            raise InvalidTransitionError(
                f"Cannot move from '{self.current_state}' to '{target_state}': the primary path is "
                f"forward-only, one step at a time (no skipping stages)."
            )

        self.current_state = target_state
        self._record(target_state)

    def _enter_side_state(self, side_state: str) -> None:
        allowed_from = self.side_state_entry_allowed_from.get(side_state, [])
        if self.current_state not in allowed_from:
            raise InvalidTransitionError(
                f"Cannot enter side-state '{side_state}' from '{self.current_state}'. "
                f"Allowed from: {allowed_from}"
            )
        self._pre_side_state = self.current_state
        self.current_state = side_state
        self._record(side_state)

    def resume(self) -> None:
        """Return from a resumable side-state (BLOCKED/PAUSED/REFUND_REVIEW) to where the client was."""
        if self.current_state not in ("BLOCKED", "PAUSED", "REFUND_REVIEW"):
            raise InvalidTransitionError(f"'{self.current_state}' is not a resumable side-state.")
        if self._pre_side_state is None:
            raise InvalidTransitionError("No prior state recorded to resume to.")
        self.current_state = self._pre_side_state
        self._record(self.current_state)

    def is_terminal(self) -> bool:
        return self.current_state in ("CANCELED", "OFFBOARDED")

    def is_live(self) -> bool:
        return self.current_state in ("LIVE", "OPTIMIZATION")
