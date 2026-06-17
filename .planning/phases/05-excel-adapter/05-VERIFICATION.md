---
phase: 05-excel-adapter
verified: 2026-06-17T16:00:38Z
status: passed
score: 3/3 success criteria verified (+ Task Zero hardening confirmed)
overrides_applied: 0
re_verification:
  previous_status: null
  previous_score: null
human_verification: []
---

# Phase 5: Excel Adapter Verification Report

**Phase Goal:** Extract cell/sheet structure from `.xlsx` via openpyxl into `Claim(+Trace)` with `sheet!cell` locators, routing every value openpyxl cannot resolve to `unextracted[]` rather than emitting it as data.
**Verified:** 2026-06-17T16:00:38Z
**Status:** passed
**Re-verification:** No — initial verification
**Branch:** claude/youthful-fermi-dly6mi (not switched; read-only + VERIFICATION write only)

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Excel adapter extracts cell/sheet structure into `Claim(+Trace)` with `sheet!cell` locators | ✓ VERIFIED | `excel_adapter.py:170-202` serializes `Sheet!A1<sep>value` row-major; `:198` `FreeLocator(text=f"{sheet}!{cell.coordinate}")`; units hand to shared `normalize()` (`:311`) which mints content-addressed traces. Live probe: claims `["2"]`, `["5"]` etc. with `is_addressed=True`, `claim.text == transcript[start:end]`. |
| 2 | Uncomputed/`None`-cache formula cells routed to `unextracted[]`, never emitted as `0`/empty (the crux) | ✓ VERIFIED | LIVE probe with openpyxl-saved formula (no cache): A1=5 emitted as `"5"`, A2=`=A1*10` → `unextracted[("S!A2", "formula cell A2 has no cached value (uncomputed: '=A1*10') — not faithfully extractable")]`, `complete=False`, and **no claim with text `"0"`/`""`**. Decision logic `_cell_decision` `:108-138` (formula-ness from FORMULA view, cache from DATA view). Formula WITH cache (XML-injected `<v>`) IS extracted: `formula_with_cache.xlsx` → claims `["2","20"]`, `complete=True`. |
| 3 | Golden test covers fixture with formulas + merged cells, asserting zero silent drops | ✓ VERIFIED | `tests/test_excel_golden.py` (317 lines): 8 committed byte-reproducible fixtures; `test_zero_silent_drops` asserts `#claims + #unextracted == #units walked` for ALL fixtures; per-fixture routing asserts (`test_formula_no_cache_routes_to_unextracted_never_zero`, `test_merged_anchor_emitted_exactly_once`, `test_chart_is_disclosed_not_extracted`, `test_error_cell_routes_to_unextracted`). 98 phase-5 tests pass. |

**Score:** 3/3 success criteria verified.

### Task Zero — Coverage-Persistence Hardening (carried from Phase-4 verifier)

| Check | Status | Evidence |
|-------|--------|----------|
| Typed carrier travels with Source | ✓ VERIFIED | `locators.py:101-121` `ExtractedDrop`/`ExtractionRecord` (AI-free leaf, stdlib+pydantic); `semantic.py:65-69` `Source.extraction: Optional[ExtractionRecord] = None`, excluded from `content_hash()` (`:71-83`, addresses transcript only). |
| In-memory dict keyed by `source.id` is GONE (email) | ✓ VERIFIED | `grep` for `self._drops`/`[source.id]`/`defaultdict` in `email_adapter.py` → **0 matches**. Comment `:132-136` documents removal. Drops set on `Source.extraction` via `encode_coverage` at `parse()` (`:201`), recovered via `decode_coverage(source.extraction)` at `_units_for()` (`:380`). |
| Round-trip parity — Email | ✓ VERIFIED | LIVE: parsed `forwarded_rfc822.eml`, `html_only.eml`, `malformed_boundary.eml` → `model_dump_json` → reload → FRESH `EmailAdapter().distill()` → coverage signature EQUAL. `tests/test_coverage_roundtrip.py` parametrized matrix covers both adapters. |
| Round-trip parity — Excel | ✓ VERIFIED | `test_roundtrip_coverage_parity` (golden) over all 8 fixtures; LIVE confirmed adapter B (never parsed) reproduces coverage from a reloaded Source. |
| R2 safety-net (no false `complete=True`) | ✓ VERIFIED | LIVE: hand-made `Source(extraction=None)` → both `ExcelAdapter.distill` and `EmailAdapter.distill` return `complete=False` with `unextracted` reason `coverage-not-reconstructable`. Code: `excel_adapter.py:307-308`, `email_adapter.py:331-332`, marker `_coverage_codec.py:68-77`. |

