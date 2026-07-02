---
phase: 03-worked-synthetic-module-report
plan: 03
subsystem: tests
tags: [module-corpus, end-to-end, honesty-panel, determinism, ledger, confidentiality, byte-stable]

# Dependency graph
requires:
  - phase: 03-01 (modulesite builder + committed corpus)
    provides: build_module_surfaces / build_module_site + content/module/ (config, R-001 ledger, site)
  - phase: 03-02 (--corpus module CLI + gate)
    provides: the additive, unforked review_blockers gate wiring proven both ways
  - phase: 11 (worksurface)
    provides: the corpus-level test patterns mirrored (no-external-call, byte-stable, committed==fresh)
provides:
  - tests/test_modulesite.py — the end-to-end + trust-guard + determinism + confidentiality suite (9 tests)
  - Gate-visible proof that the worked example honors the REAL contract (traced+addressed, populated honesty panel visible in HTML, R-001 stable, byte-stable, committed==fresh, synthetic-only content)
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Assert on STRUCTURE + INVARIANTS, reading concrete values from the composed surface (never a hardcoded lane/metric string) — the abstraction guard honored in tests"
    - "Fresh-tmp-ledger rebuild to prove append-only R-001 stability (proven by rebuild, not by asserting a literal twice)"
    - "Non-vacuous confidentiality scan: a planted real-looking name/email self-check proves the denylist actually fires"

key-files:
  created:
    - tests/test_modulesite.py
  modified: []

key-decisions:
  - "Located the single-endpoint disclosure by the composer's phrasing ('only one endpoint is usable') then asserted the FULL escaped surface.missing entry renders — reads the real entry, hardcodes no lane name"
  - "Confidentiality denylist = generic real-name SHAPES (representative real-looking tokens + an email pattern), not a list of secrets; scan restricted to authored content (.yml + site/*.html + ids.json), NOT the vendored OFL font-license text"
  - "Byte-stable + committed==fresh compare the WHOLE output tree (HTML + fonts), and snapshot the committed ledger to assert the shared-path save is idempotent (unchanged bytes)"

requirements-completed: [MODA-01, MODA-02]

# Metrics
duration: ~20min
completed: 2026-07-02
---

# Phase 3 Plan 03: Module worked-example test suite Summary

**A 9-test end-to-end suite (`tests/test_modulesite.py`) that proves the synthetic `module` corpus honors the real trust contract: every built claim traced+addressed, a populated honesty panel with the single-endpoint disclosure VISIBLE in the rendered HTML, a sourced owner quote, zero external calls, byte-stable double-render, R-001 stable across rebuild, committed==fresh-build, EPOCH_ZERO determinism, and a non-vacuous synthetic-name confidentiality check — closing MODA-01 (gate-visible worked example) and MODA-02 (byte-stable double-render over the new corpus).**

## Performance
- **Duration:** ~20 min
- **Completed:** 2026-07-02
- **Tasks:** 2 (+1 black-formatting commit)
- **Files created:** 1 (`tests/test_modulesite.py`)

## Accomplishments
- **Task 1 (trust + gate-visible):** `test_every_claim_traced_and_addressed` (every ClaimsBlock claim `is_traced` + every trace `is_addressed`, body non-empty, honesty panel populated — Hole B closed, Pitfall 11 guarded); `test_single_endpoint_disclosure_visible_in_html` (honesty panel + `claim-span` present AND the exact single-endpoint disclosure rendered, read from `surface.missing`); `test_owner_quote_rendered_from_sourced_path` (the traced `QuoteBlock` text renders); `test_no_external_calls` (no google-fonts/`src="http"`/`url(http`/`<link href="http">`, self-hosted `fonts/*.woff2` present).
- **Task 2 (determinism + integrity + confidentiality):** `test_byte_stable_double_render` (whole-tree byte equality — SITE-06/MODA-02); `test_r001_stable_across_rebuild` (fresh tmp ledger → `R-001`, reload+rebuild → same ref, append-only proven by rebuild); `test_committed_equals_fresh_build` (fresh build reproduces committed `content/module/site/` byte-for-byte + committed ledger idempotent); `test_no_datetime_now_reachable` (`Surface.created` + `Source.timestamp` == `EPOCH_ZERO`); `test_committed_content_is_synthetic` (denylist clean over `.yml`+`site/*.html`+`ids.json`, fabricated markers present, non-vacuous planted-leak self-check).
- Every assertion reads config-derived values from the composed surface — no hardcoded lane/metric string.

