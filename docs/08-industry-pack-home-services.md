# Industry Pack: Home-Services Revenue OS

Structured data: `config/snapshots/industry-pack-home-services.json`
(extends `universal-core`). Covers the initial sub-verticals: HVAC,
plumbing, roofing, electrical, general contracting, remodeling,
restoration — one pack, shared structure, because these trades share
near-identical revenue workflows (this is the highest "repeatability"
score in the market scorecard).

## Problems this pack solves

Missed calls, slow estimate response, unqualified leads, unscheduled
estimates, unsold estimates, missed appointments, weak review generation,
no maintenance reminders, no customer reactivation.

## Components

- **Two pipelines**: Service Request (call → estimate → sold → job →
  invoiced → paid) and Maintenance Plan (recurring service enrollment) —
  separated because maintenance-plan revenue is a distinct, recurring
  revenue stream from one-off service jobs.
- **AI receptionist + Voice AI qualification**: answers and qualifies
  every inbound call/text, including after-hours.
- **Emergency-service routing**: triages true emergencies (e.g., no heat
  in winter, active leak) to immediate dispatch vs. standard scheduling —
  the client supplies the triage rules (see below).
- **Estimate calendar + estimate-reminder workflow + unsold-estimate
  follow-up**: directly targets the brief's named "unscheduled estimates"
  and "unsold estimates" leakage points.
- **Financing-interest capture**: routes to the client's licensed
  financing partner only — this system never performs in-house credit
  decisioning.
- **Job-status communication**: keeps the customer informed job → invoice
  → paid, reducing inbound "where's my technician" support load.
- **Review-generation workflow, seasonal service campaigns, maintenance
  reminders, customer reactivation**: the recurring-revenue and retention
  engine — home services scored highest on retention potential in the
  market scorecard precisely because of this component set.
- **Service-area qualification**: leads outside the client's service
  radius are politely declined or routed to a referral-partner network
  rather than wasting the client's estimate capacity.
- **Revenue attribution**: every closed job traced back to lead source for
  marketing-spend ROI reporting.

## Compliance review controls (gating)

Before `LAUNCH_APPROVED`: contractor license number confirmed and
displayed per local requirement, TCPA consent present on all intake forms,
and financing-interest capture confirmed to route only to a licensed
financing partner.

## What requires client-supplied content (never assumed)

Service-area boundaries, emergency-vs-standard triage rules, financing
partner options, and the seasonal service calendar are all client-supplied
— the pack ships the workflow structure that consumes that data, not the
data itself.
