# Revenue-Agent Definitions

Structured data: `config/agents/*.json` (one file per role, machine-
readable — responsibilities, hard constraints, KPIs, and ownership all
copy verbatim from the brief plus this repo's file ownership map).

## Org chart

```
Owner
  └─ Chief Revenue Officer
       ├─ Market Opportunity Analyst
       ├─ Productization Director
       ├─ Sales Director
       ├─ Client Onboarding Director
       ├─ Client Success and Retention Director
       └─ Revenue Operations Analyst
```

## Role summary

| Role | Owns (files) | Cannot do |
|---|---|---|
| Chief Revenue Officer | Cross-division coordination, offer/pricing approval | Represent projections as guarantees; publish pricing without owner approval; authorize live activation |
| Market Opportunity Analyst | `docs/01-market-opportunity-scorecard.md` | Recommend activating a vertical outside CRO-approved set; fabricate market data |
| Productization Director | `config/snapshots/*.json` | Put client-specific logic in universal-core or an industry pack |
| Sales Director | `config/pipelines/sales-pipeline.json`, `sales-assets/` | Invent facts/pricing/commitments; skip loss-reason capture; quote unapproved pricing |
| Client Onboarding Director | `config/onboarding/state-machine.json`, `src/onboarding/`, `src/provisioning/` | Approve launch without compliance controls satisfied; activate live billing/provisioning without authorization |
| Client Success and Retention Director | Adoption/risk monitoring, executive reports | Use a testimonial without documented permission + compliance approval |
| Revenue Operations Analyst | `src/revenue/*.js` | Combine contracted and collected revenue into one number; hide a below-floor margin account |

## How these definitions are meant to be used

Each JSON file is written to be directly loadable by an agent-orchestration
layer (whether that's Claude Projects/sub-agents, a GHL-side workflow
naming convention, or a future internal tool) — `responsibilities` and
`hardConstraints` are the operating brief for that role, and `owns` is the
literal file/config boundary that role is allowed to change. This keeps
the six subordinate agents from silently overlapping scope.
