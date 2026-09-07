# Revenue OS — White-Label AI Revenue Operating System

Built on GoHighLevel (GHL). This repository is the productized expansion of the
C-Suite AI Agent System into a duplicatable, scalable, salable **Revenue
Operating System** — installed business infrastructure, not a generic CRM —
for insurance agencies, real estate teams, and home-services businesses, with
an architecture designed to expand into additional verticals later.

> **Operating target, not a guarantee.** The 90-day $1,037,050 combined figure
> throughout this repo is a modeled planning target for contracted revenue and
> cash collected. It is never to be presented to a prospect or client as a
> promised or guaranteed outcome. See `docs/21-risks-and-assumptions.md`.

> **Dry-run by default.** Every provisioning, billing, messaging, and
> publishing integration in `src/` defaults to dry-run mode and only logs
> intended actions. Nothing here creates a live GHL subaccount, charges a
> card, sends a real message, or publishes a page. Live activation requires
> explicit owner authorization (see `docs/17-credentials-and-ghl-ids.md`).

> **Pricing is configurable and unpublished.** Every number in
> `config/offers/offer-ladder.json` is a draft target range pending your
> approval — see `docs/03-offer-ladder.md`.

## Repository audit (start here)

`docs/00-audit-and-roadmap.md` — what existed before this work (a single
personal-brand static site with no CRM, agent, or GHL code), what this build
reuses, what it builds now, and what it deliberately postpones per the
"don't launch ten industries at once" rule.

## The 20 deliverables

| # | Deliverable | Location |
|---|---|---|
| 1 | Market-opportunity scorecard | `docs/01-market-opportunity-scorecard.md` |
| 2 | Final three-industry recommendation | `docs/02-industry-recommendation.md` |
| 3 | Complete offer ladder | `docs/03-offer-ladder.md`, `config/offers/offer-ladder.json` |
| 4 | 90-day financial model | `docs/04-financial-model.md`, `config/scenarios/90-day-revenue-scenarios.json`, `src/revenue/financialModel.js` |
| 5 | Universal snapshot specification | `docs/05-universal-snapshot-spec.md`, `config/snapshots/universal-core.json` |
| 6–8 | Three industry-pack specifications | `docs/06-…insurance.md`, `docs/07-…real-estate.md`, `docs/08-…home-services.md`, `config/snapshots/industry-pack-*.json` |
| 9 | SaaS provisioning architecture | `docs/09-saas-provisioning-architecture.md`, `src/provisioning/dryRunProvisioner.js` |
| 10 | Revenue-agent definitions | `docs/10-revenue-agent-definitions.md`, `config/agents/*.json` |
| 11 | Sales pipeline | `docs/11-sales-pipeline.md`, `config/pipelines/sales-pipeline.json`, `src/pipeline/pipeline.js` |
| 12 | Client onboarding system | `docs/12-client-onboarding-system.md`, `config/onboarding/state-machine.json`, `src/onboarding/stateMachine.js` |
| 13 | Fulfillment workflow | `docs/13-fulfillment-workflow.md` |
| 14 | Client-success workflow | `docs/14-client-success-workflow.md` |
| 15 | Executive command-center specification | `docs/15-executive-command-center-spec.md` |
| 16 | Sales assets | `docs/16-sales-assets.md`, `sales-assets/` |
| 17 | Tests | `tests/` (`npm test`) |
| 18 | Required credentials and GHL IDs | `docs/17-credentials-and-ghl-ids.md` |
| 19 | Deployment plan | `docs/18-deployment-plan.md` |
| 20 | 90-day implementation calendar | `docs/19-implementation-calendar.md` |
| — | Capacity and hiring requirements | `docs/20-capacity-and-hiring.md` |
| — | Risks and assumptions | `docs/21-risks-and-assumptions.md` |

## Code layout

```
config/          Data-as-config: agents, offer ladder, pipeline, onboarding
                 state machine, universal + industry snapshots, scenarios.
                 This is what gets duplicated per client/industry — never
                 hard-code client or industry specifics into src/.
src/revenue/     Financial model (3 scenarios), contracted-vs-collected
                 revenue ledger, profitability / margin-alert engine.
src/onboarding/  PAYMENT_RECEIVED → … → OPTIMIZATION state machine, plus
                 BLOCKED / PAUSED / CANCELED / REFUND_REVIEW / OFFBOARDED.
src/provisioning/ Dry-run SaaS provisioning workflow: snapshot selection,
                 subaccount creation (simulated), duplicate prevention,
                 tenant isolation, global pause, safe offboarding.
src/pipeline/    Sales pipeline stage list, weighted pipeline value,
                 loss-reason tracking.
src/agents/      AI usage limiter (guardrail against runaway AI cost).
src/permissions/ Role-based permission checks.
tests/           node:test coverage for every item in the "Required Tests"
                 list. Run with `npm test` (zero external dependencies).
```

## Running the tests

```
npm test
```

Uses Node's built-in test runner (Node ≥ 18) — no install step required.

## GHL snapshot boundary

Anything that **cannot** ship inside a GHL snapshot (custom API integrations,
AI conversation/voice agent connections, billing/SaaS Configurator setup,
DNS/domain work, A2P 10DLC registration, compliance sign-off) is called out
explicitly in `docs/09-saas-provisioning-architecture.md` and
`docs/17-credentials-and-ghl-ids.md` rather than silently assumed.
