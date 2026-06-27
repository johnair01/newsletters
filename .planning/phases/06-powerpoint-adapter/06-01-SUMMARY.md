---
phase: 06-powerpoint-adapter
plan: 01
subsystem: adapters
tags: [determinism, timestamp, email-adapter, excel-adapter, openpyxl, stdlib]

# Dependency graph
requires:
  - phase: 04-adapter-foundation
    provides: shared normalize() + adapter/DistillPort pattern + Coverage/unextracted[]
  - phase: 05-excel-adapter
    provides: ExcelAdapter, Source.extraction carrier + codec, round-trip parity matrix
provides:
  - "adapters/_timestamps.py — EPOCH_ZERO sentinel + deterministic_timestamp(intrinsic) shared helper"
  - "email + excel adapters always pass an explicit deterministic Source.timestamp (never wall-clock now())"
  - "intrinsic_created() — reads xlsx docProps created from raw OOXML (faithful None when absent)"
  - "tests/test_timestamp_determinism.py — parametrized cross-adapter determinism proof with a pptx seam"
affects: [06-03-pptx-adapter, 06-04-golden-fixtures]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deterministic adapter timestamp: always timestamp=deterministic_timestamp(<intrinsic-or-None>), never the Source _utcnow default factory"
    - "Read intrinsic metadata from RAW document bytes when the parsing library fabricates a wall-clock default"

key-files:
  created:
    - src/newsletters/adapters/_timestamps.py
    - tests/test_timestamp_determinism.py
  modified:
    - src/newsletters/adapters/email_adapter.py
    - src/newsletters/adapters/excel_adapter.py

key-decisions:
  - "Fixed EPOCH_ZERO sentinel (1970-01-01T00:00:00Z) for no-intrinsic-timestamp, not now() or content-derived — deterministic + obvious to a reviewer"
  - "Do NOT modify semantic.py: Source.timestamp stays non-optional with its _utcnow default (L1 option iii rejected); adapters always pass the value explicitly"
  - "Excel reads `created` from raw docProps/core.xml (stdlib zipfile+ElementTree), NOT wb.properties.created, because openpyxl fabricates a wall-clock `created or now()` when the element is absent"

patterns-established:
  - "deterministic_timestamp(intrinsic) is the single timestamp source for ALL file adapters; pptx joins it in 06-03"
  - "Determinism test parametrized across adapters with a documented seam — append one tuple to add an adapter"

requirements-completed: [ADAPT-04]

# Metrics
duration: ~20min
completed: 2026-06-17
---

# Phase 6 Plan 01: Deterministic Adapter Timestamp (Front Fix) Summary

**Shared `adapters/_timestamps.py` (EPOCH_ZERO + `deterministic_timestamp`) retrofits email + excel off the wall-clock `now()` fallback, with excel reading its intrinsic `created` from raw OOXML to defeat openpyxl's fabricated-timestamp determinism trap; proven by a parametrized cross-adapter determinism test.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-17T16:24Z
- **Completed:** 2026-06-17T16:28:45Z
- **Tasks:** 2 (TDD)
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- `adapters/_timestamps.py`: `EPOCH_ZERO = datetime(1970,1,1,tzinfo=utc)` + `deterministic_timestamp(intrinsic) -> datetime` returning the intrinsic value (tz-naive coerced to UTC) or `EPOCH_ZERO`, NEVER `now()`. Stdlib-only, no new dependency, safe for the bare AI-free core path.
- Both adapters ALWAYS pass `timestamp=deterministic_timestamp(...)` explicitly — no code path falls back to the `Source` `_utcnow` default factory (grep confirms only comments mention `now()`).
- Cross-adapter determinism proof: a no-Date `.eml` and a no-`created` `.xlsx` each parse to byte-identical Sources twice (`model_dump_json` equal) with `timestamp == EPOCH_ZERO`; intrinsic-timestamp docs still use their own date.
- Found and fixed a real determinism bug (see Deviations): openpyxl fabricates a wall-clock `created` when the docProps element is absent, which would have silently re-introduced the non-determinism the front-fix exists to remove.

## The `_timestamps.py` API (for 06-03 / 06-04)

