# Requirements: Newsletters (Rev2)

**Defined:** 2026-06-14
**Core Value:** A deterministic, auditable pipeline that traces every published claim to evidence and never auto-publishes — AI is an optional accelerator, never an authority.

> Rev1 spine is **Validated** (merged from `claude/magical-einstein-hfd1np`): typed
> `Source/Claim/Trace/Distillation/Surface`, deterministic capture, review gate, HTML renderer.
> The v1 requirements below are the **Rev2** scope that builds on it.

## v1 Requirements

### Distill Socket

- [x] **SOCK-01**: A `DistillPort` protocol defines one backend contract — `distill(sources) -> Distillation` — that the pipeline consumes without knowing which backend produced the result
- [x] **SOCK-02**: A backend registry lets an operator register/select a distill backend (manual / adapter / AI) by name
- [x] **SOCK-03**: A `ManualBackend` lets an operator author claims+traces by hand with zero AI and emit a valid `Distillation`
- [x] **SOCK-04**: The socket defines a coverage manifest / `unextracted[]` contract so any backend reports what it could not extract (never silently drops content)
- [x] **SOCK-05**: A backend conformance suite verifies any backend honors the contract (traces present, coverage reported, faithfulness gate passes)

### AI-Optional Packaging

- [x] **PKG-01**: `pip install .` with no extras installs a fully working pipeline with zero AI dependencies
- [x] **PKG-02**: All AI/LLM dependencies live behind an `[ai]` extra and are lazy-imported only inside the AI backend
- [x] **PKG-03**: A CI gate runs the full pipeline on a bare (no-extras) install and fails if any AI import is reachable from core
- [x] **PKG-04**: An import-linter contract forbids `core` from importing any AI package; CI enforces it every phase

### Format Adapters

- [x] **ADAPT-01**: A shared `normalize()` step converts any adapter's raw extraction into typed `Claim(+Trace)` with source locators — the faithful-extraction rule lives in exactly one place
- [x] **ADAPT-02**: An Email adapter extracts structured content from `.eml` into `Claim(+Trace)`, reporting unextracted parts
- [x] **ADAPT-03**: An Excel adapter extracts cell/sheet structure via openpyxl, routing uncomputed/`None` formula cells to `unextracted[]`
- [x] **ADAPT-04**: A PowerPoint adapter extracts slide/shape text via python-pptx, reporting shapes it cannot read (e.g. SmartArt)
- [x] **ADAPT-05**: A Power BI adapter extracts from PBIP/TMDL text (or pbixray fallback), reporting row-cap/aggregation limits
- [x] **ADAPT-06**: Each adapter is covered by golden-file tests (fixture file → expected typed claims+traces)

### Provenance & Faithfulness

- [x] **PROV-01**: Every claim's `Trace` is content-addressed (hash + offset), not positional, so source edits cannot silently mis-attribute
- [x] **PROV-02**: A faithfulness gate verifies each emitted claim is entailed by its traced evidence span; the no-AI mode uses deterministic span-containment
- [x] **PROV-03**: `missing[]` and `unextracted[]` are surfaced to the reviewer on every surface, never hidden
- [x] **PROV-04**: CI blocks merge of any surface containing a STALE, un-entailed, or open-`missing[]` claim

### Rev2 Site & Renderer

- [x] **SITE-01**: A `Site/Collection/Page` content model carries stable per-surface IDs (`EP01`, `R-001`, slug, issue/date) independent of list position
- [x] **SITE-02**: The front door is the real marketing Home (8-section spec); the archive is a separate Library page
- [x] **SITE-03**: The Library renders as a status board (columns by gate state: Draft / In Review / Published)
- [x] **SITE-04**: Global navigation resolves to four real destinations with breadcrumbs and prev/next within a surface type
- [x] **SITE-05**: The fan-out diagram and every cited source render as working links (e.g. `vision.md` → repo file)
- [x] **SITE-06**: All site output regenerates from the renderer/templates (no hand-edited HTML)

### Work-Surface Installation

- [x] **WORK-01**: An operator can `pip install` Newsletters and point read-only adapters at a work codebase with data staying local
- [x] **WORK-02**: An operator can author a Report by hand (manual backend) and have it inherit the traced structure
- [x] **WORK-03**: The published Library shows how the work was done (process visible via Provenance/Lineage on each surface)

### Learning & Onboarding

- [x] **LEARN-01**: A Learning/Onboarding surface preset re-cuts a reviewed record for a newcomer/learner audience — progressive disclosure, prerequisite context, and an in-context glossary of terms
- [ ] **LEARN-02**: Every concept on a learning surface links back to its source record/claim, so a learner can trace explanation → evidence (teaching by traceability)
- [ ] **LEARN-03**: An onboarding path sequences multiple records into an ordered learning track for a new team member / training-program participant

### Problem Lifecycle Layer (A2 — Rev2 extension)

> Routed 2026-06-17 (`/gsd-explore` A1-vs-A2 design pass). Decision: **A2, scoped as a legibility
> layer, not an execution tracker.** Rationale + boundary reconciliation in
> `.planning/notes/a2-problem-lifecycle-decision.md`. Extends the spine after Phase 12; does not
> alter Phases 1–12.

