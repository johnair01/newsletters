---
phase: 10-reviewer-surfacing-merge-block
plan: 03
subsystem: renderer
tags: [PROV-03, SITE-06, render, review-surfacing, honesty-panel]
requires:
  - "10-01: Surface.missing[] carrier + SpanContainmentFaithfulness + Claim.is_stale/Trace.is_stale_against"
provides:
  - "render._honesty_panel: per-surface amber What's-not-here/not-verified panel (missing[] + Source.extraction.unextracted[])"
  - "render._block_html(sources=): claim-beside-verbatim-span view with inline STALE/unfaithful badge"
  - "regenerated content/rev1/site/ carrying the panel + inline spans (byte-stable, SITE-06)"
affects:
  - "src/newsletters/render.py"
  - "content/rev1/site/*.html"
  - "docs/surfaces.md"
tech-stack:
  added: []
  patterns:
    - "render_surface self-derives the {source_id: Source} lookup from surface.traces — no caller signature change"
    - "faithful-not-suggestive: span box only for addressed non-empty traces; un-addressed Rev1 traces show the chip alone"
    - "honesty panel always present (presence is the proof); clean surface shows positive confirmation"
key-files:
  created: []
  modified:
    - "src/newsletters/render.py"
    - "tests/test_render.py"
    - "docs/surfaces.md"
    - "content/rev1/site/ (11 HTML files regenerated)"
decisions:
  - "render.py imports .distill.faithfulness (deterministic, stdlib-only) — lint-imports confirms it stays AI-free (1 kept / 0 broken)"
  - "No dogfood signature change: render_surface derives sources from surface.traces internally"
  - "STALE badge takes precedence over the unfaithful badge (drift is the louder signal)"
metrics:
  duration: "~25 min"
  completed: "2026-06-18"
  tasks: 3
  files: 4
---

# Phase 10 Plan 03: Renderer Surfacing (PROV-03) Summary

The review gate is now visible on every rendered surface: each claim renders beside its verbatim `Trace.span` by default with an inline amber STALE/unfaithful badge, and every surface carries an always-present amber "What's not here / not verified" honesty panel listing `Surface.missing[]` + every `Source.extraction.unextracted[]`. No JS, deterministic, byte-stable (SITE-06).

## What shipped

**Task 1 — claim-beside-verbatim-span view (PROV-03 / SC3).** Extended `_block_html` with an optional `sources: dict[str, Source] | None` param, threaded from `render_surface` (self-derived as `{s.id: s for s in surface.traces}` — no dogfood signature change). The `ClaimsBlock` branch now renders each addressed `Trace.span` inline in a quoted mono `.claim-span` box directly under the claim text, *by default, no click, no JS*. An un-addressed Rev1 trace (empty span) shows its evidence chip alone — never an empty box (faithful, not suggestive). Inline `.claim-badge` (amber): STALE (`Claim.is_stale(sources)`) takes precedence; else unfaithful (`not SpanContainmentFaithfulness().entails(claim)`); a clean claim carries none. `SpanContainmentFaithfulness` imported from `.distill.faithfulness` at module top (AI-free).

**Task 2 — honesty panel (PROV-03).** Added `_honesty_panel(surface)`, rendered once on every surface inside `render_surface` between the blocks and prev/next. Lists every `surface.missing[]` entry (unsubstantiated) and, for every traced `Source` with an `extraction` record, each `unextracted[]` drop as `locator.display` + `reason` (coverage gaps). Never collapsed (T-10-08). When both lists are empty the same panel shell renders a positive "Fully traced — nothing outstanding" confirmation, so the panel's *presence* is the proof. One `.honesty` CSS rule (`--color-amber`, mono uppercase eyebrow). Every interpolation `_e`-escaped (T-10-07); pure markup, no JS.

**Task 3 — regenerate + document (SITE-06).** Process order was load-bearing (Phase-9 lesson): regenerated `content/rev1/site/` FIRST via `newsletters build`, then ran ALL gates LAST. 11 HTML files modified, filenames byte-stable (no adds/deletes). `index.html`/`library.html` changed only by the shared `_CSS` additions (they render via `render_home`/`render_library`, not `render_surface`). Added `docs/surfaces.md` "The review view" section documenting the claim-beside-span device, the honesty panel, and the block scope.