```python
from newsletters.adapters._timestamps import EPOCH_ZERO, deterministic_timestamp

EPOCH_ZERO  # == datetime(1970, 1, 1, tzinfo=timezone.utc)  — tz-aware UTC

deterministic_timestamp(intrinsic: datetime | None) -> datetime
#   None        -> EPOCH_ZERO        (the deterministic "no intrinsic date" sentinel; NEVER now())
#   tz-aware dt -> dt                 (preserved verbatim)
#   tz-naive dt -> dt.replace(tzinfo=timezone.utc)   (coerced to UTC; deterministic)
```

Pure function (no clock, no state). `Source.content_hash()` hashes the transcript only, so the timestamp is excluded — Claims/Traces are provably unaffected.

**How each adapter sources its timestamp now:**
- **email** — the parsed `Date`-header datetime (`getattr(date_hdr, "datetime", None)`) or `None`, fed through `deterministic_timestamp`.
- **excel** — `intrinsic_created(raw)`: the `dcterms:created` element read from the raw `docProps/core.xml` (stdlib `zipfile` + `xml.etree`), parsed as W3CDTF (`Z` normalized to `+00:00`, tz-naive coerced to UTC), or `None` when the element is genuinely absent — fed through `deterministic_timestamp`. The unreadable-workbook path passes `deterministic_timestamp(None)` too.
- **pptx (06-03)** — will use `core_properties.created`-or-None through the same helper. NOTE: research L4 says to SET `core_properties.created` in fixtures for determinism; verify python-pptx does not fabricate a default like openpyxl does — if it can read back `None`, the raw-read trick is unnecessary; if it fabricates, mirror `intrinsic_created`.

**Determinism-test seam for pptx (06-04):** `tests/test_timestamp_determinism.py` `_DETERMINISM_CASES` is a list of `pytest.param(factory, no_intrinsic_bytes_loader, with_intrinsic_loader, id=...)`. Append one `(_pptx_factory, _pptx_no_created, _pptx_with_created)` tuple (skipif behind the `[pptx]` extra) — no test-body change. The seam comment marks the exact spot. Do NOT import python-pptx in this file (it lives behind the `[pptx]` extra gated in 06-02).

## Retrofit diff summary
- **email_adapter.py:** import `deterministic_timestamp`; annotate `timestamp: datetime | None` (added `from datetime import datetime`); replaced the conditional spread `**({"timestamp": timestamp} if timestamp is not None else {})` with `timestamp=deterministic_timestamp(timestamp)`; docstring updated to state the EPOCH_ZERO fallback.
- **excel_adapter.py:** import `deterministic_timestamp`, `io`, `zipfile`, `timezone`, `xml.etree.ElementTree`; added `intrinsic_created(raw)` helper; collapsed the `if created is not None: ... else: ...` Source-construction branch into a single `Source(..., timestamp=deterministic_timestamp(created))`; `created` now comes from `intrinsic_created(raw)` instead of `wb_formula.properties.created`; the unreadable-source path passes `timestamp=deterministic_timestamp(None)`.

## Task Commits

1. **Task 1 (RED): failing helper + determinism scaffold** - `3e99eb9` (test)
2. **Task 1 (GREEN): _timestamps.py helper** - `bf729e2` (feat)
3. **Task 2 (GREEN): retrofit email + excel + complete determinism proof** - `dbde976` (feat)

_TDD: Task 1 RED→GREEN; Task 2's behavior was authored in the same test file (RED at Task 1's commit since the parametrized adapter cases failed to collect without the helper), implemented in `dbde976`._

## Files Created/Modified
- `src/newsletters/adapters/_timestamps.py` - EPOCH_ZERO sentinel + deterministic_timestamp helper (stdlib only)
- `tests/test_timestamp_determinism.py` - helper-level tests + parametrized cross-adapter determinism proof (email + excel; pptx seam)
- `src/newsletters/adapters/email_adapter.py` - always pass deterministic_timestamp(Date-or-None)
- `src/newsletters/adapters/excel_adapter.py` - always pass deterministic_timestamp(created); intrinsic_created() reads raw OOXML

