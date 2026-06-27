---
phase: 05-excel-adapter
plan: 04
subsystem: testing
tags: [openpyxl, xlsx, golden-corpus, adapter, faithfulness, coverage, byte-reproducible, tdd]

# Dependency graph
requires:
  - phase: 05-excel-adapter (plan 03)
    provides: "ExcelAdapter (registered 'excel') + the exact unextracted[] reason strings + value->string table + Sheet!A1<tab>value transcript layout"
  - phase: 05-excel-adapter (plan 01)
    provides: "Typed coverage carrier (Source.extraction) + round-trip coverage parity matrix the golden test re-proves on each .xlsx"
  - phase: 04-shared-adapter-normalizer-email
    provides: "the golden-corpus pattern (test_email_golden.py + eml/_author_fixtures.py), assert_conforms, Coverage/Unextracted honesty"
provides:
  - "A committed, byte-reproducible .xlsx golden corpus (8 fixtures) authored programmatically with openpyxl"
  - "tests/test_excel_golden.py: the executable ADAPT-06 contract — zero-silent-drops accounting identity, verbatim + content-addressed claims, coverage honesty, conformance + JSON round-trip, determinism, and round-trip coverage parity, per fixture"
  - "A pinned per-fixture expected-counts/reasons table derived from the LIVE adapter (the formula-cache crux, error cell, chart disclosure, merged anchor)"
  - "Hardened ExcelAdapter determinism: Source.timestamp sourced from wb.properties.created (no more now() default)"
affects: [06, 07, adapters, verify-work]

# Tech tracking
tech-stack:
  added: []  # openpyxl already declared by 05-02; this plan adds no new dependency
  patterns:
    - "Byte-reproducible OOXML fixtures: pin BOTH docProps timestamps AND every ZIP entry date_time (openpyxl stamps the wall-clock into each zip local header at save time, independent of doc properties)"
    - "Author a formula-WITH-cache .xlsx by post-save XML injection of <v>cache</v> (openpyxl cannot write a formula cache via its API); the natural openpyxl save IS the no-cache case"
    - "Golden corpus drives the LIVE registered adapter and pins per-fixture counts + EXACT ordered unextracted reasons derived from it (never assumed)"

key-files:
  created:
    - tests/fixtures/xlsx/_author_fixtures.py
    - tests/fixtures/xlsx/formula_with_cache.xlsx
    - tests/fixtures/xlsx/formula_no_cache.xlsx
    - tests/fixtures/xlsx/merged_cells.xlsx
    - tests/fixtures/xlsx/multi_sheet.xlsx
    - tests/fixtures/xlsx/mixed_types.xlsx
    - tests/fixtures/xlsx/empty_cells.xlsx
    - tests/fixtures/xlsx/error_cell.xlsx
    - tests/fixtures/xlsx/chart_or_image.xlsx
    - tests/test_excel_golden.py
  modified:
    - src/newsletters/adapters/excel_adapter.py

key-decisions:
  - "Pinned BOTH the docProps timestamps (wb.properties.created/modified) AND every ZIP entry date_time for byte-reproducibility — pinning only the doc properties was insufficient because openpyxl stamps the save-time wall-clock into each zip local header independently (the original failure mode)"
  - "Used a CHART for the silent-loss fixture rather than an image: Pillow is not a declared dependency (openpyxl.drawing.image.Image requires it), and a chart exercises the identical ws._charts disclosure path the adapter walks for both charts and images"
  - "Authored formula_with_cache via post-save XML injection (replace openpyxl's empty <v /> with <v>20</v>) — openpyxl has no API to write a formula cache; the natural openpyxl output is precisely the no-cache crux case"
  - "[Rule 1] Fixed a real adapter determinism bug: Source.timestamp now derives from wb.properties.created (document-intrinsic, mirroring EmailAdapter's Date-header sourcing) instead of the now() default"

patterns-established:
  - "File-adapter golden corpora author byte-reproducible fixtures by neutralizing every embedded wall-clock (doc properties AND container/zip metadata), so the committed bytes are stable provenance and the determinism invariant is real"
  - "An adapter's Source.timestamp must be document-intrinsic (a Date header, an OOXML created property), never now(), or determinism + round-trip parity break"

