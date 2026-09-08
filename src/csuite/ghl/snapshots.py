"""
Snapshot architecture: universal core + industry pack + client configuration layer.

Keeps the three layers strictly separated (per operating rules — no single
oversized snapshot) and provides an assembler used both by the CTO Agent
(technical config) and the Client Onboarding Director (provisioning).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_ROOT = Path(__file__).resolve().parents[3] / "config"
SNAPSHOTS_DIR = CONFIG_ROOT / "snapshots"

REQUIRED_CLIENT_CONFIG_FIELDS = [
    "branding",
    "domain",
    "phone_numbers",
    "email",
    "calendars",
    "users",
    "services",
    "service_areas",
    "pricing",
    "disclosures",
    "integrations",
    "escalation_contacts",
]

INDUSTRY_SNAPSHOT_IDS = {
    "insurance_agency": "insurance_pack",
    "real_estate": "real_estate_pack",
    "home_services": "home_services_pack",
}


class SnapshotError(Exception):
    pass


class MissingClientConfigurationError(SnapshotError):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"Missing required client configuration fields: {missing_fields}")


class SnapshotApplicationError(SnapshotError):
    pass


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_universal_core() -> dict:
    return _load_json(SNAPSHOTS_DIR / "universal_core.json")


def load_industry_pack(industry: str) -> dict:
    if industry not in INDUSTRY_SNAPSHOT_IDS:
        raise SnapshotError(
            f"No industry pack defined for '{industry}'. Known packs: {list(INDUSTRY_SNAPSHOT_IDS)}"
        )
    filename = f"{INDUSTRY_SNAPSHOT_IDS[industry]}.json"
    return _load_json(SNAPSHOTS_DIR / filename)


def validate_client_config(client_config: dict) -> list[str]:
    """Returns the list of required fields missing from client_config (empty list = valid)."""
    return [f for f in REQUIRED_CLIENT_CONFIG_FIELDS if not client_config.get(f)]


class SnapshotAssembler:
    """Merges universal core + industry pack + client configuration into one deployable spec."""

    def __init__(self, industry: str, client_config: dict):
        self.industry = industry
        self.client_config = client_config

    def assemble(self) -> dict:
        missing = validate_client_config(self.client_config)
        if missing:
            raise MissingClientConfigurationError(missing)

        universal = load_universal_core()
        industry_pack = load_industry_pack(self.industry)

        return {
            "universal_core": universal,
            "industry_pack": industry_pack,
            "client_configuration": self.client_config,
            "assembled_snapshot_id": f"{universal['snapshot_id']}+{industry_pack['snapshot_id']}",
        }

    def deploy(self, adapter, location_id: str) -> dict:
        """
        Applies the assembled snapshot to a GHL location via the adapter.
        Raises SnapshotApplicationError if the adapter reports a failure, so
        callers (e.g. the onboarding state machine) can route to BLOCKED.
        """
        assembled = self.assemble()

        core_action = adapter.apply_snapshot(location_id, assembled["universal_core"]["snapshot_id"], assembled["universal_core"]["version"])
        if core_action.result.get("status") not in ("SIMULATED",) and not core_action.result.get("applied"):
            raise SnapshotApplicationError(f"Universal core snapshot failed to apply to {location_id}")

        pack_action = adapter.apply_snapshot(location_id, assembled["industry_pack"]["snapshot_id"], assembled["industry_pack"]["version"])
        if pack_action.result.get("status") not in ("SIMULATED",) and not pack_action.result.get("applied"):
            raise SnapshotApplicationError(f"Industry pack snapshot failed to apply to {location_id}")

        return assembled
