---
phase: 04-signals-voice-pr-summary
plan: "01"
subsystem: tooling/workflow
tags: [gsd, ship, pr-body, voice]
provides:
  - Signals-dispatch PR-body generation in the ship workflow (five evidence-first sections)
  - summary template feeds the dispatch (The signal / What's not here yet)
  - guard test against silent voice reversion by GSD installer updates
affects: [every future shipped phase]
tech-stack:
  added: []
  patterns: [evidence rule for PR prose, guard-test over managed workflow files]
key-files:
  created: [tests/test_signals_voice.py]
  modified: [.claude/gsd-core/workflows/ship.md, .claude/gsd-core/templates/summary-standard.md, .planning/config.json]
key-decisions:
  - "Executed inline by the orchestrator (JJ present, surgical scope) — documented mode choice"
  - "pr_body_sections emptied: fact-asserting fallbacks are the voice violation, not decoration"
  - "Guard is a pytest over the managed markdown — reversion becomes RED, not drift"
duration: ~15min
completed: 2026-07-02
---

# Phase 4: Signals-voice PR/summary Summary

**The ship workflow now writes PRs the way the product writes surfaces: claims beside evidence,
gaps disclosed, nothing fabricated.**

## The signal

`/gsd ship` PR bodies are Signals dispatches — The signal / What we learned / What's verified
(verbatim gate output) / What's not here yet / How to verify — generated from the diff + gate
output under an explicit evidence rule, with the fact-asserting fallback boilerplate removed
and a guard test that turns silent reversion into a failing suite.

## Performance
- **Duration:** ~15 min (inline)
- **Tasks:** 4
- **Files modified:** 4

## Accomplishments
- ship.md `generate_pr_body` rewritten: five dispatch sections + the evidence rule (every
  numeral/claim from gates, diff, or cited artifacts) + the voice rule (no AI framing, no hype,
  honest hedges stay).
- Configured-section rules updated: fallbacks may not assert unverified facts; the offending
  examples replaced with "not assessed"-style disclosures.
- summary-standard.md additively extended with `## The signal` and `## What's not here yet` so
  executor summaries feed the dispatch directly.
- `.planning/config.json` `ship.pr_body_sections` → `[]` (the four boilerplate sections carried
  fact-asserting fallbacks).
- `tests/test_signals_voice.py`: 5 guards (section order, verbatim mandate, no-AI-framing,
  no fact-asserting fallbacks in workflow or config, template sections present).

## Task Commits
1. **ship.md dispatch rewrite** - `b426d48`
2. **template + config** - `a9d2d08`
3. **guard test** - `c5626af`

## Decisions & Deviations
- Inline execution (no planner/executor agents): scope was fully determined, JJ present after
  the stall; the plan doc still went first and each task is an atomic commit.
- None from plan.

## What's not here yet
- The dispatch is enforced for `/gsd ship`-generated bodies; hand-written PR bodies (like
  tonight's, written before this phase) follow the voice by discipline, not tooling.
- The guard checks the *contract text* exists in the managed files — it cannot check that a
  future body-generation run actually obeyed it (that stays a human review responsibility; a
  body-linter is a possible future hardening).
- `gsd-core` updates will still overwrite these files — the guard makes it visible, not
  impossible; re-applying the voice after an update is a known maintenance step.

## Next Phase Readiness
- Milestone core complete (Phases 1–4). Morning handoff remains.
