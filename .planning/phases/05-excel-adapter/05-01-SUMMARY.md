---
phase: 05-excel-adapter
plan: 01
subsystem: api
tags: [pydantic, adapters, coverage, persistence, tdd, faithfulness]

# Dependency graph
requires:
  - phase: 04-shared-adapter-normalizer-email
    provides: "EmailAdapter, shared normalize(), Coverage/Unextracted honesty contract, DistillPort/assert_conforms"
provides:
  - "Typed coverage carrier: ExtractedDrop + ExtractionRecord (leaf, AI-free) carried on Source.extraction (R1)"
  - "Shared codec adapters/_coverage_codec.py: encode_coverage / decode_coverage (Unextracted <-> ExtractionRecord) + not_reconstructable_marker"
  - "Email adapter retrofit: in-memory source.id-keyed drop dict deleted; coverage now a pure function of the Source"
  - "R2 safety-net: an unaccountable Source forces complete=False via a 'coverage-not-reconstructable' marker"
  - "Round-trip coverage-parity conformance test (tests/test_coverage_roundtrip.py), parametrized over registered adapters"
affects: [05-03-excel-adapter, 06, 07, adapters]

# Tech tracking
tech-stack:
  added: []  # no new dependency — stdlib + Pydantic only
  patterns:
    - "TYPED coverage carrier on Source (R1) — coverage travels with the Source, never adapter instance memory"
    - "Shared adapters-tier codec as the ONE Unextracted<->carrier bridge (keeps semantic/locators free of distill imports)"
    - "R2 belt-and-suspenders safety-net: honest uncertainty (complete=False) over silent completeness"
    - "Parametrized round-trip coverage-parity conformance matrix (adapters join by appending one pytest.param)"

key-files:
  created:
    - src/newsletters/adapters/_coverage_codec.py
    - tests/test_coverage_roundtrip.py
  modified:
    - src/newsletters/locators.py
    - src/newsletters/semantic.py
    - src/newsletters/adapters/email_adapter.py

key-decisions:
  - "R1: TYPED carrier (Source.extraction: Optional[ExtractionRecord]=None), NOT JSON-in-context — overrules the research recommendation on the typed-everything/auditable convention"
  - "Carrier types live in the LEAF locators.py (not distill.coverage) so semantic.py imports them without a semantic->distill cycle"
  - "extraction is EXCLUDED from Source.content_hash() — it is metadata about extraction, not the addressed content; preserves every existing Trace's address"
  - "R2 marker reason is a shared constant (COVERAGE_NOT_RECONSTRUCTABLE) so the parity test can assert its ABSENCE for reconstructable fixtures"

patterns-established:
  - "Adapter coverage persistence: parse() sets source.extraction = encode_coverage(drops); distill() recovers via decode_coverage(source.extraction)"
  - "Adapters are stateless across parse()/distill() — no per-instance source.id-keyed state"

requirements-completed: [ADAPT-03]

# Metrics
duration: ~25min
completed: 2026-06-17
---

# Phase 5 Plan 01: TASK ZERO — Adapter Coverage-Persistence Hardening Summary

**A typed `Source.extraction` carrier + shared codec make adapter `unextracted[]` coverage a pure function of the (round-trippable) Source, retrofitting the Email adapter off its in-memory dict and pinning round-trip coverage parity + an R2 "never-false-complete" safety-net with a conformance test.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-17T~14:58Z
- **Completed:** 2026-06-17T15:24Z
- **Tasks:** 2 (TDD)
- **Files modified:** 5 (2 created, 3 modified)

