# 00 — Repository & GHL Architecture Audit

## What existed before this build

The repository contained exactly one asset: `abundance-architects-site.zip`, a
5-section static marketing page (`index.html` + `styles.css` + a logo) for
"Arrington Abundance Architects" — a personal-brand site around Faith,
Finance, Fitness, Real Estate, and Travel & Lifestyle. It is unrelated
front-end brand content, not a CRM, not a GHL integration, and not a
C-Suite AI Agent System. **There was no existing C-Suite AI Agent System,
GHL integration, snapshot, pipeline, onboarding flow, or revenue model
anywhere in the repository or in version control history** (the repo has a
single commit: "Add files via upload").

There is also no connected GoHighLevel account, API key, agency ID, or
SaaS Configurator configuration available to this build. Nothing here talks
to a live GHL instance.

## What this build adds

A complete, dry-run-by-default **White-Label AI Revenue Operating System**
scaffold, built as an installable Python package (`src/csuite/`) plus
configuration data (`config/`) plus documentation (`docs/`) plus an
executive dashboard (`dashboard/`) plus a full test suite (`tests/`):

- **13 task-oriented AI agents**: 7 C-suite agents (CEO, CRO, CMO, COO, CFO,
  CTO, CCO) plus the 6 revenue subordinates the CRO directs (Market
  Opportunity Analyst, Productization Director, Sales Director, Client
  Onboarding Director, Client Success and Retention Director, Revenue
  Operations Analyst). See `docs/05-c-suite-agent-roster.md`.
- A **GHL adapter** (`src/csuite/ghl/adapter.py`) that is the single choke
  point every agent uses to direct GoHighLevel — locations, snapshots,
  pipelines, custom fields, calendars, workflows, opportunities, billing
  events, and notifications — with a hard dry-run default and no path to a
  live call without explicit, human-driven authorization.
- **Snapshot architecture**: universal core + 3 industry packs (insurance
  agency, real estate, home services) + client configuration layer, kept
  strictly separated per the operating rules.
- **Sales pipeline**, **client onboarding state machine**, **tenant
  registry** (duplicate-account prevention + isolation), **role
  permissions**, **AI usage limits**, **global pause**, **safe
  offboarding**, and a **billing ledger** that never conflates contracted
  and collected revenue.
- A **90-day financial model** with conservative/target/aggressive
  scenarios, matching the specified target numbers exactly.
- An **executive command-center dashboard** (`dashboard/index.html`).
- **66 passing tests** (`tests/`) covering every item in the required test
  list.

## What is deliberately postponed (not built in this phase)

Per the operating rule "do not attempt to launch ten industries at once" and
"do not activate paid services without authorization":

- Live GHL API integration (no credentials exist — see
  `docs/09-credentials-and-ghl-ids.md`). `GHLAdapter._live_call` is a typed
  stub raising `NotImplementedError` until credentials are supplied.
- Actual snapshot JSON exports importable into a real GHL sub-account (the
  `config/snapshots/*.json` files are this system's own spec format, not a
  GHL export — a human with agency-admin access must build the real GHL
  snapshot and record its snapshot ID here).
- The 7 secondary industries (mortgage, med spas, dental, law firms,
  accounting/tax, fitness, coaching, property management, nonprofit,
  veteran-service orgs, sober living) — architecture supports them (just add
  a new `config/snapshots/<industry>_pack.json` + register it in
  `INDUSTRY_SNAPSHOT_IDS`), but none are productized yet.
- A real outbound-messaging/SMS/voice provider integration, a real payment
  processor, A2P 10DLC registration, and DNS/domain verification — all
  manual/carrier/compliance steps outside code, listed per-snapshot in each
  `requires_manual_or_api_configuration` field.
- A persistent database / multi-process deployment — the current system is
  an in-memory reference implementation proving the logic; the real
  deployment target is documented in `docs/17` (folded into
  `docs/10-deployment-plan-and-calendar.md`).

## How to run it

```bash
python3 scripts/run_demo.py                       # runs one full dry-run cycle
python3 -m unittest discover -s tests -t .         # runs all 66 tests
```
Then serve `dashboard/` over HTTP (not `file://`) to view the executive
command center against the demo data.
