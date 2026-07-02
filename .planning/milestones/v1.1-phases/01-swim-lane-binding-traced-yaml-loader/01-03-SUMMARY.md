---
phase: 01-swim-lane-binding-traced-yaml-loader
plan: 03
subsystem: loader-tests
tags: [yaml, trace, coverage, determinism, swimlane, fixtures, adversarial, hole-b, lane-01, lane-02]

# Dependency graph
requires:
  - phase: 01-02
    provides: "src/newsletters/swimlane.py: load_swimlanes() + SectionBinding/SwimlaneLoad + _R_* constants"
provides:
  - "tests/fixtures/swimlane/module-x.yml: generic well-formed module config (24 claims, 0 unextracted)"
  - "tests/fixtures/swimlane/module-trap.yml: adversarial fixture (anchor/alias, block scalar, coercion, duplicate, quotes, mapping-shaped values)"
  - "tests/test_swimlane.py: coverage-identity, faithful-span, LANE-01 binding, Hole-B adversarial, determinism proofs"
  - "executable LANE-01/LANE-02 verification surface for the Phase-1 circuit breaker"
affects: [01-04, "phase 2 composer"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "excel-golden read-anchored identity ported to YAML: claims+unextracted==scalars_walked, cross-checked vs an INDEPENDENT parsed scalar-leaf count"
    - "exact ordered _R_* reasons pinned via the loader's OWN module constants (no inline string duplication -> no drift)"
    - "adversarial 'prove it FIRES': the same is_addressed guard that passes for every loader trace REJECTS a hand-built un-addressed trace"
    - "byte-identical double-load determinism via model_dump_json (mirrors test_worksurface.py:111-118)"

key-files:
  created:
    - "tests/fixtures/swimlane/module-x.yml"
    - "tests/fixtures/swimlane/module-trap.yml"
    - "tests/test_swimlane.py"
  modified: []

key-decisions:
  - "Fixtures authored by DRIVING the live loader first, then pinning its actual output — never authored around a loader gap (RETRO Phase-7). No loader bug surfaced."
  - "Coverage identity cross-checked against an INDEPENDENT _count_scalar_leaves() of the parsed doc, so a loader walking too few OR too many scalars is caught (not just self-consistent)."
  - "Expected trap reasons imported from swimlane's own _R_* constants; the mapping-values missing string is rebuilt from _VALUES_KEY — both drift-resistant."
  - "Value assertions read from the SAME parsed fixture (heading, labels, mapping-trap detection) so tests track the config, never a hardcoded lane name (Pitfall 8)."
  - "Duplicate-offset check is generic: any claim text appearing >1 time must have distinct trace.start — proves the forward cursor without hardcoding the duplicate value."
  - "LANE-01 dict-level proof asserts bound objects are SectionBinding/KpiItem/Claim and NOT models.FunctionalGroup/Kpi (negative isinstance + __module__ check)."

patterns-established:
  - "Two committed fixtures — a clean-path (module-x) and an adversarial trap (module-trap) — as the executable contract, mirroring the excel golden corpus split."
  - "Synthetic-names-only fixture discipline (module-x/module-trap, lane-a, owner-1, eng-01) with a top comment marking each file synthetic (LANE-03 / T-03-01)."

requirements-completed: [LANE-01, LANE-02]

# Metrics
duration: ~20min
completed: 2026-07-02
tasks: 3
files: 3
---

# Phase 1 Plan 3: Swim-lane loader honesty & determinism proofs Summary

Two committed generic fixtures plus `tests/test_swimlane.py` make the LANE-01/LANE-02 circuit-breaker
invariants executable: the read-anchored coverage identity with exact pinned `_R_*` reasons, the
faithful-span check, the Hole-B adversarial guard, byte-stable determinism, and the dict-level
N-lanes → N-`SectionBinding`s binding — all proven by DRIVING the live loader, never asserted in prose.

## What was built

- **`tests/fixtures/swimlane/module-x.yml`** — a small, well-formed module config exercising the full
  lane / KPI / objective shape (module + area ids, two lanes each with heading/id/group/owner/members,
  KPI `values` endpoints and a single `value`, objective refs). Every scalar is uniquely and verbatim
  locatable → the loader mints **24 claims, 0 unextracted**.
- **`tests/fixtures/swimlane/module-trap.yml`** — an adversarial fixture packing each scalar-location
  trap: an anchor/alias pair, a multi-line block scalar, a `yes`→True coercion, a value repeated
  across two KPIs, single- and double-quoted scalars, and a mapping-shaped `values:` slot. The loader
  routes it to **15 claims + 3 unextracted (= 18 scalars walked)**.
- **`tests/test_swimlane.py`** — five tests: coverage-identity, faithful-spans, LANE-01 dict-level
  binding, Hole-B addressed-trace guard (positive + adversarial), and byte-stable determinism.

## Pinned counts and how they were validated as RIGHT (not bug-shaped)

All expectations were derived by running the live loader once and recording its actual output, then
each was checked to be **honest routing** rather than a fixture authored around a loader gap:

| Fixture | bindings | scalars_walked | claims | unextracted | missing[] |
|---|---|---|---|---|---|
| module-x.yml | 2 | 24 | 24 | 0 | none |
| module-trap.yml | 1 | 18 | 15 | 3 | 1 (mapping-values) |

**Cross-check that the counts aren't bug-shaped:** the test independently walks the parsed structure
(`_count_scalar_leaves`) and asserts `scalars_walked == that independent count` — so a loader that
silently skipped a scalar (too few) *or* double-counted (too many) fails, not just an internally
self-consistent tally.

**The 3 trap `unextracted` reasons, in file/walk order, each validated as honest:**
1. `_R_ANCHOR_ALIAS` — the aliased `reviewer: *shared-owner` resolves to `owner-anchored`, whose only
   text occurrence is the earlier `&shared-owner` anchor site (behind the forward cursor). There is no
   distinct forward span to address; pointing at the anchor would be provenance fiction. **Right.**
2. `_R_BLOCK_SCALAR` — the multi-line `note: |` folds/dedents to a logical value that is not a verbatim
   substring of the indented raw text. **Right.**
3. `_R_TYPE_COERCED` — `value: yes` coerces to `True`, whose `str()` ("True") is genuinely absent from
   the raw text. **Right.**

**Duplicate distinct-offset proof:** the repeated `shared-value` mints two claims at distinct offsets
(1540 ≠ 1592) — the forward-only cursor never re-points at the first occurrence. Asserted generically
(any text appearing >1× must have distinct `trace.start`), not against a hardcoded value.

**Mapping-shaped `values:` (the commit-40976cc required case):** `values: {start, close}` yields an
**empty** `KpiItem.value` display AND the `missing[]` disclosure
`"KPI declares 'values' but not as a list of period endpoints"` (rebuilt from the `_VALUES_KEY`
constant), while its endpoints `111`/`222` are still independently traced (zero silent drops).

## Deviations from Plan

None — plan executed exactly as written. No loader bug was exposed; every pinned expectation is honest
loader behavior. No `src/` edit, conftest change, or existing-test change was needed or made.

## Gate output tails (re-run independently)

- `.venv/bin/pytest tests/test_swimlane.py -q` → `5 passed`
- `.venv/bin/pytest -q` (full suite) → `579 passed in 14.13s`
- `black --check tests/test_swimlane.py` → `1 file would be left unchanged`
- `isort --profile black --check-only tests/test_swimlane.py` → clean (the project convention; plain
  `isort` fails on `test_worksurface.py`/`test_excel_golden.py` too — a pre-existing baseline, not this file)
- `mypy tests/test_swimlane.py` → only the ambient `import-untyped` notes shared by every test file
  (the installed `newsletters` package ships no `py.typed`); zero new type errors from this file.

## Concerns / notes for downstream

- **mypy `import-untyped` is ambient**, not introduced here — every test importing `newsletters.*`
  emits it because the package has no `py.typed` marker. If Plan 01-04 or a later phase wants a truly
  clean `mypy tests/` it should add `py.typed` (or a mypy `ignore_missing_imports`) in `src/` — out of
  this plan's file ownership.
- **`isort` must be run with `--profile black`** to match the repo's committed vertical-import style;
  bare `isort` disagrees with black and (falsely) flags existing files.
- Fixtures use synthetic names only (LANE-03 / T-03-01); the repo-wide abstraction-guard that enforces
  this over `src/` and committed content is Plan 01-04's responsibility.

## Self-Check: PASSED
