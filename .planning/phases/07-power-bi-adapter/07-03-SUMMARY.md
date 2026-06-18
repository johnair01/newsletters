---
phase: 07-power-bi-adapter
plan: 03
subsystem: adapters
tags: [adapter, powerbi, pbip, tmdl, pbir, distill-port, faithful-extraction, coverage, fail-loud]
requires:
  - "newsletters.adapters.normalize.normalize (the ONE faithful gate)"
  - "newsletters.adapters._tmdl.parse_tmdl (Wave-1, 07-01)"
  - "newsletters.adapters._pbir.{Detection,extract_report,detect_row_caps} (Wave-1, 07-02)"
  - "newsletters.adapters._coverage_codec (encode/decode/not_reconstructable_marker)"
  - "newsletters.adapters._timestamps.deterministic_timestamp (EPOCH_ZERO)"
  - "newsletters.distill.{register,resolve,ports,coverage,conformance}"
provides:
  - "PowerBiAdapter — registered DistillPort backend 'powerbi'"
  - "parse_path(folder) + parse(bytes) -> (Source, units, drops); ONE serializer"
  - "the _R_* unextracted[] taxonomy (TOPN/FILTER/AGGREGATED/MEASURE_VALUE/DIRECTQUERY/ROWLIMIT/NO_DATA_ROWS/PBIX_BINARY/UNREADABLE/BINARY_FILE)"
affects:
  - "src/newsletters/adapters/__init__.py (registration)"
  - "tests/test_coverage_roundtrip.py (powerbi parity param)"
  - "tests/test_timestamp_determinism.py (powerbi determinism param)"
tech-stack:
  added: []   # ZERO new dependency — stdlib only (pbixray DEFERRED, L1)
  patterns:
    - "mirror excel/pptx adapter contract: parse -> units -> normalize -> carrier -> register -> conform"
    - "anchored _RECORD_PREFIX regex unit recovery (never split values on \\n/\\t/:)"
    - "multi-file transcript with per-unit object-path prefix"
key-files:
  created:
    - src/newsletters/adapters/powerbi_adapter.py
    - tests/test_powerbi_adapter.py
  modified:
    - src/newsletters/adapters/__init__.py
    - tests/test_coverage_roundtrip.py
    - tests/test_timestamp_determinism.py
decisions:
  - "timestamp ALWAYS EPOCH_ZERO — PBIP has no single intrinsic date (never mtime)"
  - "a measure's DAX expression drives both a verbatim claim AND a _R_MEASURE_VALUE drop"
  - "_R_NO_DATA_ROWS emitted ONCE per model export -> Coverage.complete=False (fail loud)"
  - "TMSL model.bim accepted as a secondary JSON model path"
  - "relaxed determinism test's '!= EPOCH_ZERO' guard for PBIP's always-EPOCH_ZERO contract (Rule 3)"
metrics:
  duration: ~25m
  completed: 2026-06-18
  tasks: 3
  files_created: 2
  files_modified: 3
---

# Phase 7 Plan 3: PowerBiAdapter Summary

Registered the stdlib `"powerbi"` DistillPort backend that composes the Wave-1 TMDL parser and PBIR
reader onto the shared faithful spine — a PBIP folder (or a single dropped `.tmdl`/`.json`/`.bim`, or
a `.pbix` byte-deferral) becomes a content-addressed `Distillation` whose row-cap/aggregation/
data-absence signals fail loud via a precise `_R_*` `unextracted[]` taxonomy, with ZERO new dependency.

## What was built

