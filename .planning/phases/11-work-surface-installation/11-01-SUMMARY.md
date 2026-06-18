---
phase: 11-work-surface-installation
plan: 01
subsystem: ui
tags: [render, fonts, woff2, self-hosting, no-external-call, offline, sil-ofl, determinism]

# Dependency graph
requires:
  - phase: 08-10 (Site model / renderer / provenance)
    provides: "The render.py _CSS token block + build_site / newsletters build path that emits content/rev1/site/"
provides:
  - "A no-external-call rendered Library: zero auto-loading external URLs in the generated HTML/CSS"
  - "Self-hosted SIL-OFL fonts (DM Serif Display, DM Mono, Instrument Sans) vendored as woff2 under content/rev1/site/fonts/ with OFL licenses"
  - "A relative-URL @font-face block in render.py _CSS replacing the Google-Fonts @import"
  - "tests/test_render.py::test_no_external_resource_calls_in_rendered_html — the WORK-01 no-external-call guarantee (L6a/A2)"
  - "A byte-stable rev1 regen whose only change is the font-loading swap (SITE-06 intact)"
affects: [work-surface, wave-3 work corpus (reuses the same _CSS), self-hosting / offline guarantees]

# Tech tracking
tech-stack:
  added: [self-hosted woff2 font assets (static, not a pip dep)]
  patterns: ["Vendor third-party fonts as relative-URL @font-face with their license; no baked external resource URLs in rendered output"]

