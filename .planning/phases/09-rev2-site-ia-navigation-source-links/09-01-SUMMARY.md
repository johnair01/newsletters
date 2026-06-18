---
phase: 09-rev2-site-ia-navigation-source-links
plan: 01
subsystem: ui
tags: [render, static-html, home, marketing, no-js, design-system, route-split]

# Dependency graph
requires:
  - phase: 08-site-content-model-stable-ids
    provides: "Site/Collection/Page model, stable {slug}.html hrefs, render_surface/render_library, _CSS token port, _gate_badge, _chip"
provides:
  - "render_home(site) — the 8-section marketing Home (SITE-02), written to index.html"
  - "8 section helpers: _home_hero/_home_why/_home_demo/_home_engine/_home_surfaces/_home_thesis/_home_developers/_home_invitation"
  - "Home/board layout CSS + responsive @media (≤980px / ≤720px) in _CSS, tokens-only"
  - "sg-eyebrow .accent/.brand variants; _section_divider helper; IconGit/IconArrow glyphs"
  - "Route split: build_site writes index.html=Home and library.html=archive"
  - "No-JS-faithful personalization demo (default persona = maintainer, letter inline)"
affects: [09-02, 09-03, web]

# Tech tracking
tech-stack:
  added: []  # ZERO new dependencies — render.py stays stdlib (html) + typing.TypedDict + sibling core
  patterns:
    - "Hand-rolled HTML-string section helpers fed by module-level data constants (no template engine)"
    - "React useState → no-JS static default (render the default persona inline; picker is styled labels)"
    - "Per-page route split inside build_site (index=Home, library=archive); {slug}.html stays byte-stable"

key-files:
  created:
    - "tests/test_render.py — Home + route-split coverage (14 tests)"
    - "content/rev1/site/library.html — the archive page (regenerated)"
  modified:
    - "src/newsletters/render.py — render_home + 8 helpers + Home CSS + eyebrow variants + glyphs + _HomeLetter TypedDict"
    - "src/newsletters/dogfood.py — build_site route split (index.html=Home, library.html=archive); import render_home"
    - "content/rev1/site/*.html — regenerated (index now the Home; per-surface pages gained the shared Home CSS, additive)"

key-decisions:
  - "DEFAULT inline persona = the maintainer (matches home.jsx useState('maintainer')); the other two personas render as styled, non-interactive picker labels"
  - "Canonical Home copy lifted verbatim from design-reference/newsletters/home.jsx (LETTERS/NL_*) + docs/surfaces.md — NOT re-typed and NOT fed from dogfood READERS (that is a different sample domain; the home.jsx data is the authoritative Home copy)"
  - "Added a _HomeLetter TypedDict so the heterogeneous letters dict type-checks (kept mypy at the 12-error baseline; no new errors)"
  - "Regenerated the committed content/rev1/site/ (SITE-06: render.py is the single source — no hand-edited HTML)"

patterns-established:
  - "Section-helper composition: render_home joins 8 pure helpers; each owns one anchored <section>"
  - "Eyebrow variant convention: .sg-eyebrow.brand / .sg-eyebrow.accent for per-section divider colors"

requirements-completed: [SITE-02]

# Metrics
duration: 7min
completed: 2026-06-18
---

# Phase 09 Plan 01: The real marketing Home (SITE-02) Summary

**The 8-section editorial Home (Hero → Invitation) recreated in render.py from the approved V1 prototype — token-exact, no-JS-faithful personalization demo, with the route split that hands index.html to the Home and the Library archive to library.html.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-18T11:31:19Z
- **Completed:** 2026-06-18T11:38:32Z
- **Tasks:** 3 (TDD)
- **Files modified:** 3 source/test + 11 regenerated site files

## Accomplishments
- `render_home(site)` builds all 8 sections per `docs/surfaces.md` §"Home" and `design-reference/newsletters/home.jsx`, recreated as hand-rolled HTML strings with ZERO new dependency.
- The personalization demo renders the DEFAULT persona's (maintainer) letter **inline** — fully faithful with JavaScript disabled. The only `<script>` on the page is the pre-existing theme toggle (`_TOGGLE_JS`).
- Route split: `build_site` now writes the Home to `index.html` and the Library archive to `library.html`; per-surface `{slug}.html` filenames stay stable.
- Tokens matched exactly: 72px/1.03 DM Serif hero with italic emphasis nouns, 18.5px lead, 10px/0.20em DM Mono eyebrows, `--radius:0` throughout, the 3px-left-accent device, per-section accents (brand `#0068b5` / green `#2f7d4f` / accent `#d4622a`), and the ≤980px / ≤720px responsive collapses.

## Task Commits

Each task was committed atomically (TDD) and pushed:

1. **RED — failing Home + route-split tests** - `081f76f` (test)
2. **Tasks 1+2: the 8-section Home (CSS + scaffolding + full content)** - `dc70db9` (feat)
3. **Task 3: route split (index=Home, library=archive) + typed letter + regenerated site** - `93e2247` (feat)

_Tasks 1 and 2 share one cohesive `render_home` implementation (the sections reuse the same helpers, CSS, and demo scaffolding), so their GREEN landed in one commit `dc70db9`; the RED test commit `081f76f` covers both tasks' behaviors._

