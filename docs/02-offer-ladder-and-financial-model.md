# 02 — Offer Ladder & 90-Day Financial Model

Owned by: **CRO** (offer design) + **Revenue Operations Analyst** (modeling)
+ **CFO** (margin discipline).
Config: `config/offer_ladder.json`, `config/financial_scenarios.json`.
Implementation: `src/csuite/revenue/financial_model.py`.

## Offer ladder (all prices configurable — not yet approved for publication)

| Tier | Setup fee | Monthly fee | Positioning |
|---|---|---|---|
| Starter SaaS | $0–$997 (optional) | $497–$997 | White-labeled CRM + basics |
| AI Growth System | $2,500–$7,500 | $997–$2,500 | Industry snapshot + AI agents |
| AI Revenue Operating System | $10,000–$25,000 | $2,500–$5,000 | Full industry system, custom build |
| Enterprise / Agency License | $25,000–$100,000 | $5,000–$15,000 | Multi-location / white-label rights |

**Pricing is not published externally until the business owner explicitly
approves it.** Nothing in this codebase publishes a price anywhere.

## 90-day revenue model

Three scenarios (`config/financial_scenarios.json`), each combining a
**premium segment** (AI Revenue Operating System tier) and a **standardized
segment** (Starter/Growth-tier SaaS clients), modeled over 3 months of
recurring revenue:

| Scenario | Premium clients | Premium value | Standardized clients | Standardized value | Combined modeled 90-day value |
|---|---|---|---|---|---|
| Conservative | 10 | $305,000 | 20 | $109,820 | **$414,820** |
| Target | 25 | $762,500 | 50 | $274,550 | **$1,037,050** |
| Aggressive | 40 | $1,220,000 | 80 | $439,280 | **$1,659,280** |

Formula (see `FinancialModel._segment_value`):
`modeled_value = clients × setup_fee + clients × monthly_fee × recurring_months`

**These are modeled planning inputs, not guaranteed outcomes.** Every
`FinancialModel.scenario()` result is stamped `"is_guaranteed": false`, and
`RevenueOperationsAnalystAgent` always narrates this caveat alongside the
number (see `tests/test_revenue_calculations.py`).

## Revenue truth-in-reporting rule

Contracted revenue, invoiced revenue, cash collected, refunds, MRR, and
accounts receivable are tracked as **distinct fields, never summed into one
misleading number** (`src/csuite/platform/billing.py::BillingLedger`,
enforced by `tests/test_contracted_vs_collected.py`).
