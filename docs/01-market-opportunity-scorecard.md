# 01 — Market Opportunity Scorecard & Final Three-Industry Recommendation

Owned by: **Market Opportunity Analyst** (reports to the CRO).
Implementation: `src/csuite/revenue/scoring.py`, run via
`MarketOpportunityAnalystAgent`.

## Scoring model

Twelve weighted factors, each scored 0–10 (weights default to 1.0 each and
are fully configurable per `OpportunityScorer(weights=...)`):

1. Pain urgency
2. Financial impact
3. Ability to pay
4. Ease of reaching decision-makers
5. Sales-cycle length (10 = short/fast cycle)
6. Repeatability
7. GHL compatibility
8. AI automation potential
9. Compliance complexity (10 = low complexity)
10. Retention potential
11. Expansion revenue
12. Referral potential

Normalized to a 0–10 score. Recommendation thresholds (configurable in
`RECOMMENDATION_THRESHOLDS`):

| Normalized score | Recommendation |
|---|---|
| ≥ 7.5 | ACTIVATE |
| 6.0 – 7.49 | TEST |
| 4.0 – 5.99 | PAUSE |
| < 4.0 | REJECT |

## Illustrative scorecard (demo data, see `scripts/run_demo.py`)

| Industry | Normalized score | Recommendation |
|---|---|---|
| Insurance Agency | 7.58 | ACTIVATE |
| Home Services | 7.83 | ACTIVATE |
| Real Estate | 7.5 | ACTIVATE |
| Mortgage | 4.75 | PAUSE |

These are **illustrative scores from synthetic demo inputs**, not a claim
about real market conditions. The scoring inputs must be replaced with real
research (competitor density, actual GHL fit-testing, actual compliance
review) before being used to greenlight spend.

## Final three-industry recommendation

Per the mandate to prove the universal core plus three priority systems
before expanding, and consistent with the illustrative scorecard above,
this build's Phase 1 industry packs are:

1. **Insurance Agency** — highest combination of recruiting pain, GHL fit,
   and AI automation potential (licensed-agent recruiting is a repeatable,
   high-LTV problem).
2. **Real Estate** — largest addressable market with strong repeatability
   and referral potential; long sales cycles offset by database
   reactivation value.
3. **Home Services** (HVAC, plumbing, roofing, electrical, general
   contracting, remodeling, restoration) — highest pain urgency (missed
   calls = lost revenue same-day) and best repeatability across
   sub-verticals sharing one snapshot.

Mortgage and the remaining secondary industries listed in the mandate are
explicitly **not** activated in Phase 1 (see `docs/00`).
