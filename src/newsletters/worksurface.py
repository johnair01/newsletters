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

import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path

from . import capture
from .adapters._timestamps import EPOCH_ZERO
from .capture import Decision, WorkSession
from .locators import FreeLocator
from .render import render_library, render_surface
from .semantic import (
    ClaimsBlock,
    FanoutBlock,
    FanoutLink,
    Source,
    Surface,
    Trace,
)
from .site import Ledger, Site

__all__ = [
    "capture_files",
    "build_work_report",
    "build_work_surfaces",
    "build_work_site",
]


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


# --------------------------------------------------------------------------- #
# WORK-02 / WORK-03 — hand-author a Report about how THIS build was done.
# --------------------------------------------------------------------------- #
#
# An operator authors a Report BY HAND and it inherits the traced structure: each claim is
# content-addressed (``Trace.from_source``) to a VERBATIM span of a real repo file ingested by
# ``capture_files`` above. A claim whose text is NOT verbatim-locatable in its cited file is
# routed to ``Surface.missing[]`` — faithful, never fabricated (the honesty panel shows it).
#
# This MIRRORS dogfood ``_address_report`` (the content-addressing precedent) but the corpus
# is REAL: the spans pin to actual codebase files, not a synthesized session transcript. We
# reuse the one zero-AI manual backend (``capture.build_report``) and the one canonical pinning
# constructor (``Trace.from_source``) — no new hashing, no hand-minted offset, no AI import.


def build_work_report(
    sources: Sequence[Source],
    decisions: Sequence[Decision],
    *,
    surface_id: str,
    title: str,
    author: str,
    narrative: str,
    tool: str = "Claude Code",
    eyebrow: str = "Report · how this build was done",
) -> Surface:
    """Hand-author a Draft work Report, content-addressing each claim to a real file span.

    Builds a :class:`~newsletters.capture.WorkSession` from ``decisions`` (each ``source_id``
    an ingested file id) + ``sources``, lifts it to a Draft Report via the zero-AI manual
    backend :func:`newsletters.capture.build_report` (a traced ``ClaimsBlock`` + provenance),
    then content-addresses every claim MIRRORING dogfood ``_address_report``:

      * ``start = src.transcript.find(claim.text)``; if ``>= 0`` the claim text is a verbatim
        slice of the cited file, so the trace is pinned via ``Trace.from_source`` (the SOLE
        minting path) — span = the verbatim file slice, drift-checkable;
      * if ``< 0`` (paraphrase / not verbatim) the claim is NOT fabricated an offset — its text
        is routed to ``Surface.missing[]`` and the claim is dropped from the ClaimsBlock, so
        every surviving claim is genuinely traced (open_pull_request invariant 2 holds).

    Finally populates ``Surface.lineage.derived_from`` with the ingested file ids the surface
    cites (the structure half of WORK-03; ``produced`` is filled once the fan-out exists in
    Plan 11-04). Zero AI, zero new runtime dependency.

    Args:
        sources: the ingested file Sources (from :func:`capture_files`) the claims pin into.
        decisions: hand-written decisions; each ``text`` should be a VERBATIM slice of the file
            named by its ``source_id`` so it content-addresses (anything paraphrased -> missing[]).
        surface_id, title, author, narrative: the Report's identity + lead prose.
        tool: the provenance tool stamp (a human/agent name; never an AI runtime import).
        eyebrow: the surface eyebrow.

    Returns:
        A Draft Report ``Surface`` whose claims are content-addressed-or-missing, with
        ``lineage.derived_from`` populated. The review gate is untouched (no auto-publish).
    """
    by_id = {s.id: s for s in sources}
    session = WorkSession(
        id=surface_id,
        title=title,
        tool=tool,
        artifacts=sorted(by_id),
        sources=list(sources),
        decisions=list(decisions),
    )
    report = capture.build_report(
        session,
        surface_id=surface_id,
        title=title,
        eyebrow=eyebrow,
        author=author,
        narrative=narrative,
    )

    # Content-address each claim to its cited file span, OR route it honestly to missing[].
    for block in report.blocks:
        if not isinstance(block, ClaimsBlock):
            continue
        kept: list = []
        for claim in block.claims:
            if not claim.evidence:
                report.missing.append(claim.text)
                continue
            trace = claim.evidence[0]
            src = by_id.get(trace.source_id)
            start = src.transcript.find(claim.text) if src is not None else -1
            if src is not None and start >= 0:
                # Verbatim: pin via the SOLE content-address constructor. Span = file slice.
                # The locator carries the file-path id so render.link_for_source recognizes it
                # as a file-path locator and turns the claim into a WORKING repo-file link
                # (the L4 "claim->repo-file link" device, surfaced for free) — the source_id is
                # already the POSIX relpath, so the link points at the real, openable file.
                claim.evidence[0] = Trace.from_source(
                    src, start, start + len(claim.text), locator=FreeLocator(text=src.id)
                )
                kept.append(claim)
            else:
                # Paraphrase / un-locatable: NEVER fabricate an offset. Show it as missing.
                report.missing.append(claim.text)
        block.claims = kept

    # WORK-03 (structure half): lineage = the ingested file ids this surface cites.
    report.lineage.derived_from = [
        sid for sid in sorted(by_id) if _cites_source(report, sid)
    ]
    return report


