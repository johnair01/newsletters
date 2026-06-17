# Phase 5: Excel Adapter — Research

**Researched:** 2026-06-17
**Domain:** Deterministic faithful `.xlsx` extraction (openpyxl) feeding the shared `normalize()`; plus a cross-cutting "adapter coverage must survive a `Source` round-trip" hardening (task zero).
**Confidence:** HIGH (openpyxl API + the carried flaw are both verified against authoritative docs and the live repo)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
0. **TASK ZERO — harden the adapter coverage-persistence flaw BEFORE replicating the pattern.** Today an adapter's U1–U7 `unextracted[]` drops live in adapter memory keyed by `source.id`, so re-`distill()`ing a *persisted* `Source` on a fresh adapter silently loses them and falsely reports `complete=True`. Fix the PATTERN so adapter coverage is **reconstructable from the `Source` itself**. Retrofit the Email adapter, add a **round-trip coverage-parity** test (`model_dump_json → reload → fresh-adapter distill()` must equal the original coverage), THEN build the Excel adapter on the hardened pattern. Faithful-extraction "no silent drops" must hold across persistence, not just same-instance.
1. **openpyxl behind an optional `[excel]` extra, lazy-imported** (Package-Legitimacy: PRE-APPROVED). Add `excel = ["openpyxl"]` to `[project.optional-dependencies]`. Import it **lazily inside the Excel adapter only** (mirror the `[ai]` discipline) so bare `pip install .` still runs the spine, the AI-optional bare-install gate + `lint-imports` stay green, and a clear error tells the user to `pip install .[excel]`. openpyxl is NOT AI — the forbid-ai contract is unaffected — but the bare-install/import-isolation test must still pass without `[excel]` installed.
2. **Reuse the shared `normalize()` (no second extraction rule).** The Excel adapter produces a canonical text **transcript** + an ordered list of verbatim cell-value units + its own `unextracted[]`; `normalize()` content-addresses the units. The adapter never calls `Trace.from_source`/`hashlib` directly.
3. **Transcript serialization (research the exact layout).** Serialize the workbook into a deterministic canonical text (one line per non-empty cell: `Sheet!A1<sep>value`), row-major, sheet order preserved, so each cell's value string is a verbatim-locatable span. The `Trace` locator carries `sheet!cell` (ADAPT-03). The value→string rule must be faithful (no lossy rounding/reformatting) and deterministic.
4. **Formula-cache gap = the faithfulness crux (ADAPT-03 criterion 2).** `data_only=True` yields cached computed values (`None` if the file was never calculated by Excel); `data_only=False` yields formula strings. A formula cell with an empty/`None` cache MUST route to `unextracted[]` (reason names the cell), NEVER be emitted as `0` or empty. May require loading the workbook twice (formula view + data view) to distinguish "blank cell" from "formula with no cached value."
5. **Merged cells, dates, numbers, types.** Faithful handling: merged ranges (value lives in top-left anchor; other cells `None` — don't emit phantom blanks, account for the range), datetimes/numbers/booleans (canonical deterministic string form == claim text == transcript slice), and `unextracted[]` reasons (error cells `#REF!`, charts, images, pivot caches openpyxl can't read).
6. **Golden fixtures (ADAPT-06).** `.xlsx` fixtures authored programmatically with openpyxl, byte-reproducible: formulas WITH cache, formulas WITHOUT cache (→ unextracted), merged cells, multiple sheets, mixed types (date/number/bool/text), empty cells, an error cell. Assert zero-silent-drops + verbatim + content-addressed + conformance + determinism + the new round-trip coverage parity.

### Claude's Discretion
- The exact task-zero mechanism + data shape (this research recommends ONE — see Question A).
- Transcript separator, value→string rules, fixture set details.
- read_only vs standard load mode (this research recommends standard mode — see Question B/F).

### Deferred Ideas (OUT OF SCOPE)
- Cell styles/formatting, column widths, conditional formatting, chart/image *content* extraction (we DETECT and DISCLOSE these as unextracted, never extract them).
- Encrypted/password-protected `.xlsx`, `.xls` (legacy), `.xlsm` macro extraction.
- A `CellLocator` typed variant (stubbed in `locators.py:67` but NOT built this phase — use `FreeLocator(text="Sheet!A1")` per the existing pattern unless the planner decides otherwise; see Question D risk).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADAPT-03 | Excel `.xlsx` adapter: extract cell/sheet structure into `Claim(+Trace)` with `sheet!cell` locators; uncomputed formula cells → `unextracted[]` never `0`/empty | Questions B (formula-cache rule), C (value→string), D (transcript + locator), E (merged), F (silent-loss enumeration) |
| ADAPT-06 | Golden-file tests for this adapter (byte-reproducible fixtures, zero silent drops) | Question G (fixture plan) + Question A (round-trip coverage-parity test) |
| (carried) | Task-zero: adapter coverage reconstructable from the persisted `Source` | Question A (recommended mechanism + shape + parity test) |
</phase_requirements>

## Summary

openpyxl 3.1.5 is the correct, spec-named, pre-approved library [VERIFIED: PyPI `pip index versions openpyxl`]. It is pure-Python (no native build), MIT-licensed, and the only reasonable choice for reading `.xlsx` (Question H confirms: pandas is heavy + pulls numpy; xlrd is `.xls`-only and dropped `.xlsx` support; xlsxwriter is write-only). **No new dependency beyond openpyxl is needed.**

