---
phase: 06-powerpoint-adapter
plan: 02
subsystem: infra
tags: [python-pptx, packaging, optional-dependencies, lazy-import, ai-optional, smartart, lxml, ooxml, import-linter]

# Dependency graph
requires:
  - phase: 05-excel-adapter
    provides: the _openpyxl_loader lazy-boundary pattern + the [excel] bare-install gates mirrored here
provides:
  - "[pptx] optional-dependency extra (python-pptx) declared in pyproject.toml"
  - "src/newsletters/adapters/_pptx_loader.py — lazy python-pptx boundary: load_presentation(raw) + _load_pptx() + MISSING_PPTX_MESSAGE"
  - "[pptx] bare-install / AI-isolation gates in tests/test_ai_optional.py (mirror the [excel] block)"
  - "Confirmed risk-A1 SmartArt-uri detection recipe (graphicData_uri accessor + lxml @uri fallback) for 06-03"
affects: [06-03-pptx-adapter, 06-04-pptx-golden-fixtures]

# Tech tracking
tech-stack:
  added: [python-pptx 1.0.2 (transitively lxml 6.1.1, Pillow 12.2.0, XlsxWriter 3.2.9; all sandboxed behind [pptx])]
  patterns:
    - "Lazy optional-extra loader: third-party adapter dep imported ONLY inside a function, never at module top, with a teaching ImportError naming the extra"
    - "Bare-install gate via sys.meta_path blocking-finder subprocess (proves import newsletters works with the dep absent)"
    - "Type third-party objects as Any + inline # type: ignore[import-untyped] rather than adding a types-* stub dep"

key-files:
  created:
    - src/newsletters/adapters/_pptx_loader.py
    - tests/test_pptx_loader.py
  modified:
    - pyproject.toml
    - tests/test_ai_optional.py

key-decisions:
  - "python-pptx typed as Any with inline # type: ignore[import-untyped] — no types-* stub dep (mirrors the Excel Any-typing decision; python-pptx ships no inline stubs)"
  - "Confirmed shape._element.graphicData_uri IS present & reliable on python-pptx 1.0.2 (risk A1 resolved); lxml a:graphicData/@uri fallback agrees exactly — 06-03 should use the accessor first, keep the fallback for safety"
  - "Loader owns ONLY the lazy boundary + packaging; adapter registration / adapters/__init__ wiring deferred to 06-03 to keep files disjoint from the concurrent 06-01 plan"

patterns-established:
  - "Pattern: optional-extra lazy loader mirroring _openpyxl_loader.py for every new third-party adapter dependency"
  - "Pattern: A1-style risk probe test that records the confirmed accessor recipe in its docstring for the downstream consumer plan"

requirements-completed: [ADAPT-04]

# Metrics
duration: 4min
completed: 2026-06-17
---

# Phase 6 Plan 2: PowerPoint Adapter PACKAGING Summary

**Lazy `[pptx]` extra + `_pptx_loader.py` boundary (python-pptx 1.0.2) with bare-install/AI-isolation gates green, and risk-A1 SmartArt-uri detection (`graphicData_uri` accessor + lxml `@uri` fallback) confirmed and recorded for 06-03.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-17T16:25:42Z
- **Completed:** 2026-06-17T16:29:06Z
- **Tasks:** 2
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- Added the `pptx = ["python-pptx"]` optional-dependency extra and installed python-pptx 1.0.2 into the dev `.venv` (pre-approved per CONTEXT decision 1 — no Package-Legitimacy checkpoint).
- Created `_pptx_loader.py`, the lazy python-pptx boundary: zero top-level `import pptx`; `_load_pptx()` lazy-imports inside a try/except and re-raises a teaching `ImportError` naming `[pptx]`; `load_presentation(raw)` returns a `Presentation`.
- Extended `tests/test_ai_optional.py` with the `[pptx]` bare-install / AI-isolation gates (mirroring the `[excel]` block) — all existing assertions kept intact.
- Resolved risk A1: confirmed against installed python-pptx that `shape._element.graphicData_uri` is present and reliable AND the lxml `<a:graphicData>/@uri` fallback agrees, so 06-03 can detect SmartArt with confidence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the [pptx] extra + install python-pptx + lazy loader** - `4dba96a` (feat)
2. **Task 2: Extend bare-install/AI-isolation gates for [pptx] + the A1 accessor probe** - `5eeba7c` (test)

**Plan metadata:** (final docs commit — see below)

## Files Created/Modified
- `pyproject.toml` - Added `pptx = ["python-pptx"]` to `[project.optional-dependencies]` with a NON-AI / pre-approved / no-stub-dep rationale comment.
- `src/newsletters/adapters/_pptx_loader.py` - Lazy python-pptx boundary mirroring `_openpyxl_loader.py`: `_load_pptx()`, `load_presentation(raw)`, `MISSING_PPTX_MESSAGE`.
- `tests/test_ai_optional.py` - Added 5 `[pptx]` gates (extra declared, no top-level import, adapters-import-without-pptx, teaching-ImportError-without-pptx, returns-module-when-present).
- `tests/test_pptx_loader.py` - Risk-A1 probe: confirms the SmartArt graphicFrame signature and the `graphicData_uri` accessor + lxml `@uri` fallback agreement.

