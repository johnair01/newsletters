"""WORK-01 — the read-only, no-network, stdlib local-file ``Source`` ingest.

This suite is the Nyquist Wave-0 anchor for Phase 11's one genuinely new capability:
``worksurface.capture_files`` turns selected repo files into content-addressable ``Source``
records, READ-ONLY by construction (``Path.read_text`` only — never a write to the target, never
a network call). The ``id`` of each Source is the POSIX relpath, which ``render._is_file_path_locator``
already recognizes — so hand-authored claims (Wave 2 / Plan 11-03) content-address (via
``Trace.from_source``) to REAL file content and link to the working repo for free.

The locked test contract (11-CONTEXT L6b):
  (a) content-addressed Sources — each ``Source.transcript`` is the verbatim file text and a
      ``Trace.from_source`` against it round-trips; ids are POSIX relpaths;
  (b) READ-ONLY proof — ``capture_files`` writes NOTHING to the scanned tree (mtime + sha256 of
      every scanned file are unchanged, and the directory listing is unchanged);
  (c) determinism — two calls return byte-identical Sources (sorted ids + ``EPOCH_ZERO`` timestamp).

``test_operator_flow_end_to_end`` is the skipped end-to-end scaffold; its later stages
(build_work_report -> publish -> render -> check) are filled by Plans 11-03/04/05.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import pytest

from typer.testing import CliRunner

from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.cli import app
from newsletters.render import repo_url
from newsletters.semantic import Claim, ClaimsBlock, Source, Surface, Trace
from newsletters.templates import REPORT
from newsletters.worksurface import (
    build_work_site,
    build_work_surfaces,
    capture_files,
)

runner = CliRunner()


def _snapshot(paths: list[Path]) -> dict[str, tuple[float, str]]:
    """Snapshot (mtime_ns, sha256) of each file so a read-only ingest can be proven."""
    snap: dict[str, tuple[float, str]] = {}
    for p in paths:
        data = p.read_bytes()
        snap[str(p)] = (p.stat().st_mtime_ns, hashlib.sha256(data).hexdigest())
    return snap


def _build_tree(root: Path) -> list[str]:
    """Create a small fixture tree under ``root``; return the POSIX relpaths to ingest."""
    (root / "src").mkdir()
    (root / "docs").mkdir()
    files = {
        "CLAUDE.md": "# project memory\nno auto-publish, ever.\n",
        "src/semantic.py": "class Source:\n    id: str\n    transcript: str = ''\n",
        "docs/architecture.md": "# Architecture\nthe typed semantic model.\n",
    }
    for rel, text in files.items():
        (root / rel).write_text(text, encoding="utf-8")
    # Deliberately UNSORTED input order so the sorted-determinism contract is exercised.
    return ["src/semantic.py", "docs/architecture.md", "CLAUDE.md"]


def test_capture_files_read_only_content_addressed(tmp_path: Path) -> None:
    """WORK-01: capture_files reads a tree READ-ONLY into content-addressed POSIX-relpath Sources.

    Asserts (a) read-only (mtime+hash of every scanned file unchanged, dir listing unchanged),
    (b) ids are POSIX relpaths, (c) transcripts are verbatim, (d) a Trace.from_source round-trips,
    (e) the list is deterministically sorted by id and timestamps are EPOCH_ZERO.
    """
    rels = _build_tree(tmp_path)
    scanned = [tmp_path / r for r in rels]
    before = _snapshot(scanned)
    before_listing = sorted(os.listdir(tmp_path))

    sources = capture_files(rels, root=tmp_path)

    # (a) READ-ONLY — nothing on the scanned tree changed; no file created/removed.
    after = _snapshot(scanned)
    assert after == before, "capture_files mutated the scanned tree — it must be read-only"
    assert sorted(os.listdir(tmp_path)) == before_listing, "capture_files altered the directory"

    # (b) ids are the POSIX relpaths.
    assert [s.id for s in sources] == sorted(rels), "ids must be POSIX relpaths, sorted"

    # (c) transcripts are verbatim file text.
    for s in sources:
        assert s.transcript == (tmp_path / s.id).read_text(encoding="utf-8")

    # (d) the source content-addresses: a Trace.from_source over a real span round-trips.
    sem = next(s for s in sources if s.id == "src/semantic.py")
    needle = "class Source:"
    start = sem.transcript.find(needle)
    assert start >= 0
    tr = Trace.from_source(sem, start, start + len(needle))
    assert tr.span == needle
    assert tr.is_addressed
    assert tr.content_hash == sem.content_hash()
    assert not tr.is_stale_against(sem)

    # (e) deterministic timestamps.
    assert all(s.timestamp == EPOCH_ZERO for s in sources)


def test_capture_files_deterministic_byte_identical(tmp_path: Path) -> None:
    """WORK-01 determinism (SITE-06 carried): two calls produce byte-identical Sources."""
    rels = _build_tree(tmp_path)
    first = capture_files(rels, root=tmp_path)
    # Pass the SAME paths in a DIFFERENT order — sorted() must absorb the difference.
    second = capture_files(list(reversed(rels)), root=tmp_path)
    dump = [s.model_dump_json() for s in first]
    assert dump == [s.model_dump_json() for s in second]


def test_capture_files_rejects_path_escaping_root(tmp_path: Path) -> None:
    """V5 path-traversal bound: a path resolving OUTSIDE root is refused (relative_to raises)."""
    (tmp_path / "inside.md").write_text("ok\n", encoding="utf-8")
    with pytest.raises(ValueError):
        capture_files(["../outside.md"], root=tmp_path)


def test_work_report_inherits_traced_structure() -> None:
    """WORK-02/03: the hand-authored work Report inherits the traced structure (Plan 11-03).

    Every ClaimsBlock claim on a work surface EITHER content-addresses to an ingested file
    span (``evidence[0].is_addressed`` with ``source_id`` in the ingested file ids — the
    span pins to a real, openable repo file) OR appears in ``surface.missing`` — nothing
    untraced or fabricated sneaks through (mirrors open_pull_request invariant 2,
    semantic.py:525-531). Asserts:

      * the happy path is real: ≥1 claim is genuinely content-addressed to a real file span
        (not all-missing) and its span is the verbatim file slice (drift-checkable);
      * the report builds via the zero-AI ``capture.build_report`` path (provenance.tool set);
      * at least one claim was honestly routed to ``missing[]`` (a deliberately-paraphrased
        claim is NOT fabricated — faithful, not suggestive);
      * each work surface carries a populated ``Surface.lineage.derived_from`` of ingested
        file ids (the structure half of WORK-03).
    """
    surfaces = build_work_surfaces()
    assert surfaces, "build_work_surfaces() returned no surfaces"

    addressed_total = 0
    missing_total = 0

    for surface in surfaces:
        # The ingested file ids this surface cites = its Source traces' ids (== POSIX relpaths).
        ingested_ids = {src.id for src in surface.traces}
        assert ingested_ids, f"{surface.id} has no ingested file Sources to cite"

        # Lineage (WORK-03 structure half): derived_from is the ingested file ids, and every
        # entry is a real cited file id — nothing fabricated.
        assert surface.lineage.derived_from, f"{surface.id} has empty lineage.derived_from"
        assert set(surface.lineage.derived_from) <= ingested_ids, (
            f"{surface.id} lineage.derived_from cites ids it did not ingest"
        )

        missing_total += len(surface.missing)

        for block in surface.blocks:
            if not isinstance(block, ClaimsBlock):
                continue
            for claim in block.claims:
                # Invariant 2 (mirrored): a claim that survives onto a ClaimsBlock MUST be
                # content-addressed to a real ingested file span — anything not verbatim was
                # routed to missing[] (and never appears here as an untraced/fabricated claim).
                assert claim.is_traced, (
                    f"{surface.id}: claim {claim.text[:40]!r} is untraced — it should have "
                    "been routed to missing[], never left on a ClaimsBlock"
                )
                trace = claim.evidence[0]
                assert trace.is_addressed, (
                    f"{surface.id}: claim {claim.text[:40]!r} trace is not content-addressed"
                )
                assert trace.source_id in ingested_ids, (
                    f"{surface.id}: claim trace pins {trace.source_id!r}, not an ingested file"
                )
                # The span IS the verbatim file slice — content-addressed, drift-checkable.
                src = next(s for s in surface.traces if s.id == trace.source_id)
                assert trace.span == src.transcript[trace.start : trace.end]
                assert trace.span in src.transcript
                assert not trace.is_stale_against(src)
                addressed_total += 1

        # The zero-AI manual backend stamped provenance (capture.build_report path).
        assert surface.provenance is not None, f"{surface.id} has no provenance"
        assert surface.provenance.tool, f"{surface.id} provenance.tool is empty"

    # The happy path is REAL: at least one claim genuinely content-addressed to a file span.
    assert addressed_total >= 1, "no claim content-addressed to a real ingested file span"
    # And honesty is real: at least one paraphrase was routed to missing[], not fabricated.
    assert missing_total >= 1, (
        "expected ≥1 claim routed to missing[] (a paraphrase that does not verbatim-locate) — "
        "faithful, not suggestive; nothing fabricated"
    )


# --------------------------------------------------------------------------- #
# Plan 11-04 (WORK-03) — PUBLISH the work site: provenance + lineage VISIBLE on
# every surface, ZERO auto-loading external calls, byte-stable across renders.
# --------------------------------------------------------------------------- #


def _work_report_html(out: Path) -> str:
    """Build the work site into ``out`` and return the work Report page's HTML.

    The work Report's slug == its id (``work-report``, L3 backward-compat), so its page
    is ``work-report.html`` — the surface that must show the process (WORK-03).
    """
    written = build_work_site(out)
    report = out / "work-report.html"
    assert report in written, "build_work_site did not emit the work Report page"
    return report.read_text(encoding="utf-8")


def test_provenance_lineage_visible(tmp_path: Path) -> None:
    """WORK-03: the published work Report shows the PROCESS on the surface itself.

    Asserts ALL of the reused Phase 9/10 provenance/lineage devices render against the
    real work corpus:
      (a) a claim->repo-file link — a ``link_for_source`` blob URL into THIS repo (so a
          reader can open the cited file);
      (b) a ``claim-span`` div — the verbatim trace span beside the claim;
      (c) the ``honesty`` panel — the gaps shown on the surface (the 1 missing[] item);
      (d) a masthead lineage/provenance bit — "derived from" (real because Plan 11-03
          populated Surface.lineage) and "captured via";
      (e) a ``fan-row`` — the fan-out chain (lineage.produced, finalized in this plan).
    """
    html = _work_report_html(tmp_path)

    # (a) claim->repo-file link: a working blob URL into THIS repo for a cited file.
    blob_re = re.compile(re.escape(repo_url) + r"/blob/main/([^\"'#]+)")
    cited = blob_re.findall(html)
    assert cited, "no claim->repo-file link (link_for_source blob URL) on the work Report"
    # The cited path is a real file in this repo (a working citation, not just well-formed).
    repo_root = Path(__file__).resolve().parent.parent
    assert any((repo_root / p.rstrip("/")).exists() for p in cited), (
        f"work Report cites repo paths that do not exist: {cited}"
    )

    # (b) verbatim trace span beside the claim.
    assert 'class="claim-span"' in html, "no verbatim claim-span on the work Report"

    # (c) the honesty panel, showing the 1 deliberately-paraphrased missing[] item.
    assert 'class="honesty"' in html, "no honesty panel on the work Report"
    surface = build_work_surfaces()[0]
    assert surface.missing, "fixture invariant: the work Report must carry a missing[] item"
    for entry in surface.missing:
        # The missing text is shown to the reviewer (escaped) — never published silently.
        assert "unsubstantiated" in html, "honesty panel does not flag the missing[] item"
        assert entry.split(".")[0] in html or entry[:20] in html, (
            "the missing[] claim text is not surfaced in the honesty panel"
        )

    # (d) masthead lineage + provenance summary (real, driven by Surface.lineage / Provenance).
    assert "derived from" in html, "masthead does not show the lineage 'derived from' summary"
    assert "captured via" in html, "masthead does not show the 'captured via' provenance"

    # (e) the fan-out chain — lineage.produced finalized now that the fan-out exists.
    assert 'class="fan-row"' in html, "no fan-out row (fan-row) on the work Report"


def test_no_external_calls_in_work_output(tmp_path: Path) -> None:
    """A2 / T-11-10: the WORK output auto-loads ZERO external resources (self-hosted fonts).

    Mirrors the rev1 no-external-call lock (test_render.py): no Google-Fonts host, no
    ``@import url(http``, no ``src="http"``, no CSS ``url(http`` (e.g. @font-face), no
    ``<link href="http">``. Clickable ``<a href="https://...">`` repo links are NAVIGATION
    (A2) and stay permitted — the work corpus must be as clean as rev1, carrying the Plan
    11-01 self-hosted fonts into content/work/site/.
    """
    written = build_work_site(tmp_path)
    pages = sorted(p for p in written if p.suffix == ".html")
    assert pages, "build_work_site produced no HTML to scan"

    forbidden = (
        "fonts.googleapis.com",
        "fonts.gstatic.com",
        "@import url('http",
        '@import url("http',
        "@import url(http",
        'src="http',
        "src='http",
    )
    css_url_fetch = re.compile(r"url\(\s*['\"]?https?://")
    link_href_http = re.compile(r"<link\b[^>]*\bhref\s*=\s*['\"]https?://", re.IGNORECASE)

    for page in pages:
        html = page.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in html, (
                f"{page.name} bakes an auto-loading external resource: {needle!r}"
            )
        assert not css_url_fetch.search(html), (
            f"{page.name} has a CSS url(http...) fetch — work fonts must be self-hosted"
        )
        assert not link_href_http.search(html), (
            f"{page.name} has a <link href=\"http...\"> auto-loaded resource"
        )

    # The self-hosted fonts the @font-face relative urls reference must actually be present
    # in the work output (so the work Library is genuinely self-contained, not just url-clean).
    fonts_dir = tmp_path / "fonts"
    assert fonts_dir.is_dir(), "build_work_site did not emit the self-hosted fonts/ dir"
    assert any(fonts_dir.glob("*.woff2")), "no woff2 fonts in the work output fonts/ dir"

    # A2 lock: clickable navigation anchors stay ABSOLUTE and are NOT flagged.
    report = (tmp_path / "work-report.html").read_text(encoding="utf-8")
    assert f'href="{repo_url}' in report, (
        "the no-external-call guard must still permit clickable repo links (A2 navigation)"
    )


def test_work_site_byte_stable(tmp_path: Path) -> None:
    """SITE-06: build_work_site is byte-stable across two renders (no datetime.now())."""
    a, b = tmp_path / "a", tmp_path / "b"
    wa = build_work_site(a)
    wb = build_work_site(b)
    names_a = sorted(p.name for p in wa)
    names_b = sorted(p.name for p in wb)
    assert names_a == names_b, "the two work renders produced a different file set"
    for name in names_a:
        assert (a / name).read_bytes() == (b / name).read_bytes(), (
            f"{name} is not byte-identical across renders (nondeterminism in the work output)"
        )


def test_operator_flow_end_to_end(tmp_path: Path) -> None:
    """The full WORK happy path an operator runs against a real codebase.

    1. capture_files(curated repo files) -> content-addressed Source[]            (11-02)
    2. build_work_report(sources, ...)   -> Draft Report Surface, claims traced    (11-03)
    3. surface stays Draft               -> review gate, NO auto-publish           (11-04)
    4. build_work_site -> render_surface -> provenance + lineage, NO external call (11-04)
    5. newsletters check --corpus work   -> exit 0 clean / nonzero on a blocker    (11-05)

    Stages 1-4 are exercised here; stage 5 (the ``--corpus work`` check) lands in Plan 11-05.
    """
    # 1-2. The corpus exists, traced, with the honesty drop and the populated lineage.
    surfaces = build_work_surfaces()
    assert surfaces, "no work surfaces"
    report = surfaces[0]
    assert report.lineage.derived_from, "lineage not populated (11-03)"

    # 3. NO auto-publish — the work-report stays Draft; the board reflects its real state.
    assert report.gate.value == "draft", "the work-report must NOT auto-publish (Draft gate)"

    # 4. Render the corpus to a self-contained site; the process is visible, zero external call.
    written = build_work_site(tmp_path)
    assert (tmp_path / "work-report.html") in written
    html = (tmp_path / "work-report.html").read_text(encoding="utf-8")
    assert "derived from" in html and 'class="honesty"' in html

    # 5. The clean work corpus passes the SAME merge-block gate (the operator-flow finale).
    #    The hand-authored work-report is Draft → exempt from review_blockers (publication is
    #    the trust boundary), so `check --corpus work` over the clean corpus exits 0.
    result = runner.invoke(app, ["check", "--corpus", "work"])
    assert result.exit_code == 0, result.output
    assert "All published surfaces clean" in result.output


# --------------------------------------------------------------------------- #
# Plan 11-05 (WORK-03 gate wiring) — the `--corpus {rev1|work}` selector wires the
# WORK corpus into the SAME corpus-agnostic merge-block gate (review_blockers).
# --------------------------------------------------------------------------- #


def _blocked_published_work_surface() -> Surface:
    """One PUBLISHED Report with an un-entailed claim — a single deterministic work blocker.

    Mirrors test_review_cli.py's UNENTAILED fixture, but stands in for a work-corpus surface:
    an addressed trace over a transcript that does NOT contain the claim text. Not stale (the
    hash matches), so the checker reports exactly one UNENTAILED blocker — enough to flip the
    exit code and prove the work corpus runs the same gate (PROV-04 / T-11-13).
    """
    transcript = "the curated file list the work report cites"
    src = Source(id="s-work-blocked", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # addressed, but span omits the claim text
    claim = Claim(text="the work corpus auto-published itself", evidence=[trace])
    surface = Surface(
        id="sfc-work-blocked",
        template=REPORT,
        title="Crafted blocked work surface",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
    )
    surface.publish(reviewer="reviewer-w")
    assert surface.is_published
    return surface


def test_check_gates_work_corpus(monkeypatch) -> None:
    """`newsletters check --corpus work` runs the SAME merge-block gate over the work corpus.

    Both exit directions, mirroring test_review_cli.py but against the work corpus builder:

    * the clean work corpus (the Draft hand-authored work-report is exempt) -> **exit 0**; and
    * a work corpus carrying ONE blocked PUBLISHED surface -> **exit nonzero**, the report
      naming the offending surface. This proves the work corpus passes the IDENTICAL
      corpus-agnostic ``review_blockers`` gate — the selector does not fork or skip it
      (T-11-13: a corpus selector must not let an unsafe corpus bypass the gate).
    """
    # Clean direction: the real work corpus exits 0 (its only surface is Draft → exempt).
    clean = runner.invoke(app, ["check", "--corpus", "work"])
    assert clean.exit_code == 0, clean.output
    assert "All published surfaces clean" in clean.output

    # Blocked direction: inject one blocked published surface into the work corpus builder the
    # command imports, and assert the gate FIRES (Phase-7 lesson: prove it blocks, not just passes).
    import newsletters.worksurface as worksurface

    monkeypatch.setattr(
        worksurface,
        "build_work_surfaces",
        lambda *a, **k: [_blocked_published_work_surface()],
    )

    blocked = runner.invoke(app, ["check", "--corpus", "work"])
    assert blocked.exit_code != 0, blocked.output
    assert "sfc-work-blocked" in blocked.output
    assert "BLOCK" in blocked.output
    assert "merge blocked" in blocked.output


def test_check_rev1_default_unchanged() -> None:
    """`newsletters check` with no flag (default rev1) is unchanged — the clean corpus exits 0."""
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "All published surfaces clean" in result.output


def test_build_corpus_work_smoke(tmp_path: Path) -> None:
    """`newsletters build --corpus work` renders the work corpus to a chosen out dir.

    Routes to ``build_work_site`` (the work Library + work-report page), not the rev1 sample.
    """
    out = tmp_path / "worksite"
    result = runner.invoke(app, ["build", "--corpus", "work", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / "work-report.html").exists()
    assert (out / "library.html").exists()
