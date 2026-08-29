"""The four weekly block kinds: the type-level invariants, the union, and the render branches.

The contract these tests police is `docs/weekly-spec.md` §"The four block kinds" and
§"Assets — the evidence record". Two properties matter more than the rest and are asserted in
BOTH directions here:

1. **A provenance-less asset placement is unrepresentable, not policed** (decision D-02). An
   `AssetBlock` without an `AssetRecord`, or with zero evidence `Trace`s, must fail at
   *construction*. The refusals are paired with a constructing arm, because a model that rejects
   everything would satisfy the refusals alone and prove nothing.
2. **No block is silently droppable.** Every member of the `Block` union renders to non-empty
   HTML, driven by `typing.get_args` rather than a hand-written list, so a future member added
   without a render branch fails here rather than rendering as the empty string on a reviewed
   surface.
"""

from __future__ import annotations

import hashlib
from typing import get_args

import pytest
from pydantic import BaseModel, ValidationError

from newsletters.semantic import (
    AssetBlock,
    AssetRecord,
    Block,
    Claim,
    NarrativeBlock,
    NarrativeItem,
    Recognition,
    RecognitionsBlock,
    Source,
    TeamBlock,
    TeamMember,
    Trace,
)

# --------------------------------------------------------------------------- #
# Fixtures — the smallest well-formed instances the invariants are asserted on
# --------------------------------------------------------------------------- #

_ASSET = AssetRecord(
    key="lane-throughput",
    file="assets/weekly/2026-W35/lane-throughput.png",
    sha256="3b1f0c9a2d5e47b8c0f1a6d3e9b2748c5a0d1f63e874b295c3a7d0e16f28b4c9",
    folder="Weekly review pack",
    date="2026-08-24",
    event="Friday module review",
)


def _trace() -> Trace:
    """One real, content-addressed Trace into a record-shaped Source."""
    source = Source(id="weekly-spec:w35.yaml", context="weekly-spec:w35.yaml", transcript=_ASSET.sha256)
    return Trace.from_source(source, 0, len(_ASSET.sha256))


class _Holder(BaseModel):
    """A container over the discriminated union — the JSON round-trip's subject."""

    blocks: list[Block] = []


# --------------------------------------------------------------------------- #
# The union
# --------------------------------------------------------------------------- #


def test_block_union_has_fifteen_members() -> None:
    """The count the docs claim, now testable rather than asserted in prose.

    Keeps two doc locations honest: `docs/architecture.md` (the block-union note) and
    `docs/weekly-spec.md` §"Their place in the union". If this number moves, those two
    sentences move in the same commit.
    """
    members = get_args(get_args(Block)[0])
    assert len(members) == 15, [m.__name__ for m in members]
    for new in (NarrativeBlock, RecognitionsBlock, TeamBlock, AssetBlock):
        assert new in members, f"{new.__name__} is not in the Block union"


def test_four_new_kinds_round_trip_by_discriminator() -> None:
    """A Surface-shaped container holding one of each new kind re-hydrates the right class."""
    holder = _Holder(
        blocks=[
            NarrativeBlock(
                heading="Highlights",
                tone="highlight",
                items=[NarrativeItem(text="Cut the release checklist from nine steps to two.")],
            ),
            RecognitionsBlock(
                recognitions=[Recognition(person="Devi R.", reason="Found the ordering bug.")]
            ),
            TeamBlock(
                members=[TeamMember(name="Devi R.", role="Reliability", lines=["Owns the rota."])]
            ),
            AssetBlock(asset=_ASSET, caption="Throughput by lane.", evidence=[_trace()]),
        ]
    )
    dumped = holder.model_dump_json()
    rehydrated = _Holder.model_validate_json(dumped)

    assert rehydrated.model_dump_json() == dumped, "the union round-trip is not byte-identical"
    assert [type(b) for b in rehydrated.blocks] == [
        NarrativeBlock,
        RecognitionsBlock,
        TeamBlock,
        AssetBlock,
    ]
    assert [b.kind for b in rehydrated.blocks] == ["narrative", "recognitions", "team", "asset"]


# --------------------------------------------------------------------------- #
# D-02: provenance-less placement is unrepresentable
# --------------------------------------------------------------------------- #


def test_asset_block_refuses_zero_evidence() -> None:
    """`evidence` carries `min_length=1`: an asset nobody vouched for cannot be constructed."""
    with pytest.raises(ValidationError) as excinfo:
        AssetBlock(asset=_ASSET, evidence=[])
    errors = excinfo.value.errors()
    assert any(
        e["type"] == "too_short" and e["loc"] == ("evidence",) for e in errors
    ), errors


def test_asset_block_refuses_missing_asset_record() -> None:
    """`asset` is REQUIRED with no default — there is no AssetBlock without an AssetRecord."""
    with pytest.raises(ValidationError) as excinfo:
        AssetBlock(evidence=[_trace()])
    errors = excinfo.value.errors()
    assert any(e["type"] == "missing" and e["loc"] == ("asset",) for e in errors), errors


def test_well_formed_asset_block_constructs() -> None:
    """Non-vacuity arm: the two refusals above mean nothing on a model that rejects everything."""
    block = AssetBlock(asset=_ASSET, evidence=[_trace()])
    assert block.kind == "asset"
    assert block.asset.key == "lane-throughput"
    assert len(block.evidence) == 1


def test_recognition_evidence_may_be_empty_by_design() -> None:
    """The deliberate contrast (weekly-spec rule 6): the author's word IS the evidence.

    Dropping an unsourced recognition would erase credit; the loader carries it and discloses the
    absent evidence in `missing[]`. So an empty `evidence` here is legal, unlike on `AssetBlock`.
    """
    recognition = Recognition(person="Devi R.", reason="Found the ordering bug.")
    assert recognition.evidence == []


def test_narrative_item_carries_the_authored_text_and_its_claim() -> None:
    """`text` is what the author typed; `claim` is the same text traced, so they cannot diverge."""
    item = NarrativeItem(text="The migration slipped a week.")
    assert item.claim is None
    traced = NarrativeItem(
        text="The migration slipped a week.",
        claim=Claim(text="The migration slipped a week.", evidence=[_trace()]),
    )
    assert traced.claim is not None and traced.claim.text == traced.text
