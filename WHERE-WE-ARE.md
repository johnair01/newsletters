# WHERE WE ARE

> The human compass. Newest entry on top. If you read only this file, you should know where the
> build is, what's decided, and why. Updated whenever the state of the world changes — a stale
> compass is a bug. Machine-state (phases/plans/metrics) lives in `.planning/STATE.md`; this file
> is the plain-language "where + why" it complements.

## Where we are right now

**2026-06-17 (eve) — Phases 1–3 SHIPPED end-to-end. The trust spine is now formally enforced.**
Running the Rev2 roadmap autonomously (discuss → plan → execute → verify per phase, gates re-run
independently each time, every plan committed + pushed).

- ✅ **Phase 1 — Distill Socket Contract:** one `DistillPort` + registry + zero-AI `ManualBackend` +
  coverage manifest (`unextracted[]`) + conformance suite + the injectable faithfulness seam
  (`FaithfulnessCheck`/`_enforce`). Verified 4/4.
- ✅ **Phase 2 — AI-Optional Packaging Boundary:** core deps cut to `pydantic/typer/sqlmodel`;
  `pydantic-ai` behind `[ai]`; `langsmith/langchain/langgraph` dropped. `.importlinter` forbids
  core→AI; CI (`.github/workflows/ci.yml`) runs a **bare-install** full-pipeline gate + lint-imports
  on every push. This *closed a real leak found in Phase 1* — the bare-install isolation test passes
  strictly (the dev venv's ambient `logfire` pydantic-plugin is the only reason it xfails locally).
  Verified 4/4 (PKG-01..04).
- ✅ **Phase 3 — Content-Addressed Provenance & Faithfulness Gate:** `Trace` now pins SHA-256(full
  source) + char offsets + verbatim span via `Trace.from_source`; **STALE is computed** (live hash ≠
  recorded hash) — editing a source flips dependent claims to STALE, never silent mis-attribution.
  The no-AI **faithfulness gate** (`SpanContainmentFaithfulness`, normalized containment) is defaulted
  at the socket seam so every backend inherits it; unfaithful claims route to `missing[]`, never
  surfaced. Rev1 sample corpus migrated in place (20 traces addressed, 0 stale, build byte-identical).
  Verified 3/3 (PROV-01/02). All stdlib; AI-optional contract stayed green throughout.

**Next step:** Phase 4 — Shared Adapter Normalizer & Email Adapter (smart-discuss → plan → execute).
The faithful-extraction rule lands in one shared `normalize()`; the Email `.eml` adapter is the first
stdlib adapter, minting traces via `Trace.from_source` (so adapter claims are content-addressed and
come under the strict gate automatically).

**2026-06-17 — A2 design pass routed (no code). The roadmap grew two phases.** A `/gsd-explore`
session settled the long-open A1-vs-A2 question: does Signals stay a pure capture→trust→publish
membrane (A1), or add a first-class Problem/Solution lifecycle layer (A2)? **Decision: A2, scoped as
a *legibility layer*, not a tracker.** The hinge was one test — *someone needs to query across
problems* (bottlenecks across modules; the leadership pattern view), and you can't aggregate over
state you don't model. Two new phases appended (don't touch 1–12): **Phase 13 — Problem Lifecycle
Entity**, **Phase 14 — Problem Board Portfolio Surface**. Reqs PROB-01..04 added. Full rationale +
boundary reconciliation: `.planning/notes/a2-problem-lifecycle-decision.md`. Phase 1 is still the
next thing to *execute*.

**2026-06-14 — Phase 1 planned, peer-reviewed, and replanned. Ready to execute (no code yet).**

- ✅ **Shipped:** GSD installed (`.claude/`), full plan seeded (`.planning/`: PROJECT, REQUIREMENTS
  31 reqs, ROADMAP 12 phases, research). Rev1 spine **merged** onto this branch. `CLAUDE.md` rewritten
  to carry the working method (teaching build). This compass + `RETRO.md` created. **Phase 1 (Distill
  Socket Contract) is planned** — 2 plans, 2 waves — then put through an independent cross-AI review
  (`01-REVIEWS.md`), which caught a real **circular import**; the plans were **replanned** to fix it and
  re-verified by the plan-checker. All SOCK-01..05 + D-01..06 covered. The `DistillPort` shape is now
  resolved in the plans (no longer `[OPEN]`).
- ◐ **In progress:** Nothing mid-flight — at the execute/iterate fork for Phase 1.
- ○ **Not started:** Phase 1 **code** (plans ready). The work-surface interview (real content for
  Phase 11) hasn't happened. The Home 8-section spec needs confirming in writing before Phase 9.

**Next step:** `/gsd-execute-phase 1` — plans verified and committed. Wave 1 builds the leaf
`locators.py`, the `DistillPort`/registry/`Coverage` contract, and the zero-AI `ManualBackend`
end-to-end; Wave 2 adds the conformance suite + the hard-rule tests.

