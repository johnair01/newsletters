---
phase: 1
slug: distill-socket-contract
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-14
updated: 2026-06-14
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> nyquist_validation is enabled; this is the foundational contract gating all later phases, so
> validation is mandatory. Every task has an `<automated>` verify or a Wave-0 dependency.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (declared in `[dev]`/`[test]`; configured in `pyproject.toml [tool.pytest.ini_options]`: `pythonpath=["src"]`, `testpaths=["tests"]`) + mypy (Protocol-shape gate) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.mypy]`) |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_distill_socket.py -x -q` |
| **Full suite command** | `.venv/bin/python -m pytest -q` (Rev1 `test_semantic.py` + new `test_distill_socket.py`) |
| **Static gate** | `.venv/bin/python -m mypy src/newsletters/distill` |
| **Estimated runtime** | ~3–6 seconds (pure in-process Pydantic; no I/O/network) |

> Interpreter note: base shell is Python 3.11 and lacks pydantic/pytest. Wave 0 (Plan 01, Task 1)
> stands up a Python 3.12 venv via `python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev,test]"`.
> All commands run through `.venv/bin/python`.

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/python -m pytest tests/test_distill_socket.py -x -q`
- **After every plan wave:** Run `.venv/bin/python -m pytest -q` (Rev1 regression tripwire + socket suite)
- **Before `/gsd-verify-work`:** Full suite green AND `mypy src/newsletters/distill` clean
- **Max feedback latency:** ~6 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | (Wave 0 infra) | T-01-SC | No new package installed; stdlib + pre-existing Pydantic only | infra+unit | `.venv/bin/python -c "import pydantic, pytest"` + `pytest tests/test_distill_socket.py::test_socket_end_to_end_manual_roundtrip` (RED) | ❌ W0 → created | ⬜ pending |
| 1-01-02 | 01 | 1 | SOCK-01, SOCK-04, D-05, D-06 | T-01-01 | Bare-string locator coerces; unknown `kind` rejected; "complete with unextracted" unrepresentable | unit | `pytest tests/test_semantic.py -q` + contract import/assert one-liner (Plan 01 Task 2 verify) | ✅ (test_semantic) / ❌ W0 (socket) | ⬜ pending |
| 1-01-03 | 01 | 1 | SOCK-01, SOCK-02, SOCK-03, D-04 | T-01-03, T-01-04, T-01-SC | register rejects non-conformer; resolve backend-agnostic; no AI in sys.modules; socket returns truth only | unit | `pytest tests/test_distill_socket.py -x -q` + `pytest tests/test_semantic.py -q` + `mypy src/newsletters/distill` | ❌ W0 → green | ⬜ pending |
| 1-02-01 | 02 | 2 | SOCK-05 | T-01-03 | Faithfulness enforced in one injectable place; conformance has teeth | unit | `python -c "from newsletters.distill.conformance import assert_conforms; from newsletters.distill.ports import _enforce"` + `mypy src/newsletters/distill` | ❌ W0 → created | ⬜ pending |
| 1-02-02 | 02 | 2 | SOCK-05 | T-01-02, T-01-03, T-01-04, T-01-06 | Broken backend FAILED; lying coverage rejected; no auto-publish; no AI reachable | unit | `pytest tests/test_distill_socket.py -q` + `pytest tests/test_semantic.py -q` | ❌ W0 → green | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → Test Name Crosswalk (one focused test per behavior)

| Req / Rule | Test name (`tests/test_distill_socket.py`) | Plan/Task |
|------------|--------------------------------------------|-----------|
| SOCK-01 | `test_distillport_is_backend_agnostic`, `test_socket_end_to_end_manual_roundtrip` | 01 / T1,T3 |
| SOCK-02 | `test_registry_register_resolve` | 01 / T3 |
| SOCK-03 | `test_manual_backend_zero_ai_traced` | 01 / T3 |
| SOCK-04 / D-05 | `test_coverage_unextracted_distinct_from_missing`, `test_coverage_lying_completeness_rejected` | 01 / T3, 02 / T2 |
| SOCK-05 | `test_conformance_passes_manual_backend`, `test_conformance_fails_bad_backend`, `test_faithfulness_seam_rejects_untraced` | 02 / T2 |
| D-04 (JSON round-trip) | `test_sidecar_roundtrip`, `test_socket_end_to_end_manual_roundtrip` | 01 / T1,T3 |
| D-06 (Locator + span) | `test_locator_union_and_backward_compat` | 01 / T3 |
| HARD: no auto-publish | `test_socket_never_auto_publishes` | 02 / T2 |
| HARD: AI-optional core | `test_distill_package_imports_no_ai` | 01 / T3 (assert), 02 / T2 (canonical) |
| REGRESSION (Rev1 spine) | `tests/test_semantic.py` (unchanged) | both waves |

---

## Wave 0 Requirements

- [ ] Python 3.12 venv at `.venv` with `pip install -e ".[dev,test]"` (base shell is 3.11; lacks pydantic/pytest) — Plan 01, Task 1
- [ ] `mypy` added to `[project.optional-dependencies].dev` in `pyproject.toml` (referenced in config, not declared) — Plan 01, Task 1
- [ ] `tests/conftest.py` — shared WorkSession / sources fixtures mirroring `tests/test_semantic.py:_session()` — Plan 01, Task 1
- [ ] `tests/test_distill_socket.py` — created with the failing e2e test first (RED), then filled across Plan 01 T3 and Plan 02 T2 — Plans 01–02
- [ ] Intentionally-broken backend fixture (untraced claim / lying coverage) for the SOCK-05 negative tests — Plan 02, Task 2

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|

*None — all phase behaviors have automated verification (pytest + mypy). This is a pure typed-contract library phase with no UI/visual surface.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (every task has one)
- [x] Wave 0 covers all MISSING references (`tests/test_distill_socket.py`, `tests/conftest.py`, 3.12 venv, mypy in [dev])
- [x] No watch-mode flags (all commands are single-shot `-q`)
- [x] Feedback latency < 6s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-14 (planner)
