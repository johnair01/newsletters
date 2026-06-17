# Phase 7: Power BI Adapter - Research

**Researched:** 2026-06-17
**Domain:** Power BI Project (PBIP) extraction — TMDL semantic-model text + PBIR/report JSON, feeding the shared faithful `normalize()`; binary `.pbix` fallback assessment (pbixray)
**Confidence:** HIGH (primary PBIP/TMDL path — Microsoft Learn authoritative docs + a fully-established in-repo adapter pattern); MEDIUM (pbixray assessment — PyPI/GitHub verified, but the recommendation is a judgement call)

## Summary

The modern, faithful, dependency-free Power BI path is **PBIP** (Power BI Project) — a folder of **plain text files**. The semantic model lives in **TMDL** (`*.tmdl`, a YAML-like indented text format) under `<name>.SemanticModel/definition/`; the report lives in **PBIR** JSON (`definition.pbir` + `definition/` tree of `report.json`, `pages/*/page.json`, `pages/*/visuals/*/visual.json`) under `<name>.Report/`. Both are publicly documented, human-readable, and carry exactly the artifacts this adapter must extract verbatim: table/column names + dataTypes + descriptions, **measure names + their DAX expression TEXT (a formula, never a value)**, relationships, hierarchies, page/visual titles, text boxes, and field references. This maps cleanly onto the existing Excel/PPTX adapter pattern: build one canonical transcript per `Source`, slice verbatim units, hand them in transcript order to the shared `normalize()`, route everything unreadable to `unextracted[]`, carry drops on `Source.extraction`, timestamp via `deterministic_timestamp` (EPOCH_ZERO — PBIP has no single intrinsic date).

**A STDLIB line/indent parser is fully sufficient for TMDL** and is the strong recommendation — no TMDL parser dependency is needed or warranted (assessed in Q-B; not flagged as essential). TMDL's grammar is regular at the line level: object headers (`type name`), `property: value` lines, and `=`-introduced default-property expressions, all disambiguated by single-tab indentation depth. We do **not** need to evaluate DAX or M — we extract the expression text verbatim, which is exactly what faithfulness requires.

**pbixray recommendation: DEFER (do not adopt).** pbixray is MIT, active, and ~258k downloads — but it pulls **pandas + numpy + apsw + kaitaistruct plus three single-maintainer Cython compression shims (`xpress8`, `xpress9`, `xmhuffman`)**, every one of which the legitimacy seam flags **SUS**. That transitive surface directly contradicts the minimal-core invariant and adds real supply-chain risk for a *fallback* path. Route binary `.pbix` to a clear whole-source `unextracted[]` disclosure ("export to PBIP/PBIR for faithful extraction") and ship the stdlib PBIP/TMDL path alone. This keeps the bare install, AI-isolation, and `lint-imports` green with zero new dependency.

**Primary recommendation:** Build a stdlib `powerbi` adapter that walks a PBIP folder (or a single dropped `.tmdl`/`.json`/`.pbip`), serializes a canonical multi-file transcript with a per-unit object-path prefix, extracts verbatim model/report text via the shared `normalize()`, detects row-cap/aggregation/data-absence signals into a precise `unextracted[]` taxonomy, and disposes binary `.pbix` as a single honest `unextracted[]` entry (pbixray DEFERRED).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **Primary path = PBIP/TMDL text, STDLIB-only (no new dep).** PBIP is a text/folder format: TMDL (`*.tmdl` — tables/columns/measures/relationships, all text) + report definition (JSON/`.pbir`). Parse with stdlib (text + `json`). The modern, faithful, dependency-free path (success-criterion-1).
2. **pbixray fallback for binary `.pbix` — research-gated, behind an optional `[powerbi]` extra IF adopted.** Decision rule: if pbixray is clean (permissive license, no telemetry, acceptable deps) → lazy `[powerbi]` extra (mirror `[excel]`/`[pptx]`); if heavy/risky/unmaintained → DEFER (route `.pbix` to a clear `unextracted[]`/error: "export to PBIP for faithful extraction") and ship the stdlib path alone. Either way bare/core install + AI-isolation + `lint-imports` stay green.
3. **Faithful extraction = model/report TEXT, never fabricated data.** Claims = verbatim text artifacts: table/column names + dataTypes + descriptions, **measure names + their DAX expressions (verbatim, never a computed value)**, relationships, hierarchies, report page/visual titles + text boxes + field refs. A DAX measure is a formula, not a number — extract the formula text; NEVER fabricate a value.
4. **Row-cap & aggregation limits → `unextracted[]` (success criterion 2, "fail loud").** Enumerate WHERE these manifest (Top-N/row filters, summarized fields, DirectQuery/row-limit, measures whose values aren't text-computable, data the text format structurally cannot contain). A clipped/aggregated export must be DISCLOSED, never presented as complete.
5. **Reuse shared `normalize()` + coverage carrier + deterministic_timestamp.** Adapter produces canonical transcript + verbatim units + `unextracted[]`; `normalize()` content-addresses; drops on `Source.extraction`; timestamp deterministic (PBIP has no single intrinsic date → likely `EPOCH_ZERO`). Register backend "powerbi" (or "pbip"); conform. Locator = `FreeLocator(text=...)`.
6. **Golden fixtures (ADAPT-06).** Author a small PBIP/TMDL fixture tree (text files — byte-reproducible): a TMDL model (table + columns + a measure with DAX), a relationship, a report page with a visual + a Top-N-filtered/summarized visual (→ row-cap/aggregation unextracted), and (if pbixray adopted) a tiny `.pbix` or its deferral path. Assert zero silent drops, verbatim + content-addressed claims, conformance, determinism, round-trip parity.

### Claude's Discretion
- The exact transcript prefix grammar, the per-unit object-path format, the `unextracted[]` reason strings, the precise fixture file set, and the backend name (`powerbi` vs `pbip`) are the adapter author's to set — within the locked decisions. Research recommends concrete values below.
- Whether to also detect TMSL (`model.bim`) input as a secondary text path (it is JSON; trivially in-scope for the same walker) — recommended as a small addition, see Q-A.

### Deferred Ideas (OUT OF SCOPE)
- Evaluating DAX/M expressions (we extract text, never compute).
- Extracting VertiPaq data rows from a `.pbix` (structurally out of the text format; pbixray deferred).
- Any binary `.pbix` parsing in the primary path.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADAPT-05 | Power BI adapter: extract PBIP/TMDL text into `Claim(+Trace)`, with a (gated) `.pbix` fallback; report row-cap/aggregation limits to `unextracted[]`. | Q-A (PBIP layout to walk), Q-B (TMDL stdlib grammar), Q-C (PBIR report text), Q-D (row-cap/aggregation taxonomy), Q-E (pbixray DEFER + `.pbix` disposition), Q-F (transcript/locator/timestamp). |
| ADAPT-06 | Golden tests proving zero silent drops, verbatim + content-addressed claims, conformance, determinism, round-trip parity. | Q-G (hand-authored PBIP/TMDL fixture tree — byte-reproducible plain text — and the assertions to mirror from `test_pptx_golden.py`/`test_excel_golden.py`). |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Walk a PBIP folder / dropped file → bytes-or-text | Adapter (`adapters/powerbi_adapter.py`) | — | Format-specific raw extraction; mirrors Excel/PPTX `parse(raw, path)`. |
| TMDL line/indent parse → verbatim units | Adapter (stdlib helper, e.g. `_tmdl.py`) | — | Pure text; no third-party dep. |
| PBIR/report JSON traversal → verbatim units | Adapter (stdlib `json`) | — | `json` is stdlib; deterministic key walk. |
| Faithful-locate + content-address | `adapters/normalize.py` (shared) | — | The ONE faithfulness gate; adapter never hand-mints hashes. |
| Coverage honesty / `unextracted[]` | `distill/coverage.py` + `_coverage_codec.py` | adapter decides drops | Drops travel on `Source.extraction`; `Coverage` validator forbids complete-with-drops. |
| Deterministic timestamp | `adapters/_timestamps.py` (shared) | — | PBIP has no single intrinsic date → `EPOCH_ZERO`. |
| Binary `.pbix` disposition | Adapter (whole-source `unextracted[]`) | (pbixray DEFERRED) | Minimal-core: no heavy/SUS transitive deps for a fallback. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `pathlib` | (stdlib) | Walk the PBIP folder deterministically (sorted). | Already used across the repo; zero dep. |
| Python stdlib `json` | (stdlib) | Parse PBIR/report JSON (`definition.pbir`, `report.json`, `page.json`, `visual.json`) and TMSL `model.bim`. | Deterministic, stdlib; mirrors Excel's `xml.etree` use of stdlib parsers. |
| Python stdlib `str`/regex (`re`) | (stdlib) | Line/indent TMDL parse + transcript record-boundary recovery (mirror `_RECORD_PREFIX`). | TMDL is line-regular; no parser dep needed (Q-B). |
| `newsletters.adapters.normalize` | (in-repo) | The shared faithful-locate + content-address gate. | ADAPT-01; the ONE faithfulness rule. |
| `newsletters.adapters._coverage_codec` | (in-repo) | Carry `unextracted[]` on `Source.extraction`. | R1 round-trip-parity precedent. |
| `newsletters.adapters._timestamps` | (in-repo) | `deterministic_timestamp(None) → EPOCH_ZERO`. | Determinism invariant. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none) | — | — | The primary path needs NO new third-party dependency. This is the headline finding. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib TMDL line-parser | a dedicated TMDL parser dep | **REJECTED.** No mature, permissive, lightweight Python TMDL parser exists; the official `TmdlSerializer` is .NET-only (`Microsoft.AnalysisServices.Tabular`). A dep would add risk for a format whose line grammar is trivially stdlib-parseable. Not essential → not flagged. (Q-B) |
| stdlib `.pbix` deferral | `pbixray` behind `[powerbi]` | **DEFER pbixray** (Q-E): pulls pandas/numpy/apsw/kaitaistruct + 3 single-maintainer SUS Cython shims. Heavy + supply-chain risk for a fallback. |
| ignore TMSL | also accept `model.bim` (TMSL JSON) | Low-cost: TMSL is JSON; the same `json` walk extracts table/column/measure text. Recommended as a secondary text path (Q-A discretion). |

