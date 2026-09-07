# Executive Command Center — Specification

Owner: **Revenue Operations Analyst**, data supplied by all six
subordinate agents. Computation layer: `src/revenue/*.js`,
`src/pipeline/pipeline.js`. No live dashboard UI is built in this phase —
this spec defines the exact fields and computations a dashboard (GHL
custom dashboard widgets, or a lightweight internal app) must render.

## Required fields (from the brief, verbatim)

90-day revenue target · Contracted revenue · Collected revenue · Monthly
recurring revenue · Pipeline value · Weighted pipeline value · Discovery
calls · Demonstrations · Proposals · Closed clients · Average sale · Close
rate · Implementation capacity · Time to launch · Gross margin · Client
health · Churn risk · Results by industry · Results by offer · Results by
salesperson · Results by acquisition source.

## Hard rule: contracted vs. collected

Contracted revenue and collected revenue are **always two adjacent tiles**,
never one summed "revenue" tile. See `src/revenue/revenueLedger.js` and
`docs/04-financial-model.md`.

## Field → source mapping

| Field | Computed from |
|---|---|
| 90-day revenue target | `config/scenarios/90-day-revenue-scenarios.json` (target scenario) |
| Contracted revenue | `revenueLedger.contractedTotal()` |
| Collected revenue | `revenueLedger.collectedTotal()` |
| Monthly recurring revenue | `revenueLedger.mrr()` |
| Pipeline value | `pipeline.totalValue()` |
| Weighted pipeline value | `pipeline.weightedValue()` (stage probability × value) |
| Discovery calls / Demonstrations / Proposals / Closed clients | Count of opportunities that reached the corresponding pipeline stage in the period |
| Average sale | Contracted revenue ÷ Closed clients |
| Close rate | Closed Won ÷ (Closed Won + Closed Lost) |
| Implementation capacity | Fulfillment team capacity vs. active `Onboarding`/`Implementation` stage count (`docs/20-capacity-and-hiring.md`) |
| Time to launch | Average `PAYMENT_RECEIVED` → `LIVE` duration (`src/onboarding/stateMachine.js`) |
| Gross margin | `profitability.grossMargin()` aggregate |
| Client health / Churn risk | Client Success risk-signal roll-up (`docs/14-client-success-workflow.md`) |
| Results by industry / offer / salesperson / acquisition source | Grouped roll-ups over the same underlying ledger and pipeline data — one computation, four group-by dimensions |

## Design constraint

Every number on this dashboard must trace to a specific ledger entry,
pipeline stage transition, or state-machine event — no manually-typed
"vanity" figures. This is what keeps the 90-day target honest as an
*operating target*, not a claim.

## Access

Role-gated per `src/permissions/roles.js`: owner and CRO see the full
cross-tenant rollup; a Sales Director sees pipeline/close-rate views; a
Client Onboarding Director sees implementation-capacity/time-to-launch
views; a Client Success Director sees health/churn views. No role sees
another client's raw contact data through this dashboard — rollups only.
