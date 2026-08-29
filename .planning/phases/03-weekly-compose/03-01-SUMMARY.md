---
phase: 03-weekly-compose
plan: 01
subsystem: core
tags: [pydantic, discriminated-union, html-render, design-system, gate-freeze, inspect, sha256]

# Dependency graph
requires:
  - phase: 01-specify-de-risk
    provides: "docs/weekly-spec.md — the field-by-field contract for the four block kinds, the AssetRecord and the dispatch class map; decisions D-01/D-02"
provides:
  - "Four new Block union members (narrative / recognitions / team / asset), taking the union to fifteen"
  - "AssetRecord + the type-level D-02 invariant: a provenance-less asset placement is unrepresentable"
  - "Four _block_html render branches built from pre-existing design-system classes only (zero new CSS)"
  - "A fail-loud _block_html fall-through: an unrecognized block raises a teaching ValueError naming its kind"
  - "tests/test_semantic_gate_frozen.py — the review-gate protection that can actually fail in CI"
  - "tests/conftest.py::milestone_base_ref — one definition of the milestone base ref for every diff-shape gate"
affects: [03-02, 03-03, 03-04, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Type-level invariants over runtime policing (AssetBlock.asset required + evidence min_length=1)"
    - "get_args-driven dispatch coverage — a union member added without a render branch fails the suite"
    - "Source-hash freezing via inspect.getsource + a non-vacuity arm proving the digest discriminates"
    - "One definition of the milestone base ref, as a session fixture that FAILS rather than skips"

key-files:
  created:
    - tests/test_weekly_blocks.py
    - tests/test_semantic_gate_frozen.py
  modified:
    - src/newsletters/semantic.py
    - src/newsletters/render.py
    - tests/test_compose.py
    - tests/conftest.py
    - docs/architecture.md
    - docs/weekly-spec.md

key-decisions:
  - "The milestone base ref is resolved ONCE, in tests/conftest.py::milestone_base_ref, rather than duplicated in each diff-shape gate — two copies of a base ref drift exactly as two copies of a normalizer do. Consequence: `merge-base` appears in each gate's docstring, not in duplicated subprocess calls."
  - "AssetBlock renders text-only (figure.diagram + .dh + figcaption, no <img>) — relative-path resolution for the published tree is unsolved and no success criterion asks for it. DiagramBlock's unescaped {b.svg} is explicitly not a precedent."
  - "NarrativeBlock's per-line .cat tag carries the BLOCK's tone (b.tone), because tone is a block-level property in the spec's model and the class map asks for a tone label on every line."
  - "TeamBlock mirrors ChaptersBlock's wrapper nesting exactly (div.t, then one wrapper div holding .ti and .bo) because .chapter is a 64px 1fr grid; the structure is a layout contract, not cosmetics, and is asserted as a literal substring."

patterns-established:
  - "Pattern: a refusal is always asserted alongside a CONSTRUCTING arm — two ValidationError directions plus a well-formed build, so a model that rejected everything could not pass."
  - "Pattern: a byte-freeze on generated-output inputs (render._CSS sha256) states in its own message that regenerating the committed corpora is a separate declared task, never a side effect."
  - "Pattern: a gate that cannot resolve its precondition FAILS with the fix named (fetch-depth: 0), never skips."

requirements-completed: [WKLY-02, WKLY-03]

# Metrics
duration: 11min
completed: 2026-08-29
---

# Phase 3 Plan 01: Weekly block kinds, render branches and a real gate freeze — Summary

**The four weekly block kinds join the typed `Block` union as a zero-deletion insertion, each with an HTML branch built only from classes `_CSS` already defines; `_block_html`'s silent `return ""` becomes a teaching `ValueError`; and the review gate's working-tree-only tripwire is replaced by source-hash pins plus a zero-deleted-lines diff gate that was proved red by deliberate mutation.**

## Performance

- **Duration:** ~11 min
- **Started:** 2026-08-29T06:47Z
- **Completed:** 2026-08-29T06:58Z
- **Tasks:** 3
- **Files modified:** 8 (2 created, 6 modified)

## Accomplishments

- **Fifteen union members, zero deletions.** `NarrativeItem` / `Recognition` / `TeamMember` / `AssetRecord` sit beside the existing block sub-models, and `NarrativeBlock` / `RecognitionsBlock` / `TeamBlock` / `AssetBlock` are appended after `GlossaryBlock`. `git diff $(git merge-base HEAD origin/main) -- src/newsletters/semantic.py | grep '^-' | grep -v '^---' | wc -l` prints **0**.
- **D-02 encoded in the type.** `AssetBlock.asset` is required with no default and `AssetBlock.evidence` carries `min_length=1`, so "an asset without provenance reached a Surface" is unrepresentable. Both refusals are asserted by error *type and location* (`missing` on `('asset',)`, `too_short` on `('evidence',)`) and paired with a constructing non-vacuity arm. `Recognition.evidence` stays defaulted-empty by design; both docstrings carry the contrast.
- **No block is silently droppable.** All four branches render; the dispatch-coverage test drives its cases from `typing.get_args(get_args(Block)[0])`, so a future member added without a branch fails there. The fall-through is now a teaching `ValueError` naming `getattr(b, "kind", type(b).__name__)`, with a comment recording that it stays unreachable by construction and that keeping it unreachable is the point.
- **Zero new CSS, proved two ways.** A sha256 pin on `render._CSS` and a class-token check that every class the new branches emit is one `_CSS` already defines. Both committed corpora still equal a fresh render (`test_publish.py`, `test_modulesite.py` green); `git diff --stat <base> -- content/` is empty.
- **A gate that can fail in CI.** `tests/test_semantic_gate_frozen.py` pins the sha256 of the eight functions that *are* the review gate, with a non-vacuity arm proving the digest discriminates, plus a zero-deleted-lines diff assertion against the milestone base. The old `git diff HEAD` tripwire in `test_compose.py` now resolves the same base and no longer claims to protect a file this phase legitimately extends.

## Task Commits

1. **Task 1: The four block kinds join the union (pure insertion) + the docs stop saying "eleven"** — `1db9b86` (feat)
2. **Task 2: Four HTML branches with zero new CSS, and a dispatch that can no longer swallow a block** — `f6e4d17` (feat)
3. **Task 3: Replace the vacuous gate freeze with one that can fail in CI** — `4bc9702` (test)

All three pushed to `origin/claude/new-session-gw8tik`.

## Files Created/Modified

- `src/newsletters/semantic.py` — +4 sub-models (`NarrativeItem`, `Recognition`, `TeamMember`, `AssetRecord`), +4 block classes, +4 union members. Pure insertion.
- `src/newsletters/render.py` — +4 `_block_html` branches, +4 semantic imports; the bare `return ""` at the end of the dispatch replaced by a teaching `ValueError`. `_CSS` byte-untouched.
- `tests/test_weekly_blocks.py` (new, 339 lines) — union round-trip by discriminator, both D-02 refusals + the constructing arm, the fifteen-member pin, `get_args`-driven dispatch coverage, the class-token check, the `<script>alert(1)</script>` escaping assertion, the no-`<img>` pin, the `_CSS` sha256 freeze, and the fall-through refusal.
- `tests/test_semantic_gate_frozen.py` (new, 150 lines) — Half A (eight source-hash pins + digest-discriminates control + a pin-set/function-set drift check) and Half B (zero removed lines vs the milestone base).
- `tests/conftest.py` — `milestone_base_ref` session fixture: the one definition of `git merge-base HEAD origin/main`, failing (never skipping) when unresolvable.
- `tests/test_compose.py` — the byte-freeze renamed to `test_faithfulness_coverage_templates_site_are_untouched`, rebased onto the fixture, semantic.py removed from its list, and its docstring records both corrections and where semantic.py's protection moved.
- `docs/architecture.md`, `docs/weekly-spec.md` — the block-union note, the "their place in the union" paragraph and the dispatch-contract section move to the shipped tense and cite the tests that pin them.

## The mutation observation (required by the plan — an unproven guard is a vibe)

The gate freeze was proved capable of failing, once, and reverted.

**RED.** A single blank line planted inside `Surface.publish`'s body (after `src/newsletters/semantic.py:717`), then `.venv/bin/python -m pytest tests/test_semantic_gate_frozen.py -q`:

```
>       assert _digest(real) == _FROZEN["Surface.publish"]
E       AssertionError: assert 'a8650c125f0e...187da4d905e90' == '539d5296d15a...72d77c732f9cf'
E         - 539d5296d15a64eb7c8b53306f64227116a44350e9acb887ce572d77c732f9cf
E         + a8650c125f0e5775b9030aeaece27de7236622c0a33c2ee7478187da4d905e90

FAILED tests/test_semantic_gate_frozen.py::test_gate_function_source_is_frozen[Surface.publish]
FAILED tests/test_semantic_gate_frozen.py::test_the_digest_discriminates
2 failed, 9 passed in 0.05s
```

**GREEN.** `git checkout -- src/newsletters/semantic.py`, then the same command:

```
...........                                                              [100%]
11 passed in 0.03s
```

`git status --short` afterwards showed no modification to `src/newsletters/semantic.py` — the revert was clean.

**Worth recording:** the mutation was caught by Half A only. Half B (zero removed lines) stayed green, because inserting a blank line *adds* a line and deletes none. That is precisely why the two halves are independent and why neither alone is the protection: Half A catches a rewrite inside a pinned function, Half B catches a deletion anywhere in the file including code no pin covers.

## Test counts, before and after

| Point | Result |
|---|---|
| Baseline (before Task 1) | **601 passed, 64 skipped** |
| After Task 1 | 607 passed, **1 failed**, 64 skipped — the failure is the known `git diff HEAD` working-tree tripwire (`test_faithfulness_coverage_semantic_templates_site_are_untouched`), expected per 03-RESEARCH Pattern 2, green again once the edit was committed |
| After Task 2 | **615 passed, 64 skipped** |
| After Task 3 (final) | **626 passed, 64 skipped** |

Net: **+25 tests, zero regressions.** Skips stayed at 64 (all `[excel]`/`[pptx]`-extra skips; the `[excel]` install is plan 03-04's). `.venv/bin/lint-imports`: **2 contracts kept, 0 broken.**

## Where docs and implementation had to differ

**Nowhere.** Every field name, default, discriminator literal and HTML class came verbatim from `docs/weekly-spec.md`. The doc edits in this plan were tense corrections and test citations, not contract changes — the spec was implemented, not re-designed.

## Decisions Made

- **The milestone base ref is resolved once, in `tests/conftest.py`.** The plan's action text implied a `merge-base` subprocess call in each of the two gate modules; its acceptance criteria simultaneously required `grep -c '"HEAD"' tests/test_compose.py` to print `0`, which a literal `["git", "merge-base", "HEAD", "origin/main"]` argv in that file cannot satisfy. Both are satisfied honestly by a single `milestone_base_ref` session fixture consumed by both gates. This is also the better design on the repo's own precedent (the Phase 2 "ONE normalizer" decision): two copies of a base ref drift exactly as two copies of a normalizer do. Each gate's docstring names the underlying command so a reader of either file knows what it compares against.
- **`AssetBlock` emits no `<img>`.** Text-only `figure.diagram` + `.dh` + `<figcaption>`, per the spec's class map. Relative-path resolution for the published tree is unsolved; asserted by a `"<img" not in html` pin so a later phase cannot add one without noticing this decision.
- **`NarrativeBlock`'s per-line `.cat` tag carries `b.tone`.** Tone is a block-level `Literal` in the spec's model, and the class map asks for "the tone label" on each line — so each line's tag renders the block's tone rather than a per-item field the model does not have.

## Deviations from Plan

### Auto-fixed / adjusted

**1. [Rule 3 - Blocking] The base-ref acceptance criteria were mutually unsatisfiable as literally written**
- **Found during:** Task 3
- **Issue:** The plan required `grep -c 'merge-base' tests/test_compose.py >= 1` AND `grep -c '"HEAD"' tests/test_compose.py == 0`. A `git merge-base HEAD origin/main` invocation in that file necessarily contains the literal `"HEAD"` as an argv element, so no single-file implementation satisfies both.
- **Fix:** Resolved the ref once in a `tests/conftest.py` fixture consumed by both gates; each gate's docstring names `git merge-base HEAD origin/main`. All four Task-3 greps now pass, and the duplication the criteria implicitly asked for is gone.
- **Files modified:** `tests/conftest.py`, `tests/test_compose.py`, `tests/test_semantic_gate_frozen.py`
- **Verification:** `pytest tests/test_semantic_gate_frozen.py tests/test_compose.py -q` → 24 passed, 0 skipped; all four greps at their required values.
- **Committed in:** `4bc9702`

**2. [Rule 2 - Missing critical] `docs/weekly-spec.md`'s dispatch-contract paragraph corrected in Task 2, not Task 1**
- **Found during:** Task 2
- **Issue:** The plan's Task 1 asked for the "eleven" references at `weekly-spec.md:204,211` to be corrected. Line 211's sentence ("every one of the eleven union members has a branch") is a statement about the *renderer*, which was still untrue at Task 1 time — writing "fifteen" there in Task 1 would have made the spec state something false for the duration of one commit.
- **Fix:** Task 1 rewrote line 211 to an eleven-free, tense-correct historical statement ("Before this phase every one of the union's members had a branch…"), true at every point. Task 2 — the commit that made it so — moved the following paragraph ("the contract, written down before the code exists") to the shipped tense and added the two tests that now enforce it.
- **Files modified:** `docs/weekly-spec.md`
- **Verification:** `grep -c 'eleven' docs/architecture.md docs/weekly-spec.md` → 0 for both, after Task 1.
- **Committed in:** `1db9b86` (Task 1 half), `f6e4d17` (Task 2 half)

**3. [Rule 2 - Missing critical] WKLY-02 / WKLY-03 recorded as IN PROGRESS, not complete**
- **Found during:** state updates
- **Issue:** The plan's frontmatter lists `requirements: [WKLY-02, WKLY-03]`, and the GSD state step would mark both complete. Neither is. WKLY-02 requires the Weekly Spec YAML path (loader, byte-verbatim narrative with real-span traces, `config:` bound-never-claimed, absences → `missing[]`) and WKLY-03 requires the loader-side asset routing (the four `missing[]` conditions, the placement-time content-address check, the root-containment refusal). Both are plan 03-02/03-03's work. Checking them off here would be exactly the "the agent says green" failure CLAUDE.md's execution discipline exists to prevent.
- **Fix:** `.planning/REQUIREMENTS.md`'s traceability rows for WKLY-02 and WKLY-03 record **In progress (03-01)** with what landed and, explicitly, what has NOT been met and which plan owns it. The `- [ ]` checkboxes stay unchecked.
- **Files modified:** `.planning/REQUIREMENTS.md`
- **Verification:** Read back — both rows name the unmet half.
- **Committed in:** the plan-metadata commit

---

**Total deviations:** 3 (1 blocking, 2 correctness). **Impact:** no scope creep; each one removed duplication, prevented a false statement landing in the spec, or prevented a premature green. The plan's substance was executed exactly.

## Issues Encountered

- **The expected Task-1 red.** `test_compose.py::test_faithfulness_coverage_semantic_templates_site_are_untouched` went red the moment `semantic.py` was edited and green the moment it was committed — the exact behaviour 03-RESEARCH Pattern 2 predicted and the reason Task 3 exists. Not treated as a regression, not "fixed" by reverting the union edit.
- **DEF-15 (carried, maintainer-gated).** `black --check` and `isort --check-only` fail on `src/newsletters/semantic.py`, `src/newsletters/render.py` and the two new test files. Verified this is pre-existing, not introduced: the *base-ref copies* of `semantic.py` and `render.py` also fail `black --check`. The repo pins `line-length = 88` while the committed code is written at ~100, and **no CI job runs black or isort** (`grep 'black\|isort' .github/workflows/ci.yml` → no hits). New code follows the committed house width. Fixing this is a repo-wide reformat and stays maintainer-gated.

## Threat Flags

None. The plan's `<threat_model>` dispositions were all implemented as written:

| Threat | Disposition | Evidence |
|---|---|---|
| T-03-07 (dispatch fall-through) | mitigated | teaching `ValueError` + `get_args`-driven coverage test |
| T-03-08 (gate elevation) | mitigated | eight source-hash pins + zero-deleted-lines diff; mutation-proved red once |
| T-03-14 (XSS in new branches) | mitigated | every interpolation via `_e()`; planted `<script>alert(1)</script>` asserted escaped in all four |
| T-03-16 (provenance-less asset) | mitigated | required `asset` + `evidence` `min_length=1`, both directions + constructing arm |
| T-03-17 (corpora silently regenerated) | mitigated | `_CSS` sha256 pin; `test_publish.py` / `test_modulesite.py` green; `git diff --stat <base> -- content/` empty |
| T-03-SC (package installs) | accepted, unchanged | this plan installed nothing |

## Known Stubs

None. Nothing in this plan renders placeholder data; the four branches render only what a caller constructs, and the composer that will construct them is plan 03-02's.

## User Setup Required

None — no external service configuration, no new dependency.

## Next Phase Readiness

- **Ready for 03-02 (the `weeklyspec.py` loader/composer).** The typed targets it must build now exist and round-trip; `render._CSS` and the review gate are both frozen by something that can fail, so the composer's own plans inherit real protection rather than a tripwire.
- **Carried for the CI job (plan 03-03/03-04 or the PR):** Half B needs the full history. The job that runs `tests/test_semantic_gate_frozen.py` or `tests/test_compose.py` must set `fetch-depth: 0` on its checkout, or those two gates will FAIL (by design — the fixture names the fix in its own message). This is the W21 lesson applied forward: the test and the job that runs it are two different artifacts.
- **No blockers.**

## Self-Check: PASSED

All nine claimed files exist on disk; all three claimed commits (`1db9b86`, `f6e4d17`, `4bc9702`)
are in the log and pushed. Artifact minimum line counts met: `tests/test_weekly_blocks.py` 339
(min 180), `tests/test_semantic_gate_frozen.py` 150 (min 90).

---
*Phase: 03-weekly-compose*
*Completed: 2026-08-29*
