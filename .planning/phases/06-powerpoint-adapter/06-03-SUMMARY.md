---
phase: 06-powerpoint-adapter
plan: 03
subsystem: api
tags: [python-pptx, pptx, adapter, distill, normalize, faithful-extraction, coverage, smartart, determinism]

# Dependency graph
requires:
  - phase: 06-01
    provides: "deterministic_timestamp() shared helper (None -> EPOCH_ZERO, never now())"
  - phase: 06-02
    provides: "_pptx_loader.load_presentation (lazy python-pptx) + the SmartArt diagram-URI recipe + the bare-install gate"
  - phase: 05
    provides: "_coverage_codec (encode/decode/not_reconstructable_marker) + Source.extraction carrier"
  - phase: 04
    provides: "normalize() shared faithful gate + ExcelAdapter structural template"
provides:
  - "PptxAdapter registered 'pptx' — parse(raw,path)->(Source,units,drops) + DistillPort distill(sources)"
  - "Faithful verbatim slide/shape/notes text -> content-addressed Claim(+Trace) with 'Slide N / <shape>' locators (criterion 1)"
  - "Full unextracted[] taxonomy: SmartArt/chart/picture/media/OLE/unknown-graphic-frame/whole-source (criterion 2)"
  - "Nested-group recursion with the leaf-accounting identity (zero silent drops, L3)"
  - "A reusable per-shape emit/report fork + an anchored Slide-N transcript record-boundary regex"
affects: [06-04, golden-corpus, parity-matrix, determinism-matrix]

# Tech tracking
tech-stack:
  added: []  # python-pptx was added by 06-02; this plan only consumes it
  patterns:
    - "Structural clone of ExcelAdapter: parse builds transcript+units+drops carried on Source.extraction; distill re-derives via normalize()"
    - "Recursive shape walk: GROUP recursed (never reported), each LEAF emits >=1 unit OR is skipped-empty OR is one drop"
    - "Crash-free graphic-frame URI read: primary accessor + lxml fallback -> unknown frames reported, never dropped"

key-files:
  created:
    - "src/newsletters/adapters/pptx_adapter.py"
    - "tests/test_pptx_adapter.py"
  modified:
    - "src/newsletters/adapters/__init__.py"

key-decisions:
  - "python-pptx's core_properties.created returns None faithfully when dcterms:created is absent (probed) — UNLIKE openpyxl which fabricates now(); so the raw-XML intrinsic_created workaround (06-01 note) is NOT needed for pptx. Used core_properties.created directly, guarded by isinstance(datetime)."
  - "Stable locator = FreeLocator('Slide N / <shape.name>'); table cells append '[r{r}c{c}]'; notes use 'Slide N / notes'. shape.name (not shape_id) chosen for human readability; normalize()'s forward cursor disambiguates duplicate values."
  - "Notes emitted LAST per slide (after the slide's shapes) — a documented, stable transcript position."
  - "Empty/whitespace-only paragraphs and empty cells are skipped-empty (no unit, no drop), mirroring Excel's blank-cell skip; a payload-free placeholder with no taxonomy match is also skipped-empty."

patterns-established:
  - "Per-shape emit/report ladder: has_table -> per-cell; has_chart -> report; has_text_frame -> per-paragraph (\\v kept verbatim); else _classify_unreadable."
  - "Anchored record-boundary regex (^Slide \\d+ / ...\\t) so values containing \\n/\\v/\\t round-trip through distill()."

requirements-completed: [ADAPT-04]

# Metrics
duration: ~35min
completed: 2026-06-17
---

# Phase 6 Plan 03: PowerPoint Adapter Core (PptxAdapter) Summary

