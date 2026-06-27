---
phase: 10-reviewer-surfacing-merge-block
verified: 2026-06-18T00:00:00Z
status: passed
score: 3/3 success criteria verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: none
---

# Phase 10: Reviewer Surfacing & Merge-Block Gate — Verification Report

**Phase Goal:** Make the human review gate REAL, not a rubber stamp — surface every `missing[]`/`unextracted[]` on every surface, show each claim next to its verbatim trace by default, and block merge in CI while any claim is STALE, un-entailed, or has open gaps.
**Requirements:** PROV-03, PROV-04
**Verified:** 2026-06-18 (branch `claude/youthful-fermi-dly6mi`, gates via `.venv/bin/python`)
**Status:** passed
**Re-verification:** No — initial verification

This is a trust-core phase. I did NOT trust the clean pass: I constructed a LIVE blocked corpus
(STALE / un-entailed / open-`missing[]`) and confirmed the gate FIRES at both the function and the
CLI exit-code boundary, and that Draft/In-Review are exempt.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth (Success Criterion) | Status | Evidence |
|---|---------------------------|--------|----------|
| 1 | `missing[]` and `unextracted[]` surfaced to the reviewer on EVERY surface, never hidden (PROV-03) | ✓ VERIFIED | `render.py:716` `_honesty_panel` rendered once on every `render_surface` (`render.py:809-810`); built output: all 9 rendered Surfaces carry `class="honesty"` (1 each); `index.html`/`library.html` = 0 (they are Home/Library aggregation pages via `render_home`/`render_library`, not Surfaces — `dogfood.py:678-685`). Panel lists `surface.missing[]` + every `Source.extraction.unextracted[]`; clean corpus shows positive "Fully traced — nothing outstanding" confirmation (presence is the proof). `test_honesty_panel_lists_missing_and_unextracted` asserts populated content + escaping. |
| 2 | CI blocks merge of any surface with a STALE, un-entailed, or open-`missing[]` claim (PROV-04) | ✓ VERIFIED | `review.py:58` `review_blockers` (published-only, reuses `Claim.is_stale` + `SpanContainmentFaithfulness.entails`, no new trust logic). `cli.py:41` `newsletters check` exits 1 on any blocker / 0 clean. `ci.yml:75` `merge-block` job (bare `.[test]`, runs `newsletters check`). **LIVE GATE-FIRES proof below.** |
| 3 | Review view shows each claim next to its verbatim trace BY DEFAULT (unfaithful visible without a click) (PROV-03) | ✓ VERIFIED | `render.py:465` `_claim_spans` renders each addressed `Trace.span` inline in a `.claim-span` box under the claim text, no JS; `render.py:449` `_claim_badge` adds inline amber STALE/unfaithful badge. Built output: 4 content-addressed surfaces each carry a real verbatim `class="claim-span"` box (e.g. "Two layers, not five peers..."). Only 1 `<script>` per surface (theme toggle) — span view is no-click/no-JS. |

**Score:** 3/3 criteria verified.

### LIVE Gate-Fires Probe (the trust core — exercised the FAILURE path)

Constructed three crafted PUBLISHED surfaces and ran the real `review_blockers` + the real CLI:

| Blocker construction | `review_blockers` result | Status |
|----------------------|--------------------------|--------|
| STALE — `Trace.from_source` then mutated `src.transcript` (live hash drifts) | exactly `[Blocker(kind=stale)]` | ✓ FIRES |
| UNENTAILED — addressed trace whose span omits the claim text | exactly `[Blocker(kind=unentailed)]` | ✓ FIRES |
| OPEN_MISSING — published surface with non-empty `Surface.missing` | exactly `[Blocker(kind=open_missing)]` | ✓ FIRES |
| EXEMPTION — same STALE defect on a Draft surface | `[]` | ✓ EXEMPT |
| EXEMPTION — STALE + open-missing on an In-Review surface | `[]` | ✓ EXEMPT |

**CLI exit-code (end-to-end, monkeypatched `build_surfaces` → one blocked published surface):**
```
EXIT CODE: 1
BLOCK [stale] sfc-blocked: original content here
1 blocker(s) across the corpus — merge blocked (PROV-04).
```
**Clean shipped corpus:** `.venv/bin/newsletters check` → `All published surfaces clean — no blockers.` → `exit=0`.

