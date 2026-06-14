---
phase: 1
reviewers: [independent-claude-opus]
reviewed_at: 2026-06-14T17:52:32Z
plans_reviewed: [01-01-PLAN.md, 01-02-PLAN.md]
note: "Cross-vendor CLIs unavailable in this environment; this is a fresh independent-context Claude (opus) review, not multi-vendor."
---

# Cross-AI Plan Review — Phase 1

## Independent Review (Claude opus, fresh context)

### Summary

These are strong, unusually disciplined plans: scope is honest (contract-only, no premature
adapters/AI), every SOCK requirement maps to concrete tasks with `<read_first>` and
`<acceptance_criteria>`, the D-05 two-honesties distinction is preserved (separate `Coverage.unextracted[]`
model vs reused `Distillation.missing[]`), and both hard rules (no-auto-publish, AI-optional core)
are proven by named executable tests in Plan 02. The analog claims in the plans check out against the
live spine: `templates.py:165-184` is a real registry exemplar, `semantic.py:273-287` is a real
discriminated-union (`Block`), `capture_session()` builds `Trace(source_id=..., locator=<str>)` exactly
as claimed, and `synthesize()` is the `NotImplementedError` stub the plan leaves untouched. **However,
there is one HIGH-severity defect that will break execution as written:** the planned import wiring
(`semantic.py` importing from `.distill.locators` while `distill/__init__.py` eager-imports `.ports`
which imports `..semantic`) is a genuine circular import — I reproduced it deterministically. The
plan asserts this arrangement is "acyclic"; it is not. That must be resolved before execution or the
Rev1 regression tripwire (and `import newsletters` itself) will fail.

### Strengths

- **Scope is exactly right.** Builds the contract + registry + ManualBackend + Coverage/Locator +
  conformance, and explicitly stubs (commented-only) the adapter/interview `Locator` variants. No
  over-engineering (no entry-point machinery, no `core/` re-layout, no span-containment — all correctly
  deferred). ManualBackend is a thin wrapper over the existing tested `capture_session()`, not a
  reimplementation — correctly resisting the "stub the backend" failure mode.
- **D-05 honesty distinction is real, not merged.** `Coverage.unextracted[]` (UNREADABLE) is a distinct
  Pydantic model from `Distillation.missing[]` (UNPROVABLE), with a `model_validator` making
  "complete=True with non-empty unextracted[]" unrepresentable. `test_coverage_lying_completeness_rejected`
  and `test_coverage_unextracted_distinct_from_missing` police it.
- **Hard rules proven by test, not asserted.** Plan 02 names `test_socket_never_auto_publishes` and
  `test_distill_package_imports_no_ai` (sys.modules check). The no-auto-publish review correctly leaves
  the `semantic.py:142-150` gate as the sole publish path and forbids the socket from touching it.
- **Faithfulness seam is real and injectable, not hand-wavy.** `FaithfulnessCheck` Protocol +
  `StructuralFaithfulness` default + a single-place `_enforce(result, check=...)` boundary hook, with
  `test_faithfulness_seam_rejects_untraced` proving both that an untraced claim is rejected AND that a
  permissive injected checker passes — proving the Phase-3 swap point is live. This is the correct way
  to leave a seam.
- **Backward-compat strategy for `Trace.locator` is sound in principle.** Widen `str → Locator` union
  with a `field_validator(mode="before")` coercing bare strings to `FreeLocator`, plus additive `span:
  str = ""`. `tests/test_semantic.py` is a real tripwire (it constructs `Trace` via `capture_session`
  with bare-string locators and via `Source(id="s1")`-backed sessions), and `_session()` exists exactly
  as the plan claims.
- **Wave dependency is clean.** 01-02 depends only on 01-01's shipped symbols; shared files
  (`ports.py`, `__init__.py`, `tests/test_distill_socket.py`) are touched across *sequential* waves,
  not in parallel, so there is no concurrent-write hazard.
- **Toolchain reality is correctly diagnosed.** Base shell is Python 3.11.15 without pydantic/pytest;
  `/usr/bin/python3.12` exists (verified). Wave 0 stands up the venv and adds `mypy` to `[dev]` (it is
  referenced by `[tool.mypy]` but absent from extras — verified true in `pyproject.toml`).

### Concerns