def _cites_source(surface: Surface, source_id: str) -> bool:
    """True iff some surviving (content-addressed) claim on ``surface`` cites ``source_id``."""
    return any(
        trace.source_id == source_id
        for block in surface.blocks
        if isinstance(block, ClaimsBlock)
        for claim in block.claims
        for trace in claim.evidence
    )


# The CURATED file list the work Report cites (the files whose verbatim spans the claims pin
# to). A curated list, never a broad glob — no orphan Sources, every Source is evidence.
_WORK_FILES: tuple[str, ...] = (
    "CLAUDE.md",
    "src/newsletters/semantic.py",
    "src/newsletters/capture.py",
    "docs/architecture.md",
)


def build_work_surfaces(*, root: Path | None = None, author: str = "Claude") -> list[Surface]:
    """Assemble the hand-authored WORK corpus: the work Report about how this build was done.

    Ingests the curated :data:`_WORK_FILES` READ-ONLY via :func:`capture_files`, authors a
    handful of hand-written :class:`~newsletters.capture.Decision`s — each ``text`` a VERBATIM
    slice of its cited file so it content-addresses (plus one deliberately-paraphrased decision
    that routes to ``missing[]``, proving honesty is real), and builds the Draft work Report via
    :func:`build_work_report`. This is the corpus the renderer (Plan 11-04) and the check gate
    (Plan 11-05) consume. Zero AI, zero new dependency, deterministic (``EPOCH_ZERO`` sources).
    """
    sources = capture_files(_WORK_FILES, root=root)

    # Hand-written decisions. Each VERBATIM text is a real slice of its cited file (so it
    # content-addresses); the LAST decision is a deliberate PARAPHRASE that does not appear
    # verbatim, so it is routed to missing[] — faithful, not suggestive, never fabricated.
    decisions = [
        Decision(
            text="No auto-publish, ever.",
            source_id="CLAUDE.md",
            topics=["process", "core"],
        ),
        Decision(
            text="Every published claim traces to evidence.",
            source_id="CLAUDE.md",
            topics=["process", "core"],
        ),
        Decision(
            text="AI-optional core.",
            source_id="CLAUDE.md",
            topics=["core"],
        ),
        Decision(
            text="Faithful, not suggestive.",
            source_id="CLAUDE.md",
            topics=["process", "design"],
        ),
        Decision(
            text="Cannot open a review with untraced claims; move them to `missing`.",
            source_id="src/newsletters/semantic.py",
            topics=["core"],
        ),
        Decision(
            text="Newsletters does **not** do the problem-solving.",
            source_id="src/newsletters/capture.py",
            topics=["process", "vision"],
        ),
        Decision(
            text="recorded `reviewer`. **No auto-publish path exists.**",
            source_id="docs/architecture.md",
            topics=["process"],
        ),
        # DELIBERATE PARAPHRASE (not verbatim in any cited file): proves an un-locatable
        # claim is routed to missing[] and never given a fabricated offset.
        Decision(
            text="Newsletters quietly publishes the best draft on the operator's behalf.",
            source_id="CLAUDE.md",
            topics=["process"],
        ),
    ]

    report = build_work_report(
        sources,
        decisions,
        surface_id="work-report",
        title="How this build was done — the trust spine, traced to the code",
        author=author,
        narrative=(
            "An operator authored this Report by hand about how Newsletters itself was built, "
            "and it inherits the traced structure: each load-bearing decision content-addresses "
            "to a verbatim span of a real file in this repository — the same trust property the "
            "product preaches, practiced on its own build. Claims that did not verbatim-locate "
            "are shown honestly as missing, never fabricated."
        ),
    )

    # WORK-03 (the fan-out half): the same reviewed record fans out per audience. These are
    # the audience surfaces this one traced record produces (the fan-out chain shown on the
    # surface via _fanout_row). They are descriptive labels — no sibling Page exists yet — so
    # render.py renders them as plain text rows (faithful: never a dead link). `lineage.produced`
    # records what this record produces, the structural complement to `derived_from` (which is
    # already the ingested file ids cited). Kept thin: a fan-out block + the produced ids, no
    # new renderer code (the _fanout_row + masthead devices are reused as-is).
    fanout = FanoutBlock(
        heading="How this one record fans out",
        links=[
            FanoutLink(kind="article", title="How this build stays honest — the trust spine"),
            FanoutLink(kind="newsletter", title="This week in the build — re-cut per reader"),
            FanoutLink(kind="learning", title="Onboarding: read the build before the code"),
        ],
    )
    report.blocks.append(fanout)
    report.lineage.produced = [link.title for link in fanout.links]
    return [report]


