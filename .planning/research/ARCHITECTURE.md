# Architecture Research

**Domain:** Semantic information distillation framework (Python; trust/publish pipeline with swappable backends + static multi-surface renderer)
**Researched:** 2026-06-14
**Confidence:** HIGH (patterns are mature and well-documented; MEDIUM on exact current code state — see note below)

> **Brownfield reality check (read first).** PROJECT.md / brief.md describe a rich Rev1 spine
> (`Source → Claim(+Trace) → Distillation → Surface`, capture/render/promote modules, a deployed
> Library). On the working branch the code is effectively a stub: `src/newsletters/models.py`
> holds OKR-style models (`Kpi`, `KeyResult`, `Objective`, `TeamMember`) — **not** the
> Source/Claim/Trace types — and `cli.py` is empty. The deployed HTML lives on `gh-pages`. So this
> milestone is **greenfield design under a brownfield framing**: the spine must be (re)built to the
> documented shape, and this document recommends how to structure it so the four new pieces — distill
> socket, format adapters, optional-AI boundary, Rev2 renderer — drop in cleanly. Treat the type
> sketches below as the contract to build toward, not as a description of existing code.

---

## Standard Architecture

The right reference model here is **Hexagonal / Ports-and-Adapters**. The "domain" is the typed
trust pipeline (Source → Claim+Trace → Distillation → Surface → review gate → render). Everything
that varies — *how* claims get extracted, *which* file format a source is, *whether* AI is present,
*what* HTML a surface produces — sits on the outside as adapters behind narrow ports. The domain
core depends on **interfaces (Protocols), never on concrete backends or third-party libraries.**

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CORE DOMAIN (zero 3rd-party heavy deps)            │
│                   pure types + protocols + pipeline orchestration          │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ models   │   │ DistillPort  │   │ ReviewGate   │   │ SurfaceModel   │  │
│  │ Source   │   │ (Protocol)   │   │ Draft→Review │   │ (preset config │  │
│  │ Claim    │   │ distill(     │   │ →Published   │   │  over one      │  │
│  │ Trace    │   │  Sources)    │   │ no auto-pub  │   │  template)     │  │
│  │ Distill. │   │  ->Distill.  │   │              │   │                │  │
│  └──────────┘   └──────┬───────┘   └──────────────┘   └───────┬────────┘  │
└─────────────────────────┼──────────────────────────────────────┼──────────┘
                          │ implements                            │ consumed by
        ┌─────────────────┼─────────────────┐                    │
        ▼                 ▼                 ▼                     ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐  ┌──────────────────────┐
│ ADAPTER:      │ │ ADAPTER:      │ │ ADAPTER:      │  │  RENDERER (adapter)  │
│ ManualBackend │ │ FormatAdapter │ │ AIBackend     │  │ content model → HTML │
│ (by hand /    │ │ Backend       │ │ (optional     │  │  Jinja2 templates,   │
│  capture.py)  │ │ PPTX/XLSX/    │ │  extra; lazy  │  │  Home + Library board│
│               │ │ PowerBI/Email │ │  import)      │  │  cross-linked        │
│ deterministic │ │ deterministic │ │ ← langchain   │  │  no-JS, tokenized    │
│ no AI         │ │ low-token     │ │   behind here │  │                      │
└───────────────┘ └──────┬────────┘ └───────────────┘  └──────────────────────┘
                         ▼
              ┌─────────────────────────┐
              │ FORMAT EXTRACTORS        │  python-pptx, openpyxl, std email,
              │ (sub-adapters, one per   │  Power BI export — each emits a
              │  file type)              │  RawExtraction with locators
              └─────────────────────────┘
