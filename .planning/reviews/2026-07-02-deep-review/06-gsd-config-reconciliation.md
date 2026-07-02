# Round 6 — GSD machinery + config-toggle reconciliation

**Loop:** 2026-07-02 deep-review, Round 6. **Reviewer:** Claude (Bureau Chief, retroactive).
**Subject:** what `.planning/config.json`'s toggles PROMISED vs what the v1.1 session (Phases 1–4,
PRs #4–#8) ACTUALLY did — read across the totality of the session's history.
**Standing lenses:** delta-to-reality · ontological/semantic drift · total-history honesty.
**Binding scope:** `rounds/R6-SCOPE.md`. **Honesty rule (from PLAN.md §"Design principle"):**
config toggles are *forward policy* — this round **backfills artifacts and records gaps; it never
flips a toggle to hide a gap, and it recommends, never decides.** Every flip below is a
recommendation for the maintainer/Editor-in-Chief.

Evidence base: `.planning/config.json`; the 4 phase dirs' file inventories; the 4 retroactively-written
`0N-VERIFICATION.md` (Rounds 1–4); `04-PLAN.md` frontmatter (`mode: inline`); `.planning/research/`;
`RETRO.md` (2026-07-02); `git log` (PR trail #4–#12); `.claude/gsd-core/workflows/execute-phase.md`
(canonical pipeline) and `references/planning-config.md` (toggle semantics).

---

## 1. Toggle reconciliation table

**Disposition legend:** `backfilled` = the artifact the toggle promised now exists because Rounds 1–4
wrote it retroactively · `accepted-gap` = recorded with rationale, no artifact, no action needed ·
`honored` = config matched reality · `RECOMMEND` = a decision is put to the maintainer (never flipped here).

| # | Toggle (value) | Promise (one line) | What v1.1 actually did (evidence) | Gap | Disposition |
|---|----------------|--------------------|-----------------------------------|-----|-------------|
| 1 | `workflow.research: true` | Run a research agent before planning; per-phase `RESEARCH.md`. | **Milestone** research ran (`.planning/research/{ARCHITECTURE,FEATURES,PITFALLS,STACK,SUMMARY}.md`; git `146879f`…`081271c` "docs(research): v1.1 composer…"). **Zero per-phase `0N-RESEARCH.md`** in any of the 4 phase dirs. | Per-phase research skipped; milestone research honored. | **accepted-gap** — the milestone research covered the composer work end-to-end; phases were small deltas off a locked design. Recorded, not retro-written. |
| 2 | `workflow.pattern_mapper: true` | `gsd-pattern-mapper` writes `PATTERNS.md` mapping new files to analogs before planning. | Ran Phases 1–2 (`01-PATTERNS.md`, `02-PATTERNS.md` exist). **Skipped Phases 3–4** (no `03-PATTERNS.md`, no `04-PATTERNS.md`). | 2 of 4 phases have no PATTERNS. | **accepted-gap** — explicitly recorded in `03-VERIFICATION.md` §Accepted-Gap (singular analog `worksurface.py`, carried in `03-CONTEXT.md`) and `04-VERIFICATION.md` §Accepted-Gap (prose-contract phase, no module to mirror). Honest, not fiction. |
| 3 | `workflow.plan_check: true` | `gsd-plan-checker` validates plans (goal-backward) before execution. | Plans exist and executed clean; **plan-check leaves no persistent artifact** (it's an in-flow gate), so it cannot be confirmed from files. No in-repo evidence it ran per phase. | Unverifiable from disk. | **accepted-gap** — RETRO 2026-06-14 records the in-flow checker's known blind spot (passed a circular import); the loop's own per-round verification is the compensating control. No action. |
| 4 | `workflow.verifier: true` | `gsd-verifier` writes `VERIFICATION.md` after execution (goal-backward). | **No VERIFICATION.md was produced at build time.** All four exist now, each frontmatter/opening line reading *"Retroactive verification (2026-07-02)… fresh gate re-run on HEAD."* | Verifier never ran during the build. | **backfilled** — Rounds 1–4 wrote all four with fresh gate re-runs + evidence citations. This is the loop's core repair. |
| 5 | `workflow.nyquist_validation: true` | Nyquist-inspired validation gates; `VALIDATION.md` coverage-edge audit. | **No VALIDATION.md at build time.** All four now exist, written by Rounds 1–4 alongside the verifications. | Validation never ran during the build. | **backfilled** — Rounds 1–4. **RECOMMEND:** decide whether `nyquist_validation` is worth keeping `true` going forward, or whether the VALIDATION edge-list is better folded into VERIFICATION (it added a second artifact per phase that in practice only the loop produced). |
| 6 | `workflow.code_review: true` (+ `code_review_depth: standard`, `code_review_command: null`) | `execute-phase` step `code_review_gate` (marked **REQUIRED, "must not be skipped"**) auto-invokes the `gsd-code-review` skill → `NN-REVIEW.md`, advisory. | **No `*-REVIEW.md` exists for any phase.** The required gate never ran during the autonomous build. | The single "required" pipeline step that silently did not run. | **accepted-gap** + **RECOMMEND** (see Rec 2) — the deep-review loop is the retroactive substitute (Rounds 1–4 verifications flag anti-patterns: 2 stale docstrings, vacuous config arm, single-config glob). Forward: run `/gsd-code-review` (or `/code-review`) per phase so it is not loop-dependent. |
| 7 | `workflow.security_enforcement: true` (`asvs_level 1`, `block_on high`) | `/gsd-secure-phase` threat-model verification; `execute-phase` prompts for `SECURITY.md` before advancing. | **No `SECURITY.md` for any phase.** Security enforcement never ran. | Security gate skipped. | **accepted-gap** — the spine's threat surface is narrow and *already* lint-enforced: `lint-imports` proves `problem.py` imports no network/external package and core imports no AI (2 contracts KEPT, re-run green every round). Deterministic, offline, no untrusted input at build. **RECOMMEND** (Rec 4): either run `secure-phase` once at milestone close for the record, or set `security_enforcement:false` with this rationale so the config stops promising a gate the project doesn't use. |
| 8 | `workflow.ui_phase: true` + `ui_safety_gate: true` | Generate `UI-SPEC.md` for frontend phases; require a UI safety gate. | **No `UI-SPEC.md` for any phase.** Phase 3 is marked `**UI hint**: yes` in ROADMAP yet produced none. | UI contract skipped where ROADMAP hinted it. | **accepted-gap** — `03-VERIFICATION.md` §Accepted-Gap records it: Phase 3 renders through the **already-specified** Phase-9/10 `render.py` devices (claim-span + honesty panel) with **zero new UI**; a new *corpus* is not a new *surface design*. **RECOMMEND** (Rec 3): a UI-phase policy for content-rendering phases — reuse-of-existing-renderer ⇒ UI-SPEC not required; new visual component ⇒ required. |
| 9 | `workflow.skip_discuss: true` | Skip the discuss phase entirely (no `CONTEXT.md`). | **`01/02/03-CONTEXT.md` all exist**; only Phase 4 (`mode: inline`) has none. Set on via `dfb004e` "lock Stage A — skip_discuss on". | Config says skip, but CONTEXT was produced for 3 of 4 phases. | **accepted-gap / drift-note** — the CONTEXT files were authored by the orchestrator inline (lightweight decisions capture), not via the `discuss-phase` subagent, so `skip_discuss:true` is technically honored (the *subagent* was skipped) while CONTEXT still exists. Minor ontological mismatch: "skip discuss" ≠ "no CONTEXT" here. |
| 10 | `workflow.auto_advance: true` | Auto-advance to the next phase after completion. | Honored — the overnight run shipped Phases 1→2→3 (and 4) in one continuous session (`git log` #4→#7 same night). | none | **honored** |
| 11 | `workflow.human_verify_mode: "end-of-phase"` | Human UAT gate at the end of each phase. | No per-phase human UAT occurred; the build ran autonomously overnight (`autonomous: true` in plan frontmatter). Human review happened **once, retroactively**, the next morning (RETRO friction #3, JJ's live catch). | Per-phase human gate did not fire during the run. | **RECOMMEND** (Rec 5) — this directly contradicts `mode:yolo` (row 15). Reconcile the two: either honor end-of-phase gates (drop yolo for phase boundaries) or set `human_verify_mode` to match the autonomous reality and rely on the CLAUDE.md human gate + PR review instead. |
| 12 | `workflow.tdd_mode: false` | Do not require test-first discipline. | Consistent — tests landed with/after code, though several guards were *demonstrated* red→revert→green (abstraction guard, voice guard). | none | **honored** |
| 13 | `workflow.node_repair: true` (`budget: 2`) | Auto-repair failed plan nodes, ≤2 retries. | No node-failure/repair events in the trail; the mid-phase fixes (`efb635a`, `851ccf5`, `e566bfb`) were orchestrator-authored corrections, not `node_repair` retries. | Not exercised. | **accepted-gap** — nothing to repair; honored by non-occurrence. |
| 14 | `git.branching_strategy: "none"` | Never create branches; all work commits to the current branch (GSD does no branch mgmt). | **Every phase shipped as its own branch + squash-merged PR** (#4–#8), and CLAUDE.md hard-rule is *"Branch + PR only. Never push to main."* Branch names (`loop-r4/phase-4-voice`, `loop/2026-07-02-deep-review`) follow a **human/CLAUDE.md convention**, not GSD's `gsd/phase-{phase}-{slug}` template. | Config says "none"; reality is strict branch+PR-per-phase, governed outside GSD. | **RECOMMEND** (Rec 1) — the branch+PR discipline is real and load-bearing but invisible to config. Decide: (a) leave `none` and document that branching is a CLAUDE.md convention GSD doesn't drive, or (b) set `branching_strategy:"phase"` to encode it — noting GSD's template/merge automation differs from the hand-run `loop-rN/…` scheme actually used. |
| 15 | `mode: "yolo"` | Run autonomously without prompts/gates. | Honored for the *build* (autonomous overnight). But CLAUDE.md's *"interactive until trusted"* + *"human gate between phases"* held for **outward actions**: JJ gated the PR-merge click (RETRO friction #1 — the merge was pending, gates already re-run locally). | yolo vs CLAUDE.md's human-gate rules are in tension; the safety rules won at the publish boundary. | **RECOMMEND** (Rec 5) — reconcile `mode:yolo` + `human_verify_mode` + CLAUDE.md so the *intended* human-gate points are explicit, not emergent from a friction incident. |
| 16 | `ship.pr_body_sections: []` | Append-only project PR-body sections; empty = none appended (core dispatch sections only). | **Honored by design** — Phase 4 PR #7 (`57b79f8`) *deliberately emptied* it, removing 26 lines of fact-asserting fallback boilerplate; the six core dispatch sections now come from `ship.md`, guarded by `tests/test_signals_voice.py`. | none (intentional) | **honored** — `04-VERIFICATION.md` notes the guard `test_config_carries_no_boilerplate_pr_sections` is *vacuously* green while the list is empty (teeth only if a section is re-added) — logged, not a gap. |

**Row count: 16 toggles reconciled** (13 workflow/mode + 1 git + 1 ship + the milestone-vs-phase research split folded into row 1).

**Rollup:** honored 4 (10, 12, 14-partial, 16) · backfilled-by-loop 2 (verifier, nyquist) · accepted-gap 6 (research, pattern_mapper 3-4, plan_check, security, ui_phase, node_repair, skip_discuss) · recommendation-to-maintainer 5 (nyquist, code_review, security, ui_phase, branching + the yolo/human-verify reconciliation).

---

## 2. The process-drift story — roles kept, orchestration absorbed

The v1.1 session ran GSD's **roles** but not GSD's **canonical multi-subagent pipeline**. Read across the
history, the shape is consistent:

- **Ran as subagents (fresh context):** milestone research (project-researcher → `.planning/research/`),
  planning, pattern-mapping (Phases 1–2). These left durable artifacts.
- **Absorbed inline by the orchestrator:** *verify* and *ship* every phase; and **Phase 4 fully inline**
  (`04-PLAN.md` frontmatter `mode: inline (orchestrator-executed, JJ present — small surgical scope)`).
  The canonical `execute-phase` pipeline would have run — after execution — a regression sweep, a
  **required** `code_review_gate` (→ `REVIEW.md`), the **verifier** (→ `VERIFICATION.md`), **nyquist**
  validation (→ `VALIDATION.md`), and a **security** prompt (→ `SECURITY.md`). In v1.1 those became the
  orchestrator's own inline gate-runs plus the PR body — **no independent verifier artifact, no
  code-review artifact, no security artifact, thinner Phase-4 paper trail** (no CONTEXT/PATTERNS/RESEARCH).

**What was gained.** Speed and coherence: one mind held the composer design end-to-end across four phases
in a single night, the mid-phase semantic corrections (the Δ-contract's three forms; the abstraction
guard out-enforcing the plan) were made *in flight* rather than bounced through a subagent round-trip, and
the enforced gates (pytest 623, lint-imports 2/0, `check` ×3, byte-stable render) were genuinely re-run —
"green" was real, just self-reported.

**What was honestly lost.** *Independence.* The verifier's value is a **second** pair of eyes doing
goal-backward analysis; when the builder verifies itself inline, a self-consistent blind spot (a fixture
authored around the code's behavior — exactly the class RETRO 2026-06-18 caught) can pass unseen. No
`REVIEW.md` means the code-quality findings that *did* exist (2 stale docstrings, a vacuous guard arm, a
single-config glob) surfaced only weeks later, in this loop. Phase 4's inline mode left the thinnest trail
of all. And the "required, must not be skipped" code-review gate silently not running is itself the kind of
drift the project's own discipline is meant to catch.

**How the deep-review loop recovers the structure.** The Editor-in-Chief's directive — *each round is a
complete OpenGSD mini-cycle with its own PR* (STATE.md resume contract) — rebuilds the independence that
inline execution spent. Each round runs in a **fresh-context subagent** (no builder memory to be
self-consistent with), re-runs the enforced gates from scratch, writes the missing artifact
(VERIFICATION/VALIDATION/LEARNINGS), and ships it as a **client-readable PR** (#9–#12) that the
Editor-in-Chief reviews and squash-merges. **The merged per-round PR trail *is* the review record** the
inline build never produced — the review gate the product preaches (`Draft › In Review › Published`),
finally applied to the project's own process. This is the honest repair: not pretending the pipeline ran,
but reconstructing its outputs under fresh eyes and recording, per toggle above, exactly which were
backfilled versus accepted.

---

## 3. Recommendations (decision owner: maintainer / Editor-in-Chief — none actioned here)

1. **Encode (or explicitly waive) the branch+PR-only discipline.** It is a CLAUDE.md hard-rule that
   `git.branching_strategy:"none"` renders invisible — either set `"phase"` (accepting GSD's
   `gsd/phase-*` template + merge automation) or add a one-line note that branching is a CLAUDE.md
   convention GSD does not drive. *(Row 14.)*
2. **Run code review as a real per-phase step going forward** — `/gsd-code-review` (or the `/code-review`
   skill) per phase, so review findings do not depend on a once-a-milestone loop. The gate is already
   marked "required" in `execute-phase`; make the practice match. *(Row 6.)*
3. **Adopt a UI-phase policy for content-rendering phases:** reuse of an already-specified renderer ⇒
   `UI-SPEC` not required (record the reuse); any *new* visual component ⇒ `UI-SPEC` required. Phase 3
   was the correct call; write the rule down so it is policy, not improvisation. *(Row 8.)*
4. **Resolve `security_enforcement` to reality:** either run `/gsd-secure-phase` once at milestone close
   for the record, or set it `false` with the lint-imports rationale (offline deterministic spine,
   network-ban already contract-enforced) — stop promising a gate the project doesn't exercise. *(Row 7.)*
5. **Reconcile `mode:yolo` × `human_verify_mode:"end-of-phase"` × CLAUDE.md's human gates** into one
   coherent statement of where humans must approve (outward/publish actions, phase boundaries), so the
   gate points are designed, not emergent from a stall incident. *(Rows 11, 15.)*
6. **Decide whether `nyquist_validation` earns its second artifact:** in practice only the loop produced
   `VALIDATION.md`; consider folding the coverage-edge list into `VERIFICATION.md` or keep it and run it
   per phase. *(Row 5.)*
7. **Give the vacuous voice-guard teeth or note it:** `test_config_carries_no_boilerplate_pr_sections`
   passes vacuously while `pr_body_sections:[]`; add a fixture that exercises the loop body, or annotate
   the known limit. *(Row 16 / cross-ref Round 7 tests-as-promises.)*

---

## Round 6 metadata

- **Full suite re-run for the record (verbatim tail, HEAD on `loop-r6/gsd-config-reconciliation`):**
  ```
  ........................................................................ [ 92%]
  ...............................................                          [100%]
  623 passed in 11.69s
  ```
- **Method:** config read key-by-key → each toggle mapped goal-backward to phase-dir inventories + the
  4 retroactive VERIFICATIONs + the PR trail + `execute-phase.md` (what the canonical pipeline would have
  produced). No toggle flipped; no config edited; recommendations only.

*Reviewed: 2026-07-02 · Bureau Chief, deep-review loop Round 6.*