**Installation:**
```bash
# Primary path: NO install needed — stdlib only.
# pbixray is DEFERRED (not added). If a future phase reverses this:
#   pip install '.[powerbi]'   # would pull pandas, numpy, apsw, kaitaistruct, xpress8/9, xmhuffman
```

**Version verification:** Primary path uses only the Python standard library (no version to pin). pbixray metadata verified below (Package Legitimacy Audit) but DEFERRED, so no install line ships.

## Package Legitimacy Audit

> Primary path installs NO external packages — the audit below covers ONLY the assessed-and-DEFERRED `.pbix` fallback (pbixray and its transitive shims). Because the recommendation is DEFER, none of these are added to `pyproject.toml`.

| Package | Registry | Age / Last release | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|--------------------|-----------|-------------|---------|-------------|
| `pbixray` [ASSUMED→VERIFIED via PyPI] | PyPI 0.11.1 | last release 2026-06-10; 161 commits, active | ~258.5k total (pepy.tech) | github.com/Hugoberry/pbixray | SUS (`too-new`, `unknown-downloads`) | **DEFERRED — not installed** |
| `pandas` | PyPI | mature | very high | github.com/pandas-dev/pandas | (heavy) | Pulled-by-pbixray → DEFERRED |
| `numpy` | PyPI | mature | very high | github.com/numpy/numpy | (heavy) | Pulled-by-pbixray → DEFERRED |
| `apsw` | PyPI | mature (rogerbinns) | moderate | github.com/rogerbinns/apsw | SUS (`too-new`,`unknown-downloads`) | Pulled-by-pbixray → DEFERRED |
| `kaitaistruct` | PyPI | mature | moderate | kaitai.io | SUS (`unknown-downloads`) | Pulled-by-pbixray → DEFERRED |
| `xpress8` | PyPI | new (2026-05-11) | unknown | github.com/Hugoberry/xpress8-python | SUS (`unknown-downloads`) | **single-maintainer Cython shim** → DEFERRED |
| `xpress9` | PyPI | new (2025-11-30) | unknown | github.com/Hugoberry/xpress9-python | SUS (`unknown-downloads`) | **single-maintainer Cython shim** → DEFERRED |
| `xmhuffman` | PyPI | new (2026-05-15) | unknown | github.com/Hugoberry/xmhuffman-cython | SUS (`unknown-downloads`) | **single-maintainer Cython shim** → DEFERRED |

**Packages removed due to [SLOP] verdict:** none (no hallucinated packages; all exist).
**Packages flagged as suspicious [SUS]:** pbixray + apsw + kaitaistruct + xpress8 + xpress9 + xmhuffman. The decisive concern is the **three single-maintainer C-extension compression shims** (xpress8/9, xmhuffman) authored by the same person as pbixray — each a SUS `unknown-downloads` C build dependency. For a *fallback* path, that supply-chain + minimal-core cost is not justified.

> Note on the verdicts: `unknown-downloads` is a known PyPI-API false-positive (it also flagged the already-approved `python-pptx`). For pbixray *itself*, the real signal is benign (MIT, active, ~258k downloads). The DEFER decision rests on the **transitive dependency weight + the obscure C-extension shims**, not on pbixray's own legitimacy. If a future phase needs `.pbix`, re-open this with a `checkpoint:human-verify` on the three shim packages.

## Architecture Patterns

### System Architecture Diagram

```
  PBIP folder  ──┐
  (or a dropped  │   parse(raw|path, path)
   .tmdl/.json/  │        │
   .pbip/.pbix)  │        ▼
                 │   ┌─────────────────────────────────────────────┐
                 └──▶│ PowerBIAdapter.parse                          │
                     │   1. classify input (folder / .tmdl / .json /│
                     │      .pbip / .pbir / .bim / .pbix)            │
                     │   2. BINARY .pbix ──▶ whole-source            │
                     │      unextracted[] ("export to PBIP")         │
                     │   3. TMDL files ──▶ _tmdl line/indent parse ──┼──▶ units (verbatim)
                     │   4. PBIR/report JSON ──▶ json walk ──────────┼──▶ units (verbatim)
                     │   5. detect row-cap/aggregation/data-absence ─┼──▶ unextracted[]
                     │   6. build canonical transcript (prefixed)    │
                     │   7. timestamp = EPOCH_ZERO (no intrinsic)    │
                     │   8. source.extraction = encode_coverage(drops)
                     └───────────────┬─────────────────────────────┘
                                     │  (Source, units[in transcript order], drops)
                                     ▼
                            normalize(source, units)  ── shared faithful gate
                                     │  locatable → Claim(+Trace)  | not → unextracted[]
                                     ▼
                     PowerBIAdapter.distill ──▶ Coverage(complete = drops==0)
                                     ▼
                            DistillationResult(backend="powerbi")
```

