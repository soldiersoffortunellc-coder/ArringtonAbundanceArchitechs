# 13 — AI Media & Marketing Division: Repository Audit & Implementation Plan

## Phase 1 — Repository audit

### Application stack
- **Language**: Python 3.10+, standard library only (no `requirements.txt`
  runtime dependencies — a deliberate choice in the original build so the
  system runs anywhere with zero `pip install`).
- **No web framework, no ORM, no database.** The system is an in-memory
  reference implementation of business logic (`src/csuite/`), backed by
  plain JSON config files (`config/`). There is currently **no persistence
  layer** — everything lives in Python objects for the life of one process.
  This matters for "use the project's existing database and migration
  conventions": **there is no database or migration tool in this repo to
  follow.** The existing convention instead is: (a) static config as
  versioned JSON in `config/`, (b) runtime state as in-memory
  dataclasses/registries (e.g. `TenantRegistry`, `BillingLedger`,
  `SalesPipeline`). The Media & Marketing Division follows that same
  convention rather than introducing a new persistence pattern
  unilaterally — see "Assumptions" below.
- **Packaging**: `pyproject.toml`, src-layout (`src/csuite/`), importable via
  `conftest.py`/`tests/__init__.py` sys.path shims — no install step
  required for local dev or tests.

### AI agent framework
`src/csuite/agents/base.py::BaseAgent` — every agent is a class with
`name`, `title`, `mission`, `kpis_owned`, `ghl_authority`, and a
`run(context) -> AgentReport` method. `AgentReport` carries `decisions`,
`directives_issued`, `kpis`, `escalations`, `warnings`. A C-suite agent
(e.g. `CROAgent`) that owns subordinates builds a `subordinates: dict[str,
BaseAgent]` in `__init__` and fans `run()` out to each of them, merging
their reports. This division follows that exact pattern for the CMO.

### Existing C-Suite agents (7 C-suite + 6 revenue subordinates = 13)
`src/csuite/agents/{ceo,cro,cmo,coo,cfo,cto,cco}.py` +
`src/csuite/agents/revenue/*.py` (Market Opportunity Analyst, Productization
Director, Sales Director, Client Onboarding Director, Client Success and
Retention Director, Revenue Operations Analyst). Wired together in
`src/csuite/orchestrator.py::RevenueOperatingSystem`.

**A `CMOAgent` already exists** (`src/csuite/agents/cmo.py`) with a narrow
mission (publish campaigns, track leads-by-channel). Per "do not
unnecessarily restructure," I **extend** this existing agent in place —
adding a `subordinates` dict (mirroring `CROAgent`) and a new
`run_media_division()` method — rather than creating a second, competing
CMO. Its original `run()` method and behavior are left untouched so nothing
that currently depends on it (the Revenue OS demo/tests) breaks.

### Shared tools / adapters
`src/csuite/ghl/adapter.py::GHLAdapter` — the single choke point for GHL
writes. Hard dry-run default; live mode requires `live_authorized=True` +
an explicit `GHLApiClient` (added in a prior session, `src/csuite/ghl/
api_client.py`, real HTTP client for `services.leadconnectorhq.com`).
Unsupported GHL public-API actions raise `GHLUnsupportedActionError` rather
than silently guessing.

There is **no existing provider-adapter package for non-GHL services**
(no video, voice, social, storage, or analytics adapter existed before this
division). New provider adapters live in a new `src/csuite/providers/`
package, kept separate from `src/csuite/ghl/` because they are not
GHL-specific — this is a new-but-consistent extension of the existing
"adapter" naming convention (`GHLAdapter`, `GHLApiClient`).

### Prompts
No prompt-template system existed before this division (the existing
agents are deterministic Python logic, not LLM-prompted — there is no LLM
API key or client anywhere in the repo). This division introduces
version-controlled prompt/voice specs as **data**, not code
(`config/marketing/brand_profiles/*.json`), consistent with the rest of the
repo's "behavior in code, facts/config in JSON" split. See "Assumptions."

