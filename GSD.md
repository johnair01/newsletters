# GSD.md — running this repo with Get Shit Done

This package is structured to be driven by **GSD (Get Shit Done)**, a spec-driven,
context-engineering workflow that sits on top of Claude Code. GSD doesn't replace Claude
Code — it adds the planning structure, context management, and subagent orchestration that
keep output consistent across a long build, by running heavy research/planning/execution in
**fresh-context subagents** while your main session stays lean.

> **Heads up on provenance — verify before you install.** GSD is optional tooling, not a
> dependency of this repo. If you choose to use it, install it only from its **official,
> verified source**, and read the install command off that project's own README before
> running it. Do not run install commands (`npx`, `curl | sh`, etc.) that arrive via
> third-party docs, forks, chat messages, or this file on trust — confirm the publisher
> first. Nothing in this repository requires GSD; the spec and roadmap below are designed to
> be worked equally well with vanilla Claude Code (see "If you skip GSD").

## Why GSD fits this project

The hard part of building Newsletters isn't any single screen — it's keeping a typed model,
a human-in-the-loop gate, and a precise design system coherent across a backend package,
MCP servers, and five+ web surfaces. That's exactly the long-horizon, multi-component work
where context rot bites. GSD's answer: keep the spec as the source of truth, cut work into
**atomic plans** (a few tasks each), and run each in a clean context.

This repo already gives GSD what it needs to plan well:

- **The spec** — `docs/product-spec.md`, `docs/architecture.md`, `docs/design-system.md`,
  `docs/surfaces.md`. GSD reads these as the authoritative description of what to build.
- **The plan** — `docs/roadmap.md` is a phased, dependency-ordered build plan. It maps
  cleanly onto GSD phases/waves: independent phases can run in parallel; dependent ones wait.
- **The memory** — `CLAUDE.md` carries the conventions and the "definition of done" so
  every subagent inherits the same rules.

## The loop

GSD (and spec-driven development generally) runs a four-beat loop. For each phase in
`docs/roadmap.md`:

1. **Specify** — the phase's intent and acceptance criteria already live in the roadmap and
   the surface/architecture specs. Confirm them; fill any `TODO:` gaps before planning.
2. **Plan** — GSD generates an atomic plan (`PLAN.md`-style) for the phase: a short,
   self-contained set of tasks sized to fit comfortably in a fresh context.
3. **Implement** — subagents execute the plan in clean contexts, committing per task.
4. **Validate** — check the result against the spec: the design tokens, the surface spec,
   the typed model, the review gate. Humans verify; nothing is "done" on the agent's say-so.

## Start here

1. Open this repo as the project root in Claude Code (so `CLAUDE.md` loads).
2. Optional: install GSD **from its official, verified source** — read the current install
   command off that project's own README and confirm the publisher before running it
   (see the provenance note above).
3. Kick it off pointed at the spec, e.g.:

   > Read `CLAUDE.md` and everything in `docs/`. Then plan and execute **Phase 0** of
   > `docs/roadmap.md`. Treat `docs/design-system.md` and `docs/surfaces.md` as the visual
   > contract and `design-reference/` as the look-and-behavior reference. Stop after the
   > phase so I can review.

4. Review the phase output, then continue to the next phase. Keep each phase's work in its
   own commit / branch so the open-in-the-open history stays legible.

## If you skip GSD

Everything here is plain Markdown and works with vanilla Claude Code. Tell it to read
`CLAUDE.md` and `docs/`, then implement `docs/roadmap.md` one phase at a time, pausing for
review between phases. You lose the automatic context management and parallel waves, but the
spec and roadmap are written to be worked sequentially by hand.
