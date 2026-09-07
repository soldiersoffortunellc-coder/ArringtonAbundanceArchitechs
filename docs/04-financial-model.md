# 90-Day Financial Model

Owner: **Revenue Operations Analyst**, reviewed by CRO. Structured data:
`config/scenarios/90-day-revenue-scenarios.json`. Computed by
`src/revenue/financialModel.js` (tested in `tests/financialModel.test.js`).

> **This is an operating planning target, not a promised or guaranteed
> outcome.** Never present these figures to a prospect, lender, or partner
> as guaranteed revenue.

## Three scenarios

| Scenario | Premium implementation clients | Standardized SaaS clients | Modeled 90-day value |
|---|---:|---:|---:|
| Conservative (0.5×) | 13 | 25 | ≈ $533,775 |
| **Target (1.0×)** | **25** | **50** | **$1,037,050** |
| Aggressive (1.5×) | 38 | 75 | ≈ $1,570,825 |

## Target scenario detail (matches the brief exactly)

**Premium implementations** (AI Revenue Operating System tier):
25 clients × $20,000 setup = $500,000, plus 25 × $3,500/mo × 3 months =
$262,500 → **$762,500**.

**Standardized SaaS clients** (Starter SaaS tier, $2,500-setup variant):
50 clients × $2,500 setup = $125,000, plus 50 × $997/mo × 3 months =
$149,550 → **$274,550**.

**Combined modeled 90-day target: $1,037,050.**

Conservative and aggressive scenarios scale **client counts**, not the
per-client economics, at 0.5× and 1.5× the target client counts
respectively — this is a volume/execution-capacity assumption, not a price
change. Adjust the multipliers in the config file as real Days 15–30
validation data comes in.

## Metrics tracked separately (never combined into one number)

Per the rule *"Never combine contracted revenue and collected revenue into
one misleading number,"* `src/revenue/revenueLedger.js` tracks these as
distinct, separately reportable figures:

| Metric | Definition |
|---|---|
| Contracted revenue | Total value of signed agreements (setup + committed recurring term) |
| Invoiced revenue | Amount actually invoiced to date |
| Cash collected | Amount actually received to date |
| Monthly recurring revenue (MRR) | Sum of active monthly subscription value |
| Accounts receivable | Invoiced − collected |
| Refunds | Amount refunded to clients |
| Gross revenue | Cash collected − refunds |
| Direct fulfillment cost | AI usage, phone/SMS/email, software, integration, labor, onboarding, support costs directly attributable to delivering the contract |
| Gross profit | Gross revenue − direct fulfillment cost |

The Executive Command Center (`docs/15-executive-command-center-spec.md`)
renders contracted revenue and collected revenue as two separate figures,
side by side, never summed into a single headline number.

## Where this plugs into pipeline reality

`config/pipelines/sales-pipeline.json` stage `Closed Won` is what converts
a pipeline opportunity into a **contracted revenue** ledger entry; the
`Payment Pending` → `Closed Won` transition (or the first successful
billing event once live) is what starts **cash collected** counting. See
`docs/11-sales-pipeline.md` and `docs/12-client-onboarding-system.md`.
