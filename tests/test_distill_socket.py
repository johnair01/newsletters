"""End-to-end + core-contract tests for the Phase-1 distill socket (SOCK-01..04, D-04, D-06).

The conformance/hard-rule negative tests (malformed backend, no-auto-publish assertion)
land in Plan 02. This suite proves the walking skeleton: register -> resolve -> distill ->
DistillationResult through the DistillPort boundary, hand-authored, zero AI, JSON-round-tripping.
"""

from __future__ import annotations

from newsletters.capture import WorkSession
from newsletters.distill import ManualBackend, register, resolve
from newsletters.distill.ports import DistillationResult
from newsletters.semantic import Source


def test_socket_end_to_end_manual_roundtrip(
    work_session: WorkSession, sources: list[Source]
) -> None:
    """The MVP slice: register a ManualBackend, resolve it by name, distill, round-trip.

    The caller never names the backend type after construction — it speaks only through
    the DistillPort boundary (resolve(name).distill(sources)).
    """
    backend = ManualBackend(session=work_session)
    register(backend)

    result = resolve("manual").distill(sources)

    assert isinstance(result, DistillationResult)
    # (4) >=1 traced claim
    assert any(c.is_traced for c in result.distillation.claims)
    # (5) coverage present
    assert result.coverage is not None
    # (6) lossless JSON round-trip (D-04)
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result
