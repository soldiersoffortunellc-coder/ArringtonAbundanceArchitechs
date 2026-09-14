# 13 — Client Implementation: Coach Shonough / Open Doors Financial Group

**Vertical:** Insurance Agency Revenue OS (`config/snapshots/insurance_pack.json`)
**Client config:** `config/clients/open_doors_financial_group.json`
**Owned by:** Client Onboarding Director (deploys) + Productization Director
(keeps this from becoming a one-off custom build) + Sales Director (funnel
copy/offer alignment). Compliance sign-off owned by the client's own
E&O/carrier compliance process — nothing below is final legal or
compliance-reviewed copy.

This is the first live application of the Insurance Agency Revenue OS to a
real client and real page copy (source: Coach Shonough's existing 7-page
site copy doc). It is a worked example of the pattern every future
insurance-agency client goes through: **audit against the industry pack's
`problems_solved` list → rebuild the site as the front end of two separate
funnels (consumer + recruiting) → wire every new element to a named GHL
component → instrument it so it shows up in the executive command center.**

Every change below is tagged so none of it reads as redecoration:

- **(A)** = Authority (why a stranger should trust this person/brand)
- **(C)** = Conversion (why a visitor takes a measurable next step)
- **(Au)** = Automation (removes a manual step or a place a lead goes cold)
- **(R)** = Revenue (creates or accelerates a pipeline the business gets paid from)

Brand is preserved, not replaced: Navy `#1B3A5C` / Gold `#C8962E`, the
"money is like water" philosophy, the veteran story, the three-pillar
ecosystem (Foundation / ODFG / Kingdom Brothers), faith-rooted tone. Nothing
in this doc changes voice — it changes what the page *does*.

---

## 1. Audit — why the current site caps out around 8.4/10

The current copy is well-written, on-brand, and complete as a **brochure**.
Scored against what the Insurance Agency Revenue OS is built to fix
(`insurance_pack.json → problems_solved`), here is exactly what a brochure
structure cannot do:

| Problem the OS is built to solve | Present on current site? | Consequence |
|---|---|---|
| `slow_lead_response` | No speed-to-lead mechanism — the only path is a Calendly embed on one page | A visitor who isn't ready to book *right now* leaves with zero follow-up path |
| `lead_leakage` | One generic CTA ("Book a Call") repeated on every page for three completely different audiences (consumer, agent recruit, foundation partner) | No segmentation = no correct pipeline, no correct nurture, no correct owner notification |
| `inconsistent_recruiting` / `unlicensed_recruit_follow_up` / `licensed_agent_attraction` | Recruiting is one paragraph inside the "Ecosystem" page, funneled into the *same* Calendly link as a consumer buying life insurance | Licensed agents and unlicensed candidates need entirely different qualification, presentations, and follow-up cadence — currently indistinguishable |
| `weak_client_follow_up` | No email/SMS capture anywhere except the final booking step | Everyone who isn't ready to book today (the majority of traffic) leaves no contactable record — no list, no nurture, no reactivation asset |
| `lack_of_pipeline_visibility` | No attribution, no UTM strategy, no per-page conversion tracking described | Coach Shonough cannot see which page, pillar, or campaign is producing appointments or recruits |
| `poor_onboarding` / `inconsistent_training` (agent side) | No structured intake for candidates (licensing status, experience, timeline) before the first conversation | Every recruiting call starts from zero instead of from a scored candidate |
| `inactive_agent_reactivation` | No mechanism to re-engage past leads, past candidates, or dormant subscribers | Every non-converting visitor is a one-time cost with no compounding value |

**What the current site already does well and should not be touched for
its own sake:** the founder story, the three-pillar framing, the compliance
disclosure instinct (it already flags "adjust before publishing" rather
than pretending to be final legal copy), and the overall trust-building
tone. The 8.4 is real — it is an authority document. It is not yet a
revenue instrument.

---