### Recommended Project Structure
```
src/newsletters/adapters/
├── powerbi_adapter.py   # PowerBIAdapter: parse(raw,path)+distill(sources); transcript+units+drops
├── _tmdl.py             # stdlib TMDL line/indent parser → ordered verbatim units + object paths
└── (reuse) normalize.py, _coverage_codec.py, _timestamps.py
tests/
├── test_powerbi_adapter.py     # unit: TMDL/PBIR parse forks, row-cap detection, .pbix deferral
├── test_powerbi_golden.py      # golden corpus end-to-end (mirror test_pptx_golden.py)
└── fixtures/powerbi/
    ├── _author_fixtures.py     # writes the byte-reproducible PBIP tree (plain text)
    └── <the PBIP fixture tree> # see Q-G
```

### Pattern 1: The established adapter contract (mirror Excel/PPTX exactly)
**What:** `parse(raw, path) -> (Source, units, drops)` builds a canonical transcript whose every emitted unit is a verbatim substring; `distill(sources)` re-derives units from `source.transcript` and recovers drops from `source.extraction`, then calls `normalize()`. Coverage is `complete=(len(merged_unextracted)==0)`.
**When to use:** Always — this is the locked ADAPT pattern.
**Example:** (from `src/newsletters/adapters/pptx_adapter.py`, the closest analog — multi-object serialization with a structural per-record prefix)
```python
# Source: src/newsletters/adapters/pptx_adapter.py:225-252 (_serialize) — the prefix/units idiom
lines.append(f"{loc}{SEP}{text}\n")   # transcript line: PREFIX + SEP + verbatim value
units.append(text)                    # SAME string → guaranteed substring of transcript
# distill(): units re-derived via an anchored _RECORD_PREFIX regex (NOT split on \n/\t,
# because values may contain them verbatim — faithfulness). See pptx_adapter.py:387-435.
```

### Pattern 2: TMDL stdlib line/indent parse (Q-B)
**What:** A measure/column/table is a header line (`type name`) at indent depth *d*; its properties are `property: value` lines at depth *d+1*; its default-property DAX/M expression follows `=` (same line, or multi-line at depth *d+2*, or a ```` ``` ```` verbatim block). Extract the verbatim text for each artifact; the object path (`Model/Table[Sales]/Measure[Sales Amount]`) becomes the transcript prefix.
**When to use:** Every `*.tmdl` file.
**Example:** (verbatim TMDL from Microsoft Learn — the grammar an indent parser walks)
```tmdl
// Source: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview
table Sales

    /// This is the Measure Description
    measure 'Sales Amount' = SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])
        formatString: $ #,##0

    measure 'Sales (ly)' =
            var ly = ...
            return ly
        formatString: $ #,##0

    column 'Net Price'
        dataType: int64
        summarizeBy: none
        sourceColumn: "Net Price"

relationship cdb6e6a9-c9d1-42b9-b9e0-484a1bc7e123
    fromColumn: Sales.'Product Key'
    toColumn: Product.'Product Key'
```
Faithful units to emit (verbatim substrings): the measure NAME (`Sales Amount`), the measure's **DAX expression text** (`SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])` — a formula, NOT a value), the description (`This is the Measure Description`), `formatString` value, the column name, its `dataType`/`summarizeBy` values, and the relationship `fromColumn`/`toColumn` endpoints.

### Anti-Patterns to Avoid
- **Computing or fabricating a measure value.** A DAX `measure` is a formula. Extract the expression TEXT; NEVER emit a number. (Hard rule "Faithful, not suggestive" — mirrors the Excel formula-cache crux.)
- **Splitting the transcript on `\n`/`\t`/`:` to recover units.** TMDL multi-line DAX and JSON values contain those characters verbatim. Recover via an anchored record-prefix regex (mirror `_RECORD_PREFIX` in `excel_adapter.py:407` / `pptx_adapter.py:394`).
- **Hand-minting a content hash in the adapter.** `normalize()` + `Trace.from_source` is the SOLE minting path (`normalize.py:108-114`).
- **Reading `.pbix` bytes / VertiPaq.** Out of scope; the binary path is a whole-source `unextracted[]` disclosure (pbixray DEFERRED).
- **Treating a clipped/aggregated export as complete.** Any Top-N/row-limit/summarized binding/DirectQuery signal MUST emit an `unextracted[]` entry so `Coverage.complete` is forced False.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Faithful-locate + content-address | a per-adapter hasher/locator | `normalize(source, units)` | ADAPT-01: the ONE faithfulness rule; forward-cursor handles duplicate units. |
| Carry drops across persistence | instance-memory keyed by source.id | `encode_coverage`/`decode_coverage` on `Source.extraction` | R1 round-trip parity; instance memory silently loses coverage. |
| Deterministic timestamp | `datetime.now()` fallback | `deterministic_timestamp(None) → EPOCH_ZERO` | Determinism invariant; PBIP has no single intrinsic date. |
| Coverage honesty gate | ad-hoc `complete` bool | `Coverage(complete=..., unextracted=...)` validator | Makes "complete with drops" unrepresentable (`coverage.py:54-67`). |
| TMDL parsing | a DAX/M evaluator or a .NET TMDLSerializer binding | stdlib line/indent parser | We extract text, not semantics; the .NET serializer is out-of-ecosystem. |
| `.pbix` binary parse | a hand-rolled VertiPaq/xpress decompressor | (DEFER — disclose to `unextracted[]`) | Heavy, error-prone; the faithful answer is "export to PBIP". |

**Key insight:** The faithfulness machinery already exists and is proven on three adapters. Phase 7 is *almost entirely* a new front-end (folder walk + TMDL line parse + JSON walk) bolted onto the shared `normalize()`/coverage/timestamp spine. The only genuinely new logic is (a) the TMDL line parser and (b) the row-cap/aggregation detection.

## Runtime State Inventory

> N/A — this is a GREENFIELD adapter (new files only: `powerbi_adapter.py`, `_tmdl.py`, tests, fixtures). It adds a registration line to `adapters/__init__.py` and (only if pbixray were adopted — it is NOT) an extra to `pyproject.toml`. No rename/refactor/migration; no stored data, live service config, OS-registered state, secrets, or build artifacts are touched. **None — verified by greenfield scope (Decision 1/6).**

## Per-Question Findings

### Q-A. PBIP folder structure (the layout an adapter walks)

A `.pbip` save produces (CITED: learn.microsoft.com/power-bi/developer/projects/projects-overview, projects-dataset, projects-report):

```
Project/
├── <name>.pbip                      # tiny JSON: pointer to the report artifact (entry point)
├── .gitignore
├── <name>.SemanticModel/
│   ├── definition.pbism             # REQUIRED — model definition + 'version' (TMSL vs TMDL)
│   ├── diagramLayout.json           # layout only (not faithful content)
│   ├── model.bim                    # TMSL JSON  (present ONLY if saved as TMSL)
│   └── definition/                  # present ONLY if saved as TMDL  ← PRIMARY TARGET
│       ├── database.tmdl
│       ├── model.tmdl
│       ├── relationships.tmdl
│       ├── expressions.tmdl
│       ├── dataSources.tmdl
│       ├── functions.tmdl           # DAX UDFs (newer)
│       ├── tables/<Table>.tmdl      # one file per table (columns/measures/hierarchies inline)
│       ├── roles/<role>.tmdl
│       ├── cultures/<culture>.tmdl
│       └── perspectives/<p>.tmdl
└── <name>.Report/
    ├── definition.pbir              # REQUIRED — report def props + datasetReference
    ├── report.json                  # PBIR-Legacy report body (present if saved as PBIR-Legacy)
    └── definition/                  # present ONLY if saved as PBIR (enhanced)  ← PRIMARY TARGET
        ├── report.json              # report-level metadata + report-level FILTERS
        ├── version.json
        ├── reportExtensions.json    # report-level measures
        ├── pages/pages.json
        ├── pages/<pageName>/page.json        # page name + page-level FILTERS
        └── pages/<pageName>/visuals/<visualName>/visual.json   # visual config + visual FILTERS
