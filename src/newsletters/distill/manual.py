"""The author-by-hand distill backend (SOCK-03, D-01 modality (a), D-02).

``ManualBackend`` is the first of D-01's three modalities (author-by-hand); the extraction
(Phases 4-7) and interview (v2 AI) backends register against the IDENTICAL ``DistillPort``
contract later, unchanged.

It DELEGATES to the existing deterministic ``capture.capture_session()`` — it does not
reimplement claim-building. Zero AI, zero network, no editorializing (the engine already
obeys "structures, does not invent", capture.py:62-64).

SIGNATURE: ``DistillPort.distill(sources)`` is fixed by SOCK-01, but ``capture_session()``
needs a ``WorkSession`` (sources + the human's pre-authored ``Decision[]``). Resolution:
constructor-inject the ``WorkSession`` and keep ``distill(sources)`` signature-exact.

HARD RULE: this returns truth only. It must NEVER call ``Surface.publish()``, set
``ReviewState.PUBLISHED``, or construct a published ``Review``. The existing review gate
(semantic.py:142-150) stays the sole publish path.
"""

from __future__ import annotations

from ..capture import WorkSession, capture_session
from ..semantic import Source
from .coverage import Coverage
from .ports import DistillationResult


class ManualBackend:
    """Author-by-hand backend: wraps a pre-authored ``WorkSession`` into a ``DistillationResult``."""

    name = "manual"

    def __init__(self, session: WorkSession) -> None:
        self._session = session

    def distill(self, sources: list[Source]) -> DistillationResult:
        """Emit the hand-authored distillation. Hand-authored => nothing dropped (fully covered)."""
        return DistillationResult(
            distillation=capture_session(self._session),
            coverage=Coverage.fully_covered(),
            backend=self.name,
        )
