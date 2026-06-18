"""SITE-01 — the deterministic, AI-free identity core (slugify + Ledger + Site/Collection/Page).

These tests prove the two ROADMAP success criteria for Phase 8:

  1. The Site/Collection/Page model carries stable per-surface IDs (slug + per-type ref +
     issue/date) generated from content, independent of list position.
  2. Inserting or reordering surfaces does not change any existing surface's ID or break
     its cross-links (``test_reorder_and_insert_preserve_ids`` — the load-bearing test).

The committed ledger at ``content/rev1/ids.json`` is NEVER touched by this suite: every
test that needs persistence uses ``tmp_path``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from newsletters.dogfood import build_surfaces
from newsletters.semantic import ReviewState, Review, Source, Surface
from newsletters.site import Collection, Ledger, Page, Site, slugify
from newsletters.templates import REPORT, SignalColor


# --------------------------------------------------------------------------- #
# slugify (L4) — deterministic, ASCII-folded, filename-safe
# --------------------------------------------------------------------------- #


def test_slugify_is_deterministic():
    s = "Café Crème — A Story, Told!"
    assert slugify(s) == slugify(s)
    # ASCII-folds accents, lowercases, collapses every non-[a-z0-9] run to one "-", strips.
    assert slugify("Café Crème") == "cafe-creme"
    assert slugify("  Hello,   WORLD!!  ") == "hello-world"
    assert slugify("report-kickoff") == "report-kickoff"  # already slug-clean → unchanged


def test_slug_is_filename_safe():
    # Security V5 / T-08-01: no slug may contain a path-traversal or whitespace char,
    # because the slug flows into f"{slug}.html".
    hostile = [
        "../../etc/passwd",
        "a/b\\c.d",
        "with spaces and\ttabs\nnewlines",
        "..\\..\\windows",
        "dot.dot.dot",
    ]
    for raw in hostile:
        out = slugify(raw)
        for bad in ("/", ".", "\\"):
            assert bad not in out, f"{out!r} from {raw!r} contains {bad!r}"
        assert not any(ch.isspace() for ch in out), f"{out!r} contains whitespace"


# --------------------------------------------------------------------------- #
# Ledger (L5) — append-only, per-type sequential refs, byte-stable JSON
# --------------------------------------------------------------------------- #


def test_ledger_assigns_per_type_sequential_refs(tmp_path):
    ledger = Ledger.load(tmp_path / "ids.json")
    Site.from_surfaces(build_surfaces(), ledger=ledger)
    refs = {slug: ledger.ref_for(slug, None) for slug in ledger.slugs()}  # read-only, immutable
    # Four reports in build order: kickoff, datamodel, rev1, plan → R-001..R-004.
    assert refs["report-kickoff"] == "R-001"
    assert refs["report-datamodel"] == "R-002"
    assert refs["report-rev1"] == "R-003"
    assert refs["report-plan"] == "R-004"
    # The single show → EP01 (2-digit). The single article → A-001 (3-digit).
    assert refs["show-ep01"] == "EP01"
    assert refs["article-semantic-spine"] == "A-001"


def test_ledger_is_append_only(tmp_path):
    path = tmp_path / "ids.json"
    ledger = Ledger.load(path)
    first = ledger.ref_for("report-kickoff", "report")
    ledger.save()

    # Reload from disk and ask again — the recorded ref must be returned unchanged,
    # never recomputed, and the stored entry byte-equal.
    before = path.read_text("utf-8")
    reloaded = Ledger.load(path)
    again = reloaded.ref_for("report-kickoff", "report")
    assert again == first == "R-001"
    reloaded.save()
    after = path.read_text("utf-8")
    assert before == after  # no-op rebuild does not mutate the ledger


def test_ledger_json_is_stable(tmp_path):
    path = tmp_path / "ids.json"
    ledger = Ledger.load(path)
    Site.from_surfaces(build_surfaces(), ledger=ledger)
    ledger.save()
    once = path.read_text("utf-8")

    # A no-op load→save round-trip produces byte-identical content (sort_keys + trailing \n).
    Ledger.load(path).save()
    twice = path.read_text("utf-8")
    assert once == twice
    assert once.endswith("\n")
    # sort_keys=True → top-level slug keys are sorted.
    import json

    data = json.loads(once)
    assert list(data) == sorted(data)


# --------------------------------------------------------------------------- #
# Site / Collection / Page (E) — content-derived IDs + by_slug resolver
# --------------------------------------------------------------------------- #


def test_page_ids_are_content_derived(tmp_path):
    ledger = Ledger.load(tmp_path / "ids.json")
    surfaces = build_surfaces()
    site = Site.from_surfaces(surfaces, ledger=ledger)

    pages = site.pages()
    assert len(pages) == len(surfaces)
    for surface in surfaces:
        page = site.by_slug(surface.id)
        assert page is not None
        assert page.slug == surface.id  # L3 backward-compat: slug defaults to Surface.id
        assert page.href == f"{surface.id}.html"
        assert page.title == surface.title
        assert page.kind == surface.kind
        assert page.gate == surface.gate
        assert page.signal_color == surface.signal_color
        assert page.surface is surface

    # Collections group by surface kind, ordered by template.distance (show 0, report 1,
    # article 2, newsletter 3).
    kinds = [c.kind for c in site.collections]
    assert kinds == ["show", "report", "article", "newsletter"]


def test_by_slug_resolves(tmp_path):
    ledger = Ledger.load(tmp_path / "ids.json")
    site = Site.from_surfaces(build_surfaces(), ledger=ledger)
    page = site.by_slug("report-kickoff")
    assert page is not None and page.slug == "report-kickoff" and page.ref == "R-001"
    assert site.by_slug("does-not-exist") is None


def _make_new_report(title: str) -> Surface:
    """A brand-new, real REPORT Surface (not a fake) for the insert half of the L7 test."""
    return Surface(
        id=slugify(title),
        template=REPORT,
        title=title,
        traces=[Source(id="session-new")],
        review=Review(policy=REPORT.review_policy, author="Tester"),
    )


# --------------------------------------------------------------------------- #
# L7 — the load-bearing stability test (ROADMAP success criterion 2)
# --------------------------------------------------------------------------- #


def test_reorder_and_insert_preserve_ids(tmp_path):
    path = tmp_path / "ids.json"
    surfaces = build_surfaces()

    # Build once, persist the ledger.
    ledger1 = Ledger.load(path)
    site1 = Site.from_surfaces(surfaces, ledger=ledger1)
    ledger1.save()
    ids1 = {p.slug: p.ref for p in site1.pages()}
    links1 = {p.href for p in site1.pages()}

    # Reorder the input list AND insert a brand-new report at the front.
    new_report = _make_new_report("Brand New Investigation")
    assert new_report.id not in ids1  # genuinely new slug
    reordered = list(reversed(surfaces))
    reordered.insert(0, new_report)

    # Rebuild against the SAME persisted ledger.
    ledger2 = Ledger.load(path)
    site2 = Site.from_surfaces(reordered, ledger=ledger2)
    ids2 = {p.slug: p.ref for p in site2.pages()}

    # 1. every pre-existing slug→ref is byte-identical (no renumber).
    for slug, ref in ids1.items():
        assert ids2[slug] == ref, f"{slug} renumbered: {ref} → {ids2[slug]}"

    # 2. every pre-existing link target still resolves via by_slug (no link rots).
    links2 = {p.href for p in site2.pages()}
    assert links1 <= links2
    for slug in ids1:
        assert site2.by_slug(slug) is not None

    # 3. the new report got a FRESH per-type ref not previously assigned → R-005
    #    (max existing report ordinal 004 + 1), and it is not any pre-existing ref.
    new_ref = ids2[new_report.id]
    assert new_ref == "R-005"
    assert new_ref not in ids1.values()


def test_imports_are_ai_free():
    """site.py must not pull in any AI/distill module (belt-and-braces alongside lint-imports)."""
    import sys

    import newsletters.site  # noqa: F401

    forbidden = ("pydantic_ai", "langchain", "langgraph", "openai", "anthropic", "logfire")
    leaked = [m for m in sys.modules if m.startswith(forbidden)]
    assert leaked == [], f"AI modules reachable from site.py: {leaked}"
