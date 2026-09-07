# SaaS Provisioning Architecture

Owner: **Client Onboarding Director**. Code: `src/provisioning/dryRunProvisioner.js`.

## Workflow (matches the brief exactly)

Plan purchase → Payment confirmation → Subaccount creation → Correct
snapshot selection → Snapshot application → User creation → Welcome email
→ Intake form → Onboarding task creation → Credential collection →
Quality-assurance testing → Client approval → Launch → Billing and usage
monitoring.

## Design: adapter pattern, dry-run by default

`dryRunProvisioner.js` exposes a `Provisioner` that takes an **adapter**
object with methods (`createSubaccount`, `applySnapshot`, `createUser`,
`sendWelcomeEmail`, `attachBillingPlan`). The default adapter
(`dryRunAdapter`) logs every call to an in-memory action log and returns a
simulated success — **no live GHL API call is ever made by this repo**. A
real `GhlApiAdapter` can be dropped in later without changing the
provisioning logic, satisfying "use the supported GHL SaaS Configurator and
snapshot functionality where possible" while satisfying "do not automate
live account creation or billing during development."

## Guardrails implemented in code (and tested)

- **Duplicate account prevention** — before creating a subaccount, the
  provisioner checks an existing-accounts index by domain + client email;
  a duplicate request is rejected, not silently re-run.
- **Tenant isolation** — every provisioned account gets a unique
  `subaccountId` namespace; no shared mutable state crosses tenant
  boundaries in the action log or generated config.
- **Snapshot assignment correctness** — the provisioner refuses to apply an
  industry snapshot that doesn't match the client's declared industry, and
  refuses to proceed without the universal-core layer applied first.
- **Missing configuration detection** — required client-configuration
  fields (domain, phone number, calendar, disclosures, escalation contact)
  are validated before `CONFIGURATION` is marked complete; missing fields
  push the client into `BLOCKED`, not silently forward.
- **Failed snapshot application handling** — a simulated snapshot-apply
  failure moves the client to `BLOCKED` with a reason, never leaves it in
  an ambiguous state.
- **Global pause** — a single flag (`globalPause`) halts all provisioning
  actions across every tenant immediately; used for "stop everything" if
  a defect or compliance issue is discovered mid-rollout.
- **Safe offboarding** — a documented sequence (disable billing → export
  client data → revoke access → archive subaccount reference) that never
  deletes client data as its first step.

## What GHL provides natively vs. what this repo adds

| Capability | Source |
|---|---|
| Subaccount creation, snapshot import, SaaS Configurator billing plans | GHL native |
| Snapshot content (pipelines, workflows, forms) | This repo's `config/snapshots/` |
| Cross-tenant duplicate prevention, tenant-isolation checks, global pause, safe-offboarding sequencing | This repo's `src/provisioning/` (GHL has no native equivalent) |
| Time-to-launch measurement, onboarding-state gating on compliance controls | This repo's `src/onboarding/` |

## Platform gaps observed in the live pilot (Open Doors Financial Group)

The insurance pack's first live build (`config/live-pilots/odfg-ghl-workflow-status.json`,
GHL Location ID `62DWBpRjrgKxACPpgIsQ`) surfaced real GHL platform
limitations, not hypothetical ones. These apply to every future client in
any industry, not just this pilot, so they are recorded here as standing
build guidance rather than left buried in one client's build log:

| Gap | Workaround |
|---|---|
| No staff/users configured yet | Substitute Create Task/Assign User with an Internal Notification (all users, redirect to contact); upgrade to real assigned tasks once staff exist |
| No calendars configured yet | Defer any "Customer booked appointment" trigger's calendar filter until calendars exist |
| No native Filter action / custom-object-change trigger | Use If/Else gates + tag-based conditions |
| No native "Custom Field Changed" trigger | Use "Contact changed" trigger filtered to the specific field |
| Wait action's hours field caps/misbehaves above 23 | Use the days field for exact offsets (3 days = 72h) |
| No native Goal / field-based exit condition | Gate every remaining send step in the sequence with an If/Else checking the outcome field, route to END if already set — proven in LIC-002 |
| Missing custom fields needed as typed values | Create the real typed field (e.g. Date-picker) directly rather than a tag/text workaround |

Full detail and status per gap: `config/live-pilots/odfg-ghl-workflow-status.json`.
This file is meant to be updated as further live-build status reports come
in — treat it as the running log a real GHL build produces that the
dry-run provisioner and industry-pack specs should absorb over time.

## Cannot be included in a GHL snapshot (requires API/manual/external config)

Per-subaccount AI Conversation Agent and Voice AI connections, A2P 10DLC
registration, SaaS Configurator billing-plan attachment, custom domain/DNS,
and reputation-platform API keys — see each snapshot's
`cannotShipInSnapshot` field. These are handled in the `CONFIGURATION` and
`INTEGRATION_TESTING` onboarding states, tracked per-client, never assumed
to arrive "for free" with the snapshot import.
