# Phase 1 — Site IA & linkability — CONTEXT

**Requirement:** PUB-03 (no dead ends). **Defined:** 2026-07-03.
**Research base:** `.planning/research/2026-07-03-pages-publish-forensics.md` (F3/F4) +
a design study of `render.py` chrome code and the design references (below).

## Design authority (locked at milestone open)

- `docs/design-system.md` — tokens, type system, `--radius:0`, the 3px accent device.
- `design-reference/signals-navigation/` — the Claude design handoff: *"the navigation and IA
  layer … makes the fan-out visible and keeps **no surface a dead-end**."* The published site
  today violates that at the corpus level: rev1, work, and module render as three islands.

## Decisions (recorded before code — teaching build)

1. **The device is a "Records strip", not a nav-spine change.** The four-item nav spine
   (`Start here · Newsletters · Articles · The Show`) is a per-corpus contract (SITE-04, N1)
   and stays untouched. Cross-corpus linking is *chrome*, placed once per chrome page
   (Home/Library), styled like the existing mono utility rows (`.nl-crumb` conventions:
   DM Mono 11px, `--text-dim`, hairline underline on links, `--radius:0`, existing tokens
   ONLY — no new colors).
2. **Chrome pages only.** rev1 `index.html` + `library.html`; work `library.html`; module
   `library.html`. Per-surface pages never carry it — a reader inside a report is inside ONE
   record; the cross-record jump belongs at the record's front door. (Mirrors how the Library
   itself is reached via footer, not spine.)
3. **`render.py` stays corpus-blind.** The strip is an optional `records` parameter on
   `render_home` / `render_library` (default `None` → zero markup). Each *builder* declares
   its neighbors with hrefs relative to the assembled tree (`work/library.html` from root;
   `../index.html` from a subdir) — ownership mirrors the existing dogfood callout-injection
   precedent (`_LIBRARY_MAST_ANCHOR`).
4. **The 404 page is assembly chrome, not corpus content.** `render_404(base_path=…)` renders
   through `_page` (generated marker + full token CSS) with every href and font URL made
   base-path-absolute — GitHub Pages serves `404.html` at arbitrary depth, so relative URLs
   are structurally wrong there. Nav targets all resolve to Home (never a dead link; hub
   specificity needs a `Site`, which assembly deliberately does not build). It is *written at
   assemble time* (Phase 2), not committed into a corpus — it is a property of the assembled
   tree (it embeds the base path), not of any one record.
5. **SC1 amendment (honest deviation, recorded):** the roadmap's "records omitted → output
   byte-identical to before" is unprovable as written — the strip's CSS lands in the shared
   `_CSS` constant, which is inlined into every page, so all bytes change once per this phase
   regardless. The provable form: **records omitted → no strip markup** (`nl-records` absent),
   and all byte-stability invariants (double-render, committed==fresh) hold *after* the
   one-time regeneration. ROADMAP updated to match.
6. **Cross-corpus hrefs are exempt from the per-corpus dead-link test by *explicit listing*,
   not silent skip** — the test asserts they match the known cross-corpus shapes
   (`work/…`, `module/…`, `../…`) and Phase 2's assembled-tree test is their resolver of
   record (that test fails if any of them dangles in the real published tree).

## Out of scope

Nav-spine changes; any `web/` work; the assembled-tree test itself (Phase 2); content edits.
