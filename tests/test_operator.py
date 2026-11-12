"""The operator view ("my view"): loader, render, committed preview, and its guard rails.

Fixture data only (tests/fixtures/operator). Nothing here writes outside ``tmp_path``.
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from newsletters.operator import load_client, load_operator_view
from newsletters.render import render_library, render_operator_view, write_operator_preview
from newsletters.site import Ledger, Site

REPO = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO / "tests" / "fixtures" / "operator"
FIXTURE_CLIENT = FIXTURE_DIR / "fixture-client"
PREVIEW_DIR = REPO / "docs" / "runs" / "2026-11-07" / "lanes" / "B-operator-view" / "preview"

REGEN_CMD = (
    "python -c \"from newsletters.operator import load_operator_view; "
    "from newsletters.render import write_operator_preview; "
    "write_operator_preview(load_operator_view(['tests/fixtures/operator/fixture-client']), "
    "'docs/runs/2026-11-07/lanes/B-operator-view/preview')\""
)


def _write_client(tmp_path: Path, **overrides) -> Path:
    """Write a minimal client.json under tmp_path (fixture JSON + overrides); return its dir."""
    raw = json.loads((FIXTURE_CLIENT / "client.json").read_text(encoding="utf-8"))
    raw.update(overrides)
    d = tmp_path / "client"
    d.mkdir()
    (d / "client.json").write_text(json.dumps(raw), encoding="utf-8")
    return d


def test_loader_reads_fixture():
    """The fixture is the contract every other test leans on; counts and gates must match the JSON."""
    view = load_operator_view([FIXTURE_CLIENT])
    assert len(view.clients) == 1
    c = view.clients[0]
    assert c.id == "fixture-client"
    assert c.fixture is True
    assert len(c.surfaces) == 4
    assert len(c.editions) == 2
    assert len(c.interactions) == 5
    gates = {s.id: s.review.state.value for s in c.surfaces}
    assert gates == {
        "fixture-report-onboarding": "published",
        "fixture-newsletter-issue-1": "published",
        "fixture-newsletter-issue-2": "in_review",
        "fixture-article-draft": "draft",
    }


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_loader_is_read_only():
    """The loader must never write: same files, same bytes, no new files after a load."""
    before = _snapshot(FIXTURE_DIR)
    load_client(FIXTURE_CLIENT)
    assert _snapshot(FIXTURE_DIR) == before


def test_published_requires_reviewer(tmp_path):
    """No-auto-publish holds here too: 'published' with no reviewer is refused."""
    surfaces = [{"id": "s1", "kind": "report", "title": "T", "gate": "published", "author": "A"}]
    d = _write_client(tmp_path, surfaces=surfaces, editions=[], interactions=[])
    with pytest.raises(ValueError):
        load_client(d)


def test_dangling_edition_reference_fails_loud(tmp_path):
    """An edition pointing at an unknown surface must fail at load, not render a dead link."""
    editions = [{"issue": 1, "date": "2026-10-24", "surface_id": "no-such-surface"}]
    d = _write_client(tmp_path, editions=editions)
    with pytest.raises(ValueError):
        load_client(d)


def test_bad_client_id_rejected(tmp_path):
    """The id becomes a directory name and an anchor, so it must be slug-clean."""
    d = _write_client(tmp_path, id="Bad Id")
    with pytest.raises(ValidationError):
        load_client(d)


def test_interactions_split_and_editions_order():
    """The view's three columns and newest-first editions come from these two accessors."""
    c = load_client(FIXTURE_CLIENT)
    by_dir = c.interactions_by_direction()
    assert len(by_dir["received"]) == 2
    assert len(by_dir["sent"]) == 2
    assert len(by_dir["pending"]) == 1
    assert c.editions_newest_first()[0].issue == 2


