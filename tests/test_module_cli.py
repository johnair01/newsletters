"""MODA-02 — the ``--corpus module`` selector wires the synthetic worked-example corpus into
the SAME corpus-agnostic merge-block gate (``review.review_blockers``), and routes ``build`` to
the module builder.

This suite mirrors the ``test_worksurface.py`` corpus-level CLI contract, but over the ``module``
corpus (``modulesite.py``). It proves MODA-02 the honest way — the gate fires BOTH ways:

  * the CLEAN committed module corpus exits 0 (its only surface, the composed module-a Report,
    ships ``Draft`` → exempt: publication is the trust boundary, so ``review_blockers`` returns
    ``[]`` for it — a "clean exits 0" that is DRAFT-VACUOUS by design, exactly like the work
    corpus, and noted honestly here); and
  * a module corpus carrying ONE blocked PUBLISHED surface exits NONZERO with a report naming the
    offending surface — proving the selector routes only the BUILDER and runs the IDENTICAL,
    UNFORKED gate (T-03-06 / T-11-13: a corpus selector must not let an unsafe corpus bypass the
    gate). A gate that only ever sees clean input proves nothing (the Phase-10/11 norm).

The planted blocker is CONSTRUCTED IN THE TEST (an in-memory PUBLISHED surface injected by
monkeypatch) — NEVER by committing a dirty corpus (T-03-07): the committed ``content/module/``
stays clean + Draft.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from newsletters.cli import app
from newsletters.semantic import Claim, ClaimsBlock, Source, Surface, Trace
from newsletters.templates import REPORT

runner = CliRunner()


def _blocked_published_module_surface() -> Surface:
    """One PUBLISHED Report with an un-entailed claim — a single deterministic module blocker.

    Mirrors ``test_worksurface._blocked_published_work_surface`` but stands in for a module-corpus
    surface: an addressed trace over a transcript that does NOT contain the claim text. The trace
    is not stale (its hash matches the source), so the checker reports exactly one UNENTAILED
    blocker — enough to flip the exit code and prove the module corpus runs the same gate
    (PROV-04 / T-03-06). Built in memory only — never a committed dirty corpus (T-03-07).
    """
    transcript = "the swim-lane config the module report cites"
    src = Source(id="s-module-blocked", transcript=transcript)
    trace = Trace.from_source(
        src, 0, len(transcript)
    )  # addressed, but span omits the claim text
    claim = Claim(text="the module corpus auto-published itself", evidence=[trace])
    surface = Surface(
        id="sfc-module-blocked",
        template=REPORT,
        title="Crafted blocked module surface",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
    )
    surface.publish(reviewer="reviewer-m")
    assert surface.is_published
    return surface


def test_check_module_clean_exits_zero() -> None:
    """`newsletters check --corpus module` over the CLEAN committed corpus exits 0.

    The composed module-a Report ships ``Draft`` → exempt from ``review_blockers`` (publication is
    the trust boundary), so this "clean exits 0" is DRAFT-VACUOUS by design (same caveat as the
    work corpus in Phase 11). The blocking direction below is what proves the gate actually fires.
    """
    result = runner.invoke(app, ["check", "--corpus", "module"])
    assert result.exit_code == 0, result.output
    assert "All published surfaces clean" in result.output


def test_check_module_blocks_on_planted_blocker(monkeypatch) -> None:
    """`newsletters check --corpus module` runs the SAME UNFORKED merge-block gate — proven blocking.

    Inject ONE blocked PUBLISHED surface into the module corpus builder the command imports, and
    assert the gate FIRES: nonzero exit + a report naming the offending surface. This proves the
    module corpus passes the IDENTICAL corpus-agnostic ``review_blockers`` — the selector does not
    fork or skip it (T-03-06 / T-11-13). The blocker is a TEST fixture (monkeypatch), never a
    committed dirty corpus (T-03-07).
    """
    import newsletters.modulesite as modulesite

    monkeypatch.setattr(
        modulesite,
        "build_module_surfaces",
        lambda *a, **k: [_blocked_published_module_surface()],
    )

    blocked = runner.invoke(app, ["check", "--corpus", "module"])
    assert blocked.exit_code != 0, blocked.output
    assert "sfc-module-blocked" in blocked.output
    assert "BLOCK" in blocked.output
    assert "merge blocked" in blocked.output


def test_build_module_smoke(tmp_path: Path) -> None:
    """`newsletters build --corpus module` renders the module corpus to a chosen out dir.

    Routes to ``modulesite.build_module_site`` (the module Library + the module-a Report page),
    not the rev1 sample or the work corpus.
    """
    out = tmp_path / "modulesite"
    result = runner.invoke(app, ["build", "--corpus", "module", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / "report-module-a.html").exists()
    assert (out / "library.html").exists()
