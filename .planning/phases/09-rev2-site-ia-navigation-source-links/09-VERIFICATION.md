---
phase: 09-rev2-site-ia-navigation-source-links
verified: 2026-06-18T00:00:00Z
status: passed
score: 5/5 must-haves verified (SC4 gap RESOLVED 2026-06-18 — see RESOLUTION)
overrides_applied: 0
resolution: >-
  The SC4/SITE-05 gap (links well-formed but not resolving) was FIXED in commit 45471d4: the default
  repo handle `nneibaue` → `johnair01/newsletters` (the actual remote where the files live), the dev
  lockup org text, the spec (docs/surfaces.md), and the two path-drift locators
  (`semantic.py`/`render.py` → `src/newsletters/...`). Added
  `tests/test_render.py::test_file_path_source_links_resolve_to_real_files`, which asserts every
  repo-blob link in the generated site points at a path that EXISTS in the repo (working links, not
  just well-formed). Full suite 502 passed; mypy at the 12-error baseline; lint-imports 1 kept/0
  broken; build byte-stable. The orchestrator independently re-ran all gates + a dead-link sweep.
gaps:
  - truth: "The fan-out diagram and every cited source render as WORKING links (e.g. vision.md → repo file)"
    status: partial
    reason: >-
      The link MECHANISM is fully correct and faithful (real <a> anchors, plain-text
      fallback, no dead/href=None links, FanoutLink.href populated, configurable base) —
      but the default external source links do NOT resolve to real files for THIS repo as
      committed. Two distinct problems: (1) repo-handle drift — links point at
      github.com/nneibaue/newsletters while the actual remote is github.com/johnair01/newsletters,
      so every repo-blob link 404s against the live host; (2) path drift — bare-filename
      locators render render.py / semantic.py as blob/main/render.py and blob/main/semantic.py,
      but those files actually live at src/newsletters/render.py and src/newsletters/semantic.py,
      so even with the right handle those two links 404. CLAUDE.md, GSD.md, docs/architecture.md
      would resolve (modulo the handle). In-site fan-out anchors and session anchors resolve
      correctly. So source links are STRUCTURALLY satisfied but not GENUINELY resolving.
    artifacts:
      - path: "src/newsletters/render.py:49"
        issue: "repo_url = 'https://github.com/nneibaue/newsletters' — wrong handle for this repo's remote (johnair01); source_base_url derives from it. Configurable (one-line fix), but as committed all repo links 404."
      - path: "content/rev1/site/report-rev1.html (and others)"
        issue: "ev-chip links blob/main/render.py and blob/main/semantic.py point at non-existent repo paths (real files are under src/newsletters/); locator text in corpus uses bare filenames."
      - path: "docs/surfaces.md:68"
        issue: "Spec itself specifies the stale 'nneibaue / newsletters' handle — spec/reality drift; the renderer faithfully obeys the spec. Spec is source of truth, so this is a spec-update decision, not purely a renderer bug."
    missing:
      - "Point source_base_url at the real remote (johnair01/newsletters) OR document it as a deploy-time config knob and update docs/surfaces.md §7 to match."
      - "Fix the two bare-filename locators (render.py, semantic.py) to their real repo paths (src/newsletters/...), or have link_for_source map known bare module names to their src path."
      - "Optional: add a test that asserts file-path source links resolve to paths that actually exist in the repo (the current no-dead-link test only checks in-site .html links and absence of href=None)."
---

# Phase 9: Rev2 Site IA, Navigation & Source Links — Verification Report

**Phase Goal:** A real marketing Home separate from a Library status-board, four real nav
destinations with breadcrumbs, every cited source rendered as a working link — all regenerated
from templates (no hand-edited HTML).
**Verified:** 2026-06-18 (branch `claude/youthful-fermi-dly6mi`)
**Status:** gaps_found
**Re-verification:** No — initial verification

