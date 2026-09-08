"""
GHLApiClient — the real, live HTTP client for the GoHighLevel (LeadConnector) API v2.

This is the ONLY place in the codebase that ever makes a network call to
GoHighLevel. It is never constructed automatically — `GHLAdapter` only uses
it when built with `dry_run=False, live_authorized=True` AND an explicit
`api_client` instance is supplied. Nothing here reads credentials from
anywhere but environment variables, and nothing here logs or stores the
token itself.

Verified plumbing (corroborated against multiple current sources as of this
writing — GHL's own docs sites were unreachable from this build environment
via the network egress proxy, so treat exact request BODY field names below
as "best known, verify before first live use", not gospel):

    Base URL     : https://services.leadconnectorhq.com
    Auth header  : Authorization: Bearer <token>
    Version hdr  : Version: 2021-07-28   (REQUIRED on every request)
    Content type : application/json

Two token types both use the same "Authorization: Bearer <token>" header:
  - A location-scoped Private Integration Token (PIT), created inside a
    sub-account under Settings > Private Integrations. Good for acting on
    ONE location you already own. Cannot create new locations.
  - An OAuth marketplace-app access token, obtained via a user consent flow
    against an agency. Required for agency-level actions such as creating
    new sub-accounts (locations.write scope) or managing snapshots
    (snapshots.write scope, agency-level apps only).

Nothing in this module decides which one you need for a given call — that
depends on your GHL app/account setup. See docs/12-live-ghl-connection.md.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://services.leadconnectorhq.com"
DEFAULT_API_VERSION = "2021-07-28"


class GHLCredentialsMissingError(RuntimeError):
    """Raised when a live call is attempted with no access token configured."""


class GHLApiError(RuntimeError):
    """Raised on any non-2xx response from the GHL API. Carries the raw response for debugging."""

    def __init__(self, status_code: int, method: str, url: str, response_body: str):
        self.status_code = status_code
        self.method = method
        self.url = url
        self.response_body = response_body
        super().__init__(
            f"GHL API call failed: {method} {url} -> HTTP {status_code}\nResponse body: {response_body}"
        )


class GHLUnsupportedActionError(RuntimeError):
    """
    Raised for GHLAdapter action kinds that GoHighLevel's public API does not
    (as of this writing) expose a documented way to perform. These require
    either the GHL UI, the SaaS Configurator, or being baked into a snapshot
    at design time instead of being called at runtime.
    """


@dataclass
class GHLApiClient:
    access_token: str | None = None
    base_url: str = DEFAULT_BASE_URL
    version: str = DEFAULT_API_VERSION
    timeout_seconds: float = 20.0

    def __post_init__(self):
        # Never accept a hardcoded token in source — env var is the only
        # implicit source, and it's read once at construction time, not
        # logged, and not echoed back in any error message.
        if self.access_token is None:
            self.access_token = os.environ.get("GHL_ACCESS_TOKEN")
        if not self.base_url:
            self.base_url = os.environ.get("GHL_API_BASE_URL", DEFAULT_BASE_URL)
        if not self.version:
            self.version = os.environ.get("GHL_API_VERSION", DEFAULT_API_VERSION)

    def _headers(self) -> dict:
        if not self.access_token:
            raise GHLCredentialsMissingError(
                "No GHL access token configured. Set the GHL_ACCESS_TOKEN environment variable "
                "to a Private Integration Token or OAuth access token before making a live call. "
                "See docs/12-live-ghl-connection.md."
            )
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Version": self.version,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def request(self, method: str, path: str, json_body: dict | None = None, query: dict | None = None) -> dict:
        url = self.base_url.rstrip("/") + path
        if query:
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(query)}"

        data = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        req = urllib.request.Request(url=url, data=data, method=method.upper(), headers=self._headers())

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GHLApiError(exc.code, method.upper(), url, body) from exc
        except urllib.error.URLError as exc:
            raise GHLApiError(0, method.upper(), url, str(exc.reason)) from exc

    # ---- thin verbs -------------------------------------------------------

    def get(self, path: str, query: dict | None = None) -> dict:
        return self.request("GET", path, query=query)

    def post(self, path: str, json_body: dict) -> dict:
        return self.request("POST", path, json_body=json_body)

    def put(self, path: str, json_body: dict) -> dict:
        return self.request("PUT", path, json_body=json_body)

    def delete(self, path: str) -> dict:
        return self.request("DELETE", path)