## API the loader provides (for 06-03)

```python
from newsletters.adapters._pptx_loader import load_presentation, _load_pptx, MISSING_PPTX_MESSAGE

# load_presentation(raw) -> pptx Presentation (typed Any)
#   raw: str path | bytes | io.BytesIO   (bytes wrapped in a fresh BytesIO internally)
# _load_pptx() -> the `pptx` module (lazy); raises ImportError(MISSING_PPTX_MESSAGE) if absent.
```

Missing-dependency error string (exact):
> The PowerPoint adapter requires the optional 'python-pptx' dependency. Install it with: pip install '.[pptx]'  (or: pip install newsletters[pptx]). The deterministic spine runs without it — python-pptx is needed only for .pptx extraction (AI-optional / minimal-core: third-party adapter deps live behind extras).

## CONFIRMED risk-A1 SmartArt-uri detection recipe (for 06-03)

Probed against installed python-pptx **1.0.2** (`tests/test_pptx_loader.py`, green):

- A SmartArt diagram is a `graphicFrame` with `shape.shape_type is None`, `shape.has_table is False`, `shape.has_chart is False` (the public ladder is blind — RESEARCH Pitfall 1).
- The diagram namespace constant: `DIAGRAM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"`.
- **Primary accessor (CONFIRMED present & reliable):** `getattr(shape._element, "graphicData_uri", None)` returns the frame's live `@uri` — the diagram URI for SmartArt, the table/chart URI for those frames (no false positives).
- **lxml fallback (keep it):** `shape._element.find(".//" + qn("a:graphicData")).get("uri")` (where `from pptx.oxml.ns import qn`). Observed to AGREE with the accessor on the diagram URI.

Recommended 06-03 helper:
```python
def graphic_frame_uri(shape) -> str | None:
    uri = getattr(shape._element, "graphicData_uri", None)   # primary — confirmed on 1.0.2
    if uri is not None:
        return uri
    from pptx.oxml.ns import qn                               # lxml fallback — degrades, never crashes
    gd = shape._element.find(".//" + qn("a:graphicData"))
    return gd.get("uri") if gd is not None else None

# SmartArt iff: shape.shape_type is None AND graphic_frame_uri(shape) == DIAGRAM_URI
# non-None, non-diagram uri on a shape_type-None frame -> "unknown graphic frame" (reported, never dropped)
```

## Decisions Made
- **No `types-python-pptx` stub dep:** python-pptx ships no inline stubs; we type its objects as `Any` with an inline `# type: ignore[import-untyped]` on the lazy import (mirrors the Excel decision). python-pptx is the ONLY new direct dep this phase adds.
- **Accessor-first, fallback-always (A1):** the private `graphicData_uri` accessor IS reliable on 1.0.2, so 06-03 should use it, but keep the lxml fallback so detection degrades to "unknown graphic frame" (reported) rather than crashing if the name is ever renamed.
- **Loader-only scope:** this plan does NOT register an adapter or wire `adapters/__init__.py` (that is 06-03's job), keeping its files disjoint from the concurrent 06-01 plan.

## Deviations from Plan

None - plan executed exactly as written.

## Gate Results (re-run independently, actual output)

- `pytest tests/test_pptx_loader.py tests/test_ai_optional.py -q` → **17 passed, 1 xfailed** (the xfail is the pre-existing ambient-logfire pydantic-plugin guard, unrelated).
- `pytest -q` (full suite) → **297 passed, 1 xfailed** (baseline 280; the increase reflects this plan's 6 new pptx tests plus 06-01's tests landing concurrently in the same suite). No failures.
- `mypy src/newsletters/adapters` → **Success: no issues found in 9 source files** (`_pptx_loader.py` typed `Any`, inline `# type: ignore`).
- `lint-imports` → **1 kept, 0 broken** (`forbid-ai-in-core` unaffected; python-pptx + transitive lxml/Pillow do NOT trip the AI contract).
- `grep "^import pptx|^from pptx" src/newsletters/` → **none** (no top-level pptx import reachable from `import newsletters`).

## Supply-chain note (threat T-06-SC)
`.venv/bin/pip install python-pptx` materialized exactly the expected transitive deps — `lxml 6.1.1`, `Pillow 12.2.0`, `XlsxWriter 3.2.9` (typing_extensions already present). No unexpected new DIRECT dependency; no STOP-and-flag condition triggered.

## Known Stubs
None.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required. (python-pptx is installed in the dev `.venv` as a pre-approved step; end users install it via `pip install '.[pptx]'`.)

## Next Phase Readiness
- 06-03 (PptxAdapter) can now lazy-import python-pptx via `load_presentation()` and detect SmartArt via the confirmed `graphicData_uri` recipe above.
- The `test_adapters_package_imports_without_pptx` gate is pre-written so that when 06-03 registers `PptxAdapter` on package import, it inherits a green bare-install gate proving registration stays lazy / extra-free.
- No blockers.

## Self-Check: PASSED
- FOUND: src/newsletters/adapters/_pptx_loader.py
- FOUND: tests/test_pptx_loader.py
- FOUND commit: 4dba96a
- FOUND commit: 5eeba7c

---
*Phase: 06-powerpoint-adapter*
*Completed: 2026-06-17*
