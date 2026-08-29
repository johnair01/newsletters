# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.1 — Swim-Lane Module Report

**Shipped:** 2026-07-02
**Phases:** 4 | **Plans:** 12 | **Sessions:** 1 build (overnight autonomous) + 1 deep-review loop (10 rounds)

### What Was Built
- A traced YAML loader (`swimlane.py`) — config → verbatim-transcript `Source` + `SectionBinding[]`,
  every scalar addressed or disclosed under a coverage identity enforced in code.
- A pure module-scope composer (`compose.py`) — byte-stable Draft REPORT `Surface`, compute-time Δ,
  Holes A + B closed at the composer, no-auto-publish proven.
- A worked synthetic `module-a` corpus rendered into a self-contained `content/module/` Library with
  its own R-001 ledger, gate-visible and byte-stable.
- A Signals-voice `ship` contract — six-section evidence-first PR dispatches, gate output verbatim,
  guarded against silent installer reversion.

### What Worked
- **Guards with teeth out-performed plans.** The abstraction guard (LANE-03) fired **3× on real
  leaks** — including catching the *plan's own suggested defaults* (`content/module/module-a.yml`,
  a CLI docstring) a whole phase after it was written. A rule encoded as an executable test
  out-enforced planning: the plan was fallible, the rule was not. This is the milestone's headline win.
- **Adversarial "prove-it-fires" guards.** Every load-bearing invariant (Holes A/B, no-auto-publish,
  synthetic-content scanner, bare-install-yaml-blocked, the module merge-gate blocker) plants a
  violation and proves rejection — a green positive alone would be vacuous.
- **The product's own review loop, dogfooded, closed in ~19 minutes.** PR #7 (hype fix, five
  sections) merged 03:59; PR #8 (audience fix, the "Start here" client section) merged 04:18 — the
  Editor-in-Chief's "I don't understand what the shit is going on" turned into an amended, guarded
  contract + a sixth test + a Pages deploy, same session. Draft › Review › act, applied to the tooling.