```

The single most important boundary is the **`DistillPort`**: one method, `distill(sources) ->
Distillation`. Manual, format-adapter, and AI backends all implement it. The pipeline downstream
(review gate, render, fan-out) only ever sees a `Distillation` and is **backend-agnostic**.

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `models` (domain) | The typed spine: `Source`, `Claim`, `Trace`, `Distillation`, `Surface`, gate states. The vocabulary everything else speaks. | Pydantic v2 `BaseModel`s, no heavy deps. Keep SQLModel/persistence in a separate module so the types are import-light. |
| `DistillPort` (Protocol) | The socket contract: "raw Sources → traced Claims." One narrow interface; the only thing the pipeline calls to get a `Distillation`. | `typing.Protocol` (structural) + a registry for named lookup. |
| `ManualBackend` | Deterministic by-hand path. Wraps a finished work session / hand-authored report into a `Distillation` with hand-asserted traces. First-class, not a fallback. | The `capture.py` path. Zero AI, zero network. |
| `FormatAdapterBackend` | Pulls structure already present in office files into Claims with file-anchored traces. The deterministic, low-token common case. | Dispatches to per-format extractors; normalizes their output to `Claim(+Trace)`. |
| Format extractors | One per source type (PPTX, XLSX, Power BI export, Email). Read the file, emit `RawExtraction` units each carrying a **locator** (slide#/shape, sheet!cell, message-id/header). | `python-pptx`, `openpyxl`, stdlib `email`, Power BI exported tables. Each is its own optional extra. |
| `AIBackend` | The *only* place an LLM may touch content. Handles the "messy residue" the deterministic backends can't structure. Faithful-extraction only (extract + trace, never editorialize). | Implements `DistillPort`; imports `langchain`/`pydantic-ai` **lazily, inside the method**. |
| `ReviewGate` | Enforces `Draft → InReview → Published` in code. No path skips it. `missing[]` surfaces unsubstantiated material to the reviewer. | Pure state machine over domain types; "review = git PR, merge = publish." |
| `SurfaceModel` | Surfaces (report/article/newsletter/show) as typed presets over one `SurfaceTemplate` — cadence, audience, signal color, review policy as config; only prose templated. | Config objects + a registry operators extend. |
| Renderer | Turns the published content model into token-faithful, no-JS HTML: real Home, Library status-board, per-surface IDs, cross-links, source links. | Jinja2 + a content-model/page/collection layering (see Pattern 5). |

---

## Recommended Project Structure

```
src/newsletters/
├── core/                      # The domain. Import-light. No langchain, no python-pptx, no Jinja.
│   ├── models.py              # Source, Claim, Trace, Distillation, Surface, gate states (Pydantic)
│   ├── ports.py               # DistillPort (Protocol), RendererPort, RawExtraction, locator types
│   ├── pipeline.py            # orchestration: sources -> distill() -> gate -> surfaces
│   ├── gate.py                # Draft→InReview→Published state machine, missing[] handling
│   └── registry.py            # name -> backend lookup; entry-point discovery
├── distill/                   # Adapters implementing DistillPort
│   ├── manual.py              # ManualBackend + capture-from-session (deterministic, no AI)
│   ├── ai.py                  # AIBackend — lazy-imports langchain INSIDE methods
│   └── formats/               # FormatAdapterBackend + per-format extractors
│       ├── base.py            # Extractor protocol; RawExtraction -> Claim(+Trace) normalizer
│       ├── pptx.py            # python-pptx  (extra: [pptx])
│       ├── excel.py           # openpyxl     (extra: [excel])
│       ├── email_.py          # stdlib email (no extra needed)
│       └── powerbi.py         # Power BI export reader (extra: [powerbi])
├── surfaces/                  # SurfaceTemplate + presets (report/article/newsletter/show)
│   └── presets.py
├── render/                    # RendererPort implementation
│   ├── site.py                # Site/Collection/Page model + build orchestration
│   ├── templates/             # Jinja2: base, home (8-section), library board, surface pages
│   └── tokens.py              # design tokens (light/dark, signal colors) -> CSS
├── persist/                   # OPTIONAL: SQLModel storage; isolated so core stays import-light
├── cli.py                     # typer entry points: capture, distill, build, promote
└── plugins.py                 # registers built-in backends via entry points
```

### Structure Rationale

- **`core/` has no heavy imports.** This is the load-bearing decision. If `core` imports
  `langchain` or `python-pptx`, the "AI-optional, deterministic spine" promise is structurally
  impossible. Keeping `core` pure means a fork can `pip install newsletters` and run the whole
  pipeline (manual + email) with zero optional deps installed.
- **`distill/` is the adapter layer**, one file per backend, each owning its own optional deps. The
  AI backend and each format extractor map 1:1 to a `pyproject` extra, so install size scales with
  what you actually use (`newsletters[pptx,excel]`, `newsletters[ai]`).
- **`render/` is just another adapter** behind `RendererPort`. The Rev2 redesign is a change *inside*
  `render/` (new templates + a Site/Page content model); it does not touch `core`. That isolation is
  why the Rev2 track can proceed partially in parallel with the distill work.
- **`persist/` is quarantined.** SQLModel is currently a hard dep but persistence is orthogonal to
  the trust pipeline. Move it out of `core` so the types import without a DB stack.

---

## Architectural Patterns

### Pattern 1: Port-and-Adapter for the distill socket (Protocol-based)

**What:** Define one structural `Protocol` for the socket. Backends implement it by shape, not by
inheritance. The pipeline depends on the Protocol; the registry resolves a name to a concrete backend.

**When to use:** Always, for this project — it is the central decision. Protocols give duck-typed
flexibility (operators can drop in a backend without importing a base class) while still being
type-checkable by mypy.

**Trade-offs:** Protocols don't enforce at import time (a malformed backend fails at call time, not
registration). Mitigate with a tiny `register()` that runtime-checks the callable signature, plus a
mypy gate in CI.

**Example:**
```python
# core/ports.py  — the entire socket contract
from typing import Protocol, runtime_checkable
from .models import Source, Distillation