requirements-completed: [ADAPT-03, ADAPT-06]

# Metrics
duration: 8min
completed: 2026-06-17
---

# Phase 5 Plan 04: Excel Golden-File Test Corpus Summary

**A committed, byte-reproducible 8-fixture `.xlsx` golden corpus + `tests/test_excel_golden.py` that makes a silent drop a TEST FAILURE — proving the Excel adapter's extract-vs-disclose fork (formula-cache crux, error cell, chart disclosure, merged anchor) holds the zero-silent-drops accounting identity, verbatim+content-addressed claims, conformance, determinism, and round-trip coverage parity across the whole matrix; and fixing a real adapter determinism bug uncovered en route.**

## Performance
- **Duration:** ~8 min
- **Started:** 2026-06-17T15:43:15Z
- **Completed:** 2026-06-17T15:51:17Z
- **Tasks:** 2 (TDD)
- **Files modified:** 11 (10 created, 1 modified)

## Accomplishments
- **A byte-reproducible `.xlsx` golden corpus, authored programmatically.** `tests/fixtures/xlsx/_author_fixtures.py` builds all 8 fixtures with openpyxl and is fully deterministic: it pins `wb.properties.created`/`modified` AND rewrites every ZIP entry's `date_time` to a fixed constant, so `sha256(file)` is stable across processes (threat T-05-11). The plan's reproducibility gate passes: `byte-reproducible: 8`.
- **The headline ADAPT-06 invariant, executable per fixture.** For every fixture `len(claims) + len(unextracted) == units walked`, exactly, with the EXACT ordered `unextracted[].reason` strings pinned from the LIVE adapter. A silent drop is a test failure by construction (threat T-05-10).
- **The faithfulness crux pinned.** `formula_no_cache.xlsx` (the natural openpyxl no-cache output) routes its formula cell to `unextracted[]` with the exact reason and emits NO `"0"`/`""` claim; the contrast fixture `formula_with_cache.xlsx` (XML-injected cache) emits the cached value `"20"` as a verbatim claim.
- **The full faithfulness matrix covered + asserted:** verbatim spans (`claim.text == trace.span == transcript[start:end]`), content-addressed traces (`is_addressed`), coverage honesty (`complete == (unextracted == [])`), `assert_conforms` + lossless JSON round-trip, determinism, and round-trip coverage parity (T-05-12) — all green for all 8 fixtures.
- **A real adapter determinism bug found and fixed (Rule 1).** `ExcelAdapter` left `Source.timestamp` at its `now()` default, so two parses of identical bytes produced non-equal Sources, breaking the determinism AND round-trip-parity success criteria. Fixed by sourcing the timestamp from `wb.properties.created` — the document-intrinsic analog of `EmailAdapter`'s Date header.

## The 8 fixtures + what each exercises

| Fixture | Exercises | Routing (claims / unextracted) |
|---------|-----------|-------------------------------|
| `formula_with_cache.xlsx` | a formula WITH a cached value (XML-injected `<v>20</v>`) | 2 claims `["2","20"]` / 0 — complete |
| `formula_no_cache.xlsx` | THE crux: openpyxl formula with NO cache | 1 claim `["2"]` / 1 (`formula cell A2 has no cached value (uncomputed: '=A1*10') — not faithfully extractable`) |
| `merged_cells.xlsx` | merged `A1:B2`; anchor emitted once, covered cells skipped | 2 claims `["merged header","below"]` / 0 — complete |
| `multi_sheet.xlsx` | workbook-order, row-major traversal across 2 sheets | 3 claims `["first one","first two","second one"]` / 0 — complete |
| `mixed_types.xlsx` | value->string rules: text/int/float/bool/date/datetime | 6 claims `["hello text","42","3.14","TRUE","2026-06-17T00:00:00","2026-06-17T09:30:00"]` / 0 — complete |
| `empty_cells.xlsx` | sparse cells with genuine blanks (blank != no-cache) | 2 claims `["top","bottom"]` / 0 — complete |
| `error_cell.xlsx` | a cell with `data_type=='e'` (`#DIV/0!`) | 1 claim `["real value"]` / 1 (`error cell A2: #DIV/0!`) |
| `chart_or_image.xlsx` | a chart -> the silent-loss disclosure (content out of scope) | 4 claims `["cat","val","x","5"]` / 1 (`Charted: chart not extracted (chart content is out of scope)`) |