**PptxAdapter — a structural clone of ExcelAdapter that walks slides/shapes (groups recursed) into verbatim per-paragraph/per-cell/notes Claims via the shared normalize(), routes the full SmartArt/chart/picture/media/OLE unreadable taxonomy to unextracted[] with zero silent drops, registers "pptx", and is deterministic + round-trip-parity-clean.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-06-17T16:40Z
- **Tasks:** 2 (both TDD: RED→GREEN)
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- `PptxAdapter.parse` walks `prs.slides` in deck order, each `slide.shapes` in document order, RECURSES `GroupShape.shapes` (nested), emits notes last; builds one canonical transcript + ordered verbatim units + `unextracted[]`.
- Per-paragraph text-frame units, per-cell table units (row-major), per-paragraph notes — `\v` soft breaks kept VERBATIM so `claim.text == transcript slice`.
- Full unreadable taxonomy routed to `unextracted[]`: chart/picture/media/OLE by `shape_type`; SmartArt by the diagram `@uri` (primary `graphicData_uri` accessor + lxml `<a:graphicData>/@uri` fallback); any unknown graphic frame reported "unknown graphic frame", never dropped.
- Nested-group leaf-accounting identity holds; malformed `.pptx` disclosed as one whole-source drop + empty transcript (V5), never a crash.
- `distill()` mints content-addressed claims via `normalize()`, merges adapter+normalize drops into one `Coverage`, fires the R2 not-reconstructable marker only for orphan Sources; round-trip coverage parity holds on a FRESH adapter.
- Registered "pptx", resolvable, `assert_conforms` passes; bare-install gate + lint-imports + mypy + full suite stay green.

## Task Commits

1. **Task 1 (RED): failing PptxAdapter parse/distill suite** - `f17da04` (test)
2. **Task 1 (GREEN): PptxAdapter.parse — walk/recursion/taxonomy** - `bfea9ec` (feat)
3. **Task 2 (GREEN): register "pptx" + distill via normalize()** - `947ef7d` (feat)

_The distill() + _units_for logic was authored in the Task-1 GREEN module file; Task 2's commit adds the registration that makes the registration/conformance/parity tests pass. No separate REFACTOR commit was needed (code was clean on first GREEN; mypy + lint green)._

## Files Created/Modified
- `src/newsletters/adapters/pptx_adapter.py` (created) - The PptxAdapter: `parse`, `distill`, `_units_for`, the recursive `_walk`, the `_emit_or_report` leaf fork, `_classify_unreadable`, `_graphic_data_uri`, the `_serialize` deck walk, and the `_RECORD_PREFIX`/`_split_transcript_units` round-trip pair.
- `tests/test_pptx_adapter.py` (created) - 19 unit tests authoring in-memory `.pptx` bytes (title/body, table, notes, picture, chart, nested group, XML-injected SmartArt) + malformed/determinism/registration/conformance/parity.
- `src/newsletters/adapters/__init__.py` (modified) - `register(PptxAdapter())` + `PptxAdapter` in `__all__`.

## Contract for Wave 3 (06-04 golden corpus)

- **Registered name:** `pptx` (`resolve("pptx")` -> `PptxAdapter`).
- **Signatures:** `parse(raw: bytes, path: str) -> (Source, list[str] units, list[Unextracted] drops)`; `distill(sources: list[Source]) -> DistillationResult` (backend `"pptx"`).
- **Transcript layout:** `"{prefix}\t{value}\n"` per emitted text unit, NEVER escaped. Prefixes:
  - text frame: `Slide {n} / {shape.name}`
  - table cell: `Slide {n} / {shape.name} [r{r}c{c}]`
  - notes: `Slide {n} / notes`
