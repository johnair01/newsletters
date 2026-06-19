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
   (`nneibaue / newsletters · public`), the Source/Distillation/Surface explainer, "Clone the
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

---

## The Hub / Library (reference)

**File:** `design-reference/Signals Hub.html` (+ `signals/hub.jsx`). The converged hub that
ties surfaces together / the archive. Useful as the **Library** view (durable archive of
published Articles and records) and as a model for cross-surface navigation
(`.hub-body 248px 1fr`, sticky aside, `.hub-moment` and `.hub-surface` rows). Treat as the
listing/archive surface in the build.

## The Proposal (reference)

**File:** `design-reference/Signals Proposal.html` (+ `signals/proposal.jsx`). The operating-
model proposal ("Start here" in the older Signals flow). In the converged product the home
absorbs the charter, but this file documents the **operating rhythm** (daily working group →
task force → weekly review → intern review) and the slot-marked template approach — useful
context for the personalization/cadence logic and for any future standalone "how it publishes"
surface.

---

## Sample data is illustrative

Across all surfaces the worked example (a latency-regression RCA the four dashboards
disagreed about), the personas, metric values, IDs, dates, and quotes are **sample content**
chosen to demo the system well. Keep the *shapes* and the *voice*; wire the *values* to real
data. The slot/template approach (org names, system names, metrics as config) is documented in
the project's `handoff/SLOTS.md`.
