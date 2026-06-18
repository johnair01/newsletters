"""Tests for the static HTML renderer — the Home (SITE-02) and the route split.

These cover the Wave-1 marketing Home: the 8-section structure, the no-JS-faithful
default-persona demo, the new eyebrow variants, and the index/library route split.
The canonical copy is `docs/surfaces.md` §"Home" + `design-reference/newsletters/home.jsx`.
"""

from __future__ import annotations

import pathlib

from newsletters.dogfood import build_site, build_surfaces
from newsletters.render import render_home
from newsletters.semantic import ReviewState
from newsletters.site import Ledger, Site


def _site() -> Site:
    surfaces = build_surfaces()
    # An ephemeral, unsaved ledger keeps the test isolated (no committed-file writes).
    ledger = Ledger.load("content/rev1/ids.json")
    return Site.from_surfaces(surfaces, ledger=ledger)


# --------------------------------------------------------------------------- #
# Task 1 — section anchors + Hero emphasis + no-JS-faithful demo + eyebrow variants
# --------------------------------------------------------------------------- #


def test_home_has_every_section_anchor_exactly_once() -> None:
    html = render_home(_site())
    for anchor in ("#start", "#newsletters", "#engine", "#surfaces", "#developers"):
        assert f'id="{anchor[1:]}"' in html, f"missing section anchor {anchor}"
        assert html.count(f'id="{anchor[1:]}"') == 1, f"duplicate anchor {anchor}"


def test_home_hero_h1_with_italic_emphasis_nouns() -> None:
    html = render_home(_site())
    assert "Turn information into" in html
    # The two emphasis nouns are wrapped in <em> (italic) per the 72px hero spec.
    assert "<em>conversation.</em>" in html
    assert "<em>action.</em>" in html


def test_home_demo_renders_default_persona_inline_no_js() -> None:
    html = render_home(_site())
    # Default persona = the maintainer (home.jsx useState('maintainer')).
    assert "A maintainer" in html
    # At least one letter item title from the maintainer's canonical LETTERS copy.
    assert "The fix that shipped" in html
    # No <script> beyond the existing theme toggle (no-JS faithfulness, N6).
    assert html.count("<script>") == 1


def test_home_has_eyebrow_accent_brand_variants() -> None:
    html = render_home(_site())
    # The accent dividers (§3/§5/§7) use the new variant class.
    assert "sg-eyebrow accent" in html


# --------------------------------------------------------------------------- #
# Task 2 — the full 8-section content
# --------------------------------------------------------------------------- #


def test_home_section1_hero_copy_and_buttons() -> None:
    html = render_home(_site())
    assert "An open framework for working in the open" in html
    assert "See it in action" in html
    assert "View on GitHub" in html
    assert "Open source &middot; MIT &middot; self-hostable &middot; human-in-the-loop by design" in html


def test_home_section2_why_statement() -> None:
    html = render_home(_site())
    assert "In a world flooded with information," in html
    assert "<em>relevance wins.</em>" in html


def test_home_section3_demo_heading_and_feature_cards() -> None:
    html = render_home(_site())
    assert "Everyone gets the newsletter that&rsquo;s" in html
    for card in ("Codify once", "Tune to a corpus", "Re-cut on send"):
        assert card in html
    assert html.count('class="sg-card"') == 3


def test_home_section4_pipeline_and_gate_badge() -> None:
    html = render_home(_site())
    for step in ("Ingest", "Distill", "Review", "Publish"):
        assert step in html
    # The publishing engine reuses the gate badge with current = In Review.
    assert "sg-gate" in html
    assert "current s-in_review" in html


def test_home_section5_four_surface_rows_with_enter() -> None:
    html = render_home(_site())
    for name in ("The Show", "Newsletters", "The Articles", "The Report"):
        assert name in html
    assert "Enter" in html
    assert html.count('class="nl-surface-row"') == 4


def test_home_section6_five_practices() -> None:
    html = render_home(_site())
    for practice in (
        "Public storytelling",
        "Community contribution",
        "Prototyping in the wild",
        "Reflection &amp; documentation",
        "Remixable products",
    ):
        assert practice in html


def test_home_section7_repo_lockup_and_two_prompt_blocks() -> None:
    html = render_home(_site())
    assert "nneibaue" in html and "newsletters" in html
    assert "pip install newsletters" in html
    assert "synthesize" in html
    # Two dark prompt panels (install + synthesize.py).
    assert html.count('class="sg-prompt"') == 2


def test_home_section8_invitation_panel() -> None:
    html = render_home(_site())
    assert "Clone it, point it at your own work" in html
    assert "Get started on GitHub" in html
    assert "Replay the demo" in html


# --------------------------------------------------------------------------- #
# Task 3 — route split: index.html = Home, library.html = archive
# --------------------------------------------------------------------------- #


def test_build_site_writes_index_home_and_library_archive(tmp_path: pathlib.Path) -> None:
    written = build_site(tmp_path)
    names = {p.name for p in written}
    assert "index.html" in names
    assert "library.html" in names
    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    library_html = (tmp_path / "library.html").read_text(encoding="utf-8")
    # index.html is the marketing Home (the Hero H1), NOT the archive.
    assert "Turn information into" in index_html
    # library.html is the archive (the Library intro marker).
    assert "One reviewed record, fanned out." in library_html


def test_build_site_keeps_per_surface_filenames_stable(tmp_path: pathlib.Path) -> None:
    written = build_site(tmp_path)
    names = {p.name for p in written}
    # A representative per-surface filename stays stable (Phase-8 L3).
    assert "show-ep01.html" in names
