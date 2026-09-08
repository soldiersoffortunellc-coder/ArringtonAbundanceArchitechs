import unittest
from dataclasses import dataclass, field

from csuite.ghl.snapshots import SnapshotAssembler, SnapshotApplicationError

VALID_CLIENT_CONFIG = {
    "branding": {"logo_url": "x"}, "domain": "client.example.com", "phone_numbers": ["+15555550100"],
    "email": "hello@client.example.com", "calendars": ["c1"], "users": ["u1"], "services": ["s1"],
    "service_areas": ["TX"], "pricing": {"setup": 1000}, "disclosures": ["d1"],
    "integrations": ["i1"], "escalation_contacts": ["e1"],
}


@dataclass
class _FakeAction:
    result: dict = field(default_factory=dict)


class _AlwaysFailsAdapter:
    """Simulates a live GHL call that reports failure (not a SIMULATED dry-run result)."""

    def apply_snapshot(self, location_id, snapshot_id, version):
        return _FakeAction(result={"status": "ERROR", "applied": False})


class TestFailedSnapshotApplication(unittest.TestCase):
    def test_snapshot_application_failure_raises_and_blocks_launch(self):
        assembler = SnapshotAssembler(industry="insurance_agency", client_config=VALID_CLIENT_CONFIG)
        with self.assertRaises(SnapshotApplicationError):
            assembler.deploy(_AlwaysFailsAdapter(), location_id="loc_x")


if __name__ == "__main__":
    unittest.main()
