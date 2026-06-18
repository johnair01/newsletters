# Roadmap: Newsletters (Rev2)

## Overview

Rev2 operationalises the validated Rev1 spine (`Source/Claim/Trace/Distillation/Surface`, deterministic
capture, review gate, HTML renderer — already merged on this branch) into a formally-defined,
backend-agnostic trust pipeline. The journey: first lock the **distill socket contract** (the one
boundary that gates every backend — coverage manifest, content-addressed traces, entailment gate,
conformance suite) and stand up the **AI-optional packaging invariant** so the deterministic spine
ships with zero AI deps from day one. With the contract fixed, two tracks open in parallel — the
**Rev2 site/renderer** (depends only on type shapes) and the **format adapters** (Email → Excel →
PPTX → Power BI, ascending complexity). Provenance surfacing and the merge-blocking CI gate close the
human-review loop, and finally the **work-surface installation** proves the whole thing on a real
codebase, and a first-class **learning/onboarding surface** re-cuts reviewed records for newcomers
and training cohorts. AI backend (v2: AI-01/02) is explicitly out of v1 scope — the deterministic backends are
proven first; AI conforms to them later, never the reverse.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Distill Socket Contract** - One `DistillPort` with coverage manifest, conformance suite, and manual backend (completed 2026-06-17)
- [x] **Phase 2: AI-Optional Packaging Boundary** - Bare `pip install .` runs the full spine with zero AI deps, CI-enforced every phase (completed 2026-06-17)
- [x] **Phase 3: Content-Addressed Provenance & Faithfulness Gate** - Traces pin content hashes; every claim entailed by its evidence span (completed 2026-06-17)
- [ ] **Phase 4: Shared Adapter Normalizer & Email Adapter** - One faithful-extraction rule; first stdlib adapter end-to-end
- [x] **Phase 5: Excel Adapter** - openpyxl cell/sheet extraction with formula-cache gaps routed to `unextracted[]` (completed 2026-06-17)
- [x] **Phase 6: PowerPoint Adapter** - python-pptx slide/shape extraction reporting unreadable shapes (completed 2026-06-17)
- [x] **Phase 7: Power BI Adapter** - PBIP/TMDL text extraction reporting row-cap and aggregation limits (completed 2026-06-18)
- [ ] **Phase 8: Site Content Model & Stable IDs** - `Site/Collection/Page` with position-independent per-surface IDs
- [ ] **Phase 9: Rev2 Site IA, Navigation & Source Links** - Real Home, Library status-board, four-destination nav, working source links
- [ ] **Phase 10: Reviewer Surfacing & Merge-Block Gate** - `missing[]`/`unextracted[]` shown on every surface; CI blocks unsafe merges
- [ ] **Phase 11: Work-Surface Installation** - Install on a real codebase, author Reports by hand, Library shows how the work was done
- [ ] **Phase 12: Learning & Onboarding Surface** - A first-class surface that re-cuts reviewed records for newcomers and training cohorts — digestible, traceable, sequenced
- [ ] **Phase 13: Problem Lifecycle Entity (A2)** - A first-class `Problem` above `Source` with its own state ladder — legibility layer, not a tracker; solving stays external
- [ ] **Phase 14: Problem Board Portfolio Surface (A2)** - A queryable portfolio view — group/count/age problems by node, surface recurrence, every problem traced to its sources

## Phase Details

### Phase 1: Distill Socket Contract

**Goal**: Establish the one backend boundary every distill backend speaks through — including the coverage manifest, the conformance suite, and a working manual backend that proves the socket end-to-end with zero AI.
**Mode:** mvp
**Depends on**: Nothing (Rev1 spine is present/merged on this branch)
**Requirements**: SOCK-01, SOCK-02, SOCK-03, SOCK-04, SOCK-05
**Success Criteria** (what must be TRUE):

  1. An operator can register a distill backend by name and run `distill(sources) -> Distillation` without the pipeline knowing which backend produced the result
  2. An operator can author claims+traces by hand via the manual backend and emit a valid `Distillation` with zero AI dependencies
  3. Any backend reports a coverage manifest with an explicit `unextracted[]` list, so no content is silently dropped
  4. A conformance suite runs against any registered backend and fails it if traces are missing, coverage is unreported, or the faithfulness contract is violated

