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
from pathlib import Path

import pytest

from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.semantic import ClaimsBlock, Trace
from newsletters.worksurface import build_work_surfaces, capture_files


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


@pytest.mark.skip(
    reason="Wave-0 e2e scaffold: ingest (11-02, DONE) -> build_work_report (11-03) -> "
    "publish + render (11-04) -> newsletters check --corpus work (11-05). Later stages are "
    "filled by Plans 11-03/04/05; kept skipped so it never fails the suite prematurely."
)
def test_operator_flow_end_to_end(tmp_path: Path) -> None:
    """The full WORK happy path an operator runs against a real codebase.

    1. capture_files(curated repo files) -> content-addressed Source[]            (11-02, this plan)
    2. build_work_report(sources, ...)   -> Draft Report Surface, claims traced    (11-03)
    3. surface.publish(reviewer)         -> review gate, no auto-publish           (11-04)
    4. render_surface / build_work_site  -> provenance + lineage, NO external call (11-04)
    5. newsletters check --corpus work   -> exit 0 clean / nonzero on a blocker    (11-05)
    """
    raise NotImplementedError("filled by Plans 11-03/04/05")
