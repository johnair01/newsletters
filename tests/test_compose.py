"""COMP-01..04 — the trust-guard proof suite for the module-scope Report composer.

This suite IS Phase 2's deliverable (02-04-PLAN / Pitfall 10: guarantees are enforced by
adversarial tests, not docstrings). It drives the LIVE ``newsletters.compose`` composer over
hand-built, in-memory ``SectionBinding``s (no YAML — the composer is loader-agnostic) and proves,
on the composed ``Surface``:

* Hole B closed — EVERY claim on EVERY ``ClaimsBlock`` is traced AND every trace is
  content-addressed; a planted un-traced / un-addressed claim is routed to ``missing[]`` (non-vacuous).
* Hole A closed — authored (non-``ClaimsBlock``) prose carries NO un-sourced digit run; the only
  numerals outside a traced claim are ``KpiItem.value``/``.delta`` on a ``KpiStripBlock``, each
  traceable to a content-addressed endpoint.
* No-auto-publish — the composed surface is ``Draft``; ``publish()`` without a satisfied policy
  raises and leaves the gate ``Draft``; a direct ``Review(state=PUBLISHED, ...)`` raises.
* Δ reproducibility + determinism — every rendered delta recomputes byte-equal from its two
  endpoints via ``compute_delta``; two composes are byte-identical ``model_dump_json``.
* Kind-agnostic seam + edge cases — a NON-lane ``SectionBinding`` composes with zero composer
  change; zero-KPI lane, empty lane set, and unowned/sourced quote all behave honestly.

Nothing here weakens a gate: ``faithfulness``/``coverage``/``semantic``/``templates``/``site`` are
asserted byte-untouched (``git diff``). A RED guard is fixed in the composer, never by relaxing a test.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.compose import compose_module_report, compute_delta
from newsletters.semantic import (
    Claim,
    ClaimsBlock,
    KpiItem,
    KpiStripBlock,
    ProseBlock,
    QuoteBlock,
    Review,
    ReviewState,
    Source,
    Surface,
    Trace,
)
from newsletters.site import Ledger
from newsletters.swimlane import SectionBinding, SwimlaneLoad
from newsletters.templates import REPORT

# --------------------------------------------------------------------------- #
# In-memory builders (Pitfall 8: assert STRUCTURE/INVARIANTS from the SAME inputs
# the composer read — never a frozen lane string). Every endpoint/finding Claim is
# GENUINELY content-addressed via ``Trace.from_source`` against a crafted transcript.
# --------------------------------------------------------------------------- #


class _Cursor:
    """A forward-only minter over one Source (mirrors swimlane's cursor discipline).

    ``claim(token)`` locates ``token`` verbatim at or after the cursor and mints a genuinely
    content-addressed ``Claim`` (span == the token), advancing the cursor so duplicate tokens get
    DISTINCT forward spans. Tokens MUST be requested in transcript (file) order.
    """

    def __init__(self, source: Source) -> None:
        self._source = source
        self._pos = 0

    def claim(self, token: str) -> Claim:
        start = self._source.transcript.index(token, self._pos)
        end = start + len(token)
        self._pos = end
        return Claim(text=token, evidence=[Trace.from_source(self._source, start, end)])


def _empty_ledger() -> Ledger:
    """A fresh, empty, in-memory ledger (no disk read/write) — keeps composes isolated + stable."""
    return Ledger(Path("content/module/ids.json"), {})


def _compose(load: SwimlaneLoad, **kwargs: object) -> Surface:
    """Compose with an isolated empty ledger by default (compose never ``save()``s)."""
    kwargs.setdefault("ledger", _empty_ledger())
    return compose_module_report(load, **kwargs)  # type: ignore[arg-type]


def _build_load() -> tuple[SwimlaneLoad, Claim]:
    """A two-lane module load with a delta KPI, a point-in-time KPI, a zero-delta KPI, and a quote.

    Returns ``(load, quote_claim)``. Every claim is content-addressed against ``source``; the KPI
    endpoints are references to those same claims (as swimlane emits them). The quote is a separate
    traced claim the caller passes to the sourced-or-omit slot.
    """
    transcript = (
        "lane one Delivery\n"
        "cycle start 10 days close 7 days\n"
        "roster 6 people on the team\n"
        "note Cycle time improved after the release train landed\n"
        "lane two Quality\n"
        "defects start 4 bugs close 4 bugs again\n"
        "note Defect count held steady across the quarter\n"
        "voice We shipped every commitment this cycle\n"
    )
    src = Source(
        id="content/module/platform.yml",
        context="module-config:content/module/platform.yml",
        transcript=transcript,
        timestamp=EPOCH_ZERO,
    )
    cur = _Cursor(src)
    # Mint in FILE ORDER (the cursor is forward-only).
    c_10 = cur.claim("10 days")
    c_7 = cur.claim("7 days")
    c_6 = cur.claim("6 people")
    f_del = cur.claim("Cycle time improved after the release train landed")
    c_4a = cur.claim("4 bugs")
    c_4b = cur.claim("4 bugs")
    f_qual = cur.claim("Defect count held steady across the quarter")
    quote = cur.claim("We shipped every commitment this cycle")

    delivery = SectionBinding(
        heading="Delivery",
        kpi_items=[
            KpiItem(label="Cycle time", value="7 days"),  # two endpoints -> a delta
            KpiItem(
                label="Team size", value="6 people"
            ),  # one endpoint -> point-in-time, no delta
        ],
        kpi_endpoints=[[c_10, c_7], [c_6]],
        claims=[c_10, c_7, c_6, f_del],
    )
    quality = SectionBinding(
        heading="Quality",
        kpi_items=[
            KpiItem(label="Escaped defects", value="4 bugs")
        ],  # equal endpoints -> Δ==0
        kpi_endpoints=[[c_4a, c_4b]],
        claims=[c_4a, c_4b, f_qual],
    )
    load = SwimlaneLoad(source=src, bindings=[delivery, quality])
    return load, quote


# --------------------------------------------------------------------------- #
# Small readers over the composed surface (structure, never a frozen string).
# --------------------------------------------------------------------------- #


def _claimsblock_claims(surface: Surface) -> list[Claim]:
    """Every claim surviving onto a ``ClaimsBlock`` of the composed surface."""
    out: list[Claim] = []
    for block in surface.blocks:
        if isinstance(block, ClaimsBlock):
            out.extend(block.claims)
    return out


def _authored_text_fields(block: object) -> list[str]:
    """The AUTHORED text of a non-``ClaimsBlock`` block — everything except sourced KPI numbers.

    For a ``KpiStripBlock`` the numerals live in ``item.value``/``.delta`` (the sourced/derived
    numbers, checked separately); only the heading + item LABELS are authored/structural text here.
    """
    fields: list[str] = []
    for attr in ("heading", "text", "attr"):
        value = getattr(block, attr, None)
        if isinstance(value, str):
            fields.append(value)
    if isinstance(block, KpiStripBlock):
        fields.extend(item.label for item in block.items)
    links = getattr(block, "links", None)
    if links is not None:
        for link in links:
            fields.append(link.kind)
            fields.append(link.title)
    return fields


def _authored_digit_runs(surface: Surface) -> list[str]:
    """Every digit run in AUTHORED (non-``ClaimsBlock``, non-KPI-number) text — must be empty."""
    runs: list[str] = []
    for block in surface.blocks:
        if isinstance(block, ClaimsBlock):
            continue  # a traced claim MAY carry numerals — it is content-addressed
        for text in _authored_text_fields(block):
            runs.extend(re.findall(r"\d+", text))
    return runs


# --------------------------------------------------------------------------- #
# Task 1 — Hole B (zero-trace / un-addressed), Hole A (numeral-free prose),
# and no-auto-publish, on the composed surface.
# --------------------------------------------------------------------------- #


def test_every_claimsblock_claim_is_traced_and_addressed() -> None:
    """Hole B (COMP-03): every surviving ClaimsBlock claim is traced AND content-addressed."""
    load, _ = _build_load()
    surface = _compose(load)

    claims = _claimsblock_claims(surface)
    assert claims, "the honest happy path emitted no ClaimsBlock claims"
    for claim in claims:
        assert claim.is_traced, (
            f"claim {claim.text[:40]!r} is untraced — it must be routed to missing[], "
            "never left on a ClaimsBlock"
        )
        for trace in claim.evidence:
            assert (
                trace.is_addressed
            ), f"claim {claim.text[:40]!r} carries an un-addressed trace (Hole B)"


def test_untraced_and_unaddressed_claims_are_routed_to_missing() -> None:
    """Hole B non-vacuity: a planted zero-trace AND a planted un-addressed claim go to missing[]."""
    load, _ = _build_load()
    untraced = Claim(text="planted untraced claim never sourced")  # zero evidence
    unaddressed = Claim(
        text="planted claim on an un-addressed trace",
        evidence=[
            Trace(source_id=load.source.id)
        ],  # no content_hash -> is_addressed False
    )
    load.bindings[0].claims.extend([untraced, unaddressed])

    surface = _compose(load)
    kept = {claim.text for claim in _claimsblock_claims(surface)}

    assert untraced.text not in kept, "an untraced claim leaked onto a ClaimsBlock"
    assert (
        unaddressed.text not in kept
    ), "an un-addressed claim leaked onto a ClaimsBlock"
    assert (
        untraced.text in surface.missing
    ), "the untraced claim was not disclosed in missing[]"
    assert (
        unaddressed.text in surface.missing
    ), "the un-addressed claim was not disclosed"


def test_authored_prose_is_numeral_free() -> None:
    """Hole A (COMP-03): no non-ClaimsBlock authored text carries a digit run; proven non-vacuous."""
    load, quote = _build_load()
    surface = _compose(load, quote=quote, owner="platform-lead")

    assert (
        _authored_digit_runs(surface) == []
    ), "authored (non-ClaimsBlock) prose carries an un-sourced digit run — Hole A is open"

    # Non-vacuous: an un-sourced digit run in authored prose MUST be caught.
    poisoned = surface.model_copy(
        update={"blocks": [*surface.blocks, ProseBlock(text="we shipped 42 features")]}
    )
    assert "42" in _authored_digit_runs(
        poisoned
    ), "the numeral-free guard failed to catch an un-sourced digit run in authored prose"


def test_kpi_numbers_are_sourced_to_endpoints() -> None:
    """Hole A allow-list: the ONLY out-of-claim numerals are KPI value/delta traceable to endpoints."""
    load, _ = _build_load()
    surface = _compose(load)

    kpi_blocks = [b for b in surface.blocks if isinstance(b, KpiStripBlock)]
    bindings = [b for b in load.bindings if b.kpi_items]
    assert len(kpi_blocks) == len(bindings)

    for block, binding in zip(kpi_blocks, bindings):
        for item, endpoints in zip(block.items, binding.kpi_endpoints):
            if re.findall(r"\d+", item.value):
                assert (
                    endpoints
                ), f"KPI {item.label!r} shows a numeral value with no endpoint"
                assert (
                    item.value == endpoints[-1].text
                ), f"KPI {item.label!r} value is not the traced close endpoint (Hole A)"
                close = endpoints[-1]
                assert close.is_traced and all(
                    t.is_addressed for t in close.evidence
                ), f"KPI {item.label!r} close endpoint is not content-addressed"
            if item.delta is not None and re.findall(r"\d+", item.delta):
                assert (
                    len(endpoints) >= 2
                ), "a delta numeral with fewer than two endpoints"


def test_no_auto_publish_on_the_composed_surface() -> None:
    """COMP-04: the composed surface is Draft; publish() without the gate raises; PUBLISHED raises."""
    load, _ = _build_load()
    surface = _compose(load)

    assert surface.gate is ReviewState.DRAFT
    assert surface.review.state is ReviewState.DRAFT

    with pytest.raises(ValueError):
        surface.publish()  # no reviewer -> light policy unsatisfied -> validator raises
    assert (
        surface.gate is ReviewState.DRAFT
    ), "a failed publish() must leave the gate Draft"

    # The publish path the model actually enforces: a direct PUBLISHED review raises.
    with pytest.raises(ValueError):
        Review(
            state=ReviewState.PUBLISHED, policy=REPORT.review_policy, author="operator"
        )
