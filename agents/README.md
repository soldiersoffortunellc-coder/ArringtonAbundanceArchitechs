# /agents

**Status: NOT STARTED**

AI agent specifications for Open Doors Financial OS v1 (Phase 9): Lead
Qualification, Appointment Setter, Database Reactivation, Recruiting,
Agent Onboarding, Client Service, Case Preparation, Referral, Content,
CEO/Chief-of-Staff, COO Operations, CFO Analytics — 12 agents.

Each agent spec here will document, per the Phase 9 requirement: ROLE,
OBJECTIVE, ALLOWED TOOLS, ALLOWED DATA, PROHIBITED ACTIONS, ESCALATION
CONDITIONS, OUTPUT SCHEMA, AUDIT REQUIREMENTS — as data/spec files an
orchestration layer (n8n and/or the existing Python agent framework)
implements against.

## Relationship to `src/csuite/agents/`

This repository already contains a working, tested Python agent framework
(`src/csuite/agents/` — 19 agents across the Revenue OS and AI Media &
Marketing Division, with a `BaseAgent`/`AgentReport` pattern, dry-run
provider adapters, and 155 passing tests). Open Doors Financial OS v1's
Phase 9 agents are a **different, GHL/n8n-native agent set** scoped to
insurance-specific operations (lead qualification, case preparation,
recruiting, etc.) — distinct responsibilities from the existing revenue/
marketing agents, not a replacement for them. Where a Phase 9 agent's
responsibility overlaps with an existing agent's (e.g. Recruiting Agent
here vs. `client_onboarding_director`/`sales_director` in the existing
system), the implementation phase (not this first execution) will decide
whether to extend the existing Python agent or implement natively as an
n8n + LLM node — documented as an explicit decision in `ARCHITECTURE.md`
before either path is built.
