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

### The content model: `Site → Collection → Page` (the durable index)

The semantic model above describes one artifact at a time. The **content model** is the index
over all of them — the layer the Library and any cross-surface navigation read from. It *wraps*
Surfaces; it never mutates them.

- **Site** — the whole library: an ordered list of `Collection`s.
- **Collection** — a grouping of Pages **by surface type** (Reports, Articles, Newsletters,
  Shows, Learning), ordered by `template.distance` (show 0, report 1, article 2, newsletter 3).
  This is the natural board grouping. *(Grouping by gate/review state — a kanban board — is a
  later view, not this model.)*
- **Page** — one published Surface within a Collection. It carries the **stable identity**
  (`slug`, `ref`, and for cadenced surfaces `issue`/`date`) plus display metadata (`title`,
  `kind`, `gate`, `signal_color`, `href`) and points at its `Surface`. `href == f"{slug}.html"`.

**Order is data, never the source of identity.** A Page's `slug`/`ref` are a pure function of
its content and the ledger (below) — reordering or inserting surfaces never renumbers an
existing one or rots a link. This is the position-independence guarantee (it replaced an earlier
positional `enumerate` index that renumbered on every reorder).

**The ledger is the source of truth for refs.** An append-only, human-readable file
(`content/rev1/ids.json`, `slug -> {ref, type, issue, date}`, written sorted with a trailing
newline for byte-stable diffs) records each surface's `ref` **once**. Existing entries are
immutable; a new surface gets the next free per-type ordinal (`max(ordinal)+1`, not `count+1`,
so deletions never reuse a retired number). Same content → same ledger (deterministic). The
ID-string convention (`R-NNN` / `EPNN` / `A-NNN` / cadenced newsletters / `L-NNN`) is documented
in `docs/surfaces.md`.

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

---

## 7. Rev1 — as implemented (the model decisions)

Rev1 (in `src/newsletters/`) refines §1–§3 with decisions reasoned out with the co-authors.
The Reports in `content/rev1/` are the working record of *why*; this section is the *what*.

- **Two layers, not five peers.** *Truth* (`Source → Claim(+Trace) → Distillation`) is
  distinct from *Surface*. `report / article / newsletter / show` are **not four classes** —
  they are presets over **one** parameterized `SurfaceTemplate` (`templates.py`). Cadence,
  personalization, signal color, audience scope, and review policy are **typed config**;
  only prose is templated. Operators register their own templates — forkability without a
  core change.
- **The review gate is per-template.** `ReviewPolicy` is carried by the template:
  the **Report** self-approves (light PR); the **Article** requires a **peer** (approver ≠
  author). Enforced at `publish()` — still no auto-publish path.
- **Surfaces compose from typed content `blocks`** (prose, claims, kpi, quote, chapters,
  items, prompt, fanout, rationale). The blocks *are* the slots.
- **Problem-solving agents are external.** Newsletters owns capture + trust + publish, never
  the agent. `capture.py` turns a finished `WorkSession` (a bundle of `Source`s) into a
  traced Draft Report — deterministically, post-session, tool-agnostic. `Provenance` +
  `Lineage` track the process on every surface. (Push-integration is the operator add-on.)
- **Two human-gated promotions** form the grammar: `Claim → KPI` (measurable, bridges the
  OKR domain in `models.py`) and `Report → Article` (durable, peer-reviewed).
- **The renderer** (`render.py`) emits token-faithful standalone HTML (light + dark, the
  signal colors, the gate badge) — `newsletters build` writes the Library to
  `content/rev1/site/`. The agentic distill (`synthesize`) remains an external/Phase-4 stub.

---

## 8. The work-surface install / dogfood flow (Phase 11 — as implemented)

Phase 11 makes the product run on a **real codebase**, not just the Rev1 sample. The same
trust spine — content-addressed claims, the review gate, provenance + lineage on every
surface — applies to a hand-authored Report about how *this* build was done. The flow an
operator runs (`src/newsletters/worksurface.py`):

1. **Install.** `pip install newsletters` — the bare install is light and **AI-free** (the AI
   backend lives behind the `[ai]` extra; the work flow needs none of it).
2. **Point the read-only ingest at the code.** `worksurface.capture_files(paths, root=...)`
   reads a *curated list* of local files **READ-ONLY** (`Path.read_text` only — never a write
   to the scanned tree, **no network call**) into content-addressed `Source` records. Each
   `Source.id` is the POSIX relpath, so a claim citing it links back to the working repo file
   for free. Data stays local; nothing is transmitted (consistent with the §5 MCP/local-data
   stance and the §6 "no external calls on content" NFR).
3. **Hand-author a Report.** `worksurface.build_work_report(...)` lifts hand-written
   `Decision`s into a Draft Report via the zero-AI manual backend (`capture.build_report`).
   Each claim **content-addresses** to a verbatim span of its cited file (`Trace.from_source`);
   any claim that does *not* verbatim-locate is routed to `Surface.missing[]` — **faithful, not
   fabricated**. No auto-publish: the work-report stays Draft until a human publishes it.
4. **Publish / render the Library.** `worksurface.build_work_site(out="content/work/site")`
   renders the corpus to standalone HTML, reusing the Phase 9/10 devices: a claim→repo-file
   link, the verbatim trace span, the honesty panel (the `missing[]` gaps), and the masthead's
   **provenance** (`captured via`) + **lineage** (`derived from` the ingested files, and the
   per-audience fan-out it `produced`). The work output **self-hosts its fonts** (see
   `design-system.md`) so the Library makes **zero external call**, just like Rev1.
5. **Gate it through the SAME trust gate.** `newsletters check --corpus work` runs the
   corpus-agnostic `review.review_blockers` over the work corpus's PUBLISHED surfaces:
   **exit 0** when clean, **nonzero** on any STALE / un-entailed / open-`missing[]` blocker.
   The selector routes the *builder*, never forks the gate — the work corpus passes the
   identical merge-block contract as Rev1.

**The `--corpus {rev1|work}` selector.** Both `newsletters build` and `newsletters check`
accept `--corpus` (default `rev1`, so existing behavior is unchanged):

- `build --corpus rev1` → `content/rev1/site` (the sample); `build --corpus work` →
  `content/work/site` (the real corpus).
- `check --corpus rev1` gates the sample; `check --corpus work` gates the real corpus — both
  through the **same** `review_blockers`. The work corpus keeps its **own** append-only ledger
  (`content/work/ids.json`), so the sample/real boundary is preserved at the ledger layer.
