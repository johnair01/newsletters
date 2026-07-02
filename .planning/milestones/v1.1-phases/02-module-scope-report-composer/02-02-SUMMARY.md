---
phase: 02-module-scope-report-composer
plan: 02
subsystem: composer
tags: [compose, compute_delta, kpi-delta, surface, report, determinism, faithfulness, pydantic]

# Dependency graph
requires:
  - phase: 01-swim-lane-binding-traced-yaml-loader
    provides: "SectionBinding.kpi_endpoints (per-KPI ordered traced endpoint Claims), SwimlaneLoad"
  - phase: 02-01
    provides: "additive kpi_endpoints pairing on SectionBinding (endpoint Claims by reference)"
provides:
  - "src/newsletters/compose.py — new top-level module-scope Report composer"
  - "compute_delta(start, close): pure signed-Δ + dir derivation over two numeric endpoints"
  - "compose_module_report(load, *, author): deterministic Surface(REPORT, Draft) from SectionBinding[]"
affects: [02-03, 02-04, 03-render]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure derivation with undefined-as-first-class (either endpoint non-numeric -> None, never a fabricated 0)"
    - "Kind-agnostic composition seam: consume SectionBinding[] with no knowledge lanes exist"
    - "Explicit created=EPOCH_ZERO on a composed Surface for byte-stable model_dump_json"
    - "Traced-or-missing routing carried over from worksurface (select, never re-mint)"

key-files:
  created:
    - src/newsletters/compose.py
  modified: []

key-decisions:
  - "compute_delta via Decimal + a single regex parser; int endpoints render '+10' (not '+10.0'), floats strip trailing zeros"
  - "Optional trailing unit preserved only when BOTH endpoints carry the SAME unit; never invented"
  - "Δ trust gate: both endpoint Claims must be content-addressed (is_addressed) AND numeric before compute_delta is called; otherwise delta=None + missing[] note"
  - "Surface identity derived from load.source.id (slug + humanized title) — config-derived data, no hardcoded/computed numerals"
  - "missing[] is an order-preserving union (file order, no set()) to satisfy both 'union' and determinism"
  - "A leading connective ProseBlock (numeral-free) is emitted only when there are sections; omitted for an empty module"

patterns-established:
  - "compute_delta: the single pure Δ derivation; Δ lives only in KpiItem.delta/.dir, never a Claim, never traced"
  - "compose_module_report: per-section KpiStripBlock + ClaimsBlock in file order via the kind-agnostic seam"

requirements-completed: [COMP-01, COMP-02, COMP-03]

# Metrics
duration: ~25min
completed: 2026-07-02
---

# Phase 2 Plan 02: Module-scope Report composer core Summary

