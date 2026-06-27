---
phase: 01-distill-socket-contract
plan: 02
subsystem: distill-socket
tags: [conformance, faithfulness-seam, hard-rules, no-auto-publish, ai-optional, pydantic]
requires:
  - "Plan 01-01 contract: DistillPort, DistillationResult, FaithfulnessCheck, StructuralFaithfulness, Coverage (ports.py + coverage.py)"
  - "ManualBackend (the conforming in-src backend) from Plan 01-01"
  - "Rev1 review gate (Review/Surface/ReviewState + the no-auto-publish validator) in semantic.py"
provides:
  - "assert_conforms(backend, sources) -> DistillationResult — the reusable RUNTIME malformed-backend guard (SOCK-05)"
  - "_enforce(result, check=StructuralFaithfulness()) -> DistillationResult — single-place, injectable faithfulness boundary (Phase-3 swap point)"
  - "Executable proof of the two load-bearing hard rules: no auto-publish, AI-optional core"
affects:
  - "src/newsletters/distill/ports.py (adds _enforce)"
  - "src/newsletters/distill/__init__.py (re-exports assert_conforms)"
tech-stack:
  added: []
  patterns:
    - "runtime conformance suite as the real malformed-backend guard (not mypy, not isinstance shape) — review MEDIUM-2"
    - "one-trust-rule-one-place: faithfulness enforced solely in _enforce, injectable for Phase-3 span-containment"
    - "deliberately-broken in-test backend fixture proves the contract has teeth"
key-files:
  created:
    - "src/newsletters/distill/conformance.py"
  modified:
    - "src/newsletters/distill/ports.py"
    - "src/newsletters/distill/__init__.py"
    - "tests/test_distill_socket.py"
decisions:
  - "Faithfulness is enforced ONLY in ports._enforce — conformance.py delegates to it, and no backend calls it. One trust rule, one auditable place; Phase 3 swaps the FaithfulnessCheck with zero backend change."
  - "assert_conforms accepts an optional `check` kwarg (defaulting to StructuralFaithfulness) so the same conformance routine exercises the Phase-3 span-containment check unchanged."
  - "The no-auto-publish hard rule is asserted structurally: the socket's return type is DistillationResult (never Surface/Review), the backend exposes no publish/approve/review API, and the Rev1 review gate still refuses PUBLISHED without policy — proving the gate stays the sole publish path."
  - "AI-isolation is proven two ways: a clean-subprocess sys.modules assertion (Plan 01's test, still green) and a source grep showing zero AI imports under distill/."
metrics:
  duration: "~12 min"
  completed: "2026-06-17"
  tasks: 2
  files_created: 1
  files_modified: 3
---

# Phase 1 Plan 2: Conformance Suite + Faithfulness Seam Summary

The contract from Plan 01 is now **enforceable**: `assert_conforms(backend, sources)` runs ANY registered backend through the socket and FAILS it on a violation — a non-DistillPort shape, a wrong return type, an absent coverage manifest, an untraced/unfaithful claim, or a lying coverage manifest. The faithfulness rule lives in exactly one injectable place (`_enforce`), so Phase 3 can swap structural tracing for deterministic span-containment without touching any backend. The two load-bearing hard rules — no auto-publish and AI-optional core — are now executable assertions, not prose.

## What Was Built

- **`src/newsletters/distill/conformance.py`** (NEW) — `assert_conforms(backend, sources, *, check=StructuralFaithfulness())`. The RUNTIME malformed-backend guard (SOCK-05, review MEDIUM-2). Asserts, in order: (1) `isinstance(backend, DistillPort)` shape; (2) `distill()` returns a `DistillationResult` (never a `Surface`/`Review` — the no-auto-publish hard rule, structurally); (3) `coverage is not None` and internally honest (the `Coverage` validator already forbids complete-with-dropped-content); (4) every claim passes the injected faithfulness `check` via the single-place `_enforce`; (5) lossless JSON round-trip (D-04). Returns the validated result. Teaching-style assertion messages throughout. Zero AI imports.
- **`src/newsletters/distill/ports.py`** — added `_enforce(result, check=StructuralFaithfulness())`. The SOLE site faithfulness is applied: runs `check.entails(claim)` over every claim and raises a teaching-style `ValueError` on the first unfaithful one, else returns the result unchanged. The `check` parameter is the Phase-3 (PROV-02) injection point. Not called inside any backend.
- **`src/newsletters/distill/__init__.py`** — re-exports `assert_conforms` so any backend's own tests can `from newsletters.distill import assert_conforms`.
- **`tests/test_distill_socket.py`** — extended (not replaced) with a deliberately-broken `_UntracedClaimBackend` fixture and the SOCK-05 + hard-rule tests: `test_conformance_passes_manual_backend` (positive), `test_conformance_fails_bad_backend` (the runtime negative — proves teeth mypy cannot give), `test_faithfulness_seam_rejects_untraced` (rejection + permissive-injection pass-through, proving the seam is injectable), `test_coverage_lying_completeness_rejected`, `test_socket_never_auto_publishes`. The pre-existing `test_distill_package_imports_no_ai` (AI-optional hard rule, fresh subprocess) remains green.

