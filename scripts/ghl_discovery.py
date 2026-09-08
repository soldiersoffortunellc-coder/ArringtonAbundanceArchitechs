#!/usr/bin/env python3
"""
Open Doors Financial OS v1 — Phase 2: Existing GHL Discovery.

Read-only. Inventories the current Open Doors Financial Group GHL location
BEFORE anything from config/os-v1.yaml is created, so naming conflicts can
be identified up front. Every call here is a GET — nothing is created,
modified, or deleted.

Gated on Phase 1: if the connection test fails, this script writes a
BLOCKED current-state report and makes NO further API calls (no guessing
at endpoints against an unauthenticated/unresolved connection).

Endpoint confidence: several of the endpoints below (pipelines, custom
fields, tags, calendars, users) were used/confirmed working in this
project's earlier live-GHL-connection work (docs/12-live-ghl-connection.md).
Others (forms, surveys, workflows-read, webhooks list, Conversation AI
config) have NOT been confirmed against a real account from this
environment — each is attempted independently and labeled
ACCESSIBLE / NOT_ACCESSIBLE / ERROR based on what actually happens, never
assumed to work.

Contacts/opportunities are sampled minimally (a small `limit`, not a bulk
export) — this is a data-minimization decision: discovery needs to confirm
the account is queryable and see field usage, not exfiltrate client PII.

Usage:
    python3 scripts/ghl_discovery.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from csuite.ghl.api_client import GHLApiClient, GHLApiError  # noqa: E402
from ghl_connection_test import run_connection_test  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
CURRENT_STATE_JSON = os.path.join(REPO_ROOT, "config", "current-state.json")
CURRENT_STATE_DOC = os.path.join(REPO_ROOT, "docs", "GHL-CURRENT-STATE.md")
OS_V1_YAML = os.path.join(REPO_ROOT, "config", "os-v1.yaml")

DISCOVERY_TASKS = [
    {"key": "pipelines", "label": "Pipelines & stages", "method": "GET", "path": "/opportunities/pipelines", "query_uses_location": True},
    {"key": "custom_fields", "label": "Custom fields", "method": "GET", "path": "/locations/{location_id}/customFields", "query_uses_location": False},
    {"key": "custom_values", "label": "Custom values", "method": "GET", "path": "/locations/{location_id}/customValues", "query_uses_location": False},
    {"key": "tags", "label": "Tags", "method": "GET", "path": "/locations/{location_id}/tags", "query_uses_location": False},
    {"key": "calendars", "label": "Calendars", "method": "GET", "path": "/calendars/", "query_uses_location": True},
    {"key": "users", "label": "Users", "method": "GET", "path": "/users/", "query_uses_location": True},
    {"key": "contacts_sample", "label": "Contacts (schema sample, limit=1 — not a bulk export)", "method": "GET", "path": "/contacts/", "query_uses_location": True, "extra_query": {"limit": 1}},
    {"key": "forms", "label": "Forms", "method": "GET", "path": "/forms/", "query_uses_location": True},
    {"key": "surveys", "label": "Surveys", "method": "GET", "path": "/surveys/", "query_uses_location": True},
    {"key": "workflows", "label": "Workflows (read-only list, if exposed)", "method": "GET", "path": "/workflows/", "query_uses_location": True},
]


def _load_proposed_names() -> dict:
    """Best-effort load of config/os-v1.yaml's proposed pipeline/calendar names for
    conflict-checking. Falls back to an empty structure if PyYAML isn't installed —
    conflict-checking then can't run, and the report says so explicitly."""
    try:
        import yaml
    except ImportError:
        return {}
    with open(OS_V1_YAML, "r", encoding="utf-8") as fh:
        model = yaml.safe_load(fh)
    return {
        "pipelines": [p["name"] for p in model.get("pipelines", {}).values()],
        "calendars": [c["name"] for c in model.get("calendars", {}).values()],
    }


