"""Phase 12 — the learning surface foundation (LEARN-01).

Two typed contracts this plan locks, ahead of any preset/render logic:

* **L1 — the fifth ``learning`` SurfaceTemplate** is registered and flows through
  ``Site.from_surfaces`` / the ledger as a 5th type (``L-001``) with NO ``site.py`` edit —
  the Site/ledger wiring is already kind-generic.
* **L2 — the typed ``GlossaryBlock``** whose every term's definition is a traced ``Claim``
  (never a bare ``str``) — faithfulness enforced by the type system, in the Block union.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from newsletters.learning import (
    OnboardingPath,
    OnboardingStep,
    learning_surface,
)
from newsletters.semantic import (
    Claim,
    ClaimsBlock,
    Corpus,
    Distillation,
    GlossaryBlock,
    GlossaryTerm,
    ProseBlock,
    ReviewState,
    Source,
    Surface,
    Trace,
)
from newsletters.site import Ledger, Site
from newsletters.templates import (
    AudienceScope,
    Cadence,
    ReviewPolicy,
    SignalColor,
    all_templates,
    get_template,
)


# --------------------------------------------------------------------------- #
# L1 — the learning SurfaceTemplate
# --------------------------------------------------------------------------- #


def _learning_surface() -> Surface:
    """A minimal learning Surface built on the registered template."""
    return Surface(id="learn-x", template=get_template("learning"), title="Learn X")


def test_learning_template_fields_match_locked_decision() -> None:
    learning = get_template("learning")
    assert learning.name == "learning"
    assert learning.display_name == "Learning"
    assert learning.cadence == Cadence.ON_DEMAND
    assert learning.personalized is True
    assert learning.signal_color == SignalColor.GREEN
    assert learning.scope == AudienceScope.INDIVIDUAL
    assert learning.review_policy == ReviewPolicy.light()
    assert learning.slots == ["start_here", "prerequisites", "glossary", "going_deeper"]
    assert learning.distance == 4


def test_learning_template_registered_and_lands_in_site(tmp_path) -> None:
    # get_template resolves the 5th preset.
    learning = get_template("learning")
    assert learning.name == "learning"

    # all_templates() is length 5, sorted by distance, learning last (distance 4).
    templates = all_templates()
    assert len(templates) == 5
    assert [t.distance for t in templates] == sorted(t.distance for t in templates)
    assert templates[-1].name == "learning"

    # A learning Surface lands in its own Collection with ref L-001, via an in-memory
    # ledger (NEVER touching content/rev1/ids.json).
    ledger = Ledger(tmp_path / "ids.json", {})
    site = Site.from_surfaces([_learning_surface()], ledger=ledger)
    learning_cols = [c for c in site.collections if c.kind == "learning"]
    assert len(learning_cols) == 1
    page = learning_cols[0].pages[0]
    assert page.kind == "learning"
    assert page.ref == "L-001"


# --------------------------------------------------------------------------- #
# L2 — the typed GlossaryBlock (term -> traced Claim)
# --------------------------------------------------------------------------- #


def _traced_claim(text: str = "A reviewed definition.") -> Claim:
    src = Source(id="src1", transcript=text)
    return Claim(text=text, evidence=[Trace.from_source(src, 0, len(text))])


def test_glossary_definition_is_a_traced_claim_not_a_str() -> None:
    # A bare string definition is REFUSED — faithfulness enforced by the type.
    with pytest.raises(ValidationError):
        GlossaryTerm(term="X", definition="a string")  # type: ignore[arg-type]

    # A traced Claim definition is accepted and exposes its trace.
    term = GlossaryTerm(term="X", definition=_traced_claim())
    assert isinstance(term.definition, Claim)
    assert term.definition.is_traced is True


def test_glossary_block_is_in_the_block_union() -> None:
    block = GlossaryBlock(terms=[GlossaryTerm(term="X", definition=_traced_claim())])
    assert block.kind == "glossary"

    surface = Surface(
        id="learn-x",
        template=get_template("learning"),
        title="Learn X",
        blocks=[block],
    )
    rt = Surface.model_validate_json(surface.model_dump_json())
    rebuilt = rt.blocks[0]
    assert isinstance(rebuilt, GlossaryBlock)
    assert rebuilt.kind == "glossary"
    assert rebuilt.terms[0].definition.is_traced is True


# --------------------------------------------------------------------------- #
# L2 — the FAITHFUL learning preset: learning_surface()
# --------------------------------------------------------------------------- #


def _record() -> Distillation:
    """A small, fully-traced Distillation fixture standing in for a reviewed record.

    Topics drive the deterministic section routing; confidence + original index give
    the stable+total sort key. ``CI`` has a defining claim (glossable); ``Flux`` does
    NOT (it is named only in a non-defining claim) so it must route to ``missing[]``.
    """

    def traced(text: str, *, confidence: float, topics: list[str]) -> Claim:
        src = Source(id=f"src-{abs(hash(text)) % 9973}", transcript=text)
        return Claim(
            text=text,
            evidence=[Trace.from_source(src, 0, len(text))],
            confidence=confidence,
            topics=topics,
        )

    claims = [
        # onboarding/vision topic -> Prerequisites
        traced(
            "You must understand the review gate before contributing.",
            confidence=0.9,
            topics=["onboarding"],
        ),
        # high confidence, foundational -> Start here
        traced(
            "Every published claim traces to evidence.",
            confidence=0.95,
            topics=["foundations"],
        ),
        # a DEFINING claim for the term "CI" -> glossable
        traced(
            "CI is the continuous integration pipeline that runs every test.",
            confidence=0.8,
            topics=["glossary", "ci"],
        ),
        # lower confidence detail -> Going deeper; mentions Flux but does not DEFINE it
        traced(
            "We later migrated Flux jobs onto the shared runner.",
            confidence=0.4,
            topics=["deep"],
        ),
    ]
    sources = [t.evidence[0] for c in claims for t in c.evidence]
    # rebuild Source objects for traces[] (one per claim)
    srcs = [Source(id=c.evidence[0].source_id, transcript=c.text) for c in claims]
    return Distillation(narrative="A reviewed record.", claims=claims, traces=srcs)


def _all_rendered_strings(surface: Surface) -> list[str]:
    out: list[str] = []
    for b in surface.blocks:
        if isinstance(b, ClaimsBlock):
            out.extend(c.text for c in b.claims)
        elif isinstance(b, GlossaryBlock):
            out.extend(t.definition.text for t in b.terms)
    return out


def _build() -> Surface:
    return learning_surface(
        _record(),
        surface_id="learn-datamodel",
        title="Onboarding: the data model",
        audience=Corpus(name="newcomer", weights={"onboarding": 1.0}),
        glossary_terms=["CI", "Flux"],
        prerequisites=["show-ep01"],
        author="rivera",
    )


def test_learning_surface_is_faithful_no_invented_prose() -> None:
    record = _record()
    surface = learning_surface(
        record,
        surface_id="learn-datamodel",
        title="Onboarding: the data model",
        audience=Corpus(name="newcomer", weights={"onboarding": 1.0}),
        glossary_terms=["CI", "Flux"],
        prerequisites=["show-ep01"],
        author="rivera",
    )

    source_texts = {c.text for c in record.claims}
    rendered = _all_rendered_strings(surface)
    assert rendered, "the surface must render at least one claim"
    # EVERY rendered string is an existing reviewed claim — no invented prose.
    for s in rendered:
        assert s in source_texts, f"invented (non-claim) string rendered: {s!r}"

    # ZERO hand-written ProseBlock body is emitted: only ClaimsBlock + GlossaryBlock.
    assert not any(isinstance(b, ProseBlock) for b in surface.blocks)
    kinds = {b.kind for b in surface.blocks}
    assert kinds <= {"claims", "glossary"}

    # Returned as a Draft — the caller publishes (no auto-publish).
    assert surface.review.state is ReviewState.DRAFT
    assert surface.is_published is False
    assert surface.template.name == "learning"


def test_progressive_disclosure_is_deterministic() -> None:
    a = _build()
    b = _build()

    def layers(s: Surface) -> list[tuple[str, tuple[str, ...]]]:
        return [
            (blk.heading or "", tuple(c.text for c in blk.claims))
            for blk in s.blocks
            if isinstance(blk, ClaimsBlock)
        ]

    assert layers(a) == layers(b)
    # three ordered claim layers in the locked order.
    headings = [
        blk.heading for blk in a.blocks if isinstance(blk, ClaimsBlock)
    ]
    assert headings == ["Start here", "Prerequisites", "Going deeper"]


def test_glossary_definitions_are_traced() -> None:
    surface = _build()
    gloss = next(b for b in surface.blocks if isinstance(b, GlossaryBlock))
    assert gloss.terms, "CI must resolve to a defining traced claim"
    for term in gloss.terms:
        assert term.definition.is_traced is True
        assert term.definition.evidence  # non-empty evidence


def test_unglossed_term_routes_to_missing() -> None:
    surface = _build()
    gloss = next(b for b in surface.blocks if isinstance(b, GlossaryBlock))
    glossed = {t.term for t in gloss.terms}
    # "CI" has a defining claim; "Flux" does not.
    assert "CI" in glossed
    assert "Flux" not in glossed
    # The un-glossable term is routed to missing[], never fabricated.
    assert any("Flux" in m for m in surface.missing)


# --------------------------------------------------------------------------- #
# L4 — OnboardingPath / OnboardingStep (ordered slug refs, not a Surface)
# --------------------------------------------------------------------------- #


def test_onboarding_path_is_ordered_and_not_a_surface() -> None:
    path = OnboardingPath(
        id="track-newcomer",
        title="Your first week",
        audience_label="A new contributor",
        steps=[
            OnboardingStep(slug="show-ep01", label="Watch the kickoff"),
            OnboardingStep(slug="report-datamodel", label="Read the record"),
            OnboardingStep(slug="learn-datamodel", label="The newcomer re-cut"),
        ],
    )
    # ORDER preserved exactly as given.
    assert [s.slug for s in path.steps] == [
        "show-ep01",
        "report-datamodel",
        "learn-datamodel",
    ]
    # It is NOT a Surface and carries no review gate / claims of its own.
    assert not isinstance(path, Surface)
    assert not hasattr(path, "review")
    assert not hasattr(path, "publish")
    assert not hasattr(path, "claims")


def test_onboarding_step_carries_slug_and_optional_label() -> None:
    step = OnboardingStep(slug="report-datamodel")
    assert step.slug == "report-datamodel"
    assert step.label == ""  # render resolves the title via Site.by_slug (Plan 04)
