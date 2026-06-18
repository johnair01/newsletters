# Phase 12 — Context & Decisions (Learning & Onboarding Surface)

**Goal:** Add a first-class learning/onboarding surface that re-cuts reviewed records for newcomers and
training cohorts — progressive disclosure, traceable concepts, ordered onboarding paths — making org/
codebase knowledge digestible to people new to it.

**Requirements:** LEARN-01 (learning preset: progressive disclosure + prerequisite context + in-context
glossary), LEARN-02 (every concept links back to its source record/claim — trace explanation→evidence),
LEARN-03 (an onboarding path sequences multiple records into an ordered learning track).
**Depends on:** the typed model (Surface/SurfaceTemplate/Distillation/Claim/Trace), Phase 8 (Site/Page,
the `L-NNN` Learning id convention already in the ledger), Phase 9–11 (renderer + provenance/lineage
devices + the self-contained site), the personalization re-cut (`Corpus.emphasis`/`claims_for`).

## Current state (verified)
- 4 `SurfaceTemplate`s (SHOW/REPORT/ARTICLE/NEWSLETTER, distance 0–3); registry in templates.py. The
  `L-NNN` Learning id convention exists (Phase 8) but there is NO `learning` template yet.
- `docs/surfaces.md` has the `L-NNN` id row but NO learning-surface spec section (a SPEC GAP to fill).
  `docs/product-spec.md` frames the newcomer audience ("How we debug here + the reusable record +
  glossary", §"A new contributor").
- Re-cut exists: `Distillation.claims_for(audience)` orders claims by `Corpus.emphasis` — "same facts,
  new emphasis." The learning preset is a NEW kind of re-cut (newcomer-shaped), not just reordering.

## The faithfulness crux (decide first — this governs the whole phase)
A "teaching" surface naturally wants to explain/simplify — but **faithful-not-suggestive** forbids
editorializing or inventing prose. Resolution: the learning re-cut **SELECTS, ORDERS, and CONTEXTUALIZES
already-reviewed, traced claims** — it never authors new factual prose.
- **Progressive disclosure = ORDERING/LAYERING** of traced claims (simplest/prerequisite → deeper), not
  new content. Each layer's items are existing claims with their traces.
- **Glossary = term → its DEFINING traced claim/source** (the definition IS a reviewed claim with a
  Trace, surfaced in-context), NOT an invented definition. A term with no traced definition is NOT
  glossed (or routed to `missing[]`), never fabricated.
- **Prerequisite context = links to prerequisite records/claims** (traced), not new exposition.
- LEARN-02 makes this literal: every concept/glossary term/step links back to its source claim/record
  (reuse `link_for_source` + traces). If it can't trace, it isn't taught (honesty panel shows the gap).

## Decisions (design — research to validate against the spec + renderer)
1. **A `learning` SurfaceTemplate** (templates.py) — `name="learning"`, display_name e.g. "Learning",
   high `distance` (a re-cut, most-distilled), a newcomer audience scope. Register it (so the Site
   Collection + `L-NNN` ledger + the 4-destination nav/board pick it up). Research the exact fields.
2. **The learning preset** — a function (e.g. `learning_surface(distillation/record, ...) -> Surface`)
   that re-cuts a reviewed record into a learning surface: ordered progressive-disclosure sections
   (Start here / Prerequisites / Going deeper), an in-context glossary block (term → traced defining
   claim), prerequisite-context links — ALL traced (the crux above). No JS (progressive disclosure is
   ordered sections, not interactive toggles, per the static-faithful renderer).
3. **Concept→source provenance (LEARN-02)** — reuse Phase 9–11 devices: each concept/glossary term/
   step renders a claim→source link (`link_for_source`) + verbatim trace; un-traceable → not taught /
   honesty panel. (Possibly the typed-locator forward note pays off — assess.)
4. **The onboarding path (LEARN-03)** — a new typed `OnboardingPath`/`Track`: an ORDERED sequence of
   records/surfaces (steps) for a newcomer/cohort, with step order + prev/next. Rendered as a sequenced
   track page. Research the cleanest model (a list of Page/surface refs in order + a title/audience).
5. **Renderer + dogfood** — render the learning surface + the onboarding path (reuse render.py devices;
   minimal new rendering, design-system tokens, no JS, deterministic, self-contained/no external calls).
   Author a learning surface in the dogfood corpus (re-cut an existing reviewed record for newcomers) +
   one onboarding path sequencing ≥2 records. Build into content/rev1/site (byte-stable, SITE-06).
6. **Scope:** the learning preset + onboarding path + the surface/template + renderer + a dogfood
   example + the spec section. NOT the V3 PulseIQ learning engine (out of scope — only the typed
   re-cut/preset). NO AI. Read-only/no-auto-publish/all prior contracts hold.

## Hard rules in play
- **Faithful, not suggestive** — the learning re-cut SELECTS/ORDERS/links traced claims + traced
  glossary definitions; it NEVER invents explanatory prose. Un-traceable → not taught (honesty panel).
- **Every concept traces to evidence** (LEARN-02 makes provenance literal on the learning surface).
- **No auto-publish / gate intact**; **AI-optional** (preset is deterministic, zero AI); **no external
  calls** (self-hosted fonts, Phase 11); **determinism / byte-stable** (SITE-06).
- **Specs are source of truth** — add the learning-surface + onboarding-path spec to docs/surfaces.md
  in the same change (fill the gap).

## Research note (dispatch BEFORE planning)
Validate against the LIVE codebase + spec: the exact `learning` SurfaceTemplate fields (distance/scope/
signal color) consistent with the 4 existing templates + the `L-NNN`/Site/board wiring; the cleanest
FAITHFUL learning preset (progressive disclosure as ordering, glossary as traced-claim definitions,
prerequisite links) reusing `claims_for`/emphasis + the provenance devices; the `OnboardingPath` model
+ how it sequences records and renders (reuse prev/next from Phase 9); how the dogfood corpus can supply
a real newcomer re-cut + a ≥2-record path; the docs/surfaces.md learning spec to add; and the tests
(faithful: no invented prose; LEARN-02 every concept traces; LEARN-03 ordered path). Confirm zero new
dependency + no external calls. Record in 12-RESEARCH.md.
