"""Lazy PyYAML boundary — the optional ``[config]`` extra, imported only on use (LANE-04).

WHY THIS MODULE EXISTS (CONTEXT packaging decision, threat T-01-01 + T-01-SC):
``PyYAML`` is a third-party dependency that backs the swim-lane module-config loader. It is NOT AI,
so the ``forbid-ai-in-core`` import-linter contract is unaffected — but the AI-optional /
minimal-core invariant still demands that a bare ``pip install .`` (no ``[config]``) can
``import newsletters`` and run the deterministic spine with zero PyYAML. We achieve that by
mirroring the ``[ai]`` / ``[excel]`` lazy-import discipline: **yaml is never imported at module
top-level anywhere reachable from ``import newsletters``.** It is imported INSIDE
:func:`_load_yaml`, which the swim-lane loader (Plan 01-02) calls only when it actually parses a
config file. Absence raises a clear teaching :class:`ImportError` pointing at ``pip install
'.[config]'``.

This module itself must therefore have NO top-level ``import yaml`` / ``from yaml ...`` — the
bare-install gate (``tests/test_ai_optional.py``, extended by Plan 01-04) asserts grep-count 0 for
those edges.

SECURITY (CONTEXT hard rule / threat T-01-01): config YAML is parsed with :func:`yaml.safe_load`
ONLY, never :func:`yaml.load`. ``yaml.load`` can construct arbitrary Python objects from untrusted
config text; config files are data, not code. This is a hard "faithful, not suggestive / no
surprises" boundary.
"""

from __future__ import annotations

from typing import Any

# NOTE on typing: PyYAML 6.x ships inline type information, but we keep the boundary OPAQUE (``Any``)
# and deliberately do NOT add a ``types-PyYAML`` stub package — mirroring the openpyxl Any-typing
# decision. The module objects are typed as ``Any`` (mypy then treats them opaquely, which is
# correct: the faithful config-parsing logic lives in the 01-02 loader, not here).

# The exact teaching message a user sees if they reach the config loader without the extra.
# Exposed as a module constant so tests can assert against it without string-duplication drift.
MISSING_YAML_MESSAGE = (
    "The module-config loader requires the optional 'PyYAML' dependency. "
    "Install it with: pip install '.[config]'  (or: pip install newsletters[config]). "
    "The deterministic spine runs without it — PyYAML is needed only for YAML config loading "
    "(AI-optional / minimal-core: third-party deps live behind extras)."
)


def _load_yaml() -> Any:
    """Import and return the ``yaml`` module, lazily.

    The import lives INSIDE this function (never at module top) so that importing ``newsletters``
    never requires the ``[config]`` extra. If PyYAML is not installed, re-raise a teaching
    :class:`ImportError` naming the extra and the install command, and stating the spine runs
    without it.

    Returns:
        The imported ``yaml`` module.

    Raises:
        ImportError: if ``PyYAML`` is not installed, with an actionable message.
    """
    try:
        # PyYAML ships no type stubs and we deliberately do NOT add types-PyYAML (mirror the
        # openpyxl Any-typing decision) -> ignore the missing-stub error. PLC0415: lazy on
        # purpose (optional [config] extra, T-01-SC).
        import yaml  # type: ignore[import-untyped]  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(MISSING_YAML_MESSAGE) from exc
    return yaml


def load_config(text: str) -> Any:
    """Parse module-config YAML text with ``safe_load`` ONLY.

    ``yaml.safe_load`` is the sole parse path (CONTEXT hard rule / threat T-01-01): config files
    are data, not code, so we NEVER call ``yaml.load`` (which can construct arbitrary Python
    objects from untrusted input). Malformed YAML raises ``yaml.YAMLError``, which the caller
    surfaces (never swallowed).

    Args:
        text: the raw YAML config text (typically ``path.read_text("utf-8")``).

    Returns:
        The parsed YAML document (typically a ``dict``; typed ``Any`` to keep the boundary opaque).

    Raises:
        ImportError: if ``PyYAML`` is not installed (via :func:`_load_yaml`).
        yaml.YAMLError: if the config text is malformed.
    """
    return _load_yaml().safe_load(text)


__all__ = ["_load_yaml", "load_config", "MISSING_YAML_MESSAGE"]
