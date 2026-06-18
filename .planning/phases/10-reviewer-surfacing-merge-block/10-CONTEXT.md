# Phase 10 — Context & Decisions (Reviewer Surfacing & Merge-Block Gate)

**Goal:** Make the human review gate REAL, not a rubber stamp — surface every `missing[]` and
`unextracted[]` on every surface, show each claim next to its verbatim trace by default, and block
merge in CI while any claim is STALE, un-entailed, or has open gaps.

**Requirements:** PROV-03 (surface missing[]/unextracted[] on every surface), PROV-04 (CI blocks merge
of any surface with a STALE / un-entailed / open-`missing[]` claim). **Depends on:** Phase 3 (STALE
detection `stale_claims`/`is_stale`, `SpanContainmentFaithfulness.entails`, `route_unfaithful_to_missing`,
`missing[]`), Phase 4–7 (`Coverage.unextracted[]` + the `Source.extraction` carrier), Phase 8–9
(renderer/surfaces), Phase 2 (the CI workflow to extend).

## Current state (verified)
- `render.py:444` shows ONE chip ("unsubstantiated → missing[]") for an untraced claim — partial.
  It does NOT comprehensively surface `Distillation.missing[]` or `Coverage.unextracted[]` per surface,
  and there is no "claim next to its verbatim trace by default" review view.
- `Distillation.missing: list[str]`, `Distillation.stale_claims(sources)`, `Coverage.unextracted:
  list[Unextracted]`, `Source.extraction` carrier, `Claim.is_stale`, `Trace.is_stale_against`,
  `SpanContainmentFaithfulness.entails(claim)` all exist.
- CI (`.github/workflows/ci.yml`) has 2 jobs (bare-install, import-linter). Phase 10 ADDS a merge-block job.

## Decisions (design — research to validate/refine)

1. **Reviewer surfacing (PROV-03) — on EVERY surface.** Each rendered surface shows an honest
   "what's not here / not verified" panel listing its `Distillation.missing[]` (unsubstantiated claims)
   AND its `Coverage.unextracted[]` (content the adapter couldn't faithfully extract). Never hidden,
   never collapsed-by-default for the blocking items. Use the design-system tokens (amber/caution).
2. **Claim-beside-trace review view (PROV-03, 3rd criterion).** By default each claim renders next to
   its verbatim trace span (the existing evidence chip expands to show `Trace.span` inline), so an
   unfaithful claim (text not contained in its span) is visible WITHOUT a click. STALE + un-entailed
   claims are visually flagged (e.g. a STALE/unfaithful badge) inline.
3. **The merge-block checker (PROV-04) — a deterministic, AI-free function + CLI.** A pure
   `review_blockers(surface|distillation, sources) -> list[Blocker]` that flags, for a PUBLISHED
   surface: (a) STALE claims (`stale_claims`), (b) un-entailed claims (`SpanContainmentFaithfulness.
   entails` is False), (c) open `missing[]` (non-empty). A CLI entrypoint (e.g. `newsletters check`)
   exits NONZERO with a clear report if any published surface is blocked. Research: should Draft/
   In-Review surfaces be exempt (they're not published yet) — recommend YES (the gate protects the
   Published state; drafts may legitimately have gaps), but a STALE published surface is always a block.
4. **CI merge-block job (PROV-04).** Add a job to `.github/workflows/ci.yml` that runs the checker on
   the corpus (and/or the built site) and FAILS the build if any published surface has a blocker —
   so an unsafe surface cannot merge. stdlib-only, AI-free (keep the AI-optional contract green).
5. **Scope:** this is renderer surfacing + the checker + the CI job. It does NOT change the publish
   gate semantics (no-auto-publish stays; Phase 1/3). It strengthens VISIBILITY + enforcement. The
   typed-`Trace.locator` forward note (Phases 4–7) may be relevant for richer trace display — assess,
   but don't pull a cross-adapter refactor in unless cheap.

## Hard rules in play
- **Every published claim traces to evidence; unsubstantiated → `missing[]`, shown to the reviewer.**
  This phase makes "shown to the reviewer" literally true on every surface + enforced in CI.
- **No auto-publish / gate intact** — the checker + CI ADD enforcement; they never publish or mutate gates.
- **Faithful, not suggestive** — the review view shows verbatim trace spans so unfaithfulness is visible.
- **AI-optional core** — checker + renderer stdlib-only; CI job AI-free; `lint-imports` + bare-install green.
- **Determinism / no hand-edited HTML** — surfacing is rendered from data (SITE-06 holds); checker is
  a pure function of the corpus.

## Research note (dispatch BEFORE planning)
Validate against the LIVE codebase: exactly how `missing[]`/`unextracted[]`/`Source.extraction` are
populated for the dogfood surfaces today (is there real content to surface? are any sample surfaces
STALE/un-entailed?); how `render.py` renders claims/evidence (so the surfacing panel + claim-beside-
trace view fit the existing structure + tokens); the cleanest `review_blockers` design + the CLI/exit-
code contract + the CI job; whether Draft/In-Review surfaces are exempt; and how to TEST a real
blocker (craft a STALE/un-entailed/open-missing fixture surface → checker exits nonzero → CI fails).
Confirm zero new dependency. Record in 10-RESEARCH.md.
