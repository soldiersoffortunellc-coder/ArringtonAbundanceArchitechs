> **New: [Open Doors Financial OS v1](ARCHITECTURE.md)** — a separate,
> GHL/n8n-native operating-system build for Open Doors Financial Group
> specifically, living alongside the system below in this same repo. Start
> at [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`BUILD-STATUS.md`](BUILD-STATUS.md)
> for that build's current state (first execution: repo bootstrap + a
> blocked-on-credentials connection/discovery attempt — nothing has been
> created in GHL yet).

# White-Label AI Revenue Operating System — C-Suite AI Agent System

A duplicatable, scalable, salable **AI Revenue Operating System** built on
top of GoHighLevel (GHL), directed by a **C-Suite AI Agent System**: 7
C-suite-level agents (CEO, CRO, CMO, COO, CFO, CTO, CCO) directing 6 revenue
subordinate agents under the CRO **and** 6 AI Media & Marketing Division
subordinates under the CMO — **19 task-oriented agents in total**.

The **AI Media & Marketing Division** (see
[`docs/13-media-marketing-audit-and-plan.md`](docs/13-media-marketing-audit-and-plan.md))
creates, compliance-reviews, approves, publishes, tracks, and improves
AI-clone marketing videos for Rashon Arrington's businesses (Open Doors
Financial Group, Open Doors Global Development Foundation, and the Coach
Rashon personal brand) through GHL — with mandatory human approval on
every AI-clone post's first 30 days and every regulated claim, and an
optional iDecide interactive-presentation layer in the middle of the
funnel.

This is installed business infrastructure, not a generic CRM: industry-
specific Revenue Operating Systems for insurance agencies, real estate, and
home services, each built from a shared universal core plus an
industry-specific pack plus per-client configuration.

**Everything here defaults to dry-run.** No agent in this repository ever
sends a real message, provisions a real GHL account, or moves real money
unless a human explicitly constructs the system with live authorization
(see [`docs/09-credentials-and-ghl-ids.md`](docs/09-credentials-and-ghl-ids.md)).
Every modeled revenue number is explicitly labeled as a planning input, not
a guaranteed outcome.

## Connecting to a real GoHighLevel account

Not connected yet — no credentials exist in this repo or environment.
`src/csuite/ghl/api_client.py` is a real, working HTTPS client against
GoHighLevel's API v2 (`https://services.leadconnectorhq.com`, Bearer auth +
required `Version` header), and `GHLAdapter` now dispatches supported
actions (contacts/tags, opportunities, custom fields, calendars, users,
messages) to it in live mode — while clearly refusing the handful of
actions GHL's public API doesn't expose (snapshot application to an
existing location, pipeline/workflow creation, generic campaign publish,
billing events — see `docs/12`).

**To connect it yourself:** set `GHL_ACCESS_TOKEN` (a Private Integration
Token or OAuth access token) and `GHL_LOCATION_ID` as environment variables
on your own machine — never paste a token into a chat — then run:

```bash
python3 scripts/check_ghl_connection.py
```

Full details, the auth model (Private Integration Token vs. OAuth
marketplace app), and exactly which endpoints are wired up:
[`docs/12-live-ghl-connection.md`](docs/12-live-ghl-connection.md).

## Quickstart

```bash
# Run one full dry-run operating cycle against realistic synthetic data (19 agents)
python3 scripts/run_demo.py

# Walk one sample campaign through the Media & Marketing pipeline to the human-approval gate
python3 scripts/run_marketing_demo.py

# Run the full test suite (155 tests, zero external dependencies)
python3 -m unittest discover -s tests -t .

# View the executive command center (must be served over HTTP, not file://)
python3 -m http.server 8000
# then open http://localhost:8000/dashboard/
```

No dependencies beyond the Python 3.10+ standard library are required to
run the agents, the demos, or the tests.

## Repository layout

