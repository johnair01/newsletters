---
phase: 07-power-bi-adapter
verified: 2026-06-18T11:05:00Z
status: passed
score: 3/3 must-haves verified (criterion-3 gap RESOLVED 2026-06-18 — see RESOLUTION below)
overrides_applied: 0
resolution: >
  The criterion-3 silent-drop gap was FIXED in commit 94f34b1: `_tmdl.py` now recognizes the `model`
  object type (its properties attach as `Model.*`) and extracts `ref table` references, and ANY
  orphan/unrecognized line is DISCLOSED as an `unparsed:` signal → `_R_TMDL_UNPARSED` (never a silent
  drop). The golden gained `test_no_line_is_read_but_undisclosed` which anchors accounting to LINES
  READ (asserts zero `unparsed:` over the corpus + positively re-checks the previously-leaked model
  metadata), and EXPECTED_N_UNITS 21→26 (the 5 recovered model units). Full suite 448 passed, mypy
  clean, lint-imports 1 kept/0 broken. The orchestrator independently re-ran all gates. RETRO logged.
re_verification:
gaps:
  - truth: "A golden-file test covers the adapter against a fixture, asserting zero silent drops (ADAPT-06)."
    status: partial
    reason: >
      The golden's zero-silent-drops identity is len(claims)+len(normalize-misses)==len(units),
      which only accounts for units the adapter CHOOSES to emit. A file the adapter reads but emits
      neither a unit nor an unextracted[] entry for is invisible to this identity. The committed
      corpus contains exactly such a file: sample.SemanticModel/definition/model.tmdl. Its
      'model Model' header type is NOT in _tmdl._OBJECT_TYPES, so the header is skipped as an
      "unknown line" (_tmdl.py:234) and its child properties (culture: en-US,
      defaultPowerBIDataSourceVersion: powerBI_V3) have no owner frame and are dropped silently
      at _tmdl.py:177 (owner_prefix is None -> no unit, no signal, no drop). parse_tmdl(model.tmdl)
      returns ([], []). The content is read, is meaningful model metadata, and disappears with no
      disclosure — a "silent drop" under the CLAUDE.md hard rule ("No silent drops"), even though
      the golden passes because the dropped lines never become units.
    artifacts:
      - path: "src/newsletters/adapters/_tmdl.py:47-62,234,169-179"
        issue: >
          'model' missing from _OBJECT_TYPES; top-level model header skipped; its child properties
          dropped silently when the stack is empty (no _R_* disclosure).
      - path: "tests/test_powerbi_golden.py:128-149"
        issue: >
          test_zero_silent_drops measures claims+misses==units, not files-read==content-accounted;
          it cannot catch a line that was read but never emitted as a unit. The committed
          model.tmdl proves the gap is live in the corpus, not hypothetical.
    missing:
      - "Add 'model' to _tmdl._OBJECT_TYPES so the model header's child properties (culture, defaultPowerBIDataSourceVersion) extract as verbatim units — OR emit an explicit unextracted[] disclosure for read-but-unparsed lines."
      - "Strengthen the golden so the zero-silent-drops identity is anchored to files/lines READ, not only to units emitted (e.g. assert model.tmdl's culture is a claim, or that any non-comment/non-ref line is accounted for)."
deferred:
human_verification:
---

# Phase 7: Power BI Adapter — Verification Report

**Phase Goal:** Extract from Power BI PBIP/TMDL text (stdlib) into `Claim(+Trace)`, reporting the row-cap and aggregation limits that make an export look complete when it is a clipped aggregate (pbixray DEFERRED per locked decision L1 — binary `.pbix` → fail-loud deferral).
**Verified:** 2026-06-18T11:05:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification.

## Goal Achievement

