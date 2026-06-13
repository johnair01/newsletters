"""Newsletters — distill structured knowledge into audience-tuned, reviewed surfaces.

Public API (see ``docs/architecture.md §2``)::

    from newsletters import synthesize, Corpus

    out = synthesize(event=..., sources=[...], audience=Corpus.load("maintainers"))
    surface = out.render("report")
    surface.open_pull_request()      # human reviews before publish
"""

from .semantic import (
    Claim,
    Corpus,
    Distillation,
    Review,
    ReviewState,
    Source,
    Surface,
    SurfaceKind,
    Trace,
    synthesize,
)

__all__ = [
    "Claim",
    "Corpus",
    "Distillation",
    "Review",
    "ReviewState",
    "Source",
    "Surface",
    "SurfaceKind",
    "Trace",
    "synthesize",
]