key-files:
  created:
    - content/rev1/site/fonts/dm-serif-display-400.woff2 (+ italic)
    - content/rev1/site/fonts/dm-mono-400.woff2 (+ 500, + italic)
    - content/rev1/site/fonts/instrument-sans-variable.woff2 (+ italic)
    - content/rev1/site/fonts/OFL-DM_Serif_Display.txt (+ DM_Mono, + Instrument_Sans)
  modified:
    - src/newsletters/render.py
    - tests/test_render.py
    - content/rev1/site/*.html (11 pages, regenerated)

key-decisions:
  - "Took the PREFERRED vendoring path: the woff2 fetch WAS available in-env (real-browser User-Agent against fonts.googleapis.com CSS API), so the three SIL-OFL families are vendored with relative @font-face — no fallback note needed."
  - "Vendored the latin subset only (the design-system's primary subset); the DM-first token stacks at render.py:113 remain the graceful-degradation fallback if a glyph is missing."
  - "Instrument Sans is a variable font: its 400/500/600 latin woff2 are byte-identical, so consolidated to one instrument-sans-variable.woff2 referenced by font-weight:400 600."

patterns-established:
  - "Pattern: rendered HTML auto-loads ZERO external resources; fonts ship as relative-URL @font-face woff2 vendored beside the site, with their OFL license travelling alongside."

requirements-completed: [WORK-01]

# Metrics
duration: ~20min
completed: 2026-06-18
---

# Phase 11 Plan 01: NO-EXTERNAL-CALL Font Fix Summary

**Removed the one baked-in external call — the Google-Fonts `@import` at render.py:104 — by vendoring the three SIL-OFL families as relative-URL `@font-face` woff2 under `content/rev1/site/fonts/` (with OFL licenses), locking the guarantee with a no-external-call test and a byte-stable rev1 regen.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-18 (TDD: RED → GREEN → regen)
- **Completed:** 2026-06-18
- **Tasks:** 3
- **Files modified:** 2 source/test + 11 regenerated HTML + 10 vendored font assets (7 woff2 + 3 OFL)

## Accomplishments
- The Google-Fonts `@import` (render.py:104) is **gone entirely** — no progressive-enhancement remnant. This alone kills the per-page phone-home.
- Vendored the three families as woff2 (DM Serif Display normal+italic, DM Mono 400/500/italic, Instrument Sans variable + italic) with relative `src:url('fonts/...woff2')` and `font-display:swap`; OFL license files committed alongside (T-11-03 control satisfied).
- New test `test_no_external_resource_calls_in_rendered_html` asserts every generated page auto-loads zero external resources (`fonts.googleapis.com`, `fonts.gstatic.com`, `@import url(http`, `src=http`, CSS `url(http`, `<link href=http`) while **permitting** clickable `<a href="https://github.com/johnair01/...">` repo navigation (A2 lock).
- Regenerated `content/rev1/site/` byte-stable — the ONLY committed HTML change is the font-loading swap.

## Task Commits

1. **Task 1: No-external-call test (RED)** — `4e4bb50` (test) — failed naming the `fonts.googleapis.com`/`@import` hit before the fix.
2. **Task 2: Remove @import; self-host via @font-face (GREEN)** — `61730e0` (feat) — render.py + vendored fonts/ + OFL.txt.
3. **Task 3: Regenerate rev1 site byte-stable** — `eda9254` (fix) — regenerated HTML + a one-word _CSS comment reword (see Deviations).

_TDD: Task 1 RED → Task 2 GREEN; no separate refactor commit needed._

## Files Created/Modified
- `tests/test_render.py` — added `test_no_external_resource_calls_in_rendered_html` (auto-loading-URL scan, A2-permitted navigation).
- `src/newsletters/render.py` — deleted the Google-Fonts `@import`; inserted a 7-rule relative-URL `@font-face` block at the top of `_CSS`.
- `content/rev1/site/fonts/*.woff2` (7) + `OFL-*.txt` (3) — vendored SIL-OFL font assets + licenses.
- `content/rev1/site/*.html` (11) — regenerated; only the font-loading change differs.

## Decisions Made
- **PREFERRED path taken (vendored woff2 + OFL.txt), NOT the fallback.** The in-env woff2 fetch succeeded once a real-browser `User-Agent` was used against the Google Fonts CSS2 API (a naive UA returns a degraded/empty CSS — that early failure is why a UA matters). The fallback system-font-stack path was therefore unnecessary.
- **Latin subset only.** Vendored the `latin` subset per family; the `latin-ext` subset was omitted to keep the asset footprint minimal — the DM-first `--font-*` token stacks (render.py:113) cover any uncovered glyph gracefully.
- **Instrument Sans consolidated to one variable file** (the 400/500/600 latin woff2 were byte-identical, md5 `fa41c43…`), referenced by `font-weight:400 600`.
- **Zero new runtime dependency** — woff2 are static assets committed into the site, not a pip package; `lint-imports` stays 1 kept / 0 broken and core remains AI-free.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reworded a `_CSS` comment that tripped an unrelated test's substring guard**
- **Found during:** Task 3 (full-suite gate after regen)
- **Issue:** My `@font-face` comment said "covers weights 400-600". `tests/test_semantic.py::test_render_does_not_leak_private_corpus` does a naive `assert "weights" not in html` (it guards against a private `Corpus.weights` dict leaking into rendered HTML). The benign comment word "weights" collided with that substring and failed the test — a false positive caused by my change.
- **Fix:** Reworded the comment to "one file spans the 400-600 range" (no behavior change). Did NOT weaken the semantic test (it correctly guards a real leak vector; my comment was the offender).
- **Files modified:** src/newsletters/render.py (comment only), and the regenerated HTML.
- **Verification:** `test_render_does_not_leak_private_corpus` + full suite green after regen.
- **Committed in:** `eda9254` (Task 3 commit).

---

**Total deviations:** 1 auto-fixed (1 bug — a comment-vs-substring false positive my change introduced).
**Impact on plan:** Minimal; no scope creep. The fix is a one-word comment change, kept inside my exclusive file (render.py).

## Issues Encountered
- **`python -m newsletters build` does not work** — `newsletters` is a package without `__main__`. The real entrypoint is the `newsletters` console script (`.venv/bin/newsletters build`, Typer CLI in `src/newsletters/cli.py`). Used the console script for Task 3 regen.
- **Concurrent plan 11-02 collision (expected):** `tests/test_worksurface.py` fails collection (`No module named 'newsletters.worksurface'`) because 11-02's `capture_files`/`worksurface` module is not yet landed. That file is **11-02's exclusive scope**, not mine. I verified my scope by running the full suite with `--ignore=tests/test_worksurface.py`. I touched none of 11-02's files.

## Final Gate Output (re-run AFTER the regen, per the Phase-9 process lesson)
- `pytest tests/test_render.py` → **52 passed** (incl. the new no-external-call + byte-stable tests).
- `pytest -q --ignore=tests/test_worksurface.py` → **525 passed, 1 xfailed** (baseline 524 + my new test = 525; the 1 xfail is the pre-existing baseline; the only ignore is 11-02's not-yet-landed module).
- `grep -rE "fonts.googleapis|@import url('http|src=\"http|url(http" content/rev1/site/` → **empty (CLEAN_NO_EXTERNAL)**.
- `newsletters build` → renders 10 surfaces + library index; `@import` gone; `fonts/` + 3 `OFL.txt` present.
- `mypy src/newsletters` → **12 errors** (exactly the pre-existing count; no new).
- `lint-imports` → **1 kept / 0 broken** (render.py stays AI-free).

## Font Approach (recorded per the plan's output spec)
**Vendored woff2 + OFL.txt (the PREFERRED path).** The generated site has **zero auto-loading external URLs**; the three design-system families load from relative `fonts/*.woff2` paths; their SIL-OFL licenses are committed alongside. The DM-first token stacks remain as graceful-degradation fallback.

## Next Phase Readiness
- Wave-3's work corpus reuses the same `_CSS` — it inherits the self-hosted fonts and the no-external-call guarantee for free.
- The no-external-call test will catch any future renderer change that reintroduces a baked external URL.
- No blockers introduced.

## Self-Check: PASSED

---
*Phase: 11-work-surface-installation*
*Completed: 2026-06-18*