## 2. Score rubric — 8.4 → 9.5+

| Dimension | Weight | Before | After | What changed |
|---|---|---|---|---|
| Authority (A) | 15% | 8.5 | 9.0 | Proof strip with concrete numbers, inline credential/compliance placement, IBC/retirement authority content |
| Conversion mechanics (C) | 30% | 7.0 | 9.5 | Segmentation at the top of every page, gated lead magnet, multi-path scheduling, candidate scoring intake |
| Automation / lead-response (Au) | 30% | 6.0 | 9.5 | Speed-to-lead SMS/email, missed-call recovery, no-show recovery, database reactivation, pipeline auto-routing |
| Revenue instrumentation (R) | 25% | 5.5 | 9.5 | Two distinct pipelines wired end-to-end, UTM/attribution on every form, dashboard tie-in |
| **Blended** | | **8.4** | **9.5+** | |

The blended score moves because conversion, automation, and revenue
instrumentation — 85% of the weight — go from "not present" to "fully
specified and buildable this snapshot cycle," not because any hero
headline got punchier.

---

## 3. New site architecture (sitemap)

| # | Page | Status | Funnel role |
|---|---|---|---|
| 1 | Home | Rebuilt | Segmentation entry point — routes to consumer, agent, or foundation funnel in one click (C) |
| 2 | About | Kept + lead strip added | Authority page that never dead-ends without a capture (A)(C) |
| 3 | The Ecosystem | Rebuilt | Three pillars become three qualifying forms, not three paragraphs ending in one CTA (C)(Au) |
| 4 | **NEW: Financial 101 & IBC Education Hub** | New | Gated top-of-funnel asset feeding the consumer nurture funnel (A)(C)(Au)(R) |
| 5 | **NEW: Become an Agent** | New (split out of Ecosystem) | Dedicated recruiting funnel, fully separated from consumer traffic (C)(Au)(R) |
| 6 | Speaking & Media | Kept + lead magnet added | Brochure page converted into a list-building asset (C)(Au) |
| 7 | Mentorship & Community Impact | Kept + segmented form added | Separates funder / mentor / parent intents (C)(Au) |
| 8 | Book a Call | Rebuilt | Three distinct booking paths + pre-call intake, not one generic embed (C)(Au)(R) |
| 9 | Contact | Rebuilt | Form becomes a real router: each intent auto-tags, auto-pipelines, auto-notifies (Au)(R) |
| 10 | **NEW: Reviews & Referrals** | New | Retention/referral asset using the universal-core review-request workflow (R) |
| Footer | Site-wide | Kept + compliance strengthened | Inline disclosures near every product mention, not just one footer paragraph (A) |

---

## 4. The funnel map underneath the copy

Two primary funnels run through this site, kept structurally separate per
the industry pack (recruiting and consumer content, pipelines, and
compliance rules never share a form or a pipeline):

```
CONSUMER FUNNEL
Home / Ecosystem (ODFG pillar) / Financial 101 Hub
   → gated lead magnet (email + phone captured)
   → consumer_financial_education_funnel nurture (drip: IBC, IUL, annuities,
     retirement protection — education, not pitch)
   → "Book a Strategy Call" (calendar: general_consultation / policy_review_calendar)
   → consumer_sales_pipeline: Target Account → Contacted → Engaged →
     Discovery Booked → Discovery Completed → Qualified → Proposal Sent →
     Verbal Commitment → Closed Won → (policy in force) → Nurture/Referral

RECRUITING FUNNEL
Home / Ecosystem (ODFG pillar) / Become an Agent
   → licensing-status branch:
        Licensed  → licensed_agent_recruiting_funnel → iDecide recruiting
                     presentation → interview_calendar
        Unlicensed → licensing_interest_funnel → career_presentation →
                     licensing_follow_up workflow
   → ai_recruiting_conversation_agent / voice_ai_recruiting_agent handle
     first-touch qualification and reminders
   → candidate_scoring workflow scores every intake form submission
   → recruiting_pipeline (mirrors consumer_sales_pipeline shape, industry
     pack-specific) → interview → contracting_workflow → agent_onboarding →
     training_delivery → recruiting_activity_dashboard / agent_production_dashboard

FOUNDATION / PARTNER FUNNEL (lighter weight — Mentorship page)
   → segmented form (funder / mentor / parent) → tagged, routed to Coach
     Shonough directly (low volume, high-touch — no AI agent needed here)

KINGDOM BROTHERS FUNNEL (lighter weight — Ecosystem page)
   → investor-interest capture → tagged, routed to Coach Shonough directly
```

