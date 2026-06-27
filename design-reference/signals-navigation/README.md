# Handoff: Signals — Navigation & Information Architecture

## Overview
**Signals** is a content product built on one idea: a single reviewed *record* fans out into five *reader surfaces* — Report, Article, Newsletter, The Show, and Learning — and every published claim traces back to its source evidence. This handoff covers the **navigation and IA layer** that connects those surfaces: the part of the product that makes the fan-out visible and keeps no surface a dead-end.

It includes:
- A **global nav spine** present on every page (logo, primary destinations, jump-to search, breadcrumb, mobile drawer).
- A **fan-out switcher** for moving laterally between surfaces of the same record.
- A first-class **claim → evidence → back** provenance pattern (slide-in panel).
- A browsable **Library**.
- A guided **Onboarding** reading path.
- A **⌘K command palette** ("Jump to…").

The prototype is a single interactive page covering **9 views**, with light/dark theming and a desktop/mobile responsive frame.

## About the Design Files
The file in this bundle (`Signals Navigation.dc.html`) is a **design reference created in HTML** — a working prototype that shows the intended look, layout, and interaction behavior. **It is not production code to copy directly.** It is authored in a lightweight in-house template runtime (`support.js`, plus the `<x-dc>` / `<sc-if>` / `<sc-for>` tags and the `Component` logic class). That runtime exists only to make the mock interactive and should **not** be ported into your codebase.

Your task is to **recreate these designs in your target environment** (React, Vue, Svelte, SwiftUI, etc.) using its established components, routing, and state patterns. If no environment exists yet, pick the framework most appropriate for the project and implement there. Treat the HTML as the source of truth for **visual spec and behavior**, and this README as the implementation guide.

To view the prototype: open `Signals Navigation.dc.html` in a browser. Use the dark toolbar at the very top to switch screens (View dropdown), toggle Desktop/Mobile, and toggle Light/Dark. **That toolbar is a prototype harness — do not build it into the real product.** In production, view switching comes from routing and theme comes from user/system preference.

## Fidelity
**High-fidelity.** Colors, typography, spacing, and interactions are final-intent. Recreate the UI faithfully — exact hex values, fonts, and the interaction model below — adapting only to your codebase's component primitives. The placeholder element is the **body copy** of the reader surfaces (Report/Article/etc. prose is representative, not final editorial content). The **navigation, switching, provenance, library, and onboarding mechanics are the real deliverable.** When in doubt about any value, read the inline `style` attributes in the source file — they are the spec.

---

## Design Tokens

Defined as CSS custom properties on `:root` (light) and `[data-theme="dark"]`. Port these into your theme system.

### Color — Light
| Token | Hex | Use |
|---|---|---|
| `--bg` / `--paper` | `#f5f3ee` | Page background (warm off-white) |
| `--card` | `#ffffff` | Card / panel surface |
| `--ink` | `#0a0a0f` | Primary text (near-black) |
| `--muted` | `#6b6860` | Secondary text |
| `--hairline` | `#c8c4bb` | 1px borders, dividers, grid gaps |
| `--low` | `#f0ede8` | Subtle fill (active rows, breadcrumb bar) |
| `--blue` | `#0068b5` | Report surface + primary accent / links |
| `--terra` | `#d4622a` | Accent (surface color) |
| `--amber` | `#c8860a` | Accent + text selection highlight |
| `--green` | `#2f7d4f` | Accent (e.g. Published state) |
| `--chrome` | `#0a0a0f` | Header / footer background |
| `--chrome-text` | `#f5f3ee` | Text on chrome |
| `--chrome-muted` | `#8c887e` | Inactive nav text on chrome |
| `--amber-ink` | `#946400` | Amber text on light bg (AA) |
| `--terra-ink` | `#a8481d` | Terra text on light bg (AA) |
| `--ev-bg` | `#ffffff` | Evidence panel background |

### Color — Dark (`[data-theme="dark"]`)
`--bg` `#07070b` · `--paper` `#0e0e14` · `--card` `#14141b` · `--ink` `#f1efe9` · `--muted` `#9a978f` · `--hairline` `#2a2a33` · `--low` `#16161d` · `--blue` `#3a9be0` · `--terra` `#e07a48` · `--amber` `#dba62f` · `--green` `#4caa75` · `--chrome` `#050509` · `--chrome-text` `#f1efe9` · `--chrome-muted` `#7d7a74` · `--amber-ink` `#dba62f` · `--terra-ink` `#e07a48` · `--ev-bg` `#14141b`

