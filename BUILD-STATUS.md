# Build Status

Last audit: 2026-09-08 (read-only GHL connection/reconciliation pass — see
`docs/GHL-CURRENT-STATE.md` for full detail).

## Live GHL connection: NOT CONNECTED

- Environment variables `GHL_LOCATION_ID`, `GHL_PRIVATE_INTEGRATION_TOKEN`,
  and `GHL_API_VERSION` are all **set**, but two problems block a real
  connection today:
  1. The codebase's GHL client (`src/csuite/ghl/api_client.py`) reads
     `GHL_ACCESS_TOKEN`, not `GHL_PRIVATE_INTEGRATION_TOKEN` — as
     provisioned, the token is invisible to the client.
  2. `GHL_LOCATION_ID` and `GHL_PRIVATE_INTEGRATION_TOKEN` both hold
     placeholder values, not real GHL account data.
- A best-effort read-only connection check (aliasing the token env var for
  one subprocess call, token never printed) reached
  `services.leadconnectorhq.com` but was rejected by Cloudflare
  (**error 1010, `browser_signature_banned`**) before GHL's own auth logic
  ran. Plain outbound HTTPS to the host works (`curl` got `HTTP 404` on
  `/`, confirming DNS/TLS/routing).
- No GHL production object was created, modified, or deleted. No token
  was displayed or logged.

## Requested automation not present in repo

`scripts/ghl_connection_test.py`, `scripts/ghl_discovery.py`, and
`config/os-v1.yaml` do not exist in this repository. The nearest
equivalents that do exist: `scripts/check_ghl_connection.py` (single
read-only `GET /locations/{id}` check) and the per-concern JSON files
under `config/`. See `docs/GHL-CURRENT-STATE.md` → "What was asked for
vs. what exists" and → PROPOSED RESOLUTION.

## What's built (dry-run scaffold — unchanged by this audit)

See `docs/00-audit-and-roadmap.md` for the full inventory: 13 C-suite/
revenue agents, GHL adapter (dry-run by default), snapshot architecture
(universal core + insurance + real estate + home services), sales
pipeline, onboarding state machine, tenant/permissions/usage-limit/
billing controls, 90-day financial model, executive dashboard, and the
full required test suite. None of this reaches a live GHL account yet —
`GHLAdapter` only makes real calls when explicitly constructed with
`dry_run=False, live_authorized=True` and a working `GHLApiClient`, and no
code path does that automatically.

## Open items before any live/write action

1. Fix the token env-var name mismatch (rename in the environment, or add
   `GHL_PRIVATE_INTEGRATION_TOKEN` as a recognized alias in
   `GHLApiClient`).
2. Replace placeholder `GHL_LOCATION_ID` / `GHL_PRIVATE_INTEGRATION_TOKEN`
   values with real ones from the actual GHL sub-account.
3. Investigate the Cloudflare 1010 block — most likely fix is setting an
   explicit `User-Agent` header on `GHLApiClient` requests.
4. Re-run the connection check against a **sandbox** location. Only once
   it reports `CONNECTED` should a read-only discovery script be written
   and a real `CURRENT-STATE INVENTORY` be captured.
5. Author `config/os-v1.yaml` (or formally confirm the current
   JSON-per-concern layout under `config/` is the intended target of
   record) so future reconciliation has something concrete to diff
   against.

No provisioning, snapshot application, billing activation, or any other
write action against GHL should happen until items 1–4 above are closed.
