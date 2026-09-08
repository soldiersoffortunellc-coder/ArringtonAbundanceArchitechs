# GHL Current-State Reconciliation — 2026-09-08

Read-only audit. No GHL production object was created, modified, or
deleted while producing this document. The token was never printed,
logged, or included in any output below.

## What was asked for vs. what exists

The requested procedure named two scripts and one config file that do not
exist under those names in this repository:

| Requested | Actual |
|---|---|
| `scripts/ghl_connection_test.py` | Does not exist. Closest equivalent: `scripts/check_ghl_connection.py` (single read-only `GET /locations/{id}` call). |
| `scripts/ghl_discovery.py` | Does not exist anywhere in the repo. No discovery/inventory script of any kind has been built yet. |
| `config/os-v1.yaml` | Does not exist. This repo's config lives as separate JSON files under `config/` (`sales_pipeline.json`, `onboarding_states.json`, `offer_ladder.json`, `role_permissions.json`, `ai_usage_limits.json`, `financial_scenarios.json`, `config/snapshots/*.json`) — there is no single `os-v1.yaml` to reconcile against. |

Because the named connection-test script doesn't exist, `scripts/check_ghl_connection.py` was run instead, as a best-effort, strictly read-only substitute (it makes exactly one `GET` call and changes nothing). Per the run order in the request ("if and only if the connection test passes, run discovery"), discovery was correctly skipped — the connection test did not pass, and no discovery script exists to run in any case.

## Connection attempt — what actually happened

```
$ GHL_ACCESS_TOKEN=$GHL_PRIVATE_INTEGRATION_TOKEN python3 scripts/check_ghl_connection.py
NOT CONNECTED: GHL API returned HTTP 403 for GET https://services.leadconnectorhq.com/locations/<GHL_LOCATION_ID value>
Response body: Cloudflare Error 1010 — "browser_signature_banned" / "Access denied.
The site owner has blocked access based on your browser's signature."
```

Two independent, stacked problems surfaced, not one:

1. **The env var the code reads doesn't match the env var that's set.**
   `src/csuite/ghl/api_client.py` reads `GHL_ACCESS_TOKEN` exclusively —
   `GHL_PRIVATE_INTEGRATION_TOKEN` is referenced nowhere in the codebase.
   The alias above (`GHL_ACCESS_TOKEN=$GHL_PRIVATE_INTEGRATION_TOKEN`,
   set only for the one subprocess call, never echoed) was used to get a
   real read on the rest of the chain; it is not a code fix.
2. **`GHL_LOCATION_ID` and `GHL_PRIVATE_INTEGRATION_TOKEN` both hold
   placeholder values**, not real GHL account data — pattern-checked
   without printing either value (`GHL_LOCATION_ID` matches a
   `YOUR_..._ID`-style placeholder; `GHL_PRIVATE_INTEGRATION_TOKEN`
   matches a placeholder pattern too). `GHL_API_VERSION` is the one
   variable holding a real, usable value (`2021-07-28`, which matches
   `DEFAULT_API_VERSION` in `api_client.py`).

Given (2), a request to `/locations/<placeholder>` was never going to
succeed regardless of the token's validity — so the run cannot by itself
prove or disprove whether the token itself is good.

On top of both of those, the request was rejected by Cloudflare's bot
filter (**error 1010, `browser_signature_banned`**) before GHL's own
auth/authz logic would have run. This is a client-signature block against
Python's default `urllib` user agent, not a credentials failure. A plain
`curl` to the same host's root path succeeded (`HTTP 404`, the expected
response for an unauthenticated request to `/`), confirming DNS, TLS, and
routing to `services.leadconnectorhq.com` all work — the network path
itself is fine. The failure is specific to the plain default UA an
unauthenticated-looking API request presents, layered on top of the
placeholder location ID.

## CURRENT-STATE INVENTORY

No live GHL object inventory could be produced — the one read call that
was attempted never got past Cloudflare's edge, so nothing about the real
GHL account (locations, snapshots, pipelines, custom fields, users) is
known beyond what was already documented as "not connected" in
`docs/12-live-ghl-connection.md` and `docs/09-credentials-and-ghl-ids.md`.

