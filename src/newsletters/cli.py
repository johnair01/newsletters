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
