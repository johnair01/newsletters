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

import subprocess
import sys

from newsletters.review import Blocker, BlockerKind, review_blockers
from newsletters.semantic import (
    Claim,
    ClaimsBlock,
    ReviewState,
    Source,
    Surface,
    Trace,
)
from newsletters.templates import REPORT

AI_MODULES = ("langchain", "langgraph", "langsmith", "pydantic_ai", "openai", "anthropic")


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


# --------------------------------------------------------------------------- #
# Task 3 — prove the gate FIRES (L7): three crafted PUBLISHED negatives,
#          draft/in-review exemption, a clean published surface, the no-AI guard.
# --------------------------------------------------------------------------- #
#
# Every fixture is built INLINE (we do NOT add a blocker to the shipped dogfood corpus — that would
# correctly fail the CI gate). REPORT uses ReviewPolicy.light() (min_approvals=1, require_peer=False),
# so a single approval publishes.


def _published_surface_with_claim(claim: Claim, sources: list[Source]) -> Surface:
    """A PUBLISHED Report surface carrying one ClaimsBlock + its source traces."""
    surface = Surface(
        id="sfc-pub",
        template=REPORT,
        title="Q3 Investigation",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=sources,
    )
    surface.publish(reviewer="reviewer-a")
    assert surface.is_published
    return surface


def test_blocks_stale_published_claim() -> None:
    """A published claim whose addressed trace has DRIFTED -> exactly one STALE Blocker.

    Mint a content-addressed, entailing trace, publish, THEN mutate the source transcript so the live
    hash drifts past the pinned hash -> ``claim.is_stale`` is True -> a STALE blocker fires.
    """
    transcript = "we shipped the mobile app this quarter"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # addressed + entailing at publish time
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = _published_surface_with_claim(claim, [src])

    # Drift the live source so the recorded content_hash no longer matches.
    src.transcript = transcript + " and more drift"

    blockers = review_blockers(surface, {src.id: src})
    assert blockers == [
        Blocker(
            surface_id="sfc-pub",
            kind=BlockerKind.STALE,
            detail="we shipped the mobile app",
            locator="s1",
        )
    ]


def test_blocks_unentailed_published_claim() -> None:
    """A published addressed claim whose span omits the claim text -> exactly one UNENTAILED Blocker.

    Mirrors test_faithfulness_gate.py:68 — an addressed trace over a transcript that does NOT contain
    the claim text. Not stale (the hash matches), so STALE is skipped and the elif fires UNENTAILED.
    """
    transcript = "we discussed the roadmap and the budget"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # addressed, but span omits the claim text
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = _published_surface_with_claim(claim, [src])

    blockers = review_blockers(surface, {src.id: src})
    assert len(blockers) == 1
    assert blockers[0].kind is BlockerKind.UNENTAILED
    assert blockers[0].surface_id == "sfc-pub"
    assert blockers[0].detail == "we shipped the mobile app"


def test_blocks_open_missing_published_surface() -> None:
    """A published surface with a non-empty ``missing[]`` -> one OPEN_MISSING Blocker per entry."""
    transcript = "we shipped the mobile app this quarter"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # clean, entailing claim
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = Surface(
        id="sfc-pub",
        template=REPORT,
        title="Q3 Investigation",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
        missing=["unsubstantiated: we doubled revenue", "unsubstantiated: churn fell"],
    )
    surface.publish(reviewer="reviewer-a")

    blockers = review_blockers(surface, {src.id: src})
    assert [b.kind for b in blockers] == [BlockerKind.OPEN_MISSING, BlockerKind.OPEN_MISSING]
    assert {b.detail for b in blockers} == {
        "unsubstantiated: we doubled revenue",
        "unsubstantiated: churn fell",
    }


def test_draft_surface_is_exempt() -> None:
    """A DRAFT surface with the same defects (un-entailed claim + open missing) -> [] (L3)."""
    transcript = "we discussed the roadmap and the budget"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # un-entailed span
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = Surface(
        id="sfc-draft",
        template=REPORT,
        title="Q3 Investigation",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
        missing=["unsubstantiated: we doubled revenue"],
    )
    assert surface.review.state is ReviewState.DRAFT
    assert review_blockers(surface, {src.id: src}) == []


def test_in_review_surface_is_exempt() -> None:
    """An IN-REVIEW surface with the same defects -> [] (publication is the trust boundary, L3)."""
    transcript = "we discussed the roadmap and the budget"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # un-entailed span
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = Surface(
        id="sfc-inreview",
        template=REPORT,
        title="Q3 Investigation",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
        missing=["unsubstantiated: we doubled revenue"],
    )
    surface.open_pull_request()
    assert surface.review.state is ReviewState.IN_REVIEW
    assert review_blockers(surface, {src.id: src}) == []


def test_clean_published_surface_has_no_blockers() -> None:
    """A published surface: addressed, entailed, non-stale claim + empty missing[] -> []."""
    transcript = "we shipped the mobile app this quarter"
    src = Source(id="s1", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = _published_surface_with_claim(claim, [src])

    assert review_blockers(surface, {src.id: src}) == []


def test_review_module_imports_no_ai() -> None:
    """A fresh subprocess importing ``newsletters.review`` loads no AI module (AI-optional core).

    Copies the test_faithfulness_gate.py:134-143 pattern, swapping in the review module + AI tuple.
    """
    code = (
        "import sys, newsletters.review; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('clean')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"AI leaked: {proc.stdout}{proc.stderr}"
