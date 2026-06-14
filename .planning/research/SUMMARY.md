# Project Research Summary

**Project:** Newsletters (Rev2 milestone)
**Domain:** Semantic information distillation framework — faithful structured extraction → claim-level provenance → human review gate → multi-surface fan-out
**Researched:** 2026-06-14
**Confidence:** MEDIUM-HIGH overall (stack HIGH; architecture HIGH on patterns, MEDIUM on code state; features MEDIUM; pitfalls MEDIUM-HIGH)

---

## Executive Summary

Newsletters Rev2 is a brownfield extension of a deterministic trust-and-publish pipeline. The core thesis — "the trust-and-publish layer is the product, not the generation" — is well-differentiated against the surveyed landscape: no single OSS competitor combines claim-level provenance, a git-PR review gate, AI-optional architecture, and multi-surface fan-out. Rev1 built the typed semantic spine and human gate in principle; Rev2 operationalises them with a formally-defined distill socket, format adapters (PPTX/XLSX/Power BI/Email), an AI-optional packaging boundary, and a corrected static-site renderer. The recommended approach is Hexagonal / Ports-and-Adapters: a `DistillPort` Protocol at the centre, three peer backends (manual / format-adapter / AI) behind it, and a `RendererPort` for the site — with every third-party library living in optional extras, never in the core import graph.

The two non-negotiable invariants that must be established in Phase 1 and kept permanently green are: (a) a bare `pip install newsletters` (no extras) runs the full capture → review → render pipeline end-to-end with zero AI dependencies, enforced by CI and an import-linter contract; and (b) every emitted claim is entailed by its traced evidence span, enforced for all backends by a faithfulness/entailment gate at the socket boundary. These are standing CI invariants, not one-time tasks — every subsequent phase must leave them green.

**Critical roadmap precondition — the Rev1 spine:** Architecture research confirmed that the current working branch does not contain the documented Rev1 spine. `src/newsletters/models.py` holds OKR-style types (`Kpi`, `KeyResult`, `Objective`, `TeamMember`), not `Source / Claim / Trace / Distillation / Surface`. The documented spine exists on branch `claude/magical-einstein-hfd1np`. The roadmap must begin with an explicit decision: **merge the Rev1 branch into main OR build the spine to spec from scratch on this branch.** No subsequent phase can proceed without `Source / Claim / Trace / Distillation / Surface` present in the working codebase.

---

## Key Findings

### Recommended Stack

The stack is fully resolved and license-clean. The core package depends only on `pydantic>=2`, `jinja2>=3.1.6`, `typer`, and `sqlmodel`. Format adapters live behind a `[adapters]` extra (`python-pptx==1.0.2`, `openpyxl==3.1.5`, `olefile==0.47`, `pbixray==0.11.1`); the AI backend lives behind an `[ai]` extra (`pydantic-ai>=1.107.0`). Email and Power BI TMDL/PBIP paths use stdlib only and require no extra. `langchain`, `langgraph`, and `langsmith` must leave `[project.dependencies]` entirely — `langsmith` phones home, violating the no-telemetry constraint.

**Core technologies:**
- `python-pptx==1.0.2`: PPTX adapter — MIT, pure-Python, deterministic; trace anchor = slide/shape coordinates
- `openpyxl==3.1.5`: XLSX adapter — MIT, cell-level reads; read formula + cached value; trace anchor = `sheet!cell`
- `stdlib email`: Email adapter — zero deps, deterministic; trace anchor = `Message-ID` + part index
- `stdlib csv/pathlib` + TMDL text walk: preferred Power BI path — zero deps, fully faithful, diffable
- `pbixray==0.11.1`: Binary `.pbix` fallback — MIT; pulls pandas/numpy transitively so keep in `[adapters]`
- `pydantic-ai>=1.107.0`: The single optional AI distill socket — MIT, model-agnostic, built-in typed/structured output; shares Pydantic v2 with existing models
- `jinja2==3.1.6`: Rev2 static-site renderer — BSD-3; `autoescape=True`; no JS, no external calls
- **Never ship:** `extract-msg` (GPL-3.0, incompatible with MIT core); `langchain/langgraph/langsmith` in core deps; `pandas/numpy` as required deps for XLSX

### Expected Features

Rev1 already delivered the table-stakes spine. Rev2 must close the remaining gaps and establish the socket that gates everything else.

