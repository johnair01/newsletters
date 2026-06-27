---
phase: 13-problem-lifecycle-entity
verified: 2026-06-19T07:05:00Z
status: passed
score: 3/3 success criteria verified (WARNING resolved 2026-06-19)
overrides_applied: 0
resolution: >-
  The human-gate WARNING (a default-mutable pydantic model let `p.state = ...` bypass the actor
  check/ladder/log) was FIXED in commit 89e0947: a `__setattr__` guard refuses direct assignment to
  `state`/`log` unless `transition()` is actively applying a recorded, ladder-legal, human-gated move
  (a private `_via_transition` gate). In-place `transition`, round-trip serialization, and construction
  all still work; direct `p.state=`/`p.log=` now raise `AttributeError`. Regression test
  `test_state_and_log_cannot_be_set_directly_outside_transition` added. 573 passed; lint-imports 2 kept/
  0 broken; mypy clean on problem.py. "transition is the SOLE mutator" is now literally true.
gaps:
  - truth: "transition() is the SOLE mutator of Problem.state (human-gated, never bypassable)"
    status: partial
    reason: >-
      The no-write-back crux is airtight and there is no AUTO-mutation path, so the
      phase goal is met. BUT `Problem` is a default-mutable pydantic model (no
      `model_config` with `frozen=True` or `validate_assignment=True`), so direct
      attribute assignment `prob.state = ProblemState.VERIFIED` succeeds — bypassing
      the actor check, the ladder validation, AND the transition log (log stays []).
      This contradicts the explicit code claim in problem.py:162 ("this method is the
      only way state changes") and weakens the human-gated guarantee's airtightness.
      It does NOT create any external/write-back path (the hard PROB-03 constraint
      holds) and is not an automatic mutation, so it is a WARNING, not a blocker.
    artifacts:
      - path: "src/newsletters/problem.py"
        issue: >-
          class Problem(BaseModel) has no model_config; defaults to mutable +
          no validate_assignment, so `p.state = X` bypasses transition() entirely.
    missing:
      - >-
        Make the human gate airtight: either `model_config = ConfigDict(frozen=True)`
        (force a copy-on-transition pattern) OR `validate_assignment=True` + a
        field validator that refuses direct `state` reassignment outside transition(),
        OR add a boundary test that pins the chosen guarantee. Soften the
        problem.py:162 docstring claim if direct assignment is to remain permitted.
human_verification:
  - test: >-
      Decide whether the direct-attribute-assignment bypass of the human gate
      (`prob.state = ProblemState.VERIFIED` succeeds with an empty log) is
      acceptable for a legibility layer, or whether the field must be frozen /
      assignment-validated to make "transition is the sole mutator" literally true.
    expected: >-
      Either accept (legibility layer trusts the operator; transition is the
      sanctioned path and direct field-poking is out of scope) and soften the
      docstring claim, or harden the model so the gate cannot be bypassed.
    why_human: >-
      This is a design-intent judgment about how airtight the human gate must be
      for a "record, not a tracker" entity — not a programmatically decidable
      pass/fail. The hard constraint (no write-back) is independently verified PASS.
---

# Phase 13: Problem Lifecycle Entity — Verification Report

**Phase Goal:** Add a first-class `Problem` entity ABOVE `Source` that consolidates the scattered
`problem → owned → solution → verified` lifecycle into one legible, evidence-traced home — a
LEGIBILITY LAYER, not a second tracker. Problem-solving stays external/operator-owned.
**Verified:** 2026-06-19T07:05:00Z
**Status:** human_needed (3/3 criteria substantively achieved; one WARNING on gate airtightness needs a human decision)
**Re-verification:** No — initial verification
**Branch:** claude/youthful-fermi-dly6mi (no source modified, no branch switched)

## Goal Achievement

### Observable Truths (the 3 ROADMAP Success Criteria)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Problem aggregates ≥1 traced Source + carries its own typed lifecycle ladder (Identified→Owned→In Progress→Resolved→Verified) | ✓ VERIFIED | Live probe + `problem.py:65-91,113-180`; ≥1 enforced; ladder typed; transition records from→to/actor |
| 2 | Problem ladder provably DISTINCT in code from the review gate (Draft→In Review→Published) + fan-out chain — no shared/overloaded "promotion" term | ✓ VERIFIED | Distinct types, disjoint values, `transition` verb unique to axis-3 (live probe + greps below) |
| 3 | Transitions human-gated, never auto-mutated; NO write-back to any external system; semantic.py spine boundary preserved, proven by test | ✓ VERIFIED (crux airtight) ⚠️ WARNING (gate bypassable by direct field assignment) | lint-imports 2 kept/0 broken; adversarial grep clean; spine byte-identical; BUT default-mutable model allows `p.state = X` bypass |

**Score:** 3/3 success criteria substantively verified. The hard PROB-03 constraint (no write-back)
is airtight. One WARNING on Criterion 3's "sole mutator" airtightness routed to human decision.

---

## Criterion 1 — Aggregation + typed ladder — PASS

**Live probe result:**
```
state start: identified | source_ids: ['session-rev1'] | len(evidence)>=1: True
after 2 legal transitions: in_progress | log: [('identified','owned','Claude'),('owned','in_progress','Claude')]
>=1 source enforced: empty evidence REFUSED
```

- `ProblemState` is a typed `StrEnum`: IDENTIFIED → OWNED → IN_PROGRESS → RESOLVED → VERIFIED
  (`problem.py:65-78`).
- `Problem.evidence: list[Trace]` with a `field_validator` that refuses empty evidence
  (`problem.py:129-139`) — ≥1 traced Source enforced **at construction** (probe: empty REFUSED).
- `transition()` advances legally and records `TransitionEvent(from_state, to_state, by, note, at)`
  on `log` (`problem.py:94-105, 176-179`) — from→to + actor captured (probe confirms).
- `source_ids` property resolves de-duplicated constituent Source ids (`problem.py:141-148`; probe
  returns `['session-rev1']`).
- Ladder enforcement: forward-one-rung + explicit re-open (Resolved/Verified → In Progress) only;
  skips and arbitrary backward jumps raise (`_LADDER` table `problem.py:85-91`; covered by
  `test_transition_refuses_illegal_move`).
- Typed end to end (Pydantic) — mypy reports **zero** errors in problem.py.

## Criterion 2 — Terminology distinctness (adversarial) — PASS

**Live probe:**
```
ProblemState values: ['identified','in_progress','owned','resolved','verified']
ReviewState values : ['draft','in_review','published']
shared values: NONE (disjoint)
distinct types: True
```

- `ProblemState is not ReviewState`; neither subclasses the other (probe + `test_problemstate_distinct_from_reviewstate`).
- Member **values** disjoint; member **names** disjoint; the close pair is explicitly different:
  `IN_PROGRESS="in_progress"` vs `IN_REVIEW="in_review"` (`problem.py:76` vs `semantic.py:252`).
- Verb axis: `grep "transition"` across `semantic.py`, `promote.py`, `render.py` → **no match**.
  The lifecycle verb `transition` is owned by axis-3 alone. The within-truth promotion verbs
  (`promote_claim_to_kpi`/`promote_report_to_article`) and the gate verb (`publish`/`approve`) do
  not appear on `Problem`; `transition` does not appear on `Surface`
  (`test_lifecycle_verb_collides_with_no_axis_verb`).
- **No collision found across all three axes.**

## Criterion 3 — THE CRUX (legibility, not a tracker) — PASS on the hard constraint, WARNING on airtightness

### (a) NO WRITE-BACK — AIRTIGHT (PASS)

- **Static (import-linter):** `.importlinter:50-63` defines `forbid-external-write-in-problem`
  forbidding socket/http/urllib/ftplib/smtplib/subprocess/requests from `newsletters.problem`.
  **`lint-imports` actual output: `Contracts: 2 kept, 0 broken`** (both this contract and the
  AI-in-core contract KEPT). Matches the RESEARCH note that the count moves to "2 kept".
- **Runtime:** `test_problem_loads_no_external_module` (subprocess baseline-delta) PASSES — importing
  `newsletters.problem` introduces zero forbidden modules over the spine baseline; the real tracker
  SDKs (jira/ado) and requests/ftplib/smtplib are absent from baseline, so the delta keeps teeth.
- **Adversarial grep of problem.py** for `socket|http|urllib|requests|subprocess|jira|ado|devops|
  export|push|sync|send|post|upload|remote|webhook|api_key|os.system|open(` → **only hit is the
  word "line" inside a comment**; no external/write token in any code path. The public API is
  `transition` + `source_ids` (read-only) only.
- **Live full-sequence probe:** ran IDENTIFIED→OWNED→IN_PROGRESS→RESOLVED→VERIFIED;
  `Source.content_hash()` **byte-identical** before/after, transcript unchanged. Problem mutates
  **nothing external and no Source**. (`test_spine_unchanged_by_problem` confirms in-suite.)
- **API allow-list:** `test_problem_api_has_no_write_back_method` PASSES — no public name contains
  export/push/sync/write/send/post/upload/save/jira/ado/devops/remote/publish.

  **Judgment: the no-write-back boundary is airtight.** There is no method, no import, and no field
  that carries external state out. This is the single most important invariant of the phase and it
  is independently proven (static + runtime + adversarial + live byte-equality).

### (b) HUMAN-GATED — PASS (auto-mutation) with a WARNING (direct-assignment bypass)

- Empty/whitespace actor refused, state + log unchanged (`problem.py:164-168`;
  `test_transition_human_gated`, `test_transition_human_gated_empty_actor_raises`). VERIFIED.
- **No AUTO-advance path:** no scheduler, no code path mutates state without an explicit `by`.
  `self.state = to` occurs ONLY at `problem.py:179` inside `transition`. VERIFIED.
- **⚠️ WARNING — the gate is bypassable by direct attribute assignment.** `Problem(BaseModel)` has
  no `model_config` (no `frozen=True`, no `validate_assignment=True`), so pydantic's default
  mutability allows:
  ```
  p.state = ProblemState.VERIFIED   # succeeds; log stays []  (live probe confirmed)
  ```
  This bypasses the actor check, the ladder validation, and the log. It contradicts the explicit
  code claim at `problem.py:162` ("this method is the only way state changes") and the
  docstring/test framing that `transition` is the SOLE mutator. It is **not** an auto-mutation and
  creates **no** external path — so the phase GOAL holds — but the human gate is not literally
  airtight. The boundary tests assert no `set_state`/`advance` *method*, but none freeze the field.
  Routed to human decision (acceptable for a legibility layer vs. harden the model).

### (c) SPINE PRESERVED — PASS

- `semantic.py` does **not** import `problem` (the only `problem` tokens at `semantic.py:22,599` are
  docstring prose: "problem-solving step is external"). Dependency is strictly one-way
  `problem → semantic` (`test_spine_unchanged_by_problem` part ii).
- Source/Distillation/Surface and the review gate are **unchanged by Phase 13** — git scope below.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/problem.py` | Problem entity + ProblemState ladder + human-gated transition | ✓ VERIFIED | 180 lines, substantive, imports only stdlib+pydantic+`.semantic`; one WARNING (default-mutable model) |
| `src/newsletters/__init__.py` | Export Problem/ProblemState/TransitionEvent | ✓ VERIFIED | diff is +3 import + entry in `__all__`, nothing else |
| `.importlinter` | `forbid-external-write-in-problem` contract | ✓ VERIFIED | contract present `:50-63`; lint-imports 2 kept/0 broken |
| `tests/test_problem.py` | Entity/ladder/human-gate/dogfood tests | ✓ VERIFIED | 9 tests; real dogfood Problem aggregates `session-rev1` (not a stub) |
| `tests/test_problem_boundary.py` | No-write-back + terminology + spine proofs | ✓ VERIFIED | 4 boundary/terminology tests; all PASS |
| Dogfood Problem | Real aggregation of a traced Source, end-to-end | ✓ VERIFIED | `test_dogfood_problem_end_to_end`: real session-rev1 Source, non-stale content-addressed Trace, full ladder |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| problem.py | semantic (Source/Trace) | `from .semantic import Source, Trace` | ✓ WIRED | the only non-stdlib/pydantic import; acyclic |
| __init__.py | problem.py | `from .problem import ...` + `__all__` | ✓ WIRED | exports reachable as `newsletters.Problem` (live probe) |
| .importlinter | newsletters.problem | `source_modules = newsletters.problem` | ✓ WIRED | lint-imports enforces it (KEPT) |
| semantic.py | problem | (must NOT exist) | ✓ ABSENT | one-way edge preserved |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Problem aggregates traced Source + ladder | live `newsletters` probe | start identified, advances, ≥1 enforced | ✓ PASS |
| ProblemState ≠ ReviewState | live enum probe | disjoint values, distinct types | ✓ PASS |
| Full transition leaves Source byte-identical | live probe | content_hash identical | ✓ PASS |
| Direct field assignment bypasses gate | live probe | `p.state=VERIFIED` succeeded, log [] | ✗ FAIL (WARNING) |
| Named entity + boundary tests | `pytest tests/test_problem*.py -q` | 13 passed | ✓ PASS |

### Gate Output (actual)

| Gate | Command | Result | Status |
|------|---------|--------|--------|
| Tests | `.venv/bin/python -m pytest -q` | **572 passed, 1 xfailed in 12.69s** | ✓ PASS |
| Types | `.venv/bin/mypy src/newsletters` | **9 errors, all pre-existing in capture.py/dogfood.py; ZERO in problem.py** | ✓ PASS (no new) |
| Imports | `.venv/bin/lint-imports` | **2 kept, 0 broken** | ✓ PASS |

The 9 mypy errors are in `capture.py`/`dogfood.py`, neither touched by Phase 13 (git-confirmed) —
pre-existing, matching the expected ~9.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PROB-01 | 13-01 | First-class Problem above Source, ≥1 traced, typed ladder distinct from gate+fan-out | ✓ SATISFIED | Criteria 1+2 |
| PROB-03 | 13-02 | Legibility layer, no write-back, human-gated never auto-mutated, spine preserved + tested | ✓ SATISFIED (hard constraint airtight; WARNING on gate airtightness) | Criterion 3 |
| PROB-02 | (Phase 14) | Queryable portfolio | ✓ CORRECTLY DEFERRED | no `list[Problem]`/portfolio/grouping in problem.py |
| PROB-04 | (Phase 14) | Board surface | ✓ CORRECTLY DEFERRED | no render/site/templates touched |

### Scope (Phase-14 leak check)

- Git diff `365d5c7..HEAD`: only `.importlinter`, planning docs, `__init__.py` (+3), `problem.py`
  (new), `test_problem.py`, `test_problem_boundary.py`. **No render.py/site.py/templates.py/semantic.py
  source touched.**
- No `list[Problem]`/portfolio/Portfolio/group_by/grouping in problem.py. **No Phase-14 leak.**

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| problem.py | 113 | `class Problem(BaseModel)` with no `model_config` (default-mutable) | ⚠️ Warning | Direct `p.state = X` bypasses the human gate, ladder, and log — contradicts the "sole mutator" claim at :162 |

No TBD/FIXME/XXX/TODO debt markers in any Phase-13 file. No hollow stubs — `return null/[]/{}` patterns
absent; the dogfood Problem is a genuine aggregation of a real, non-stale Source.

### Human Verification Required

**1. Is the direct-assignment bypass of the human gate acceptable for a legibility layer?**
- **Test:** `prob.state = ProblemState.VERIFIED` succeeds with an empty `log`, skipping the actor
  check and ladder validation (live probe confirmed; model is default-mutable).
- **Expected:** Either (a) accept — a legibility layer trusts the operator; `transition` is the
  sanctioned, recorded path and field-poking is out of scope — and soften the `problem.py:162`
  docstring claim; or (b) harden the model (`frozen=True` or `validate_assignment=True` + a `state`
  field validator) and add a boundary test so "transition is the sole mutator" is literally true.
- **Why human:** A design-intent call about how airtight the human gate must be for a "record, not
  a tracker." The hard PROB-03 constraint (no write-back) is independently PASS regardless.

### Gaps Summary

The phase goal is achieved: a first-class, typed `Problem` entity sits above `Source`, aggregates
≥1 traced Source, carries a lifecycle ladder provably distinct (type, values, names, verb) from the
review gate and fan-out, and — the crux — has **no write-back path to any external system**, proven
static + runtime + adversarial-grep + live byte-equality (lint-imports 2 kept/0 broken; Source
content_hash byte-identical across a full transition sequence). The spine is unchanged and the edge
is one-way. PROB-02/04 are correctly deferred to Phase 14; no leak.

The one gap is an **airtightness WARNING, not a goal failure**: because `Problem` is a default-mutable
pydantic model, `transition()` is the only *sanctioned* mutator but not the only *possible* one —
direct attribute assignment bypasses the human gate, the ladder, and the log, contradicting the
explicit "this method is the only way state changes" claim in the code. This does not open any
external/write-back path (the hard constraint holds) and is not an auto-mutation, so the phase goal
stands; but the human-gated guarantee is not literally airtight. Routed to a human decision: accept
(and soften the claim) or harden the model.

---

_Verified: 2026-06-19T07:05:00Z_
_Verifier: Claude (gsd-verifier)_