- [ ] **PROB-01**: A first-class `Problem` entity sits *above* `Source`, aggregating ≥1 traced `Source` (scattered ticket / passdown / RCA) and carrying its own lifecycle state ladder (`Identified → Owned → In Progress → Resolved → Verified`) — kept rigorously distinct from the surface review gate (`Draft → In Review → Published`) and the surface fan-out chain
- [ ] **PROB-02**: The problem portfolio is queryable and aggregatable — group/count/age problems by node/area and surface recurrence across records (the cross-record view A1 structurally cannot produce)
- [ ] **PROB-03** *(hard constraint)*: The Problem layer is a **legibility layer, not an execution tracker** — no write-back to external systems (Jira/Azure DevOps); the problem-SOLVING step stays external/operator-owned (preserves the `semantic.py` spine boundary). Lifecycle-state transitions are human-gated, never auto-mutated
- [ ] **PROB-04**: A problem-board surface renders the portfolio alongside the existing gate-state board; every problem links back to its constituent `Source` records/claims, so the lifecycle stays traceable to evidence

## v2 Requirements

### AI Backend

- **AI-01**: An `AIBackend` (pydantic-ai, lazy import) produces traced claims conforming to the same socket contract
- **AI-02**: Claim-level evidence UX (PaperTrail-style supported / unsupported / omitted) on review surfaces

### Personalization

- **PERS-01**: Per-reader re-cut from a typed, local corpus hook (the config boundary only — the learning engine is V3/out of scope)

### Connections (candidate — parked)

- **CONN-01**: Model and show relationships between records, claims, and surfaces (a connection / map view) so readers can see how knowledge connects — beyond per-surface cross-links. *Parked: explore after core V2.*

## Out of Scope

| Feature | Reason |
|---------|--------|
| V3 PulseIQ learning engine | Proprietary, separate; only the typed config hook is in V2 |
| Auto-publish of any kind | Violates the human-in-the-loop core |
| Editorializing/abstractive distillation | Breaks "faithful, not suggestive" and auditability |
| Telemetry / external calls on content | Self-hostable, no phone-home (drop `langsmith`) |
| `.msg` via GPL `extract-msg` | License incompatible (GPL would force whole package to GPL) |
| Owning the problem-solving agent | Newsletters owns capture + trust + publish, not the working agent |

## Traceability

Mapped during roadmap creation (2026-06-14). Every v1 requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SOCK-01 | Phase 1 — Distill Socket Contract | Done (01-01) |
| SOCK-02 | Phase 1 — Distill Socket Contract | Done (01-01) |
| SOCK-03 | Phase 1 — Distill Socket Contract | Done (01-01) |
| SOCK-04 | Phase 1 — Distill Socket Contract | Done (01-01) |
| SOCK-05 | Phase 1 — Distill Socket Contract | Complete |
| PKG-01 | Phase 2 — AI-Optional Packaging Boundary | Complete |
| PKG-02 | Phase 2 — AI-Optional Packaging Boundary | Complete |
| PKG-03 | Phase 2 — AI-Optional Packaging Boundary | Complete |
| PKG-04 | Phase 2 — AI-Optional Packaging Boundary | Complete |
| PROV-01 | Phase 3 — Content-Addressed Provenance & Faithfulness Gate | Complete |
| PROV-02 | Phase 3 — Content-Addressed Provenance & Faithfulness Gate | Complete |
| ADAPT-01 | Phase 4 — Shared Adapter Normalizer & Email Adapter | Complete |
| ADAPT-02 | Phase 4 — Shared Adapter Normalizer & Email Adapter | Complete |
| ADAPT-06 | Phase 4 — Shared Adapter Normalizer & Email Adapter | Complete |
| ADAPT-03 | Phase 5 — Excel Adapter | Complete |
| ADAPT-04 | Phase 6 — PowerPoint Adapter | Complete |
| ADAPT-05 | Phase 7 — Power BI Adapter | Complete |
| SITE-01 | Phase 8 — Site Content Model & Stable IDs | Complete |
| SITE-02 | Phase 9 — Rev2 Site IA, Navigation & Source Links | Complete |
| SITE-03 | Phase 9 — Rev2 Site IA, Navigation & Source Links | Complete |
| SITE-04 | Phase 9 — Rev2 Site IA, Navigation & Source Links | Complete |
| SITE-05 | Phase 9 — Rev2 Site IA, Navigation & Source Links | Complete |
| SITE-06 | Phase 9 — Rev2 Site IA, Navigation & Source Links | Complete |
| PROV-03 | Phase 10 — Reviewer Surfacing & Merge-Block Gate | Complete |
| PROV-04 | Phase 10 — Reviewer Surfacing & Merge-Block Gate | Complete |
| WORK-01 | Phase 11 — Work-Surface Installation | Complete |
| WORK-02 | Phase 11 — Work-Surface Installation | Complete |
| WORK-03 | Phase 11 — Work-Surface Installation | Complete |
| LEARN-01 | Phase 12 — Learning & Onboarding Surface | Complete |
| LEARN-02 | Phase 12 — Learning & Onboarding Surface | Pending |
| LEARN-03 | Phase 12 — Learning & Onboarding Surface | Pending |
| PROB-01 | Phase 13 — Problem Lifecycle Entity | Pending |
| PROB-02 | Phase 14 — Problem Board Portfolio Surface | Pending |
| PROB-03 | Phase 13 — Problem Lifecycle Entity | Pending |
| PROB-04 | Phase 14 — Problem Board Portfolio Surface | Pending |

**Coverage:**

- v1 requirements: 31 total
- A2 extension (Rev2.1): 4 (PROB-01..04) — mapped to Phases 13–14
- Mapped to phases: 35/35 (100%) — no orphans, no duplicates
- v2 deferred: AI-01, AI-02 (AI backend track); PERS-01 (V3 config hook only); CONN-01 (connections — parked)

---
*Requirements defined: 2026-06-14*
*Last updated: 2026-06-17 — added A2 Problem Lifecycle Layer (PROB-01..04 → Phases 13–14)*