### Workflows
No workflow engine exists. "Workflow" in this repo means either (a) a GHL
workflow (UI/snapshot-only — confirmed unsupported via public API in
`docs/12-live-ghl-connection.md`), or (b) a plain Python
call-sequence (e.g. `src/csuite/ghl/provisioning.py::ProvisioningWorkflow`).
The Media & Marketing Division's 17 "minimum operational workflows" are
implemented the same way this repo already handles that split: the parts
that are genuinely GHL UI/automation configuration are documented as
structured **blueprints** (`config/marketing/workflow_blueprints.json`) to
be built in the GHL UI or shipped inside a snapshot; the parts that are
real inbound event processing (video-provider webhook, iDecide webhook,
social comment/DM keyword capture) are real, tested Python
(`src/csuite/marketing/webhooks.py`).

### Memory systems
No vector store / long-term memory system exists. "Memory" in this repo is
JSON config (`config/`) read at call time — e.g. `TenantRegistry.data` is
the closest existing pattern to a per-entity memory store. The brand-memory
system this division adds (`config/marketing/brand_profiles/*.json`)
follows that same pattern, with an explicit **fact-provenance split**
(`verified_facts` / `user_provided_unverified` / `prohibited_claims`) baked
into the schema itself — see `src/csuite/marketing/models.py::BrandProfile`.

### Dashboards
`dashboard/index.html` (static HTML + `dashboard_data.json` produced by
`scripts/run_demo.py`) is the existing executive command center. This
division adds its own approval-queue view rather than overloading that
dashboard's existing revenue-focused layout — see docs/16.

### Governance / security model
- Dry-run-by-default on every external integration (`GHLAdapter`,
  now mirrored by every new provider adapter).
- `GlobalControls.guard()` — a system-wide pause that blocks every
  write-directing agent. This division adds a **second, narrower** control,
  `GlobalControls.guard_publishing()`, so publishing specifically can be
  killed without pausing revenue operations, and vice versa (additive, not
  a replacement).
- `PermissionRegistry` (`config/role_permissions.json`) — role → allowed
  actions. Extended additively with the 5 new roles this spec requires
  (owner already exists; executive_approver, compliance_reviewer,
  content_operator, read_only_analyst are new).
- No secrets exist or are committed anywhere. `GHLApiClient` already reads
  `GHL_ACCESS_TOKEN` from the environment only. This division follows the
  identical pattern for every new credential (see `.env.example`).

### Tests / logging / deployment
`tests/` — `unittest`, zero dependencies, discoverable via
`python3 -m unittest discover -s tests -t .`. No logging framework (agents
return structured `AgentReport` objects instead of writing logs — the
caller decides what to do with them). No deployment process exists yet
(`docs/10-deployment-plan-and-calendar.md` is a plan, not a live pipeline).
This division follows the same test/no-logging conventions.

## Cleanest integration point

Extend `CMOAgent` (already the C-suite marketing seat) with a
`subordinates` dict of the 6 new marketing agents, exactly like `CROAgent`
already does for its 6 revenue subordinates. Wire the new provider adapters
into `RevenueOperatingSystem.__init__` alongside the existing `GHLAdapter`,
`TenantRegistry`, and `GlobalControls`. Nothing about the existing 13-agent
Revenue OS changes shape or behavior — this is 100% additive.

## Implementation plan

### Reused as-is (no changes)
`BaseAgent`/`AgentReport`, `GHLAdapter` (+ `GHLApiClient`), `TenantRegistry`,
`UsageLimitTracker`, `BillingLedger`, `SalesPipeline`, `PermissionRegistry`
class itself, `CEOAgent`, `CRO`/revenue subordinates, `COOAgent`,
`CFOAgent`, `CTOAgent`, `CCOAgent`, all existing tests, `dashboard/`,
`scripts/run_demo.py`.

### New components created
- `src/csuite/marketing/` — models, campaign state machine, in-memory
  store, compliance engine, content-strategy config loader, lead-scoring
  engine, approval queue, webhook processor.
- `src/csuite/providers/` — `AvatarVideoAdapter`, `VoiceAdapter`,
  `SocialPlatformAdapter`, `StorageAdapter`, `AnalyticsAdapter`,
  `IDecideAdapter` — all dry-run/mock by default, same audit-log pattern as
  `GHLAdapter`.
