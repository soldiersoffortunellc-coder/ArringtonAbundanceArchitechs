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
| Insurance Agency | `insurance_pack.json` | Recruiting + consumer pipelines, licensed-agent recruiting funnel, iDecide recruiting presentation, interview calendar, AI/voice recruiting agents, candidate scoring, contracting workflow, compliance review controls, **Meta (Facebook/Instagram) Lead Ads recruiting sync** |
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

## Meta (Facebook/Instagram) Lead Ads recruiting sync (insurance pack)

`config/pipelines/recruiting_pipeline.json` defines the 12-stage candidate
pipeline (`New Candidate (Meta Lead)` → ... → `Active Agent` /
`Disqualified`, the latter requiring a disqualification reason from a fixed
vocabulary — same enforcement pattern as the sales pipeline's loss reasons).
`config/meta_lead_ads/insurance_recruiting_form_mapping.json` maps a Meta
Lead Ads form's raw answer keys onto this system's candidate fields
(`full_name`, `phone`, `licensing_status`, ...) and routes the resulting
candidate to `licensed_agent_recruiting_funnel` or
`licensing_interest_funnel` based on their answer.

Implementation: `src/csuite/pipeline/recruiting_pipeline.py`
(`RecruitingPipeline`, kept separate from `SalesPipeline` — a candidate and
a sales opportunity carry different fields) and
`src/csuite/ghl/meta_recruiting.py` (`MetaRecruitingLeadRouter.ingest_lead()`
— maps the raw lead, validates required fields, normalizes the licensing
answer, opens a recruiting-pipeline candidate, and tags/opens an opportunity
via `GHLAdapter`, deduping on `fb_lead_id` so a redelivered webhook never
creates a second candidate).

**Important:** GHL's own Facebook integration (connected in the GHL UI) is
what actually receives the ad platform's webhook and creates the contact —
there is no public API endpoint that "ingests a lead" directly.
`GHLAdapter.fb_get_integration` / `fb_get_page_lead_forms` (both real,
read-only GHL API v2 calls under `/ad-publishing/facebook/...`, confirmed
against GHL's live operation registry) only verify that integration and its
lead forms are connected; `MetaRecruitingLeadRouter` handles what happens
*after* GHL has already created the contact.

## Versioning

Every snapshot file carries a `version` field. `ProductizationDirectorAgent`
reports the current universal-core version and the full list of productized
industry packs each cycle, so drift between the "current" and "deployed to
client X" version is visible instead of silent.
