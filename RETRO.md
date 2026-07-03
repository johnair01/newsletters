# RETRO — friction log & hardened rules

> Log friction honestly — name mistakes, don't paper over them. Each durable fix becomes a rule
> (in `CLAUDE.md`) or a guard, not a vibe. A recurring friction you haven't hardened is a bug.
> Newest on top.

## 2026-07-03 — The published site rotted because publishing had three channels and zero tests

**Friction observed**

Live forensics (v1.2 research doc) found the "deployed" site was a 2-week-stale *hand-pushed*
`gh-pages` snapshot; the automated workflow built a DIFFERENT site (the placeholder `web/` app)
and had failed 4/4 runs — **including run #3 from `main`**, which invalidates the "merging to
main will deploy" assumption the two-gates entry below left standing; and no test anywhere saw
the *assembled* tree, so `/module/…` 404'd live and every work/module page's "Start here"/Home/
fan-out link pointed at a nonexistent corpus-local `index.html`. Each corpus was individually
green; the composition was broken. The repo's own record believed the site was fine.

**Rules hardened**

- *One publish channel, and it republishes only what a human already merged.* The deploy
  workflow re-runs the merge-block gate and the byte-drift checks over the **committed**
  corpora, assembles via the same tested function everything else uses (`publish.assemble_site`
  — never ad-hoc `cp` in YAML), and pushes through the channel with the fewest invisible gates
  (single-commit force-push to `gh-pages`: one visible `contents: write` permission, no
  environment allowlist). Manual `gh-pages` pushes are retired.
- *Test the composition, not just the parts.* The published tree is a first-class test subject
  (`tests/test_publish.py`, PR-blocking): assembled-tree link resolution, committed==fresh for
  ALL corpora, fonts-present, generated-marker. The assembled-tree link test caught the live
  dead-nav bug on its first run — a per-corpus test structurally never could.
- *A "next step: publish" left manual will silently rot.* The 6/19 UAT snapshot was correct the
  day it was pushed and wrong within two weeks. If publishing is a standing intention, it must
  be a workflow, not a memory.

## 2026-07-02 (late) — Pages deploy: a workflow change cannot see a repo-settings gate

**Friction observed**

PR #8 extended the Pages workflow to publish the report corpora and to deploy from the
integration branch — the build succeeded, but the DEPLOY job was rejected: the
`github-pages` environment's protection rule (Settings → Environments, a repo setting,
invisible to the workflow file and to CI) only allows deployments from approved branches.
The /reports/ URLs 404'd while every gate we could see was green; found only when the
Editor-in-Chief asked for the preview.

**Rule hardened**

- *An outward-facing deploy has TWO gates: the workflow (in-repo, we can change it) and
  the environment protection rule (repo settings, maintainer-only).* When shipping a
  deploy-from-a-new-branch change, verify the environment allowlist covers that branch —
  or state plainly in the PR that the maintainer must allow it / merge to an allowed
  branch before the deploy can land. "The workflow is correct" ≠ "the deploy will run."

## 2026-07-02 — Session: v1.1 overnight run (Phases 1–3 shipped; one stall JJ caught live)

**Friction observed**

1. **A background CI-wait stalled the run — three compounding mistakes in one decision.** After
   shipping PR #6's body I gated the merge on a *backgrounded* poll loop: (a) the container
   restarted and killed it — the EXACT failure class already hardened in the 2026-06-18 entry
   ("a completion notification is not liveness"), violated again; (b) the loop used
   unauthenticated `curl` to api.github.com, which returns empty in this environment, so it
   could never succeed; (c) the head commit was docs-only and never triggered CI at all —
   zero check runs would ever appear. JJ caught the silence and flagged it. The gates had
   already been independently re-run locally; only the merge click was pending.
2. **Recurring smaller class, positive note:** the abstraction guard (LANE-03) fired three times
   tonight on genuine leaks (a planned default path, a CLI docstring, a planted self-test) — a
   rule encoded as a test did its job repeatedly where a convention would have silently rotted.

**Friction observed (morning review, from JJ directly)**

3. **The PRs fixed hype but not audience.** The Signals dispatch removed boilerplate and tied
   claims to evidence — and was still unreadable to the person it was for: "I don't understand
   what the shit is going on." The bodies assumed a co-engineer; the reviewer is a CLIENT being
   taught. And the deliverable (the rendered report) wasn't one click away — the Pages deploy
   only published the web app, never the report corpora, so "review" meant reading diffs.

