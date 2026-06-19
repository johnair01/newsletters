# Design System — Newsletters (the "Signals" editorial language)

The visual contract. Every value here is lifted verbatim from
`design-reference/signals/tokens.css`. Port these tokens 1:1 into the real stack; do not
re-pick colors or fonts. The aesthetic is **flat editorial**: hairline rules, hard corners
(`--radius: 0`), a left-border accent as the dominant device, generous serif display type.

> Tokens are scoped to a `.signals` root in the prototype so multiple themeable roots can
> coexist. In the real app, promote them to `:root` (or your theme provider). Dark mode is a
> data attribute: `[data-theme="dark"]`.

---

## 1. Palette — light (default)

| Token | Value | Use |
|---|---|---|
| `--color-ink` | `#0a0a0f` | Primary text, near-black |
| `--color-paper` | `#f5f3ee` | Page background (warm off-white) |
| `--color-white` | `#ffffff` | Cards |
| `--color-brand-primary` | `#0068b5` | Brand blue — links, primary buttons, left accents |
| `--color-brand-mid` | `#005a9e` | Button hover |
| `--color-brand-light` | `#e8f2fb` | Pull-quote / "why you're seeing this" wash |
| `--color-brand-dark` | `#003d6b` | Avatar background |
| `--color-accent` | `#d4622a` | Editorial accent (terracotta) — The Show, "live", down-deltas |
| `--color-amber` | `#c8860a` | "In Review" gate state, the Newsletter signal color |
| `--color-green` | `#2f7d4f` | Positive delta, the "new contributor" persona accent |
| `--color-rule` | `#c8c4bb` | Hairline rules + borders (`--line`) |
| `--color-muted` | `#6b6860` | Dimmed text (`--text-dim`) |
| `--color-surface-low` | `#f0ede8` | Low surface (KPI bg, insets) |
| `--color-surface-mid` | `#e8e4de` | Mid surface |

**Semantic aliases:** `--bg: --color-paper` · `--card: --color-white` · `--text: --color-ink`
· `--text-dim: --color-muted` · `--line: --color-rule`.

**Chrome** (nav / hero / footer that stay dark in *both* themes — do NOT derive from
`--color-ink`, which inverts): `--chrome-bg: #0a0a0f` · `--chrome-fg: #f5f3ee` ·
`--chrome-dim: rgba(245,243,238,0.62)` · `--chrome-line: rgba(255,255,255,0.12)`.

## 2. Palette — dark (`[data-theme="dark"]`)

| Token | Value |
|---|---|
| `--color-ink` | `#f0ede8` |
| `--color-paper` | `#0f0f14` |
| `--color-white` | `#1a1a22` |
| `--color-brand-primary` | `#3f9ae0` |
| `--color-brand-mid` | `#5aa9e6` |
| `--color-brand-light` | `#15293a` |
| `--color-brand-dark` | `#0c1b29` |
| `--color-accent` | `#e07a45` |
| `--color-amber` | `#d99a2a` |
| `--color-green` | `#4fa873` |
| `--color-rule` | `rgba(240,237,232,0.16)` |
| `--color-muted` | `rgba(240,237,232,0.55)` |
| `--color-surface-low` | `#16161d` |
| `--color-surface-mid` | `#20202a` |
| `--chrome-bg` | `#07070b` |
| `--chrome-line` | `rgba(255,255,255,0.10)` |

---

## 3. Type

Loaded from Google Fonts in the prototype; self-host in production.

| Token | Stack | Role |
|---|---|---|
| `--font-display` | `'DM Serif Display', Georgia, serif` | Display / headlines (also italic for emphasis) |
| `--font-body` | `'Instrument Sans', system-ui, sans-serif` | Body — weights 400/500/600 |
| `--font-mono` | `'DM Mono', 'Courier New', monospace` | Eyebrows, labels, tags, code, metadata |

Base body: **14px / line-height 1.6**, antialiased, `text-rendering: optimizeLegibility`.

**Type primitives (observed sizes):**
- `.sg-display` — DM Serif, weight 400, line-height 1.08, letter-spacing -0.02em. Hero H1 in V1
  is **72px / 1.03**; section H2 ~44px; card/letter H3 ~26–30px.
