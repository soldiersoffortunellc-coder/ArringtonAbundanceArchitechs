# 10 — Deployment Plan, 90-Day Calendar, Capacity & Hiring

## Deployment plan (this codebase → production)

1. **Package** — `pip install -e .` from `pyproject.toml` (src-layout,
   already configured); or containerize with the same `src/` tree.
2. **Wire credentials** — populate the environment variables in docs/09;
   implement `GHLAdapter._live_call` against the real GHL API once
   credentials exist.
3. **Persistence** — replace the in-memory `TenantRegistry`, `BillingLedger`,
   `SalesPipeline`, and `UsageLimitTracker` with a real datastore (Postgres
   recommended); the current classes are the reference implementation of
   the *rules*, not the storage layer — swap the storage, keep the rules.
4. **Scheduling** — run `RevenueOperatingSystem.run_cycle()` on a recurring
   cadence (daily recommended) via a scheduler/cron/queue worker; feed it
   real pipeline/onboarding/billing events instead of `scripts/run_demo.py`'s
   synthetic context.
5. **Dashboard** — point `dashboard/index.html`'s fetch at a real API
   endpoint that serves the latest `run_cycle()` output per agency.
6. **Human-in-the-loop gates stay in place**: live-mode authorization,
   pricing publication approval, testimonial/compliance approval, and
   `safe_offboard(confirm=True)` all require an explicit human action —
   do not automate these away during deployment.

## 90-day execution calendar (as specified)

| Phase | Days | Focus |
|---|---|---|
| Foundation | 1–14 | Brand, offer architecture, universal snapshot, SaaS plans, billing structure, onboarding form, sales pipeline, proposal templates, reporting dashboard, fulfillment checklist, demo accounts, 3 industry MVPs |
| Validation | 15–30 | Pilot clients, demonstrations, objection tracking, implementation-time measurement, case studies (with permission), offer/onboarding refinement, margin confirmation, finalize sellable snapshots |
| Sales Acceleration | 31–60 | Outbound, referral partnerships, webinar funnel, AI-generated content, database reactivation, industry demos, appointment-setting workflows, sales scorecards, affiliate program, daily pipeline review |
| Scale | 61–90 | More daily demos, faster snapshot deployment, added implementation capacity, better close rate, reduced time-to-launch, referral expansion, upsells, churn-risk monitoring, standardized client success, decide next secondary industry |

## Capacity & hiring requirements (planning estimate, not a commitment)

Based on the target scenario (25 premium + 50 standardized clients over 90
days) and the COO agent's capacity model
(`implementation_capacity_used_pct` in `src/csuite/agents/coo.py`):

- **Fulfillment/implementation**: at ~10 concurrent implementations per
  specialist (per the demo's `max_capacity` assumption) and a ~10-day
  average time-to-launch, roughly 75 total onboardings across 90 days
  implies needing to plan for **2–3 dedicated fulfillment specialists** by
  the Sales Acceleration phase, scaling to a 4th in the Scale phase if
  volume holds.
- **Sales**: enough reps/setters to run the discovery→demo→proposal cadence
  needed to hit the modeled close-rate assumptions — track actual
  discovery/demo volume from Day 15 onward and staff to the Sales
  Director's `close_rate` KPI, not to a guess.
- **Client Success**: one dedicated Client Success and Retention function
  once the live client count passes roughly 15–20 accounts (the point at
  which manual QBRs stop scaling).
- **Technical/CTO function**: one person owning snapshot versioning, GHL
  technical config, and (once activated) live API integration.

These are planning estimates from the model above, explicitly not a hiring
guarantee — actual staffing should follow real pipeline and fulfillment
data once the Validation phase produces it.