Verification was done against LIVE code (`src/newsletters/render.py`, `site.py`, `diagrams.py`,
`dogfood.py`) and the BUILT, COMMITTED output (`content/rev1/site/*.html`), not the SUMMARYs.
All four DoD gates were re-run independently via `.venv/bin/python`.

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|--------------------|--------|----------|
| 1 | Front door is the real 8-section marketing Home; archive is a separate Library page | ✓ VERIFIED | `index.html` carries all 8 section anchors (`#start`,`#newsletters`,`#engine`,`#surfaces`,`#developers` + hero/why/thesis/invite) exactly once; `home-hero`/`home-h1` present; no `lib-board` element (only the shared responsive CSS rule matches). The board is its own `library.html`. `render_home`→index, `render_library`→library (`dogfood.py:678,685`). |
| 2 | Library = status board, 3 columns by gate state (Draft/In Review/Published), CSS columns, no JS | ✓ VERIFIED | `library.html` has `lib-board` (CSS grid), 3 `lib-col` + `lib-col-head` headers labelled Draft/In Review/Published, cards placed by `Page.gate` (`_board` buckets by gate, `render.py:786`), empty-column placeholder rendered (`lib-col-empty` x2). Exactly 1 `<script>` — byte-identical to the theme toggle inherited by every surface page; no board JS. |
| 3 | Global nav = four real destinations + breadcrumbs + prev/next WITHIN a surface type | ✓ VERIFIED | Nav resolves to `index.html`, `newsletter-jj.html`, `article-semantic-spine.html`, `show-ep01.html` (4 real hrefs, zero `href="None"`/`href="#"` site-wide). Breadcrumb `Home › {Collection} › {title}` on every surface, current page plain text. Prev/next confined to surface type: all `report-*` link only to `report-*`, all `newsletter-*` only to `newsletter-*`; single-page show collection renders an empty prev/next row (no dead links). |
| 4 | Fan-out diagram + every cited source render as WORKING links (vision.md → repo file) | ✗ PARTIAL | Mechanism correct: fan-out SVG boxes are real in-site `<a>` anchors (`show-ep01.html` etc.), `FanoutLink.href` populated (`semantic.py:355` now used), evidence chips render `<a>` when resolvable / plain `<span>` otherwise (19 plain-text fallbacks, no dead links). BUT the default repo-blob links point at `nneibaue/newsletters` while the real remote is `johnair01/newsletters`, and two bare-filename locators (`render.py`,`semantic.py`) map to repo-root paths that don't exist (real files under `src/newsletters/`). Structurally satisfied, not genuinely resolving as committed. See Gap. |
| 5 | All site output regenerates from renderer/templates, no hand-edited HTML | ✓ VERIFIED | Two fresh `build_site()` renders are byte-identical (no nondeterminism); committed `content/rev1/site/` is byte-identical to a fresh render (no hand-edits); `newsletters build` CLI leaves a clean git tree. No `datetime.now`/`uuid`/`random`/`today()` in render/diagrams/site. Generated marker `<!-- generated by newsletters.render; do not hand-edit -->` on all 11 committed pages. |

**Score:** 4/5 truths verified (SC4 partial).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/render.py` | `render_home`+8 section helpers, `render_library`+`_board*`, `_nav_targets`/`_breadcrumb`/`_prevnext`, `link_for_source`/`_ev_chip` | ✓ VERIFIED | All present, substantive, wired via `dogfood.build_site`. |
| `src/newsletters/diagrams.py` | `fanout(links)` wrapping boxes in SVG `<a>` | ✓ VERIFIED | `fanout()` accepts `links` map, wraps each box in `<a href=…>` (no JS); escaped via `quoteattr`. |
| `src/newsletters/dogfood.py` | route split: index=Home, library=board; per-surface `{slug}.html` stable | ✓ VERIFIED | `build_site` writes index.html via `render_home`, library.html via `render_library`, surfaces via `render_surface(site,page)`. |
| `src/newsletters/site.py` | `Page.gate` load-bearing for the board | ✓ VERIFIED | `_board` groups `site.pages()` by `Page.gate`. |
| `content/rev1/site/index.html` | 8-section Home | ✓ VERIFIED | All anchors + hero present; not the board. |
| `content/rev1/site/library.html` | 3-col gate board, no JS | ✓ VERIFIED | Grid + 3 columns + empty placeholder; only inherited toggle JS. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| nav spine | 4 hub destinations | `_nav_targets` → first `Page.href` per kind | ✓ WIRED | Resolves to real existing files; falls back to index.html (never None). |
| surface | neighbours | `_prevnext` over own `Collection.pages` | ✓ WIRED | Never crosses surface type; first/last/single handled. |
| evidence chip | repo file / in-site anchor | `link_for_source` | ⚠️ PARTIAL | Anchors emitted correctly; default targets point at wrong repo handle + two wrong paths. |
| fan-out box | in-site surface | `diagrams.fanout(_fanout_box_links)` | ✓ WIRED | Real SVG `<a>` to existing `{slug}.html`. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Two renders byte-identical (determinism) | `build_site` x2 → byte compare | 0 mismatches | ✓ PASS |
| Committed == fresh render (no hand-edits) | fresh vs `content/rev1/site` byte compare | 0 drift | ✓ PASS |
| Sanctioned build CLI | `python -m newsletters.cli build` | rendered 10 surfaces + library; clean tree | ✓ PASS |
| No dead links site-wide | grep `href="None"`/`href="#"` | 0 | ✓ PASS |
| In-site file-path links resolve | manual: render.py/semantic.py paths vs disk | repo-root paths DO NOT exist | ✗ FAIL (SC4) |

### Gate Results (re-run independently)

| Gate | Command | Result |
|------|---------|--------|
| Tests | `.venv/bin/python -m pytest -q` | **501 passed, 1 xfailed** |
| Types | `.venv/bin/python -m mypy src/newsletters` | **12 errors** — exactly the documented pre-existing baseline (capture.py, render.py 468/476/492, dogfood.py); NO new errors from Phase 9 |
| Imports | `.venv/bin/lint-imports` | **KEPT** — Core must not import any AI/LLM package (AI-optional core intact) |
| Build | `newsletters build` | clean, byte-stable tree |

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| SITE-02 | Home + separate Library | ✓ SATISFIED | SC1 |
| SITE-03 | Library status-board, gate columns, no JS | ✓ SATISFIED | SC2 |
| SITE-04 | 4 nav destinations + breadcrumbs + prev/next within type | ✓ SATISFIED | SC3 |
| SITE-05 | Fan-out + every cited source = working link | ⚠️ PARTIAL | SC4 — mechanism done, default targets don't resolve |
| SITE-06 | All output regenerated from templates, no hand-edits | ✓ SATISFIED | SC5 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| render.py | 1174 | stale docstring ("uses anchors / `#` placeholders") | ℹ️ Info | render_home docstring is out of date — §5/§7 actually resolve real hrefs; doc nit only. |
| render.py | 49 / surfaces.md:68 | `nneibaue` repo handle | ⚠️ Warning | Drives the SC4 partial — see gap. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/placeholder debt markers in any Phase-9 source file. The
`#newsletters` hrefs are legitimate in-page anchors (the demo section `id="newsletters"`), not
dead placeholders. The empty-column "placeholder" is an intended board feature.

