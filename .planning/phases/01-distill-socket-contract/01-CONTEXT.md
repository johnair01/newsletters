# Phase 1: Distill Socket Contract - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the **`DistillPort`** contract — the one boundary every distill backend
speaks through — plus a backend registry, a **ManualBackend**, the coverage/`unextracted[]`
contract, and a conformance suite (SOCK-01..05). The contract must be big enough to fit
**three distill modalities** without building all of them here. Builds on the merged Rev1
spine (`Source/Claim/Trace/Distillation/Review/Surface` in `semantic.py`).
</domain>

<decisions>
## Implementation Decisions

### The socket's modalities (the core decision)
- **D-01:** The socket supports **three distill modalities, all emitting the same typed
  `Distillation`**: (a) **author by hand** (human states claims + evidence directly),
  (b) **generic, low-token file extraction** (template-*agnostic* adapters — PPTX, email,
  Excel, …; the MBPS reports are PowerPoints, so no bespoke per-template parsers),
  (c) **agentic interview** (agents interview the human / their work / their codebase to
  fill gaps). Downstream (review, render, promote) is modality-agnostic.
- **D-02:** Phase 1 builds the **contract + registry + the manual backend** (wrapping the
  existing `capture.capture_session()`). The extraction backends are the adapter phases
  (4–7); the interview/AI backend is the v2 AI track (AI-01/02). Phase 1 only has to make
  the contract accommodate all three.

### Low-token is a first-class property
- **D-03:** "Cheapest model, minimal reasoning" is the default posture; **format consistency
  is the lever** that keeps extraction cheap. The contract should carry a notion of
  cost/effort so an operator can prefer the cheap path. Generic, not bespoke.

### Output shape
- **D-04:** A `Distillation` must serialize losslessly to/from **JSON** (sidecar/adjacent
  files) — extractions persist as diffable artifacts and feed templated articles.

### How gaps are reported (Area 2)
- **D-05:** **Two distinct kinds of honesty, both surfaced, never silent:** *unreadable* —
  raw content a backend could not extract (the coverage manifest / `unextracted[]`); and
  *unprovable* — a claim with no entailed evidence (the existing `Distillation.missing[]`).
  Keep them separate.

### Seeing evidence as you write (Area 4)
- **D-06:** At draft/author time each claim is shown next to its **exact source snippet**
  (its `Trace`), so "faithful, not suggestive" is *visible*, not trusted. The reviewer UI is
  Phase 10, but the **contract must carry the verbatim span** to make it possible.

### Claude's Discretion
The exact Python shape of `DistillPort` (Protocol signature, registry mechanism, JSON
(de)serialization), and how `ManualBackend` adapts `capture_session()` — builder/researcher's
call, to be surfaced in the Phase-1 research cycle (flagged `[OPEN]` in STATE).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The spine this builds on
- `src/newsletters/semantic.py` — `Source/Trace/Claim/Distillation/Review/Surface`; the
  `synthesize()` stub (the boundary being formalized); the no-auto-publish gate.
- `src/newsletters/capture.py` — the deterministic, no-LLM `capture_session()` the
  ManualBackend wraps.

### Requirements & research
- `.planning/REQUIREMENTS.md` — SOCK-01..05 (this phase).
- `.planning/research/ARCHITECTURE.md` — ports-and-adapters / `DistillPort` guidance; the
  custom locator/provenance layer.
- `.planning/research/STACK.md` — `pydantic-ai` behind `[ai]`; adapter libraries; license gate.

### Project truths & spec
- `CLAUDE.md` and `WHERE-WE-ARE.md` — the truths + hard rules the contract must honor
  (no auto-publish; faithful not suggestive; AI-optional core; low-token generic default).
- `docs/architecture.md` §1–§3 — typed model, package API (`synthesize`/`Corpus`/`render`),
  the publish loop.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Distillation` / `Claim` / `Trace` already exist and are typed — the socket emits these.
- `Distillation.missing[]` already exists — reuse it for the "unprovable" gap (D-05).
- `capture.capture_session()` — the engine of the **manual** modality (D-02).

### Established Patterns
- The review gate (`Review`, `ReviewState`, policy; `_published_requires_satisfied_policy`)
  is enforced in `semantic.py`. The socket produces a `Distillation`; a `Surface` wraps it
  under that gate. **No auto-publish path** — the socket must not create one.

### Integration Points
- `synthesize(event, sources, audience) -> Distillation` is the current entrypoint (raises
  `NotImplementedError`). The socket either backs it or sits beside it — builder's call.
</code_context>

<specifics>
## Specific Ideas

- **"Agents are interviewers"** is the signature interaction — interview the human / their
  work / their codebase. Carry it as a first-class modality even though it's built later.
- Output to **JSON sidecars**; consistent-format inputs (e.g., MBPS PowerPoints) keep
  extraction cheap. The engine reads reports already filled by hand, learns from good
  examples, and asks "what's needed to fill this faithfully?"
- The promotion chain **Report → Article → Newsletter** (each human-gated) is the spine the
  socket feeds.
</specifics>

<deferred>
## Deferred Ideas

- **Swim-lane / KPI organizing unit** — a tracked area with KPIs/topics that reports roll up
  under; relates to `models.py` (OKR/KPI) and the `Claim → KPI` promotion. Model later.
- **Templates-as-scaffold learning** — read good filled examples, ask what's needed to fill a
  report template faithfully. Extraction/interview capability — later phase.
- **Interview-agent tooling** — the interns' interview → bring-in-reports → validate flow.
- **The five deployment contexts** (work / PulseIQ / interns / Newsletters / generic) — these
  are corpora + config, not Phase-1 code.

### Reviewed Todos (not folded)
None — discussion stayed within phase scope.
</deferred>

---

*Phase: 1-Distill Socket Contract*
*Context gathered: 2026-06-14*
