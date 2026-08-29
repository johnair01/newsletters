---
phase: 02-renderer
plan: 02
subsystem: renderer
tags: [pptx, python-pptx, template-binding, fail-loud, formatting-fidelity, review-gate, opc-core-properties]

# Dependency graph
requires:
  - phase: 02-renderer
    provides: "plan 02-01's promoted normalizer, the five shared constants, the five in-test deck builders + RICH_SLOTS, the two bare-install guards, and W17 as a repo-owned fact"
  - phase: 01-specify-de-risk
    provides: "the recorded determinism/marker/template-contract decision note (binding input), and EPOCH_ZERO as the repo's one epoch sentinel"
provides:
  - "bind_slots(prs, slots) — a group-RECURSIVE name->shape map that refuses five ambiguities with three-part teaching errors instead of guessing"
  - "fill_slot(text_frame, lines) — the reuse-and-clone primitive: the operator's rPr AND pPr survive on every filled line, because a bullet can only be inherited"
  - "render_surface_pptx_bytes(surface, *, template, slots) -> bytes — the deterministic, normalized deck"
  - "render_surface_pptx(surface, *, template, slots, out_path) -> Path — one write of complete, already-normalized bytes"
  - "the Draft watermark (added, never toggled) and the OPC core-properties generated-by marker, both asserted by reopening the WRITTEN file"
  - "SC-1 (7 tests), formatting fidelity (5 tests), SC-3 both halves and SC-4 (5 tests) — 19 passing, 0 skipped locally"
