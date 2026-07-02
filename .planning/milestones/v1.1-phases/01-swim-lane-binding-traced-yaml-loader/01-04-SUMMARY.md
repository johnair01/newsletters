---
phase: 01-swim-lane-binding-traced-yaml-loader
plan: 04
subsystem: testing
tags: [abstraction-guard, ai-optional, pyyaml, packaging, lazy-import, pytest]

# Dependency graph
requires:
  - phase: 01-02
    provides: src/newsletters/swimlane.py + src/newsletters/_yaml_loader.py (the modules these gates police)
  - phase: 01-01
    provides: the [config] extra + MISSING_YAML_MESSAGE teaching-error constant
provides:
  - "Abstraction-guard test (LANE-03): fails the suite on any fixture/org/config-specific token in src/newsletters/"
  - "[config]/yaml lazy-boundary + AI-free swimlane gates (LANE-04): bare install runs the spine with yaml unreachable"
affects: [02-composition, 03-worked-example, packaging, ci-bare-install]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "grep-style source-text scan with a self-contained, word-bounded denylist (abstraction guard)"
    - "one-for-one port of the [excel]/[pptx] lazy-boundary gate family to a new optional extra"
    - "planted-leak self-test proving a guard is live, not vacuous"

key-files:
  created:
    - tests/test_abstraction_guard.py
  modified:
    - tests/test_ai_optional.py

key-decisions:
  - "Case-sensitive, word-bounded (\\b) denylist matching so generic structural keys (lanes/owner/module/area) in source never false-positive — only concrete CONFIG values (module-x, area-1, owner-1) trip the guard"
  - "Excluded the bare crew name 'Data' from the denylist (too generic; would false-positive on ordinary source) while keeping distinctive idsids/full-names/org-metric names"
  - "no-top-level-yaml scan covers BOTH _yaml_loader.py AND swimlane.py (swimlane is a plain top-level module, so a yaml import in either breaks the bare install)"
  - "swimlane AI-free test guards the load_swimlanes() call in try/except ImportError so a bare env (no PyYAML) still proves the import path is AI-free"

patterns-established:
  - "Abstraction guard: shared _scan_text() exercised by BOTH the real-source walk and the planted-leak self-test, so the clean pass is provably non-vacuous"
  - "New optional extra gets the full [excel]-parallel gate set: extra-declared, no-top-level-import, imports-with-dep-blocked, teaching-error, returns-module-when-present, module-is-AI-free"

requirements-completed: [LANE-03, LANE-04]

# Metrics
duration: ~25min
completed: 2026-07-02
---

# Phase 1 Plan 04: Abstraction-guard + [config]/yaml lazy-boundary enforcement Summary

**Two enforcement suites turned the ABSTRACT-EVERYTHING principle and the AI-optional/minimal-core packaging into invariants-in-code: a denylist scanner that fails the suite on any config-specific name leaking into `src/newsletters/` (LANE-03), and a `[config]`/yaml lazy-boundary gate set proving a bare `pip install .` runs the spine with `import yaml` unreachable and swimlane AI-free (LANE-04).**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2
- **Files modified:** 2 (1 created, 1 extended)
- **Test delta:** 579 → 587 passed (+8: 2 abstraction-guard, 6 config/yaml/swimlane)