## The truths (load-bearing — break one, it's a conversation, not a commit)

1. **The trust layer is the product, not the generation.** Make work legible *and believable* —
   every published claim traces to evidence; nothing publishes without a human.
2. **AI is optional, never an authority.** The deterministic spine runs with zero AI; AI is a
   swappable backend behind one boundary.
3. **Faithful, not suggestive.** Distil extracts and traces; it never editorialises.
4. **Low-token & generic by default.** Cheapest models; format consistency is the lever that keeps
   extraction cheap; manual authoring is the floor. **Agents are interviewers** — of you, your work,
   your codebase. (Refined 2026-06-14 from "manual-first": there *is* AI at work, just budgeted.)
5. **Teaching build.** Understanding the *why* is the bar; "it works" is not.

## Decisions, and why (teaching log — decide once, don't re-litigate)

- **Faithfulness gate scope — "Option A": strict containment only where there's content-addressed
  evidence; un-addressed traces fall back to structural (is-traced)** (2026-06-17, Phase 3). An
  executor caught that the live capture path mints *empty-span* traces, so a strict "claim text must
  appear in span" rule would falsely reject every Rev1/capture claim — violating *faithful-not-
  suggestive* (no false positives). Resolution mirrors the approved STALE rule: **absence of content-
  addressing means "not applicable," never a false verdict.** So the gate has teeth exactly where
  there's a real verbatim span to check, and **self-strengthens** as the pipeline adopts content-
  addressing. *Accepted scope boundary (forward note, not a gap):* claims born on the live `capture.py`
  path get the structural pass until that path is content-addressed — which happens naturally as the
  **adapters** (Phase 4+) mint traces via `Trace.from_source`. Rejected Option B (harden `capture.py`
  now) as scope creep into a phase whose criteria were already met. Verifier confirmed 3/3 criteria in
  live code; the only reason it flagged `human_needed` was to get this scope call on record — now made.
- **A2 over A1 — model the problem lifecycle, but as a legibility layer, not a tracker** (2026-06-17).
  The scattered `problem→owned→solution→promoted` lifecycle gets a first-class `Problem` entity above
  `Source` *because* someone needs to query the portfolio across problems (A1 can't aggregate state it
  doesn't model). The guardrail that keeps it from becoming a second Jira: **no write-back; solving
  stays external** (`semantic.py` boundary holds) — Signals owns record-legibility, not execution.
  → Phases 13–14, PROB-01..04. **Terminology watch:** this adds a *third* state axis; the existing
  "**promotion chain**" decision below names axis-2 (surface fan-out) — that word now collides with the
  axis-3 lifecycle ladder. Resolve naming before Phase 13 code (seed:
  `promotion-terminology-guard.md`).
- **Merge Rev1 in, don't rebuild** — the spine already existed on `claude/magical-einstein-hfd1np`;
  merging (conflict-free) beats duplicating proven work.
- **Distill is a *socket*, not "the AI step"** — one interface, backends: by-hand / OSS tool / AI. This
  is what makes the system AI-optional and the manual path first-class.
- **Format adapters first (PPT / Power BI / Excel / Email)** — deterministic, low-token; pull the
  structure already in the file. AI only for the messy residue.
- **Open-core: V2 Newsletters (this, open) / V3 PulseIQ (private, learns over runs).** Product-line
  versions — *not* the same axis as GSD's 12 phases (which are the current build of V2).
- **Learning/onboarding is a first-class surface** (Phase 12); a connection/relationship-map view is
  **parked** (CONN-01) until after core V2.
- **Adopt the crew working method here** — teaching build, this compass + `RETRO.md`, and execution
  discipline layered on GSD (verify each subagent against the live repo; one dependent change at a time).
- **Design the surface first, then hunt the data** — decide what the artifact should look like, then
  go find the inputs.
- **The engine is one promotion chain** — Sources → Report → Article → Newsletter, each human-gated.
  Grounded in five worked contexts (work quality-events, work weeklies-by-swim-lane, interns, PulseIQ,
  Newsletters itself). See `PROJECT.md` → How it's used.
- **The distill socket has three modalities** — author by hand / generic low-token extraction /
  agentic interview — all emitting one reviewed `Distillation` (Phase-1 decision; see
  `.planning/phases/01-distill-socket-contract/01-CONTEXT.md`).
- **The `Locator` union lives in a top-level leaf `src/newsletters/locators.py`, not under `distill/`**
  — so `semantic.py` can import it (`from .locators`, mirroring `from .templates`) without triggering
  the `distill/__init__` barrel → `ports` → `..semantic` import cycle. Caught by cross-AI review, which
  reproduced the cycle the in-flow plan-checker had missed; guarded now by a fresh-interpreter
  import-order acceptance check on the affected tasks.
- **Generic, not template-specific** — extraction handles formats (PowerPoint, email, …) generically;
  no bespoke per-report parsers.
