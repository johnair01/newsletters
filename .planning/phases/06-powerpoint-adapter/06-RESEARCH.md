# Phase 6: PowerPoint Adapter - Research

**Researched:** 2026-06-17
**Domain:** Deterministic faithful `.pptx` text extraction (python-pptx behind a lazy `[pptx]` extra) + a cross-adapter deterministic-timestamp front-fix
**Confidence:** HIGH (python-pptx API verified against the installed 1.0.2 sdist source; codebase patterns read directly)

## Summary

Phase 6 mirrors the Excel adapter (the most recent adapter) almost line-for-line: a stateless `PptxAdapter` whose `parse(raw, path)` builds one canonical text `transcript` + ordered verbatim `units` + an `unextracted[]` carried on `Source.extraction`, and whose `distill(sources)` re-derives units from the transcript and routes them through the shared `normalize()`. The format-specific work is a deterministic walk of `prs.slides` -> `slide.shapes` (document order), extracting paragraph text from text frames, table cells, and speaker notes, while reporting every shape the high-level API cannot read (SmartArt, charts, pictures, media, OLE, and unreadable group members) into `unextracted[]`. python-pptx 1.0.2 is MIT, mature (scanny/python-pptx, since 2013), and is the verified standard; it pulls `lxml`, `Pillow`, `XlsxWriter`, `typing_extensions` — all sandboxed behind the `[pptx]` extra, never core.

The Phase-0 front-fix is the higher-risk item: today email falls back to `Source._utcnow()` when there is no `Date`, and Excel falls back to the default factory `_utcnow()` when `properties.created` is `None`. That makes two parses of identical bytes produce non-equal `Source`s, breaking the determinism / round-trip-parity property for any real document lacking an intrinsic timestamp. The recommendation is a **single shared deterministic sentinel** (`EPOCH_ZERO = datetime(1970,1,1, tzinfo=timezone.utc)`) applied by one helper used by all three adapters. Because `Source.content_hash()` addresses `transcript` ONLY (verified: `semantic.py:71-83`), `timestamp` is NOT in the hash and NOT in the transcript — so claims/traces are provably unaffected; the fix changes only `Source` equality/round-trip determinism, exactly the property being protected.

**Primary recommendation:** Build `PptxAdapter` as a structural clone of `ExcelAdapter` (double-load is unnecessary — single `Presentation`), with a `_pptx_loader.py` lazy boundary mirroring `_openpyxl_loader.py`; detect SmartArt by the `graphicData_uri` diagram namespace (python-pptx returns `shape_type == None` for SmartArt); recurse into groups extracting member text and reporting only the unreadable members; and land the timestamp front-fix as a shared `EPOCH_ZERO` sentinel helper retrofitted to email + excel + pptx with one determinism test.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `.pptx` byte parsing | Adapter (`PptxAdapter.parse`) | `_pptx_loader` (lazy import boundary) | Format-specific; isolated behind the `[pptx]` extra |
| Faithful unit->Claim minting | `normalize()` (shared gate) | — | The ONE faithfulness rule lives only here (ADAPT-01) |
| Trace/hash minting | `Trace.from_source` (semantic spine) | — | Sole content-address path; adapters never hash |
| Coverage persistence | `Source.extraction` + `_coverage_codec` | `distill.coverage.Coverage` | Drops survive JSON round-trip (Phase-5 carrier) |
| Backend registration | `adapters/__init__.py` -> `distill.register` | — | Side-effect-on-import, AI-free, extra-free |
| Deterministic timestamp | shared `EPOCH_ZERO` helper (new) | `Source.timestamp` field | Front-fix touches the fallback only, not the spine |
| Conformance / parity | `distill.conformance.assert_conforms` | golden tests | Reused unchanged; adapter joins the parity matrix |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| python-pptx | 1.0.2 | Read `.pptx` slides/shapes/text/tables/notes | [VERIFIED: PyPI] MIT, scanny/python-pptx, the de-facto standard Python OOXML-pptx lib since 2013; named by ADAPT-04 + pre-approved in CONTEXT decision 1 |

### Supporting (transitive, pulled by python-pptx — NOT direct deps we add)
| Library | Version constraint | Role | Note |
|---------|---------|---------|-------------|
| lxml | >=3.1.0 | OOXML XML parsing engine | [VERIFIED: sdist PKG-INFO] C-extension — acceptable behind the extra |
| Pillow | >=3.3.2 | image handling for `add_picture` / image parts | [VERIFIED: sdist PKG-INFO] C-extension — **hard dep of python-pptx since 1.0.0**, not optional |
| XlsxWriter | >=0.5.7 | writing embedded chart workbooks | [VERIFIED: sdist PKG-INFO] pure-Python; only used on the AUTHOR/chart path |
| typing_extensions | >=4.9.0 | typing backports | [VERIFIED: sdist PKG-INFO] pure-Python |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| python-pptx | raw `zipfile` + `lxml` over OOXML | Re-implements the entire shape/text model by hand — violates "Don't Hand-Roll"; python-pptx already owns parsing |
| python-pptx | `python-pptx-ng` (a fork) | [ASSUMED] fork adds `has_smart_art` etc., but it is a less-trusted fork; CONTEXT pre-approved python-pptx — do NOT switch |