- **`PowerBiAdapter`** (registered `"powerbi"`), mirroring `excel_adapter.py`/`pptx_adapter.py`:
  - `parse_path(path: str) -> (Source, list[str], list[Unextracted])` — walks a PBIP FOLDER tree
    (every directory listing `sorted()`), `*.SemanticModel/definition/**/*.tmdl` then the
    `*.Report/definition/**` page/visual tree, plus TMSL `model.bim`. A single dropped-file path is
    delegated to `parse`.
  - `parse(raw: bytes, path: str) -> (Source, list[str], list[Unextracted])` — a single dropped
    `.tmdl`/`.json`/`.bim`; a `.pbix`/ZIP/OLE byte input (sniffed by magic bytes AND `.pbix` suffix)
    routes to the whole-source `_R_PBIX_BINARY` deferral (the ZIP is NEVER decompressed).
  - `distill(sources) -> DistillationResult` — re-derives units from the transcript, recovers drops
    from `Source.extraction`, calls the shared `normalize()`, returns truth only (never publishes).
  - Both entrypoints converge on ONE serializer (`_serialize_tree` / `_serialize_tmdl_text` /
    `_serialize_report_json`); unit recovery via the anchored `_RECORD_PREFIX` regex.
- **Registration** in `adapters/__init__.py` (`register(PowerBiAdapter())`, `__all__` entry) — runs on
  a bare install (stdlib-only, acyclic, AI-free).
- **Unit suite** `tests/test_powerbi_adapter.py` (15 tests, inline `tmp_path` PBIP fixtures).
- **Matrix joins**: `id="powerbi"` appended to both `ADAPTER_CASES` (coverage parity) and
  `_DETERMINISM_CASES` (determinism) — no skip-mark (stdlib-only).

## Adapter API (for Wave 3 / Plan 07-04 golden)

- **Registered name:** `"powerbi"` (`resolve("powerbi").name == "powerbi"`).
- **Signatures:** `parse_path(path)` and `parse(raw, path)` both return `(Source, units, drops)`.
- **Transcript layout:** one line `"<prefix>\t<verbatim value>\n"` per unit; `SEP = "\t"`; files
  walked SORTED, objects in declaration order. The prefix is NOT part of the claim value.
  Example transcript head:
  ```
  Model/Table[Sales].name\tSales
  Model/Table[Sales]/Measure[Total].name\tTotal
  Model/Table[Sales]/Measure[Total].expression\tSUMX(S,1)
  Model/Table[Sales]/Column[Q].name\tQ
  Model/Table[Sales]/Column[Q].dataType\tint64
  ```
  Prefix grammar: `Model/Table[<t>]`, `.../Measure[<m>].{name,expression}`,
  `.../Column[<c>].{name,dataType}`, `Model/Relationship[<id>].{fromColumn,toColumn}`,
  `Report/Page[<dir>].displayName`, `Report/Page[<dir>]/Visual[<dir>].{title,textbox,field,filter}`.
- **Locator:** `FreeLocator(text=prefix)` (the object-path / file string) — no schema change.
- **Unit recovery:** anchored `_RECORD_PREFIX = re.compile(r"[^\n]*?\t")` matched at line starts —
  values containing `\n`/`\t`/`:` stay verbatim and locatable.

### The EXACT `_R_*` reason strings (the contract Plan 04 imports and pins)

| Constant | String |
|----------|--------|
| `_R_TOPN` | `Top-N filter restricts the row set — rows beyond the top N are clipped, not in the export` |
| `_R_FILTER` | `a restricting filter limits the row set — full detail not represented in the export` |
| `_R_AGGREGATED` | `a field is shown aggregated — underlying detail rows are not in the export` |
| `_R_MEASURE_VALUE` | `measure: aggregate formula extracted; the computed value is not present (never fabricated)` |
| `_R_DIRECTQUERY` | `a DirectQuery partition stores no rows in the model — no data rows are extractable` |
| `_R_ROWLIMIT` | `a visual data-reduction/row limit is set — displayed data may be truncated` |
| `_R_NO_DATA_ROWS` | `PBIP/TMDL/PBIR is a definition format — it contains no data rows; measure/column values are not present and are never fabricated` |
| `_R_PBIX_BINARY` | `binary .pbix not extractable by the text adapter — export to PBIP/PBIR (File > Save as Power BI project) for faithful extraction` |
| `_R_UNREADABLE` | `Power BI project file ({path}) could not be read ({error}) — not extractable` (templated) |
| `_R_BINARY_FILE` | `binary/non-text artifact ({path}) not extracted` (templated) |

### How `_pbir.Detection` maps to reasons

