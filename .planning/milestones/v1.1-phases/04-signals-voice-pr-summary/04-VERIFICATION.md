---
phase: 04-signals-voice-pr-summary
verified: 2026-07-02T20:40:00Z
status: passed
score: 3/3 success criteria verified
---

# Phase 4: Signals-voice PR/summary Verification Report

Retroactive verification (2026-07-02). Evidence: **PR #7 body** (squash merge `57b79f8` — "Phase 4:
Signals-voice PR/summary generation (VOICE-01..02)") + **PR #8 body** (squash merge `fd96ea0` —
"Client-readable reviews: plain-terms PR sections + reports on Pages") + `04-SUMMARY.md` §Accomplishments/
§Task Commits + a **fresh gate re-run on current HEAD** `e1b1611db60f5dabd3e372c9a887ed282e0b5216`
(branch `loop-r4/phase-4-voice`).

**Phase Goal (ROADMAP):** The `ship` workflow generates PR/summary bodies that read as faithful,
evidence-first Signals dispatches — built from the diff + verbatim gate output, weakening no gate.
**Verified:** 2026-07-02
**Status:** passed

> **Scope note (verification target = CURRENT HEAD, not the plan-time snapshot).** The contract
> verified here is the state AFTER the same-day #7→#8 evolution. PR #7 shipped a **five-section**
> dispatch (The signal / What we learned / What's verified / What's not here yet / How to verify).
> PR #8, hours later, prepended a mandatory **"Start here" client section**, making the live contract
> **six** core sections — the phase's ontological story (see below and `04-LEARNINGS.md`). Everything
> asserted here is what runs on HEAD today. Pre-squash task commits are still reachable via `--all`:
> `b426d48` (ship.md dispatch rewrite), `a9d2d08` (template + config), `c5626af` (guard test) under
> PR #7; `8158fdf` (client-readable "Start here" + Pages deploy) under PR #8.

## The five-→-six-section drift (the phase's story, verified on HEAD)

The phase's real story is **audience discovered as a second, distinct faithfulness failure — and
corrected through the product's own feedback loop within the hour.**

1. **PR #7 (`57b79f8`, merged 03:59 PDT)** fixed **hype**: `generate_pr_body` was rewritten as a
   five-section dispatch under an explicit *evidence rule* (every numeral/claim from gates, diff, or
   cited artifacts) and *voice rule* (no AI framing, no hype adjectives, honest hedges stay). Verified
   live at `57b79f8:.claude/gsd-core/workflows/ship.md` — sections numbered `**2. The signal**` …
   `**6. How to verify**`; the guard test carried **5** `def test_` functions.
2. **PR #8 (`fd96ea0`, merged 04:18 PDT — ~19 min later)** fixed **audience**: after the
   Editor-in-Chief's morning review ("the reviewer is a client being taught; visual deliverables get
   deployed, not diffed"), a mandatory `## Start here — what this is, in plain terms` section was
   prepended, with three parts (*What we built* / *Why it matters to you* / *How to review it*),
   plain-language, clickable links, rendered artifact first. The guard grew to **6** `def test_`
   functions (added `test_ship_requires_the_client_section`).

Fixing hype did not fix comprehension: a body can be hype-free and still unreadable to a non-engineer.
Those are two separate unfaithfulnesses, and the correction arrived through the very Draft › Review ›
act loop the product preaches — dogfooded on its own tooling. See `04-LEARNINGS.md`.

## Goal Achievement

### Observable Truths (the 3 ROADMAP Phase-4 success criteria, goal-backward)