**A new `compose.py` with a pure `compute_delta` (signed Δ + dir, undefined-as-first-class) and `compose_module_report` that assembles `SectionBinding[]` into a byte-stable Draft REPORT `Surface` — per-section KPI strip + traced claims, honest `missing[]` routing, no authored facts.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2 (both `tdd`-flagged; verified via the plan's `python -c` smoke checks — the test suite is owned by Plan 02-04)
- **Files modified:** 1 (new `src/newsletters/compose.py`)

## Accomplishments
- `compute_delta(start, close)` — a pure, deterministic function: `("10","20") -> ("+10","up")`, `("20","8") -> ("-12","down")`, `("5","5") -> ("0",None)` honest no-change, `("abc","20")`/`("10","")` -> `(None,None)`. Never a fabricated 0.
- `compose_module_report` — one `KpiStripBlock` + one `ClaimsBlock` per `SectionBinding` in file order via the kind-agnostic seam; per-KPI Δ computed only from two content-addressed numeric endpoints; declared-but-uncomputable movement routed to `missing[]` (delta=None); untraced/unaddressed claims dropped from the block and disclosed; zero-KPI section omits its strip + discloses; empty section set still yields a valid Draft with populated `missing[]`.
- Deterministic composed `Surface`: `template=REPORT`, `review` Draft, `created=EPOCH_ZERO` passed explicitly (the confirmed `now()` determinism trap avoided), `traces=[load.source]`, order-preserving `missing[]` union, no `set()`/`publish()` in the lane path — two composes are byte-identical.

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Module scaffold + pure compute_delta** - `f682620` (feat)
2. **Task 2: compose_module_report kind-agnostic assembly + deterministic Surface** - `3a51bf0` (feat)

_Note: both tasks carry `tdd="true"` in the plan, but this plan's verification is the two `python -c` smoke checks and the gate suite; the `tests/test_compose.py` trust-guard suite is explicitly owned by Plan 02-04 and by the forbidden-list ("owns ONLY compose.py") — so no test file was created here._

## Files Created/Modified
- `src/newsletters/compose.py` — pure `compute_delta` + `compose_module_report` core; AI-free, yaml-free/loader-agnostic; stdlib (`re`/`decimal`) + pydantic + `semantic`/`swimlane`/`templates`/`adapters._timestamps` only.

## Decisions Made
- **Δ arithmetic via `Decimal`** parsed by one regex (`^\s*([+-]?\d+(?:\.\d+)?)\s*(\S*)\s*$`): keeps int/float distinction (int pair renders `+10`, not `+10.0`), avoids binary-float artifacts, deterministic. Arithmetic done once, then formatted once (no rounding inside a format string).
- **Unit-preserving is conservative:** the trailing non-numeric unit is appended only when both endpoints carry the *same* unit; never invented.
- **Content-address trust gate on endpoints:** `compose_module_report` computes Δ only when both endpoint Claims are traced *and* `is_addressed`; otherwise `delta=None` + a `missing[]` note. `compute_delta` itself is the numeric gate (non-numeric -> `(None,None)`).
- **Identity from config data:** slug + humanized title derive from `load.source.id` (no hardcoded module name, no computed numerals authored into title/eyebrow/prose).
- **`missing[]` = order-preserving union** (file order; deduped without `set()`), honoring both the "union" contract and byte-determinism.
- **Connective `ProseBlock`** emitted only when sections exist; its text is transition-only and numeral-free (COMP-03; the numeral-free-prose guard lands in 02-04).

## Deviations from Plan

None - plan executed exactly as written. (`black` reformatted the new file after Task 2 authoring; this is the project's formatting gate, not a behavioral change.)

## Issues Encountered
None. `swimlane.py` was untouched (its `kpi_endpoints` field was already landed by Plan 02-01), so no additive extension was needed in this plan — endpoints were consumed as-built.

## Gate Results (independently re-run)
- `.venv/bin/pytest -q` → **592 passed** (matches the 02-01 baseline; zero regressions).
- `lint-imports` → 2 contracts kept, 0 broken (compose is AI-free / yaml-free / loader-agnostic).
- `black --check`, `isort --profile black --check-only`, `mypy` on `compose.py` → all clean, zero new errors.
- Both plan smoke checks (`compute_delta` cases; `compose_module_report` template/gate/created/delta/determinism/empty) → pass.
- Independent edge-case check: single-endpoint KPI (value-only, no note), non-computable movement (delta=None + note), untraced claim (dropped + disclosed), zero-KPI section (strip omitted + disclosed), interleaved file-order blocks, path-derived id determinism → all correct.

## Next Phase Readiness
- COMP-01/02/03 core is in place. Plan 02-03 adds (same file, extensible signature already in place): the owner-quote slot, the fanout stub, and the `R-NNN` identity ledger (`from .site import Ledger`, `content/module/ids.json`).
- Plan 02-04 lands `tests/test_compose.py` — the trust-guard suite (zero-trace-claim, all-content-addressed, numeral-free-prose, no-auto-publish on the composed surface, Δ reproducibility, kind-agnostic seam).

## Self-Check: PASSED
- FOUND: `src/newsletters/compose.py`
- FOUND: `.planning/phases/02-module-scope-report-composer/02-02-SUMMARY.md`
- FOUND commit: `f682620` (Task 1)
- FOUND commit: `3a51bf0` (Task 2)

---
*Phase: 02-module-scope-report-composer*
*Completed: 2026-07-02*
