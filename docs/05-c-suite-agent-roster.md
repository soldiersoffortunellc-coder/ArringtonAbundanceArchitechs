# 05 — C-Suite AI Agent System: Full Roster (13 agents)

Every agent below is implemented as a real Python class in
`src/csuite/agents/`, with a `run(context) -> AgentReport` method that
produces decisions, GHL directives (via `GHLAdapter`), KPIs, and
escalations — not prose. Wire-up: `src/csuite/orchestrator.py`,
`RevenueOperatingSystem`. Minimum requested was 5 C-suite agents; this
build ships **7 C-suite agents directing 6 revenue subordinates — 13
task-oriented agents in total** (`tests/test_agent_roster.py` enforces this
floor going forward).

## The 7 C-Suite agents

| Agent | File | Mission | GHL authority |
|---|---|---|---|
| **CEO** | `agents/ceo.py` | Sets strategic direction, aggregates every C-suite escalation, tracks progress against the 90-day target, and is the one role that can decide to convene a cross-functional review. | None directly — authorizes/escalates |
| **CRO** | `agents/cro.py` | Owns commercialization and revenue strategy; coordinates all 6 revenue subordinates below and rolls their reports into one revenue picture. | Delegated to subordinates |
| **CMO** | `agents/cmo.py` | Drives outbound, inbound, referral, webinar, and reactivation campaigns. | `publish_campaign`, `create_workflow` |
| **COO** | `agents/coo.py` | Protects implementation capacity, time-to-launch, and QA pass rate; escalates when capacity nears its limit or QA fails. | None directly — approves releases |
| **CFO** | `agents/cfo.py` | Runs per-account margin calculations, flags accounts below the required margin, and owns the billing ledger (contracted vs. collected, AR, refunds — never conflated). | `create_billing_event` |
| **CTO** | `agents/cto.py` | Owns snapshot technical validation, tenant isolation enforcement, and AI usage-limit enforcement. | `manage_ghl_integration`, `manage_snapshot_technical_config` |
| **CCO** (Chief Client Officer) | `agents/cco.py` | The executive escalation point above the Client Success Director — turns "N clients at risk" into "these specific clients need an executive intervention plan." | None directly — escalates |

## The 6 Revenue Subordinates (report to the CRO)

| Agent | File | Mission |
|---|---|---|
| **Market Opportunity Analyst** | `agents/revenue/market_opportunity_analyst.py` | Scores industries on 12 weighted factors; recommends Activate / Test / Pause / Reject. |
| **Productization Director** | `agents/revenue/productization_director.py` | Confirms which snapshot versions are current and productized; prevents unnecessary custom work. |
| **Sales Director** | `agents/revenue/sales_director.py` | Owns the sales pipeline: opens/moves opportunities, enforces a loss reason on every Closed Lost, reports pipeline value and close rate. |
| **Client Onboarding Director** | `agents/revenue/client_onboarding_director.py` | Runs the provisioning workflow end-to-end for every new client; reports live vs. blocked counts. |
| **Client Success and Retention Director** | `agents/revenue/client_success_retention_director.py` | Flags churn-risk signals (adoption, appointment volume, engagement, failed automations) and finds expansion candidates; withholds testimonial requests without explicit permission. |
| **Revenue Operations Analyst** | `agents/revenue/revenue_operations_analyst.py` | The single source of truth for every revenue number in the funnel-to-cash chain, and the agent that enforces "never conflate contracted and collected revenue." |

## How a cycle runs

`RevenueOperatingSystem.run_cycle(context)`:

```
CRO.run()  → runs all 6 subordinates → aggregates their reports
CMO.run()  → campaign directives
COO.run()  → capacity + QA
CFO.run()  → margin + billing
CTO.run()  → snapshot validation + usage limits + isolation checks
CCO.run()  → reads the CRO's client-success sub-report → executive escalations
CEO.run()  → reads every C-suite report above → strategic decisions
```

One call to `scripts/run_demo.py` exercises all 13 agents against realistic
synthetic data and writes the result to `dashboard/dashboard_data.json`.

## Design rules every agent follows

- **No invented facts.** Every KPI comes from config, passed-in data, or a
  computation over those (`BaseAgent` docstring).
- **No silent GHL writes.** Every write goes through the shared
  `GHLAdapter`; every action is logged and dry-run by default.
- **Global pause is absolute.** `BaseAgent._guard()` checks
  `GlobalControls.guard()` before any agent with GHL authority acts —
  a paused system blocks every write-directing agent
  (`tests/test_global_pause.py`).
- **Modeled revenue is always labeled as modeled**, never presented as a
  guarantee, at the point of computation (`FinancialModel`) and again at
  the point of narration (`RevenueOperationsAnalystAgent`, `CEOAgent`).
