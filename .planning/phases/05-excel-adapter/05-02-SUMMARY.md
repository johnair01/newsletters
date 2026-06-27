---
phase: 05-excel-adapter
plan: 02
subsystem: infra
tags: [openpyxl, packaging, optional-dependency, lazy-import, ai-optional, xlsx]

# Dependency graph
requires:
  - phase: 02-ai-optional-packaging
    provides: "the [ai] lazy-import discipline + tests/test_ai_optional.py bare-install gate (the pattern this plan mirrors for openpyxl)"
provides:
  - "excel = [\"openpyxl\"] optional extra in pyproject.toml (non-AI, behind an extra)"
  - "src/newsletters/adapters/_openpyxl_loader.py — lazy _load_openpyxl() with a teaching ImportError + load_workbook_pair() encapsulating the R3 double-load"
  - "extended bare-install gate proving newsletters.adapters imports without openpyxl"
  - "R4 Wave-0 probe pinning the confirmed openpyxl chart/image detection attribute names (ws._charts / ws._images)"
affects: [05-03-excel-adapter]

# Tech tracking
tech-stack:
  added: [openpyxl 3.1.5 (behind the [excel] extra)]
  patterns:
    - "Lazy optional-dependency import mirroring the [ai] discipline (openpyxl imported inside _load_openpyxl(), never at module top)"
    - "Annotate third-party objects with no stubs as Any rather than pull a stub dependency (types-openpyxl avoided)"

key-files:
  created:
    - src/newsletters/adapters/_openpyxl_loader.py
    - tests/test_openpyxl_probe.py
  modified:
    - pyproject.toml
    - tests/test_ai_optional.py

key-decisions:
  - "openpyxl typed as Any (Workbook = Any + # type: ignore[import-untyped]) — types-openpyxl is a separate stub package and openpyxl is the ONLY new dependency permitted this phase"
  - "load_workbook_pair() lives in the loader (not the future adapter) so 05-03 just calls it for the R3 double-load"

patterns-established:
  - "Optional adapter deps live behind an extra and are lazy-imported inside a single accessor with a teaching ImportError naming the install command"
  - "Wave-0 attribute-name probes pin tertiary-confidence assumptions against the installed library version as committed tests"

requirements-completed: [ADAPT-03]

# Metrics
duration: ~20min
completed: 2026-06-17
---

# Phase 5 Plan 02: openpyxl packaging Summary

**The `[excel]` optional extra + a lazy `_load_openpyxl()` boundary (with the R3 double-load helper) that keeps the bare-install AI-isolation gate green without openpyxl, plus an R4 probe confirming `ws._charts` / `ws._images` against openpyxl 3.1.5.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-17T15:05Z (approx)
- **Completed:** 2026-06-17T15:26Z
- **Tasks:** 2
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments
- Declared `excel = ["openpyxl"]` under `[project.optional-dependencies]`; openpyxl installed into the dev `.venv` (3.1.5).
- Built the lazy openpyxl boundary: `_load_openpyxl()` imports openpyxl inside the function and re-raises a teaching `ImportError`; `load_workbook_pair()` encapsulates the R3 double-load so 05-03 just calls it.
- Extended `tests/test_ai_optional.py` with 5 new gates proving the bare install holds (package imports without openpyxl, loader raises the teaching error when absent, zero top-level openpyxl imports, happy path returns the module, extra declared correctly) — all existing assertions kept intact.
- Confirmed the openpyxl chart/image detection attribute names (assumption A1) against the installed version via the committed R4 probe.

## Task Commits

1. **Task 1: [excel] extra + lazy loader + extend bare-install gate** - `3d2424b` (feat)
2. **Task 2: R4 Wave-0 probe pinning chart/image attribute names** - `e569318` (test)
3. **Typing fix (Rule 3): loader Workbook = Any to keep mypy green without a stub dep** - `7a10e00` (fix)

_(05-01 ran concurrently; its commit `1bba430` interleaves in `git log` — expected, not a conflict.)_

## Files Created/Modified
- `pyproject.toml` - added `excel = ["openpyxl"]` optional extra (non-AI, behind the extra).
- `src/newsletters/adapters/_openpyxl_loader.py` - lazy `_load_openpyxl()` + `load_workbook_pair()` + `MISSING_OPENPYXL_MESSAGE`; zero top-level openpyxl import.
- `tests/test_ai_optional.py` - 5 new bare-install/lazy-boundary tests (all prior assertions intact).
- `tests/test_openpyxl_probe.py` - R4 probe pinning `ws._charts` / `ws._images`.

## For Plan 05-03 (Wave 2) — the contract you consume

**Loader API (`src/newsletters/adapters/_openpyxl_loader.py`):**
- `_load_openpyxl() -> module` — returns the `openpyxl` module; raises the teaching `ImportError` if absent. Use this if you need the module directly (e.g. `from openpyxl.utils import ...`).
- `load_workbook_pair(path_or_bytes) -> (wb_formula, wb_data)` — the R3 **double-load**. Accepts a `str` path, raw `bytes`, or a `BytesIO` (bytes/BytesIO are copied into a fresh `BytesIO` per view). Returns two **standard-mode** (`read_only=False`, `keep_links=False`) workbooks:
  - `wb_formula` (`data_only=False`) — `cell.data_type == 'f'` identifies formula cells; `cell.value` is the formula string / literal.
  - `wb_data` (`data_only=True`) — `cell.value` is the cached computed value, or `None` if Excel never wrote a cache.
  - **You must `.close()` both** when done. Zip the two views cell-by-cell (`zip(wb_f.worksheets, wb_d.worksheets)`, then `zip(ws_f.iter_rows(), ws_d.iter_rows())`).