**Rules hardened**

- *The reviewer is a client being taught.* Every PR body now MUST open with a plain-terms
  "Start here" section — what we built / why it matters to you / how to review with clickable
  links, the rendered artifact first. Encoded in ship.md's generate_pr_body + enforced by
  `tests/test_signals_voice.py` (a reverted contract is a RED suite, not a vibe).
- *If the deliverable is visual, deploy it.* The Pages workflow now publishes the rendered
  corpora at `/reports/{rev1,work,module}/` alongside the web app — a review link, not a diff.
- *Never gate forward progress on a background wait.* At a decision point, check external state
  SYNCHRONOUSLY through the authenticated channel (GitHub MCP tools here — plain curl to
  api.github.com is dead in this environment), act on what you find, and move on. Background
  monitors are for *notification*, never for *sequencing*.
- *Before waiting on CI, confirm CI was actually triggered for that SHA* (docs-only commits may
  not trigger it). Waiting on a run that doesn't exist looks identical to a slow run.
- *When local enforced gates are green and CI's jobs are a strict subset of what was re-run
  locally, a docs-only head commit does not block the merge* — verify the post-merge run on the
  integration branch instead.

**Friction observed (deep-review loop, rounds 1–8)**

4. **The milestone shipped functionally but was never formally closed per GSD.** All 4 phases were
   built, verified, and merged (PRs #4–#8) — but there were **no per-phase VERIFICATION/VALIDATION/
   LEARNINGS**, no `MILESTONES.md`, no retrospective, no archive, no tag, and STATE/ROADMAP/PROJECT
   carried internal contradictions (STATE frozen mid-Phase-2 with a "3 plans" metrics table; ROADMAP
   Phase-3 checkboxes unticked and Phase-4 "Plans: TBD"; the ROADMAP five-section criterion vs the
   shipped six-section dispatch). "Green tests + merged PRs" felt like "done", so the GSD close ritual
   — the part that produces the *learning* artifacts — was silently skipped. Shipped ≠ closed.
5. **A self-verifying builder cannot see its own self-consistent blind spots.** The overnight run
   verified every phase against its own plan and passed — yet the drift above (and the R5 "weakest
   link", the R7 unguarded arms, the R8 ontology drift) was invisible to that inline verification
   *because it was self-consistent with the builder's own frame*. It took a **fresh-context, adversarial
   deep-review loop** — reading the live repo with standing lenses (delta-to-reality / drift / total-
   history honesty) rather than re-checking intent — to surface what the builder could not see about
   itself. The code enforces its ontology in tests, but the tests prove enums/verbs disjoint, not the
   *prose*; only an outside read caught the compass still saying "promotion chain".

**Rules hardened**

- *A milestone is not done when the code is green — it is done when it is CLOSED per GSD.* Before
  declaring a milestone complete: per-phase VERIFICATION/VALIDATION/LEARNINGS exist, the compass
  (STATE/ROADMAP/PROJECT/WHERE-WE-ARE) is internally consistent with the live repo, and the
  `audit-milestone → complete-milestone` ritual (archive + RETROSPECTIVE + tag) has run. "Merged PRs"
  is a build signal, not a close signal. (This loop is the retroactive execution of that rule.)
- *Independent, fresh-context review catches what inline verification structurally cannot.* Self-
  verification checks the work against the builder's own frame, so self-consistent blind spots survive
  it. For anything load-bearing (trust invariants, ontology, the promise ledger), run a fresh-context
  review that reads the LIVE object with adversarial lenses — the value it buys is *independence, not
  correctness*. (Generalises "the agent says green ≠ green" from executors to the builder's own
  verification pass.)

## 2026-06-19 — Session: autonomous Phases 8–13 (the cut to UAT)

**Friction observed**

1. **A "sole-mutator" claim that a mutable model didn't enforce.** Phase-13's `Problem` documented
   "transition is the only way state changes" + a human-gated guarantee — but it was a default-mutable
   pydantic model, so `p.state = VERIFIED` bypassed the actor check, the ladder, AND the log. The
   verifier's adversarial probe caught it. Same CLASS as the Phase-7 silent-drop: **a comment/claim
   that the code doesn't actually enforce.** (Also recurred smaller: Phase-9 stale-green — gates run
   before content regen; Phase-12 a publish() attempt the merge-gate correctly blocked.)
2. **A planner subagent died mid-write, leaving truncated + uncommitted plans** (Phase 12). Caught only
   because I audited the plans against the locked decisions and found render+dogfood uncovered + a
   truncated 12-03. The "agent says green ≠ green" rule applied to a *planner*, not just executors.

**Rules hardened**

- *Enforce invariants in CODE, prove by TEST — never in a comment.* A trust guarantee (human-gated, no
  silent drops, faithful, no auto-publish) is real only if a bypass attempt RAISES and a test proves it.
  `Problem.state`/`log` are now `__setattr__`-guarded; the adversarial "try to bypass it" probe is now
  part of verification, not optional. Generalises the Phase-7 lesson to ALL claimed invariants.
- *Audit a returned plan against the locked decisions before executing* — a plan set can be thin or
  truncated (dead subagent). Re-plan/extend to full coverage; don't execute an under-scoped plan.
- *A completion notification is not liveness; gates run AFTER content regen; push every task* — carried
  forward from the 16h stall and reconfirmed across these phases.

## 2026-06-18 — Session: autonomous Phases 5–7 (+ a 16h stall + a silent-drop bug)

**Friction observed**

1. **Background agents stalled silently for ~16h (container idle-reclaim).** Two parallel Phase-7
   Wave-1 executors were dispatched; the remote container was idle-reclaimed while they were
   mid-flight, killing them AND the completion notifications I was waiting on. 07-02 had committed its
   RED test but not `_pbir.py`, so the suite was broken at collection. I sat waiting on notifications
   that would never arrive until the user flagged "16 hours." **Root cause:** trusting the completion-
   notification channel as liveness; it's only live while the container is.
2. **A real silent-drop bug, authored INTO the proof corpus.** The Phase-7 verifier caught that
   `_tmdl.py` didn't know the `model` object type (nor `ref table` lines), so `model.tmdl`'s header +
   `culture`/`defaultPowerBIDataSourceVersion` + table refs were READ then dropped with no unit and no
   `unextracted[]` disclosure — violating the #1 invariant. Worse, the golden test's identity
   (`claims + misses == units`) structurally *couldn't* see it (the dropped lines never became units),
   and `_author_fixtures.py` literally documented "ref lines, which the parser skips" — the corpus was
   authored to match the bug.

**Rules hardened**

- *A completion notification is not a liveness check.* When a background agent has been quiet far
  longer than its peers took, STOP waiting and diagnose the LIVE repo (git log timestamps, run the
  suite) — don't trust silence. Commit+push after EVERY task so a reclaim can never lose work (now in
  every executor brief). Recovered 07-02 inline from its committed RED test rather than re-dispatching.