```

**Faithfully-extractable TEXT carriers:** `definition/*.tmdl` and `tables/*.tmdl` (model text); `<name>.Report/.../report.json`, `page.json`, `visual.json`, `reportExtensions.json` (report text). **Non-content / skip:** `.pbi/` (user-local, git-ignored — `localSettings.json`, `cache.abf`), `diagramLayout.json`, `semanticModelDiagramLayout.json`, `mobileState.json` (layout/appearance only). The walker should walk `<name>.SemanticModel/definition/**.tmdl` and `<name>.Report/definition/**.json` (or the legacy `model.bim` / `report.json`), **sorted** for determinism, and disclose any readable-but-not-extracted file class to `unextracted[]` (mirror Excel's chart/image disclosure).

**TMSL `model.bim` (secondary, recommended — discretion):** when the model is saved as TMSL, the model is one JSON file (`model.bim`) with `model.tables[].columns[]/measures[]/...`. The same `json` walk extracts the same artifacts (column `name`/`dataType`, measure `name`/`expression`). Low-cost to support; recommended so an older PBIP still extracts.

**Input shapes the adapter should accept:** (1) a PBIP folder root, (2) a `<name>.SemanticModel`/`<name>.Report` subfolder, (3) a single dropped `*.tmdl` / `*.json` / `*.bim` (extract just that), (4) a `.pbip`/`.pbir` pointer (resolve the relative `datasetReference.byPath`), (5) a binary `.pbix` → whole-source `unextracted[]` (Q-E). Because `parse(raw, path)` takes bytes today, the planner should decide whether to extend the entrypoint to accept a folder/path (recommended: add a `parse_path(path)` that reads the tree, keeping `parse(raw, path)` for single dropped files; both converge on the same serializer).

### Q-B. TMDL grammar — stdlib parse feasibility (CRUCIAL)

TMDL is "a grammar syntax similar to YAML… minimal delimiters… indentation to demark parent-child relationships" with a **default single-tab indentation rule** and **three indent levels** (CITED: learn.microsoft.com/analysis-services/tmdl/tmdl-overview):

1. **Object declaration** — `type name` (e.g. `table Sales`, `column Quantity`, `measure 'Sales Amount'`). Name is single-quoted iff it contains `. = : '` or whitespace; embedded `'` is doubled.
2. **Object properties** (depth d+1) — `property: value` (colon delimiter; value on same line, trimmed). Boolean shortcut: bare property name (e.g. `isHidden`) implies `true`.
3. **Default-property expression** (after `=`) — for `measure`/`calculated column`/`calculationItem`/etc. the default property is a **DAX expression**; for `partition`/`expression` it is **M**. Single-line on the header, or **multi-line indented one level deeper than properties**, or a ```` ``` ````-fenced verbatim block (read literally, indentation preserved).
4. **Descriptions** — `/// text` triple-slash lines immediately above the object declaration (multi-line allowed). No whitespace between the description block and the object token.
5. **`ref` lines** — `ref table X` etc. declare collection ordering (skip for extraction; they carry no content).
6. **Annotations / extended properties** — `annotation name = value` (Text default property).

**Object types to extract:** `table` (name + `/// description`), `column` (name + `dataType`, `summarizeBy`, `description`, `formatString`, `sortByColumn`), `measure` (name + **DAX `expression` text** + `description` + `formatString` + `displayFolder`), `hierarchy` (name + `level`/`column` refs), `partition` (name + `mode`; M source is extractable text but high-volume — optional), `relationship` (`fromColumn`/`toColumn`), `role` (name + `tablePermission` filter DAX), `expression` (M parameters/queries).

**Feasibility verdict (the locked question): STDLIB IS SUFFICIENT — DO NOT ADD A TMDL PARSER DEP.** The grammar is line-regular and indent-structured:
- Tokenize by physical line; compute indent depth from leading tabs.
- A non-`///`, non-blank line whose first token is a known object type at the current depth = an object header. Capture trailing `= <expr>` if present.
- Lines at depth+1 starting `property:` are properties; a line at depth+1 that is `=` (or the header carried `=`) starts a default-property expression that runs until the indent returns to ≤ the property depth (respecting ```` ``` ```` fences and blank-line inclusion rules).
- `///` lines accumulate as the description of the NEXT object.

**The faithfulness win:** we do NOT parse DAX or M — we capture the expression text verbatim, which is precisely what "extract the formula, never the value" requires. Edge cases the parser must respect (all from the spec): tab indentation (TMDL default; tolerate the spec's own examples which sometimes show spaces — normalize on `\t` but be lenient on leading-whitespace *count* per relative depth); single-quoted names with doubled `'`; double-quoted property values with doubled `"` and optional surrounding quotes; ```` ``` ```` verbatim expression blocks; partial declaration (a table's measures may live in a different file — extraction is per-file, so this is fine: each file's objects are emitted under their declared parent path). **Not flagged as essential to add a dependency** — the stdlib parser is the recommendation.

### Q-C. Report definition (PBIR / report.json) — extractable text + where filters live

**Two formats** (CITED: projects-report):
- **PBIR (enhanced, the future default)** — `definition/` tree, each object a separate JSON file with a public `$schema`. Files: `report.json` (report metadata + **report-level filters**), `pages/<page>/page.json` (page display name + **page-level filters**), `pages/<page>/visuals/<visual>/visual.json` (visual type, position, formatting, **query/field projections**, **visual-level filters**), `reportExtensions.json` (report-level measures), `bookmarks/*.bookmark.json`.
- **PBIR-Legacy** — a single `report.json` (the doc says it "doesn't support external editing"; structurally it's a nested JSON with `sections[]` (pages) → `visualContainers[]` whose `config` is a JSON string). Still text-extractable via `json` + a nested-string-parse, but messier. **Recommend: PBIR (enhanced) is the primary report target; PBIR-Legacy is best-effort.**

**Faithfully-extractable text:** page display names, visual titles and text-box content, field/measure references (the query projections binding fields to a visual), and **annotations** (PBIR supports name/value `annotations` on `report`/`page`/`visual`). Visual `title` text and a text box's runs are verbatim prose units; field references (`Table.Column` / measure names) are verbatim model references.

**Where FILTERS live (the row-cap crux anchor):**
- **Report-level** → `definition/report.json` ("report metadata, such as report level filters").
- **Page-level** → `pages/<page>/page.json` ("page level filters").
- **Visual-level** → `pages/<page>/visuals/<visual>/visual.json` ("visual metadata… query").

> **IMPORTANT data-leak caveat (CITED, projects-report):** "Some report metadata files, such as visual.json… can be saved with data values… if you apply a filter for 'Company' = 'Contoso', the value 'Contoso' will persist as part of the metadata." So filter *literal values* in `visual.json` ARE present as text — extract them verbatim as field-reference/filter units (they are part of the report definition), but understand they are config, not query result data. Slicer selections and series formatting likewise persist.

### Q-D. Row-cap & aggregation limits → the `unextracted[]` taxonomy (success criterion 2)

These are the signals that make an export *look* complete while it is a clipped aggregate. Where they manifest and the exact `unextracted[]` reasons to emit:

**1. Top-N / Bottom-N visual filters** — in `visual.json` (visual-level) or `page.json`/`report.json`, a filter with `filterType: TopN` (the FilterType enum value 5; CITED: PowerBI-JavaScript Filters wiki + RADACAD) carrying `operator: "Top"|"Bottom"`, `itemCount: N`, and an `orderBy`/`target`. **Signal:** a `filterType`/`type` of `TopN` (or a `topN`/`itemCount` key). **Reason:** `"visual {path}: Top-N filter (operator={op}, itemCount={n}) — only the top {n} rows are shown; underlying detail is clipped"`.

**2. Other restricting filter types** — `Advanced`/`Categorical`/`RelativeDate`/`Passed` filters that restrict the row set. **Signal:** any non-trivial filter object on a visual/page/report. **Reason:** `"{level} filter on {target} restricts the row set — full detail not represented in the export"`. (Be precise: a filter is config text we DO extract; the *consequence* — that the visual shows a subset — is the disclosure.)

**3. Summarized / aggregated field bindings** — a visual query projection binds a field with an aggregation (`Sum`/`Average`/`Count`/`Min`/`Max`) rather than the underlying detail rows. In TMSL/visual query this surfaces as an `aggregation`/`Aggregation` function on a field ref, and in TMDL a column's `summarizeBy: sum` (vs `none`). **Signal:** a field projection carrying an aggregation function, or a measure (a measure is inherently an aggregate). **Reason:** `"field {ref} is shown aggregated ({fn}); underlying detail rows are not in the export"` and, for measures, `"measure {name} is an aggregate formula; its computed value is not present (faithful: formula extracted, value never fabricated)"`.

**4. DirectQuery / row-limit / maxRows** — DirectQuery storage mode and the 1M-row import cap / visual data-point limits. Storage mode lives on the model/partition (`mode: directQuery` in TMDL partition); visual data limits / "show items with no data" live in `visual.json` formatting. **Signal:** `mode: directQuery`, a `maxRows`/data-reduction/`limit` key, or `showAllDataPoints`/`showItemsWithNoData`. **Reason:** `"partition {name} is DirectQuery — data is not stored in the model; no rows are extractable"` / `"visual {path} has a data-reduction/row limit ({n}); displayed data may be truncated"`.

**5. Structurally-absent data rows (the whole class)** — **PBIP/TMDL/PBIR text contains the MODEL and REPORT definition, NOT data rows.** This is not a per-visual signal; it is a categorical truth. The adapter should emit ONE whole-source disclosure whenever it extracts a model/report: **Reason:** `"PBIP/TMDL/PBIR is a definition format — it contains no data rows; measure/column values are not present and are never fabricated"`. This guarantees a model-only export never reads as a complete dataset.

**Taxonomy summary (reason-string constants to pin in the golden corpus, mirroring `pptx_adapter._R_*`):**
| Constant | Reason string (template) |
|----------|--------------------------|
| `_R_TOPN` | `"{path}: Top-N filter (operator={op}, itemCount={n}) — rows beyond the top {n} are clipped"` |
| `_R_FILTER` | `"{level} filter on {target} restricts the row set — full detail not represented"` |
| `_R_AGGREGATED` | `"{ref} shown aggregated ({fn}) — underlying detail rows not in the export"` |
| `_R_MEASURE_VALUE` | `"measure {name}: aggregate formula extracted; computed value not present (never fabricated)"` |
| `_R_DIRECTQUERY` | `"partition {name} is DirectQuery — no data rows stored/extractable"` |
| `_R_ROWLIMIT` | `"{path}: visual data-reduction/row limit ({n}) — displayed data may be truncated"` |
| `_R_NO_DATA_ROWS` | `"PBIP definition format contains no data rows; values are not present and never fabricated"` |
| `_R_PBIX_BINARY` | `"binary .pbix not extractable by the text adapter — export to PBIP/PBIR (File > Save as Power BI project) for faithful extraction"` |
| `_R_UNREADABLE` | `"Power BI project file could not be read ({error}) — not extractable"` |
| `_R_BINARY_FILE` | `"{path}: binary/non-text artifact (cache.abf/diagramLayout/etc.) not extracted"` |

### Q-E. pbixray ASSESSMENT — adopt or defer

**Verified facts** (VERIFIED via PyPI JSON API + GitHub; CITED: pypi.org/pypi/pbixray/json, github.com/Hugoberry/pbixray, pepy.tech):
- **License:** MIT (clean). **Python:** `>=3.8`. **Author:** Igor Cotruta (PyPI owner `hugoberry`). **Maintenance:** active — 161 commits, latest release **0.11.1 on 2026-06-10**, 128 stars. **Downloads:** ~258.5k total (pepy.tech) — not niche.
- **Telemetry/network:** none disclosed; it is a local file parser (no documented network calls). (LOW-confidence on "zero network" — not source-audited this session.)
- **Dependencies (requires_dist):** `pandas`, `numpy`, `apsw` (SQLite), `kaitaistruct` (binary parsing), and three single-maintainer Cython compression shims **`xpress8`, `xpress9`, `xmhuffman`** (all authored by the same Hugoberry, all C-extensions).
- **API surface:** `PBIXRay(path)` exposes `tables`, `schema`, `metadata`, `power_query`, `m_parameters`, `dax_measures`, `dax_tables`, `dax_columns`, `relationships`, `rls`, `statistics`, `size`, 31+ `tmschema_*` low-level tables, and `get_table(name)` (returns full VertiPaq table contents as a DataFrame). So it DOES expose the model surface (measures' DAX, schema, relationships) AND the row-cap surface (statistics/row counts) AND actual data rows.

**RECOMMENDATION: DEFER. Do NOT adopt pbixray.** Rationale:
1. **Minimal-core conflict (decisive).** pbixray transitively pulls `pandas`+`numpy` (heavy) plus **three obscure single-maintainer C-extension compression shims** the legitimacy seam flags SUS. Even behind a lazy `[powerbi]` extra, that is a large, hard-to-audit supply-chain surface for a *fallback* path. The repo's whole thesis is AI-optional / minimal-core; adding this for a secondary input is the wrong trade.
2. **The faithful answer to a binary `.pbix` is "export to PBIP".** PBIP/PBIR is Microsoft's own recommended, text-based, source-controllable format. Routing `.pbix` to a clear `unextracted[]` ("Save as Power BI project") is honest and actionable, not a degradation.
3. **Determinism/round-trip risk.** A VertiPaq DataFrame round-trip would need its own faithful serialization + the same determinism guarantees we already have for text — extra surface for little gain.

**`.pbix` disposition (the DEFER path, concrete):** when `path` ends `.pbix` (or the bytes are a ZIP/OLE binary, not a PBIP folder), `parse` returns a `Source` with `transcript=""`, `timestamp=deterministic_timestamp(None)`, and `extraction=encode_coverage([Unextracted(FreeLocator(path), _R_PBIX_BINARY)])` — exactly mirroring the Excel/PPTX whole-source-unreadable branch (`excel_adapter.py:287-302`). `Coverage.complete` is then forced False; no crash, no fabricated data.

**IF a future phase reverses this:** gate each of pbixray + xpress8 + xpress9 + xmhuffman behind a `checkpoint:human-verify` task (the three shims are the real risk), confirm zero network at runtime by source audit, add `[powerbi] = ["pbixray"]` lazily (mirror `_openpyxl_loader.py`), and route `statistics`/row-count/`get_table` to the SAME row-cap `unextracted[]` taxonomy (Q-D) — never emit a computed measure value as a claim.

### Q-F. Transcript layout + locator + timestamp

**Canonical transcript:** one line per emitted unit, `PREFIX{SEP}{verbatim value}\n`, where `SEP = "\t"` (mirror Excel/PPTX), files walked in **sorted** order, objects in declaration order within a file. The **per-unit prefix carries the file + object path** and is NOT part of the claim value (the value after `SEP` is the unit `normalize()` locates):

| Artifact | Prefix (example) |
|----------|------------------|
| Table description | `Model/Table[Sales]` |
| Column dataType | `Model/Table[Sales]/Column[Net Price].dataType` |
| Measure name | `Model/Table[Sales]/Measure[Sales Amount].name` |
| Measure DAX | `Model/Table[Sales]/Measure[Sales Amount].expression` |
| Relationship endpoint | `Model/Relationship[<id>].fromColumn` |
| Page name | `Report/Page[Sales Overview].displayName` |
| Visual title | `Report/Page[Sales Overview]/Visual[abc123].title` |
| Text box | `Report/Page[Sales Overview]/Visual[abc123].textbox` |
| Field ref | `Report/Page[Sales Overview]/Visual[abc123].field` |

The prefix is deterministic (derived from file path + object names/order). **Unit recovery in `distill()`** uses an anchored `_RECORD_PREFIX` regex (mirror `excel_adapter.py:407` / `pptx_adapter.py:394`) so values containing `\n`/`\t`/`:` stay verbatim and locatable. **Locator:** `FreeLocator(text=prefix)` — the same content-anchor pattern Excel/PPTX use; **no schema change** (the `CellLocator`/`SlideLocator` stubs in `locators.py:66-69` are explicitly "build none now"; `FreeLocator` carrying the object-path string is the contract-correct choice).

**Timestamp:** PBIP has **no single intrinsic date** (the model/report files carry no `created` analogous to OOXML `docProps`). Recommend **`deterministic_timestamp(None) → EPOCH_ZERO`** unconditionally — deterministic and honestly signals "no intrinsic date". (Do NOT read filesystem mtime — non-deterministic across clones. The `.pbip`/`.platform` files carry no reliable creation date either.) This matches the `_timestamps.py` contract exactly.

### Q-G. Golden fixture plan (ADAPT-06)

**Author a tiny, hand-written, byte-reproducible PBIP/TMDL tree as plain text** (no binary needed for the primary path — this is the headline advantage over the Excel/PPTX fixtures, which needed openpyxl/python-pptx to author). A `_author_fixtures.py` writes the files with stdlib (`pathlib.write_text`), so `sha256(tree)` is stable with no third-party authoring dep. Mirror the assertions in `tests/test_pptx_golden.py:8-41` and `test_excel_golden.py`.

**Fixture tree (`tests/fixtures/powerbi/sample.PBIP-tree/`):**
```
sample.pbip                                   # entry pointer (JSON)
sample.SemanticModel/
├── definition.pbism                          # version 4.0 (TMDL)
└── definition/
    ├── model.tmdl                            # culture; ref tables
    ├── relationships.tmdl                    # 1 relationship Sales→Product
    └── tables/
        ├── Sales.tmdl                        # table desc; 3 columns (int64/string/decimal,
        │                                     #   with dataType + description + summarizeBy);
        │                                     #   1 measure 'Total Sales' = SUMX(...) (DAX)
        └── Product.tmdl                       # 1 key column
sample.Report/
├── definition.pbir                           # datasetReference byPath ../sample.SemanticModel
└── definition/
    ├── report.json                           # report-level (no filter)
    ├── version.json
    └── pages/
        ├── pages.json
        └── Overview/
            ├── page.json                     # page name "Overview"
            └── visuals/
                ├── plainTable/visual.json    # a plain table visual (title + field refs) → claims
                └── topProducts/visual.json   # a Top-N-filtered + summarized visual
                                              #   (filterType TopN, itemCount 5, Sum aggregation)
                                              #   → row-cap + aggregation unextracted[]
```

**What each fixture proves (the executable contract, derived by driving the LIVE adapter — never assumed):**
1. **TMDL extraction** — `Sales.tmdl` yields verbatim claims: table description, 3 column names + dataTypes + descriptions, measure name + **DAX expression text** (`SUMX(...)`, never a value), `formatString`.
2. **Relationship** — `relationships.tmdl` yields `fromColumn`/`toColumn` claims.
3. **Plain report visual** — `plainTable/visual.json` yields the visual title + field-reference claims.
4. **Row-cap/aggregation disclosure** — `topProducts/visual.json` emits `unextracted[]` entries: `_R_TOPN` (Top-5), `_R_AGGREGATED` (Sum), plus the whole-source `_R_NO_DATA_ROWS`. The golden test asserts these reasons EXACTLY (pin the constants).
5. **Whole-source data-absence** — every fixture that extracts a model emits `_R_NO_DATA_ROWS` once → `Coverage.complete is False` for any non-trivial export (fail-loud proven).
6. **`.pbix` deferral path** — a tiny non-PBIP binary fixture (`fake.pbix`, a few bytes — does NOT need to be a real `.pbix`) drives the binary branch: asserts a single `_R_PBIX_BINARY` whole-source disclosure, empty transcript, no crash, `complete is False`. (No real `.pbix` needed because pbixray is DEFERRED — we only test the deferral, not parsing.)

**Invariants asserted per fixture (copy from `test_pptx_golden.py`):** zero silent drops (`len(claims)+len(unextracted) == units walked`); faithful spans (`claim.text == trace.span == transcript[start:end]`); content-addressed (`trace.is_addressed`); coverage honesty (`complete == (unextracted==[])`); `assert_conforms(PowerBIAdapter(), [source])`; `DistillationResult` JSON round-trip; **determinism on the parsed Source** (`s1.model_dump_json() == s2.model_dump_json()`); **round-trip coverage parity** (dump Source → reload → distill on a FRESH adapter → coverage equals original — drops travel on `Source.extraction`).

## Common Pitfalls

### Pitfall 1: Treating a measure's DAX as a value
**What goes wrong:** Emitting a number for a `measure` (it has no value in text).
**Why it happens:** Spreadsheet intuition (a cell has a value).
**How to avoid:** A `measure` default property is a DAX FORMULA — extract the expression text verbatim; emit `_R_MEASURE_VALUE` to disclose that the computed value is absent. (Mirrors the Excel formula-cache crux, `excel_adapter.py:18-20`.)
**Warning signs:** Any code path that parses/evaluates DAX, or emits a numeric claim from TMDL.

### Pitfall 2: Splitting the transcript on `\n`/`\t`/`:`
**What goes wrong:** Multi-line DAX and JSON values contain those chars; naive splitting corrupts units and breaks `claim.text == transcript slice`.
**How to avoid:** Recover units via an anchored `_RECORD_PREFIX` regex at line starts (mirror `excel_adapter.py:407-444`). Never escape values.
**Warning signs:** A unit that fails to locate in `normalize()` (routed to `unextracted` as "not verbatim-locatable").

### Pitfall 3: A clipped/aggregated export silently reading as complete
**What goes wrong:** A model-only or Top-N export looks like a full dataset; `Coverage.complete=True` is a lie.
**How to avoid:** Always emit the whole-source `_R_NO_DATA_ROWS` when extracting a model, plus per-visual `_R_TOPN`/`_R_AGGREGATED`/`_R_DIRECTQUERY`/`_R_ROWLIMIT`. The `Coverage` validator then forces `complete=False` (`coverage.py:54-67`). This IS success criterion 2.
**Warning signs:** A golden fixture with a Top-N visual whose result has `complete=True`.

### Pitfall 4: Non-deterministic folder walk / timestamp
**What goes wrong:** OS-order `os.listdir` or filesystem mtime → different Source bytes per run, breaking round-trip parity.
**How to avoid:** `sorted()` every directory listing; `deterministic_timestamp(None) → EPOCH_ZERO`. Never read mtime.
**Warning signs:** `s1.model_dump_json() != s2.model_dump_json()` on the determinism assertion.

### Pitfall 5: TMDL tabs-vs-spaces and quoting edge cases
**What goes wrong:** The spec mandates tab indentation but its own examples sometimes show spaces; single-quoted names with doubled `'`, double-quoted values with doubled `"`, and ```` ``` ````-fenced expressions can trip a naive parser.
**How to avoid:** Compute relative indent depth (lenient on whitespace *kind*, strict on *increase/decrease*); handle quote-doubling un-escaping; treat ```` ``` ```` blocks as verbatim until the closing fence. Extract text verbatim (don't normalize inside values).
**Warning signs:** Mis-grouped child objects, or a measure name still wrapped in `'...'` in a claim.

## Code Examples

### Walk + serialize a PBIP folder (sketch, stdlib only)
```python
# Source: pattern mirrors src/newsletters/adapters/pptx_adapter.py:225-252 (_serialize)
import json, pathlib
SEP = "\t"
def serialize_tree(root: pathlib.Path):
    lines, units, drops = [], [], []
    for tmdl in sorted(root.glob("*.SemanticModel/definition/**/*.tmdl")):
        for prefix, value in parse_tmdl(tmdl.read_text(encoding="utf-8")):  # _tmdl.py
            lines.append(f"{prefix}{SEP}{value}\n"); units.append(value)
    for vj in sorted(root.glob("*.Report/definition/**/visual.json")):
        cfg = json.loads(vj.read_text(encoding="utf-8"))
        for prefix, value in extract_visual(cfg):  # title, field refs (verbatim)
            lines.append(f"{prefix}{SEP}{value}\n"); units.append(value)
        for reason in detect_row_caps(cfg):         # Q-D taxonomy
            drops.append(Unextracted(locator=FreeLocator(text=str(vj)), reason=reason))
    return "".join(lines), units, drops