`detect_row_caps()` returns typed `Detection(kind, path, params)`; the adapter's `_DETECTION_REASON`
dict maps `kind` -> reason: `topn`→`_R_TOPN`, `filter`→`_R_FILTER`, `aggregated`→`_R_AGGREGATED`,
`measure_value`→`_R_MEASURE_VALUE`, `directquery`→`_R_DIRECTQUERY`, `rowlimit`→`_R_ROWLIMIT`. Unknown
kinds degrade to `_R_FILTER` (never a silent miss). The TMDL `"directQuery"` SIGNAL (from
`parse_tmdl`) also maps to `_R_DIRECTQUERY`. A measure's `.expression` unit additionally emits a
`_R_MEASURE_VALUE` drop. `_R_NO_DATA_ROWS` is emitted exactly ONCE whenever any model is extracted.

## Verification (gates re-run independently — ACTUAL output)

- `pytest tests/test_powerbi_adapter.py -q` → **15 passed**.
- `pytest tests/test_coverage_roundtrip.py tests/test_timestamp_determinism.py -q -k powerbi` →
  **5 passed, 31 deselected**; both matrices full → **36 passed**.
- `pytest -q` (full) → **434 passed, 1 xfailed** (baseline was 414 passed, 1 xfailed; +20 = 15 unit +
  5 matrix params).
- `mypy src/newsletters/adapters src/newsletters/distill` → **Success: no issues found in 20 source
  files**.
- `lint-imports` → **Contracts: 1 kept, 0 broken** (AI-isolation intact; zero new dependency).
- `python -c "import newsletters; import newsletters.adapters; from newsletters.distill import
  resolve; resolve('powerbi')"` → **powerbi** (bare-install registration green).
- `newsletters build` → **rendered 9 surfaces + the library index** (CLI unaffected).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Determinism test body incompatible with PBIP's always-EPOCH_ZERO contract**
- **Found during:** Task 3 (joining the determinism matrix).
- **Issue:** `test_intrinsic_timestamp_is_preserved` hardcoded `assert source.timestamp != EPOCH_ZERO`.
  The plan explicitly directs PBIP's `with_intrinsic` recipe to ALSO expect EPOCH_ZERO (PBIP is the
  one format with no intrinsic-date branch — Q-F). The hardcoded guard would have failed the powerbi
  param.
- **Fix:** Guarded that assertion behind `if expected != EPOCH_ZERO:` so it fires only for formats
  whose recipe expects a real date; for the always-EPOCH_ZERO contract, `expected == EPOCH_ZERO` IS
  the assertion. No behavior change for email/excel/pptx (all expect non-EPOCH_ZERO dates).
- **Files modified:** `tests/test_timestamp_determinism.py`.
- **Commit:** `933d7de`.

This was the only deviation. The adapter, registration, and unit suite were implemented exactly as
the plan specified; all `_R_*` strings match the 07-RESEARCH Q-D taxonomy.

## Authentication gates

None — fully autonomous, no checkpoints, no installs (pbixray DEFERRED; zero new dependency).

## Known Stubs

None. The adapter wires real data end to end; the `_R_*` reasons are concrete strings. No placeholder
values flow to any surface.

## Threat surface scan

No NEW security surface beyond the plan's `<threat_model>`. All mitigations applied: `sorted()` walks
+ EPOCH_ZERO (T-07-12), try/except per file → `_R_UNREADABLE` (T-07-11), `.pbix` ZIP never
decompressed (T-07-10), filter literals surfaced as config text (T-07-13), no network/external-link
following. The model-completeness spoofing mitigation (T-07-08) is the headline behavior:
`_R_NO_DATA_ROWS` + the per-signal taxonomy force `Coverage.complete=False`.

## Self-Check: PASSED

- `src/newsletters/adapters/powerbi_adapter.py` — FOUND
- `tests/test_powerbi_adapter.py` — FOUND
- commit `25b37cb` (test RED) — FOUND
- commit `5215aa0` (feat GREEN) — FOUND
- commit `933d7de` (test matrices) — FOUND