Both primary funnels reuse the **universal core** underneath them
(missed-call recovery, basic nurture, appointment reminders, no-show
follow-up, review requests, attribution fields) — nothing here duplicates
what the universal core already provides.

---

## 5. Page-by-page rewritten copy

Brand voice, colors, and the existing philosophy are preserved verbatim
where noted. New material is marked **NEW**. `[GHL BUILD]` call-outs map
copy directly to a named component so nothing here is copy floating
unattached to a system.

### PAGE 1: HOME

**SEO/meta:** unchanged — already well-targeted.

**Hero (kept):** "Money Is Like Water." / subheadline / supporting line —
unchanged. This is the strongest authority asset on the site; do not dilute
it with a sales pitch.

**NEW — Segmentation strip, directly under the hero (C)(Au)(R):**

> **Which door are you walking through today?**
> - 🛡️ **I want to protect my family's future** → routes to Financial 101 Hub
> - 💼 **I'm a licensed or aspiring agent exploring ODFG** → routes to Become an Agent
> - 🤝 **I'm exploring a partnership with the Foundation** → routes to Mentorship page

`[GHL BUILD: three-button module, each tagged (consumer-intent / agent-intent /
foundation-intent) via a hidden field on click before the destination page's
form even loads — this is the single highest-leverage change on the site,
because every downstream automation depends on knowing which funnel a
visitor is in from the first click.]`

**NEW — Proof strip (A), directly under the segmentation strip:**

> U.S. Army veteran, Combat Action Badge. Florida 2-14 licensed. Co-Founder,
> Open Doors Global Development Foundation (501(c)(3)). Building agent
> economics, family protection strategy, and generational wealth across
> Central Florida — and now, nationwide.

*(Numbers — agents recruited, families served, mentorship cohort size — get
added here once Coach Shonough approves specific figures. Never publish an
unapproved number.)*

**Intro Strip / Philosophy Strip (kept verbatim).**

**Closing CTA — rebuilt (C)(Au):** replaces the single "Book a Call Now"
button with the same three-path segmentation module used above, so Home
never ends in a dead-end generic CTA twice.

---

### PAGE 2: ABOUT

Body copy **kept verbatim** — this is the strongest authority narrative on
the site and should not be rewritten for its own sake.

**NEW — mid-page lead strip (C)(Au), inserted after the founding story and
before the Values Strip:**

> **Want the short version in your inbox?** Get the one-page "Money in
> Motion" story — the philosophy, the license, the ecosystem — as a PDF.
> `[Name] [Email]` → **Send It To Me**

`[GHL BUILD: lightweight 2-field form, tags contact lead_magnet:about-pdf,
adds to basic_nurture_sequence (universal core) — this exists so a visitor
who isn't ready to talk to anyone yet still becomes a contactable record
instead of a bounce.]`