**Installation:**
```bash
pip install '.[pptx]'   # adds: pptx = ["python-pptx"]
```

**Version verification:** `pip index versions python-pptx` -> latest `1.0.2` (released 2024-08-07). [VERIFIED: PyPI] Dependency list extracted from the 1.0.2 sdist `PKG-INFO`. [VERIFIED: sdist PKG-INFO]

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| python-pptx | PyPI | first release 2013; 1.0.2 = 2024-08-07 | unknown via API (PyPI hides counts) | github.com/scanny/python-pptx | SUS (reason: `unknown-downloads` only) | **Approved** — pre-approved by CONTEXT decision 1; canonical repo, MIT, 11+ yr history |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** python-pptx — the `SUS` verdict is solely `unknown-downloads` (the PyPI JSON API does not expose download counts; this is a known false-positive vector, not a real risk signal). Repo is the canonical `scanny/python-pptx`, license MIT, no postinstall script, decade-old. **No human-verify checkpoint required** because the package is named in the requirement (ADAPT-04) AND pre-approved in CONTEXT decision 1 AND verified against the official repo. The planner SHOULD note the seam's `SUS` in the install task so a reviewer understands why it is acceptable.

No other new direct dependency is needed. Pillow/lxml are transitive C-extensions sandboxed in `[pptx]`; this is explicitly acceptable per CONTEXT decision 1.

## Architecture Patterns

### System Architecture Diagram

```
.pptx bytes + path
       |
       v
PptxAdapter.parse(raw, path)
       |
       |-- _pptx_loader.load_presentation(raw)   [LAZY import of python-pptx; ImportError -> teaching msg]
       |        |
       |        v
       |   Presentation(BytesIO(raw))   -> prs.slides (ordered)
       |
       |-- _serialize(prs):  for each slide (order) -> for each shape in slide.shapes (doc order)
       |        |                                    -> RECURSE into GroupShape.shapes
       |        |
       |        +--> readable text (text frame paras / table cells / notes)
       |        |        -> transcript line "Slide N / <shape>\t<text>\n"  + unit (verbatim <text>)
       |        |
       |        +--> unreadable shape (SmartArt / chart / picture / media / OLE / empty)
       |                 -> Unextracted(locator=FreeLocator("Slide N / <shape>"), reason=...)
       |
       |-- timestamp = _deterministic_timestamp(intrinsic=core_props.created)   [FRONT-FIX]
       |
       v
Source(id=path, context=path, transcript=..., extraction=encode_coverage(drops), timestamp=...)
   + units (transcript order)  + drops
       |
       v
PptxAdapter.distill([source])
       |-- _units_for(source): re-split transcript -> units ; decode_coverage(source.extraction) -> drops
       |-- normalize(source, units) -> (claims, norm_drops)     [SHARED faithful gate; mints Trace.from_source]
       |-- Coverage(complete = (drops+norm_drops == 0), unextracted = drops + norm_drops)
       v
DistillationResult(distillation, coverage, backend="pptx")   -> assert_conforms passes
```

### Recommended Project Structure
```
src/newsletters/adapters/
├── _pptx_loader.py     # NEW: lazy python-pptx boundary (mirror _openpyxl_loader.py)
├── pptx_adapter.py     # NEW: PptxAdapter (mirror excel_adapter.py structure)
├── _timestamps.py      # NEW (front-fix): EPOCH_ZERO + deterministic_timestamp() shared helper
├── excel_adapter.py    # RETROFIT: use deterministic_timestamp() instead of bare default
├── email_adapter.py    # RETROFIT: use deterministic_timestamp() instead of None->_utcnow()
├── normalize.py        # UNCHANGED (shared gate)
├── _coverage_codec.py  # UNCHANGED (reused)
└── __init__.py         # register(PptxAdapter())
```

### Pattern 1: Lazy loader boundary (mirror `_openpyxl_loader.py`)
**What:** A module with NO top-level `import pptx`; the import lives inside a `_load_pptx()` function that raises a teaching `ImportError` -> `pip install '.[pptx]'`.
**When to use:** Always — the bare-install + `lint-imports` gates assert grep-count 0 for `import pptx` edges reachable from `import newsletters`. `__init__.py` registers `PptxAdapter()` on import, so the loader MUST stay lazy.
**Example:**
```python
# Source: mirrors src/newsletters/adapters/_openpyxl_loader.py (verified pattern)
import io
from typing import Any

MISSING_PPTX_MESSAGE = (
    "The PowerPoint adapter requires the optional 'python-pptx' dependency. "
    "Install it with: pip install '.[pptx]'  (or: pip install newsletters[pptx]). "
    "The deterministic spine runs without it — python-pptx is needed only for .pptx extraction."
)

def _load_pptx() -> Any:
    try:
        import pptx  # type: ignore[import-untyped]  # noqa: PLC0415 — lazy, optional [pptx] extra
    except ImportError as exc:
        raise ImportError(MISSING_PPTX_MESSAGE) from exc
    return pptx

def load_presentation(raw: bytes) -> Any:
    pptx = _load_pptx()
    return pptx.Presentation(io.BytesIO(raw))  # bytes -> file-like (verified accepts BytesIO)
```

