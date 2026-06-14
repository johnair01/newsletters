# Requirements: Newsletters (Rev2)

**Defined:** 2026-06-14
**Core Value:** A deterministic, auditable pipeline that traces every published claim to evidence and never auto-publishes — AI is an optional accelerator, never an authority.

> Rev1 spine is **Validated** (merged from `claude/magical-einstein-hfd1np`): typed
> `Source/Claim/Trace/Distillation/Surface`, deterministic capture, review gate, HTML renderer.
> The v1 requirements below are the **Rev2** scope that builds on it.

## v1 Requirements

### Distill Socket

- [ ] **SOCK-01**: A `DistillPort` protocol defines one backend contract — `distill(sources) -> Distillation` — that the pipeline consumes without knowing which backend produced the result
- [ ] **SOCK-02**: A backend registry lets an operator register/select a distill backend (manual / adapter / AI) by name
- [ ] **SOCK-03**: A `ManualBackend` lets an operator author claims+traces by hand with zero AI and emit a valid `Distillation`
- [ ] **SOCK-04**: The socket defines a coverage manifest / `unextracted[]` contract so any backend reports what it could not extract (never silently drops content)
- [ ] **SOCK-05**: A backend conformance suite verifies any backend honors the contract (traces present, coverage reported, faithfulness gate passes)

### AI-Optional Packaging

- [ ] **PKG-01**: `pip install .` with no extras installs a fully working pipeline with zero AI dependencies
- [ ] **PKG-02**: All AI/LLM dependencies live behind an `[ai]` extra and are lazy-imported only inside the AI backend
- [ ] **PKG-03**: A CI gate runs the full pipeline on a bare (no-extras) install and fails if any AI import is reachable from core
- [ ] **PKG-04**: An import-linter contract forbids `core` from importing any AI package; CI enforces it every phase

### Format Adapters

- [ ] **ADAPT-01**: A shared `normalize()` step converts any adapter's raw extraction into typed `Claim(+Trace)` with source locators — the faithful-extraction rule lives in exactly one place
- [ ] **ADAPT-02**: An Email adapter extracts structured content from `.eml` into `Claim(+Trace)`, reporting unextracted parts
- [ ] **ADAPT-03**: An Excel adapter extracts cell/sheet structure via openpyxl, routing uncomputed/`None` formula cells to `unextracted[]`
- [ ] **ADAPT-04**: A PowerPoint adapter extracts slide/shape text via python-pptx, reporting shapes it cannot read (e.g. SmartArt)
- [ ] **ADAPT-05**: A Power BI adapter extracts from PBIP/TMDL text (or pbixray fallback), reporting row-cap/aggregation limits
- [ ] **ADAPT-06**: Each adapter is covered by golden-file tests (fixture file → expected typed claims+traces)

### Provenance & Faithfulness

- [ ] **PROV-01**: Every claim's `Trace` is content-addressed (hash + offset), not positional, so source edits cannot silently mis-attribute
- [ ] **PROV-02**: A faithfulness gate verifies each emitted claim is entailed by its traced evidence span; the no-AI mode uses deterministic span-containment
- [ ] **PROV-03**: `missing[]` and `unextracted[]` are surfaced to the reviewer on every surface, never hidden
- [ ] **PROV-04**: CI blocks merge of any surface containing a STALE, un-entailed, or open-`missing[]` claim

### Rev2 Site & Renderer

- [ ] **SITE-01**: A `Site/Collection/Page` content model carries stable per-surface IDs (`EP01`, `R-001`, slug, issue/date) independent of list position
- [ ] **SITE-02**: The front door is the real marketing Home (8-section spec); the archive is a separate Library page
- [ ] **SITE-03**: The Library renders as a status board (columns by gate state: Draft / In Review / Published)
- [ ] **SITE-04**: Global navigation resolves to four real destinations with breadcrumbs and prev/next within a surface type
- [ ] **SITE-05**: The fan-out diagram and every cited source render as working links (e.g. `vision.md` → repo file)
- [ ] **SITE-06**: All site output regenerates from the renderer/templates (no hand-edited HTML)

### Work-Surface Installation

- [ ] **WORK-01**: An operator can `pip install` Newsletters and point read-only adapters at a work codebase with data staying local
- [ ] **WORK-02**: An operator can author a Report by hand (manual backend) and have it inherit the traced structure
- [ ] **WORK-03**: The published Library shows how the work was done (process visible via Provenance/Lineage on each surface)

## v2 Requirements

### AI Backend

- **AI-01**: An `AIBackend` (pydantic-ai, lazy import) produces traced claims conforming to the same socket contract
- **AI-02**: Claim-level evidence UX (PaperTrail-style supported / unsupported / omitted) on review surfaces

### Personalization

- **PERS-01**: Per-reader re-cut from a typed, local corpus hook (the config boundary only — the learning engine is V3/out of scope)

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

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| (to be mapped by roadmapper) | — | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 0 (pending roadmap)

---
*Requirements defined: 2026-06-14*
*Last updated: 2026-06-14 after initialization*