Repo-side (code/config) inventory, which is what's actually reconcilable
right now:

- `src/csuite/ghl/api_client.py` — real HTTP client, reads `GHL_ACCESS_TOKEN` / `GHL_API_BASE_URL` / `GHL_API_VERSION`.
- `src/csuite/ghl/adapter.py` — dry-run-by-default adapter; live calls require explicit `dry_run=False, live_authorized=True`.
- `config/snapshots/*.json` — this system's own snapshot spec format (universal core + insurance + real estate + home services). **Not** real GHL snapshot IDs yet — see `docs/09-credentials-and-ghl-ids.md`.
- `config/sales_pipeline.json`, `config/onboarding_states.json`, `config/offer_ladder.json`, `config/role_permissions.json`, `config/ai_usage_limits.json`, `config/financial_scenarios.json` — this system's internal config, not yet mapped to any live GHL location.
- No `config/os-v1.yaml` exists to reconcile against live state.

## CONFLICTS FOUND

1. **Credential env-var name mismatch.** The environment provisions
   `GHL_PRIVATE_INTEGRATION_TOKEN`; the code's only real GHL client reads
   `GHL_ACCESS_TOKEN`. As provisioned, the token is invisible to
   `GHLApiClient` and every live call would fail with
   `GHLCredentialsMissingError` even with a fully valid token value.
2. **Placeholder credential values.** `GHL_LOCATION_ID` and
   `GHL_PRIVATE_INTEGRATION_TOKEN` are both set to placeholder-shaped
   strings, not real GoHighLevel account values, so even after fixing
   conflict #1 there is nothing real to authenticate with or query yet.

## BLOCKERS

1. **The requested scripts and config file don't exist.**
   `scripts/ghl_connection_test.py`, `scripts/ghl_discovery.py`, and
   `config/os-v1.yaml` are not present anywhere in this repository. Only
   `scripts/check_ghl_connection.py` (a single-endpoint connection check)
   exists; there is no discovery/inventory script, and no `os-v1.yaml`
   config file, to build or run against.

## PROPOSED RESOLUTION

- Do not build a discovery script that writes anything — keep it strictly
  `GET`-only, matching `scripts/check_ghl_connection.py`'s pattern, once
  there's a real connection to discover against.
- Rename/re-point env var usage so provisioning and code agree — either
  (a) set `GHL_ACCESS_TOKEN` in the environment going forward, or (b) add
  `GHL_PRIVATE_INTEGRATION_TOKEN` as a recognized alias inside
  `GHLApiClient.__post_init__` (falling back to `GHL_ACCESS_TOKEN` if
  unset) — a small, backward-compatible code change, not a live call.
- Replace the placeholder `GHL_LOCATION_ID` and
  `GHL_PRIVATE_INTEGRATION_TOKEN` values with real ones from the actual
  GHL sub-account (Settings → Private Integrations for the token; the
  location's own ID for the location) before attempting connection again.
- Once real credentials are in place, re-run the (renamed/aliased)
  connection check with an explicit, non-default `User-Agent` header set
  on the request (`GHLApiClient` currently sends none, so `urllib`'s
  default is used) — that's the most likely fix for the Cloudflare 1010
  block, independent of the credential fixes above.
- Only after a connection check returns `CONNECTED` should a **read-only**
  discovery script be written and run to build the real
  `CURRENT-STATE INVENTORY` this document currently can't populate.
- Author `config/os-v1.yaml` (or confirm the JSON-file-per-concern layout
  under `config/` is the intended permanent format) so future
  reconciliation runs have an actual target to diff against.

## NEXT DEPLOYMENT ACTION

Fix the two conflicts above (env var name, placeholder values) with the
business owner, off of this session — the token must never be pasted into
a chat. Once `check_ghl_connection.py` (or its renamed equivalent) reports
`CONNECTED` against a real sandbox/test sub-account, come back and: (1)
add a `User-Agent` header to `GHLApiClient` if Cloudflare still blocks the
request, (2) write the read-only discovery script, (3) run it, and (4)
regenerate this document's `CURRENT-STATE INVENTORY` section from real
data. No provisioning, snapshot application, or write action of any kind
should happen before that loop closes.
