---
phase: 12-learning-onboarding-surface
plan: 04
subsystem: render
tags: [render, glossary, onboarding-path, faithfulness, learning-surface, provenance, no-js]

# Dependency graph
requires:
  - phase: 12-learning-onboarding-surface
    plan: 01
    provides: "typed GlossaryBlock/GlossaryTerm (definition = traced Claim) in the Block union"
  - phase: 12-learning-onboarding-surface
    plan: 03
    provides: "learning_surface() preset (emits ClaimsBlock x3 + GlossaryBlock, un-glossable -> missing[]) + OnboardingPath/OnboardingStep models"
  - phase: 09-11
    provides: "render.py provenance/navigation devices: link_for_source, _ev_chip, _claim_spans, _claim_badge, _prevnext, _honesty_panel, _page, _e; self-hosted fonts (WORK-01)"
provides:
  - "render._block_html GlossaryBlock branch — each term's DEFINING traced Claim renders through the reused claim devices (linked ev-chip + verbatim span), so every glossary definition shows its provenance (LEARN-02)"
  - "render.render_path(path, *, site, theme) — an OnboardingPath rendered as an ordered track over already-gated surfaces, each step resolved via Site.by_slug, with in-track prev/next (LEARN-03); unresolved step -> plain text, never a dead link"
  - "render._claim_row(claim, site, sources) — the single shared claim-row renderer now used by BOTH the ClaimsBlock and GlossaryBlock branches"
affects: [12-05-dogfood]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Provenance-by-reuse: a glossary definition is rendered through the EXACT claim devices a finding uses (_claim_row -> _ev_chip/_claim_spans/_claim_badge), so faithfulness/links are identical and there is one code path, not two"
    - "Faithful-on-the-HTML: the no-invented-prose guarantee is asserted on the RENDERED main region (set-membership of every rendered string in the source claims) + no STALE/unfaithful badge, not just on the model"
    - "Progressive disclosure as DOM ORDER: three ordered <section>-equivalent block divs (Start here/Prerequisites/Going deeper), zero <details>/onclick, exactly one <script> (theme toggle)"
    - "Faithful navigation: an unresolved track step renders plain text (mirror _fanout_row), never href=\"None\"; in-track prev/next reuses the _prevnext first-no-prev/last-no-next boundary contract"

key-files:
  created: []
  modified:
    - src/newsletters/render.py
    - tests/test_learning.py

key-decisions:
  - "Extracted _claim_row() from the ClaimsBlock branch so the GlossaryBlock branch renders each definition through the IDENTICAL device chain — one source of truth for claim+provenance rendering (RESEARCH 'Don't Hand-Roll')"
  - "render_path replicates the _prevnext boundary semantics over path.steps rather than calling _prevnext directly (which is Collection/Page-indexed); the track's neighbours are the adjacent RESOLVED steps, so prev/next point at the neighbouring surface href"
  - "render.py now imports OnboardingPath/OnboardingStep from .learning and SignalColor from .templates; render -> learning (not the reverse) keeps the graph acyclic and AI-free (lint-imports 1 kept/0 broken)"
  - "Both tasks landed in one feat commit: the test module imports render_path at module level, so Task 1's tests cannot COLLECT until render_path exists — an artificial split would leave an uncollectable intermediate state (see Deviations)"

patterns-established:
  - "A teaching surface's glossary cannot show invented prose on the page: every definition is a traced Claim rendered through the same linked-ev-chip device as any finding — provenance is structural, not bolted on"

requirements-completed: [LEARN-01, LEARN-02, LEARN-03]

# Metrics
duration: 5min
completed: 2026-06-19
---

# Phase 12 Plan 04: Render the learning surface (GlossaryBlock + render_path) Summary

**The typed GlossaryBlock (Plan 01) and OnboardingPath/learning preset (Plan 03) now have a renderer: a GlossaryBlock branch in `_block_html` renders each term's DEFINING traced Claim through the reused claim devices (linked evidence chip + verbatim span), the learning surface's three sections render as ordered DOM sections with no JS, and `render_path()` renders an OnboardingPath as an ordered track over already-gated surfaces with in-track prev/next — faithfulness proven on the RENDERED HTML, zero external calls, zero new dependency.**

## Performance
- **Duration:** ~5 min
- **Started:** 2026-06-19T05:29:13Z
- **Completed:** 2026-06-19T05:34:40Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 2 (0 created; render.py + tests/test_learning.py)