- **Stable locator:** `FreeLocator(text=<prefix above>)`. Chosen identifier is `shape.name` (human-readable; duplicates are fine — normalize()'s forward cursor disambiguates duplicate VALUES).
- **EXACT unextracted reason strings (pin these):**
  - chart: `"chart not extracted (chart data is out of scope)"`
  - picture: `"image not extracted (picture content out of scope)"`
  - media: `"media (audio/video) not extracted"`
  - OLE (embedded or linked): `"embedded/linked OLE object not extracted"`
  - SmartArt: `"SmartArt/diagram not extracted (no high-level API)"`
  - unknown graphic frame: `"unknown graphic frame ({uri}) not extracted"` (uri interpolated)
  - whole-source unreadable: `"presentation could not be read by python-pptx ({error}) — not extractable"` (error = exception class name)
- **Group recursion + accounting rule:** a `GroupShape` (shape_type == GROUP) is recursed into (`group.shapes`), nested groups handled; the group node itself is NEVER a claim or a drop. Identity (holds with nesting): `count(leaf shapes recursively) == count(shapes producing >=1 unit) + count(skipped-empty) + count(unextracted-from-shapes)`. Notes + whole-source drops are separate (like Excel's feature drops).
- **Timestamp sourcing:** `core_properties.created` (guarded by `isinstance(..., datetime)`) -> `deterministic_timestamp(...)`. **python-pptx does NOT fabricate `created`** — it returns `None` faithfully when `dcterms:created` is absent (probed against python-pptx 1.0.2), so no raw-XML workaround was needed (unlike Excel's openpyxl `intrinsic_created`). Note: the python-pptx DEFAULT template embeds a fixed `2013-01-27T09:14:16Z` created date; that is deterministic (not wall-clock), so determinism holds.
- **Empty/whitespace frames:** skipped-empty (no unit, no drop). Empty paragraphs and empty cells are skipped; a payload-free placeholder with no taxonomy match is skipped-empty.

## Decisions Made
See `key-decisions` frontmatter. Headline: python-pptx `core_properties.created` is faithful (None when absent) — confirmed by a probe that stripped `dcterms:created` and observed `created == None` — so the Excel raw-XML `intrinsic_created` defense was unnecessary here.

## Deviations from Plan

None - plan executed exactly as written. The plan's optional flag (A4: confirm `row.cells` vs `table.iter_cells`) resolved to `table.rows`→`row.cells` (works, row-major); merged-cell handling was not exercised (no merged-cell fixture in this plan — 06-04 may add one).

## Issues Encountered
- The SmartArt fixture's first draft used `qn("dgm:relIds")`, but `dgm` is not in python-pptx's nsmap (KeyError). Resolved by stripping the table payload to leave an EMPTY `graphicData` with the diagram `@uri` — probed to yield `shape_type is None` + the diagram URI via BOTH the primary accessor and the lxml fallback. (Caught during fixture authoring, before the GREEN implementation — not a code bug.)
- A `SyntaxWarning: invalid escape sequence '\d'` in two docstrings (transcript-format documentation). Fixed by making the affected docstrings raw strings (`r"""`). No behavior change.

## Known Stubs
None. Every code path is wired and tested; no placeholder/TODO/empty-data stubs.

## Threat Flags
None. The adapter reads only shape TYPE + text (never embedded image/OLE/media bytes), wraps `Presentation()` in try/except (whole-source disclosure), and follows no external links — matching the plan's `<threat_model>` mitigations (T-06-06/07/08/09). No new security surface beyond the plan.

## Gate Results (re-run independently)
- `pytest tests/test_pptx_adapter.py -q` → 19 passed.
- `pytest -q` (full) → **316 passed, 1 xfailed** (baseline was 297 passed, 1 xfailed; +19 new).
- `mypy src/newsletters/adapters src/newsletters/distill` → Success, no issues (17 files).
- `lint-imports` → 1 kept / 0 broken.
- `python -c "import newsletters"` → bare import ok.
- `newsletters build` → rendered 9 surfaces + library index, no errors.

## TDD Gate Compliance
- RED gate: `test(06-03)` commit `f17da04` (failed with ModuleNotFoundError before the impl).
- GREEN gate: `feat(06-03)` commits `bfea9ec` (parse) and `947ef7d` (registration) after it.
- REFACTOR: none needed (first GREEN was mypy/lint clean).

## Next Phase Readiness
- 06-04 (golden corpus) can drive `resolve("pptx")` against committed `.pptx` fixtures (incl. SmartArt + nested groups) and join the parity + determinism matrices. The exact reason strings, transcript layout, locator format, group-accounting rule, timestamp sourcing, and skip rules are all pinned above.
- No blockers.

## Self-Check: PASSED
- FOUND: src/newsletters/adapters/pptx_adapter.py
- FOUND: tests/test_pptx_adapter.py
- FOUND: .planning/phases/06-powerpoint-adapter/06-03-SUMMARY.md
- FOUND commits: f17da04 (test), bfea9ec (feat parse), 947ef7d (feat register)

---
*Phase: 06-powerpoint-adapter*
*Completed: 2026-06-17*