The faithfulness crux is the **double-load**: an openpyxl-saved (and many real) `.xlsx` carries NO formula cache, so `data_only=True` returns `None` for a formula cell — indistinguishable from a genuinely blank cell *unless* you also load `data_only=False` and inspect `cell.data_type == 'f'`. The rule is: **formula cell (`data_type=='f'` in the formula view) whose cached value (`data_only` view) is `None` → `unextracted[]`, NEVER emitted as `0`/empty.** [CITED: openpyxl tutorial — `data_only` "controls whether cells with formulae return the formula or the cached value from Excel's last save"]

**Load mode: use STANDARD mode (`read_only=False`), not `read_only=True`.** In read_only mode merged cells return an `<EmptyCell>` (the merge structure is unreadable) and ad-hoc access is deprecation-warned [VERIFIED: openpyxl docs + openpyxl-users list]. Faithful merged-cell + silent-loss accounting REQUIRES standard mode. Memory is a non-issue for the small fixtures and typical inputs; if a future huge-file path is needed it is a separate, descoped concern.

**Task zero — recommended mechanism:** persist the adapter's `unextracted[]` determination as a **structured JSON payload on `Source.context`** (option i, the `source.context` variant), reconstructed by `distill()` via `json.loads`. This keeps `Source` schema-stable (no new field, no new dependency, AI-free, round-trips through `model_dump_json` for free), makes coverage a pure function of the `Source`, and lets BOTH adapters (email retrofit + excel) share one tiny encode/decode helper that a single round-trip-parity conformance test pins. See Question A for the exact shape and the rejected alternatives.

**Primary recommendation:** Build the Excel adapter as a lazy-openpyxl `DistillPort` that (1) double-loads the workbook, (2) walks sheets in workbook order, row-major, emitting one canonical `Sheet!A1\t<value>` transcript line per non-empty *extractable* cell with a deterministic value→string rule, (3) routes uncomputed-formula / error / merged-overflow / unreadable-feature gaps to `unextracted[]`, and (4) carries that `unextracted[]` determination in `Source.context` so `distill()` is stateless and survives persistence. Retrofit Email to the same `Source.context` mechanism first, and add a shared round-trip coverage-parity conformance test both adapters pass.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `.xlsx` byte → workbook parse | Excel adapter (`adapters/excel_adapter.py`) | — | Format-specific; mirrors `email_adapter.py` owning `email` parsing. Lazy-imports openpyxl. |
| Faithful verbatim claim minting | shared `normalize()` (`adapters/normalize.py`) | — | The ONE place the faithful rule lives (ADAPT-01). Adapter never mints/hashes. |
| Coverage / `unextracted[]` honesty | `Coverage` model (`distill/coverage.py`) | adapter (produces the list) | The `complete↔unextracted` invariant is enforced in `Coverage`'s validator. |
| Coverage persistence across round-trip | `Source.context` (data) + a shared codec helper | both adapters | TASK ZERO: makes coverage a pure function of the `Source`, not adapter memory. |
| Trace minting / content-address | `Trace.from_source` (`semantic.py`) | `normalize()` (sole caller) | Sole hashing path; offsets validated before slicing. |
| Backend contract / conformance | `DistillPort` + `assert_conforms` (`distill/`) | — | Round-trip parity test extends `assert_conforms` semantics (D-04 already checks result JSON round-trip; we add a coverage-parity check across a *Source* round-trip + fresh adapter). |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openpyxl | 3.1.5 | Read `.xlsx` cells/sheets/merges; detect formula-cache gaps | The de-facto pure-Python `.xlsx` reader/writer; spec-named (ADAPT-03); MIT; no native deps; mature (releases since 2010). [VERIFIED: PyPI] |
| python stdlib `json` | (stdlib) | Encode/decode the coverage payload on `Source.context` (task zero) | No new dependency; deterministic with `sort_keys`; round-trips via Pydantic for free. [CITED: docs.python.org/3/library/json] |
| python stdlib `datetime` | (stdlib) | Canonical ISO-8601 string for date/time cells (`.isoformat()`) | Lossless, deterministic, no locale. [CITED: docs.python.org/3/library/datetime] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl (in `tests/fixtures/xlsx/_author_fixtures.py`) | 3.1.5 | Author byte-reproducible `.xlsx` fixtures programmatically | Test-only; mirrors Phase-4's `_author_fixtures.py`. The formula-WITHOUT-cache case is the *natural* openpyxl output (it never writes a cache). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| openpyxl | pandas (`read_excel`) | Heavy; pulls numpy (PKG hard rule: minimal core); coerces types and silently drops formula/merge structure — anti-faithful. Already gated behind the `panel` extra; do NOT use for the adapter. |
| openpyxl | xlrd | `.xls`-only; xlrd **removed** `.xlsx` support (security) — cannot read the target format. |
| openpyxl | xlsxwriter | **Write-only.** Cannot read. (Useful only if we needed to author fixtures via a second lib — openpyxl already does that.) |
| openpyxl standard mode | openpyxl `read_only=True` | Lower memory, BUT merged cells become unreadable `<EmptyCell>` and ad-hoc access is deprecation-warned — breaks faithful merge accounting. Rejected (Question B/F). |

**Installation:**
```bash
pip install ".[excel]"   # adds openpyxl; bare `pip install .` still runs the AI-free spine
```

**Version verification:** `pip index versions openpyxl` → latest `3.1.5`; full history back to 1.1.0 [VERIFIED: PyPI, run 2026-06-17].

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| openpyxl | PyPI | mature (1.x since ~2010; 3.1.5 current) | very high (tens of millions/mo class) | foss.heptapod.net/openpyxl/openpyxl (canonical home) | OK (override — see note) | Approved (CONTEXT pre-approved) |

