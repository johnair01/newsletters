"""Tests for the Rev1 semantic spine, templates, promotions, capture, and renderer."""

import pytest

from newsletters import (
    ARTICLE,
    NEWSLETTER,
    REPORT,
    SHOW,
    Claim,
    ClaimsBlock,
    Corpus,
    Decision,
    ProseBlock,
    Review,
    ReviewState,
    Source,
    Surface,
    Trace,
    WorkSession,
    all_templates,
    build_report,
    capture_session,
    promote_claim_to_kpi,
    promote_report_to_article,
    render_library,
    render_surface,
)
from newsletters.models import KpiStatus


def _session() -> WorkSession:
    return WorkSession(
        id="s1", title="t", tool="Claude Code", sources=[Source(id="s1")],
        decisions=[Decision(text="we decided X", source_id="s1", topics=["core"])],
    )


def _report(author="Claude") -> Surface:
    return build_report(_session(), surface_id="r1", title="R", author=author)


# --- templates ---------------------------------------------------------------- #

def test_four_presets_registered():
    names = {t.name for t in all_templates()}
    assert {"show", "report", "article", "newsletter"} <= names
    # ordered by distance: show is rawest, newsletter most distilled
    ordered = [t.name for t in all_templates()]
    assert ordered.index("show") < ordered.index("report") < ordered.index("newsletter")


def test_report_is_light_article_is_peer():
    assert REPORT.review_policy.require_peer is False
    assert ARTICLE.review_policy.require_peer is True
    assert NEWSLETTER.personalized is True and SHOW.personalized is False


# --- Invariant 1: review policy per template (no auto-publish) ----------------- #

def test_report_self_approves():
    r = _report()
    r.publish(reviewer="Claude")
    assert r.is_published and r.review.reviewer == "Claude"


def test_published_without_approval_is_rejected():
    with pytest.raises(ValueError):
        Review(state=ReviewState.PUBLISHED, policy=ARTICLE.review_policy, author="Claude")


def test_article_requires_a_peer_not_the_author():
    r = _report(author="Claude")
    r.publish(reviewer="Claude")
    article = promote_report_to_article(r, surface_id="a1", title="A", author="Claude")
    assert article.gate is ReviewState.IN_REVIEW  # opened for peer review
    # author cannot self-approve a peer-reviewed surface
    with pytest.raises(ValueError):
        article.publish(reviewer="Claude")
    assert not article.is_published
    # a peer can
    article.publish(reviewer="JJ")
    assert article.is_published and article.review.reviewer == "JJ"


# --- Invariant 2: untraced claims blocked ------------------------------------- #

def test_untraced_claim_blocks_review():
    s = Surface(id="x", template=REPORT, title="X",
                blocks=[ClaimsBlock(claims=[Claim(text="unsupported")])],
                review=Review(policy=REPORT.review_policy, author="Claude"))
    with pytest.raises(ValueError):
        s.open_pull_request()


def test_traced_claim_passes_review():
    s = Surface(id="x", template=REPORT, title="X",
                blocks=[ClaimsBlock(claims=[Claim(text="ok", evidence=[Trace(source_id="s1")])])],
                review=Review(policy=REPORT.review_policy, author="Claude"))
    s.open_pull_request()
    assert s.gate is ReviewState.IN_REVIEW


# --- Invariant 3: corpus never serialized into a surface ----------------------- #

def test_private_corpus_not_serialized_into_surface():
    corpus = Corpus(name="maintainers", weights={"core": 1.0}, read=["r1"], owned=["Core"])
    # emphasis is read at render time; the surface stores only a label
    s = Surface(id="x", template=NEWSLETTER, title="X", audience_label=f"{corpus.role}")
    dumped = s.model_dump()
    assert "weights" not in dumped and "read" not in dumped and "owned" not in dumped
    j = s.model_dump_json()
    assert "weights" not in j and "core" not in j


def test_corpus_emphasis_orders_without_leaking():
    corpus = Corpus(name="n", weights={"core": 1.0})
    c_core = Claim(text="core", evidence=[Trace(source_id="s1")], topics=["core"])
    c_other = Claim(text="other", evidence=[Trace(source_id="s1")], topics=["x"])
    from newsletters import Distillation
    d = Distillation(claims=[c_other, c_core])
    assert d.claims_for(corpus)[0] is c_core


# --- capture (post-session, deterministic) ------------------------------------ #

def test_capture_session_traces_every_decision():
    d = capture_session(_session())
    assert d.claims and all(c.is_traced for c in d.claims)
    assert d.claims[0].text == "we decided X"


# --- promotions --------------------------------------------------------------- #

def test_promote_claim_to_kpi_requires_trace():
    with pytest.raises(ValueError):
        promote_claim_to_kpi(Claim(text="untraced"), title="K", owner="o", data_link="x")
    kpi = promote_claim_to_kpi(
        Claim(text="t", evidence=[Trace(source_id="s1")]), title="K", owner="o",
        data_link="https://x", status=KpiStatus.IN_PROGRESS)
    assert kpi.title == "K" and kpi.status == KpiStatus.IN_PROGRESS


def test_promotion_records_lineage_both_ways():
    r = _report()
    r.publish(reviewer="Claude")
    a = promote_report_to_article(r, surface_id="a1", title="A", author="Claude")
    assert r.id in a.lineage.derived_from and a.id in r.lineage.produced


# --- renderer ----------------------------------------------------------------- #

def test_render_surface_is_faithful_html():
    r = _report()
    r.publish(reviewer="Claude")
    html = render_surface(r)
    assert "<!doctype html>" in html
    assert "Published" in html and "sg-gate" in html
    assert "--color-brand-primary" in html  # tokens embedded
    assert r.title in html


def test_render_does_not_leak_private_corpus():
    corpus = Corpus(name="secret-reader", weights={"core": 0.9}, read=["x"])
    s = Surface(id="n", template=NEWSLETTER, title="N", audience_label="a role",
                review=Review(policy=NEWSLETTER.review_policy, author="Claude"))
    s.publish(reviewer="Claude")
    html = render_surface(s)
    assert "weights" not in html and "secret-reader" not in html


def test_render_library_lists_surfaces():
    r = _report()
    r.publish(reviewer="Claude")
    html = render_library([r])
    assert r.title in html and "The Library" in html


def test_diagram_block_renders_themeable_svg():
    from newsletters import DiagramBlock
    from newsletters.diagrams import two_layer
    s = Surface(id="d", template=REPORT, title="D",
                blocks=[DiagramBlock(title="T", svg=two_layer(), caption="c")],
                review=Review(policy=REPORT.review_policy, author="Claude"))
    s.publish(reviewer="Claude")
    html = render_surface(s)
    assert "<svg" in html and "viewBox" in html
    # themed via tokens, not hardcoded colors
    assert "var(--text)" in html and "#0068b5" not in two_layer()


def test_build_surfaces_includes_plan_and_renders_all():
    from newsletters.dogfood import build_surfaces
    surfaces = build_surfaces()
    ids = {s.id for s in surfaces}
    assert "report-plan" in ids and "article-semantic-spine" in ids
    # the plan is a Report awaiting review; the article awaits a peer
    plan = next(s for s in surfaces if s.id == "report-plan")
    assert plan.gate is ReviewState.IN_REVIEW
    for s in surfaces:  # every surface renders without error
        assert "<!doctype html>" in render_surface(s)


def test_synthesize_is_external_stub():
    from newsletters import synthesize
    with pytest.raises(NotImplementedError):
        synthesize(event="e", sources=["apm"], audience=Corpus.load("m"))