### Hard-Rule Status

- **AI-optional core:** ✓ `lint-imports` KEPT; render/diagrams/site are stdlib-only.
- **No hand-edited HTML (SITE-06):** ✓ committed output == fresh render, byte-stable.
- **Specs source of truth:** ⚠️ `docs/surfaces.md` was NOT updated this phase; its §7 still
  specifies the stale `nneibaue` handle that the renderer faithfully reproduces. The handle drift
  is a spec/reality decision, not silent code drift — but it should be resolved.
- **No auto-publish / gate intact:** ✓ the board reflects real `Page.gate`; rendering never mutates gate state.
- **Visual fidelity:** Deferred to the separate UI review per CONTEXT. No obvious token drift
  observed (CSS ported 1:1, `--radius:0px`, three-font system present).

### Source-Link "Working vs Structural" Judgment (the SC4 verdict)

The renderer does everything SITE-05 asks for *structurally*: real `<a>` anchors, the three-branch
resolution rule, plain-text fallback that never emits a dead link, populated `FanoutLink.href`, and
navigable SVG fan-out boxes with no JS. The *data* is the problem. As committed:

- **Repo handle is wrong for this repo.** `repo_url = nneibaue/newsletters` (render.py:49); the live
  remote is `johnair01/newsletters`. Every repo-blob link 404s against the real host.
- **Two locator paths are wrong even ignoring the handle.** `render.py` and `semantic.py` resolve to
  `blob/main/render.py` / `blob/main/semantic.py`, but the files live under `src/newsletters/`.
- It is configurable (`source_base_url` is a single constant), and the spec itself names `nneibaue`,
  so this is partly spec drift. But "every cited source renders as a *working* link" is the literal
  criterion, and these links do not currently work. **Recommendation:** treat as a real (small) gap —
  point `source_base_url` at the real remote (or document it as a deploy-time knob and update
  surfaces.md), and fix the two bare-filename locators to their `src/newsletters/` paths.

### Human Verification Required

None blocking for this report (visual fidelity is handled by the separate UI review). The author
should DECIDE on the SC4 gap: fix the repo handle/paths now, or accept `nneibaue` as the canonical
public handle and treat link resolution as a deploy-time config (in which case record an override).

### Gaps Summary

Four of five success criteria are solidly achieved in live code and committed output, with all four
DoD gates green (501 passed, 12 baseline mypy errors only, lint-imports KEPT, byte-stable build).
The single gap is SC4/SITE-05: the source-link machinery is complete and faithful, but the default
link targets do not resolve for this repo — the repo handle (`nneibaue` vs `johnair01`) and two
bare-filename paths point at non-existent locations. This is a small, configurable fix (plus a
spec-handle decision), but it means "every cited source renders as a working link" is not literally
true as committed. Phase should not be marked fully passed until the handle/paths are corrected or
the deviation is explicitly accepted via an override.

---

_Verified: 2026-06-18_
_Verifier: Claude (gsd-verifier)_
