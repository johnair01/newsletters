"""Helpful CLI for newsletters development."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(
    help="Newsletters — distill structured knowledge into reviewed, audience-tuned surfaces.",
    no_args_is_help=True,
)


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
    out: str = typer.Option("content/rev1/site", help="Output directory for rendered HTML."),
) -> None:
    """Render the Rev1 dogfood surfaces + the Library index to standalone HTML."""
    from .dogfood import build_site

    written = build_site(out)
    for p in written:
        typer.echo(f"  {p}")
    typer.echo(f"\nrendered {len(written) - 1} surfaces + the library index -> {out}")
    typer.echo(f"open {Path(out) / 'index.html'}")


@app.command()
def check() -> None:
    """Merge-block the corpus (PROV-04): fail nonzero on any unsafe PUBLISHED surface.

    Runs the deterministic, AI-free ``review_blockers`` (Plan 10-01) across every PUBLISHED
    surface in the dogfood corpus and prints a per-surface, per-kind report. The exit code IS the
    CI contract:

    * **exit 0** — every published surface is clean (no STALE / un-entailed / open-``missing[]``
      claim). The clean shipped corpus MUST pass so the gate is green on main.
    * **exit 1** — at least one published surface carries a blocker; the report names each one and
      the build fails so an unsafe surface cannot merge.

    Draft / In-Review surfaces are exempt — publication is the trust boundary (``review_blockers``
    returns ``[]`` for them). Lazy-imports only the AI-free checker + corpus builder, so the bare
    install stays light and AI-free.
    """
    from .dogfood import build_surfaces
    from .review import review_blockers

    surfaces = build_surfaces()
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
