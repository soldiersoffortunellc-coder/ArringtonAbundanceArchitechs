# /dashboards

**Status: NOT STARTED**

Executive dashboard data models for Open Doors Financial OS v1 (Phase 14):
leads today/this week, appointments booked, show rate, applications,
submitted/placed/issued premium, annuity assets submitted/funded, IBC
cases, licensed recruits, new/active agents, agent production, funnel
conversion rates, revenue forecast.

Every metric here must trace to a defined source (a GHL object, a webhook
event, or an n8n aggregation step recorded in `config/ghl-object-registry.json`
or `/logs`) — no fabricated dashboard data, per the Phase 14 rule.

The existing `dashboard/` directory (singular — note the different name)
is the Revenue OS's executive command center for the broader C-Suite AI
Agent System (contracted/collected revenue, pipeline value, market
opportunity ranking). This `dashboards/` directory (plural) is OS v1's
insurance-operations-specific dashboard data layer — kept separate rather
than overloading the existing one, matching the same reasoning documented
in `docs/07-executive-command-center.md`.
