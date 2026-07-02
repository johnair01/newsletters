---
phase: 02-module-scope-report-composer
plan: 03
subsystem: api
tags: [composer, ledger, quote, fanout, faithfulness, determinism, pydantic]

# Dependency graph
requires:
  - phase: 02-02
    provides: "compose.py core — compute_delta + compose_module_report (per-lane KpiStripBlock/ClaimsBlock, missing[] routing, EPOCH_ZERO determinism)"
  - phase: 01-swim-lane-binding-traced-yaml-loader
    provides: "SwimlaneLoad / SectionBinding (traced bindings, kpi_endpoints); site.Ledger + slugify (the R-NNN authority)"
provides:
  - "Sourced-or-omit owner/manager QuoteBlock (traced claim -> QuoteBlock(text, attr=owner id); absent -> omit + missing[] note; never fabricated)"
  - "Always-present FanoutBlock stub (declared kinds article/newsletter/learning, every href=None)"
  - "Stable, append-only R-NNN via the REUSED site.Ledger keyed by the surface slug (first report -> R-001); compose is disk-write-free (no save())"
affects: [phase-03, build_module_site, module-site-render]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Sourced-or-omit slot: a content-tied block is emitted ONLY from a traced+addressed Claim; absence is disclosed in missing[], never fabricated"
    - "Reuse-not-fork identity: ref comes solely from site.Ledger.ref_for; the surface slug is BOTH the Surface id and the ledger key (so Phase 3's Site.from_surfaces reads the same ref)"
    - "Read/assign-only ledger in the composer; the caller owns save() (mirrors Site.from_surfaces / build_work_site)"

key-files:
  created: []
  modified:
    - src/newsletters/compose.py

key-decisions:
  - "Owner quote flows via explicit keyword params (quote: Claim | None, owner: str | None) — a parallel structure, NOT a SectionBinding extension (swimlane.py frozen after Plan 02-01)"
  - "Surface id == ledger key == 'report-{slugify(stem)}' (slug-clean) so Phase 3's Site.from_surfaces reads the ref assigned at compose time"
  - "compose_module_report never calls ledger.save(); persistence deferred to Phase 3's caller (keeps compose disk-write-free, tests isolated)"
  - "Ref literals (R-001, len()+1) kept OUT of code AND docstrings so the ref-format audit is grep-unambiguous"

patterns-established:
  - "Sourced-or-omit block emission (quote): traced Claim -> block; else omit + missing[] note"
  - "Fan-out stub: declared audience kinds with href=None (declared intent, never a dead link)"
  - "Ledger reuse: ref_for as the SOLE ref source, keyed by the surface slug, save() deferred to caller"

requirements-completed: [COMP-04]

# Metrics
duration: 12min
completed: 2026-07-02
---

# Phase 2 Plan 03: Module Report Composer — Identity & Structure Summary

**COMP-04 lands on compose.py: a sourced-or-omit owner QuoteBlock, an always-present FanoutBlock stub (href=None), and a stable append-only R-NNN via the reused site.Ledger — all Draft-only, authoring no facts.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-07-02T05:05:12Z (base 02-02 commit)
- **Completed:** 2026-07-02T05:16:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Sourced-or-omit owner/manager quote: a `QuoteBlock(text=<traced claim text>, attr=<owner id>)` is emitted ONLY when a content-addressed quote claim is supplied; absent/untraced -> the block is omitted and a `missing[]` note discloses the gap. An unowned lane falls back to an `"unassigned"` honesty marker — never a fabricated quote (T-02-10).
- Always-present `FanoutBlock` stub with the declared kinds `article`/`newsletter`/`learning`, each `FanoutLink.href=None` (a declared intent, never a dead/fabricated link — T-02-12).
- Stable, append-only `R-NNN`: the surface slug (via the REUSED `site.slugify`) is BOTH the `Surface.id` and the ledger key; the ref comes solely from `site.Ledger.ref_for` (immutable on re-sight; first report -> R-001). No inline ref format, no count+1 ordinal (T-02-09).
- `compose_module_report` stays disk-write-free: it reads/assigns the in-memory ledger but never calls `ledger.save()` — persistence is the caller's job in Phase 3 (mirrors `Site.from_surfaces` / `build_work_site`).

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Sourced-or-omit QuoteBlock + FanoutBlock stub** - `e9eaf17` (feat)
2. **Task 2: Stable R-NNN via reused site.Ledger** - `c4ad5cb` (feat)

