---
phase: 02-ai-optional-packaging-boundary
plan: 02
subsystem: infra
tags: [ci, github-actions, ai-optional, bare-install, import-linter, standing-invariant, supply-chain]

# Dependency graph
requires:
  - phase: 02-ai-optional-packaging-boundary
    plan: 01
    provides: "pyproject [ai]/[dev]/[test] extras, .importlinter forbidden contract, tests/test_ai_optional.py (incl. plugin-aware guard + bare-pipeline smoke)"
provides:
  - "First CI workflow (.github/workflows/ci.yml) — the STANDING AI-optional invariant on every push/PR"
  - "bare-install job (PKG-03): pip install .[test] with NO [ai], runs the full deterministic pipeline + spine/AI-optional tests, asserts zero AI reachable from core — the canonical source-of-truth gate"
  - "import-linter job (PKG-04): lint-imports forbids any static core->AI import edge on every push"
affects: [all-subsequent-phases]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CI bare no-extras install as the runtime source-of-truth for AI-optional core: with AI packages absent, neither a static import nor a pydantic-group AI plugin can fire — closes the import-linter blind spot the leak-note names"
    - "Two-job CI gate: runtime bare-install proof (definitive) + static import-linter contract (fast complement)"

key-files:
  created:
    - .github/workflows/ci.yml
  modified: []

key-decisions:
  - "bare-install job installs .[test] (pytest only — a test runner, not an AI dep) so the pipeline tests can execute while the runtime graph stays AI-free; NEVER [ai]/[dev]/[panel] in that job"
  - "First-party actions only (checkout@v4, setup-python@v5) — no marketplace/AI supply-chain surface (T-02-SC)"
  - "Python 3.12 pinned to match requires-python / [tool.mypy] python_version"
  - "No matrix/caching/coverage — a focused invariant gate, not a full CI build-out (later phases extend it)"

requirements-completed: [PKG-03, PKG-04]

# Metrics
duration: 2min
completed: 2026-06-17
---

# Phase 2 Plan 02: CI Standing AI-Optional Invariant Summary

**The AI-optional boundary is now a per-push CI gate: a `bare-install` job (`pip install .[test]`, NO `[ai]`) runs the full deterministic pipeline + the spine/AI-optional tests on a bare interpreter and asserts zero AI reachable from core (PKG-03, the canonical source-of-truth), alongside an `import-linter` job that forbids any static core->AI edge (PKG-04) — both on every push/PR, the gate every later phase must keep green.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-06-17T08:44:22Z
- **Completed:** 2026-06-17
- **Tasks:** 1 completed (autonomous, no checkpoints)
- **Files modified:** 1 (1 created)

## Accomplishments

### Task 1 — `.github/workflows/ci.yml` (the first CI workflow)
Created the project's first GitHub Actions workflow, triggered `on: [push, pull_request]`, Python 3.12, first-party actions only (`actions/checkout@v4`, `actions/setup-python@v5`). Two independent jobs:

**`bare-install` (PKG-03 — canonical):**
1. checkout + setup-python 3.12
2. `pip install ".[test]"` — NO `[ai]`/`[dev]`/`[panel]` (`[test]` adds only pytest)
3. assert each AI module (`logfire`, `pydantic_ai`, `openai`, `anthropic`, `langsmith`, `langchain`, `langgraph`) raises `ImportError` — belt-and-suspenders that the bare install really is AI-free
4. run the FULL deterministic pipeline `newsletters build --out "$RUNNER_TEMP/site"` (capture -> build_report -> promote -> render via `build_site`) and assert `index.html` was written
5. run the spine + AI-optional tests on the bare interpreter (`pytest tests/test_semantic.py tests/test_distill_socket.py tests/test_ai_optional.py`)
6. final assert: after `import newsletters`, no AI module is in `sys.modules`

**`import-linter` (PKG-04 — static contract):**
1. checkout + setup-python 3.12
2. `pip install ".[dev]"` (brings import-linter)
3. `lint-imports` from repo root — fails on any static core->AI import edge

A top-of-file comment records this as the standing AI-optional invariant and marks `bare-install` as canonical (catches BOTH static imports AND pydantic-plugin activation), pointing to the leak-note.

## Local Proof of the PKG-03 Logic (actual output — the real verification)