```
config/                  All configurable data: pricing, financial scenarios, pipeline
                          stages, onboarding states, role permissions, AI usage limits,
                          the 3-layer snapshot specs (universal core + 3 industry packs),
                          and marketing/ (content pillars, content mix, brand profiles,
                          prohibited claims, disclosures, workflow blueprints, iDecide config).
src/csuite/
  agents/                 The 7 C-suite agents (ceo, cro, cmo, coo, cfo, cto, cco)
  agents/revenue/         The 6 revenue subordinates the CRO directs
  agents/marketing/       The 6 Media & Marketing subordinates the CMO directs
  ghl/                    GHLAdapter (the single directed interface onto GoHighLevel),
                          snapshot assembly, and the SaaS provisioning workflow
  marketing/              Campaign state machine, in-memory store, compliance engine,
                          content-strategy loader, lead scoring, approval queue, webhooks
  providers/              AvatarVideoAdapter, VoiceAdapter, SocialPlatformAdapter,
                          StorageAdapter, AnalyticsAdapter, IDecideAdapter — all
                          dry-run/mock by default, same convention as GHLAdapter
  onboarding/             The client onboarding state machine
  pipeline/               The sales pipeline model
  platform/               Tenant isolation, role permissions, AI usage limits,
                          global pause + scoped publishing pause, safe offboarding, billing ledger
  revenue/                90-day financial model, margin/profitability calculator,
                          market opportunity scoring model
  orchestrator.py          RevenueOperatingSystem — wires all 19 agents together
scripts/run_demo.py               Runs one full Revenue OS cycle, writes dashboard_data.json
scripts/run_marketing_demo.py     Walks a sample campaign to the human-approval gate
dashboard/                Executive command-center (static HTML, reads dashboard_data.json)
tests/                    155 tests; tests/marketing/ and tests/providers/ cover the new division
docs/                     The requested deliverables (see mapping below)
```

## Deliverables index

| # | Deliverable | Where |
|---|---|---|
| 1 | Audit of the existing repository/GHL architecture | [`docs/00-audit-and-roadmap.md`](docs/00-audit-and-roadmap.md) |
| 2 | Market-opportunity scorecard | [`docs/01-market-opportunity-scorecard.md`](docs/01-market-opportunity-scorecard.md) |
| 3 | Final three-industry recommendation | [`docs/01-market-opportunity-scorecard.md`](docs/01-market-opportunity-scorecard.md) |
| 4 | Complete offer ladder | [`docs/02-offer-ladder-and-financial-model.md`](docs/02-offer-ladder-and-financial-model.md), [`config/offer_ladder.json`](config/offer_ladder.json) |
| 5 | 90-day financial model | [`docs/02-offer-ladder-and-financial-model.md`](docs/02-offer-ladder-and-financial-model.md), [`config/financial_scenarios.json`](config/financial_scenarios.json), [`src/csuite/revenue/financial_model.py`](src/csuite/revenue/financial_model.py) |
| 6 | Universal snapshot specification | [`docs/03-snapshot-architecture.md`](docs/03-snapshot-architecture.md), [`config/snapshots/universal_core.json`](config/snapshots/universal_core.json) |
| 7 | Three industry-pack specifications | [`docs/03-snapshot-architecture.md`](docs/03-snapshot-architecture.md), [`config/snapshots/`](config/snapshots/) |
| 8 | SaaS provisioning architecture | [`docs/04-ghl-provisioning-architecture.md`](docs/04-ghl-provisioning-architecture.md) |
| 9 | Revenue-agent definitions | [`docs/05-c-suite-agent-roster.md`](docs/05-c-suite-agent-roster.md), [`src/csuite/agents/`](src/csuite/agents/) |
| 10 | Sales pipeline | [`docs/06-sales-pipeline-and-onboarding.md`](docs/06-sales-pipeline-and-onboarding.md), [`config/sales_pipeline.json`](config/sales_pipeline.json) |
| 11 | Client onboarding system | [`docs/06-sales-pipeline-and-onboarding.md`](docs/06-sales-pipeline-and-onboarding.md), [`config/onboarding_states.json`](config/onboarding_states.json) |
| 12 | Fulfillment workflow | [`docs/04-ghl-provisioning-architecture.md`](docs/04-ghl-provisioning-architecture.md) |
| 13 | Client-success workflow | [`docs/05-c-suite-agent-roster.md`](docs/05-c-suite-agent-roster.md) → Client Success and Retention Director |
| 14 | Executive command-center specification | [`docs/07-executive-command-center.md`](docs/07-executive-command-center.md), [`dashboard/`](dashboard/) |
| 15 | Sales assets | [`docs/08-sales-assets.md`](docs/08-sales-assets.md) |
| 16 | Tests | [`tests/`](tests/) (66 passing tests) |
| 17 | Required credentials and GHL IDs | [`docs/09-credentials-and-ghl-ids.md`](docs/09-credentials-and-ghl-ids.md) |
| 18 | Deployment plan | [`docs/10-deployment-plan-and-calendar.md`](docs/10-deployment-plan-and-calendar.md) |
| 19 | 90-day implementation calendar | [`docs/10-deployment-plan-and-calendar.md`](docs/10-deployment-plan-and-calendar.md) |
| 20 | Capacity and hiring requirements | [`docs/10-deployment-plan-and-calendar.md`](docs/10-deployment-plan-and-calendar.md) |
| — | Risks and assumptions | [`docs/11-risks-and-assumptions.md`](docs/11-risks-and-assumptions.md) |
| — | Live GHL connection (auth model, wired endpoints, how to connect) | [`docs/12-live-ghl-connection.md`](docs/12-live-ghl-connection.md) |
| — | **AI Media & Marketing Division** — audit + implementation plan | [`docs/13-media-marketing-audit-and-plan.md`](docs/13-media-marketing-audit-and-plan.md) |
| — | Media & Marketing architecture + Mermaid diagram | [`docs/14-media-marketing-architecture.md`](docs/14-media-marketing-architecture.md) |
| — | iDecide integration (capability matrix, adapter, models) | [`docs/15-idecide-integration.md`](docs/15-idecide-integration.md) |
| — | Media & Marketing setup, checklists, troubleshooting, deployment, rollback | [`docs/16-media-marketing-setup-and-checklist.md`](docs/16-media-marketing-setup-and-checklist.md) |

