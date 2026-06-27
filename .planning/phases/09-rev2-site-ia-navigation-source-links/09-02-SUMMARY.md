---
phase: 09-rev2-site-ia-navigation-source-links
plan: 02
subsystem: ui
tags: [render, static-html, library-board, gate-state, navigation, breadcrumb, prevnext, no-js, design-system]

# Dependency graph
requires:
  - phase: 09-rev2-site-ia-navigation-source-links
    plan: 01
    provides: "render_home + route split (index.html=Home, library.html=archive); render_library; _CSS token port; Site/Collection/Page plumbing"
provides:
  - "render_library(site) — a 3-column gate-state status board (Draft / In Review / Published), pure CSS grid, no JS (SITE-03)"
  - "_board(site) / _board_column(state,label,accent,pages) / _board_card(page) — group site.pages() by Page.gate; empty-column placeholder"
  - "_nav_targets(site) — resolves the four nav destinations to real existing Page.hrefs (SITE-04)"
  - "_nav/_page accept an optional resolved targets map; _footer links to library.html"
  - "_breadcrumb(site, page) — Home > Collection > Page; _prevnext(site, page) — within-type neighbors"
  - "render_surface gains optional site=/page= kwargs (build path wires the resolved Site + Page)"
  - "board / breadcrumb / prev-next CSS + ≤820px collapses in _CSS"
affects: [09-03, web]

# Tech tracking
tech-stack:
  added: []  # ZERO new dependencies — render.py stays stdlib (html) + typing + sibling core
  patterns:
    - "Gate→column board: group site.pages() into a fixed ReviewState ladder of three columns; empty buckets render a placeholder so the board shape never collapses"
    - "Optional resolved targets map threaded into _nav/_page; single-surface callers fall back to raw _NAV_ITEMS hrefs (keeps test_semantic green without a Site)"
    - "Breadcrumb/prev-next are emitted only when both site+page are supplied (no neighbors to resolve otherwise) — backward-compatible render_surface(surface)"

key-files:
  created: []
  modified:
    - "src/newsletters/render.py — _board/_board_column/_board_card + render_library rewrite; _nav_targets + _nav/_page targets threading; _footer library link; _breadcrumb/_prevnext/_collection_for; board+crumb+prevnext CSS; render_surface site=/page= kwargs; Collection import"
    - "src/newsletters/dogfood.py — build_site threads site=site, page=page into render_surface (committed in the Task-2 commit)"
    - "tests/test_render.py — 14 new tests (6 board, 3 nav/footer, 5 breadcrumb/prevnext)"
    - "content/rev1/site/*.html — regenerated from render.py (SITE-06): library.html=board; every surface gains nav targets + breadcrumb + prev/next + footer library link"

key-decisions:
  - "Board columns are a fixed three-entry ladder (_BOARD_COLUMNS) with per-column header accents Draft=--text / In Review=--color-amber / Published=--color-brand-primary (design-system.md §6); empty columns keep their header + a muted 'No surfaces in this state.' placeholder (T-09-04)"
  - "_nav_targets resolves each type hub to the first Page.href of its Collection (Newsletters→newsletter-jj, Articles→article-semantic-spine, The Show→show-ep01), index.html fallback only when a collection is empty — no None/dead hrefs (T-09-05)"
  - "render_surface keeps a backward-compatible signature: site=/page= are optional kwargs; when absent the nav uses the raw _NAV_ITEMS hrefs and breadcrumb/prev-next are omitted — so existing test_semantic.py/test_site.py callers stay green untouched"
  - "Breadcrumb Collection segment links to the resolved hub; for a collection's first page that hub href equals the page's own href (acceptable — the 'here' segment is the plain-text current page)"
  - "Regenerated the committed content/rev1/site/ AFTER the implementation and BEFORE running the gate suite (the 09-01 stale-green lesson)"

patterns-established:
  - "Fixed-ladder column board keyed off an enum field, with always-rendered empty placeholders"
  - "Optional resolved-context threading (targets/site/page) that degrades gracefully for context-free callers"

requirements-completed: [SITE-03, SITE-04]

# Metrics
duration: 9min
completed: 2026-06-18
---

# Phase 09 Plan 02: The gate-state Library board + four-destination nav Summary

**The Library archive becomes a pure-CSS three-column status board keyed off `Page.gate` (Draft / In Review / Published), and the global navigation becomes real — four resolved destinations, a Home > Collection > Page breadcrumb on every surface, within-type prev/next, and a footer link to the board.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-06-18T11:45:22Z
- **Tasks:** 3 (TDD: RED → GREEN each)
- **Files modified:** 2 source (render.py; dogfood.py in the Task-2 commit) + 1 test + 11 regenerated site files

