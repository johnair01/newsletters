---
phase: 07-power-bi-adapter
plan: 04
subsystem: adapters
tags: [adapter, powerbi, pbip, tmdl, pbir, golden-file, fixtures, zero-silent-drops, fail-loud, determinism]
requires:
  - "newsletters.adapters.powerbi_adapter.PowerBiAdapter (07-03) — parse_path/parse/distill + the _R_* taxonomy"
  - "newsletters.adapters.normalize.normalize (the faithful gate, for the zero-silent-drops accounting)"
  - "newsletters.distill.{assert_conforms, DistillationResult} (conformance + JSON round-trip)"
provides:
  - "tests/fixtures/powerbi/_author_fixtures.py — stdlib write_text generator for the byte-reproducible PBIP/TMDL tree + the .pbix deferral byte fixture"
  - "tests/fixtures/powerbi/sample.PBIP-tree/ — the committed PBIP corpus (TMDL model + relationship + plain + Top-N/summarized visuals)"
  - "tests/fixtures/powerbi/fake.pbix — the few-byte .pbix deferral fixture"
  - "tests/test_powerbi_golden.py — the ADAPT-06 golden corpus suite (zero silent drops, the row-cap taxonomy, conformance, determinism, round-trip parity)"
affects:
  - "tests/ (new golden suite; +13 tests joining the full run)"
tech-stack:
  added: []   # ZERO new dependency — the corpus is hand-authored plain text (no openpyxl/python-pptx)
  patterns:
    - "byte-reproducible fixture authoring via stdlib pathlib.write_text/write_bytes (no clock, no random)"
    - "pin the _R_* taxonomy by DRIVING the live adapter, never hand-guessing (A1 resolution)"
    - "import the _R_* reason constants from the adapter so a drift on EITHER side fails the suite"
    - "zero-silent-drops asserted as the normalize accounting (claims + normalize-misses == units)"
key-files:
  created:
    - tests/fixtures/powerbi/_author_fixtures.py
    - tests/fixtures/powerbi/sample.PBIP-tree/  (12 committed files)
    - tests/fixtures/powerbi/fake.pbix
    - tests/test_powerbi_golden.py
  modified: []
decisions:
  - "the committed PBIP tree is hand-authored plain text via stdlib write_text — NO authoring dependency (the headline advantage over the excel/pptx goldens, which needed openpyxl/python-pptx)"
  - "the golden has NO skip-mark — the powerbi adapter is stdlib-only, so the corpus runs on a bare install (unlike the pptx/excel goldens that skipif their extra)"
  - "the JSON fixture shapes mirror the shapes the 07-03 unit suite already proved drive the live detectors, so the row-cap taxonomy is pinned by driving the live adapter (A1), not assumed"
  - "zero-silent-drops is asserted as claims + normalize-misses == units walked; the adapter-side _R_* drops (measure-value/row-cap/no-data-rows) are ADDITIONAL honest disclosures, pinned separately"
metrics:
  duration: ~15m
  completed: 2026-06-18
  tasks: 2
  files_created: 4
  files_modified: 0
---

# Phase 7 Plan 4: Power BI Golden Corpus Summary