## Operating rules this codebase enforces in code, not just policy

- **Dry-run by default, everywhere.** `GHLAdapter(dry_run=False)` without
  `live_authorized=True` raises immediately.
- **Contracted revenue and cash collected are never conflated** — tracked
  as separate fields end-to-end (`BillingLedger`, `RevenueOperationsAnalystAgent`).
- **Modeled revenue is never presented as guaranteed** — every scenario is
  stamped `is_guaranteed: false` and every narrative caveat says so.
- **A global pause blocks every write-directing agent**, immediately
  (`GlobalControls.guard()`).
- **Offboarding requires an explicit `confirm=True`** and retains client
  data rather than destroying it.
- **Duplicate accounts and cross-tenant data access are structurally
  prevented**, not just discouraged (`TenantRegistry`).
- **Closed Lost always requires a loss reason** from a fixed vocabulary.
- **Missing client configuration or a failed snapshot apply blocks
  onboarding** instead of launching a broken account.
- **A minimum of 5 (this build ships 7) distinct C-suite agents** exist and
  are enforced by `tests/test_agent_roster.py`.
- **Every AI-clone video's script must clear compliance review, and every
  AI-clone post in its first 30 days requires human approval regardless of
  risk level** — enforced in `ComplianceEngine`, not just documented policy.
- **Blocked phrases (e.g. "guaranteed returns", "risk-free wealth",
  "instant approval") are hard-blocked outright**, not just flagged.
- **A permission check succeeding is never confused with an approval** —
  `ApprovalQueue` still requires the campaign to actually be sitting in
  `HUMAN_APPROVAL_REQUIRED`; the RBAC check and the state-machine
  transition are two independent gates.
- **No avatar video or synthetic voice is ever generated without a
  documented `ConsentAuthorization`** — `AvatarVideoAdapter`/`VoiceAdapter`
  raise `ConsentRequiredError` otherwise.
- **Duplicate social posts (same platform + identical content) are
  structurally rejected**, not just discouraged.
- **Publishing has its own scoped kill switch** (`GlobalControls
  .pause_publishing()`), independent of the full-system pause, so marketing
  can be halted without stopping revenue operations and vice versa.
- **Every inbound comment/DM/webhook payload is treated as untrusted data**
  — sanitized and pattern-matched against a literal keyword allow-list,
  never evaluated, executed, or treated as an instruction
  (`tests/marketing/test_webhook_authentication.py::TestPromptInjectionResistance`).

## What this is not (yet)

This is a reference implementation of the *business logic and rules* — an
in-memory, dependency-free Python package proving out the agent
coordination, snapshot architecture, revenue truth-in-reporting, and
guardrails described in the mandate. It is **not** connected to a real GHL
account (no credentials exist — see docs/09), does not send real messages,
and does not move real money. See
[`docs/00-audit-and-roadmap.md`](docs/00-audit-and-roadmap.md) for exactly
what's built vs. postponed, and
[`docs/10-deployment-plan-and-calendar.md`](docs/10-deployment-plan-and-calendar.md)
for how this becomes a live, multi-tenant production system.

---

The pre-existing `abundance-architects-site.zip` (a personal-brand static
site unrelated to this system) is left untouched in the repository root.
