---
phase: 06-powerpoint-adapter
plan: 04
subsystem: testing
tags: [python-pptx, pptx, golden-corpus, smartart, grouped-shapes, determinism, coverage-parity, fixtures]

# Dependency graph
requires:
  - phase: 06-03
    provides: "PptxAdapter (registered 'pptx') + the exact unextracted reason strings + the group-accounting rule + timestamp sourcing"
  - phase: 06-02
    provides: "lazy python-pptx loader + the SmartArt diagram-URI recipe + the bare-install gate"
  - phase: 06-01
    provides: "deterministic_timestamp()/EPOCH_ZERO + the documented determinism-matrix SEAM"
  - phase: 05
    provides: "the byte-reproducible xlsx generator + golden-test methodology to mirror; Source.extraction carrier; the parity matrix"
provides:
  - "A 9-file byte-reproducible .pptx golden corpus incl. SmartArt + a nested group (ROADMAP criterion 3), plus title+body/text box/table/notes/chart/image/empty slide"
  - "tests/test_pptx_golden.py — zero-silent-drops (incl. nested-group accounting), verbatim+content-addressed, conformance+JSON round-trip, Source-determinism (L5), round-trip coverage parity, per-fixture routing"
  - "The pptx backend joined to BOTH the round-trip coverage-parity matrix and the cross-adapter determinism matrix"
affects: [phase-06-verification, golden-corpus, adapter-conformance]

# Tech tracking
tech-stack:
  added: []  # python-pptx was added by 06-02; this plan only consumes it
  patterns:
    - "Programmatic byte-reproducible .pptx generator mirroring the Phase-4/5 xlsx generator (pinned core props + _normalize_zip)"
    - "Recurse _normalize_zip into a chart's EMBEDDED .xlsx to pin its openpyxl core.xml — the one cross-process drift python-pptx leaves"
    - "Golden expectations DERIVED from the live adapter (not assumed); reason strings IMPORTED from pptx_adapter so any drift is a failure"

key-files:
  created:
    - "tests/fixtures/pptx/_author_fixtures.py"
    - "tests/fixtures/pptx/{title_body,text_box,table,notes,chart,image,smartart,nested_group,empty_slide}.pptx"
    - "tests/test_pptx_golden.py"
  modified:
    - "tests/test_coverage_roundtrip.py"
    - "tests/test_timestamp_determinism.py"

key-decisions:
  - "Determinism asserted on the PARSED Source (s1.model_dump_json()==s2.model_dump_json()), NOT on re-saved .pptx bytes — the L5 property ADAPT-06 needs, immune to python-pptx re-save drift (risk A3)."
  - "The chart fixture's ONE cross-process nondeterminism is its embedded chart-data .xlsx (openpyxl stamps a wall-clock created/modified). Pinned by recursing _normalize_zip into the embedded workbook + rewriting dcterms:created/modified to a fixed instant — so even the chart fixture is byte-reproducible (not strictly required, but a clean git diff)."
  - "Golden EXPECTED table derived by driving the live PptxAdapter over each committed fixture; reason strings imported from pptx_adapter (_R_CHART/_R_PICTURE/_R_SMARTART) so a drift on either side fails the build."
  - "The determinism-matrix pptx 'no-intrinsic' case strips dcterms:created from the saved zip (python-pptx refuses created=None AND the default template embeds a fixed 2013 date); the 'with-intrinsic' case uses that fixed 2013-01-27T09:14:16Z template date (deterministic, not wall-clock)."

patterns-established:
  - "Per-fixture builder docstring pins the EXPECTED routing (claims vs unextracted); the golden test asserts it against the live adapter — the executable faithfulness contract."
  - "Optional-extra test modules gate with importlib.util.find_spec('pptx') and keep ALL python-pptx imports local to recipe functions, so the modules import (and the bare-install gate stays green) without the [pptx] extra."

requirements-completed: [ADAPT-04, ADAPT-06]

# Metrics
duration: ~7min
completed: 2026-06-17
---

# Phase 6 Plan 04: PowerPoint Golden-File Corpus Summary

**A 9-fixture byte-reproducible `.pptx` golden corpus — including the ROADMAP criterion-3 SmartArt + nested-group decks — that drives `PptxAdapter` end-to-end asserting zero silent drops (with exact nested-group leaf accounting), verbatim content-addressed claims, conformance + lossless JSON round-trip, determinism on the parsed Source (L5), and round-trip coverage parity, and joins the cross-adapter parity + determinism matrices.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-17T16:45Z
- **Completed:** 2026-06-17T16:52Z
- **Tasks:** 2
- **Files modified:** 13 (12 created, 2 modified — 1 modified file pair listed once)

## Accomplishments
- A committed, byte-reproducible 9-file `.pptx` corpus authored by a documented generator: SmartArt (XML-injected diagram `graphicFrame`) + a NESTED group (the ROADMAP criterion-3 pair), plus title+body, free text box, table, speaker notes, chart, embedded 1x1-PNG image, and an empty slide.
- `tests/test_pptx_golden.py`: for EVERY fixture — zero-silent-drops (`#claims + #unextracted == #units`), verbatim spans (`claim.text == trace.span == transcript slice`) + content-addressed (`trace.is_addressed`), coverage honesty, `assert_conforms` + lossless JSON round-trip, **determinism on the parsed Source** (`model_dump_json` equal on two parses, L5), and round-trip coverage parity on a FRESH adapter.
- Targeted routing proofs: SmartArt is disclosed and emits NO text claim; the nested group's readable member IS extracted while its unreadable picture member IS disclosed and the two group nodes contribute nothing (the L3 nested accounting); chart + image disclosed not extracted; the empty slide loses nothing.
- The pptx backend joined BOTH the round-trip coverage-parity matrix (`test_coverage_roundtrip.py`, reading the committed corpus) and the cross-adapter determinism matrix (`test_timestamp_determinism.py`, `timestamp == EPOCH_ZERO` for a stripped-`created` deck + the intrinsic 2013 template date preserved).

