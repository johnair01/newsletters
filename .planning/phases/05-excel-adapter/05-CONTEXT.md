# Phase 5 — Context & Decisions (Excel Adapter)

**Goal:** Extract cell/sheet structure from `.xlsx` via openpyxl into `Claim(+Trace)` with `sheet!cell`
locators, routing every value openpyxl cannot resolve (uncomputed/`None` formula cache) to
`unextracted[]` — never emitted as `0`/empty data.

**Requirements:** ADAPT-03 (+ ADAPT-06 golden tests for this adapter). **Depends on:** Phase 4
(shared `normalize()`, the adapter/DistillPort pattern, the Coverage/`unextracted[]` contract).

## Decisions

0. **TASK ZERO — harden the adapter coverage-persistence flaw BEFORE replicating the pattern**
   (carried from the Phase-4 verifier; see RETRO 2026-06-17). Today an adapter's U1–U7 `unextracted[]`
   drops live in adapter memory keyed by `source.id`, so re-`distill()`ing a *persisted* `Source` on a
   fresh adapter silently loses them and falsely reports `complete=True`. Fix the PATTERN so adapter
   coverage is **reconstructable from the `Source` itself** (the researcher recommends the cleanest
   mechanism — e.g. persist the adapter's `unextracted[]` determination as data that travels with the
   `Source`, vs re-deriving from `source.context`). Retrofit the Email adapter, add a **round-trip
   coverage-parity** test to the conformance/golden pattern (`model_dump_json → reload → fresh-adapter
   distill()` must equal the original coverage), THEN build the Excel adapter on the hardened pattern.
   Faithful-extraction "no silent drops" must hold across persistence, not just same-instance.

1. **openpyxl behind an optional `[excel]` extra, lazy-imported** (Package-Legitimacy: PRE-APPROVED).
   `openpyxl` is named by the spec (ADAPT-03), MIT-licensed, pure-Python (no native deps), mature, no
   telemetry/phone-home. Add `excel = ["openpyxl"]` to `[project.optional-dependencies]`. Import it
   **lazily inside the Excel adapter only** (mirror the `[ai]` discipline) so: bare `pip install .`
   still runs the spine; the AI-optional bare-install gate + `lint-imports` stay green; a clear error
   tells the user to `pip install .[excel]` if they use the adapter without it. openpyxl is NOT AI —
   the forbid-ai contract is unaffected — but the bare-install/import-isolation test must still pass
   without `[excel]` installed.

2. **Reuse the shared `normalize()` (no second extraction rule).** The Excel adapter produces a
   canonical text **transcript** of the workbook + an ordered list of verbatim cell-value units +
   its own `unextracted[]` (formula-cache gaps etc.); `normalize()` content-addresses the units. The
   adapter never calls `Trace.from_source`/`hashlib` directly.

3. **Transcript serialization (research the exact layout).** A spreadsheet isn't linear text, so the
   adapter serializes the workbook into a deterministic canonical text (e.g. one line per non-empty
   cell: `Sheet!A1<sep>value`), row-major, sheet order preserved, so each cell's value string is a
   verbatim-locatable span. The `Trace` locator carries `sheet!cell` (ADAPT-03). The canonical
   value→string rule must be faithful (no lossy rounding/reformatting) and deterministic — research it.

4. **Formula-cache gap = the faithfulness crux (ADAPT-03 criterion 2).** Decide load strategy via
   research: openpyxl `data_only=True` yields cached computed values (`None` if the file was never
   calculated by Excel); `data_only=False` yields formula strings. A formula cell with an empty/`None`
   cache MUST route to `unextracted[]` (reason names the cell), NEVER be emitted as `0` or empty. May
   require loading the workbook twice (formula view + data view) to distinguish "blank cell" from
   "formula with no cached value." Research the precise openpyxl semantics + read_only/memory options.

5. **Merged cells, dates, numbers, types.** Research faithful handling: merged ranges (value lives in
   the top-left anchor; other cells are `None` — don't emit phantom blanks, account for the range),
   datetimes/numbers/booleans (canonical deterministic string form == claim text == transcript slice),
   and what counts as an `unextracted[]` reason here (e.g. unreadable/error cells `#REF!`, charts,
   images, pivot caches openpyxl can't read).

6. **Golden fixtures (ADAPT-06).** `.xlsx` fixtures (authored programmatically with openpyxl, byte-
   reproducible) covering: formulas WITH cached values, formulas WITHOUT cache (→ unextracted),
   merged cells, multiple sheets, mixed types (date/number/bool/text), empty cells, and an error cell.
   Assert the zero-silent-drops identity + verbatim + content-addressed + conformance + determinism +
   the new round-trip coverage parity.

## Hard rules in play
- **Faithful, not suggestive** — uncomputed formula cells become `unextracted[]`, never fabricated 0/empty.
- **No silent drops** — now enforced ACROSS persistence (task zero), not just same-instance.
- **AI-optional core** — openpyxl is behind `[excel]`, lazy; bare-install + `lint-imports` stay green.
- **Minimal core** — third-party adapter deps live behind extras (openpyxl is the precedent-setter here).
- **Every claim traces to evidence** — cell claims are content-addressed via the shared normalize().

## Research note (dispatch BEFORE planning)
Best-known openpyxl methods: `load_workbook(data_only=?, read_only=?)`, formula-vs-cache detection
(double-load), merged-cell handling (`worksheet.merged_cells`), faithful value→string for
date/number/bool, error-value cells, what openpyxl silently cannot read (charts/images/pivots) → all
into `unextracted[]`. Also the cleanest mechanism for task-zero (adapter coverage reconstructable from
`Source`). Cite openpyxl + python docs. Confirm openpyxl is the right lib (vs xlsxwriter [write-only],
pandas [heavy + pulls numpy]). Record in 05-RESEARCH.md.
