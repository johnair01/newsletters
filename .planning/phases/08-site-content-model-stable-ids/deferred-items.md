# Deferred items — Phase 08

Out-of-scope discoveries logged during execution (not fixed; not caused by this phase's tasks).

## Pre-existing mypy errors in unrelated files (discovered during 08-01)

`.venv/bin/mypy src/newsletters` reports 12 errors, ALL in files this plan does not touch.
Verified pre-existing on clean HEAD (`d734f3b`, before site.py was added) — site.py itself is
mypy-clean (`mypy src/newsletters/site.py` → "Success: no issues found"). Out of scope per the
executor scope boundary (only auto-fix issues directly caused by the current task).

- `src/newsletters/render.py:243,251,267` — `Incompatible types in assignment (str vs list[str])`
- `src/newsletters/capture.py:68` — `Trace(locator=...)` expects `FreeLocator | SessionLocator`, got `str`
- `src/newsletters/dogfood.py:454,490` — `Source(...)` missing named args `context` / `transcript`
- `src/newsletters/dogfood.py:564,568,572,576` — `Trace(locator=...)` str vs locator union

These predate Phase 8. Recommend a dedicated typing-cleanup task (not Phase 8 / SITE scope).