**Note on the seam verdict:** `gsd-tools query package-legitimacy check --ecosystem pypi openpyxl` returned `SUS` with reasons `unknown-age`, `unknown-downloads`, `no-repository` — but every signal was `null` (`exists:null`, `publishedAt:null`, `weeklyDownloads:null`, `repoUrl:null`), i.e. the probe could not reach the registry in this sandbox, not that the package is genuinely suspicious. Independent verification overrides this: `pip index versions openpyxl` confirms the package exists with a 15-year release history ending at 3.1.5 [VERIFIED: PyPI], it is the library NAMED BY THE SPEC (ADAPT-03), and CONTEXT decision 1 PRE-APPROVED it (MIT, pure-Python, no telemetry). `postinstall` is N/A (PyPI/wheel has no npm-style postinstall; openpyxl ships as a pure-Python wheel). **Disposition: Approved.** The planner does NOT need a `checkpoint:human-verify` for openpyxl — it is spec-mandated and independently confirmed; the SUS verdict is a known offline-probe false-positive.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** openpyxl (offline-probe artifact only — overridden by independent PyPI verification + spec mandate; no checkpoint required).

## Architecture Patterns

### System Architecture Diagram

```
                       .xlsx bytes + path
                              │
                              ▼
            ┌───────────────────────────────────────┐
            │  ExcelAdapter.parse(raw, path)         │   (lazy: import openpyxl HERE)
            │                                        │
            │  load_workbook(BytesIO, data_only=F) ──┼─► FORMULA view  (cell.data_type=='f', cell.value=='=...')
            │  load_workbook(BytesIO, data_only=T) ──┼─► DATA view     (cached computed value or None)
            └───────────────┬───────────────────────┘
                            │ walk sheets in wb.worksheets order, row-major (iter_rows)
                            ▼
        ┌──────────────────────────────────────────────────────┐
        │  per cell, decide  (the faithful fork):                │
        │   • blank (both views None, not 'f')      → skip       │
        │   • literal value (str/int/float/bool/dt) → EMIT       │──┐ value→string (Q.C)
        │   • formula WITH cache (data view != None) → EMIT cache │  │
        │   • formula NO cache (data view None,'f')  → UNEXTRACTED│──┤
        │   • error string '#REF!' etc (data_type 'e')→ UNEXTRACTED│ │
        │   • merged non-anchor cell (None)          → skip (Q.E)  │ │
        └────────────────────────┬───────────────────────────────┘ │
                                  │                                  │
        workbook-level scan:      │                                  ▼
        merged ranges, +unreadable│        ┌──────────────────────────────┐
        features (charts/images/  │        │ canonical TRANSCRIPT           │
        pivots) → UNEXTRACTED ────┤        │  "Sheet!A1\t<value>\n" ...     │
                                  │        │  (sheet order, row-major)      │
                                  ▼        └──────────────┬─────────────────┘
        ┌──────────────────────────────────┐             │ units = [<value>, <value>, ...]
        │ unextracted[]  (the adapter drops)│             │  in transcript order
        │ encode → JSON → Source.context ───┼─────────────┼──────────┐
        └──────────────────────────────────┘             ▼          │ (TASK ZERO: travels WITH Source)
                                                  Source(transcript, │
                                                         context=JSON)│
                                                          │           │
                          ┌───────────────────────────────┘           │
                          ▼                                            │
            ExcelAdapter.distill(sources)  ◄── (may be a FRESH adapter, post model_dump_json reload)
                          │                                            │
                          │  for each source:                          │
                          │   units  = re-derive from transcript ──────┘ (deterministic re-split)
                          │   drops  = decode Source.context  ◄── coverage reconstructed from Source, not memory
                          ▼
                normalize(source, units) ─► Claim(+Trace via Trace.from_source)  + normalize-drops
                          │
                          ▼
            DistillationResult( Distillation, Coverage(complete = (len(all_drops)==0), unextracted=all_drops) )
```

### Recommended Project Structure
```
src/newsletters/adapters/
├── normalize.py            # UNCHANGED — the one faithful gate
├── _coverage_codec.py      # NEW (task zero): encode/decode unextracted[] <-> Source.context JSON  (shared)
├── email_adapter.py        # RETROFIT — write drops to Source.context in parse(); read them in distill()
├── excel_adapter.py        # NEW — lazy openpyxl; double-load; row-major transcript; drops -> Source.context
└── __init__.py             # register(ExcelAdapter()) alongside EmailAdapter

tests/
├── fixtures/xlsx/
│   ├── _author_fixtures.py # NEW — author byte-reproducible .xlsx (mirror eml/_author_fixtures.py)
│   └── *.xlsx              # committed golden corpus
├── test_excel_golden.py    # NEW — golden corpus (mirror test_email_golden.py)
└── test_coverage_roundtrip.py  # NEW (task zero) — round-trip coverage parity, parametrized over BOTH adapters
```

