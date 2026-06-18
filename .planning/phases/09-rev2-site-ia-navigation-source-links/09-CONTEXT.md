# Phase 9 — Context & Decisions (Rev2 Site IA, Navigation & Source Links)

**Goal:** Fix the deployed site's information architecture — a real marketing Home separate from a
Library status-board, four real nav destinations with breadcrumbs + prev/next, and every cited source
rendered as a working link — all regenerated from templates (no hand-edited HTML).

**Requirements:** SITE-02 (Home + separate Library), SITE-03 (Library status-board by gate state,
CSS columns, no JS), SITE-04 (4 nav destinations + breadcrumbs + prev/next within a surface type),
SITE-05 (fan-out diagram + every cited source = working link), SITE-06 (all output regenerated from
the renderer/templates; no hand-edited HTML).
**Depends on:** Phase 8 (`Site/Collection/Page`, `by_slug`, stable refs/slugs), the Rev1 renderer
`render.py`, `docs/surfaces.md` (the Home 8-section spec + per-surface specs), `docs/design-system.md`
(tokens), `design-reference/*.html` (the approved look-and-behavior prototypes).

## Scope / target (decisions)

1. **Target = the Python renderer `render.py` → `content/rev1/site/` (the deployed git-backed site).**
   NOT the Next.js `web/` stub (that's a later phase). SITE-06 ("regenerated from the renderer") = the
   render.py templates. Everything is produced by code; no hand-edited HTML.
2. **Recreate the design-reference prototypes in the real stack — do NOT copy the Babel-in-browser
   setup.** `design-reference/Newsletters - Home.html` is the approved V1 Home; the `Signals *.html`
   are the surface look. Match `docs/design-system.md` EXACTLY — tokens, the DM Serif / Instrument Sans
   / DM Mono type system, the flat editorial aesthetic (`--radius: 0`). Visual fidelity is non-negotiable.
3. **Home (SITE-02):** the real marketing Home per `docs/surfaces.md` §"Home — Start here (V1, approved)"
   — the 8 sections (Hero `#start`, … through the fan-out + persona letters). The front door leads with
   the *why*. It is SEPARATE from the Library (its own page/route).
4. **Library status-board (SITE-03):** the archive as a board with columns BY GATE STATE
   (Draft / In Review / Published), using CSS columns (e.g. CSS grid/columns), **NO JS**. Driven by the
   Phase-8 `Site` — `Page.gate` now becomes load-bearing (it was merely carried in Phase 8). Columns are
   gate state; cards are Pages showing `ref`/title/signal.
5. **Navigation (SITE-04):** global nav resolves to FOUR real destinations (e.g. Home / Library /
   <the surface-type hubs or the four nav targets named in surfaces.md> ) with breadcrumbs and
   prev/next WITHIN a surface type (uses `Collection` ordering + `by_slug`). The UI-researcher pins the
   exact four destinations from `surfaces.md`.
6. **Source links (SITE-05):** the fan-out diagram and every cited source render as WORKING links —
   e.g. a claim's `Trace`/source → the repo file (`vision.md` → the file on the repo host), and
   `FanoutLink.href` (currently defined but UNUSED) becomes real anchors. Cited sources in surfaces
   link to their evidence. (This is where the Phases-4–7 "typed-locator" forward note may finally pay
   off — the UI-researcher assesses whether transcript-prefix locators suffice for link targets.)
7. **Template regen (SITE-06):** all of `content/rev1/site/` regenerates from `render.py`; a test
   asserts no file is hand-edited (re-render → byte-stable, or a "generated" guard).

## Hard rules in play
- **Visual fidelity is not optional** — match `docs/design-system.md` tokens + the design-reference
  look exactly. Flat editorial, `--radius: 0`, the three-font system.
- **Specs are source of truth** — `docs/surfaces.md` Home/Library/surface specs govern; update the spec
  in the same change if anything diverges.
- **AI-optional core** — `render.py` stays stdlib-only (no new dep; no AI import). `lint-imports` green.
- **No hand-edited HTML** — everything from templates (SITE-06); prove by regeneration.
- **No auto-publish / gate intact** — the board reflects the real gate states; rendering never changes them.

## Research note → use the UI track
Dispatch a UI-researcher to produce a precise UI-SPEC.md design contract BEFORE planning: extract the
exact Home 8-section structure + copy anchors from `docs/surfaces.md` + `design-reference/Newsletters
- Home.html`; the design tokens (fonts, color roles, spacing, `--radius:0`) from `docs/design-system.md`;
the four nav destinations + breadcrumb/prev-next model; the Library board column model (gate states) +
the CSS-columns/no-JS technique; the source-link/fan-out anchor model (what each cited source links to,
and how `FanoutLink.href` is populated); and the components render.py must emit. Cite files/lines.
Confirm zero new dependency (render.py is hand-rolled HTML strings — no template-engine dep). Record in
09-UI-SPEC.md (or 09-RESEARCH.md). Flag any spec ambiguity (the four destinations; what a source link
targets) and RESOLVE with a recommended default (uninterrupted mode — don't block on the reviewer).
