---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 06-02-PLAN.md
last_updated: "2026-06-18T11:02:02.680Z"
last_activity: 2026-06-18 -- Phase 08 execution started
progress:
  total_phases: 14
  completed_phases: 6
  total_plans: 25
  completed_plans: 23
  percent: 43
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-14)

**Core value:** A deterministic, auditable pipeline that traces every published claim to evidence and never auto-publishes — AI is an optional accelerator, never an authority.
**Current focus:** Phase 08 — site-content-model-stable-ids

## Current Position

Phase: 08 (site-content-model-stable-ids) — EXECUTING
Plan: 2 of 2
Status: Ready to execute
Last activity: 2026-06-18 -- Phase 08 execution started

Progress: Phase 04 [██████████] 3/3 plans (04-01, 04-02, 04-03 complete)

## Performance Metrics

**Velocity:**

- Total plans completed: 2 (Phase 01)
- Average duration: ~18 min
- Total execution time: ~0.6 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01    | 2     | ~37m  | ~18m     |

**Recent Trend:**

- Last 5 plans: 01-01 (~25m), 01-02 (~12m)
- Trend: faster (skeleton → enforcement)

*Updated after each plan completion*

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| 01-01 | ~25 min | 3 tasks | 11 files |
| 01-02 | ~12 min | 2 tasks | 4 files |
| Phase 02 P01 | 4min | 3 tasks | 4 files |
| Phase 02 P02 | 2min | 1 tasks | 1 files |
| Phase 03 P01 | 12min | 3 tasks | 2 files |
| Phase 03 P02 | ~8min | 2 tasks | 2 files |
| Phase 03 P03 | ~15min | 3 tasks | 5 files |
| Phase 04 P01 | 12min | 2 tasks | 3 files |
| Phase 04 P02 | 6min | 3 tasks | 4 files |
| Phase 04 P03 | 4min | 2 tasks | 10 files |
| Phase 05 P01 | 25min | 2 tasks | 5 files |
| Phase 05 P02 | 20min | 2 tasks | 4 files |
| Phase 05 P03 | 6min | 2 tasks | 4 files |
| Phase 05 P04 | 8min | 2 tasks | 11 files |
| Phase 06 P02 | 4min | 2 tasks | 4 files |
| Phase 06 P01 | 20min | 2 tasks | 4 files |
| Phase 06 P03 | 35min | 2 tasks | 3 files |
| Phase 06 P04 | ~7min | 2 tasks | 13 files |
| Phase 07 P03 | 25m | 3 tasks | 5 files |
| Phase 07 P04 | 15m | 2 tasks | 4 files |
| Phase 08 P01 | 30min | 2 tasks | 5 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Distill socket contract (SOCK-01..05) is the critical path — it gates all adapters, the AI backend, the coverage manifest, and the faithfulness gate. Built first.
- [Roadmap]: AI-optional packaging (PKG) sequenced early (Phase 2); PKG-03/PKG-04 + PROV-04 are standing CI invariants verified every subsequent phase.
- [Roadmap]: Site track (Phases 8–9) depends only on Phase 1 type shapes — may run in parallel with the adapter track (Phases 4–7).
- [Roadmap]: Format adapters built in ascending complexity — Email → Excel → PPTX → Power BI.
- [Roadmap]: AI backend (v2: AI-01/02) is out of v1 scope; deterministic backends proven first, AI conforms later.
- [Intent review]: Learning/onboarding is a first-class V2 surface (Phase 12, LEARN-01..03) — teaching newcomers/training cohorts by re-cutting reviewed records.
- [Intent review]: A connection/relationship map (CONN-01) is parked — a real direction, revisit after core V2.
- [Intent review]: PROJECT.md reframed to lead with purpose (information→conversation→action; legible/transparent/digestible work), with auditability as the load-bearing constraint.
- [Phase 1]: [01-02] Faithfulness enforced in exactly one injectable place (ports._enforce); conformance.py delegates to it. The runtime conformance suite (not mypy) is the malformed-backend guard.
- [Phase ?]: Phase 02-01: dropped langsmith/langchain/langgraph entirely (zero usage); pydantic-ai relocated to [ai] extra; AI boundary policed by import-linter forbidden contract + runtime pydantic-plugin entry-point guard
- [Phase ?]: CI bare no-extras install (.[test], no [ai]) is the runtime source-of-truth for AI-optional core: with AI packages absent, neither a static import nor a pydantic-group AI plugin can fire — the plugin guard passes strictly on the bare interpreter (proven locally: 37 passed, 0 xfailed)
- [Phase ?]: PROV-01: Trace content-addressed via stdlib SHA-256 of full Source + char offsets + verbatim span; STALE is a computed property (no stored flag); content-address fields optional for Rev1 backward-compat
- [Phase ?]: 03-03: faithfulness = deterministic span-containment (Option A) defaulted at the _enforce/assert_conforms seam; un-addressed traces are structural fallback, content-addressed traces get strict normalized containment; capture.py untouched
- [Phase ?]: 03-02: the shipped Rev1 dogfood corpus is migrated IN PLACE to content-addressed traces (20 traces) — faithful (claim text + rendered HTML byte-identical), self-verifying, not stale at capture; unlocatable spans reported (MigrationReport.unlocated), never fabricated; report-plan's structural-locator traces left un-addressed
- [Phase 04]: normalize() empty unit ('') mints a zero-width Claim (str.find('')==cursor); cursor not advanced
- [Phase 04]: normalize() cursor is forward-only: overlapping/out-of-order units route to unextracted[] (non-overlapping provenance)
- [Phase 04]: Email adapter: distill(sources) stays DistillPort-exact; parse(raw,path) builds the Source and records U1-U7 drops, recovered in distill via a per-source-id dict (manual.py-style state carry)
- [Phase 04]: 04-03: 8 byte-exact .eml golden fixtures (committed, via _author_fixtures.py generator) drive EmailAdapter across the full routing matrix; the zero-silent-drops accounting identity (len(claims)+len(unextracted)==units walked) holds for all 8 — the executable proof of CONTEXT decision 4. No adapter bug found; expected counts pinned from the live adapter, not assumed.
- [Phase ?]: R1: TYPED Source.extraction carrier (not JSON-in-context); carrier types in leaf locators.py; excluded from content_hash()
- [Phase ?]: R2 safety-net: unaccountable Source forces complete=False via coverage-not-reconstructable marker
- [Phase ?]: openpyxl behind [excel] extra, lazy-imported via _load_openpyxl(); bare install runs spine without it
- [Phase ?]: openpyxl typed as Any (no types-openpyxl stub dep) — openpyxl is the only new dep permitted this phase
- [Phase ?]: Excel adapter uses the TYPED Source.extraction carrier (R1), not JSON-in-context; transcript SEP is a tab and values are emitted verbatim (never escaped); formula-no-cache and error cells route to unextracted[] (never 0/empty)
- [Phase ?]: Excel golden corpus: pin both docProps AND zip-entry timestamps for byte-reproducible .xlsx fixtures (openpyxl stamps zip local headers from the save-time wall-clock independently)
- [Phase ?]: ExcelAdapter Source.timestamp derives from wb.properties.created (document-intrinsic), not now() — fixed a real determinism/round-trip-parity bug (Rule 1)
- [Phase ?]: 06-02: confirmed shape._element.graphicData_uri is reliable on python-pptx 1.0.2 (risk A1); lxml a:graphicData/@uri fallback agrees — 06-03 uses accessor first, keeps fallback
- [Phase ?]: 06-01: Fixed EPOCH_ZERO sentinel (1970-01-01Z) for no-intrinsic adapter timestamps, never now()
- [Phase ?]: 06-01: Excel reads docProps created from raw OOXML (intrinsic_created), not openpyxl properties which fabricate a wall-clock created when absent
- [Phase ?]: 06-03: python-pptx core_properties.created is faithful (None when absent), unlike openpyxl — no raw-XML workaround needed; used it directly via deterministic_timestamp
- [Phase ?]: 06-03: PptxAdapter clones ExcelAdapter — recursive shape walk, Slide N / <shape.name> locators, notes last, empty frames skipped-empty, full SmartArt/chart/picture/media/OLE taxonomy with zero silent drops
- [Phase ?]: 06-04: determinism asserted on the parsed Source (L5), not re-saved .pptx bytes — immune to python-pptx re-save drift
- [Phase ?]: 06-04: _normalize_zip recurses into a chart's embedded openpyxl .xlsx to pin its core.xml -> the whole .pptx corpus is byte-reproducible cross-process
- [Phase ?]: 07-03: PowerBiAdapter registered 'powerbi' — stdlib PBIP/TMDL+PBIR onto shared normalize(); timestamp always EPOCH_ZERO; _R_NO_DATA_ROWS forces fail-loud; zero new dependency
- [Phase ?]: 07-04: Power BI golden corpus is hand-authored plain text via stdlib write_text (zero authoring dep)
- [Phase ?]: 07-04: the golden has no skip-mark — the powerbi adapter is stdlib-only so the corpus runs on a bare install
- [Phase 08]: 08-01: identity moved out of presentation into a deterministic core (site.py); stable IDs = pure function of content + an append-only ledger (content/rev1/ids.json); existing slug->ref IMMUTABLE, new = max(per-type ordinal)+1; slug defaults to Surface.id for Rev1 backward-compat; reorder/insert stability proven by test_reorder_and_insert_preserve_ids (L7)

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- [Phase 1]: RESOLVED in 01-01 — `DistillPort` is `@runtime_checkable Protocol`(name, distill(sources)->DistillationResult); coverage is `Coverage`(complete/unextracted[]/cost_hint/effort_hint); `Locator` is a `FreeLocator|SessionLocator` discriminated union in the top-level leaf `locators.py`; the entailment gate is the injectable `FaithfulnessCheck`/`StructuralFaithfulness` seam.
- [Phase 3 / Phase 10]: Entailment gate implementation choice (deterministic span-containment for no-AI mode) needs to be resolved in planning.
- [Phase 9]: Confirm the Home 8-section spec is captured in writing before templating begins.
- [Phase 5/6/7]: Each format adapter has documented non-obvious extraction gaps (formula cache, SmartArt/grouped shapes, Power BI row caps) — run a focused research cycle per format during planning.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| v2 scope | AI backend (AI-01) + claim-level evidence UX (AI-02) | Deferred | Roadmap (out of v1) |
| v3 scope | Per-reader personalization (PERS-01) — config hook only; learning engine is V3 PulseIQ | Out of scope | Roadmap |
| candidate | Connection/relationship map (CONN-01) — show how records/claims/surfaces connect | Parked | Intent review |

## Session Continuity

Last session: 2026-06-18T11:01:21.431Z
Stopped at: Completed 06-02-PLAN.md
Resume file: None
