# Universal Snapshot Specification

Owner: **Productization Director**. Structured data:
`config/snapshots/universal-core.json`.

## Purpose

Every client — regardless of industry — gets this layer. It is the
"missed-call recovery, basic nurture, reporting, attribution" backbone the
brief requires, and it is deliberately kept small: industry-specific
pipelines, workflows, forms, funnels, and AI prompts belong in the industry
pack (`docs/06–08`), never here. This prevents the "one oversized snapshot
that is difficult to maintain" failure mode the brief explicitly warns
against.

## Components (all native to a GHL snapshot)

1. **Contact structure** — standard custom fields and tags for lead
   source, campaign, industry tag, referral source, and compliance-consent
   timestamp (the latter is required before any AI/voice outreach touches
   the contact — see `docs/06-industry-pack-insurance.md` compliance
   controls for the strictest version of this rule).
2. **Opportunity framework** — a minimal universal pipeline
   (`New Inquiry → Contacted → Qualified → Booked → Won/Lost`) used only
   until the industry pipeline (`docs/11-sales-pipeline.md` is the
   *internal sales* pipeline; each industry pack ships its own *client-
   facing* pipeline, e.g., Buyer/Seller/Investor for real estate) is
   applied.
3. **Calendar framework** — a general consultation calendar and a
   round-robin team-availability pool, extended per industry.
4. **Missed-call recovery** — instant SMS text-back plus voicemail
   transcription/task on every missed inbound call. This is the single
   highest-ROI universal component per the brief's positioning
   ("Recover missed calls").
5. **Basic nurture** — 14-day SMS/email sequence for any contact not yet
   booked.
6. **Appointment reminders** — 24-hour and 2-hour reminders, SMS + email.
7. **No-show follow-up** — automatic reschedule sequence on a no-show
   status.
8. **Review requests** — triggered 24 hours after an opportunity is marked
   Won, to Google and Facebook.
9. **Reporting fields** — time-to-first-response, show rate, source,
   assigned user — the minimum fields the Executive Command Center needs
   from every subaccount regardless of industry.
10. **Attribution fields** — UTM + referral-partner-ID, standardized so
    cross-industry rollup reporting works without per-client mapping.
11. **Support workflow** — a `support-request` tag routes into the support
    pipeline and notifies the Client Success and Retention Director.

## What this layer explicitly does NOT include

Industry pipelines, industry-specific workflows/forms/funnels, AI
conversation prompts, industry knowledge bases, industry dashboards, and
compliance disclosures are all industry-pack-layer (see `docs/06-08`) or
client-configuration-layer (see the client-configuration section of each
industry-pack doc), never universal-core.

## What cannot ship inside any GHL snapshot

Listed explicitly in `config/snapshots/universal-core.json` →
`cannotShipInSnapshot`: AI Conversation Agent live connections, Voice AI
telephony connections, A2P 10DLC registration, SaaS Configurator billing
attachment, custom domain/DNS, and reputation-platform API keys. These are
per-subaccount, credential-bearing configuration steps handled by
`docs/09-saas-provisioning-architecture.md`'s `CONFIGURATION` and
`INTEGRATION_TESTING` onboarding states — never assumed to travel with the
snapshot import itself.

## Versioning

`version` field follows semver. A breaking change to any universal
component (e.g., renaming a custom field every downstream workflow
depends on) is a major version bump and requires a migration note in this
file before it ships to any existing client.
