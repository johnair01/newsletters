---
phase: 02-renderer
plan: 01
subsystem: renderer
tags: [pptx, python-pptx, determinism, opc, zip-normalization, ai-optional, testing]

# Dependency graph
requires:
  - phase: 01-specify-de-risk
    provides: "the recorded determinism decision + its committed evidence, the OPC normalizer written as a spike fixture (tests/fixtures/weekly/_determinism.py), and the committed synthetic template"
provides:
  - "src/newsletters/pptx_writer.py — the ONE canonical OPC-zip normalizer in the writer path, stdlib-only at module level and importable on a bare install"
  - "the writer's shared constants (SLOT_PREFIX, WATERMARK_NAME, MARKER, DRAFT_STATUS, WATERMARK_TEXT) as module constants, so tests assert against one spelling"
  - "two bare-install guards for the writer module, running on the CI bare-install job"
  - "five in-test .pptx deck builders + RICH_SLOTS covering group nesting, duplicate names, a template-owned watermark, a non-text NL_ slot and an empty-run slot"
  - "W17 (slide.shapes does not recurse into groups) re-proved as a repo-owned fact"
  - "a python-pptx>=1.0.2 floor pin scoping the determinism claim to its exercised version"
affects: [02-02 writer implementation, 02-03 proof + CI, 03-weekly-compose, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []   # nothing installed; python-pptx was already declared behind the [pptx] extra
  patterns:
    - "verbatim promotion: a spike module moves to src/ unchanged (git records it as a rename) so a reviewer can diff the move and see nothing was tidied"
    - "bare-install guards live in test_ai_optional.py, never in the module they guard (an importorskip'd file cannot prove 'imports without the extra')"
    - "in-test deck builders write only into tmp_path and route bytes through normalize_opc_zip before one write_bytes"
    - "falsifiability controls: fixture timestamps and core properties deliberately differ from what the writer must set"

key-files:
  created:
    - src/newsletters/pptx_writer.py
    - tests/test_pptx_writer.py
  modified:
    - tests/test_ai_optional.py
    - tests/test_pptx_determinism.py
    - tests/fixtures/weekly/_author_template.py
    - tests/fixtures/weekly/_record_determinism_evidence.py
    - tests/fixtures/pptx/_author_fixtures.py
    - pyproject.toml
  deleted:
    - tests/fixtures/weekly/_determinism.py

key-decisions:
  - "P-01: the module is src/newsletters/pptx_writer.py with NO leading underscore — it carries the phase's public entry point (render.py / publish.py / casespec.py precedent); _pptx_loader.py earns its underscore by having no public surface"
  - "P-02: the public API will be render_surface_pptx_bytes / render_surface_pptx, NOT render_weekly_deck — D-01 says the weekly reuses Surface(REPORT) and the renderer is an output FORMAT; a 'weekly' in the writer's name smuggles the semantic kind back into the format layer"
  - "P-03: the writer takes an explicit slots mapping; deriving slots from a Surface is Phase 3's job, because only the composer knows which authored block belongs in which Selection-Pane name"
  - "P-04: cp:contentStatus is implemented verbatim per the decision note ('draft' if not published else ''); the tri-state question (IN_REVIEW is also labelled 'draft') is raised in the PR body, never deviated from silently"
  - "P-05 (IN-04 REJECTED): _author_template._FIXED stays 2026-01-01, deliberately != EPOCH_ZERO — consolidating would set the TEMPLATE's dcterms:created to the exact value the writer must write, so 02-02's marker read-back would pass even if the writer never set it. Recorded in-code as a falsifiability control"
  - "P-06: the committed tests/fixtures/weekly/template.pptx stays BYTE-UNCHANGED; the rich and pathological decks are authored in-test into tmp_path — its part digests are the committed determinism evidence and are in the recorder's CHECKED_FIELDS"
  - "P-07: word_wrap=True / auto_size=NONE applied to the in-test decks and carried forward to Phase 4's docs/weekly.md operator recipe (add_textbox's defaults let overflow escape the slide silently)"
  - "P-08: _author_fixtures._normalize_zip does NOT delegate this phase — delegation swaps _FIXED_ZIP_DATE_TIME for DOS_EPOCH and adds create_system=0, so all nine ADAPT-06 binaries would need regenerating, which this phase's own binary gate forbids. IN-02's second half is satisfied the other way CONTEXT permits: the weekly copy is SUPERSEDED (deleted), not delegated. Carried to Phase 4"
  - "the [pptx] extra carries a FLOOR pin (python-pptx>=1.0.2), not a ceiling: a floor lets a security fix land, a ceiling would pretend we had tested versions we have not"

patterns-established:
  - "One normalizer contract: exactly one normalize_opc_zip implementation is reachable from the writer path; a second would drift exactly as a second epoch sentinel would"
  - "No sys.path mutation in the weekly fixture path — package imports only (IN-03 closed by removing the shadowing MECHANISM, not the symptom)"
  - "Every in-test deck is a fixed point of the normalizer, and the self-test re-proves it rather than asserting it in prose"

requirements-completed: [WKLY-01]   # partial — WKLY-01 completes at plan 02-03

# Metrics
duration: 12min
completed: 2026-08-29
---

# Phase 2 Plan 01: Renderer foundation Summary

**The OPC-zip normalizer promoted verbatim from the Phase 1 spike into `src/newsletters/pptx_writer.py` (stdlib-only, bare-importable, one contract), guarded by the same two bare-install gates that police the loader, with five in-test deck builders that make the fail-loud contract testable against realistic and pathological decks.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-29T05:00:00Z (approx — first commit 05:06:29Z)
- **Completed:** 2026-08-29T05:12:16Z
- **Tasks:** 3
- **Files modified:** 8 (2 created, 5 modified, 1 deleted)

## Accomplishments

- **One canonical normalizer, in `src/`.** `DOS_EPOCH`, `normalize_opc_zip`, `part_digest`,
  `differing_parts`, `differing_zipinfo_fields`, `_reject_duplicate_member_names` and
  `_COMPARED_FIELDS` moved out of `tests/fixtures/weekly/_determinism.py` **verbatim** — git
  recorded the change as a rename, so the "nothing was tidied" review that 02-RESEARCH §Security
  asks for is a one-command diff. The security-critical in-memory `read`/`writestr` loop is
  character-for-character unchanged, so the zip-slip property stays closed *by construction*.
- **IN-03 closed at the mechanism.** All three `sys.path.insert(0, FIXTURE_DIR)` lines are gone and
  the stale `tests/fixtures/weekly/__pycache__/` is deleted. A `sys.path.insert` plus a stale
  `_determinism.*.pyc` was the shadowing mechanism the Phase 1 review warned about; removing the
  insert removes the mechanism, not just the symptom.
- **The writer module is policed before it exists.** `test_pptx_writer_has_no_toplevel_pptx_import`
  and `test_pptx_writer_imports_without_pptx` were added to `tests/test_ai_optional.py` — the file
  the CI `bare-install` job runs — so plan 02-02 lands the writer into a module that is *already*
  proven bare-safe instead of retrofitting the guard afterwards.
- **Five deck builders + `RICH_SLOTS`,** covering group nesting, duplicate shape names, a template
  that owns `NL_DRAFT_WATERMARK`, a non-text `NL_` slot, and an empty-run slot. Each was
  independently smoke-verified (see *Verification*), not accepted on the test's green.
- **W17 is now a repo-owned fact.** `test_group_nesting_hides_a_slot_from_slide_shapes` proves
  `slide.shapes` does not descend into groups, which is what makes the group-recursive binding map
  in plan 02-02 falsifiable rather than a research citation.
- **Zero committed binary regenerated.** The evidence `--check` still exits 0 against the committed
  `part_digest_a`/`part_digest_b`.

## Task Commits

1. **Task 1: Promote the OPC normalizer; retire the fixture copy** — `e163450` (refactor)
2. **Task 2: The two AI-optional writer guards + the python-pptx floor pin** — `02035b7` (test)
3. **Task 3: The in-test deck builders and their self-test** — `173c28a` (test)

## Files Created/Modified

- `src/newsletters/pptx_writer.py` **(new, 268 lines)** — the promoted normalizer (verbatim) under a
  new WHY-first preamble that states the bare-install rule and names the two guards that enforce it,
  plus the writer's five shared string constants. Ten names in `__all__`. Deliberately **not**
  re-exported from `newsletters/__init__.py` (that module imports eagerly; widening it widens the
  bare-install blast radius).
- `tests/test_pptx_writer.py` **(new, 440 lines)** — the phase's proof module, scaffold half: five
  builders, `RICH_SLOTS`, `RICH_SHAPE_NAMES`, a `_walk` recursion, and two self-tests.
- `tests/test_ai_optional.py` — the two writer guards, with an in-file comment explaining why they
  live here and not next to the writer's own tests.
- `tests/test_pptx_determinism.py` — package import replaces the `sys.path` game; `import sys`
  dropped; `_render_bytes` re-documented as the **container** measurement whose naive `tf.text` fill
  and flat `{name: shape}` map must NOT be copied into the writer. Every assertion kept, including
  the negative control.
- `tests/fixtures/weekly/_author_template.py` — package import; `_FIXED` annotated as a
  falsifiability control (P-05).
- `tests/fixtures/weekly/_record_determinism_evidence.py` — package import; `CHECKED_FIELDS`
  untouched.
- `tests/fixtures/pptx/_author_fixtures.py` — **docstring only**; repointed at the promoted module
  and records the ADAPT-06 delegation as a Phase 4 carry-forward with its cost.
- `pyproject.toml` — `pptx = ["python-pptx>=1.0.2"]` with the floor-vs-ceiling reasoning on the line.
- `tests/fixtures/weekly/_determinism.py` — **deleted** (superseded by the promotion).

## Decisions Made

P-01 … P-08 were recorded in the plan and implemented as written — they are reproduced in this
summary's frontmatter `key-decisions` because plans 02-02 / 02-03 and Phases 3 / 4 inherit them as
**inputs, not open questions**. The two that will bite later if forgotten:

- **P-06** — do not regenerate `tests/fixtures/weekly/template.pptx`. Its part digests are the
  committed determinism evidence.
- **P-05** — do not "tidy" `_FIXED` onto `EPOCH_ZERO`. The difference is what keeps 02-02's marker
  read-back able to fail.

One decision was taken during execution, inside the phase's own reasoning:

- **The in-test decks carry the same falsifiability control as the committed template.** Their
  `category` / `content_status` are empty and `created` is `2026-01-01`, and
  `test_test_decks_have_the_expected_shape_inventory` **asserts** they are not the writer's values.
  Without that, plan 02-02's read-back assertion would be green on a deck the writer never touched
  — P-05's argument applied to the decks P-06 introduced.

## Carry-forwards (explicit, to Phase 4)

1. **ADAPT-06 normalizer delegation (P-08).** `tests/fixtures/pptx/_author_fixtures._normalize_zip`
   still implements the contract separately. Delegating to `newsletters.pptx_writer.normalize_opc_zip`
   swaps `_FIXED_ZIP_DATE_TIME` (2026-01-01) for `DOS_EPOCH` (1980-01-01) and adds
   `create_system=0`, so **all nine golden `.pptx` binaries must be regenerated in the same change**
   (W23 measured: zero assertion changes needed). Phase 4 owns the committed==fresh `.pptx` gate
   work, which is where a deliberate corpus regeneration belongs. Recorded in the file's own
   docstring so it cannot be lost with this summary.
2. **Operator-template `word_wrap` / `auto_size` guidance (P-07).** `docs/weekly.md` (the WKLY-06
   operator recipe) must tell the operator to author their template's text boxes with
   `word_wrap = True` and `auto_size = NONE`: `add_textbox`'s defaults are no wrapping plus a stored
   size PowerPoint only corrects when a human edits the box, so overflow escapes the slide with
   nothing raising. The in-test decks already do this; the shipped template is Phase 4's.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Extended the `_render_bytes` re-documentation to the module docstring**
- **Found during:** Task 1
- **Issue:** The plan asked for `_render_bytes`'s *function* docstring to stop calling itself "the
  Phase 2 writer in miniature". The module docstring of `tests/test_pptx_determinism.py` makes the
  identical claim in its own paragraph; fixing only one leaves the misleading sentence in the more
  prominent place, which is the failure mode the instruction exists to prevent.
- **Fix:** Both now say the function is the **container** measurement, and the function docstring
  names the two naiveties that must never reach the writer (`tf.text` destroying run/paragraph
  formatting — W3; the flat `{name: shape}` map being group-blind and last-wins — W17).
- **Files modified:** `tests/test_pptx_determinism.py`
- **Verification:** `pytest tests/test_pptx_determinism.py -q` — 88 passed with the sibling modules.
- **Committed in:** `e163450`

**2. [Rule 2 - Missing Critical] Added the falsifiability-control assertions to the in-test decks**
- **Found during:** Task 3
- **Issue:** The plan specified neutral core properties for the built decks but no assertion that
  they are *not* the writer's values. P-05 rejects consolidating `_FIXED` precisely because a
  template that pre-carries the writer's output makes the read-back unfalsifiable — the same hazard
  applies to the decks this task introduces, and nothing was guarding it.
- **Fix:** `test_test_decks_have_the_expected_shape_inventory` now asserts `category != MARKER`,
  `content_status != DRAFT_STATUS` and `created != EPOCH_ZERO` on the built deck, plus that the deck
  is its own normalization and that two builds share a `part_digest` (the builder is deterministic).
- **Files modified:** `tests/test_pptx_writer.py`
- **Verification:** `pytest tests/test_pptx_writer.py -q` — 2 passed, 0 skipped.
- **Committed in:** `173c28a`

**3. [Rule 3 - Blocking] `build_rich_template(tmp_path / "again")` needed its directory created**
- **Found during:** Task 3 (writing the determinism half of the self-test)
- **Issue:** Builders do one `write_bytes` into their `directory` argument and do not `mkdir` — by
  design, so a builder can never create a directory outside its argument.
- **Fix:** the test creates the second directory itself.
- **Files modified:** `tests/test_pptx_writer.py`
- **Committed in:** `173c28a`

---

**Total deviations:** 3 auto-fixed (2 missing-critical, 1 blocking)
**Impact on plan:** All three tighten falsifiability or documentation honesty inside the plan's own
scope. No scope creep; no new package; no production behaviour added (the writer half is 02-02).

## Issues Encountered

- **An acceptance criterion in the plan contradicts itself, and the contradiction is recorded rather
  than papered over.** Task 1 requires `git diff --exit-code -- tests/fixtures/pptx/` to exit 0 *and*
  requires a docstring edit to `tests/fixtures/pptx/_author_fixtures.py`. Both cannot hold. Resolved
  in favour of the load-bearing half — **no committed binary changed** — and verified with the
  narrower gate `git diff --exit-code -- 'tests/fixtures/pptx/*.pptx'` (exit 0). The full-directory
  diff shows the mandated docstring edit and nothing else.
- **`isort` and `black` disagree repo-wide, and this is pre-existing.** The repo declares `isort` in
  `[dev]` but configures no `profile = "black"`, so isort wants grid-wrapped imports and black wants
  vertical-hanging-indent: any parenthesized multi-line import fails one of them. Verified against
  `HEAD` that `test_ai_optional.py`, `test_pptx_determinism.py` and
  `_record_determinism_evidence.py` **already** failed `isort --check-only` before this plan, and
  that `_author_fixtures.py` already failed `black --check`. New files are formatted to **black**
  (the de-facto house style — `black --check` is clean on both). No new formatter failure was
  introduced. Logged as friction; fixing it means adding an isort profile and reformatting the repo,
  which is not this plan's scope.

- **WKLY-01 was NOT marked complete, deliberately.** The plan's frontmatter carries
  `requirements: [WKLY-01]`, and the state step would tick it off. Nothing in this plan renders a
  deck — the writer is 02-02 and the CI proof is 02-03 — so `REQUIREMENTS.md` records WKLY-01 as
  *in progress* with the remaining plans named, instead of checking a box the behaviour cannot back.
- **The GSD state handlers mangled their own records again** (second consecutive phase).
  `state.advance-plan` errored (`Cannot parse Current Plan or Total Plans`), `state.update-progress`
  wrote new plan counts while leaving `percent: 25` stale even though it printed 67%,
  `state.record-metric` rejected its documented positional arguments, and
  `roadmap.update-plan-progress` emitted a malformed table row. All four repaired by hand and logged
  in `RETRO.md`.

## Verification (run once each, independently — "the agent says green" is not green)

| Gate | Result |
|------|--------|
| `.venv/bin/python -m pytest -q` | **571 passed, 64 skipped** (baseline 567/64; +2 guards, +2 self-tests, 0 regressions) |
| `.venv/bin/python -m pytest tests/test_pptx_determinism.py tests/test_pptx_golden.py tests/test_pptx_adapter.py -q` | 88 passed |
| `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` | 2 passed, **0 skipped** |
| the three named guards (`..._imports_without_pptx`, `..._has_no_toplevel_pptx_import`, `test_pptx_extra_declared`) | 3 **passed**, not skipped |
| `.venv/bin/lint-imports` | 2 contracts **KEPT**, 0 broken |
| `.venv/bin/mypy src/newsletters/pptx_writer.py` | Success, no issues |
| `_record_determinism_evidence.py --check` | **exit 0** — 6 implementation-independent fields re-verified; `raw_bytes_equal: False` (negative control holds) |
| `git diff --exit-code -- src/newsletters/semantic.py 'tests/fixtures/pptx/*.pptx' tests/fixtures/weekly/template.pptx` | **exit 0** — the gate source and every committed binary are byte-unchanged |
| `grep -rn "sys.path.insert" tests/test_pptx_determinism.py tests/fixtures/weekly/` | **no matches** (IN-03 closed) |
| `diff` of the promoted functions vs the deleted fixture module | **identical** (verbatim promotion confirmed before deletion) |
| independent smoke test of all five builders (reopened each written deck) | duplicate `NL_WEEK_TITLE` ×2 ✓ · `NL_DRAFT_WATERMARK` present ✓ · `NL_NOT_TEXT.has_text_frame is False` ✓ · empty-run paragraph has **0 runs** ✓ · rich deck `word_wrap=True`, `auto_size=NONE`, normalizer fixed point ✓ |
| `git status --porcelain` | clean; no untracked `.pptx` anywhere |

## Known Stubs

None. `src/newsletters/pptx_writer.py` intentionally contains only the normalizer half — the writer
half (`render_surface_pptx_bytes` / `render_surface_pptx`) is **plan 02-02's scope**, stated in the
module docstring and in this plan's objective. Nothing in this plan renders a deck, so nothing here
returns placeholder content to a reader.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern or schema change at a trust boundary
was introduced. The three registered trust boundaries (operator `.pptx` → normalizer; fixture author
script → committed binary; bare install → package) are all still mitigated as planned:
`_reject_duplicate_member_names` promoted verbatim and still raising (T-02-01, re-proved by
`test_duplicate_member_names_are_refused_loudly`); the in-memory read/writestr loop unchanged
(T-02-02); no XML parser constructed anywhere in the new test module — `etree.SubElement` operates
on an already-parsed tree, stated in a comment so a later edit cannot silently reintroduce one
(T-02-03); floor pin only, `[pptx]` still exactly one requirement (T-02-04); all fixture content
fabricated and written only into `tmp_path` (T-02-10); the `sys.path` shadowing mechanism deleted
(T-02-11). **No package was installed by this phase** (T-02-SC), so no legitimacy checkpoint applies.

## User Setup Required

None — no external service configuration, no install, no credential.

## Next Phase Readiness

**Ready for plan 02-02 (the writer).** It inherits:

- a module that is already guarded, already imported by the determinism suite, and already proven
  bare-importable with `pptx` blocked on `sys.meta_path`;
- the five constants its raises and core-property writes must use, so no string is duplicated;
- five decks that exercise every case its fail-loud contract must refuse, plus `RICH_SLOTS` as the
  happy path (Unicode and XML metacharacters included);
- `_walk` / W17 proved in-repo, so the group-recursive binding map has a falsifiable foundation.

**Open, and deliberately so:**

- The **`checkpoint:human-verify`** the decision note records — *a normalized deck opens correctly in
  real PowerPoint* — is still unproven in this environment (no `.pptx` consumer exists here;
  `libreoffice-core` lacks the Impress filters). It belongs to plan 02-03 / the PR review, not here.
- The **P-04 tri-state question** (an `IN_REVIEW` Surface is labelled `"draft"` by
  `cp:contentStatus`, same as `DRAFT`) is implemented verbatim per the binding decision note and
  must be **raised in the PR body**, not silently changed.
- **02-RESEARCH Pitfall 7 / W21**: no CI job installs `[pptx]`, so every pptx test — including this
  plan's two new self-tests — is `s`-skipped in CI today. Plan 02-03 adds the job. Until then, this
  plan's green is a **local** green, and that is stated rather than assumed.

---
*Phase: 02-renderer*
*Completed: 2026-08-29*

## Self-Check: PASSED

All claimed files exist on disk (`src/newsletters/pptx_writer.py`, `tests/test_pptx_writer.py`, and
the six modified files); `tests/fixtures/weekly/_determinism.py` is confirmed absent; all three task
commits (`e163450`, `02035b7`, `173c28a`) are present in `git log` and pushed to
`origin/claude/new-session-gw8tik`.