## Accomplishments
- `tests/test_abstraction_guard.py` walks every `src/newsletters/*.py` and fails the suite on any denylisted token (swim-lane fixture ids + sample_team crew/org/metric names + the seed's fabricated worked-example scheme + `eng-NN`/`toolset-N` patterns).
- The guard is proven live two ways: an in-memory planted-leak self-test, AND a manual real-source planting demonstration (`owner-1` planted into `swimlane.py` → suite went red → reverted → green).
- Extended `tests/test_ai_optional.py` (ADD-ONLY) with the `[config]`/yaml block: extra-declared (PyYAML-only, non-AI), no-top-level-`import yaml` in `_yaml_loader.py` + `swimlane.py`, meta-path-blocked import proving `yaml` stays out of `sys.modules`, teaching `ImportError` asserted against `MISSING_YAML_MESSAGE`, happy-path returns-module (skips bare env), and a swimlane-is-AI-free subprocess gate.
- LANE-03 + LANE-04 marked complete in REQUIREMENTS.md via the SDK verb.

## Task Commits

1. **Task 1: Abstraction-guard test (LANE-03)** — `e55393d` (test)
2. **Task 2: [config]/yaml lazy-boundary + AI-free swimlane gates (LANE-04)** — `e56f93e` (test)

## Files Created/Modified
- `tests/test_abstraction_guard.py` (created) — source-text denylist scanner; `test_no_config_specific_name_in_src` + `test_guard_detects_planted_leak`.
- `tests/test_ai_optional.py` (modified, ADD-ONLY) — 6 new tests: `test_config_extra_declared`, `test_yaml_loader_has_no_toplevel_yaml_import`, `test_swimlane_package_imports_without_yaml`, `test_yaml_loader_raises_teaching_error_without_yaml`, `test_yaml_loader_returns_module_when_present`, `test_swimlane_import_loads_no_ai_module`.

## Decisions Made
- **Word-bounded, case-sensitive denylist matching** so the generic STRUCTURAL keys the loader legitimately keys on (`lanes`, `heading`, `owner`, `module`, `area`) never false-positive — only concrete CONFIG values (`module-x`, `area-1`, `owner-1`) trip the guard.
- **Excluded the bare crew name `Data`** (too generic; would false-positive on ordinary source) while keeping distinctive idsids, full crew names, org/module names, and org metric names.
- **no-top-level-yaml scan covers both `_yaml_loader.py` and `swimlane.py`** — swimlane is a plain top-level module with no lazy registration, so a top-level yaml import in either would break the bare install.
- **The swimlane AI-free test guards its `load_swimlanes()` call** in `try/except ImportError`, so on a bare env (no PyYAML) it still proves the import path is AI-free without failing.

## Deviations from Plan

None — plan executed exactly as written. (One mechanical adjustment inside scope: added `# type: ignore[import-untyped]` to the two new dev-only imports so the `[config]` block introduces ZERO new mypy errors versus the baseline; this mirrors the tolerance the pre-existing openpyxl/pptx test imports already have.)

## Issues Encountered
- mypy initially flagged the new `import yaml` / `from newsletters._yaml_loader` lines as `import-untyped` (same class as the existing openpyxl/pptx test imports). Silenced with targeted `# type: ignore[import-untyped]` so the new code is baseline-clean; the 3 remaining mypy errors in the file are all pre-existing (openpyxl lines 417/424, pptx line 576), unchanged by this plan.

## Verification (gates re-run independently)
- `.venv/bin/pytest -q` → **587 passed** (579 baseline + 8 new).
- `.venv/bin/pytest tests/test_ai_optional.py -q` → **22 passed** (16 existing unchanged + 6 new).
- Abstraction guard proven to FIRE: planting `owner-1` into `src/newsletters/swimlane.py` produced `AssertionError: ... swimlane.py: ['owner-1']`; reverted → passes clean.
- black `--check` clean; isort `--profile black --check-only` clean on both files.
- mypy: zero NEW errors introduced (3 pre-existing openpyxl/pptx errors only).
- `ci.yml` byte-unchanged; no other file touched (only the two files this plan owns + the SDK-driven REQUIREMENTS.md).

## Next Phase Readiness
- LANE-01..04 all complete → Phase 1 (swim-lane binding + traced YAML loader) is fully green on the enforced gate set; Phase 2's composer can consume `SectionBinding[]` on a proven-honest, proven-abstract, AI-optional loader.
- No blockers. The abstraction guard now standing-enforces the ABSTRACT-EVERYTHING principle for all future source edits.

## Self-Check: PASSED
- tests/test_abstraction_guard.py — FOUND
- tests/test_ai_optional.py — FOUND
- 01-04-SUMMARY.md — FOUND
- commit e55393d — FOUND
- commit e56f93e — FOUND

---
*Phase: 01-swim-lane-binding-traced-yaml-loader*
*Completed: 2026-07-02*
