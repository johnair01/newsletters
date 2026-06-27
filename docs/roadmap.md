# Roadmap — phased build plan

Dependency-ordered phases. Each phase is sized to be cut into **atomic plans** (a few tasks
each) and run in a fresh context. Work them in order; within a phase, independent tasks can
run as parallel waves. Each phase lists **acceptance criteria** — validate against them (and
against `design-system.md` / `surfaces.md`) before moving on. Nothing is "done" on the
agent's say-so; a human verifies.

> Legend: ▸ = task. Keep each task small enough to finish and commit in one fresh context.

---

## Phase 0 — Foundations

Establish the repo, the design tokens, and the shared component kit so every later surface
is consistent.

> **Status (2026-06-27): in progress.** `web/` is scaffolded as a Next.js 14 (App Router) +
> TS app and the **"Signals — Navigation & IA" handoff** is being recreated there — a
> front-loaded slice of Phase 0 plus the Phase 0→1/3 seam (global chrome, fan-out switcher,
> claim→evidence provenance, ⌘K palette, Library, Onboarding, the review-gate edge state).
> Tokens are being reconciled onto the `design-system.md` / `design-reference/signals/tokens.css`
> namespace (the visual contract). Do **not** re-scaffold; resume from the token foundation.
> Decision recorded this round: the reader-facing set is **five surfaces** (Report · Article ·
> Newsletter · Show · **Learning**) at the presentation layer — see the note in
> `architecture.md §1`. The shared component-kit atoms named below (`Eyebrow`, `GateBadge`, …)
> are still to be extracted from the inline-styled chrome built for the handoff.

▸ Scaffold the repo per `architecture.md` §4 (`/core`, `/mcp`, `/web`, `/content`, `/docs`).
▸ Stand up the web app (Next.js + TS recommended) with SSR and a no-JS-renders baseline.
▸ Port `design-reference/signals/tokens.css` into the app as the global token layer
  (`:root` + `[data-theme="dark"]`). Self-host DM Serif Display / Instrument Sans / DM Mono.
▸ Build the shared component kit from `atoms.jsx`: `Eyebrow`, `SectionDivider`, `Tag`,
  `GateBadge`, `ProfileChip`, `KpiBlock`, `PromptBlock`, `ThemeToggle`, `Button`,
  `ImgPlaceholder`, icons. Build chrome: `NLNav`, `NLFooter`.
▸ Wire light/dark theming end to end.

**Acceptance:** a blank themed page renders with nav + footer in both themes, no console
errors, tokens match `design-system.md` exactly, components render in a kitchen-sink/storybook
route.

## Phase 1 — The Home (V1)

Ship the approved front door. Highest-value, fully specified, exercises the whole kit.

▸ Build sections 1–8 from `surfaces.md` → Home, in order.
▸ Implement the **personalization demo** with the three personas and the canonical `LETTERS`
  copy from `home.jsx`; `who` state re-renders the letter card with the `sg-fade` entrance.
▸ Implement all responsive collapses (≤980 / ≤720).

**Acceptance:** pixel-matches `Newsletters - Home.html` in light + dark; persona switch
re-cuts the letter; renders meaningfully without JS; Lighthouse a11y ≥ AA.

## Phase 2 — Typed core + the model

The spine everything else depends on. Can start in parallel with Phase 1 (no UI dependency).

▸ Implement `Source`, `Distillation`, `Surface`, `Corpus`, `Claim`, `Trace`, `Review` as
  typed models (Pydantic v2) per `architecture.md` §1.
▸ Enforce the **invariants** in code: no publish without a `Published` review + reviewer;
  every published claim has a trace; corpora never serialized into surfaces/sources.
▸ Expose the package API: `synthesize()`, `Corpus.load()`, `Distillation.render(kind)`,
  `Surface.open_pull_request()` / `.gate`. Make it `pip install`-able and headless-runnable.

**Acceptance:** unit tests cover the invariants (publishing without review fails;
untraced claim is rejected/relegated to `missing[]`); the `synthesize.py` example from
`architecture.md` §2 runs end to end against a fixture event.

## Phase 3 — The content surfaces

Recreate the four reader-facing surfaces in the real stack, reading from Phase-2 models.

▸ **Newsletter** surface (`Signals Newsletter.html`) — standalone weekly letter + per-reader
  re-cut using the Corpus model.
▸ **Article** surface (`Signals Article.html`) — peer-reviewed write-up, traced claims, sticky
  TOC, print/PDF styles.
▸ **Report** surface (`Signals Report.html`) — the structured record / RCA, KPI strips, live
  gate, fan-out.
▸ **Show** surface (`Signals Show.html`) — episode page with chapters + fan-out.
▸ Render every surface with its `GateBadge` driven by the real `Review` state.

**Acceptance:** each surface matches its reference file + tokens; gate state is real, not
hardcoded; Article prints cleanly to PDF; surfaces render from `Surface` objects, not static copy.

## Phase 4 — The publish loop (human in the loop)

Make the gate real: agent drafts, human reviews via PR, merge publishes.

▸ **Ingest:** adapters turn source events into `Source` records.
▸ **Distill:** the agentic-journalist step — LLM call over a structured `Source` + target
  `Corpus`, returning claims with traces (model swappable behind one `distill()` boundary).
▸ **Review:** open the draft `Surface` as a real pull request against `/content`; diff is
  human-readable surface content.
▸ **Publish:** on merge, render final surfaces, write to the Library, schedule per-reader sends.

**Acceptance:** a fixture event flows Ingest→Distill→Review(PR)→Publish; no auto-publish path
exists; published output appears in the Library and as a personalized letter per corpus.

## Phase 5 — Library, corpora & MCP

▸ **Library/Hub** surface (`Signals Hub.html`) as the durable archive + cross-surface nav.
▸ **Private corpus** creation & management; encrypted at rest; never transmitted.
▸ **MCP servers** per source system (APM, traces, logs, RUM, work-order, wiki) so source data
  and corpora stay in the operator's environment.

**Acceptance:** archive lists published surfaces; a corpus round-trips locally encrypted;
the distiller reads sources only through MCP servers (no direct long-lived source creds in core).

## Phase 6 — Open-source release

▸ Slot-marked templating so an operator repopulates surfaces with their own specifics
  (see the project's `handoff/SLOTS.md` for the slot manifest).
▸ MIT license, self-host docs, "no telemetry / renders without JS / WCAG AA" verified.
▸ Working-in-the-open repo hygiene: public history, contributing guide, the spec set kept in
  sync with the code.

**Acceptance:** a fresh operator can clone, repopulate slots, self-host, and publish their
first surface following the README alone.

---

## Cross-cutting (every phase)

- Keep `docs/` in sync with the code; if behavior changes, update the spec in the same change.
- Maintain the visual contract (`design-system.md`) — flat editorial, `--radius: 0`, the
  3px left-accent device, the three-font system.
- Keep the review gate present in model, API, and UI.
- Commit atomically; keep the history legible (working in the open is a product principle).
