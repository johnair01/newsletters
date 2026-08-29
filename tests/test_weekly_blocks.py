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
import re
from typing import Literal, get_args

import pytest
from pydantic import BaseModel, ValidationError

from newsletters import render
from newsletters.render import _block_html
from newsletters.semantic import (
    AssetBlock,
    AssetRecord,
    Block,
    Chapter,
    ChaptersBlock,
    Claim,
    ClaimsBlock,
    DiagramBlock,
    FanoutBlock,
    FanoutLink,
    GlossaryBlock,
    GlossaryTerm,
    ItemsBlock,
    KpiItem,
    KpiStripBlock,
    LetterItem,
    NarrativeBlock,
    NarrativeItem,
    PromptBlock,
    ProseBlock,
    QuoteBlock,
    RationaleBlock,
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


# --------------------------------------------------------------------------- #
# The render branches — zero new CSS, no silent drops, everything escaped
# --------------------------------------------------------------------------- #

# The design-system contract, pinned by content. `_CSS` is inlined into EVERY page
# (`render._page`), so `tests/test_publish.py::test_committed_rev1_equals_fresh_build` and
# `..._work_...` compare committed corpus HTML against a fresh render of it. Changing one byte of
# `_CSS` therefore forces a full regeneration of `content/rev1/site` and `content/work` — that is a
# separate, DECLARED task with its own reviewed diff, never a side effect of adding a block kind.
# Proven by experiment in 03-RESEARCH: planting a single `.nl-scratch{color:red}` rule turned both
# committed==fresh gates red.
_CSS_SHA256 = "d9eeca3a40f1bd1d7b1920ad5bbe0ef0699560a2aa589856f83bd016a9f025b6"

# Every class name `_CSS` defines, however it is selected (`.item`, `.chapter .t`, `.sg-tag.cat`).
_CSS_CLASSES = frozenset(re.findall(r"\.([A-Za-z][\w-]*)", render._CSS))

_XSS = "<script>alert(1)</script>"


def _sample_blocks() -> dict[type, object]:
    """One constructed instance of EVERY union member, keyed by class.

    Deliberately a mapping rather than a list: the coverage test below drives its cases from
    `typing.get_args(Block)` and fails on any member missing from here, so a future block kind
    cannot be added without both a sample and a render branch.
    """
    claim = Claim(text="A traced finding.", evidence=[_trace()])
    return {
        ProseBlock: ProseBlock(heading="Lead", text="One paragraph.\n\nAnd another."),
        ClaimsBlock: ClaimsBlock(claims=[claim]),
        KpiStripBlock: KpiStripBlock(items=[KpiItem(label="Lead time", value="2d", delta="-1d", dir="down")]),
        QuoteBlock: QuoteBlock(text="In their words.", attr="platform-lead"),
        ChaptersBlock: ChaptersBlock(chapters=[Chapter(time="00:10", title="Opening", body="Body.")]),
        ItemsBlock: ItemsBlock(items=[LetterItem(tag="note", title="Title", body="Body.")]),
        PromptBlock: PromptBlock(label="shell", body="newsletters assemble"),
        FanoutBlock: FanoutBlock(links=[FanoutLink(kind="report", title="The report", href="r.html")]),
        RationaleBlock: RationaleBlock(text="Why you are seeing this."),
        DiagramBlock: DiagramBlock(title="Flow", svg="<svg></svg>", caption="A caption."),
        GlossaryBlock: GlossaryBlock(terms=[GlossaryTerm(term="Trace", definition=claim)]),
        NarrativeBlock: NarrativeBlock(
            heading="Highlights",
            tone="highlight",
            items=[NarrativeItem(text="Cut the release checklist from nine steps to two.")],
        ),
        RecognitionsBlock: RecognitionsBlock(
            recognitions=[Recognition(person="Devi R.", reason="Found the ordering bug.")]
        ),
        TeamBlock: TeamBlock(
            members=[TeamMember(name="Devi R.", role="Reliability", lines=["Owns the rota."])]
        ),
        AssetBlock: AssetBlock(
            heading="Throughput", asset=_ASSET, caption="Throughput by lane.", evidence=[_trace()]
        ),
    }


def test_css_is_byte_frozen() -> None:
    """Zero new CSS this phase — the four branches reuse classes that already exist."""
    digest = hashlib.sha256(render._CSS.encode("utf-8")).hexdigest()
    assert digest == _CSS_SHA256, (
        "render._CSS changed. Every page inlines it, so the committed corpora "
        "(content/rev1/site, content/work) no longer equal a fresh render. Regenerating them is a "
        "separate declared task with its own reviewed diff — never a side effect of another change."
    )


def test_every_union_member_has_a_render_branch() -> None:
    """No block is silently droppable: every union member renders to non-empty HTML.

    Driven by `get_args`, not a hand-written list, so a member added to the union without a
    `_block_html` branch fails HERE rather than rendering as the empty string on a reviewed
    surface — the precise failure `docs/weekly-spec.md` §"The dispatch contract" describes.
    """
    members = get_args(get_args(Block)[0])
    samples = _sample_blocks()
    unsampled = [m.__name__ for m in members if m not in samples]
    assert not unsampled, f"union members with no sample instance in this test: {unsampled}"

    for member in members:
        html = _block_html(samples[member])
        assert html.strip(), f"{member.__name__} rendered to an empty string — it would vanish"


def test_new_branches_use_only_existing_design_system_classes() -> None:
    """The four new branches introduce no class `_CSS` does not already define (zero new CSS)."""
    samples = _sample_blocks()
    for member in (NarrativeBlock, RecognitionsBlock, TeamBlock, AssetBlock):
        html = _block_html(samples[member])
        used = {
            token
            for attr in re.findall(r'class="([^"]*)"', html)
            for token in attr.split()
        }
        assert used, f"{member.__name__} rendered no class at all"
        unknown = sorted(used - _CSS_CLASSES)
        assert not unknown, f"{member.__name__} uses class(es) absent from render._CSS: {unknown}"


def test_team_block_mirrors_the_chapters_wrapper_structure() -> None:
    """`.chapter` is a `64px 1fr` GRID, so a flat structure lands the name in the wrong cell.

    The layout contract is structural, not cosmetic: `div.t` (role) is the first grid cell and a
    single wrapper `<div>` holding `.ti` (name) and `.bo` (lines) is the second — exactly what the
    `ChaptersBlock` branch emits.
    """
    html = _block_html(
        TeamBlock(members=[TeamMember(name="Devi R.", role="Reliability", lines=["Owns the rota."])])
    )
    assert (
        '<div class="chapter"><div class="t">Reliability</div>'
        '<div><div class="ti">Devi R.</div>' in html
    ), html
    assert "Owns the rota." in html


def test_authored_markup_is_escaped_in_every_new_branch() -> None:
    """T-03-14: authored strings cross into served markup — every one goes through `_e()`.

    `DiagramBlock`'s unescaped `{b.svg}` is the sole raw interpolation in this renderer and is
    explicitly NOT a precedent: `AssetBlock` emits no `<img>` and no raw markup.
    """
    blocks = [
        NarrativeBlock(heading=_XSS, items=[NarrativeItem(text=_XSS)]),
        RecognitionsBlock(heading=_XSS, recognitions=[Recognition(person=_XSS, reason=_XSS)]),
        TeamBlock(heading=_XSS, members=[TeamMember(name=_XSS, role=_XSS, lines=[_XSS])]),
        AssetBlock(heading=_XSS, asset=_ASSET, caption=_XSS, evidence=[_trace()]),
    ]
    for block in blocks:
        html = _block_html(block)
        assert "<script>" not in html, f"{type(block).__name__} emitted raw markup: {html}"
        assert "&lt;script&gt;" in html, f"{type(block).__name__} did not carry the escaped text"


def test_asset_block_emits_no_image_tag() -> None:
    """Text only this phase: relative-path resolution for the published tree is not solved."""
    html = _block_html(AssetBlock(heading="Throughput", asset=_ASSET, caption="Cap.", evidence=[_trace()]))
    assert "<img" not in html
    assert 'class="diagram"' in html and 'class="dh"' in html and "<figcaption>" in html


def test_unrecognized_block_raises_a_teaching_error_naming_its_kind() -> None:
    """The fall-through is a refusal, not a silent empty string.

    Unreachable by construction (`Surface.blocks` is a discriminated `list[Block]`) — and keeping
    it unreachable is the point. This test reaches it by calling `_block_html` directly with an
    object that is not a union member, which is the only way it can be reached at all.
    """

    class _NotAUnionMember(BaseModel):
        kind: Literal["invented-kind"] = "invented-kind"

    with pytest.raises(ValueError) as excinfo:
        _block_html(_NotAUnionMember())
    assert "invented-kind" in str(excinfo.value)