### Typography
Three self-hosted families (woff2 files in `/fonts`, declared in the source's `@font-face` block — also mirrored in `fonts/fonts.css`):
- **DM Serif Display** (400, + italic) — display headlines, logo wordmark. e.g. headlines `clamp(34px, 5vw, 52px)`, line-height ~1.04; logo 22px.
- **DM Mono** (400, 500) — labels, kickers, nav items, breadcrumbs, metadata. Always **UPPERCASE**, letter-spacing `.1em`–`.2em`, sizes 10.5–13px.
- **Instrument Sans** (400, 400 italic, 500, 600) — body text and UI. Base family on the root container.

`::selection` is amber (`--amber`) on near-black ink.

### Surface accent colors
Each reader surface has an identity color used in the fan-out switcher and headers: **Report → blue**, and Article / Newsletter / The Show / Learning use the terra/amber/green/ink accents. Confirm exact per-surface assignment by reading each surface's view in the source.

---

## Global Chrome (on every product view)

### Global nav header
- Sticky. Background `--chrome`, text `--chrome-text`. Row height **62px**, horizontal padding **22px**, item gap **20px**.
- **Logo**: a 13×13px `--blue` square + the word "Signals" in DM Serif Display 22px. Click → Home.
- **Primary nav** (desktop only): six items, DM Mono 11.5px, uppercase, letter-spacing `.1em`, padding `7px 11px`. Order: **Start here · Library · Newsletters · Articles · The Show · Learning**. Active item = `--chrome-text` color with a **2px `--blue` bottom border**; inactive = `--chrome-muted` with a transparent bottom border.
- **Jump-to button** (desktop, right-aligned): translucent fill `rgba(255,255,255,.06)`, 1px border `rgba(255,255,255,.14)`, label "Jump to… ⌘K". Opens the command palette.
- **Hamburger** (mobile only): three 20×2px bars; opens the mobile drawer.
- **Mobile drawer**: full-width list of the six nav items, DM Mono 13px uppercase, each row padded `13px 2px` and separated by `1px rgba(255,255,255,.08)` bottom borders.

### Breadcrumb bar
Below the header. Background `--low`, 1px `--hairline` bottom border, padding `11px 22px`. DM Mono 10.5px uppercase, letter-spacing `.1em`. Pattern: `Home / <current view label>`. "Home" is a button; the current crumb uses `--ink`. The label per view comes from the `crumbMap` object in the logic class.

### Footer
Background `--chrome`. Brand blurb column (logo + one sentence) + link columns, then a bottom rule with copyright and the review-gate reminder. Padding ~`40px 22px 34px`.

### Viewport frame
Content is centered in a frame: **max-width 1180px** desktop / **412px** mobile, with 1px `--hairline` left/right borders against the `--bg` page. This simulates the device — in production it's just your normal responsive page; the 412px width is the mobile breakpoint.

---

## Views / Screens (9 total)

Selected by `state.view`; default is `ia`. Order in the harness dropdown:

1. **IA & Patterns** (`ia`) — *reference doc, not a product screen.* Explains the system to the team: hero ("Make the fan-out visible."), a clickable sitemap, a Record → 5-Surfaces cross-link graph, the global-nav concept, three **fan-out switcher** treatments (A: segmented control [shipped]; B: "See this as" strip; C: sibling rail), and two **provenance** treatments (A: slide-in panel [shipped]; B: jump-to-highlighted-span). Build this only if you want an internal style reference; it is not a product page.
2. **Home** (`home`) — landing/orientation: hero with the "one record · five surfaces · every claim traced" thesis, and entry points into the surfaces and Library.
3. **Library** (`library`) — browsable index of records/surfaces.
4. **Report** (`report`) — the canonical reviewed surface; blue identity. Hosts the **claim → evidence** provenance interaction.
5. **Article** (`article`) — editorial surface of the same record.
6. **Newsletter** (`newsletter`) — email-style surface.
7. **The Show** (`show`) — audio/video surface.
8. **Learning** (`learning`) — structured-learning surface.
9. **Onboarding** (`onboarding`) — guided first-run reading path.

> Surfaces 4–8 are the **five fan-out surfaces of one record.** The defining behavior is that a reader on any one can jump laterally to the same record on another via the fan-out switcher, and the URL/state should reflect both *which record* and *which surface*.

---

## Key Interactions

### Fan-out switcher ("See this record as…")
Shipped treatment is a **segmented control** that lets the reader swap the current record between its five surfaces without losing context. Each segment carries the destination surface's accent color. Implement as: same record id + a `surface` parameter; switching changes the surface route while preserving the record. Treatments B and C in the IA view are alternatives — build the segmented control unless told otherwise.

### Provenance: claim → evidence → back
Shipped treatment is a **slide-in evidence panel** (`--ev-bg` background, animates in via the `evIn` keyframe — `translateX(24px)` + fade). A claim in a Report is an inline trigger; activating it opens the panel with the supporting source/evidence; a clear "back" returns the reader to the claim in place. Every published claim must be traceable this way.

### Command palette ("Jump to…", ⌘K)
Opened from the desktop nav button or the ⌘K shortcut. A searchable jump-to across records/surfaces/destinations. Wire the keyboard shortcut globally.

### Theming
Light/dark via the `data-theme` attribute on the root container. In production, drive from user/system preference (`prefers-color-scheme`) rather than the harness toggle.

### Review gate
The product concept includes a **Draft · In Review · Published** review gate on every surface (surfaced in the footer reminder and IA doc). Treat publish-state as a first-class attribute on records/surfaces; the IA view documents its intent.

---

## Implementation Notes
- **Accessibility**: interactive elements use a `data-nav` hook with a visible focus ring (`2px solid --blue`, offset 2px). Preserve keyboard focus styling and ensure the command palette, drawer, and evidence panel are keyboard-operable and focus-trapped where appropriate.
- **Responsive**: a single breakpoint at the 412px mobile frame. Desktop shows inline nav + jump-to; mobile collapses to the hamburger drawer.
- **Don't port**: `support.js`, the `<x-dc>`/`<sc-*>` tags, the `Component` logic class, and the prototype harness toolbar. Rebuild state (`view`, `theme`, drawer/panel/palette open flags) in your framework's idiomatic way.
- **Fonts**: ship the woff2 files in `/fonts` (self-hosted, no external calls) or substitute your project's equivalents of DM Serif Display / DM Mono / Instrument Sans.

## Files in this package
```
design_handoff_signals_navigation/
├── README.md                     ← this file
├── Signals Navigation.dc.html    ← the prototype (visual + behavior spec)
├── support.js                    ← prototype runtime (reference only — DO NOT port)
└── fonts/                        ← self-hosted woff2 + fonts.css
```
