---
phase: 03-content-addressed-provenance-faithfulness
plan: 03
subsystem: distill-faithfulness-gate
tags: [provenance, faithfulness, span-containment, socket-seam, deterministic, no-ai, prov-02]

# Dependency graph
requires:
  - phase: 03-01
    provides: Trace.is_addressed, Trace.span, Trace.from_source (content-addressed evidence)
  - phase: 01-distill-socket
    provides: injectable FaithfulnessCheck seam (_enforce / assert_conforms), StructuralFaithfulness
  - phase: 02-ai-optional-packaging
    provides: import-linter AI-optional contract (core = stdlib + pydantic only)
provides:
  - SpanContainmentFaithfulness — deterministic, stdlib-only span-containment FaithfulnessCheck
  - route_unfaithful_to_missing(result, check=...) — relocate unfaithful claim text to missing[]
  - _enforce / assert_conforms DEFAULT swapped to span-containment (every backend inherits it)
  - FaithfulnessCheck made @runtime_checkable (parity with DistillPort)
affects: [adapters, ai-backends, review-surface, 03-02]

# Tech tracking
tech-stack:
  added: []  # stdlib str.casefold + str.split only — zero new dependency, AI-optional preserved
  patterns:
    - "Span-containment faithfulness: normalize (casefold + whitespace-collapse) on TRANSIENT copies, then substring-contain claim in trace span"
    - "Option A self-strengthening gate: un-addressed traces => structural fallback (never a false positive); content-addressed traces => strict containment with teeth"
    - "Single-place seam default swap: change _enforce's default check, every backend inherits with zero backend change (D-3)"
    - "Lazy default to break an import cycle: check=None resolves the .faithfulness default inside _enforce (faithfulness imports from ports, not vice-versa)"

key-files:
  created:
    - src/newsletters/distill/faithfulness.py
    - tests/test_faithfulness_gate.py
  modified:
    - src/newsletters/distill/ports.py
    - src/newsletters/distill/conformance.py
    - src/newsletters/distill/__init__.py

key-decisions:
  - "OPTION A (resolved by reviewer, implemented exactly): entails iff >=1 trace AND (a) some trace is un-addressed [structural fallback, span-containment N/A] OR (b) some content-addressed trace's normalized span contains the normalized claim text"
  - "Untraced claim => never entailed (preserves Phase-1 structural rejection of untraced claims)"
  - "Default seam swapped via lazy check=None resolution to keep the import graph acyclic (faithfulness imports ports)"
  - "FaithfulnessCheck made @runtime_checkable (parity with DistillPort) so a checker satisfies the seam via isinstance"
  - "capture.py NOT touched (Option B rejected — false-positive risk, out of scope)"

requirements-completed: [PROV-02]

# Metrics
duration: ~15min
completed: 2026-06-17
---

# Phase 3 Plan 03: Span-Containment Faithfulness Gate Summary

**A deterministic, stdlib-only `SpanContainmentFaithfulness` gate — normalized (casefold + whitespace-collapse) substring containment of a claim in its content-addressed trace span — made the DEFAULT at the single `_enforce`/`assert_conforms` seam so every backend inherits it with zero backend change, plus a `route_unfaithful_to_missing` companion that relocates unfaithful claims to `missing[]` verbatim, never as a fact.**

## Performance
- **Duration:** ~15 min
- **Tasks:** 3 (TDD: one RED gate, then GREEN per task)
- **Files:** 2 created, 3 modified

## Accomplishments
- `SpanContainmentFaithfulness.entails(claim)` — deterministic, no-AI. `_normalize(text) = " ".join(text.casefold().split())` runs on TRANSIENT copies only; the stored `claim.text` / `trace.span` are never mutated (faithful, not suggestive).
- Made `SpanContainmentFaithfulness()` the DEFAULT check at `ports._enforce` and `conformance.assert_conforms` — every backend now inherits span-containment with ZERO backend change (D-3). The seam stays injectable: an explicit `check` still overrides; `_enforce`/`assert_conforms` signatures are unchanged (the default became `None`, resolved lazily).
- `route_unfaithful_to_missing(result, check=SpanContainmentFaithfulness())` — the non-raising companion: keeps only entailed claims, appends each failing claim's `text` VERBATIM to `Distillation.missing[]`, builds a fresh result via `model_copy(update=...)` (no in-place mutation). Uses the SAME default check as `_enforce` (one definition of "faithful").
- `FaithfulnessCheck` made `@runtime_checkable` (parity with `DistillPort`).

## OPTION A — the resolved design decision (implemented exactly)
The reviewer resolved the empty-span problem with **Option A**, mirroring the approved 03-01 STALE rule ("un-addressed ⇒ not content-addressed ⇒ never a false positive"):

`entails(claim)` is True iff the claim has ≥1 trace AND at least one trace satisfies:
- **(a) un-addressed** (`trace.is_addressed is False` — the Rev1/capture path): STRUCTURAL fallback. Counts as entailed because it is traced; span-containment is NOT APPLICABLE without content-addressed evidence. **OR**
- **(b) content-addressed** (`is_addressed is True`) AND `_normalize(claim.text)` ⊆ `_normalize(trace.span)`.

A claim with NO traces is never entailed.

