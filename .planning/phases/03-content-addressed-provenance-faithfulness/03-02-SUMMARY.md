---
phase: 03-content-addressed-provenance-faithfulness
plan: 02
subsystem: dogfood-corpus
tags: [provenance, content-addressing, migration, faithful, dogfood, stale-detection]

# Dependency graph
requires:
  - phase: 03-content-addressed-provenance-faithfulness
    plan: 01
    provides: Trace.from_source / Source.content_hash / Trace.is_addressed / is_stale_against / Distillation.stale_claims
provides:
  - "dogfood._address_trace(source, trace) — faithful single-trace content-address by verbatim str.find + Trace.from_source"
  - "dogfood.address_corpus_traces(sources, traces) -> MigrationReport — in-place corpus migration that REPORTS unlocatable spans"
  - "dogfood.MigrationReport — addressed / skipped_no_span / unlocated outcome record"
  - "the shipped Rev1 sample corpus is itself content-addressed (20 traces) and not stale at capture time"
affects: [03-03, faithfulness-gate, adapters]

# Tech tracking
tech-stack:
  added: []  # stdlib str.find only; reuses 03-01 hashing; AI-optional contract intact
  patterns:
    - "Faithful migration: locate the existing verbatim span via str.find, re-mint via the one Trace.from_source constructor; never re-implement hashing/offsets"
    - "Report-don't-fabricate: unlocatable spans (empty / not-substring) raise a teaching ValueError (helper) or land in MigrationReport.unlocated (corpus), never a bogus 0:0 offset"
    - "The session Source transcript IS the verbatim record of its decisions (_record_transcript), so addressing pins real evidence, not invented evidence"
    - "Structural-locator traces (no verbatim span) stay un-addressed — the faithful outcome, never stale"

key-files:
  created:
    - tests/test_provenance_migration.py
  modified:
    - src/newsletters/dogfood.py

key-decisions:
  - "Migration is IN PLACE and FAITHFUL: claim text + rendered HTML are byte-identical before/after; only content_hash+start+end are added"
  - "Build the session transcript FROM its decision texts (_record_transcript) so each decision-derived trace has a real verbatim span to content-address — honest, not fabricated"
  - "report-plan's doc-roadmap traces use structural locators with no verbatim span; they are left UN-addressed (never stale) rather than given invented offsets"
  - "address_corpus_traces COLLECTS unlocatable spans into MigrationReport.unlocated; _address_trace RAISES — corpus migration never aborts on one un-pinnable span, but never drops it silently either"

patterns-established:
  - "Single mint point reuse: the corpus migration consumes Trace.from_source (03-01); pinning logic lives in exactly one place"
  - "Faithful-not-suggestive proven by test at both granularities: helper (span/locator byte-identical) and corpus (span == claim.text == live transcript window)"

requirements-completed: [PROV-01]

# Metrics
duration: ~8min
completed: 2026-06-17
---

# Phase 3 Plan 02: Migrate the Rev1 Dogfood Corpus to Content-Addressed Traces Summary

**A faithful in-place migration that content-addresses the shipped Rev1 sample corpus — 20 sample traces pinned to their verbatim decision spans via `Trace.from_source` (03-01), self-verifying and not stale at capture time, with unlocatable spans reported rather than fabricated; claim text and rendered HTML byte-identical, AI-optional contract intact.**