### Pattern 1: Lazy optional-dependency import (mirror the `[ai]` discipline)
**What:** Import openpyxl INSIDE the method that needs it, with a teaching error if absent.
**When to use:** Any adapter behind an optional extra; keeps bare install AI-free and `lint-imports` green.
**Example:**
```python
# Source: mirrors the [ai] lazy-import discipline (CLAUDE.md hard rule) + ports._enforce lazy import (ports.py:119-122)
def _load_openpyxl():
    try:
        import openpyxl  # noqa: PLC0415 — deliberately lazy (optional [excel] extra)
        return openpyxl
    except ImportError as e:  # pragma: no cover - exercised by the bare-install gate
        raise ImportError(
            "The Excel adapter needs openpyxl. Install it with: pip install '.[excel]'. "
            "The deterministic spine runs without it (AI-optional / minimal-core)."
        ) from e
```
The module-level imports of `excel_adapter.py` must NOT include openpyxl (so importing the module — which `adapters/__init__.py` does to `register()` — does not require the extra). The `import openpyxl` lives only inside `parse()`/its helper.

### Pattern 2: Double-load to distinguish formula-no-cache from blank (the crux)
**What:** Load the same bytes twice — once `data_only=False` (formula view), once `data_only=True` (data view) — and join on coordinate.
**When to use:** Always, for faithful Excel extraction.
**Example:**
```python
# Source: openpyxl tutorial — data_only "controls whether cells with formulae return the formula
# or the cached value from Excel's last save" [CITED: openpyxl.readthedocs.io/en/stable/tutorial.html]
import io
opx = _load_openpyxl()
data = raw  # bytes
wb_f = opx.load_workbook(io.BytesIO(data), data_only=False, read_only=False, keep_links=False)
wb_d = opx.load_workbook(io.BytesIO(data), data_only=True,  read_only=False, keep_links=False)
# read_only=False is REQUIRED: read_only makes merged cells unreadable (<EmptyCell>) — Q.F.
# keep_links=False: we do not resolve external workbook caches.
for ws_f, ws_d in zip(wb_f.worksheets, wb_d.worksheets):   # workbook order preserved
    for row_f, row_d in zip(ws_f.iter_rows(), ws_d.iter_rows()):  # row-major
        for cell_f, cell_d in zip(row_f, row_d):
            ... # the faithful fork (see value rules)
wb_f.close(); wb_d.close()
```

### Anti-Patterns to Avoid
- **Emitting `0`/`""` for an uncomputed formula cell.** This is the exact faithfulness violation ADAPT-03 criterion 2 forbids. `data_only=True` returns `None` for an uncached formula — route to `unextracted[]`, never fabricate a value.
- **Using `read_only=True`.** Merged cells become `<EmptyCell>` (merge structure lost) and ad-hoc access deprecation-warns — breaks faithful merge + silent-loss accounting. [VERIFIED: openpyxl-users list]
- **Using `cell.value` from the data view to decide "is this a formula?"** — a data-view formula cell shows its cache (or None), never `'='`. Decide formula-ness from the FORMULA view (`cell.data_type == 'f'`).
- **Reconstructing the transcript with a different value→string rule than the one that produced the units.** Units must be exact substrings of the transcript (the `normalize()` cursor-find depends on it). Build the transcript FROM the same canonical strings.
- **Storing drops in adapter instance memory** (the carried flaw). Drops must travel WITH the `Source` (task zero).
- **`pandas.read_excel`** — type-coerces, drops formulas/merges, pulls numpy. Forbidden for the adapter.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parse the `.xlsx` ZIP/OOXML | A custom XML/zip reader | `openpyxl.load_workbook` | OOXML is deceptively deep (shared strings, styles, number formats, merge XML at end of sheet). |
| Distinguish formula vs blank vs literal | A heuristic on `cell.value` | `cell.data_type` (`'f'`,`'s'`,`'n'`,`'b'`,`'e'`) + the data-view cache | openpyxl already classifies the cell type from the XML. |
| Detect error cells (`#REF!` etc.) | String matching every value | `cell.data_type == 'e'` (openpyxl sets `'e'` for the 7 error codes) | openpyxl maps `'#NULL!','#DIV/0!','#VALUE!','#REF!','#NAME?','#NUM!','#N/A'` to type `'e'`. [CITED: openpyxl cell module] |
| Find merged ranges | Scan for repeated/blank cells | `ws.merged_cells.ranges` | The merge set is authoritative XML; guessing is wrong. |
| Mint content-addressed traces | `hashlib` in the adapter | shared `normalize()` → `Trace.from_source` | ADAPT-01: one faithful rule, one place. Adapter NEVER hashes. |
| Serialize coverage across persistence | A bespoke sidecar file | JSON on `Source.context` (task zero) | `Source` already round-trips via `model_dump_json`; ride it. |

**Key insight:** The adapter's job is *decision-making* (extract vs. route-to-unextracted), not parsing — exactly as the Email adapter docstring says. openpyxl owns parsing; `normalize()` owns faithfulness; the adapter owns the honest fork and the coverage-on-Source plumbing.

## Runtime State Inventory

> Task zero is a refactor of how coverage persists. The "stored state" here is the adapter's in-memory dict — the thing being eliminated.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `EmailAdapter._adapter_unextracted: dict[str, list[Unextracted]]` (`email_adapter.py:134`) — drops keyed by `source.id`, populated in `parse()` (`:203`), read in `_units_for()` (`:364`). This is THE flaw. | **Code edit:** replace with encode-to-`Source.context` in `parse()` and decode-from-`Source.context` in `distill()`/`_units_for()`. No data migration (no persisted instances exist; `Source`s are re-`parse()`d). |
| Live service config | None — no external service stores this string. | None. |
| OS-registered state | None. | None. |
| Secrets/env vars | None. | None. |
| Build artifacts | `pyproject.toml` gains `excel = ["openpyxl"]` under `[project.optional-dependencies]`; a fresh `.xlsx` fixture corpus under `tests/fixtures/xlsx/`. No stale artifact to clean (new files only). | Add the extra; author fixtures. |