### Pattern 2: Recursive shape walk with exact group accounting
**What:** A generator/recursive function over `slide.shapes` that, for a `GroupShape`, recurses into `group_shape.shapes` rather than reporting the whole group. Each LEAF shape is either a claim-source (its text frame / table / notes) or an `unextracted[]` entry.
**When to use:** Always — the ROADMAP fixture has grouped shapes and asserts zero silent drops; the accounting identity must hold for nested groups.
**Example:**
```python
# Source: verified against python-pptx 1.0.2 src (shapes/group.py:53-61, shapes/base.py)
from pptx.enum.shapes import MSO_SHAPE_TYPE

def _walk(shapes, slide_no, units, lines, drops):
    for shape in shapes:                       # document order (verified: GroupShapes is ordered)
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            _walk(shape.shapes, slide_no, units, lines, drops)   # RECURSE — do not report the group itself
            continue
        _emit_or_report(shape, slide_no, units, lines, drops)    # leaf decision (see taxonomy)
```
**Counting identity (zero silent drops, with nesting):** every LEAF shape visited contributes EXACTLY ONE of: (a) >=1 emitted text unit, (b) a skipped-empty (no text frame content, no readable payload, and not in the unreadable taxonomy — e.g. an empty placeholder; mirror Excel's "blank cell skip"), or (c) one `unextracted[]` entry. A GROUP node itself contributes nothing (it is a container) — only its leaves count. Test the identity as: `count(leaf shapes recursively) == count(shapes that produced >=1 unit) + count(skipped-empty) + count(unextracted entries from shapes)`. (The whole-source-unreadable and notes entries are separate, like Excel's feature drops.)

### Anti-Patterns to Avoid
- **Reporting a whole GROUP as one drop:** loses the readable text of its members and inflates/deflates the count — recurse instead.
- **Using `text_frame.text` for the claim value across paragraphs:** it joins paragraphs with `\n` and soft breaks with `\v` (verified), making the claim a multi-paragraph blob that is harder to locate and audit. Prefer per-paragraph units (CONTEXT decision 3: "per-paragraph for auditable atoms").
- **Escaping cell/paragraph text in the transcript:** breaks `claim.text == transcript slice` (the Phase-3 span gate). Mirror Excel: never escape values; use a structural record prefix instead.
- **`now()` fallback for timestamp:** the exact bug the front-fix removes.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parse `.pptx` (zip + OOXML) | A `zipfile`+`lxml` slide/shape model | `pptx.Presentation` | python-pptx owns the entire shape/text/table/notes model and the edge cases |
| Detect chart/table/OLE in a graphic frame | XML sniffing | `has_chart`, `has_table`, `shape_type`, `ole_format` | First-class API (verified `shapes/graphfrm.py`) |
| SmartArt detection | guesswork | the `graphicData_uri` diagram-namespace check (below) | The ONLY reliable signal python-pptx exposes (no high-level SmartArt API) |
| Content hashing / trace minting | hashlib in the adapter | `normalize()` -> `Trace.from_source` | The sole minting path; adapters never hash (verified `normalize.py`) |
| Coverage persistence | instance dict by source.id | `Source.extraction` + `_coverage_codec` | Phase-5 carrier; survives JSON round-trip |

**Key insight:** Every faithfulness, hashing, and coverage-persistence concern is already solved upstream. Phase 6 is 90% a deterministic walk + a faithful emit/report decision per shape — the same shape as the Excel per-cell fork.

## Runtime State Inventory

> Phase 6 is greenfield-plus-retrofit (new adapter + a fallback change to two existing adapters). No stored data / live services / OS state involved.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — verified: adapters are stateless; no datastore keys on the renamed/changed path | none |
| Live service config | None — verified: no external services | none |
| OS-registered state | None | none |
| Secrets/env vars | None | none |
| Build artifacts | `pyproject.toml` gains `pptx` extra — after edit, `pip install '.[pptx]'` to materialize | reinstall with extra |

**Front-fix behavioral migration note (NOT a data migration):** email/excel `Source.timestamp` for a doc with no intrinsic timestamp CHANGES from "wall-clock at parse time" to `EPOCH_ZERO`. No persisted `Source` JSON exists in the repo to migrate (verified: fixtures are authored at test time), so this is a pure code change. Any consumer asserting "timestamp ~ now" in a test would need updating — search for such assertions during planning.

## Common Pitfalls

