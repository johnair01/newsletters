# Stack Research

**Domain:** Deterministic format-extraction adapters + optional-LLM boundary + standalone HTML rendering (Python framework, Newsletters Rev2)
**Researched:** 2026-06-14
**Confidence:** HIGH (versions/licenses verified against PyPI JSON; provider-comparison MEDIUM)

> Scope note: this researches only the **new** Rev2 stack — (a) the AI-optional packaging boundary, (b) format adapters (PPTX / XLSX / Power BI / Email), (c) the static-site renderer. The existing Rev1 spine (typed models, capture, render) is not re-researched.
>
> Guiding constraints from PROJECT.md: **MIT / self-hostable, no telemetry, no external calls on content, deterministic-first, low-token, faithful-not-suggestive, Python 3.12, no-JS render.** Every recommendation below is filtered through these.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **python-pptx** | `1.0.2` | PPTX adapter — extract slides, shapes, text frames, tables, speaker notes into typed claims+traces | The canonical, only-serious OSS PowerPoint reader. **MIT.** Pure-Python, zero native deps, fully deterministic, no network. Gives a faithful object tree (slide → shape → paragraph/run, plus `notes_slide`) that maps cleanly to `Claim(+Trace)` with slide/shape coordinates as the trace anchor. |
| **openpyxl** | `3.1.5` | XLSX adapter — read cell values, formulas, sheet/cell coordinates into traced claims | The standard pure-Python xlsx reader. **MIT.** Deterministic, streaming `read_only=True` for large books. Trace anchor = `sheet!cell` (e.g. `Q3 Budget!B14`). Read **both** `data_only=False` (formula) and the cached value so a claim can trace "value 1.2M, derived by `=SUM(...)`". |
| **stdlib `email`** | Python 3.12 stdlib | Email adapter for `.eml` / RFC 822 (MIME) — headers, parts, bodies | Zero dependencies, in the standard library, deterministic, no network. `email.parser.BytesParser` + `policy.default` gives a faithful message tree. This is the **default email path** — most "email" inputs can be exported to `.eml`. Trace anchor = `Message-ID` + part index. |
| **Jinja2** | `3.1.6` | Rev2 static-site renderer / templates (Home, Library status-board, surface pages) | Industry-standard templating. **BSD-3** (MIT-compatible). Renders fully standalone HTML with **no JS and no external calls**; `autoescape=True` enforces safe, token-faithful output. Pairs with the existing token/signal-color design system. |
| **pydantic-ai** | `1.107.0` | The single optional `distill()` LLM backend (one of three sockets: hand / OSS tool / **AI**) | **MIT**, built by the Pydantic team — same typed-model lineage as the existing models. Model-agnostic (Anthropic/OpenAI/Gemini/local) and gives **built-in typed/structured output** so an AI distillation returns a validated `Distillation`, not free text. Lives entirely behind an `[ai]` optional extra; the spine never imports it. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **MarkupSafe** | `3.0.x` | Autoescaping primitive under Jinja2 | Transitive dep of Jinja2; pin only if you build escaping helpers. MIT-compatible (BSD). |
| **olefile** | `0.47` | MIT-compatible OLE2/`.msg` primitive | Use when you must read Outlook `.msg` **inside the MIT core** without GPL contamination (see "What NOT to Use"). BSD-2. You parse the OLE streams yourself → more work, but license-clean. |
| **pbixray** | `0.11.1` | Binary `.pbix` extraction (tables, DAX measures, M/Power Query, schema, relationships) | Use **only** when the source is a binary `.pbix` and no PBIP/TMDL export exists. **MIT.** Prefer the TMDL text path (below) for faithfulness and low token cost. |
| **stdlib `csv` / `pathlib`** | stdlib | TMDL/PBIP folder walk + plain-text Power BI semantic model parse | Preferred Power BI path: PBIP projects store the model as **TMDL** — one human-readable `.tmdl` file per table/measure/relationship. Walk the `/definition` folder and parse text deterministically; trace anchor = `model/tables/<t>.tmdl#measure:<name>`. Zero extra deps, fully faithful, diffable. |
| **extract-msg** | `0.55.0` | High-level `.msg` parsing convenience | **GPL-3.0 — do NOT ship in the MIT core.** Acceptable only in a clearly-isolated, non-distributed dev/conversion script (e.g. an operator converts `.msg`→`.eml` locally, outside the package). See warnings. |
| **litellm** | `1.89.0` | Alternative provider-routing shim | Only if you want pure provider routing (100+ providers, cost/rate limiting) and will add `instructor` for structured output. Heavier than pydantic-ai for this use; MIT. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **pytest** | Adapter golden-file tests | Already in `[dev]`. Each adapter needs fixture files (a sample `.pptx`/`.xlsx`/`.eml`/`.tmdl`) with golden typed output — this is how "faithful, not suggestive" is enforced in CI. |
| **ruff** | Lint + format | Already configured (`line-length = 88`). Can replace black/isort to cut dev deps. |
| **mypy** | Type checking | Already configured for 3.12; critical since the whole value prop is typed/auditable output. |
| **pip-licenses** / `uv pip compile` | License audit gate | Add a CI check that fails on any non-MIT-compatible license entering the **core** dependency set (catches GPL creep from `.msg` tooling). |

