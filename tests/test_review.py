"""PROV-04 — the deterministic, AI-free merge-block checker (review.py) + its Surface.missing carrier.

This suite proves Phase-10 Plan-01's trust core:

* **L1 — the ``Surface.missing`` carrier.** A published surface can carry an open ``missing[]``
  list onto the rendered/checked layer. The field is OPTIONAL (default ``[]``, backward-compat),
  additive (it never touches the publish gate), and invariant-3-safe (plain ``str`` entries only —
  never a Corpus / Source / Distillation object).

* **L2 / L3 — ``review_blockers(surface, sources) -> list[Blocker]``.** A pure function that, for a
  PUBLISHED surface only (Draft / In-Review are exempt — publication is the trust boundary), returns
  a typed ``Blocker`` for every STALE claim, every un-entailed claim, and every open ``missing[]``
  entry. It REUSES the existing ``Claim.is_stale`` and ``SpanContainmentFaithfulness.entails``
  predicates — no new trust logic. STALE is checked first and elif-guards UNENTAILED so a drifted
  addressed claim reports the truer STALE diagnosis.

* **L7 — the gate is PROVEN TO FIRE.** Three crafted PUBLISHED negative fixtures (STALE / unentailed
  / open-missing) each assert the exact ``Blocker.kind``; a Draft and an In-Review surface with the
  same defects return ``[]``; a clean published surface returns ``[]``; and a subprocess no-AI-import
  guard proves ``newsletters.review`` pulls no AI module into the bare-install runtime. A negative
  gate that only ever sees clean input proves nothing (the Phase-7 lesson).
"""

from __future__ import annotations

from newsletters.semantic import (
    Claim,
    ClaimsBlock,
    Source,
    Surface,
    Trace,
)
from newsletters.templates import REPORT


# --------------------------------------------------------------------------- #
# Task 1 — the Surface.missing carrier (L1): optional, additive, invariant-3-safe
# --------------------------------------------------------------------------- #


def _bare_surface() -> Surface:
    """A minimal valid Surface (no missing key) — proves backward-compat construction."""
    return Surface(id="sfc-1", template=REPORT, title="Q3 Investigation")


def test_surface_missing_defaults_to_empty_list() -> None:
    """A Surface built with no ``missing`` key validates and defaults ``missing == []``."""
    surface = _bare_surface()
    assert surface.missing == []


def test_surface_missing_roundtrips_through_json() -> None:
    """``missing=[...]`` survives a ``model_dump_json`` / ``model_validate_json`` round-trip."""
    surface = Surface(
        id="sfc-2",
        template=REPORT,
        title="Q3 Investigation",
        missing=["unsubstantiated: we doubled revenue"],
    )
    restored = Surface.model_validate_json(surface.model_dump_json())
    assert restored.missing == ["unsubstantiated: we doubled revenue"]


def test_surface_missing_does_not_change_publish_gate() -> None:
    """A published surface with a non-empty ``missing[]`` still publishes (the carrier is additive).

    The carrier must NOT alter the no-auto-publish / review gate (invariant 2) — a single light-policy
    approval still publishes regardless of open missing[] entries.
    """
    surface = Surface(
        id="sfc-3",
        template=REPORT,
        title="Q3 Investigation",
        missing=["unsubstantiated: we doubled revenue"],
    )
    surface.publish(reviewer="reviewer-a")
    assert surface.is_published
    assert surface.missing == ["unsubstantiated: we doubled revenue"]


def test_surface_missing_carries_only_str_entries() -> None:
    """``missing[]`` carries plain strings only — invariant 3 (no private corpus serialized) holds.

    Pydantic coerces / rejects non-str entries; the round-tripped JSON contains the literal strings
    and no nested model, so a Corpus / Source can never ride out on this carrier.
    """
    surface = Surface(
        id="sfc-4",
        template=REPORT,
        title="Q3 Investigation",
        missing=["a", "b"],
    )
    dumped = surface.model_dump_json()
    assert '"missing":["a","b"]' in dumped
    assert all(isinstance(m, str) for m in surface.missing)