**Must have — Rev2 core (P1):**
- Distill socket interface (one `DistillPort` Protocol; coverage manifest + entailment contract baked in) — everything else is gated on this
- AI-optional packaging (`langchain` → `[ai]` extra; bare-install CI gate + import-linter)
- "Faithful, not suggestive" enforcement — claims must be entailed by their traced evidence span; adversarial fixtures for all backends
- Per-surface stable IDs (`EP01`, `R-001`, slug) — fixes numbering-collision bug; unblocks links, board, cross-links
- Real traceable source links (cited sources → clickable repo/file links)
- Rev2 site IA fix — real Home vs Library status-board split; four nav links → four real destinations
- By-hand backend formalised through the socket (`capture.py` → `ManualBackend` emitting `Distillation`)

**Should have — Rev2.x after core validates (P2):**
- Format adapters: Email (stdlib, no extra) → Excel → PPTX → Power BI, in ascending complexity order
- Claim-level provenance UX (supported/unsupported/omitted, brushing-and-linking, margin annotations) — depends on real source links
- AI distill backend (pydantic-ai behind the socket) — only after deterministic backends are proven
- Library status-board + cross-links + clickable fan-out diagram — depends on per-surface IDs

**Defer (v2+ / explicit boundary):**
- Per-reader corpus personalization engine — this is V3 PulseIQ, private + out of OSS scope
- Additional ingest connectors (Slack/Confluence/etc.) — connector sprawl is an anti-feature until demand-driven

**Anti-features (never build):**
- Auto-publish of any kind
- Editorializing / suggestive distillation
- LLM as required dependency
- Telemetry / cloud engagement tracking
- Heavy in-app WYSIWYG editor + comment threads

### Architecture Approach

The right reference model is Hexagonal / Ports-and-Adapters. The domain core (`core/`) holds pure Pydantic types and Protocols; it imports only pydantic + stdlib. All third-party libs live in adapter modules gated by extras and (for AI) lazy function-local imports. The single most important boundary is `DistillPort`: one method `distill(sources: list[Source]) -> Distillation`. Manual, format-adapter, and AI backends all implement it by structural duck-typing (Python `Protocol`); the pipeline downstream never knows which backend ran. The renderer is also an adapter behind `RendererPort`, meaning the Rev2 template redesign is internal to `render/` and does not touch core — enabling parallel tracks.

**Major components:**
1. `core/models.py` — typed spine: `Source`, `Claim`, `Trace`, `Distillation`, `Surface`, gate states (Pydantic v2; no heavy deps)
2. `core/ports.py` — `DistillPort` Protocol + `RawExtraction` / typed `Locator` union (`CellLocator | SlideLocator | MessageLocator`)
3. `core/gate.py` — `Draft → InReview → Published` state machine; `missing[]` + `unextracted[]` handling; no auto-publish edge
4. `distill/manual.py` — `ManualBackend` (zero AI, zero network; the primary deterministic path)
5. `distill/formats/` — `FormatAdapterBackend` + per-format extractors (PPTX, XLSX, email, Power BI); shared normalizer maps `RawExtraction → Claim(+Trace)` in one place
6. `distill/ai.py` — `AIBackend` with lazy `pydantic-ai` import; faithful extraction only, never editorialising
7. `render/` — `Site / Collection / Page` content model → Jinja2 templates → tokenised no-JS HTML; IDs from model, never from list position
8. `core/registry.py` + `plugins.py` — entry-point discovery for backends (stevedore pattern; built-ins registered the same way as third-party backends)

### Critical Pitfalls

1. **Silent extraction loss** — Format adapters silently drop SmartArt, grouped shapes, charts, formula-cells-with-no-cache, Power BI row-cap truncation, forwarded email parts. Prevent: every adapter emits a `coverage manifest` + `unextracted[]` list alongside its claims; route `unextracted[]` into `missing[]`; round-trip fidelity CI test. The `unextracted[]` contract must be designed into the socket interface before any adapter is built — retrofitting across three adapters is expensive.

2. **Traceability rot** — Traces by file path / slide index / row number / list position silently point at wrong evidence after the source changes. Prevent: `Trace` stores a content hash + verbatim evidence span, not position. Stable surface IDs generated from content, never from `enumerate()`. `newsletters build` recomputes hashes and bounces STALE claims to `InReview`; merge blocked while any claim is STALE or unresolved.

