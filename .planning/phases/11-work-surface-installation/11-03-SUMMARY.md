---
phase: 11-work-surface-installation
plan: 03
subsystem: work-report
tags: [capture, content-address, trace, lineage, missing, ledger, ai-optional, determinism]

# Dependency graph
requires:
  - phase: 11-work-surface-installation
    provides: "capture_files(paths, *, root) -> list[Source] (Plan 11-02) — the ingested file Sources the claims pin into"
  - phase: 01-foundation
    provides: "Trace.from_source / Surface.missing[] / Surface.lineage — the content-address + honesty + fan-out carriers"
  - phase: 03-capture-promote
    provides: "capture.build_report / WorkSession / Decision — the zero-AI manual backend that lifts a session into a traced Draft Report"
  - phase: 08-10-site-render
    provides: "site.Ledger — the append-only slug->ref ledger API reused to seed the work corpus"
provides:
  - "build_work_report(sources, decisions, *, surface_id, title, author, narrative, tool, eyebrow) -> Surface: hand-author a Draft work Report; each claim content-addresses to a verbatim file span OR routes to missing[]"
  - "build_work_surfaces(*, root, author) -> list[Surface]: assemble the WORK corpus (curated real-file ingest + verbatim hand-written decisions)"
  - "Surface.lineage.derived_from populated with the ingested file ids each surface cites (WORK-03 structure half)"
  - "content/work/ids.json — the work corpus's own append-only ledger (work-report -> R-001), separate from content/rev1/"
affects: [11-04-publish-render, 11-05-check-corpus, work-surface, provenance, lineage]

# Tech tracking
tech-stack:
  added: []  # ZERO new runtime dependency — capture + semantic + site + stdlib only
  patterns:
    - "Hand-authored claim content-addresses to a REAL repo file: str.find(claim.text) -> Trace.from_source over the verbatim slice (mirrors dogfood._address_report, but the corpus is real code, not a synthesized transcript)"
    - "Faithful-not-suggestive routing: a claim whose text is NOT verbatim-locatable is dropped from the ClaimsBlock and its text appended to Surface.missing[] — NEVER a fabricated offset"
    - "Every surviving ClaimsBlock claim is genuinely traced -> open_pull_request invariant 2 holds by construction"
    - "Surface.lineage.derived_from = the ingested file ids actually cited by surviving claims (computed, not hand-listed)"
    - "Work corpus ledger seeded via the same Ledger.load -> Site.from_surfaces -> ledger.save discipline as build_site — refs append-only / immutable, never hand-edited"

key-files:
  created:
    - content/work/ids.json
  modified:
    - src/newsletters/worksurface.py
    - tests/test_worksurface.py

key-decisions:
  - "build_work_report takes decisions explicitly (sources, decisions, *, ...) rather than embedding a fixed list, so the author path is reusable and the corpus content lives in build_work_surfaces — keeps the minting logic generic and the curated content in one place"
  - "Un-locatable claims are DROPPED from the ClaimsBlock (not left untraced) AND mirrored into Surface.missing[] — this is the only way open_pull_request's untraced-claim invariant and the honesty panel are both satisfied without fabricating evidence"
  - "lineage.produced left empty here — the fan-out surfaces do not exist until Plan 11-04; derived_from is the structure that is real NOW so the masthead 'derived from' line is real from this wave"
  - "Lineage field already existed at semantic.py:496 (added in a prior plan) — no schema change needed; L4 is pure population, additive and backward-compatible (529->530 suite stays green)"
  - "Work corpus is a SEPARATE ledger (content/work/ids.json) starting its own R-001 ordinal — the sample (content/rev1/) vs real (content/work/) boundary is preserved at the ledger layer"

patterns-established:
  - "Real-codebase content-addressing: a hand-authored Report's claims pin to verbatim spans of live repo files, drift-checkable via Trace.is_stale_against"
  - "Traced-or-missing invariant test: assert EVERY claim is_addressed to an ingested id OR in missing[], plus >=1 real addressed claim and >=1 honest missing entry"

requirements-completed: [WORK-02, WORK-03]

# Metrics
duration: 4min
completed: 2026-06-18
---

# Phase 11 Plan 03: Hand-authored work Report (traced to the code) Summary

A hand-authored Report **about how this build was done** now exists as the WORK corpus, built
through the zero-AI manual backend (`capture.build_report`) and content-addressed to **real
repository files**: each load-bearing decision pins (`Trace.from_source`) to a *verbatim span*
of a live file, and a deliberately-paraphrased claim is routed honestly to `Surface.missing[]`
rather than given a fabricated offset. WORK-02 (the hand-authored traced Report) and the
structure half of WORK-03 (populated `Surface.lineage`) made real on this repo, with its own
append-only ledger.

## What was built

- **`build_work_report(sources, decisions, *, surface_id, title, author, narrative, tool, eyebrow) -> Surface`**
  (`src/newsletters/worksurface.py`): builds a `WorkSession` from hand-written `Decision`s +
  ingested `Source`s, lifts it via `capture.build_report` (zero AI) to a Draft Report with a
  traced `ClaimsBlock` + provenance, then content-addresses each claim by mirroring dogfood
  `_address_report`: `start = src.transcript.find(claim.text)`; `>= 0` → pin via
  `Trace.from_source(src, start, start+len)` (span = the verbatim file slice); `< 0` → drop the
  claim and append its text to `Surface.missing[]`. Finally populates `lineage.derived_from`.
- **`build_work_surfaces(*, root, author) -> list[Surface]`**: ingests the curated file list via
  `capture_files`, authors the verbatim decisions (plus one paraphrase), and returns the work
  corpus (`[work-report]`). This is what the renderer (11-04) and the check gate (11-05) consume.