## Accomplishments
- **R1 typed carrier** — `ExtractedDrop` + `ExtractionRecord` (AI-free, field-identical to `Unextracted`) added to the LEAF `locators.py`, and `Source.extraction: Optional[ExtractionRecord] = None` on `Source`. Backward-compatible (legacy Source JSON with no `extraction` key still validates) and excluded from `content_hash()` (no Trace re-keying / staleness).
- **Shared codec** — `adapters/_coverage_codec.py` bridges `Unextracted <-> ExtractionRecord` losslessly, order-preserving, and totally (`decode_coverage(None) -> []`, never raises). One encode/decode site for both the Email retrofit and the future Excel adapter.
- **Email retrofit** — deleted the `_adapter_unextracted` instance dict (the Phase-4 flaw); `parse()` now writes drops to `source.extraction`, `distill()`/`_units_for()` recover them from the (possibly round-tripped) Source on a FRESH adapter.
- **R2 safety-net** — a Source with no carrier that this adapter did not produce gets a `coverage-not-reconstructable` marker, forcing `Coverage.complete=False`. Never a silent `complete=True`.
- **The headline proof** — `tests/test_coverage_roundtrip.py` pins round-trip coverage parity (`model_dump_json -> reload -> fresh-adapter distill()` == original coverage) for every `.eml` fixture, parametrized so the Excel adapter joins the same matrix.

## Task Commits

Each task was committed atomically (TDD: RED in the test file, then GREEN impl):

1. **Task 1: TYPED carrier (R1) — leaf ExtractionRecord + Source.extraction + shared codec** — `35d438a` (feat)
2. **Task 2: Retrofit Email adapter to the carrier + R2 safety-net** — `1bba430` (feat)

_(`3d2424b` between them is concurrent plan 05-02, not part of this plan.)_

## Files Created/Modified
- `src/newsletters/locators.py` — Added leaf `ExtractedDrop` ({locator, reason}) and `ExtractionRecord` ({unextracted: list[ExtractedDrop]}). AI-free; lives in the leaf so `semantic` can import without a `distill` cycle.
- `src/newsletters/semantic.py` — Added `Source.extraction: Optional[ExtractionRecord] = None`; documented its exclusion from `content_hash()`.
- `src/newsletters/adapters/_coverage_codec.py` — `encode_coverage`, `decode_coverage`, `not_reconstructable_marker`, and the `COVERAGE_NOT_RECONSTRUCTABLE` constant.
- `src/newsletters/adapters/email_adapter.py` — Deleted the in-memory dict; `parse()` sets `source.extraction`; `distill()` adds the R2 marker for unaccountable Sources; `_units_for()` decodes drops from the carrier.
- `tests/test_coverage_roundtrip.py` — Carrier+codec unit tests, round-trip parity matrix, and R2 safety-net test.

## Carrier + Codec API (for Wave 2 / Excel adapter, Plan 03)

**Carrier shapes (in `newsletters/locators.py`, the leaf):**
```python
class ExtractedDrop(BaseModel):       # field-identical to distill.coverage.Unextracted
    locator: Locator                  # FreeLocator | SessionLocator (discriminated union)
    reason: str = ""

class ExtractionRecord(BaseModel):
    unextracted: list[ExtractedDrop] = Field(default_factory=list)
```

**Carrier field (in `newsletters/semantic.py`):**
```python
class Source(BaseModel):
    ...
    extraction: Optional[ExtractionRecord] = Field(default=None, ...)  # NOT in content_hash()
```

**Codec API (in `newsletters/adapters/_coverage_codec.py`):**
```python
encode_coverage(drops: list[Unextracted]) -> ExtractionRecord      # parse()-time, order-preserving, verbatim
decode_coverage(record: Optional[ExtractionRecord]) -> list[Unextracted]  # distill()-time, total (None -> [])
not_reconstructable_marker(source_id: str) -> Unextracted          # R2 marker; reason == COVERAGE_NOT_RECONSTRUCTABLE
COVERAGE_NOT_RECONSTRUCTABLE: str = "coverage-not-reconstructable"  # shared constant
```

**How an adapter wires it (the pattern Plan 03 copies):**
- In `parse()`: compute `unextracted: list[Unextracted]` as today, then construct the `Source` with `extraction=encode_coverage(unextracted)`.
- In `distill()`: for each source, if `source.extraction is None` (and the adapter cannot otherwise account for it), append `not_reconstructable_marker(source.id)` to the merged drops (R2). Recover the carried drops via `decode_coverage(source.extraction)` instead of any instance state.

**Parity-test helper:** `tests/test_coverage_roundtrip.py` defines `ADAPTER_CASES` (a list of `pytest.param(factory, fixtures_loader, id=...)`) and a `_coverage_signature(coverage) -> (complete, [(locator.display, reason), ...])` comparator. The Excel adapter joins by appending one `pytest.param(ExcelAdapter, _xlsx_fixtures, id="excel")` — no test-body change. Three parametrized tests cover: round-trip parity, the R2-marker-absent-for-real-fixtures invariant, and the R2 safety-net on an unaccountable Source.

