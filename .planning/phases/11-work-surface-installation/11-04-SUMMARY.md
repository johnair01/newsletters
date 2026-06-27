---
phase: 11-work-surface-installation
plan: 04
subsystem: work-surface
tags: [publish, render, provenance, lineage, fan-out, self-hosted-fonts, no-external-call, byte-stable, ai-optional]

# Dependency graph
requires:
  - phase: 11-work-surface-installation
    provides: "build_work_surfaces(*, root, author) -> list[Surface] + populated Surface.lineage.derived_from (Plan 11-03)"
  - phase: 11-work-surface-installation
    provides: "self-hosted woff2 fonts under content/rev1/site/fonts/ + relative @font-face (Plan 11-01)"
  - phase: 08-10-site-render
    provides: "render.py devices (link_for_source, _claim_spans, _honesty_panel, _fanout_row, render_surface masthead captured-via/derived-from, render_library) + site.Site/Ledger"
provides:
  - "build_work_site(out_dir='content/work/site', *, root) -> list[Path]: render the WORK corpus to standalone HTML reusing render.py + emitting self-hosted fonts; zero external call; byte-stable"
  - "content/work/site/ — the rendered work Library (work-report.html + library.html + fonts/), self-contained"
  - "claim->repo-file link surfaced: build_work_report now sets the trace locator to the file-path id so link_for_source emits a working repo blob URL per claim"
  - "Surface.lineage.produced finalized + a thin FanoutBlock so the fan-out chain renders on the work surface"
affects: [11-05-check-corpus, work-surface, provenance, lineage]

# Tech tracking
tech-stack:
  added: []  # ZERO new runtime dependency — render + site + capture + semantic + stdlib (shutil) only
  patterns:
    - "Publish a separate corpus by mirroring dogfood.build_site over its OWN ledger (content/work/ids.json): Ledger.load -> Site.from_surfaces -> ledger.save -> render_surface per page -> render_library, REUSING render.py (no new renderer)"
    - "Surface a claim->repo-file link 'for free' by setting the trace locator text to the file-path id — render._is_file_path_locator recognizes it and link_for_source returns the repo blob URL (a working citation, not a dead link)"
    - "Self-contained export: copy the Plan-11-01 vendored woff2 (+ OFL licenses) into the output's fonts/ so the relative @font-face urls resolve offline — zero auto-loading external call"
    - "Regen-FIRST, gates-LAST (Phase 9 process lesson): regenerate the committed built dir before running the byte-stable/visibility tests that read it, so a pre-regen pytest can never be a stale green"

key-files:
  created:
    - content/work/site/work-report.html
    - content/work/site/library.html
    - content/work/site/fonts/  # 7 woff2 + 3 OFL license txt (copied from content/rev1/site/fonts/)
  modified:
    - src/newsletters/worksurface.py
    - tests/test_worksurface.py

key-decisions:
  - "The populated masthead 'derived from' line (Plan 11-03's Surface.lineage) SUFFICED for lineage — no thin lineage summary helper was needed. Two REAL gaps remained and were closed minimally, not via a renderer rewrite: (1) the claim->repo-file link and (2) the fan-out chain."
  - "Gap 1 (claim->repo-file link): the work claims' locators were empty FreeLocators, so link_for_source returned None (plain text, no link). Fixed in build_work_report by setting locator=FreeLocator(text=src.id) — the source_id is already the POSIX relpath, so the existing file-path-locator branch fires and emits a WORKING repo blob URL. No render.py change."
  - "Gap 2 (fan-out chain + lineage.produced): build_work_surfaces had no FanoutBlock and produced==[]. Added a thin FanoutBlock (3 faithful plain-text rows — no sibling Page exists yet, so _fanout_row renders them as text, never a dead link) and set lineage.produced to the fan-out titles. No render.py change."
  - "build_work_site copies the Plan-11-01 vendored fonts into content/work/site/fonts/ rather than re-vendoring, so the work output is byte-for-byte the same font set as rev1 and stays zero-external-call; if the vendored dir were absent (the DM-first fallback path) it skips silently and the font-stack fallback applies — still no external call."
  - "The work-report stays Draft — build_work_site has NO publish() call. The board/Library reflects its real review state; no auto-publish path (the single most important invariant)."
  - "The work corpus keeps its OWN ledger (content/work/ids.json, R-001) — the sample (content/rev1/) vs real (content/work/) boundary is preserved at the ledger layer; rev1 is untouched and byte-stable."

patterns-established:
  - "Published process: every claim on the work surface links to its real repo file (blob URL), shows its verbatim trace span, the honesty panel shows the gap, and the masthead + fan-row show provenance/lineage — WORK-03's 'process visible on each surface' made real."

