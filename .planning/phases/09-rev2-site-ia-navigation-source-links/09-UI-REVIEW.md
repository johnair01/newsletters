# Phase 9 — UI Review (Rev2 Site IA, Navigation & Source Links)

**Audited:** 2026-06-18
**Baseline:** `09-UI-SPEC.md` (the locked design contract) + `docs/design-system.md` (authoritative tokens) + `docs/surfaces.md` (Home 8-section + Library spec) + `design-reference/newsletters/home.jsx` (the approved look).
**Branch:** `claude/youthful-fermi-dly6mi` (read-only audit; no source modified, no branch switch).
**Screenshots:** NOT captured — this is a Python stdlib static-HTML renderer (`render.py` → `content/rev1/site/`); there is no dev server and no pixel renderer. Audited **structurally** against the emitted HTML/CSS values vs. the ported tokens + the JSX prototype's exact inline values, per the audit brief.

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Typography | 4/4 | Hero 72px/1.03 max-960 + 18.5px lead + 10px/0.20em eyebrow + 16.5px §2 body all match the JSX prototype's inline values 1:1. DM Serif/Instrument Sans/DM Mono loaded; weight 400 display. |
| 2. Color | 4/4 | 60/30/10 holds: paper bg, white cards, brand/per-signal accents reserved correctly. Gate columns colored Draft=text, In Review=amber, Published=brand (design-system §6). No hardcoded hexes outside the ported token block + the intentional `#0c0c12` prompt panel + `#fff` on-accent text. |
| 3. Spacing / Layout | 4/4 | `--radius:0` everywhere (no rounded corner except 50% on avatars/dots, correct). 3px-left-accent device on cards/KPI/prompt/quote/board cards/pipeline-cell-1/invitation. max-width 1180px, section padding 72px/44px, scroll-margin 80px — match prototype. Editorial half-steps (18.5/16.5/30/26px) preserved per the Spacing Exception. |
| 4. Components | 4/4 | All SITE-02..05 atoms emit: 8 Home sections, gate-state board (3 cols + empty placeholder), breadcrumb, prev/next, SVG fan-out anchors, evidence chips. Gate badge present on surfaces + §4. |
| 5. Consistency | 4/4 | Single `_CSS` token block; every page shares chrome (nav/footer), the signal-driven `--signal`, the generated marker. Board refs are content-identity (R-003/A-001/EP01), never positional — SITE-01 preserved. |
| 6. Fidelity to reference | 3/4 | Structure + token values match the prototype precisely. One honest gap: the persona re-cut is a static default (no-JS faithful, as the spec resolves) — the live `sg-fade` re-cut is deferred (not a defect, but it is < the animated prototype). Minor: `semantic.py` evidence-chip URL points at repo root, not `src/newsletters/semantic.py` (corpus-locator data, not a renderer bug). |

**Overall: 23/24** — PASS.

---

## Verdict

**PASS — ship.** The biggest visual phase lands the contract. No BLOCK. Two FLAGs, both informational / out-of-scope by the spec's own resolution.

### Findings by severity

**PASS (verified against the live output):**
- **Home anchors** — `#start`, `#newsletters`, `#engine`, `#surfaces`, `#developers` all present in `index.html`. (§2 "Why" and §6 "Thesis" carry no anchor; the spec only assigns anchors to those five — compliant.)
- **Hero typography** — `.home-h1{font-size:72px;line-height:1.03;max-width:960px;margin-top:26px}` is a 1:1 match to `home.jsx:55` `{fontSize:72, lineHeight:1.03, maxWidth:960, marginTop:26}`; lead 18.5px/1.6 max-620; eyebrow 10px/0.20em DM Mono with `.brand`/`.accent` variants. Italic emphasis on both nouns (`<em>conversation.</em>` / `<em>action.</em>`).
- **§1 color split / chrome** — hero sits on `--color-paper` (matches the prototype; hero is NOT dark-chrome), cards `--color-white`, accents reserved. The "chrome-bg hero option" in the spec was correctly NOT taken (prototype hero is on paper).
- **3px-left-accent device** — applied on `.sg-card`, `.sg-kpi`, `.sg-prompt`, `.sg-quote`, `.lib-card`, `.pipe-cell.first` (brand), `.home-invite-panel` (accent), demo letter top-border + why-inset (persona accent), masthead top-border. Per-section accents (brand/green/accent) on the 3 how-cards + personas.
- **`--radius:0`** — confirmed; zero stray `border-radius` other than the intended `50%` avatar/dot.
- **Library board** — 3 gate-state columns Draft(0)/In Review(3)/Published(4), colored `var(--text)` / `var(--color-amber)` / `var(--color-brand-primary)` (design-system §6). Pure CSS grid, the only `<script>` is the theme toggle. Empty Draft column renders header + "No surfaces in this state." placeholder — board shape stays legible.
- **Board cards** — ref-led (`R-003`, `A-001`, `EP01`, …), 3px left signal border, serif title, mono meta, status pill. **No `enumerate` position** — SITE-01 identity rule held.
- **Nav** — the four destinations resolve to real files: Start here→`index.html`, Newsletters→`newsletter-jj.html`, Articles→`article-semantic-spine.html`, The Show→`show-ep01.html`. Active state set (`class="active"` 2px accent underline). Library reachable via footer (intentionally off the 4-item spine, N1).
- **Breadcrumb** — `Home › The Show › Episode 01 …` mono 11px, `›` separators, current page plain `--text`. Present on surfaces.
- **Prev/next** — within-collection only (report-kickoff → Next: "Getting the data models right"); first page omits prev, correct.
- **Source links** — evidence chips render as real `<a class="ev-chip">` when the locator resolves (e.g. `session-kickoff:CLAUDE.md` → `…/blob/main/CLAUDE.md`); session locators with no recording surface (`session-datamodel:layers`) fall back to plain `<span>` — **faithful, never a dead link.** Fan-out SVG wraps all four surface boxes in `<a href='…'>` anchors (show/report/article/newsletter). **Zero dead links** (`href="None"` / `href=""` / `href="#"` = 0 across all 11 files).
- **Regen marker** — `<!-- generated by newsletters.render; do not hand-edit -->` on every committed file.

