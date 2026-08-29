# Phase 4: Sample corpus + recipe - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning
**Mode:** Auto-generated (discuss skipped via workflow.skip_discuss; recorded decisions binding)

<domain>
## Phase Boundary

The weekly is proven repeatable **by someone who is not the author**: a fully synthetic sample
weekly (fabricated org/people/metrics) in the `content/module` lineage composes and renders to
`.pptx` in CI under the full carried gate set, exercising the honesty path end to end (a lane
with no KPIs, a recognition with no source email, an asset with no provenance — each in
`missing[]`, none dropped); and `docs/weekly.md` walks an operator from real inputs (workbook /
template deck / .eml drop / photo folder — read-only, data local, the WORK-01 pattern) through
authoring, composing, rendering, and reviewing. Requirements: WKLY-05, WKLY-06. Five success
criteria: `.planning/ROADMAP.md` Phase 4. **The sample ships Draft, watermarked — nothing
publishes, nothing touches `main`.**

</domain>

<decisions>
## Implementation Decisions

**Binding:** all milestone decisions + Phase 1–3 recorded decisions carry. The deck is
**text-only** (recorded); the sample commits **both the `.pptx` binary and its part_digest**,
asserting the digest (Phase 1 decision Q3). Ledgers append-only. Zero new CSS.

**Corpus placement — decide per precedent, log the choice:** the seed says "in the
`content/module` lineage". The repo's established pattern for a new content family is a
sibling corpus with its own builder, `ids.json` ledger, library page and `--corpus` gate wiring
(work → module precedent) — that keeps committed==fresh gates one-builder-per-corpus. Lean that
way (e.g. `content/weekly/` built by a `weeklysite.py`-style builder or an extension of
`modulesite.py`) unless research shows extending `content/module` in place is genuinely
smaller WITHOUT mixing builders in one byte-stable corpus. Whatever is chosen: the publish
assembly (`publish.assemble_site`), `newsletters check`, the site-integrity tests and the
Records strip must all see the new pages — no dead ends (PUB-03 carries).

**Claude's discretion** (log): synthetic fixture content (abstraction-guard denylist grows),
recipe structure of docs/weekly.md, CLI surface (e.g. `newsletters weekly compose|render` or
reuse of existing entry points).

</decisions>

<code_context>
## Existing Code Insights

- `src/newsletters/modulesite.py` — the module-corpus builder precedent (site build, ledger,
  library integration, committed==fresh).
- `src/newsletters/publish.py` + `tests/test_publish.py` — assembly + the four PR-blocking
  guarantees; adding corpus pages must keep them green (links resolve, marker, fonts, drift).
- `src/newsletters/weeklyspec.py` — load_weekly_spec / build_weekly_report / weekly_slots
  (Phase 3); `src/newsletters/pptx_writer.py` — render_surface_pptx (Phase 2);
  `tests/fixtures/weekly/template.pptx` — the synthetic template (P-06: not regenerated).
- `docs/weekly-spec.md` — authoring contract; `docs/case-spec.md` + WORK-01 (worksurface) —
  the read-only/local-data doc pattern for docs/weekly.md.
- CI: `weekly` job (Phase 3) runs the compose path; `site-integrity` runs publish tests;
  bare-install untouched. The deploy workflow publishes from main only — this phase must NOT
  make the sample publishable (Draft gate untouched).

</code_context>

<specifics>
## Specific Ideas

- Honesty-path coverage is a REQUIREMENT, not decoration: the three planted absences must be
  visible in the built HTML honesty panel and the deck's disclosure lines, proven by test.
- The recipe's commands must be executed against the synthetic corpus as part of the phase
  (copy-pasteable = actually pasted, per ROADMAP SC-4).
- Compass + RETRO per CLAUDE.md; spec/docs updated where behavior changed.

</specifics>

<deferred>
## Deferred Ideas

Carried to PR: real-PowerPoint open; first CI green of pptx/weekly jobs; deck images (round
two); contentStatus tri-state; template regeneration + fixture delegation (P-06/P-08 carry).

</deferred>