requirements-completed: [WORK-03]

# Metrics
duration: 5min
completed: 2026-06-18
---

# Phase 11 Plan 04: PUBLISH the work site (WORK-03) Summary

`build_work_site` renders the hand-authored WORK corpus to `content/work/site/` as standalone,
self-contained HTML — **reusing the Phase 9/10 renderer with no new renderer code** — so the
published Library shows **how the work was done**: every claim links to its real repo file,
shows its verbatim trace span, the honesty panel shows the one deliberately-paraphrased gap, and
the masthead + fan-out chain show provenance/lineage. Zero auto-loading external call (self-hosted
fonts), byte-stable across renders, Draft (no auto-publish).

## What was built

- **`build_work_site(out_dir="content/work/site", *, root=None) -> list[Path]`**
  (`src/newsletters/worksurface.py`): mirrors `dogfood.build_site` over the REAL work corpus and
  its OWN append-only ledger (`content/work/ids.json`): `Ledger.load → Site.from_surfaces(
  build_work_surfaces(), ledger) → ledger.save → render_surface(page.surface, site, page)` per
  page → `render_library(site)`. Then emits the self-hosted fonts into `out/fonts/`. Returns the
  written paths.
  - **Output:** `content/work/site/work-report.html`, `content/work/site/library.html`,
    `content/work/site/fonts/` (7 woff2 + 3 OFL license txt).
- **`_emit_fonts(out)`** helper: copies `content/rev1/site/fonts/*` (the Plan 11-01 vendored
  assets) into `out/fonts/` so the relative `@font-face` urls resolve offline.
- **build_work_report locator fix:** the content-address now sets `locator=FreeLocator(text=src.id)`
  so each claim's evidence chip becomes a **working repo-file link** via `link_for_source`.
- **build_work_surfaces fan-out:** a thin `FanoutBlock` (3 faithful rows) + `lineage.produced`
  finalized so the fan-out chain renders (`_fanout_row`).

### How the provenance/lineage renders (which reused devices)

| Device (render.py) | What it shows on the work surface | How it is driven |
|---|---|---|
| `link_for_source` / `_ev_chip` | claim → repo-file link (`…/blob/main/CLAUDE.md`) | the trace locator is the file-path id (this plan's fix) |
| `_claim_spans` | the verbatim trace span beside each claim (`claim-span` div) | the content-addressed span (Plan 11-03) |
| `_honesty_panel` | the gap on every surface — the 1 `missing[]` item (`unsubstantiated`) | `Surface.missing[]` (Plan 11-03) |
| masthead `captured via` | the provenance tool | `Surface.provenance.tool` |
| masthead `derived from` | the ingested file ids the surface cites | `Surface.lineage.derived_from` (Plan 11-03, **sufficed as-is**) |
| `_fanout_row` | the fan-out chain (`fan-row`) | the thin `FanoutBlock` (this plan) |

Spot-checked **present in the committed `work-report.html`**: `derived from`, `captured via`,
`class="claim-span"`, `class="honesty"`, `class="fan-row"`, `blob/main/CLAUDE.md`, `unsubstantiated`.

### Font / self-contained approach + zero external calls (confirmed)

The renderer's `@font-face` uses **relative** `url('fonts/...woff2')`, so a self-contained Library
needs a `fonts/` dir beside the HTML. `build_work_site` copies the Plan 11-01 vendored woff2 (+ OFL
licenses) from `content/rev1/site/fonts/` into `content/work/site/fonts/`. **Confirmed zero
external calls:** `grep -rE "fonts.googleapis|@import url\('http|src=\"http|url\(http"
content/work/site/` → **empty**; the no-external-call test passes; clickable `<a href="https://…">`
repo links (A2 navigation) stay permitted.

## Deviations from Plan

The plan anticipated this exactly: "verify the masthead line reads as a real provenance/lineage
summary; add only a tiny addition if a gap shows" / "Add a thin lineage summary ONLY if Task 1
shows a real gap." Task 1 surfaced **two real gaps**; both were closed minimally **without any
render.py change** (no new renderer). These are Rule 2 (missing critical functionality for WORK-03's
"process visible on each surface") additions, applied in this plan's own files.

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] claim→repo-file link did not render**
- **Found during:** Task 1 (the provenance-visible test asserts a `link_for_source` blob URL).
- **Issue:** the work claims carried empty `FreeLocator` locators (Plan 11-03 passed through the
  Decision's default empty locator), so `link_for_source` hit neither the file-path branch (empty
  text) nor an in-site slug (source_id is a file path, not a Page slug) and returned `None` →
  the evidence chip rendered as plain text, NOT a link. WORK-03 requires the claim→repo-file link.
