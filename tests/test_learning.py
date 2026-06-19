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


# --------------------------------------------------------------------------- #
# L3 / Plan 04 — RENDER the learning surface + GlossaryBlock + render_path
#
# These exercise render.py directly on a real learning Surface (built via the
# Plan-03 preset on a small Distillation IN-TEST — NOT depending on Plan 05's
# dogfood wiring). They assert the RENDERED HTML, not the model: faithful (no
# invented prose on the page), LEARN-02 (every concept links to its source),
# LEARN-03 (render_path ordered + prev/next), no-JS ordered sections, and the
# self-contained / no-external-call invariant (Phase 11 self-hosted fonts).
# --------------------------------------------------------------------------- #

import re as _re  # noqa: E402  (grouped with the render-side imports below)

from newsletters.render import render_path, render_surface  # noqa: E402


def _render_record() -> Distillation:
    """A small reviewed record whose claims carry FILE-PATH locators (so they link).

    ``link_for_source`` resolves a file-path locator to the repo blob URL, so each
    rendered evidence chip becomes an ``<a class="ev-chip" href=...>`` — that is what
    makes LEARN-02 ("every concept links to its source") literal on the HTML (the Plan
    01/03 logic fixtures used a FreeLocator() with empty text, which renders plain text).

    Each claim's Trace is content-addressed against the SAME ``Source`` object that the
    Distillation carries in ``traces[]`` (one source per claim), so the rendered claim is
    NOT spuriously STALE (the live source hash matches the hash the Trace pinned).

    ``CI`` has a defining claim (glossable, traced to a file) → its glossary definition
    renders with a working source link. ``Flux`` is mentioned but never DEFINED → it routes
    to ``missing[]`` and surfaces in the honesty panel, never as a glossary definition.
    """
    from newsletters.locators import FreeLocator

    specs = [
        ("You must understand the review gate before contributing.", "docs/product-spec.md", 0.9, ["onboarding"]),
        ("Every published claim traces to evidence.", "docs/architecture.md", 0.95, ["foundations"]),
        ("CI is the continuous integration pipeline that runs every test.", "docs/architecture.md", 0.8, ["glossary", "ci"]),
        ("We later migrated Flux jobs onto the shared runner.", "docs/architecture.md", 0.4, ["deep"]),
    ]
    claims: list[Claim] = []
    srcs: list[Source] = []
    for i, (text, locator, confidence, topics) in enumerate(specs):
        src = Source(id=f"docs-record-{i}", transcript=text)
        trace = Trace.from_source(src, 0, len(text), locator=FreeLocator(text=locator))
        claims.append(Claim(text=text, evidence=[trace], confidence=confidence, topics=topics))
        srcs.append(src)
    return Distillation(narrative="A reviewed record.", claims=claims, traces=srcs)


def _render_surface() -> Surface:
    return learning_surface(
        _render_record(),
        surface_id="learn-datamodel",
        title="Onboarding: the data model",
        eyebrow="Learning · the newcomer re-cut",
        audience=Corpus(name="newcomer", weights={"onboarding": 1.0}),
        glossary_terms=["CI", "Flux"],
        prerequisites=["show-ep01"],
        author="rivera",
    )


def _main_region(html: str) -> str:
    """The surface's <main> body, with the honesty panel + chrome excluded.

    The faithful-on-the-HTML assertion is about SURFACE CONTENT (claims + glossary
    definitions), not the honesty panel (which deliberately lists un-glossed terms /
    coverage gaps) nor the page chrome (nav, footer, masthead labels)."""
    m = _re.search(r'<main class="wrap">(.*)</main>', html, _re.DOTALL)
    body = m.group(1) if m else html
    # Drop the honesty panel — it is not surface content (it is the gaps panel).
    return _re.sub(r'<div class="honesty">.*?</div>\s*$', "", body, flags=_re.DOTALL)


def test_glossary_block_renders_each_definition_with_a_source_link() -> None:
    html = render_surface(_render_surface())
    # The glossary heading renders.
    assert "Glossary" in html
    # The glossed term name appears, escaped.
    assert "CI" in html
    # The defining claim's text renders.
    assert "continuous integration pipeline" in html
    # The defining claim's evidence renders as a WORKING link (LEARN-02) — an <a ev-chip>.
    assert _re.search(
        r'<a class="ev-chip" href="https://github.com/[^"]*docs/architecture\.md">', html
    )
    # The verbatim addressed span box (_claim_spans) is present for the definition.
    assert "claim-span" in html
    # No dead href on the page.
    assert 'href="None"' not in html
    assert 'href=""' not in html


def test_rendered_learning_surface_is_faithful_no_invented_prose() -> None:
    record = _render_record()
    surface = _render_surface()
    html = render_surface(surface)
    body = _main_region(html)

    source_texts = {c.text for c in record.claims}
    # Every reviewed claim that the surface selected must appear verbatim on the page.
    rendered = _all_rendered_strings(surface)
    assert rendered
    for s in rendered:
        from newsletters.render import _e

        assert _e(s) in body, f"a selected claim is missing from the rendered body: {s!r}"
        assert s in source_texts, f"a non-source string slipped into the surface: {s!r}"

    # Faithful is also NEGATIVE: no STALE / unfaithful badge on a clean surface (the trace
    # source hash matches the carried source — nothing drifted, nothing invented).
    assert "STALE" not in body
    assert "unfaithful" not in body

    # "Flux" is NOT glossed (it is only mentioned, never defined) — it must not appear as a
    # glossary DEFINITION, only inside its own (legitimate, traced) Going-deeper claim.
    surface_gloss = next(b for b in surface.blocks if isinstance(b, GlossaryBlock))
    assert all("Flux" not in t.term for t in surface_gloss.terms)


