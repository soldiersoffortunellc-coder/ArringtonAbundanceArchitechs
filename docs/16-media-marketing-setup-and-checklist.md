# 16 — Setup, Checklists, Troubleshooting, Deployment, Rollback

## Local development setup

```bash
git clone <repo> && cd ArringtonAbundanceArchitechs
cp .env.example .env               # fill in values later; empty is fine for dry-run
python3 -m unittest discover -s tests -t .    # 155 tests, zero pip installs required
python3 scripts/run_demo.py                    # full 19-agent Revenue OS cycle
python3 scripts/run_marketing_demo.py          # one sample campaign to HUMAN_APPROVAL_REQUIRED
```

No database, no migrations, no `pip install` step exist or are required —
see docs/13 for why (no DB in this repo; everything is in-memory + JSON
config, matching the existing convention).

## Creating your first real campaign

```python
from csuite.orchestrator import RevenueOperatingSystem

ros = RevenueOperatingSystem()  # dry-run GHLAdapter + all provider adapters, by default
result = ros.run_media_division({
    "brand_voice_content_strategist": {
        "campaign_id": "camp_manual_1", "brand_id": "coach_rashon",
        "platforms": ["instagram", "tiktok"], "key_messages": ["<your actual message here>"],
        "cta_text": "DM WEALTH",
    },
})
```
See `scripts/run_marketing_demo.py` for the full walk-through including the
compliance gate and approval queue.

## Approving, revising, rejecting, or pausing a campaign

```python
# role must be one your PermissionRegistry grants the relevant action to —
# config/role_permissions.json ships: executive_approver, compliance_reviewer,
# content_operator, read_only_analyst (plus the existing owner/agent roles).
ros.approval_queue.approve(campaign_id, role="executive_approver", actor_id="rashon", reason="approved")
ros.approval_queue.reject(campaign_id, role="executive_approver", actor_id="rashon", reason="off-brand")
ros.approval_queue.request_revision(campaign_id, role="compliance_reviewer", actor_id="jane", reason="unsupported claim in body")
ros.approval_queue.pause_campaign(campaign_id, role="executive_approver", actor_id="rashon", reason="pending legal review")
```
An API call succeeding here does **not** mean the campaign moved forward —
`ApprovalQueue` still routes through `CampaignStateMachine.transition()`,
which refuses the move unless the campaign is actually sitting in
`HUMAN_APPROVAL_REQUIRED` (`tests/marketing/test_approval_queue.py`).

## Activating / deactivating publishing (the kill switch)

```python
ros.global_controls.pause_publishing("reason")   # blocks video submission + social scheduling only
ros.global_controls.resume_publishing()
ros.global_controls.pause("reason")              # full system pause — blocks EVERYTHING, revenue ops included
```

## GHL configuration checklist

1. Copy `config/marketing/ghl_marketing_config.template.json` →
   `ghl_marketing_config.json` (git-ignored) and fill in every `PLACEHOLDER`.
2. Build the 3 pipelines (`config/marketing/pipelines/*.json`) by hand in
   GHL — the public API does not support creating them (docs/12) — then
   record the real `ghl_pipeline_id`/`ghl_stage_id` values back into those
   files.
3. Create the custom fields listed in `ghl_marketing_config.template.json`
   and `config/marketing/idecide/field_map.template.json`; record real
   field IDs.
4. Build the 17 workflow blueprints in `config/marketing/
   workflow_blueprints.json` inside the GHL UI (or ship them in a
   snapshot) — record workflow IDs.
5. Confirm social account mappings for each platform GHL Social Planner
   will publish to; verify TikTok/YouTube/LinkedIn support for your account
   specifically (`SocialPlatformAdapter.PLATFORM_CAPABILITIES` flags these
   `"verify_current_tos"`).
6. Run `python3 scripts/check_ghl_connection.py` (from the earlier GHL
   live-connection work, docs/12) to confirm auth before anything else.
7. Validate: `validate_ghl_marketing_config(json.load(open("config/marketing/ghl_marketing_config.json")))`
   must return `[]` before this config is trusted for live use.

## Compliance configuration checklist

1. Replace every `PLACEHOLDER` disclosure text in
   `config/marketing/disclosure_requirements.json` with real,
   attorney/compliance-approved language (by carrier, agency, state,
   platform, product, campaign type as applicable).
2. Fill in `compliance_reviewer_of_record` in each brand profile
   (`config/marketing/brand_profiles/*.json`) — currently `NEEDS_INPUT`.
3. Review `config/marketing/prohibited_claims.json`'s `blocked_phrases` and
   `claim_categories` with your actual compliance/legal function; extend as
   needed (nothing here is legal advice).