# --------------------------------------------------------------------------- #
# WORK-03 — PUBLISH the work site: render the corpus reusing the Phase 9/10
# provenance/lineage devices, self-contained (self-hosted fonts), zero external call.
# --------------------------------------------------------------------------- #

# The vendored, self-hosted fonts (Plan 11-01) the rendered @font-face urls reference with a
# RELATIVE `fonts/...woff2` path. They live committed under content/rev1/site/fonts/; the work
# output gets its OWN copy so content/work/site/ is self-contained (zero external call) too.
_REV1_FONTS_DIR = Path("content/rev1/site/fonts")


def _emit_fonts(out: Path) -> None:
    """Copy the self-hosted woff2 fonts (+ their OFL licenses) into ``out / fonts``.

    The renderer's ``@font-face`` blocks reference ``fonts/<name>.woff2`` with a RELATIVE url
    (render.py:_CSS), so a self-contained Library needs that ``fonts/`` dir beside the HTML.
    Plan 11-01 vendored these under ``content/rev1/site/fonts/``; we copy the SAME assets into
    the work output (rather than re-vendor) so the work Library makes zero external call too
    (T-11-10). Deterministic: shutil.copy2 preserves bytes; the set is the committed font set.
    If the vendored dir is absent (the DM-first fallback path of Plan 11-01), the relative urls
    simply do not resolve to a local file and the font-stack fallback applies — still no
    external call — so we skip silently rather than fail.
    """
    if not _REV1_FONTS_DIR.is_dir():
        return
    fonts_out = out / "fonts"
    fonts_out.mkdir(parents=True, exist_ok=True)
    for asset in sorted(_REV1_FONTS_DIR.iterdir()):
        if asset.is_file():
            shutil.copy2(asset, fonts_out / asset.name)


def build_work_site(
    out_dir: str | Path = "content/work/site",
    *,
    root: Path | None = None,
) -> list[Path]:
    """Render the WORK corpus to standalone HTML at ``out_dir`` — the published process (WORK-03).

    Mirrors :func:`newsletters.dogfood.build_site`, but over the REAL work corpus and its OWN
    append-only ledger (``content/work/ids.json``), kept SEPARATE from the rev1 sample:

      * ``Ledger.load("content/work/ids.json")`` → ``Site.from_surfaces(build_work_surfaces(),
        ledger=ledger)`` → ``ledger.save()`` (refs append-only / immutable);
      * each page is written to ``out / page.href`` via ``render_surface(page.surface, site=site,
        page=page)`` — REUSING the Phase 9/10 devices with NO new renderer: ``link_for_source``
        turns each claim's file-path locator into a working repo-file link, ``_claim_spans``
        shows the verbatim trace span, ``_honesty_panel`` shows the gap(s), the masthead emits
        ``captured via`` + ``derived from`` (real because Plan 11-03 populated ``Surface.lineage``),
        and ``_fanout_row`` renders the fan-out chain;
      * a Library index (``library.html``) is rendered from the Site;
      * the self-hosted fonts (Plan 11-01) are emitted into ``out / fonts`` so the work Library
        is self-contained — ZERO auto-loading external call (T-11-10).

    Deterministic / byte-stable (SITE-06): sorted inputs, ``EPOCH_ZERO`` sources, append-only
    ledger, no ``datetime.now()``. Zero AI, zero new runtime dependency. The work-report stays
    Draft — there is NO auto-publish path; the board reflects its real review state.

    Args:
        out_dir: where to write the work Library (default ``content/work/site``).
        root: the repo root the ingest's relpath ids resolve against (default cwd).

    Returns:
        The written paths (every ``{slug}.html`` + ``library.html``), in write order.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_work_surfaces(root=root)

    # The work corpus has its OWN ledger (R-001 starts fresh) — the sample/real boundary is
    # preserved at the ledger layer. Load → build the Site → persist any newly-assigned refs.
    ledger = Ledger.load("content/work/ids.json")
    site = Site.from_surfaces(surfaces, ledger=ledger)
    ledger.save()

    written: list[Path] = []
    for page in site.pages():
        p = out / page.href
        # Pass the resolved Site + this Page so the nav/breadcrumb/prev-next resolve neighbors.
        p.write_text(render_surface(page.surface, site=site, page=page), encoding="utf-8")
        written.append(p)

    # The Library index (the gate-state board) — the work corpus's own archive view.
    # Records strip (PUB-03): the work corpus lives at work/ in the assembled published
    # tree, so its neighbors are one level up — assembled-tree-relative by design.
    library = out / "library.html"
    library.write_text(
        render_library(
            site,
            records=(
                ("The Rev1 record", "../index.html"),
                ("The module record", "../module/library.html"),
            ),
        ),
        encoding="utf-8",
    )
    written.append(library)

    # Self-host the fonts beside the HTML so the work Library is zero-external-call (T-11-10).
    _emit_fonts(out)

    return written
