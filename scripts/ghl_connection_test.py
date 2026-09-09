#!/usr/bin/env python3
"""
Open Doors Financial OS v1 — Phase 1: GHL Connection Test.

Read-only. Makes exactly one API call (GET /locations/{id}) to verify:
  - the Private Integration Token authenticates
  - GHL_LOCATION_ID resolves to a real location
  - the configured API version is accepted

Never prints a secret value — only whether each required env var is SET or
UNSET. Mutates nothing. Reuses the existing, tested HTTP client
(csuite.ghl.api_client.GHLApiClient) rather than a new implementation —
see ARCHITECTURE.md for why.

Usage:
    python3 scripts/ghl_connection_test.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from csuite.ghl.api_client import GHLApiClient, GHLApiError, GHLCredentialsMissingError  # noqa: E402

REQUIRED_VARS = ["GHL_LOCATION_ID", "GHL_PRIVATE_INTEGRATION_TOKEN", "GHL_API_VERSION"]


def check_env_vars() -> dict:
    """Returns SET/UNSET per required var. Never returns or prints a value."""
    return {var: ("SET" if os.environ.get(var) else "UNSET") for var in REQUIRED_VARS}


def run_connection_test() -> dict:
    env_status = check_env_vars()
    missing = [v for v, status in env_status.items() if status == "UNSET"]

    report = {
        "phase": "PHASE_1_CONNECTION_TEST",
        "env_vars": env_status,  # SET/UNSET only — never a value
        "connection_status": "NOT_ATTEMPTED",
        "location_resolved": False,
        "api_version_accepted": None,
        "http_status": None,
        "error": None,
        "missing_env_vars": missing,
    }

    if missing:
        report["connection_status"] = "FAIL"
        report["error"] = f"Missing required environment variable(s): {', '.join(missing)}"
        return report

    location_id = os.environ["GHL_LOCATION_ID"]
    client = GHLApiClient(
        access_token=os.environ["GHL_PRIVATE_INTEGRATION_TOKEN"],
        version=os.environ["GHL_API_VERSION"],
    )

    try:
        result = client.get(f"/locations/{location_id}")
    except GHLCredentialsMissingError as exc:
        report["connection_status"] = "FAIL"
        report["error"] = str(exc)
        return report
    except GHLApiError as exc:
        report["connection_status"] = "FAIL"
        report["http_status"] = exc.status_code
        # Truncate the response body defensively — GHL error bodies don't echo
        # the token, but keep this bounded regardless.
        body = exc.response_body or ""
        report["error"] = body[:500]
        if "cloudflare_error" in body or "browser_signature_banned" in body:
            report["error"] += (
                " — this is Cloudflare's bot-protection rejecting the HTTP client "
                "(edge layer, before GHL's own API/auth logic ran), NOT an invalid token "
                "or scope issue. If this recurs, verify GHLApiClient is sending a "
                "browser-like User-Agent header (see docs/12-live-ghl-connection.md)."
            )
        elif exc.status_code == 401:
            report["error"] += " — the token was rejected by GHL itself (invalid/expired Private Integration Token)."
        elif exc.status_code == 403:
            report["error"] += (
                " — the token authenticated but lacks a required scope for this call. "
                "Check the exact scopes granted to this token in GHL Settings > Private "
                "Integrations rather than requesting broader access."
            )
        return report
    except Exception as exc:  # network errors etc.
        report["connection_status"] = "FAIL"
        report["error"] = f"{type(exc).__name__}: {exc}"
        return report

    location = result.get("location", result)
    report["connection_status"] = "PASS"
    report["location_resolved"] = bool(location.get("id") or location.get("name"))
    report["api_version_accepted"] = True
    report["http_status"] = 200
    report["location_name"] = location.get("name")  # not a secret; useful for a human sanity check
    return report


def main() -> None:
    report = run_connection_test()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["connection_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