**Plans**: 2 plans (2 waves)Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Walking skeleton: DistillPort + registry + ManualBackend + Coverage/Locator contract, end-to-end through the socket with zero AI (SOCK-01..04, D-04, D-06) — DONE (27 tests green, mypy clean, acyclic imports)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Conformance suite (SOCK-05) + the no-auto-publish / AI-optional hard rules proven by test; injectable faithfulness seam

### Phase 2: AI-Optional Packaging Boundary

**Goal**: Make the deterministic spine ship with zero AI dependencies, and turn that property into a standing CI invariant that every subsequent phase must keep green.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: PKG-01, PKG-02, PKG-03, PKG-04
**Success Criteria** (what must be TRUE):

  1. `pip install .` with no extras installs a fully working pipeline that runs capture → review → render end-to-end with zero AI dependencies
  2. All AI/LLM dependencies live behind an `[ai]` extra and are lazy-imported only inside the AI backend module
  3. A CI gate runs the full pipeline on a bare (no-extras) install and fails if any AI import is reachable from core
  4. An import-linter contract forbids `core` from importing any AI package, and CI enforces it

**Plans**: 2 plans (2 waves)

**Wave 1**

- [x] 02-01-PLAN.md — Dependency reorg (core = non-AI only; `[ai]` = pydantic-ai; drop langsmith/langchain/langgraph) + import-linter forbidden contract + plugin-aware runtime AI-isolation test (PKG-01, PKG-02, PKG-04)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02-PLAN.md — CI workflow: the bare no-extras install full-pipeline gate (PKG-03, the canonical source-of-truth) + the import-linter contract job (PKG-04) — the standing AI-optional invariant on every push

### Phase 3: Content-Addressed Provenance & Faithfulness Gate

**Goal**: Make traces resistant to source drift and make unfaithful claims structurally unable to pass as audited — content-address every trace and enforce entailment at the socket boundary for all backends.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: PROV-01, PROV-02
**Success Criteria** (what must be TRUE):

  1. Every claim's `Trace` is content-addressed (hash + offset + verbatim span), not positional, so editing a source flips dependent claims to STALE instead of silently mis-attributing
  2. A faithfulness gate verifies each emitted claim is entailed by its traced evidence span, using deterministic span-containment in no-AI mode
  3. A claim whose text cannot be located in or entailed by its own trace is routed to `missing[]`, never surfaced as a fact

**Plans**: 3 plans (2 waves)

**Wave 1**

- [x] 03-01-PLAN.md — Content-addressed Trace (SHA-256 of full Source + char offsets + verbatim span), self-verifying `Trace.from_source`, and STALE as a computed property at trace/claim/distillation granularity (PROV-01, D-1/D-2/D-4)

**Wave 2** *(blocked on Wave 1; 03-02 and 03-03 run in parallel — disjoint files)*

- [x] 03-02-PLAN.md — Migrate the Rev1 dogfood sample sources to content-addressed traces in place (faithful, reports anything unlocatable); corpus addressed + not stale after build (PROV-01, D-4)
- [x] 03-03-PLAN.md — `SpanContainmentFaithfulness` (normalized, deterministic, stdlib-only) defaulted at the Phase-1 `_enforce`/`assert_conforms` seam so every backend inherits it, plus `route_unfaithful_to_missing` (PROV-02, D-3/D-4)

### Phase 4: Shared Adapter Normalizer & Email Adapter

**Goal**: Put the faithful-extraction rule in exactly one place (the shared normalizer) and prove it with the first, simplest adapter — Email, stdlib-only, no extra.
**Mode:** mvp
**Depends on**: Phase 1, Phase 3
**Requirements**: ADAPT-01, ADAPT-02, ADAPT-06
**Success Criteria** (what must be TRUE):

  1. A shared `normalize()` step converts any adapter's raw extraction into typed `Claim(+Trace)` with source locators, and the faithful-extraction rule lives in exactly one place
  2. The Email adapter extracts structured content from `.eml` into `Claim(+Trace)` and reports unextracted parts (forwarded `message/rfc822`, charset-fallback losses) in `unextracted[]`
  3. A golden-file test (fixture `.eml` → expected typed claims+traces) covers the Email adapter and asserts zero silent drops