## The surfacing structure

- **Per claim:** `<li class="claim"><div class="claim-text">{text}{badge}</div>{spans}<div class="claim-ev">{chips}{conf}</div></li>` — badge inline in the text line, verbatim span box(es) below it, chips/confidence last.
- **Per surface:** `<main>{masthead}{blocks}{honesty}{prevnext}</main>` — the honesty panel is `<div class="honesty"><div class="h">What's not here / not verified</div>{ul-of-items | clean-line}</div>`.
- **Sources threading for STALE:** `render_surface` derives `{s.id: s for s in surface.traces}` and passes it to `_block_html`; `_claim_badge` uses it for `claim.is_stale(sources)`. Without the lookup (single-surface callers) no false STALE fires — `Claim.is_stale` skips sources it cannot see.

## docs/surfaces.md addition

New section "The review view — every surface shows its work (PROV-03)" between The Report and The Hub/Library: documents (1) claim beside verbatim trace with the STALE/unfaithful badge semantics and the no-false-positive rule for un-addressed traces, (2) the always-on honesty panel listing missing[] + unextracted[] with the clean-surface positive confirmation, and (3) the block scope (claim device on ClaimsBlock; panel on the whole surface; identical in draft/in-review/published).

## Gate output (run AFTER content regeneration)

- `newsletters build` — rendered 10 surfaces + library index, exit 0; re-run produced the identical 11-file modified set (deterministic, no `datetime.now`).
- `pytest tests/test_render.py -q` — **51 passed** (44 baseline + 7 new: 3 claim/badge, 3 honesty, 1 dogfood-panel).
- `pytest -q` — **524 passed, 1 xfailed** (baseline 513+1; +11 = my 7 + concurrent 10-02 additions).
- `mypy src/newsletters` — **12 errors, exactly the pre-existing baseline** (capture.py:1, render.py:3 `rows` list→str reassignments in pre-existing block branches, dogfood.py:8). Zero new errors from `_claim_badge`/`_claim_spans`/`_honesty_panel`.
- `lint-imports` — **1 kept / 0 broken** (render.py importing `distill.faithfulness` stays AI-free).
- Built-site grep — `report-datamodel.html` carries both the amber honesty panel (`border-left:3px solid var(--color-amber)`) and a verbatim `class="claim-span"` box ("Two layers, not five peers: a Truth layer..."). No false badges on the clean corpus (correct).

## Deviations from Plan

None — plan executed exactly as written. The header literal uses a plain apostrophe ("What's") rather than `&rsquo;` so it reads as authored in the HTML; this was a consistency choice within the planned helper, not a behavior change.

## Known Stubs

None. The shipped Rev1 corpus is all-clean by design (no missing[]/unextracted[] in the sample data, content-addressed traces all entailed and non-stale), so every surface renders the positive "Fully traced" confirmation and no badges fire — this is correct per Plan 01 (the gate-fires proof lives in the renderer tests, which build fixtures with missing[]/unextracted[]/STALE/un-entailed claims). The 4 surfaces with content-addressed traces (article-semantic-spine, report-datamodel, report-kickoff, report-rev1) do show real verbatim `.claim-span` boxes.

## Threat surface scan

No new threat surface beyond the plan's `<threat_model>`. All three mitigations applied: T-10-07 (every interpolation `_e`-escaped; the no-script test asserts injection strings are escaped and `<script>` count stays at 1 — the theme toggle), T-10-08 (panel always rendered, never collapsed; clean → positive confirmation), T-10-09 (rendered from typed data; byte-stable regen test + regenerate-first/gates-last order).

## Self-Check: PASSED

- src/newsletters/render.py — FOUND
- tests/test_render.py — FOUND
- docs/surfaces.md — FOUND
- content/rev1/site/report-datamodel.html — FOUND (carries panel + verbatim span)
- Commits 670d406, 723512a, b255cbb, 4465c1f, f0bcb3e — all on branch, pushed