GitHub Actions cannot run here, so the bare-install job logic was proven in a throwaway Python 3.12 venv (`pip install .[test]`, NO `[ai]`), running each CI step verbatim:

```
$ pip list | grep -iE "logfire|pydantic-ai|openai|anthropic|langsmith|langchain|langgraph"
  (no AI packages installed — good)

# STEP 3 — assert AI modules not importable
bare install is AI-free (none importable): ('logfire','pydantic_ai','openai','anthropic','langsmith','langchain','langgraph')

# STEP 4 — full deterministic pipeline
$ newsletters build --out /tmp/bare-site
  ... 9 surfaces + index.html ...
  rendered 9 surfaces + the library index -> /tmp/bare-site
index.html written: OK

# STEP 5 — spine + AI-optional tests on the bare interpreter
$ python -m pytest tests/test_semantic.py tests/test_distill_socket.py tests/test_ai_optional.py -q
37 passed in 2.45s          # NOTE: 0 xfailed (vs dev .venv's "4 passed, 1 xfailed")

# THE CANONICAL PROOF — plugin guard passes STRICTLY (not xfail) when logfire is absent
$ python -m pytest tests/test_ai_optional.py::test_no_ai_pydantic_plugin_active -v
tests/test_ai_optional.py::test_no_ai_pydantic_plugin_active PASSED   [100%]
1 passed in 0.01s

# STEP 6 — no AI module reachable from core
$ python -c "import sys, newsletters; bad=[m for m in (...AI...) if m in sys.modules]; assert not bad; print('core ai-free on bare install')"
core ai-free on bare install
```

This is the load-bearing result: `test_no_ai_pydantic_plugin_active` **PASSES strictly** on the bare install (where the dev `.venv` xfails it due to ambient logfire). With AI packages physically absent there is no `pydantic`-group AI plugin to auto-activate — exactly the leak-note's source-of-truth condition. The bare-install job is therefore the definitive runtime defense, catching the pydantic-plugin activation path the static import-linter structurally cannot see.

The static `import-linter` job logic was also re-confirmed (in the dev `.venv`, which has import-linter via `[dev]`):

```
$ lint-imports
Analyzed 27 files, 78 dependencies.
Core (newsletters) must not import any AI/LLM package KEPT
Contracts: 1 kept, 0 broken.        # exit 0
```

## YAML Validity (plan verify step)

```
$ python -c "import yaml; d=yaml.safe_load(open('.github/workflows/ci.yml')); ..."
triggers: ['push', 'pull_request']
jobs: ['bare-install', 'import-linter']
workflow shape ok
```

Valid YAML; two jobs `bare-install` + `import-linter`; bare job installs `.[test]` and NOT `[ai]`; `lint-imports` present.

## Files

**Created:**
- `.github/workflows/ci.yml` — the first CI workflow: `bare-install` job (PKG-03, canonical bare no-extras full-pipeline gate) + `import-linter` job (PKG-04). The standing AI-optional invariant on every push/PR. Commit `730e58e`.

**Reused unchanged (from 02-01):** `pyproject.toml` (`[ai]`/`[dev]`/`[test]`), `.importlinter` (forbidden contract), `tests/test_ai_optional.py`. **Pre-existing:** `newsletters build` / `build_site`, the spine + distill-socket tests.

## Deviations from Plan

None — plan executed exactly as written. (Note: the `typer 0.26.7 does not provide the extra 'all'` warning surfaced during the throwaway-venv install; it is a pre-existing benign upstream warning from the `typer[all]` core dep — install still succeeded and the pipeline ran. Out of scope for this CI plan; not introduced here. Logged for awareness, not fixed.)

## Authentication Gates

None.

## Known Stubs

None — CI infrastructure; no UI data sources or placeholders introduced.

## Threat Flags

None — no new runtime/network/auth/PII/file-access surface. This plan reduces risk: it makes the AI-optional boundary a standing per-push gate (mitigating T-02-05/06/07) using only pinned first-party actions (T-02-SC, no AI/marketplace supply-chain surface). No new pip package added (reuses 02-01's deps).

## Self-Check: PASSED

- `.github/workflows/ci.yml` exists on disk.
- Commit `730e58e` present in git history.