**Plans**: 3 plans (3 waves)

**Wave 1**

- [x] 04-01-PLAN.md — Shared `normalize()` (ADAPT-01): the single faithful-extraction site — cursor-advancing offset location + `Trace.from_source` minting; non-locatable units routed to `unextracted[]`; new `src/newsletters/adapters/` package, stdlib-only

**Wave 2** *(blocked on Wave 1 — imports `normalize()`)*

- [x] 04-02-PLAN.md — Email `.eml` adapter (ADAPT-02): registered `DistillPort` backend — `policy.default` parse, canonical decoded transcript, deterministic charset ladder + U+FFFD detection, HTML-only emit-both, full U1–U8 `unextracted[]` routing; selectable as `"email"` and conforming

**Wave 3** *(blocked on Wave 2 — drives the built adapter)*

- [x] 04-03-PLAN.md — Golden-file corpus (ADAPT-06): 8 committed `.eml` fixtures + zero-silent-drops accounting identity + verbatim/content-addressed assertions + `assert_conforms` (span-containment + JSON round-trip) + determinism — identity holds for all 8; no adapter bug found

### Phase 5: Excel Adapter

**Goal**: Extract cell and sheet structure from workbooks via openpyxl, routing every value openpyxl cannot resolve to `unextracted[]` rather than emitting it as data.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: ADAPT-03
**Success Criteria** (what must be TRUE):

  1. The Excel adapter extracts cell/sheet structure into `Claim(+Trace)` with `sheet!cell` locators
  2. Uncomputed / `None` formula cells (openpyxl-saved-without-cache) are routed to `unextracted[]`, never emitted as `0` or empty data
  3. A golden-file test covers the Excel adapter against a fixture containing formulas and merged cells, asserting zero silent drops

**Plans**: 4 plans (3 waves)

**Wave 1**

- [x] 05-01-PLAN.md — Task Zero: typed `Source.extraction` carrier (R1) + shared coverage codec; retrofit Email adapter (kill the in-memory dict); R2 safety-net; round-trip coverage-parity conformance test (ADAPT-03 carried hardening)
- [x] 05-02-PLAN.md — openpyxl `[excel]` extra + lazy `_load_openpyxl()`; extend the bare-install AI-isolation gate; R4 Wave-0 probe pinning the chart/image attribute names (ADAPT-03)

**Wave 2** *(blocked on Wave 1 — needs the carrier + the lazy loader/probe)*

- [x] 05-03-PLAN.md — `ExcelAdapter` (registered `"excel"`): double-load, canonical `sheet!cell` transcript, faithful per-cell fork (formula-no-cache/error/charts → `unextracted[]`), merged-anchor handling, drops on `Source.extraction`, conforms (ADAPT-03)

**Wave 3** *(blocked on Wave 2 — drives the built adapter)*

- [x] 05-04-PLAN.md — Byte-reproducible `.xlsx` golden corpus (ADAPT-06): formula±cache, merged, multi-sheet, mixed types, empty, error cell, chart/image; zero-silent-drops + verbatim + content-addressed + conformance + determinism + round-trip coverage parity

### Phase 6: PowerPoint Adapter

**Goal**: Extract slide and shape text from decks via python-pptx, explicitly reporting the shapes the high-level API cannot read.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: ADAPT-04
**Success Criteria** (what must be TRUE):

  1. The PowerPoint adapter extracts slide/shape text into `Claim(+Trace)` with slide/shape locators
  2. Shapes the adapter cannot read (e.g. SmartArt, grouped shapes) are reported in `unextracted[]`, so the reviewer sees the slide had content the extractor skipped
  3. A golden-file test covers the PowerPoint adapter against a fixture containing SmartArt and grouped shapes, asserting zero silent drops

**Plans**: 4 plans (3 waves)

**Wave 1** *(parallel — disjoint file ownership)*

- [x] 06-01-PLAN.md — FRONT FIX (CONTEXT decision 0 / L1): shared `adapters/_timestamps.py` (`EPOCH_ZERO` + `deterministic_timestamp`); retrofit email + excel off the `now()` fallback; cross-adapter determinism test (ADAPT-04 pattern prerequisite)
- [x] 06-02-PLAN.md — PACKAGING (CONTEXT decision 1): `pptx = ["python-pptx"]` extra + lazy `_pptx_loader.py` (no top-level pptx import); install python-pptx in `.venv`; extend the bare-install AI-isolation gate; A1 graphic-frame `@uri` accessor + lxml-fallback probe (ADAPT-04)