- `.sg-eyebrow` — DM Mono, **10px**, uppercase, letter-spacing **0.20em**. Variants `.brand`
  (blue) / `.accent` (terracotta). Often paired with a hairline rule extending right.
- `.sg-mono` — DM Mono, **11px**, letter-spacing 0.02em, dim.
- Body copy in V1 ranges 13–18.5px depending on role; lead paragraph 18.5px / 1.6.

---

## 4. Shape, motion, spacing

- **Radius:** `--radius: 0px`. **Hard corners everywhere.** This is core to the look.
- **Durations:** `--dur-fast: 120ms` · `--dur-base: 200ms` · `--dur-slow: 380ms`.
- **Easing:** `--ease-out: cubic-bezier(0,0,0.2,1)`.
- **Borders:** 1px hairlines in `--line`. The signature device is a **3px left border** in an
  accent color on cards, KPI blocks, prompt blocks, and pull quotes.
- **Layout rhythm:** content max-width **1180px**, section padding ~`56–78px 44px`. Two-up
  grids collapse to one column under ~980–1040px (see responsive rules in `tokens.css`).
- **Entrance:** `.sg-fade` — fade + 12px rise over `--dur-slow`, gated behind
  `prefers-reduced-motion: no-preference`.

---

## 5. Components (from `signals/atoms.jsx`)

Recreate these as real components. Each is token-driven and theme-aware.

| Component | What it is | Key props / states |
|---|---|---|
| `Eyebrow` | Mono uppercase kicker, optional trailing rule | `variant` (brand/accent), `withRule` |
| `SectionDivider` | Eyebrow + hairline; the standard section header | `label`, `variant`, `centered` |
| `Tag` | Mono pill | `kind`: `cat / live / published / draft / review / peer / featured`. `live` pulses a dot; `peer` shows a check. |
| `GateBadge` | The governance gate `Draft › In Review › Published` | `current`; the active step colors by state (amber = In Review, blue = Published) and shows a dot. **Load-bearing UI — present on every artifact.** |
| `ProfileChip` | Avatar (initials or photo) + name + role | `initials`, `name`, `role`, `size`, `photo` |
| `KpiBlock` | Bordered grid of metric cells, 3px left accent | `items: [{label, value, delta, dir}]`; deltas color up=green / down=accent |
| `PromptBlock` | Dark code/prompt panel with copy button | `label`; syntax spans `.k`(blue) `.a`(amber) `.d`(dim) |
| `ThemeToggle` | Sun/moon, light/dark | `theme`, `onToggle`, `onDark` (for dark chrome) |
| `Button` | `.sg-btn` mono uppercase; `.ghost` variant | `ghost`, `withArrow` |
| `ImgPlaceholder` | Diagonal-striped placeholder with label | Use real imagery in production; keep the shape/ratio |
| Icons | `IconArrow, IconCheck, IconPlay, IconSun, IconMoon` (atoms) + `IconGit` (home-atoms) | Simple stroked glyphs; no icon font |

**Chrome components** (in `newsletters/home-atoms.jsx`): `NLNav` (sticky dark bar, 64px,
"Newsletters · working in the open" lockup, mono nav links with a 2px accent underline on
active, theme toggle + GitHub button) and `NLFooter` (dark, 3px brand top border, three
columns: tagline / Surfaces / Project, with the "Open source · MIT · self-hostable" and
"Renders without JavaScript · WCAG AA" lines).

> The older `SiteNav`/`SITE` map in `atoms.jsx` belongs to the pre-converged "Signals"
> surfaces. For the product, the nav spine is **Start here · Newsletters · Articles · The
> Show** as in `NLNav`.

---

## 6. Tags & gate — exact mapping

- `.sg-tag.cat` neutral · `.live` accent bg + pulsing dot · `.published` brand-blue bg ·
  `.draft` outline/dim · `.review` amber outline · `.peer` brand-light bg + check ·
  `.featured` ink bg.
- Gate states color: **Draft** = text default, **In Review** = `--color-amber`,
  **Published** = `--color-brand-primary`.