- *No-silent-drops must be anchored to LINES READ, not units emitted.* A coverage identity over
  emitted units cannot catch a line that's read and dropped before becoming a unit. Parsers now
  DISCLOSE any orphan/unrecognized line (`unparsed:` signal → `_R_TMDL_UNPARSED`), and golden suites
  assert zero `unparsed:` over the corpus + positively anchor previously-leaked content
  (`test_no_line_is_read_but_undisclosed`). Generalises the Phase-4 "verify the persisted object"
  rule to "verify against the SOURCE lines, not just the parser's output."
- *A proof corpus authored around a bug proves nothing.* Treat "the parser skips X" notes in fixtures
  as a red flag, not a given.

## 2026-06-17 — Session: autonomous Phases 2–4

**Friction observed**

1. **Adapter coverage drops are not reconstructable from the `Source` — a silent-drop-on-round-trip.**
   Phase 4's `EmailAdapter` holds its U1–U7 `unextracted[]` entries in an in-memory dict keyed by
   `source.id`. The Phase-4 verifier proved live that persisting a `Source` (JSON round-trip) and then
   calling `distill()` on a *fresh* adapter instance **silently loses the forwarded-rfc822 (U1) drop
   and reports `complete=True`** — a direct violation of the "no silent drops" invariant, just outside
   the same-instance `parse()→distill()` flow the golden test exercises. Body claims still mint
   faithfully, so it didn't block Phase 4 — but **Phases 5/6/7 will copy this adapter pattern**, so the
   flaw would replicate ×3 if not hardened at this fork.

