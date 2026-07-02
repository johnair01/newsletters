"""LANE-01/LANE-02 — the read-only, deterministic, AI-free swim-lane config loader (Phase 1).

This module turns a MODULE-CONFIG YAML file into a content-addressed ``Source`` (whose transcript
IS the raw file text) plus one :class:`SectionBinding` per configured lane, minting every value it
reads into a content-addressed ``Claim``/``KpiItem`` via ``Trace.from_source`` — or routing it
honestly to ``unextracted[]`` with a reason code. It is the milestone's foundation: Phase 2's
composer consumes ``SectionBinding[]``. Because it is the circuit-breaker gate, honesty and
determinism are enforced *in code*, not asserted in prose.

WHY a new top-level module (sibling of ``worksurface.py``, not an ``adapters/`` adapter): like
``worksurface.py`` this is a plain, read-only, content-addressed ``Source`` ingest over a
hand-authored corpus (here, a YAML config), NOT a modality extraction routed through a
``DistillPort``. It mirrors ``worksurface.capture_files``'s edge policy and ``adapters/normalize``'s
forward-only cursor mint loop — the two proven precedents this module is a composite of.

The four-property contract (mirrors ``worksurface.py``):

* READ-ONLY. The ONLY filesystem operation is ``Path.read_text`` — no write, no network, no
  ``datetime.now()``. Config files are read as data, never executed (parsing is delegated to Plan
  01-01's ``_yaml_loader.load_config``, i.e. ``yaml.safe_load`` ONLY).
* CONTENT-ADDRESSABLE. Every value is pinned via ``Trace.from_source`` — the SOLE trace-minting
  path (this module NEVER hand-mints a ``content_hash`` or fabricates an offset). Every emitted
  trace ``is_addressed`` is True (closes Hole B upstream: no un-addressed free-pass trace ever
  leaves this loader).
* DETERMINISTIC. ``Source.timestamp`` is the fixed ``EPOCH_ZERO`` sentinel (never ``now()``);
  lanes/KPIs/scalars are iterated in FILE ORDER (no ``set()``, no non-total sort), so the same
  file always produces byte-identical Sources + bindings (SITE-06).
* AI-FREE / MINIMAL-CORE. Imports only stdlib + pydantic + the core ``semantic`` / ``locators`` /
  ``_timestamps`` / ``coverage`` modules + the lazy ``_yaml_loader`` boundary. NO ``distill``
  package, ``render``, ``site``, ``models``, or any AI package is imported (respect the leaf rule).
  ``yaml`` is never imported at module top level — it comes via the lazy ``[config]`` boundary.

READ-ANCHORED COVERAGE (Pitfall 9, the Phase-7 silent-drop lesson): coverage is anchored to the
scalars actually READ, not to the units emitted. Every non-null scalar leaf in the parsed config is
either minted into a content-addressed ``Claim``/``KpiItem`` value OR disclosed in
``unextracted[]`` with a reason code — ``len(all claims) + len(all unextracted) == scalars walked``,
zero silent drops. This identity is enforced by construction (a mismatch raises).

NON-GOALS (deliberate, by design):

* NO ``Surface`` / composition — Phase 2 consumes this phase's ``SectionBinding[]``.
* NO ``compute_delta`` — KPI period endpoints are emitted as INDEPENDENTLY-traced values; Phase 2
  computes Δ from the two traced endpoints. ``KpiItem.delta``/``.dir`` are left ``None`` here.
* NO ``models.py`` instantiation. Lanes are bound at the PARSED-DICT level; this loader never
  constructs ``models.FunctionalGroup``/``Kpi``/``Objective`` (the live ``owner: str`` idsid vs
  ``TeamMember`` type tension is out of scope by design). ``models.py`` is untouched.
* NO fixture/org-specific name in this source (LANE-03) — the loader generalizes over an arbitrary
  lane set via generic STRUCTURAL keys only; no concrete lane/module/owner value appears here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from ._yaml_loader import load_config as _parse_config
from .adapters._timestamps import EPOCH_ZERO
from .distill.coverage import Unextracted
from .locators import FreeLocator
from .semantic import Claim, KpiItem, Source, Trace

__all__ = ["SectionBinding", "SwimlaneLoad", "load_swimlanes"]


# --------------------------------------------------------------------------- #
# Routing reason codes + preview length (mirror normalize.py:42-47 +
# test_excel_golden's R_* convention). Named module-level constants so the Plan
# 01-03 coverage test asserts them WITHOUT inline-string drift.
# --------------------------------------------------------------------------- #

# How many characters of a non-locatable scalar to keep as the content-anchor preview. A content
# preview (never an ordinal index) is what locators.py:17-19 requires; mirrors normalize.py:45.
_PREVIEW_CHARS = 60

# The scalar's raw token is simply not a verbatim substring of the raw config text from the
# forward-only cursor onward (and none of the more specific cases below apply).
_R_NOT_VERBATIM = (
    "scalar not verbatim-locatable in raw config text (faithful, not suggestive)"
)

# YAML coerced the scalar to a non-string Python type whose ``str()`` form is not the raw token
# (e.g. ``yes`` -> True, ``007`` -> 7, ``1,024`` -> a number) so it cannot content-address verbatim.
_R_TYPE_COERCED = "scalar type-coerced by YAML (e.g. yes->True, 007->7); raw token not verbatim in config text"

# A block scalar (``|`` / ``>``): the folded/chomped LOGICAL value is not a verbatim substring of
# the raw text, so span-containment cannot hold — disclosed, never fabricated.
_R_BLOCK_SCALAR = "block scalar (| or >): folded/chomped logical value is not a verbatim substring of raw text"

# The value occurs in the text ONLY earlier than the forward-only cursor (a duplicate whose
# occurrences are exhausted, or an alias whose characters live at the anchor site) — there is no
# DISTINCT forward span to address, so pointing at the earlier one would be provenance fiction.
_R_ANCHOR_ALIAS = (
    "value occurs only earlier than the forward cursor (duplicate exhausted / anchor-alias); "
    "no distinct forward span to address"
)


# --------------------------------------------------------------------------- #
# Generic STRUCTURAL schema keys (NOT fixture-specific values — LANE-03). These
# name the shape the loader generalizes over; the concrete lane/module/owner
# VALUES live only in the config file, never here.
# --------------------------------------------------------------------------- #

_LANES_KEY = "lanes"
_HEADING_KEY = "heading"
_KPIS_KEY = "kpis"
_LABEL_KEY = "label"
_VALUE_KEY = "value"
_VALUES_KEY = "values"


# --------------------------------------------------------------------------- #
# SectionBinding — the kind-agnostic per-lane seam Phase 2's composer consumes.
# A small, AI-free Pydantic model reusing the EXISTING KpiItem/Claim (no new
# block type; models.py untouched). Bound at the parsed-DICT level.
# --------------------------------------------------------------------------- #


class SectionBinding(BaseModel):
    """One configured lane, bound to its traced content at the parsed-dict level (LANE-01).

    ``heading`` is the lane's display heading (its own traced scalar). ``kpi_items`` are the
    display KPIs (label + value; ``delta``/``dir`` left ``None`` — Phase 2 computes Δ). ``claims``
    are the content-addressed atoms for EVERY scalar this lane read (including the ones backing the
    kpi values and heading), so the read-anchored coverage identity is assertable per lane.
    ``missing`` carries human-facing honesty-panel strings for declared-but-absent slots;
    ``unextracted`` is the typed coverage carrier for scalars that were read but not
    verbatim-locatable (each with a reason code).
    """

    heading: str
    kpi_items: list[KpiItem] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    unextracted: list[Unextracted] = Field(default_factory=list)


class SwimlaneLoad(BaseModel):
    """The result of loading one module-config file: the ``Source`` + one binding per lane.

    ``claims`` / ``unextracted`` carry MODULE-LEVEL scalars — those outside any lane (e.g. the
    module id, an area id) — so the read-anchored coverage identity spans the WHOLE load, not just
    the lanes. ``scalars_walked`` is the count of non-null scalar leaves the loader read; by
    construction ``len(all_claims) + len(all_unextracted) == scalars_walked`` (enforced in
    :func:`load_swimlanes`, which raises on any drift).
    """

    source: Source
    bindings: list[SectionBinding] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    unextracted: list[Unextracted] = Field(default_factory=list)
    scalars_walked: int = 0

    @property
    def all_claims(self) -> list[Claim]:
        """Every content-addressed claim minted across the load (module-level + all lanes)."""
        out = list(self.claims)
        for binding in self.bindings:
            out.extend(binding.claims)
        return out

    @property
    def all_unextracted(self) -> list[Unextracted]:
        """Every disclosed unextracted scalar across the load (module-level + all lanes)."""
        out = list(self.unextracted)
        for binding in self.bindings:
            out.extend(binding.unextracted)
        return out


# --------------------------------------------------------------------------- #
# The forward-only cursor mint (mirrors adapters/normalize.py:88-117). ONE
# cursor over the RAW config text for the WHOLE document, so duplicate values get
# DISTINCT, forward-only offsets and consumed text is never re-pointed at.
# --------------------------------------------------------------------------- #


class _Minter:
    """Locate each scalar VERBATIM in the raw config text and mint it (or route it honestly).

    A single ``str.find`` from a monotonically-advancing cursor over ``source.transcript`` (the RAW
    file text — NEVER a re-serialized dump, Pitfall 3). On a hit the scalar is minted via
    ``Trace.from_source`` — the SOLE trace-minting path (never a hand-minted hash, never a
    fabricated offset). On a miss the scalar is routed to an ``Unextracted`` with a content preview
    and the most specific ``_R_*`` reason. WHY the cursor: two identical scalars would both resolve
    to the FIRST occurrence without it, mis-attributing the second's provenance (normalize.py:17-20).
    """

    def __init__(self, source: Source) -> None:
        self._source = source
        self._transcript = source.transcript
        self._cursor = 0
        self.walked = 0

    def mint(self, value: object) -> Claim | Unextracted:
        """Route ONE scalar leaf: a content-addressed ``Claim`` on a verbatim hit, else honest gap.

        Increments ``walked`` for every scalar READ (read-anchored coverage, Pitfall 9). The raw
        candidate token is the value itself for a string, else ``str(value)`` — we search for the
        token as written and, if the coerced form is not verbatim, disclose it rather than fabricate.
        """
        self.walked += 1
        token = value if isinstance(value, str) else str(value)
        idx = self._transcript.find(token, self._cursor)
        if idx == -1:
            return Unextracted(
                locator=FreeLocator(text=token[:_PREVIEW_CHARS]),
                reason=self._classify(value, token),
            )
        end = idx + len(token)
        # Trace.from_source validates 0 <= start <= end <= len before slicing (raises on a bad
        # range), pins content_hash, and stores span == transcript[idx:end]. is_addressed is True.
        trace = Trace.from_source(self._source, idx, end)
        self._cursor = end  # advance -> duplicates get distinct, forward-only offsets
        return Claim(text=token, evidence=[trace], confidence=0.0)

    def _classify(self, value: object, token: str) -> str:
        """Pick the most specific routing reason for a non-locatable scalar (cheap type checks)."""
        if not isinstance(value, str):
            return _R_TYPE_COERCED
        if "\n" in token:
            return _R_BLOCK_SCALAR
        # It exists in the text, but only BEFORE the forward cursor (duplicate exhausted / an alias
        # whose characters live at an earlier anchor site) — no distinct forward span to address.
        if self._transcript.find(token) != -1:
            return _R_ANCHOR_ALIAS
        return _R_NOT_VERBATIM


def _route(
    minted: Claim | Unextracted, claims: list[Claim], unextracted: list[Unextracted]
) -> None:
    """Append a minted scalar to the correct sink (claim vs disclosed gap)."""
    if isinstance(minted, Claim):
        claims.append(minted)
    else:
        unextracted.append(minted)


def _walk_generic(
    node: object,
    minter: _Minter,
    claims: list[Claim],
    unextracted: list[Unextracted],
) -> None:
    """Recursively mint EVERY non-null scalar leaf under ``node`` in file order (zero silent drops).

    The STRUCTURE vs CONTENT split (Pitfall 9): mapping KEYS (``lanes:``, ``kpis:``) are structure
    and are never minted; mapping VALUES and list items are recursed; a terminal (non-container,
    non-None) node is a scalar leaf and is routed via the minter. A ``None`` leaf is a
    declared-but-absent slot — nothing was READ, so it is not counted (recognized slots disclose
    their own absence via ``missing[]``; see :func:`_bind_lane`).
    """
    if isinstance(node, dict):
        for child in node.values():
            _walk_generic(child, minter, claims, unextracted)
    elif isinstance(node, list):
        for item in node:
            _walk_generic(item, minter, claims, unextracted)
    elif node is None:
        return
    else:
        _route(minter.mint(node), claims, unextracted)


def _bind_lane(lane: object, minter: _Minter) -> SectionBinding:
    """Bind one configured lane to a SectionBinding at the parsed-dict level (LANE-01).

    Task-2 scope: capture the lane ``heading`` and mint EVERY other lane scalar generically so the
    coverage identity holds. The KPI display projection (``kpi_items``) is layered in by Task 3 —
    the SAME scalars, additionally projected for display (minted once, never double-counted).
    """
    heading = ""
    claims: list[Claim] = []
    unextracted: list[Unextracted] = []
    missing: list[str] = []

    if isinstance(lane, dict):
        for key, value in lane.items():
            if key == _HEADING_KEY and isinstance(value, str):
                heading = value
                _route(minter.mint(value), claims, unextracted)
            else:
                _walk_generic(value, minter, claims, unextracted)
    else:
        # A non-mapping lane entry: mint its scalars honestly, empty heading.
        _walk_generic(lane, minter, claims, unextracted)

    return SectionBinding(
        heading=heading,
        kpi_items=[],
        claims=claims,
        missing=missing,
        unextracted=unextracted,
    )


def load_swimlanes(path: str | Path, *, root: Path | None = None) -> SwimlaneLoad:
    """Load a module-config YAML file into a ``Source`` + one ``SectionBinding`` per lane (LANE-02).

    Read-only, deterministic, AI-free. Mirrors ``worksurface.capture_files``'s edge policy: the path
    is resolved under ``root`` (default :func:`Path.cwd`) and any path escaping root raises
    ``ValueError`` (the path-traversal bound); a missing file raises ``FileNotFoundError`` and a
    non-UTF-8 file raises ``UnicodeDecodeError`` — never skipped silently, never lossy-decoded. The
    ``Source.transcript`` is the RAW file text VERBATIM (never a re-serialized dump, Pitfall 3) and
    ``Source.timestamp`` is the fixed ``EPOCH_ZERO`` sentinel (never ``now()``, Pitfall 5).

    The parsed structure (via Plan 01-01's ``safe_load`` boundary) is walked to learn WHICH scalar
    values exist and in what file order; each is located in the RAW transcript by the forward-only
    cursor and minted via ``Trace.from_source`` — or disclosed in ``unextracted[]``. The
    read-anchored coverage identity ``len(all_claims) + len(all_unextracted) == scalars_walked`` is
    enforced by construction (a mismatch raises — a scalar read but neither claimed nor disclosed is
    a silent drop, forbidden by Pitfall 9 / the RETRO Phase-7 lesson).

    Args:
        path: the module-config file to load (str or Path; absolute or relative to ``root``).
        root: the repo root the relpath ``Source.id`` is computed against. Defaults to ``Path.cwd()``.

    Returns:
        A :class:`SwimlaneLoad` — the ``Source``, the per-lane ``SectionBinding[]`` in file order,
        the module-level claims/unextracted, and the ``scalars_walked`` count.

    Raises:
        ValueError: if ``path`` resolves OUTSIDE ``root`` (path-traversal bound).
        FileNotFoundError: if ``path`` does not exist.
        UnicodeDecodeError: if the file is not valid UTF-8.
        RuntimeError: if the read-anchored coverage identity is violated (a silent drop).
    """
    root_path = (root or Path.cwd()).resolve()
    candidate = Path(path)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(
        root_path
    ).as_posix()  # raises ValueError if it escapes root
    transcript = resolved.read_text(
        encoding="utf-8"
    )  # READ ONLY — no write, no network

    source = Source(
        id=rel,
        context=f"module-config:{rel}",
        transcript=transcript,
        timestamp=EPOCH_ZERO,
    )

    # Parse ONLY to learn which scalars exist and in what file order; locate them in the RAW text.
    parsed = _parse_config(transcript)

    minter = _Minter(source)
    module_claims: list[Claim] = []
    module_unextracted: list[Unextracted] = []
    bindings: list[SectionBinding] = []

    if isinstance(parsed, dict):
        for key, value in parsed.items():
            if key == _LANES_KEY and isinstance(value, list):
                # Iterate the lane list DIRECTLY in file order (never a set / non-total sort,
                # Pitfall 6) so lane order is deterministic and matches the config.
                for lane in value:
                    bindings.append(_bind_lane(lane, minter))
            else:
                _walk_generic(value, minter, module_claims, module_unextracted)
    elif parsed is not None:
        # A non-mapping top-level document: mint its scalars honestly at module level.
        _walk_generic(parsed, minter, module_claims, module_unextracted)

    load = SwimlaneLoad(
        source=source,
        bindings=bindings,
        claims=module_claims,
        unextracted=module_unextracted,
        scalars_walked=minter.walked,
    )

    # Read-anchored coverage identity, enforced BY CONSTRUCTION (Pitfall 9 / RETRO Phase-7): every
    # scalar READ is either a content-addressed claim or a disclosed gap — zero silent drops.
    minted = len(load.all_claims) + len(load.all_unextracted)
    if minted != minter.walked:
        raise RuntimeError(
            f"swimlane read-anchored coverage identity violated: {minted} "
            f"(claims+unextracted) != {minter.walked} scalars walked — a scalar was read but "
            "neither claimed nor disclosed (silent drop, forbidden)."
        )
    return load