**Plan metadata:** this SUMMARY commit (docs)

_TDD: both tasks used the plan's `python -c` smoke checks as the RED (fails against prior code) -> GREEN (passes after implementation) gate. No new test file was added (files_modified is strictly compose.py; existing suite of 592 stays green)._

## Files Created/Modified
- `src/newsletters/compose.py` - Added `QuoteBlock`/`FanoutBlock`/`FanoutLink` imports + `Ledger`/`slugify` from `.site`; new `quote`/`owner`/`ledger`/`ledger_path` params on `compose_module_report`; `_quote_block` and `_fanout_stub` helpers; `_slug` now reuses `site.slugify`; ref registration via `ledger.ref_for` keyed by the surface slug; updated module + function docstrings.

## Decisions Made
- **Quote flows via explicit keyword params, not a SectionBinding extension.** `swimlane.py` is frozen after Plan 02-01, so the owner quote is a parallel structure (`quote: Claim | None`, `owner: str | None`) passed by the caller — the block is emitted only when the claim is content-addressed. This keeps the composer loader-agnostic and the swimlane spine untouched (02-CONTEXT.md discretion).
- **Surface id == ledger key.** The slug `report-{slugify(stem)}` is slug-clean, so Phase 3's `Site.from_surfaces` (`slug = surface.id if surface.id == slugify(surface.id) else ...`) will read the SAME ledger key/ref assigned here — no renumber on re-sight.
- **Ref never in prose.** The ref lives only in the ledger; a bare ref in a ProseBlock would trip the numeral-free-prose guard (02-04). Literal ref strings and `len()+1` were kept out of docstrings too, so a grep-based ref-format audit is unambiguous.

## Deviations from Plan

None - plan executed exactly as written. (Black reformatted `compose.py` for line-wrapping only; behavior unchanged, both smoke checks and 592 tests green after the format.)

## Issues Encountered
- The initial `from .site import Ledger, slugify` was placed before `.semantic`, which `isort --profile black` orders after `.semantic`. Corrected the import order before the first gate run — no functional impact.

## TDD Gate Compliance
Both tasks are `tdd="true"`. The plan supplies its behavioral spec as inline `python -c` smoke checks rather than pytest files, and scopes `files_modified` to `compose.py` alone. Each task's smoke check was confirmed FAILING against the prior code (RED: Task 1 fanout assertion failed; Task 2 raised `TypeError` for the unknown `ledger` kwarg) and PASSING after implementation (GREEN). No separate `test(...)` commit exists because no test file was created (would exceed the plan's file scope); the RED/GREEN evidence is captured here and the full suite (592) remains green.

## Next Phase Readiness
- The composer is complete (COMP-01..04). Phase 3 can now build `build_module_site`: `Ledger.load("content/module/ids.json") -> compose_module_report(...) -> ledger.save()`, mirroring `build_work_site`.
- `content/module/ids.json` is intentionally NOT created by this plan (compose is disk-write-free); Phase 3's caller creates/persists it on first `save()`.
- No blockers. `site.py` reused unmodified; the AI-optional-core import boundary (`lint-imports`) stays green.

## Self-Check: PASSED
- FOUND: src/newsletters/compose.py
- FOUND commit e9eaf17 (Task 1)
- FOUND commit c4ad5cb (Task 2)
- site.py UNMODIFIED (git diff --exit-code clean)
- content/module/ids.json NOT created (compose disk-write-free)

---
*Phase: 02-module-scope-report-composer*
*Completed: 2026-07-02*
