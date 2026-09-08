# /n8n

**Status: NOT STARTED**

Version-controlled n8n orchestration-layer workflow exports for Open Doors
Financial OS v1 (Phase 8): GHL Event Router, Lead Router, Opportunity
Router, Appointment Router, Recruiting Router, Client Router, AI Agent
Router, Error Handler, Human Approval Queue, Daily KPI Aggregator.

Blocked on Phases 3–7 (canonical data model, pipelines/stages, custom
fields/tags, calendars, webhook event bus) being stable and their real GHL
object IDs recorded in `config/ghl-object-registry.json` — n8n workflows
must reference logical names through that registry, not hard-coded IDs.

Each exported workflow JSON will be accompanied by a matching
`<workflow-name>.md` documenting: input schema, validation, logging, error
handling, retry strategy, human escalation path, and a test payload — per
the Phase 8 requirement that no n8n workflow ships undocumented.