```

### TMDL measure extraction (the faithfulness crux)
```tmdl
# Source: https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview
measure 'Sales Amount' = SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])
    formatString: $ #,##0
# → emit unit "Sales Amount" (name) under prefix .../Measure[Sales Amount].name
# → emit unit "SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])" (DAX) under .expression
# → NEVER emit a numeric value; emit _R_MEASURE_VALUE to disclose the value is absent
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.pbix` binary (proprietary) | **PBIP** text project (TMDL + PBIR JSON) | PBIP preview ~2023; PBIR enhanced 2024; PBIR → GA-bound (will become the ONLY report format) | The faithful, source-controllable, dependency-free path — exactly what this adapter targets. |
| TMSL `model.bim` (one big JSON) | **TMDL** folder (one file per object) | TMDL preview 2023 | Easier diffs; per-object files; the primary model target. TMSL still readable as secondary JSON. |
| report.json (PBIR-Legacy, opaque) | **PBIR** `definition/` tree (per-file, public `$schema`) | 2024 | Each page/visual a separate documented JSON — clean to walk. |

**Deprecated/outdated:**
- PBIR-Legacy `report.json`: still emitted for un-upgraded reports, but Microsoft states PBIR will be the only supported format at GA. Support it best-effort; target PBIR enhanced.
- Reading `.pbix` directly: avoid (binary, proprietary, heavy deps) — disclose + recommend PBIP export.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | PBIP/PBIR JSON keys for filters use `filterType: TopN` / `itemCount` / `operator` as in the PowerBI-JS Filters model; exact PBIR `visual.json` filter key names not byte-confirmed against a live file this session. | Q-D | Detection logic may need key-name tweaks; mitigated by authoring the golden `topProducts/visual.json` against the real schema and driving the LIVE adapter to pin reasons. |
| A2 | PBIP has no reliable single intrinsic creation date in any always-present text file. | Q-F | If a stable date field exists, EPOCH_ZERO is still safe (deterministic); only loses a real date. Low risk. |
| A3 | pbixray makes no network calls (not source-audited this session; "local parser" inferred from docs/usage). | Q-E | Moot — pbixray is DEFERRED. If reversed, audit before adopting. |
| A4 | The `parse(raw, path)` entrypoint will be extended (or paired with `parse_path`) to accept a folder, since PBIP is multi-file. | Q-A, Q-F | Planner decides the entrypoint shape; the serializer/units/normalize contract is unaffected. |

**If this table is empty:** it is not — these four assumptions need confirmation during planning/execution (author the row-cap fixture against the real PBIR schema to resolve A1).

## Open Questions

1. **Exact PBIR `visual.json` filter/aggregation key names.**
   - What we know: filters live at report/page/visual level; `filterType: TopN` + `itemCount` + `operator` is the documented filter model; aggregations surface as field-projection functions.
   - What's unclear: the precise nested key path inside the enhanced `visual.json` (the public schemas at github.com/microsoft/json-schemas/.../visualContainer define it).
   - Recommendation: during 07-planning, fetch the `visualContainer`/`filterConfig` JSON schema and author the golden `topProducts/visual.json` to match; pin `_R_TOPN`/`_R_AGGREGATED` reasons against the LIVE adapter output (mirror how PPTX/Excel counts were "derived by driving the live adapter").

2. **`parse` entrypoint shape for a multi-file folder.**
   - What we know: existing adapters take `parse(raw: bytes, path)`; PBIP is a folder.
   - Recommendation: add `parse_path(path)` for the folder/tree case and keep `parse(raw, path)` for a single dropped `.tmdl`/`.json`/`.pbix`; both feed the one serializer. Planner to confirm.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python stdlib (`pathlib`,`json`,`re`,`datetime`) | Primary PBIP/TMDL path | ✓ | 3.12 (`tool.mypy`) | — |
| pbixray (+ pandas/numpy/apsw/kaitaistruct/xpress8/9/xmhuffman) | `.pbix` binary fallback | n/a | — (DEFERRED) | Whole-source `unextracted[]` ("export to PBIP") — the chosen path |

**Missing dependencies with no fallback:** none — the primary path is stdlib-only.
**Missing dependencies with fallback:** `.pbix` parsing → disclosed to `unextracted[]` (pbixray DEFERRED by design, not by absence).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (configured: `tool.pytest.ini_options`, `pythonpath=["src"]`, `testpaths=["tests"]`) |
| Config file | `pyproject.toml` |
| Quick run command | `.venv/bin/pytest tests/test_powerbi_adapter.py -x -q` |
| Full suite command | `.venv/bin/pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADAPT-05 | TMDL/PBIR verbatim extraction via normalize() | unit | `pytest tests/test_powerbi_adapter.py -x` | ❌ Wave 0 |
| ADAPT-05 | Row-cap/aggregation/data-absence → unextracted[] | unit | `pytest tests/test_powerbi_adapter.py -k rowcap -x` | ❌ Wave 0 |
| ADAPT-05 | `.pbix` binary deferral (whole-source disclosure) | unit | `pytest tests/test_powerbi_adapter.py -k pbix -x` | ❌ Wave 0 |
| ADAPT-06 | Golden corpus: zero silent drops, faithful spans, content-addressed, conformance, determinism, round-trip parity | golden | `pytest tests/test_powerbi_golden.py -x` | ❌ Wave 0 |
| (invariant) | Bare-install / AI-isolation / lint-imports stay green (no new dep added) | gate | `pytest tests/test_ai_optional.py -q && lint-imports` | ✅ exists |

