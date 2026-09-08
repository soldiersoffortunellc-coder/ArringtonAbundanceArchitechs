# 03 — Universal Snapshot & Three Industry-Pack Specifications

Owned by: **Productization Director** (defines) + **CTO** (technical
config) + **Client Onboarding Director** (deploys).
Config: `config/snapshots/*.json`. Implementation:
`src/csuite/ghl/snapshots.py`.

## Three-layer architecture (kept strictly separated — no oversized snapshot)

```
Universal Core  →  Industry Pack  →  Client Configuration Layer
(one, shared)      (one per vertical)  (one per client, never shared)
```

### 1. Universal Core (`config/snapshots/universal_core.json`)

Every client, regardless of industry, gets: contact structure (lead source,
lifecycle stage, risk flag fields + tags), an opportunity framework tied to
the sales pipeline, a general calendar framework, missed-call recovery,
basic nurture, appointment reminders, no-show follow-up, review requests,
reporting/attribution fields, and a support-escalation workflow.

**Requires manual/API configuration outside any snapshot** (cannot be
packaged into a GHL snapshot export):
- A2P 10DLC phone registration (carrier-side, manual)
- Domain + DNS verification for email sending
- Voice AI phone number porting/purchase
- Payment processor connection for client billing
- SaaS Configurator plan mapping per GHL agency account

### 2. Industry Packs (extend the universal core)

| Pack | File | Key components |
|---|---|---|
| Insurance Agency | `insurance_pack.json` | Recruiting + consumer pipelines, licensed-agent recruiting funnel, iDecide recruiting presentation, interview calendar, AI/voice recruiting agents, candidate scoring, contracting workflow, compliance review controls |
| Real Estate | `real_estate_pack.json` | Buyer/seller/investor pipelines, home-valuation funnel, missed-call text-back, showing calendar, long-term nurture, database reactivation, iDecide buyer/seller/recruiting presentations |
| Home Services | `home_services_pack.json` | Estimate/job pipelines, AI receptionist, emergency-service routing, estimate reminders, unsold-estimate follow-up, maintenance reminders, revenue attribution dashboard |

Each pack declares its own `problems_solved` list and `disclosures` —
compliance content is never shared across industries (insurance disclosures
never apply to home services, etc.).

### 3. Client Configuration Layer

Twelve required fields validated before any snapshot is applied
(`REQUIRED_CLIENT_CONFIG_FIELDS`): branding, domain, phone_numbers, email,
calendars, users, services, service_areas, pricing, disclosures,
integrations, escalation_contacts. Missing any of these raises
`MissingClientConfigurationError` and blocks onboarding
(`tests/test_missing_configuration.py`).

## Assembly & deployment

`SnapshotAssembler.assemble()` merges the three layers without ever leaking
one layer's data into another (`tests/test_snapshot_assignment.py`).
`SnapshotAssembler.deploy(adapter, location_id)` applies universal core then
industry pack via the `GHLAdapter`, and raises `SnapshotApplicationError` —
routing the onboarding state machine to `BLOCKED` — if either apply call
fails (`tests/test_failed_snapshot_application.py`).

## Versioning

Every snapshot file carries a `version` field. `ProductizationDirectorAgent`
reports the current universal-core version and the full list of productized
industry packs each cycle, so drift between the "current" and "deployed to
client X" version is visible instead of silent.