**Nothing found in categories** *Live service config / OS-registered state / Secrets*: verified — coverage is a pure in-process computation; the only persisted carrier today is the adapter instance dict, which is exactly what task zero removes.

## Common Pitfalls

### Pitfall 1: Formula-with-no-cache reads as `None` and looks blank
**What goes wrong:** `data_only=True` returns `None` for a formula cell whose cache Excel never wrote (openpyxl-saved files NEVER write a cache). If you only look at the data view, you cannot tell it from a truly empty cell — and emitting `0`/empty is a faithfulness violation.
**Why it happens:** openpyxl does not evaluate formulas; the cache is whatever Excel last stored, often nothing.
**How to avoid:** Double-load. Decide formula-ness from the FORMULA view (`cell.data_type == 'f'`). If formula AND data-view value is `None` → `unextracted[]` (reason names the cell + formula text). [CITED: openpyxl tutorial `data_only`]
**Warning signs:** A test fixture with a formula but no cache emits a claim with text `"0"` or `""`.

### Pitfall 2: read_only mode silently breaks merged-cell + feature accounting
**What goes wrong:** In `read_only=True`, merged cells return `<EmptyCell>` and `ws.merged_cells` is not populated the same way; you cannot account for merges, so "zero silent drops" is dishonest.
**Why it happens:** read_only lazy-loads cells before the merge XML (which lives at the end of the sheet) is parsed.
**How to avoid:** Use `read_only=False` (standard mode). [VERIFIED: openpyxl-users list "merged cells return `<EmptyCell>` … not possible to change" in read_only]
**Warning signs:** Merged fixture yields phantom blank cells or no merge disclosure.

### Pitfall 3: float repr drift (`0.1 + 0.2`)
**What goes wrong:** `str(0.1 + 0.2)` is `'0.30000000000000004'`; naive `repr`/formatting can change a value's text non-deterministically across platforms or lose precision.
**Why it happens:** IEEE-754. But `str(float)`/`repr(float)` in CPython 3.1+ is the *shortest round-tripping* decimal and is deterministic.
**How to avoid:** Use `repr(value)` for floats (shortest round-trip, lossless, deterministic in CPython). Do NOT use `f"{v:.2f}"` or `format()` with fixed precision. Keep `int` as `str(int)` (no `.0`). See value-rules table. [CITED: docs.python.org `repr`/float]
**Warning signs:** `1.0` vs `1`, or a long float string differing from the cell's true value.

### Pitfall 4: Duplicate cell values and the normalize() cursor
**What goes wrong:** Two cells with identical value strings — the second must locate at its OWN transcript offset, not re-point to the first.
**Why it happens:** `normalize()` uses a forward-only cursor `str.find(unit, cursor)` so duplicates get distinct offsets — but ONLY if the units are presented in transcript order and each value string appears in the transcript exactly where its unit is.
**How to avoid:** Emit units in the SAME row-major/sheet order as the transcript lines, and make each transcript line contain the value verbatim. The `Sheet!A1\t<value>\n` layout guarantees each value string is a distinct, ordered, locatable span (the prefix `Sheet!A1\t` separates adjacent values so a value never accidentally straddles two lines). [VERIFIED: `normalize.py:92-116` cursor logic]
**Warning signs:** A claim's `trace.start` points into the wrong cell's line.

### Pitfall 5: A value string that contains the separator or a newline
**What goes wrong:** A cell whose text contains `\t` or `\n` could break the line-oriented transcript or make a value non-locatable.
**Why it happens:** Excel string cells can contain tabs/newlines.
**How to avoid:** The value is still emitted verbatim as the unit (faithfulness), and `normalize()` locates it as a substring regardless of embedded `\t`/`\n` — the transcript line just visually spans more than one physical line. Do NOT escape/replace characters in the value (that would make `claim.text != transcript slice`). The separator choice (`\t`) only needs to not be ambiguous for a *human* reader; `normalize()` does pure substring matching, so correctness holds even with embedded separators. Add a fixture with a tab/newline-containing cell to prove it.
**Warning signs:** A multiline cell value routes to `unextracted[]` for "not locatable."

### Pitfall 6: Merged-range non-anchor cells read as `None`
**What goes wrong:** Emitting phantom blank claims for the N-1 covered cells of a merge, or losing the merge entirely.
**Why it happens:** In a merged range only the top-left anchor holds the value; the rest are `None`.
**How to avoid:** Emit the anchor value ONCE (it is a normal non-None cell in the walk). Skip the `None` covered cells (they are skipped anyway as blank). Additionally record a workbook-level disclosure of each merged range in `unextracted[]`? — **No: a merge is faithfully extracted (the anchor value is emitted), so it is NOT a drop.** Only record the merge *range* if the planner wants provenance; the value itself is not lost. Recommendation: do NOT add merges to `unextracted[]` (nothing is dropped); optionally note the range in the anchor's locator text if useful. (See Question E.)
**Warning signs:** A 2×2 merge produces 4 claims instead of 1, or `complete=False` with a spurious merge "drop."

## Code Examples