@runtime_checkable
class DistillPort(Protocol):
    name: str
    def distill(self, sources: list[Source]) -> Distillation: ...
    # Distillation carries claims[] each with a Trace, plus missing[] for the gate.

# distill/manual.py — a backend is just a class with that shape; NO base class needed
class ManualBackend:
    name = "manual"
    def distill(self, sources: list[Source]) -> Distillation:
        # deterministic structuring of a hand-authored session; every claim's
        # Trace is the human's asserted citation. Zero AI, zero network.
        ...
```

### Pattern 2: Entry-point plugin discovery for backends

**What:** Built-in *and* third-party backends register through `importlib.metadata` entry points
under a group like `newsletters.distill_backends`. The registry loads them lazily by name. Using
entry points even for in-tree backends "eliminates special cases" (the stevedore/OpenStack lesson).

**When to use:** As soon as there is more than one backend — which is from day one (manual + formats
+ AI). It is what lets a fork ship its own backend as a separate package with no core changes.

**Trade-offs:** Entry points resolve at runtime and can surface as confusing errors if a plugin's
deps are missing. Wrap discovery so a backend whose optional dep is absent is *listed but
unavailable* with a clear "install `newsletters[pptx]`" message, rather than crashing discovery.

**Example:**
```toml
# pyproject.toml
[project.entry-points."newsletters.distill_backends"]
manual  = "newsletters.distill.manual:ManualBackend"
formats = "newsletters.distill.formats.base:FormatAdapterBackend"
ai      = "newsletters.distill.ai:AIBackend"      # importing this triggers lazy ai deps only when used
```

### Pattern 3: Optional-AI boundary via lazy import behind one adapter

**What:** The LLM dependency lives *only* inside `AIBackend`, and is imported **inside the method
body**, not at module top. Combined with a `pyproject` extra (`[ai]`), the spine runs with the AI
package uninstalled; instantiating/using the AI backend without it raises a single, friendly error.
This is the standard Python "optional dependency" idiom (defer the `ImportError`, give a good
message).

**When to use:** This is a non-negotiable for this project ("the system must degrade gracefully to a
no-AI mode"). One boundary, one extra, one error site.

**Trade-offs:** Function-local imports slightly obscure the dependency graph and add tiny per-call
overhead. Acceptable and intended here — it is exactly what makes AI optional. Document the dep at
the top of the module in a comment so it's discoverable.

**Example:**
```python
# distill/ai.py
class AIBackend:
    name = "ai"
    def distill(self, sources: list[Source]) -> Distillation:
        try:
            from langchain_anthropic import ChatAnthropic   # lazy: only when AI is actually invoked
        except ImportError as e:
            raise RuntimeError(
                "The 'ai' distill backend requires optional deps. "
                "Install with:  pip install 'newsletters[ai]'"
            ) from e
        # ... faithful extraction only: produce Claims + Traces, never editorialize.