**Wave 2** *(blocked on Wave 1 — needs `_timestamps.py` + `_pptx_loader.py`)*

- [x] 06-03-PLAN.md — `PptxAdapter` (registered `"pptx"`): ordered slide/shape walk, group recursion (L3), per-paragraph/cell/notes verbatim claims, full unreadable taxonomy (SmartArt/chart/picture/media/OLE → `unextracted[]`, L2), drops on `Source.extraction`, deterministic timestamp, conforms; lazy python-pptx only (ADAPT-04 criteria 1+2)

**Wave 3** *(blocked on Wave 2 — drives the built adapter)*

- [x] 06-04-PLAN.md — Byte-reproducible `.pptx` golden corpus (ADAPT-06 + criterion 3): SmartArt + nested grouped shapes, title+body, text box, table, notes, chart, image, empty slide; zero-silent-drops (incl. nested-group accounting) + verbatim + content-addressed + conformance + Source-determinism (L5) + round-trip coverage parity; join the parity matrix + the cross-adapter determinism test

### Phase 7: Power BI Adapter

**Goal**: Extract from Power BI PBIP/TMDL text (stdlib, ZERO new dependency), reporting the row-cap and aggregation limits that make an export look complete when it is a clipped aggregate; route binary `.pbix` to a fail-loud "export to PBIP" disclosure (pbixray DEFERRED per research-locked L1).
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: ADAPT-05
**Success Criteria** (what must be TRUE):

  1. The Power BI adapter extracts from PBIP/TMDL text (stdlib) into `Claim(+Trace)`; binary `.pbix` routes to a whole-source `unextracted[]` deferral ("export to PBIP for faithful extraction") — pbixray DEFERRED (research-locked L1), ZERO new dependency
  2. Row-cap hits and summarized-vs-underlying aggregation limits are reported in `unextracted[]`, failing loud rather than presenting a clipped aggregate as complete
  3. A golden-file test covers the Power BI adapter against a fixture, asserting zero silent drops

**Plans**: 4 plans (3 waves)

**Wave 1** *(parallel — disjoint file ownership; pure stdlib parsers, unit-testable)*

- [x] 07-01-PLAN.md — Stdlib TMDL line/indent parser (`_tmdl.py`, L2): ordered verbatim `(object-path, value)` units for tables/columns/measures/relationships/hierarchies/annotations; DAX extracted as TEXT, never evaluated; directQuery surfaced as a signal (ADAPT-05, D-3/L2)
- [x] 07-02-PLAN.md — Stdlib PBIR report reader (`_pbir.py`, L3): verbatim page/visual/textbox/field units + the typed row-cap/aggregation detection taxonomy (TopN, restricting filters, summarized/aggregated bindings, DirectQuery/rowlimit), filter literals disclosed as config text (ADAPT-05, D-4/L3)

**Wave 2** *(blocked on Wave 1 — composes both parsers)*

- [x] 07-03-PLAN.md — `PowerBiAdapter` (registered `powerbi`): folder `parse_path` + byte `parse`, canonical prefixed transcript (L5), `.pbix` deferral (L1/`_R_PBIX_BINARY`), the full `_R_*` taxonomy + categorical `_R_NO_DATA_ROWS` → `unextracted[]` (fail loud), drops on `Source.extraction`, EPOCH_ZERO timestamp, conforms; joins the parity + determinism matrices (ADAPT-05 criteria 1+2)

**Wave 3** *(blocked on Wave 2 — drives the built adapter)*

- [x] 07-04-PLAN.md — Hand-authored byte-reproducible PBIP/TMDL golden corpus (ADAPT-06 criterion 3): TMDL model + relationship + plain + Top-N/summarized visuals + `.pbix` deferral; zero-silent-drops + verbatim/content-addressed claims + pinned `_R_TOPN`/`_R_AGGREGATED`/`_R_NO_DATA_ROWS`/`_R_PBIX_BINARY` + conformance + Source-determinism (L5) + round-trip coverage parity (ADAPT-05, ADAPT-06)

