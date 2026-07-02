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

__all__ = ["SectionBinding"]


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
