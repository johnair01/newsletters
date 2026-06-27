# Phase 7 — Context & Decisions (Power BI Adapter)

**Goal:** Extract from Power BI PBIP/TMDL text (stdlib) into `Claim(+Trace)`, with a pbixray fallback
for binary `.pbix`; report the **row-cap and aggregation limits** that make an export look complete when
it is actually a clipped aggregate — failing loud rather than presenting a clipped aggregate as complete.

**Requirements:** ADAPT-05 (+ ADAPT-06 golden tests). **Depends on:** Phase 4 (shared `normalize()`,
adapter/DistillPort pattern, Coverage/`unextracted[]`), Phase 5/6 (hardened coverage carrier
`Source.extraction`, lazy-extra packaging precedent, `deterministic_timestamp`).

## Decisions (scope lean — research to confirm/refine)

1. **Primary path = PBIP/TMDL text, STDLIB-only (no new dep).** PBIP (Power BI Project) is a
   text/folder format: TMDL (`*.tmdl`, tabular model definition — tables/columns/measures/relationships,
   all text) + report definition (JSON/`.pbir`). Parse these with stdlib (text + `json`). This is the
   modern, faithful, dependency-free path and the success-criterion-1 focus ("PBIP/TMDL text (stdlib)").

2. **pbixray fallback for binary `.pbix` — research-gated, behind an optional `[powerbi]` extra IF
   adopted.** The goal names a pbixray fallback for binary decks. Research MUST assess pbixray
   (maturity, license, transitive deps incl. whether it pulls pandas/numpy, telemetry, last release)
   before adoption. Decision rule: if pbixray is clean (permissive license, no telemetry, acceptable
   deps), add it behind a lazy `[powerbi]` extra (mirror `[excel]`/`[pptx]`); if it's heavy/risky/
   unmaintained, DEFER it — route `.pbix` binary input to a clear `unextracted[]`/error ("export to
   PBIP for faithful extraction") and ship the stdlib PBIP/TMDL path alone. Either way the bare/core
   install + AI-isolation + `lint-imports` stay green. If pbixray (or any dep) is adopted, it is a
   Package-Legitimacy decision the orchestrator makes from the research (no reviewer interrupt unless
   the research surfaces a real red flag — license/telemetry/abandoned).

3. **Faithful extraction = model/report TEXT, never fabricated data (the crux).** TMDL/PBIP carry the
   MODEL and REPORT definition, NOT data rows. Claims = verbatim text artifacts: table names, column
   names + dataTypes + descriptions, **measure names + their DAX expressions (verbatim, never a
   computed value)**, relationships, hierarchies, report page/visual titles + text boxes + field refs.
   A DAX measure is a formula, not a number — extract the formula text; NEVER fabricate a value.

4. **Row-cap & aggregation limits → `unextracted[]` (success criterion 2, "fail loud").** Research
   WHERE these manifest in PBIP/TMDL and enumerate them: e.g. visuals with Top-N/row filters, summarized
   fields (an aggregate shown without underlying detail), DirectQuery/row-limit settings, measures whose
   values aren't computable from text, and any data the text format structurally cannot contain. The
   point: a clipped/aggregated export must be DISCLOSED in `unextracted[]`, never presented as complete.

5. **Reuse shared `normalize()` + coverage carrier + deterministic_timestamp.** Adapter produces a
   canonical transcript + verbatim units + `unextracted[]`; `normalize()` content-addresses; drops on
   `Source.extraction` (join the round-trip parity matrix); timestamp deterministic (PBIP has no single
   intrinsic date → likely `EPOCH_ZERO`, or a project-file date if one exists — research). Register
   backend "powerbi" (or "pbip"); conform. Locator = `FreeLocator(text=...)` (transcript-prefix pattern).

6. **Golden fixtures (ADAPT-06).** Author a small PBIP/TMDL fixture tree (text files — easy to author
   by hand/generator, byte-reproducible) covering: a TMDL model (table + columns + a measure with DAX),
   a relationship, a report page with a visual + a Top-N-filtered/summarized visual (→ row-cap/aggregation
   unextracted), and (if pbixray adopted) a tiny `.pbix` or its deferral path. Assert zero silent drops,
   verbatim + content-addressed claims, conformance, determinism, round-trip parity.

## Research-locked choices (07-RESEARCH.md accepted 2026-06-17; HIGH primary / MEDIUM on PBIR key names)

- **L1 — pbixray DEFERRED (orchestrator decision, from research).** pbixray is MIT/active, but its dep
  tree (pandas+numpy+apsw+kaitaistruct + 3 single-maintainer Cython shims `xpress8/xpress9/xmhuffman`,
  all SUS/unknown-downloads) is too heavy/hard-to-audit for a *fallback*. **Phase 7 adds ZERO new
  dependency.** Binary `.pbix` input → a whole-source `unextracted[]` disclosure: "export to PBIP/PBIR
  for faithful extraction" (fail loud, faithful). No `[powerbi]` extra. (If ever reversed, gate the 3
  shims behind a human-verify checkpoint.) → No Package-Legitimacy concern this phase.