### Pitfall 1: SmartArt is invisible to `shape_type`
**What goes wrong:** A SmartArt diagram is a `graphicFrame` whose `shape_type` returns **`None`** (verified `shapes/graphfrm.py:98-119`) — `has_chart`/`has_table` are both `False` and there is **no `has_smart_art` in 1.0.2**. A naive walk silently drops it -> violates zero-silent-drops AND the ROADMAP fixture criterion.
**Why it happens:** python-pptx has no high-level SmartArt support; only the XML `graphicData uri` identifies it.
**How to avoid:** Detect via the `graphicData` URI. Reliable check:
```python
# Source: verified — pptx/spec.py URI constants + graphfrm.py shape_type logic
DIAGRAM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"
# graphic frames expose graphicData_uri on the underlying element:
uri = shape._element.graphicData_uri  # private but stable; or read via lxml find on a:graphicData/@uri
if uri == DIAGRAM_URI:
    # SmartArt -> unextracted
```
Prefer the public ladder first: `if shape.has_chart -> report chart; elif shape.has_table -> extract; elif shape.shape_type is None and <graphic frame> -> SmartArt -> report; ` then fall back to URI inspection. **Flag for planner:** `graphicData_uri` is an internal helper; confirm its name at implement time and add a lxml fallback (`shape._element.find('.//{...drawingml/2006/main}graphicData')`-style read of `@uri`) so a future rename does not crash — worst case report as "unknown graphic frame", never drop.
**Warning signs:** a fixture slide with SmartArt yields `complete=True`.

### Pitfall 2: Newline / soft-break semantics in text
**What goes wrong:** `text_frame.text` separates paragraphs with `\n` and soft line breaks with `\v` (vertical tab); `paragraph.text` uses `\v` for soft breaks and also translates `\n`. (Verified: python-pptx text API docs.) If the transcript stores one form and the unit another, `normalize()` fails to locate and falsely reports `unextracted`.
**How to avoid:** Pick per-paragraph granularity and use `paragraph.text` for BOTH the transcript line and the unit (same string -> guaranteed substring), exactly as Excel reuses one `value_to_str`. Do NOT normalize `\v` away (that would make the claim differ from the source slice). Normalize `\r\n`/`\r` -> `\n` ONCE at the boundary if present (mirror email_adapter.py:234), but keep `\v` verbatim.
**Warning signs:** paragraphs with soft breaks route to `unextracted` as "not verbatim-locatable".