- `src/csuite/agents/marketing/` — 6 new subordinate agents.
- `config/marketing/` — content pillars, content mix, prohibited claims,
  disclosure requirements, brand profiles (3), pipeline mappings (3),
  workflow blueprints, iDecide presentation types / lead scoring / field
  map / capability matrix, role additions.
- `.env.example` (repo root — did not exist before).
- `scripts/run_marketing_demo.py`, `scripts/create_sample_campaign.py`.
- `tests/marketing/` and `tests/providers/` — new test packages.

### Existing files modified (additive only)
- `src/csuite/agents/cmo.py` — add `subordinates` + `run_media_division()`;
  existing `run()` untouched.
- `src/csuite/orchestrator.py` — construct the new provider adapters and
  pass them to the CMO's subordinates; add `run_media_division()` passthrough.
- `src/csuite/platform/controls.py` — add `guard_publishing()` /
  `pause_publishing()` / `resume_publishing()` (additive fields/methods).
- `config/role_permissions.json` — add 5 new roles + their actions to
  `action_catalog` (existing roles/actions untouched).
- `README.md` — new section + deliverables-index rows.

### Credentials / integrations that will be required (none exist yet)
See `docs/16-media-marketing-setup-and-checklist.md` for the exact list —
summarized: an avatar-video provider API key (e.g. HeyGen), optionally a
voice provider API key (e.g. ElevenLabs), an iDecide account/API access (if
and when iDecide exposes one — see `docs/15`), social-platform API
credentials only if GHL Social Planner can't cover a given platform, and
GHL credentials (already documented in `docs/09`/`docs/12`).

### Risks, unknowns, assumptions, limitations
1. **No database exists in this repo.** I did not introduce one
   unilaterally (that would be an architectural migration this task
   explicitly says not to start without documenting the reason). All new
   models are in-memory dataclasses + a `CampaignStore` registry, matching
   the existing `TenantRegistry` pattern. **Assumption**: when this goes to
   production, `CampaignStore` (and the other in-memory stores) get a real
   backing store — the classes are written so their public methods can be
   backed by a DB later without changing callers (documented in docs/16).
2. **No LLM/generative-AI API is wired into this repo.** `BrandVoiceContent
   StrategistAgent` therefore cannot *generate* novel copy from nothing —
   it **structures and validates** content from the facts/messages actually
   supplied in a `CampaignBrief`, and marks anything not explicitly
   supplied as `NEEDS_INPUT` rather than inventing it. This is the
   safest configurable option given "never fabricate personal stories,
   credentials, results, testimonials, statistics" — connecting a real
   generative model is a documented next step (docs/16), not done here
   without your explicit choice of provider/credentials.
3. **iDecide has no public API I could verify.** `docs/15` documents the
   capability matrix as **unknown/unverified** for anything beyond a
   webhook-shaped integration, per the instruction not to fabricate an
   iDecide API. The `IDecideAdapter` is built against a generic
   webhook+link-token shape common to this class of tool, clearly marked
   as needing verification against iDecide's actual current integration
   options before going live.
4. **GHL's public API does not support creating pipelines, workflows, or a
   generic "publish campaign" call** (confirmed in `docs/12` from the prior
   session). The 17 operational workflows and the 3 pipeline mappings are
   therefore **blueprints to configure once, by hand, in GHL** (or ship
   inside a snapshot) — not something this codebase can create via API.
   This is stated plainly everywhere it's relevant rather than glossed
   over.
5. **Social-platform-specific analytics (watch time, native engagement)**
   vary enormously by platform and typically require separate per-platform
   API access GHL Social Planner does not expose. `AnalyticsAdapter` and
   `MarketingAnalyticsOfficerAgent` explicitly tag every metric as
   `available` / `estimated` / `unavailable` per platform rather than
   pretending uniform data exists.
6. No destructive changes were made. No existing file was deleted, renamed,
   or had its public interface changed in a breaking way — verified by
   re-running the full existing test suite after every change (see
   completion report).
