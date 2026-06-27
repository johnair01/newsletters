# Surfaces — per-view hi-fi specs

One spec per screen. The **Home** is fully specified (it is V1 and approved). The four
content surfaces are specified structurally — open the matching `design-reference/*.html`
file for pixel-level detail and exact copy, and match the tokens in `design-system.md`.

Global chrome on every surface: sticky **`NLNav`** (top) and **`NLFooter`** (bottom). Nav
spine: **Start here · Newsletters · Articles · The Show**. Content max-width **1180px**,
section padding ~`56–78px 44px`. Light/dark theme state lives at the page root.

---

## Home — "Start here" (V1, approved)

**File:** `design-reference/Newsletters - Home.html` (+ `newsletters/home.jsx`,
`newsletters/home-atoms.jsx`). **Purpose:** the single front door — lead with the *why*,
prove it with the *wow* (live personalization), hand off to the *how* (engine + code).

Page state: `theme` (light/dark) and `who` (which persona the demo is viewing as). Sections,
in order:

1. **Hero (`#start`)** — eyebrow "An open framework for working in the open"; H1 (sg-display
   **72px / 1.03**, max 960px): *"Turn information into **conversation.** Conversation into
   **action.**"* (italic emphasis on the two nouns). Lead paragraph 18.5px/1.6, max 620px.
   Two buttons: primary **"See it in action →"** (→ `#newsletters`), ghost **"View on
   GitHub"** with git glyph. Mono line: "Open source · MIT · self-hostable · human-in-the-loop
   by design". Bottom hairline.

2. **Why this exists** — two-column (`1fr 1fr`, gap 56): left a `SectionDivider` + serif
   30px statement *"In a world flooded with information, **relevance wins.**"*; right two
   body paragraphs (the "knowledge evaporates" + "semantic bridge" copy).

3. **Personalization demo (`#newsletters`)** — *the signature interaction.* Accent
   `SectionDivider` "See it in action · audience-aware by design"; H2 ~44px *"Everyone gets
   the newsletter that's **about them.**"* Grid `300px 1fr`, gap 36:
   - **Left (sticky):** "Viewing as" label + three persona buttons. Active button: card bg,
     3px left border in the persona accent, soft shadow. Below: an ink-bordered inset
     "Same source — All three letters are cut from one reviewed record — the latency-regression RCA."
   - **Right:** the generated letter card (top border 3px in persona accent), re-rendered with
     a `sg-fade` on `who` change. Header: kicker (persona accent) + "The weekly signal" +
     `ProfileChip`. Body: a `Tag` (the lead tag), serif H3 ~30px title, lead paragraph, then a
     list of `[title, body]` items separated by hairlines, then a brand-light "Why you're
     seeing this" inset.
   - **Personas** (`NL_PERSONAS`): `maintainer` (MK, "Owns the service", **brand-primary**) ·
     `contributor` (NC, "First month", **green**) · `lead` (EL, "Sponsors the team",
     **accent**). The exact per-persona letter copy (`LETTERS` in `home.jsx`) is the canonical
     content — preserve it; it demonstrates "same facts, different emphasis."
   - Below the demo: three `sg-card`s — **Codify once / Tune to a corpus / Re-cut on send**,
     numbered, left-accented in the three persona colors.

4. **The publishing engine (`#engine`)** — `SectionDivider` "How it publishes · human in the
   loop"; a 4-column bordered pipeline (`NL_PIPELINE`): **Ingest → Distill → Review →
   Publish**, each cell numbered (mono, accent) with title + description, an `IconArrow`
   bridging cells, 3px brand left-border on the first. Below: "The review gate, on every
   artifact:" + a `GateBadge current="In Review"`.

5. **The four surfaces (`#surfaces`)** — accent `SectionDivider` "One conversation, many
   surfaces"; a bordered list (`NL_SURFACES`), each row `76px 1fr 240px`: big serif index
   (01–04), name + italic tail + body, right-aligned cadence meta + "Enter →" link. Order:
   The Show / Newsletters / The Articles / The Report.

6. **The thesis** — `SectionDivider` "The thesis · five practices of working in the open"; a
   5-column bordered grid (`NL_PRACTICES`): Public storytelling / Community contribution /
   Prototyping in the wild / Reflection & documentation / Remixable products.