## Decisions Made
- Fixed EPOCH_ZERO sentinel over content-derived or now(): deterministic, reviewer-obvious, side-effect-free.
- semantic.py untouched — the fix lives entirely in the adapters passing an explicit value (L1 option iii rejected as an out-of-scope spine change).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Excel timestamp non-determinism via openpyxl's fabricated `created`**
- **Found during:** Task 2 (excel retrofit + determinism proof)
- **Issue:** The plan said to source excel's intrinsic timestamp from `wb.properties.created`. But openpyxl's `DocumentProperties` does `self.created = created or datetime.now(utc)` (verified in openpyxl 3.1.5 `packaging/core.py`) — it FABRICATES a wall-clock `created` whenever the source `docProps/core.xml` lacks the element. So `wb.properties.created` is non-deterministic for any document genuinely missing a creation date, and the plan's truth #2 ("no-`created` xlsx parses to byte-identical Sources twice with `timestamp == EPOCH_ZERO`") could NOT hold via the high-level property. (Symptom: the no-`created` determinism test failed; setting `properties.created = None` also makes `wb.save()` raise `AttributeError` on `.set()`.)
- **Fix:** Added `intrinsic_created(raw)` to the excel adapter — reads `dcterms:created` straight from the raw `docProps/core.xml` (stdlib `zipfile` + `xml.etree`), returning a UTC-coerced datetime when present or `None` when genuinely absent. The adapter now sources its timestamp from this raw read, not the openpyxl property. Test fixture authored by saving a normal workbook then stripping the `created`/`modified` elements from the zip (stdlib), since neither `properties.created = None` (crashes) nor a default workbook (fabricated now()) can author a deterministic no-`created` xlsx through the high-level API.
- **Files modified:** src/newsletters/adapters/excel_adapter.py, tests/test_timestamp_determinism.py
- **Verification:** `test_no_intrinsic_timestamp_parses_byte_identical_twice[excel]` passes (timestamp==EPOCH_ZERO, byte-identical); `test_intrinsic_timestamp_is_preserved[excel]` passes; full suite + round-trip parity matrix green.
- **Committed in:** dbde976 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The fix is exactly what L1's stated truth #2 requires — without it the front-fix would be cosmetic for excel. Stdlib-only, no new dependency, no scope creep. NOTE for 06-03: verify whether python-pptx fabricates `core_properties.created` the same way; if so, mirror `intrinsic_created`.

## Issues Encountered
- openpyxl cannot save a workbook with `properties.created = None` (raises `AttributeError` inside `core.py`), and a default workbook stamps `created` with `now()`. Resolved by authoring the deterministic no-`created` fixture via a stdlib zip rewrite that strips the element.

## Verification (gates re-run independently)
- `pytest tests/test_timestamp_determinism.py` — 9 passed
- `pytest tests/test_email_adapter.py tests/test_excel_adapter.py tests/test_coverage_roundtrip.py` (+ the determinism file) — 77 passed (email Date-header regression + round-trip parity matrix green)
- `pytest -q` (full) — **294 passed, 1 xfailed** (280 baseline + 9 here + 5 from concurrent 06-02)
- `mypy src/newsletters/adapters` — Success, 9 files; `mypy src/newsletters/semantic.py` — Success
- `lint-imports` — 1 contract kept, 0 broken (forbid-ai-in-core intact; `_timestamps.py` stdlib-only)
- Bare-import check — `import newsletters` / `newsletters.adapters._timestamps` pulls no openpyxl, no AI

## Next Phase Readiness
- The shared deterministic-timestamp pattern is locked; PptxAdapter (06-03) imports `deterministic_timestamp` and joins the convention instead of copying the `now()` bug.
- The determinism test seam is ready for 06-04 to append the pptx param.
- Open item for 06-03: confirm python-pptx's `core_properties.created` behavior for absent elements (fabricated vs. None) — mirror `intrinsic_created` if it fabricates.

## Self-Check: PASSED
- FOUND: src/newsletters/adapters/_timestamps.py
- FOUND: tests/test_timestamp_determinism.py
- FOUND: .planning/phases/06-powerpoint-adapter/06-01-SUMMARY.md
- FOUND commits: 3e99eb9 (test), bf729e2 (feat), dbde976 (feat)

---
*Phase: 06-powerpoint-adapter*
*Completed: 2026-06-17*
