"""The ``DistillPort`` contract — the one boundary every distill backend speaks through (SOCK-01).

The boundary is deliberately MODALITY-AGNOSTIC (D-01): the same ``DistillPort`` ->
``DistillationResult`` shape must accommodate all three distill modalities — author-by-hand,
generic file extraction, agentic interview — so downstream review/render/promote never learns
which one produced a result. Phase 1 builds only the author-by-hand backend (``ManualBackend``);
the others slot into this identical contract in later phases.

``DistillationResult`` is a WRAPPER around ``Distillation`` (it does not mutate it), so the
Rev1 ``Distillation`` type and its tests stay stable (RESEARCH Open Q1). ``backend`` is an
audit-trail string, NOT a behavior switch.

The faithfulness seam (``FaithfulnessCheck`` / ``StructuralFaithfulness``) is injectable: the
Phase-1 default checks only that a claim is traced (reusing ``Claim.is_traced``); Phase 3 can
swap in span-containment without touching any backend.

IMPORT-GRAPH NOTE: the ``from ..semantic import ...`` below is safe. It runs only when
``distill/__init__.py`` imports this module, which happens AFTER ``semantic`` has finished
initializing — because ``semantic`` no longer imports anything from the ``distill`` package
(only from the leaf ``..locators``).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from ..semantic import Claim, Distillation, Source
from .coverage import Coverage


# --------------------------------------------------------------------------- #
# The result wrapper — Distillation + Coverage manifest + audit trail
# --------------------------------------------------------------------------- #


class DistillationResult(BaseModel):
    """What every backend returns: a traced ``Distillation`` plus its ``Coverage`` manifest."""

    distillation: Distillation
    coverage: Coverage = Field(default_factory=Coverage)
    backend: str = ""  # audit trail (which backend produced this), NOT a behavior switch


# --------------------------------------------------------------------------- #
# The port — the runtime-checkable structural contract
# --------------------------------------------------------------------------- #


@runtime_checkable
class DistillPort(Protocol):
    """The one boundary every distill backend speaks through (SOCK-01).

    ``@runtime_checkable`` enables the registry's shallow ``isinstance`` shape guard — it
    checks ATTRIBUTE PRESENCE (``name`` + ``distill``) only, NOT signatures or return types.
    The real malformed-backend guard is Plan 02's runtime conformance suite.
    """

    name: str

    def distill(self, sources: list[Source]) -> DistillationResult: ...


# --------------------------------------------------------------------------- #
# The faithfulness seam — injectable, defaulted to structural (is_traced)
# --------------------------------------------------------------------------- #


class FaithfulnessCheck(Protocol):
    """The injectable faithfulness predicate seam (Phase 3 swaps in span-containment)."""

    def entails(self, claim: Claim) -> bool: ...


class StructuralFaithfulness:
    """The Phase-1 default: a claim is faithful iff it is traced (reuses ``Claim.is_traced``)."""

    def entails(self, claim: Claim) -> bool:
        return claim.is_traced
