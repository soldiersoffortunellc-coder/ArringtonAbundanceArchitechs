# Required Credentials and GHL IDs

Owner: **Client Onboarding Director**. This is a checklist of what must
exist before any live (non-dry-run) provisioning happens — no credential
is stored in this repo.

## Agency-level (one-time)

- GHL Agency account (white-label branding configured)
- SaaS Configurator enabled on the agency account
- Twilio (or GHL-native telephony) account for number provisioning
- A2P 10DLC brand registration at the agency level
- AI Conversation Agent vendor account + API key (vendor TBD — not
  selected in this phase)
- Voice AI vendor account + API key (vendor TBD — not selected in this
  phase)
- Domain/DNS access for the parent white-label domain
- Payment processor (Stripe or GHL-native) connected to SaaS Configurator
- Reputation-management platform API access (Google Business Profile,
  Facebook) — agency-level app credentials where applicable

## Per-client (collected during `INTAKE_COMPLETED` → `CREDENTIALS_PENDING`)

- Business legal name, address, branding assets
- Domain access or DNS delegation
- Phone number (new provision or port authorization)
- Email sending domain access
- Calendar/staff availability
- Compliance/legal contact (required for insurance and real estate)
- Financing partner details (home services, if applicable)
- Escalation contact

See the client-facing version: `sales-assets/onboarding-checklist.md`.

## GHL IDs to track per client (populated at provisioning time, not here)

`locationId` (subaccount), `snapshotId` applied, `pipelineIds`,
`calendarIds`, `customFieldIds`, `workflowIds`, `userIds`. Tracked in the
provisioning action log (`src/provisioning/dryRunProvisioner.js`), never
hard-coded into `config/snapshots/`.

## Live pilot in progress: Open Doors Financial Group, LLC

The first real (non-dry-run, built directly in GHL) client build is
underway for the Insurance Agency Revenue OS:

- **Client:** Open Doors Financial Group, LLC
- **GHL Location ID:** `62DWBpRjrgKxACPpgIsQ`
- **Build tracker:** `config/live-pilots/odfg-ghl-workflow-status.json`
  (28 workflows across 9 folders, 7 published as of the last status
  report — update this file as further status reports arrive)
- **Platform gaps discovered:** see
  `docs/09-saas-provisioning-architecture.md` → "Platform gaps observed in
  the live pilot" — these apply to every future client build, not just
  this one, and should be treated as standing operating guidance for
  whoever builds the next subaccount by hand until a live API adapter
  exists.

This pilot is the first real signal on actual implementation time and
fulfillment cost (`docs/13-fulfillment-workflow.md`,
`docs/20-capacity-and-hiring.md`) — once it's complete, replace the
estimated figures in those docs with its actuals.

## Authorization gate

None of the agency-level or per-client credentials above are to be
activated for live billing, live messaging, or live publishing without
explicit owner authorization, per the brief's dry-run-by-default rule.
The Open Doors pilot is being built directly in the live GHL UI by a
separate build session and is therefore outside this repo's dry-run
guardrail by construction — treat its workflow-by-workflow published
status as the source of truth for that one subaccount, not this repo's
`src/provisioning/dryRunProvisioner.js` action log.
