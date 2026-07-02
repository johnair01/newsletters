---
phase: 4
slug: signals-voice-pr-summary
status: retroactive
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 4 — Validation Strategy (retroactive)

> Retroactive validation audit (2026-07-02), written for the deep-review loop (Round 4). Maps each
> Phase-4 requirement to how it is validated on current HEAD
> `e1b1611db60f5dabd3e372c9a887ed282e0b5216`: **test-validated** (an executable assertion checks the
> live contract text in the managed files), **structurally validated** (guaranteed by construction —
> additive edit, no gate touched — no test forces the edge), or **unvalidated** (an honest edge no
> test or structure currently covers). The central honesty of this phase: its guards validate the
> **contract text**, not a **generated body** — stated plainly below, not papered over.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/pytest tests/test_signals_voice.py -q` |
| **Full suite command** | `.venv/bin/pytest -q` |
| **Import contract** | `.venv/bin/lint-imports` |
| **Estimated runtime** | ~0.02 s targeted (6 tests); ~11.1 s full (623 tests) |

The guard is a **pure-Python file-content test** — no live `/gsd ship` run, no `gh`, no network. It
reads `ship.md`, `summary-standard.md`, and `config.json` off disk and asserts the contract's presence,
order, and prohibitions. This is deliberate (it must run in CI with zero GSD/gh dependency) and is the
source of the phase's defining validation limit.

---

## Sampling Rate (as executed)

- **Per task (PR #7):** each of the three task commits (`b426d48` ship.md, `a9d2d08` template+config,
  `c5626af` guard) ran the full suite; 04-PLAN §Verification also pins `git diff --exit-code` on
  `ci.yml`/`.importlinter`/`conftest`/existing tests (proving VOICE-02's "weakens nothing").
- **Per amendment (PR #8):** the client-section addition added a sixth guard
  (`test_ship_requires_the_client_section`) and re-ran the full suite (623).
- **This round:** targeted (6 passed), full suite (623 passed), lint-imports (2 kept, 0 broken) — all
  re-run fresh on HEAD. Verbatim tails in `04-VERIFICATION.md`.
- **Max feedback latency:** < 12 s (full suite); < 0.1 s for the targeted guard.

---

## Per-Requirement Validation Map

| Requirement | Behavior | Validation kind | Evidence / Command | Status |
|-------------|----------|-----------------|--------------------|--------|
| VOICE-01 | The dispatch's core sections exist **in the prescribed order** (Start here → The signal → What we learned → What's verified → What's not here yet → How to verify) | **test** | `test_ship_pr_body_is_a_signals_dispatch` — finds all six `_DISPATCH_SECTIONS` in `generate_pr_body`, asserts `positions == sorted(positions)` | ✅ green (contract-text order, incl. `## Start here`) |
| VOICE-01 | Gate output must be **verbatim**; no AI framing; evidence rule binds numerals/claims to gates/diff/artifacts | **test** | `test_ship_mandates_verbatim_gate_output_and_forbids_hype` — asserts `verbatim`, `never paraphrase(d)`, `no ai framing`, `evidence rule` all present | ✅ green |
| VOICE-01 | Configured-section fallbacks may not assert unverified facts; the canonical offender may not return as guidance | **test** | `test_ship_forbids_fact_asserting_fallbacks` — asserts `may not assert a fact` present, and `"No known high-risk rollout dependencies"` absent from the post-`forbidden` text | ✅ green |
| VOICE-01 | The client "Start here" section's three mandatory parts + client framing + link-the-rendered rule survive (the #8 amendment) | **test** | `test_ship_requires_the_client_section` — asserts `What we built` / `Why it matters to you` / `How to review it`, plus `client`, `rendered`, `link` | ✅ green |
| VOICE-01 | `summary-standard.md` feeds the dispatch (carries `## The signal` + `## What's not here yet`) | **test** | `test_summary_template_feeds_the_dispatch` | ✅ green |
| VOICE-01 | `config.json` `ship.pr_body_sections` holds no fact-asserting fallback boilerplate | **test** | `test_config_carries_no_boilerplate_pr_sections` — iterates sections, asserts no `no known` / `are covered` in any fallback | ⚠️ passes **vacuously** on `[]` (see Unvalidated Edges #1) |
| VOICE-02 | The voice contract's reversion becomes a **RED suite** (installer-clobber protection) | **test (adversarial-by-design)** | The whole `tests/test_signals_voice.py` file IS the guard; `_pr_body_step` hard-fails if the `generate_pr_body` step is deleted | ✅ green — teeth proven by construction (any missing heading/phrase → named AssertionError). See Structurally-Validated #1 for the un-run "flip it red" step |
| VOICE-02 | Weakens no existing check (no gate edited/relaxed) | **structural** | PR #7 diff: `ci.yml`/`.importlinter`/`conftest`/existing tests byte-untouched (04-PLAN §Verification `git diff --exit-code`); suite 617→622→623, zero pre-existing tests changed; lint-imports still 2 kept 0 broken | ✅ by construction |

---

## Structurally-Validated (guaranteed, not test-driven)

Correct by construction, but **no test forces the edge**:

1. **The guard's own teeth were not exercised "in anger" this round.** The loop PLAN's honesty ritual
   ("temporarily revert a contract line → suite RED → restore") was applied to the *collaboration*
   guard (Round 9) and asserted-by-construction here: every assertion carries a specific failure
   message, and deletion of the `generate_pr_body` step trips `_pr_body_step`'s hard assert. I did not
   perform a live revert-to-red on `ship.md` this round (the review does not edit managed files). The
   RED behavior is guaranteed by the assertion structure, not demonstrated by a planted reversion.

2. **VOICE-02 "weakens nothing" is structural, not continuously re-asserted.** The proof lives in the
   PR #7 diff (`git diff --exit-code` on the gate configs at build time). No standing test re-checks
   on every run that no gate config drifted; the additive-only property is a historical fact of the
   diff plus the reproducible full-suite/lint-imports greens.

3. **Append-only / cannot-reorder property of configured sections.** `ship.md:221` states configured
   sections "cannot replace, remove, or reorder the required core sections". No test constructs a
   populated `pr_body_sections` and asserts the rendered order is preserved — the property is prose in
   the contract, guaranteed only by whoever executes the workflow honoring it.

---

## Unvalidated Edges (honest gaps — no test AND no structural guarantee)

1. **`config.json` empty-state makes the fallback guard vacuous.** With `pr_body_sections: []`,
   `test_config_carries_no_boilerplate_pr_sections` iterates zero sections and passes without
   asserting anything. It only gains teeth if a section is added later. Correct today (empty by
   design), but the "no fact-asserting fallback" promise is currently unexercised — the guard is a
   tripwire armed for a future config, not a live check.

2. **Nothing verifies a GENERATED body — only the contract text.** This is the phase's defining edge.
   All six guards assert the *instructions* exist in the managed markdown; **none runs
   `generate_pr_body` and checks the produced PR body obeys the evidence rule, quotes gates verbatim,
   omits hype, or leads with a real Start-here section.** A future body could satisfy every guard and
   still violate the voice (e.g. paraphrase a gate tail, or invent a numeral). This stays human review
   by design; a body-linter over the generated output is the named future hardening (04-SUMMARY).

3. **The six-section ORDER is pinned in the contract text, not end-to-end.** `test_ship_...dispatch`
   asserts the headings appear in order *inside `ship.md`*. No test asserts a rendered body emits the
   six sections in that order with `Start here` first — again, contract-text validation, not
   generated-artifact validation.

4. **Installer-clobber recovery is manual and untested.** The guard turns a `gsd-core` overwrite RED,
   but nothing tests the *recovery* path (re-applying the voice after an update). "Re-apply after
   update" is a documented manual maintenance step, wholly outside the test net.

5. **The client-section "link the rendered artifact" rule is a keyword check.** The guard asserts the
   words `rendered` and `link` are present in the step; it cannot verify a real body actually linked a
   deployed page rather than a repo path. Same text-vs-behavior gap as #2, narrowed to the #8 addition.

---

## Nyquist Compliance (honestly derived)

**nyquist_compliant: true** — for what this phase actually delivered: a **prose contract in
installer-managed files, plus an anti-reversion guard**. Both requirements have executable, non-vacuous
tests. VOICE-01's contract (six sections in order, verbatim mandate, no-hype/evidence rules, the client
section, the template feed) is sampled by five assertions that each fail with a specific message if the
contract text regresses. VOICE-02's reversion-protection IS the test file, whose structure guarantees a
RED on any contract deletion; "weakens nothing" is closed structurally by the build-time
`git diff --exit-code` plus reproducible clean gates.

The gaps above are **edges around a well-sampled contract**, not core blind spots — with one honest,
load-bearing caveat that must not be smoothed over: **the guards validate contract text, never a
generated body** (Edge #2/#3/#5). That is not a Nyquist violation of the phase's *stated* goal (the
goal was "the ship workflow *generates* dispatch-shaped bodies" — i.e. carries the contract — and
VOICE-02 was explicitly scoped to "make silent reversion visible," which it does). But it is the ceiling
of what this phase can prove: compliance of any specific body remains a human-review act. The vacuous
config guard (Edge #1) and the un-run revert-to-red (Structural #1) are tripwires armed but not fired
this round — logged as recommended future exercises rather than counted as demonstrated coverage.

---
*Validation audit: 2026-07-02 (retroactive, deep-review loop Round 4)*
*Auditor: Claude (Bureau Chief)*