**Confirmation:** the zero-silent-drops accounting identity AND round-trip coverage parity hold for ALL 8 fixtures (`test_zero_silent_drops` + `test_roundtrip_coverage_parity`, both parametrized over the full corpus, all green).

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the byte-reproducible .xlsx golden corpus** — `1f24e8e` (test)
2. **Task 2: Golden corpus test + fix non-deterministic Source.timestamp** — `3c3575b` (test, includes the Rule 1 adapter fix)

_TDD plan: each task bundled its RED authoring/test with the GREEN it proves; the determinism RED (8 failing `test_determinism` cases) was observed before the adapter fix took it GREEN — see TDD Gate Compliance._

## Files Created/Modified
- `tests/fixtures/xlsx/_author_fixtures.py` — deterministic openpyxl generator: `_finalize` (pins doc + zip timestamps via `_normalize_zip`), one builder per fixture with inline expected-routing docs, plus the post-save `<v>` cache-injection technique for `formula_with_cache`.
- `tests/fixtures/xlsx/*.xlsx` (8 files) — the committed, byte-reproducible corpus.
- `tests/test_excel_golden.py` — the golden suite: an `Expected`/`EXPECTED` table pinned from the live adapter, `_distill(name)` (fresh adapter per call), 6 parametrized invariant tests + the parametrized round-trip parity test, and 8 targeted per-fixture routing tests. Skips cleanly without the `[excel]` extra (module-level `pytestmark` skipif).
- `src/newsletters/adapters/excel_adapter.py` — **(Rule 1 fix)** `parse()` reads `wb.properties.created` and passes it as `Source.timestamp` when present; falls back to the default only when absent. No other behavior changed.

## Decisions Made
- **Byte-reproducibility needed TWO clocks neutralized, not one.** The first generator pinned only `wb.properties.created`/`modified` and the corpus still drifted run-to-run; diagnosis showed openpyxl writes each ZIP entry's local-header `date_time` from the save-time wall-clock independently. Added `_normalize_zip` to rewrite every entry's `date_time` to a fixed constant. (See Issues.)
- **Chart, not image, for the silent-loss fixture.** `openpyxl.drawing.image.Image` requires Pillow, which is not a declared dependency; embedding an image would have added one. A `BarChart` exercises the identical `ws._charts`/`ws._images` disclosure path with no new dependency. Documented inline in the fixture.
- **Formula-with-cache via XML injection.** openpyxl has no API to write a formula's cached value, and a normal save produces exactly the no-cache case. To author the contrast, the generator replaces openpyxl's emitted empty `<v />` with `<v>20</v>` in the worksheet XML, then rebuilds the zip in entry order — verified deterministic and verified to make the DATA view read `20`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Non-deterministic `Source.timestamp` in ExcelAdapter**
- **Found during:** Task 2 (the `test_determinism` invariant failed for all 8 fixtures).
- **Issue:** `ExcelAdapter.parse()` constructed `Source` without a `timestamp`, so it defaulted to `_utcnow()`. Two parses of identical bytes produced Sources differing only in `timestamp` (e.g. `...51.548333Z` vs `...51.555222Z`), failing BOTH the determinism and round-trip-parity success criteria (the persisted Source no longer re-distilled identically).
- **Fix:** `parse()` now sources `Source.timestamp` from `wb.properties.created` (read before closing the workbook) when it is a `datetime`, mirroring `EmailAdapter` sourcing its timestamp from the `Date` header rather than `now()`. Falls back to the default only when `created` is absent.
- **Files modified:** `src/newsletters/adapters/excel_adapter.py`
- **Verification:** all 8 `test_determinism` + 8 `test_roundtrip_coverage_parity` cases green; full suite 280 passed / 1 xfailed; mypy clean; lint-imports 1 kept / 0 broken; bare import does not load openpyxl.
- **Committed in:** `3c3575b` (Task 2 commit)
- **Scope note:** `excel_adapter.py` is owned by Plan 03. Per the plan's `<critical_correctness>`, an adapter bug is fixed only if "truly blocking" — this was: the determinism + round-trip-parity success criteria of ADAPT-06 cannot hold without a deterministic Source. The fix is minimal (timestamp sourcing only) and matches the established `EmailAdapter` pattern. Escalated here as a marked deviation rather than silently.