## Task Commits

1. **Task 1: byte-reproducible `.pptx` generator + 9 fixtures** - `916d69e` (test)
2. **Task 2: golden test + parity/determinism matrix joins** - `95d20b3` (test)

## Files Created/Modified
- `tests/fixtures/pptx/_author_fixtures.py` (created) - The programmatic byte-reproducible generator: 1x1 PNG byte literal (Pillow-free), author-then-group + nested-group, XML-injected SmartArt frame, pinned core props, `_normalize_zip` recursing into the chart's embedded `.xlsx`.
- `tests/fixtures/pptx/*.pptx` (9 created) - The committed corpus.
- `tests/test_pptx_golden.py` (created) - The golden corpus: the 7 per-fixture invariants + 7 targeted routing assertions; reason strings imported from `pptx_adapter`.
- `tests/test_coverage_roundtrip.py` (modified) - Added the `pptx` param to `ADAPTER_CASES` (`_pptx_adapter_factory` + `_pptx_fixtures` reading the committed corpus, skipif no python-pptx).
- `tests/test_timestamp_determinism.py` (modified) - Joined the documented SEAM with the `(_pptx_factory, _pptx_no_created, _pptx_with_created)` param (`_strip_created_from_pptx` helper; local python-pptx imports only).

## Decisions Made
See `key-decisions` frontmatter. Headline: determinism is asserted on the parsed **Source** (L5), not on re-saved `.pptx` bytes; the chart fixture's only cross-process byte drift (its embedded openpyxl chart-data workbook) is pinned by recursing `_normalize_zip` into it, so the whole corpus is byte-reproducible across processes.

## Deviations from Plan
None - plan executed exactly as written.

(The plan flagged byte-identical re-saved `.pptx` files as a nice-to-have, not a blocker — the Source-determinism property being the one ADAPT-06 needs. We achieved full byte-reproducibility anyway by pinning the chart's embedded workbook timestamps; this is within the plan's `_normalize_zip` mandate, not a scope change.)

## Issues Encountered
- **Chart fixture cross-process byte drift.** A fresh `chart.pptx` build did not match the committed bytes: python-pptx packages a chart by embedding a real `.xlsx` of the chart data, and openpyxl stamps that inner workbook's `docProps/core.xml` with a wall-clock `created`/`modified`. Resolved by recursing `_normalize_zip` into any embedded `.xlsx` and rewriting `dcterms:created`/`modified` to a fixed W3CDTF instant — confirmed byte-reproducible across regeneration (the other 8 fixtures were already stable).
- **No high-level way to author a no-intrinsic-timestamp `.pptx`.** python-pptx refuses `core_properties.created = None` (validates a datetime) AND its default template embeds a fixed 2013 created date. Resolved exactly like the xlsx case: `_strip_created_from_pptx` removes `dcterms:created` from the saved zip's `core.xml`, so the adapter reads `None` -> `EPOCH_ZERO`.

## Real Adapter Bug Found
None. The live `PptxAdapter` (06-03) matched every pinned expectation exactly — counts, ordered reason strings, nested-group accounting, timestamp sourcing, and round-trip parity all held without touching `pptx_adapter.py`.

## Known Stubs
None. Every fixture is wired and asserted; no placeholder/TODO/empty-data stubs.

## Threat Flags
None. The corpus introduces no new security surface — the fixtures are constant bytes (a 68-byte PNG literal, a minimal SmartArt dataModel), and the adapter (06-03) reads only shape TYPE + text, never embedded image/OLE/media bytes.

## User Setup Required
None - no external service configuration required.

## Gate Results (re-run independently)
- `pytest tests/test_pptx_golden.py tests/test_coverage_roundtrip.py tests/test_timestamp_determinism.py -x -q` → **93 passed**.
- `pytest -q -k pptx` (the matrix joins specifically) → **5 passed** (3 parity + 2 determinism — the params ran, not skipped).
- `pytest -q` (full) → **383 passed, 1 xfailed** (baseline 316 passed + 1 xfailed; +67 new).
- `mypy src/newsletters/adapters src/newsletters/distill` → Success, no issues (17 files).
- `lint-imports` → 1 kept / 0 broken.
- `newsletters build` → rendered 9 surfaces + library index, no errors.
- Bare-install AI-isolation (`tests/test_ai_optional.py`) → 14 passed, 1 xfailed; all three pptx test modules import without triggering python-pptx at top level (the [pptx] params skip cleanly when absent).
- Corpus byte-reproducibility: regenerating writes byte-identical files for all 9 fixtures (no now()/random leak).

## Next Phase Readiness
- Phase 6 is COMPLETE: the PowerPoint adapter (06-03) now has its executable proof of correctness (the golden corpus) and is joined to the cross-adapter parity + determinism matrices.
- The corpus + generator are the template for any future file adapter's golden suite (the chart-embedded-workbook normalization gotcha is documented in `_author_fixtures.py`).
- No blockers.

## Self-Check: PASSED
- FOUND: tests/fixtures/pptx/_author_fixtures.py
- FOUND: tests/fixtures/pptx/smartart.pptx + nested_group.pptx + the other 7
- FOUND: tests/test_pptx_golden.py
- FOUND commits: 916d69e (test corpus), 95d20b3 (test golden + matrix joins)

---
*Phase: 06-powerpoint-adapter*
*Completed: 2026-06-17*
