# Deployment Plan

## Environments

| Environment | Purpose |
|---|---|
| Dry-run (this repo, default) | All provisioning/billing/messaging logic runs against `dryRunAdapter` — safe to run anytime, no live side effects |
| Live pilot subaccount(s) | Hand-built or API-provisioned real GHL subaccounts for actual clients (e.g., Open Doors Financial Group — `docs/17-credentials-and-ghl-ids.md`) |
| Production (post-authorization) | Real `GhlApiAdapter` swapped in behind the same `Provisioner` interface once owner authorizes live billing/provisioning |

## Rollout sequence

1. **Universal core + 3 industry-pack snapshots** finalized as GHL
   snapshots inside the agency account (manual export/import initially;
   API-driven later).
2. **First live pilot per industry** — build one real client by hand in
   GHL per priority industry (insurance pilot already underway; real
   estate and home services pilots next), capturing platform gaps the same
   way `config/live-pilots/odfg-ghl-workflow-status.json` does.
3. **Reconcile pilot learnings into snapshots** — once a pilot's workflows
   are stable, fold the actual workflow structure back into
   `config/snapshots/industry-pack-*.json` so the *next* client of that
   industry starts from the proven build, not the original spec.
4. **Repeat for remaining Phase 1 clients** using the reconciled snapshot,
   manually or via the dry-run provisioner's adapter once a live adapter
   is authorized and built.
5. **Live billing activation** — only after explicit owner authorization;
   swap `dryRunAdapter` for a real GHL API + SaaS Configurator adapter
   behind the unchanged `Provisioner` interface.

## Rollback

Any client stuck mid-provisioning routes to `BLOCKED` (see
`docs/12-client-onboarding-system.md`), never left partially configured
without a status. A defect discovered across multiple clients triggers
`globalPause` (`src/provisioning/dryRunProvisioner.js`) to halt further
provisioning while it's fixed.

## Versioning and change management

Snapshot changes are semver'd (`docs/05-08`). A breaking universal-core
change requires a migration note and is never pushed silently to a live
client's subaccount.