- **One mind, end-to-end coherence.** The composer design held across four phases in one night; the
  mid-phase semantic corrections (the Δ-contract's three forms) were made in flight.

### What Was Inefficient
- **Independence was spent for speed.** The autonomous run kept GSD's *roles* but absorbed the
  *verify* and *ship* steps inline. The verifier's value is a **second** pair of eyes; when the
  builder verifies itself, a self-consistent blind spot survives — e.g. `test_compose.py`'s fixture
  drifted from the loader's actual emission (`efb635a`) and no test caught it, because the suite was
  self-consistent with the builder's own frame. The "required, must not be skipped" `code_review_gate`
  silently did not run.
- **Shipped ≠ closed.** All 4 phases were built, verified-inline, and merged (PRs #4–#8) — but with
  **no per-phase VERIFICATION/VALIDATION/LEARNINGS, no MILESTONES.md, no retrospective, no archive,
  no tag**, and a compass carrying internal contradictions (STATE frozen mid-Phase-2; ROADMAP
  Phase-3 checkboxes unticked; the ROADMAP five-section criterion vs the shipped six). "Green tests +
  merged PRs" *felt* like done, so the GSD close ritual — the part that produces the *learning*
  artifacts — was silently skipped.
- **The stall.** A background CI-wait gated forward progress and died to a container restart — the
  exact failure class (`a completion notification is not liveness`) already hardened in 2026-06-18,
  violated again: unauthenticated `curl` that returns empty here, on a docs-only head commit that
  never triggered CI. JJ caught the silence. Merge sequencing must be synchronous through the
  authenticated channel, never a background wait.
- **Drift as a speed artifact.** The persona rename happened twice in one afternoon; the sixth
  dispatch section landed 19 min after the fifth without touching the ROADMAP; STATE froze mid-Phase-2
  while the run finished all four. Language lagged reality not from confusion but from moving faster
  than the paper trail.

### Patterns Established
- **Rule-as-test out-enforces planning** — a hardened denylist/guard holds against every future edit,
  including the plan's own defaults; the right response to a firing guard is to make the source *more*
  abstract, never to relax the guard.
- **Guard-test-over-managed-markdown** — enforce a prose contract that lives in an installer-owned
  file (`.claude/gsd-core/`) with a pytest that asserts headings/order/prohibitions; reversion becomes
  a RED suite, not silent drift. Minted for the voice contract, reused for the collaboration contract.
- **Read-anchored coverage identity** — anchor "no silent drops" to scalars *read*, cross-checked
  against an independent yardstick, enforced by a `RuntimeError`, not asserted in prose.
- **The deep-review loop as the repair pattern** — each round a fresh-context, adversarial mini-cycle
  with its own client-readable PR, reading the *live* object under standing lenses (delta-to-reality /
  drift / total-history honesty) rather than re-checking intent. The merged per-round PR trail *is*
  the review record the inline build never produced.

### Key Lessons
1. **A milestone is done when it is CLOSED per GSD, not when the code is green.** Merged PRs are a
   build signal, not a close signal. (Hardened in RETRO 2026-07-02; this loop is its retroactive
   execution.)
2. **Independent, fresh-context review catches what inline verification structurally cannot** — the
   value it buys is *independence, not correctness*. Self-verification checks the work against the
   builder's own frame, so self-consistent blind spots survive it. Generalises "the agent says
   green ≠ green" from executors to the builder's own verification pass.
3. **Over-firing honesty is also unfaithful.** A disclosure that fires when nothing was promised
   erodes trust exactly as a silent omission does (the Δ-contract's three forms: silent →
   over-disclosing → movement-form-only). The right predicate is "was a promise declared and left
   unmet," not "is an endpoint missing."
4. **The chain's automated teeth are conditional on producer honesty; its unconditional guarantee is
   the human gate.** The faithfulness gate's Option-A fallback passes un-addressed traces; Hole A is
   composer-only. Ready for a *trusted* producer, not an *untrusted* one — harden the DistillPort seam
   before DEF-11.

### Cost Observations
- Model mix: not instrumented this milestone (single-operator autonomous build + loop). Notable: the
  overnight autonomous run outpaced its own bookkeeping — the durable memory that survived was the
  round artifacts + STATE file, not the tooling's live parse.
- Sessions: 1 build + 10 deep-review rounds.
- Notable: GSD state tooling could not parse this milestone's `0N-name` phase-directory format
  (`state.advance-plan` choked; `milestone.complete` emitted a STATE-format warning and produced
  broken one-liner extraction) — the close was hand-authored template-faithfully. Machinery friction,
  not a product defect; reinforces that the human-readable compass must survive a tooling parse gap.

---

## Milestone: v1.2 — The Published Record

**Live:** 2026-07-03 · **Formally closed:** 2026-08-29
**Phases:** 2 | **Plans:** 2

### What Was Built

One publish channel: `publish.assemble_site` composes committed corpus bytes verbatim into the
published tree; four invariants (links/drift/fonts/marker) run as the PR-blocking `site-integrity`
job; `deploy-pages.yml` gate-checks then force-pushes `gh-pages` from `main` only. Plus the
cross-corpus Records strip + design-system 404 (no surface a dead-end), and — in the same window —
the `web/` preview fix (round 2) and the Case Spec authoring path (PR #24).

### What Worked

- **Live forensics over repo belief.** The milestone was born from curling the live site and
  reading the Actions history — the repo's own record believed the site was fine. Diagnose the
  live object, not the repo's intent.
- **The new assembled-tree test caught a real live bug (`home_href` dead nav) on its FIRST run** —
  the strongest possible argument for testing the assembled artifact, not the parts.
- **Choosing the proven channel (branch force-push) over the fashionable one** (environment
  deploys, 4/4 failures) closed the loop; the fancier channel is DEF-14, a settings decision.

### What Was Inefficient

- The formal close lagged the ship by ~8 weeks — the milestone was live and UAT'd 2026-07-03 but
  not closed until the v1.3 kickoff forced it. A milestone isn't done until the ritual runs.
- Phase dirs carried no SUMMARY.md (PLAN/CONTEXT/VERIFICATION only), so `milestone.complete`'s
  accomplishment extraction came up empty and the close was hand-authored again (same friction as
  v1.1's close).

### Patterns Established

- **Republish committed bytes only** — the deploy step is never a second author.
- **Placeholder data never wears the product's URL** — previews deploy labeled, under the record.
- **File text IS the evidence** for authored specs (Case Spec) — the mechanism v1.3's Weekly Spec
  inherits.

### Key Lessons

1. An automated publish channel is only real once it has succeeded end-to-end from `main` —
   4 failed runs sat unnoticed because nothing watched the watcher; the warn-only preflight +
   site-integrity job now watch it.
2. Close milestones when they ship. A stale open milestone silently blocks the planning state
   (STATE.md pointed at "pages review" for 8 weeks).

### Cost Observations

- Sessions: 2 (build+merge 2026-07-03; formal close 2026-08-29 at v1.3 kickoff)
- Notable: post-merge UAT was live-verified twice (at merge, and at close) at trivial cost —
  curl beats belief.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 (Rev2) | ~6 (autonomous Phases 2–13, cross-AI review at Phase 1) | 14 | Established the trust spine + GSD four-beat loop; cross-AI peer review caught a circular import the in-flow checker passed; silent-drop bugs found + hardened (Phases 4/7) |
| v1.1 | 1 build + 10 review rounds | 4 | Composer bolted on; **the close ritual itself became a deliverable** — a 10-round fresh-context deep-review loop retroactively produced the VERIFICATION/VALIDATION/LEARNINGS + cross-cut reviews that the inline autonomous build skipped. Independence recovered *after* the fact. |
| v1.2 | 2 (build+merge; late formal close) | 2 | Milestone born from live forensics, not a seed; assembled-artifact testing caught a live bug on first run; the close ritual lagged the ship by 8 weeks (lesson: close when shipped) |

### Cumulative Quality

| Milestone | Tests | Import contracts | Zero-Dep / AI-Optional Additions |
|-----------|-------|------------------|----------------------------------|
| v1.0 (Rev2) | 574 (at v1.1 start) | 2 KEPT | AI-optional core, distill socket, 4 format adapters, faithfulness gate, merge gate, Problem entity |
| v1.1 | 626 | 2 KEPT | `[config]` PyYAML lazy boundary (bare install stays yaml-free); loader + composer + module corpus all AI-free |
| v1.2 | 639 | 2 KEPT | `publish.py` stdlib-only, AI-free assembly; deploy gates AI-free; Case Spec path (post-window) zero-AI on the same spine |

### Top Lessons (Verified Across Milestones)

1. **"The agent says green ≠ green"** — verified across v1.0 (executors, planners, the plan-checker
   that passed a circular import) and v1.1 (the *builder's own* inline verification). Independent
   reproduction/review is the compensating control at every scale.
2. **Enforce invariants in CODE, prove by TEST — never in a comment** — the Phase-7 silent-drop, the
   Phase-13 `__setattr__` human-gate loophole, and v1.1's abstraction guard all confirm: a guarantee
   is real only if a bypass attempt RAISES and a test proves it fires.
3. **A completion notification is not liveness; never gate forward progress on a background wait** —
   the 16h stall (2026-06-18) and the CI-wait stall (2026-07-02) are the same class, twice.
4. **No-silent-drops must be anchored to what was READ, not what was emitted** — ported from the
   Phase-7 TMDL parser to the v1.1 YAML loader's read-anchored coverage identity.