### Sampling Rate
- **Per task commit:** `.venv/bin/pytest tests/test_powerbi_adapter.py -x -q`
- **Per wave merge:** `.venv/bin/pytest -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/fixtures/powerbi/_author_fixtures.py` — writes the byte-reproducible PBIP tree (stdlib `write_text`)
- [ ] `tests/fixtures/powerbi/<PBIP tree>` — the committed corpus (Q-G)
- [ ] `tests/test_powerbi_adapter.py` — unit suite (parse forks, row-cap detection, `.pbix` deferral)
- [ ] `tests/test_powerbi_golden.py` — golden suite (mirror `test_pptx_golden.py` invariants)
- [ ] No framework install needed — pytest already configured.

## Security Domain

> `security_enforcement: true`, ASVS level 1. Power BI project files are UNTRUSTED input.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | **yes** | Wrap all file/JSON/TMDL parsing in try/except → whole-source `unextracted[]` (`_R_UNREADABLE`), never an unhandled crash (mirror `excel_adapter.py:287-302`). Cap/guard pathological inputs. |
| V6 Cryptography | no | `Trace.from_source` pins the content hash; adapter never hashes. |

### Known Threat Patterns for the PBIP adapter
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed TMDL/JSON crashes the walk | DoS | try/except per file → disclose, never crash (V5). |
| Path traversal via `datasetReference.byPath` / folder walk | Tampering | Resolve only relative paths *within* the project root; reject absolute/`..`-escaping paths (the docs already forbid absolute byPath). |
| Zip/decompression amplification (a `.pbix` is a ZIP) | DoS | Do NOT decompress `.pbix` — disclose binary to `unextracted[]` (pbixray DEFERRED avoids touching the zip entirely). |
| Embedded data values in `visual.json` (e.g. filter literal `'Contoso'`) | Information disclosure | Extract verbatim as config text (it IS the report definition); the reviewer sees it — never silently surfaced as "data". |
| Non-deterministic walk leaking environment (mtime/listdir order) | Tampering w/ provenance | `sorted()` + `EPOCH_ZERO` → deterministic Source. |

