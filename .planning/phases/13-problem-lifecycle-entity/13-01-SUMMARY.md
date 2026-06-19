---
phase: 13-problem-lifecycle-entity
plan: 01
subsystem: core
tags: [pydantic, strenum, state-machine, problem-lifecycle, leaf-module, tdd]

# Dependency graph
requires:
  - phase: 02-typed-core (semantic spine)
    provides: "semantic.Source / semantic.Trace (the evidence-pointer types Problem references) and the human-gated Surface.approve/publish idiom mirrored by transition()"
provides:
  - "src/newsletters/problem.py — a NEW AI-free leaf module above Source"
  - "Problem entity: id/title/state/evidence(list[Trace], >=1)/log(list[TransitionEvent])/opened + source_ids property"
  - "ProblemState StrEnum: IDENTIFIED -> OWNED -> IN_PROGRESS -> RESOLVED -> VERIFIED"
  - "TransitionEvent(from_state, to_state, by, note, at) — the immutable per-move record"
  - "_LADDER allow-table: sequential forward + explicit re-open (Resolved/Verified -> In Progress)"
  - "transition(to, by, note='') — the SOLE state mutator; human-gated + ladder-enforced; never auto-advances"
  - "Problem/ProblemState/TransitionEvent exported first-class from the newsletters package"
affects: [phase-13-plan-02, phase-14-problem-portfolio, phase-14-problem-board]

# Tech tracking
tech-stack:
  added: []  # ZERO new dependency — stdlib enum.StrEnum/datetime + pydantic + in-repo semantic
  patterns:
    - "Human-gated, validator-enforced state transform (transition mirrors Surface.approve/publish — `not by` refusal)"
    - "Leaf-tier module above the spine: problem -> semantic -> {locators, templates}, acyclic, AI-free"
    - "Allow-table state machine via a stdlib dict[_LADDER] (no state-machine library)"
    - "Evidence reuse: Problem.evidence is list[Trace], the same evidence grammar as Claim.evidence"

key-files:
  created:
    - "src/newsletters/problem.py"
    - "tests/test_problem.py"
  modified:
    - "src/newsletters/__init__.py"

key-decisions:
  - "Reference constituent Sources by list[semantic.Trace] (content-addressed, drift-aware for free), not bare id strings"
  - "Ladder is sequential-forward PLUS explicit re-open (Resolved/Verified -> In Progress) — the legible record of a REAL lifecycle (research A1)"
  - "transition is the SOLE mutator; empty/whitespace actor refused; no public setter / advance() / auto path"
  - "ProblemState values kept disjoint from ReviewState (IN_PROGRESS='in_progress' vs IN_REVIEW='in_review'); the formal distinctness PROOF is Plan 02"
  - "Dogfood lives in the TEST file, not problem.py, keeping the module a pure type module"

patterns-established:
  - "Pattern 1: human-gated transition() with required `by` + _LADDER legal-move check, mirroring the no-auto-publish gate"
  - "Pattern 2: a new AI-free leaf tier above semantic (problem -> semantic), one-way + acyclic"

requirements-completed: [PROB-01]

# Metrics
duration: ~15min
completed: 2026-06-19
---

# Phase 13 Plan 01: Problem Lifecycle Entity Summary

