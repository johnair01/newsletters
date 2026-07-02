---
phase: 02-module-scope-report-composer
plan: 01
subsystem: api
tags: [swimlane, pydantic, kpi, delta, traceability, endpoint-pairing]

# Dependency graph
requires:
  - phase: 01-swim-lane-binding-traced-yaml-loader
    provides: "swimlane.SectionBinding / SwimlaneLoad / _bind_kpis (traced KPI minting), the read-anchored coverage identity, the module-x/module-trap fixtures"
provides:
  - "SectionBinding.kpi_endpoints: additive per-KPI ordered traced endpoint Claims (by reference)"
  - "_mint_scalar now returns the minted Claim (or None) so callers can pair endpoints without re-minting"
  - "tests/test_swimlane_endpoints.py: executable proof of the endpoint-pairing invariant"
affects: [02-02 compose.py, compute_delta, KpiStripBlock]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reference-not-re-mint pairing: an accumulator collects the SAME Claim objects already appended to claims[], keeping the read-anchored coverage identity intact"
    - "Lockstep parallel arrays: kpi_endpoints appended in step with kpi_items so len() are equal by construction"

key-files:
  created:
    - tests/test_swimlane_endpoints.py
  modified:
    - src/newsletters/swimlane.py

key-decisions:
  - "kpi_endpoints modeled as list[list[Claim]] parallel to kpi_items (element i pairs kpi_items[i]) rather than a new typed carrier — reuses existing Claim, keeps models.py untouched"
  - "_mint_scalar returns a 3-tuple (display_token, is_scalar, minted_claim_or_none); the Claim is handed back by reference so _bind_kpis pairs endpoints with zero re-mints"
  - "A non-locatable / type-coerced / mapping-shaped endpoint contributes NO reference (never a placeholder), so a delta can only ever be derived from genuinely traced endpoints"

patterns-established:
  - "Additive-only extension of a frozen Phase-1 module under the byte-untouched-tests hard condition"

requirements-completed: []  # COMP-01/COMP-02 unblocked but NOT complete — COMP reqs close only when the phase completes (per plan rules)

# Metrics
duration: 5min
completed: 2026-07-02
---

# Phase 2 Plan 01: SectionBinding endpoint-pairing Summary

**Additive `SectionBinding.kpi_endpoints` (per-KPI ordered traced endpoint Claims, by reference) that lets Phase-2's composer derive Δ from two independently content-addressed endpoints — with the Phase-1 loader tests byte-untouched and the coverage identity intact.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-02T04:45:21Z
- **Completed:** 2026-07-02T04:50:03Z
- **Tasks:** 2
- **Files modified:** 2 (1 modified, 1 created)

## Accomplishments
- Added the additive `kpi_endpoints: list[list[Claim]]` field to `SectionBinding`, 1:1 with `kpi_items`, holding each KPI's ordered traced endpoint Claims by REFERENCE (never re-minted).
- Threaded a per-KPI endpoints accumulator through `_bind_kpis` by extending `_mint_scalar` to also return the minted Claim (or `None`), appended in lockstep with `kpi_items`.
- Proved the invariant with a new dedicated test suite (alignment, reference-not-re-mint object identity, coverage identity intact, `values:`-list ordering, no fabricated reference for the disclosed mapping-shaped trap).
- Kept `tests/test_swimlane.py` and `tests/test_abstraction_guard.py` byte-untouched and green; full suite 587 → 592 passed.

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Add additive kpi_endpoints field + reference population** - `e3554ed` (feat)
2. **Task 2: Prove the pairing invariant** - `619b76e` (test)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified
- `src/newsletters/swimlane.py` - Added `kpi_endpoints` field + docstring on `SectionBinding`; `_mint_scalar` returns `(token, is_scalar, minted_claim_or_none)`; `_bind_kpis` threads a per-KPI endpoints accumulator appended in lockstep with `kpi_items`; `_bind_lane` creates and passes the accumulator into the constructor.
- `tests/test_swimlane_endpoints.py` - New proof suite over both committed fixtures: alignment, reference identity, coverage identity, ordering (file order + addressed), no fabricated reference.

## Decisions Made
- `kpi_endpoints` is `list[list[Claim]]` parallel to `kpi_items` (not a new typed carrier) — reuses `Claim`, leaves `semantic.py`/`models.py` untouched (forbidden list honored).
- `_mint_scalar` extended to return the minted Claim by reference; the two existing recognized-slot callers (`_LABEL_KEY`, `_VALUE_KEY`, `_VALUES_KEY`) updated to capture (or discard, for labels) the third element.
- Non-locatable/type-coerced/mapping-shaped endpoints contribute no reference — a KPI can carry fewer references than it declares, so Δ is only ever derivable from genuinely traced endpoints (matches the trap's disclosed `values:` mapping and the `yes`→True coerced value).

## Deviations from Plan

None - plan executed exactly as written. (Two auto-format passes by `black` on the touched files, which is the sanctioned house style; not a behavioral deviation.)

## Issues Encountered
- `mypy` run directly on the new test file reports `import-untyped` for the `newsletters` package (no `py.typed` marker). This is pre-existing BASELINE behavior — the existing `tests/test_swimlane.py` emits the identical error class when mypy is pointed at it directly. Zero NEW mypy error categories were introduced. `mypy src/newsletters/swimlane.py` is clean (`Success: no issues found`).

## Gate Results (independently re-run, per CLAUDE.md discipline)
- `pytest tests/test_swimlane_endpoints.py tests/test_swimlane.py tests/test_abstraction_guard.py` → **12 passed**.
- Full suite `pytest -q` → **592 passed** (587 baseline + 5 new).
- `git diff --exit-code tests/test_swimlane.py tests/test_abstraction_guard.py` → **exit 0** (byte-untouched, also verified vs plan-start commit ec50396).
- `lint-imports` → **2 kept, 0 broken** (loader stays AI-free / yaml-free at top level).
- `black --check` / `isort --check-only --profile black` on both touched files → clean.
- `mypy src/newsletters/swimlane.py` → clean; test-file `import-untyped` is baseline noise (see above).

## Next Phase Readiness
- Wave 2 (`compose.py`) can now consume `binding.kpi_endpoints[i]` to feed `compute_delta(start, close)` from two independently traced endpoints — the endpoint-pairing gap identified in 02-PATTERNS.md is closed.
- COMP-01 (kind-agnostic strip) and COMP-02 (two-endpoint delta) are unblocked; they remain formally incomplete until the phase completes.

## Self-Check: PASSED

- FOUND: src/newsletters/swimlane.py
- FOUND: tests/test_swimlane_endpoints.py
- FOUND: .planning/phases/02-module-scope-report-composer/02-01-SUMMARY.md
- FOUND commit: e3554ed (Task 1)
- FOUND commit: 619b76e (Task 2)

---
*Phase: 02-module-scope-report-composer*
*Completed: 2026-07-02*
