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
    * ``weekly`` — the synthetic WEEKLY worked-example corpus (``weeklysite.py``): the committed
      Weekly Spec under ``content/weekly`` composed against the ``content/module`` lane config
      (its bindings source — one fabricated module, one source of truth) and rendered to
      ``content/weekly/site``. Its ``.pptx`` deck is a CORPUS ARTIFACT, not a served page: it
      lives under ``content/weekly/deck/`` and ``publish.assemble_site`` copies
      ``content/*/site`` only, so no deck can reach the published tree (W0-2 / T-04-08).

    All corpora run the SAME corpus-agnostic merge-block gate (``review.review_blockers``) — the
    selector routes the BUILDER, never forks the gate (T-11-13).
    """

    rev1 = "rev1"
    work = "work"
    module = "module"
    weekly = "weekly"


# Per-corpus default output dirs for ``build`` (the work corpus keeps its OWN site dir, separate
# from the rev1 sample, so content/rev1/ is never touched by a work render).
_DEFAULT_OUT: dict[CorpusName, str] = {
    CorpusName.rev1: "content/rev1/site",
    CorpusName.work: "content/work/site",
    CorpusName.module: "content/module/site",
    CorpusName.weekly: "content/weekly/site",
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
        "module (the synthetic worked example), or weekly (the synthetic weekly record).",
    ),
    out: str | None = typer.Option(
        None,
        "--out",
        help="Output directory for rendered HTML (defaults per corpus: "
        "content/{rev1,work,module,weekly}/site).",
    ),
    author: str | None = typer.Option(
        None,
        "--author",
        help="The byline for the weekly record (default: the spec's `config: author:` value; "
        "one of the two must be given). Weekly-only — the other corpora carry their byline "
        "in their own content.",
    ),
) -> None:
    """Render a corpus's surfaces + the Library index to standalone HTML.

    ``--corpus rev1`` (default) renders the Rev1 dogfood sample to ``content/rev1/site`` — the
    UNCHANGED legacy behavior. ``--corpus work`` renders the real hand-authored work corpus to
    ``content/work/site`` (the install/dogfood Library, with provenance + lineage on every
    surface). ``--corpus weekly`` renders the synthetic weekly record to
    ``content/weekly/site`` — the HTML only: the deck is a separate entry point
    (``newsletters weekly``), so rendering the site never drags the ``[pptx]`` extra in.
    ``--author`` exists here because the weekly's no-byline error NAMES it (WR-03): the error
    used to point at a flag only ``newsletters weekly`` had, so the operator following it hit a
    second error. Lazy-imports only the selected builder so the bare install stays light +
    AI-free.
    """
    target = out or _DEFAULT_OUT[corpus]

    if author is not None and corpus is not CorpusName.weekly:
        # Refuse rather than ignore: a silently-dropped byline is a name somebody thought they
        # signed with. Only the weekly builder has an author seam this milestone.
        raise typer.BadParameter(
            f"--author applies to `--corpus weekly` only — the {corpus.value} corpus's byline "
            "is authored inside its own content, not passed at build time."
        )

    if corpus is CorpusName.work:
        from .worksurface import build_work_site

        written = build_work_site(target)
        index_name = "library.html"
    elif corpus is CorpusName.module:
        from .modulesite import build_module_site

        written = build_module_site(target)
        index_name = "library.html"
    elif corpus is CorpusName.weekly:
        from .weeklysite import build_weekly_site

        # The no-byline refusal (and any sibling refusal, e.g. a root-escaping asset) is a
        # TEACHING error: echo its message and exit 1 instead of dumping a Typer traceback.
        try:
            written = build_weekly_site(target, author=author)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
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
def assemble(
    out: str = typer.Option(
        "dist/site",
        "--out",
        help="Directory to assemble the publishable tree into (refuses a non-empty dir that "
        "is not a previous assembly).",
    ),
    base_path: str = typer.Option(
        "/newsletters/",
        "--base-path",
        help="URL prefix the tree is served under (GitHub project pages). Embedded ONLY in "
        "404.html; every other page keeps relative links.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Replace a non-empty --out even when it does not prove it is a previous assembly "
        "of this tool. Destructive; the default guard requires BOTH assembly markers "
        "(.nojekyll AND the generated-by marker in index.html) before clobbering.",
    ),
) -> None:
    """Assemble the published tree (PUB-01/02): rev1 at the root + work/ + module/ + weekly/.

    Copies the COMMITTED corpora byte-for-byte (what was reviewed is what publishes) and adds
    the assembly chrome (.nojekyll + the base-path-absolute 404.html). This is the ONE
    definition of "the site" — the same ``publish.assemble_site`` the tests and the deploy
    workflow run. Lazy-imports the publish module so the bare install stays light.
    """
    from .publish import assemble_site

    written = assemble_site(out, base_path=base_path, force=force)
    for p in written:
        typer.echo(f"  {p}")
    typer.echo(f"\nassembled {len(written)} files -> {out}")
    typer.echo(f"open {Path(out) / 'index.html'}")


@app.command()
def weekly(
    spec: str | None = typer.Option(
        None,
        "--spec",
        help="The Weekly Spec to render (default: the single *.yml under content/weekly).",
    ),
    lanes: str | None = typer.Option(
        None,
        "--lanes",
        help="The lane config whose KPIs/claims are bound into the weekly (default: the "
        "single *.yml under content/module — the corpus this weekly is the weekly FOR).",
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        help="Your template deck. Its Selection-Pane shape names must start with 'NL_' "
        "(default: content/weekly/template.pptx).",
    ),
    author: str | None = typer.Option(
        None,
        "--author",
        help="The byline for this weekly (default: the spec's `config: author:` value). "
        "Never invented — one of the two must be given.",
    ),
    out: str = typer.Option(
        ...,
        "--out",
        help="Where to write the deck. YOUR choice of path — it is never derived from the "
        "record's content. The digest sidecar is written beside it as <out>.digest.",
    ),
) -> None:
    """Render a Weekly Spec to a `.pptx` deck + its integrity digest (WKLY-05).

    Three properties an operator should be able to rely on, all of them tested:

    * **Deterministic.** Two renders of ONE reviewed record produce the same deck under the
      recorded ``part_digest`` definition (sorted, length-prefixed part-content rows) — so a
      re-render is checkable rather than merely plausible. The sidecar written beside the deck
      IS that digest, and it can be verified on a bare install with no optional extra.
    * **Draft, and watermarked, until a human publishes it.** The surface this renders stays
      ``Draft``; the deck carries the Draft watermark on EVERY slide and ``cp:contentStatus =
      draft``. Nothing here advances the ``Draft › In Review › Published`` gate.
    * **``--out`` is yours.** The output path is caller-supplied and never derived from the
      record's content, so authored data can never steer a write (threat T-02-08).

    ``--spec`` / ``--lanes`` / ``--template`` fall through to the corpus's structural discovery
    when omitted. Lazy-imports the builder (and, inside it, the ``[pptx]`` extra), so the bare
    install stays light and an operator without the extra gets the teaching ``ImportError``
    naming ``pip install '.[pptx]'``.
    """
    from .weeklysite import build_weekly_deck

    # A refusal (no byline, a root-escaping path) is a TEACHING error: echo its message and
    # exit 1 rather than surfacing a raw Typer traceback (WR-03).
    try:
        deck = build_weekly_deck(
            out,
            spec_path=spec,
            lanes_path=lanes,
            template=template,
            author=author,
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    digest = deck.with_suffix(deck.suffix + ".digest")
    typer.echo(f"  {deck}")
    typer.echo(f"  {digest}")
    typer.echo(
        f"\nrendered 1 Draft deck + its part_digest -> {deck.parent} "
        f"(digest: {digest.read_text(encoding='utf-8').strip()})"
    )


@app.command()
def check(
    corpus: CorpusName = typer.Option(
        CorpusName.rev1,
        "--corpus",
        case_sensitive=False,
        help="Which corpus to gate: rev1 (the sample, default), work (the real codebase), "
        "module (the synthetic worked example), or weekly (the synthetic weekly record).",
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
    corpus; ``--corpus weekly`` gates the synthetic weekly record. ANY way the SAME
    corpus-agnostic ``review_blockers`` is run over the selected corpus — the selector routes the
    builder, it does NOT fork the gate (T-11-13), so every corpus passes the IDENTICAL trust gate.

    EVERY branch below imports the MODULE OBJECT and resolves the builder off it at CALL time.
    That is load-bearing, not stylistic: it is what lets a test monkeypatch a builder to return
    ONE blocked PUBLISHED surface and watch this command FIRE. Binding the function at import
    time (``from .weeklysite import build_weekly_surfaces``) would make the blocking direction
    untestable — and a gate that cannot be proven to fire is not a gate (T-04-09).

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
    elif corpus is CorpusName.weekly:
        from . import weeklysite

        surfaces = weeklysite.build_weekly_surfaces()
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