- **`content/work/ids.json`**: the work corpus's own append-only ledger, generated via the
  `Ledger.load → Site.from_surfaces → ledger.save` discipline (not hand-edited). `work-report → R-001`.

### Signatures (for Plan 11-04)

```python
build_work_report(
    sources: Sequence[Source],
    decisions: Sequence[Decision],
    *, surface_id: str, title: str, author: str, narrative: str,
    tool: str = "Claude Code",
    eyebrow: str = "Report · how this build was done",
) -> Surface
build_work_surfaces(*, root: Path | None = None, author: str = "Claude") -> list[Surface]
```

### Curated ingested file list

`build_work_surfaces` ingests `_WORK_FILES` (a curated list, never a broad glob — no orphan Sources):

- `CLAUDE.md`
- `src/newsletters/semantic.py`
- `src/newsletters/capture.py`
- `docs/architecture.md`

### Claims → files mapping (what content-addressed vs went to missing[])

The work Report carries **7 content-addressed claims** across **4 files** and **1 missing**:

| Claim text (verbatim) | Cited file | Span offsets |
|---|---|---|
| `No auto-publish, ever.` | `CLAUDE.md` | 3898:3920 |
| `Every published claim traces to evidence.` | `CLAUDE.md` | 4153:4194 |
| `AI-optional core.` | `CLAUDE.md` | 4367:4384 |
| `Faithful, not suggestive.` | `CLAUDE.md` | 4614:4639 |
| `Cannot open a review with untraced claims; move them to \`missing\`.` | `src/newsletters/semantic.py` | 20734:20800 |
| `Newsletters does **not** do the problem-solving.` | `src/newsletters/capture.py` | 81:129 |
| `recorded \`reviewer\`. **No auto-publish path exists.**` | `docs/architecture.md` | 1847:1900 |

**Routed to `Surface.missing[]`** (deliberate paraphrase, not verbatim in any cited file — proves
honesty is real, no fabricated offset):

- `"Newsletters quietly publishes the best draft on the operator's behalf."`

(Offsets are character positions into each file's live transcript; spans are drift-checkable via
`Trace.is_stale_against` — they will go STALE if the cited line changes, which is the point.)

### Surface.lineage shape

```python
surface.lineage.derived_from == [
    "CLAUDE.md", "docs/architecture.md",
    "src/newsletters/capture.py", "src/newsletters/semantic.py",
]   # the ingested file ids actually cited by surviving claims
surface.lineage.produced == []   # fan-out surfaces land in Plan 11-04
```

### The work ledger

```json
{ "work-report": { "date": null, "issue": null, "ref": "R-001", "type": "report" } }
```

Generated via the `Ledger` API (append-only, `sort_keys`, trailing newline). A **separate corpus**
from `content/rev1/` — the work ledger starts its own `R-001` ordinal, keeping the sample/real
boundary at the ledger layer. Refs are immutable from the first render.

## Deviations from Plan

None — plan executed exactly as written. The `Lineage` field the plan flagged as "add minimally
if absent" already existed at `semantic.py:496` (a prior plan), so L4 was pure population with no
schema change. One in-task correctness fix below.

### Auto-fixed Issues

**1. [Rule 1 - Bug] mypy union-attr on the trace branch**
- **Found during:** Task 2 (mypy gate)
- **Issue:** the initial loop computed `trace = claim.evidence[0] if claim.evidence else None`,
  so mypy could not narrow `trace` to non-`None` at the `Trace.from_source(..., locator=trace.locator)`
  call — 1 NEW error (`Item "None" of "Trace | None" has no attribute "locator"`, worksurface.py:192),
  pushing the count to 13 vs the 12 baseline.
- **Fix:** restructured to `if not claim.evidence: route to missing[]; continue` then bind
  `trace = claim.evidence[0]` unconditionally — mypy narrows cleanly; back to 12 baseline errors.
- **Files modified:** `src/newsletters/worksurface.py`
- **Commit:** `130af08`

## Gate results (re-run independently — actual output)

- `pytest tests/test_worksurface.py -q` → **4 passed, 1 skipped** (the e2e scaffold stays skipped until 11-04/11-05)
- `pytest -q` (full) → **530 passed, 1 skipped, 1 xfailed** (baseline 529 + the 1 new traced-structure test)
- `mypy src/newsletters` → **12 errors** (exactly the pre-existing baseline; worksurface.py has none)
- `lint-imports` → **1 kept, 0 broken** (worksurface.py stays AI-free)
- `content/work/ids.json` → non-empty append-only ledger (`work-report → R-001`)

## Note for Wave 3 (Plan 11-04)

Plan 11-04 publishes the work site reusing `render.py` + the populated `Surface.lineage`, and will
fill `lineage.produced` once the fan-out surfaces exist. It should load `content/work/ids.json` via
`Ledger.load("content/work/ids.json")` (the same discipline as `build_site`) so refs stay stable,
and must NOT touch `render.py`'s rev1 path or `content/rev1/`.

## Known Stubs

None that prevent the plan's goal. `lineage.produced == []` is intentional and documented — the
fan-out surfaces do not exist until Plan 11-04; `derived_from` (the structure that is real now) is
fully populated. The e2e scaffold test (`test_operator_flow_end_to_end`) remains skipped by design
(its publish/render/check stages land in 11-04/11-05).

## Self-Check: PASSED

- Files: `content/work/ids.json`, `src/newsletters/worksurface.py`, `tests/test_worksurface.py`,
  `.planning/phases/11-work-surface-installation/11-03-SUMMARY.md` — all FOUND.
- Commits: `a3a2d97` (test/RED), `130af08` (feat/GREEN), `8229db1` (chore/ledger) — all FOUND.
- `build_work_report` present in `worksurface.py`.