7. **For developers (`#developers`)** — accent `SectionDivider` "For developers · clone it,
   point it at your work"; two-column. Left: a GitHub repo lockup
   (`johnair01 / newsletters · public`), the Source/Distillation/Surface explainer, "Clone the
   repo" + "Read the spec" buttons. Right: two `PromptBlock`s — `install` (`pip install
   newsletters`) and `synthesize.py` (the API example from `architecture.md` §2).

8. **Invitation** — surface-low panel, 3px accent left-border, serif italic 27px CTA +
   "Get started on GitHub" / "Replay the demo" buttons.

**Responsive:** two-up grids and the demo grid collapse to one column ≤980px; nav links hide
≤720px; the practice grid steps 5→2→1. See the `<style>` block in the HTML + `tokens.css`.

---

## The Show — recorded conversations

**File:** `design-reference/Signals Show.html` (+ `signals/show.jsx`). **Signal color:**
accent (terracotta). **Purpose:** an episode page — the raw practitioner conversation
everything is distilled from. **Cadence:** new episode every other week. Structurally: episode
hero (title, guests via `ProfileChip`, `GateBadge`), a chaptered transcript/onboarding with
timestamps, and a "fan-out" block showing what this episode produced (Report/Article/Letter).
Match the accent-colored eyebrows and `live`/`featured` tags. Open the file for chapter copy
and timestamps (illustrative — replace with real episode data).

## Newsletters — the weekly signal

**File:** `design-reference/Signals Newsletter.html` (+ `signals/newsletter.jsx`). **Signal
color:** amber. **Purpose:** the weekly digest — one shared edition plus the personalized
variant. ~6-min read. The personalization mechanic is demonstrated on the Home; this surface
is the full standalone letter: masthead, the lead story, secondary items, KPI strip
(`KpiBlock`), pull quote (`sg-quote`), and the "why you're seeing this" rationale. Each issue
carries a `GateBadge`. Reuse the persona/`LETTERS` model for per-reader re-cuts.

## The Articles — peer-reviewed write-ups

**File:** `design-reference/Signals Article.html` (+ `signals/article.jsx`). **Signal color:**
ink. **Purpose:** a durable, peer-reviewed write-up; every claim traced to a source,
human-validated before publish; published to the Library. Layout is container-query driven
(`.article-root` / `.article-body` `240px 1fr` with a sticky aside TOC). Includes a `peer`
tag, an action/byline row (`.article-action`), traced claims, prompt/code blocks, and print
styles (it's meant to be saved as PDF). The aside collapses ≤1040px (container width, not
viewport). See `Signals Article - Sidebar Options.html` in the project for sidebar variants
that were explored (not copied here).

## The Report — the reusable record

**File:** `design-reference/Signals Report.html` (+ `signals/report.jsx`). **Signal color:**
brand / live. **Purpose:** the flagship structured record a surface is built on (the worked
example is a downtime/latency root-cause analysis), regenerated per event so the next person
inherits the shape, not a blank page. Includes the live `GateBadge`, KPI strips, a
four-system reconciliation narrative, traced claims, and the fan-out to the other surfaces.
This is the `Surface(kind="report")` made visible — the most data-dense view.

## Learning — the reviewed record, re-cut for someone new

**Signal color:** green. **Purpose:** take an *already-reviewed* record and re-cut it for a
newcomer or a training cohort — the fifth surface and the most distilled re-cut (distance 4).
The audience is the `product-spec.md` §"A new contributor": *"How we debug here + the reusable
record + glossary"* — first month, needs orientation. It is a `Surface(kind="learning")` made
visible, authored from the `learning` template (`L-NNN` id, the row above at line 176).

**The faithfulness contract (the crux — read this first).** A teaching surface naturally wants
to explain and simplify, but **faithful, not suggestive** (CLAUDE.md) forbids editorializing or
inventing prose. The learning re-cut therefore **SELECTS, ORDERS, and LINKS already-reviewed,
traced claims — it never authors new factual prose.** Every device below is a re-arrangement of
the reviewed record, not new content:

- **Progressive disclosure = ORDERING/LAYERING, not new content.** The three layers are ordered
  DOM sections — **Start here** → **Prerequisites** → **Going deeper** — each populated with
  existing traced claims (`ClaimsBlock`s). There is **no JavaScript** and no interactive toggles
  (the static-faithful renderer, Phase 11); the layers are just deterministic ordering. The
  order is derived from each claim's **`confidence` + `topics`** — a stable, total sort key, no
  schema change, byte-stable on double-render (SITE-06).
- **The in-context glossary = term → its DEFINING traced Claim.** Each glossary term renders a
  typed `GlossaryBlock` whose definition **IS a reviewed `Claim` with a `Trace`**, surfaced in
  context — never an invented `str` of prose. A term with **no traced defining claim is not
  glossed**: it is routed to `surface.missing[]` and shown in the honesty panel, never fabricated.
- **Prerequisite context = links, not exposition.** Prerequisite material is reached by **links
  to prerequisite records/claims** (the provenance device), not by new explanatory text.
- **Un-traceable → not taught.** Anything that cannot trace to a reviewed claim does not appear
  as taught content; it surfaces in the **honesty** panel (the shared "What's not here / not
  verified" device documented below). If it can't trace, it isn't taught.

**Provenance — every concept links to its source (LEARN-02).** This surface makes the trace
literal: every concept, glossary term, and onboarding step links back to its source claim/record.
It is **pure reuse** of the Phase 9–11 devices — `link_for_source`, the claim/span rendering, the
claim badges, and the honesty panel all run unchanged on the learning surface. No new provenance
machinery; the same gate-visible review applies (claim beside its verbatim trace, badges for
stale/unfaithful claims).

**Placement / template fields.** `name="learning"`, `display_name="Learning"`, `signal_color`
GREEN, `cadence=ON_DEMAND`, `scope=AudienceScope.INDIVIDUAL`, `review_policy` light, `distance=4`
(the most-distilled re-cut), `personalized=True` (the `Corpus.emphasis` re-cut hook only — same
facts, newcomer-shaped emphasis). Slots: `start_here / prerequisites / glossary / going_deeper`.
Registered in `templates.py`; the Site collection, the `L-NNN` ledger, and the board/nav pick it
up like the other four surfaces.

### The OnboardingPath — an ordered learning track (LEARN-03)

An **OnboardingPath** sequences several records/surfaces into an ordered learning track for a
newcomer or cohort: `OnboardingPath(id, title, audience_label, steps: list[OnboardingStep(slug,
label)])` — an **ORDERED list of slug refs**. Rendered as a sequenced track page with **prev**/
next navigation *within the track* (reusing the Phase 9 prev/next device, resolving each step via
`Site.by_slug`).

Crucially, **an OnboardingPath is NOT a Surface and has NO own review gate.** It publishes nothing
new — it is navigation *over surfaces that have already passed the gate*. Because it authors no
claims and emits no published distillation, the no-auto-publish invariant is not implicated by the
path itself; the gate lives on each surface it sequences. It lives in its own
`src/newsletters/learning.py`, separate from the report/article/show templates, to keep its
identity-only import boundary clean.

---

## The review view — every surface shows its work (PROV-03)

Every rendered surface makes the review gate *visible*, not merely enforced. Two devices,
both always present, neither behind a click:

**Claim beside its verbatim trace (SC3).** In a `ClaimsBlock`, each claim renders its
addressed `Trace.span` inline — the verbatim source snippet sits in a quoted mono
`.claim-span` box directly under the claim text, *by default* (no toggle, no JavaScript).
An un-addressed Rev1 trace (empty span) shows its evidence chip alone — never an empty box
(faithful, not suggestive). A claim that has **drifted** from its live source carries an
inline amber `STALE` badge; a claim whose addressed span does **not contain** the claim text
carries an inline amber `unfaithful` badge (`SpanContainmentFaithfulness`). A clean
addressed-entailed-non-stale claim carries no badge. So an unfaithful claim is visible
*without a click*. The `{source_id: Source}` lookup the STALE check needs is derived from the
surface's own `traces`, so no caller signature changes.

**The "What's not here / not verified" honesty panel.** After the blocks, every surface
renders one amber `.honesty` panel listing, never collapsed:

- every `Surface.missing[]` entry — the *unsubstantiated / un-entailed* material; and
- for every traced `Source` with an `extraction` record, each `unextracted[]` drop as
  `locator.display` + `reason` — the *coverage gaps* an adapter could not read.

When both lists are empty the same panel shell renders a positive "Fully traced — nothing
outstanding" confirmation: the panel's *presence* is the proof on every surface. Uses
`--color-amber` with a mono uppercase eyebrow; pure markup, no JS, every interpolation
HTML-escaped (XSS-safe). The shipped Rev1 corpus is all-clean, so it renders the positive
confirmation and no badges fire — the gate-fires proof lives in the renderer tests.

**Block scope.** The claim-beside-span device applies to `ClaimsBlock` claims; the honesty
panel applies to the surface as a whole regardless of its blocks. Both render identically in
draft, in-review, and published state — review is shown at every gate, not only at publish.

---

## The Hub / Library (reference)

**File:** `design-reference/Signals Hub.html` (+ `signals/hub.jsx`). The converged hub that
ties surfaces together / the archive. Useful as the **Library** view (durable archive of
published Articles and records) and as a model for cross-surface navigation
(`.hub-body 248px 1fr`, sticky aside, `.hub-moment` and `.hub-surface` rows). Treat as the
listing/archive surface in the build.

### ID conventions (stable, content-derived — never positional)

Every surface in the Library carries two stable identifiers, both independent of its position
in any list. The Library renders the **`ref`** in each row's lead slot (it used to render a
positional `01..NN`, which renumbered whenever surfaces were reordered — the rot point).

| Surface type | `ref` format | Example | Notes |
|--------------|--------------|---------|-------|
| Report | `R-NNN` (3-digit) | `R-001` | sequential per type |
| Article | `A-NNN` (3-digit) | `A-001` | sequential per type |
| Show / episode | `EPNN` (2-digit) | `EP01` | sequential per type |
| Newsletter | keyed by `issue` + `date` | issue 02 · 2026-06-18 | **cadenced** — no sequential ref |
| Learning | `L-NNN` (3-digit) | `L-001` | sequential per type |

- **`slug`** — the content-derived canonical link key (a deterministic `slugify` of the title;
  for the Rev1 corpus it defaults to the existing `Surface.id` for backward-compatibility, so no
  committed `*.html` link rots). It is the URL: `href == f"{slug}.html"`.
- **`ref`** — the human, per-type identifier above, **assigned once from the append-only ledger**
  (`content/rev1/ids.json`) and **never renumbered** when surfaces are reordered or inserted.
  Newsletters are cadenced: their identity is `issue` + `date`, not a sequential ref.

**Why content-stable, not positional:** identity must be deterministic and durable — a link,
a citation, or a board reference to `R-002` must keep pointing at the same record no matter how
many surfaces are added before it. The full `Site → Collection → Page` content model and the
ledger mechanics are documented in `docs/architecture.md`.

## The Proposal (reference)

**File:** `design-reference/Signals Proposal.html` (+ `signals/proposal.jsx`). The operating-
model proposal ("Start here" in the older Signals flow). In the converged product the home
absorbs the charter, but this file documents the **operating rhythm** (daily working group →
task force → weekly review → intern review) and the slot-marked template approach — useful
context for the personalization/cadence logic and for any future standalone "how it publishes"
surface.

---

## Navigation & IA layer

Added 2026-06-27 from the **"Signals — Navigation & IA"** design package
(`design-reference/signals-navigation/`), which specifies the connective tissue the older
per-surface specs didn't: how a reader moves *between* surfaces of one record and from a claim
to its evidence. Built in `web/`. The mechanics below are the contract; body prose is
illustrative.

- **Five reader surfaces.** The package presents one record as **Report · Article · Newsletter ·
  Show · Learning** — note the fifth, `learning` (see `architecture.md §1`). Per-surface accent:
  Report → blue, Article → ink, Newsletter → amber, Show → terra, Learning → green.
- **Global nav spine.** Persistent near-black chrome on every page: logo → Home, six primary
  destinations (Start here · Library · Newsletters · Articles · The Show · Learning), a "Jump
  to… ⌘K" button, a breadcrumb bar (`Home / <view>`), and a mobile hamburger drawer.
- **Fan-out switcher** ("See this record as") — the signature control; a sticky **segmented
  control** (shipped treatment A) that swaps the current record between its surfaces, preserving
  context. The active segment carries the destination surface's accent underline.
- **Provenance: claim → evidence → back** — every published claim carries an inline **EV**
  trigger that opens a **slide-in evidence panel** (shipped treatment A) showing the claim, its
  trace (source + locator), and the source span, with a clear return and an "open source
  surface" jump.
- **Library** — browsable index, by **record** or **topic**, with review-state filter chips
  (state is a badge + filter, never the way in) and empty states.
- **Onboarding** — an ordered guided path (Show → Report → Article → Learning) with a stepper.
- **⌘K command palette** — searchable jump across surfaces, pages, and records.
- **Review gate is first-class in the IA** — surfaces carry their `Draft · In Review ·
  Published` state as a badge; a Draft surface renders the **gated edge state** (`/gated`):
  claims aren't readable and can't be cited until they clear the gate.

The prototype runtime (`support.js`, the `<x-dc>`/`<sc-*>` tags, the harness toolbar) is
reference only — **not** ported. See `design-reference/signals-navigation/README.md` for the
full visual spec and `web/README.md` for the implementation.

## Sample data is illustrative

Across all surfaces the worked example (a latency-regression RCA the four dashboards
disagreed about), the personas, metric values, IDs, dates, and quotes are **sample content**
chosen to demo the system well. Keep the *shapes* and the *voice*; wire the *values* to real
data. The slot/template approach (org names, system names, metrics as config) is documented in
the project's `handoff/SLOTS.md`.