**Why this is correct (the rationale):** the live capture path (`src/newsletters/capture.py`) builds traces with EMPTY spans and no content hash. Strict span-containment would falsely reject every Rev1/capture claim — violating the "faithful, not suggestive" hard rule (no false positives) and breaking `test_conformance_passes_manual_backend` / `test_socket_end_to_end_manual_roundtrip`. Option A gives span-containment **teeth exactly where there is real content-addressed evidence** to check against, while legacy un-addressed traces keep the structural guarantee. The gate **self-strengthens** as the pipeline adopts content-addressing: 03-02 migrates the sample corpus to `Trace.from_source`, so those claims come under strict containment (b) automatically.

**`capture.py` was NOT touched** (Option B, rejected — out of scope, false-positive risk). The plan's "empty span ⇒ unfaithful" edge case was implemented in its correct scoped form: *a CONTENT-ADDRESSED trace whose span does NOT contain the claim text ⇒ unfaithful ⇒ routed to `missing[]`*. An un-addressed/empty-span trace is the structural-fallback case, not auto-unfaithful.

## Final API
```python
# src/newsletters/distill/faithfulness.py
def _normalize(text: str) -> str:                       # casefold + whitespace-collapse (transient)

class SpanContainmentFaithfulness:
    def entails(self, claim: Claim) -> bool: ...         # Option A (above); multi-trace: ANY one entails

def route_unfaithful_to_missing(
    result: DistillationResult,
    check: FaithfulnessCheck = SpanContainmentFaithfulness(),
) -> DistillationResult: ...                             # relocate failing claim text -> missing[] verbatim

# src/newsletters/distill/ports.py
def _enforce(result, check: Optional[FaithfulnessCheck] = None) -> DistillationResult: ...
#   check=None resolves lazily to SpanContainmentFaithfulness() (acyclic-import-safe DEFAULT swap)

# src/newsletters/distill/conformance.py
def assert_conforms(backend, sources, *, check: Optional[FaithfulnessCheck] = None) -> DistillationResult: ...
#   inherits the same span-containment default; signature unchanged
```

## Task Commits
1. **RED** — failing span-containment gate tests — `3276597` (test)
2. **GREEN Task 1** — `SpanContainmentFaithfulness` + barrel export + `@runtime_checkable` — `4e806a6` (feat)
3. **GREEN Task 2** — seam default swapped to span-containment at `_enforce`/`assert_conforms` — `a51ceee` (feat)

_Note: `route_unfaithful_to_missing` (Task 3) landed inside the Task-1 GREEN `faithfulness.py` as one cohesive module; its 5 routing tests were in the single RED gate and pass under that GREEN commit. No separate Task-3 feat commit was needed._

## Gate Results (re-run independently via .venv/bin/python — ACTUAL output)
- `pytest tests/test_faithfulness_gate.py -q`: **21 passed**.
- `pytest tests/test_distill_socket.py -q`: **14 passed** (seam regression green: ManualBackend conformance, e2e round-trip, untraced rejection, injectable-seam all green).
- `pytest -q` (full suite, includes concurrent 03-02 tests): **85 passed, 1 xfailed** — zero regressions.
- `mypy src/newsletters/distill`: **Success: no issues found in 7 source files**.
- `lint-imports`: **Contracts: 1 kept, 0 broken** (AI-optional core intact — `faithfulness.py` imports only `..semantic` + stdlib `str.casefold`/`str.split`).
- `import sys, newsletters.distill; assert no AI module loaded`: **clean**.

## Deviations from Plan
1. **[Resolved decision — Option A]** The plan's "empty span ⇒ unfaithful" edge case was implemented in its reviewer-corrected scoped form: only a CONTENT-ADDRESSED non-containing span is unfaithful; an un-addressed/empty-span trace is the structural fallback. This is the authoritative resolution provided in the task brief, not a re-opening of the decision. `capture.py` was deliberately NOT modified.
2. **[Rule 3 — blocking import cycle]** `_enforce`'s default could not bind `SpanContainmentFaithfulness()` as a module-level default value, because `faithfulness.py` imports from `ports.py` — a module-level default would create an import cycle. Resolved by defaulting `check=None` and resolving the span-containment default lazily inside `_enforce` (and threading `check=None` through `assert_conforms`). Signatures and the injection contract are preserved.
3. **[Rule 2 — protocol conformance]** Made `FaithfulnessCheck` `@runtime_checkable` (parity with `DistillPort`) so a concrete checker satisfies the seam via `isinstance`. Additive, behavior-neutral for the existing checkers.

## Known Stubs
None.

## Threat Flags
None — the changes mitigate the planned threats: T-03F-01 (unfaithful claim posing as a fact — rejected at the default seam, routed to `missing[]`), T-03F-02 (per-backend bypass — enforced at the single socket seam), T-03F-03 (gate editorializing — pure read + verbatim relocation, proven by no-mutation assertions), T-03F-04 (silent drop — routed to `missing[]`, never silently removed). No new dependency (T-03F-SC).

## TDD Gate Compliance
- RED gate present: `test(03-03)` commit `3276597` (collection error — symbols absent — i.e. failing).
- GREEN gates present: `feat(03-03)` commits `4e806a6` and `a51ceee` after RED.
- REFACTOR: none required.

## Self-Check: PASSED
- FOUND: src/newsletters/distill/faithfulness.py
- FOUND: tests/test_faithfulness_gate.py
- FOUND commit: 3276597 (RED)
- FOUND commit: 4e806a6 (GREEN Task 1)
- FOUND commit: a51ceee (GREEN Task 2)

---
*Phase: 03-content-addressed-provenance-faithfulness*
*Completed: 2026-06-17*
