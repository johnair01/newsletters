"""WORK-01 — the read-only, no-network, stdlib local-file ``Source`` ingest (Phase 11).

This module is the ONE genuinely new capability of Phase 11: a minimal reader that points
Newsletters at a REAL work codebase and captures selected files as evidence, READ-ONLY. It is the
literal "install + point read-only adapters at the code, data stays local" of WORK-01.

WHY a new top-level module (not ``dogfood.py``, not an ``adapters/`` adapter):

* ``dogfood.py`` is the Rev1 *sample* corpus — a synthesized session whose transcript literally
  contains the decision statements. ``worksurface.py`` is the *real* corpus: its Sources' transcripts
  ARE the verbatim file contents of an actual codebase. Mixing the two would muddy the
  "sample vs real" boundary ``dogfood.py`` documents.
* The ``adapters/`` framework (``DistillPort``) is for *modality* extraction (email/excel/pptx) that
  routes through a distiller. A plain file reader over a hand-authored corpus is simpler and the
  honest fit — no ``DistillPort``, no auto-distillation.

READ-ONLY BY CONSTRUCTION. ``capture_files`` performs ONLY ``Path.read_text`` against the target.
It never opens a file for writing, never creates/removes anything in the scanned tree, and makes NO
network call (no ``urllib``/``requests``/``socket`` import anywhere in this module). The read-only
contract is proven by ``tests/test_worksurface.py`` (mtime + sha256 of every scanned file unchanged).

CONTENT-ADDRESSABLE. Each file becomes ``Source(id=<posix relpath>, transcript=<file text>)``. The
relpath ``id`` is exactly what ``render._is_file_path_locator`` recognizes, so a claim citing it
links to the working repo file for free, and a hand-authored claim (Plan 11-03) content-addresses to
the real file span via ``Trace.from_source`` — the SOLE pinning path. This module NEVER hand-mints a
``content_hash`` (anti-pattern); it only constructs ``Source`` records.

DETERMINISTIC. Inputs are ``sorted()`` (stable order regardless of caller/filesystem order) and the
``Source.timestamp`` is the fixed ``EPOCH_ZERO`` sentinel (reused from ``adapters/_timestamps.py``),
so the same files always produce byte-identical Sources — the byte-stability the corpus depends on
(SITE-06).

AI-FREE / ZERO NEW DEPENDENCY. Imports only stdlib ``pathlib`` + the core ``semantic``/``_timestamps``
modules; importable on a bare, no-extras install (policed by ``tests/test_ai_optional.py``).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .adapters._timestamps import EPOCH_ZERO
from .semantic import Source

__all__ = ["capture_files"]


def capture_files(paths: Iterable[str | Path], *, root: Path | None = None) -> list[Source]:
    """Read selected local files READ-ONLY into content-addressed ``Source`` records (WORK-01).

    For each path (resolved under ``root``, default :func:`Path.cwd`), build one
    ``Source(id=<posix relpath>, context="work-codebase:<relpath>", transcript=<file text>,
    timestamp=EPOCH_ZERO)``. The result is ``sorted()`` by id for determinism.

    Read-only by construction: the ONLY filesystem operation is ``Path.read_text`` — no write, no
    network. The POSIX-relpath ``id`` is recognized by ``render._is_file_path_locator`` so claims
    link to the working repo file and content-address (via ``Trace.from_source``) to its real content.

    Args:
        paths: the curated list of file paths to ingest (str or Path; absolute or relative).
            Order does not matter — the output is sorted by id.
        root: the repo root the relpath ``id`` is computed against. Defaults to ``Path.cwd()``.

    Returns:
        One ``Source`` per input path, sorted by ``id`` (the POSIX relpath).

    Raises:
        ValueError: if a path resolves OUTSIDE ``root`` (the V5 path-traversal bound —
            ``Path.relative_to`` raises). Ingest a fixed curated list, not arbitrary user input.
        FileNotFoundError: if a path does not exist (a curated list should cite only real files;
            surfacing the missing file loudly is correct — we never silently skip evidence).
        UnicodeDecodeError: if a file is not valid UTF-8 (read with ``encoding="utf-8"``; the
            corpus is code/text/markdown — a binary file is not valid evidence and is refused
            rather than mojibake'd).

    Edge-case policy (documented for Plan 11-03 to build on):
        * missing / unreadable file -> raise (never skip-silently; a curated list cites real files).
        * non-UTF-8 file            -> raise UnicodeDecodeError (no lossy decode; text corpus only).
        * absolute vs relative path -> normalized to a repo-relative POSIX ``id`` via
          ``resolve().relative_to(root)`` (so the id is stable regardless of how it was passed).
    """
    root_path = (root or Path.cwd()).resolve()
    sources: list[Source] = []
    for raw in sorted(str(p) for p in paths):
        # Resolve under root; reject anything escaping it (V5 path-traversal bound).
        candidate = Path(raw)
        absolute = candidate if candidate.is_absolute() else (root_path / candidate)
        resolved = absolute.resolve()
        rel = resolved.relative_to(root_path).as_posix()  # raises ValueError if it escapes root
        sources.append(
            Source(
                id=rel,
                context=f"work-codebase:{rel}",
                transcript=resolved.read_text(encoding="utf-8"),  # READ ONLY — no write, no network
                timestamp=EPOCH_ZERO,
            )
        )
    # Sort by id for determinism (sorted(paths) above orders raw strings; abs-vs-rel inputs and
    # symlinks can yield ids in a different order, so sort the final records by their canonical id).
    sources.sort(key=lambda s: s.id)
    return sources