### Observable Truths (the three ROADMAP success criteria, stdlib-only path)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The Power BI adapter extracts from PBIP/TMDL text (stdlib) into Claim(+Trace) with object locators. | ✓ VERIFIED | Live temp-folder test (NOT in suite): a PBIP tree with a measure `DIVIDE(SUM(Orders[Amt]), 12)` + columns + page + visual yielded 7 verbatim claims; for every claim `claim.text == trace.span == transcript[start:end]` AND `trace.is_addressed`; DAX extracted as TEXT (never a value); drop locators carry object paths (`Model/Table[Orders]/Measure[Net Revenue].expression`). `_tmdl.py`, `powerbi_adapter.py:346-415`. |
| 2 | Row-cap + summarized-vs-underlying aggregation limits reported in unextracted[], failing loud (no clipped aggregate read as complete). | ✓ VERIFIED | Live tests confirm TopN→`_R_TOPN`, restricting filter→`_R_FILTER`, aggregation→`_R_AGGREGATED`, measure→`_R_MEASURE_VALUE`, DirectQuery→`_R_DIRECTQUERY`, maxRows→`_R_ROWLIMIT`, and `_R_NO_DATA_ROWS` once per model → `complete is False`. `.pbix`/ZIP byte input defers to `_R_PBIX_BINARY` with the ZIP NEVER decompressed (sniffed by magic + suffix), `complete is False`. `powerbi_adapter.py:85-119,371-415`, `_pbir.py:221-262`. |
| 3 | A golden-file test covers the adapter against a fixture, asserting zero silent drops (ADAPT-06). | ✗ PARTIAL | `tests/test_powerbi_golden.py` (13 tests) drives the LIVE adapter over a committed byte-reproducible corpus and asserts verbatim+addressed claims, the exact `_R_*` taxonomy in emission order, conformance, JSON round-trip, determinism, EPOCH_ZERO, round-trip coverage parity — all PASS. BUT the zero-silent-drops identity (`claims+misses==units`) does not account for content READ-but-never-emitted: the committed `model.tmdl` (`culture`, `defaultPowerBIDataSourceVersion`, the `model` object) is silently dropped and the golden passes anyway. See Gaps. |

**Score:** 2/3 truths verified (criterion 3 PARTIAL).

### Recovery-Integrity Assessment — `_pbir.py` (written inline after the agent stall)

**VERDICT: SOUND and complete — not narrowly test-fitted.** The recovered module handles the full L3 taxonomy robustly and key-leniently. Evidence from a LIVE object NOT in the test suite:

- A single visual carrying a **TopN filter AND an Aggregation AND a maxRows AND a Measure projection AND a generic filter** fired ALL detections together: `['aggregated','filter','measure_value','rowlimit','topn']` (`_pbir.py:221-262`).
- An **unknown/garbage filter shape** (`{"weird":[...],"nope":{...}}`) degraded to a generic `filter` detection — no crash, no silent miss (`_pbir.py:242-245`, research A1 mitigation realized).
- **Malformed inputs degrade safely:** `extract_report("not a dict", ...) == []`, `detect_row_caps(None, ...) == []`, a non-list `filters` value → `[]`. Every helper guards with `isinstance(...)` before traversal (`_pbir.py:64-178`).
- The aggregate-function enum maps `Function 0 → "Sum"` (`_AGG_FN`, `_pbir.py:28-38`); filter literals (e.g. `'Contoso'`) are surfaced verbatim as config text AND recorded in the detection params — disclosed, never silently treated as data (`_pbir.py:157-169,243-245`).

