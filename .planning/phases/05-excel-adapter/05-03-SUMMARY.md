---
phase: 05-excel-adapter
plan: 03
subsystem: adapters
tags: [openpyxl, xlsx, adapter, faithfulness, coverage, tdd, distill-port]

# Dependency graph
requires:
  - phase: 05-excel-adapter (plan 01)
    provides: "Typed coverage carrier (Source.extraction + ExtractionRecord/ExtractedDrop) + shared _coverage_codec (encode/decode/not_reconstructable_marker) + R2 safety-net + parametrized round-trip parity matrix"
  - phase: 05-excel-adapter (plan 02)
    provides: "[excel] extra + lazy _load_openpyxl()/load_workbook_pair() double-load + R4-confirmed ws._charts/ws._images attribute names"
  - phase: 04-shared-adapter-normalizer-email
    provides: "shared normalize(), DistillPort/assert_conforms, Coverage/Unextracted honesty, EmailAdapter pattern"
provides:
  - "ExcelAdapter: lazy-openpyxl double-load .xlsx -> canonical Sheet!A1<tab>value transcript -> verbatim units -> shared normalize()"
  - "The faithful per-cell fork: formula-no-cache / error cells -> unextracted[] (never 0/empty); merged anchor emitted once; charts/images disclosed"
  - "value_to_str: deterministic lossless R3 value->string (bool-before-int, str(int), repr(float), .isoformat())"
  - "Registered backend name 'excel' (resolve('excel')); assert_conforms passes; drops travel on Source.extraction (R1); malformed .xlsx disclosed-not-crashed"
  - "Excel joins tests/test_coverage_roundtrip.py ADAPTER_CASES (round-trip coverage parity proven for .xlsx)"
affects: [05-04-golden-corpus, 06, 07, adapters]

# Tech tracking
tech-stack:
  added: []  # openpyxl already declared by 05-02; this plan adds no new dependency
  patterns:
    - "Faithful per-cell fork decided from the FORMULA view's data_type, cache read from the DATA view (R3 double-load)"
    - "Canonical transcript Sheet!A1<sep>value as the single source of truth; units re-derived from it by an anchored record-prefix regex so distill() is stateless across a Source round-trip"
    - "Stateless adapter: drops carried on Source.extraction via the shared codec, never instance memory (R1)"

key-files:
  created:
    - src/newsletters/adapters/excel_adapter.py
    - tests/test_excel_adapter.py
  modified:
    - src/newsletters/adapters/__init__.py
    - tests/test_coverage_roundtrip.py

key-decisions:
  - "Transcript separator SEP = '\\t' (tab) per CONTEXT R3 / RESEARCH recommendation; values are NEVER escaped (an embedded tab/newline is emitted verbatim and stays locatable because normalize() does pure substring matching)"
  - "Followed the plan's TYPED carrier (Source.extraction) NOT the research's JSON-in-context — R1 overruled the research on the typed-everything convention; the Wave-1 APIs and plan must_haves mandate the typed carrier"
  - "Units are re-derived from the transcript in distill() via an anchored record-prefix regex (Sheet!coord<SEP>) rather than a naive '\\n' split, so a value containing '\\n'/SEP round-trips as one unit"
  - "Locator for unextracted entries = FreeLocator(text='Sheet!A1') (no CellLocator built, no Trace/normalize signature change — RESEARCH Open Q1)"

patterns-established:
  - "File adapters serialize their non-linear content into a deterministic canonical transcript whose lines carry the address prefix, so claim provenance (sheet!cell) is recoverable from the transcript and units stay verbatim-locatable"

requirements-completed: [ADAPT-03]

# Metrics
duration: ~6min
completed: 2026-06-17
---

# Phase 5 Plan 03: ExcelAdapter core (the faithful .xlsx fork) Summary

