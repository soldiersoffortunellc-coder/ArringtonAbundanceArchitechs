# 06 — Sales Pipeline & Client Onboarding State Machine

## Sales pipeline

Config: `config/sales_pipeline.json`. Implementation:
`src/csuite/pipeline/sales_pipeline.py`. Owned by the **Sales Director**.

```
Target Account → Contacted → Engaged → Discovery Booked → Discovery Completed →
Qualified → Demo Booked → Demo Completed → Proposal Sent → Verbal Commitment →
Payment Pending → Closed Won → Onboarding → Implementation → Quality Assurance →
Live → Expansion Opportunity → Nurture → Closed Lost
```

- `Closed Lost` **requires** a `loss_reason` from a fixed vocabulary
  (`no_budget`, `no_decision_authority`, `chose_competitor`, `chose_diy`,
  `bad_timing`, `unresponsive`, `not_a_fit`, `compliance_blocker`, `other`).
  Attempting to close-lost without one raises `LossReasonRequiredError`
  (`tests/test_sales_pipeline.py`).
- Pipeline value excludes terminal stages, so Closed Lost never inflates an
  active pipeline number.

## Client onboarding state machine

Config: `config/onboarding_states.json`. Implementation:
`src/csuite/onboarding/state_machine.py`. Owned by the **Client Onboarding
Director**.

### Primary path (strictly forward-only — no skipping stages)

```
PAYMENT_RECEIVED → AGREEMENT_CONFIRMED → INTAKE_SENT → INTAKE_COMPLETED →
CREDENTIALS_PENDING → SNAPSHOT_SELECTED → SUBACCOUNT_CREATED →
SNAPSHOT_APPLIED → CONFIGURATION → INTEGRATION_TESTING → CLIENT_REVIEW →
LAUNCH_APPROVED → LIVE → OPTIMIZATION
```

### Side-states (reachable only from specific primary states)

| Side-state | Reachable from | Resume target |
|---|---|---|
| `BLOCKED` | Any state from `INTAKE_SENT` through `CLIENT_REVIEW` | Returns to the state the client was in |
| `PAUSED` | `LIVE`, `OPTIMIZATION`, `CLIENT_REVIEW`, `CONFIGURATION` | Returns to the state the client was in |
| `CANCELED` | Any pre-launch state, or from `BLOCKED`/`PAUSED` | Terminal — no resume |
| `REFUND_REVIEW` | `LIVE`, `OPTIMIZATION`, `BLOCKED`, `PAUSED`, `CANCELED` | Resume or move to offboard |
| `OFFBOARDED` | `PAUSED`, `CANCELED`, `REFUND_REVIEW`, `LIVE`, `OPTIMIZATION` | Terminal — no resume |

Enforcement details (`tests/test_client_onboarding_transitions.py`):
onboarding must start at `PAYMENT_RECEIVED`; every primary-path move must be
exactly one step forward (no skipping stages, no jumping backward); a
side-state can only be entered from its allow-listed source states;
`resume()` returns to the pre-side-state exactly.

## Why they're linked

`ProvisioningWorkflow` (docs/04) drives one `OnboardingStateMachine`
instance per tenant through the primary path, and routes to `BLOCKED`
automatically the moment `SnapshotAssembler` reports missing configuration
or a failed snapshot application — the two systems are one integrated flow,
not two independent trackers that can drift out of sync.