## Performance
- **Duration:** ~8 min
- **Tasks:** 2 (TDD: RED once, GREEN per task)
- **Files:** 1 created, 1 modified
- **Sample traces migrated:** 20 (kickoff 4 + datamodel 6 + rev1 4 + the promoted article's 6, which share the datamodel source)

## Accomplishments
- `_address_trace(source, trace)` — the faithful single-trace helper: locates the existing `trace.span` verbatim in `source.transcript` via `str.find` and re-mints through `Trace.from_source(source, start, end, locator=trace.locator)`. It reuses 03-01's one pinning constructor; it does not re-implement hashing or offset logic. An empty span, or a span that is not a substring, raises a teaching `ValueError` naming the span + source — never a bogus offset.
- `address_corpus_traces(sources, traces) -> MigrationReport` — the corpus-level in-place migration: pins every locatable trace and copies the additive `content_hash`/`start`/`end` onto the live trace object; collects every unlocatable span into `MigrationReport.unlocated` (reported, not raised, not dropped); counts `addressed` and `skipped_no_span`.
- Wired into `build_surfaces`: each session `Source.transcript` is now the verbatim record of its decisions (`_record_transcript`), and `_address_report` pins each report's claim traces. The shipped Rev1 corpus is itself content-addressed (20 traces) and `stale_claims`-clean at capture time.
- `MigrationReport` dataclass records the migration outcome (`addressed` / `skipped_no_span` / `unlocated`).

## How the corpus migrated (per surface)

| Surface | Claim traces | Outcome |
|---|---|---|
| report-kickoff | 4 (session-kickoff) | addressed, not stale |
| report-datamodel | 6 (session-datamodel) | addressed, not stale |
| report-rev1 | 4 (session-rev1) | addressed, not stale |
| article-semantic-spine | 6 (session-datamodel, promoted) | addressed, not stale |
| report-plan | 4 (doc-roadmap) | **un-addressed** — structural locators ("Phase 0 / Phase 2", "Cross-cutting"), no verbatim span; faithful outcome, never stale |

**Spans that could not be located:** none were silently skipped. The `report-plan` traces carry *no span* (empty), so they are correctly never sent to `from_source` and stay un-addressed — the plan's prescribed faithful outcome for structural-locator evidence, not an error. Any span that was present-but-absent-from-transcript would land in `MigrationReport.unlocated` (proven by `test_address_corpus_traces_collects_unlocatable_without_raising`).

## Task Commits
1. **RED** — failing migration tests (`beb29fc`, test): helper/`MigrationReport`/corpus wrapper absent → ImportError.
2. **GREEN Task 1** — `_address_trace` + `address_corpus_traces` + `MigrationReport` (`261074d`, feat).
3. **GREEN Task 2** — `_record_transcript` + `_address_report` wired into `build_surfaces` (`db56ced`, feat).

_No separate REFACTOR commit — implementation was minimal at GREEN._

## Gate Results (re-run independently via .venv/bin/python)
- `pytest tests/test_provenance_migration.py -q`: **11 passed**.
- `pytest tests/test_semantic.py tests/test_ai_optional.py tests/test_provenance.py -q` (the dogfood/build/provenance regression set): **39 passed, 1 xfailed** — Rev1 dogfood render + AI-optional subprocess checks stay green.
- `newsletters build` (the documented CLI build entrypoint): **rendered 9 surfaces + the library index → content/rev1/site, exit 0**. `content/rev1/site/report-kickoff.html` is byte-identical to the committed version (faithfulness: no rendered claim-text change).
- `lint-imports`: **Contracts: 1 kept, 0 broken** (AI-optional contract intact — stdlib `str.find` + reuse of 03-01 hashing, zero AI import, zero new dependency).
- Full `pytest -q`: **85 passed, 1 xfailed** at end of run (after concurrent plan 03-03 landed its faithfulness gate). Mid-run it was briefly mixed while 03-03's `tests/test_faithfulness_gate.py` was in-flight — those are 03-03's files, not this plan's.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored two claim texts I had inadvertently altered while extracting decision lists**
- **Found during:** Task 2 (caught by inspecting the `content/rev1/site/report-kickoff.html` git diff before staging)
- **Issue:** While extracting `kickoff_decisions`, I had dropped "§4" from one decision and the single quotes around "'verify any install…'" from another — which changed the *rendered* claim text. That violates faithful-not-suggestive (migration must add metadata only).
- **Fix:** Restored both decision texts verbatim; rebuilt; confirmed `report-kickoff.html` is byte-identical to the committed version. Added `test_built_corpus_is_faithful_span_round_trips_to_live_source` asserting every addressed trace's `span == claim.text == transcript[start:end]` to guard the regression.
- **Files modified:** src/newsletters/dogfood.py, tests/test_provenance_migration.py
- **Commit:** db56ced

### mypy on dogfood.py — pre-existing errors NOT fixed (scope boundary)
`mypy src/newsletters/dogfood.py` reports 8 errors, ALL in functions untouched by this plan (`_newsletter_for` L454, `_show` L490, `_plan_report` L564–576): `Source(id=...)` missing-arg and bare-string `Trace(locator=...)` — valid at runtime (Pydantic defaults + `Trace._coerce_locator`), but flagged under the project's plugin-less `[tool.mypy]`. They predate this phase (03-01 only ran mypy on `semantic.py`/`distill`). The migration code added here (`_address_trace`, `address_corpus_traces`, `MigrationReport`, `_record_transcript`, `_address_report`) is **mypy-clean**. Logged to `deferred-items.md`; not fixed per the SCOPE BOUNDARY rule (out-of-scope, pre-existing, in unrelated functions).

## Known Stubs
None. All locatable sample traces are content-addressed; `report-plan`'s structural-locator traces are intentionally and faithfully un-addressed (documented above), not stubs.

## Threat Flags
None new. The plan's threats are mitigated:
- **T-03M-01** (bogus offsets): `_address_trace` only pins spans located via `str.find`; unlocatable → ValueError / `MigrationReport.unlocated`. Proven by `test_address_trace_reports_unlocatable_span_via_value_error` and `test_address_corpus_traces_collects_unlocatable_without_raising`.
- **T-03M-02** (editorializing): faithful proven by `test_address_trace_is_faithful_span_and_claim_text_unchanged` + `test_built_corpus_is_faithful_span_round_trips_to_live_source` + byte-identical rendered HTML.
- **T-03M-03** (breaking the corpus): surface set/order unchanged, `build_site` renders all 9 + index, full suite green.

## Issues Encountered
The dogfood traces minted via `capture.py` carry an *empty* span and structural-tag locators, so there was nothing verbatim to address out of the box. Resolved faithfully by making each session `Source.transcript` the verbatim record of its decisions (`_record_transcript`) — the transcript honestly IS that record — so the migration pins real evidence rather than inventing it.

## Self-Check: PASSED
- FOUND: src/newsletters/dogfood.py
- FOUND: tests/test_provenance_migration.py
- FOUND commit: beb29fc (RED)
- FOUND commit: 261074d (GREEN Task 1)
- FOUND commit: db56ced (GREEN Task 2)

---
*Phase: 03-content-addressed-provenance-faithfulness*
*Completed: 2026-06-17*