The gate is proven BOTH directions: nonzero on a live blocked corpus, zero on the clean corpus. A
gate that only ever sees clean input is not what we have here.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/review.py` | `BlockerKind` + `Blocker` + `review_blockers` | ✓ VERIFIED | Substantive (122 lines), published-only, STALE-first `elif`-guard, reuses existing predicates, AI-free. Wired: imported by `cli.py:58`. |
| `src/newsletters/semantic.py` (`Surface.missing`) | additive str carrier | ✓ VERIFIED | `semantic.py:487` `missing: list[str] = Field(default_factory=list)`. Git diff confirms ONLY this field added; publish gate untouched. |
| `src/newsletters/cli.py` (`check`) | exit 0 clean / 1 blocked | ✓ VERIFIED | `cli.py:40-73`, lazy-imports checker + corpus, corpus-wide sources lookup, `typer.Exit(1)`. Wired into the CI job. |
| `src/newsletters/render.py` (surfacing) | honesty panel + claim-span + badge | ✓ VERIFIED | `_honesty_panel` (716), `_claim_spans` (465), `_claim_badge` (449), threaded via `render_surface` (753). Wired & data flows (see below). |
| `.github/workflows/ci.yml` | 3 jobs incl. merge-block | ✓ VERIFIED | jobs = `['bare-install','merge-block','import-linter']`; merge-block installs `.[test]` (no `[ai]`), runs `newsletters check`. |
| `content/rev1/site/*.html` | regenerated, byte-stable | ✓ VERIFIED | 11 files; rebuild to `/tmp` diffed identical (zero DIFFERS) — byte-stable (SITE-06). |
| `tests/{test_review,test_review_cli,test_render}.py` | gate-fires + surfacing tests | ✓ VERIFIED | Negatives for all 3 blocker kinds + exemptions + CLI exit both ways + populated honesty panel + inline badge + XSS-escape + no-JS. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `_honesty_panel` | `surface.missing[]` + `Source.extraction.unextracted[]` | typed model fields, threaded from `render_surface` | Yes — `test_honesty_panel_lists_missing_and_unextracted` proves populated content renders; clean corpus correctly shows positive confirmation | ✓ FLOWING |
| `_claim_spans` | `Trace.span` (addressed, non-empty) | `surface.traces` → `{s.id:s}` self-derived in `render_surface:792` | Yes — 4 built surfaces show real verbatim span boxes | ✓ FLOWING |
| `_claim_badge` | `Claim.is_stale(sources)` / `entails(claim)` | live `{source_id:Source}` lookup | Yes — fires in `test_claim_flags_stale_and_unfaithful_inline`; correctly silent on clean corpus | ✓ FLOWING |
| `review_blockers` | `Surface.blocks`/`missing`/live source hashes | the dogfood corpus | Yes — live probe fires all 3 kinds | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite | `.venv/bin/python -m pytest -q` | 524 passed, 1 xfailed | ✓ PASS |
| Clean gate exits 0 | `.venv/bin/newsletters check` | clean message, exit 0 | ✓ PASS |
| Gate FIRES (blocked) | live probe + CLI monkeypatch | exit 1, BLOCK report | ✓ PASS |
| Import contract | `.venv/bin/lint-imports` | 1 kept, 0 broken | ✓ PASS |
| Type check | `.venv/bin/mypy src/newsletters` | 12 errors, all pre-existing (capture.py:1, dogfood.py:8, render.py:3 — the `rows` list→str reassignments in pre-existing Chapters/Items/Fanout branches; zero in review.py/cli.py/new surfacing) | ✓ PASS (no new) |
| Build byte-stable | `newsletters build --out /tmp/site-verify` + diff | 11/11 identical | ✓ PASS |
| AI-optional | `pytest tests/test_ai_optional.py -q` | 14 passed, 1 xfailed (documented plugin-leak xfail) | ✓ PASS |
| CI structure | yaml parse | 3 jobs, merge-block bare `.[test]` + `newsletters check` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PROV-03 | 10-01, 10-03 | `missing[]`/`unextracted[]` surfaced every surface + claim-beside-trace | ✓ SATISFIED | Honesty panel + claim-span on every Surface (built output) |
| PROV-04 | 10-01, 10-02 | CI blocks merge of STALE/un-entailed/open-missing | ✓ SATISFIED | `review_blockers` + `newsletters check` exit-1 + merge-block CI job; gate-fires proven live |

### Hard-Rule Status

| Hard rule | Status | Evidence |
|-----------|--------|----------|
| No auto-publish / gate UNCHANGED | ✓ INTACT | Git diff on semantic.py = only the additive `Surface.missing` field; `Review._published_requires_satisfied_policy` / `open_pull_request` / `approve` untouched; 46 publish/gate/review tests pass. The checker ADDS enforcement, never publishes or mutates the gate. |
| Every published claim traces; unsubstantiated → `missing[]` shown | ✓ STRENGTHENED | Now literal (honesty panel shows it on every surface) AND enforced (open-missing is a CI blocker). |
| Faithful, not suggestive | ✓ HELD | Verbatim spans shown (`_claim_spans` renders `Trace.span` unmodified); un-addressed Rev1 traces show chip alone (no empty box, no false badge). |
| AI-optional core | ✓ HELD | `review.py`/`cli.py` import only `.semantic` + `.distill.faithfulness` + stdlib/typer; `lint-imports` 1 kept/0 broken; merge-block CI job runs on bare `.[test]` (no `[ai]`). |
| Determinism / no hand-edited HTML | ✓ HELD | Surfacing rendered from typed data; built site byte-stable across two renders. |

### Anti-Patterns Found

None. No `TODO`/`FIXME`/`XXX`/placeholder markers in the phase-modified source. `Surface.missing`
defaulting to `[]` is an intentional documented carrier (populated at the capture/promote seam in a
later plan), not a UI stub — the gate-fires proof uses crafted fixtures, not the corpus.

### Scope / Bypass Analysis (adversarial)

I actively looked for a published path that bypasses the gate. Honest findings:

1. **Claim-kind coverage — no bypass.** `ClaimsBlock` is the ONLY block type carrying `Claim`
   objects (verified across all 10 block types). All other blocks hold non-claim content
   (KpiItem/Chapter/LetterItem/FanoutLink/prose strings). `QuoteBlock.text` / `RationaleBlock.text`
   are free narrative, not traced claims — correctly out of scope ("emphasis/narrative is the
   human's job"). `review_blockers` checking every `ClaimsBlock` covers every checkable claim.

2. **Corpus enumeration — scoped, not a defect.** `newsletters check` enumerates the in-code dogfood
   corpus (`build_surfaces()` → fixed list of all 7 surface families). A hand-authored surface added
   OUTSIDE `build_surfaces()` (e.g. a future on-disk corpus) would not be enumerated. That is the
   correct scope for this phase — the dogfood corpus IS today's published set; on-disk/work-codebase
   corpora are Phase 11 (Work-Surface Installation). Not a Phase-10 gap. Worth carrying forward so
   Phase 11 wires the work corpus into `check`.

3. **`logfire` ambient leak — pre-existing, not Phase-10.** Importing pydantic pulls `logfire` into
   the dev venv via the pydantic-plugin entry-point (documented in
   `.planning/notes/ai-optional-pydantic-plugin-leak.md`). No source file imports logfire; `import
   newsletters` alone triggers it. The canonical defense is the bare-install CI job where logfire is
   absent. Not introduced by this phase; review.py/cli.py are AI-free per lint-imports.

### Human Verification Required

None. All three criteria are verifiable programmatically (built-HTML inspection, live blocked-corpus
probe, exit-code contract). The visual rendering was confirmed via grep on built output and the
no-JS/no-click guarantee via `<script>` count (= 1, the theme toggle only).

### Gaps Summary

No blocking gaps. All 3 success criteria VERIFIED against live code + built output + live
gate-fires probes. The trust gate genuinely BLOCKS (proven nonzero on a crafted STALE/un-entailed/
open-missing published corpus) and correctly exempts Draft/In-Review. The no-auto-publish gate is
unchanged. One forward note (not a gap): Phase 11 should wire any on-disk/work-codebase corpus into
`newsletters check` so newly-authored published surfaces are enumerated by the gate.

---

_Verified: 2026-06-18_
_Verifier: Claude (gsd-verifier) — goal-backward, gate-fires exercised live_
