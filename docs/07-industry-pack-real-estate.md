# Industry Pack: Real Estate Revenue OS

Structured data: `config/snapshots/industry-pack-real-estate.json`
(extends `universal-core`).

## Problems this pack solves

Slow response to internet leads, missed calls, leads receiving generic
follow-up, long sales cycles, database neglect, inconsistent showing
follow-up, weak seller nurture, poor referral generation.

## Components

- **Three pipelines**: Buyer, Seller, Investor — each with its own stage
  set because the sales motion differs (showings vs. listing appointments
  vs. deal underwriting).
- **Speed-to-lead engine**: missed-call text-back, AI lead qualification,
  Voice AI, showing calendar and showing follow-up — this is the single
  highest-leverage component for real estate, since internet leads are
  famously time-decayed (response-time competitiveness is the core sales
  pitch for this pack).
- **Long-term nurture + database reactivation**: solves "database neglect"
  — the brief's named problem — by treating the agent's existing contact
  database as an active revenue asset, not a static list.
- **Home-valuation funnel**: seller lead generation.
- **Post-closing follow-up + review/referral workflow**: solves "poor
  referral generation" — real estate has the highest referral-potential
  score in the market scorecard (`docs/01-market-opportunity-scorecard.md`),
  so this workflow is not optional.
- **Open-house workflow**: sign-in form → funnel → buyer pipeline.
- **iDecide presentations**: buyer and seller presentations always
  included; an agent-recruiting presentation is available where a team or
  brokerage wants to use it to recruit agents, not just close deals.

## Compliance review controls (gating)

Before `LAUNCH_APPROVED`: Fair Housing Act–compliant language confirmed
across all funnels/forms/AI prompts, TCPA consent present on every lead
form, and the client's state agency-disclosure requirement confirmed. Real
estate's compliance burden is lighter than insurance's but is still gating
— see `docs/12-client-onboarding-system.md`.

## What requires client-supplied content (never assumed)

Local MLS/market data and financing/pre-approval details must be
client-supplied and kept current by the client; this pack's AI agents are
scoped to lead qualification and appointment booking, not lending advice.