## Accomplishments

- **SITE-03 — the status board.** `render_library` no longer renders a flat list. `_board(site)` groups `site.pages()` by `page.gate` into the fixed three-column ReviewState ladder; `_board_column` renders a mono header (label + count, colored per design-system.md §6) over stacked `_board_card`s; an empty column keeps its header + a muted "No surfaces in this state." placeholder so the board shape is always legible (T-09-04). Pure CSS grid (`repeat(3,1fr)`), NO JS — the "Renders without JavaScript" footer claim stays honest.
- **SITE-04 — four real destinations.** `_nav_targets(site)` resolves the three previously-`None` spine hrefs to the first `Page.href` of each surface-type Collection (Newsletters, Articles, The Show), falling back to `index.html` only for an empty collection. The resolved map is threaded through `_nav`/`_page`; the footer now links to `library.html` (the Library is intentionally outside the four-item spine, N1).
- **SITE-04 — breadcrumb + prev/next.** Every surface now shows a `Home › Collection › Page` breadcrumb above the masthead (`_breadcrumb`) and within-type prev/next at the foot (`_prevnext`). Neighbors are resolved by the page's index in its OWN `Collection.pages` order — never crossing surface type (ROADMAP SC3). First page has no prev, last no next, single-page collection neither.
- **Determinism (N5):** the new code emits nothing time-varying; a double-render byte-stability check passes.
- **Zero new dependency**; `lint-imports` stays 1 kept / 0 broken.

## Task Commits (each atomic, TDD, pushed)

1. **RED — board tests** — `e77b475` (test)
2. **GREEN — the gate-state board** — `f282b41` (feat)
3. **RED — nav-target tests** — `9b6074f` (test)
4. **GREEN — four resolved nav destinations + footer library link** — `150dec0` (feat)
5. **RED — breadcrumb/prev-next tests** — `4f5e75f` (test)
6. **GREEN — breadcrumb + prev/next + regenerated content** — `5a78114` (feat)

## Wave-3 handoff notes (for 09-03)

- **Board renderer + gate→column mapping:** `_board(site)` → `<div class="lib-board">` (CSS grid `repeat(3,1fr)`); buckets `site.pages()` by `page.gate` into the fixed `_BOARD_COLUMNS` ladder `[(DRAFT,"Draft",--text), (IN_REVIEW,"In Review",--color-amber), (PUBLISHED,"Published",--color-brand-primary)]`. Each `_board_card(page)` is `<a class="lib-card" href="{page.href}" style="--signal:{page.signal_color.css_var}">` with the stable `_lib_ref_label(page)` lead + the `_status_tag(surface)` pill. The intro + fan-out diagram are kept ABOVE the board (Wave 3 links the fan-out rows — leave them as-is until then).
- **The four nav destinations + how hubs resolve:** `_nav_targets(site) -> dict[label,href]`. `Start here`→`index.html`; the three type hubs (`_NAV_KIND` map) → the first `Page.href` of the newsletter/article/show Collection (in the deployed full site those are `newsletter-jj.html`, `article-semantic-spine.html`, `show-ep01.html`). Wave 3's no-dead-link regen test can assert every `_nav_targets` value exists on disk.
- **Breadcrumb / prev-next API + the render_surface signature change (load-bearing for Wave 3 + existing callers):**
  - `render_surface(surface, *, theme="light", site: Site | None = None, page: Page | None = None) -> str`. The new kwargs are **optional**. `build_site` now calls `render_surface(page.surface, site=site, page=page)`. Callers that pass only a `surface` (e.g. `test_semantic.py`) still work: nav uses raw `_NAV_ITEMS` hrefs, and breadcrumb/prev-next are omitted. **Wave 3, if it changes render_surface again, must preserve this optional-kwarg contract.**
  - `_breadcrumb(site, page)` → `<nav class="nl-crumb">`; Home + Collection are `<a>`, current page is `<span class="here">`.
  - `_prevnext(site, page)` → `<div class="nl-prevnext">` with `<a class="prev">`/`<a class="next">`; resolves neighbors via `_collection_for(site, page)` (matches by `page.kind`).
- **CSS hooks now present:** `.lib-board`/`.lib-col`/`.lib-col-head`/`.lib-col-label`/`.lib-col-count`/`.lib-col-empty`/`.lib-card`, `.nl-crumb`, `.nl-prevnext` — all tokens-only, `--radius:0`, with the ≤820px 1-col board collapse.