**A lazy-openpyxl `ExcelAdapter` that double-loads an `.xlsx`, serializes a canonical `Sheet!A1<tab>value` transcript with a deterministic lossless value->string rule, routes the formula-cache gap / error cells / charts / images / parse failures to `unextracted[]` (never a fabricated `0`/empty), feeds verbatim units to the shared `normalize()`, registers as `"excel"`, carries its drops on `Source.extraction`, and conforms — with round-trip coverage parity proven on the shared matrix.**

## Performance
- **Duration:** ~6 min
- **Started:** 2026-06-17T15:30:25Z
- **Completed:** 2026-06-17T15:36:37Z
- **Tasks:** 2 (TDD)
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- **The faithful per-cell fork (the ADAPT-03 criterion-2 crux).** `_cell_decision(cell_f, cell_d)` decides formula-ness from the FORMULA view (`data_type == 'f'`) and reads the cache from the DATA view. A formula cell with a `None` cache routes to `unextracted[]` naming the cell + formula — it is **never** emitted as `0`/`""`. A formula whose cache is itself an error code, and an error cell (`data_type == 'e'`), also route to `unextracted[]`. A genuinely blank cell is skipped.
- **Deterministic lossless `value_to_str`.** bool BEFORE int (`TRUE`/`FALSE`), int -> `str(int)` (no `.0`), float -> `repr(float)` (shortest round-trip), date/datetime/time -> `.isoformat()`, str verbatim.
- **Canonical transcript + verbatim units.** `_serialize` walks both views in workbook order, row-major, emitting one `Sheet!A1<tab>value\n` line per emitted cell and collecting the SAME value strings as the ordered units. Every unit is by construction an exact substring of the transcript; duplicates get distinct, forward-only offsets via `normalize()`'s cursor.
- **Merged ranges accounted faithfully.** The top-left anchor's value is emitted once (covered cells are `None` and skipped) — a 2x2 merge yields exactly 1 claim, and the merge is **not** a drop (nothing is lost).
- **Silent-loss objects disclosed.** `_feature_drops` scans `ws._charts` / `ws._images` (R4-confirmed, standard mode) and discloses each as `unextracted[]`.
- **Stateless, round-trip-safe.** `parse()` sets `source.extraction = encode_coverage(drops)`; `distill()` re-derives units from the transcript (anchored record-prefix regex) and recovers drops via `decode_coverage(source.extraction)`, with the R2 safety-net for unaccountable Sources. Round-trip coverage parity proven for `.xlsx` on the shared `ADAPTER_CASES` matrix.
- **Robust to untrusted input (V5).** A malformed `.xlsx` (openpyxl raises) is caught and disclosed as a single whole-source `unextracted[]` entry; both workbooks are always `.close()`d (no leak); never an unhandled crash.
- **Registered + conforms.** `register(ExcelAdapter())`; `resolve("excel")` works; `assert_conforms(ExcelAdapter(), [source])` passes. Bare import unaffected (openpyxl stays lazy; top-level import grep count = 0).

## Adapter API (for Wave 3 / Plan 04 golden corpus)

**Registered name:** `"excel"` — `newsletters.distill.resolve("excel")` returns the instance after `import newsletters.adapters`.

**Entrypoints (mirror EmailAdapter):**
```python
ExcelAdapter().parse(raw: bytes, path: str) -> tuple[Source, list[str] units, list[Unextracted] drops]
ExcelAdapter().distill(sources: list[Source]) -> DistillationResult
```
`parse()` double-loads `raw` via `load_workbook_pair`, builds the transcript + units, collects drops, and sets `source.extraction = encode_coverage(drops)`. `distill()` is stateless: it re-derives units from `source.transcript` and recovers drops from `source.extraction`, so a JSON-round-tripped Source distills identically on a fresh adapter.

