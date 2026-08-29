# Phase 2: Renderer - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning
**Mode:** Auto-generated (discuss skipped via workflow.skip_discuss; the ONE milestone
discussion round already happened — decisions below are binding)

<domain>
## Phase Boundary

A composed weekly `Surface(REPORT)` becomes a `.pptx` deck through an operator-supplied
template — deterministically, marked as generated, visibly Draft-watermarked until a human
publishes it, with the review gate untouched (WKLY-01). Full success criteria:
`.planning/ROADMAP.md` Phase 2 (5 criteria). The writer lands in `src/newsletters/` behind the
`[pptx]` extra (lazy import inside the writer only); a minimal synthetic template ships in the
repo and a sample Surface renders through it in CI.

</domain>

<decisions>
## Implementation Decisions

**Phase 1's recorded decision note is BINDING input, not open questions:**
`.planning/notes/2026-08-29-pptx-determinism-decision.md` — read it first. It fixes:

1. **Determinism**: BYTE-STABLE via declared post-save OPC-zip normalization (fixed 1980
   date_time, create_system, compression pinned); scoped to the (python-pptx, zlib) pair;
   `part_digest` is the implementation-independent committed==fresh assertion; in-process
   double-render asserts full byte equality WITH a negative control.
2. **Marker**: OPC core properties — `cp:category` = generated-by marker, `cp:contentStatus` =
   "draft", `dcterms:created/modified` = EPOCH_ZERO, `cp:identifier` = Surface id — asserted by
   reading the WRITTEN file back (tz-naive comparison gotcha handled). Provenance, not
   authenticity.
3. **Template contract**: fill the operator's EXISTING slides — never `add_slide` (it
   regenerates placeholder names); `NL_` reserved shape-name prefix; duplicate `NL_` names
   raise; missing/unknown names fail loud in BOTH directions with teaching errors;
   `NL_DRAFT_WATERMARK` is the watermark slot shape.
4. Milestone decisions D-01/D-02/D-03 (reuse REPORT; provenance minimum; named placeholders).

**Deferred-to-here from Phase 1 fixes (scheduled work, do not drop):**
- IN-02 second half: pin `create_system` in the normalizer promotion (the writer-side normalizer
  is promoted to `src/newsletters/` — e.g. `_pptx_writer.py` — the fixture normalizer delegates
  or is superseded per the decision note's one-contract rule).
- IN-03/IN-04: the promotion to `src/` resolves the fixture import-mechanism collision; consider
  consolidating `_FIXED` on EPOCH_ZERO only if it does not require regenerating golden binaries
  in this phase without cause.

**Remaining choices are Claude's discretion**, decided per the recorded reasoning
(evidence-first, smallest change, fail-loud) and logged.

</decisions>

<code_context>
## Existing Code Insights

- The spike artifacts: `tests/fixtures/weekly/_determinism.py` (normalizer + part_digest,
  duplicate-name refusal), `_author_template.py` (synthetic template author),
  `template.pptx` (committed synthetic template), `tests/test_pptx_determinism.py`.
- Loader-side python-pptx: `src/newsletters/adapters/pptx_adapter.py` + `_pptx_loader.py`
  (lazy-import discipline to copy).
- Surface/blocks: `src/newsletters/semantic.py` (Surface, review gate — MUST stay
  byte-unchanged), `templates.py`/`semantic.py` Block union, `render.py` (HTML renderer —
  untouched this phase).
- EPOCH_ZERO: `src/newsletters/adapters/_timestamps.py`.
- CI: bare-install job must stay green (writer lazy-imports pptx; import-linter contracts).

</code_context>

<specifics>
## Specific Ideas

- Renderer never advances or mutates review state; a test proves rendering a Draft Surface
  leaves it Draft; `semantic.py` byte-unchanged (git diff gate).
- Every assertion about the written deck reads the file back — never trusts the writer.
- The one unverifiable link here (deck opens in real PowerPoint) is a recorded human-check for
  the PR review, not a phase gap.

</specifics>

<deferred>
## Deferred Ideas

None — scope locked by seed + roadmap; Phase 3 owns the block kinds and composition.

</deferred>
