---
phase: 08-site-content-model-stable-ids
plan: 02
subsystem: render
tags: [page-driven, stable-ids, library, ssg, ledger, spec, backward-compat]

# Dependency graph
requires:
  - phase: 08-01
    provides: "src/newsletters/site.py — Site/Collection/Page + append-only Ledger + slugify; seeded content/rev1/ids.json"
provides:
  - "render_library(site) — Page-driven Library renderer (page.ref in the lead slot, page.href links; no positional enumerate)"
  - "build_site() — builds the Site via the ledger, persists it (append-only), writes per-surface pages + the Library index"
  - "docs/architecture.md — the Site/Collection/Page content model + ledger + position-independence guarantee"
  - "docs/surfaces.md — the L1 ID convention (R-NNN/A-NNN/EPNN/cadenced/L-NNN) with rationale"
  - "tests/test_site.py::test_existing_links_do_not_rot — the L3 no-rot structural guard"
affects: ["phase-9 site IA / nav / Home", "cross-link anchor rendering", "gate-state board (phase 10)"]

# Tech tracking
tech-stack:
  added: []  # zero new dependencies
  patterns:
    - "Presentation tier consumes the typed content model (Site/Page), not raw lists — identity stays out of the view"
    - "Content-stable lead label (page.ref) replaces a positional enumerate index — the rot fix"
    - "Cadenced surfaces (newsletters) fall back to issue/kind for their label since their identity is issue+date, not a sequential ref"

key-files:
  created: []
  modified:
    - src/newsletters/render.py
    - src/newsletters/dogfood.py
    - tests/test_semantic.py
    - tests/test_site.py
    - docs/architecture.md
    - docs/surfaces.md
    - content/rev1/site/index.html

key-decisions:
  - "render_library signature changed from (surfaces: Iterable[Surface]) to (site: Site); it iterates site.pages() so row order == build_surfaces order (show, reports, article, newsletter) — visible order unchanged, only the lead label changed"
  - "_lib_ref_label helper: page.ref if present, else #{issue:02d} for cadenced surfaces with a recorded issue, else the 2-letter kind abbreviation (Rev1 newsletters -> 'NE') — always content-derived, never positional"
  - "build_site loads + saves the committed ledger (append-only; byte-identical for the seeded corpus), and writes out / page.href so filenames stay byte-stable (L3)"
  - "Spec gap (L2) filled in the same change: ID convention in surfaces.md, content model in architecture.md"

patterns-established:
  - "The Library is rendered from the Site model; reordering surfaces no longer renumbers it or rots a link"

requirements-completed: [SITE-01]

# Metrics
duration: ~25min
completed: 2026-06-18
---

# Phase 8 Plan 02: Page-Driven Renderer & Spec Convention Summary

**The Library now renders each surface's stable per-type ref (R-001 / EP01 / A-001) from the Site/ledger model instead of a positional `enumerate` index — closing the rot point — with every committed `*.html` filename and href byte-stable, and the ID convention + content model now documented in the spec.**

## Performance
- **Duration:** ~25 min
- **Completed:** 2026-06-18
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 7

## Accomplishments
- **The rot fix (Task 1).** `render_library` was rewritten from `render_library(surfaces: Iterable[Surface])` with a positional `for i, s in enumerate(surfaces, 1)` / `<span class="lib-idx">{i:02d}</span>` to `render_library(site: Site)` iterating `site.pages()`, rendering `page.ref` in the lead slot and `page.href` for the link. The `enumerate` import-of-position is gone — that positional `01..NN` was the only thing that renumbered on reorder.
- **Build is Site-driven (Task 1).** `build_site()` now loads the committed ledger (`Ledger.load("content/rev1/ids.json")`), builds `Site.from_surfaces(build_surfaces(), ledger=ledger)`, `ledger.save()` (append-only — byte-identical for the seeded corpus), writes each page to `out / page.href`, and renders the Library from a `Site`. Output directory and filenames are unchanged.
- **Spec gap closed (Task 2, L2).** `docs/architecture.md` gained a `Site → Collection → Page` subsection (order is data not identity; the append-only ledger; the position-independence guarantee). `docs/surfaces.md` gained the L1 ID-convention table (`R-NNN` / `A-NNN` / `EPNN` / cadenced newsletters / `L-NNN`) with the *why* (determinism / durable references). No silent code↔spec drift.
- **No-rot locked (Task 2, L3).** `tests/test_site.py::test_existing_links_do_not_rot` asserts the set of `page.href` for the Rev1 corpus equals the committed `content/rev1/site/*.html` filenames (minus `index.html`) and that each href is the `{slug}.html` form — a structural backward-compat guard (Pitfall 2).
- **Zero new dependencies; no scope creep into Phase 9/10** (no Home, nav, clickable fan-out anchors, or gate-state board).

