# Architecture — Newsletters

How the product is structured. The **typed semantic model** is the spine; everything else
hangs off it. This document recommends a stack — keep the models, the review gate, and the
design system whatever you choose.

---

## 1. The typed semantic model

Everything is a typed model so outputs stay consistent and auditable. Three core objects
carry the whole system:

- **Source** — `id`, `timestamp`, `context`, `transcript`, `embeddings`. A record of
  something that happened; embeddings power semantic search.
- **Distillation** — `claims[]`, `narrative`, `audience: Corpus`, `missing[]`. The agent's
  synthesis, with **every claim linked back to evidence** (a `Source` + locator). `missing[]`
  records what the agent could not substantiate — surfaced to the reviewer, never published silently.
- **Surface** — `kind`, `body`, `gate: Review`, `traces: Source[]`. The published artifact and
  the review state that gates it. `kind ∈ { show, newsletter, article, report }`.

Supporting types:

- **Corpus** — a reader's private profile: `role`, `owned[]` (services/areas), `read[]`
  (what they've seen), `weights`. **Local and encrypted.** Drives personalization; never leaves
  the operator's environment.
- **Claim** — `text`, `evidence: Trace[]`, `confidence`. The atom of auditability.
- **Trace** — a pointer from a claim to its `Source` and location within it.
- **Review** — the gate enum `Draft | InReview | Published` plus `reviewer`, `pr_url`, `notes[]`.

```
Source ──distill──▶ Distillation ──render(kind, Corpus)──▶ Surface
  ▲                      │                                    │
  └────── traces ────────┴──────── Review gate ───────────────┘
```

### Invariants (enforce in code, not just docs)
- A `Surface` may not reach `Published` without a `Review` whose state is `Published` and a
  recorded `reviewer`. **No auto-publish path exists.**
- Every `Claim` in a published `Distillation` has at least one `Trace`. Unsubstantiated
  material lives in `missing[]` and blocks nothing but is shown to the reviewer.
- A `Corpus` is never serialized into a `Surface` or a `Source`. Personalization reads it at
  render time; the output carries emphasis, not the corpus.

---

## 2. The package API (developer surface)

The home demo advertises a Python package. Preserve this ergonomics — it is the public API:

```python
# one conversation → record, article, letter, episode
from newsletters import synthesize, Corpus

out = synthesize(
    event="latency-regression-2026-06-12",
    sources=["apm", "traces", "logs", "rum"],
    audience=Corpus.load("maintainers"),
)
out.open_pull_request()   # human reviews before publish
```

- `synthesize(event, sources, audience) -> Distillation` — ingest + distill in one call.
- `Corpus.load(name) -> Corpus` — load a reader/audience profile from local config.
- `Distillation.render(kind) -> Surface` — produce a specific surface from the synthesis.
- `Surface.open_pull_request() / .gate` — drive the review loop; merging the PR publishes.
- Installable as `pip install newsletters`. Keep it importable as a library **and** runnable
  headless (for scheduled weekly sends).

---

## 3. The publish loop, in code

```
Ingest    sources → Source              (adapters per system; MCP-backed, see §5)
Distill   Source  → Distillation        (the agentic journalist; claims traced)
Review    Distillation → Surface(Draft) → PR   (human edits/approves)
Publish   merge → Surface(Published)     → fan-out to Show / Newsletter / Article / Library
```

- **Distill** is the one agent step. It calls an LLM with the structured `Source` + the target
  `Corpus` and must return claims with traces. Treat the model as swappable.
- **Review** is a real pull request against the content repo. The diff is human-readable
  surface content. Approval = merge.
- **Publish** is deterministic system work: render final surfaces, write to the Library, send
  the weekly per-reader letters.

---

## 4. Recommended tech stack

No codebase exists yet. This is a strong default; swap freely as long as the invariants hold.

| Layer | Recommendation | Why |
|---|---|---|
| **Core / agent** | **Python 3.12 + Pydantic v2** for the typed models, **FastAPI** for the service | Matches the advertised `pip install newsletters` API; Pydantic gives the typed/auditable guarantee for free. |
| **LLM orchestration** | Provider-agnostic client; one `distill()` boundary | Keep the model swappable; don't couple the data model to a vendor. |
| **Web surfaces** | **Next.js (App Router) + TypeScript + React** | Prototypes are React; SSR matches the "renders without JS" goal in the footer; good fit for content surfaces. |
| **Styling** | Plain CSS / CSS Modules driven by the design tokens in `design-system.md` | The aesthetic is flat editorial with `--radius: 0`; a utility framework would fight it. Port `tokens.css` directly. |
| **Content store** | Git-backed Markdown/MDX for surfaces + a small DB for indices/embeddings | "Review = a pull request" wants content in git; embeddings/search want a vector index. |
| **Personalization** | Render-time re-cut against a local `Corpus`; encrypted at rest | Spec requires corpora stay local + encrypted. |
| **Integrations** | **MCP servers**, one per source system | See §5. |

### Repository shape (suggested)
```
/core         # python package `newsletters` (models, synthesize, render, gate)
/mcp          # MCP servers per source system
/web          # Next.js app — the surfaces
/content      # git-backed published surfaces (the Library)
/docs         # this spec set, kept in sync
```

---

## 5. MCP servers — keeping data local

Deploy via modular **MCP servers** so private corpora and sources stay in the operator's
environment. Each source system (APM, traces, logs, RUM, work-order, wiki, …) is wrapped by an
MCP server that exposes read access to the distiller without the data leaving the perimeter.
The core never holds long-lived credentials to source systems directly — it talks to MCP
servers. Corpora are loaded locally and never transmitted.

---

## 6. Non-functional requirements

- **Auditable:** every published claim traces to evidence; the trace is inspectable from the
  surface.
- **Renders without JavaScript** where possible; **WCAG AA** (both stated in the V1 footer).
- **Self-hostable, MIT, no telemetry** baked into the product. No external calls on content.
- **Themeable:** full light + dark, driven entirely by tokens (see `design-system.md`).
- **Forkable:** surfaces are slot-marked templates; an operator repopulates with their specifics.