| # | Truth (ROADMAP success criterion) | Status | Evidence (fresh, on HEAD) |
|---|-------|--------|----------|
| 1 | PR-body generation + `summary-standard.md` produce dispatches with the dispatch sections (The signal / What we learned / What's verified / What's not here yet / How to verify), generated FROM the diff + gate output, no AI framing, no hype | ✓ VERIFIED | `ship.md` `generate_pr_body` step carries the sections in order (now **six** — `## Start here` leads, then the five). `test_ship_pr_body_is_a_signals_dispatch` asserts all six exist in prescribed order; `test_summary_template_feeds_the_dispatch` confirms `summary-standard.md` carries `## The signal` + `## What's not here yet`. Evidence rule at `ship.md:97-99`, voice rule at `ship.md:100-102`. **Delta:** the ROADMAP criterion text still names FIVE sections; the shipped contract has SIX (spec not updated when #8 amended it — see Anti-Patterns + `04-LEARNINGS.md`). |
| 2 | Gate output appears **byte-verbatim** in the body (never paraphrased/softened); numeral-free-unless-sourced rule applies to prose | ✓ VERIFIED | `ship.md:159-174` mandates gate output "**verbatim** — copied bytes inside a fenced block, never paraphrased, never summarized, never softened". `test_ship_mandates_verbatim_gate_output_and_forbids_hype` asserts `verbatim`, `never paraphrase(d)`, `no ai framing`, and `evidence rule` all present. The evidence rule pins numerals to gates/diff/artifacts. |
| 3 | The voice change is proven by a test/snapshot and **weakens no existing check** (no gate edited or relaxed) | ✓ VERIFIED | `tests/test_signals_voice.py` = 6 guards, all green (fresh: `6 passed in 0.02s`). Purely additive: PR #7 diff touched no existing test/gate config (`ci.yml`/`.importlinter`/`conftest` untouched — 04-PLAN §Verification `git diff --exit-code`); full suite grew 617→623 with zero pre-existing tests changed. lint-imports still `2 kept, 0 broken`. |

**Score:** 3/3 success criteria verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.claude/gsd-core/workflows/ship.md` | `generate_pr_body` step = Signals dispatch (six core sections, evidence + voice rules, verbatim mandate, no fact-asserting fallbacks) | ✓ EXISTS + SUBSTANTIVE | `<step name="generate_pr_body">` present; §2 Start here (client), §3 The signal, §4 What we learned, §5 What's verified (verbatim), §6 What's not here yet, §7 How to verify; §8 configured-sections evidence rule ("a `fallback` may not assert a fact no gate or artifact verified"). |
| `.claude/gsd-core/templates/summary-standard.md` | Additively carries `## The signal` + `## What's not here yet` so executor summaries feed the dispatch | ✓ EXISTS + SUBSTANTIVE | Both sections present (lines 25-28, 52-55); existing frontmatter/sections intact (additive — other consumers keep parsing). |
| `.planning/config.json` `ship.pr_body_sections` | Emptied — fact-asserting fallback boilerplate removed | ✓ EXISTS + SUBSTANTIVE | `"ship": { "pr_body_sections": [] }`. PR #7 diff removed 26 lines of boilerplate whose fallbacks asserted unverified facts. |
| `tests/test_signals_voice.py` | Guard test against silent voice reversion (VOICE-02) | ✓ EXISTS + SUBSTANTIVE | 6 tests: dispatch-order, verbatim+no-hype, no-fact-asserting-fallbacks, **client-section (the #8 addition)**, template-feeds-dispatch, config-carries-no-boilerplate. All green. |

**Artifacts:** 4/4 verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `summary-standard.md` `## The signal` / `## What's not here yet` | `ship.md` `## The signal` / `## What's not here yet` | executor SUMMARY feeds dispatch | ✓ WIRED | ship.md:136-145 sources The signal from "the SUMMARY files' `## The signal` one-liners"; ship.md:176-186 sources What's not here yet from SUMMARY `## What's not here yet`. |
| `ship.md` What's verified | project enforced gates | verbatim paste at ship time | ✓ WIRED | ship.md:159-174 — "Run (or collect from VERIFICATION.md) the project's enforced gate commands at ship time and paste their tails exactly." |
| `tests/test_signals_voice.py` | `ship.md` + `summary-standard.md` + `config.json` | regex/parse of managed files | ✓ WIRED | `_pr_body_step` extracts the `<step name="generate_pr_body">` block; asserts contract text present. Reversion → RED. |
| `ship.md` configured sections | `config.json` `pr_body_sections` | `gsd_run query config-get ship.pr_body_sections` | ✓ WIRED | ship.md:208 reads config; `[]` → no configured sections rendered (append-only, cannot reorder core). |

**Wiring:** 4/4 connections verified

## Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| VOICE-01: `/gsd ship` PR bodies are Signals dispatches — faithful, no hype, teaching, evidence-first, gate output verbatim, generated from diff + gates | ✓ SATISFIED | - |
| VOICE-02: the voice contract is protected against silent reversion by a guard test, weakening no existing check | ✓ SATISFIED | - |

**Coverage:** 2/2 requirements satisfied

## Accepted-Gap Records (recorded at build time, NOT retro-created)

These artifacts the wider GSD workflow could have produced were **consciously not produced this
phase** — recorded here as accepted gaps, never retro-fabricated into fiction:

1. **04-CONTEXT.md was never produced.** Phases 1–3 each carry `0N-CONTEXT.md`; Phase 4 does not.
   Accepted: the phase ran in **inline orchestrator-executed mode** (no `discuss-phase`/`plan-phase`
   subagent chain) — the mode choice is documented in `04-PLAN.md` frontmatter (`mode: inline
   (orchestrator-executed, JJ present — small surgical scope; documented per CLAUDE.md)`) and in
   `04-SUMMARY.md` §Decisions. The scope was fully determined and surgical; a separate CONTEXT pass
   would have added ceremony, not signal. Not retro-written.

2. **04-PATTERNS.md was never produced.** The `gsd-pattern-mapper` step was skipped — the same inline
   decision. There was no code-pattern analog to map: the deliverable is prose contract text in
   managed markdown + one presence-guard test, not a new module mirroring an existing one. Recorded,
   not retro-written. (Also absent by the same inline choice: `04-RESEARCH.md`, `04-UAT.md`.)

## Honest Limits (restated — the guard's true reach)

1. **The guard protects contract TEXT, not future compliance.** All six tests assert that the
   dispatch contract *exists* in the managed files (headings, order, the verbatim/no-hype/evidence
   phrases). **No test drives a body generation run and checks the generated body obeyed the
   contract.** Whether a real PR body honors the evidence and voice rules stays a human-review
   responsibility (a body-linter is a possible future hardening — named in `04-SUMMARY.md`).

2. **`gsd-core` updates can overwrite these files.** `.claude/gsd-core/` is installer-managed; a GSD
   update can silently revert `ship.md`/`summary-standard.md` to upstream PRD boilerplate. The guard
   makes that reversion a **RED suite**, not an impossibility — re-applying the voice after an update
   is a known maintenance step (04-SUMMARY §What's not here yet).

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/ROADMAP.md` | 129 | Success-criterion text still names **five** sections while the shipped contract (post-#8) has **six** (`Start here` added). Spec not updated in the same change that amended the contract. | ⚠️ Warning | Spec/code drift against the repo's own "update the spec in the same change" convention. Behavior is correct (contract + guard + tests all reflect six); only the ROADMAP prose lags. Logged for the Round-8 ontology/compass sweep; not a goal gap. |
| `tests/test_signals_voice.py` | `test_config_carries_no_boilerplate_pr_sections` | With `pr_body_sections: []` the loop body never executes → the test **passes vacuously**. | ℹ️ Info | Correct today (config is empty by design), but the guard only has teeth if a section is ever added. Logged in `04-VALIDATION.md` §Unvalidated Edges. |

**Anti-patterns:** 2 found (0 blockers, 1 warning, 1 info)

## Human Verification Required

None for the phase goal — all three success criteria are verifiable programmatically and were re-run
fresh on HEAD. The one thing no automation covers (does a *generated* body actually obey the contract?)
is an inherent human-review responsibility, not a gap this phase promised to close.

## Gaps Summary

**No goal gaps.** All three ROADMAP Phase-4 success criteria (and both VOICE requirements) are achieved
on current HEAD. Two artifacts (04-CONTEXT, 04-PATTERNS) are recorded as accepted build-time gaps above;
two honest limits (text-not-compliance, installer-clobber) are restated; one spec-drift warning (ROADMAP
five vs six) is logged for the compass sweep. See `04-VALIDATION.md` for the full validation-coverage edges.

## Fresh Gate Re-Run (verbatim tails, HEAD e1b1611)

```
$ .venv/bin/pytest tests/test_signals_voice.py -q
......                                                                   [100%]
6 passed in 0.02s
```

```
$ .venv/bin/pytest -q
........................................................................ [ 69%]
........................................................................ [ 80%]
........................................................................ [ 92%]
...............................................                          [100%]
623 passed in 11.13s
```

```
$ .venv/bin/lint-imports
Contracts
---------

Analyzed 65 files, 244 dependencies.
------------------------------------

Core (newsletters) must not import any AI/LLM package KEPT
problem.py must not import any network/external-system package KEPT

Contracts: 2 kept, 0 broken.
```

Full-suite count is 623 on HEAD (Phases 1–4 all merged). At PR #7 merge the phase brought the count to
622 (per the #7 body); PR #8's client-section test took it to 623. The +6 over the Phase-3 baseline
(617) is exactly this phase's six guard tests.

## Reflexivity check (this phase's contract governs the loop's own PRs)

This phase installed the dispatch contract that the deep-review loop's own PRs now ship under. Verified
against the live PR bodies: **PR #9 and PR #10 both comply** — each carries `## Start here — what this
is, in plain terms` (with *What we built* / *Why it matters to you* / *How to review it*), `## The
signal`, `## What we learned`, `## What's verified` (verbatim gate tails in a fenced block), `## What's
not here yet`, `## How to verify`, in the prescribed order, hype-free. One reflexive near-miss: **PR #9
carries a "_Generated by Claude Code_" footer** — arguably the AI framing the voice rule forbids — while
**PR #10 dropped it**. Both were hand-written, not `/gsd ship`-generated, so their compliance is by
discipline, exactly the limit `04-SUMMARY.md` names.

## Verification Metadata

**Verification approach:** Goal-backward (3 ROADMAP success criteria) + artifact/wiring/requirement
audit + git-history reconstruction of the #7→#8 five-→-six evolution + live re-run of the guard suite +
reflexive audit of PRs #9/#10 against the installed contract.
**Must-haves source:** `.planning/ROADMAP.md` Phase-4 success criteria + `04-PLAN.md` frontmatter (VOICE-01/02).
**Automated checks:** targeted pytest (6), full suite (623), lint-imports (2 kept 0 broken) — all green.
**Human checks required:** 0 for the goal (generated-body compliance is inherent human review, not a phase promise).
**Total verification time:** ~40 min (paper trail + live contract text + git history + fresh gates + PR-body reflexivity).

---
*Verified: 2026-07-02*
*Verifier: Claude (Bureau Chief, deep-review loop Round 4 — retroactive)*