**Transcript layout + separator:** one record per emitted cell, `"{sheet}!{coord}{SEP}{value}\n"`, where `SEP = "\t"` (a tab). Sheets in workbook order, row-major. Values are NEVER escaped — an embedded tab/newline is emitted verbatim and stays locatable (normalize does pure substring matching). Units are recovered from the transcript by an anchored record-prefix regex `[^\n]+?![A-Z]+[0-9]+\t` at line start, so a multi-line value round-trips as one unit.

**value->string rules (as implemented in `value_to_str`):**

| Python type | Output | Note |
|-------------|--------|------|
| `bool` | `"TRUE"` / `"FALSE"` | checked BEFORE int (bool is an int subclass) |
| `int` | `str(int)` | `1` -> `"1"`, never `"1.0"` |
| `float` | `repr(float)` | shortest round-trip; `1.0` -> `"1.0"`, `0.1+0.2` -> exact |
| `datetime` | `.isoformat()` | e.g. `2026-06-17T09:30:00` |
| `date` | `.isoformat()` | e.g. `2026-06-17` |
| `time` | `.isoformat()` | e.g. `09:30:15` |
| `str` (and fallback) | verbatim | passthrough |

**Exact `unextracted[]` reason strings (Plan 04 pins these):**

| Case | Reason string (`{...}` are filled) | Locator |
|------|-------------------------------------|---------|
| formula, no cache | `formula cell {coord} has no cached value (uncomputed: {formula!r}) — not faithfully extractable` | `FreeLocator(text="Sheet!coord")` |
| formula -> error cache | `formula cell {coord} evaluates to error {err}` | `FreeLocator(text="Sheet!coord")` |
| error cell (`data_type=='e'`) | `error cell {coord}: {err}` | `FreeLocator(text="Sheet!coord")` |
| chart | `{sheet}: chart not extracted (chart content is out of scope)` | `FreeLocator(text=sheet)` |
| image | `{sheet}: image not extracted (drawing content is out of scope)` | `FreeLocator(text=sheet)` |
| unreadable workbook (parse failure) | `workbook could not be read by openpyxl ({error}) — not extractable` | `FreeLocator(text=path)` |