**A first-class AI-free `Problem` entity above `Source` — typed `ProblemState` ladder
(Identified→Owned→In Progress→Resolved→Verified), evidence≥1 validator, and a single human-gated
`transition()` mutator with sequential-forward + explicit-re-open enforcement, proven end-to-end
by a dogfood Problem aggregating the real session-rev1 Source.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-06-19
- **Completed:** 2026-06-19
- **Tasks:** 2 (Task 1 TDD: RED + GREEN; Task 2 export/dogfood folded into Task 1's GREEN — see Deviations)
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- New leaf module `src/newsletters/problem.py` carrying `Problem`, `ProblemState`,
  `TransitionEvent`, the `_LADDER` allow-table, and `transition()` — imports only stdlib +
  pydantic + `.semantic` (`Source`, `Trace`); acyclic (`semantic.py` never imports `problem`).
- The lifecycle is human-gated and ladder-enforced: `transition(to, by, note)` refuses an empty
  actor and an illegal move, never auto-advances, and appends an immutable `TransitionEvent` per
  move. `evidence` is validated `≥1` (every Problem traces to evidence). `source_ids` gives the
  de-duplicated constituent Source ids (single-entity traceability; the cross-Problem query is
  Phase 14).
- `Problem`/`ProblemState`/`TransitionEvent` exported first-class from the `newsletters` package;
  `_LADDER` kept private.
- A dogfood Problem (the real "Locator union risked a circular import" build problem, aggregating
  the `session-rev1` Source) runs `Identified → Owned → In Progress → Resolved → Verified` with a
  peer actor on the VERIFIED step, and asserts its evidence stays content-addressed + non-stale —
  zero rendering.

## Task Commits

1. **Task 1 (RED): failing tests for the entity/ladder/transition** — `641d6d8` (test)
2. **Task 1 (GREEN): implement problem.py + package export** — `c2bccbc` (feat)

Task 2 (export + dogfood) required no additional source changes: the package export was a
blocking prerequisite for Task 1's package-level test imports, so it landed in `c2bccbc`, and the
dogfood end-to-end test was authored in the RED commit. Both Task 2 done-criteria
(`from newsletters import Problem, ProblemState, TransitionEvent` works + all three in `__all__`;
`test_dogfood_problem_end_to_end` passes; full suite green) are verified below.

**Plan metadata:** committed with STATE.md / ROADMAP.md / REQUIREMENTS.md in the final docs commit.

_TDD task: RED (`test`) → GREEN (`feat`); no REFACTOR commit was needed (GREEN was already clean)._

## Files Created/Modified
- `src/newsletters/problem.py` (created) — `Problem` / `ProblemState` / `TransitionEvent` /
  `_LADDER` / `transition()`. The AI-free leaf above the spine.
- `tests/test_problem.py` (created) — 7 tests: evidence≥1, ladder forward+reopen, illegal-move
  refusal, human-gated empty-actor refusal + sole-mutator check, source_ids de-dup, dogfood
  end-to-end, TransitionEvent typed-record.
- `src/newsletters/__init__.py` (modified) — `from .problem import Problem, ProblemState,
  TransitionEvent` + the three names added to `__all__` under a `# problem lifecycle (A2)` group.

## Decisions Made
- **Evidence as `list[Trace]`** (not bare ids): reuses the one evidence grammar
  (`Claim.evidence` is also `list[Trace]`) and gives content-addressing + drift-awareness for free.
- **Sequential + explicit re-open ladder** (research A1): a legible record of the *real* lifecycle
  must allow reopening a bottleneck (Resolved/Verified → In Progress); both re-open edges are still
  *recorded* human transitions. Every other backward/skip move is refused.
- **`transition` is the sole mutator**: required `by` (empty/whitespace refused), no public
  setter, no `advance()`/auto path — the human-gated guarantee, mirroring the no-auto-publish gate.
- **Whitespace-only actor also refused** (`not by.strip()`): a stricter reading of "explicit human
  actor" than the plan's literal "empty `by`" — a space-only actor is not a recorded human.
- **Dogfood kept in the test file**, so `problem.py` stays a pure type module.

## API delivered (for Plan 02 — the no-write-back boundary proof)

```python
class ProblemState(StrEnum):
    IDENTIFIED = "identified"; OWNED = "owned"; IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"; VERIFIED = "verified"

_LADDER: dict[ProblemState, set[ProblemState]] = {
    IDENTIFIED:  {OWNED},
    OWNED:       {IN_PROGRESS},
    IN_PROGRESS: {RESOLVED},
    RESOLVED:    {VERIFIED, IN_PROGRESS},   # re-open
    VERIFIED:    {IN_PROGRESS},             # regression re-open
}

class TransitionEvent(BaseModel):
    from_state: ProblemState; to_state: ProblemState; by: str
    note: str = ""; at: datetime = Field(default_factory=_utcnow)

class Problem(BaseModel):
    id: str; title: str
    state: ProblemState = ProblemState.IDENTIFIED
    evidence: list[Trace] = Field(default_factory=list)   # validated >=1
    log: list[TransitionEvent] = Field(default_factory=list)
    opened: datetime = Field(default_factory=_utcnow)

    @property
    def source_ids(self) -> list[str]: ...   # distinct, de-duplicated source ids

    def transition(self, to: ProblemState, by: str, note: str = "") -> "Problem":
        # SOLE mutator: raises on empty/whitespace `by`; raises on `to not in _LADDER[state]`;
        # appends TransitionEvent + sets state; never auto-advances.
```

For Plan 02: `problem.py` imports only `from .semantic import Source, Trace` (+ stdlib `enum`/
`datetime` + pydantic). `transition` is the only behavioral method; the public surface is
`{id, title, state, evidence, log, opened, source_ids, transition, ...pydantic}` — **no**
export/push/sync/write/jira/ado path exists. `semantic.py` does **not** import `problem` (one-way,
acyclic). The 2nd import-linter contract (`forbid-external-write-in-problem`) and the boundary
tests are Plan 02 — after which `lint-imports` becomes "2 kept, 0 broken" (it is "1 kept" here).

## Gate output (re-run independently — not trusted on a subagent's "green")

Via `.venv/bin/python`:

- `pytest tests/test_problem.py -q` → **7 passed** in 0.02s.
- `pytest -q` (full) → **566 passed, 1 xfailed** (baseline was 559 passed, 1 xfailed; +7 new). Green.
- `mypy src/newsletters` → **Found 9 errors in 2 files** (capture.py + dogfood.py) — the exact
  pre-existing baseline; **0 errors in problem.py** (`mypy src/newsletters/problem.py` → "Success:
  no issues found"). 36 source files checked (was 35).
- `lint-imports` → **Contracts: 1 kept, 0 broken** (the 2nd contract is added in Plan 02, as planned).
- Fresh import (problem alone): `import newsletters.problem` → exit 0.
- Acyclic source check: `semantic.py` references `problem` → **False** (one-way edge confirmed).
- Package export: `from newsletters import Problem, ProblemState, TransitionEvent` → works
  (`ProblemState.IDENTIFIED.value == "identified"`); all three in `__all__`; `_LADDER` not exported.

### Human-gated proof
`Problem(...).transition(ProblemState.OWNED, by="")` and `by="   "` each raise `ValueError`;
state stays `IDENTIFIED` and the log stays empty (`test_transition_human_gated`). The public
surface contains `transition` and contains no `advance`/`auto_advance`/`set_state`/`publish`/
`approve` — `transition` is the sole mutator. The dogfood's VERIFIED step is recorded by a peer
actor ("JJ Airuoyo"), echoing the peer-review ethos without reusing the gate API.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Package export landed in the Task-1 GREEN commit**
- **Found during:** Task 1 (GREEN) — the tests import `from newsletters import Problem,
  ProblemState, TransitionEvent`, so the package-level export is a hard prerequisite for the
  Task-1 tests to even collect (the RED step failed with `ImportError: cannot import name
  'Problem'`).
- **Issue:** The plan scheduled the `__init__.py` export as Task 2, but Task 1's verify command
  (`pytest tests/test_problem.py`) cannot run without it.
- **Fix:** Added `from .problem import ...` + the three `__all__` entries in the Task-1 GREEN
  commit (`c2bccbc`). No code remained for a separate Task-2 source commit; both Task-2
  done-criteria were then verified, not re-implemented.
- **Files modified:** `src/newsletters/__init__.py`
- **Verification:** `from newsletters import Problem, ProblemState, TransitionEvent` works; all
  three in `__all__`; `_LADDER` private; `test_dogfood_problem_end_to_end` passes; full suite green.
- **Committed in:** `c2bccbc` (Task 1 GREEN commit)

**2. [Rule 2 - Missing Critical] Whitespace-only actor refused, not just empty string**
- **Found during:** Task 1 (GREEN)
- **Issue:** The plan said "raises on empty/whitespace `by`". A literal `if not by:` would let a
  space-only actor (`"   "`) through — that is not a recorded human, weakening the human-gate.
- **Fix:** Guard is `if not by or not by.strip():`. Added a `by="   "` assertion to
  `test_transition_human_gated`.
- **Files modified:** `src/newsletters/problem.py`, `tests/test_problem.py`
- **Verification:** `test_transition_human_gated` asserts both `""` and `"   "` raise; state
  unchanged.
- **Committed in:** `641d6d8` (test) / `c2bccbc` (impl)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing-critical).
**Impact on plan:** No scope creep. The export was unavoidable for Task-1 collection; the
whitespace guard strengthens the human-gate invariant. The plan's two-task structure is preserved
in intent — all done-criteria for both tasks are met and verified.

## Scope guard (Phase-14 leak check)
No `list[Problem]` query / aggregation / portfolio container / grouping taxonomy was built. No
`render.py` / `site.py` / `templates.py` was touched. Zero new dependency; no AI; no external
call. `source_ids` is single-entity traceability only (PROB-04 prep), not a cross-Problem query.

## Known Stubs
None. The entity is fully wired and exercised end-to-end by the dogfood test; no placeholder data
or unwired surface exists. (Rendering/aggregation is deliberately Phase 14, not a stub.)

## Issues Encountered
None. The one collection-order subtlety (`import newsletters.semantic` runs the package `__init__`,
which now imports `problem`, so a naive `sys.modules` check trips) was diagnosed as an artifact of
package-init order, not a cycle — confirmed acyclic by a source-level check that `semantic.py`
contains no `problem` import.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- **Plan 02 (Wave 2)** can proceed: it adds the `forbid-external-write-in-problem` import-linter
  contract + the no-write-back / spine-boundary / terminology-distinctness boundary tests on the
  API delivered here. After it, `lint-imports` becomes "2 kept, 0 broken" — any test asserting
  "1 kept" must be updated.
- **Phase 14** has its entity foundation: `Problem` + `source_ids` are ready for the queryable
  portfolio (PROB-02) and the board surface (PROB-04).

## Self-Check: PASSED
- FOUND: src/newsletters/problem.py
- FOUND: tests/test_problem.py
- FOUND: .planning/phases/13-problem-lifecycle-entity/13-01-SUMMARY.md
- FOUND commit 641d6d8 (test RED)
- FOUND commit c2bccbc (feat GREEN + export)
- FOUND export edge `from .problem import` in __init__.py

---
*Phase: 13-problem-lifecycle-entity*
*Completed: 2026-06-19*
