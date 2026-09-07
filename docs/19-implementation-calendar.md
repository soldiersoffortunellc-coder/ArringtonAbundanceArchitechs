# 90-Day Implementation Calendar

Mirrors the brief's four execution phases exactly; treat week numbers as
planning targets, adjustable as real data comes in during Days 15-30.

## Days 1-14 — Foundation

- Week 1: Brand finalization, offer architecture approval
  (`docs/03-offer-ladder.md` → owner sign-off), universal snapshot build.
- Week 2: SaaS plans/billing structure defined, onboarding form built,
  sales pipeline configured, proposal templates finalized, reporting
  dashboard fields confirmed, fulfillment checklist finalized, demo
  accounts built, insurance/real-estate/home-services MVP snapshots
  complete. *(In progress in parallel: the live Open Doors Financial Group
  insurance build — `docs/17-credentials-and-ghl-ids.md`.)*

## Days 15-30 — Validation

- Recruit pilot clients (target: at least 1 per priority industry).
- Run demonstrations, track objections against
  `sales-assets/objection-handling-library.md`, add any new ones found.
- Measure actual implementation time per pilot
  (`docs/13-fulfillment-workflow.md`) and replace estimates with actuals.
- Secure case studies where permission is granted
  (`sales-assets/case-study-framework.md`).
- Reconcile pilot-build learnings into snapshots (per
  `docs/18-deployment-plan.md` step 3).
- Confirm delivery margins against `targetMarginFloor` per tier
  (`src/revenue/profitability.js`).
- Finalize first sellable snapshot versions (bump to `1.1.0`+ as needed).

## Days 31-60 — Sales Acceleration

- Launch outbound, referral (`sales-assets/referral-partner-campaign.md`),
  webinar (`sales-assets/webinar-presentation-outline.md`), and database-
  reactivation campaigns.
- Publish AI-generated educational content per industry.
- Stand up sales-team scorecards (activity/conversion by rep and source —
  `docs/15-executive-command-center-spec.md`).
- Launch affiliate/referral program (pending compliance review for
  insurance/real estate).
- Institute daily pipeline review cadence.

## Days 61-90 — Scale

- Increase daily demonstration volume; deploy proven snapshots faster.
- Add implementation capacity per `docs/20-capacity-and-hiring.md` triggers.
- Improve close rate and reduce time-to-launch using accumulated data.
- Expand referrals; upsell active clients (`Expansion Opportunity` stage).
- Monitor and act on churn risk (`docs/14-client-success-workflow.md`).
- Standardize client-success playbooks from what worked in Days 31-60.
- Re-score and decide the next secondary industry to activate
  (`docs/02-industry-recommendation.md`).

## Reporting cadence

Weekly pipeline review from Day 1; daily from Day 31 onward, per the
brief's Days 31-60 objective.