3. **"Optional" AI quietly becomes required** — A single top-level `import langchain` anywhere on the core import path defeats the AI-optional promise. Prevent: bare `pip install .` (no extras) + full-pipeline CI is a release blocker; import-linter contract; AI imports are lazy function-local only; default backend = `manual`. This is a standing CI invariant, not a one-time task.

4. **Editorialising / hallucination leaking through the gate** — The AI backend adds emphasis, framing, or facts not in the source; ROUGE does not catch this. Prevent: entailment gate at the socket boundary — every emitted claim must be entailed by its traced evidence span; claims that fail go to `missing[]`; adversarial faithfulness fixtures on every backend. This contract lives on the socket interface, not just the AI adapter.

5. **Review gate becomes a rubber stamp** — Volume + automation bias causes reviewers to merge without inspecting traces. Prevent: review view shows each claim next to its verbatim Trace and open `missing[]`/`unextracted[]` items by default; merge CI-blocked while any claim is STALE, un-entailed, or has unresolved flags; per-flag forcing functions, not a single approve button.

6. **Backend divergence** — AI backend built first; interface ossifies around its output; manual path becomes second-class. Prevent: build `ManualBackend` first; define the conformance + faithfulness test suite with the socket interface; every backend must pass it; no `if backend ==` branches downstream.

---

## Implications for Roadmap

### PRECONDITION: Resolve the Rev1 spine branch

Before Phase 1 can begin, the team must make an explicit decision:

**Option A — Merge:** merge branch `claude/magical-einstein-hfd1np` into main to bring the documented Rev1 spine (`Source / Claim / Trace / Distillation / Surface`, capture, render, promote) into the working codebase.

**Option B — Rebuild:** treat the current working branch as greenfield and build the spine to spec from scratch, using the documented Rev1 design as the authoritative specification.

Either option must resolve before any Phase 1 work begins. The roadmap cannot proceed assuming the spine exists on the current branch — it does not.

---

### Phase 1: Spine + Socket Foundation

**Rationale:** The `DistillPort` socket contract is the critical path item that gates every subsequent phase. Architecture's build-order analysis, Features' dependency graph, and Pitfalls' phase-mapping all converge: define the socket (including the `coverage manifest / unextracted[]` contract and the entailment/faithfulness conformance suite) before building any adapter or backend. The AI-optional packaging boundary must also land here so the "deterministic spine ships without AI" invariant is true from day one. If the Rev1 spine is absent from the working branch (see Precondition), rebuilding/merging it is also Phase 1 work.

**Delivers:**
- `core/models.py` — `Source`, `Claim`, `Trace`, `Distillation`, `Surface`, gate states
- `core/ports.py` — `DistillPort` Protocol; `RawExtraction` + typed `Locator` union; `coverage_manifest` + `unextracted[]` fields on `Distillation`
- `core/gate.py` — `Draft → InReview → Published` state machine; no auto-publish edge
- `core/pipeline.py` + `core/registry.py` — backend-agnostic orchestration + entry-point discovery
- `distill/manual.py` — `ManualBackend` (zero AI; proves the socket end-to-end with one concrete backend)
- `pyproject.toml` refactor — `langchain/langgraph/langsmith` moved to `[ai]` extra
- CI gates — bare `pip install .` full-pipeline test; import-linter contract (both standing invariants)
- Conformance + faithfulness test suite (adversarial fixtures; entailment gate stub for all backends)

**Addresses:** distill socket interface, AI-optional packaging, by-hand backend formalised, "faithful, not suggestive" enforcement
**Avoids:** Pitfalls 3 (dependency creep), 4 (editorialising), 6 (backend divergence)
**Research flag:** NEEDS RESEARCH-PHASE — exact `DistillPort` contract shape is marked `[OPEN]` in the brief. Close with a planning-research cycle before implementation.

---

### Phase 2: Rev2 Renderer + Site IA

**Rationale:** The renderer track depends on core types but is independent of which distill backend runs — it can be prototyped against fixture data in parallel with adapter work. Landing it early fixes the deployed site (broken navigation, numbering collisions, no real Home vs Library split) and unblocks per-surface IDs, which in turn unblock source links, the status board, and cross-links.

