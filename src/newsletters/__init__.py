"""Newsletters — distill structured knowledge into audience-tuned, reviewed surfaces.

Two layers (see ``docs/vision.md`` and ``docs/architecture.md``):

* **Truth** — ``Source → Claim(+Trace) → Distillation``.
* **Surface** — a parameterized ``SurfaceTemplate`` bound to a truth, composed of typed
  content ``blocks``, gated by a ``Review`` whose policy is carried per template.

Two human-gated promotions form the grammar: ``promote_claim_to_kpi`` and
``promote_report_to_article``. Problem-solving agents are external; ``capture`` turns a
finished session into a traced Report.
"""

from .capture import Decision, WorkSession, build_report, capture_session
from .problem import Problem, ProblemState, TransitionEvent
from .promote import promote_claim_to_kpi, promote_report_to_article
from .render import render_library, render_surface
from .site import Collection, Ledger, Page, Site, slugify
from .semantic import (
    Chapter,
    Claim,
    ClaimsBlock,
    Corpus,
    DiagramBlock,
    Distillation,
    FanoutBlock,
    FanoutLink,
    ItemsBlock,
    KpiItem,
    KpiStripBlock,
    LetterItem,
    Lineage,
    ProseBlock,
    PromptBlock,
    Provenance,
    QuoteBlock,
    RationaleBlock,
    Review,
    ReviewState,
    Source,
    Surface,
    Trace,
    synthesize,
)
from .templates import (
    ARTICLE,
    NEWSLETTER,
    REPORT,
    SHOW,
    AudienceScope,
    Cadence,
    ReviewPolicy,
    SignalColor,
    SurfaceTemplate,
    all_templates,
    get_template,
    register,
)

__all__ = [
    # truth
    "Source", "Trace", "Claim", "Distillation", "Corpus", "synthesize",
    # review / surface
    "Review", "ReviewState", "Surface", "Provenance", "Lineage",
    # content blocks
    "ProseBlock", "ClaimsBlock", "KpiStripBlock", "QuoteBlock", "ItemsBlock",
    "PromptBlock", "FanoutBlock", "RationaleBlock", "DiagramBlock", "KpiItem", "Chapter",
    "LetterItem", "FanoutLink",
    # templates
    "SurfaceTemplate", "Cadence", "SignalColor", "AudienceScope", "ReviewPolicy",
    "SHOW", "REPORT", "ARTICLE", "NEWSLETTER", "register", "get_template", "all_templates",
    # capture + promotion
    "WorkSession", "Decision", "capture_session", "build_report",
    "promote_claim_to_kpi", "promote_report_to_article",
    # problem lifecycle (A2) — a first-class entity above Source, distinct verb `transition`
    "Problem", "ProblemState", "TransitionEvent",
    # render
    "render_surface", "render_library",
    # site (identity core — slug / ledger / content model)
    "Site", "Collection", "Page", "Ledger", "slugify",
]