(`coord` is the cell coordinate like `B2`; the unextracted locator's `display` is `"{sheet}!{coord}"`. The R2 marker reason `coverage-not-reconstructable` is supplied by the shared codec, not the adapter.)

**Error codes:** `_ERROR_CODES = {#NULL!, #DIV/0!, #VALUE!, #REF!, #NAME?, #NUM!, #N/A}` (openpyxl ERROR_CODES).

**Merged ranges:** the anchor value is a normal non-`None` cell in the walk and is emitted once; the N-1 covered cells read `None` and are skipped as blank. A merge is faithfully extracted (nothing lost) and is therefore NOT recorded in `unextracted[]`.

## Task Commits
1. **Task 1: Excel per-cell fork + value_to_str + transcript serialization** — `20be78b` (feat)
2. **Task 2: register ExcelAdapter as 'excel', conform, join coverage-parity matrix** — `0b6371c` (feat)

## Files Created/Modified
- `src/newsletters/adapters/excel_adapter.py` — the adapter: `value_to_str`, `_cell_decision`, `_feature_drops`, `_serialize`, `_split_transcript_units`/`_RECORD_PREFIX`, and the `ExcelAdapter` class (parse/distill/_units_for). openpyxl reached only via `_openpyxl_loader` (lazy).
- `src/newsletters/adapters/__init__.py` — `register(ExcelAdapter())` alongside `EmailAdapter`; added to `__all__`.
- `tests/test_excel_adapter.py` — 22 unit tests: value_to_str, the per-cell fork, merged/blank/duplicate/embedded-newline transcript, parse/distill end-to-end, formula-cache gap, multi-sheet order, drops-on-extraction, registration, conformance, malformed-input disclosure, sheet!cell locators.
- `tests/test_coverage_roundtrip.py` — appended one `pytest.param(excel)` to `ADAPTER_CASES` (skipif no openpyxl) with in-memory `.xlsx` fixtures (literals, formula gap, error cell); proves round-trip coverage parity for Excel on the shared matrix.

## Decisions Made
- Followed the plan and R1/R2/R3 exactly. The one judgment call worth recording: the **research recommended JSON-on-`Source.context`** for the coverage carrier, but the plan's `must_haves`/`key_links` and the Wave-1 dependency APIs mandate the **typed `Source.extraction` carrier** (R1 explicitly overruled the research). I used the typed carrier (`encode_coverage`/`decode_coverage`), consistent with the Email retrofit.
- Unit recovery in `distill()` uses an anchored record-prefix regex rather than a naive `\n` split, so a cell value containing `\n` or a tab round-trips as exactly one unit (proven by `test_value_with_embedded_newline_round_trips_as_one_unit`). This keeps `claim.text == transcript slice` (the Phase-3 span-containment gate) for pathological values.

## Deviations from Plan
None — plan executed exactly as written. No deviation rules (1-4) fired; no architectural change; no auth gate; no package install (openpyxl was declared by 05-02).

## TDD Gate Compliance
This plan is `type: tdd`. Each of the two tasks bundled its RED tests and GREEN implementation into a single `feat(...)` commit (the test and implementation share files, and each task's `<action>` directs "write tests FIRST (RED), then implement to GREEN"). The RED step was executed and verified before implementation — `pytest tests/test_excel_adapter.py` failed with `ModuleNotFoundError: No module named 'newsletters.adapters.excel_adapter'` prior to writing the module — but there is **no standalone `test(...)` RED commit**; RED and GREEN are committed together per task. The MVP+TDD runtime gate (`MVP_MODE`/`TDD_MODE`) was not signalled active by the orchestrator, so the behavior-adding halt gate did not apply.

## Issues Encountered
- The initial transcript inverse (`_record_end` heuristic) was fragile for values containing both a tab and a newline. Replaced before any commit with a precise anchored record-prefix regex (`_RECORD_PREFIX`) that splits on true record boundaries. Pinned by `test_value_with_embedded_newline_round_trips_as_one_unit`. (Caught and fixed during Task 1 implementation; not a post-commit defect.)

## Gate Results (re-run independently via `.venv/bin/python` — actual output)
- `pytest tests/test_excel_adapter.py -q` → **22 passed**
- `pytest tests/test_coverage_roundtrip.py -q` → **17 passed** (14 original + 3 new excel parity params)
- `pytest -q` (full) → **224 passed, 1 xfailed** (baseline 199 passed/1 xfailed; +25 new)
- `mypy src/newsletters/adapters src/newsletters/distill` → **Success: no issues found in 14 source files**
- `lint-imports` → **Contracts: 1 kept, 0 broken** (openpyxl is not AI; lazy; no new edge)
- `python -c "import newsletters; print('ok')"` → **ok** (bare import works without [excel])
- `grep -v '^#' excel_adapter.py | grep -c "^import openpyxl\|^from openpyxl"` → **0** (openpyxl stays lazy)
- registration → `available()` == `['email', 'excel']`

## Next Phase Readiness
- **Wave 3 (Plan 04, golden corpus) is unblocked.** It can author byte-reproducible `.xlsx` fixtures and drive `ExcelAdapter().parse(...)`/`distill(...)` against the documented transcript layout, value->string table, and exact `unextracted[]` reason strings above. The zero-silent-drops identity is honest per-cell + per-feature; the round-trip coverage parity already passes on the shared matrix.

## Self-Check: PASSED
- Created files exist: `src/newsletters/adapters/excel_adapter.py`, `tests/test_excel_adapter.py`, `.planning/phases/05-excel-adapter/05-03-SUMMARY.md`.
- Commits exist: `20be78b` (Task 1), `0b6371c` (Task 2).

---
*Phase: 05-excel-adapter*
*Completed: 2026-06-17*
