# Industry Pack: Insurance Agency Revenue OS

Structured data: `config/snapshots/industry-pack-insurance.json` (extends
`universal-core`).

## Problems this pack solves

Slow lead response, inconsistent recruiting, unlicensed-recruit follow-up,
licensed-agent attraction, missed appointments, inactive-agent
reactivation, poor onboarding, inconsistent training, lead leakage, weak
client follow-up, lack of pipeline visibility.

## Components

- **Three pipelines**: Licensed Agent Recruiting, Licensing-Interest
  (unlicensed recruits), and Consumer Financial Education — kept separate
  because they have different buyers, cycle lengths, and compliance
  profiles.
- **Recruiting engine**: licensed-agent recruiting funnel, licensing-
  interest funnel, career presentation, iDecide recruiting presentation,
  interview calendar, AI recruiting conversation agent, Voice AI recruiting
  agent, candidate scoring, interview reminders + no-show recovery,
  licensing follow-up, contracting workflow, agent onboarding, training
  delivery, inactive-agent reactivation.
- **Activity dashboard**: recruiting-activity and agent-production
  dashboards for the agency principal.
- **Consumer financial-education funnel**: separate from recruiting, for
  the agency's own policy-sales lead flow.

## Compliance review controls (gating)

This is the pack with the heaviest compliance load in Phase 1. Before an
insurance client reaches `LAUNCH_APPROVED` in the onboarding state machine,
the `CLIENT_REVIEW` state must confirm:

1. TCPA consent language present on every intake form.
2. State-specific insurance recruiting/licensing disclosure language
   reviewed by the client's own compliance or legal contact (this repo
   never drafts that language — it flags where it belongs).
3. AI conversation and voice agent scripts contain no guaranteed-income or
   guaranteed-commission-rate claims.
4. E&O and active-licensing-status verification is part of the contracting
   workflow before an agent is marked Active.

No insurance client is provisioned past `CLIENT_REVIEW` without this
checklist signed off — see `src/provisioning/dryRunProvisioner.js` and
`docs/12-client-onboarding-system.md`.

## Candidate scoring (model outline)

Score each recruiting candidate 1–5 on: licensing status, prior insurance
experience, geographic fit to agency's book, stated income goal alignment,
and responsiveness during the recruiting conversation. This scoring model
lives in the AI recruiting conversation agent's prompt
(`config/ai-prompts/insurance-recruiting-conversation-agent.md` —
placeholder path; full prompt engineering is fulfillment-phase work, see
`docs/13-fulfillment-workflow.md`).

## Live pilot: Open Doors Financial Group, LLC

This pack's first real build is underway directly in GHL (Location ID
`62DWBpRjrgKxACPpgIsQ`), independent of this repo's dry-run provisioner —
28 workflows across 9 folders (`00 SYSTEM` … `80 LEADERSHIP`), 7 published
as of the last status report. Workflow IDs follow a
`<FOLDER-PREFIX>-<sequence>` convention (`SYS-001`, `REC-001`, `LIC-002`,
…) that `config/snapshots/industry-pack-insurance.json`'s `workflows` list
should be reconciled against once all 9 folders are enumerated — see
`config/live-pilots/odfg-ghl-workflow-status.json` for the live tracker and
`docs/09-saas-provisioning-architecture.md` for the platform-gap
workarounds this build has already surfaced (these apply to every future
client, any industry). Until reconciled, treat the `workflows` array in
this pack's snapshot config as the target design and the tracker JSON as
the as-built reality.

## What requires client-supplied content (never assumed)

Compensation/commission structure, carrier appointments offered, and
state-by-state licensing requirements must come from the client — this
pack ships the *structure* (forms, workflows, knowledge-base topic list),
never invented compliance or compensation facts.
