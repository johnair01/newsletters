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
from newsletters.semantic import Trace
from newsletters.worksurface import capture_files


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
