---
phase: 02-ai-optional-packaging-boundary
plan: 01
subsystem: infra
tags: [packaging, pyproject, import-linter, pydantic-plugins, ai-optional, supply-chain]

# Dependency graph
requires:
  - phase: 01-distill-socket
    provides: "AI-clean src/newsletters/distill/ (registry/port pattern) and the AI_MODULES subprocess-isolation idiom in tests/test_distill_socket.py"
provides:
  - "Core pyproject.toml dependencies reduced to non-AI only (pydantic>=2, typer[all], sqlmodel)"
  - "[ai] optional-dependencies extra carrying pydantic-ai as the single planned AI backend"
  - "langsmith dropped entirely (telemetry); langchain[anthropic] and langgraph removed (unused)"
  - ".importlinter forbidden contract barring AI packages from core (PKG-04), proven to have teeth"
  - "tests/test_ai_optional.py: structural dep-boundary + import-linter contract + plugin-aware runtime guard + bare-pipeline smoke"
affects: [02-02-ci-bare-install-gate, ai-backend-implementation]

# Tech tracking
tech-stack:
  added: [import-linter==2.11 (dev-only, PKG-04 static contract tool)]
  patterns:
    - "Two-gate AI-boundary enforcement: static import-linter contract + runtime pydantic-plugin entry-point guard (necessary-but-not-sufficient pair)"
    - "Subprocess isolation with PYDANTIC_DISABLE_PLUGINS=true to measure OUR import graph, not ambient dev-venv plugins"

key-files:
  created:
    - .importlinter
    - tests/test_ai_optional.py
  modified:
    - pyproject.toml
    - .devcontainer/requirements.txt

key-decisions:
  - "Drop langsmith/langchain/langgraph entirely (zero usage proven by grep across src/tests/mcp/web) rather than relocate to [ai]"
  - "Relocate pydantic-ai to [ai] (not delete) — it is the single planned AI backend and the logfire-leak source; out of core fixes the leak"
  - "Keep sqlmodel in core — genuinely used by src/newsletters/models.py, not AI"
  - "import-linter needs include_external_packages=True because forbidden_modules are external packages"
  - "test_no_ai_pydantic_plugin_active xfails (not skips/fails) on the ambient-logfire dev .venv; the canonical 'no AI plugin' proof is the bare-install CI job in 02-02"

patterns-established:
  - "Static contract (import edges) + runtime entry-point enumeration together close the pydantic-plugin blind spot the import-linter structurally cannot see"
  - "Prove a forbidden-import contract has teeth by transiently injecting the forbidden import, confirming non-zero exit, then reverting"

requirements-completed: [PKG-01, PKG-02, PKG-04]

# Metrics
duration: 4min
completed: 2026-06-17
---

# Phase 2 Plan 01: AI-Optional Packaging Boundary Summary

**The deterministic spine now declares zero AI runtime deps — core = pydantic/typer/sqlmodel, pydantic-ai lives in a new `[ai]` extra, telemetry/unused AI are gone, and two complementary local gates (an import-linter `forbidden` contract + a pydantic-plugin-aware runtime test) police the boundary.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-17T08:36:07Z
- **Completed:** 2026-06-17T08:40:13Z
- **Tasks:** 3 completed (1 blocking-human gate pre-approved, 2 TDD execute)
- **Files modified:** 4 (2 created, 2 modified)

## Accomplishments

### Task 1 — Package Legitimacy Gate (PRE-APPROVED)
The blocking-human checkpoint for adding `import-linter` was approved in advance by the reviewer
(per the execution objective): the genuine David Seddon project (`import-linter` 2.11 on PyPI,
permissive BSD-family license, `lint-imports` CLI, static analysis with no telemetry — exactly
fit for PKG-04). Recorded as PASSED; Tasks 2 and 3 were unblocked. The reviewer also pre-approved
moving `pydantic-ai` to `[ai]` and dropping `langsmith`/`langchain`/`langgraph` from core — and I
grep-confirmed zero usage of those three across `src/` before deleting them.

### Task 2 — pyproject.toml reorg (TDD)
- RED: `test_pyproject_dependency_boundary` failed against the unchanged file (AI packages in core).
- GREEN: core `dependencies` = `["pydantic>=2", "typer[all]", "sqlmodel"]`; new `ai = ["pydantic-ai"]`
  extra; `import-linter` added to `[dev]`; `langsmith`/`langchain[anthropic]`/`langgraph` removed
  from every section. `.devcontainer/requirements.txt` aligned (dropped the same three).