def run_discovery() -> dict:
    connection = run_connection_test()

    report = {
        "phase": "PHASE_2_DISCOVERY",
        "generated_at": time.time(),
        "connection": {"status": connection["connection_status"]},
        "tasks": {},
        "conflicts": [],
        "blocked_reason": None,
    }

    if connection["connection_status"] != "PASS":
        report["blocked_reason"] = (
            "Discovery requires a passing Phase 1 connection test. "
            f"Connection status: {connection['connection_status']}. "
            f"{connection.get('error', '')}"
        )
        for task in DISCOVERY_TASKS:
            report["tasks"][task["key"]] = {"status": "BLOCKED", "label": task["label"]}
        return report

    location_id = os.environ["GHL_LOCATION_ID"]
    client = GHLApiClient(
        access_token=os.environ["GHL_PRIVATE_INTEGRATION_TOKEN"],
        version=os.environ["GHL_API_VERSION"],
    )

    discovered_pipeline_names = []
    discovered_calendar_names = []

    for task in DISCOVERY_TASKS:
        path = task["path"].format(location_id=location_id)
        query = {"locationId": location_id} if task["query_uses_location"] else None
        if query is not None and "extra_query" in task:
            query.update(task["extra_query"])

        entry = {"label": task["label"], "endpoint": f"{task['method']} {path}"}
        try:
            result = client.get(path, query=query)
            entry["status"] = "ACCESSIBLE"
            entry["summary"] = _summarize(task["key"], result)
            if task["key"] == "pipelines":
                discovered_pipeline_names = [p.get("name") for p in result.get("pipelines", []) if p.get("name")]
            if task["key"] == "calendars":
                discovered_calendar_names = [c.get("name") for c in result.get("calendars", []) if c.get("name")]
        except GHLApiError as exc:
            entry["status"] = "NOT_ACCESSIBLE" if exc.status_code in (403, 404, 501) else "ERROR"
            entry["http_status"] = exc.status_code
            entry["detail"] = (exc.response_body or "")[:300]
        except Exception as exc:
            entry["status"] = "ERROR"
            entry["detail"] = f"{type(exc).__name__}: {exc}"

        report["tasks"][task["key"]] = entry

    proposed = _load_proposed_names()
    if not proposed:
        report["conflicts"] = ["Conflict-check skipped — PyYAML not installed, could not load config/os-v1.yaml. Run: pip install pyyaml"]
    else:
        for name in discovered_pipeline_names:
            if name in proposed.get("pipelines", []):
                report["conflicts"].append(f"Pipeline name already exists in GHL: '{name}' — do not create a duplicate; compare configuration before reuse.")
        for name in discovered_calendar_names:
            if name in proposed.get("calendars", []):
                report["conflicts"].append(f"Calendar name already exists in GHL: '{name}' — do not create a duplicate; compare configuration before reuse.")
        if not report["conflicts"]:
            report["conflicts"] = ["None found among accessible categories at this pass."]

    return report


def _summarize(key: str, result: dict) -> dict:
    """Small, non-exhaustive summary — full detail lives in current-state.json, not printed to console."""
    if key == "pipelines":
        pipelines = result.get("pipelines", [])
        return {"count": len(pipelines), "names": [p.get("name") for p in pipelines]}
    if key in ("custom_fields", "custom_values", "tags"):
        items = result.get(key, result.get("customFields", result.get("customValues", result.get("tags", []))))
        return {"count": len(items) if isinstance(items, list) else "unknown"}
    if key == "calendars":
        calendars = result.get("calendars", [])
        return {"count": len(calendars), "names": [c.get("name") for c in calendars]}
    if key == "users":
        users = result.get("users", [])
        return {"count": len(users) if isinstance(users, list) else "unknown"}
    if key == "contacts_sample":
        return {"sample_size_requested": 1, "note": "Schema sample only — not a bulk export."}
    return {"note": "raw result available in current-state.json"}


def write_outputs(report: dict) -> None:
    with open(CURRENT_STATE_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    lines = [
        "# GHL Current State — Open Doors Financial Group",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(report['generated_at']))}",
        "",
        f"**Connection status: {report['connection']['status']}**",
        "",
    ]
    if report["blocked_reason"]:
        lines += ["## Blocked", "", report["blocked_reason"], ""]
    lines += ["## Discovery tasks", "", "| Category | Status | Detail |", "|---|---|---|"]
    for key, entry in report["tasks"].items():
        detail = entry.get("summary") or entry.get("detail") or ""
        lines.append(f"| {entry['label']} | {entry['status']} | {json.dumps(detail) if isinstance(detail, dict) else detail} |")
    lines += ["", "## Naming conflicts against config/os-v1.yaml", ""]
    for c in report["conflicts"]:
        lines.append(f"- {c}")
    lines += ["", "Full machine-readable detail: `config/current-state.json`.", ""]

    with open(CURRENT_STATE_DOC, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    report = run_discovery()
    write_outputs(report)
    print(f"Wrote {CURRENT_STATE_JSON}")
    print(f"Wrote {CURRENT_STATE_DOC}")
    print(json.dumps({"connection_status": report["connection"]["status"], "blocked_reason": report["blocked_reason"]}, indent=2))


if __name__ == "__main__":
    main()
