# /ghl

Home of the Open Doors Financial OS v1 GoHighLevel integration layer.

**Status: NOT STARTED (infrastructure), IN PROGRESS (connection/discovery tooling)**

This directory holds OS-v1-specific GHL integration artifacts as they're
built (Phases 1–7): connection verification, discovery output, object
creation scripts, and validation.

## Reuse decision

The actual HTTP client (Bearer-token auth, required `Version` header,
`services.leadconnectorhq.com` base URL, HTTPError handling) is **not**
duplicated here. It already exists, is tested, and is correct:
`src/csuite/ghl/api_client.py::GHLApiClient` (built for the existing
Revenue OS/Marketing Division work in this same repo). OS v1's scripts
(`scripts/ghl_connection_test.py`, `scripts/ghl_discovery.py`) import and
reuse it directly, passed OS v1's own credentials
(`GHL_PRIVATE_INTEGRATION_TOKEN`, `GHL_LOCATION_ID`, `GHL_API_VERSION` —
see root `.env.example`) rather than the existing system's
`GHL_ACCESS_TOKEN`. See `ARCHITECTURE.md` for why both env vars coexist.

Object-creation code (pipelines, custom fields, tags, calendars — Phases
4–6) will live here once the discovery/approval gate in this first
execution is cleared by the business owner.
