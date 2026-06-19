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

from newsletters.semantic import (
    Claim,
    GlossaryBlock,
    GlossaryTerm,
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