affects: [02-03 proof + CI job, 03-weekly-compose, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []   # nothing installed; python-pptx was already declared behind the [pptx] extra
  patterns:
    - "reuse-and-clone fill: paragraph 0 is the formatting CARRIER; extra lines are deepcopy(p0._p) with the run's text replaced — inheritance, never construction"
    - "cheap API where the writer owns the shape (the watermark's tf.text), preserving primitive where the operator does (fill_slot) — the contrast is commented in both places"
    - "one lazy pptx import per render, obtained through the EXISTING _load_pptx() boundary; the writer never writes a second `try: import pptx`"
    - "the Surface annotation lives under TYPE_CHECKING so module level stays stdlib-only and the bare-install claim in the docstring remains literally true"
    - "every deck assertion reopens the WRITTEN bytes/file — never the in-memory object the writer just mutated"

key-files:
  created: []
  modified:
    - src/newsletters/pptx_writer.py
    - tests/test_pptx_writer.py

key-decisions:
  - "P-04 implemented VERBATIM: cp:contentStatus is 'draft' if not published else ''. ReviewState has three members, so an IN_REVIEW deck is also labelled 'draft' — the tri-state amendment is RAISED IN THE PR BODY, not deviated from silently"
  - "W20 recorded in code: core_properties.identifier serializes as dc:identifier, NOT cp:identifier — a wording correction to the decision note's field table, with no code consequence"
  - "_add_watermark takes the pptx module rather than importing pptx.util/pptx.dml itself — keeps the module's lazy-import count at exactly one per render and its column-0 import count at zero"
  - "the redundant `# type: ignore[import-untyped]` on the MSO_SHAPE_TYPE import was dropped (mypy resolves the enum module) so the line clears isort's width — DEF-15 avoided rather than added to"
  - "the watermark is ADDED, never toggled off an operator element: W13 disproved the decision note's mechanical objection, but the binding one stands (a toggle makes gate behaviour depend on template content). Both recorded in code so nobody reopens them"

patterns-established:
  - "A refusal that does not name the offender is not a teaching error — every SC-1 test pins the offending name in its `match=` regex"
  - "Assert font.size == Pt(20) explicitly, never `is not None`: a None IS the silent-downgrade failure, and this is the only automated way to see it"
  - "Inverted assertions are load-bearing: the Published deck's 'no watermark, empty contentStatus' test is what stops an unconditional watermark from passing"

requirements-completed: [WKLY-01]   # PARTIAL — WKLY-01 completes at plan 02-03 (the CI job). Left unchecked in REQUIREMENTS.md.

# Metrics
duration: 7min
completed: 2026-08-29
---

# Phase 2 Plan 02: The writer Summary

**The writer half of `pptx_writer.py`: a group-recursive binding map that refuses five ambiguities
rather than guessing, a reuse-and-clone fill that inherits the operator's 20pt bold bullets instead
of constructing its own, and two entry points whose Draft watermark and generated-by marker are
proved by reopening the file they wrote.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-08-29T05:19:00Z (approx — first commit 05:20:25Z)
- **Completed:** 2026-08-29T05:26:36Z
- **Tasks:** 3 (+1 formatter fix commit)
- **Files modified:** 2 (0 created — both files existed from 02-01)

## The public API Phase 3 builds `weekly_slots(surface)` against (verbatim)

```python
def bind_slots(prs: Any, slots: Mapping[str, Sequence[str]]) -> dict[str, Any]: ...

def fill_slot(text_frame: Any, lines: Sequence[str]) -> None: ...

def render_surface_pptx_bytes(
    surface: "Surface",
    *,
    template: Union[str, Path],
    slots: Mapping[str, Sequence[str]],
) -> bytes: ...

def render_surface_pptx(
    surface: "Surface",
    *,
    template: Union[str, Path],
    slots: Mapping[str, Sequence[str]],
    out_path: Union[str, Path],
) -> Path: ...
```

`Presentation` and shape objects stay `Any` (python-pptx ships no stubs and this repo deliberately
adds no `types-*` package — the `_pptx_loader.py` precedent). `Surface` is imported under
`TYPE_CHECKING` only, so module level remains stdlib-only and the bare-install guarantee in the
docstring is literally true rather than approximately true. Import path is unchanged:
`from newsletters.pptx_writer import render_surface_pptx` — the module is still **not** re-exported
from `newsletters/__init__.py`.

## Accomplishments

- **The binding map refuses five ambiguities, in a fixed order, each naming the offender.**
  Duplicate shape name (T-02-04) → template owns `NL_DRAFT_WATERMARK` (T-02-05) → unknown content
  name → unfilled `NL_` slot → slot cannot hold text (T-02-13). Every message is the house
  three-part shape: what was found with `!r` values, why it cannot be resolved silently, what the
  operator does next. `ValueError` in all five cases — never `KeyError`, never `AttributeError`.
- **`_walk` recursion is load-bearing, and now proved in both directions.** 02-01 proved
  `slide.shapes` hides a grouped slot; `test_group_nested_slot_is_bound` proves `bind_slots` finds
  it anyway, and asserts the map equals the deck's full recursive inventory so a gap is a red rather
  than a silent drop.
- **The reserved prefix is proved to discriminate.** `test_unprefixed_shape_is_not_a_slot` binds the
  rich deck with the full `RICH_SLOTS` and shows `Footer` and `Narrative Group` are **bound** (so a
  duplicate of either is still caught) while neither triggers the unfilled refusal. Without the
  prefix, direction (b) would reject every operator logo and page number, and D-03 would be unusable
  on a real deck.
- **Formatting fidelity is asserted off the written bytes, on every line.** Three lines into the
  20pt bold `buChar` slot read back as three paragraphs, each with `font.size == Pt(20)`,
  `font.bold is True` and a `buChar` inside its `pPr`. The size is asserted **explicitly** — the
  failure message says in so many words that a `None` here means the operator's deck is being
  silently downgraded, because that is the only automated way to see Pitfall 1.
- **`fit_text` is banned by name, with its reason, and there is no call.** `grep -n fit_text`
  matches exactly one line: the ban.
- **The gate is read and cannot be written.** No assignment to `surface.review`,
  `surface.review.state` or any `Surface` field exists in the module (grep exit 1).
  `test_render_does_not_touch_the_gate` captures `model_dump()` before, renders, and asserts
  bit-for-bit identity plus `state is ReviewState.DRAFT`. `git diff --exit-code --
  src/newsletters/semantic.py` exits 0.
- **SC-3 is asserted in both directions.** The Draft deck carries `NL_DRAFT_WATERMARK` **last** in
  shape order on **each** of two slides with `rotation == 315.0`; the Published deck carries none and
  reports `content_status == ""`. Without the inversion, an unconditional watermark would pass every
  Draft assertion and still brand approved work as unreviewed forever.
- **The marker read-back is the decision note's block, verbatim, against `Presentation(str(out_path))`
  — the file, not the return value.** It is falsifiable because the template deliberately carries
  none of those values (P-05's `_FIXED = 2026-01-01`, empty `category`/`content_status`).

## Task Commits

1. **Task 1: the group-recursive binding map and its five refusals** — `6cd4755` (feat)
2. **Task 2: the formatting-preserving fill primitive** — `b30ec36` (feat)
3. **Task 3: watermark, marker, the two entry points, and the gate proof** — `1bacad5` (feat)
4. *(follow-up)* **keep `pptx_writer.py` isort-clean (DEF-15 no-new-failures)** — `679a9e4` (style)

All four pushed to `origin/claude/new-session-gw8tik`.

## Files Created/Modified

- `src/newsletters/pptx_writer.py` — **268 → 627 lines.** Gained a banner comment separating the
  stdlib/bare-importable half from the half that needs the `[pptx]` extra *at call time*; `_walk`,
  `bind_slots`, `fill_slot`, `_add_watermark`, `render_surface_pptx_bytes`, `render_surface_pptx`;
  and three new module-docstring sections (the gate is read never written; the marker is provenance
  not authenticity, T-02-07; this module constructs no XML parser, T-02-03). Module-level imports
  gained only stdlib (`copy`, `pathlib`) plus a `TYPE_CHECKING`-guarded `Surface`.
- `tests/test_pptx_writer.py` — **440 → 957 lines.** Gained the SC-1 battery (7), the fidelity
  battery (5), the SC-3/SC-4 battery (5), plus `_fill_and_reread`, `_paragraphs`, `_watermarks` and
  `_sample_weekly_surface(state)`.

## Amendments raised for the PR body (NOT resolved here)

Both are recorded in code comments as well, so they cannot be lost with this summary.

1. **P-04, the `cp:contentStatus` tri-state question.** The decision note's mapping is binary —
   `"draft"` if not published else `""` — and is implemented verbatim. But `ReviewState` has **three**
   members, so a Surface sitting in `IN_REVIEW` produces a deck labelled exactly like a `DRAFT` one.
   That is arguably correct (both are "not approved for a reader"), and arguably a lost distinction
   for a reviewer looking at File → Info. **Decide in the PR, not in the writer.** Changing it here
   would be a silent deviation from a binding note.
2. **W20, `cp:identifier` → `dc:identifier`.** The decision note's field table says the Surface id
   lands in `cp:identifier`; measured, `core_properties.identifier` serializes as
   **`dc:identifier`**. The python-pptx attribute name and the read-back assertion in the note are
   both correct — only the OPC element name in the table is wrong. **Wording only, no code
   consequence.** Fix the sentence when the note is next touched.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A new isort failure in a previously-clean file**
- **Found during:** Task 3 verification (the formatter no-new-failures check)
- **Issue:** Task 1's lazy import carried two trailing pragmas
  (`# type: ignore[import-untyped]  # noqa: PLC0415`), pushing the line past isort's width. isort
  then wanted a backslash continuation that black refuses — DEF-15's exact conflict. Verified
  against `b1369e0` that `src/newsletters/pptx_writer.py` **passed** isort before this plan, so this
  was a genuinely new failure, not inherited debt.
- **Fix:** dropped the redundant `type: ignore` (mypy resolves `pptx.enum.shapes` and re-ran green
  without it) and recorded why in a comment, so the line clears isort's width without a black
  conflict. DEF-15 was avoided rather than added to.
- **Files modified:** `src/newsletters/pptx_writer.py`
- **Verification:** `isort --check-only` exit 0; `black --check` unchanged; `mypy` Success.
- **Committed in:** `679a9e4`

**2. [Rule 2 - Missing Critical] `_watermarks()` searches recursively, not just top level**
- **Found during:** Task 3
- **Issue:** The plan's Published-case assertion is "no slide of the written file carries
  `WATERMARK_NAME`". A top-level-only scan would be blind to a watermark nested inside a group —
  the same W17 hole the whole phase exists to close, reintroduced in the test that is supposed to
  prove its absence. A negative assertion made with a blind search is the worst kind of green.
- **Fix:** the helper walks recursively (`_walk`), so "no watermark" means no watermark anywhere.
- **Files modified:** `tests/test_pptx_writer.py`
- **Committed in:** `1bacad5`

**3. [Rule 2 - Missing Critical] `Surface` imported under `TYPE_CHECKING` rather than at module level**
- **Found during:** Task 3
- **Issue:** The plan says the entry points are fully annotated. The obvious way — a module-level
  `from .semantic import Surface` — would have made the module docstring's claim ("everything at
  module level here is stdlib only") false, weakening a sentence two CI guards are written against.
- **Fix:** `if TYPE_CHECKING: from .semantic import Surface` with string annotations (the module
  already has `from __future__ import annotations`). Full annotations, docstring stays literally
  true, `test_pptx_writer_imports_without_pptx` still green.
- **Files modified:** `src/newsletters/pptx_writer.py`
- **Committed in:** `1bacad5`

---

**Total deviations:** 3 auto-fixed (1 blocking, 2 missing-critical)
**Impact on plan:** All three are inside the plan's own scope and tighten it. No scope creep, no new
package, no architectural change, no checkpoint required.

## Issues Encountered

- **`tests/test_pptx_writer.py` still fails `isort --check-only`, and it did before this plan.**
  Verified by checking out the file at `b1369e0` and running isort against it with the repo's
  settings: it failed there too. This is DEF-15 (the repo declares isort with no `profile = "black"`,
  so any parenthesized multi-line import fails one formatter or the other). Not introduced here, not
  fixed here — fixing it means adding a profile and reformatting the repo.
- **Local green is still a LOCAL green (W21, carried).** No CI job installs `[pptx]`, so all 19
  tests in this module are `s`-skipped in CI today. Plan 02-03 adds the job. Stated rather than
  assumed.
- **The `checkpoint:human-verify` remains open**: no `.pptx` consumer exists in this environment
  (`libreoffice-core` has no Impress filters), so "a normalized, watermarked deck opens correctly in
  real PowerPoint, the bullets survived, the watermark is legible, an overfull slot is acceptable,
  the marker is readable in File → Info" is unproven. It belongs to 02-03 / the PR review.

## Verification (run once each, independently — "the agent says green" is not green)

| Gate | Result |
|------|--------|
| `.venv/bin/python -m pytest -q` | **588 passed, 64 skipped** (baseline 571/64; +17 tests, 0 regressions) |
| `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` | **19 passed, 0 skipped** (2 scaffold + 7 SC-1 + 5 fidelity + 5 SC-3/SC-4) |
| `.venv/bin/python -m pytest tests/test_semantic.py tests/test_ai_optional.py -q` | 41 passed, 1 skipped |
| `.venv/bin/lint-imports` | 2 contracts **KEPT**, 0 broken |
| `.venv/bin/mypy src/newsletters/pptx_writer.py` | Success, no issues |
| `.venv/bin/black --check` (both files) | clean |
| `.venv/bin/isort --check-only src/newsletters/pptx_writer.py` | **exit 0** (was failing mid-plan; fixed in `679a9e4`) |
| `git diff --exit-code -- src/newsletters/semantic.py` | **exit 0** — the review gate is byte-unchanged (SC-4) |
| `git diff --exit-code -- tests/fixtures/pptx/ tests/fixtures/weekly/template.pptx` | **exit 0** — every committed binary unchanged (P-06) |
| `_record_determinism_evidence.py --check` | **exit 0** — 6 fields re-verified; `raw_bytes_equal: False` (negative control holds) |
| `grep -n '^import pptx\|^from pptx' src/newsletters/pptx_writer.py` | **no matches** (exit 1) — the only pptx imports are indented |
| `grep -n 'surface\.review\s*=\|\.review\.state\s*=' src/newsletters/pptx_writer.py` | **no matches** (exit 1) — no write path to the gate |
| `grep -n 'fit_text' src/newsletters/pptx_writer.py` | one match: the **ban**, no call (T-02-15) |
| `grep -n 'text_frame.text\s*=' src/newsletters/pptx_writer.py` | no match outside `_add_watermark`'s owned shape |
| `git status --porcelain` | clean; no stray `.pptx` anywhere |

## Known Stubs

None. Every function this plan added is fully implemented and exercised by a test that reads the
written bytes back. Nothing returns placeholder content, and no slot value is hardcoded: the
`slots` mapping is a required keyword argument, and an unfilled `NL_` slot **raises** rather than
rendering a blank box. The Surface→slots derivation is not a stub here — it is Phase 3's scope by
recorded decision P-03, stated in the module docstring and in this plan's objective.

## Threat Flags

None. No new network endpoint, auth path or schema change at a trust boundary. The four registered
boundaries are all mitigated as planned:

- **operator `.pptx` → `bind_slots`**: shape names are used only as dict keys and in messages —
  never as paths, never `eval`'d (T-02-04, T-02-05, T-02-12, T-02-13 all raise, each with a test).
- **authored Surface content → deck XML**: written as XML *text* through python-pptx, which escapes
  it; `test_unicode_and_xml_metacharacters_roundtrip` proves `<&>` round-trips intact (T-02-14).
- **review gate → deck**: mirrored outward only; no assignment path exists (T-02-06).
- **caller `out_path` → filesystem**: caller-supplied, never derived from `surface.id`; stated in
  the docstring (T-02-08).

T-02-03 (XXE) stays mitigated upstream — this plan constructs no XML parser; `copy.deepcopy` and
`getparent().remove()` operate on already-parsed trees, and the module docstring now says so.
T-02-07 (marker forgery) and T-02-09 (decompression bomb) remain **accepted**, recorded in the
module docstring and the plan's register respectively. No package was installed.

## User Setup Required

None — no external service, no install, no credential.

## Next Phase Readiness

**Ready for plan 02-03 (proof + CI).** It inherits:

- the two entry points, stable and fully annotated, to render the sample Surface through;
- `_sample_weekly_surface(state)` in the test module, already satisfying the policy validator in
  both gate states;
- a writer whose only clock is `prs.save(BytesIO)` and whose output is always normalized — so SC-2's
  double-render byte equality has nothing left to fight;
- 19 local-green tests that will start actually running the moment the `[pptx]` CI job exists.

**Open, and deliberately so:** the P-04 tri-state amendment and the W20 wording correction (both
above, both for the PR body); the PowerPoint human-verify checkpoint; and W21 — until 02-03 adds the
job, every number in this summary is a local measurement.

---
*Phase: 02-renderer*
*Completed: 2026-08-29*

## Self-Check: PASSED

Both claimed files exist on disk (`src/newsletters/pptx_writer.py` 627 lines,
`tests/test_pptx_writer.py` 957 lines — both above the plan's `min_lines`), and all four commits
(`6cd4755`, `b30ec36`, `1bacad5`, `679a9e4`) are present in `git log` and pushed to
`origin/claude/new-session-gw8tik` (remote HEAD is `679a9e4`).