## Sources

### Primary (HIGH confidence)
- [CITED] learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview — TMDL grammar (indentation, object declaration, properties, default-property expressions, descriptions, folder structure, expression backtick rules). Doc updated 2026-06-11.
- [CITED] learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset — SemanticModel folder (definition.pbism, definition/ TMDL files, model.bim TMSL, version table). Updated 2026-05-30.
- [CITED] learn.microsoft.com/en-us/power-bi/developer/projects/projects-report — Report folder (definition.pbir, report.json PBIR-Legacy, PBIR definition/ tree, pages/visuals files, report/page/visual filters, embedded data-value caveat). Updated 2026-01-12.
- [CITED] learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview — PBIP overview (folder layout).
- [VERIFIED via PyPI JSON API] pypi.org/pypi/pbixray/json — pbixray 0.11.1, MIT, Python>=3.8, requires_dist (pandas/numpy/apsw/kaitaistruct/xpress8/xpress9/xmhuffman), release 2026-06-10.
- [VERIFIED via seam] `gsd-tools query package-legitimacy check` — pbixray + all transitive shims SUS (unknown-downloads / too-new).

### Secondary (MEDIUM confidence)
- [CITED] github.com/Hugoberry/pbixray — maintenance (161 commits, 128 stars), API surface (tables/schema/dax_measures/get_table/statistics).
- [CITED] pepy.tech/projects/pbixray — ~258.5k downloads.
- [CITED] github.com/microsoft/PowerBI-JavaScript/wiki/Filters + radacad.com top-n-filter — FilterType.TopN (value 5), `operator`/`itemCount`/`orderBy`/`target` filter shape.

### Tertiary (LOW confidence)
- WebSearch summaries of PBIR `visual.json` filter key paths — cross-check against github.com/microsoft/json-schemas during planning (Open Q1).

## Metadata

**Confidence breakdown:**
- Standard stack (stdlib-only primary path): HIGH — Microsoft Learn authoritative + three proven in-repo adapters establish the exact pattern.
- Architecture (transcript/normalize/coverage/timestamp reuse): HIGH — directly mirrors `excel_adapter.py`/`pptx_adapter.py`.
- TMDL stdlib parse feasibility: HIGH — grammar is line-regular per the official spec; no dep needed.
- Row-cap/aggregation taxonomy: MEDIUM — the WHERE (report/page/visual levels) is HIGH; exact PBIR JSON key names need schema confirmation (Open Q1).
- pbixray DEFER recommendation: MEDIUM-HIGH — metadata verified; the call rests on minimal-core + transitive-SUS-shim risk (a judgement consistent with the repo's invariants).

**Research date:** 2026-06-17
**Valid until:** ~2026-07-17 (PBIP/PBIR are in active preview heading to GA — re-verify report-format key names if planning slips; TMDL grammar is stable).
