"""The deterministic, AI-free merge-block checker (PROV-04) — one trust rule, one place.

This module is the single function the CLI (``newsletters check``, Plan 10-02) and CI both call to
decide whether a PUBLISHED surface is safe to merge. It is a TOP-LEVEL sibling of ``render.py`` (NOT
inside ``distill/``, which stays modality-agnostic — per L2).

``review_blockers(surface, sources) -> list[Blocker]`` flags, for a PUBLISHED surface only
(Draft / In-Review are exempt — publication is the trust boundary, L3):

* **STALE** — a claim whose trace has drifted from its live source (``Claim.is_stale``).
* **UNENTAILED** — an addressed claim whose span does NOT contain the claim text
  (``SpanContainmentFaithfulness.entails`` is False).
* **OPEN_MISSING** — a published surface carrying a non-empty ``Surface.missing[]``.

It REUSES the existing predicates — it derives NO new trust logic (the anti-pattern flagged in
research). STALE is checked first and ``elif``-guards UNENTAILED, so a drifted addressed claim
reports the truer STALE diagnosis, never double-reported.

HARD RULE — AI-optional core: this module imports only ``.semantic`` and ``.distill.faithfulness``
(both AI-free) plus stdlib + Pydantic. No AI module is reachable from here, keeping the bare-install
runtime and ``lint-imports`` green (PKG-03 / PKG-04). It is a PURE function — it never mutates the
surface and never routes to ``missing[]`` (that is ``route_unfaithful_to_missing``'s job at the
distill boundary).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from .distill.faithfulness import SpanContainmentFaithfulness
from .semantic import Claim, ClaimsBlock, Source, Surface


class BlockerKind(StrEnum):
    """The three reasons a published surface is unsafe to merge (PROV-04)."""

    STALE = "stale"
    UNENTAILED = "unentailed"
    OPEN_MISSING = "open_missing"


class Blocker(BaseModel):
    """One typed reason a published surface is blocked from merge.

    Mirrors the ``Unextracted`` / ``Claim`` style: a small, serializable record. ``detail`` is a
    short human-facing description (truncated claim text, or the verbatim missing entry); ``locator``
    optionally pins the offending trace's source id.
    """

    surface_id: str
    kind: BlockerKind
    detail: str
    locator: str = ""


def review_blockers(
    surface: Surface,
    sources: dict[str, Source] | None = None,
) -> list[Blocker]:
    """Return every merge-blocker for ``surface`` — STALE / UNENTAILED / OPEN_MISSING (L2, L3).

    Published-only scope (L3): a Draft or In-Review surface is not yet at the trust boundary, so this
    returns ``[]`` immediately for it. For a PUBLISHED surface it checks every claim in every
    ``ClaimsBlock`` and every ``missing[]`` entry, reusing the existing predicates:

    * ``Claim.is_stale(sources)`` -> a ``STALE`` blocker (checked FIRST);
    * ``elif not SpanContainmentFaithfulness().entails(claim)`` -> an ``UNENTAILED`` blocker
      (so a drifted addressed claim reports the truer STALE diagnosis, never both);
    * each entry in ``surface.missing`` -> an ``OPEN_MISSING`` blocker.

    ``sources`` is a ``{source_id: Source}`` lookup. When ``None`` it is self-built from
    ``surface.traces`` (mirroring ``Distillation.stale_claims``), so a self-contained surface can
    report its own drift. PURE: never mutates ``surface``, never routes to ``missing[]``.
    """
    if not surface.is_published:
        # L3 — Draft / In-Review are exempt; only the PUBLISHED state is the trust boundary.
        return []

    lookup = sources if sources is not None else {s.id: s for s in surface.traces}
    checker = SpanContainmentFaithfulness()
    blockers: list[Blocker] = []

    claims: list[Claim] = []
    for block in surface.blocks:
        if isinstance(block, ClaimsBlock):
            claims.extend(block.claims)

    for claim in claims:
        locator = claim.evidence[0].source_id if claim.evidence else ""
        if claim.is_stale(lookup):
            # STALE first — the truer diagnosis for a drifted addressed claim (elif-guards below).
            blockers.append(
                Blocker(
                    surface_id=surface.id,
                    kind=BlockerKind.STALE,
                    detail=claim.text[:80],
                    locator=locator,
                )
            )
        elif not checker.entails(claim):
            blockers.append(
                Blocker(
                    surface_id=surface.id,
                    kind=BlockerKind.UNENTAILED,
                    detail=claim.text[:80],
                    locator=locator,
                )
            )

    for entry in surface.missing:
        blockers.append(
            Blocker(
                surface_id=surface.id,
                kind=BlockerKind.OPEN_MISSING,
                detail=entry,
            )
        )

    return blockers