## How It Works (the why)

`@runtime_checkable isinstance(.., DistillPort)` only checks attribute *presence*, and mypy only ever type-checks the conforming in-`src` `ManualBackend` — the broken backend that PROVES the contract has teeth lives in `tests/` and is invisible to the type checker. So the *runtime* conformance routine is the real malformed-backend guard. Faithfulness is enforced in one place (`_enforce`) rather than scattered across backends, which is what makes the Phase-3 swap a one-line injection rather than an N-backend edit. The no-auto-publish rule is enforced by construction: the socket's only output type is `DistillationResult`, so there is no return path to a published `Surface`/`Review`; the merged review gate (`semantic.py`) stays the sole publish path.

## Deviations from Plan

**None — plan executed as written.** Two minor mechanical notes: `Claim` was added to the test module's `semantic` import (needed by the broken-backend fixtures), and the positive case the plan names `test_conformance_passes_manual_backend` subsumed the Task-1 RED placeholder (the RED test was committed at 5a1f6f6, then evolved into the plan's named positive test) — no behavior lost, both the module/barrel-identity check and the conforming-pass assertion are retained.

## Verification (gates re-run independently, actual output)

- `pytest tests/test_distill_socket.py -q` -> **14 passed** (10 from Plan 01 + 4 new SOCK-05/hard-rule).
- `pytest tests/test_semantic.py -q` (Rev1 regression tripwire) -> **18 passed**.
- `pytest -q` (whole suite, phase gate) -> **32 passed**.
- `mypy src/newsletters/distill` -> **Success: no issues found in 6 source files**.
- Independent AI-isolation (env-recommended): `PYDANTIC_DISABLE_PLUGINS=true python -c "import newsletters.distill"` -> AI in sys.modules: **NONE — clean**.
- Source assertion: `grep langchain|langgraph|langsmith|pydantic_ai|openai|anthropic src/newsletters/distill` -> **0 occurrences**.
- Teeth check (independent): `assert_conforms(<untraced-claim backend>, [])` -> **rejected (ValueError at the faithfulness seam)**.

## Hard Rules Honored

- **No auto-publish (the single most important invariant):** proven by `test_socket_never_auto_publishes` — the socket returns `DistillationResult` only (not `Surface`/`Review`), the backend exposes no publish/approve/review API, and `Review(state=PUBLISHED)` without policy still raises. The Rev1 gate remains the sole publish path.
- **Every published claim traces to evidence:** `_enforce` (structural default = `Claim.is_traced`) rejects any untraced claim crossing the socket; `assert_conforms` routes it through that seam.
- **AI-optional core:** `conformance.py` and the `_enforce` addition import only stdlib + the package's Pydantic types; zero AI reachable (source grep + clean-subprocess sys.modules assertion).
- **Typed everything / faithful, not suggestive:** all new code is typed; the faithfulness seam is deterministic and injectable, never editorializing.

## Known Stubs

None introduced by this plan. (The adapter-phase `Locator` variants noted in Plan 01 remain intentional documented stubs for Phases 4-7; no Phase-1 goal depends on them.)

## Self-Check: PASSED

- File created — FOUND: `src/newsletters/distill/conformance.py`.
- Commits exist: 5a1f6f6 (RED test), 3e50edf (Task 1 GREEN), ccf1734 (Task 2 tests).