### The faithful per-cell fork (the heart of the adapter)
```python
# Source: openpyxl cell data_type constants [CITED: openpyxl.readthedocs.io .../cell/cell.html]
#   's' string, 'n' numeric, 'b' bool, 'd' date, 'e' error, 'f' formula
def _cell_decision(cell_f, cell_d, value_to_str):
    """Return ('emit', text) | ('skip', None) | ('unextracted', reason)."""
    if cell_f.data_type == 'f':
        # FORMULA. The data view holds the cache; None => uncomputed.
        cached = cell_d.value
        if cached is None:
            return ('unextracted',
                    f"formula cell {cell_f.coordinate} has no cached value "
                    f"(uncomputed: {cell_f.value!r}) — not faithfully extractable")
        if isinstance(cached, str) and cached in _ERROR_CODES:    # cache can itself be an error
            return ('unextracted', f"formula cell {cell_f.coordinate} evaluates to error {cached}")
        return ('emit', value_to_str(cached))
    if cell_f.data_type == 'e':
        return ('unextracted', f"error cell {cell_f.coordinate}: {cell_f.value}")
    if cell_f.value is None:
        return ('skip', None)                                     # genuinely blank (incl. merge-covered)
    return ('emit', value_to_str(cell_f.value))                   # literal str/int/float/bool/datetime
```

### Canonical value → string (deterministic, lossless)
```python
# Source: docs.python.org datetime.isoformat / repr(float) shortest-round-trip
from datetime import datetime, date, time
_ERROR_CODES = {'#NULL!', '#DIV/0!', '#VALUE!', '#REF!', '#NAME?', '#NUM!', '#N/A'}

def value_to_str(v) -> str:
    if isinstance(v, bool):       return "TRUE" if v else "FALSE"   # bool BEFORE int (bool is an int subclass!)
    if isinstance(v, int):        return str(v)                     # 1 -> "1", never "1.0"
    if isinstance(v, float):      return repr(v)                    # shortest round-trip; 1.0 -> "1.0", 0.1+0.2 -> exact
    if isinstance(v, datetime):   return v.isoformat()              # 'YYYY-MM-DDTHH:MM:SS[.ffffff]'
    if isinstance(v, date):       return v.isoformat()              # 'YYYY-MM-DD'
    if isinstance(v, time):       return v.isoformat()              # 'HH:MM:SS'
    return str(v)                                                   # str passes through verbatim
```

### Workbook-level silent-loss detection (charts / images / pivots)
```python
# Source: openpyxl docs — "images and charts will be lost from existing files"; pivots may raise.
def _feature_drops(wb_f) -> list[str]:
    out = []
    for ws in wb_f.worksheets:
        # openpyxl exposes parsed charts/images it COULD read; their mere presence is a disclosure
        # (we extract no chart/image CONTENT — deferred). Pivots/comments/data-validations similarly.
        for n in getattr(ws, "_charts", []):  out.append(f"{ws.title}: chart not extracted")
        for n in getattr(ws, "_images", []):  out.append(f"{ws.title}: image not extracted")
    return out
# NOTE: openpyxl does not read every OOXML item; some (pivot caches, shapes, comments in some paths)
# are simply absent from the object model — see Question F for the honest-limits caveat.
```