---

**Total deviations:** 1 auto-fixed (1 Rule 1 bug).
**Impact on plan:** The fix was necessary for two stated success criteria (determinism, round-trip parity) and changes no extraction behavior — it only makes the Source timestamp document-intrinsic. No scope creep. ExcelAdapter's existing 22 unit tests + 17 coverage-roundtrip tests stay green.

## Issues Encountered
- **Byte-reproducibility drifted despite pinned doc properties.** The first reproducibility gate failed; in-process the builders were deterministic but cross-process the bytes differed by one byte. Inspecting the zip revealed each entry's `date_time` was the current wall-clock (openpyxl stamps it at save, independent of `wb.properties`). Resolved by adding `_normalize_zip` to force a fixed `date_time` on every entry; the gate then reported `byte-reproducible: 8`. Caught and fixed during Task 1 before any commit.
- **Pillow unavailable for image fixtures.** `openpyxl.drawing.image.Image` raised `ImportError: You must install Pillow`. Resolved by using a chart for the silent-loss fixture (same `_charts`/`_images` disclosure path, no new dependency).

## Gate Results (re-run independently via `.venv/bin/python` — actual output)
- `pytest tests/test_excel_golden.py -q` → **56 passed**
- `pytest tests/test_excel_golden.py -k "formula_no_cache or silent_drops or merged or roundtrip" -q` → **32 passed, 24 deselected**
- `pytest -q` (full) → **280 passed, 1 xfailed** (baseline 224 passed / 1 xfailed; +56 new golden tests)
- `mypy src/newsletters/adapters src/newsletters/distill` → **Success: no issues found in 14 source files**
- `lint-imports` → **Contracts: 1 kept, 0 broken**
- `newsletters build` → **rendered 9 surfaces + the library index** (renderer still works)
- byte-reproducibility gate → **byte-reproducible: 8**
- openpyxl laziness → bare `import newsletters` does NOT load openpyxl (AI-optional core intact)

## TDD Gate Compliance
This plan is `type: tdd`. The corpus + tests were authored, then run against the LIVE adapter. The determinism invariant produced a genuine RED (8 failing `test_determinism` cases) that was observed before the adapter timestamp fix took it GREEN — the golden corpus did its job: it caught a real defect. RED and GREEN are committed together per task (the test file and the fix it requires share the same task), so there is no standalone `test(...)`-then-`feat(...)` commit pair; both task commits are `test(...)`-typed because the deliverable is the corpus + suite (the adapter change is a bundled Rule 1 fix). The MVP+TDD runtime gate (`MVP_MODE`/`TDD_MODE`) was not signalled active by the orchestrator (`tdd_mode: false`, `mvp_mode: false` in config), so the behavior-adding halt gate did not apply.

## Next Phase Readiness
- **Phase 5 (Excel adapter) is complete and ready for `/gsd-verify-work`.** The adapter (Plan 03) is now proven by a committed, byte-reproducible golden corpus that makes a silent drop a test failure by construction (ADAPT-06) and re-proves round-trip coverage parity on Excel. The formula-cache crux, error cells, chart disclosure, and merged anchors are all pinned.
- No blockers. No new dependency introduced (openpyxl stays the optional `[excel]` extra, reachable only lazily).

## Self-Check: PASSED
- Created files exist: `tests/fixtures/xlsx/_author_fixtures.py`, 8 `.xlsx` fixtures, `tests/test_excel_golden.py`, `.planning/phases/05-excel-adapter/05-04-SUMMARY.md`.
- Modified file exists: `src/newsletters/adapters/excel_adapter.py`.
- Commits exist: `1f24e8e` (Task 1), `3c3575b` (Task 2).

---
*Phase: 05-excel-adapter*
*Completed: 2026-06-17*