The recovery has **no functional gaps** in the detection/extraction contract. (The one silent-drop class found in this phase lives in `_tmdl.py`, not `_pbir.py`.)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/adapters/_tmdl.py` | stdlib TMDL parser | ✓ VERIFIED (with gap) | 348 lines, pure, `re`-only; fenced/multi-line/single-line DAX as verbatim text; DirectQuery signal. Gap: `model` header type missing → top-level props silently dropped. |
| `src/newsletters/adapters/_pbir.py` | stdlib PBIR reader | ✓ VERIFIED | 263 lines, recovered; full L3 taxonomy + key-lenient degradation proven on live objects. |
| `src/newsletters/adapters/powerbi_adapter.py` | registered "powerbi" backend | ✓ VERIFIED | 544 lines; `parse_path`/`parse`/`distill`; one serializer; the 10-entry `_R_*` taxonomy; EPOCH_ZERO; try/except per file → `_R_UNREADABLE`; ZIP never decompressed. |
| `tests/test_tmdl_parser.py` | TMDL unit suite | ✓ VERIFIED | runs (part of 59 phase-7 tests passing). |
| `tests/test_pbir_reader.py` | PBIR unit suite | ✓ VERIFIED | 15 tests; covers the full taxonomy + key-leniency + disclosure caveat. |
| `tests/test_powerbi_adapter.py` | adapter unit suite | ✓ VERIFIED | 15 tests. |
| `tests/test_powerbi_golden.py` | ADAPT-06 golden, no skip-mark | ✓ VERIFIED (with gap) | 13 tests, NO skip-mark (stdlib runs bare). Identity gap noted in criterion 3. |
| `tests/fixtures/powerbi/*` | hand-authored PBIP tree + fake.pbix | ✓ VERIFIED | 13 committed files via stdlib `write_text`; Top-N/Sum/maxRows visual present; 43-byte `fake.pbix`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `adapters/__init__.py` | `PowerBiAdapter` | `register(PowerBiAdapter())` | ✓ WIRED | `__init__.py:19,32,39`; `resolve("powerbi").name == "powerbi"` on bare install. |
| `powerbi_adapter` | `_tmdl.parse_tmdl` | import + `_serialize_tmdl_text` | ✓ WIRED | `:72,182`. |
| `powerbi_adapter` | `_pbir.{extract_report,detect_row_caps}` | import + `_serialize_report_json` | ✓ WIRED | `:70,199-200`. |
| `Detection.kind` | `_R_*` reason | `_DETECTION_REASON` (unknown→`_R_FILTER`) | ✓ WIRED | `:107-114,161-165`. |
| `parse` | matrices | coverage-parity + determinism params | ✓ WIRED | `test_coverage_roundtrip.py:183`, `test_timestamp_determinism.py:299-302`, both no skip-mark. |
| drops | `Source.extraction` | `encode_coverage` / `decode_coverage` | ✓ WIRED | `:433,500`; round-trip parity test passes on a fresh adapter. |

### Behavioral Spot-Checks (run independently, live)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Combined detections fire together | live obj: TopN+Agg+maxRows+Measure+filter | all 5 kinds present | ✓ PASS |
| Garbage filter degrades | live obj: unknown filter keys | `['filter']`, no crash | ✓ PASS |
| Criterion 1 live folder | temp PBIP tree, distill | 7 verbatim+addressed claims, DAX as text | ✓ PASS |
| DirectQuery fail-loud | dropped `.tmdl` with `mode: directQuery` | `_R_DIRECTQUERY`, complete False | ✓ PASS |
| `.pbix` deferral | ZIP-magic bytes | `[_R_PBIX_BINARY]`, empty transcript, complete False | ✓ PASS |
| ZIP sniff w/o `.pbix` suffix | `PK\x05\x06...` as `.txt` | `[_R_PBIX_BINARY]` | ✓ PASS |
| **Silent-drop hunt** | committed `model.tmdl` walked | `culture`/`defaultPowerBIDataSourceVersion` absent from transcript & drops | ✗ FAIL (silent drop) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ADAPT-05 | 07-01/02/03 | PBIP/TMDL→Claim(+Trace); row-cap/aggregation fail-loud | ✓ SATISFIED | Criteria 1+2 verified live. |
| ADAPT-06 | 07-04 | Golden proving zero silent drops, verbatim, conformance, determinism, round-trip | ⚠ PARTIAL | All assertions pass, but the zero-silent-drops identity has a blind spot (criterion 3 gap). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `_tmdl.py` | 177 | `owner_prefix is None` → silent skip of top-level property | ⚠ Warning | Read-but-undisclosed model metadata (the criterion-3 gap). |
| `_tmdl.py` | 47-62 | `model` absent from `_OBJECT_TYPES` | ⚠ Warning | Root cause of the silent drop. |
| (none) | — | No TBD/FIXME/XXX/placeholder markers in any phase-7 file | ℹ Info | Clean — debt-marker gate passes. |

### Hard-Rule Status

| Rule | Status | Evidence |
|------|--------|----------|
| Faithful, not suggestive (DAX/data never evaluated) | ✓ HOLDS | DAX emitted verbatim as `.expression` text; no eval path; live test confirms `DIVIDE(...)`/`SUMX(...)` are claim text, never numbers. |
| AI-optional + ZERO new dependency | ✓ HOLDS | `pyproject.toml` diff across the whole phase is EMPTY; no `[powerbi]`/`pbix`/`pbixray` entry; `.importlinter`/`setup.cfg`/`pyproject` last touched in Phase 6; `lint-imports` → 1 kept, 0 broken. |
| No-auto-publish | ✓ UNTOUCHED | `distill` returns truth only; no `Surface.publish`/`PUBLISHED` path. |
| No silent drops (incl. round-trip) | ✗ VIOLATED (one class) | `model.tmdl` top-level props read but dropped with no `unextracted[]`. Round-trip parity itself holds (carrier on `Source.extraction`). |
| Every claim traces to evidence | ✓ HOLDS | every claim `is_traced` + `is_addressed`; span reslice exact. |
| Determinism | ✓ HOLDS | EPOCH_ZERO always; sorted walks; two parses byte-identical Sources. |

### Gate Output (re-run independently, ACTUAL)

- `pytest -q` (full) → **447 passed, 1 xfailed** in 9.58s.
- phase-7 suites (tmdl+pbir+adapter+golden) → **59 passed**.
- `mypy src/newsletters/adapters src/newsletters/distill` → **Success: no issues found in 20 source files**.
- `lint-imports` → **Contracts: 1 kept, 0 broken**.
- registration → `resolve("powerbi").name` → **powerbi** (bare install).
- `newsletters build` → **rendered 9 surfaces + the library index** (CLI unaffected).

### Determinism-guard auto-fix (07-03) — assessed, legitimate

`test_timestamp_determinism.py:342` still asserts `source.timestamp == expected` for ALL formats (the strong assertion); `:345-346` adds the extra `!= EPOCH_ZERO` guard ONLY when `expected != EPOCH_ZERO`, so email/excel/pptx are unchanged. PBIP's `expected == EPOCH_ZERO` IS its contract. No over-weakening.

### Gaps Summary

The adapter achieves criteria 1 and 2 cleanly and the `_pbir.py` recovery is sound. The one real gap is in criterion 3 / the no-silent-drops hard rule: the committed `model.tmdl` is walked, but its `model` header type is unknown to the TMDL parser, so the header and its child properties (`culture`, `defaultPowerBIDataSourceVersion`) vanish with no claim and no `unextracted[]` disclosure. The golden's accounting identity (`claims + misses == units`) cannot see this because the lines never become units. This is the exact failure mode the phase set out to prevent — content read but undisclosed — surviving inside the very corpus meant to prove it cannot happen. It is the difference between "every emitted unit is accounted for" (what the golden proves) and "every line read is accounted for" (what the hard rule demands). Severity: WARNING / fix-before-milestone, not a goal-breaking BLOCKER — the headline fail-loud behavior (row caps, aggregation, no-data-rows, .pbix) is intact and `complete=False` is forced correctly; the leak is metadata, not a clipped aggregate masquerading as complete. Two-line fix: add `model` to `_OBJECT_TYPES` (the parser then extracts `culture`/`defaultPowerBIDataSourceVersion` as units, proven by simulation) and add a golden assertion anchoring the identity to lines read.

---

_Verified: 2026-06-18T11:05:00Z_
_Verifier: Claude (gsd-verifier)_
