---
phase: 03-worked-synthetic-module-report
plan: 01
subsystem: content
tags: [swimlane, compose, ledger, render, worked-example, corpus, yaml, honesty-panel]

# Dependency graph
requires:
  - phase: 01 (swim-lane loader)
    provides: load_swimlanes — read-only, content-addressed, deterministic config load
  - phase: 02 (module composer)
    provides: compose_module_report — quote/owner sourced-or-omit, compose-time Δ, missing[] routing
  - phase: 11 (worksurface)
    provides: build_work_site structural template + _emit_fonts (self-hosted fonts) reused as-is
provides:
  - A committed synthetic module-a config (fabricated §5 scheme, five §4 lanes, KPI movement mix, zero-KPI lane, traced module-owner quote)
  - modulesite.py — build_module_surfaces + build_module_site (thin loader→composer→ledger→render seam, zero edits to existing modules)
  - content/module/ids.json (R-001) + content/module/site/ committed built output (committed==fresh-build)
affects: [03-02 (CLI --corpus module + gate), 03-03 (end-to-end module test suite)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Corpus builder as a sibling module (not in the compose leaf): mirrors worksurface.build_work_site"
    - "Config discovery via sorted glob keeps the config-specific filename out of src/ (abstraction guard)"
    - "Sourced-or-omit quote hand-off: re-read module-level quote/owner via the lazy _yaml_loader, select the already-traced Claim"

key-files:
  created:
    - content/module/module-a.yml
    - src/newsletters/modulesite.py
    - content/module/ids.json
    - content/module/site/report-module-a.html
    - content/module/site/library.html
  modified: []

key-decisions:
  - "Discover the single *.yml under content/module/ instead of hardcoding the fixture filename — LANE-03 abstraction guard forbids config-specific names (module-a) in src/"
  - "modulesite.py is a new sibling module (compose.py is a leaf that must not import render/site); reuses worksurface._emit_fonts with zero edits"
  - "KPI mix designed so the honesty panel is populated honestly: up/down/Δ==0/single-endpoint + one zero-KPI lane + point-in-time value-only (no false disclosure)"

patterns-established:
  - "Committed==fresh-build corpus: byte-identical repeat build verified before commit"
  - "Zero-edit reuse of render/site/compose/swimlane/worksurface — proven by git diff --exit-code"

requirements-completed: [MODA-01]

# Metrics
duration: ~25min
completed: 2026-07-02
---

# Phase 3 Plan 01: Worked synthetic Module Report Summary

**A committed synthetic `module-a` config + a thin `modulesite` builder that composes and renders it end-to-end (loader → composer → ledger → render → Library) into a self-contained `content/module/` corpus with its own R-001 ledger, a sourced owner quote, 33 claim-beside-verbatim-trace rows, and an honestly-populated honesty panel.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-02
- **Tasks:** 3 (+1 deviation fix)
- **Files modified/created:** 15 (config, builder, ledger, 2 HTML pages, 11 font assets)

## Accomplishments
- `content/module/module-a.yml`: fabricated §5 scheme (module-a / area-bem, five §4 lanes, owners owner-safety|ma|quality|vf|mor, eng-NN, toolset-N, fabricated metrics), exercising the REAL contract — loads clean with 5 bindings, 37 addressed claims, 0 unextracted.
- KPI movement mix, all rendered correctly: safety-observations +8 (up), recordable-incidents −5 (down), throughput-index 0 (Δ==0 honest no-change), defect-rate single-endpoint (disclosed), transfer-readiness point-in-time value-only (no false disclosure), MOR/IQ zero-KPI lane (disclosed).
- `src/newsletters/modulesite.py`: `build_module_surfaces` + `build_module_site` mirroring `worksurface.py`, sole ledger writer, reusing `worksurface._emit_fonts`. Zero edits to any existing module.
- `content/module/ids.json` (first ref R-001, `report-module-a`) + `content/module/site/` committed; byte-identical on repeat build.
- Draft REPORT surface with a rendered sourced `QuoteBlock` (owner-safety) and a populated honesty panel (single-endpoint + zero-KPI disclosures).

## Task Commits

1. **Task 1: Author synthetic module-a config** - `81f8c13` (feat)
2. **Task 2: modulesite builder (build_module_surfaces + build_module_site)** - `7998239` (feat)
3. **Task 3: Generate + commit built module corpus output (R-001 + site)** - `61fd586` (feat)
4. **Deviation fix: discover config generically (abstraction guard)** - `851ccf5` (fix)

**Plan metadata:** (this SUMMARY) — docs commit.

## Files Created/Modified
- `content/module/module-a.yml` - Synthetic worked-example config (fabricated scheme, KPI mix, zero-KPI lane, module-owner quote)
- `src/newsletters/modulesite.py` - Corpus builder: build_module_surfaces + build_module_site (loader→composer→ledger→render seam)
- `content/module/ids.json` - The module corpus's own append-only ledger (first ref R-001)
- `content/module/site/report-module-a.html` - Rendered Draft REPORT (claim-beside-trace + honesty panel + sourced quote)
- `content/module/site/library.html` - Rendered module Library index
- `content/module/site/fonts/*` - Self-hosted woff2 + OFL licenses (emitted via reused _emit_fonts; zero external call)

## Decisions Made
- **Config discovery over hardcoded filename.** The plan suggested `config_path="content/module/module-a.yml"` as the default, but any `module-a` literal in `src/` trips the LANE-03 abstraction guard. Resolved by discovering the single `*.yml` under the corpus dir via a sorted glob (deterministic, byte-stable) and scrubbing all fixture-name literals from source. Composer derives the slug/title from the config identity at runtime.
- **New sibling module, not compose.py.** `compose.py` is a leaf that must not import `render`/`site`; the build-and-render seam therefore lives in a `worksurface`-style sibling. `worksurface._emit_fonts` is reused directly (zero edits).
- **KPI mix chosen for an honest, non-vacuous honesty panel** (a point-in-time value-only KPI proves the composer does NOT falsely flag point-in-time declarations).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Hardcoded fixture filename tripped the abstraction guard**
- **Found during:** Post-Task-3 full pytest gate
- **Issue:** `test_abstraction_guard::test_no_config_specific_name_in_src` failed — the literal `module-a` (in the `_CONFIG_PATH` constant and docstrings of `modulesite.py`) is a denylisted config-specific value; CONTEXT.md is explicit that these specifics live ONLY in config/content, never in `src/`.
- **Fix:** Replaced the hardcoded default with `_discover_config` (sorted glob of the single `*.yml` under `content/module/`); scrubbed every `module-a`/`report-module-a` literal from docstrings. Behavior unchanged: `build_module_surfaces()`/`build_module_site()` with no args still build the corpus.
- **Files modified:** src/newsletters/modulesite.py
- **Verification:** `grep module-a src/newsletters/*.py` clean; rendered output byte-identical (git diff --exit-code content/module/); full suite 605 passed.
- **Committed in:** `851ccf5`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix was required for a hard-rule gate (abstraction guard) and preserved identical build output. No scope creep; the plan's suggested literal default was the only casualty, replaced by a more abstract equivalent.

## Issues Encountered
- None beyond the deviation above. Byte-stability, R-001 ledger, sourced quote, and honesty-panel population all verified on the first working build.

## Verification Evidence (independent re-run)
- Loader: 5 bindings, 37 addressed claims, 0 unextracted.
- Composed surface: Draft, 1 rendered `QuoteBlock`, missing[] = [single-endpoint disclosure, zero-KPI lane disclosure].
- Built HTML: `class="honesty"` present with both planted disclosures; 33 `claim-span` verbatim-trace rows; owner-safety quote rendered.
- Byte-identical repeat build (diff empty); `content/module/ids.json` first ref R-001.
- Gates green: full pytest 605 passed (baseline 605); black/isort(--profile black)/mypy clean on modulesite.py; lint-imports 2 kept/0 broken; bare import (no yaml/AI at top level) ok.
- Reuse-only proof: `git diff --exit-code` clean on render/site/review/worksurface/compose/swimlane.
- No-external-call: the only `http(s)://` in output is the inline SVG `xmlns` namespace URI (a spec constant), identical to the work corpus — no network fetch.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The module corpus is built and committed. Ready for 03-02 (additive `--corpus module` CLI routing + the unforked `review_blockers` gate, proven both ways) and 03-03 (end-to-end module test suite).
- Note (honest caveat, same as Phase 11): the report ships `Draft`, so a published-only `check` scope passes vacuously — 03-02 must plant a blocker to prove the gate fires.
- STATE/ROADMAP/REQUIREMENTS counters intentionally NOT touched per plan instructions.

## Self-Check: PASSED

- Files: all 5 key artifacts present (config, builder, ledger, report HTML, library HTML).
- Commits: 81f8c13, 7998239, 61fd586, 851ccf5 all present in history.

---
*Phase: 03-worked-synthetic-module-report*
*Completed: 2026-07-02*
