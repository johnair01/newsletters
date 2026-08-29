---
phase: 01-specify-de-risk
plan: 02
subsystem: infra
tags: [python-pptx, opc, determinism, core-properties, decision-record, docstring-supersession]

# Dependency graph
requires:
  - phase: 01-01
    provides: "the committed measurement (`.planning/notes/2026-08-29-pptx-determinism-evidence.json`), the `normalize_opc_zip` / `part_digest` contract, and `tests/test_pptx_determinism.py`"
provides:
  - "The recorded decision note Phase 2 reads instead of `01-RESEARCH.md` — one determinism outcome, one scope, one normalizer contract"
  - "The generated-by marker decision (OPC core properties) with a literal read-back assertion against the WRITTEN FILE"
  - "The template contract (fill existing template slides, `NL_` reserved prefix, raise on duplicate names, bind over `slide.shapes`) and the `NL_DRAFT_WATERMARK` shape spec"
  - "D-01 / D-02 / D-03 each with a testable consequence a later phase can gate on"
  - "Q1-Q5 closed in writing, so Phases 2-4 re-litigate nothing"
  - "A repo with no contradicting determinism claim: the ADAPT-06 golden-fixture docstring is corrected and its parsed-`Source` scope note superseded for the writer side"
affects: [02-renderer, 03-weekly-compose, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Decision notes cite committed evidence by path and quote it by value — never restate remembered numbers"
    - "Supersede a wrong claim in place (keep the original reasoning, state what changed and why) rather than deleting it"
    - "One normalizer contract with two call sites; delegation is scheduled to the phase that can absorb the corpus rebuild"

key-files:
  created:
    - .planning/notes/2026-08-29-pptx-determinism-decision.md
  modified:
    - tests/fixtures/pptx/_author_fixtures.py
    - tests/test_pptx_determinism.py

key-decisions:
  - "Determinism = BYTE-STABLE via a declared post-save OPC-zip normalization, scoped in writing to a fixed (python-pptx, zlib) pair; the committed==fresh gate asserts `part_digest`, never a full-file hash"
  - "The generated-by marker lives in OPC core properties, not a notes slide: `cp:category` = `generated-by:newsletters`, `cp:contentStatus` = `draft`, `dcterms:created/modified` = `EPOCH_ZERO`, `cp:identifier` = the Surface id"
  - "The marker is provenance, NOT an authenticity control — `cp:category` is operator-editable, recorded as accepted so nobody later treats an unmarked deck as proof"
  - "Template contract = fill existing template slides (`add_slide` regenerates placeholder names and discards the operator's Selection-Pane naming); Pattern 2b (`add_slide` + name restore by `placeholder_format.idx`) is the one sanctioned escape hatch"
  - "`NL_` reserved prefix, and the `{name: shape}` map raises on duplicate names (legal in OOXML) rather than last-wins dropping a slot"
  - "The Weekly Spec schema lives in a NEW `docs/weekly-spec.md` (Q1); Phase 4 commits the `.pptx` AND asserts the part digest (Q3); `cp:identifier` carries the Surface id (Q4); the doc names design-system classes per block (Q5)"
  - "The Weekly Spec is a sibling loader (`weeklyspec.py`), never a widened `casespec._KNOWN_KEYS`"
  - "ONE normalizer contract: `_determinism.normalize_opc_zip` is canonical; `_author_fixtures._normalize_zip` delegates in Phase 2, NOT now — delegating today would rebuild nine golden binaries inside a spec phase"
  - "The ADAPT-06 docstring's byte-stability claim was FALSE and is corrected against the measurement; the same-second probe is named as its likely cause"

patterns-established:
  - "A decision that lives only in a research document has not been recorded — the note is the artifact the implementer reads"
  - "Every recorded decision carries a stated reason AND the assertion that re-proves it"
  - "Spec-vs-code drift is closed in the same change that creates the newer claim (CLAUDE.md §Conventions)"

requirements-completed: []  # Phase 1 carries no WKLY requirement; this plan de-risks WKLY-01

# Metrics
duration: 14min
completed: 2026-08-29
---

# Phase 1 Plan 02: The recorded determinism decision Summary

**Plan 01-01's measurement is now a recorded decision with a stated scope — `.pptx` output is BYTE-STABLE via a declared post-save zip normalization, the generated-by marker lives in OPC core properties with a literal read-back assertion, and the two places in the repo that said otherwise have been corrected in writing rather than silently contradicted.**

## The recorded outcome, in one sentence

> A rendered `.pptx` is **BYTE-STABLE via a declared post-save OPC-zip normalization** — save to
> `BytesIO`, rewrite every entry with `date_time=(1980,1,1,0,0,0)`, `create_system=0`,
> `compress_type=ZIP_DEFLATED`, emitted entry order and `external_attr` preserved, then one atomic
> write — **scoped in writing to a fixed (python-pptx, zlib) pair**, with the
> implementation-independent **part-content digest** (`sha256` over sorted
> `(part name, sha256(part bytes))`) as the assertion the committed==fresh gate must use. Neither
> assertion normalizes XML.

Evidence: `.planning/notes/2026-08-29-pptx-determinism-evidence.json` (`raw_bytes_equal: false`,
`varying_parts: []`, `varying_zip_fields: ["date_time"]`, `normalized_bytes_equal: true`,
`part_digest_a == part_digest_b == 606c2464…`, python-pptx 1.0.2 / zlib 1.3). Re-proved on every
run by `tests/test_pptx_determinism.py`.

## What Phase 2 inherits (so plan 01-03 can cite the note without re-reading it)

**Marker fields — OPC core properties, zero new parts:**

| What | Attribute | OPC element | Value |
|------|-----------|-------------|-------|
| generated-by marker | `core_properties.category` | `cp:category` | `"generated-by:newsletters"` |
| review-gate state | `core_properties.content_status` | `cp:contentStatus` | `"draft"` while not `PUBLISHED` |
| determinism | `.created` / `.modified` | `dcterms:created` / `dcterms:modified` | `EPOCH_ZERO` |
| which Surface produced it | `core_properties.identifier` | `cp:identifier` | the Surface id |

Asserted by reopening the **written file** (`Presentation(str(out_path))`), never the writer's
return value, and comparing `cp.created == EPOCH_ZERO.replace(tzinfo=None)` (Pitfall 5: `dcterms`
reads back tz-naive; the repo's `EPOCH_ZERO` is tz-aware).

**Template contract:** fill shapes on slides that **already exist** in the operator's template;
never `add_slide` (it regenerates placeholder names and discards Selection-Pane naming —
`WEEKLY_LANE_TITLE` measured back as `Title 1`). Escape hatch for a variable slide count:
`add_slide` + restore names from the layout by `placeholder_format.idx`. Bind over `slide.shapes`,
not `slide.placeholders`.

**Reserved prefix:** `NL_`. Only `NL_`-prefixed shapes are renderer slots; without it the fail-loud
contract rejects every operator logo, footer and page number. Duplicate shape names are **legal**
in OOXML, so the binding map **raises on collision**. Two failing-direction tests are Phase 2's
testable consequence for **D-03**.

**Watermark shape name:** `NL_DRAFT_WATERMARK` — one textbox per slide, added last (top of
z-order), `rotation=315.0`, `Pt(96)`, bold, `RGBColor(0xD0,0xD0,0xD0)`. Fixed literals only; no
`a:alpha` XML; not a template element toggled off.

**Milestone decisions with their gate:** **D-01** → `git diff --exit-code -- src/newsletters/semantic.py`
stays empty through Phases 2-4 and the writer only *reads* `review.state`. **D-02** → the exact
`missing[]` routing table by field name in `docs/weekly-spec.md` (plan 01-03) plus
`AssetBlock.asset` **required**. **D-03** → the two failing-direction tests above.

## Performance

- **Duration:** ~14 min
- **Started:** 2026-08-29T03:52:00Z
- **Completed:** 2026-08-29T04:06:00Z
- **Tasks:** 2
- **Files created:** 1 · **modified:** 2

## Accomplishments

- **One outcome, one scope, evidence-cited.** The note states BYTE-STABLE without hedging, then
  states the boundary the claim must not cross (a fixed zlib pair) in the same blockquote. It cites
  the committed evidence artifact by path and quotes it by value rather than restating remembered
  numbers — the anti-repudiation move (T-01-12), and the reason a `--check` re-run keeps this
  decision bound to a live measurement.
- **The false-green trap is written down.** Two writes inside one wall-clock second are already
  byte-identical, so a probe without a delay "proves" a stability that isn't there. That sentence is
  in the note because it is exactly the mistake the ADAPT-06 docstring made two milestones ago.
- **The marker's honest limit is recorded, not glossed.** `cp:category` is operator-editable, so
  the marker is **provenance, not an authenticity control** (threat T-01-11, accepted). Claiming
  otherwise would be the unsafe default a spec-encoded decision propagates for three more phases.
- **The repo no longer contradicts itself.** `tests/fixtures/pptx/_author_fixtures.py` asserted
  *"python-pptx does NOT stamp the save-time wall-clock"*. The measurement says it does. The claim
  is corrected in place, its likely cause named (a same-second probe), and the real reason the
  golden corpus is stable stated: every fixture routes through `_finalize` → `_normalize_zip`.
- **The deferred risk is closed by name.** The 06-04 `NOTE on the DETERMINISM ASSERTION` deferred
  "determinism on re-saved `.pptx` bytes" as risk A3. That is precisely the question Phase 1 was
  asked to settle, so the note is superseded **for the writer side only** — the parsed-`Source`
  scope remains correct for the loader (ADAPT-06) and the original reasoning is kept, not deleted,
  so the history stays legible.
- **Zero production surface, zero corpus churn.** `git diff --exit-code -- tests/fixtures/pptx/*.pptx
  src/newsletters/ pyproject.toml` exits 0; the two file edits are docstring text only (no `def`,
  `return`, `import` or `class` line appears in the diff).

## Task Commits

1. **Task 1: Write the recorded determinism + marker + template-contract decision** — `231e59d` (docs)
2. **Task 2: Supersede the contradicting claims — one normalizer contract, one determinism scope** — `e1f766d` (docs)

## Files Created/Modified

- `.planning/notes/2026-08-29-pptx-determinism-decision.md` (**new**, 340 lines) — the recorded
  decision. Sections: The question · The hinge · **Decision** (one blockquote-scoped outcome +
  the measured evidence table) · The three assertions Phases 2 and 4 inherit · The generated-by
  marker · The template contract · The Draft watermark · The three milestone decisions with their
  testable consequence · Other decisions (Q1-Q5, the sibling loader, the floor pin, XXE, zip-slip,
  the one-normalizer reconciliation) · How it slots into the roadmap · Truths checked.
- `tests/fixtures/pptx/_author_fixtures.py` — **module docstring only.** The
  `BYTE-REPRODUCIBILITY` claim corrected against the measurement; a new `ONE NORMALIZER CONTRACT`
  paragraph; the `NOTE on the DETERMINISM ASSERTION` marked SUPERSEDED for the writer side with
  the loader-side reasoning preserved.
- `tests/test_pptx_determinism.py` — **module docstring only.** A five-line pointer naming the
  decision this module enforces and the evidence behind it.

## Decisions Made

Beyond the decisions the plan directed (recorded in the note and listed in frontmatter), three
judgement calls were made during execution:

- **The `_author_fixtures` docstring's *second* inaccuracy was corrected too.** The original text
  said `_normalize_zip` was used "for the SmartArt fixture" specifically. The live code routes
  **every** fixture through `_finalize` → `_normalize_zip`. Since the corrected paragraph's whole
  point is *why* the corpus is stable, leaving a second wrong sentence next to the fix would have
  reproduced the drift the task exists to close.
- **The one-normalizer reconciliation names the concrete blocker, not just the schedule.** The two
  normalizers differ in their epoch literal (`2026-01-01` here vs the canonical DOS epoch) and in
  `create_system` / `compress_type`. Delegating today would therefore change the fixture bytes and
  rebuild all nine golden binaries. Saying "delegate in Phase 2" without that sentence would read
  as procrastination rather than as a gated decision.
- **`cp:identifier` was folded into the marker table rather than left as an open recommendation.**
  Q4 asked whether to record which Surface produced a deck. Recording it as a table row (with a
  matching line in the read-back assertion) is what makes it a decision Phase 2 can implement
  without re-reading the research.

## Deviations from Plan

The two plan tasks executed exactly as written. Two record-keeping fixes were applied during the
state-update step:

### Auto-fixed Issues

**1. [Rule 1 - Bug] `roadmap.update-plan-progress` mangled the Phase 1 progress row**
- **Found during:** state updates (post-Task 2)
- **Issue:** The SDK handler rewrote `| 1. Specify + de-risk | 1/3 | In Progress (3 plans, 3 waves) | - |`
  as `| 1. Specify + de-risk | 2/3 | In Progress|  |` — correct count, but it dropped the wave
  detail and left a malformed cell. It also appended the per-plan metric row
  (`| Phase 01-specify-de-risk P02 | 14min | … |`) to the end of the **Recent Trend** bullet list
  in `STATE.md` instead of into the **Per-plan execution** table, and replaced the prose
  `Last session:` paragraph with a bare ISO timestamp, orphaning the two lines that followed it.
- **Fix:** Restored the ROADMAP row's wording and `- ` completed cell; moved the metric row into
  the per-plan table with the table's existing `Phase 1 P02` label; rewrote the `Last session:`
  paragraph; updated `Last activity`, the velocity line and the by-phase row, which the handlers
  do not touch.
- **Files modified:** `.planning/ROADMAP.md`, `.planning/STATE.md`
- **Verification:** `git diff` reviewed line by line; both tables render.
- **Committed in:** the plan-metadata commit

**2. [Rule 1 - Bug] Phase 1's plan checkboxes were stale**
- **Found during:** the same step
- **Issue:** `01-01-PLAN.md` was still `- [ ]` in the ROADMAP despite `01-01-SUMMARY.md` existing
  on disk, so the roadmap simultaneously claimed "2/3 plans complete" and showed zero plans
  checked — a record that contradicts itself is worse than a blank one.
- **Fix:** Checked both `01-01` and `01-02` (each has a committed SUMMARY).
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** `ls .planning/phases/01-specify-de-risk/*-SUMMARY.md` → two files, matching two
  checked boxes.
- **Committed in:** the plan-metadata commit

---

**Total deviations:** 2 auto-fixed (both Rule 1 — record drift, no code touched)
**Impact on plan:** None on scope or behaviour. Both are corrections to planning records that the
SDK handlers wrote imprecisely; no production or test file was involved.

## Issues Encountered

- **A literal-string trap in the plan's own gate.** Task 1's verification asserts
  `t.count('## Decision') == 1` — a *substring* count over the whole file, not a heading count. Any
  `### Decision…` sub-heading or a `## Decisions Made` section would have silently broken it
  (`### Decision` contains `## Decision`). The note is written with exactly one occurrence, and
  the section that would naturally have been called "Decisions" is titled
  `## The three milestone decisions, with their testable consequence`. Worth knowing before plan
  01-03 writes a similar gate.
- **Pre-existing `black` / `isort` failures on both touched files remain.** `tests/test_pptx_golden.py`
  and `tests/fixtures/pptx/_author_fixtures.py` already fail the installed `black 26.5.1` /
  `isort 9.0.1` (recorded in 01-01's summary as the 2026-07-02-baseline no-NEW-failures policy).
  Reformatting them would have polluted a docstring-only diff and put code lines into a change the
  acceptance criteria require to contain none. Left alone; no NEW failure introduced (the edits
  are string content, which `black` does not reflow, and all new lines stay within the file's
  existing ~100-column docstring width).

## Verification (each gate run once, independently)

| Gate | Result |
|------|--------|
| Task 1 decision-note completeness check (18 required strings + exactly one `## Decision`) | **exit 0** — "decision note complete, 328 lines" (340 after Task 2's addition) |
| All Task 1 acceptance greps (`status: decided`, `BYTE-STABLE`, evidence path, test path, `cp:category`, `content_status`, `cp:identifier`, `replace(tzinfo=None)`, `add_slide`, `NL_`, `duplicate`, D-01/02/03, Q1-Q5, `NL_DRAFT_WATERMARK`) | **all ≥ required counts** |
| `git diff --exit-code -- tests/fixtures/pptx/ ':!…/_author_fixtures.py'` | **exit 0** — no golden binary regenerated |
| Diff confined to docstrings (`grep` for `def `/`return `/`import `/`from `/`class ` in the diff) | **no matches** |
| `pytest tests/test_pptx_golden.py tests/test_pptx_determinism.py -x -q` | **67 passed** in 3.62s |
| `pytest -q` (full suite) | **565 passed, 64 skipped** in 13.13s — no regression |
| `git diff --exit-code -- tests/fixtures/pptx/*.pptx src/newsletters/ pyproject.toml` | **exit 0** |
| `git diff HEAD~2 --stat -- src/newsletters/ pyproject.toml .github/ .importlinter` | **empty** — no production surface touched by this plan |
| Read-through as the Phase 2 implementer (gate 5) | **passes** — determinism definition, marker fields + read-back assertion, template contract, prefix, duplicate rule, watermark, D-01/02/03 consequences and Q1-Q5 are all in the note; the only pointer outward is the deliberate one to the evidence JSON |

The 64 skips are the pre-existing optional-extra skips (`[excel]`, `[ai]`, `[panel]` not
installed), not new.

## Known Stubs

None. The note is a decision record, complete as written; both docstring edits describe live code
(verified: `_finalize` routes every fixture through `_normalize_zip`, and
`tests/test_pptx_determinism.py` does enforce the cited decision).

## Threat Flags

None. No network endpoint, auth path, file-access pattern or schema change at a trust boundary was
introduced — this plan wrote prose. Two threat-register items were actively discharged: T-01-11
(the marker's spoofability is stated in the note as accepted, so nobody treats it as authenticity)
and T-01-13 (the golden corpus is byte-unchanged, gated by `git diff --exit-code`).

## User Setup Required

None — no external service configuration.

## Next Phase Readiness

**Ready for plan 01-03** (`docs/weekly-spec.md` + the block kinds + the asset record):

- **D-02's consequence is the direct input:** the note requires the exact `missing[]` routing table
  *by field name*, and `AssetBlock.asset` typed **required** so a provenance-less placement is
  unrepresentable.
- **Q1 is closed:** a new `docs/weekly-spec.md`, a pointer from `docs/case-spec.md`, a link from
  `docs/architecture.md` §1; `docs/weekly.md` stays reserved for the WKLY-06 operator recipe.
- **Q5 is closed:** the doc must name the design-system classes each new block reuses, so Phase 3
  has no visual discretion.
- The note can be cited rather than re-read — this SUMMARY's "What Phase 2 inherits" table is the
  short form.

**Carried to Phase 2:**

- Move `tests/fixtures/weekly/_determinism.py` to `src/newsletters/_pptx_writer.py` behind the
  `[pptx]` extra, then make `_author_fixtures._normalize_zip` delegate to it (the corpus rebuild is
  acceptable in a code phase; it was not in this one).
- Verify — do not assume — that a `python-pptx>=1.0.2` floor pin leaves
  `test_pptx_extra_declared` green (RESEARCH A7).
- Carry a **`checkpoint:human-verify`**: open one normalized deck in real PowerPoint. No `.pptx`
  consumer exists in this environment (`libreoffice-core` without the Impress filters), so this is
  the single unverified link in the normalization chain (RESEARCH A8).
- Confirm the `NL_` reserved prefix against a real operator deck at that same checkpoint
  (RESEARCH A4, medium confidence).

## Self-Check: PASSED

- `.planning/notes/2026-08-29-pptx-determinism-decision.md` — **FOUND**
- `tests/fixtures/pptx/_author_fixtures.py` (modified) — **FOUND**
- `tests/test_pptx_determinism.py` (modified) — **FOUND**
- Commit `231e59d` — **FOUND** in `git log`, pushed to `origin/claude/new-session-gw8tik`
- Commit `e1f766d` — **FOUND** in `git log`, pushed to `origin/claude/new-session-gw8tik`

---
*Phase: 01-specify-de-risk*
*Completed: 2026-08-29*
