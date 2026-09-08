# Open Doors Financial OS v1 — Deployment SOP

This is the standard operating procedure for taking OS v1 from its current
state (config drafted, nothing deployed) to a live, tested GHL build. It
enforces the phase order from `ARCHITECTURE.md` — no phase starts before
its dependencies show **COMPLETE, TESTED** in `BUILD-STATUS.md`.

## 1. Supply credentials (unblocks Phase 1)

On the machine that will run these scripts — **never in chat, never
committed**:

```bash
export GHL_LOCATION_ID="<Open Doors Financial Group's GHL location id>"
export GHL_PRIVATE_INTEGRATION_TOKEN="<Private Integration Token from GHL Settings > Private Integrations>"
export GHL_API_VERSION="2021-07-28"
```

Grant the Private Integration Token the narrowest scope set that covers
read access to: locations, opportunities/pipelines, contacts, custom
fields, custom values, tags, calendars, users. Do not request write scopes
yet — Phase 1/2 are read-only.

## 2. Run the connection test (Phase 1)

```bash
python3 scripts/ghl_connection_test.py
```
Exit code 0 = PASS. Non-zero = FAIL, with the exact cause (missing env
var, invalid token, insufficient scope, wrong location id) printed —
**never a token value**. Do not proceed until this passes.

## 3. Run discovery (Phase 2)

```bash
pip install pyyaml   # once, for the conflict-check step
python3 scripts/ghl_discovery.py
```
Produces `docs/GHL-CURRENT-STATE.md` and `config/current-state.json`.
Review both for naming conflicts against `config/os-v1.yaml` before
proceeding. If conflicts exist, resolve them in `os-v1.yaml` (rename the
proposed object, or point the logical name at the existing object's real
ID) — do not create a duplicate.

## 4. Reconcile the canonical model (Phase 3)

Update `config/os-v1.yaml` with any conflict resolutions, then regenerate
the registry:
```bash
python3 scripts/build_object_registry.py
```
`config/ghl-object-registry.json` is now the up-to-date, pre-creation
proposal.

## 5. Approval gate (mandatory, human)

Before any `CREATE`/`PUT`/`POST` call runs against the live account, a
human with business/compliance authority reviews:
- `docs/GHL-CURRENT-STATE.md` (what exists today)
- The diff between that and `config/os-v1.yaml` (what would be created)
- Any flagged conflicts

Only after explicit approval does Phase 4 (pipeline creation) begin. This
SOP does not define an auto-approve path — there isn't one.

## 6. Build phases 4–7 (pipelines → fields/tags → calendars → webhooks)

Each phase's creation scripts must, before creating anything: query for an
existing object with the same name, skip creation and record the existing
ID if found, otherwise create and immediately re-fetch to verify. Running
any phase's script twice must be a no-op the second time (idempotency —
see `ARCHITECTURE.md`). After each phase, update `BUILD-STATUS.md` and
commit.

## 7. n8n + agents (Phases 8–9)

Only after Phases 3–7 show **COMPLETE, TESTED**. Every n8n workflow
references GHL objects via `config/ghl-object-registry.json` logical
names — never a hard-coded ID pasted into an n8n node.

## 8. 28 production workflows (Phase 11)

Only after Phases 3–9 show **COMPLETE, TESTED**. `workflows/
WORKFLOW-MASTER-MATRIX.md` is written and reviewed before any workflow is
turned on for real traffic. First launch of any bulk outbound campaign
requires explicit human approval (Phase 10 rule).

## 9. Test environment (Phase 12) — required before any phase is marked TESTED

Synthetic contacts/opportunities only. Never test destructive logic (stage
changes, cancellations, bulk tagging) against a real client record.
`tests/TEST-RESULTS.md` must show PASS/FAIL/BLOCKED for every listed test
before the corresponding component is marked TESTED in `BUILD-STATUS.md`.

## 10. Observability, dashboards, duplication (Phases 13–15)

Standard build order — see `ARCHITECTURE.md`. Duplication into a second
GHL subaccount (`deployment/NEW-LOCATION-CHECKLIST.md`) is not attempted
until the first location's build is COMPLETE, TESTED end to end.

## Rollback

Every phase's changes are additive and reversible at the config layer
(`os-v1.yaml`/`ghl-object-registry.json` are the source of truth — revert
the commit that changed them). GHL objects actually created (Phase 4+) are
NOT auto-deleted by any rollback — removing a live pipeline/field/calendar
that may already have data attached is a business decision requiring
explicit human approval, never an automated rollback action.
