"""Role-based permission checks, backed by config/role_permissions.json."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "role_permissions.json"


class PermissionDeniedError(Exception):
    pass


class PermissionRegistry:
    def __init__(self, config: dict | None = None):
        if config is None:
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                config = json.load(fh)
        self.roles: dict[str, list[str]] = config["roles"]
        self.action_catalog: list[str] = config["action_catalog"]

    def can(self, role: str, action: str) -> bool:
        if role not in self.roles:
            return False
        allowed = self.roles[role]
        return "*" in allowed or action in allowed

    def require(self, role: str, action: str) -> None:
        if not self.can(role, action):
            raise PermissionDeniedError(f"Role '{role}' is not permitted to perform action '{action}'.")
