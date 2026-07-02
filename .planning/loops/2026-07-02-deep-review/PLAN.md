# Plan: Close v1.1 per GSD + 10-round deep-review loop + collaboration contract

## Context (why)

The v1.1 milestone (4 phases, PRs #4–#8, merged to the integration branch on GitHub) is
functionally done but **not formally closed per OpenGSD**, and JJ asked for three things:

1. **Capture everything the workflow expects.** Verified gaps: every phase is missing
   `VERIFICATION.md` / `VALIDATION.md` / **`LEARNINGS.md`** (the learning component JJ
   suspected — `extract-learnings` never ran); no `MILESTONES.md`, no retrospective, no
   archive, no tag; STATE/PROJECT/ROADMAP carry internal contradictions; raw gate output
   lives only in ephemeral /tmp + GitHub PR bodies (nothing verbatim in-repo).
2. **A 10-round comprehensive deep-review /loop** over every thought/decision/code/config
   from the session — understanding *captured to disk* each round (researched: /loop state
   between rounds = transcript + files only, so round artifacts + a state file ARE the
   loop's memory; fixed-prompt form, not the autonomous sentinel).
3. **A canonical collaboration contract** (his UX / "psycho-tech"): JJ owns intent + sets
   pace; Claude owns execution coordination + keeps time; JJ addressed by a named role;
   engagement rules stated as canonical goals in the codebase.

## Design principle: the loop IS the capture vehicle

No separate gap-closing pass. Each round's deep review and its GSD artifact are the same
act — reviewing Phase N deeply *produces* its honest `VERIFICATION/VALIDATION/LEARNINGS`.
Ordering constraint honored: `audit-milestone` hard-requires per-phase VERIFICATION.md, so
per-phase rounds (1–4) run before the close round (10).

**Honesty rules (non-negotiable):**
- Retroactive artifacts say so: each VERIFICATION.md opens with *"Retroactive verification.
  Evidence: PR #N body + NN-XX-SUMMARY §gates + fresh gate re-run on <SHA> <date>."*
  `status: passed` only where a fresh re-run + cited evidence support it.
- **Never fabricate pre-build artifacts**: missing 03-PATTERNS, Phase-3 UI-SPEC,
  04-CONTEXT/PATTERNS are *recorded as accepted gaps*, not retro-written fiction.
- **The loop reviews; it does not refactor.** Real bugs found → backlog + surfaced to JJ,
  fixed in separate gated changes. Only allowed code write: one new guard test.
- Config toggles are forward policy — backfill artifacts, don't flip toggles to hide gaps.

## Pre-work (setup, not a round)

- Sync local checkout: pull integration branch (PR #8 is merged on GitHub; local is
  behind), branch `loop/2026-07-02-deep-review` off it. All rounds commit+push there;
  the whole effort lands as **one client-readable PR into the integration branch**.
- Create loop state file `.planning/loops/2026-07-02-deep-review/STATE.md`:
  frontmatter `round: 0 / total_rounds: 10 / pace: <JJ's choice> / interval / next_action`
  + a round-log table. **Resume contract:** on any wake/restart, read this file; if
  `round == 10` → stop. This survives compaction/restarts (tonight proved restarts real).

## The 10 rounds

Per-round ritual: deep review → write artifact(s) → commit + push → increment STATE round
counter + log row → one-line plain-terms report to JJ (artifact link first).

| # | Layer reviewed deeply | Artifact(s) written |
|---|---|---|
| 1 | Phase 1 loader (`swimlane.py`: coverage identity, Hole-B, abstraction guard, `[config]`) | `01-VERIFICATION.md` + `01-VALIDATION.md` + `01-LEARNINGS.md` |
| 2 | Phase 2 composer (`compose.py`: Δ contract, Holes A+B, no-auto-publish, ledger) | `02-…` triad |
| 3 | Phase 3 module-a (render, honesty panel, `--corpus module`, byte-stable) | `03-…` triad + accepted-gap records (PATTERNS, UI-SPEC) |
| 4 | Phase 4 voice (ship dispatch contract, guards) | `04-…` triad + accepted-gap records (CONTEXT, PATTERNS) |
| 5 | Semantic spine + trust invariants cross-phase, re-run on merged HEAD | `.planning/reviews/2026-07-02-deep-review/05-trust-invariants.md` |
| 6 | GSD machinery + config-toggle reconciliation (verifier/nyquist/code_review/security/ui promised vs ran) | `06-gsd-config-reconciliation.md` (+ toggle-change recommendations for JJ, not unilateral flips) |
| 7 | Tests-as-promises inventory (map every guard test → invariant; find unguarded promises) | `07-tests-as-promises.md` |
| 8 | Docs/compass coherence — fix STATE contradictions (stopped_at, metrics, todos ref), ROADMAP Phase-3 checkboxes + Phase-4 plan list, WHERE-WE-ARE catch-up entry, RETRO entry ("shipped ≠ closed" lesson) | in-place edits |
| 9 | **Collaboration contract** — CLAUDE.md §2 roles subsection + `docs/collaboration.md` (full contract) + `tests/test_collaboration_contract.py` (presence guard, mirrors the voice guard) | contract files + guard |
| 10 | Milestone close + synthesis: `/gsd-audit-milestone` (VERIFICATIONs now exist) → `/gsd-complete-milestone` (PROJECT evolution: Active→Validated, Key Decisions outcomes; MILESTONES.md; archive ROADMAP/REQUIREMENTS/phase dirs to `.planning/milestones/`; RETROSPECTIVE.md; STATE final; tag per JJ's answer) → loop terminates (round==10, no reschedule) | close artifacts + synthesis |

## The collaboration contract (round 9 content)

**Roles (newsroom-consistent; "user" retired):**
- **Editor-in-Chief — JJ**: owns intent, sets pace, approves through the review gate into
  the public square; stop authority, always.
- **<Claude's title — JJ picks>**: owns execution coordination, keeps time, runs the
  subagent reporters; reports in plain terms.
- Existing terms mapped, not overloaded: operator (deployer), reviewer (the approval act),
  author, reader, practitioner.

**docs/collaboration.md sections:** Roles & mapping · The intent/pace/time split · Pace
signals + reporting cadence · Review surfaces (the reviewer is a client being taught) ·
One-click artifacts (visual deliverable ⇒ deploy it) · Approval gates (interactive until
trusted; mirrors Draft›In Review›Published) · Stop-and-teach + why-before-what · How this
contract changes (a truth change is a conversation, not a commit).

**Guard:** `tests/test_collaboration_contract.py` asserts the role terms + load-bearing
bullets are present in CLAUDE.md + docs/collaboration.md (presence check, not prose
police) — a reverted contract is a RED suite, per the repo's own hardened rule.

## Files touched (representative)

- `.planning/phases/0{1..4}-*/NN-{VERIFICATION,VALIDATION,LEARNINGS}.md` (new, 12 files)
- `.planning/reviews/2026-07-02-deep-review/0{5,6,7}-*.md` (new)
- `.planning/loops/2026-07-02-deep-review/STATE.md` (new — loop memory)
- `.planning/{STATE,ROADMAP,PROJECT}.md`, `WHERE-WE-ARE.md`, `RETRO.md` (reconciliation)
- `CLAUDE.md` §2 + `docs/collaboration.md` + `tests/test_collaboration_contract.py` (new)
- Round 10: `MILESTONES.md`, `.planning/milestones/v1.1-*`, `.planning/RETROSPECTIVE.md`, tag
- Reused machinery: `workflows/extract-learnings.md`, `audit-milestone.md`,
  `complete-milestone.md`, `templates/verification-report.md` — invoked, not modified.

## Verification (end-to-end)

1. Full enforced gate set on the final HEAD: pytest (622 + new guard), lint-imports,
   `newsletters check` ×3 corpora, byte-stable double-render — doc/test additions broke nothing.
2. `audit-milestone` returns passed (4/4 VERIFICATIONs, 12/12 requirements, nyquist known).
3. Guard has teeth: temporarily revert a contract line → suite RED → restore (proven, like the voice guard).
4. Provenance audit: every retroactive artifact cites evidence; every accepted gap recorded.
5. Compass coherence: WHERE-WE-ARE / STATE / PROJECT / ROADMAP / MILESTONES agree; no dangling wakeup/monitor; loop STATE shows 10/10.

## Decisions (answered by the Editor-in-Chief, 2026-07-02)

1. **Bureau Chief** confirmed as Claude's role title.
2. **Continuous, now** — start with round 1 immediately.
3. **Roles are hats, not people** (amendment): the contract defines transferable POSITIONS
   — Editor-in-Chief, Bureau Chief, maintainer, contributor, operator, reviewer, author,
   reader — any collaborator can hold different ones per project. Main/tag ownership
   belongs to the **maintainer role** (JJ holds it here). Tag v1.1 on the integration
   branch; the audit effort lands as one PR into integration; maintainer merges to main.

## Amendments from the Editor-in-Chief's answers

**A. Total-history rigor + ontological/semantic drift.** The review treats the repo "in
the totality of its history": every round examines its layer's git/PR history, and
Round 8 expands from "docs/compass coherence" to **"Ontology, semantic drift & compass
coherence across the repo's whole history"** — mining commits/PRs for term evolution
(known candidates: "promotion"→"fan-out" rename, the three-state-axes terminology guard,
persona renames Founder→Architect/Maintainer→Engineer, Signals↔Newsletters naming, v1.0
phase numbering vs the web/ build's conflicting "Phase 0–5" numbering) → captured in
`08-ontology-and-drift.md` + compass fixes.

**B. "Everybody learns everywhere all the time"** becomes a canonical stated intent in
docs/collaboration.md: users, maintainers, contributors, the codebase, systems, and
documentation are all learners; the 10-round loop is dogfooding that intent (the project
reviewing itself with its own honesty rules — storytellers, truth tellers).

**C. Stateful, fresh-session-resumable setup (context budget is real).** The ideal setup:
- Persist THIS PLAN into the repo: `.planning/loops/2026-07-02-deep-review/PLAN.md`
  (committed first, before round 1), alongside `STATE.md` (round counter + log) and
  `RESUME-PROMPT.md` — a copy-paste prompt that lets a FRESH session resume the loop at
  whatever round STATE says, with zero dependence on this conversation's context.
- Heavy reading runs in fresh-context subagents per round (one reviewer agent per round,
  returning the artifact draft); the main loop stays lean: dispatch → verify → commit →
  report → advance. Main-context cost per round ≈ verification + bookkeeping only.
- Every round's artifact + STATE update is committed AND pushed before advancing (a
  container restart or compaction loses nothing — proven necessary twice today).