## Decisions Made

See `key-decisions` frontmatter. Headlines: a fixed three-column ladder with always-rendered empty placeholders; `_nav_targets` resolves to real first-pages with an `index.html` empty-collection fallback; `render_surface` keeps a backward-compatible optional-kwarg signature so context-free callers stay green; content regenerated AFTER implementation and BEFORE the gate suite (the 09-01 stale-green lesson).

## Deviations from Plan

None affecting scope. Two in-task adjustments, both to **my own RED tests** (the implementation behavior was correct):

### Test corrections (not implementation changes)

**1. Breadcrumb test assertion relaxed**
- **Found during:** Task 3 GREEN
- **Issue:** The test asserted `<a href="{page.href}"` is absent from the breadcrumb, but the Collection segment correctly links to the resolved hub, which for a collection's *first* page equals that page's own href.
- **Fix:** Assert instead that the current page renders as `<span class="here">{title}</span>` (genuinely non-link). No implementation change.

**2. prev/next bounds test assertion tightened**
- **Found during:** Task 3 GREEN
- **Issue:** The test used `"prev" not in first_out.lower()`, but the wrapper class is always `nl-prevnext` (contains "prev").
- **Fix:** Assert on `class="prev"` / `class="next"` anchor absence + the `&larr;`/`&rarr;` glyph absence — precise to the actual neighbor anchors. No implementation change.

Both were faulty assertions in the new tests; the renderer behaved correctly throughout. No source logic changed to make tests pass.

## Package Verification (T-09-SC)

Zero packages added (no npm/pip/cargo installs). The package-legitimacy checkpoint does not apply. `lint-imports` (1 kept / 0 broken) is the standing guard that `render.py` stays AI-free and stdlib-only — confirmed green.

## DoD Gate Results (re-run independently, AFTER regenerating content/rev1/site/)

Per the 09-01 lesson, `content/rev1/site/` was regenerated via `newsletters build` FIRST, then all gates were run and the results below are the ACTUAL post-regen output:

- `newsletters build` → rendered 10 surfaces + the library index; `index.html`=Home, `library.html`=the 3-column board (grid, empty-state placeholder verified), per-surface `{slug}.html` stable; every surface carries nav targets (no `href="None"`), breadcrumb (`nl-crumb`), prev/next (`nl-prevnext`), footer `library.html` link.
- `.venv/bin/pytest tests/test_render.py tests/test_site.py -q` → **38 passed**
- `.venv/bin/pytest -q` → **486 passed, 1 xfailed** (baseline 472 + 14 new; suite green)
- `.venv/bin/mypy src/newsletters` → **12 errors** (all pre-existing baseline — capture.py, render.py:368/376/392 `_block_html` loop-var reassignments, dogfood.py; NO new errors from this plan)
- `.venv/bin/lint-imports` → **Contracts: 1 kept, 0 broken**
- Determinism: a double `build_site` byte-compare across `index.html`/`library.html`/`show-ep01.html`/`newsletter-jj.html` is byte-identical (no nondeterminism reaches the rendered HTML, N5).

## Known Stubs

None. The board, nav targets, breadcrumb, and prev/next are all wired to real `Site`/`Collection`/`Page` data. (The Home §5 "Enter →" and §7 repo links remain `#`/anchor placeholders — that is Wave 3 / SITE-05 source-links scope, explicitly out of scope for this plan.)

## Threat Flags

None. All interpolated titles/refs pass through `_e()`; all hrefs are built from `{slug}.html` (slugify-guaranteed `[a-z0-9-]`) or the fixed `index.html`/`library.html` literals. No new network endpoint, auth path, or trust-boundary surface introduced (T-09-03 / T-09-04 / T-09-05 mitigations applied).

## Issues Encountered

None beyond the two test-assertion corrections above.

## User Setup Required

None — no external service configuration.

## Next Phase Readiness

- Wave 3 (09-03) can add source links (`link_for_source` + `source_base_url`), the `FanoutLink.href` + SVG fan-out anchors, and the generated-marker + byte-stable regen + no-dead-link tests on top of this nav. The `_nav_targets` map is the resolver for in-site anchor targets; the full page set + breadcrumb/prev-next exist for the regen/dead-link assertions to be total.
- No blockers.

## Self-Check: PASSED

All claimed files exist on disk and all six task commits are present in git history (verified below).

---
*Phase: 09-rev2-site-ia-navigation-source-links*
*Completed: 2026-06-18*
