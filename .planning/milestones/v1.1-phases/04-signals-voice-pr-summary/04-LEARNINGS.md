---
phase: 4
phase_name: "Signals-voice PR/summary"
project: "Newsletters"
generated: "2026-07-02"
counts:
  decisions: 5
  lessons: 3
  patterns: 2
  surprises: 3
missing_artifacts:
  - "04-CONTEXT.md (inline orchestrator execution — mode documented in 04-PLAN frontmatter; accepted gap, see 04-VERIFICATION)"
  - "04-PATTERNS.md (pattern_mapper skipped — no code analog to map; accepted gap)"
  - "04-RESEARCH.md / 04-UAT.md (never produced — inline mode, prose-contract phase)"
---

# Phase 4 Learnings: Signals-voice PR/summary

> Retroactively extracted (2026-07-02) from the phase paper trail (04-PLAN, 04-SUMMARY), the live
> contract text (`.claude/gsd-core/workflows/ship.md`, `templates/summary-standard.md`), the guard
> (`tests/test_signals_voice.py`), config (`.planning/config.json`), and git history — the same-day
> two-PR evolution `57b79f8` (#7, five-section dispatch: `b426d48`/`a9d2d08`/`c5626af`) → `fd96ea0`
> (#8, `8158fdf`, the mandatory "Start here" client section). Builds on Rounds 1–3 (`01/02/03-LEARNINGS`);
> does not repeat them. This is the reflexive phase: its rules govern the loop's own PR bodies (#9, #10).

## Decisions

### The evidence rule — every numeral and claim traces to a gate, the diff, or a cited artifact
`ship.md`'s `generate_pr_body` opens with a hard rule: "every numeral and every factual claim in the
body must be drawn from the gate output, the diff (`git diff --stat`), or a committed planning artifact
it cites. If a statement cannot be re-derived from those sources, it does not ship."

**Rationale:** This is the product's own "every published claim traces to evidence" invariant applied to
the PR itself — the PR body is a Distillation, its gates and diff are the Traces. A PR is the surface
through which work reaches the reviewer; letting it assert unbacked facts would violate the same
faithfulness the composer enforces on content. Message–code consistency by construction.
**Source:** ship.md:97-99, 04-PLAN Task 1, 04-SUMMARY §Accomplishments

### The voice rule — no AI framing, no hype adjectives, honest hedges stay honest
Explicit prohibition list: no "powerful/seamless/robust/comprehensive", no emoji decoration, no
aspiration stated as fact; and — the non-obvious half — honest hedges ("passes vacuously", "not
exercised end-to-end") are **never softened away**.

**Rationale:** "Faithful, not suggestive" (CLAUDE.md hard rule) applied to prose. Hype is one direction
of unfaithfulness (overclaiming); softening a real hedge is the other (hiding a limit). The rule guards
both. Verbatim gate output (ship.md:159-174, "copied bytes … never paraphrased, never softened") is the
mechanical enforcement — a paraphrase is where softening sneaks in.
**Source:** ship.md:100-102, 159-174, 04-SUMMARY §Accomplishments

### Boilerplate-fallback removal — the fallback strings WERE the voice violation
`config.json` `ship.pr_body_sections` was emptied to `[]` (PR #7 removed 26 lines). The configured
sections' `fallback` strings asserted facts no gate verified (e.g. "No known high-risk rollout
dependencies") — the exact thing the voice rule forbids. `ship.md:222` codifies the replacement policy:
absence of evidence is disclosed as "not assessed", or the section is omitted.

**Rationale:** A default that *fills in* a confident-sounding fact when it has no data is a lie generator.
Emptying the channel removes the temptation; the six core sections carry everything, and any team that
re-adds configured sections inherits the "a fallback may not assert a fact" rule.
**Source:** 04-PLAN Task 3, ship.md:219-228, config.json:51-53, PR #7 config diff (−26 lines)

### Guard-over-managed-files — a pytest over installer-owned markdown
The contract lives in `.claude/gsd-core/`, which the GSD installer overwrites. So the enforcement is a
pytest (`test_signals_voice.py`) that parses the managed markdown and asserts the contract's presence,
order, and prohibitions — reversion becomes a RED suite, not silent drift.

**Rationale:** You cannot make an installer-managed file immutable, but you can make its reversion
*loud*. A guard test over prose you don't control is the honest maximum: it can't prevent the overwrite,
it can make it impossible to miss. Purely additive (VOICE-02) — no existing check touched.
**Source:** test_signals_voice.py docstring + module, 04-PLAN Task 4, 04-SUMMARY §Decisions

### Inline execution mode — orchestrator-executed, no planner/executor subagents
Phase 4 skipped the `discuss → plan → execute` subagent chain and ran inline: the orchestrator wrote
the plan doc, then executed three atomic commits directly (JJ present, scope fully determined).

**Rationale:** GSD's subagent machinery buys fresh context for large or uncertain work; this was a
small, surgical, fully-specified edit to four files. The mode choice was *documented* (04-PLAN
frontmatter `mode: inline …; documented per CLAUDE.md`), the plan doc still went first, and each task
is an atomic commit — the discipline survived without the ceremony. The cost: no 04-CONTEXT/PATTERNS/
RESEARCH (recorded as accepted gaps, not retro-fabricated).
**Source:** 04-PLAN frontmatter:13, 04-SUMMARY §Decisions & Deviations

---

## Lessons

### Hype and audience are DIFFERENT faithfulness failures — fixing one does not fix the other
PR #7 fixed hype: the body became evidence-first, no adjectives, gates verbatim. It was still, in the
Editor-in-Chief's words, incomprehensible — a hype-free body written for a co-engineer is opaque to a
client who won't read the code. PR #8 fixed audience: the mandatory "Start here — what this is, in plain
terms" section (What we built / Why it matters / How to review), plain language, rendered artifact first.

**Context:** Faithfulness has two axes the voice contract must both cover: *don't overclaim* (hype) and
*be understood by the actual reader* (audience). #7 solved the first and revealed the second as
independent — a body can be perfectly honest and perfectly useless to its reader. The product's
"legible to the audience it's for" thesis turned out to apply to its own PRs, and the five-section
dispatch had quietly assumed an engineer audience.
**Source:** git history #7 (`57b79f8`, 5 sections) → #8 (`fd96ea0`, +Start here); PR #8 message ("the
reviewer is a client being taught; visual deliverables get deployed, not diffed")

### Feedback became contract within the hour — the product's own loop, dogfooded
#7 merged 03:59 PDT; #8 merged 04:18 PDT — ~19 minutes. The Editor-in-Chief's "I don't understand what
the shit is going on" review was turned into an amended, guarded contract (new section + sixth test +
Pages deploy) and shipped, same session.

**Context:** This is the phase's cleanest proof that the review gate the product preaches
(Draft › In Review › act on feedback) works on the tooling that builds the product. The correction did
not wait for a retro or a next milestone; the feedback loop closed in real time, and the amendment was
hardened into a test the same commit so it can't silently un-happen. The reviewer being a *client being
taught* is now contract text, not a preference.
**Source:** `git show` author dates on `57b79f8` (03:59:17) and `fd96ea0` (04:18:34); RETRO.md #8 entry

### Prose contracts need presence guards, because installers clobber
A contract that lives only in installer-managed markdown (`.claude/gsd-core/`) has no defense: the next
`gsd-core` update reverts it to upstream PRD boilerplate, silently. The lesson generalized from this
phase: any load-bearing rule that must live in a file you don't own gets a presence guard in a file you
*do* own (`tests/`), so reversion is RED, not drift.

**Context:** This pattern was minted here for the voice contract and then *reused deliberately* in Round
9 for the collaboration contract (CLAUDE.md + docs/collaboration.md) — the loop PLAN cites "mirrors the
voice guard". A durable rule earned from friction, encoded as a test, then applied twice.
**Source:** test_signals_voice.py docstring; loop PLAN.md:63,84 ("presence guard, mirrors the voice guard")

---

## Patterns

### Guard-test-over-managed-markdown (presence + order, not prose police)
Enforce a prose contract that lives in an installer-managed file by extracting the relevant block with a
regex and asserting the required headings (in order), the mandate phrases, and the forbidden strings are
present/absent. Assert *structure and keywords*, never full prose — a presence check that survives
legitimate wording edits but fails on reversion.
**When to use:** any load-bearing contract that must live in a file outside your ownership (vendored,
installer-managed, generated) where you can't prevent overwrites but can make them loud.
**Source:** test_signals_voice.py (whole module); reused in tests/test_collaboration_contract.py (Round 9)

### Contract-describes-itself PR (the dogfooding / reflexive PR)
The PR that installs a body-format contract ships *under that very format* — and every subsequent PR
does too. The contract's first and continuing proof is that the project's own PR bodies obey it.
**When to use:** when a phase's deliverable is a communication standard; make the phase's own
communication the first instance, so drift in the standard shows up as drift in your own PRs.
**Source:** PR #9 and PR #10 bodies (both carry the six-section dispatch in order); 04-SUMMARY §The signal

---

## Surprises

### The fact-asserting fallbacks were baked into the GSD default config — a latent lie, pre-existing
The `pr_body_sections` fallbacks that asserted unverified facts ("No known high-risk rollout
dependencies", "…are covered") were **not introduced by this project** — they shipped in the GSD default
config and predated every Phase-4 decision. The phase's job was partly *removing an inherited lie
generator*, not just avoiding a new one.

**Impact:** Reframed the phase from "write a good voice" to "the tooling's defaults were already
voice-violating." The guard's `test_config_carries_no_boilerplate_pr_sections` exists precisely because
the offending strings could return via an installer update, exactly like the ship.md reversion risk.
**Source:** 04-PLAN Task 3 ("its fallback strings assert facts no gate verified"); config.json PR #7 diff

### The ROADMAP success criterion still says FIVE sections — the shipped contract has SIX
The ROADMAP Phase-4 success criterion (`ROADMAP.md:129`) enumerates exactly five sections. PR #8 added a
sixth (`Start here`) to the contract, the guard, and the tests — but the ROADMAP prose was never updated
in that same change, against the repo's own "update the spec in the same change" convention.

**Impact:** A small, honest spec/code drift born of the same-day amendment moving faster than the plan
doc. Behavior is correct everywhere that runs (contract + guard + tests all six); only the ROADMAP
sentence lags. Logged for the Round-8 ontology/compass sweep — recorded here so the drift isn't
discovered as a "bug" later. (It also means the guard test now enforces *more* than the ROADMAP promised.)
**Source:** ROADMAP.md:129 (five sections) vs ship.md `generate_pr_body` (six); 04-VERIFICATION §Anti-Patterns

### PR #9 carries a "Generated by Claude Code" footer — the AI framing its own contract forbids
The voice rule (installed by this phase) prohibits "AI framing". PR #9's body — a body written *under*
that contract — ends with "_Generated by [Claude Code]…_". PR #10, one round later, dropped the footer.

**Impact:** A reflexive near-miss: the contract governs its own author, and the author tripped on it once
before self-correcting. It also sharpens the phase's central limit — the guards check the *contract
text*, not a *generated/written body*, so a body can pass every guard and still carry a forbidden
framing line. Exactly the human-review responsibility 04-SUMMARY names, caught here by manual review of
the loop's own output.
**Source:** PR #9 body (footer present) vs PR #10 body (absent); 04-VALIDATION §Unvalidated Edges #2

---
*Learnings extracted: 2026-07-02 (retroactive, deep-review loop Round 4)*
*Extractor: Claude (Bureau Chief)*