- **Fix:** in `build_work_report`, content-address with `locator=FreeLocator(text=src.id)`; the
  source_id is already the POSIX relpath, so `render._is_file_path_locator` recognizes it and
  `link_for_source` emits the working repo blob URL. No render.py change.
- **Files modified:** `src/newsletters/worksurface.py`
- **Commit:** `d1a82e1`

**2. [Rule 2 - Missing critical functionality] no fan-out chain / `lineage.produced` empty**
- **Found during:** Task 1 (the test asserts a `fan-row`) + Task 2 (the plan asks to finalize
  `lineage.produced`).
- **Issue:** `build_work_surfaces` produced only ProseBlock + ClaimsBlock — no `FanoutBlock` —
  and `lineage.produced == []`, so the fan-out chain device had nothing to render.
- **Fix:** appended a thin `FanoutBlock` (3 faithful plain-text rows; `_fanout_row` renders them
  as text since no sibling Page exists — never a dead link) and set `lineage.produced` to the
  fan-out titles. No render.py change.
- **Files modified:** `src/newsletters/worksurface.py`
- **Commit:** `d1a82e1`

## Gate results (re-run independently — actual output, AFTER regenerating content/work/site)

- `pytest tests/test_worksurface.py -q` → **8 passed** (3 new work-site tests + the now-un-skipped
  e2e scaffold, all green on the committed built dir)
- `pytest -q` (full) → **534 passed, 1 xfailed** (was 530 passed + 1 skipped + 1 xfailed; +3 new
  work tests and the e2e scaffold is now un-skipped & passing, so 0 skipped)
- `grep -rE "fonts.googleapis|@import url\('http|src=\"http|url\(http" content/work/site/` →
  **empty** (zero external resource URL)
- `newsletters build` → renders 10 rev1 surfaces + library; **rev1 site byte-stable / unchanged**;
  `content/work/site/` present and self-contained
- `mypy src/newsletters` → **12 errors** (exactly the pre-existing baseline; none in worksurface.py)
- `lint-imports` → **1 kept, 0 broken** (worksurface.py AI-free even after importing render/site —
  both are AI-free, as dogfood already imports them)

## Work-site structure

```
content/work/site/
├── work-report.html   # the Draft work Report — process visible (links/spans/honesty/lineage/fan-out)
├── library.html       # the gate-state board (work-report in the Draft column)
└── fonts/             # self-hosted woff2 (+ OFL licenses) — copied from content/rev1/site/fonts/
    ├── dm-mono-400.woff2 / dm-mono-500.woff2 / dm-mono-400-italic.woff2
    ├── dm-serif-display-400.woff2 / dm-serif-display-400-italic.woff2
    ├── instrument-sans-variable.woff2 / instrument-sans-400-italic.woff2
    └── OFL-DM_Mono.txt / OFL-DM_Serif_Display.txt / OFL-Instrument_Sans.txt
```

`content/work/ids.json` unchanged (`work-report → R-001`). Separate from `content/rev1/`.

## Note for Wave 4 (Plan 11-05)

Plan 11-05 adds the `--corpus {rev1|work}` CLI selector + docs and fills stage 5 of the e2e
scaffold (`newsletters check --corpus work`). The renderer + corpus are ready: load via
`build_work_site()` / `build_work_surfaces()`, and the work ledger is `content/work/ids.json`.
Do NOT touch `content/rev1/` or the rev1 render path.

## Threat surface scan

No new security-relevant surface beyond the plan's `<threat_model>`. T-11-10 (leftover external
URL) is mitigated and enforced by `test_no_external_calls_in_work_output` + the committed-dir grep;
T-11-11 (injection) holds — all interpolations stay `_e`-escaped (render.py) and the locator text
that now enters an href is a path/slug-safe POSIX relpath, never free claim text; T-11-12
(provenance/lineage not visible) is mitigated and enforced by `test_provenance_lineage_visible`.

## Known Stubs

None. The fan-out rows are descriptive labels (no sibling Page exists yet) and render as faithful
plain text via `_fanout_row` — this is the intended faithful behavior, not a stub. The work-report
stays Draft by design (no auto-publish).

## Self-Check: PASSED

- Files: `content/work/site/work-report.html`, `content/work/site/library.html`,
  `content/work/site/fonts/dm-mono-400.woff2`, `src/newsletters/worksurface.py`,
  `.planning/phases/11-work-surface-installation/11-04-SUMMARY.md` — all FOUND.
- Commits: `4b929e0` (test/RED), `d1a82e1` (feat/GREEN), `7e79fc5` (feat/regen) — all FOUND (pushed).
- `build_work_site` present in `worksurface.py`.
