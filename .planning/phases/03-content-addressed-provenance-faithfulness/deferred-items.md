# Deferred items — Phase 03

Out-of-scope discoveries logged during execution (not fixed; SCOPE BOUNDARY rule).

## 03-02 — pre-existing mypy errors in `src/newsletters/dogfood.py`

`mypy src/newsletters/dogfood.py` reports 8 errors, ALL in functions NOT touched by
plan 03-02 (`_newsletter_for`, `_show`, `_plan_report` — lines 398, 434, 508–520):

- `Missing named argument "transcript"/"context" for "Source"` — `Source(id="...")` calls
  that rely on Pydantic field defaults mypy does not see under the project's minimal
  `[tool.mypy]` config (no pydantic plugin configured).
- `Argument "locator" to "Trace" has incompatible type "str"` — the Rev1 bare-string
  locator path, valid at runtime via `Trace._coerce_locator`, but not modelled for mypy.

These predate this phase (03-01 only ran mypy on `semantic.py`/`distill`, never `dogfood.py`).
The migration helper added in 03-02 (`_address_trace`, `address_corpus_traces`,
`MigrationReport`) is mypy-clean. Runtime is unaffected — Pydantic supplies the defaults and
coerces the locator. A future cleanup could enable the pydantic mypy plugin or make the
arguments explicit; out of scope for the faithful in-place trace migration.
