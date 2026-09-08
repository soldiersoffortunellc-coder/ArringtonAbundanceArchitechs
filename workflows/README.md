# /workflows

**Status: NOT STARTED — explicitly blocked until Phases 3–7 are stable and tested**

Home of `WORKFLOW-MASTER-MATRIX.md` (Phase 11) and the 28 production GHL
workflows it documents, separated into REVENUE, RECRUITING, ONBOARDING,
CLIENT SERVICE, OPERATIONS, and COMPLIANCE lanes.

Per the operating rule: **"Do not create the 28 production workflows
until the underlying data model, IDs, stages, fields, tags, calendars and
routing rules are stable."** Nothing is built here in this first
execution — see `BUILD-STATUS.md` for what's actually blocking this
phase.

## Relationship to `config/marketing/workflow_blueprints.json`

The existing Revenue OS/Marketing Division work already documented 17
workflow blueprints for the AI-clone marketing pipeline specifically
(`config/marketing/workflow_blueprints.json`,
`docs/13-media-marketing-audit-and-plan.md`). This directory's 28
production workflows are a broader, insurance-agency-wide operational set
(lead routing, recruiting, onboarding, client service, compliance) — a
distinct scope. Where a workflow would duplicate one already blueprinted
there (e.g. compliance review, human-approval notification), the
implementation phase will reference the existing blueprint rather than
re-specify it from scratch.