### Phase 8: Site Content Model & Stable IDs

**Goal**: Replace position-derived numbering with a `Site/Collection/Page` content model that carries stable per-surface IDs, so links and boards stop rotting when content reorders.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: SITE-01
**Success Criteria** (what must be TRUE):

  1. The `Site/Collection/Page` content model carries stable per-surface IDs (`EP01`, `R-001`, slug, issue/date) generated from content, independent of list position
  2. Inserting or reordering surfaces does not change any existing surface's ID or break its cross-links

**Plans**: 2 plans

Plans:

- [x] 08-01-PLAN.md — Identity core (TDD): `site.py` slugify + append-only `Ledger` + `Site/Collection/Page` + `from_surfaces`/`by_slug`, the reorder/insert stability test (L7), seeded `content/rev1/ids.json`, package exports
- [ ] 08-02-PLAN.md — Page-driven renderer: rewrite `render_library` to use `Page.ref` (drop the positional index) + `build_site` builds the Site, plus the spec update (L2) and the no-rot regression test

**UI hint**: yes

### Phase 9: Rev2 Site IA, Navigation & Source Links

**Goal**: Fix the deployed site's information architecture — a real marketing Home separate from a Library status-board, four real nav destinations with breadcrumbs, and every cited source rendered as a working link — all regenerated from templates.
**Mode:** mvp
**Depends on**: Phase 8
**Requirements**: SITE-02, SITE-03, SITE-04, SITE-05, SITE-06
**Success Criteria** (what must be TRUE):

  1. The front door is the real marketing Home (8-section spec) and the archive is a separate Library page
  2. The Library renders as a status board with columns by gate state (Draft / In Review / Published) using CSS columns, no JS
  3. Global navigation resolves to four real destinations with breadcrumbs and prev/next within a surface type
  4. The fan-out diagram and every cited source render as working links (e.g. `vision.md` → repo file)
  5. All site output regenerates from the renderer/templates with no hand-edited HTML

**Plans**: TBD
**UI hint**: yes

### Phase 10: Reviewer Surfacing & Merge-Block Gate

**Goal**: Make the human review gate real rather than a rubber stamp — surface every `missing[]` and `unextracted[]` item on every surface, and block merge in CI while any claim is STALE, un-entailed, or has open gaps.
**Mode:** mvp
**Depends on**: Phase 3, Phase 9
**Requirements**: PROV-03, PROV-04
**Success Criteria** (what must be TRUE):

  1. `missing[]` and `unextracted[]` are surfaced to the reviewer on every surface, never hidden
  2. CI blocks merge of any surface containing a STALE, un-entailed, or open-`missing[]` claim
  3. The review view shows each claim next to its verbatim trace by default, so the unfaithful thing is visible without a click

**Plans**: TBD
**UI hint**: yes

### Phase 11: Work-Surface Installation

**Goal**: Prove the whole pipeline on a real work codebase — install Newsletters, point read-only adapters at the code with data staying local, author a Report by hand, and publish a Library that shows how the work was done.
**Mode:** mvp
**Depends on**: Phase 4, Phase 10
**Requirements**: WORK-01, WORK-02, WORK-03
**Success Criteria** (what must be TRUE):

  1. An operator can `pip install` Newsletters and point read-only adapters at a work codebase with all data staying local (no external calls on content)
  2. An operator can author a Report by hand via the manual backend and have it inherit the traced structure
  3. The published Library shows how the work was done, with process visible via Provenance/Lineage on each surface

**Plans**: TBD
**UI hint**: yes

### Phase 12: Learning & Onboarding Surface

**Goal**: Add a first-class learning/onboarding surface that re-cuts reviewed records for newcomers and training-program participants — progressive disclosure, traceable concepts, and ordered onboarding paths — making org/codebase knowledge digestible to people new to it.
**Mode:** mvp
**Depends on**: Phase 8, Phase 9
**Requirements**: LEARN-01, LEARN-02, LEARN-03
**Success Criteria** (what must be TRUE):

  1. A Learning/Onboarding surface preset re-cuts a reviewed record for a newcomer audience with progressive disclosure, prerequisite context, and an in-context glossary
  2. Every concept on the surface links back to its source record/claim, so a learner can trace explanation → evidence
  3. An onboarding path sequences multiple records into an ordered learning track for a new team member / training cohort

