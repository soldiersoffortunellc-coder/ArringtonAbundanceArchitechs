#!/usr/bin/env python3
"""
Builds config/ghl-object-registry.json (the flat, machine-readable ID
ledger) from config/os-v1.yaml (the human-authored canonical proposal).

This is the ONLY OS-v1 script with a dependency beyond the Python standard
library (PyYAML) — the rest of this repository is deliberately
dependency-free. Install with: pip install pyyaml

Usage:
    python3 scripts/build_object_registry.py
"""

from __future__ import annotations

import json
import os
import sys

try:
    import yaml
except ImportError:
    print(
        "PyYAML is required for this script only (the rest of this repo has no "
        "dependencies). Install it with:\n\n    pip install pyyaml\n",
        file=sys.stderr,
    )
    sys.exit(2)

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
YAML_PATH = os.path.join(REPO_ROOT, "config", "os-v1.yaml")
REGISTRY_PATH = os.path.join(REPO_ROOT, "config", "ghl-object-registry.json")

CATEGORY_KEYS = ["pipelines", "calendars", "contact_fields", "opportunity_fields"]


def build_registry(model: dict) -> dict:
    registry = {
        "_note": (
            "Machine-readable, script-updated ledger of GHL objects for Open Doors "
            "Financial OS v1. Generated from config/os-v1.yaml by "
            "scripts/build_object_registry.py. Every 'id' stays empty until the object "
            "is actually created in GHL and this file is re-synced — ids are never "
            "fabricated. Reference objects by logical_name (the JSON key), never by a "
            "hard-coded id, from n8n workflows or agent tooling."
        ),
        "version": model.get("version"),
        "location_logical_name": model.get("location_logical_name"),
        "objects": {},
    }

    for category in CATEGORY_KEYS:
        for logical_name, obj in model.get(category, {}).items():
            entry = {
                "category": category,
                "type": obj.get("type"),
                "ghl_name": obj.get("name"),
                "purpose": obj.get("purpose"),
                "id": obj.get("id", ""),
                "deployment_status": obj.get("deployment_status", "NOT_CREATED"),
                "dependencies": obj.get("dependencies", []),
            }
            if "stages" in obj:
                entry["stages"] = [{"name": s, "id": ""} for s in obj["stages"]]
            registry["objects"][logical_name] = entry

    tag_taxonomy = model.get("tag_taxonomy", {})
    registry["tag_taxonomy"] = {
        "prefixes": tag_taxonomy.get("prefixes", {}),
        "deployment_status": tag_taxonomy.get("deployment_status", "NOT_CREATED"),
        "tags": {},  # populated in Phase 5 after discovery confirms no duplicates
    }

    return registry


def main() -> None:
    with open(YAML_PATH, "r", encoding="utf-8") as fh:
        model = yaml.safe_load(fh)

    registry = build_registry(model)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2)
        fh.write("\n")

    object_count = len(registry["objects"])
    stage_count = sum(len(o.get("stages", [])) for o in registry["objects"].values())
    print(f"Wrote {REGISTRY_PATH}")
    print(f"  {object_count} objects ({stage_count} pipeline stages) — all NOT_CREATED.")


if __name__ == "__main__":
    main()