## Installation

```bash
# Core spine — ZERO AI, deterministic-only (this is the default install)
pip install "newsletters"
#   -> pydantic, jinja2, (sqlmodel/typer already present)

# Format-adapter extras (still deterministic, no AI)
pip install "newsletters[adapters]"
#   -> python-pptx==1.0.2  openpyxl==3.1.5  olefile==0.47  pbixray==0.11.1
#   (email + tmdl adapters need no extra deps — stdlib only)

# Optional AI distill socket (the ONLY place LLM deps live)
pip install "newsletters[ai]"
#   -> pydantic-ai>=1.107
```

Proposed `pyproject.toml` shape (the packaging-boundary deliverable):

```toml
[project]
dependencies = ["pydantic>=2", "jinja2>=3.1.6", "typer", "sqlmodel"]  # NO langchain/langgraph/langsmith here

[project.optional-dependencies]
adapters = ["python-pptx==1.0.2", "openpyxl==3.1.5", "olefile==0.47", "pbixray==0.11.1"]
ai       = ["pydantic-ai>=1.107"]
dev      = ["pytest", "ruff", "mypy"]
```

> This directly satisfies the Active requirement *"move `langchain` to an optional extra; the spine runs with zero AI deps."* Note `langchain[anthropic]`, `langgraph`, `langsmith`, `langsmith` telemetry must all leave `dependencies` — `langsmith` in particular phones home, violating the no-telemetry constraint.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| python-pptx | Aspose.Slides / Spire.Presentation | Never for this project — commercial/proprietary, not MIT, often phone-home. Only if you needed render-to-image fidelity (you don't; you extract structure). |
| openpyxl | pandas `read_excel` | When you want tabular dataframes for analysis, not cell-level provenance. pandas loses cell coordinates and formulas, which **breaks traceability** — wrong for claim extraction. Adds numpy/pandas weight. |
| openpyxl | `python-calamine` | When you need pure-speed bulk reads of huge sheets and don't need to write or read formulas. Faster, but no formula access — keep openpyxl as default for faithful "value + how it was derived". |
| Power BI **TMDL/PBIP text** | pbixray (binary `.pbix`) | When the operator only has a binary `.pbix` and cannot re-export as a PBIP project. TMDL is preferred: deterministic, diffable, lowest token cost, no parsing of compressed VertiPaq. |
| stdlib `email` (.eml) | mailbox / `mail-parser` | `mailbox` for `.mbox` archives (multi-message). `mail-parser` only if you want convenience over stdlib — but it adds a dep for what stdlib already does faithfully. |
| pydantic-ai | litellm + instructor | When provider routing/cost-control across 100+ vendors matters more than a tight typed boundary. For a *single optional socket*, pydantic-ai is leaner and structurally typed. |
| pydantic-ai | langchain / langgraph | Effectively never — these are the deps being *removed*. Heavy, churny, opinionated orchestration that pulls the spine toward AI-as-authority and telemetry (langsmith). |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **langchain / langgraph / langsmith in core** | Violates "AI-optional spine" and "no telemetry" (langsmith phones home). Heavy, fast-churning APIs couple the trust layer to a single AI stack. | `pydantic-ai` behind an `[ai]` extra; deterministic adapters in `[adapters]`. |
| **extract-msg in the distributed core** | **GPL-3.0** — incompatible with the project's MIT license; shipping it would force the whole package to GPL. | `olefile` (BSD-2) for in-core `.msg`, **or** convert `.msg`→`.eml` in a separate operator-side script and feed the `.eml` to the stdlib adapter. |
| **pandas/numpy as a required dep for XLSX** | Loses cell coordinates + formulas (breaks provenance), adds large binary deps to a low-token framework. | `openpyxl` cell-level reads; keep pandas in the existing optional `[panel]` extra only. |
| **Aspose / Spire / GroupDocs (any format)** | Proprietary, non-MIT, license-fee, some call home. Violates self-hostable + MIT. | `python-pptx`, `openpyxl`, TMDL text, stdlib `email`. |
| **An LLM in the default/distill path by default** | Contradicts "AI is an accelerator, never an authority" and the token-constrained operator. | Make `distill()` a socket whose **default backend is deterministic** (format adapter or by-hand); AI only on the messy residue, opt-in. |
| **`data_only=True` without a freshness check** | openpyxl returns the value Excel last cached — `None` if the file was never opened in Excel after editing. Silent wrong/empty claims. | Read formula **and** cached value; surface "uncomputed formula" to `missing[]` rather than publishing a blank. Faithful, not suggestive. |
| **Sempy / Fabric REST for Power BI** | Microsoft-Fabric-only, requires cloud auth + external calls. Violates self-hostable / no-external-calls. | Local PBIP/TMDL text parse, or `pbixray` for binary files. |
| **`html.parser`-based ad-hoc HTML string building** | Hand-built HTML invites injection + breaks token-faithful escaping. | Jinja2 with `autoescape=True`. |

## Stack Patterns by Variant

**If the operator has Power BI as a modern PBIP project (recommended export):**
- Walk the `*.SemanticModel/definition/**.tmdl` text files with stdlib.
- Parse measures/columns/relationships deterministically; trace each claim to its `.tmdl` file + object name.
- Because: zero binary parsing, zero extra deps, fully diffable, lowest token cost, most faithful.

**If the operator only has a binary `.pbix`:**
- Use `pbixray==0.11.1` to extract DAX, M, tables, schema.
- Because: TMDL text is unavailable; pbixray is the MIT option that reads VertiPaq without Fabric.

**If the email source is Outlook `.msg` (not `.eml`):**
- Preferred: convert to `.eml` outside the package, then use the stdlib `email` adapter (license-clean, faithful).
- In-core fallback: `olefile` (BSD-2) to read the OLE2 streams directly.
- Because: avoids GPL-3.0 `extract-msg` contaminating the MIT distribution.

**If running fully offline / token-zero (the primary operator path):**
- Install `newsletters[adapters]` only; never install `[ai]`.
- `distill()` resolves to a deterministic adapter or by-hand backend; pipeline runs end-to-end with zero AI deps and no network.
- Because: this is the validated core thesis — the trust layer must hold with no AI present.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `python-pptx==1.0.2` | Python 3.8–3.12 | **No 3.13 classifier yet** (works in practice, but pin runtime to 3.12 per project constraint). Depends on `lxml`, `Pillow`, `XlsxWriter` (all MIT-compatible). |
| `openpyxl==3.1.5` | Python 3.8–3.12 | Pure-Python; `read_only`/`data_only` flags as documented. |
| `jinja2==3.1.6` | `MarkupSafe>=2.0` | 3.1.6 includes the 2025 security fixes; do not pin below 3.1.6. |
| `pydantic-ai>=1.107` | `pydantic>=2` | Shares Pydantic v2 with the existing typed models — no v1/v2 split risk. Keep isolated in `[ai]` extra. |
| `pbixray==0.11.1` | Python 3.9+ | MIT; pulls `pandas`/`numpy` transitively — another reason to keep it in `[adapters]`, never core. |
| `olefile==0.47` | Python 3.5–3.12 | BSD-2; tiny, no deps. |

## License Summary (gate: must be MIT-compatible)

| Library | License | Core-safe? |
|---------|---------|-----------|
| python-pptx | MIT | ✅ yes |
| openpyxl | MIT | ✅ yes |
| stdlib `email`/`csv` | PSF | ✅ yes |
| Jinja2 / MarkupSafe | BSD-3 / BSD | ✅ yes |
| pydantic-ai | MIT | ✅ yes (optional `[ai]`) |
| pbixray | MIT | ✅ yes (optional `[adapters]`) |
| olefile | BSD-2 | ✅ yes |
| litellm | MIT | ✅ yes |
| **extract-msg** | **GPL-3.0** | ❌ **no — never in distributed core** |
| Sempy / Aspose / Spire | Proprietary/MS-only | ❌ no |

## Sources

- PyPI JSON API (`pypi.org/pypi/<pkg>/json`) — verified current versions + licenses for python-pptx 1.0.2, openpyxl 3.1.5, jinja2 3.1.6, litellm 1.89.0, pydantic-ai 1.107.0, pbixray 0.11.1, olefile 0.47, extract-msg 0.55.0 — **HIGH**
- openpyxl docs (read_only / data_only / formula semantics) — **HIGH**
- Microsoft Learn + community (PBIP/TMDL text format, Sempy is Fabric-only) — **MEDIUM**
- Web comparison (litellm vs pydantic-ai structured output) — **MEDIUM**
- decalage.info / oletools (olefile BSD, extract-msg GPL-3.0) — **HIGH**

---
*Stack research for: format-extraction adapters + optional-LLM boundary + standalone HTML rendering*
*Researched: 2026-06-14*
