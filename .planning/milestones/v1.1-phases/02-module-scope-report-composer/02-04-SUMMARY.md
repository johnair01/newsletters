---
phase: 02-module-scope-report-composer
plan: 04
subsystem: testing
tags: [pytest, compose, trust-guards, content-addressing, determinism, delta, review-gate]

# Dependency graph
requires:
  - phase: 02-03
    provides: "compose.py complete — compute_delta + compose_module_report(load, *, author, quote, owner, ledger, ledger_path)"
  - phase: 01
    provides: "swimlane.SectionBinding / SwimlaneLoad — the kind-agnostic per-section seam, kpi_endpoints pairing"
provides:
  - "tests/test_compose.py — the executable trust-guard contract over the live composer"
  - "Hole A + Hole B closure PROVEN at the composer (adversarial, non-vacuous)"
  - "Δ reproducibility + determinism (byte-equality) proof for the composed surface"
  - "no-auto-publish adversarial proof on the composed Draft surface"
  - "kind-agnostic seam proof (a non-lane SectionBinding composes unchanged)"
affects: [03-render-content, phase-3-worked-module]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "In-memory SectionBinding fixtures (no YAML) driving the live composer"
    - "Forward-only _Cursor minter for genuinely content-addressed Claims via Trace.from_source"
    - "Assert structure/invariants from the SAME inputs the composer read (Pitfall 8), never a frozen string"
    - "git diff --exit-code as a runtime gate-untouched proof (Pitfall 11)"

key-files:
  created:
    - tests/test_compose.py
  modified: []

key-decisions:
  - "Endpoint Claims are also placed in SectionBinding.claims (mirrors swimlane's read-anchored model), so numeral-bearing content on a ClaimsBlock is exercised as a legitimate traced case"
  - "Numeral-free-prose guard exempts ONLY KpiItem.value/.delta on a KpiStripBlock (checked traceable separately); heading + labels + all Prose/Quote/Fanout text must be digit-free"
  - "Isolated empty in-memory Ledger per compose (no disk I/O) — compose never save()s, so tests stay hermetic and byte-stable"

patterns-established:
  - "Non-vacuity is proven, not assumed: planted untraced + un-addressed claims shown routed to missing[]; a poisoned ProseBlock proves the numeral guard bites"
  - "Delta reproducibility recomputes every rendered delta from its two paired endpoints and asserts byte-equality of delta AND dir"

requirements-completed: [COMP-01, COMP-02, COMP-03, COMP-04]

# Metrics
duration: ~25min
completed: 2026-07-02
---

# Phase 2 Plan 04: Composer Trust-Guard Suite Summary

**13 adversarial tests over the live composer that close research Holes A + B at the composer, prove Δ reproducibility + byte-determinism, enforce no-auto-publish on the composed Draft surface, and prove the kind-agnostic seam — with every protected gate byte-untouched.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-02
- **Tasks:** 3
- **Files modified:** 1 (created)

## Accomplishments
- Hole B closed at the composer: every ClaimsBlock claim is traced AND content-addressed; a planted zero-trace claim AND a planted un-addressed-trace claim are proven routed to `missing[]` (non-vacuous).
- Hole A closed at the composer: authored (non-ClaimsBlock) prose is numeral-free (proven non-vacuous by a poisoned block); the only out-of-claim numerals are `KpiItem.value`/`.delta` on a KpiStripBlock, each traceable to a content-addressed endpoint.
- Δ contract proven on the composed surface: every rendered delta recomputes byte-equal from its two paired endpoints via `compute_delta` (delta AND dir); all three arms exercised — real movement, point-in-time (no fabricated 0), Δ==0 (dir=None + computed zero form).
- Determinism proven: two composes of the same load are byte-identical `model_dump_json`; `created == EPOCH_ZERO`; a repeated KPI value across two lanes stays byte-stable in file order.
- No-auto-publish proven: composed surface is Draft; `publish()` without the gate raises and leaves Draft; a direct `Review(state=PUBLISHED, ...)` raises.
- Kind-agnostic seam proven: a NON-lane SectionBinding (a "risk register") composes into a valid Draft surface with ZERO composer change. Edge cases (zero-KPI lane, empty binding set, unowned/sourced quote) all behave honestly.
- Gate-untouched proof: `faithfulness`/`coverage`/`semantic`/`templates`/`site` are byte-untouched (`git diff --exit-code`).

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Hole A/B guards + no-auto-publish** - `cc581c2` (test)
2. **Task 2: delta reproducibility + determinism** - `dd4ab64` (test)
3. **Task 3: kind-agnostic seam + edge cases + gate-untouched proof** - `6aae29f` (test)

## Files Created/Modified
- `tests/test_compose.py` - The phase's trust-guard proof suite (13 tests) over the live `newsletters.compose` composer, driven by hand-built, genuinely content-addressed in-memory SectionBindings.

## Decisions Made
- Placed endpoint Claims in `SectionBinding.claims` as well as `kpi_endpoints` (the same objects, by reference) to mirror swimlane's read-anchored model — this also exercises numeral-bearing content as a legitimate traced ClaimsBlock case.
- The numeral-free guard exempts only KpiItem.value/.delta (validated traceable separately); every heading, KPI label, and all Prose/Quote/Fanout text must be digit-free.
- Each compose uses a fresh empty in-memory `Ledger` (no disk read/write), keeping tests hermetic and output byte-stable (compose never calls `save()`).

## Deviations from Plan

None - plan executed exactly as written. All three tasks landed as specified; the only writable target (`tests/test_compose.py`) was the sole file touched.

## Issues Encountered
- One authoring slip during Task 1: an early assertion called `.is_addressed` on a `Claim` (that property lives on `Trace`). Fixed immediately by checking `claim.is_traced and all(t.is_addressed for t in claim.evidence)`. Not a composer bug — a test-code fix, caught by the failing run before commit.

## Composer Bugs Found
None. The live composer (built in 02-02 / 02-03) passed every adversarial guard on the honest happy path and on the planted-cheat paths. No honest failing expectation had to be left RED; no composer source was touched (forbidden by scope and unnecessary).

## Verification (independently re-run)
- `.venv/bin/pytest tests/test_compose.py -q` → 13 passed.
- `.venv/bin/pytest -q` (full suite) → **605 passed** (was 592; +13 new).
- `.venv/bin/lint-imports` → 2 contracts kept, 0 broken.
- `.venv/bin/black` + `.venv/bin/isort --profile black` on the test file → clean.
- `.venv/bin/mypy tests/test_compose.py` → only the baseline `import-untyped` notes (identical to existing test files, e.g. test_worksurface.py); zero NEW failures.
- `git diff HEAD --exit-code` on faithfulness/coverage/semantic/templates/site → clean (exit 0).

## Next Phase Readiness
- The composer's trust guarantees are now enforced by executable adversarial tests (COMP-01..04 provably satisfied). Phase 3 (rendering into `content/`, the worked `module-a`) can build on a composer whose Draft-only, faithful, reproducible, kind-agnostic contract is locked.
- No blockers.

## Self-Check: PASSED
- `tests/test_compose.py` exists (FOUND).
- Commits FOUND: `cc581c2`, `dd4ab64`, `6aae29f`.

---
*Phase: 02-module-scope-report-composer*
*Completed: 2026-07-02*
