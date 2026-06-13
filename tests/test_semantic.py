"""Tests for the typed semantic spine — the three architectural invariants.

These are the Phase-2 acceptance criteria from ``docs/roadmap.md``:
publishing without review fails; an untraced published claim is rejected (and lives in
``missing`` instead); a ``Corpus`` is never serialized into a ``Surface`` or ``Source``.
"""

import pytest

from newsletters import (
    Claim,
    Corpus,
    Distillation,
    Review,
    ReviewState,
    Source,
    Surface,
    SurfaceKind,
    Trace,
)


def _traced_distillation() -> Distillation:
    src = Source(id="evt-1", transcript="something happened")
    return Distillation(
        narrative="A thing happened and was rolled back.",
        audience=Corpus.load("maintainers"),
        claims=[
            Claim(text="the thing happened", evidence=[Trace(source_id="evt-1")], confidence=0.9),
        ],
        traces=[src],
    )


# --- Invariant 1: no publish without a reviewer (no auto-publish path) --------- #


def test_review_published_requires_reviewer():
    with pytest.raises(ValueError):
        Review(state=ReviewState.PUBLISHED)  # no reviewer
    ok = Review(state=ReviewState.PUBLISHED, reviewer="alice")
    assert ok.reviewer == "alice"


def test_surface_publish_requires_reviewer():
    surface = _traced_distillation().render("report")
    assert surface.gate is ReviewState.DRAFT
    with pytest.raises(ValueError):
        surface.publish(reviewer="")
    assert surface.gate is ReviewState.DRAFT  # unchanged after a failed publish


def test_gate_transitions_draft_review_published():
    surface = _traced_distillation().render("newsletter")
    assert surface.gate is ReviewState.DRAFT
    surface.open_pull_request(pr_url="https://example/pr/9")
    assert surface.gate is ReviewState.IN_REVIEW
    assert surface.review.pr_url == "https://example/pr/9"
    surface.publish(reviewer="bob")
    assert surface.gate is ReviewState.PUBLISHED
    assert surface.is_published
    assert surface.review.reviewer == "bob"


# --- Invariant 2: every published claim is traced; untraced => blocked --------- #


def test_render_rejects_untraced_claims():
    d = Distillation(
        narrative="n",
        claims=[Claim(text="unsupported assertion", evidence=[])],
        traces=[Source(id="evt-1")],
    )
    assert d.untraced_claims
    with pytest.raises(ValueError):
        d.render("report")


def test_untraced_material_lives_in_missing_and_does_not_block():
    # Move the unsubstantiated material to `missing` instead of claiming it; now render works.
    d = Distillation(
        narrative="n",
        claims=[Claim(text="supported", evidence=[Trace(source_id="evt-1")])],
        missing=["could not confirm the root cause"],
        traces=[Source(id="evt-1")],
    )
    surface = d.render("article")
    assert surface.gate is ReviewState.DRAFT
    assert "supported" in surface.body


# --- Invariant 3: a Corpus is never serialized into a Surface or Source -------- #


def test_corpus_not_serialized_into_surface():
    corpus = Corpus(name="maintainers", role="oncall", weights={"latency": 1.0})
    d = _traced_distillation()
    surface = d.render("report", audience=corpus)
    dumped = surface.model_dump()
    # Structurally there is no corpus field, and the corpus name must not leak into output.
    assert "audience" not in dumped
    assert "corpus" not in dumped
    assert "maintainers" not in surface.body
    assert "maintainers" not in surface.model_dump_json()


def test_corpus_not_serialized_into_source():
    dumped = Source(id="evt-1", transcript="x").model_dump()
    assert "audience" not in dumped
    assert "corpus" not in dumped


# --- Package API surface ------------------------------------------------------- #


def test_synthesize_is_stubbed_until_phase_4():
    # Honest stub: it refuses rather than fabricating untraced claims.
    with pytest.raises(NotImplementedError):
        from newsletters import synthesize

        synthesize(event="e", sources=["apm"], audience=Corpus.load("maintainers"))


def test_surface_kind_round_trips():
    assert SurfaceKind("report") is SurfaceKind.REPORT
    surface = Surface(kind="show")
    assert surface.kind is SurfaceKind.SHOW