### Pitfall 3: `shape.name` is not unique; `shape_id` is per-slide
**What goes wrong:** Multiple shapes can share a name ("TextBox 3"); using name alone in the locator is ambiguous. `shape_id` is a read-only positive int unique within a slide (verified) but not globally.
**How to avoid:** Compose the locator as `"Slide {n} / {shape.name}"` for human readability (mirrors Excel's `Sheet!A1` readability goal), and rely on `normalize()`'s forward-only cursor to give duplicate VALUES distinct spans (it already does this — verified `normalize.py:83-85`). The locator is a FreeLocator preview, not a uniqueness key, so duplicate names are acceptable. If a reviewer needs disambiguation, append `shape_id`: `"Slide {n} / {name} (id {shape_id})"`.
**Warning signs:** none functional — but a reviewer confused by two identical locators suggests adding the id.

### Pitfall 4: Charts have text but it is not plain prose
**What goes wrong:** `has_chart` is True; the chart has categories/series/title that look extractable, but chart "text" is structured data, not a faithful prose claim.
**How to avoid:** Conservative (CONTEXT "faithful, not suggestive"): report the WHOLE chart as one `unextracted[]` entry, like Excel reports charts. Do NOT cherry-pick the title. (If a future phase wants chart titles, that is a deliberate decision, not this phase.)
**Warning signs:** a claim whose text is a chart category label.

### Pitfall 5: Determinism — wall-clock leaks via `Presentation` and timestamp fallback
**What goes wrong:** (a) the front-fix bug; (b) python-pptx, when SAVING, stamps zip mtimes and may touch core-props — but Phase 6 only READS, so save-time non-determinism affects only FIXTURE AUTHORING, not extraction.
**How to avoid:** Front-fix per below. For fixtures, set `core_properties.created`/`modified` explicitly and (if byte-identical fixtures are required) freeze zip mtimes — see Fixture Authoring.
**Warning signs:** the determinism test (parse same bytes twice -> equal Source) fails.

## Code Examples

### Per-shape emit/report decision (the heart of ADAPT-04)
```python
# Source: verified against python-pptx 1.0.2 src (shapes/base.py, shapes/graphfrm.py, table.py, slide.py)
from pptx.enum.shapes import MSO_SHAPE_TYPE

def _emit_or_report(shape, slide_no, units, lines, drops):
    loc = f"Slide {slide_no} / {shape.name}"
    st = shape.shape_type

    # 1) Tables (graphic frame) -> extract every cell verbatim, row-major
    if shape.has_table:
        for r, row in enumerate(shape.table.rows):
            for c, cell in enumerate(row.cells):     # or table.iter_cells() (flattens merges)
                text = cell.text                      # verified attr
                if text:
                    lines.append(f"{loc} [r{r}c{c}]\t{text}\n"); units.append(text)
        return

    # 2) Charts -> report (faithful: chart data is not prose)
    if shape.has_chart:
        drops.append(_drop(loc, "chart not extracted (chart data is out of scope)")); return

    # 3) Text frames (text boxes, titles, body placeholders, auto shapes with text)
    if shape.has_text_frame:
        emitted = False
        for para in shape.text_frame.paragraphs:      # ordered
            text = para.text                          # \v for soft breaks (verified)
            if text:
                lines.append(f"{loc}\t{text}\n"); units.append(text); emitted = True
        if emitted:
            return
        # an empty text frame is a skipped-empty (like a blank cell), NOT a drop

    # 4) Unreadable taxonomy (no readable text frame / table)
    reason = _classify_unreadable(shape, st)          # see taxonomy table
    if reason is not None:
        drops.append(_drop(loc, reason))
    # else: a genuinely empty placeholder with no payload -> skipped-empty (no drop, no unit)
```

### `unextracted[]` taxonomy
```python
DIAGRAM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"

def _classify_unreadable(shape, st):
    if st == MSO_SHAPE_TYPE.PICTURE:            return "image not extracted (picture content out of scope)"
    if st == MSO_SHAPE_TYPE.MEDIA:              return "media (audio/video) not extracted"
    if st in (MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT, MSO_SHAPE_TYPE.LINKED_OLE_OBJECT):
                                                return "embedded/linked OLE object not extracted"
    if st == MSO_SHAPE_TYPE.CHART:             return "chart not extracted (chart data out of scope)"
    # SmartArt: shape_type is None on its graphicFrame -> URI check
    uri = getattr(shape._element, "graphicData_uri", None)
    if uri == DIAGRAM_URI:                     return "SmartArt/diagram not extracted (no high-level API)"
    if uri is not None:                         return f"unknown graphic frame ({uri}) not extracted"
    return None  # not in the unreadable taxonomy -> caller treats as skipped-empty
```

| Shape kind | Detection | Disposition | Suggested reason string |
|------------|-----------|-------------|--------------------------|
| Title / body placeholder / text box / auto-shape w/ text | `has_text_frame` + non-empty paragraphs | emit per paragraph | — |
| Table | `has_table` | emit per cell | — |
| Speaker notes | `slide.has_notes_slide` -> `notes_slide.notes_text_frame.text` | emit per paragraph, locator `Slide N / notes` | — |
| Chart | `has_chart` (also `shape_type==CHART`) | report | `chart not extracted (chart data is out of scope)` |
| SmartArt / diagram | graphic frame, `shape_type is None`, `graphicData_uri == DIAGRAM_URI` | report | `SmartArt/diagram not extracted (no high-level API)` |
| Picture / image | `shape_type == PICTURE` | report | `image not extracted (picture content out of scope)` |
| Media (audio/video) | `shape_type == MEDIA` | report | `media (audio/video) not extracted` |
| OLE object | `shape_type in {EMBEDDED_OLE_OBJECT, LINKED_OLE_OBJECT}` | report | `embedded/linked OLE object not extracted` |
| WordArt / text-on-path | usually an auto-shape with a text frame -> text extracts; if no readable frame, report | per case | `WordArt not faithfully extractable` (only if unreadable) |
| Group | `shape_type == GROUP` | RECURSE into members; report only unreadable members | (container — never a drop itself) |
| Empty placeholder / connector / line with no text | no readable payload, not in taxonomy | skipped-empty (no drop) | — |
| Whole presentation unreadable (corrupt bytes) | `Presentation()` raises | one whole-source drop + empty transcript | `presentation could not be read by python-pptx ({error}) — not extractable` |

### Front-fix: deterministic timestamp shared helper
```python
# NEW: src/newsletters/adapters/_timestamps.py
from datetime import datetime, timezone

# A documented, deterministic sentinel for "this document has no intrinsic timestamp".
# Chosen as the Unix epoch in UTC: unambiguous, sorts before any real document date,
# and is obviously a sentinel to a reviewer (1970-01-01T00:00:00+00:00).
EPOCH_ZERO = datetime(1970, 1, 1, tzinfo=timezone.utc)

def deterministic_timestamp(intrinsic: datetime | None) -> datetime:
    """Return the document's intrinsic timestamp, or the deterministic EPOCH_ZERO sentinel.

    NEVER returns now()/wall-clock — so two parses of identical bytes produce equal Sources
    (determinism + round-trip parity). tz-naive intrinsics are coerced to UTC for consistency.
    """
    if intrinsic is None:
        return EPOCH_ZERO
    if intrinsic.tzinfo is None:
        return intrinsic.replace(tzinfo=timezone.utc)
    return intrinsic
```
Retrofit each adapter so `Source(timestamp=deterministic_timestamp(...))` is ALWAYS passed explicitly (never the default factory):
- **email_adapter.py:** replace the conditional `**({"timestamp": timestamp} ...)` spread with `timestamp=deterministic_timestamp(timestamp)` (where `timestamp` is the `Date` datetime or `None`).
- **excel_adapter.py:** collapse the `if created is not None` branch into one `Source(..., timestamp=deterministic_timestamp(created))`.
- **pptx_adapter.py:** `created = getattr(prs.core_properties, "created", None); Source(..., timestamp=deterministic_timestamp(created if isinstance(created, datetime) else None))`.

**Why a sentinel over the alternatives:**
| Option | Verdict | Reason |
|--------|---------|--------|
| (i) fixed EPOCH_ZERO sentinel | **CHOSEN** | Deterministic, obvious-to-a-human, one constant, trivial test, no coupling to content |
| (ii) derive from content hash | rejected | Non-monotonic garbage datetime; couples timestamp to transcript; surprising to reviewers; offers no real benefit since timestamp is not addressed |
| (iii) leave `None` | rejected | `Source.timestamp` is non-optional (`datetime` with default_factory `_utcnow`) — making it Optional is a spine change touching every consumer; out of scope and riskier |

**Impact on content_hash / parity (CONFIRMED):** `Source.content_hash()` hashes `transcript` ONLY (verified `semantic.py:71-83`), and `timestamp` is metadata never written into the transcript. Therefore `Trace`s are content-addressed independent of timestamp; claims, traces, and the span gate are **provably unaffected**. The only thing the sentinel changes is `Source.__eq__` / `model_dump_json` determinism — exactly the property the front-fix exists to protect.

**Determinism test design:**
```python
# tests/test_timestamp_determinism.py
def test_no_intrinsic_timestamp_parses_byte_identical_twice(adapter, raw_bytes_no_date):
    s1, _, _ = adapter.parse(raw_bytes_no_date, "doc")
    s2, _, _ = adapter.parse(raw_bytes_no_date, "doc")
    assert s1.timestamp == EPOCH_ZERO
    assert s1.model_dump_json() == s2.model_dump_json()   # byte-identical Sources
# Parametrize over (EmailAdapter, .eml-without-Date), (ExcelAdapter, .xlsx-with-created=None),
# (PptxAdapter, .pptx-with-created=None). Also assert an intrinsic-timestamp doc still uses it.
```

### Transcript layout (canonical serialization)
Mirror Excel exactly: one physical record per emitted text unit, `"{locator-prefix}{SEP}{value}\n"`, where the prefix is a structural anchor NOT part of the claim, and the value is the verbatim paragraph/cell text appended to `units` unchanged.
- `SEP = "\t"` (same as Excel).
- Record prefix: `Slide {n} / {shape.name}` (text frame), `Slide {n} / {shape.name} [r{r}c{c}]` (table cell), `Slide {n} / notes` (notes).
- Re-derivation in `distill()` (`_units_for`): split on the record boundary using an anchored regex like Excel's `_RECORD_PREFIX` (a `Slide N / ...\t` line-start), so a value containing `\n`, `\v`, or `\t` still round-trips. **Flag:** the prefix grammar is freer than Excel's `Sheet!A1` (shape names can contain almost anything incl. `/`); design the boundary regex to anchor on `^Slide \d+ / ` + the `\t` separator, and confirm shape names cannot contain a newline (they cannot — OOXML attribute). Keep `\v` verbatim in both transcript and unit.

## Fixture Authoring Plan (ADAPT-06, byte-reproducible)

Mirror the Phase-4/5 programmatic generator. All authoring uses python-pptx high-level APIs except SmartArt (XML injection).

| Fixture element | API (verified python-pptx 1.0.2) | Note |
|-----------------|-----------------------------------|------|
| Title + body slide | `prs.slides.add_slide(layout)` then placeholder `.text_frame` | standard |
| Text box | `slide.shapes.add_textbox(l,t,w,h).text_frame` | verified `shapetree.py:389` |
| Table | `slide.shapes.add_table(rows,cols,l,t,w,h).table` | verified `shapetree.py:589` |
| Speaker notes | `slide.notes_slide.notes_text_frame.text = ...` | verified `slide.py:151-211` |
| Picture | `slide.shapes.add_picture(io.BytesIO(png_bytes), l, t)` | verified `shapetree.py:353`; accepts a file-like |
| Chart | `slide.shapes.add_chart(chart_type, x,y,cx,cy, CategoryChartData(...))` | verified `shapetree.py:236`; needs `pptx.chart.data.CategoryChartData` |
| Grouped shapes | create members first, then `slide.shapes.add_group_shape([s1, s2])` | **verified `shapetree.py:278-294`: members must ALREADY exist on the tree — `add_group_shape` MOVES them into the group**; for NESTED groups, add an inner group then group it |
| SmartArt | **no authoring API** — XML-inject a `graphicFrame` with `graphicData uri="...drawingml/2006/diagram"` + a `dgm:relIds` to a minimal `data1.xml` diagram part | mirror Phase-5's chart-fixture XML-injection precedent |
| Empty slide | `prs.slides.add_slide(blank_layout)` | for the empty-slide assertion |

**Fixture gotchas (flag for planner):**
1. **Pillow is a HARD dependency of python-pptx** (>=3.3.2, since 1.0.0) — it installs with `[pptx]` automatically. `add_picture` needs valid image bytes but does NOT require you to use Pillow yourself: a tiny hand-written valid PNG (a ~68-byte 1x1 PNG byte literal) embeds fine via `io.BytesIO`. So you can synthesize the image WITHOUT calling Pillow, even though Pillow is present. **Recommend: embed a constant 1x1 PNG byte literal** for byte-reproducibility (no Pillow call, no nondeterminism).
2. **Group authoring order:** `add_group_shape(shapes)` requires the shapes to be pre-existing on the slide; it re-parents them. Author members, capture their handles, THEN group. Nested = group an inner group.
3. **SmartArt requires manual OOXML parts** (`diagrams/data1.xml`, layout/colors/style rels) — the minimum to be DETECTED is a `graphicFrame` whose `a:graphicData/@uri` is the diagram namespace; the diagram itself can be a near-empty `dgm:dataModel`. Validate detection (`shape_type is None` + URI), not rendering. This is the single most involved fixture — budget a dedicated task.
4. **Byte-reproducibility:** set `prs.core_properties.created` and `.modified` to fixed datetimes; python-pptx writes the zip with python-pptx's own packaging — if the test asserts byte-identical `.pptx` files across runs, freeze zip member mtimes (python-pptx uses a fixed `Default` template; confirm at implement time whether re-save introduces wall-clock — if so, the determinism assertion should be on the PARSED `Source`, not on the `.pptx` bytes, which is sufficient for ADAPT-06).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-pptx 0.6.x (no Pillow hard dep, py2) | 1.0.x (Pillow/typing_extensions hard deps, py3.8+, typed) | 1.0.0 (2024) | Pillow is now unavoidable behind `[pptx]`; type hints improve mypy story |
| `has_smart_art` (proposed/fork) | NOT in upstream 1.0.2 — use `graphicData_uri` | — | Do not rely on `has_smart_art`; use the URI check |

**Deprecated/outdated:**
- `has_smart_art` property: appears in some docs/forks (python-pptx-ng) but is **absent in upstream 1.0.2** (verified by reading `shapes/graphfrm.py`). Use the diagram-URI check.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `shape._element.graphicData_uri` is the accessor for the graphic-frame URI | Pitfall 1 / taxonomy | LOW — name is internal; add lxml `@uri` fallback. SmartArt would mis-classify as "unknown graphic frame" (still reported, never dropped) |
| A2 | A 1x1 PNG byte literal embeds via `add_picture` without a Pillow call | Fixture gotchas | LOW — if Pillow validation rejects it, generate via Pillow (it is installed) |
| A3 | Re-saving a `.pptx` with python-pptx is byte-reproducible when core-props are fixed | Fixture gotcha 4 | MEDIUM — if not, assert determinism on the parsed `Source`, not the bytes (the property that actually matters) |
| A4 | `table.iter_cells()` / `row.cells` and `cell.text` are the cell-text accessors | Code example | LOW — verified the names exist in 1.0.2 table.py module surface; confirm `iter_cells` vs `rows[].cells` at implement time |
| A5 | No persisted `Source` JSON exists to migrate for the timestamp change | Runtime State Inventory | LOW — fixtures are authored at test time; grep for committed `*.json` Sources during planning |

## Open Questions

1. **Exact graphic-frame URI accessor name in 1.0.2.**
   - What we know: `shape_type` returns `None` for SmartArt; `graphicData_uri` is used internally (`graphfrm.py`).
   - What's unclear: whether it is reliably reachable as `shape._element.graphicData_uri` from a high-level `GraphicFrame`.
   - Recommendation: use the public ladder (`has_chart`/`has_table`/`shape_type`) first; for the `None` case, read `@uri` via lxml on the `<a:graphicData>` element as a stable fallback; never crash — unknown frames are reported, not dropped.

2. **Merged table cells.**
   - What we know: `table.iter_cells()` flattens; merged cells may repeat the span value or expose `cell.is_spanned`.
   - Recommendation: emit the merge ORIGIN cell's text once; treat spanned cells like Excel's merge-covered cells (skip, not a drop). Confirm the `is_spanned`/`span_height` API at implement time and add a merged-cell fixture if cheap.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python-pptx | the adapter (behind `[pptx]`) | ✓ (installable) | 1.0.2 | — (bare install must still import newsletters; adapter raises teaching ImportError) |
| Pillow (transitive) | python-pptx image parts | ✓ (pulled by `[pptx]`) | >=3.3.2 | — |
| lxml (transitive) | python-pptx XML | ✓ (pulled by `[pptx]`) | >=3.1.0 | — |

**Missing dependencies with no fallback:** none (all install via `pip install '.[pptx]'`).
**Missing dependencies with fallback:** the deterministic spine + bare install run with ZERO of the above (verified pattern from `[excel]`); the adapter is reachable only after installing the extra.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (configured in `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (`pythonpath=["src"]`, `testpaths=["tests"]`) |
| Quick run command | `pytest tests/test_pptx_adapter.py -x` |
| Full suite command | `pytest` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADAPT-04 | `.pptx` text frames/tables/notes -> verbatim content-addressed claims | unit | `pytest tests/test_pptx_adapter.py -x` | ❌ Wave 0 |
| ADAPT-04 | SmartArt/chart/picture/media/OLE -> `unextracted[]`, zero silent drops | unit | `pytest tests/test_pptx_adapter.py -k unextracted -x` | ❌ Wave 0 |
| ADAPT-04 | nested grouped shapes: members extracted, unreadable members reported, count identity holds | unit | `pytest tests/test_pptx_adapter.py -k group -x` | ❌ Wave 0 |
| ADAPT-06 | golden fixtures: verbatim + content-addressed + conformance + determinism + round-trip parity | golden | `pytest tests/test_pptx_golden.py -x` | ❌ Wave 0 |
| Decision 0 | no-intrinsic-timestamp -> byte-identical Sources twice (email+excel+pptx) | unit | `pytest tests/test_timestamp_determinism.py -x` | ❌ Wave 0 |
| Decision 1 | bare install + `lint-imports` + AI-isolation green WITHOUT `[pptx]` | guard | `pytest tests/test_ai_optional.py -x` (extend) | ✅ (extend existing) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_pptx_adapter.py -x`
- **Per wave merge:** `pytest tests/test_pptx_adapter.py tests/test_pptx_golden.py tests/test_timestamp_determinism.py tests/test_ai_optional.py`
- **Phase gate:** full `pytest` green before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_pptx_adapter.py` — covers ADAPT-04 (emit/report decisions, group recursion, taxonomy)
- [ ] `tests/test_pptx_golden.py` — covers ADAPT-06 (golden corpus + parity + determinism + conformance)
- [ ] `tests/test_timestamp_determinism.py` — covers Decision 0 across all three adapters
- [ ] `tests/fixtures/` pptx generator — byte-reproducible authoring incl. SmartArt (XML-inject) + nested group + 1x1 PNG image
- [ ] Extend `tests/test_ai_optional.py` to assert grep-count 0 for `import pptx` reachable from `import newsletters`, and assert `register("pptx")` works without the extra.
- [ ] Extend the round-trip parity matrix (Phase-5) with the `pptx` backend param.

## Security Domain

> `security_enforcement: true`, ASVS level 1. Relevant categories below.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | adapter handles files, not auth |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | **yes** | `.pptx` is UNTRUSTED input: wrap `Presentation()` in try/except and disclose a whole-source `unextracted[]` entry on failure — NEVER an unhandled crash (mirror `excel_adapter.py:234`). Do not follow external OLE/links; do not `get_or_add_image_part` on read. |
| V6 Cryptography | no | hashing is delegated to `Trace.from_source` (spine); adapter computes none |

### Known Threat Patterns for python-pptx / OOXML
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Zip-bomb / decompression DoS | DoS | python-pptx reads via `zipfile`; do not eagerly read embedded blobs (we never call `image.blob` / OLE bytes — we only read shape TYPE). Catch+disclose on parse error. |
| XML external entity (XXE) | Info disclosure / DoS | python-pptx uses lxml with entity resolution off by default for OOXML; do not enable custom resolvers. [ASSUMED] confirm lxml parse settings unchanged. |
| Malformed/corrupt `.pptx` crash | DoS | whole-source try/except -> `unextracted[]` (V5) |
| Embedded macro / OLE payload | Tampering | we NEVER extract or execute OLE/media bytes — only report their presence; no code path touches payloads |

## Sources

### Primary (HIGH confidence)
- python-pptx 1.0.2 sdist source (read directly): `src/pptx/shapes/graphfrm.py` (shape_type=None for SmartArt, has_chart/has_table, ole_format), `src/pptx/shapes/group.py` (GroupShape.shape_type==GROUP, `.shapes`), `src/pptx/shapes/shapetree.py` (add_group_shape moves members, add_picture/add_textbox/add_table/add_chart), `src/pptx/slide.py` (has_notes_slide/notes_slide/notes_text_frame), `src/pptx/spec.py` (GRAPHIC_DATA_URI_* constants), `PKG-INFO` (Requires-Dist: Pillow/XlsxWriter/lxml/typing_extensions; MIT; Requires-Python>=3.8)
- Codebase (read directly): `normalize.py`, `excel_adapter.py`, `email_adapter.py`, `_openpyxl_loader.py`, `_coverage_codec.py`, `locators.py`, `semantic.py` (content_hash addresses transcript only), `distill/{ports,registry,coverage,conformance}.py`, `pyproject.toml`

### Secondary (MEDIUM confidence)
- python-pptx docs — Text API (paragraph/text_frame `\n`/`\v` semantics): https://python-pptx.readthedocs.io/en/latest/api/text.html
- python-pptx docs — Shapes / GraphicFrame: https://python-pptx.readthedocs.io/en/latest/api/shapes.html

### Tertiary (LOW confidence)
- WebSearch on SmartArt detection (corroborated by source read): https://python-pptx.readthedocs.io/en/latest/dev/analysis/shp-graphfrm.html

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions/deps/license read from the actual sdist
- Architecture: HIGH — mirrors the verified Excel adapter; python-pptx API read from source
- Pitfalls: HIGH — SmartArt/newline/group behaviors verified in source
- Front-fix: HIGH — content_hash-excludes-timestamp confirmed in semantic.py; sentinel design is straightforward
- Fixture SmartArt authoring: MEDIUM — XML-injection path is correct but unbuilt (A1/A3)

**Research date:** 2026-06-17
**Valid until:** 2026-07-17 (python-pptx is stable/slow-moving; 30 days)
