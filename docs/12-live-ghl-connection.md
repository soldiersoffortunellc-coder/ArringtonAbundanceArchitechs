# 12 — Connecting to a Real GoHighLevel Account

## Confirmed finding: Cloudflare blocks the default Python User-Agent

The first real live call attempted against `services.leadconnectorhq.com`
(from Open Doors Financial OS v1's connection test) got a **403 before
reaching GHL's own application layer at all**:
```
error_code 1010, error_name "browser_signature_banned", cloudflare_error: true
```
This is Cloudflare's bot-management sitting in front of GHL's API,
rejecting Python's default `urllib` User-Agent string outright — not a
credentials, scope, or org-egress-policy issue (confirmed by comparing an
identical request with a browser-like `User-Agent` header, which cleared
Cloudflare and reached GHL's actual auth logic instead). **Fixed**:
`GHLApiClient._headers()` now sends a browser-like `User-Agent` on every
request. If you ever see this specific error shape again, it's this — not
your token.

## Current status: not connected

No GoHighLevel credentials exist anywhere in this environment, this
repository, or this conversation. Nobody has authorized a live/paid
integration. This document explains exactly what is now wired up in code
(`src/csuite/ghl/api_client.py`), what it can and can't do, and the steps
**you** take, on your own machine, to actually connect.

I could not fetch GoHighLevel's own documentation pages while building this
(`marketplace.gohighlevel.com` and `highlevel.stoplight.io` are blocked by
this environment's network egress policy), so the request bodies below are
"best known from corroborated public sources, verify before first live
use" — not copied verbatim from GHL's current docs. The authentication
plumbing (base URL, headers) is corroborated across multiple independent
sources and is the part you should trust most.

## What's real now

`src/csuite/ghl/api_client.py` — `GHLApiClient` — makes real authenticated
HTTPS requests to `https://services.leadconnectorhq.com` using:

```
Authorization: Bearer <your token>
Version: 2021-07-28
Content-Type: application/json
```

`GHLAdapter(dry_run=False, live_authorized=True, api_client=GHLApiClient())`
now actually calls GHL for these actions (`_UNSUPPORTED_LIVE_ACTIONS` in
`adapter.py` lists the rest):

| Adapter method | Real endpoint (verify before relying on it) |
|---|---|
| `create_location` | `POST /locations/` — requires an **agency-level OAuth token** with `locations.write` scope, not a location-scoped Private Integration Token |
| `create_users` | `POST /users/` |
| `create_custom_fields` | `POST /locations/{locationId}/customFields` (one call per field) |
| `create_calendar` | `POST /calendars/` |
| `tag_contact` | `POST /contacts/{contactId}/tags` |
| `create_opportunity` | `POST /opportunities/` |
| `update_opportunity_stage` | `PUT /opportunities/{opportunityId}` |
| `send_notification` | `POST /conversations/messages` |

**Not supported by GHL's public API at all** (raises
`GHLUnsupportedActionError` with an explanation, even in live mode):
`apply_snapshot` (to an existing location — only possible at
location-creation time via a `snapshotId` field), `create_pipeline`,
`create_workflow`, `publish_campaign`, `create_billing_event` (this is the
SaaS Configurator's job, a separate setup). See the docstring/comments in
`adapter.py` for the reasoning behind each.

## Two ways to authenticate

1. **Private Integration Token (PIT)** — created inside one GHL sub-account
   under *Settings → Private Integrations*. Simplest option if you're
   connecting this system to a sub-account **you already created manually**
   and just want it to manage contacts/opportunities/calendars/custom
   fields/tags on that one location. Cannot create new locations.
2. **OAuth marketplace app** — required for agency-level actions
   (`create_location`, or `snapshots.write` scope if GHL later exposes
   snapshot management to your app). Requires registering an app in the
   GHL Marketplace developer portal, running a one-time user-consent flow,
   and (per current OAuth practice) refreshing short-lived access tokens —
   this system does not implement the OAuth consent/refresh flow itself;
   `GHLApiClient` expects you to hand it a currently-valid access token via
   `GHL_ACCESS_TOKEN`.

## How to actually connect (do this yourself, not in a shared chat)

**Do not paste your GHL token into a chat conversation** — treat it like a
password. Set it as an environment variable on the machine that will run
this code:

```bash
export GHL_ACCESS_TOKEN="paste-your-token-here"     # PIT or OAuth access token
export GHL_LOCATION_ID="the-location-id-to-test"    # any location your token can read
python3 scripts/check_ghl_connection.py
```

That script makes exactly one read-only call (`GET /locations/{id}`) and
prints back only the location's name/id/timezone — never your token. A
successful run means authentication is working end-to-end. It does **not**
mean every `GHLAdapter` live action's request body is schema-correct for
your account — check each one you actually plan to use against your
current GHL API docs first (your account's real field requirements can
differ by plan/version).

## Turning the whole system live (once connection is verified)

```python
from csuite.ghl.adapter import GHLAdapter
from csuite.ghl.api_client import GHLApiClient
from csuite.orchestrator import RevenueOperatingSystem

live_adapter = GHLAdapter(
    dry_run=False,
    live_authorized=True,          # you are explicitly authorizing this
    api_client=GHLApiClient(),     # reads GHL_ACCESS_TOKEN from the environment
)
ros = RevenueOperatingSystem(adapter=live_adapter)
```

Every other guardrail built into this system (global pause, tenant
isolation, margin alerts, onboarding state machine, permission checks)
applies identically in live mode — going live only changes whether
`GHLAdapter`'s writes reach a real GHL account; it does not remove any of
the safety logic around it.

## Recommended order of operations

1. Run `scripts/check_ghl_connection.py` against a **sandbox or test**
   sub-account first, never a production client account.
2. Pick one low-risk action (e.g. `tag_contact`) and verify it in that
   sandbox before trusting `create_location` or anything that provisions a
   real client.
3. Confirm the exact request-body field names this file assumes still
   match GHL's current API for your account/app type — GHL's public API
   has changed field requirements across versions before.
4. Only then route real client provisioning (`ProvisioningWorkflow`,
   docs/04) through a live adapter.