### Task-zero coverage codec on Source.context (shared by both adapters)
```python
# Source: docs.python.org json (sort_keys deterministic) + Pydantic model_dump (round-trips for free)
import json
from ..distill.coverage import Unextracted

_COVERAGE_KEY = "newsletters.adapter_unextracted"   # namespaced so context stays human/forward-compatible

def encode_coverage(path: str, drops: list[Unextracted]) -> str:
    """Return the JSON to store on Source.context, carrying the adapter's drops WITH the Source."""
    payload = {
        "source_path": path,
        _COVERAGE_KEY: [u.model_dump(mode="json") for u in drops],
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)

def decode_coverage(context: str) -> list[Unextracted]:
    """Reconstruct the adapter's drops from a (possibly round-tripped) Source.context. Total: never raises."""
    try:
        payload = json.loads(context)
        raw = payload.get(_COVERAGE_KEY, [])
    except (ValueError, AttributeError):
        return []                                   # a Source not produced by an adapter -> no drops
    return [Unextracted.model_validate(item) for item in raw]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Adapter drops in instance dict keyed by `source.id` (`email_adapter.py:134`) | Drops encoded on `Source.context` (pure function of the Source) | This phase (task zero) | Coverage survives `model_dump_json` round-trip + fresh adapter; "no silent drops" holds across persistence. |
| xlrd for `.xlsx` | openpyxl | xlrd 2.0 (2020) dropped `.xlsx` for security | openpyxl is the only maintained pure-Python `.xlsx` reader. |
| `cell.style`/positional reads | `cell.data_type` + double-load `data_only` | openpyxl 2.x+ | Type-aware faithful extraction; cache-gap detection. |

**Deprecated/outdated:**
- `ws.merged_cell_ranges` (property) → use `ws.merged_cells.ranges`. [CITED: openpyxl worksheet API deprecation note]
- xlrd `.xlsx` support — removed; do not use.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `ws._charts` / `ws._images` are the attributes exposing parsed drawings to detect chart/image presence | Code Examples (feature drops), Question F | LOW — these are internal attrs; the planner should add a fixture and verify the exact attribute name against the installed openpyxl 3.1.5 in a Wave-0 probe. Public alternative: parse fails to surface them at all (then the disclosure is simply "openpyxl does not read drawings" stated once). The faithfulness guarantee does not depend on the exact attr — worst case we disclose conservatively. |
| A2 | Storing JSON on `Source.context` does not collide with any existing consumer of `context` | Question A | LOW — Email today sets `context = path` (a plain string); no code parses `context` semantically (grep shows only assignment). The codec keeps `source_path` inside the payload so the human-facing path is preserved. Planner should grep `\.context` to confirm no consumer assumes a bare path. |
| A3 | `repr(float)` is deterministic across the target CPython versions (shortest round-trip) | Question C | LOW — true for CPython ≥3.1; project targets py3.12 (`pyproject` mypy `python_version=3.12`). |
| A4 | A `datetime` cell surfaces as a Python `datetime`/`date`/`time` via openpyxl (not a raw serial) when the cell has a date number-format | Question C | LOW — openpyxl converts date-formatted cells to datetime by default; verify with the date fixture. Edge: a date-formatted cell with a non-date value still typed `'n'`. |

**If this table is empty:** it is not — all four are LOW risk and pinned by a Wave-0 probe or a fixture; none blocks planning.

## Open Questions

1. **`CellLocator` typed variant vs `FreeLocator(text="Sheet!A1")`.**
   - What we know: `locators.py:67` stubs `CellLocator(kind="cell"; sheet; ref)` as a documented-but-unbuilt variant; the Email adapter uses `FreeLocator`. The `Locator` union (`locators.py:77`) currently contains only `FreeLocator` + `SessionLocator`.
   - What's unclear: whether to build `CellLocator` now (adds it to the discriminated union — a schema change) or carry `sheet!cell` as `FreeLocator(text=...)`.
   - Recommendation: **Use `FreeLocator(text="Sheet!A1")`** for the unextracted entries' locators (matches the Email pattern, no schema change, ADAPT-03 only requires the `sheet!cell` locator be *carried*, which `FreeLocator.text`/`display` does). Note: claim traces themselves get their locator from `Trace.from_source`'s default `FreeLocator()` via `normalize()`; the `sheet!cell` address is preserved in the transcript line prefix and recoverable. If the planner wants first-class cell addresses on every claim trace, that is a `normalize()` signature change (out of the one-place rule's current shape) — flag as a deliberate decision, do NOT smuggle it.

2. **Should the workbook-level merged-range be disclosed at all?**
   - What we know: the anchor value IS extracted, so nothing is dropped.
   - What's unclear: whether reviewers want merge provenance.
   - Recommendation: do NOT add merges to `unextracted[]` (no drop). Optionally include the range string (e.g. `"A1:B2"`) in the emitted claim's context for provenance — but only if cheap; not required for ADAPT-03.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | spine + adapter | ✓ | 3.12 (project target) | — |
| openpyxl | Excel adapter (`[excel]` extra) | ✗ (not yet declared) | 3.1.5 (to add) | None — adapter requires it; bare install runs spine without the adapter (by design) |
| stdlib `json`, `datetime`, `io` | task-zero codec, value rules, BytesIO load | ✓ | stdlib | — |

**Missing dependencies with no fallback:** openpyxl is required *for the adapter only*; the spine (and `pip install .`) intentionally runs without it. Planner must add `excel = ["openpyxl"]` and ensure the bare-install/import-isolation test still passes (openpyxl imported lazily, not at module top).

**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (declared in `[project.optional-dependencies] test`/`dev`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`pythonpath=["src"]`, `testpaths=["tests"]`) |
| Quick run command | `.venv/bin/python -m pytest tests/test_excel_golden.py -q` |
| Full suite command | `.venv/bin/python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADAPT-03 | Uncomputed formula → unextracted, never `0`/empty | unit/golden | `pytest tests/test_excel_golden.py -k formula_no_cache -x` | ❌ Wave 0 |
| ADAPT-03 | Cell value → verbatim, content-addressed `Claim(+Trace)` with `sheet!cell` locator | golden | `pytest tests/test_excel_golden.py -k verbatim -x` | ❌ Wave 0 |
| ADAPT-03 | Merged range emits anchor once, no phantom blanks | golden | `pytest tests/test_excel_golden.py -k merged -x` | ❌ Wave 0 |
| ADAPT-03 | Error cell + chart/image → unextracted (zero silent drops) | golden | `pytest tests/test_excel_golden.py -k silent_drops -x` | ❌ Wave 0 |
| ADAPT-06 | Byte-reproducible fixtures + accounting identity + determinism + conformance + JSON round-trip | golden | `pytest tests/test_excel_golden.py -q` | ❌ Wave 0 |
| (task zero) | Round-trip coverage parity for BOTH adapters | conformance | `pytest tests/test_coverage_roundtrip.py -q` | ❌ Wave 0 |
| (regression) | Bare install (no `[excel]`) still imports adapters package + runs spine | unit | `pytest tests/test_ai_optional.py -q` (extend) | exists; extend |

