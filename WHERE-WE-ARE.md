# WHERE WE ARE

> The human compass. Newest entry on top. If you read only this file, you should know where the
> build is, what's decided, and why. Updated whenever the state of the world changes — a stale
> compass is a bug. Machine-state (phases/plans/metrics) lives in `.planning/STATE.md`; this file
> is the plain-language "where + why" it complements.

## Where we are right now

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