## Accomplishments
- **LEARN-01 (render):** the learning surface renders three ORDERED DOM sections (Start here / Prerequisites / Going deeper — the ClaimsBlocks the preset emits) plus one in-context GlossaryBlock; progressive disclosure is ORDER, not toggles (no `<details>`, no `onclick`, exactly one `<script>` = the theme toggle).
- **LEARN-02 (render):** each GlossaryTerm renders its name + its DEFINING traced Claim through the SAME devices a finding uses — `_ev_chip` yields an `<a class="ev-chip" href=...>` (the repo-blob source link) and `_claim_spans` renders the verbatim span box. Un-glossable terms (`Flux`) never reach the body — they live in `surface.missing[]`, surfaced by the reused `_honesty_panel`.
- **LEARN-03 (render):** `render_path(path, *, site, theme)` resolves each `OnboardingStep` via `Site.by_slug` and renders an ordered, numbered track; each resolved step is an `<a href="{page.href}">`, with in-track prev/next (first step no Previous, last no Next). An unresolved step renders as plain text — never a dead `href="None"`.
- **FAITHFUL on the HTML:** every rendered string in the surface's main region is a traced reviewed claim (set-membership against the source Distillation); no STALE/unfaithful badge on the clean surface; `Flux` is never a glossary term.
- **NO-EXTERNAL-CALL:** both the learning surface and the path page load zero off-box resources (self-hosted relative `fonts/*.woff2`), and carry only the theme-toggle `<script>`.
- Refactor bonus: extracted `_claim_row()` from the ClaimsBlock branch so both branches share one provenance code path; this cleared the 1 pre-existing render.py mypy error (12 -> 9 baseline errors).

## Task Commits
Each task committed atomically (TDD; commit + push after each):
1. **RED scaffold (both tasks):** `c864ff2` (test) — failing render tests (import error: `render_path` absent)
2. **GREEN — GlossaryBlock branch + render_path (Tasks 1 & 2):** `8b52128` (feat)
3. **Test refinement (fixtures + faithful negatives):** `2f21cd5` (test)

_No standalone REFACTOR commit — the `_claim_row` extraction is part of the GREEN feat (it is how the GlossaryBlock branch reuses the claim devices)._

## Downstream contract (for Wave 4 — Plan 05 dogfood + build_site)

**GlossaryBlock render structure** (`render._block_html`, `kind == "glossary"`):
```html
<div class="block">
  <h3 class="block-h">{heading}</h3>
  <div class="gloss-term">
    <div class="gloss-name">{term}</div>
    <ul>{ _claim_row(term.definition) }</ul>   <!-- linked ev-chip + verbatim span -->
  </div>
  ...
</div>
```
- Each term's definition is rendered by the shared `_claim_row(claim, site, sources)` — IDENTICAL to a ClaimsBlock row, so provenance (the `<a class="ev-chip" href=...>` source link from `link_for_source`, the `.claim-span` verbatim box, the STALE/unfaithful `.claim-badge`) renders on every glossary definition.
- **How provenance renders on a glossary term:** the defining Claim's `evidence` Traces go through `_ev_chip` → a file-path locator becomes a repo-blob `<a>`; a session/in-site locator resolves via `site.by_slug` to `{slug}.html`; neither → plain text (faithful). Pass `site=` into `render_surface` (the build path) so in-site source links resolve.
- New CSS classes added (design-system GREEN, `--radius:0`, no JS): `.gloss-term`, `.gloss-name` (and `.gloss-term .claim` resets the left border so the term's left-accent leads).

**`render_path()` signature + output:**
```python
def render_path(path: OnboardingPath, *, site: Site, theme: str = "light") -> str
```
- Resolves every `step.slug` via `site.by_slug` ONCE (Page or None), preserving track order.
- Output: a `_page()` shell (GREEN signal, `active="Start here"`, nav targets resolved from `site`) with a masthead (`path.title` + `path.audience_label` + step count) and a `<div class="track">` of numbered `.track-step` rows.
  - resolved step → `<a class="track-link" href="{page.href}">{label or page.title}</a>` + a `.track-kind` mono tag; in-track prev/next as `.track-nav` links to the neighbouring resolved step's href.
  - unresolved step → `<span class="track-link">{label or slug}</span>` (plain text, no link).
- The path carries no claims of its own (navigation over already-gated surfaces, A5), so it renders NO honesty panel — each linked surface carries its own.
- New CSS: `.track`, `.track-step`, `.track-num`, `.track-link`, `.track-kind`, `.track-nav`.

**For Plan 05 (build_site + content/rev1/site regen):** wire the dogfood learning surface (via `learning_surface()` on `report-datamodel`) and the onboarding path (`show-ep01 → report-datamodel → <learning re-cut>`) into `build_site`, calling `render_surface(..., site=site, page=page)` for the learning Page and `render_path(path, site=site)` for the track page, then regenerate `content/rev1/site` (byte-stable). This wave is render.py + tests ONLY — `content/rev1/site` was deliberately NOT regenerated here.

## Decisions Made
- **`_claim_row` extraction (shared device path):** rather than re-implement claim+evidence rendering inside the GlossaryBlock branch, I pulled the ClaimsBlock row body into `_claim_row()` and call it from both branches. This is the literal application of RESEARCH "Don't Hand-Roll" — one provenance code path means a glossary definition can never diverge from a finding in how it links/escapes/badges.
- **render_path replicates `_prevnext` boundary semantics rather than calling it:** `_prevnext(site, page)` indexes a Page within its own Collection; a track's neighbours are the adjacent track STEPS, not collection siblings. I reused the first-no-prev/last-no-next CONTRACT (and point prev/next at the neighbouring resolved step's `page.href`) without forcing the Collection-shaped device onto a different domain.
- **One feat commit for both tasks** — see Deviations.

