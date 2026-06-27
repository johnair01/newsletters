---
phase: 01-distill-socket-contract
plan: 01
subsystem: distill-socket
tags: [contract, registry, locator, coverage, pydantic, ports-and-adapters]
requires:
  - "Rev1 spine (Source/Claim/Trace/Distillation/Review) in src/newsletters/semantic.py"
  - "capture_session() in src/newsletters/capture.py"
  - "the templates.py registry idiom + the Block discriminated-union idiom"
provides:
  - "DistillPort Protocol — the modality-agnostic distill boundary (SOCK-01)"
  - "register/resolve/available backend registry (SOCK-02)"
  - "ManualBackend — the author-by-hand modality (SOCK-03, D-01/D-02)"
  - "Coverage + Unextracted — the unextracted[] honesty contract (SOCK-04, D-05)"
  - "Locator discriminated union + widened Trace (typed locator + verbatim span, D-06)"
  - "DistillationResult — lossless JSON sidecar round-trip (D-04)"
affects:
  - "src/newsletters/semantic.py (Trace widened, backward-compatible)"
  - "src/newsletters/render.py (evidence-chip now reads locator.display)"
tech-stack:
  added: []
  patterns:
    - "ports-and-adapters: @runtime_checkable typing.Protocol as the contract boundary"
    - "top-level leaf module to break a would-be import cycle"
    - "self-consistency model_validator that makes a dishonest state unrepresentable"
    - "field_validator(mode='before') for idempotent str -> typed coercion"
key-files:
  created:
    - "src/newsletters/locators.py"
    - "src/newsletters/distill/__init__.py"
    - "src/newsletters/distill/coverage.py"
    - "src/newsletters/distill/ports.py"
    - "src/newsletters/distill/registry.py"
    - "src/newsletters/distill/manual.py"
    - "tests/test_distill_socket.py"
    - "tests/conftest.py"
  modified:
    - "src/newsletters/semantic.py"
    - "src/newsletters/render.py"
    - "pyproject.toml"
decisions:
  - "Placed the Locator union in a TOP-LEVEL leaf module (src/newsletters/locators.py), not inside the distill package, to keep the import graph genuinely acyclic (semantic -> locators leaf; distill -> locators leaf)."
  - "DistillationResult WRAPS Distillation rather than adding a coverage field to it — keeps the Rev1 type and tests stable (RESEARCH Open Q1)."
  - "ManualBackend constructor-injects the WorkSession so distill(sources) stays signature-exact per SOCK-01."
  - "Replaced the in-process sys.modules AI-isolation assertion with a fresh-subprocess guard, because pytest's setuptools-entrypoint plugin autoload (logfire/pydantic-ai) pulls langsmith into the runner independently of our import graph."
metrics:
  duration: "~25 min"
  completed: "2026-06-17"
  tasks: 3
  files_created: 8
  files_modified: 3
---

# Phase 1 Plan 1: Distill Socket Contract Summary

The thinnest end-to-end slice that proves the distill socket: a caller can `register(ManualBackend(session=ws))`, then `resolve("manual").distill(sources)` through the `DistillPort` boundary and receive a valid `DistillationResult` (traced `Distillation` + `Coverage` manifest) that round-trips losslessly to/from JSON — all with zero AI. The contract is deliberately modality-agnostic (D-01): the same `DistillPort -> DistillationResult` shape will accommodate file-extraction and agentic-interview backends unchanged in later phases.

## What Was Built

- **`src/newsletters/locators.py`** (NEW top-level leaf) — the `Locator` discriminated union (`FreeLocator` + `SessionLocator`, `Field(discriminator="kind")`), importing only stdlib + pydantic. This placement is the load-bearing circular-import fix: both `semantic` and `distill` depend on it as a leaf, with no path back into a partially-initialized `semantic`. Adapter-phase variants (Message/Cell/Slide/Code/Turn) are commented stubs documenting the contract's reach. Each variant carries a `display` property used by the renderer.
- **`src/newsletters/distill/coverage.py`** — `Coverage` + `Unextracted`. A `model_validator(mode="after")` makes "complete with dropped content" *unrepresentable* (D-05 honesty invariant), mirroring the no-auto-publish gate. `unextracted[]` (unreadable) stays distinct from `Distillation.missing[]` (unprovable). `fully_covered()` classmethod takes no args. `cost_hint`/`effort_hint` carry the D-03 low-token signal.
- **`src/newsletters/distill/ports.py`** — `DistillationResult` (wraps `Distillation`, default `Coverage`, `backend` audit string), `@runtime_checkable DistillPort` Protocol, the injectable `FaithfulnessCheck` seam + `StructuralFaithfulness` (`entails == claim.is_traced`).
- **`src/newsletters/distill/registry.py`** — `_BACKENDS` dict + `register`/`resolve`/`available`, copying the `templates.py` idiom; `register` raises `TypeError` on a non-conforming object (shallow `isinstance(DistillPort)` shape guard).
- **`src/newsletters/distill/manual.py`** — `ManualBackend` (name `"manual"`, constructor-injected `WorkSession`) delegates to `capture_session()`; emits `fully_covered()` coverage. Hard rule honored: returns truth only, never publishes.
- **`src/newsletters/distill/__init__.py`** — public barrel; `register`/`resolve` deliberately NOT re-exported at package root (would shadow `templates.register`).
- **`semantic.py`** — `Trace.locator` widened `str -> Locator` with an idempotent `str -> FreeLocator` coercion validator; new verbatim `span: str = ""` field (D-06). Imports from the leaf `.locators`.
- **Tooling** — `pyproject.toml` adds `mypy` to `[dev]` (core `dependencies` untouched); a Python 3.12 venv was stood up and installed editable with `[dev,test]`.