### Lazy openpyxl / AI-optional boundary

| Check | Status | Evidence |
|-------|--------|----------|
| No top-level openpyxl reachable from `import newsletters` | ✓ VERIFIED | `grep "^.*import openpyxl"` across `src/newsletters` → only `_openpyxl_loader.py:56` (INSIDE `_load_openpyxl()`, with `# noqa: PLC0415`). `adapters/__init__.py` registers `ExcelAdapter` without pulling openpyxl. |
| Bare import works without `[excel]` | ✓ VERIFIED | `test_adapters_package_imports_without_openpyxl` installs a `sys.meta_path` finder blocking openpyxl in a subprocess, then `import newsletters` + `import newsletters.adapters` + loader module — passes; asserts `openpyxl not in sys.modules`. |
| Teaching ImportError when absent | ✓ VERIFIED | `_openpyxl_loader.py:52-58` re-raises with `MISSING_OPENPYXL_MESSAGE` (names `pip install '.[excel]'`); `test_loader_raises_teaching_error_without_openpyxl` passes. |
| `[excel]` extra = openpyxl only | ✓ VERIFIED | `pyproject.toml` `excel = ["openpyxl"]`; `test_excel_extra_declared` asserts `excel_names == {"openpyxl"}` and not AI. |
| `.importlinter` unchanged | ✓ VERIFIED | `git log` over phase-5 commits touching `.importlinter`/`pyproject.toml` → no commit modified `.importlinter`; openpyxl correctly NOT in forbidden list (it is not AI). |

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `src/newsletters/locators.py` | ✓ VERIFIED | `ExtractedDrop` + `ExtractionRecord` leaf types (AI-free). |
| `src/newsletters/semantic.py` | ✓ VERIFIED | `Source.extraction` typed carrier, excluded from `content_hash()`. |
| `src/newsletters/adapters/_coverage_codec.py` | ✓ VERIFIED | `encode_coverage`/`decode_coverage` total bridge + R2 marker. |
| `src/newsletters/adapters/_openpyxl_loader.py` | ✓ VERIFIED | Lazy `_load_openpyxl()` + `load_workbook_pair` double-load (`data_only` ±, `read_only=False`, `keep_links=False`). |
| `src/newsletters/adapters/excel_adapter.py` | ✓ VERIFIED | 393 lines; `ExcelAdapter` per-cell fork, value_to_str (R3 rule), transcript serialize/round-trip inverse, drops → `Source.extraction`. |
| `src/newsletters/adapters/email_adapter.py` | ✓ VERIFIED | Retrofit: stateless, drops on carrier, R2 net, dict gone. |
| `src/newsletters/adapters/__init__.py` | ✓ VERIFIED | `register(ExcelAdapter())` as `"excel"`. |
| `tests/fixtures/xlsx/*` | ✓ VERIFIED | `_author_fixtures.py` + 8 committed byte-reproducible `.xlsx` (`_finalize` pins `created`/`modified` + normalizes ZIP times). |
| `tests/test_excel_adapter.py`, `test_excel_golden.py`, `test_coverage_roundtrip.py`, `test_openpyxl_probe.py` | ✓ VERIFIED | Present, substantive, all passing. |

### Behavioral Spot-Checks (run live, this verifier's own process)

