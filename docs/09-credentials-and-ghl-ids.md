# 09 — Required Credentials & GHL IDs

**None of the values below exist in this repository, in an environment
variable, or anywhere in this build.** This document exists so the business
owner knows exactly what to gather before `GHLAdapter._live_call` can be
implemented and any paid integration activated. Nothing here should ever be
committed to source control — use a secrets manager or environment
variables injected at deploy time.

## GHL agency-level

| Item | Needed for |
|---|---|
| Agency API key / Private Integration token | All `GHLAdapter` live calls |
| Agency ID | Location creation, SaaS Configurator |
| SaaS Configurator plan IDs (one per offer-ladder tier) | `create_location(..., plan_id=...)` mapping to real billing |
| Snapshot IDs (one per productized snapshot, once built inside GHL) | `apply_snapshot(...)` — the `snapshot_id` values in `config/snapshots/*.json` are this system's own spec IDs, not yet real GHL snapshot IDs |

## Per-integration credentials

| Integration | Needed for |
|---|---|
| A2P 10DLC brand/campaign registration | SMS sending at scale (carrier compliance, not a code change) |
| Twilio/GHL native phone provisioning | Phone number purchase/porting per location |
| Domain registrar + DNS access | Email sending domain verification per client |
| Payment processor (Stripe or GHL-native) | Client billing, `create_billing_event` going live |
| Voice AI provider credentials | Voice AI agents in the insurance/real-estate/home-services packs |
| iDecide account/API access | The iDecide interactive presentations referenced in each industry pack |

## Environment variables (naming convention, not yet wired to code)

```
GHL_AGENCY_API_KEY=
GHL_AGENCY_ID=
GHL_LIVE_AUTHORIZED=false   # must be explicitly "true" AND paired with dry_run=False in code
PAYMENT_PROCESSOR_API_KEY=
VOICE_AI_PROVIDER_API_KEY=
```

## The authorization gate in code

`GHLAdapter(dry_run=False, live_authorized=True, api_client=GHLApiClient())`
is the only way any part of this system issues a real GHL call. The live
HTTP client now exists (`src/csuite/ghl/api_client.py`) and is wired to
real endpoints for the actions GoHighLevel's public API supports — see
**[`docs/12-live-ghl-connection.md`](12-live-ghl-connection.md)** for
exactly what's connected, what isn't, and the steps to authenticate with
your own credentials (never pasted into a chat — set as an environment
variable on your own machine).