## Task Commits
1. **Task 1: end-to-end + trust-guard + honesty-panel module suite** — `272bdb0` (test)
2. **Task 2: determinism, R-001 stability, committed==fresh, confidentiality** — `7e94b6a` (test)
3. **Black formatting of the module suite** — `bac34ca` (style)

**Plan metadata:** (this SUMMARY) — docs commit.

## Files Created/Modified
- `tests/test_modulesite.py` — the 9-test end-to-end + trust-guard + determinism + confidentiality suite for the module corpus.

## Decisions Made
- **Disclosure located by composer phrasing, asserted on the full entry.** The single-endpoint disclosure is found via the composer's `"only one endpoint is usable"` wording (composer source, not a lane name), then the full escaped `surface.missing` entry is asserted present in the HTML — tracks the config, hardcodes nothing.
- **Confidentiality denylist = generic real-name shapes, scan scoped to authored content.** Representative real-looking tokens (the repo's own Star-Trek sample-team names as canonical "real-looking" nomenclature) + an email-address pattern, scanned only over `.yml`/`site/*.html`/`ids.json`. The vendored OFL font-license text is deliberately NOT scanned (third-party license copy, not our authored content; scanning it would false-positive on foundry names). A planted `Jean-Luc Picard` / `ops@starfleet.int` self-check proves the scanner fires (Phase-7 "prove it blocks" norm).
- **Whole-tree comparisons + ledger-idempotence snapshot.** Byte-stable and committed==fresh compare HTML *and* fonts; the committed ledger is snapshotted before/after the build and asserted unchanged, which is how the shared-ledger-path side effect (below) is made safe and turned into positive evidence of append-only stability.

## Deviations from Plan
None — plan executed exactly as written. Black reformatted the new test (advisory gate); committed separately as `style(03-03)`.

## Concerns / Caveats (honest)
- **Shared ledger path (plan-checker warning, inherited from 03-01).** `build_module_site(out_dir)` loads and saves its ledger at the FIXED committed path `content/module/ids.json`, NOT under `out_dir`. So any test that calls `build_module_site` re-saves that committed file. Because the committed ledger already holds `R-001` and `Ledger.save()` is byte-stable (`sort_keys` + trailing newline), the rebuild is IDEMPOTENT — empirically confirmed: `git status` is clean after the full suite runs. This is documented in the suite's module docstring and in the per-test comments, and `test_committed_equals_fresh_build` asserts the ledger bytes are unchanged. A future hardening would thread the ledger path through `out_dir` so builds into a tmp dir are fully hermetic; out of scope for this test-only plan (which owns only `tests/test_modulesite.py`).
- **Draft-scope vacuity (same caveat as Phase 11 / noted in 03-01/03-02).** The module report ships `Draft`, so a published-only `check` scope passes vacuously on the clean corpus; the gate-fires-on-a-planted-blocker proof lives in 03-02's suite, not here.

## Verification Evidence (independent re-run)
- **Full suite:** `pytest -q` → **617 passed** (was 608; +9 new tests).
- **Module suite:** `pytest tests/test_modulesite.py -q` → **9 passed**.
- **lint-imports:** 2 kept, 0 broken (core AI-free contract intact).
- **Corpus gates:** `newsletters check` (rev1), `--corpus work`, `--corpus module` → all "All published surfaces clean — no blockers."
- **Advisory formatters on the new test:** black clean, isort `--profile black` clean. mypy shows only the baseline `import-untyped` noise (the package ships no `py.typed`; identical class to `test_worksurface.py`'s 7) — no NEW failures.
- **Working tree clean** after all test runs (`git status --short` empty) — the shared-path ledger save is byte-identical, confirming append-only idempotence.

## Next Phase Readiness
- MODA-01 (gate-visible worked example) and MODA-02 (byte-stable double-render over the module corpus) are now covered by an executable suite. STATE/ROADMAP/REQUIREMENTS counters intentionally NOT touched per plan instructions.

## Self-Check: PASSED
- Files: `tests/test_modulesite.py` present (9 tests collected).
- Commits: `272bdb0`, `7e94b6a`, `bac34ca` all present in history.

---
*Phase: 03-worked-synthetic-module-report*
*Completed: 2026-07-02*
