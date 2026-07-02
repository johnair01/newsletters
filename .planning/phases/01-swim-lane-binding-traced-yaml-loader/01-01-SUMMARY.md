---
phase: 01-swim-lane-binding-traced-yaml-loader
plan: 01
subsystem: packaging / config boundary
tags: [lazy-import, optional-extra, yaml, ai-optional, LANE-04]
requires: []
provides:
  - "src/newsletters/_yaml_loader.py — lazy PyYAML boundary (_load_yaml, load_config, MISSING_YAML_MESSAGE)"
  - "[config] optional extra declaring PyYAML>=6.0.3"
affects:
  - "Plan 01-02 (swimlane loader) consumes load_config()/_load_yaml()"
  - "Plan 01-04 (tests/test_ai_optional.py) asserts against MISSING_YAML_MESSAGE + bare-install gate"
tech-stack:
  added: ["PyYAML>=6.0.3 (behind [config] extra only)"]
  patterns: ["lazy optional-dependency boundary (mirrors adapters/_openpyxl_loader.py)"]
key-files:
  created: ["src/newsletters/_yaml_loader.py"]
  modified: ["pyproject.toml"]
decisions:
  - "PyYAML lives behind a [config] extra, NOT [project] dependencies (CONTEXT LOCKED, overriding one RESEARCH core-placement line) — keeps bare `pip install .` yaml-free."
  - "safe_load ONLY, never yaml.load (config is data, not code — LANE-04 hard rule)."
  - "No types-PyYAML stub; boundary typed Any with `# type: ignore[import-untyped]`, mirroring the openpyxl Any-typing decision."
metrics:
  duration: "~10 min"
  completed: "2026-07-02"
  tasks: 2
  files: 2
---

# Phase 1 Plan 01: Lazy PyYAML Boundary + [config] Extra Summary

Established the packaging edge for the swim-lane milestone (LANE-04): PyYAML lives behind a new
`[config]` optional extra and is lazy-imported inside a single boundary module, so a bare
`pip install .` runs the deterministic spine with zero PyYAML — mirroring the hardened
`_openpyxl_loader.py` / `[excel]` precedent beat-for-beat.

## What Shipped

- **`src/newsletters/_yaml_loader.py`** (new): four-property module docstring (yaml is NON-AI but
  minimal-core still forbids a top-level import); `MISSING_YAML_MESSAGE` teaching constant naming
  `pip install '.[config]'`; `_load_yaml()` lazy-imports yaml inside the function and re-raises a
  teaching `ImportError` on absence; `load_config(text)` parses via `yaml.safe_load` ONLY;
  `__all__` lists the three public names. Zero top-level yaml import (the sole yaml reference is the
  indented import at line 61).
- **`pyproject.toml`** (modified): added `config = ["PyYAML>=6.0.3"]` to
  `[project.optional-dependencies]` beside `[excel]`/`[pptx]` with a mirroring rationale comment.
  `[project] dependencies` untouched (pydantic/typer/sqlmodel only — no PyYAML in core).

## Commits

- `63fa496` feat(01-01): add lazy PyYAML boundary with safe_load-only parse
- `8899cbb` chore(01-01): declare [config] extra for PyYAML>=6.0.3

## Verify / Gate Output (tails)

- Task 1 check: `boundary ok, safe_load only, no top-level yaml import`
- Task 2 check: `config extra ok, core stays yaml-free`
- New-file gates: black `1 file would be left unchanged`; isort clean; `mypy … Success: no issues found in 1 source file`
- `.venv/bin/lint-imports`: `Contracts: 2 kept, 0 broken.`
- `.venv/bin/pytest -q`: `574 passed in 13.64s` (baseline held, zero new failures)
- Grep `^\s*(import yaml|from yaml)` over `src/`: only the indented lazy import inside `_load_yaml()`
- `pip install -e ".[dev,test,excel,pptx,config]"` → PyYAML 6.0.3 resolved; boundary smoke:
  `load_config('a: 1\nb: [yes, 1.0]')` → `{'a': 1, 'b': [True, 1.0]}`

## Deviations from Plan

**None** — plan executed exactly as written. One expected in-plan detail: the new file needed
`# type: ignore[import-untyped]` on the lazy `import yaml` (PyYAML ships no stubs), which the plan
explicitly directed ("mirror the openpyxl Any-typing decision"). Not a scope deviation.

## Known Stubs

None — this is an interface-first packaging plan; the boundary is fully wired and exercised via
smoke test. Downstream consumers (swimlane loader, formal bare-install tests) are owned by Plans
01-02 and 01-04 by design (single-owner-per-file).

## Self-Check: PASSED

- `src/newsletters/_yaml_loader.py` — FOUND
- pyproject.toml `[config]` extra — FOUND (`config = ["PyYAML>=6.0.3"]`)
- Commit `63fa496` — FOUND
- Commit `8899cbb` — FOUND
