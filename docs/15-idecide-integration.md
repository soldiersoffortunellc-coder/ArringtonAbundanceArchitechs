# 15 — iDecide Integration

## Capability matrix (machine-readable: `config/marketing/idecide/capability_matrix.json`)

**I could not find or verify a documented public iDecide API** from this
build environment — no iDecide account, docs access, or prior integration
code exists in this repository, and I will not fabricate one. Every
capability below is marked UNVERIFIED except where this repo's own code
(not iDecide's) can act once *any* link/webhook payload is available:

| Capability | Native GHL | Webhook | Zapier/Make | Manual | Status |
|---|---|---|---|---|---|
| Create personalized presentation link | Unverified | Unverified | Possibly (if listed) | Yes, via iDecide dashboard | **UNVERIFIED** |
| Associate presentation with GHL contact | Unverified | Possible | Possibly | Yes, manual paste | **UNVERIFIED** |
| Store link in GHL custom field | Unverified | **Yes** (this repo can write it once received) | Possibly | Yes | **PARTIALLY SUPPORTED** |
| Receive presentation-started event | Unverified | Possible | Possibly | No | **UNVERIFIED** |
| Receive presentation-completed event | Unverified | Possible | Possibly | No | **UNVERIFIED** |
| Receive viewer choices / slides viewed | Unverified | Possible (payload-dependent) | Possibly | No | **UNVERIFIED — payload shape unknown** |
| Trigger a GHL workflow on completion | Unverified | Likely (if iDecide can POST to a GHL inbound webhook URL) | Likely (common pattern) | Yes | **LIKELY SUPPORTED, NOT CONFIRMED** |

**Recommended approach** (and what this build does): build `IDecideAdapter`
against the generic webhook + link-token shape common to this class of
tool, verify each row against your actual iDecide account/subscription
before enabling anything live, and fall back to a plain GHL calendar link
or short form for any capability that turns out unsupported — per the
operating rule "do not force the prospect through an unnecessary
presentation."

## Architecture

See the `iDecideFlow` subgraph in
`docs/14-media-marketing-architecture.md`'s Mermaid diagram for the full
data-flow picture:

```
AI Clone Video → Social CTA → GHL Lead Capture → Personalized iDecide Link
→ Interactive Presentation → Viewer Behavior Captured → AI Lead Qualification
→ GHL Tagging/Segmentation → Correct Follow-Up Workflow
→ Appointment / Recruiting Interview / Application / Program Inquiry
→ Pipeline Advancement → Conversion Tracking
```

iDecide does not replace GHL — GHL remains the CRM/pipeline/scheduling/
attribution system of record. iDecide is the personalized presentation
layer in the middle.

## IDecideAdapter

`src/csuite/providers/idecide_adapter.py`. Dry-run/mock by default (same
convention as every other provider adapter). Implements:
`create_personalized_link`, `record_started_event`,
`record_completion_event` (idempotent — refuses to double-process a
repeated `event_id`, since iDecide may re-fire the completion webhook),
`isolate_session_for_contact` (cross-contact isolation guard). Live calls
are not wired up (no confirmed API) — this is the same
`ProviderLiveModeNotAuthorized` pattern used everywhere else in this repo.

## Data models

`src/csuite/marketing/models.py` — `IDecidePresentation`,
`IDecidePresentationVersion`, `IDecidePersonalizedLink`,
`IDecideViewerSession`, `IDecideViewerChoice`, `IDecideOutcome`,
`IDecideCompletionEvent`, `IDecideCTASelection`, `IDecideAgentAssignment`,
`IDecideCampaignMapping`, `IDecideGHLFieldMapping`,
`IDecideWorkflowMapping`, `IDecideSubaccountConfiguration` — all present,
all in-memory dataclasses (no database in this repo — see docs/13).

## Presentation types (`config/marketing/idecide/presentation_types.json`)

Four configured types, each with its own viewer-path → pipeline-stage
routing: **Licensed Agent Recruiting** (8 paths), **Consumer Financial
Education** (9 paths, `individualized_recommendation_blocked: true` — no
automated product recommendation, ever, without licensed human
fact-finding), **Agent Onboarding and Training** (9 paths), **Open Doors
Community Programs** (9 paths). Kept separated per business — cross-brand
mixing requires explicit approval, same rule as content pillars.

## Lead scoring (`config/marketing/idecide/lead_scoring.json`)

Event-weighted, fully configurable (`src/csuite/marketing/
lead_scoring.py::LeadScoringEngine`). Repeat completions are recorded
(`repeat_completion_count`) but score **zero points by default** — the spec
explicitly says not to auto-interpret repeats as higher intent; the
qualification agent evaluates that fact in context.

## GHL custom fields (`config/marketing/idecide/field_map.template.json`)

17 fields, every value a `PLACEHOLDER` — validated by
`content_strategy.validate_ghl_marketing_config()`
(`tests/marketing/test_missing_credentials_and_config.py` proves the
shipped template is 100% placeholders, so it can never be mistaken for a
filled-in config).

## Compliance controls

`MarketingComplianceOfficerAgent`/`ComplianceEngine` apply identically to
iDecide presentation scripts as to social scripts — same risk levels, same
mandatory-approval categories, same prohibited-phrase blocking. An
unapproved presentation version must never be attached to an active
campaign (`IDecidePresentationVersion.compliance_approved` gates this —
enforcing it against a live iDecide account is a next-phase integration
step once the API is confirmed).

## Subaccount scalability

`IDecideSubaccountConfiguration` models one iDecide integration per GHL
location explicitly (its own account/login, field map, workflow map — never
assumed to be shared agency-wide). No code here assumes agency-level
installation licenses every subaccount automatically.

## What's implemented vs. manual vs. unsupported

| Layer | Status |
|---|---|
| Data models, lead scoring, compliance gating, cross-contact isolation, idempotent completion handling | **Implemented, tested** (`tests/providers/test_idecide_integration.py`) |
| Personalized link creation, started/completion event ingestion | **Implemented as dry-run/mock** — real iDecide wiring needs a confirmed API (see capability matrix) |
| GHL custom-field writes for iDecide data | **Implemented via GHLAdapter** once field IDs are supplied (docs/09) |
| Triggering a GHL workflow from a completion event | **Manual GHL configuration** (webhook → workflow trigger), same limitation as every other GHL workflow in this system |
| The actual iDecide↔GHL native integration, if one exists | **UNVERIFIED — confirm in your iDecide account before relying on anything beyond the adapter above** |