- **[HIGH] The planned import graph is circular — it is NOT acyclic as the plan claims.**
  01-01-PLAN Task 2 says: *"`locators.py` must import NOTHING from `semantic.py` (keep the graph acyclic
  — `semantic` -> `distill.locators`, never the reverse)."* That reasoning is incomplete. Importing
  `from .distill.locators import FreeLocator` in `semantic.py` first runs the **`distill` package
  `__init__.py`**, which (per Task 3 and the barrel design) eager-imports `.ports`, which imports
  `from ..semantic import Source, Distillation, Claim` — but `semantic` is only *partially initialized*
  at that point (it is mid-import, having paused on its `from .distill.locators` line). Result:
  `ImportError: cannot import name 'Source' from partially initialized module 'newsletters.semantic'`.
  I reproduced this with a minimal package mirroring the exact planned structure — it fails on **both**
  `import newsletters.semantic` and `import newsletters.distill`, because `newsletters/__init__.py`
  imports `semantic` at the top. This means the Rev1 regression tripwire (`pytest tests/test_semantic.py`,
  which does `from newsletters import ...`) will fail at collection, and so will `import newsletters`
  generally. The plan's own verify step in Task 2 (`from newsletters.semantic import Trace`) would also
  fail. This is the load-bearing defect: the plan's central backward-compat mechanism (Trace→Locator)
  and its package barrel are wired in a way that cannot import. **It is not caught by any acceptance
  criterion as written** — the criteria assume the imports succeed.

- **[MEDIUM] Namespacing rationale is slightly miswritten and could mislead the executor.** Both
  SKELETON.md and 01-01 Task 3 say to keep `register`/`resolve` namespaced because they "collide with
  `templates`' top-level `register`/`resolve` exports." Verified: `templates` exports `register` and
  `get_template` (not `resolve`), and only `register` is re-exported at the **package root**
  (`newsletters/__init__.py:69`). So the only genuine collision is `register` at the package root; there
  is no `templates.resolve`. The *guidance* (do not re-export distill's `register`/`resolve` at package
  root) is correct and should be followed, but the stated reason is inaccurate. An executor who checks
  and finds no `templates.resolve` might wrongly conclude the whole namespacing note is stale and
  re-export at root, reintroducing the `register` collision. Tighten the rationale to: "package root
  already exports `templates.register`; do not shadow it."

- **[MEDIUM] `mypy` Protocol-shape gate may not actually catch a malformed backend, and is asserted as
  the safety net for `@runtime_checkable`'s call-time-only checking.** `@runtime_checkable` only checks
  *attribute presence* (does the object have `name` and `distill`?), not signatures or return types — so
  `register(badbackend)` passes the `isinstance` check even if `distill` has the wrong signature. The
  plans lean on `mypy src/newsletters/distill` to compensate. But mypy only type-checks code it can see;
  the in-test broken-backend fixture (Plan 02) lives in `tests/`, which is not in the `mypy
  src/newsletters/distill` target, and `ManualBackend` is the *only* in-`src` backend — so mypy will
  confirm ManualBackend conforms but will never exercise a *non*-conforming backend. The structural gate
  is therefore weaker than the plans imply. The runtime conformance tests (Plan 02) are the real teeth;
  the plan should not over-credit mypy. Low functional risk (conformance tests cover it), but the
  stated defense-in-depth is partly illusory.

- **[LOW] `conftest.py` is introduced for the first time in this repo.** There is currently no
  `tests/conftest.py` (verified) and `test_semantic.py` defines its own local `_session()`. Adding a
  conftest is fine and additive, but the plan should ensure the new fixtures do not shadow/conflict with
  `test_semantic.py`'s module-local `_session()` (they will not, since the latter is a plain function not
  a fixture, but a fixture also named `_session` in conftest would be confusing). Name the conftest
  fixtures distinctly (e.g. `work_session`, `sources`) to avoid reader confusion.

- **[LOW] `Coverage.fully_covered(reason=...)` signature accepts and discards `reason`.** Per the
  RESEARCH/PATTERNS shape, `fully_covered(reason: str = "")` returns `cls(complete=True, unextracted=[])`
  and never stores `reason`. ManualBackend calls it with a descriptive reason that vanishes. Harmless,
  but it is dead-parameter API surface; either drop the parameter or store it (a `note` field). Minor.

- **[LOW] JSON round-trip equality for the discriminated union is asserted but the failure mode is
  subtle.** `DistillationResult.model_validate_json(r.model_dump_json()) == r` depends on Pydantic v2
  preserving the `kind` discriminator on dump and re-selecting the right `Locator` variant on load. This
  works, but `Trace.locator` now defaults via `default_factory=FreeLocator` plus a `mode="before"`
  coercion validator — confirm the validator is idempotent on an already-`FreeLocator`/dict input (it
  must pass instances and `{"kind": "free", ...}` dicts through untouched), or round-trip can raise or
  double-wrap. The plan's behavior list mentions this but no acceptance criterion explicitly tests
  "re-validating an already-coerced Locator is a no-op." Add that micro-assertion.

### Suggestions

