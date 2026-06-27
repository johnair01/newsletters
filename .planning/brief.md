# Newsletters — Project Brief (GSD idea document)

> Seed/idea document for `/gsd-new-project --auto @.planning/brief.md`.
> Distilled from the architect ↔ agent discussion on 2026-06-14.
> **Decision status is marked explicitly: [DECIDED] vs [OPEN].** Treat [OPEN] items as
> discuss-phase questions, not settled scope.

## What this is

**Newsletters** is an open-source framework for **semantic information distillation**: it turns
one reviewed, evidence-traced record into multiple audience-specific communication surfaces
(report, article, newsletter, recorded show). The thesis the project is betting on:

> **The trust-and-publish layer is the product — not the generation.** The value is a
> deterministic, auditable pipeline that collects, structures, traces, reviews, and presents
> information faithfully. AI is an optional accelerator, never an authority.

## Architecture spine (already built — Rev1, in `src/newsletters/`)

- **Typed semantic model:** `Source → Claim(+Trace) → Distillation → Surface`. Every published
  claim links to evidence; unsubstantiated material goes to `missing[]` and is shown to the
  reviewer, never published silently.
- **Review gate:** `Draft → InReview → Published`, enforced in code. **No auto-publish path.**
  Review = a real git PR; merge publishes.
- **Surfaces are presets, not classes:** `report / article / newsletter / show` are configs over
  one parameterized `SurfaceTemplate`. Cadence, personalization, signal color, audience scope,
  and review policy are typed config; only prose is templated. Operators register their own.
- **Promotions (human-gated):** `Claim → KPI` and `Report → Article` (peer-reviewed).
- **Renderer:** emits token-faithful standalone HTML (light/dark, signal colors, gate badge),
  renders without JavaScript, no external calls on content. `newsletters build` writes a Library.

## Key decisions from this discussion

1. **[DECIDED] AI-optional, deterministic core.** The entire spine (capture → structure → review
   → render → fan-out) runs with **zero AI**. AI is one swappable socket at the `distill` step.
   Action: move `langchain` to an optional extra so a fork can run with no AI dependencies.
2. **[DECIDED] Manual capture is first-class, not a fallback.** `capture.py` structures a finished
   work session into a Draft Report deterministically (no LLM). This is the primary path for a
   token-constrained operator.
3. **[DECIDED] Distill is a *socket*, not "the AI step."** One interface — "turn raw Sources into
   traced claims" — with swappable backends: **(a) by hand, (b) borrowed OSS tool, (c) AI.** All
   three emit the same typed `Distillation`; the rest of the pipeline is backend-agnostic.
4. **[DECIDED] Format adapters are the first borrowable backends.** Faithful structured extraction
   from **PowerPoint, Power BI, Excel, Email** (python-pptx, openpyxl, email libs, Power BI
   export). Deterministic and low-token — the common case is "pull the structure already in the
   file"; AI is only for the messy residue.
5. **[DECIDED] Faithful, not suggestive.** Distill *extracts and traces*; it never editorializes.
   Emphasis/narrative is the human's job (or, later, the configured corpus's). This is what makes
   the system auditable.
6. **[DECIDED] Open-core strategy.**
   - **V2 — Newsletters (open source):** the industry play. Speed-first. The framework + distill
     socket + format adapters + faithful-extraction rule. Tells its own story by being built in
     the open.
   - **V3 — PulseIQ (private):** the proprietary layer. Privatized with starting configs; **learns
     over runs from captured usage** (what people actually read/edit); gets smarter; stays
     portable. "Manage by usage, not heavy reasoning."

## Immediate user goal (the work-surface installation)

Install Newsletters on a work codebase. Build the reports **by hand** (token-constrained at work),
document the process, pull it into Newsletters so the Library **shows how the work was done**, then
present it. Order of operations: **design the work-surface picture first, then go hunt for the
data.** Lead a small team / task force; capture the key problems and how they were solved.

## Rev2 design track (related, partially separate)

Fix the deployed site, in the **renderer/templates** (`content/rev1`), so it regenerates correctly:
- **IA split:** real marketing **Home** (the approved 8-section spec) at `index.html`; move the
  **Library** to its own page, reframed as a **status board** (columns by gate state).
- **Navigation:** four nav links → four real destinations; breadcrumbs + prev/next; clickable
  fan-out diagram; cross-links between surfaces.
- **Fix numbering collision:** per-surface IDs (`EP01`, `R-001`, slug, issue/date), not list
  positions.
- **Traceability:** cited sources become real links (e.g. `vision.md` → repo file).
- **Visual:** keep the flat-editorial "Signals" skin; graft on the blog's HTML-artifact patterns
  (live editor/preview, color-coded SVG, kanban-by-gate-state, margin annotations).

## Positioning / prior art

No single OSS project does the whole thing; the slices are proven:
- **Private ingest + grounded answers:** Onyx (formerly Danswer), RAGFlow.
- **Claim→evidence provenance:** GenProve, Valsci, sciwrite-lint (science-focused).
- **Delivery:** listmonk / Keila (send only).
The novelty is the **integration** and the **trust-layer-as-product** thesis.

## Open questions (for `/gsd-discuss-phase`)

- **[OPEN]** Exact shape of the distill socket interface (the backend contract).
- **[OPEN]** Which format adapters to build/borrow first, and how to normalize their output to
  `Claim(+Trace)`.
- **[OPEN]** Rev2 navigation specifics and the Home/Library board design.
- **[OPEN]** The work-surface design (interview the architect to capture it).

## Constraints / non-negotiables

- Self-hostable, MIT, no telemetry, no external calls on content.
- Auditable: every published claim traces to evidence.
- Renders without JavaScript; WCAG AA; full light/dark via tokens.
- Human-in-the-loop by design: no auto-publish, ever.
