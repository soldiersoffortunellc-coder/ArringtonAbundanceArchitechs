# Risks and Assumptions

## Core assumption discipline

The $1,037,050 combined 90-day target
(`docs/04-financial-model.md`) is built from assumed client counts (25
premium + 50 standardized) at assumed price points, not from any signed
contracts as of this writing. It is a **planning target** the Sales
Director and CRO work toward, not a forecast represented to anyone
outside the business as guaranteed. This applies equally to the ROI
calculator (`sales-assets/roi-calculator.md`) shown to individual
prospects — always their own numbers, always labeled as an estimate.

## Key risks

| Risk | Mitigation |
|---|---|
| Sales-cycle length underestimated (esp. insurance) | Sequenced go-to-market prioritizes shorter-cycle home services first (`docs/02-industry-recommendation.md`) to fund the sprint while longer-cycle deals mature |
| Implementation capacity becomes the bottleneck | Capacity triggers defined in `docs/20-capacity-and-hiring.md`; time-to-launch tracked from Day 1 pilot onward |
| Compliance failure (insurance/real estate) damages trust or creates liability | Hard gating in the onboarding state machine — `LAUNCH_APPROVED` cannot be reached without the industry pack's compliance checklist complete |
| Margin erosion on custom/enterprise deals | `targetMarginFloor` per tier + `src/revenue/profitability.js` margin-alert flagging before a deal is treated as healthy |
| Live GHL platform limitations slow fulfillment | Already surfacing in the Open Doors Financial Group pilot (`docs/09-saas-provisioning-architecture.md` platform-gaps section) — documented workarounds feed back into every future build |
| Overbuilding secondary industries too early dilutes focus | Explicit rule: no secondary industry activates before Day 90 re-evaluation (`docs/01-02`) |
| AI Conversation/Voice Agent gives a compliance-risk answer (e.g., guaranteed income, lending advice) | Prompt review is part of `complianceReviewControls`; scripts explicitly avoid guaranteed-outcome and licensed-advice language per industry pack |
| Client data mishandled on cancellation | Safe-offboarding sequence never deletes data first (`docs/12-client-onboarding-system.md`) |
| Testimonial/case-study used without permission | Hard gate in `docs/14-client-success-workflow.md` and `sales-assets/case-study-framework.md` |

## Explicit non-goals for this phase

- No secondary industry (mortgage, med spa, dental, etc.) is built before
  Day 90 re-evaluation.
- No live billing, live AI/voice connection, or live message send is
  automated by this repo without explicit owner authorization — the
  Open Doors pilot is being built directly in GHL by hand/Cowork, outside
  this constraint, and is tracked separately for that reason.
- No pricing is published externally before owner approval.
- No legal agreement is sent to a client before attorney review.

## Open items requiring owner decisions

1. Approve final pricing in `config/offers/offer-ladder.json`.
2. Select AI Conversation Agent and Voice AI vendors (not chosen in this
   phase — `docs/17-credentials-and-ghl-ids.md`).
3. Engage an attorney to draft the Implementation Agreement from
   `sales-assets/implementation-agreement-requirements.md`.
4. Confirm the compliance reviewer(s) for insurance and real estate
   clients.
5. Authorize when live (non-dry-run, non-pilot-by-hand) provisioning and
   billing may begin.
