# Open Doors Financial OS v1 — Architecture

Status: **first execution only** (discovery + proposed architecture). No
GHL infrastructure has been created. See `BUILD-STATUS.md` for the
authoritative per-component status table.

## What this is

A duplicatable, GoHighLevel-centered operating system for Open Doors
Financial Group (and, eventually, other insurance agencies) with three
layers:

1. **GoHighLevel** — system of record: contacts, opportunities, pipelines,
   calendars, custom fields/tags, workflows (UI-configured), conversations.
2. **n8n** — orchestration layer: routes GHL webhook events, coordinates
   AI agents, handles retries/dead-lettering/human escalation.
3. **AI agents** — intelligence layer: 12 specialized agents (Phase 9),
   each scoped to one job with a defined output schema, prohibited
   actions, and escalation conditions — never one agent doing everything.

Build order is strict (see the phase list below) because n8n workflows and
AI agents both need stable GHL object IDs to reference. Building workflows
against IDs that don't exist yet, or that later change, produces silent
breakage — hence Phase 11 (the 28 production workflows) is explicitly
blocked until Phases 3–7 are stable and tested.

## Relationship to the existing repository content

This repository already contains a separate, working system built in an
earlier phase of this engagement: the **White-Label AI Revenue Operating
System / C-Suite AI Agent System** (`src/csuite/`, `config/*.json` at the
existing paths, `docs/00`–`docs/16`, `dashboard/`). That system is a
Python-native, dry-run-by-default reference implementation of C-suite
agent coordination (19 agents), a GHL adapter, and an AI-clone marketing
pipeline for the Coach Rashon / Open Doors brands generally.

**Open Doors Financial OS v1 is a new, GHL/n8n-native build for Open Doors
Financial Group specifically** (Phases 1–15 above), living alongside that
existing system in the same repository, not replacing it:

| Existing system | Open Doors Financial OS v1 |
|---|---|
| `src/csuite/` (Python classes) | `/ghl`, `/n8n`, `/agents`, `/workflows` (GHL objects + n8n JSON + agent specs) |
| `GHLAdapter` (dry-run, generic) | Real, read-only GHL API calls first; object creation only after this first execution's approval gate |
| `config/*.json` at root paths | `config/os-v1.yaml` + `config/ghl-object-registry.json` (new, additive files) |
| `dashboard/` (Revenue OS KPIs) | `dashboards/` (insurance-ops KPIs — plural, separate) |
| `docs/00`–`docs/16` | `docs/GHL-CURRENT-STATE.md` + this file + `DEPLOYMENT-SOP.md`/`CHANGELOG.md`/`BUILD-STATUS.md` |

**Reused directly, not duplicated:** `src/csuite/ghl/api_client.py`
(`GHLApiClient`) — its Bearer-token + required `Version`-header HTTP
plumbing against `https://services.leadconnectorhq.com` is already correct
and tested (`tests/test_ghl_live_connection.py`). OS v1's scripts import it
and pass it OS v1's own credentials explicitly (see below) rather than
copy-pasting an HTTP client.

## Credentials — two separate env-var sets, on purpose

The existing system's `GHLAdapter`/`GHLApiClient` reads `GHL_ACCESS_TOKEN`
by default (a deliberate decision made earlier in this engagement — kept
as-is, not renamed, to avoid touching working code). Open Doors Financial
OS v1's security rules explicitly require:

```
GHL_LOCATION_ID
GHL_PRIVATE_INTEGRATION_TOKEN
GHL_API_VERSION
```

Both can point at the same underlying GHL Private Integration Token
value — they are just two names read by two different scripts. OS v1's
scripts (`scripts/ghl_connection_test.py`, `scripts/ghl_discovery.py`)
read the OS-v1-specific names and pass them into `GHLApiClient` explicitly
(`GHLApiClient(access_token=..., version=...)`), never relying on that
client's internal default env var. This satisfies OS v1's own named
security requirement without renaming or duplicating shared, working
infrastructure.

## Phase status summary

See `BUILD-STATUS.md` for the full table. As of this first execution:
Phase 0 (bootstrap) — IN PROGRESS/COMPLETE this run. Phase 1 (connection
test) — see the PASS/FAIL report below/in the final report. Phase 2
(discovery) — BLOCKED pending credentials. Phases 3–15 — NOT STARTED
(Phase 3's *proposed*, undeployed architecture is drafted now per the
first-execution instructions — see `config/os-v1.yaml`).

## Proposed canonical data model (Phase 3, PROPOSED — not yet deployed)

`config/os-v1.yaml` is the source of truth going forward: every GHL object
this system creates gets a logical name, GHL display name, purpose, type,
generated ID (blank until created), dependencies, and deployment status.
`config/ghl-object-registry.json` is the flat, machine-readable ID lookup
n8n workflows and agent tooling will reference by logical name — never a
hard-coded GHL ID.

Proposed objects (drawn directly from the mandate; not yet created,
not yet compared against the live account — that comparison is Phase 2,
currently blocked on credentials):

- **6 pipelines**: `01 | Insurance Sales`, `02 | Agent Recruiting`,
  `03 | Licensing`, `04 | Agent Onboarding`, `05 | Annuity / Rollover`,
  `06 | IBC / Debt Action` — full stage lists in `config/os-v1.yaml`.
- **7 calendars**: Insurance Discovery, IBC/Debt Strategy,
  Annuity/Rollover, Agent Opportunity, Agent Onboarding, Leadership
  Interview, Client Annual Review.
- **Custom fields**: contact-level classification/consent/assignment
  fields and opportunity-level product/financial fields per the mandate's
  minimum-necessary list — see `config/os-v1.yaml` for the full field
  list with logical names.
- **Tag taxonomy**: prefixed (`SRC |`, `INT |`, `STATUS |`, `AGENT |`,
  `CLIENT |`, `CAMPAIGN |`, `COMPLIANCE |`) — the taxonomy structure is
  proposed in `config/os-v1.yaml`; the exhaustive tag list is a Phase 5
  deliverable once discovery confirms what already exists (to avoid
  proposing duplicates of tags already in the account).

**None of this has been created in GHL.** Creating it requires (a) a
successful connection test, (b) a completed discovery pass to check for
naming conflicts against what already exists, and (c) explicit approval —
none of which this first execution is authorized to skip past.

## Idempotency commitment (binding on all future creation code)

Every object-creation script for Phases 4–6 must, before creating
anything: query for an existing object with the same logical/display name,
compare configuration if found, and refuse to create a duplicate. Running
any deployment script twice must be a no-op the second time. This is not
yet exercised (nothing has been created yet) but is a hard constraint on
the code that will do so.
