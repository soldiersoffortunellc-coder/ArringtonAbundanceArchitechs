# Market Opportunity Scorecard

Owner: **Market Opportunity Analyst** (reports to Chief Revenue Officer).

## Scoring model

12 factors, scored 1 (worst) – 5 (best), summed to a 60-point composite.
For "Compliance complexity," a **higher** score means **lower** regulatory
burden (i.e., more favorable), so the composite stays consistently
"higher = more attractive" across all 12 factors.

| Factor | What it measures |
|---|---|
| Pain urgency | How immediately painful the problem is to the business owner |
| Financial impact | Dollar cost of the problem if unsolved |
| Ability to pay | Typical business cash flow / margin to fund the fix |
| Ease of reaching decision-makers | Can we identify and contact the buyer directly |
| Sales-cycle length | Shorter cycle = higher score |
| Repeatability | How standardized the fix is across businesses in the vertical |
| GHL compatibility | How well GHL's native feature set covers the vertical's needs |
| AI automation potential | How much AI conversation/voice can replace manual labor |
| Compliance complexity | Lower regulatory/legal burden = higher score |
| Retention potential | Likelihood of long-term subscription retention |
| Expansion revenue | Upsell/multi-location/multi-user potential |
| Referral potential | Density of the buyer's peer network for referrals |

## Priority industries (full scoring)

| Factor | Insurance | Real Estate | Home Services |
|---|---:|---:|---:|
| Pain urgency | 4 | 5 | 5 |
| Financial impact | 5 | 4 | 5 |
| Ability to pay | 4 | 3 | 4 |
| Ease of reaching decision-makers | 3 | 4 | 4 |
| Sales-cycle length | 3 | 4 | 4 |
| Repeatability | 5 | 5 | 5 |
| GHL compatibility | 5 | 5 | 5 |
| AI automation potential | 5 | 5 | 5 |
| Compliance complexity (favorability) | 2 | 4 | 5 |
| Retention potential | 4 | 3 | 5 |
| Expansion revenue | 4 | 4 | 5 |
| Referral potential | 4 | 5 | 4 |
| **Composite (of 60)** | **48** | **51** | **56** |

**Reading the scores:** all three clear a high bar (≥ 48/60) and all three
were pre-selected in the brief as Phase 1 verticals — this scorecard
confirms that selection rather than overriding it. Home services scores
highest on urgency, retention, and expansion (recurring maintenance plans,
multi-trade/multi-location owners); insurance scores lowest primarily on
compliance complexity (state-by-state insurance and TCPA rules) and
sales-cycle length (agency principals move slower, often through
FMOs/IMOs). None of that changes the recommendation — see
`docs/02-industry-recommendation.md` — it changes **sequencing and
compliance investment**, not selection.

## Secondary industries (abbreviated screen)

Full 12-factor scoring is deferred until a secondary vertical is actually
activated (post-Day-90, per the brief). This is a directional screen only,
used to order the "what's next" queue in
`docs/02-industry-recommendation.md`.

| Industry | Directional composite | Key driver | Key drag |
|---|---:|---|---|
| Property management | High | Recurring, multi-unit, strong retention | Fragmented software incumbents (AppFolio, Buildium) |
| Med spas | High | High ticket, strong AI-booking fit | Regulatory (medical directors), seasonal demand |
| Dental practices | Medium-High | High ticket, recall/reactivation fit | Long incumbent software entrenchment (Dentrix, etc.) |
| Mortgage | Medium-High | High urgency (rate-sensitive speed-to-lead) | Heavy compliance (RESPA, state licensing) |
| Fitness | Medium | Strong reactivation/referral fit | Lower ability to pay per location |
| Business coaching | Medium | High AI-content fit, fast sales cycle | Market saturated with "guru" CRM offers |
| Law firms | Medium | High ticket for PI/family law | Ethics-rule compliance varies heavily by state/practice area |
| Accounting/tax firms | Medium | Strong seasonal reactivation fit | Long, relationship-driven sales cycle |
| Nonprofit organizations | Low-Medium | Mission alignment, donor reactivation fit | Low ability to pay, grant-cycle budgeting |
| Veteran-service organizations | Low-Medium | Strong mission fit, referral density | Low ability to pay, funding-cycle dependent |
| Sober living / transitional housing | Low-Medium | Underserved, high retention once installed | Compliance/licensing risk, low ability to pay |

## How this scorecard is used

- `config/snapshots/` is only built for verticals scoring in the "priority"
  tier today.
- The Days 61–90 execution phase decision ("which secondary industry
  activates next") should draw from the top of the secondary table —
  currently **property management** or **med spas** — re-scored with the
  full 12-factor model once Phase 1 delivery margin is confirmed.