## Deviations from Plan

### Process deviations (no user permission needed)

**1. [Process] Task 1 and Task 2 GREEN landed in one feat commit (`8b52128`)**
- **Found during:** Task 1 GREEN gate.
- **Issue:** `tests/test_learning.py` imports `render_path` at MODULE level (`from newsletters.render import render_path, render_surface`). Until `render_path` exists, the whole test module fails to COLLECT — so Task 1's four render tests cannot run in isolation without Task 2's function present.
- **Resolution:** One RED commit (`c864ff2`) covered both tasks' tests; one GREEN feat (`8b52128`) landed both the GlossaryBlock branch and `render_path`. Both tasks' `<verify>` `-k` selections were run and pass independently. Splitting would leave an uncollectable intermediate commit with no value.
- **Files:** `src/newsletters/render.py`, `tests/test_learning.py`. **Commit:** `8b52128`.

**2. [Rule 1 - Bug] Test fixture produced spurious STALE badges**
- **Found during:** Task 1 GREEN (first full test run).
- **Issue:** the first `_render_record()` minted each claim's Trace against `Source(transcript=text)` (per-claim text) but carried a single combined-transcript Source in `traces[]`. The live source hash then differed from the Trace's pinned hash → every claim rendered a `STALE` badge, and a naive `"Flux" not in body` assertion mis-fired.
- **Fix:** one `Source` per claim, shared between `Trace.from_source` and `Distillation.traces[]`, so the live hash matches the pinned hash (no spurious STALE). Replaced the over-broad `"Flux" not in body` assertion with the precise faithful negatives (no STALE/unfaithful badge; `Flux` never a glossary term — it is a legitimate traced Going-deeper claim, only un-GLOSSED).
- **Files:** `tests/test_learning.py`. **Commit:** `2f21cd5`.

## Issues Encountered
None beyond the deviations above.

## User Setup Required
None — no external service configuration, zero new dependency.

## Known Stubs
None. `content/rev1/site` regeneration + the dogfood learning surface/path wiring are deliberately deferred to Plan 05 (documented above), not stubs — the render logic this plan owns is complete and tested.

## Verification (re-run independently per CLAUDE.md — actual output)
- `pytest tests/test_learning.py -q` → **17 passed** (10 prior logic tests + 7 new render tests)
- `pytest -q` (full) → **554 passed, 1 xfailed** (baseline 547+1; +7 new; **0 regressions**)
- `mypy src/newsletters` → **9 errors in 2 files** (capture.py/dogfood.py — all pre-existing; **0 in render.py or learning.py**; the prior single render.py error was cleared by the `_claim_row` extraction, 12 -> 9)
- `lint-imports` → **1 contract kept, 0 broken** (render imports .learning/.templates, never .distill from the learning path; core stays AI-free)
- `pytest tests/test_ai_optional.py -q` → **15 passed, 1 xfailed** (no AI import reachable from core after render imports .learning)

## The proven faithfulness negative (on the HTML)
`test_rendered_learning_surface_is_faithful_no_invented_prose`: the rendered `<main>` body's every claim/glossary-definition string is set-member of the source Distillation's claim texts; no `STALE`/`unfaithful` badge appears (the clean surface); and `Flux` (mentioned, never DEFINED) is never a glossary term. `test_every_concept_traces_to_source_on_the_rendered_surface` proves LEARN-02 on the page: every evidence chip is a working link (no `href="None"`) and the un-glossable term appears only in the honesty panel.

## Next Phase Readiness
- LEARN-01/02/03 render complete: the GlossaryBlock branch + `render_path` are the render spine Plan 05 (dogfood a real re-cut + a ≥2-record path, regenerate `content/rev1/site` byte-stable) builds against. The render structure + `render_path` signature + provenance-on-glossary contract are documented above for that wave.
- No blockers. Zero new dependency. Self-contained (no external calls), no JS, deterministic.

## Self-Check: PASSED
- `src/newsletters/render.py` + `tests/test_learning.py` modified on disk; `12-04-SUMMARY.md` written.
- All task commits exist in git history and are pushed: `c864ff2` (test RED), `8b52128` (feat GREEN), `2f21cd5` (test refinement).

---
*Phase: 12-learning-onboarding-surface*
*Completed: 2026-06-19*