- **Resolve the circular import explicitly in 01-01 before execution.** Cleanest options, in order of
  preference:
  1. Make `distill/__init__.py` **not** trigger the `semantic` import during `semantic`'s own
     initialization. The simplest robust fix: have `semantic.py` import the locator types from the
     **leaf module** in a way that does not run code importing `semantic` back — but note `from
     .distill.locators import X` *always* runs `distill/__init__.py` first. So either (a) keep
     `distill/__init__.py` empty of eager submodule imports that reach back into `semantic` (i.e. do the
     barrel re-exports lazily / via `__getattr__`), or (b) move `FreeLocator`/`Locator` somewhere
     `semantic` can import without traversing the `distill` package init (e.g. define the `Locator` union
     in a tiny `src/newsletters/locators.py` *outside* the `distill` package, and have `distill`
     re-export it). Option (b) is the least surprising and keeps `distill/__init__.py` free to eager-import
     `ports`. I verified that removing the eager `.ports` import from the package `__init__` also fixes
     it, but that guts the barrel's purpose.
  2. Whichever fix is chosen, **add an explicit acceptance criterion**: `python -c "import newsletters;
     import newsletters.distill; import newsletters.semantic"` succeeds in a fresh interpreter (test all
     three import orders), and add it to Task 2's verify (not just Task 3), since Task 2 is where
     `semantic.py` first imports from the distill package.
- **Add a "fresh-interpreter import-order" check to the conformance/regression gate.** The Rev1 tripwire
  catches it indirectly, but an explicit one-liner import test localizes the failure instantly.
- **Downgrade the mypy claim** from "the Protocol-shape gate" to "a static aid"; rely on the runtime
  conformance suite for the real malformed-backend coverage, and consider widening the mypy target to
  include `tests/` if you want the broken-backend fixture statically checked (it is intentionally
  malformed, so you'd need a `# type: ignore` — probably not worth it; just adjust the wording).
- **Fix the namespacing rationale** to reference the real `templates.register` package-root export.
- **Name conftest fixtures distinctly** (`work_session`/`sources`) to avoid confusion with
  `test_semantic.py`'s local `_session()`.
- **Add the idempotent-coercion micro-test** for the `Trace.locator` validator (str, dict, and instance
  inputs all yield an equal `FreeLocator`; re-validation is a no-op).

### Risk Assessment

**MEDIUM-HIGH.** The architecture, scope, requirement coverage, and hard-rule enforcement are all
sound and well-specified — this is a high-quality plan set. But it contains one concrete, reproducible
defect (the circular import) that will stop execution at Task 2/Task 3 and fail the Rev1 regression
tripwire, and the plan explicitly mis-states that arrangement as acyclic. Until that wiring is
corrected with an explicit import-order acceptance check, the phase cannot complete as written. Once the
import graph is fixed, residual risk drops to LOW (the remaining concerns are accuracy/robustness
polish, not blockers).

---

## Consensus Summary

### Agreed Strengths
- Correct, honest scope (contract-only; adapters/AI/span-containment deferred and stubbed).
- D-05 two-honesties distinction preserved as distinct models, with a "lying coverage" validator.
- Both hard rules (no-auto-publish, AI-optional core) proven by named executable tests.
- Real, injectable faithfulness seam with a one-place `_enforce` hook and a positive+negative test.
- Analog claims (registry idiom, discriminated-union idiom, `capture_session` Trace construction,
  `synthesize()` stub, 3.12 interpreter availability) all verified against the live repo.
- Clean sequential wave dependency; no parallel-write hazard on shared files.

### Agreed Concerns
- **[HIGH] Circular import** between `semantic.py` → `.distill.locators` (which runs `distill/__init__.py`
  → `.ports` → `..semantic`), reproduced deterministically. The plan wrongly calls this acyclic; it
  breaks `import newsletters` and the Rev1 tripwire. **Must fix before execution.**
- **[MEDIUM]** Namespacing rationale mis-cites a nonexistent `templates.resolve`; only `register` actually
  collides (at package root). Guidance is right; reason is wrong.
- **[MEDIUM]** `mypy` is over-credited as the malformed-backend safety net; `@runtime_checkable` only
  checks attribute presence and the only in-`src` backend conforms, so the runtime conformance suite is
  the real coverage.
- **[LOW]** New `conftest.py` fixtures should be named to avoid confusion with `test_semantic.py`'s
  `_session()`; `Coverage.fully_covered(reason=...)` discards `reason`; add an idempotent-coercion
  micro-test for the `Trace.locator` validator.

### Divergent Views
Single-reviewer pass — consensus equals this reviewer's findings. **Highest-priority item to address
before execution: resolve the circular import (relocate the `Locator` union outside the `distill`
package init, or make `distill/__init__.py` re-export lazily) and add an explicit fresh-interpreter
import-order acceptance check to 01-01 Task 2 and Task 3.** Everything else is polish that can be
hardened during execution without re-planning.