**FLAG (informational — resolved by the spec, not a regression):**
- **F1 — Static persona default, not the live re-cut.** The demo renders the maintainer letter inline with the picker as styled labels; the prototype's `sg-fade` re-cut on `who` change needs React state. The spec (SITE-02 "Static-render note" + Risk 1) explicitly resolves this as the no-JS-faithful default and says **do not block.** It is the one place the output is < the animated prototype — hence Fidelity 3/4, not 4/4.
- **F2 — `semantic.py` evidence-chip URL resolves to repo root.** A corpus locator text of `semantic.py` produces `…/blob/main/semantic.py`, but the file lives at `src/newsletters/semantic.py` (a 404 on GitHub). This is driven by the **locator data in `dogfood.py`**, not the renderer rule — `link_for_source` faithfully maps the path it is given. Fix belongs in the corpus locator, not `render.py`. Low impact (the renderer's contract is satisfied; the no-dead-link guarantee is about in-site nav, and the rule degrades unknowns to plain text).

---

## Token-fidelity assessment

**No drift.** Every emitted CSS value traces to a `design-system.md` token or the documented editorial half-step:

- The `_CSS` `:root`/`.signals` block is the verbatim 1:1 port of `signals/tokens.css` (palette light + dark, the three font stacks, `--radius:0px`, durations, easing, chrome quad). Spot-checked against design-system §1/§2/§3/§4 — exact.
- New layout CSS added this phase (`.home-*`, `.lib-board/col/card`, `.nl-crumb`, `.nl-prevnext`, `.nl-pipe`, `.nl-practice-grid`) uses **only existing custom properties** for color — no new hex introduced (the lone literals are `#0c0c12` for the dark prompt panel, already the established `.sg-prompt` bg, and `#fff` for text on accent fills, both pre-existing).
- The editorial half-steps the SPEC flags as authoritative (18.5 lead, 16.5 §2 body, 30 statement/letter-H3, 26 block-h, 22/27/34/36/44/72 display steps) are all present at their prototype values — the checker correctly defers to the ported tokens over a naive 8-point rule (Spacing Exception, spec L123-126).
- Cross-check against the prototype's inline JSX styles: `home.jsx:55` (72/1.03/960/26), `:78,:81` (16.5/1.72), `:89/:172/:231` (`72px 44px 0`, scrollMarginTop 80) all match the emitted classes byte-for-intent.

---

## Divergence from design-system.md / design-reference

None that breaks the contract. The only deltas are the two spec-sanctioned ones above (static persona default; an out-of-renderer corpus locator path). The flat editorial aesthetic — hairline rules, hard corners, 3px-left accent, serif display, three-font system, dark chrome nav/footer — is reproduced faithfully in the real stack with zero new dependency and no hand-edited HTML.

---

## Top fidelity risk

**The static-vs-animated persona demo (F1).** The single most visible place the deployed Home is < the approved prototype is the personalization "wow": three readers are shown but only the maintainer's letter is rendered, with no interactive re-cut. This is explicitly the spec's resolved no-JS default and is correctly out of scope here — but it is the item to close in the `web/` phase to fully honor the prototype's signature interaction. Track it; do not block Phase 9 on it.

---

## Files Audited

- `src/newsletters/render.py` (the renderer — CSS/HTML emitted, all SITE-02..06 helpers)
- `content/rev1/site/index.html` (Home), `library.html` (board), `show-ep01.html`, `report-kickoff.html`, `report-datamodel.html`, `report-rev1.html`, `article-semantic-spine.html`, `newsletter-jj.html` (built output)
- `.planning/phases/09-rev2-site-ia-navigation-source-links/09-UI-SPEC.md`, `docs/design-system.md`, `docs/surfaces.md`, `design-reference/newsletters/home.jsx` (the bar)