- `MISSING_OPENPYXL_MESSAGE` — the exact teaching string, importable so your tests can assert against it without duplication.

**Exact teaching ImportError message:**
> The Excel adapter requires the optional 'openpyxl' dependency. Install it with: pip install '.[excel]'  (or: pip install newsletters[excel]). The deterministic spine runs without it — openpyxl is needed only for .xlsx extraction (AI-optional / minimal-core: third-party adapter deps live behind extras).

**CONFIRMED chart/image attribute names (R4 probe, openpyxl 3.1.5):**
- `ws._charts` — **CONFIRMED.** List of chart objects. Charts SURVIVE a standard-mode reload (a `BarChart` round-trips and is found in `_charts`). Use `for c in getattr(ws, "_charts", []): ...` to disclose `unextracted[]` chart drops.
- `ws._images` — **CONFIRMED present** as a list attribute. **Caveat:** openpyxl LOSES images from existing files on reload, so a reloaded `ws._images` is typically empty even if the source `.xlsx` had images. The attribute is the correct detection surface; apply it to the freshly-parsed worksheet object. (Conservative fallback if a future version drops content: disclose "openpyxl does not read drawings" once — the faithfulness guarantee does not depend on the exact count.)
- **Both attributes are ABSENT in `read_only=True` mode** — a second, independent reason (on top of R3's merged-cell mandate) that 05-03 must load with `read_only=False`. `load_workbook_pair()` already does.

## Decisions Made
- **openpyxl typed as `Any`** (`Workbook = Any` + `# type: ignore[import-untyped]` on the lazy import) instead of adding `types-openpyxl`. CONTEXT permits openpyxl as the ONLY new dependency this phase; pulling a stub package would violate that. The faithful per-cell logic (and its real types) lives in the 05-03 adapter, so opaque typing here is correct.
- **`load_workbook_pair()` lives in the loader, not the adapter** — so the double-load discipline (`data_only` pair, `read_only=False`, per-view BytesIO) is encapsulated once and 05-03 cannot get it wrong.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Typed openpyxl workbooks as `Any` to keep `mypy src/newsletters/adapters` green without adding a stub dependency**
- **Found during:** Task 1 (gate re-run — `mypy src/newsletters/adapters`)
- **Issue:** mypy reported `Library stubs not installed for "openpyxl" [import-untyped]` for both a `TYPE_CHECKING` `from openpyxl import Workbook` and the lazy `import openpyxl`. The standard mypy remedy (`pip install types-openpyxl`) would add a SECOND new dependency, which CONTEXT forbids (openpyxl is the only permitted new dep this phase).
- **Fix:** Removed the `TYPE_CHECKING` openpyxl import, aliased `Workbook = Any`, and added `# type: ignore[import-untyped]` on the lazy `import openpyxl` line (with a comment explaining why no stub dep). A first attempt placed the `# type: ignore[...]` on its own preceding line, which mypy parsed as an `Invalid "type: ignore" comment [syntax]`; moving it inline on the import statement resolved it.
- **Files modified:** src/newsletters/adapters/_openpyxl_loader.py
- **Verification:** `mypy src/newsletters/adapters` → `Success: no issues found in 6 source files`; loader still has 0 top-level openpyxl imports; full suite + lint-imports stayed green.
- **Committed in:** `7a10e00`

---

**Total deviations:** 1 auto-fixed (1 blocking, Rule 3).
**Impact on plan:** The fix avoids a forbidden second dependency while keeping the typecheck gate green. No scope creep; no behavior change.

## Issues Encountered
- `src/newsletters/adapters/_coverage_codec.py` already existed (created by the concurrently-running 05-01). It is NOT one of my files and I did not touch it. No conflict on my exclusive files (`pyproject.toml`, `_openpyxl_loader.py`, `test_ai_optional.py`, `test_openpyxl_probe.py`).

## Gate Results (re-run independently via .venv)
- `pytest tests/test_openpyxl_probe.py -q` → **3 passed**
- `pytest tests/test_ai_optional.py -q` → **9 passed, 1 xfailed** (5 new + 4 existing; xfail is the documented ambient-plugin caveat)
- `pytest -q` (full) → **199 passed, 1 xfailed** (baseline was 177+1; increase = my 8 new tests + 05-01's concurrent tests)
- `mypy src/newsletters/adapters` → **Success: no issues found in 6 source files**
- `lint-imports` → **Contracts: 1 kept, 0 broken** (openpyxl is not AI; the forbid-ai contract is unaffected)
- `python -c "import newsletters"` → **ok**; `grep` for top-level `import openpyxl` across `src/newsletters/` → **none** (loader grep-count 0)

## User Setup Required
None - no external service configuration required. (openpyxl is installed into the dev `.venv` as a sanctioned, pre-approved setup step; no Package-Legitimacy checkpoint per CONTEXT decision 1 + RESEARCH audit.)

## Next Phase Readiness
- 05-03 (ExcelAdapter) can now: lazy-load openpyxl via `_load_openpyxl()`, double-load via `load_workbook_pair()`, and disclose charts/images via the confirmed `ws._charts` / `ws._images` attributes (standard mode only).
- No blockers. The bare-install / AI-optional invariant is intact and gated.

---
*Phase: 05-excel-adapter*
*Completed: 2026-06-17*

## Self-Check: PASSED
- Files: `_openpyxl_loader.py`, `test_openpyxl_probe.py`, `05-02-SUMMARY.md` all FOUND on disk; `pyproject.toml` excel extra FOUND.
- Commits: `3d2424b`, `e569318`, `7a10e00` all FOUND in git log.