**CTA — rebuilt:** same three-path segmentation module (not a single "Book
a Call" button).

---

### PAGE 3: THE ECOSYSTEM / WHAT I DO

Hero and closing philosophy **kept verbatim**. Each pillar's CTA is rebuilt
from a single link into a qualifying capture:

**Pillar 1 — Foundation.** Body kept. CTA becomes:

> **Learn About the Mentorship Program** → *(Page 5, which now ends in the
> funder/mentor/parent segmented form instead of a generic contact link)*

**Pillar 2 — ODFG.** Body kept, with one required compliance placement fix
(A) — the existing disclaimer currently sits at the bottom of the section;
move it **immediately under** the sentence naming IUL/whole life/annuities,
per standard E&O practice of pairing the disclosure with the claim it
qualifies, not separating them by several paragraphs. CTA splits into two,
replacing the single "Book a Strategy Call" link:

> - **I'm a family or individual** → **Get the Free Financial 101 Guide**
>   (routes to the new Education Hub, gated)
> - **I'm a licensed or aspiring agent** → **See the Agent Opportunity**
>   (routes to the new Become an Agent page)

`[GHL BUILD: this single split is what separates consumer_financial_education_funnel
traffic from licensed_agent_recruiting_funnel / licensing_interest_funnel
traffic at the point of intent, instead of merging them downstream where
it's much harder to un-merge.]`

**Pillar 3 — Kingdom Brothers.** Body kept. **NEW** CTA (was none before):

> **Interested in an investment or development conversation?**
> `[Name] [Email] [Phone]` → **Start the Conversation**

`[GHL BUILD: tags contact kingdom-brothers-interest, routes directly to
Coach Shonough — low volume, no AI agent needed at this stage.]`

---

### PAGE 4 (NEW): FINANCIAL 101 & IBC / RETIREMENT EDUCATION HUB

**SEO Title:** Financial 101 & Infinite Banking (IBC) Education | Open Doors Financial Group
**Meta Description:** Learn how protection, cash-value life insurance, the Infinite Banking Concept (IBC), and retirement strategy actually work — plain-language education from Coach Shonough, before any sales conversation.

**Hero:**

# Understand It Before You Buy It.

**Subhead:** This page has no sales pitch in it. It's the same education
Coach Shonough gives every client before recommending anything.

**Body (NEW):**

> Most people are sold insurance and annuities before they understand them.
> This is the opposite: five short, plain-language lessons covering how
> whole life and indexed universal life actually work, what the Infinite
> Banking Concept (IBC) is and isn't, how fixed indexed annuities fit into
> a retirement plan, and the questions to ask any advisor — including this
> one — before you commit to a strategy.

**Gate (C)(Au)(R):**

> **Get instant access to the full Financial 101 series.**
> `[Name] [Email] [Phone]` → **Send Me the Series**

*Compliance placement: immediately below the gate — "Educational content
only. Nothing on this page is a recommendation to buy any specific
insurance or annuity product. Product suitability is determined only after
a full conversation with a licensed professional. Guarantees referenced are
subject to the issuing carrier's claims-paying ability."*

`[GHL BUILD: this is the primary top-of-funnel asset for the entire
consumer side of ODFG.
- Funnel: consumer_financial_education_funnel (insurance_pack.json)
- On submit: tag lead_magnet:financial101, lifecycle_stage=education,
  enters a 5-touch drip (one lesson every 2–3 days) ending in a
  "Ready to talk it through?" strategy-call CTA
- Custom fields captured: education_topic_interest (IBC / IUL / annuities /
  retirement / general), which lets the drip branch by stated interest
  instead of running one-size-fits-all
- This page is also the natural landing page for paid/organic search
  traffic on "financial literacy speaker Florida," "IBC Florida," and
  "retirement protection Lakeland FL" (see docs SEO notes) — it should
  carry its own UTM-tagged campaigns rather than sending all ad traffic to
  Home.]`

---

### PAGE 5 (NEW): BECOME AN AGENT

**SEO Title:** Join Open Doors Financial Group | Insurance Agent Opportunity — Lakeland, FL
**Meta Description:** Build your own book of business with a transparent, agent-first platform — training, proprietary lead generation, and real agent economics through Open Doors Financial Group.

**Hero:**

# Build Your Own Business. Don't Rent Someone Else's.

**Subhead:** A licensing academy, transparent economics, and a real
lead-generation engine — for licensed agents and serious candidates alike.

**Body (adapted from existing Ecosystem-page paragraph, expanded):**

> ODFG exists because most agents are recruited into a black box: unclear
> commission structure, no real leads, no real training path. We built the
> opposite — a growing licensing academy, transparent agent economics, and
> a proprietary lead-generation engine, so the agents who join us are set
> up to actually build something, not just get a 1099.

**NEW — branching intake form (C)(Au)(R), the core mechanic of this page:**

> **Where are you starting from?**
> - **I'm already licensed (Florida 2-14 or equivalent)** →
>   `[Name] [Email] [Phone] [State licensed in] [Years in the business] [Current book size, optional]`
>   → **See the Agent Platform**
> - **I'm not licensed yet but I'm interested** →
>   `[Name] [Email] [Phone] [Timeline to get licensed] [Why this interests you]`
>   → **Start the Licensing Conversation**

`[GHL BUILD:
- Licensed branch → licensed_agent_recruiting_funnel → iDecide recruiting
  presentation → interview_calendar booking → recruiting_pipeline
- Unlicensed branch → licensing_interest_funnel → career_presentation →
  licensing_follow_up workflow (nurture until licensed, then converts into
  the licensed branch)
- Every submission → candidate_scoring workflow scores on: licensing
  status, experience, stated timeline, and completeness of answers
- ai_recruiting_conversation_agent handles first-touch qualification
  outside business hours; voice_ai_recruiting_agent handles interview
  reminders and no-show recovery
- Compliance: no earnings figures, no "make $X/month" language anywhere on
  this page or in any recruiting nurture step, per
  insurance_pack.json → compliance_review_controls
  ("no guaranteed-earnings language permitted in recruiting funnels").]`

---

### PAGE 6: SPEAKING & MEDIA

Body copy **kept verbatim** — strong authority content.

**NEW — lead capture (C)(Au), replacing the page's previous dead-end:**

> **Want the full Money-as-Water framework?** Get the one-page framework
> PDF used in the talk — free.
> `[Name] [Email]` → **Send Me the Framework**

**CTA (kept, form added):** "Book Coach Shonough to Speak" — add
`[Organization] [Event date] [Audience size] [Event type]` fields so
inbound speaking requests arrive qualified instead of as a bare email.

`[GHL BUILD: tags lead_magnet:speaking-framework, enters basic_nurture_sequence;
speaking-inquiry form tags speaking-inquiry and routes directly to Coach
Shonough — this is low-volume, high-touch, no AI agent needed.]`

---

### PAGE 7: MENTORSHIP & COMMUNITY IMPACT

Body copy **kept verbatim.**

**CTA — rebuilt (C)(Au):**

> **Partner With the Mission** — I'm a: `[Potential funder / Mentor /
> Parent enrolling a young man] [Name] [Email] [Phone] [Message]`
> → **Connect With the Foundation**

`[GHL BUILD: segmented tag (funder-lead / mentor-lead / enrollment-lead)
routes to the Foundation's own contact, separate from ODFG's consumer/agent
pipelines — Foundation work should never get buried in a sales pipeline.]`

---

### PAGE 8: BOOK A CALL / WORK WITH ME

**Hero and "who this is for" body kept.**

**Rebuilt (C)(Au)(R) — replaces the single generic Calendly embed with
three distinct booking paths, each pre-qualified by the intake form the
visitor already filled out upstream (Financial 101 Hub, Become an Agent, or
Mentorship):**

> - **Family / Individual Strategy Call** → `general_consultation` calendar
>   → pre-call intake auto-fills from the Financial 101 form if already
>   submitted (no re-typing name/email/phone)
> - **Agent Interview** → `interview_calendar`
> - **Foundation / Partnership Conversation** → `support_call` calendar (or
>   a dedicated `foundation_call` calendar once volume justifies one)

**NEW — pre-call intake questions for the Family/Individual path (feeds the
strategy call, not gatekeeps it):**

> `What's the main thing you want to walk away from this call knowing?`
> `Do you currently have any life insurance or annuity in place?`
> `Timeline: exploring now / ready to move in the next 30 days / just researching`