## Files Created/Modified
- `src/newsletters/render.py` — `render_home` + 8 section helpers, Home/board layout CSS + responsive `@media`, `.sg-eyebrow.accent/.brand` variants, `IconGit`/`IconArrow` glyphs, `_section_divider`, `_HomeLetter` TypedDict + the verbatim `_HOME_*` copy constants.
- `src/newsletters/dogfood.py` — `build_site` route split; imports `render_home`.
- `tests/test_render.py` — 14 tests (anchors, hero emphasis, no-JS demo, eyebrow variants, all 8 sections, route split, filename stability).
- `content/rev1/site/` — regenerated (SITE-06); `index.html` is now the Home, `library.html` is new; per-surface pages gained the shared Home CSS (additive only — masthead/structure unchanged, no deletions).

## Wave-2 handoff notes (for 09-02)

- **Home renderer:** `render_home(site: Site, *, theme: str = "light") -> str` in `render.py`. It accepts the resolved `Site` (currently unused in the body) so Wave 3 can resolve §5 "Enter →" and §7 links to real hub hrefs.
- **Section anchors:** `#start` (Hero), `#newsletters` (demo), `#engine` (pipeline), `#surfaces` (the four surfaces), `#developers`. §2 (Why) and §6 (Thesis) are unanchored.
- **Route-split mechanics:** in `build_site` (`dogfood.py`), after the per-surface loop, `index.html ← render_home(site)` (full Site) and `library.html ← render_library(library)` (the `listed` Site that collapses the 3 newsletters to `newsletter-jj`). Per-surface `{slug}.html` writes are unchanged.
- **No-JS approach:** the persona picker is static styled `<div class="demo-persona">` labels; the default (`maintainer`) is marked `.on` and its letter is rendered inline. There is no JS-gated content. Wave 2's board must stay equally no-JS (pure CSS grid).
- **CSS hooks already present (for Wave 2):** the new `_CSS` block adds Home section/grid rules; the board (`.lib-board`/`.lib-col`/`.lib-card`), breadcrumb (`.nl-crumb`) and prev/next (`.nl-prevnext`) rules from the UI-SPEC Component Inventory are NOT yet added — Wave 2 adds them.
- `render_library` still renders the flat archive list (unchanged this wave); Wave 2 turns it into the 3-column gate-state board.

## Decisions Made
See `key-decisions` frontmatter. Headline: the default inline persona is the maintainer (matching the prototype); the canonical copy comes from `home.jsx`, not the dogfood `READERS` (a separate sample domain); a `_HomeLetter` TypedDict keeps mypy at baseline.

## Deviations from Plan

None affecting scope. Two small in-task adjustments, both Rule 3 (blocking) / correctness, no new behavior:

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added a `_HomeLetter` TypedDict to hold the mypy baseline**
- **Found during:** Task 3 (gate re-run)
- **Issue:** The heterogeneous `_HOME_LETTERS` dict made mypy infer `letter[...]` as `Sequence[Sequence[str]]`, producing 5 NEW `arg-type` errors on the `_e(letter[...])` calls — over the 12-error baseline the plan requires holding.
- **Fix:** Declared a `_HomeLetter` TypedDict (`kicker/tag/title/body/why: str`, `items: list[tuple[str,str]]`) and annotated `_HOME_LETTERS: dict[str, _HomeLetter]`.
- **Files modified:** `src/newsletters/render.py`
- **Verification:** `mypy src/newsletters` → exactly 12 errors (no new); part of `93e2247`.
- **Committed in:** `93e2247` (Task 3 commit)

**2. [Rule 2 - Missing Critical] Regenerated the committed `content/rev1/site/`**
- **Found during:** Task 3
- **Issue:** SITE-06 mandates `render.py` is the single source — the deployed `index.html` was still the old archive; leaving it stale would contradict the must-have "opening index.html shows the 8-section Home."
- **Fix:** Ran `build_site()` to regenerate the committed site (index=Home, library.html added, per-surface pages picked up the shared Home CSS additively).
- **Files modified:** `content/rev1/site/*.html`
- **Verification:** `index.html` contains the Hero H1; `library.html` exists; `show-ep01.html` is additive-only (79 insertions, 0 deletions, masthead intact).
- **Committed in:** `93e2247` (Task 3 commit)

---

**Total deviations:** 2 (1 blocking, 1 missing-critical) — both correctness, no scope creep.
**Impact on plan:** None. The plan's standing invariants all held.

## Package Verification (T-09-SC)

This plan added **zero packages** (no npm/pip/cargo installs). The package-legitimacy checkpoint does **not** apply. `lint-imports` (1 kept / 0 broken) is the standing guard that `render.py` stays AI-free and stdlib-only — confirmed green.

## DoD Gate Results (re-run independently)

- `.venv/bin/pytest tests/test_render.py -q` → **14 passed**
- `.venv/bin/pytest -q` → **472 passed, 1 xfailed** (baseline 458 + 14 new; suite green)
- `newsletters build` (`build_site`) → renders; `index.html`=Home, `library.html` exists, `show-ep01.html` (per-surface) stable
- `.venv/bin/mypy src/newsletters` → **12 errors** (all pre-existing baseline; no new)
- `.venv/bin/lint-imports` → **Contracts: 1 kept, 0 broken**

## Issues Encountered
None beyond the two auto-fixes above.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- Wave 2 (09-02) can build the gate-state board + the 4-destination nav on top of the index/library split. The `library.html` page exists and `render_library` is intact for the board rewrite.
- No blockers. The no-JS-faithful pattern + the tokens-only CSS convention are established for the board to follow.

## Self-Check: PASSED

All claimed files exist on disk (render.py, tests/test_render.py, content/rev1/site/index.html, content/rev1/site/library.html, 09-01-SUMMARY.md) and all three task commits (`081f76f`, `dc70db9`, `93e2247`) are present in git history.

---
*Phase: 09-rev2-site-ia-navigation-source-links*
*Completed: 2026-06-18*
