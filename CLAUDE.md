# CLAUDE.md — Newsletters

> Project memory for Claude Code. Loaded at the start of every session and after each
> compaction. Keep it short — a **map**, not the territory. Link out to `docs/` and
> `.planning/` rather than restating them.
>
> **⏯ ACTIVE RESUME — read [`WHERE-WE-ARE.md`](WHERE-WE-ARE.md) first** (the human compass:
> where we are + why), then `.planning/STATE.md` (GSD machine-state). A stale compass is a bug.

## What we are building

**Newsletters** makes how work gets done **legible** — it turns the messy record of an
organization or codebase into clear, audience-specific stories people can read, trust, and act
on. One reviewed, evidence-traced record fans out into audience-tuned surfaces (report, article,
newsletter, recorded show, learning/onboarding). **Drafted however — by hand, by a borrowed tool,
or by AI — approved by humans, published in the open.** The pipeline is the means; *sense-making
for people is the point.* Turn information into conversation, conversation into action.

The why and the information architecture live in **`docs/product-spec.md`** and **`docs/vision.md`**
(source of truth for *what*). The live plan lives in **`.planning/`**. This file governs *how* we build.

## How we work together (tone — read this, it's load-bearing)

**This is a TEACHING build.** You should understand the work well enough to *own* it, not just
receive shipped code.

- **Why before what.** Explain the reason and the decision a thing serves *before* building it.
  Never move silently. If I start moving without explaining, stop me — that's allowed.
- **No vibing.** "It works" is not the bar; "we understand *why* it works, and why it's built this
  way" is. Don't accept or hand over code neither of us can explain.
- **Hold the truths.** The load-bearing principles live in `WHERE-WE-ARE.md`. Each turn, check the
  work is still honest to them. A change that breaks one is a conversation, not a commit.
- **Keep the compass current.** Update `WHERE-WE-ARE.md` as the world changes. It's the screen that
  survives context resets.
- **Stop on request, always.** "Wait / explain that" → stop and teach. That's the method, not an
  interruption.
- **Review-and-harden at every fork.** At each phase end and significant fork, review the session for
  robustness, encode durable fixes as rules/guards (not vibes), and log friction honestly in
  [`RETRO.md`](RETRO.md) — name mistakes, don't paper over them. A recurring friction you haven't
  hardened is a bug. (This rule generates the others.)

## Execution discipline (learned the hard way — layered on GSD)

- **"The agent says green" ≠ green.** After any GSD subagent or executor reports success,
  *independently* verify before accepting: re-run the definition-of-done gates yourself (tests,
  typecheck, build, lint), and for planning subagents, check their claims against the **live repo**.
  (Canonical example from this build: a researcher claimed the Rev1 spine existed; it was on another
  branch — verifying the live branch caught it.) Run a gate *once* per check; rapid re-runs throw
  transient errors.
- **One dependent change at a time.** GSD parallelism is for *independent* work. When steps have
  hidden dependencies, dispatch → return → verify → *then* dispatch the next.
- **Verify through the sanctioned channel only** — the test suite / the package API — never ad-hoc
  probes or writes against shared infra "just to check."
- **Diagnose the live object, not the repo's intent.** On a live failure, read what's actually
  running and localise with the smallest experiment before proposing a fix. An unverified fix is a vibe.
- **When stdout degrades, verify via file-write + Read.** Don't trust an empty echo.
- **One task, one atomic commit.** Determinism over cleverness. Commit + push — the container is
  ephemeral; unpushed work is lost work.

## Hard rules (non-negotiable)

- **No auto-publish, ever.** A `Surface` reaches `Published` only through the gate
  `Draft › In Review › Published` with a recorded reviewer. Enforced in `src/newsletters/semantic.py`;
  prove it with a test. This is the single most important invariant.
- **Every published claim traces to evidence.** Each claim in a published `Distillation` has ≥1
  `Trace`; unsubstantiated material goes to `missing[]`, is shown to the reviewer, and is never
  published silently.
- **AI-optional core.** `core` imports only stdlib + Pydantic. AI/LLM deps live behind an `[ai]`
  extra, lazy-imported inside the AI backend only; CI fails if any AI import is reachable from core.
  The deterministic spine must run with zero AI.
- **Faithful, not suggestive.** Distill *extracts and traces*; it never editorialises. Emphasis and
  narrative are the human's job (or, later, the configured corpus's).
- **Interactive until trusted.** Never auto-approve sensitive or outward-facing actions (publishing,
  external sends, installs that write config) without an explicit human gate.
- **Secrets live in git-ignored env files; never commit them.** Private corpora stay local + encrypted.

## The compass pattern

Two human-first files at the repo root complement GSD's machine-state, never replace it:

- **`WHERE-WE-ARE.md`** — where we are now (newest on top: shipped / in-progress / not-started), the
  load-bearing truths, and the decisions-and-why log (teaching version). Update it every time the
  state of the world changes.
