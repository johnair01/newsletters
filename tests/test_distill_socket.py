"""End-to-end + core-contract tests for the Phase-1 distill socket (SOCK-01..04, D-04, D-06).

The conformance/hard-rule negative tests (malformed-backend conformance, no-auto-publish
assertion) land in Plan 02. This suite proves the walking skeleton: register -> resolve ->
distill -> DistillationResult through the DistillPort boundary, hand-authored, zero AI,
JSON-round-tripping, with the import graph guarded acyclic.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from newsletters.capture import WorkSession
from newsletters.distill import (
    Coverage,
    DistillationResult,
    DistillPort,
    FreeLocator,
    ManualBackend,
    SessionLocator,
    Unextracted,
    available,
    register,
    resolve,
)
from newsletters.semantic import Distillation, Source, Trace

AI_MODULES = ("langchain", "langgraph", "langsmith", "pydantic_ai")


# --- SOCK-01..04 + D-04: the end-to-end slice --------------------------------- #


def test_socket_end_to_end_manual_roundtrip(
    work_session: WorkSession, sources: list[Source]
) -> None:
    """The MVP slice: register a ManualBackend, resolve it by name, distill, round-trip."""
    register(ManualBackend(session=work_session))

    result = resolve("manual").distill(sources)

    assert isinstance(result, DistillationResult)
    assert any(c.is_traced for c in result.distillation.claims)  # >=1 traced claim
    assert result.coverage is not None  # coverage present
    # lossless JSON round-trip (D-04)
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result


def test_distillport_is_backend_agnostic(
    work_session: WorkSession, sources: list[Source]
) -> None:
    """The caller uses resolve(name).distill(...) without naming the backend type (D-01)."""
    register(ManualBackend(session=work_session))
    backend = resolve("manual")  # typed as DistillPort, not ManualBackend
    assert isinstance(backend, DistillPort)
    result = backend.distill(sources)
    assert isinstance(result, DistillationResult)


# --- SOCK-02: the registry ---------------------------------------------------- #


def test_registry_register_resolve(work_session: WorkSession) -> None:
    """register stores by name; resolve hits/misses correctly; non-conforming raises TypeError."""
    register(ManualBackend(session=work_session))
    assert "manual" in available()
    assert resolve("manual").name == "manual"

    with pytest.raises(KeyError) as ei:
        resolve("nope")
    assert "nope" in str(ei.value) and "Known" in str(ei.value)

    with pytest.raises(TypeError):
        register(object())  # type: ignore[arg-type]  — no name/distill, fails the shape guard


# --- SOCK-03: the manual backend, zero AI ------------------------------------- #


def test_manual_backend_zero_ai_traced(
    work_session: WorkSession, sources: list[Source]
) -> None:
    """Every emitted claim is traced; the by-hand path drops nothing.

    NOTE: the *AI-isolation* guarantee is checked by ``test_distill_package_imports_no_ai``
    in a fresh subprocess. We do NOT assert ``m not in sys.modules`` here, because pytest's
    setuptools-entrypoint plugin autoload (logfire / pydantic-ai register pytest plugins)
    pulls ``langsmith`` into the *test runner's* sys.modules independently of our import
    graph — that pollution would make an in-process check measure pytest, not our code.
    """
    result = ManualBackend(session=work_session).distill(sources)
    assert result.distillation.claims  # non-empty
    assert all(c.is_traced for c in result.distillation.claims)
    assert result.coverage.complete is True and result.coverage.unextracted == []
    assert result.backend == "manual"
    # content equivalence with the deterministic engine it wraps (no invention)
    from newsletters.capture import capture_session

    assert result.distillation == capture_session(work_session)


# --- SOCK-04 / D-05: coverage honesty, distinct from missing[] ---------------- #


def test_coverage_unextracted_distinct_from_missing(
    work_session: WorkSession,
) -> None:
    """unextracted[] (unreadable) and Distillation.missing[] (unprovable) are different fields."""
    cov = Coverage(
        complete=False,
        unextracted=[Unextracted(locator=FreeLocator(text="raw blob"), reason="binary")],
    )
    dist = Distillation(narrative="n", missing=["an unprovable claim"])
    assert isinstance(cov.unextracted[0], Unextracted)
    assert isinstance(dist.missing[0], str)
    assert type(cov.unextracted) is not type(dist.missing) or (
        cov.unextracted and dist.missing
    )
    # the D-05 honesty invariant: complete + dropped content is unrepresentable
    with pytest.raises(ValueError):
        Coverage(complete=True, unextracted=[Unextracted(locator=FreeLocator(text="x"))])


# --- D-04: lossless JSON sidecar round-trip ----------------------------------- #


def test_sidecar_roundtrip(work_session: WorkSession, sources: list[Source]) -> None:
    """A hand-authored DistillationResult round-trips losslessly via JSON (D-04)."""
    result = ManualBackend(session=work_session).distill(sources)
    reloaded = DistillationResult.model_validate_json(result.model_dump_json())
    assert reloaded == result


# --- D-06: typed Locator union + backward-compat ------------------------------ #


def test_locator_union_and_backward_compat() -> None:
    """Bare str coerces; SessionLocator round-trips; unknown kind rejected; coercion idempotent."""
    # bare string coerces to FreeLocator (the Rev1 / capture path)
    t = Trace(source_id="s1", locator="line 3")
    assert isinstance(t.locator, FreeLocator) and t.locator.text == "line 3"
    assert t.span == ""  # verbatim span defaults empty

    # SessionLocator round-trips through JSON via the discriminator
    t2 = Trace(source_id="s1", locator=SessionLocator(source_id="s1", note="kickoff"))
    rt = Trace.model_validate_json(t2.model_dump_json())
    assert isinstance(rt.locator, SessionLocator) and rt.locator.note == "kickoff"

    # idempotent re-coercion: instance and discriminator-dict both yield equal FreeLocator (no double-wrap)
    assert Trace(source_id="s1", locator=FreeLocator(text="x")).locator == FreeLocator(text="x")
    assert Trace(source_id="s1", locator={"kind": "free", "text": "x"}).locator == FreeLocator(text="x")

    # an unknown discriminator kind is rejected
    with pytest.raises(Exception):
        Trace(source_id="s1", locator={"kind": "bogus", "text": "x"})


# --- import-graph guard (the previously-found cycle, closed and policed) ------- #


def test_import_order_no_cycle() -> None:
    """Fresh subprocess imports of newsletters/.semantic/.distill exit 0 in BOTH orders."""
    forward = "import newsletters; import newsletters.semantic; import newsletters.distill"
    reverse = "import newsletters.distill; import newsletters.semantic; import newsletters"
    for code in (forward, reverse):
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert proc.returncode == 0, f"import order failed:\n{proc.stderr}"


def test_distill_package_imports_no_ai() -> None:
    """A fresh subprocess importing newsletters.distill loads no AI module."""
    code = (
        "import sys, newsletters.distill; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('clean')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"AI leaked: {proc.stdout}{proc.stderr}"


# --- SOCK-05 (Task 1 RED): the conformance API + single-place faithfulness seam --- #


def test_conformance_api_and_seam_exist(
    work_session: WorkSession, sources: list[Source]
) -> None:
    """The Task-1 deliverables are wired: assert_conforms (barrel + module) and _enforce.

    assert_conforms passes the conforming ManualBackend; _enforce applies a default
    StructuralFaithfulness and is the single injectable boundary (the Phase-3 swap point).
    """
    from newsletters.distill import assert_conforms as barrel_assert_conforms
    from newsletters.distill.conformance import assert_conforms
    from newsletters.distill.ports import _enforce, StructuralFaithfulness

    assert barrel_assert_conforms is assert_conforms  # re-exported, same object

    # conforming backend passes and returns the result unchanged
    result = assert_conforms(ManualBackend(session=work_session), sources)
    assert isinstance(result, DistillationResult)

    # _enforce default-applies StructuralFaithfulness and returns the result unchanged
    assert _enforce(result) is result
    assert _enforce(result, StructuralFaithfulness()) is result
