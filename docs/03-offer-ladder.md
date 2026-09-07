# Offer Ladder

Structured data: `config/offers/offer-ladder.json`. **Status: DRAFT — not
approved for publication, quoting, or contracting.** Every dollar figure
below is a target range pending your sign-off, per the rule *"Pricing must
remain configurable. Do not publish pricing until I approve it."*

## The four tiers

| Tier | Setup (range) | Monthly (range) | Snapshot layers used | Sold by |
|---|---|---|---|---|
| 1. Starter SaaS | $0–$500 | $497–$997 | Universal core only | Sales Director (transactional) |
| 2. AI Growth System | $2,500–$7,500 | $997–$2,500 | Universal core + industry pack | Sales Director (consultative) |
| 3. AI Revenue Operating System | $10,000–$25,000 | $2,500–$5,000 | Universal core + industry pack + client config | Sales Director + CRO sign-off on custom scope |
| 4. Enterprise / Agency License | $25,000–$100,000 | $5,000–$15,000 (+ optional per-location/per-agent) | All layers + multi-tenant rollup | CRO-led |

Full inclusion lists live in `config/offers/offer-ladder.json` (machine-
readable, matches the brief's tier definitions verbatim) — this doc is the
narrative layer on top of it.

## Ladder logic

- **Starter SaaS** is the low-friction entry point: proves missed-call
  recovery and reputation-management ROI fast, creates the install base
  from which Tier 2/3 upsells are sourced by the Client Success and
  Retention Director.
- **AI Growth System** is where the industry snapshot and AI Conversation
  Agent first appear — this is the tier most home-services and real-estate
  prospects should land on for a first close.
- **AI Revenue Operating System** is the flagship tier and the one modeled
  as "premium implementation" in the 90-day financial model
  (`docs/04-financial-model.md`). This is the tier insurance-agency
  recruiting systems and multi-agent real estate teams are sized for.
- **Enterprise / Agency License** exists for multi-location home-services
  groups, franchise/master-agency insurance relationships, and real estate
  brokerages — and for the possibility of licensing the whole Revenue OS to
  other agency owners. Pricing here is the least standardized and should
  route through the CRO before quoting.

## Margin guardrail

Every tier carries a `targetMarginFloor` in the config
(0.40–0.55 depending on tier). `src/revenue/profitability.js` flags any
priced deal that would fall below its tier's floor before it is closed —
see `docs/14-client-success-workflow.md` and the "Client Profitability
Controls" requirement in the brief.

## Approval workflow before any price is quoted externally

1. Owner reviews `config/offers/offer-ladder.json`.
2. Owner approves final numbers per tier (can differ from the ranges
   above).
3. `status` field flips from `DRAFT` to `APPROVED` with a date and the
   approved figures locked in.
4. Only then do Sales Assets (`docs/16-sales-assets.md`) get numbers
   inserted — every sales asset in this repo currently uses `$[TBD]`
   placeholders for this reason.
