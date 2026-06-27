---
phase: 13-problem-lifecycle-entity
plan: 02
subsystem: core
tags: [import-linter, boundary-proof, sys-modules-guard, terminology-guard, no-write-back, prob-03]

# Dependency graph
requires:
  - phase: 13-problem-lifecycle-entity (plan 01)
    provides: "src/newsletters/problem.py — Problem/ProblemState/TransitionEvent/transition (the entity under proof) + the package export"
  - phase: 02-typed-core (semantic spine)
    provides: "semantic.Source.content_hash (the spine-unchanged proof), semantic.ReviewState + Surface (the terminology-distinctness proof)"
provides:
  - ".importlinter — second forbidden contract `forbid-external-write-in-problem` (the static half of the PROB-03 no-write-back boundary)"
  - "tests/test_problem_boundary.py — the three no-write-back sub-proofs (runtime import guard + API allow-list + spine-unchanged) + the human-gated standing copy + the terminology-distinctness proof"
  - "lint-imports now reports 2 kept, 0 broken (exit 0)"
affects: [phase-14-problem-portfolio, phase-14-problem-board]

# Tech tracking
tech-stack:
  added: []  # ZERO new dependency — .importlinter is config; import-linter already in [dev]
  patterns:
    - "Two-layer no-write-back boundary mirroring AI-optional core: a static import-linter forbidden contract PLUS a runtime sys.modules subprocess guard"
    - "Baseline-DELTA runtime guard: import the spine first as baseline, assert the layer above introduces ZERO new forbidden modules (isolates the module's OWN footprint from framework noise)"
    - "API allow-list test that subtracts the pydantic BaseModel surface so framework hooks (model_post_init) do not false-positive — polices the entity's OWN declared API"
    - "Terminology-distinctness proof: distinct enum types + disjoint member value AND name sets + reserved-verb non-collision"

key-files:
  created:
    - "tests/test_problem_boundary.py"
  modified:
    - ".importlinter"

key-decisions:
  - "Runtime guard uses a baseline-delta (spine-first), not raw sys.modules membership: pydantic itself drags socket/subprocess/http/urllib into sys.modules, so a raw check fails on framework noise; the delta isolates problem.py's own marginal footprint while keeping full teeth for jira/ado/requests/ftplib/smtplib (absent from the baseline)"
  - "API allow-list subtracts the pydantic BaseModel surface so model_post_init (a pydantic lifecycle hook matching the 'post' substring) does not false-positive; the list then polices exactly Problem's own surface {source_ids, transition}"
  - "No test edit for the lint-imports count was needed — the existing test_import_linter_contract_holds asserts EXIT 0 only, never a literal '1 kept' (verified in the live repo, as the plan predicted)"

requirements-completed: [PROB-03, PROB-01]

# Metrics
duration: ~5min
completed: 2026-06-19
---

# Phase 13 Plan 02: Problem Lifecycle Boundary Proof Summary

**The PROB-03 legibility-layer-not-a-tracker guarantee made durable: a second import-linter
contract (`forbid-external-write-in-problem`, the static no-write-back edge) plus
`tests/test_problem_boundary.py` carrying the three no-write-back sub-proofs (runtime sys.modules
guard, API allow-list, spine-unchanged), the human-gated standing copy, and the
terminology-distinctness proof — `lint-imports` now reports 2 kept, 0 broken.** This is the LAST
wave of the cut.

## Performance

- **Duration:** ~5 min
- **Completed:** 2026-06-19
- **Tasks:** 2 (Task 1: import-linter contract; Task 2: the boundary + distinctness test file)
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

### Task 1 — the static no-write-back edge (L5a static)
Added a SECOND `forbidden` contract to `.importlinter`,
`[importlinter:contract:forbid-external-write-in-problem]`, forbidding `newsletters.problem` from
statically importing `socket / http / urllib / ftplib / smtplib / subprocess / requests`. Mirrors
the existing `forbid-ai-in-core` shape and reuses the file-scope `include_external_packages = True`.
`lint-imports` now reports **"Contracts: 2 kept, 0 broken"** (exit 0), both contracts listed KEPT.

### Task 2 — the boundary + distinctness proofs (six tests, all MANDATORY gates)
Created `tests/test_problem_boundary.py` mirroring the `test_ai_optional.py` idioms:

