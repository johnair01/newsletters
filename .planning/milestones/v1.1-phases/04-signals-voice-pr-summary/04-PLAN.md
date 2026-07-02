---
phase: 04-signals-voice-pr-summary
plan: "01"
wave: 1
depends_on: []
files_modified:
  - .claude/gsd-core/workflows/ship.md
  - .claude/gsd-core/templates/summary-standard.md
  - .planning/config.json
  - tests/test_signals_voice.py
autonomous: true
requirements: [VOICE-01, VOICE-02]
mode: inline (orchestrator-executed, JJ present — small surgical scope; documented per CLAUDE.md)
---

# Plan 04-01: Signals-voice PR bodies from the ship workflow

**Goal (VOICE-01/02):** `/gsd ship` generates PR bodies that read as Signals dispatches —
faithful, no hype, teaching, evidence-first — with exactly five sections (The signal / What we
learned / What's verified / What's not here yet / How to verify), generated FROM the diff + gate
output; proven by a guard test; weakening no existing check.

## Tasks

1. **Rewrite `ship.md`'s `generate_pr_body` step** to the five-section dispatch:
   - The signal — one honest line (what shipped, why it matters to the story), derived from the
     phase goal + SUMMARY one-liners + `git diff --stat` vs base — never from aspiration.
   - What we learned — the decision the phase served; deviations and what they taught (from
     SUMMARY "Decisions & Deviations" + STATE decisions).
   - What's verified — the gate commands run at ship time with their output **verbatim in a
     fenced block** (copied bytes, never paraphrased or softened); numerals in the body may come
     ONLY from gate output or the diff.
   - What's not here yet — the PR's honest missing[]: deferrals, skipped sub-tasks, open seams,
     known caveats (from SUMMARY "Next Phase Readiness"/concerns + ROADMAP deferrals).
   - How to verify — exact reviewer-runnable commands.
   - Explicit prohibitions: no AI framing, no hype adjectives, no claims unbacked by diff/gates;
     body must be re-derivable from the artifacts it cites (message–code consistency).
2. **Extend `summary-standard.md` ADDITIVELY** with `## The signal` (one-liner) and
   `## What's not here yet` sections so executor summaries feed the dispatch directly. Existing
   sections/frontmatter untouched (other consumers keep parsing).
3. **Empty `ship.pr_body_sections` in `.planning/config.json`** — its fallback strings assert
   facts no gate verified ("No known high-risk rollout dependencies"), which is exactly the
   voice violation. `[]` removes the boilerplate channel; the five sections carry everything.
4. **Guard test `tests/test_signals_voice.py`** — asserts the five headings exist in order in
   ship.md's generate_pr_body step; the verbatim-gate-output mandate and the no-AI-framing
   prohibition are present; summary-standard.md carries the two new sections; config
   pr_body_sections is empty/assertion-free. Rationale: `.claude/gsd-core/` is overwritten by
   GSD installer updates — the test makes silent voice-reversion visible (VOICE-02), and it
   weakens nothing (purely additive test).

## Verification
Full pytest (617 + new), lint-imports, check (3 corpora), byte-stable render test, black/isort
(--profile black)/mypy on the new test file; git diff --exit-code on ci.yml/.importlinter/
conftest/existing tests.