def test_render_shows_all_panes():
    """Every pane the operator asked for is on the page, with Library cards linking into <client-id>/."""
    view = load_operator_view([FIXTURE_CLIENT])
    out = render_operator_view(view)
    for needle in (
        "Library", "Editions", "Interactions", "Received", "Sent", "Pending",
        html.escape(view.clients[0].name), "Fixture data", "Not part of the published site",
    ):
        assert needle in out, needle
    hrefs = re.findall(r'class="lib-card" href="([^"]*)"', out)
    assert hrefs
    assert all(h.startswith("fixture-client/") for h in hrefs), hrefs


def test_render_is_deterministic():
    """Committed previews are only checkable if two independent loads render byte-identically."""
    a = render_operator_view(load_operator_view([FIXTURE_CLIENT]))
    b = render_operator_view(load_operator_view([FIXTURE_CLIENT]))
    assert a.encode("utf-8") == b.encode("utf-8")


def test_no_fixture_banner_for_real_client(tmp_path):
    """The 'Fixture data' banner must only appear for fixture clients, never a real one."""
    d = _write_client(tmp_path, fixture=False)
    out = render_operator_view(load_operator_view([d]))
    # The CSS rule `.op-fixture{...}` is always in <style>; the banner ELEMENT is what must be absent.
    assert 'class="op-fixture"' not in out
    assert "Fixture data" not in out


def test_committed_preview_matches_fresh_render(tmp_path):
    """The committed preview must be exactly what the engine renders now (no hand edits, no drift)."""
    if not PREVIEW_DIR.is_dir():
        pytest.fail(f"committed preview missing at {PREVIEW_DIR}; regenerate with:\n{REGEN_CMD}")
    view = load_operator_view([FIXTURE_CLIENT])
    written = write_operator_preview(view, tmp_path)
    fresh = {str(p.relative_to(tmp_path)) for p in written}
    for rel in sorted(fresh):
        committed = PREVIEW_DIR / rel
        assert committed.is_file(), f"{rel} missing from committed preview; regenerate with:\n{REGEN_CMD}"
        assert committed.read_bytes() == (tmp_path / rel).read_bytes(), (
            f"{rel} differs from a fresh render; regenerate with:\n{REGEN_CMD}"
        )
    on_disk = {str(p.relative_to(PREVIEW_DIR)) for p in PREVIEW_DIR.rglob("*") if p.is_file()}
    assert on_disk == fresh, f"extra files in committed preview: {sorted(on_disk - fresh)}"


def test_operator_module_is_ai_free():
    """Importing the operator module pulls in no AI library (AI-optional core)."""
    forbidden = ("pydantic_ai", "langchain", "langgraph", "openai", "anthropic")
    code = (
        "import sys, newsletters.operator; "
        f"bad=[m for m in sys.modules if m.startswith({forbidden!r})]; "
        "assert not bad, bad; print('operator ai-free')"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=REPO
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_public_pages_untouched_by_operator_css():
    """Operator-only CSS/text must not leak into the public Library page."""
    surfaces = load_client(FIXTURE_CLIENT).surfaces
    site = Site.from_surfaces(surfaces, ledger=Ledger(Path("<in-memory>"), {}))
    out = render_library(site)
    assert "op-fixture" not in out
    assert "My view" not in out


def test_no_email_address_renders_in_interactions(tmp_path):
    """Real interaction logs hold client email addresses; none may reach the page."""
    raw = json.loads((FIXTURE_CLIENT / "client.json").read_text("utf-8"))
    raw["interactions"].append(
        {"direction": "received", "date": "2026-11-05", "channel": "mail from someone@example.org",
         "summary": "Reply from first.last+tag@sub.example.co.uk about Issue 1."}
    )
    d = tmp_path / "c"
    d.mkdir()
    (d / "client.json").write_text(json.dumps(raw), encoding="utf-8")
    out = render_operator_view(load_operator_view([d]))
    assert "[email hidden]" in out
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]", out), "an email address rendered"
