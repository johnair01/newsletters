"""Lane D: Library connector v0 (mcp/library/). Read-only MCP server over one Library.

Fixture tests run with no MCP SDK; server tests skip if `mcp` is not installed.
Spec: docs/runs/2026-11-07/lanes/D-connector/spec.md
"""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CONNECTOR = REPO / "mcp" / "library"
FIXTURE = REPO / "tests" / "fixtures" / "library-fixture"
REV1 = REPO / "content" / "rev1"

sys.path.insert(0, str(CONNECTOR))
from library_reader import Library, LibraryError, parse_edition_html  # noqa: E402


@pytest.fixture
def lib() -> Library:
    return Library(FIXTURE)


# ---- what a Library is -------------------------------------------------------------------


def test_not_a_library_is_refused(tmp_path):
    with pytest.raises(LibraryError, match="not a Library"):
        Library(tmp_path)


def test_fixture_is_labelled_as_fixture():
    assert "FIXTURE" in (FIXTURE / "README.md").read_text()
    assert "not Pulse IQ data" in (FIXTURE / "README.md").read_text()


# ---- list_editions -----------------------------------------------------------------------


def test_list_editions_serves_published_only_and_counts_withheld(lib):
    out = lib.list_editions()
    assert out["library"] == "library-fixture"
    assert [e["slug"] for e in out["editions"]] == ["newsletter-fixture-week1", "report-fixture-gate"]
    # report-fixture-draft is Draft; report-fixture-missing-html has no page (not counted at all)
    assert out["withheld_unpublished"] == 1
    gate = out["editions"][1]
    assert gate == {
        "slug": "report-fixture-gate",
        "ref": "R-001",
        "type": "report",
        "title": "[FIXTURE] How the review gate works",
        "status": "published",
        "issue": None,
        "date": None,
    }
    assert out["editions"][0]["issue"] == 1 and out["editions"][0]["date"] == "2026-11-02"


def test_non_ledger_pages_are_not_editions(lib):
    slugs = [e["slug"] for e in lib.list_editions()["editions"]]
    assert "library" not in slugs


# ---- read_edition ------------------------------------------------------------------------


def test_read_edition_returns_main_text_only(lib):
    ed = lib.read_edition("report-fixture-gate")
    assert ed["title"] == "[FIXTURE] How the review gate works"
    assert "recorded reviewer" in ed["text"]
    assert "&amp;" not in ed["text"] and "&" in ed["text"]  # entities decoded
    assert "navonlyword" not in ed["text"]  # nav stripped
    assert "secretscriptword" not in ed["text"]  # script stripped
    assert "color:#111" not in ed["text"]  # style stripped
    assert "The Report Published" in ed["text"]  # adjacent tags do not run together


@pytest.mark.parametrize(
    "slug, match",
    [
        ("report-fixture-draft", "not published"),
        ("report-fixture-missing-html", "no page on disk"),
        ("nope", "No edition"),
        ("../../../etc/passwd", "No edition"),
        ("library", "No edition"),
    ],
)
def test_read_edition_refusals(lib, slug, match):
    with pytest.raises(LibraryError, match=match):
        lib.read_edition(slug)


# ---- search ------------------------------------------------------------------------------


def test_search_ranks_by_hits_and_requires_every_word(lib):
    out = lib.search("review gate")
    assert [r["slug"] for r in out["results"]] == ["report-fixture-gate", "newsletter-fixture-week1"]
    assert out["results"][0]["hits"] > out["results"][1]["hits"]
    assert "gate" in out["results"][0]["snippet"].lower()
    assert lib.search("gate onboarding")["results"][0]["slug"] == "newsletter-fixture-week1"
    assert len(lib.search("gate onboarding")["results"]) == 1


def test_search_never_returns_unpublished(lib):
    assert lib.search("zebradraftword")["results"] == []


def test_search_is_case_insensitive_and_limited(lib):
    assert len(lib.search("GATE", limit=1)["results"]) == 1


def test_search_empty_query_refused(lib):
    with pytest.raises(LibraryError, match="empty"):
        lib.search("   ")


# ---- conformance with the engine's real output -------------------------------------------


def test_rev1_library_conforms():
    """Every ledger edition in the engine's own Library parses to a title and a known status."""
    library = Library(REV1)
    ledger = json.loads((REV1 / "ids.json").read_text())
    for slug in ledger:
        page = REV1 / "site" / f"{slug}.html"
        parsed = parse_edition_html(page.read_text())
        assert parsed["title"], slug
        assert parsed["status"] in {"published", "in_review", "draft"}, slug
        assert len(parsed["text"]) > 200, slug
    listed = library.list_editions()
    assert len(listed["editions"]) + listed["withheld_unpublished"] == len(ledger)
    assert all(e["status"] == "published" for e in listed["editions"])
    assert library.read_edition("report-kickoff")["title"].startswith("Kicking off the build")


# ---- the MCP server ----------------------------------------------------------------------

mcp = pytest.importorskip("mcp", reason="MCP SDK not installed; server tests skipped")


def _field(obj, snake: str, camel: str):
    """MCP SDK 2.x uses snake_case attributes, 1.x uses camelCase. Accept either."""
    return getattr(obj, snake) if hasattr(obj, snake) else getattr(obj, camel)


def _server_module():
    return importlib.import_module("server")


def test_server_registers_exactly_three_read_only_tools():
    server = _server_module().build_server(FIXTURE)
    tools = asyncio.run(server.list_tools())
    assert sorted(t.name for t in tools) == ["list_editions", "read_edition", "search_library"]
    for t in tools:
        assert t.annotations is not None and _field(t.annotations, "read_only_hint", "readOnlyHint") is True, t.name
        assert _field(t.annotations, "destructive_hint", "destructiveHint") is False, t.name


def test_stdio_round_trip():
    """Start the server as a real subprocess and call each tool through an MCP client."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable, args=[str(CONNECTOR / "server.py"), "--library", str(FIXTURE)]
    )

    def payload(result):
        assert not _field(result, "is_error", "isError"), result
        return json.loads(result.content[0].text)

    async def run():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = payload(await session.call_tool("list_editions", {}))
                read_ = payload(await session.call_tool("read_edition", {"slug": "report-fixture-gate"}))
                found = payload(await session.call_tool("search_library", {"query": "gate"}))
                refused = await session.call_tool("read_edition", {"slug": "report-fixture-draft"})
                return listed, read_, found, refused

    listed, read_, found, refused = asyncio.run(run())
    assert len(listed["editions"]) == 2
    assert "recorded reviewer" in read_["text"]
    assert found["results"][0]["slug"] == "report-fixture-gate"
    assert _field(refused, "is_error", "isError") and "not published" in refused.content[0].text
