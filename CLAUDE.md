# CLAUDE.md — Newsletters

> Project memory for Claude Code. This file is loaded into context at the start of
> every session and after each compaction. Keep it short. It is a **map**, not the
> territory — link out to the deep specs in `docs/` rather than restating them.

## What we are building

**Newsletters** is an open framework and publishing layer that distills structured
knowledge into audience-tuned artifacts — reports, articles, dashboards, and letters —
**drafted by agents, approved by humans, published in the open.** One reviewed record
fans out into four reader-facing surfaces, each re-cut per reader from their own corpus.

The product, the why, and the information architecture live in **`docs/product-spec.md`**.
That is the source of truth for *what* to build. This file governs *how* we build it.

## Build order — read these in sequence

0. `docs/vision.md` — the north star: the city / co-learning economy, what "truth" means here.
1. `docs/product-spec.md` — the why, the four surfaces, the publish loop, personalization.
2. `docs/architecture.md` — the typed semantic model (Source / Distillation / Surface),
   the package API, MCP servers, the chosen tech stack.
3. `docs/design-system.md` — exact tokens, type scale, components. Non-negotiable visual contract.
4. `docs/surfaces.md` — per-view hi-fi specs for every screen.
5. `docs/roadmap.md` — the phased, atomic build plan. **Work phases in order; do not skip ahead.**

## The design references are prototypes, not production code

`design-reference/` holds HTML/React-via-Babel prototypes that show the **intended look
and behavior**. They are pixel-level hi-fi. **Do not ship them as-is and do not copy the
Babel-in-the-browser setup.** Recreate them in the real stack (see `docs/architecture.md`)
using its components and patterns. `design-reference/Newsletters - Home.html` is V1 — the
approved home. The `Signals *.html` files are the four surfaces + the proposal.

## Repository layout (as built)

`architecture.md §4` suggests `/core /mcp /web /content /docs`. As built, the Python core
lives in `src/newsletters` (the importable `newsletters` package, kept where the existing
packaging expects it); the other top-level dirs match the spec:

| Spec dir   | In this repo        | Holds |
|------------|---------------------|-------|
| `/core`    | `src/newsletters/`  | The typed semantic model + package API (`synthesize`, `Corpus`, `render`, the review gate). `semantic.py` is the spine; `models.py` holds the OKR/team sample domain. |
| `/docs`    | `docs/`             | The spec set — source of truth for *what* to build. |
| `/web`     | `web/`              | Next.js surfaces (Phase 0–3). Stub until Phase 0. |
| `/content` | `content/`          | Git-backed published surfaces — the Library. Stub until Phase 4. |
| `/mcp`     | `mcp/`              | One MCP server per source system. Stub until Phase 5. |
| reference  | `design-reference/` | Hi-fi HTML/JSX prototypes — the look-and-behavior contract, **not** production code. |

Build status lives in `docs/roadmap.md`. The semantic spine (Phase 2 models + invariants +
the package-API surface) is implemented and tested; the agentic `distill()` step is stubbed
until Phase 4.

## Conventions

- **Specs are the source of truth.** If code and spec disagree, the spec wins — or you
  update the spec in the same change and say why. Never let them drift silently.
- **Typed everything.** Source, Distillation, and Surface are typed models end to end
  (Pydantic on the core, TypeScript types on the web). Outputs must stay auditable.
- **Human-in-the-loop is load-bearing, not decoration.** Nothing publishes without
  passing the review gate `Draft › In Review › Published`. Keep that gate in the data
  model, the API, and the UI. Do not add an auto-publish path.
- **Strip the proprietary, preserve the personal.** Org names, system names, and metrics
  are configurable. The practitioner's voice and reasoning in sample content is the point —
  keep it.
- **Open by default.** MIT, self-hostable, no analytics or external calls baked into the
  product. Private corpora stay local and encrypted.
- **Visual fidelity is not optional.** Match `docs/design-system.md` exactly — tokens, the
  DM Serif / Instrument Sans / DM Mono type system, the editorial flat aesthetic (no
  rounded corners, `--radius: 0`). When in doubt, open the reference file and match it.

## Definition of done (per task)

- Matches the relevant section of `docs/surfaces.md` and the design tokens.
- Typed, with the review gate intact where applicable.
- Renders/serves with no console or server errors.
- Spec updated if behavior changed.

## Using GSD

This repo is set up to be driven by **GSD (Get Shit Done)**, the spec-driven Claude Code
workflow. See **`GSD.md`** for install and the phase loop. The short version: GSD runs
research/planning/execution in fresh-context subagents and treats `docs/` as the spec it
plans against. Point it at `docs/roadmap.md` and let it cut atomic plans per phase.