**Delivers:**
- Per-surface stable IDs (`EP01`, `R-001`, slug, issue-date) — generated from content, never from list position
- `render/site.py` — `Site / Collection / Page` content model
- Jinja2 templates — real Home (8-section spec), Library status-board (CSS columns by gate state), surface pages with breadcrumbs + prev/next
- Real traceable source links (Trace locator → `<a href>` into repo/file)
- Cross-links between surfaces; clickable fan-out diagram
- Nav fix: four nav links → four real destinations

**Addresses:** Rev2 site IA fix, per-surface IDs, real traceable source links
**Avoids:** Pitfall 2 (traceability rot — IDs and links now content-derived); Pitfall 5 (review view shows evidence first)
**Uses:** Jinja2 3.1.6 with `autoescape=True`; design tokens → CSS; no JS
**Research flag:** Standard patterns — Jinja2 SSG well-documented. Verify the Home 8-section spec is written down before templating.

---

### Phase 3: Format Adapters

**Rationale:** Adapters are the highest-value Rev2 feature for the primary operator (format-in → trusted claim-out, deterministic, no AI tokens). They depend on Phase 1's socket contract + `RawExtraction / Locator` types. Build in ascending-complexity order: Email (stdlib, no extra) → Excel → PPTX → Power BI.

**Delivers:**
- `distill/formats/base.py` — shared `RawExtraction → Claim(+Trace)` normalizer (one trust rule, one place)
- `distill/formats/email_.py` — stdlib email adapter; charset fallback + logged replacement; `message/rfc822` recursion
- `distill/formats/excel.py` — openpyxl adapter; formula + cached-value reads; merge-range detection; `data_only=None` → `unextracted[]`
- `distill/formats/pptx.py` — python-pptx adapter; grouped-shape recursion; OOXML SmartArt fallback; notes slides
- `distill/formats/powerbi.py` — TMDL text walk (stdlib) preferred; `pbixray` binary fallback; row-cap detection → `unextracted[]`
- Round-trip fidelity CI test for each adapter
- `pyproject.toml` `[adapters]` extra wired

**Addresses:** multi-format ingest (PPT/Excel/Email/Power BI)
**Avoids:** Pitfall 1 (silent extraction loss — coverage manifest + `unextracted[]` enforced per adapter)
**Uses:** python-pptx 1.0.2, openpyxl 3.1.5, stdlib email, stdlib csv/pathlib, pbixray 0.11.1, olefile 0.47
**Research flag:** NEEDS RESEARCH-PHASE per adapter — non-obvious extraction gaps (SmartArt, merged cells, Power BI row caps, charset mismatches) require fixture-driven investigation.

---

### Phase 4: AI Backend + Provenance UX

**Rationale:** The AI backend is the last backend to add — after manual and format-adapter backends are proven and the conformance suite is in place. AI must conform to the established typed shape, not the other way around. Claim-level provenance UX depends on real source links (Phase 2). Both complete the "faithful, not suggestive" story end-to-end.

**Delivers:**
- `distill/ai.py` — `AIBackend` with lazy `pydantic-ai` import; structured typed `Distillation` output; extractive-only prompt; entailment gate applied to output
- `pyproject.toml` `[ai]` extra wired
- Claim-level provenance UX — supported/unsupported/omitted indicators in review view; hover/highlight claim ↔ source span; margin annotations; gate badges
- Merge-block CI check on provenance state (STALE / un-entailed / open `missing[]` → merge blocked)

**Addresses:** AI distill backend, claim-level provenance UX
**Avoids:** Pitfall 4 (hallucination — entailment gate on AI output); Pitfall 5 (rubber-stamp gate — evidence-first review view + merge block)
**Uses:** pydantic-ai 1.107.0 (MIT, model-agnostic, built-in structured output)
**Research flag:** NEEDS RESEARCH-PHASE — pydantic-ai prompt patterns for faithful (extractive) distillation; entailment gate implementation (local NLI model vs heuristic vs AI self-check).

---

### Phase Ordering Rationale

- **Socket before adapters:** Pitfalls 1, 4, 6 are all prevented by contracts defined at the socket. Retrofitting `unextracted[]`, the entailment gate, and the conformance suite after three adapters exist means rewriting all three.
- **Manual backend before AI:** manual is the primary user path and the zero-dep baseline. AI must conform to it, not vice versa.
- **Renderer in parallel with adapters:** depends only on core types, not on which backend runs. Fixes the deployed site immediately and unblocks per-surface IDs.
- **Format adapters before AI:** deterministic common case; AI handles only the messy residue.
- **AI last:** conforms to established conformance suite; no structural privilege over other backends.
- **Standing invariants from Phase 1 onward:** bare-install CI gate + import-linter + entailment gate must stay green across every phase — not one-time deliverables.