**Plans**: TBD
**UI hint**: yes

### Phase 13: Problem Lifecycle Entity (A2)

**Goal**: Add a first-class `Problem` entity *above* `Source` that consolidates the scattered problem→owned→solution→promoted lifecycle (today spread across Jira/Azure DevOps, passdowns, and people's heads) into one legible, queryable home — **as a legibility layer, not a second tracker**. The problem-SOLVING step stays external/operator-owned; Signals models the *record* of the lifecycle, not its execution.
**Mode:** mvp
**Depends on**: Phase 1 (socket/type shapes), Phase 3 (content-addressed traces), Phase 11 (real Source capture)
**Requirements**: PROB-01, PROB-03
**Success Criteria** (what must be TRUE):

  1. A `Problem` entity aggregates ≥1 traced `Source` and carries its own lifecycle state ladder (`Identified → Owned → In Progress → Resolved → Verified`), typed end to end
  2. The problem lifecycle ladder is provably distinct in code from the surface review gate (`Draft → In Review → Published`) and the surface fan-out chain — no shared/overloaded "promotion" term (enforced per the terminology-guard seed)
  3. Lifecycle-state transitions are human-gated and never auto-mutated; there is no write-back path to any external system (Jira/ADO) — the `semantic.py` spine boundary (solving is external) is preserved and proven by a test

**Plans**: TBD
**UI hint**: no

### Phase 14: Problem Board Portfolio Surface (A2)

**Goal**: Render the consolidated problem portfolio as a queryable surface alongside the existing gate-state board — the cross-record view A1 structurally cannot produce — so a real consumer can watch bottlenecks, ages, and recurring problem-types across the portfolio.
**Mode:** mvp
**Depends on**: Phase 9 (site IA / board rendering), Phase 13 (Problem entity)
**Requirements**: PROB-02, PROB-04
**Success Criteria** (what must be TRUE):

  1. The problem board renders the portfolio grouped/countable/age-able by node/area and surfaces recurrence across records (the aggregate query A1 cannot answer)
  2. Every problem on the board links back to its constituent `Source` records/claims, so the lifecycle stays traceable to evidence
  3. The board regenerates from the renderer/templates (no hand-edited HTML) and sits alongside — not replacing — the gate-state board

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14

Phases 13–14 (A2 Problem Lifecycle Layer) are a Rev2 extension routed 2026-06-17 — they build on
the spine (Phases 1/3/11) and the site board (Phase 9), and do not alter Phases 1–12.

Phases 8–9 (site track) depend only on Phase 1 type shapes and may proceed in parallel with the
adapter track (Phases 4–7) once the socket contract is fixed. Phases 2 (PKG-03/04) and the PROV-04
merge-block gate (Phase 10) establish standing CI invariants verified on every subsequent phase.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Distill Socket Contract | 2/2 | Complete   | 2026-06-17 |
| 2. AI-Optional Packaging Boundary | 2/2 | Complete   | 2026-06-17 |
| 3. Content-Addressed Provenance & Faithfulness Gate | 3/3 | Complete   | 2026-06-17 |
| 4. Shared Adapter Normalizer & Email Adapter | 2/3 | In Progress|  |
| 5. Excel Adapter | 4/4 | Complete   | 2026-06-17 |
| 6. PowerPoint Adapter | 4/4 | Complete   | 2026-06-17 |
| 7. Power BI Adapter | 4/4 | Complete   | 2026-06-18 |
| 8. Site Content Model & Stable IDs | 1/2 | In Progress|  |
| 9. Rev2 Site IA, Navigation & Source Links | 0/TBD | Not started | - |
| 10. Reviewer Surfacing & Merge-Block Gate | 0/TBD | Not started | - |
| 11. Work-Surface Installation | 0/TBD | Not started | - |
| 12. Learning & Onboarding Surface | 0/TBD | Not started | - |
| 13. Problem Lifecycle Entity (A2) | 0/TBD | Not started | - |
| 14. Problem Board Portfolio Surface (A2) | 0/TBD | Not started | - |
