"""The reusable RUNTIME conformance checker (SOCK-05) — the contract's immune system.

``assert_conforms(backend, sources)`` runs ANY registered backend through the socket
contract and FAILS it on a violation. This routine — NOT mypy — is the malformed-backend
guard (review MEDIUM-2):

* ``@runtime_checkable`` ``isinstance(.., DistillPort)`` only checks ATTRIBUTE PRESENCE
  (``name`` + ``distill``), never signatures or return types.
* mypy only ever type-checks the conforming in-``src`` ``ManualBackend``; the deliberately
  broken backend that PROVES the contract has teeth lives in ``tests/`` and is never seen by
  the type checker.

So the runtime checks here are the real teeth. A backend that smuggles an untraced claim,
returns a lying coverage manifest, returns the wrong type, or tries to route around the
no-auto-publish gate is rejected HERE, at runtime.

This module lives in ``distill/`` (importable by any backend's own tests), DISTINCT from
``tests/test_distill_socket.py`` which *drives* it with a broken-backend fixture.

HARD RULE — AI-optional core: this module imports only stdlib + Pydantic via the package; it
imports no AI library. The faithfulness rule is delegated to the single-place ``_enforce``
seam in ``ports.py`` (injectable for the Phase-3 span-containment swap).
"""

from __future__ import annotations

from ..semantic import Source
from .ports import (
    DistillationResult,
    DistillPort,
    FaithfulnessCheck,
    StructuralFaithfulness,
    _enforce,
)


def assert_conforms(
    backend: DistillPort,
    sources: list[Source],
    *,
    check: FaithfulnessCheck = StructuralFaithfulness(),
) -> DistillationResult:
    """Run ``backend`` through the socket contract; raise on any violation, else return its result.

    The malformed-backend guard (SOCK-05). Asserts, in order:

    1. ``isinstance(backend, DistillPort)`` — it has ``name`` + ``distill()`` (the shape guard;
       a runtime-checkable structural test, the same one the registry uses).
    2. ``distill(sources)`` returns a ``DistillationResult`` — never a ``Surface``/``Review`` or
       any other type (the return type is truth-only; this is also the no-auto-publish hard
       rule — the socket cannot hand back a published anything).
    3. ``result.coverage is not None`` and is internally honest — the ``Coverage`` validator
       already forbids "complete with dropped content" (SOCK-04 / D-05), so merely receiving a
       constructed ``Coverage`` proves that invariant held.
    4. Every emitted claim passes the injected faithfulness ``check`` via the single-place
       ``_enforce`` seam (default: every claim traced — ``StructuralFaithfulness``). The
       ``check`` parameter is the Phase-3 swap point; no backend changes when it changes.
    5. The lossless JSON round-trip ``model_validate_json(model_dump_json()) == result`` (D-04)
       — the result is a faithful, serializable sidecar.

    Returns the validated ``DistillationResult`` so a caller can keep using it.
    """
    # 1. shape guard — must look like a DistillPort (name + distill)
    assert isinstance(backend, DistillPort), (
        f"Not a DistillPort: {type(backend).__name__} is missing `name` and/or `distill()`. "
        "A backend must satisfy the @runtime_checkable DistillPort shape (SOCK-01)."
    )

    result = backend.distill(sources)

    # 2. return-type guard — truth only, never a published Surface/Review (HARD RULE)
    assert isinstance(result, DistillationResult), (
        f"distill() returned {type(result).__name__}, not a DistillationResult. "
        "The socket returns truth only — never a Surface or Review. No auto-publish path."
    )

    # 3. coverage present + honest (the Coverage validator already enforced SOCK-04/D-05)
    assert result.coverage is not None, (
        "DistillationResult has no coverage manifest. Every result must report what it read "
        "and what it dropped (SOCK-04 / D-05) — there is no silent dropping."
    )

    # 4. faithfulness — enforced in exactly one place (ports._enforce), injectable check
    _enforce(result, check)

    # 5. lossless JSON sidecar round-trip (D-04)
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result, (
        "DistillationResult does not round-trip losslessly through JSON (D-04). The sidecar "
        "must be a faithful, serializable record of the distillation."
    )

    return result