### Research Flags

Phases needing deeper research during planning:
- **Phase 1 (socket contract):** `[OPEN]` in brief — exact `DistillPort` shape, `coverage_manifest` fields, `Locator` union design, entailment gate integration point.
- **Phase 3 (format adapters):** each adapter has documented non-obvious extraction gaps. Run a focused research cycle per format before implementation.
- **Phase 4 (AI backend):** pydantic-ai structured-output patterns for faithful (extractive) distillation; entailment gate implementation options.

Phases with standard patterns (skip research-phase):
- **Phase 2 (renderer):** Jinja2 SSG + CSS-columns status-board are well-documented. Primary unknowns are UX/design decisions resolvable from the existing brief/design spec.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions and licenses verified against PyPI JSON; all MIT-compatible; no ambiguity on what goes in core vs extras |
| Features | MEDIUM | No single OSS competitor implements the integrated whole; individual category norms MEDIUM-HIGH; integrated UX is inferred |
| Architecture | HIGH (patterns) / MEDIUM (code state) | Hexagonal/ports-and-adapters is mature and well-documented; current code state on working branch is a stub, not the Rev1 spine |
| Pitfalls | MEDIUM-HIGH | Extraction-fidelity and faithfulness pitfalls HIGH (official library docs + research); HITL rubber-stamp and provenance-integrity pitfalls MEDIUM (applied literature) |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **`DistillPort` exact contract shape (`[OPEN]`):** must be resolved in Phase 1 planning before any backend or adapter is built against it. Key questions: what fields does `coverage_manifest` expose? What is the full `Locator` union? How does the entailment gate plug into the socket?
- **Rev1 branch decision (PRECONDITION):** the roadmap cannot proceed until the team decides whether to merge `claude/magical-einstein-hfd1np` or rebuild the spine on the current branch.
- **Home 8-section spec:** brief references "the approved 8-section spec" for the Home page. Verify this spec is captured in writing before Phase 2 templating begins.
- **Work-surface installation design:** brief marks this `[OPEN]` — should be captured early so Phase 2 templates serve the real operator context.
- **Entailment gate implementation:** for Phase 1 socket contract and Phase 4 AI backend, a lightweight faithfulness check is needed. Whether this is a local NLI model, a verbatim-span heuristic, or an AI self-check has cost and correctness implications. Research during Phase 1 planning.

---

## Sources

### Primary (HIGH confidence)
- PyPI JSON API — versions and licenses for python-pptx 1.0.2, openpyxl 3.1.5, jinja2 3.1.6, pydantic-ai 1.107.0, pbixray 0.11.1, olefile 0.47, extract-msg 0.55.0
- python-pptx official docs — structure, SmartArt/grouped-shape limitations, notes slides
- openpyxl official docs — `read_only`, `data_only`, formula/cache semantics, merged cells
- Python Packaging User Guide — entry-point plugin discovery
- PEP 810 / discuss.python.org — optional/lazy dependency boundary idiom
- `.planning/PROJECT.md`, `.planning/brief.md`, `src/newsletters/models.py`, `pyproject.toml` — ground truth for current code state

### Secondary (MEDIUM confidence)
- PaperTrail (CHI'26) — claim-level provenance UX: supported/unsupported/omitted, brushing-and-linking
- GenProve, CiteCheck, TROVE — faithfulness vs correctness; ROUGE hides hallucination; extractive = inherently faithful
- stevedore/OpenStack essays — "use entry points even for built-ins to eliminate special cases"
- Onyx/Danswer, RAGFlow, ReleaseNotes.io, Planable — category norms for grounded answers, changelog, internal comms
- Microsoft Learn — Power BI export row caps (30k/150k/16MB), summarised vs underlying data
- HITL/oversight literature — rubber-stamp risk, automation bias, reviewer fatigue, forcing functions

### Tertiary (LOW confidence — inferred / single-source)
- Integrated UX across all five surveyed categories — no single competitor implements the whole; the combination is inferred from parts
- Provider-comparison pydantic-ai vs litellm — web comparison, not direct implementation test

---

*Research completed: 2026-06-14*
*Ready for roadmap: yes — pending Rev1 branch decision (see Precondition above)*
