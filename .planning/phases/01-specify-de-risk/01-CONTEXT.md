# Phase 1: Specify + de-risk - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning
**Mode:** Auto-generated (discuss skipped via workflow.skip_discuss; the ONE milestone
discussion round already happened — decisions below are binding)

<domain>
## Phase Boundary

The two things that would be expensive to discover late are settled *before* any code depends
on them: (1) the Weekly Spec schema and the four new block kinds (`NarrativeBlock`,
`RecognitionsBlock`, `TeamBlock`, `AssetBlock`) exist in the docs, specified against
`docs/architecture.md` and extending the `docs/case-spec.md` mechanism; (2) `.pptx`
determinism has a recorded definition backed by evidence from a REAL python-pptx double-write
(byte-stable, or content-stable = unzipped parts byte-identical under normalized zip
metadata). Nothing is discovered in Validate. This phase ships spec text + a recorded decision
with committed evidence — no production renderer/composer code.

Full success criteria: `.planning/ROADMAP.md` Phase 1 (5 criteria).

</domain>

<decisions>
## Implementation Decisions

**Binding decisions from the ONE discussion round (2026-08-29, Editor-in-Chief):**

1. The weekly deck **reuses `Surface(REPORT)`** — the PPTX renderer is an output format, not a
   new semantic kind. No `semantic.py` kind change.
2. Asset provenance minimum = **folder + date + event label**; deep link optional — EXCEPT a BI
   screenshot standing in for values (WKLY-04), where the deep link is REQUIRED. No provenance
   → `missing[]`, never placed silently.
3. Template contract = **named placeholders, fail-loud** on missing/unknown names. The renderer
   never invents layout.

**Remaining choices are Claude's discretion**, decided per the recorded recommendations and
reasoning (evidence-first, smallest change, fail-loud honesty) and logged — e.g. the
generated-by-marker mechanism (core properties vs. notes) is THIS phase's job to decide with a
stated reason and a stated read-back assertion.

</decisions>

<code_context>
## Existing Code Insights

- `EPOCH_ZERO` / `deterministic_timestamp` pattern: `src/newsletters/adapters/_timestamps.py`.
- python-pptx already behind the `[pptx]` extra (loader side: `adapters/_pptx_loader.py`,
  `adapters/pptx_adapter.py`) — the writer SHARES this extra; no new dependency.
- Case Spec mechanism to extend: `src/newsletters/casespec.py` + `docs/case-spec.md`.
- Block union + HTML dispatch: `src/newsletters/templates.py` (blocks), `render.py` (dispatch
  ends in a silent `return ""` fall-through at ~line 620 — Phase 3 closes it; the spec written
  in THIS phase must anticipate that every new block kind renders or fails loud).

</code_context>

<specifics>
## Specific Ideas

- The determinism spike must run a REAL write twice and commit the evidence (hashes; varying
  parts/fields if any) — a decision without evidence is a vibe.
- Spike scratch code is deleted or lands as a test fixture — never an unguarded import in
  `src/newsletters/`.
- The Weekly Spec section must be complete enough that a reader can hand-author a valid spec
  from the doc alone.

</specifics>

<deferred>
## Deferred Ideas

None — scope is locked by the seed and the roadmap.

</deferred>