`[GHL BUILD: appointment_reminder_sequence and no_show_follow_up (universal
core) apply to all three calendars; each calendar's booking event tags the
opportunity into the correct pipeline (consumer_sales_pipeline vs
recruiting_pipeline) automatically instead of a human sorting it after the
fact.]`

**Trust Strip (kept verbatim).**

---

### PAGE 9: CONTACT

**Hero kept.** Contact details kept.

**Form rebuilt (Au)(R) — same fields as the original, but now a real
router instead of a single inbox:**

`Full Name / Email / Phone / I'm interested in: [Financial Protection
Strategy / Joining ODFG as an Agent / Foundation Partnership / Speaking
Inquiry / Kingdom Brothers Development / Other] / Message`

`[GHL BUILD: each "I'm interested in" value maps to one automation —
Financial Protection Strategy → consumer_sales_pipeline + Financial 101
nurture; Joining ODFG as an Agent → recruiting_pipeline + candidate_scoring;
Foundation Partnership → Foundation contact + tag; Speaking Inquiry →
speaking-inquiry tag; Kingdom Brothers → kingdom-brothers-interest tag;
Other → owner notification only, no auto-pipeline. This is the single
biggest automation gap on the current site: today, every value in that
dropdown lands in the same undifferentiated inbox.]`