**Rules hardened**

- *Adapter coverage must be reconstructable from the `Source`, not adapter memory.* Before replicating
  the adapter pattern (Phase 5 Excel), the coverage/`unextracted[]` for a `Source` must travel with the
  `Source` (or be recomputable from it), so re-distilling a persisted `Source` cannot silently report
  `complete=True`. **Folded into Phase 5 as task zero** + a round-trip coverage-parity test added to the
  conformance/golden pattern (fresh-adapter `distill()` of a persisted `Source` must equal the original
  coverage). Tracked in `WHERE-WE-ARE.md` (Phase-4 close note).
- *Verify the persisted/round-trip path, not just the same-instance happy path.* Golden/conformance
  suites for any extractor must exercise `model_dump_json → reload → re-derive` and assert coverage
  parity — the same-instance test hid this. (Generalises "the agent says green ≠ green" to "the
  in-memory object ≠ the persisted object.")

## 2026-06-14 — Session: plan Phase 1 + cross-AI review

**Friction observed**

1. **The in-flow plan-checker passed plans that contained a real circular import.** The GSD
   plan-checker and source-grounding passes both green-lit Phase 1's plans, which wired
   `semantic.py` to `import from .distill.locators` while `distill/__init__` eager-imports `ports`,
   which imports back from `semantic` — a `semantic → distill/__init__ → ports → semantic(partial)`
   cycle that breaks `import newsletters` and the Rev1 test tripwire. The plan even *asserted* the
   arrangement was "acyclic." Only an **independent cross-AI review** (`/gsd-review`, fresh-context
   opus) caught it — by *reproducing* the cycle with a minimal package mirror, not by reasoning.
2. **The replan's own consistency sweep left one stray.** After the leaf-module fix, `01-PATTERNS.md`
   still had one executor-facing line saying `import ... from .distill.locators` — the exact
   cycle-causing path. Caught by an independent grep for the old path after the planner reported done
   ("the agent says green" applied to the *replan*, not just the original).

**Rules hardened**

- *Peer-review foundational/typed-contract phases before executing* — the in-flow checker reasons
  about plans; it does not run them. For phases that define import structure, an independent reviewer
  that **reproduces** the failure is worth the extra cycle. (Confirmed: review paid for itself here.)
- *Bake a fresh-interpreter import-order check into acceptance criteria* whenever a phase adds a
  module that a core module must import across a package boundary:
  `python -c "import pkg; import pkg.core; import pkg.subpkg"` (both orders) must exit 0. Now in the
  Phase 1 plans; reusable guard for any package with an eager-`__init__` barrel.
- *After a replan, re-grep for the thing you fixed* — a planner's self-reported consistency sweep is a
  claim; verify the old pattern is gone from **all** artifacts (plans, PATTERNS, SKELETON, RESEARCH).

## 2026-06-14 — Session: publish Rev1 → plan Rev2 with GSD

**Friction observed**

1. **Outward/irreversible actions got blocked by the auto-mode classifier** — publishing a public
   GitHub Pages site, pushing branches, writing permission rules, running an agent-chosen installer.
   Each block was *correct*: the trigger was acting on links/scripts without explicit user intent, or
   self-authorizing external code.
2. **Doc/agent claims didn't match the live repo** — the brief (and a research subagent) described the
   Rev1 spine as present "in `src/newsletters/`", but on this branch `models.py` was still the OKR
   stub; the real spine was on another branch. Caught only by checking the live branch.
3. **Ephemeral container kept threatening to eat work** — repeated Stop-hook nudges to commit/push;
   GSD install + planning would vanish on recycle if not pushed.
4. **`AskUserQuestion` rejected a call** — omitted the required `question` field on each item.

**Rules hardened (now in `CLAUDE.md`)**

- *Interactive until trusted* — never auto-approve outward/irreversible or self-permission actions;
  surface to the human, don't fight the classifier.
- *"The agent says green" ≠ green* — verify subagent/doc claims against the **live repo** before
  building on them (rule born directly from friction #2).
- *Commit + push every stage* — the container is ephemeral; unpushed work is lost work.

**Still open**

- Work-surface interview not done → Phase 11 is a shell.
- `DistillPort` exact contract shape is `[OPEN]` → needs a planning-research cycle before Phase 1 code.
- Home 8-section spec needs confirming in writing before Phase 9.