```
```toml
[project.optional-dependencies]
ai     = ["langchain[anthropic]", "pydantic-ai"]   # NOT in core dependencies
pptx   = ["python-pptx"]
excel  = ["openpyxl"]
powerbi= []          # reads exported CSV/JSON; stdlib only
```
**Migration note:** today `langchain`, `langgraph`, `langsmith`, `pydantic-ai` are in
`[project.dependencies]`. Step one of this milestone is moving them to `[ai]`.

### Pattern 4: Normalize-to-`Claim(+Trace)` via a two-stage extract→normalize pipeline

**What:** Each format extractor is dumb and faithful: it walks the file and emits `RawExtraction`
units, each carrying the **raw value + a typed locator** (the provenance anchor). A single shared
**normalizer** maps `RawExtraction → Claim(+Trace)`. Extractors never decide what's a "claim" beyond
structure; the normalizer applies the one faithful rule and attaches the Trace. This keeps per-format
code minimal and the trust rule in exactly one place.

**When to use:** For every format adapter. The locator is what makes the published claim auditable
("this number came from `Q2.xlsx` sheet `Revenue` cell `C14`").

**Trade-offs:** A uniform `RawExtraction` is a slightly lossy common denominator across very
different file models (a slide vs a cell vs an email thread). Solve it with a small typed-union
`Locator` (`SlideLocator | CellLocator | MessageLocator`) rather than stringly-typed anchors.

**Example:**
```python
# core/ports.py
class CellLocator(BaseModel):    kind="cell";    workbook:str; sheet:str; ref:str   # "C14"
class SlideLocator(BaseModel):   kind="slide";   deck:str; slide:int; shape:str
Locator = CellLocator | SlideLocator | MessageLocator
class RawExtraction(BaseModel):  value: str; locator: Locator; context: str | None

# distill/formats/base.py
def normalize(raws: list[RawExtraction]) -> Distillation:
    claims = [Claim(text=r.value, trace=Trace.from_locator(r.locator)) for r in raws]
    return Distillation(claims=claims, missing=collect_unanchored(raws))
```
*Note from research:* `python-pptx`/`openpyxl` give you the structure and cell/shape addresses, but
**neither provides provenance/trace tracking out of the box** — the locator layer above is yours to
build. That is a feature, not a gap: it is precisely the trust-layer-as-product.

### Pattern 5: Content-model SSG (Site / Collection / Page) for multi-surface render

**What:** Don't template pages ad-hoc. Model the site as **Site → Collections → Pages** (the
render-engine pattern). A `Collection` is a surface type (all Reports, all Episodes); a `Page` is one
instance with a stable per-surface ID (`R-001`, `EP01`). The Site object owns cross-links, the
Library status-board (group Pages by gate state into columns), and nav generation. Templates are
Jinja2 over this model; IDs come from the model, **never from list position** (this is the fix for
the Rev2 numbering collision).

**When to use:** For the Rev2 renderer. It directly solves the brief's four asks: real Home vs
Library split, per-surface IDs, cross-linking, and traceable source links (a Trace's locator renders
to a real `<a href>` into the repo/file).

**Trade-offs:** More upfront structure than "loop over a list and emit HTML." Worth it because every
Rev2 bug listed (numbering collisions, missing nav, no cross-links) is a symptom of having no content
model. Keep it no-JS: the status-board is CSS columns, not a JS kanban.

**Example:**
```python
# render/site.py
class Page(BaseModel):    surface_id: str; gate: GateState; surface: Surface; links: list[str]
class Collection(BaseModel): kind: SurfaceKind; pages: list[Page]
class Site(BaseModel):
    collections: list[Collection]
    def library_board(self) -> dict[GateState, list[Page]]:   # columns by gate state
        ...
    def build(self, out_dir: Path) -> None:                   # Jinja2 render, tokenized CSS, no JS
        ...