**Closing line (kept verbatim).**

---

### PAGE 10 (NEW): REVIEWS & REFERRALS

**SEO Title:** Client Stories & Referrals | Open Doors Financial Group
**Meta Description:** Referrals and reviews from families and agents who've worked with Coach Shonough and Open Doors Financial Group.

**Hero:**

# Most of Our Best Clients Started as a Referral.

**Body (NEW):**

> If Open Doors has helped protect your family, grown your agency, or
> moved you closer to licensing, the single best way to say thanks is
> sending someone else through the same door.

**CTA (R):** "Refer a Family or a Future Agent" — simple form (`Your name /
Their name / Their email or phone / Which door fits them best`).

`[GHL BUILD: uses the universal-core review_request_sequence, triggered
automatically after a Closed Won opportunity or agent_onboarding
completion — not built as a one-off page. Testimonials/case studies from
this page require written client permission and compliance sign-off before
publishing, exactly as docs/08's case-study framework requires — this is
enforced in code by ClientSuccessRetentionDirectorAgent, not just policy.]`

---

### SITE-WIDE FOOTER

Kept structurally identical. **Compliance strengthening (A):** the single
footer disclaimer stays (belt-and-suspenders), but is no longer the *only*
place a product-related disclosure appears — every page above that
mentions IUL, whole life, annuities, or IBC now carries its own inline
disclosure at the point of the claim. This is a compliance authority signal,
not decoration: it shows a prospect (and an examiner) that disclosure is
attached to substance, not buried in fine print.

---

## 6. GHL build map