- **L2 — TMDL = stdlib line/indent parse, NO parser dep.** YAML-like single-tab-indent grammar: object
  headers `type name`, `property: value`, `=`-introduced default-property expressions (single-line /
  indent-deeper multi-line / ```` ``` ````-fenced), `///` descriptions. A stdlib tokenizer extracts
  every artifact verbatim. **Never evaluate DAX** — a measure's `expression` is a FORMULA, extracted as
  text, never a value (the Excel formula-cache crux restated).
- **L3 — Row-cap/aggregation `unextracted[]` taxonomy (fail loud).** Detect + report: (1) `filterType:
  TopN` (+operator/itemCount); (2) restricting filters (report/page/visual level); (3) summarized field
  bindings / `summarizeBy` / measure aggregates; (4) `mode: directQuery` + visual row/data limits;
  (5) **the categorical truth that PBIP text has NO data rows → a whole-source `_R_NO_DATA_ROWS` entry
  forcing `Coverage.complete=False`** on any model export. Filters live in report.json / page.json /
  visual.json. Data-leak caveat: visual.json filter LITERALS (e.g. `'Contoso'`) are extracted as config
  text surfaced to the reviewer, never silently treated as data.
- **L4 — Entrypoint:** PBIP is a multi-file FOLDER, so add `parse_path(path) -> ...` alongside the
  byte-oriented `parse(raw, path)` (planner finalizes the shape; a `.pbix`/zip byte path routes to the
  L1 deferral disclosure). Register backend `"powerbi"`. Timestamp → `EPOCH_ZERO` (PBIP has no single
  reliable intrinsic date) via `deterministic_timestamp`.
- **L5 — Transcript layout:** multi-file, so each unit's prefix carries file+object path (e.g.
  `Model/Table[Sales]/Measure[Total]`, `report/page1/visual3/title`), prefix NOT part of the claim
  value, composing with cursor-advancing normalize(). Locator = `FreeLocator(text=prefix)`.
- **L6 — Fixtures = hand-authored PLAIN-TEXT PBIP/TMDL tree** via stdlib `write_text` (byte-reproducible,
  NO authoring dep — unlike excel/pptx). Risk A1: PBIR `visual.json` filter/aggregation key paths not
  byte-confirmed — author the golden against `microsoft/json-schemas .../visualContainer` and PIN the
  reason strings by driving the LIVE adapter (same method excel/pptx used).

## Hard rules in play
- **Faithful, not suggestive** — extract DAX/model TEXT verbatim; NEVER compute or fabricate a data
  value; clipped aggregates disclosed, not presented as complete.
- **No silent drops** (incl. across persistence). Fail loud on row-cap/aggregation limits.
- **AI-optional / minimal core** — primary path stdlib; any binary fallback (pbixray) behind `[powerbi]`,
  lazy; bare-install + `lint-imports` stay green.
- **Every claim traces to evidence** — model/report claims content-addressed via shared normalize().
- **Determinism** — same input → identical claims/coverage.

## Research note (dispatch BEFORE planning)
Best-known methods: PBIP folder structure + TMDL grammar (tables/columns/measures/relationships
serialization), report `definition.pbir`/`report.json` structure (pages/visuals/filters), where Top-N /
row-cap / summarized-aggregation settings live in the JSON, deterministic text parsing of TMDL (stdlib —
do NOT add a TMDL parser dep unless essential; if one seems essential, STOP and flag). Assess pbixray
(PyPI: license, deps incl pandas/numpy?, telemetry, maintenance, last release) for the binary fallback
decision. Recommend the transcript layout + the row-cap/aggregation `unextracted[]` taxonomy + the
fixture-authoring plan (a hand-authored PBIP/TMDL tree). Cite Microsoft PBIP/TMDL docs + pbixray repo.
Record in 07-RESEARCH.md.