1. **`test_problem_loads_no_external_module` (L5a runtime)** — a fresh `PYDANTIC_DISABLE_PLUGINS=true`
   subprocess imports the spine `newsletters.semantic` as a baseline, then imports
   `newsletters.problem`, and asserts it introduces **zero** new forbidden module over that
   baseline. The runtime complement to the Task-1 static contract.
2. **`test_problem_api_has_no_write_back_method` (L5b API allow-list)** — `Problem`'s own public
   surface (`{source_ids, transition}`, with the pydantic BaseModel surface subtracted) contains
   NO name matching `export/push/sync/write/send/post/upload/save/jira/ado/devops/remote/publish`;
   `transition` IS present; no `set_state/advance/auto_advance/publish/approve` foreign mutator.
3. **`test_spine_unchanged_by_problem` (L5c, two assertions)** — (i) a Source's `content_hash()` is
   byte-identical (and its fields unchanged) across a FULL `IDENTIFIED → OWNED → IN_PROGRESS →
   RESOLVED → VERIFIED` transition sequence; (ii) `semantic.py` contains no `import` line referencing
   `problem` (the dependency stays one-way `problem → semantic`).
4. **`test_transition_human_gated_empty_actor_raises` (L4 reinforced)** — `transition` with `""`,
   `"   "`, `"\t\n"` raises `ValueError`; state stays `IDENTIFIED` and the log stays empty — no
   auto-advance path.
5. **`test_problemstate_distinct_from_reviewstate` (L6)** — `ProblemState is not ReviewState`,
   neither subclasses the other, member VALUE sets and NAME sets are disjoint; explicit adjacency
   assertion `IN_PROGRESS="in_progress" != IN_REVIEW="in_review"`.
6. **`test_lifecycle_verb_collides_with_no_axis_verb` (L6)** — `transition` is not among the
   review-gate/fan-out/promote verbs; `Surface` has no `transition` attribute; `Problem` has no
   gate verb (`publish/approve/open_pull_request`).

## Task Commits

1. **Task 1 (feat): forbid-external-write-in-problem import-linter contract** — `fa55760` (pushed)
2. **Task 2 (test): boundary + terminology-distinctness gates** — `b265476` (pushed)

Both tasks were committed atomically and pushed to `claude/youthful-fermi-dly6mi` immediately after
each. Plan metadata (this SUMMARY + STATE/ROADMAP/REQUIREMENTS) lands in the final docs commit.

## Files Created/Modified
- `.importlinter` (modified) — added the second `forbidden` contract
  `forbid-external-write-in-problem` with a teaching comment naming its runtime complement.
- `tests/test_problem_boundary.py` (created) — six MANDATORY gates: the three no-write-back
  sub-proofs + the human-gated standing copy + the two terminology-distinctness tests.

## The boundary proofs (what is now durable)

| Proof | Layer | Mechanism |
|-------|-------|-----------|
| No external import edge from `problem` | static | `.importlinter` contract `forbid-external-write-in-problem` (KEPT) |
| No external module reachable at runtime | runtime | spine-baseline-delta `sys.modules` subprocess guard — introduces 0 |
| No write-back/export path on the API | API | allow-list over Problem's own surface (`{source_ids, transition}`) |
| Spine unchanged | data | `Source.content_hash` byte-identical across a full transition sequence |
| Dependency one-way | structure | `semantic.py` never imports `problem` (source-text check) |
| Human-gated, never auto-mutated | invariant | empty/whitespace actor raises; state + log unchanged |
| Three axes distinct | terminology | distinct types, disjoint value+name sets, reserved-verb non-collision |

## Gate output (re-run independently — not trusted on a subagent's "green")

Via `.venv/bin/python`:

- `pytest tests/test_problem_boundary.py -q` → **6 passed** in 0.46s.
- `pytest -q` (full) → **572 passed, 1 xfailed** (baseline 566 passed, 1 xfailed; +6 new). Green.
- `.venv/bin/lint-imports` → **"Contracts: 2 kept, 0 broken"**, exit 0 — both
  `forbid-ai-in-core` and `forbid-external-write-in-problem` listed KEPT (analyzed 59 files, 214
  dependencies).
