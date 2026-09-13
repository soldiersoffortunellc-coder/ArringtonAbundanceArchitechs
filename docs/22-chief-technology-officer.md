# Chief Technology Officer — Technology Division

Structured data: `config/agents/chief-technology-officer.json`. This is
the first role added outside the Revenue division defined in
`docs/10-revenue-agent-definitions.md` — the original brief specified only
the CRO and its 6 subordinates; the CTO is a peer division the owner
requested afterward, and this doc + config is where it becomes a real,
versioned part of the org chart rather than a one-off chat aside.

## Org chart (updated)

```
Owner
  ├─ Chief Revenue Officer (Revenue division)
  │    └─ 6 subordinate revenue agents — docs/10-revenue-agent-definitions.md
  └─ Chief Technology Officer (Technology division)
       (single role for now; scope below covers both the live GHL build
       and this repo's engineering — split into subordinates later only
       if the owner asks for that)
```

## Scope: both halves, one role

Per the owner's direction, the CTO owns two things that were previously
either implicit or split:

1. **The live GHL technical build** — the actual correctness of every
   client subaccount (starting with the Open Doors Financial Group
   insurance pilot, `docs/17-credentials-and-ghl-ids.md`), and the
   platform-gap/workaround registry
   (`config/live-pilots/odfg-ghl-workflow-status.json`) that build
   produces. This was previously just "whoever is building it reports
   gaps" — the CTO now owns that registry and any workaround design
   before it's reused.
2. **This repo's engineering** — `src/`, `tests/`, and eventually the live
   `GhlApiAdapter` that replaces `dryRunAdapter` behind the unchanged
   `Provisioner` interface (`docs/09-saas-provisioning-architecture.md`).

## Division of labor with existing roles (no overlap)

| Question | Owner |
|---|---|
| What should the snapshot contain (workflows, pipelines, forms)? | Productization Director |
| How is that content actually built/implemented, safely, in GHL and in code? | **CTO** |
| What price, offer, or guarantee do we sell? | CRO |
| Is this client's compliance checklist complete? | Client Onboarding Director (unchanged — CTO cannot override a compliance gate) |
| Is a workaround pattern safe to reuse on the next workflow/client? | **CTO** |

## Deployment: where and when

This role is defined two places, deliberately:

1. **In this repo, now** — `config/agents/chief-technology-officer.json`
   and this doc. This is the durable, versioned definition — the same
   treatment every other C-Suite role gets.
2. **In the live Cowork/GHL session, now** — this repo cannot reach into a
   separate Cowork conversation. The practical deployment step is pasting
   the operating brief (`config/agents/cto-cowork-operating-brief.md`) as
   an instruction into that session (the one running the Open Doors
   Financial Group build, or a new one) — it takes effect on that
   session's next turn. There is no separate "install" step; a Cowork
   session's behavior is defined by what's in its own instructions/
   context, not by a deployment pipeline.

## Authorization boundary (unchanged)

The CTO's technical readiness sign-off is necessary but never sufficient
for live activation — the owner's explicit authorization is still required
before any live billing, messaging, or provisioning goes live
(`docs/21-risks-and-assumptions.md`).
