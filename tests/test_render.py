"""Tests for the static HTML renderer — the Home (SITE-02) and the route split.

These cover the Wave-1 marketing Home: the 8-section structure, the no-JS-faithful
default-persona demo, the new eyebrow variants, and the index/library route split.
The canonical copy is `docs/surfaces.md` §"Home" + `design-reference/newsletters/home.jsx`.
"""

from __future__ import annotations

import pathlib

from newsletters.dogfood import build_site, build_surfaces
from newsletters.render import render_home, render_library
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


# --------------------------------------------------------------------------- #
# Wave 2 — Task 1: the gate-state status board (SITE-03)
# --------------------------------------------------------------------------- #


def _full_site() -> Site:
    """The full Site (all surfaces, all three newsletters) for board tests."""
    return _site()


def _board_section(html: str) -> str:
    """Return only the board markup (everything from `lib-board` onward)."""
    i = html.index("lib-board")
    return html[i:]


def test_board_groups_pages_into_three_gate_columns_in_ladder_order() -> None:
    html = render_library(_full_site())
    board = _board_section(html)
    # Three columns, headers in the Draft → In Review → Published ladder order.
    draft_at = board.index("Draft")
    review_at = board.index("In Review")
    published_at = board.index("Published")
    assert draft_at < review_at < published_at, "columns not in ReviewState ladder order"
    assert board.count('class="lib-col"') == 3, "board must always show exactly three columns"


def test_board_places_a_published_page_only_in_the_published_column() -> None:
    site = _full_site()
    html = render_library(site)
    # Find a published page and assert its card is in the Published column, not elsewhere.
    published = [p for p in site.pages() if p.gate is ReviewState.PUBLISHED]
    assert published, "fixture must contain at least one Published surface"
    # Each gate column is a <div class="lib-col">…</div>; split on the column boundaries.
    cols = html.split('class="lib-col"')
    # cols[0] is preamble; cols[1..3] are Draft / In Review / Published in order.
    assert len(cols) == 4
    published_col = cols[3]
    earlier_cols = cols[1] + cols[2]
    for p in published:
        assert f'href="{p.href}"' in published_col, f"{p.href} not in Published column"
        assert f'href="{p.href}"' not in earlier_cols, f"{p.href} leaked into a non-Published column"


def test_board_empty_column_still_renders_header_and_placeholder() -> None:
    # A Site with only a single PUBLISHED page → Draft + In Review columns are empty.
    surfaces = build_surfaces()
    published_only = [s for s in surfaces if s.gate is ReviewState.PUBLISHED][:1]
    assert published_only, "need at least one published surface for the fixture"
    site = Site.from_surfaces(published_only, ledger=Ledger.load("/nonexistent.json"))
    html = render_library(site)
    board = _board_section(html)
    assert board.count('class="lib-col"') == 3, "empty columns must not collapse"
    # The empty-state placeholder is shown for the empty columns.
    assert "No surfaces in this state." in board


def test_board_is_pure_css_grid_with_no_new_script() -> None:
    html = render_library(_full_site())
    assert "lib-board" in html
    assert "grid-template-columns:repeat(3,1fr)" in html  # CSS grid, three columns
    # The only <script> is the existing theme toggle — the board adds none.
    assert html.count("<script>") == 1


def test_board_cards_lead_with_stable_ref_and_carry_status_tag() -> None:
    site = _full_site()
    html = render_library(site)
    board = _board_section(html)
    # Cards are anchors to page.href; a representative stable ref leads (never enumerate).
    show = next(p for p in site.pages() if p.kind == "show")
    assert f'href="{show.href}"' in board
    assert show.ref in board  # EP01 — the stable ledger ref, not a position
    assert "lib-card" in board
    # Each card carries a gate status pill (sg-tag).
    assert "sg-tag" in board


def test_board_column_headers_count_their_pages() -> None:
    site = _full_site()
    html = render_library(site)
    cols = html.split('class="lib-col"')[1:]
    assert len(cols) == 3
    buckets = {ReviewState.DRAFT: 0, ReviewState.IN_REVIEW: 0, ReviewState.PUBLISHED: 0}
    for p in site.pages():
        buckets[p.gate] += 1
    ladder = [ReviewState.DRAFT, ReviewState.IN_REVIEW, ReviewState.PUBLISHED]
    for col, state in zip(cols, ladder):
        # The header carries the bucket count for its state.
        assert f"({buckets[state]})" in col, f"{state} column header missing its count"