- `pytest tests/test_ai_optional.py -q` → **15 passed, 1 xfailed** — the existing
  `test_import_linter_contract_holds` still green with 2 contracts (it asserts exit 0, not a count;
  no edit needed, as the plan predicted).
- `mypy src/newsletters` → **9 errors in 2 files** (capture.py + dogfood.py) — the exact pre-existing
  baseline; zero new errors (the new gate lives in `tests/`, not `src/`).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Runtime guard rewritten as a baseline-DELTA, not a raw sys.modules check**
- **Found during:** Task 2
- **Issue:** The plan's literal "import newsletters.problem then assert none of FORBIDDEN_MODULES is
  in sys.modules" (mirroring test_core_import_loads_no_ai_module) FAILS — pydantic itself pulls
  `socket`/`subprocess` (and its deps pull `http`/`urllib`) into `sys.modules` on import, so the
  raw check trips on framework noise, not on anything problem.py reaches. (Diagnosed live: a
  pristine interpreter is clean; `import pydantic` already adds `socket`/`subprocess`; the AI-test
  precedent works only because its AI modules are genuinely never imported by anything in the spine.)
- **Fix:** Import the spine `newsletters.semantic` FIRST as a baseline, then import
  `newsletters.problem` and assert it introduces ZERO new forbidden module over that baseline. This
  isolates problem.py's OWN marginal footprint (the real claim) while keeping full teeth for the
  modules absent from the baseline (`jira`/`ado`/`requests`/`ftplib`/`smtplib`). The static
  no-direct-EDGE guarantee remains the import-linter contract from Task 1.
- **Files modified:** `tests/test_problem_boundary.py`
- **Verification:** `introduced by problem: []` over the spine baseline; test passes.
- **Committed in:** `b265476`

**2. [Rule 1 - Bug] API allow-list subtracts the pydantic BaseModel surface**
- **Found during:** Task 2
- **Issue:** Enumerating `{n for n in dir(Problem) if not n.startswith("_")}` includes pydantic's
  `model_post_init` — a BaseModel lifecycle hook whose name matches the `post` write-back substring,
  producing a false positive (not an HTTP POST / write-back path).
- **Fix:** Subtract the pydantic `BaseModel` public surface before matching, so the allow-list
  polices exactly Problem's OWN declared API (`{source_ids, transition}`). Teeth intact: a future
  `export_to_jira` on Problem lands in this set and trips.
- **Files modified:** `tests/test_problem_boundary.py`
- **Verification:** allow-list now sees `{source_ids, transition}`; `transition` present; no
  write-back name; test passes.
- **Committed in:** `b265476`

---

**Total deviations:** 2 auto-fixed (both Rule 1 — the planned test idiom was correct in shape but
over-claimed against framework noise; both fixes make the proofs TRUE and keep their teeth). No
scope change; no new dependency; AI-free.

## Scope guard (Phase-14 leak check)
Tests + `.importlinter` only. No `render.py`/`site.py`/`templates.py` touched; no `list[Problem]`
aggregation/portfolio/board built; no new dependency; no AI; the subprocess guard imports local
modules only (no external call).

## Known Stubs
None. Every gate is a real, executing proof against the live `problem.py` API and the live
`semantic.py` spine.

## Threat coverage (from the plan's threat register)
- **T-13-04** (out-of-boundary write) — mitigated: static contract + runtime delta guard + API
  allow-list.
- **T-13-05** (spine tampering) — mitigated: content_hash byte-identical across a full sequence;
  one-way dependency proven.
- **T-13-06** (axis collision) — mitigated: distinct types, disjoint value+name sets, reserved-verb
  non-collision.
- **T-13-01** (human-gated copy) — mitigated: empty-actor-raises standing test in the boundary file.
- **T-13-SC** (supply chain) — N/A: zero installs; `.importlinter` is config.

## Self-Check: PASSED
- FOUND: tests/test_problem_boundary.py
- FOUND: .importlinter (contains `forbid-external-write-in-problem`)
- FOUND: .planning/phases/13-problem-lifecycle-entity/13-02-SUMMARY.md
- FOUND commit fa55760 (feat — import-linter contract)
- FOUND commit b265476 (test — boundary + distinctness gates)

---
*Phase: 13-problem-lifecycle-entity*
*Completed: 2026-06-19*
