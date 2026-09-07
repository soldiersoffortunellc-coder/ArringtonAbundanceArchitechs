# Repository Audit & Build Roadmap

## What existed before this task

The repository (`soldiersoffortunellc-coder/arringtonabundancearchitechs`)
contained a single commit ("Add files via upload") holding one file:
`abundance-architects-site.zip`, which unpacks to a 3-file static personal
brand page:

- `index.html` — "Arrington Abundance Architects", pillars: Faith, Finance,
  Fitness, Real Estate, Lifestyle & Travel.
- `styles.css` — basic styling.
- `assets/logo.png` — logo image.

**There was no C-Suite AI Agent System code, no GHL integration, no CRM
schema, no agent definitions, no pipeline, no onboarding logic, and no
tests anywhere in this repository.** The "C-Suite AI Agent System" referenced
in the brief exists as a business/operating concept the owner is running
(agent roles, org design) rather than as code checked into this repo. This
build treats that concept as the starting org chart and productizes it.

## What this build reuses

- The brand name/positioning language ("Arrington Abundance Architects") is
  preserved as the parent brand in `docs/17-credentials-and-ghl-ids.md` and
  `docs/18-deployment-plan.md` as the default white-label identity, subject
  to the owner's confirmation — nothing about the existing static site is
  modified or removed.
- Nothing else was reusable: no data model, no automation, no dashboard.

## What this build creates now (Phase 1: universal core + 3 priority industries)

Per the brief's own rule — *"Begin with insurance, real estate and home
services. Do not attempt to launch ten industries at once."* — this build
delivers:

1. The **Chief Revenue Officer** division and its 6 subordinate agents, as
   structured, versioned config (`config/agents/`), not prose only.
2. The **universal snapshot spec** (industry-agnostic core every client
   gets) and **three industry-pack specs** (insurance, real estate,
   home-services), kept as separate layered documents/config per the
   "don't build one oversized snapshot" rule.
3. A working, tested **revenue engine**: 90-day 3-scenario financial model,
   contracted-vs-collected revenue ledger, profitability/margin-alert
   calculator.
4. A working, tested **onboarding state machine** matching the exact state
   list in the brief, plus the 5 exception states.
5. A working, tested **dry-run SaaS provisioning workflow** — snapshot
   selection, simulated subaccount creation, duplicate-account prevention,
   tenant isolation, global pause, safe offboarding. No live GHL account,
   billing event, or message send is ever triggered by this code.
6. The **sales pipeline** (exact 19 stages from the brief) with loss-reason
   capture and weighted-pipeline-value math.
7. **Sales assets** as editable templates (offer sheets, scripts, ROI
   calculator, proposal template, onboarding checklist, objection library,
   follow-up sequences, referral campaign, webinar outline, case-study
   framework) — legal agreement *requirements* only, not a drafted
   agreement (attorney review required before any agreement is published).
8. The **executive command-center specification** and the metric set it
   must render, wired to the same revenue engine.
9. **Deployment plan, 90-day calendar, capacity/hiring plan, and risks &
   assumptions** documents.

## What this build explicitly postpones

- The 11 secondary industries (mortgage, med spa, dental, law, accounting,
  fitness, coaching, property management, nonprofit, veteran-service,
  sober-living/transitional-housing). The architecture (`config/snapshots/`
  layering: universal core → industry pack → client config) is designed so
  a 4th+ industry pack is additive, but no secondary pack is built in this
  phase. See `docs/02-industry-recommendation.md`.
- Live GHL API integration (real subaccount creation, real SaaS Configurator
  billing, real A2P 10DLC/number provisioning, real AI voice/telephony
  vendor wiring). These require live credentials, a live GHL agency
  account, and your explicit authorization — none of which exist in this
  session. `src/provisioning/dryRunProvisioner.js` is the adapter interface
  a live GHL adapter plugs into later without changing calling code.
- Any published pricing (offer ladder values are drafts pending your
  approval — see `docs/03-offer-ladder.md`) and any drafted legal agreement
  (requires attorney review — see `docs/16-sales-assets.md`).
- AI Conversation/Voice Agent prompt content beyond the industry
  knowledge-base *outlines* captured in each industry-pack spec — full
  prompt engineering and voice-agent scripting is downstream fulfillment
  work, tracked in `docs/13-fulfillment-workflow.md`.

## Build vs. buy inside GHL

GHL natively provides: subaccounts, snapshots, pipelines, calendars, forms,
funnels, workflows, SaaS Configurator/billing, reputation management,
conversation AI, and reporting widgets. This repo does **not** reimplement
any of those — it specifies how to configure them (snapshots/pipelines as
data) and provides the orchestration/guardrail logic GHL does not offer out
of the box: cross-account revenue rollups with contracted-vs-collected
separation, margin-alert flagging, onboarding SLA tracking, and dry-run
provisioning safety rails.