### Sampling Rate
- **Per task commit:** `pytest tests/test_excel_golden.py -q` (+ `tests/test_coverage_roundtrip.py` once it exists)
- **Per wave merge:** `pytest -q` (full suite — currently `177 passed, 1 xfailed`; must stay green) + `mypy src/newsletters/adapters src/newsletters/distill` + `lint-imports`
- **Phase gate:** full suite green + `lint-imports` `Contracts: 1 kept, 0 broken` before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/fixtures/xlsx/_author_fixtures.py` — author the byte-reproducible `.xlsx` corpus (mirror `eml/_author_fixtures.py`)
- [ ] `tests/test_excel_golden.py` — golden corpus test (mirror `test_email_golden.py` assertions)
- [ ] `tests/test_coverage_roundtrip.py` — round-trip coverage-parity, parametrized over `[EmailAdapter, ExcelAdapter]`
- [ ] `src/newsletters/adapters/_coverage_codec.py` — shared encode/decode (task zero)
- [ ] Extend `tests/test_ai_optional.py` — assert importing `newsletters.adapters` works WITHOUT openpyxl, and that calling `ExcelAdapter().parse(...)` without it raises the teaching `ImportError`
- [ ] Add `excel = ["openpyxl"]` to `pyproject.toml`

## Security Domain

> `security_enforcement: true`, ASVS level 1. This phase ingests UNTRUSTED `.xlsx` files (a ZIP container) — the relevant threat is malicious/oversized archives.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — (no auth in this phase) |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | openpyxl parses the OOXML; treat all cell text as untrusted data (never `eval`/format-inject). Catch parse exceptions and route to `unextracted[]` rather than crashing (mirror Email's defect handling). |
| V6 Cryptography | no | — (encrypted `.xlsx` is out of scope; if encountered, openpyxl raises → catch → `unextracted[]`) |

### Known Threat Patterns for openpyxl / `.xlsx` ingest
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Zip-bomb / decompression bomb (`.xlsx` is a ZIP) | DoS | openpyxl has internal guards but is not a sandbox. Bound input size BEFORE load (the caller already controls file selection; mirror Email's T-04-05 "never decode unbounded payloads" posture — do not eagerly read every cell of an unbounded sheet in a hostile context). Document as a known limit; not a blocker for trusted local files. |
| XML external entity (XXE) / billion-laughs | Tampering / DoS | openpyxl uses `lxml`/stdlib XML with entity resolution disabled by default for OOXML; no external DTD fetch. Confirm no `resolve_entities` is enabled (openpyxl default is safe). |
| Formula injection (CSV/Excel) | Tampering | We READ, never re-emit to a spreadsheet; cell text becomes plain `Claim.text`. No formula is executed (openpyxl does not evaluate). Low risk. |
| Malformed/partial archive | DoS | Wrap `load_workbook` in try/except; a parse failure becomes an `unextracted[]` disclosure for the whole source, never an unhandled crash (faithful: we disclose we could not read it). |

**Block-on-high:** none of the above are HIGH for the trusted-local-file use case; the zip-bomb/oversize concern is documented as a known limit with a bounded-input recommendation, consistent with the Email adapter's DoS posture.

## Sources

### Primary (HIGH confidence)
- PyPI via `pip index versions openpyxl` — confirmed 3.1.5 latest, full release history (existence + maturity).
- openpyxl tutorial — `load_workbook` params (`data_only`, `read_only`, `keep_vba`, `keep_links`), cell access, `data_only` semantics. https://openpyxl.readthedocs.io/en/stable/tutorial.html
- openpyxl cell module source — `TYPE_STRING='s'`, `TYPE_FORMULA='f'`, `TYPE_NUMERIC='n'`, `TYPE_BOOL='b'`, `TYPE_ERROR='e'`, `TYPE_NULL='n'`, `TYPE_INLINE='inlineStr'`, `TYPE_FORMULA_CACHE_STRING='str'`, `'d'` internal date type, the 7 ERROR_CODES, `is_date`. https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/cell/cell.html
- openpyxl worksheet API — `ws.merged_cells.ranges` (deprecates `merged_cell_ranges`), `iter_rows`, `max_row/max_column`, `calculate_dimension`. https://openpyxl.readthedocs.io/en/stable/api/openpyxl.worksheet.worksheet.html
- openpyxl optimized/read-only docs — `ReadOnlyCell`, must `close()`, `iter_cols` unavailable in read_only. https://openpyxl.readthedocs.io/en/stable/optimized.html
- docs.python.org — `datetime.isoformat`, `repr(float)` shortest round-trip, `json.dumps(sort_keys=True)`. https://docs.python.org/3/library/datetime.html , https://docs.python.org/3/library/json.html
- Live repo — `normalize.py`, `email_adapter.py` (the flaw at `:134/:203/:364`), `coverage.py`, `ports.py`, `conformance.py`, `semantic.py` (`Source`/`Trace`), `locators.py`, `04-VERIFICATION.md` (exact flaw description).

### Secondary (MEDIUM confidence)
- openpyxl-users mailing list + docs search — read_only merged cells return `<EmptyCell>`; "images and charts will be lost from existing files"; pivots without worksheet sources raise. https://groups.google.com/g/openpyxl-users/c/pdDdIvp_YYY , https://openpyxl.readthedocs.io/en/stable/changes.html

### Tertiary (LOW confidence)
- `ws._charts` / `ws._images` internal attribute names for drawing detection (assumption A1 — Wave-0 probe against installed 3.1.5).

## Metadata

**Confidence breakdown:**
- Standard stack (openpyxl 3.1.5, no other dep): HIGH — PyPI-verified, spec-named, alternatives ruled out.
- Architecture / task-zero mechanism (`Source.context` JSON codec): HIGH — derived from the live model (`Source.context` is a free string that round-trips; `Coverage` validator already enforces the honesty invariant) + the exact flaw in `04-VERIFICATION.md`.
- Formula-cache rule + value→string + merged + data_type constants: HIGH — confirmed against openpyxl docs/source.
- Silent-loss enumeration (charts/images/pivots/read_only): MEDIUM-HIGH — confirmed loss exists; exact detection attribute (`_charts`/`_images`) is LOW (A1).
- Pitfalls: HIGH — grounded in the cited semantics + the `normalize()` cursor logic.

**Research date:** 2026-06-17
**Valid until:** ~2026-07-17 (openpyxl is stable/slow-moving; 30 days). Re-confirm the `_charts`/`_images` attribute names against the installed version in Wave 0.
