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

SECURITY (CONTEXT hard rule / threat T-01-01): config YAML is parsed through a
``yaml.SafeLoader`` subclass ONLY — safe-only construction, never ``yaml.load`` with a full
loader, which can construct arbitrary Python objects from untrusted config text; config files are
data, not code. This is a hard "faithful, not suggestive / no surprises" boundary. The one
extension the subclass carries is a REFUSAL, not a widening: duplicate mapping keys raise a
teaching ``ValueError`` instead of silently keeping the last occurrence (03-review CR-01).
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
    """Parse module-config YAML text with safe-only construction — and REFUSE duplicate keys.

    Safe-only (CONTEXT hard rule / threat T-01-01): config files are data, not code, so the parse
    path is a ``yaml.SafeLoader`` subclass and NOTHING else — we NEVER call ``yaml.load`` with a
    full loader (which can construct arbitrary Python objects from untrusted input). Malformed
    YAML raises ``yaml.YAMLError``, which the caller surfaces (never swallowed).

    DUPLICATE MAPPING KEYS ARE A REFUSAL (03-review CR-01). ``yaml.safe_load`` keeps only the
    LAST occurrence of a duplicated key, silently dropping everything the first one carried — a
    weekly authored with ``highlights:`` twice (a plausible append or merge-conflict mistake)
    would lose its entire first list before any validator ever saw it. That is precisely the
    failure the strict spec schemas exist to refuse ("Refusing to drop authored content
    silently"), so the refusal lives HERE, at the ONE parse boundary, and every loader that
    parses through it (``casespec``, ``swimlane``, ``weeklyspec``) inherits it. The check runs on
    every mapping node at every depth — a duplicated field inside a recognition or an asset
    record is the same silent drop one level down.

    Args:
        text: the raw YAML config text (typically ``path.read_text("utf-8")``).

    Returns:
        The parsed YAML document (typically a ``dict``; typed ``Any`` to keep the boundary opaque).

    Raises:
        ImportError: if ``PyYAML`` is not installed (via :func:`_load_yaml`).
        ValueError: if any mapping carries the same key twice (a teaching error naming the key
            and BOTH line numbers — never a silent last-wins drop).
        yaml.YAMLError: if the config text is malformed.
    """
    yaml = _load_yaml()

    class _NoDuplicateKeys(yaml.SafeLoader):  # a SafeLoader SUBCLASS — still safe-only
        pass

    def _checked_mapping(loader: Any, node: Any, deep: bool = False) -> Any:
        seen: dict[Any, Any] = {}
        for key_node, _value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                first = seen.get(key)
            except TypeError:
                # An unhashable key (a list/mapping key) — SafeLoader.construct_mapping below
                # raises its own ConstructorError for it; duplicate detection does not apply.
                continue
            if first is not None:
                raise ValueError(
                    f"duplicate key {key!r} at line {key_node.start_mark.line + 1} "
                    f"(first authored at line {first.start_mark.line + 1}) — YAML keeps only "
                    "the LAST occurrence, silently dropping everything the first one carried. "
                    "Refusing to drop authored content silently."
                )
            seen[key] = key_node
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)

    _NoDuplicateKeys.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _checked_mapping
    )
    # Drive the loader directly (exactly what ``yaml.load(text, Loader=...)`` does internally),
    # so no ``yaml.load`` call — the module's safe-only banner stays literally true.
    loader = _NoDuplicateKeys(text)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


__all__ = ["_load_yaml", "load_config", "MISSING_YAML_MESSAGE"]
