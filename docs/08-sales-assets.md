# 08 — Sales Assets (templates, not final copy)

These are structural templates for the Sales Director agent's workflows to
populate — not final marketing/legal copy, and not published anywhere.
**Legal agreement language must be attorney-reviewed before use** (per
operating rules); nothing below is a legal agreement.

## Discovery call script (outline)

1. Context: business type, team size, current lead-response process.
2. Pain confirmation: missed calls/leads last week? average speed-to-lead?
   current no-show rate? current review count/velocity?
3. Cost of inaction: estimate $ value of leads lost to slow response using
   the ROI calculator below.
4. Qualify: budget authority, timeline, decision process.
5. Book: demo, naming the specific industry pack that fits.

## Qualification form (fields)

`company_name, industry, monthly_lead_volume, current_crm, current_response_time_minutes, missed_call_volume_per_month, average_deal_value, decision_maker_confirmed (bool), budget_range, timeline_to_start`

## ROI calculator (formula, mirrors `ClientProfitability` inputs)

```
leads_recovered_per_month = missed_call_volume_per_month * recovery_rate_assumption
recovered_revenue_per_month = leads_recovered_per_month * close_rate_assumption * average_deal_value
```
`recovery_rate_assumption` and `close_rate_assumption` must be sourced from
the client's own numbers or clearly labeled as an industry benchmark
assumption — never presented as guaranteed.

## Proposal template (sections)

Problem summary → recommended tier (from the offer ladder) → what's
included (pulled from the tier's `includes` list) → implementation timeline
→ pricing (owner-approved numbers only) → next steps.

## Objection-handling library (categories, not scripts)

Price, "we already have a CRM," "we tried AI before and it felt robotic,"
compliance concerns (route to the relevant industry pack's disclosures),
"we need to think about it" (nurture sequence trigger).

## Onboarding checklist (mirrors the onboarding state machine)

Maps 1:1 to `config/onboarding_states.json`'s primary path — see docs/06.
No separate checklist format is used, so the sales asset and the system's
actual tracked state can never drift apart.

## Case-study framework

Problem → system deployed → measurable before/after (speed-to-lead,
show rate, review count, revenue attribution) → **testimonial only with
explicit written permission and compliance sign-off**
(`ClientSuccessRetentionDirectorAgent` enforces this gate in code, not just
policy — see `src/csuite/agents/revenue/client_success_retention_director.py`).

## Webinar / referral-partner assets

Structural outlines only (audience → problem → 3 proof points → offer →
CTA for webinar; partner value prop → commission structure → co-marketing
assets for referral). Final copy requires owner/marketing sign-off.
