"""The distill socket — the modality-agnostic boundary every backend speaks through.

See ``docs/architecture.md`` and ``.planning/phases/01-distill-socket-contract/``. The
contract: ``register(backend)`` then ``resolve(name).distill(sources) -> DistillationResult``,
so downstream review/render/promote never knows which backend (author-by-hand, file
extraction, agentic interview) produced a result (D-01).

NAMESPACING: ``register``/``resolve`` are exported from ``newsletters.distill`` ONLY — never
re-exported at the package root ``newsletters``, where they would shadow the existing
``templates.register`` re-export (review MEDIUM-1).

The ``Locator`` union is re-exported here from the top-level leaf ``..locators`` so consumers
can do ``from newsletters.distill import Locator``; it physically lives outside this package to
keep the import graph acyclic.
"""

from __future__ import annotations

from ..locators import FreeLocator, Locator, SessionLocator
from .coverage import Coverage, Unextracted
from .manual import ManualBackend
from .ports import (
    DistillationResult,
    DistillPort,
    FaithfulnessCheck,
    StructuralFaithfulness,
)
from .registry import available, register, resolve

__all__ = [
    # contract
    "DistillPort",
    "DistillationResult",
    "FaithfulnessCheck",
    "StructuralFaithfulness",
    # registry (NOT re-exported at package root — would shadow templates.register)
    "register",
    "resolve",
    "available",
    # backends
    "ManualBackend",
    # coverage / honesty
    "Coverage",
    "Unextracted",
    # locators (re-exported from the top-level leaf ..locators)
    "Locator",
    "FreeLocator",
    "SessionLocator",
]
