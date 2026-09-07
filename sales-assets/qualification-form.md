# Qualification Form

Fields (map to CRM opportunity/contact custom fields):

| Field | Type | Used for |
|---|---|---|
| Business name | text | Record |
| Industry | select: insurance / real-estate / home-services / other | Snapshot routing |
| Sub-vertical (home services only) | select | Industry-pack context |
| Number of leads/calls per week | number | ROI calculator input, deal sizing |
| Average ticket / commission / production value | currency | ROI calculator input |
| Current CRM/software in use | text | Migration/integration scoping |
| Number of staff/agents | number | Tier sizing (Starter vs. Growth vs. full OS vs. Enterprise) |
| Number of locations | number | Enterprise/Agency License routing |
| Stated urgency | select: fix now / this quarter / exploring | Pipeline stage-probability weighting |
| Decision-maker confirmed | boolean | `buying_authority_confirmed` field for routing |
| Budget range (self-reported, optional) | text | Sales Director qualification only, never quoted back verbatim |
| Compliance contact available? (insurance/real estate) | boolean | Onboarding `CLIENT_REVIEW` planning |
| Referral source | text | Attribution / acquisition-source reporting |

## Qualification threshold (routing rule)

- **Not yet qualified** → Nurture pipeline stage, added to long-term
  nurture sequence.
- **Qualified, no confirmed decision-maker** → Discovery Booked, but flag
  for a multi-threaded follow-up.
- **Qualified, decision-maker confirmed, urgency = fix now** → fast-track
  to Demo Booked.