| Behavior | Result | Status |
|----------|--------|--------|
| openpyxl-saved formula (no cache) → unextracted, no `0`/empty claim | claims `["5"]`; A2 disclosed at `S!A2`; complete=False | ✓ PASS |
| formula WITH cache → extracted | `formula_with_cache.xlsx` → `["2","20"]`, complete=True | ✓ PASS |
| R2 safety-net both adapters (extraction=None) | both `complete=False`, `coverage-not-reconstructable` | ✓ PASS |
| Email round-trip parity (3 fixtures) | coverage equal on fresh adapter | ✓ PASS |
| Whitespace-only string cell faithfulness | `"   "` emitted verbatim; `transcript[start:end]==text`; addressed | ✓ PASS |

### Gate Output (re-run independently)

| Gate | Command | Result |
|------|---------|--------|
| Full test suite | `.venv/bin/python -m pytest -q` | **280 passed, 1 xfailed** in 6.33s |
| Phase-5 modules | `pytest tests/test_excel_*.py tests/test_coverage_roundtrip.py tests/test_openpyxl_probe.py` | **98 passed** |
| Type check | `mypy src/newsletters/adapters src/newsletters/distill` | **Success: no issues found in 14 source files** |
| Import contract | `.venv/bin/lint-imports` | **1 kept, 0 broken** (Core must not import AI) |
| Build | `.venv/bin/newsletters build` | rendered 9 surfaces + library index, no errors |

openpyxl 3.1.5 is installed in the dev `.venv`, so the `[excel]`-gated tests ACTUALLY RAN (not skipped) — confirmed.

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| ADAPT-03 | Excel adapter extracts cell/sheet via openpyxl, uncomputed/None formulas → `unextracted[]` | ✓ SATISFIED | Criteria 1+2 verified; live crux probe. |
| ADAPT-06 | Each adapter covered by golden-file tests (fixture → expected typed claims+traces) | ✓ SATISFIED | `test_excel_golden.py` 8-fixture corpus, zero-silent-drops identity. |

### Skeptical-Edge Findings (probed live)

**(a) Determinism when a workbook has NO intrinsic `created` timestamp — REAL EDGE, narrow scope.**
The adapter sources `Source.timestamp` from `wb.properties.created` (`excel_adapter.py:260,268-275`). If `created` reads back as `None`, the code falls through to the `else` branch (no `timestamp=` kwarg) → `Source`'s `default_factory=_utcnow()` fires. LIVE proof (forcing `created=None` after load): two parses of the same bytes produced **different** timestamps (`...38.014736` vs `...38.029450`) and `distill()` results were **not equal** — determinism AND round-trip parity break. Mitigating facts: (1) `openpyxl.Workbook()` always sets `created` and openpyxl REFUSES to save a workbook with `created=None` (raises `AttributeError`), so an openpyxl-authored file always carries it; (2) the committed corpus pins `created=2026-01-01` via `_finalize`, so the determinism/parity tests pass and the edge is never exercised by the suite. The residual risk is a third-party-authored `.xlsx` (Excel/LibreOffice/xlsxwriter) whose `docProps/core.xml` lacks a `created` value — for such a file determinism is not guaranteed. The success criteria do not require determinism for arbitrary externally-authored workbooks, so this is a **robustness edge, not a goal failure** — but it is worth a follow-up (deterministic fallback, e.g. a fixed epoch when `created` is None, rather than wall-clock). Surfaced as a risk below.

**(b) Float faithfulness (`0.1+0.2`) — NOT a concern; faithful to the source as read.**
The objective hypothesizes `0.1+0.2 → "0.3"`. LIVE: the adapter emits `"0.3"`, BUT not because of any rounding in the adapter — openpyxl reads `0.3` back from the xlsx (xlsx stores ~15 sig digits; openpyxl reconstructs the float `0.3`, whose `repr()` is `"0.3"`). The adapter never sees `0.30000000000000004` (that value existed only in the authoring process before serialization). `value_to_str` uses `repr(float)` — the shortest round-tripping decimal — so the emitted string equals exactly what openpyxl read from the bytes, losslessly. For a value openpyxl returns with full precision (e.g. `1/3 → 0.3333333333333333`) the adapter emits all the digits verbatim. **Judgment: correctly faithful to the source as read; no fixed-precision reformatting; deterministic.**