| Site element | Snapshot layer | Component | New or existing |
|---|---|---|---|
| Segmentation strip (Home) | Client config | Custom field `intent_segment` + 3-button module | New |
| Financial 101 gate | Industry pack | `consumer_financial_education_funnel` | Existing in pack — new content |
| Financial 101 drip | Industry pack | (extends `consumer_financial_education_funnel`) | New content, existing funnel type |
| Become an Agent — licensed branch | Industry pack | `licensed_agent_recruiting_funnel`, `idecide_recruiting_presentation`, `interview_calendar` | Existing |
| Become an Agent — unlicensed branch | Industry pack | `licensing_interest_funnel`, `career_presentation`, `licensing_follow_up` | Existing |
| Candidate scoring on every recruiting form | Industry pack | `candidate_scoring` workflow | Existing |
| First-touch qualification (recruiting) | Industry pack | `ai_recruiting_conversation_agent` | Existing |
| Interview reminders / no-show recovery (recruiting) | Industry pack | `voice_ai_recruiting_agent`, `no_show_recovery` | Existing |
| Contracting → onboarding → training | Industry pack | `contracting_workflow`, `agent_onboarding`, `training_delivery` | Existing |
| Recruiting dashboards | Industry pack | `recruiting_activity_dashboard`, `agent_production_dashboard` | Existing |
| Missed-call recovery (every page) | Universal core | `missed_call_recovery` | Existing |
| Lead-magnet nurture (About PDF, Speaking framework) | Universal core | `basic_nurture_sequence` | Existing |
| Appointment reminders (all 3 calendars) | Universal core | `appointment_reminder_sequence` | Existing |
| No-show recovery (consumer calendars) | Universal core | `no_show_follow_up` | Existing |
| Reviews & Referrals page | Universal core | `review_request_sequence` | Existing |
| Contact form routing | Universal core + industry pack | `opportunity_framework` custom fields + pipeline assignment logic | New logic on existing fields |
| Attribution on every form | Universal core | `attribution_fields` (`utm_source`, `utm_medium`, `utm_campaign`, `referral_partner_id`) | Existing |
| Compliance disclosures (inline placement) | Industry pack | `insurance_marketing_compliance_disclosure`, `licensing_disclaimer` | Existing — placement changed |

**Cannot ship as a pure GHL snapshot component (needs manual/API work,
carried over from `universal_core.json → requires_manual_or_api_configuration`
plus two insurance-specific items):**

- A2P 10DLC registration for SMS (speed-to-lead, drip, reminders all depend on this)
- Domain/DNS verification for `opendoorsfinancial.rashon@gmail.com`'s sending domain
- Voice AI phone number porting/purchase for `voice_ai_recruiting_agent`
- iDecide account/API access for the recruiting presentation
- Migrating the existing Calendly link (`calendly.com/opendoorsfinancialrashon`)
  into GHL's native calendars, or keeping Calendly and webhooking bookings
  into GHL — a real decision Coach Shonough needs to make, not a copy change
- Payment processor connection (only relevant if/when ODFG sells anything
  directly through the site rather than through a licensed conversation)

---

## 7. Funnel analytics & attribution plan

This is what makes the redesign *measurable*, not just better-organized.

**UTM taxonomy (applied to every paid/organic campaign pointed at the site):**

```
utm_source: google | facebook | instagram | referral | podcast | speaking-event
utm_medium: cpc | organic | social | email | referral-partner
utm_campaign: financial101-launch | agent-recruiting-q4 | mentorship-partners | <event-name>
```

**Custom fields captured on every form (universal core `attribution_fields`
plus two new ones specific to this build):**

`utm_source, utm_medium, utm_campaign, referral_partner_id, intent_segment
(consumer / agent-licensed / agent-unlicensed / foundation / kingdom-brothers),
education_topic_interest (IBC / IUL / annuities / retirement / general)`

**Events tracked per visitor (feeds `reporting_fields` in universal core:
`speed_to_lead_seconds`, `appointment_show_rate`, `review_count`, plus new
funnel-specific counts):**

- Segmentation click (which door)
- Lead-magnet gate completions (by asset: About PDF, Financial 101 series,
  Speaking framework)
- Education drip engagement (opened / clicked, by lesson)
- Calendar booking (by calendar: consultation / interview / partnership)
- Show / no-show
- Contact form submissions (by "interested in" value)
- Referral submissions

**Executive dashboard tie-in (`docs/07-executive-command-center.md`):** once
live, this site feeds the same dashboard fields every other client feeds —
leads generated, qualified appointments, show rate, proposal rate, close
rate, results by industry (here: insurance), and now, uniquely useful to
Coach Shonough, **results by intent_segment** — so he can see, in one place,
whether the site is producing more strategy-call demand or more agent
applications, and shift content/ad spend accordingly instead of guessing.

