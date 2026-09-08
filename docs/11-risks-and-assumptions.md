# 11 — Risks and Assumptions

## Assumptions baked into this build

- No real GHL account, API credentials, or agency ID were available —
  everything is dry-run and industry/pricing/scenario numbers are
  configurable planning inputs, not researched market data.
- The 90-day financial model's client counts and price points are the
  numbers given in the mandate; they are **not** derived from actual pilot
  or market data yet (Validation phase, docs/10, is where that gets
  corrected).
- The market opportunity scorecard's factor scores in `scripts/run_demo.py`
  are illustrative/synthetic, not real vertical research.
- The three priority industries (insurance, real estate, home services) are
  assumed correct per the mandate; the scoring model exists precisely so
  this can be re-validated with real data during Validation.
- Margin/cost inputs (software cost, AI usage cost, labor rate, etc.) in
  `ClientProfitability` are illustrative — real unit economics must replace
  them before the margin-alert threshold is trusted operationally.

## Key risks

| Risk | Mitigation already in place | Residual risk |
|---|---|---|
| Presenting modeled revenue as guaranteed | Every scenario is stamped `is_guaranteed: false`; every revenue narrative explicitly caveats it | Human communicators (sales scripts, proposals) must not strip the caveat when talking to prospects |
| Over-customizing per client, eroding margin | Universal core / industry pack / client layer separation; `ClientProfitability` margin alerts | Requires actual discipline from fulfillment staff to resist ad-hoc custom work |
| Compliance exposure (insurance recruiting, fair housing, HIPAA-adjacent home-services financing) | Each industry pack carries its own `disclosures` and, for insurance, explicit `compliance_review_controls` | Real compliance review by qualified counsel is still required before any consumer-facing content ships |
| Cross-tenant data leakage | `TenantRegistry` isolation boundary + tests | Only enforced within this codebase's data access pattern — a real multi-tenant datastore must replicate this boundary at the DB/query layer |
| Runaway AI usage cost eroding margin | Per-tier `UsageLimitTracker` with hard-stop multiplier | Real cost-per-interaction figures from a live AI provider are needed to calibrate the caps correctly |
| Accidental live/paid activation | `LiveModeNotAuthorized` gate on `GHLAdapter` construction | A human must still remember to keep `GHL_LIVE_AUTHORIZED` false outside of an authorized go-live |
| Premature ten-industry expansion diluting fulfillment quality | Explicit Phase 1 scope limited to 3 industries (docs/00, docs/01) | Requires continued discipline not to activate secondary industries early |
| Testimonial/case-study use without permission | Code-level gate in `ClientSuccessRetentionDirectorAgent` (withholds request without `testimonial_permission_granted`) | Still requires a human compliance sign-off step, which is not automatable |

## Explicitly out of scope for this phase

See `docs/00-audit-and-roadmap.md` → "What is deliberately postponed."
