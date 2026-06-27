# web/ — Signals surfaces + navigation/IA (Next.js)

The reader-facing surfaces and the navigation/IA layer that connects them, built from
the **"Signals — Navigation & IA"** design handoff (`design-reference/signals-navigation/`).
Stack: **Next.js 14 (App Router) + TypeScript + React**, plain CSS driven by design tokens
(per `docs/architecture.md §4`). No utility framework — the aesthetic is flat editorial,
`--radius: 0`.

## Run

```bash
cd web
npm install
npm run dev      # http://localhost:3000
npm run build    # production build — all routes prerender static
npm start        # serve the production build
```

## What's here

**Routes** (`app/`) — one per view in the handoff:

| Route | View |
|---|---|
| `/` | Home — the fan-out thesis + entry points |
| `/ia` | IA & Patterns — *internal* style reference (sitemap, cross-link graph, switcher + provenance treatment mockups) |
| `/library` | Library — browse by record / topic, filter by review state |
| `/report` `/article` `/newsletter` `/show` `/learning` | the five reader surfaces of one record |
| `/onboarding` | guided reading path (stepper) |
| `/gated` | the review-gate edge state (a Draft surface, held) |

**Global chrome + overlays** (`components/`, mounted in `app/layout.tsx`):
`Nav` (sticky spine, ⌘K jump button, mobile drawer), `Breadcrumb`, `Footer`,
`FanoutSwitcher` (the "See this record as" segmented control — shipped treatment A),
`MarginRail` (sibling surfaces + provenance legend), `EvButton` + `EvidencePanel`
(claim → evidence → back, slide-in — shipped treatment A), `CommandPalette` (⌘K).
`SignalsProvider` holds theme + drawer + palette + evidence state and the global
⌘K / Esc handling.

**Data** (`lib/data.ts`) — typed, route-keyed, server/client-safe: surfaces, nav spine,
crumbs, sitemap, footer, library records, evidence map, onboarding steps, ⌘K jump groups.

## Tokens & theming

The global token layer (`app/globals.css`) uses the **`docs/design-system.md` /
`design-reference/signals/tokens.css` namespace** — the non-negotiable visual contract:
raw `--color-*`, semantic `--bg/--card/--text/--text-dim/--line`, and `--chrome-*` (which
stay dark in both themes). Three tokens are folded in from the Navigation & IA handoff:
`--color-amber-ink` / `--color-accent-ink` (AA text-on-light for the amber/terra surfaces)
and `--ev-bg` (evidence panel). The handoff's own `--blue/--ink/--hairline` names are **not**
used — they were reconciled onto the spec namespace.

Light/dark is driven by `prefers-color-scheme` + a `localStorage` override, applied to
`<html data-theme>` by a tiny pre-paint inline script (no flash). The three font families
(DM Serif Display / Instrument Sans / DM Mono) are self-hosted in `public/fonts` — no
external calls.

## Notes

- Fonts, content, and the framed viewport render server-side; interactive layers (palette,
  drawer, evidence panel, theme) enhance progressively — core content reads with JS disabled.
- The prototype's harness toolbar (Desktop/Mobile/View/Theme switches) is intentionally
  **not** ported; view switching is routing and theme is preference-driven.
- Body prose in the surfaces is representative placeholder — the navigation, switching,
  provenance, library, and onboarding **mechanics** are the deliverable.
