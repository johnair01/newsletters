"""The distill-backend registry (SOCK-02) — copies the ``templates.py`` registry idiom.

``register(backend)`` stores a backend under ``backend.name``; ``resolve(name)`` looks it up
(``KeyError`` naming the known backends on a miss); ``available()`` lists registered names.

The ``isinstance(backend, DistillPort)`` check in ``register()`` is a SHALLOW shape guard —
``@runtime_checkable`` only confirms ATTRIBUTE PRESENCE (``name`` + ``distill``), not the
signature or return type (review MEDIUM-2). The real malformed-backend guard is Plan 02's
runtime conformance suite (``assert_conforms``); ``mypy`` only confirms the in-``src``
ManualBackend conforms. Do not over-credit either.

NAMESPACING: ``register``/``resolve`` live under ``newsletters.distill`` only — never at the
package root, where ``register`` would shadow the existing ``templates.register`` re-export.
"""

from __future__ import annotations

from .ports import DistillPort

_BACKENDS: dict[str, DistillPort] = {}


def register(backend: DistillPort) -> DistillPort:
    """Register a distill backend under ``backend.name`` (forkability — no core change needed).

    Raises ``TypeError`` if ``backend`` does not structurally satisfy ``DistillPort`` (the
    shallow attribute-presence guard).
    """
    if not isinstance(backend, DistillPort):
        raise TypeError(
            f"{backend!r} does not satisfy the DistillPort contract "
            "(needs a 'name' attribute and a 'distill' method)."
        )
    _BACKENDS[backend.name] = backend
    return backend


def resolve(name: str) -> DistillPort:
    """Look up a registered backend by name."""
    try:
        return _BACKENDS[name]
    except KeyError:
        raise KeyError(
            f"No distill backend named {name!r}. Known: {sorted(_BACKENDS)}"
        ) from None


def available() -> list[str]:
    """The sorted names of all registered backends."""
    return sorted(_BACKENDS)