```

---

## Data Flow

### Primary flow: source → published surface

```
[raw Sources: .pptx / .xlsx / email / hand-authored session]
      │
      ▼   pipeline.distill(sources)  — resolves backend by name via registry
[DistillPort backend]  (manual | formats | ai)
      │      formats: extract → RawExtraction(+Locator) → normalize → Claim(+Trace)
      ▼
[Distillation]  = claims[] (each Trace-anchored) + missing[] (unsubstantiated)
      │
      ▼   ReviewGate:  Draft → InReview(missing[] shown to human) → Published
[Published content]    (NO path bypasses the gate; merge of git PR = publish)
      │
      ▼   surfaces: one Distillation fans out to many SurfaceModels (presets)
[Surface instances: report / article / newsletter / show]
      │
      ▼   Renderer (Site/Collection/Page → Jinja2 → tokenized no-JS HTML)
[Static site: Home + Library status-board + cross-linked surface pages with source links]
```

### Key Data Flows

1. **Backend-agnostic distill:** the pipeline calls `DistillPort.distill()` and receives a
   `Distillation` — it cannot tell (and must not care) whether a human, a format adapter, or an LLM
   produced it. This is what makes AI swappable and optional.
2. **Provenance flow:** a `Locator` created at extraction time rides through `Trace` all the way to a
   rendered `<a href>`. The chain `cell C14 → Claim → Trace → published link` is the auditability
   guarantee, end to end.
3. **Fan-out (one-to-many):** a single reviewed `Distillation` produces multiple `Surface` instances
   via presets. Surfaces are config, not subclasses — so adding a surface type is registering a
   preset, not writing a renderer.
4. **Gate is a hard wall:** `missing[]` always reaches a human before publish; there is no auto-publish
   edge in the state machine. Encode this so it's a compile/test-checkable invariant, not a convention.

---

## Build Order (dependency-driven)

This is the load-bearing section for the roadmap. Components are listed so each depends only on
earlier ones.

1. **Core types + ports first** (`core/models.py`, `core/ports.py`). Nothing compiles without
   `Source/Claim/Trace/Distillation/Surface` and the `DistillPort` Protocol. *Blocks everything.*
   Includes building the real spine that PROJECT.md describes (it isn't in code yet).
2. **Review gate + pipeline skeleton** (`core/gate.py`, `core/pipeline.py`, `core/registry.py`).
   The state machine and the backend-agnostic orchestration. Depends on (1).
3. **Manual backend + capture** (`distill/manual.py`). The first concrete `DistillPort`; proves the
   socket with zero AI and serves the primary token-constrained user. Depends on (1),(2).
4. **Optional-AI boundary refactor** (move langchain to `[ai]` extra; `distill/ai.py` with lazy
   import). Can run in parallel with (3); both are independent backends behind the same port. This is
   small but should land early so the "deterministic spine ships without AI" property is true from the
   start, not retrofitted.
5. **Format adapters** (`distill/formats/`): `base.py` normalizer + `RawExtraction`/`Locator` first,
   then one extractor at a time — **Email (stdlib, no extra) → Excel → PPTX → Power BI** in roughly
   ascending complexity. Depends on (1),(2); reuses the normalizer for all formats.
6. **Surfaces presets** (`surfaces/`). Depends on (1); needed before render is meaningful.
7. **Rev2 renderer** (`render/`: Site/Collection/Page model → templates → tokens). Depends on (1) and
   (6) for content, but the *template/IA redesign* (Home spec, Library board, IDs, cross-links) can be
   prototyped against fixture data in parallel with 3–5, since it only depends on the type shapes, not
   on real backends. **This is why the Rev2 track is "partially separate."**
8. **Persistence** (`persist/`) last and isolated — the pipeline must work file-in/file-out before a
   DB is introduced, to protect the import-light core.

**Critical path:** 1 → 2 → 3 (a usable manual end-to-end pipeline) and 1 → 6 → 7 (a usable site).
4 and 5 widen the funnel of inputs; 8 is deferrable. The two tracks (distill, render) meet only at
the `Surface`/content-model boundary, so they can be staffed in parallel after (1).

---

## Scaling Considerations

This is a self-hosted, batch, static-output framework — "scale" is about **corpus size and number of
surfaces/operators**, not concurrent web traffic.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single operator / one work codebase | File-in/file-out, build to static HTML. No DB needed. This is the immediate target. |
| Team / many Reports & sources | Introduce `persist/` (SQLModel) for indexing/querying Claims; incremental rebuilds in the renderer (only re-render changed Pages). |
| Org / many operators & forks with custom backends | Entry-point plugin ecosystem matters; pin a stable `DistillPort` / `RendererPort` contract version so third-party backends don't break on upgrades. |

### Scaling Priorities

1. **First bottleneck: full-site rebuild time** as the Library grows. Fix with incremental build
   keyed on content hashes in the Site model — *not* by adding a server.
2. **Second bottleneck: AI-backend cost/latency** on large messy corpora. Mitigate by design: the
   deterministic format adapters handle the common case; the AI backend only touches the "messy
   residue," so token spend scales with messiness, not corpus size.

---

## Anti-Patterns

### Anti-Pattern 1: "The distill step is the AI step"

**What people do:** Bake an LLM call into the pipeline as *the* way claims are produced; manual/format
paths become awkward special-cases bolted on later.
**Why it's wrong:** It inverts the project thesis. AI becomes load-bearing authority; the no-AI mode
becomes a degraded afterthought; auditability erodes because the LLM is in the critical path.
**Do this instead:** Distill is a *port* with three peer backends. AI is one adapter behind a lazy
import. The pipeline never imports an AI library.

### Anti-Pattern 2: Heavy imports in `core`

**What people do:** Import `langchain`, `python-pptx`, `openpyxl`, or even `sqlmodel` at the top of
domain modules "for convenience."
**Why it's wrong:** It makes `pip install newsletters` drag in the entire ML/office stack and makes
the "runs with zero AI deps" promise structurally false — one transitive import defeats it.
**Do this instead:** `core` imports only `pydantic` + stdlib. All third-party libs live in adapter
modules, gated by extras and (for AI) lazy imports.

### Anti-Pattern 3: IDs and links derived from list position

**What people do:** Number Reports/Episodes by their index in a loop; link by array offset.
**Why it's wrong:** This is the exact Rev2 bug — reordering or inserting content silently breaks every
ID and cross-link. Provenance links rot.
**Do this instead:** Stable surface IDs live on the `Page`/`Surface` model (`R-001`, `EP01`, slug);
the renderer reads them. Cross-links resolve through the Site content model, not positions.

### Anti-Pattern 4: Editorializing extractors

**What people do:** Let an extractor (or the AI backend) summarize, rank, or emphasize during distill.
**Why it's wrong:** It breaks auditability — a published claim no longer maps faithfully to its source
locator; emphasis is smuggled in without a human deciding it.
**Do this instead:** Extract + trace only. Emphasis/narrative is the human's job at the gate (or a
configured corpus later). Enforce the faithful rule in the *single* normalizer, where it's testable.

### Anti-Pattern 5: A JS kanban for the Library board

**What people do:** Reach for a JS framework to build the status-board / live editor.
**Why it's wrong:** Violates the no-JS, WCAG-AA, no-external-calls constraints.
**Do this instead:** CSS-columns grouped by gate state, server-rendered at build time. Any
"live editor/preview" is a static HTML artifact, not a runtime app.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| LLM provider (Anthropic etc.) | Behind `AIBackend` / `DistillPort`, lazy-imported, optional extra | Provider-agnostic; the *only* external content call, and it's opt-in. No telemetry. |
| Office files (PPTX/XLSX) | Per-format extractor adapter, each its own extra | `python-pptx`, `openpyxl`. Deterministic, offline. Build locator anchors yourself. |
| Email | stdlib `email`, no extra | Parse headers/message-id as locators. |
| Power BI | Read *exported* tables (CSV/JSON), not a live API call | Keeps "no external calls on content" intact; export is an offline file. |
| GitHub (review/publish) | Review = PR, merge = publish | The gate's "Published" transition maps to a merge; no in-app auth/telemetry. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `core` ↔ `distill/*` | `DistillPort` Protocol + registry/entry points | Core depends on the Protocol only; adapters depend on core types. One-directional. |
| `distill/formats` ↔ extractors | `RawExtraction` + `Locator` typed union → shared normalizer | One trust rule, one place. Adding a format = one extractor + a locator variant. |
| `core` ↔ `render/` | `RendererPort` over the Surface/content model | Rev2 redesign is internal to `render/`; doesn't touch core. Enables parallel tracks. |
| `core` ↔ `persist/` | Optional repository interface | Quarantined so types stay import-light; pipeline works file-in/file-out without it. |

---

## Sources

- [Ports and Adapters (Hexagonal) Pattern](https://hemanthhari2000.medium.com/the-ports-and-adapters-pattern-unraveling-the-mystery-2efbf678ab9b) — port/adapter framing for the distill socket (MEDIUM/community).
- [Creating and discovering plugins — Python Packaging User Guide](https://packaging.python.org/guides/creating-and-discovering-plugins/) — entry-point plugin discovery (HIGH/official).
- [stevedore: Dynamic Code Patterns (OpenStack)](https://docs.openstack.org/stevedore/latest/user/essays/pycon2013.html) — "use entry points even for built-ins to eliminate special cases" (HIGH/curated).
- [Implementing a Plugin Architecture in Python — Siv Scripts](https://alysivji.com/simple-plugin-system.html) — registry pattern (MEDIUM/community).
- [Optional imports for optional dependencies — discuss.python.org](https://discuss.python.org/t/optional-imports-for-optional-dependencies/104760) and [PEP 810 – Explicit lazy imports](https://peps.python.org/pep-0810/) — optional/lazy dependency boundary idiom (HIGH/official-adjacent).
- [About Open XML Packaging — python-pptx docs](https://python-pptx.readthedocs.io/en/latest/dev/resources/about_packaging.html) — structure/addressing for locators; confirms no built-in provenance (HIGH/official).
- [Render Engine (Site/Collection/Page)](https://github.com/render-engine) and [Static Site Generators — Full Stack Python](https://www.fullstackpython.com/static-site-generator.html) — content-model SSG layering for the Rev2 renderer (MEDIUM/curated).
- Internal: `/home/user/newsletters/.planning/PROJECT.md`, `/home/user/newsletters/.planning/brief.md`, `/home/user/newsletters/src/newsletters/models.py`, `/home/user/newsletters/pyproject.toml` (HIGH/ground truth for current state).

---
*Architecture research for: semantic information distillation framework (Python, trust-layer-as-product)*
*Researched: 2026-06-14*
