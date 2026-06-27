---
phase: 02
name: ai-optional-packaging-boundary
status: passed
verified_by: orchestrator (independent gate re-run, not trusted from SUMMARY)
date: 2026-06-17
score: 4/4 success criteria (PKG-01..04)
---

# Phase 2 Verification — AI-Optional Packaging Boundary

**Status: PASSED** (4/4 success criteria). Verified by independently re-running the gates against
the live repo, not by trusting the executor SUMMARYs.

## Success criteria

1. **Bare `pip install .` runs the full spine with zero AI (PKG-01)** — ✅ Proven in a throwaway
   3.12 venv (`pip install .[test]`, no `[ai]`): all 7 AI modules raise `ImportError`,
   `newsletters build` writes `index.html` (9 surfaces), and `import newsletters` leaves zero AI
   in `sys.modules`. Core `dependencies` are now `pydantic>=2`, `typer[all]`, `sqlmodel` only.
2. **AI deps behind `[ai]`, lazy-only (PKG-02)** — ✅ `[project.optional-dependencies] ai =
   ["pydantic-ai"]`; `langsmith` dropped (CLAUDE.md out-of-scope), `langchain`/`langgraph` removed
   (grep-confirmed zero usage). `grep -rnE 'import (langchain|langgraph|langsmith|pydantic_ai|
   logfire)' src/` → 0.
3. **CI bare-install gate fails if AI reachable (PKG-03)** — ✅ `.github/workflows/ci.yml` job
   `bare-install` installs `.[test]`, asserts AI absence, runs the full pipeline, runs the AI-
   isolation suite under the bare interpreter. Canonical proof: on the bare install
   `test_no_ai_pydantic_plugin_active` passes **strictly** (dev-venv xfail → bare-install pass),
   closing the Phase-1 pydantic-plugin leak. YAML validated: jobs `[bare-install, import-linter]`,
   triggers `[push, pull_request]`.
4. **Import-linter contract, CI-enforced (PKG-04)** — ✅ `.importlinter` forbidden contract
   `lint-imports` → "Contracts: 1 kept, 0 broken"; teeth proven (a transient core→pydantic_ai edge
   flipped it to broken, then reverted). CI job `import-linter` runs `lint-imports` every push/PR.

## Hard rules
- **AI-optional core** — enforced two ways now: static (import-linter, necessary-not-sufficient) +
  runtime/bare-install (canonical, catches pydantic-plugin activation). The leak-note guidance is
  fully implemented.
- **No telemetry / phone-home** — `langsmith` removed entirely.
- **Rev1 + Phase-1 regression** — 36 passed / 1 xfailed in dev venv (xfail = ambient logfire, by
  design); 37 passed / 0 xfailed on bare install.

## Gaps / notes
- None blocking. Benign: newer `typer` (≥0.26) deprecates the `[all]` extra (warning only; install
  succeeds). Low-priority cleanup — change `typer[all]` → `typer` whenever a future phase touches
  deps. Logged, not fixed (out of Phase-2 scope).
