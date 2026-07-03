# Fix prompt — Signals `web/` app (Navigation & IA implementation, round 2)

> Paste this whole file to Claude Code at the root of `johnair01/newsletters`.

## Context

`web/` implements the "Signals — Navigation & IA" design handoff (Next.js 14 App Router,
static-exportable, token-driven plain CSS). An audit against the design reference found the
**component fidelity is good** — nav spine, breadcrumb, fan-out switcher, evidence panel,
library, onboarding, ⌘K palette all match the spec. The app *looks* broken for
**packaging/deployment reasons**, not design reasons. Fix the items below in order.
Do not restyle or restructure components except where a task says so.

**Repo constraints to respect (do not violate):**
- The gh-pages root URL belongs to the assembled corpus site (workflow decision DEF-13:
  the web app must not wear the product's root URL). The web app deploys under a
  **`/web/` subpath** as a labeled design preview.
- `deploy-pages.yml` publishes via single-commit force-push to `gh-pages` after its two
  gates (`newsletters check` per corpus + `tests/test_publish.py`). Keep both gates intact.
- CI's AI-optional jobs are untouched by this work.

---

## Task 1 — Fonts 404 everywhere (the "it looks wrong" bug)

`web/app/globals.css` hardcodes `url('/newsletters/fonts/…')` in every `@font-face`,
assuming a `basePath` from a `next.config.mjs` that **was never committed**. In `npm run dev`
fonts are actually served at `/fonts/…`, so all three families 404 and the app renders in
Georgia / system-ui / Courier New fallbacks — nothing like the design.

**Fix (bundler-managed URLs, works in dev AND under any basePath):**
1. Move the 8 woff2 files from `web/public/fonts/` to `web/app/fonts/` and delete
   `web/public/fonts/`.
2. In `globals.css`, change every `@font-face` `src` to a relative URL, e.g.
   `url('./fonts/dm-mono-400-normal.woff2')`. Next bundles these into `_next/static/media`
   and rewrites URLs for dev, export, and basePath automatically. Remove the stale
   "/newsletters prefix" comment.
3. Keep the literal family names (`'DM Mono'`, `'DM Serif Display'`, `'Instrument Sans'`)
   — components reference them directly. Do **not** switch to `next/font` (it hashes
   family names).

**Verify:** `npm run dev` → every woff2 request is 200; headings render in DM Serif
Display (serif, high-contrast), labels in DM Mono (monospace uppercase).

## Task 2 — Instrument Sans 500/600 are fake (defect in the design bundle itself)

`instrument-sans-400/500/600-normal.woff2` are **byte-identical copies of the 400 file**
(29,904 bytes each — same blob hash in git). Medium/semibold never render anywhere.
This defect came from the design handoff bundle, so it's in both places.

1. Get genuine files: `npm i -D @fontsource/instrument-sans`, then copy
   `node_modules/@fontsource/instrument-sans/files/instrument-sans-latin-500-normal.woff2`
   and `…-600-normal.woff2` over the fakes in `web/app/fonts/` (drop the dev dep after,
   or keep it and document). 
2. Also overwrite the same two files in the in-repo design reference bundle if present
   (`design-reference/signals-navigation/fonts/`).
3. **Verify:** `sha256sum web/app/fonts/instrument-sans-*` → three distinct hashes;
   in the browser, buttons/labels at weight 500/600 are visibly heavier than body text.

## Task 3 — Add the missing `web/next.config.mjs`

```js
/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_BASE_PATH ?? '';
const nextConfig = {
  output: 'export',
  basePath,
  trailingSlash: true,   // folder/index.html URLs — required for gh-pages subpath serving
  images: { unoptimized: true },
};
export default nextConfig;
```

- Local dev/build: no env → no basePath.
- Pages build: `NEXT_BASE_PATH=/newsletters/web` (set by the workflow in Task 4).
- **Verify:** `npm run build` emits `web/out/` with `index.html` for all 11 routes
  (`/`, `/ia`, `/library`, `/report`, `/article`, `/newsletter`, `/show`, `/learning`,
  `/onboarding`, `/gated`, plus 404).

## Task 4 — Actually deploy it (this is why "nothing showed up")

`deploy-pages.yml` deliberately excludes `web/` — nothing built from the handoff has ever
been published. Extend the **existing** publish job (keep it one workflow, one force-push):

1. In `on.push.paths`, add `"web/**"`.
2. After the "Assemble the published tree" step, add:
   ```yaml
   - uses: actions/setup-node@v4
     with: { node-version: 20, cache: npm, cache-dependency-path: web/package-lock.json }
   - name: Build the web design preview (served at /newsletters/web/)
     run: |
       cd web
       npm ci
       NEXT_BASE_PATH=/newsletters/web npm run build
       cp -r out ../_site/web
   ```
   Order matters: build **after** assemble so `cp` lands inside the final `_site`.
   The root `.nojekyll` from assemble already covers `_site/web/_next/`.
3. Leave both publish gates and the force-push step exactly as they are.
4. Add a comment updating the DEF-13 note: root still belongs to the corpus record;
   `/web/` is the design preview.
5. **Verify after merge:** `https://johnair01.github.io/newsletters/web/` renders the Home
   page with correct fonts; nav to all routes works; corpus site at the root is unchanged.

## Task 5 — Dark theme tokens drifted from spec

`[data-theme="dark"]` in `globals.css` uses near-miss hexes. Replace with the handoff's exact
values, and restore the page-vs-frame distinction the dark design relies on:

| Token | Now (wrong) | Spec |
|---|---|---|
| `--color-paper` (frame/paper) | `#0f0f14` | `#0e0e14` |
| page background (new, see below) | — | `#07070b` |
| `--color-white` (card) | `#1a1a22` | `#14141b` |
| `--color-ink` | `#f0ede8` | `#f1efe9` |
| `--color-muted` | `rgba(240,237,232,.55)` | `#9a978f` |
| `--color-rule` | `rgba(240,237,232,.16)` | `#2a2a33` |
| `--color-brand-primary` | `#3f9ae0` | `#3a9be0` (digits transposed) |
| `--color-accent` | `#e07a45` | `#e07a48` |
| `--color-amber` | `#d99a2a` | `#dba62f` |
| `--color-green` | `#4fa873` | `#4caa75` |
| `--color-amber-ink` / `--color-accent-ink` | follow amber/accent | `#dba62f` / `#e07a48` |
| `--chrome-bg` | `#07070b` | `#050509` |
| `--chrome-dim` | (unchanged) | `#7d7a74` |

Page-vs-frame: in dark, the page behind the framed viewport is `#07070b` while the frame
itself is paper `#0e0e14`. Implement minimally: set `--bg: #07070b` in the dark block
(keep `--bg: var(--color-paper)` in light), and change `.viewport { background: … }` to
`var(--color-paper)`. Nothing else references `--bg` except `html`/`body`.
`--color-surface-low: #16161d` is already correct; leave `--color-surface-mid` as is.

## Task 6 — Text selection color

Spec: `::selection { background: var(--color-amber); color: #0a0a0f; }` (amber highlight,
near-black text — in both themes). Currently blue/white. Fix in `globals.css`.

## Task 7 — CI coverage for `web/` (so this can't silently rot again)

No CI job touches `web/`. Add a path-filtered job (in `ci.yml` or a new
`.github/workflows/web-ci.yml`) that runs on `web/**` changes:

```yaml
web-build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: 20, cache: npm, cache-dependency-path: web/package-lock.json }
    - run: cd web && npm ci
    - run: cd web && npx tsc --noEmit
    - run: cd web && npm run build
    - name: Fonts are real (three distinct Instrument Sans weights)
      run: |
        cd web/app/fonts
        test "$(sha256sum instrument-sans-*-normal.woff2 | awk '{print $1}' | sort -u | wc -l)" -ge 3
```

## Acceptance checklist (run before opening the PR)

- [ ] `cd web && npm run dev` — all 8 woff2 load (200), zero console errors.
- [ ] Three distinct sha256s across Instrument Sans 400/500/600.
- [ ] `npm run build` succeeds; `out/` contains all 11 routes.
- [ ] `NEXT_BASE_PATH=/newsletters/web npm run build && npx serve out` (or equivalent) —
      pages, fonts, and client nav all work under the subpath.
- [ ] Dark mode: page `#07070b` vs frame `#0e0e14` visible; blue is `#3a9be0`;
      selection is amber with near-black text in both themes.
- [ ] `python -m pytest tests/test_publish.py -q` still green (publish gates untouched).
- [ ] After merge: `…/newsletters/web/` live; corpus root unchanged.

## Explicitly out of scope

Component markup/layout changes, the IA-view reference page, corpus/site pipeline,
AI-optional CI jobs, and any content edits. The implementation already matches the
design reference — this round is packaging, tokens, fonts, and deployment only.
