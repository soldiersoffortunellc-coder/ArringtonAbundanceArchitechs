# 04 — SaaS Provisioning Architecture (directed at GoHighLevel)

Owned by: **Client Onboarding Director** + **CTO**.
Implementation: `src/csuite/ghl/adapter.py`, `src/csuite/ghl/provisioning.py`.

## The GHLAdapter — the single directed interface onto GHL

Every agent that needs to affect GoHighLevel goes through one class,
`GHLAdapter`, which models the GHL concepts this system directs:

| Method | GHL concept |
|---|---|
| `create_location` | Create a sub-account (a client's GHL "location") |
| `apply_snapshot` | Apply a snapshot to a location |
| `create_users` | Create user logins on a location |
| `create_pipeline` / `create_custom_fields` / `create_calendar` / `create_workflow` | Structural configuration |
| `tag_contact` / `create_opportunity` / `update_opportunity_stage` | CRM data operations |
| `send_notification` / `publish_campaign` | Outbound messaging / publishing |
| `create_billing_event` | Billing / SaaS Configurator events |

**Dry-run is the hard default.** `GHLAdapter(dry_run=True)` (the default)
logs every intended action to `self.actions` and returns a simulated
result — nothing leaves the process. Constructing a live adapter
(`dry_run=False`) *raises `LiveModeNotAuthorized`* unless the caller also
passes `live_authorized=True` — a flag that must come from an explicit,
human decision, never from agent logic (`tests/test_subaccount_provisioning_dry_run.py`).
Even in "live" mode, `_live_call` is a stub that raises `NotImplementedError`
until a real GHL API client is wired in — see `docs/09` for what's needed.

## Provisioning sequence (`ProvisioningWorkflow.run`)

```
plan purchase → payment confirmation → subaccount creation →
correct snapshot selection → snapshot application → user creation →
welcome email → intake form → onboarding task creation →
credential collection → QA testing → client approval → launch →
billing/usage monitoring
```

Concretely, one call to `ProvisioningWorkflow.run(...)`:

1. Drives the client through `PAYMENT_RECEIVED` → `SNAPSHOT_SELECTED` on the
   onboarding state machine (docs/06).
2. Registers the tenant in the `TenantRegistry` — **duplicate account
   prevention** happens here, before any GHL location is created
   (`tests/test_duplicate_account_prevention.py`).
3. Calls `adapter.create_location(...)`, attaches the returned location id
   to the tenant (one location per tenant, enforced).
4. Runs `SnapshotAssembler.deploy(...)` — on missing config or a failed
   apply, the state machine moves to `BLOCKED` and provisioning halts
   cleanly rather than leaving a half-configured account live.
5. Creates users, advances through `CONFIGURATION` → `INTEGRATION_TESTING` →
   `CLIENT_REVIEW` → `LAUNCH_APPROVED` → `LIVE`.

## What cannot be done from inside a GHL snapshot

Documented per-snapshot in `requires_manual_or_api_configuration` /
per-pack `disclosures` fields, and summarized in `docs/09`: A2P 10DLC
registration, DNS/domain verification, phone number porting, payment
processor connection, and the SaaS Configurator plan-to-price mapping in
the agency's own GHL account. These require either a human with agency
admin access, or a real GHL API integration once credentials exist.

## Billing & usage monitoring

`CFOAgent` records billing events through the same adapter
(`create_billing_event`) into `BillingLedger`, and `CTOAgent` enforces
per-tier AI usage caps (`config/ai_usage_limits.json`) via
`UsageLimitTracker`, flagging over-cap usage and hard-stopping runaway usage
(`tests/test_ai_usage_limits.py`).
