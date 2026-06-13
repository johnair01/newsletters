"""Helpful CLI for newsletters development."""

from __future__ import annotations

import typer

from . import SurfaceKind
from .semantic import Claim, Corpus, Distillation, Source, Trace

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
def demo(
    kind: SurfaceKind = typer.Option(SurfaceKind.REPORT, help="Which surface to render."),
    reviewer: str = typer.Option("", help="Reviewer; provided => publish the surface."),
) -> None:
    """Run the typed pipeline on a fixture event end to end (no LLM, Phase-2 spine).

    Builds a tiny traced ``Distillation`` by hand, renders it to a ``Surface`` (Draft),
    opens a review PR, and — only if a reviewer is given — publishes. Demonstrates the
    gate without the agentic distill step (that lands in Phase 4).
    """
    src = Source(
        id="latency-regression-2026-06-12",
        context="apm",
        transcript="p99 latency rose 3x after deploy 8f2a; rolled back at 14:20.",
    )
    distillation = Distillation(
        narrative="A latency regression was introduced and rolled back the same day.",
        audience=Corpus.load("maintainers"),
        claims=[
            Claim(
                text="p99 latency tripled after deploy 8f2a.",
                evidence=[Trace(source_id=src.id, locator="apm:p99")],
                confidence=0.9,
            ),
        ],
        traces=[src],
    )

    surface = distillation.render(kind)
    typer.echo(f"rendered {surface.kind.value} -> gate={surface.gate.value}")
    surface.open_pull_request(pr_url="https://example/pr/1")
    typer.echo(f"opened PR -> gate={surface.gate.value}")
    if reviewer:
        surface.publish(reviewer=reviewer)
        typer.echo(f"published by {reviewer} -> gate={surface.gate.value}")
    else:
        typer.echo("no reviewer given -> left in review (no auto-publish path)")
    typer.echo("")
    typer.echo(surface.body)


if __name__ == "__main__":
    app()