def test_every_concept_traces_to_source_on_the_rendered_surface() -> None:
    html = render_surface(_render_surface())
    body = _main_region(html)
    # Every ev-chip in the surface body is a LINK (these fixtures all carry file locators),
    # never a dead/empty href.
    chips = _re.findall(r'<(a|span) class="ev-chip"[^>]*>', body)
    assert chips, "the surface must render evidence chips"
    for href in _re.findall(r'class="ev-chip" href="([^"]*)"', body):
        assert href and href != "None", f"dead evidence href: {href!r}"
    # The un-glossable term surfaces in the honesty panel (LEARN-02 honesty).
    assert "Flux" in html  # present somewhere — in the honesty panel
    assert "honesty" in html


def test_learning_surface_is_no_js_ordered_sections() -> None:
    html = render_surface(_render_surface())
    # The three section headings render IN DOM ORDER.
    i_start = html.find("Start here")
    i_prereq = html.find("Prerequisites")
    i_deep = html.find("Going deeper")
    assert -1 < i_start < i_prereq < i_deep, "sections must render in disclosure order"
    # Progressive disclosure is ORDER, not toggles: no <details>, no onclick.
    assert "<details" not in html
    assert "onclick" not in html
    # Exactly ONE <script> — the existing theme toggle.
    assert html.count("<script>") == 1


# --------------------------------------------------------------------------- #
# LEARN-03 — render_path() for the OnboardingPath (ordered track + prev/next)
# --------------------------------------------------------------------------- #


def _site_with_steps() -> Site:
    """A Site holding the three step targets the onboarding path sequences."""
    from newsletters.templates import get_template

    surfaces = [
        Surface(id="show-ep01", template=get_template("show"), title="Kickoff: how we debug"),
        Surface(id="report-datamodel", template=get_template("report"), title="The data model"),
        _render_surface(),  # id == learn-datamodel, kind == learning
    ]
    return Site.from_surfaces(surfaces, ledger=Ledger(__import__("pathlib").Path("/tmp/x.json"), {}))


def _path() -> OnboardingPath:
    return OnboardingPath(
        id="track-newcomer",
        title="Your first week",
        audience_label="A new contributor",
        steps=[
            OnboardingStep(slug="show-ep01", label="Watch the kickoff"),
            OnboardingStep(slug="report-datamodel", label="Read the record"),
            OnboardingStep(slug="learn-datamodel", label="The newcomer re-cut"),
        ],
    )


def test_onboarding_path_renders_ordered_with_prevnext() -> None:
    site = _site_with_steps()
    html = render_path(_path(), site=site)
    # The three steps render in track ORDER, each linking to its resolved page.href.
    i1 = html.find("show-ep01.html")
    i2 = html.find("report-datamodel.html")
    i3 = html.find("learn-datamodel.html")
    assert -1 < i1 < i2 < i3, "steps must render in track order, each linking to its surface"
    # Each step is an <a href="{slug}.html"> (resolved via Site.by_slug).
    assert '<a' in html and 'href="show-ep01.html"' in html
    # prev/next within the track: the first step has NO Previous, the last has NO Next.
    # Reuse the _prevnext device's first-no-prev/last-no-next contract.
    assert "Next" in html  # there is a next from step 1 / 2
    assert "Previous" in html  # there is a prev into step 2 / 3
    assert 'href="None"' not in html


def test_onboarding_path_unresolved_step_is_plain_text() -> None:
    site = _site_with_steps()
    path = OnboardingPath(
        id="track-x",
        title="Track",
        steps=[
            OnboardingStep(slug="show-ep01", label="Watch"),
            OnboardingStep(slug="does-not-exist", label="Missing step"),
        ],
    )
    html = render_path(path, site=site)
    # The unresolved step renders as plain text (its label), never a dead link.
    assert "Missing step" in html
    assert 'href="does-not-exist.html"' not in html
    assert 'href="None"' not in html
    assert 'href=""' not in html


def test_learning_surface_and_path_make_no_external_call() -> None:
    surface_html = render_surface(_render_surface())
    path_html = render_path(_path(), site=_site_with_steps())
    for html in (surface_html, path_html):
        # No auto-loading external resource: no http(s):// in a @font-face src, <script src>,
        # <link href>, or <img src>. Fonts are the self-hosted RELATIVE woff2 only (WORK-01).
        assert _re.search(r"@font-face[^}]*src:url\('https?://", html) is None
        assert _re.search(r"<script[^>]+src=", html) is None
        assert _re.search(r"<link[^>]+href=\"https?://", html) is None
        assert _re.search(r"<img[^>]+src=\"https?://", html) is None
        # The only <script> is the theme toggle.
        assert html.count("<script>") == 1
    # Self-hosted fonts: the woff2 src is a RELATIVE url (no scheme).
    assert "url('fonts/" in surface_html
