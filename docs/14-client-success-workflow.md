# Client Success and Retention Workflow

Owner: **Client Success and Retention Director**.

## Monitoring (continuous, from `LIVE`/`OPTIMIZATION` onward)

Track per client: appointment volume trend, login/usage frequency, failed
automation count, support ticket volume, invoice/payment status, and
margin status (from `src/revenue/profitability.js`).

## Risk signals → interventions (not silent)

| Signal | Threshold (default, configurable) | Intervention |
|---|---|---|
| Appointment volume decline | ≥ 25% drop vs. trailing 30-day average | Success call scheduled within 3 business days |
| Login frequency decline | No login in 14 days | Automated check-in + task for success rep |
| Failed automation count | ≥ 3 failures in 7 days | Technical review ticket, client notified |
| Support ticket volume spike | ≥ 2× trailing average | Escalation to Client Onboarding Director for root-cause |
| Invoice overdue | > 15 days | Finance/CRO notified; do not auto-suspend without CRO approval |

Every triggered intervention is logged, not just displayed as a dashboard
color — see `config/agents/client-success-retention-director.json`
`hardConstraints`.

## Executive reporting

Deliver a recurring (monthly, minimum) executive report per client showing
their own results: leads handled, appointments booked, show rate,
missed-calls recovered, reviews generated, and — where applicable —
recruiting/production numbers. This is the client-facing proof of the
"installed business infrastructure" value proposition, not just an
internal metric.

## Expansion and renewal

Expansion candidates (upsell to the next offer tier, add a location/user,
add an industry-pack feature) are identified from usage data and routed to
the Sales Director as `Expansion Opportunity` pipeline entries — this
closes the loop from `docs/11-sales-pipeline.md`.

## Testimonials and referrals

Never use a client testimonial or case study without (1) documented client
permission and (2) compliance approval (critical for insurance and real
estate given Fair Housing / TCPA / licensing constraints). Referral
requests are made only after a client shows a positive health signal
(no active risk flags) for at least one full billing cycle.

## Churn handling

A client requesting cancellation routes into `PAUSED` (if temporary) or
`CANCELED`/`REFUND_REVIEW` (if terminating) in the onboarding state
machine — never straight deletion. Churn reasons are captured with the
same rigor as sales loss reasons (`docs/11-sales-pipeline.md`) and rolled
up by industry and snapshot version for the Revenue Operations Analyst.
