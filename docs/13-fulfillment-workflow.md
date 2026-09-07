# Fulfillment Workflow

Owner: **Client Onboarding Director**, supported by **Productization
Director** for snapshot content.

## Scope

Fulfillment is everything between `Closed Won` (sales pipeline) and `Live`
(onboarding state machine) — it is the operational execution of the
onboarding state machine, staffed and checklisted.

## Fulfillment checklist (per client)

1. Confirm signed agreement and payment (`AGREEMENT_CONFIRMED`).
2. Send intake form; chase to completion (`INTAKE_SENT` → `INTAKE_COMPLETED`).
3. Collect credentials: domain access/DNS, phone number ownership or
   porting authorization, calendar/email access, branding assets
   (`CREDENTIALS_PENDING`).
4. Confirm industry snapshot selection matches the sold offer
   (`SNAPSHOT_SELECTED`).
5. Create subaccount (dry-run in this repo; live once authorized) and
   check for duplicates (`SUBACCOUNT_CREATED`).
6. Apply universal core, then the industry pack
   (`SNAPSHOT_APPLIED`).
7. Configure client-specific layer: branding, domain, numbers, users,
   services, service areas, pricing, disclosures, integrations, escalation
   contacts (`CONFIGURATION`).
8. Connect AI Conversation Agent, Voice AI, billing plan, and any custom
   integrations; run through the QA test list below
   (`INTEGRATION_TESTING`).
9. Walk the client through their system live; confirm industry compliance
   checklist (`CLIENT_REVIEW`).
10. Obtain explicit launch sign-off (`LAUNCH_APPROVED`).
11. Flip to live, notify the client, start usage monitoring (`LIVE`).
12. Hand off to Client Success and Retention Director for `OPTIMIZATION`.

## Quality-assurance test list (before `CLIENT_REVIEW` closes)

- Missed-call recovery fires a test SMS within the SLA.
- Every calendar books and reminders send.
- Every form submits and creates a contact with correct tags/fields.
- Every workflow in the applied industry pack fires without error on a
  test contact.
- AI Conversation Agent responds appropriately to 3–5 scripted test
  scenarios per industry, including at least one out-of-scope/escalation
  scenario.
- Voice AI answers a test call and routes correctly (emergency routing for
  home services, interview booking for insurance recruiting, showing
  booking for real estate).
- Reporting fields populate correctly on a test transaction.
- Compliance checklist for the assigned industry pack is 100% complete.

## Implementation time and cost tracking

Productization Director estimates and the Client Onboarding Director
records actual labor hours per fulfillment stage, per client, per
snapshot version — this feeds `src/revenue/profitability.js` (fulfillment
cost input) and the "implementation time" line in
`docs/20-capacity-and-hiring.md`.