4. Confirm the "every AI-clone post in the first 30 days requires human
   approval" rule's 30-day window is enforced by whatever schedules
   `within_first_30_days` in the caller's context — it is a caller-supplied
   fact today, not derived from a stored "campaign started" date, because
   there is no persistence layer yet (docs/13). Wire this to a real clock
   once a datastore exists.

## Credentials I (the business owner) must supply — nothing is fabricated

| Credential | Where it's used | Currently |
|---|---|---|
| `GHL_ACCESS_TOKEN` (+ agency/location IDs) | `GHLAdapter` live calls | Not supplied — see docs/09, docs/12 |
| Real GHL pipeline/stage/calendar/workflow/field/tag IDs | `config/marketing/*.json` | All `PLACEHOLDER` |
| Avatar-video provider API key (e.g. HeyGen) | `AvatarVideoAdapter` live calls | Not supplied |
| Voice provider API key (e.g. ElevenLabs), if used | `VoiceAdapter` live calls | Not supplied |
| iDecide account access + confirmation of its actual API/webhook options | `IDecideAdapter` live calls | Not supplied; capability matrix UNVERIFIED |
| Social platform API keys, only if GHL Social Planner can't cover a platform | `SocialPlatformAdapter` live calls | Not supplied |
| `ConsentAuthorization` records for Coach Rashon's likeness/voice | Gates every `AvatarVideoAdapter`/`VoiceAdapter` call | Not yet created — required before ANY real video job |
| Real disclosure text (carrier/agency/state/product-specific) | `config/marketing/disclosure_requirements.json` | All `PLACEHOLDER` |
| Compliance reviewer name(s) of record | Brand profiles | `NEEDS_INPUT` |

## Troubleshooting

- **"KeyError" loading a brand/pillar/pipeline config** → the `*_id` you
  passed doesn't match a file in `config/marketing/` — check spelling
  against the JSON filenames exactly.
- **`ConsentRequiredError` on video/voice submission** → no
  `consent_authorization_id` was passed. This is correct behavior, not a
  bug — create a `ConsentAuthorization` record first.
- **`PermissionDeniedError` on approval actions** → the `role` passed isn't
  granted that action in `config/role_permissions.json`. Check the role →
  action mapping; don't grant broader access to work around it.
- **`InvalidCampaignTransitionError`** → the campaign isn't in a state that
  allows the transition you tried (e.g. trying to `APPROVED` a campaign
  still in `COMPLIANCE_REVIEW`). Check `campaign.audit_trail` for its real
  current state.
- **`SystemPausedError` / `PublishingPausedError`** → a kill switch is
  engaged. Check `global_controls.pause_reason` /
  `.publishing_pause_reason`.
- **`WebhookSignatureError`** → the signing secret or raw payload bytes
  don't match what was actually sent — confirm you're verifying against
  the exact raw request body, not a re-serialized copy (re-serializing JSON
  can change byte-for-byte content and break HMAC verification).

## Deployment checklist

1. Provision a real datastore behind `CampaignStore`/`TenantRegistry`/
   `BillingLedger` (currently in-memory — see docs/13's documented
   limitation).
2. Supply every credential in the table above via your deployment
   platform's secret manager — never commit `.env`.
3. Implement `GHLAdapter._live_call`'s remaining gaps and each provider
   adapter's `_live_call` against its real API once credentials exist.
4. Run the full test suite in CI on every change:
   `python3 -m unittest discover -s tests -t .`
5. Deploy with `dry_run=True` everywhere by default; flip to live per
   integration only after a human explicitly authorizes it
   (`live_authorized=True` + a real adapter instance — see docs/12's
   "Recommended order of operations").
6. Point `dashboard/index.html` (or a new marketing-specific view) at a
   real API surface serving `RevenueOperatingSystem.run_cycle()` /
   `run_media_division()` output.

## Rollback plan

Every change in this division is additive (see docs/13's file-by-file
list) — nothing existing was deleted or had its interface broken. To roll
back:
1. Revert the specific commit(s) that introduced `src/csuite/marketing/`,
   `src/csuite/providers/`, `src/csuite/agents/marketing/`, and the
   `config/marketing/` tree.
2. Revert the additive edits to `src/csuite/agents/cmo.py` (subordinates +
   `run_media_division` — the original `run()` method is untouched, so even
   a partial revert leaves existing Revenue OS behavior intact),
   `src/csuite/orchestrator.py`, `src/csuite/platform/controls.py`
   (`pause_publishing`/`guard_publishing` are additive methods), and
   `config/role_permissions.json` (5 added roles).
3. Re-run `python3 -m unittest discover -s tests -t .` — the original 78
   Revenue OS tests must still pass on their own regardless of whether the
   marketing-division tests are present, since nothing in the Revenue OS
   depends on the Media & Marketing Division.
4. No data migration is needed to roll back, because no persistent store
   was introduced (everything is in-memory for the life of one process).
