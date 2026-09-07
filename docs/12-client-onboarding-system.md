# Client Onboarding System

Structured data: `config/onboarding/state-machine.json`. Code:
`src/onboarding/stateMachine.js`. Owner: **Client Onboarding Director**.

## Main sequence (exact list from the brief)

`PAYMENT_RECEIVED → AGREEMENT_CONFIRMED → INTAKE_SENT → INTAKE_COMPLETED →
CREDENTIALS_PENDING → SNAPSHOT_SELECTED → SUBACCOUNT_CREATED →
SNAPSHOT_APPLIED → CONFIGURATION → INTEGRATION_TESTING → CLIENT_REVIEW →
LAUNCH_APPROVED → LIVE → OPTIMIZATION`

## Exception states (reachable from any main-sequence state)

`BLOCKED`, `PAUSED`, `CANCELED`, `REFUND_REVIEW`, `OFFBOARDED`. `CANCELED`
and `OFFBOARDED` are terminal; `BLOCKED` and `PAUSED` allow re-entry back
into the main sequence at the state they left from.

## Gating rule: compliance before launch

`LAUNCH_APPROVED` cannot be reached until the assigned industry pack's
`complianceReviewControls.requiredBeforeLaunch` checklist is fully
satisfied (see `docs/06-08` industry-pack docs). This is enforced in code
(`src/onboarding/stateMachine.js`), not left as a documentation-only rule.

## What each state validates

| State | Validates |
|---|---|
| `AGREEMENT_CONFIRMED` | Signed agreement on file (attorney-reviewed template, per `docs/16-sales-assets.md`) |
| `INTAKE_COMPLETED` | Domain, phone numbers, calendars, branding, offers, disclosures, integrations, escalation contacts all captured |
| `SNAPSHOT_SELECTED` | Industry tag matches an existing `config/snapshots/industry-pack-*.json` |
| `SUBACCOUNT_CREATED` | No duplicate subaccount for this client (domain + email check) |
| `SNAPSHOT_APPLIED` | Universal core applied before industry pack; failure routes to `BLOCKED` |
| `CONFIGURATION` | All client-configuration-layer fields present (branding, domain, numbers, users, services, service areas, pricing, disclosures, integrations, escalation contacts) |
| `INTEGRATION_TESTING` | AI/voice connections, billing plan attachment, and any custom integrations pass QA |
| `CLIENT_REVIEW` | Client has reviewed the live-in-staging system and industry compliance checklist is complete |
| `LAUNCH_APPROVED` | Explicit client sign-off recorded |
| `LIVE` | System is active; time-to-launch metric closes here |
| `OPTIMIZATION` | Ongoing — this is where Client Success and Retention Director activity begins |

## Time-to-launch measurement

`PAYMENT_RECEIVED` timestamp to `LIVE` timestamp = time-to-launch, tracked
per client and rolled up by industry and snapshot version in the Revenue
Operations Analyst's reporting (`docs/15-executive-command-center-spec.md`).

## Safe offboarding

`OFFBOARDED` always follows the sequence: disable billing → export client
data → revoke access → archive subaccount reference. Never deletes client
data as the first action. See `src/provisioning/dryRunProvisioner.js`.