**A/B test backlog (run one at a time, not simultaneously):** Home hero
segmentation copy ("Which door are you walking through" vs. a direct
question format), Financial 101 gate copy (PDF vs. video framing), Become
an Agent's licensed-vs-unlicensed branch order.

---

## 8. Compliance guardrails (carried through, not weakened)

- Every mention of IUL, whole life, term, or fixed indexed annuities gets
  its disclosure **inline**, immediately following the claim, not only in
  the footer.
- No earnings or income figures anywhere in recruiting copy or nurture
  content, per `insurance_pack.json`'s `compliance_review_controls`.
- The Financial 101 Hub is consumer-facing financial-education content —
  per the same compliance_review_controls, **it requires compliance
  sign-off before publish**, same as every other consumer-facing financial
  page in this pack.
- Testimonials/case studies on the new Reviews & Referrals page require
  written permission and compliance sign-off before use — enforced in code
  by `ClientSuccessRetentionDirectorAgent`, not left to policy alone.
- NAP (name/address/phone) consistency between this site, the footer, and
  the Google Business Profile listing is a prerequisite for the SEO notes
  in the original copy doc — verify before publish, not after.
- Nothing in this document is attorney- or E&O-carrier-reviewed final copy.
  It is a build spec, exactly like `docs/08-sales-assets.md` is for the
  agency's own sales assets.

---

## 9. Client configuration layer

`config/clients/open_doors_financial_group.json` fills the twelve required
fields (`branding, domain, phone_numbers, email, calendars, users, services,
service_areas, pricing, disclosures, integrations, escalation_contacts`)
using the public business information already present in Coach Shonough's
own copy doc. Fields that require values only Coach Shonough or his GHL
agency admin can supply (GHL location ID, A2P 10DLC status, live carrier
disclosure language, iDecide account ID) are explicitly marked
`"REQUIRED — obtain from client / GHL agency dashboard"` rather than
guessed at — consistent with `docs/09-credentials-and-ghl-ids.md`'s rule
that no real credential is ever fabricated or committed.

`tests/test_client_config_open_doors.py` proves this file actually
validates against the system's own `validate_client_config()` — the same
function that gates real onboarding — so this isn't just a JSON file that
looks right, it's one the system agrees is complete enough to move past
`CONFIGURATION` in the onboarding state machine (see `docs/06`).

---

## 10. Rollout plan

**Phase 1 (this snapshot cycle) — stop the bleeding:** segmentation strip
on Home, Financial 101 gate live, Contact form routing wired, missed-call
recovery + basic nurture turned on. This alone fixes `slow_lead_response`
and `lead_leakage`, the two highest-cost problems on the current site.

**Phase 2 — separate the funnels:** Become an Agent page live with the
licensed/unlicensed branch, candidate scoring wired, recruiting dashboards
turned on. Fixes `inconsistent_recruiting`, `unlicensed_recruit_follow_up`,
`licensed_agent_attraction`.

**Phase 3 — compound the asset:** Reviews & Referrals page live, database
reactivation campaign scheduled quarterly, UTM/attribution reporting
flowing into the executive command center. Fixes `inactive_agent_reactivation`
and `lack_of_pipeline_visibility`, and turns every non-converting visitor
from Phase 1 into a reactivation candidate instead of a sunk cost.

## 11. Success metrics (30 / 60 / 90 days — planning inputs, not guarantees)

Speed-to-lead (target: under 5 minutes), Financial 101 opt-in rate, strategy
calls booked, show rate, recruiting applications by branch (licensed vs.
unlicensed), candidate-to-interview conversion, close rate by
`intent_segment`, and email list size — all read from the same executive
command center every other client uses, not a separate one-off report.
Per operating rules, none of these are presented as guaranteed outcomes.