## How It Works (the why)

The socket is a ports-and-adapters boundary. `DistillPort` is the *port*; `ManualBackend` is the first *adapter*. The registry decouples selection (`resolve(name)`) from construction, so downstream review/render/promote never learn which modality produced a result — that is what makes the contract modality-agnostic. The faithfulness seam is injectable in one place so Phase 3 can swap structural tracing for span-containment without touching any backend. The Locator-as-leaf decision is the genuinely-acyclic fix the prior cross-AI review flagged: a union inside the distill package would force `semantic` to trigger the distill barrel mid-init.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Locator widening broke the evidence-chip renderer**
- **Found during:** Task 2 (the `pytest tests/test_semantic.py` regression tripwire).
- **Issue:** `render.py:215` did `_e(t.locator)`, assuming `locator` is a `str`. After the widening it became a `FreeLocator`, raising `AttributeError: 'FreeLocator' object has no attribute 'replace'` in two Rev1 render tests.
- **Fix:** Added a `display` property to each `Locator` variant (free-text passthrough; session -> `source_id (note)`) and changed the renderer to read `t.locator.display`. Keeps rendering faithful and makes the union self-describing.
- **Files modified:** `src/newsletters/locators.py`, `src/newsletters/render.py`
- **Commit:** f58ac01

**2. [Rule 1 - Bug] In-process AI-isolation assertion measured pytest, not our code**
- **Found during:** Task 3 (`test_manual_backend_zero_ai_traced` failed: "langsmith leaked into sys.modules").
- **Issue:** pytest autoloads setuptools-entrypoint plugins (logfire / pydantic-ai), which import `langsmith` into the *test runner's* `sys.modules` independently of our import graph. The in-process `assert m not in sys.modules` therefore measured the runner, not the distill package.
- **Fix:** Removed the in-process `sys.modules` assertion; the AI-isolation guarantee is enforced by the fresh-subprocess `test_distill_package_imports_no_ai` (which the plan already specifies). Verified directly: a clean `python -c "import newsletters.distill"` leaks zero AI modules.
- **Files modified:** `tests/test_distill_socket.py`
- **Commit:** fdb7154

## Verification (gates re-run independently, actual output)

- Fresh-interpreter import order, **both directions**: `forward OK` / `reverse OK` (no circular import).
- `pytest tests/test_distill_socket.py -q` -> **9 passed**.
- `pytest tests/test_semantic.py -q` (Rev1 regression tripwire) -> **18 passed**.
- `pytest -q` (whole suite) -> **27 passed**.
- `mypy src/newsletters/distill` -> **Success: no issues found in 5 source files**.
- No AI in `sys.modules` after a clean-subprocess `import newsletters.distill` (`langchain`/`langgraph`/`langsmith`/`pydantic_ai` all absent).
- Source assertion: no AI imports anywhere under `src/newsletters/distill/` or in `src/newsletters/locators.py`.
- Namespacing: `newsletters.register is templates.register` (not shadowed); no `resolve` at package root.

## Hard Rules Honored

- **AI-optional core:** `distill/` and `locators.py` import only stdlib + Pydantic; zero AI reachable from core (source + clean-subprocess `sys.modules` assertion).
- **No auto-publish:** `ManualBackend` returns a `DistillationResult` only — never calls `Surface.publish()`, sets `ReviewState.PUBLISHED`, or builds a published `Review`. The Rev1 review gate stays the sole publish path (Rev1 suite still green).
- **Typed everything / faithful, not suggestive:** all new models are Pydantic; `ManualBackend` delegates to the deterministic `capture_session()` (structures, does not invent).

## Known Stubs

The adapter-phase `Locator` variants (`MessageLocator`/`CellLocator`/`SlideLocator`/`CodeLocator`/`TurnLocator`) are intentional commented stubs in `locators.py` documenting the contract's reach — they are built in the adapter phases (4–7) and the v2 AI track, not Phase 1. This is by design per D-02; no Phase-1 goal depends on them.

## Self-Check: PASSED

- Files created — all FOUND: `locators.py`, `distill/{__init__,coverage,ports,registry,manual}.py`, `tests/test_distill_socket.py`, `tests/conftest.py`.
- Commits exist: a57dd82 (Task 1), f58ac01 (Task 2), fdb7154 (Task 3).