## Retrofit diff summary (`email_adapter.py`)
- **Removed:** `__init__` body's `self._adapter_unextracted: dict[str, list[Unextracted]]` and its population (`self._adapter_unextracted[source.id] = unextracted`).
- **Added (parse):** `extraction=encode_coverage(unextracted)` on the `Source(...)` constructor.
- **Added (distill):** an R2 guard at the top of the per-source loop — `if source.extraction is None: merged_unextracted.append(not_reconstructable_marker(source.id))`.
- **Changed (_units_for):** `adapter_unx = decode_coverage(source.extraction)` replaces `self._adapter_unextracted.get(source.id, [])`.
- Net: the adapter is now stateless across `parse()`/`distill()`; behavior on the same-instance path is preserved (golden corpus unchanged).

## Decisions Made
- Followed the plan and R1/R2 exactly. The only judgment call: the R2 reason is a shared module constant (`COVERAGE_NOT_RECONSTRUCTABLE`) so the parity test can assert it is ABSENT for reconstructable fixtures and PRESENT for the unaccountable case — keeps the contract DRY across adapter and test.

## Deviations from Plan

None — plan executed exactly as written. No deviation rules (1-4) fired; no architectural change; no auth gate; no package install.

## Issues Encountered
- **Out-of-scope (concurrent plan 05-02):** `mypy src/newsletters/adapters ...` reports one error in `src/newsletters/adapters/_openpyxl_loader.py:26` (missing openpyxl stubs). That file is owned and committed by plan 05-02 (`3d2424b`), NOT this plan — it is outside my exclusive file set and within 05-02's scope to resolve. mypy on this plan's four files (`_coverage_codec.py`, `email_adapter.py`, `semantic.py`, `locators.py`) is **clean**. Not fixed here per the parallel-safety boundary; flagged for 05-02.

## Gate Results (re-run independently via `.venv/bin/python` — actual output)
- `pytest tests/test_coverage_roundtrip.py -q` → **14 passed** (12 carrier/codec unit + parity + R2).
- `pytest tests/test_email_adapter.py tests/test_email_golden.py -q` → **78 passed** (email regression green; same-instance behavior preserved).
- `pytest tests/test_provenance.py tests/test_semantic.py -q` → **35 passed** (content_hash / stale unaffected).
- `pytest -q` (full) → **196 passed, 1 xfailed** (baseline 177+1xfail; +19 new across waves; my 14 included).
- `mypy <this plan's 4 files>` → **Success: no issues found in 4 source files**. (The aggregate `mypy src/newsletters/adapters ...` shows 1 error in 05-02's `_openpyxl_loader.py` — see Issues.)
- `lint-imports` → **Contracts: 1 kept, 0 broken** (no `semantic -> distill` edge added; carrier is in the leaf).
- Fresh-interpreter acyclic import, BOTH orders → **exit 0** (`import newsletters; import newsletters.semantic; import newsletters.distill` and the reverse).
- `grep -v '^#' email_adapter.py | grep -c "_adapter_unextracted"` → **0** (in-memory dict fully removed).

## Next Phase Readiness
- **Wave 2 (Plan 03, ExcelAdapter) is unblocked:** it inherits the hardened pattern — set `source.extraction = encode_coverage(drops)` in `parse()`, recover via `decode_coverage` in `distill()`, add the R2 guard, and append one `pytest.param` to `ADAPTER_CASES` so the Excel `.xlsx` fixtures are pinned by the same round-trip coverage-parity matrix.
- The Phase-4 documented LIMITATION (round-trip silent drop / false `complete=True`) is fixed and pinned executable.

## Self-Check: PASSED
- Created files exist: `src/newsletters/adapters/_coverage_codec.py`, `tests/test_coverage_roundtrip.py`, `.planning/phases/05-excel-adapter/05-01-SUMMARY.md`.
- Commits exist: `35d438a` (Task 1), `1bba430` (Task 2).

---
*Phase: 05-excel-adapter*
*Completed: 2026-06-17*