### Task 3 — import-linter contract + plugin-aware runtime guards (TDD)
- Installed `import-linter==2.11`; created `.importlinter` with a `forbidden` contract barring the
  AI set from `newsletters` core (`include_external_packages = True`). `lint-imports` exits 0.
- Proved the contract has teeth: transiently injected `import pydantic_ai` into `cli.py` →
  `lint-imports` exited 1 ("newsletters.cli -> pydantic_ai") → reverted → green again.
- `tests/test_ai_optional.py` carries: the structural boundary test, `test_import_linter_contract_holds`,
  `test_core_import_loads_no_ai_module`, `test_no_ai_pydantic_plugin_active` (the plugin-leak guard),
  and `test_bare_pipeline_runs_ai_free` (build_site end-to-end in a clean subprocess, zero AI).

## Gate Results (actual output, independently re-run)

```
$ .venv/bin/lint-imports
Analyzed 27 files, 78 dependencies.
Core (newsletters) must not import any AI/LLM package KEPT
Contracts: 1 kept, 0 broken.        # exit 0

$ .venv/bin/python -m pytest tests/test_ai_optional.py -q
4 passed, 1 xfailed in 1.21s        # xfail = ambient-logfire plugin (documented)

$ .venv/bin/python -m pytest -q
36 passed, 1 xfailed in 4.35s       # full suite (Rev1 + Phase-1 regression green)

$ .venv/bin/python -m mypy src/newsletters/distill
Success: no issues found in 6 source files

$ grep -rn "import (langchain|langgraph|langsmith|pydantic_ai|logfire)" src/
0 AI imports in src/ (good)
```

## pyproject.toml — before / after

**Before — core `dependencies`:**
`pydantic>=2`, `pydantic-ai`, `typer[all]`, `sqlmodel`, `langgraph`, `langsmith`, `langchain[anthropic]`
Extras: `panel`, `dev` (pytest/black/ipdb/ipython/isort/mypy), `test`.

**After — core `dependencies`:**
`pydantic>=2`, `typer[all]`, `sqlmodel`
Extras: `ai` = `pydantic-ai` (new); `panel`; `dev` (+ `import-linter`); `test`.
Dropped entirely from every section: `langsmith`, `langchain[anthropic]`, `langgraph`.

## Files

**Created:**
- `.importlinter` — root_package `newsletters` + `forbid-ai-in-core` forbidden contract; documents the plugin-activation blind spot and points to the runtime guard + the bare-install CI job (02-02).
- `tests/test_ai_optional.py` — the packaging-boundary suite (5 tests).

**Modified:**
- `pyproject.toml` — core non-AI only; `[ai]` extra; `import-linter` in `[dev]`; AI cruft removed.
- `.devcontainer/requirements.txt` — dropped langsmith/langchain/langgraph; clarifying comment.

## Deviations from Plan

**1. [Rule 3 - Blocking config] `.importlinter` required `include_external_packages = True`**
- **Found during:** Task 3
- **Issue:** With external `forbidden_modules`, `lint-imports` errored: "The top level configuration must have include_external_packages=True when there are external forbidden modules."
- **Fix:** Added `include_external_packages = True` to the `[importlinter]` table (with an explanatory comment).
- **Files modified:** `.importlinter`
- **Commit:** afe9a17

No architectural (Rule 4) deviations. The package-install of `import-linter` was the pre-approved
Task-1 gate, not an unsanctioned Rule-3 install.

## Authentication Gates

None.

## Known Stubs

None — this plan is packaging/infra; no UI data sources or placeholders introduced.

## Threat Flags

None — no new network/auth/PII/file-access surface. The plan reduces supply-chain surface
(drops three packages) and adds one human-verified dev-only tool.

## Notes for Plan 02-02 (the CI standing invariant, PKG-03)
- `test_no_ai_pydantic_plugin_active` currently **xfails** in the dev `.venv` because ambient
  `logfire` registers `logfire-plugin` in `entry_points(group="pydantic")`. On the bare no-extras
  install CI job (PKG-03) the AI packages are absent, so that plugin is gone and the test should
  pass strictly. The test guards the MECHANISM regardless; the bare install is the canonical proof.
- Wire `.venv/bin/lint-imports` and `pytest tests/test_ai_optional.py` into CI; add the bare
  `pip install .` (no extras) + full-pipeline job that is the true source of truth.

## Self-Check: PASSED

All created/modified files exist on disk; all three task commits (dc0bdf2, e745424, afe9a17) are present in git history.
