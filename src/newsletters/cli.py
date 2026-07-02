"""Helpful CLI for newsletters development."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import typer

app = typer.Typer(
    help="Newsletters — distill structured knowledge into reviewed, audience-tuned surfaces.",
    no_args_is_help=True,
)


class CorpusName(str, Enum):
    """The selectable corpora for ``build`` / ``check`` (L5 corpus selector).

    * ``rev1`` — the synthesized Rev1 *sample* corpus (``dogfood.py``). The DEFAULT, so the
      existing ``build`` / ``check`` behavior is unchanged (backward-compat).
    * ``work`` — the REAL hand-authored work corpus (``worksurface.py``): the install/dogfood
      flow over an actual codebase, rendered to ``content/work/site``.
    * ``module`` — the synthetic worked-example corpus (``modulesite.py``): the swim-lane
      config composed + rendered to ``content/module/site`` — running the SAME
      corpus-agnostic merge-block gate as rev1/work.

    All corpora run the SAME corpus-agnostic merge-block gate (``review.review_blockers``) — the
    selector routes the BUILDER, never forks the gate (T-11-13).
    """

    rev1 = "rev1"
    work = "work"
    module = "module"


# Per-corpus default output dirs for ``build`` (the work corpus keeps its OWN site dir, separate
# from the rev1 sample, so content/rev1/ is never touched by a work render).
_DEFAULT_OUT: dict[CorpusName, str] = {
    CorpusName.rev1: "content/rev1/site",
    CorpusName.work: "content/work/site",
    CorpusName.module: "content/module/site",
}


@app.command()
def version() -> None:
    """Print the installed package version."""
    from importlib.metadata import PackageNotFoundError, version as _v

    try:
        typer.echo(_v("newsletters"))
    except PackageNotFoundError:
        typer.echo("0.1.0 (not installed)")


@app.command()
def build(
    corpus: CorpusName = typer.Option(
        CorpusName.rev1,
        "--corpus",
        case_sensitive=False,
        help="Which corpus to render: rev1 (the sample, default), work (the real codebase), "
        "or module (the synthetic worked example).",
    ),
    out: str | None = typer.Option(
        None,
        "--out",
        help="Output directory for rendered HTML (defaults per corpus: "
        "content/rev1/site or content/work/site).",
    ),
) -> None:
    """Render a corpus's surfaces + the Library index to standalone HTML.

    ``--corpus rev1`` (default) renders the Rev1 dogfood sample to ``content/rev1/site`` — the
    UNCHANGED legacy behavior. ``--corpus work`` renders the real hand-authored work corpus to
    ``content/work/site`` (the install/dogfood Library, with provenance + lineage on every
    surface). Lazy-imports only the selected builder so the bare install stays light + AI-free.
    """
    target = out or _DEFAULT_OUT[corpus]

    if corpus is CorpusName.work:
        from .worksurface import build_work_site

        written = build_work_site(target)
        index_name = "library.html"
    elif corpus is CorpusName.module:
        from .modulesite import build_module_site

        written = build_module_site(target)
        index_name = "library.html"
    else:
        from .dogfood import build_site

        written = build_site(target)
        index_name = "index.html"

    for p in written:
        typer.echo(f"  {p}")
    typer.echo(f"\nrendered {len(written) - 1} surfaces + the library index -> {target}")
    typer.echo(f"open {Path(target) / index_name}")


@app.command()
def check(
    corpus: CorpusName = typer.Option(
        CorpusName.rev1,
        "--corpus",
        case_sensitive=False,
        help="Which corpus to gate: rev1 (the sample, default), work (the real codebase), "
        "or module (the synthetic worked example).",
    ),
) -> None:
    """Merge-block a corpus (PROV-04): fail nonzero on any unsafe PUBLISHED surface.

    Runs the deterministic, AI-free ``review_blockers`` (Plan 10-01) across every PUBLISHED
    surface in the SELECTED corpus and prints a per-surface, per-kind report. The exit code IS the
    CI contract:

    * **exit 0** — every published surface is clean (no STALE / un-entailed / open-``missing[]``
      claim). The clean shipped corpus MUST pass so the gate is green on main.
    * **exit 1** — at least one published surface carries a blocker; the report names each one and
      the build fails so an unsafe surface cannot merge.

    ``--corpus rev1`` (default) gates the Rev1 dogfood sample (UNCHANGED behavior); ``--corpus
    work`` gates the real work corpus; ``--corpus module`` gates the synthetic worked-example
    corpus. ANY way the SAME corpus-agnostic ``review_blockers`` is run over the selected corpus —
    the selector routes the builder, it does NOT fork the gate (T-11-13), so every corpus passes
    the IDENTICAL trust gate.

    Draft / In-Review surfaces are exempt — publication is the trust boundary (``review_blockers``
    returns ``[]`` for them). Lazy-imports only the AI-free checker + corpus builder, so the bare
    install stays light and AI-free.
    """
    from .review import review_blockers

    if corpus is CorpusName.work:
        from . import worksurface

        surfaces = worksurface.build_work_surfaces()
    elif corpus is CorpusName.module:
        from . import modulesite

        surfaces = modulesite.build_module_surfaces()
    else:
        from . import dogfood

        surfaces = dogfood.build_surfaces()
    # Corpus-wide {source_id: Source} lookup so a claim's trace can be checked against the live
    # source even when its Source object lives on another surface's traces.
    sources = {s.id: s for surf in surfaces for s in surf.traces}
    blockers = [b for surf in surfaces for b in review_blockers(surf, sources)]

    if not blockers:
        typer.echo("All published surfaces clean — no blockers.")
        return

    for b in blockers:
        typer.echo(f"BLOCK [{b.kind.value}] {b.surface_id}: {b.detail}")
    typer.echo(f"\n{len(blockers)} blocker(s) across the corpus — merge blocked (PROV-04).")
    raise typer.Exit(1)


@app.command()
def templates() -> None:
    """List the registered surface templates (presets + any operator-registered)."""
    from .templates import all_templates

    for t in all_templates():
        typer.echo(
            f"  {t.name:<11} {t.display_name:<14} cadence={t.cadence.label:<16} "
            f"personalized={t.personalized!s:<5} gate=[{t.review_policy.describe()}]"
        )


if __name__ == "__main__":
    app()