- **`RETRO.md`** — friction log + the rules we hardened from it.
- **`.planning/STATE.md`** — GSD's machine-state (phases, plans, metrics). The compass complements it.

## Build order — read these in sequence

0. `docs/vision.md` — the north star: the city / co-learning economy, what "truth" means here.
1. `docs/product-spec.md` — the why, the surfaces, the publish loop, personalization.
2. `docs/architecture.md` — the typed semantic model (Source / Distillation / Surface), the package API, MCP servers, tech stack.
3. `docs/design-system.md` — exact tokens, type scale, components. Non-negotiable visual contract.
4. `docs/surfaces.md` — per-view hi-fi specs for every screen.
5. `.planning/ROADMAP.md` — **the current, live build plan (Rev2, 12 phases). Supersedes `docs/roadmap.md` for active work.** Work phases in order; don't skip ahead.

## The design references are prototypes, not production code

`design-reference/` holds HTML/React-via-Babel prototypes showing the **intended look and behavior**
(pixel-level hi-fi). **Do not ship them as-is; do not copy the Babel-in-the-browser setup.** Recreate
them in the real stack using its components. `Newsletters - Home.html` is V1 — the approved home; the
`Signals *.html` files are the surfaces + the proposal.

## Repository layout (as built)

| Spec dir   | In this repo        | Holds |
|------------|---------------------|-------|
| `/core`    | `src/newsletters/`  | The typed semantic model + package API. `semantic.py` is the spine (`Source/Claim/Trace/Distillation/Surface`, the review gate); `models.py` holds the OKR/team sample domain. |
| `/docs`    | `docs/`             | The spec set — source of truth for *what* to build. |
| `/web`     | `web/`              | Next.js surfaces. Stub until its phase. |
| `/content` | `content/`          | Git-backed published surfaces — the Library (`content/rev1/` holds the Rev1 renderer output). |
| `/mcp`     | `mcp/`              | One MCP server per source system. Stub until its phase. |
| reference  | `design-reference/` | Hi-fi HTML/JSX prototypes — the look-and-behavior contract, **not** production code. |
| plan       | `.planning/`        | GSD's live plan: PROJECT / REQUIREMENTS / ROADMAP / STATE / research. |

Current status lives in `.planning/STATE.md` and `WHERE-WE-ARE.md`. The Rev1 spine is merged on this
branch; Rev2 (the distill **socket**, format adapters, AI-optional packaging, the site fix, learning
surface) is the active 12-phase roadmap.

## Conventions

- **Specs are the source of truth.** If code and spec disagree, the spec wins — or you update the spec
  in the same change and say why. Never let them drift silently.
- **Typed everything.** Source, Distillation, Surface are typed end to end (Pydantic on the core,
  TypeScript on the web). Outputs stay auditable.
- **Strip the proprietary, preserve the personal.** Org names, system names, metrics are configurable;
  the practitioner's voice and reasoning in sample content is the point — keep it.
- **Open by default.** MIT, self-hostable, no analytics or external calls baked in.
- **Visual fidelity is not optional.** Match `docs/design-system.md` exactly — tokens, the
  DM Serif / Instrument Sans / DM Mono type system, the flat editorial aesthetic (`--radius: 0`).

## Definition of done (per task)

- Matches the relevant `docs/surfaces.md` section and the design tokens.
- Typed, with the review gate and the hard rules intact where applicable.
- **DoD gates re-run independently** (not trusted on a subagent's "green"); renders/serves with no errors.
- Spec updated if behavior changed; **`WHERE-WE-ARE.md` updated; new friction logged in `RETRO.md`.**

## Working mode / operating loop (non-negotiable)

Every change runs the GSD four-beat loop — **Specify › Plan › Implement › Validate**
(see `GSD.md`) — against `docs/` as the spec. The loop is enforced here, not optional:

- **Branch + PR only. Never push to `main`.** All work lands on a feature branch and merges
  via pull request. There is no direct-to-`main` path — the same discipline the product's
  review gate enforces for content (`Draft › In Review › Published`).
- **Phase-by-phase, with a human gate between phases.** Work `docs/roadmap.md` in order. At
  the end of a phase, **stop and let a human review** before starting the next. Nothing is
  "done" on the agent's say-so (see *Definition of done*).
- **Atomic commits.** One task = one focused commit; keep the history legible (working in
  the open is a product principle).
- **Heavy work in fresh-context subagents.** Cut each phase into atomic plans (a few tasks
  each), sized to finish in one clean context. Research / planning / execution run in
  subagents so the main session stays lean.

If you cannot satisfy this loop for a change, stop and surface it — do not work around it.

## Using GSD

This repo is driven by **GSD (Get Shit Done)** — installed under `.claude/`, plan in `.planning/`.
See `GSD.md`. GSD runs research/planning/execution in fresh-context subagents. Resume a session with
`/gsd-progress` (or `/gsd-resume-work`). Per "Method × GSD": keep GSD's orchestration, but verify each
subagent's output against the live repo before building on it, and run dependent changes one at a time.
