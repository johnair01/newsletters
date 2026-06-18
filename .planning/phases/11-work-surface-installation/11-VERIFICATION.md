---
phase: 11-work-surface-installation
verified: 2026-06-18T23:55:00Z
status: passed
score: 3/3 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
---

# Phase 11: Work-Surface Installation — Verification Report

**Phase Goal:** Prove the whole pipeline on a real work codebase — install Newsletters, point read-only adapters at the code (data stays LOCAL, no external calls on content), author a Report by hand, and publish a Library that shows HOW the work was done (Provenance/Lineage on each surface).
**Verified:** 2026-06-18T23:55:00Z
**Status:** passed
**Re-verification:** No — initial verification
**Mode:** mvp (ROADMAP `Mode: mvp`). The phase goal is NOT in User-Story form ("As a… I want… so that…"), so standard goal-backward verification was applied with the three ROADMAP Success Criteria (WORK-01/02/03) as the observable truths. (Surfaced as a minor MVP-mode mismatch, not a blocker — see Gaps Summary.)

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 (WORK-01) | Operator can `pip install` + point read-only adapters at a work codebase, all data local (no external calls on content) | ✓ VERIFIED | `capture_files` read-only by construction (only `Path.read_text`, no network import) — live probe on a temp tree: mtime+sha256 of every file unchanged, zero new files. Both built sites contain ZERO auto-loading external URLs (grep across `content/rev1/site/*.html` + `content/work/site/*.html`: no `fonts.googleapis`, no `@import`, no `src="http`, no `<link href=http`, no `url(http`). |
| 2 (WORK-02) | Operator can author a Report by hand (manual backend) inheriting the traced structure | ✓ VERIFIED | `build_work_surfaces()` live: 7 surviving claims, ALL `is_addressed` with `claim.text == trace.span` (verbatim, content-addressed to real repo files via `Trace.from_source`); the deliberately-paraphrased claim routed to `missing[]` (never fabricated); surface gate = **draft** (no auto-publish); zero-AI manual backend (`capture.build_report`). |
| 3 (WORK-03) | Published Library shows how the work was done (Provenance/Lineage visible on each surface) AND work corpus runs the SAME gate | ✓ VERIFIED | Built `content/work/site/work-report.html` shows: 7 `claim-span` verbatim traces, `ev-chip` claim→repo-file links (resolve to johnair01/newsletters real files), honesty panel with the missing claim ("unsubstantiated"), masthead `captured via Claude Code · derived from CLAUDE.md, docs/architecture.md, src/newsletters/capture.py, src/newsletters/semantic.py`, and the fan-out chain (3 audience surfaces). `newsletters check --corpus work` exits 0 clean; planted published blocker → exit 1 (same corpus-agnostic `review_blockers`). |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/worksurface.py` | `capture_files` (read-only ingest), `build_work_report`/`build_work_surfaces` (hand-authored traced Report), `build_work_site` (publish) | ✓ VERIFIED | 437 lines, substantive. Imports only stdlib (`pathlib`, `shutil`) + core `semantic`/`capture`/`render`/`site` — no AI, no network. All four `__all__` exports present and exercised. |
| `src/newsletters/render.py` (font fix) | Self-hosted `@font-face`, no Google-Fonts `@import` | ✓ VERIFIED | Lines 104-114: 7 `@font-face` blocks with RELATIVE `src:url('fonts/…woff2')`. No `@import`, no `fonts.googleapis` anywhere. `repo_url` (line 53) is an absolute navigation anchor (A2-allowed). |
| `src/newsletters/cli.py` (`--corpus`) | `--corpus {rev1|work}` on build + check, routing to work corpus, same gate | ✓ VERIFIED | `CorpusName` enum; `--corpus` on both build (→ `build_work_site`) and check (→ `build_work_surfaces` + `review_blockers`). Default rev1 unchanged. |
| `content/work/site/` | Rendered work Library (HTML + self-hosted fonts), no external URL | ✓ VERIFIED | `work-report.html`, `library.html`, `fonts/` (7 woff2 + 3 OFL licenses). Regenerates byte-identical (sha256 match on both HTML files). |
| `content/work/ids.json` | Work corpus append-only ledger, separate from rev1 | ✓ VERIFIED | `{"work-report": {"ref": "R-001", "type": "report", …}}`. Distinct from `content/rev1/ids.json` (rev1 unchanged — git clean). |
| `content/rev1/site/fonts/` | Vendored OFL woff2 + OFL.txt licenses | ✓ VERIFIED | 7 woff2 + 3 `OFL-*.txt` present and travel with the fonts. |
| `tests/test_worksurface.py` | Read-only, traced-structure, no-external-call, provenance/lineage, gate-block tests | ✓ VERIFIED | 11 tests, all PASS. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `capture_files` | `Source` / `Trace.from_source` | `Source(id=relpath, transcript=read_text)`, content-addressed | ✓ WIRED | Live: source ids are POSIX relpaths recognized by `_is_file_path_locator`; claims pin via `Trace.from_source`. |
| `build_work_report` claim | ingested file span | `Trace.from_source(src, find(claim.text), …)` or `missing[]` | ✓ WIRED | 7 verbatim claims pinned; 1 paraphrase → `missing[]`. |
| `Surface.lineage` | ingested ids + fan-out ids | `derived_from`/`produced` populated | ✓ WIRED | `derived_from` = 4 cited files; `produced` = 3 fan-out titles. Both render in masthead. |
| `content/work/site/*.html` | cited repo files + fan-out | `link_for_source` + masthead + `_fanout_row` | ✓ WIRED | `ev-chip` anchors resolve to johnair01/newsletters real files; fan-out rows render. |
| `cli.py check --corpus work` | `review_blockers` over `build_work_surfaces` | corpus-agnostic merge-block gate | ✓ WIRED | Live: clean → exit 0, planted blocker → exit 1. |
| `content/work/site/` | `fonts/*.woff2` | `@font-face` + `build_work_site` emits fonts | ✓ WIRED | `_emit_fonts` copies the vendored set (woff2 + OFL) into the work output. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `work-report.html` | claim spans / ev-chips | `build_work_surfaces` → `capture_files` over real repo files | Yes — verbatim slices of CLAUDE.md / semantic.py / capture.py / architecture.md | ✓ FLOWING |
| `work-report.html` | honesty panel | `Surface.missing[]` | Yes — the real paraphrased claim | ✓ FLOWING |
| `work-report.html` | masthead lineage | `Surface.lineage.derived_from/produced` | Yes — actual ingested file ids + fan-out titles | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Read-only ingest | live probe: snapshot temp tree, `capture_files`, re-snapshot | mtime+sha256 unchanged, no new files | ✓ PASS |
| WORK-02 traced structure | live `build_work_surfaces()` | 7 claims is_addressed, text==span, paraphrase→missing, gate=draft | ✓ PASS |
| Byte-stable regen | rebuild work site to temp, sha256 vs committed | both HTML identical | ✓ PASS |
| Gate clean (rev1+work) | `newsletters check --corpus {rev1,work}` | both exit 0 | ✓ PASS |
| Gate blocks (work) | planted published blocker via test helper | exit 1, "1 blocker(s) … merge blocked" | ✓ PASS |
| Build both corpora | `newsletters build --corpus {rev1,work}` | 10+1 / 1+1 surfaces rendered; fonts+OFL emitted; no external call | ✓ PASS |
| AI-optional import | `import newsletters.worksurface` (bare) | clean | ✓ PASS |
| No-external-call (both sites) | grep auto-load patterns | none | ✓ PASS |

### Gate Results (re-run independently via .venv/bin/python)

| Gate | Result |
|------|--------|
| `pytest -q` (full) | **537 passed, 1 xfailed** in 14.0s |
| `tests/test_worksurface.py` | **11/11 PASSED** |
| `mypy src/newsletters` | **12 errors** — all PRE-EXISTING (8 dogfood.py, 1 capture.py, 3 render.py at lines 530/538/554 blamed to commits 5aca6f2d/6f665a21, NOT the Phase-11 font commits). ZERO new errors in `worksurface.py`/`cli.py`/the font change. |
| `lint-imports` | **KEPT** — "Core (newsletters) must not import any AI/LLM package" (1 kept, 0 broken) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| WORK-01 | 11-01, 11-02 | pip install + read-only adapters, data local | ✓ SATISFIED | Truth 1 + read-only probe + no-external-call grep |
| WORK-02 | 11-03 | author Report by hand inheriting traced structure | ✓ SATISFIED | Truth 2 + live traced-structure probe |
| WORK-03 | 11-03, 11-04, 11-05 | published Library shows process via Provenance/Lineage; same gate | ✓ SATISFIED | Truth 3 + built HTML devices + live gate-block |

No orphaned requirements — all three WORK ids are claimed by plans and verified.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No `TBD`/`FIXME`/`XXX` debt markers in Phase-11 files; no hollow stubs; no `return []`/`{}` that flows to render | — | Clean. The few `return` early-exits (`_emit_fonts` when fonts dir absent) are documented graceful-degradation, not stubs. |

### Hard-Rule Status

| Hard rule | Status | Evidence |
|-----------|--------|----------|
| No external calls baked in (now literal) | ✓ HELD | Both built sites: zero auto-loading external URLs; fonts vendored + OFL licenses travel. Only external URLs are `<a>` navigation anchors (A2). |
| Read-only on the target | ✓ HELD | `capture_files` only `Path.read_text`; live probe confirms zero mutation, no new files; no network import. |
| Every claim traces to evidence | ✓ HELD | 7 surviving claims all content-addressed verbatim; paraphrase → `missing[]` (shown, never fabricated). |
| No auto-publish | ✓ HELD | work-report gate = **draft**; gate-block test proves the publish gate fails nonzero on an unsafe published surface. |
| AI-optional core | ✓ HELD | lint-imports KEPT; `worksurface` imports on bare install; test_ai_optional extended to worksurface. |
| Determinism / byte-stable | ✓ HELD | `EPOCH_ZERO` sources, sorted inputs, append-only ledger; both HTML regenerate byte-identical. |
| Work corpus separate from rev1 | ✓ HELD | own ledger `content/work/ids.json`; rev1 git-clean / unchanged. |

### Human Verification Required

None. All three success criteria are verifiable programmatically against live code and built output (read-only probe, no-external-call grep, content-addressing assertions, live gate exit codes). Visual fidelity of the work Library is a nice-to-have but the goal ("shows HOW the work was done") is satisfied by the verified presence of the provenance/lineage/honesty devices in the built HTML.

### Gaps Summary

No blocking gaps. The phase goal and all three success criteria (WORK-01/02/03) are achieved in live code and built output, independently re-verified (not trusted from SUMMARYs):

- WORK-01: the new `capture_files` ingest is read-only by construction and the no-external-call guarantee is now literal across BOTH built sites (the Google-Fonts `@import` was removed and replaced with vendored self-hosted `@font-face`, OFL licenses included).
- WORK-02: a real hand-authored Draft Report content-addresses its claims verbatim to actual repo files, with the deliberate paraphrase honestly surfaced as missing — never fabricated, never auto-published.
- WORK-03: the published work Library surfaces the full process (claim→repo-file links, verbatim spans, honesty panel, derived-from/fan-out lineage) reusing the Phase 9/10 devices, and the work corpus runs the IDENTICAL merge-block gate (exit 0 clean / exit 1 on a planted blocker).

The "real codebase" demonstration is HONEST, not a hollow stub: claims trace to repo files that exist, the anchor links resolve to johnair01/newsletters real paths, no path makes an external call on content, and rev1 is untouched.

**Minor note (not a gap):** ROADMAP marks the phase `Mode: mvp`, but the phase goal is a standard goal, not a User-Story ("As a… I want… so that…"). Per `verify-mvp-mode.md` this would normally trigger a "reformat the goal" request; here it had no material effect — the three explicit Success Criteria are the contract and were fully verified. Recorded for awareness; does not block the phase.

**Pre-existing mypy debt (not introduced here):** 12 mypy errors persist in dogfood.py/capture.py/render.py (the render.py ones blame to pre-Phase-11 commits). Phase 11 added zero new type errors. This is existing tech debt outside this phase's scope.

---

_Verified: 2026-06-18T23:55:00Z_
_Verifier: Claude (gsd-verifier)_