A hand-authored, byte-reproducible PBIP/TMDL fixture tree written with stdlib `write_text` (NO
authoring dependency — the headline advantage over the Excel/PPTX goldens) drives the LIVE
`PowerBiAdapter` end-to-end and PROVES zero silent drops, the exact row-cap/aggregation `_R_*`
taxonomy, verbatim content-addressed claims (including the measure's DAX as text, never a value),
conformance, Source determinism, and round-trip coverage parity — closing ROADMAP Phase-7
success-criterion 3 (ADAPT-06).

## What was built

- **`tests/fixtures/powerbi/_author_fixtures.py`** — a stdlib-only generator (`pathlib.write_text` /
  `write_bytes`, no `now()`/`random`, every byte a literal) that writes the committed corpus
  byte-reproducibly across processes. Each builder's docstring documents what its fixture exercises.
- **`tests/fixtures/powerbi/sample.PBIP-tree/`** (12 committed files) — a minimal but complete PBIP
  project authored against the documented PBIR `visualContainer` + Power BI filter shape (A1):
  - PBIP entry pointers (`sample.pbip`, `definition.pbism`) — committed so the tree is a real PBIP.
  - `sample.SemanticModel/definition/` (TMDL): `model.tmdl` (culture + `ref` lines the parser skips),
    `relationships.tmdl` (one Sales→Product relationship), `tables/Sales.tmdl` (a `///` description, a
    measure `'Total Sales'` with verbatim DAX `SUMX(...)` + `formatString`, two columns with
    `dataType` + `summarizeBy`), `tables/Product.tmdl` (the key column).
  - `sample.Report/definition/` (PBIR): `definition.pbir`, `report.json`, `pages/pages.json`,
    `pages/Overview/page.json` (displayName "Overview"), a **plain** `plainTable/visual.json`
    (literal title + a column field projection → claims, no cap), and a **Top-N + Sum-summarized +
    maxRows-capped** `topProducts/visual.json` (the disclose side of the fork; criterion-3 fixture).
- **`tests/fixtures/powerbi/fake.pbix`** — a 43-byte non-PBIP binary (ZIP magic + filler) for the
  `_R_PBIX_BINARY` deferral; the ZIP is NEVER decompressed (pbixray DEFERRED, zero new dependency).
- **`tests/test_powerbi_golden.py`** (13 tests, NO skip-mark — the adapter is stdlib-only so it runs
  on a bare install) — imports the `_R_*` constants FROM the adapter and drives the LIVE adapter over
  the committed corpus.

## What each fixture exercises (pinned by driving the live adapter)

| Fixture artifact | Exercises | Live result (pinned) |
|------------------|-----------|----------------------|
| `tables/Sales.tmdl` measure | verbatim DAX claim + absent value disclosed | `SUMX(...)` claim + `_R_MEASURE_VALUE` |
| `tables/Sales.tmdl` columns / `///` / table name | TMDL extraction | verbatim claims (`int64`, the description, …) |
| `relationships.tmdl` | relationship endpoints | `Sales.'Product Key'` / `Product.'Product Key'` claims |
| `plainTable/visual.json` | the extract side | title `Sales by product` + field `Sales.Quantity` claims, no cap |
| `topProducts/visual.json` | the disclose side (criterion 3) | EXACTLY `_R_TOPN` + `_R_AGGREGATED` + `_R_ROWLIMIT` |
| every model export | the categorical truth | `_R_NO_DATA_ROWS` once → `complete is False` |
| `fake.pbix` | the L1 deferral | exactly `_R_PBIX_BINARY`, empty transcript, `complete False`, no crash |

The PBIP tree walks **21 units**, all 21 become content-addressed verbatim claims (zero normalize
misses), plus 5 adapter-side disclosures in this emission order:
`_R_MEASURE_VALUE`, `_R_TOPN`, `_R_AGGREGATED`, `_R_ROWLIMIT`, `_R_NO_DATA_ROWS`.

## Confirmation of the load-bearing invariants

- **Zero silent drops** — `len(claims) + len(normalize-misses) == len(units)` (21 + 0 == 21); a
  silent drop is, by construction, a test failure (T-07-14).
- **The `_R_*` taxonomy is pinned by driving the live adapter** (A1), in emission order, with the
  constants imported from the adapter so a drift on EITHER side fails (T-07-15).
- **Round-trip coverage parity + Source determinism** hold: persisting the Source and distilling on a
  FRESH adapter yields identical coverage; two parses produce byte-identical Sources (`timestamp ==
  EPOCH_ZERO`).
- **No real adapter bug found.** The committed JSON shapes (mirroring the 07-03 unit suite's proven
  shapes) drove every detector first try; `powerbi_adapter.py` / `_tmdl.py` / `_pbir.py` were NOT
  touched.

## Verification (gates re-run independently — ACTUAL output)

- `pytest tests/test_powerbi_golden.py -q` → **13 passed**.
- `pytest -q` (full) → **447 passed, 1 xfailed** (baseline 434 passed + 1 xfailed; +13 = the new
  golden suite).
- `mypy src/newsletters/adapters src/newsletters/distill` → **Success: no issues found in 20 source
  files**.
- `lint-imports` → **Contracts: 1 kept, 0 broken** (AI-isolation intact; zero new dependency).
- `python -c "import newsletters; import newsletters.adapters; resolve('powerbi')"` → **powerbi**
  (bare-install registration green).
- `newsletters build` → **rendered 9 surfaces + the library index** (CLI unaffected).

## Deviations from Plan

None — the plan executed exactly as written. No auto-fixes, no architectural changes, no auth gates.
The fixtures and golden suite are the only deliverables; the adapter and its parsers were left
untouched (read-only verification per the plan's critical-correctness boundary).

## Authentication gates

None — fully autonomous, no checkpoints, no installs (zero new dependency).

## Known Stubs

None. The golden drives the real adapter end to end over real committed fixtures; every `_R_*` reason
is a concrete imported constant. No placeholder values flow anywhere.

## Threat surface scan

No NEW security surface beyond the plan's `<threat_model>`. All four registered mitigations are
realized: T-07-14 (the accounting identity is asserted per fixture), T-07-15 (the golden imports the
`_R_*` constants and pins them by driving the live adapter), T-07-16 (the generator uses stdlib
`write_text` only, no clock/random; Source determinism is asserted on the PARSED Source), T-07-SC
(zero new dependency — hand-authored plain text, no install task).

## Self-Check: PASSED

- `tests/fixtures/powerbi/_author_fixtures.py` — FOUND
- `tests/fixtures/powerbi/sample.PBIP-tree/sample.SemanticModel/definition/tables/Sales.tmdl` — FOUND
- `tests/fixtures/powerbi/fake.pbix` — FOUND
- `tests/test_powerbi_golden.py` — FOUND
- commit `22dc728` (Task 1, fixtures) — FOUND
- commit `58cd86b` (Task 2, golden suite) — FOUND