## What changed in `render_library` (the rot fix)
| Before | After |
|--------|-------|
| `render_library(surfaces: Iterable[Surface], ...)` | `render_library(site: Site, ...)` |
| `for i, s in enumerate(surfaces, 1)` | `for page in site.pages()` |
| `<span class="lib-idx">{i:02d}</span>` (positional `01..07`) | `<span class="lib-idx">{_lib_ref_label(page)}</span>` (`EP01 / R-001..R-004 / A-001 / NE`) |
| `href="{s.id}.html"` | `href="{page.href}"` (== `{slug}.html`, byte-identical) |
| reads off `s` / `s.template` | reads off `page` (ref/title/gate/signal_color) + `page.surface.template` |

`_lib_ref_label(page)` is the new helper: `page.ref` if present, else `#{issue:02d}` for a cadenced surface with a recorded issue, else the kind abbreviation. All fields stay HTML-escaped via the existing `_e()` (T-08-04 mitigation preserved). Masthead/fan-out markup, `_NAV_ITEMS`, and the Home were untouched (L6).

## Spec sections added
- **`docs/architecture.md`** → section 1, after the invariants: *"The content model: `Site → Collection → Page` (the durable index)"* — the three objects, type-grouped collections ordered by `template.distance`, order-is-data, and the append-only ledger mechanics + determinism.
- **`docs/surfaces.md`** → in "The Hub / Library": *"ID conventions (stable, content-derived — never positional)"* — the per-type `ref` table, `slug` as the canonical link key, and the rationale (durable references / determinism).

## Filenames byte-stable + refs content-stable (verified)
- `build_site()` into a temp dir produced exactly the 10 committed filenames (9 surfaces + `index.html`) — set equality asserted.
- Regenerating the committed output changed **only `content/rev1/site/index.html`**; no per-surface file changed, no rename, and `content/rev1/ids.json` is byte-identical (`git status` clean for the ledger).
- The only visible delta in `index.html` is the lead label per row: `01 02 03 04 05 06 07` → `EP01 R-001 R-002 R-003 R-004 A-001 NE`. Row order and all hrefs are unchanged.

## Task Commits
1. **Task 1 — Page-driven render + Site-driven build** — `eb5c4a8` (feat)
2. **Task 2 — spec convention + model + no-rot test** — `e2fb92d` (docs)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated `test_render_library_lists_surfaces` for the new Site signature**
- **Found during:** Task 1 (full-suite gate)
- **Issue:** `tests/test_semantic.py::test_render_library_lists_surfaces` called `render_library([r])` with a raw list; the plan's signature change to `render_library(site: Site)` broke it (`AttributeError: 'list' object has no attribute 'pages'`). This caller was not listed in the plan's files but is directly blocked by the planned API change.
- **Fix:** Build a `Site` in the test via `Site.from_surfaces([r], ledger=Ledger.load("/nonexistent-ledger.json"))` (a missing path starts an empty ledger, per the 08-01 `Ledger.load` contract) and pass it to `render_library`.
- **Files modified:** tests/test_semantic.py
- **Commit:** eb5c4a8

**Total deviations:** 1 auto-fixed (1 blocking caller update). No scope creep.

## Issues Encountered
- **Pre-existing mypy errors (out of scope, unchanged).** `mypy src/newsletters/render.py dogfood.py` reports the same errors documented in `deferred-items.md` from 08-01 (render.py:243/251/267 str-vs-list; dogfood.py Source/Trace call-arg/arg-type). My edits introduced **zero new** mypy errors — `render_library`, `_lib_ref_label`, and the `build_site` changes are clean. Line numbers shifted by a few (e.g. dogfood 454→455) only because I added imports/comments; same pre-existing errors. Not fixed (executor scope boundary).

## Gate Results (re-run independently)
- `pytest tests/test_site.py -q` → **10 passed** (incl. `test_existing_links_do_not_rot`).
- `pytest -q` (full) → **458 passed, 1 xfailed** (baseline 457 + 1 new test; no regression).
- `newsletters build` → **rendered 9 surfaces + the library index**; only `index.html` changed; filenames byte-stable; visible refs are now `R-001`/`EP01`/`A-001`, not a positional number.
- `lint-imports` → **1 kept, 0 broken** (render.py imports `.site`, which is AI-free; no AI edge).
- `mypy src/newsletters/site.py src/newsletters/render.py` → only the documented PRE-EXISTING render.py errors; **no new errors** from this plan's edits.

## Known Stubs
None. The Library is rendered from the real dogfood corpus via the seeded ledger; no mock/placeholder data was introduced.

## Self-Check: PASSED
- Files: src/newsletters/render.py, src/newsletters/dogfood.py, docs/architecture.md, docs/surfaces.md, tests/test_site.py, tests/test_semantic.py, content/rev1/site/index.html — all FOUND.
- Commits: eb5c4a8 (Task 1 feat), e2fb92d (Task 2 docs) — both FOUND in git log.

---
*Phase: 08-site-content-model-stable-ids*
*Completed: 2026-06-18*