**(c) "Zero silent drops" airtightness for edge structures — held under every probe tried.**
- Sheet with ONLY a chart (no cells): the empty sheet contributes no cell units; the chart is disclosed once via `_feature_drops` → `unextracted`. No phantom cells; identity holds.
- Fully-merged region (`A1:C3`, anchor `"only"`): anchor emitted once, the 8 covered cells are `None`→skipped, `complete=True`. No phantom blanks, nothing lost.
- Whitespace-only string cell (`"   "`): emitted as a verbatim claim (`transcript[start:end] == "   "`, addressed). Defensible — it IS content in the source; faithful preservation, not a drop. (A judgment call: whitespace-only is treated as data, not blank; `_cell_decision` skips only `value is None`.)
- Image branch caveat (minor): openpyxl LOSES images from existing files on reload (documented in `test_openpyxl_probe.py:84-101`), so a reloaded `_images` is empty. The `chart_or_image.xlsx` fixture embeds only a CHART (no real image — Pillow not a dep, honestly disclosed in `_author_fixtures.py:227`). The IMAGE branch of `_feature_drops` (`:160-166`) is therefore symmetric-with-charts code that is NOT exercised against a real round-tripped image. This is a **test-coverage caveat**, not a goal gap — the per-cell accounting and chart disclosure both hold, and the success criteria name formulas+merged cells (both covered). Noted as a minor risk.

**No silent-drop gap was found.** The accounting identity is asserted per-fixture as a test failure-by-construction, and every live edge probe stayed on exactly one side of the ledger.

### Hard-Rule Status

| Hard rule | Status | Evidence |
|-----------|--------|----------|
| AI-optional core (openpyxl behind `[excel]`, lazy) | ✓ HELD | Only lazy import (`_openpyxl_loader.py:56`); bare-install subprocess test passes; lint-imports green. |
| Faithful, not suggestive (uncomputed → unextracted, never fabricated 0/empty) | ✓ HELD | Live crux probe; `value_to_str` lossless; error cells + None-cache disclosed. |
| No silent drops across persistence | ✓ HELD | Carrier on `Source.extraction` + R2 net; parity matrix both adapters. |
| No auto-publish untouched | ✓ HELD | Adapter never calls `Surface.publish`/`PUBLISHED` (only docstring references the rule); returns truth only. |
| Only ONE new dependency (openpyxl) | ✓ HELD | `pyproject` `excel = ["openpyxl"]` (test asserts == {openpyxl}); `.importlinter` unchanged. |
| Minimal core / typed-everything | ✓ HELD | Carrier is Pydantic-native typed (R1 honored — no JSON-in-context). |

### Anti-Patterns Found

None. `grep` for `TBD|FIXME|XXX|HACK|PLACEHOLDER|not yet implemented|coming soon` across all phase-5 source files → 0 matches.

### Gaps Summary

No blocking gaps. All 3 ROADMAP success criteria and both requirements (ADAPT-03, ADAPT-06) are achieved in live code, the Task-Zero hardening is genuinely fixed (in-memory dict removed; parity proven for both adapters; R2 net live), and all four gates pass with openpyxl actually present so the `[excel]` tests ran rather than skipped.

**Non-blocking risks to track (do NOT block phase completion):**
1. **Determinism with absent `created` (edge a):** an externally-authored `.xlsx` lacking `docProps/core.xml` `created` falls back to wall-clock `now()`, breaking determinism/round-trip parity for that file. Consider a deterministic fallback (fixed epoch / hash-derived) when `created is None`. Not exercised by openpyxl-authored fixtures.
2. **Image disclosure path untested against a real image (edge c):** openpyxl drops images on reload and no Pillow dep means the corpus exercises only the chart branch; the symmetric image branch is unverified end-to-end. Low risk (code is symmetric with the verified chart path).

---

_Verified: 2026-06-17T16:00:38Z_
_Verifier: Claude (gsd-verifier)_
