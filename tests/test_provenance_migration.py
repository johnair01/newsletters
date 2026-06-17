"""Plan 03-02 — content-address the Rev1 dogfood sample corpus IN PLACE, faithfully.

These tests prove the migration helper in ``newsletters.dogfood``:

* pins a Trace's content_hash + char offsets by locating its *verbatim* span inside the
  live ``Source.transcript`` (it reuses ``Trace.from_source`` from 03-01 — it does not
  re-implement hashing or offset pinning);
* is FAITHFUL — it changes neither the claim text nor the span string, only adds the
  content-address metadata (hash/start/end);
* REPORTS any span it cannot locate (empty span or not a substring) instead of fabricating
  offsets — "faithful, not suggestive", no silent dropping;
* and, applied across the dogfood build, makes the shipped corpus content-addressed and
  NOT stale at capture time, without breaking ``build_surfaces`` / ``build_site``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from newsletters.dogfood import (
    MigrationReport,
    _address_trace,
    address_corpus_traces,
    build_site,
    build_surfaces,
)
from newsletters.semantic import Source, Trace

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# Task 1 — the faithful, self-verifying migration helper
# --------------------------------------------------------------------------- #


def _src(text: str) -> Source:
    return Source(id="s1", transcript=text)


def test_address_trace_content_addresses_a_verbatim_span():
    """A span that IS a verbatim substring is pinned: hash + offsets locate it."""
    source = _src("Two layers, not five peers: a Truth layer and a Surface layer over it.")
    span = "Two layers, not five peers"
    trace = Trace(source_id="s1", span=span)

    migrated = _address_trace(source, trace)

    assert migrated.is_addressed is True
    assert migrated.content_hash == source.content_hash()
    # the offsets locate the span exactly
    assert source.transcript[migrated.start : migrated.end] == span
    assert migrated.start == source.transcript.find(span)
    assert migrated.end == migrated.start + len(span)


def test_address_trace_is_self_verifying_and_not_stale():
    """After migration the trace round-trips and is NOT stale against its own source."""
    source = _src("The Report is the investigation you approve; the Article is the lesson.")
    span = "The Report is the investigation you approve"
    migrated = _address_trace(source, Trace(source_id="s1", span=span))

    # self-verifying: the recomputed window equals the stored span
    assert source.transcript[migrated.start : migrated.end] == migrated.span
    # not stale right after migration
    assert migrated.is_stale_against(source) is False


def test_address_trace_is_faithful_span_and_claim_text_unchanged():
    """Migration adds metadata only — the span string is byte-identical before/after."""
    source = _src("Agents draft, humans decide; the gate is part of the product.")
    span = "the gate is part of the product"
    before = Trace(source_id="s1", span=span, locator="ReviewPolicy")

    after = _address_trace(source, before)

    assert after.span == before.span  # byte-identical, not rewritten
    assert after.span == span
    # the only mutation is the additive content-address metadata
    assert before.is_addressed is False and after.is_addressed is True
    # locator carried through faithfully
    assert after.locator == before.locator


def test_address_trace_reports_unlocatable_span_via_value_error():
    """A span that is NOT in the transcript is refused — never given bogus offsets."""
    source = _src("Foundation pass: spec set, repo shape, typed semantic spine, tests.")
    trace = Trace(source_id="s1", span="this phrase is not in the transcript")

    with pytest.raises(ValueError) as exc:
        _address_trace(source, trace)
    # teaching error names the span and the source so it is reported, not silent
    assert "this phrase is not in the transcript" in str(exc.value)
    assert "s1" in str(exc.value)


def test_address_trace_empty_span_is_reported_not_fabricated():
    """An empty span carries no evidence to locate — reported, never pinned to 0:0."""
    source = _src("some transcript")
    with pytest.raises(ValueError):
        _address_trace(source, Trace(source_id="s1", span=""))


def test_address_corpus_traces_collects_unlocatable_without_raising():
    """The corpus-level wrapper REPORTS unlocatable spans instead of raising."""
    source = _src("Two layers, not five peers.")
    locatable = Trace(source_id="s1", span="Two layers, not five peers")
    empty = Trace(source_id="s1", span="")  # un-addressable, but not an error to skip
    missing = Trace(source_id="s1", span="absent phrase")

    report = address_corpus_traces(
        {"s1": source},
        [locatable, empty, missing],
    )

    assert isinstance(report, MigrationReport)
    # the locatable one was addressed
    assert locatable.is_addressed is True
    assert locatable.is_stale_against(source) is False
    # the absent phrase was reported, not silently dropped or fabricated
    assert any("absent phrase" in u for u in report.unlocated)
    assert report.addressed == 1


# --------------------------------------------------------------------------- #
# Task 2 — the shipped Rev1 corpus is content-addressed and not stale
# --------------------------------------------------------------------------- #


def _corpus_traces(surfaces):
    """Every Claim Trace across the built surfaces, paired with its source lookup."""
    from newsletters.semantic import ClaimsBlock

    out = []
    for s in surfaces:
        sources = {src.id: src for src in s.traces}
        for b in s.blocks:
            if isinstance(b, ClaimsBlock):
                for c in b.claims:
                    for t in c.evidence:
                        out.append((t, sources))
    return out


def test_built_corpus_addresses_every_trace_with_a_verbatim_span():
    """After build, every trace whose span is non-empty is content-addressed."""
    surfaces = build_surfaces()
    pairs = _corpus_traces(surfaces)
    spanned = [(t, srcs) for t, srcs in pairs if t.span]
    assert spanned, "expected the migrated corpus to carry at least one verbatim-span trace"
    for t, _ in spanned:
        assert t.is_addressed is True, f"trace with span {t.span!r} was not content-addressed"


def test_built_corpus_has_no_stale_traces_at_capture_time():
    """No migrated trace is stale against its own source immediately after build."""
    surfaces = build_surfaces()
    for t, sources in _corpus_traces(surfaces):
        if t.source_id in sources:
            assert t.is_stale_against(sources[t.source_id]) is False


def test_build_site_still_writes_the_same_surface_set_as_non_empty_html(tmp_path):
    """Migration did not change the surface set/order, and every file renders to HTML."""
    expected_ids = [s.id for s in build_surfaces()]
    written = build_site(tmp_path)

    # the surface files + the library index
    written_names = {p.name for p in written}
    for sid in expected_ids:
        assert f"{sid}.html" in written_names
    assert "index.html" in written_names

    for p in written:
        text = p.read_text(encoding="utf-8")
        assert text.strip(), f"{p.name} is empty"
        assert "<!doctype html>" in text.lower()


def test_dogfood_build_imports_no_ai_module():
    """The migration is stdlib-only: a fresh build_site loads no AI module (D-4 contract)."""
    ai_modules = (
        "pydantic_ai",
        "langchain",
        "langgraph",
        "langsmith",
        "logfire",
        "openai",
        "anthropic",
    )
    code = (
        "import sys, tempfile; "
        "from newsletters.dogfood import build_site; "
        "build_site(tempfile.mkdtemp()); "
        f"bad=[m for m in {ai_modules!r} if m in sys.modules]; "
        "print('LEAK:'+','.join(bad)) if bad else print('CLEAN')"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYDANTIC_DISABLE_PLUGINS": "true", "PATH": __import__("os").environ.get("PATH", "")},
    )
    assert proc.returncode == 0, proc.stderr
    assert "CLEAN" in proc.stdout, proc.stdout
