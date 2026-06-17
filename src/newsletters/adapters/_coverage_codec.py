"""The shared adapter coverage codec (TASK ZERO, R1) — the ONE Unextracted <-> carrier bridge.

An adapter determines its ``unextracted[]`` drops as ``list[Unextracted]`` (the ``distill.coverage``
honesty type). To make that determination survive a ``Source`` round-trip (R1), it is carried on
``Source.extraction`` as an ``ExtractionRecord`` (the leaf carrier in ``locators``). This module is
the SINGLE place that bridges the two:

* ``encode_coverage(drops)``  — at ``parse()`` time, an adapter sets ``source.extraction =
  encode_coverage(drops)`` so the drops travel with the Source through ``model_dump_json``.
* ``decode_coverage(record)`` — at ``distill()`` time, an adapter recovers the drops via
  ``decode_coverage(source.extraction)``, reconstructing the original ``list[Unextracted]`` exactly.

This module lives in the ``adapters`` tier precisely because it imports BOTH the leaf carrier
(``locators.ExtractionRecord``/``ExtractedDrop``) AND ``distill.coverage.Unextracted`` — it is the
allowed bridge, so neither ``semantic`` nor ``locators`` ever has to import ``distill`` (the
acyclic-import rule). Both the Email retrofit (Plan 02-this) and the Excel adapter (Plan 03) use
this one codec; the round-trip parity test pins it.

The codec is TOTAL: ``decode_coverage(None) -> []`` (a Source not produced by an adapter has no
carrier) and it never raises. Pydantic validates the ``ExtractionRecord`` itself at load time, so a
structurally invalid carrier fails at ``model_validate``, not silently here (threat T-05-03).

AI-free: stdlib + Pydantic only, no new dependency.
"""

from __future__ import annotations

from typing import Optional

from ..distill.coverage import Unextracted
from ..locators import ExtractedDrop, ExtractionRecord, FreeLocator

# The explicit R2 safety-net reason: an adapter handed a Source it cannot account for (no carrier
# AND not re-derivable) records THIS marker so Coverage.complete is forced False — never a silent
# complete=True. Shared so the parity test can assert it is ABSENT for reconstructable fixtures.
COVERAGE_NOT_RECONSTRUCTABLE = "coverage-not-reconstructable"


def encode_coverage(drops: list[Unextracted]) -> ExtractionRecord:
    """Map an adapter's ``list[Unextracted]`` to the typed ``ExtractionRecord`` carrier (R1).

    Each ``Unextracted`` becomes an ``ExtractedDrop`` carrying the SAME ``locator`` and ``reason``,
    verbatim and order-preserving. The result is set on ``Source.extraction`` so the determination
    travels with the Source. Round-trips losslessly: ``decode_coverage(encode_coverage(drops)) ==
    drops``.
    """
    return ExtractionRecord(
        unextracted=[
            ExtractedDrop(locator=u.locator, reason=u.reason) for u in drops
        ]
    )


def decode_coverage(record: Optional[ExtractionRecord]) -> list[Unextracted]:
    """Reconstruct an adapter's ``list[Unextracted]`` from a (possibly round-tripped) carrier.

    TOTAL by contract: ``decode_coverage(None) -> []`` (a Source not produced by an adapter has no
    drops) and it never raises. Reconstructs the original list exactly, including ``FreeLocator``
    and ``SessionLocator`` variants and empty reasons.
    """
    if record is None:
        return []
    return [
        Unextracted(locator=d.locator, reason=d.reason) for d in record.unextracted
    ]


def not_reconstructable_marker(source_id: str) -> Unextracted:
    """The R2 safety-net marker for a Source whose coverage cannot be reconstructed.

    Naming the source id keeps the disclosure auditable; the fixed reason
    (``COVERAGE_NOT_RECONSTRUCTABLE``) forces ``Coverage.complete=False`` via the Coverage
    validator. Honest uncertainty over a silent ``complete=True``.
    """
    return Unextracted(
        locator=FreeLocator(text=source_id), reason=COVERAGE_NOT_RECONSTRUCTABLE
    )
