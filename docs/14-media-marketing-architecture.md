# 14 — AI Media & Marketing Division: Architecture

## Agent roster (extends the existing 13-agent C-Suite to 19)

| Agent | Reports to | Owns |
|---|---|---|
| CMO (extended) | CEO | Strategy, calendar balance, the 6 subordinates below, submission for approval — never publishes directly |
| Brand Voice & Content Strategist | CMO | Scripts/captions/hooks, structured from supplied facts only |
| AI Video Production Director | CMO | VideoGenerationJob lifecycle via AvatarVideoAdapter/VoiceAdapter |
| Marketing Compliance Officer | CMO | Risk scoring, prohibited-phrase blocking, mandatory-approval gating |
| Social Distribution Director | CMO | Per-platform SocialPost/PublishingJob, duplicate-publish prevention |
| Lead-Conversion Director | CMO | CTA → GHL pipeline/stage routing, LeadAttribution |
| Marketing Analytics Officer | CMO | PerformanceMetric collection, evidence-only OptimizationRecommendation |

## System diagram

```mermaid
flowchart TB
    subgraph CSuite["C-Suite (existing, unchanged)"]
        CEO
        CRO
        CFO
        COO
        CTO
        CCO
        CMO["CMO (extended)"]
    end

    subgraph MediaDivision["AI Media & Marketing Division (new)"]
        BV["Brand Voice & Content Strategist"]
        VID["AI Video Production Director"]
        COMP["Marketing Compliance Officer"]
        SOC["Social Distribution Director"]
        LCD["Lead-Conversion Director"]
        ANA["Marketing Analytics Officer"]
    end

    CMO --> BV & VID & COMP & SOC & LCD & ANA

    subgraph Pipeline["Campaign State Machine"]
        IDEA --> BRIEF_CREATED --> SCRIPT_DRAFTED --> BRAND_REVIEW --> COMPLIANCE_REVIEW
        COMPLIANCE_REVIEW --> REVISION_REQUIRED --> SCRIPT_DRAFTED
        COMPLIANCE_REVIEW --> HUMAN_APPROVAL_REQUIRED
        HUMAN_APPROVAL_REQUIRED -->|"executive_approver only"| APPROVED --> VIDEO_GENERATING --> VIDEO_REVIEW --> SCHEDULED --> PUBLISHED --> PERFORMANCE_TRACKING --> OPTIMIZATION_COMPLETE
        HUMAN_APPROVAL_REQUIRED --> REJECTED
    end

    BV -->|drafts| SCRIPT_DRAFTED
    COMP -->|reviews| COMPLIANCE_REVIEW
    VID -->|submits job on APPROVED| VIDEO_GENERATING
    SOC -->|schedules on SCHEDULED| PUBLISHED
    LCD -->|attributes on PUBLISHED| GHL[(GHL: pipelines, tags,\nopportunities, calendars)]
    ANA -->|reads| PerformanceData[(PerformanceMetric)]

    subgraph Providers["Provider Adapters (dry-run/mock by default)"]
        GHLA[GHLAdapter]
        AVA[AvatarVideoAdapter]
        VOA[VoiceAdapter]
        SPA[SocialPlatformAdapter]
        STA[StorageAdapter]
        ANAA[AnalyticsAdapter]
        IDA[IDecideAdapter]
    end

    LCD --> GHLA
    VID --> AVA & VOA
    SOC --> SPA & GHLA
    ANA --> ANAA
    MediaDivision -.->|content/link/webhook events| IDA

    subgraph iDecideFlow["iDecide Journey (see docs/15)"]
        AICLONE["AI Clone Video"] --> SOCIALCTA["Social CTA"] --> GHLCAPTURE["GHL Lead Capture"]
        GHLCAPTURE --> IDLINK["Personalized iDecide Link"] --> IDPRES["Interactive Presentation"]
        IDPRES --> BEHAVIOR["Viewer Behavior Captured"] --> QUALIFY["AI Lead Qualification"]
        QUALIFY --> TAGGING["GHL Tagging/Segmentation"] --> FOLLOWUP["Correct Follow-Up Workflow"]
        FOLLOWUP --> CONVERSION["Appointment / Interview / Application"]
    end

    IDA --> QUALIFY
    LCD --> TAGGING

    subgraph Controls["Governance (shared with existing Revenue OS)"]
        PERM[PermissionRegistry\n+5 new roles]
        GC["GlobalControls\n.guard() + .guard_publishing()"]
        AUDIT[(AuditEvent trail\nper campaign)]
    end

    CMO -.-> PERM
    MediaDivision -.-> GC
    Pipeline -.-> AUDIT
```

## Data flow summary

1. CMO balances the weekly calendar against `content_mix.json` and assigns
   an idea to a content pillar + business + platform set.
2. Brand Voice & Content Strategist drafts a `ScriptVersion` from supplied
   `key_messages` only (never invents facts).
3. CMO brand-reviews, then Marketing Compliance Officer scores risk and
   determines the mandatory-approval gate.
4. `ApprovalQueue` (RBAC via `PermissionRegistry`) is the only path from
   `HUMAN_APPROVAL_REQUIRED` to `APPROVED` — a permission check succeeding
   is never confused with an actual approval (the state machine itself
   still gates the transition).
5. AI Video Production Director submits to `AvatarVideoAdapter` (consent
   required) once `APPROVED`.
6. Social Distribution Director schedules per-platform posts (dedup by
   content hash) once `VIDEO_REVIEW` passes.
7. Lead-Conversion Director routes resulting leads/contacts to the correct
   GHL pipeline/stage via `GHLAdapter`.
8. Marketing Analytics Officer collects `PerformanceMetric` (tagged by data
   quality) and produces evidence-based `OptimizationRecommendation`s —
   submitted for approval, never auto-applied.
9. iDecide (where confirmed usable — see docs/15) sits between step 6/7 and
   adds an interactive qualification layer feeding richer intent data back
   into step 7's routing decision.
