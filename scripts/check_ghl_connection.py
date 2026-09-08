#!/usr/bin/env python3
"""
Verifies that this machine can authenticate to a real GoHighLevel account.

Run this YOURSELF, on a machine you trust, with your own credentials set as
environment variables. This script never hardcodes, logs, or transmits your
token anywhere except directly to GoHighLevel's own API over HTTPS.

Setup:
    export GHL_ACCESS_TOKEN="<your Private Integration Token or OAuth access token>"
    export GHL_LOCATION_ID="<a location id your token can access>"   # for the location check
    python3 scripts/check_ghl_connection.py

What it does:
    1. Confirms GHL_ACCESS_TOKEN is set (fails fast, clearly, if not).
    2. Makes ONE lightweight authenticated GET request — fetching the
       location referenced by GHL_LOCATION_ID — to confirm the token,
       Version header, and base URL are all correct.
    3. Prints only non-secret response fields (location name/id/timezone).

This script makes exactly one real API call and does not create, modify, or
delete anything in your GHL account.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from csuite.ghl.api_client import GHLApiClient, GHLApiError, GHLCredentialsMissingError  # noqa: E402


def main() -> int:
    location_id = os.environ.get("GHL_LOCATION_ID")
    if not location_id:
        print(
            "GHL_LOCATION_ID is not set. Set it to a location id your token can access, e.g.:\n"
            "    export GHL_LOCATION_ID=abc123\n"
            "(This script only reads that location — it changes nothing.)",
            file=sys.stderr,
        )
        return 2

    client = GHLApiClient()

    try:
        result = client.get(f"/locations/{location_id}")
    except GHLCredentialsMissingError as exc:
        print(f"NOT CONNECTED: {exc}", file=sys.stderr)
        return 2
    except GHLApiError as exc:
        print(
            f"NOT CONNECTED: GHL API returned HTTP {exc.status_code} for GET {exc.url}\n"
            f"Response body: {exc.response_body}\n"
            "Check: is GHL_ACCESS_TOKEN valid and not expired? Does it have access to this "
            "location? Is GHL_LOCATION_ID correct?",
            file=sys.stderr,
        )
        return 1

    location = result.get("location", result)
    print("CONNECTED to GoHighLevel.")
    print(f"  Location name : {location.get('name', '(unknown)')}")
    print(f"  Location id   : {location.get('id', location_id)}")
    print(f"  Timezone      : {location.get('timezone', '(unknown)')}")
    print(
        "\nThis confirms authentication works. It does NOT confirm every "
        "GHLAdapter live action's request schema — verify each endpoint you "
        "actually use against your current GHL API docs before relying on it "
        "in production (see docs/12-live-ghl-connection.md)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
