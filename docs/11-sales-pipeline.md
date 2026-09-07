# Sales Pipeline

Structured data: `config/pipelines/sales-pipeline.json`. Code:
`src/pipeline/pipeline.js` (weighted pipeline value, loss-reason
enforcement). Owner: **Sales Director**.

## Stages (exact list from the brief)

Target Account → Contacted → Engaged → Discovery Booked → Discovery
Completed → Qualified → Demo Booked → Demo Completed → Proposal Sent →
Verbal Commitment → Payment Pending → Closed Won → Onboarding →
Implementation → Quality Assurance → Live → Expansion Opportunity →
Nurture → Closed Lost.

Note this single pipeline spans **sales AND fulfillment through Live** —
that's intentional: the brief's stage list keeps a deal visible end-to-end
from first contact through go-live, rather than handing it to a second,
disconnected system at Closed Won. `Onboarding` → `Live` mirrors (but does
not replace) the more granular onboarding state machine in
`docs/12-client-onboarding-system.md`; the pipeline stage is the
coarse-grained, sales-visible status, the state machine is the
fine-grained operational status.

## Stage probabilities (weighted pipeline value)

Each stage carries a default win-probability weight (`config/pipelines/sales-pipeline.json`)
used to compute **weighted pipeline value** = Σ(opportunity value × stage
probability) for the Executive Command Center. These are starting
assumptions — recalibrate from real Days 15–30 conversion data, not left
as permanent constants.

## Loss reasons (required, not optional)

`Closed Lost` is `requiresLossReason: true` in the pipeline config;
`src/pipeline/pipeline.js` throws if a `closed_lost` transition is
attempted without one. Suggested taxonomy (extend as real data comes in):
`price`, `timing`, `no_decision_authority`, `chose_competitor`,
`chose_diy`, `unresponsive`, `not_qualified`, `compliance_concern`, `other`.

## Routing

Opportunities route by industry (insurance / real estate / home services —
determines which industry pack demo/proposal is used), company size,
urgency, budget, and buying authority. Routing rules are sales-team
operating procedure, not hard-coded logic — this repo defines the *fields*
(`industry_tag` from the universal snapshot, plus a `company_size`,
`stated_urgency`, and `buying_authority_confirmed` opportunity field) that
routing decisions key off of, so the same data feeds both routing and the
Executive Command Center's "results by industry" report.

## Activity and conversion tracking

Every stage transition should be timestamped and attributed to a
salesperson and an acquisition source (outbound, inbound, referral,
webinar, partnership, database-reactivation) so
`docs/15-executive-command-center-spec.md`'s "results by salesperson" and
"results by acquisition source" views can be computed without a separate
tracking system.
