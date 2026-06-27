"""The learning/onboarding surface — the FAITHFUL newcomer re-cut (LEARN-01/02/03).

This module is the genuinely-new logic of Phase 12. It holds two things:

* :func:`learning_surface` (L2 — the faithfulness crux) — re-cuts an already-reviewed
  ``Distillation`` into a newcomer-shaped ``Surface``. It **SELECTS, ORDERS, and LINKS
  existing traced reviewed claims and traced glossary definitions — it never authors new
  factual prose.** Progressive disclosure is three ordered DOM sections (Start here /
  Prerequisites / Going deeper) built from existing claims, keyed deterministically by
  ``confidence`` + ``topics`` (a stable+total sort key, for byte-stability). The glossary
  is a :class:`~newsletters.semantic.GlossaryBlock` whose every term's definition is a
  DEFINING traced ``Claim`` selected from the record; a requested term with no traceable
  defining claim is routed to ``surface.missing[]`` (the honesty panel) — never fabricated.
  The surface is returned as a ``Draft`` — the caller publishes (no auto-publish path).

* :class:`OnboardingPath` / :class:`OnboardingStep` (L4) — a typed, ORDERED list of slug
  refs sequencing surfaces that ALREADY passed the review gate. The path is *navigation*,
  not a ``Surface``: it carries no claims and **no own review gate** (it publishes nothing
  new, so no-auto-publish is not implicated). ``render_path()`` (Plan 04) resolves each step
  via ``Site.by_slug``; rendering is deliberately NOT here.

IMPORT-GRAPH NOTE (load-bearing — the AI-optional-core boundary): this module imports ONLY
stdlib + ``pydantic`` + the sibling core modules ``.semantic`` / ``.templates``. It must
NEVER import the ``.distill`` package or any AI/LLM dependency (mirror ``site.py``).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .semantic import (
    Block,
    Claim,
    ClaimsBlock,
    Corpus,
    Distillation,
    GlossaryBlock,
    GlossaryTerm,
    Lineage,
    Review,
    Surface,
)
from .templates import LEARNING

# Topics that mark a claim as foundational prerequisite context for a newcomer. Matched
# case-insensitively against ``Claim.topics``. Deterministic membership test — no AI.
_PREREQUISITE_TOPICS = frozenset(
    {"onboarding", "vision", "prerequisite", "prerequisites", "prereq", "foundation"}
)
# Topics that mark a claim as deeper detail (last layer).
_DEEPER_TOPICS = frozenset({"deep", "deeper", "advanced", "detail", "appendix"})
# Confidence at/above which an un-routed claim is treated as foundational (Start here).
_START_HERE_CONFIDENCE = 0.7


def _topic_set(claim: Claim) -> frozenset[str]:
    return frozenset(t.casefold() for t in claim.topics)


def _layer_for(claim: Claim) -> str:
    """Deterministically assign a claim to one of the three progressive-disclosure layers.

    Routing is a pure function of ``topics`` + ``confidence`` (A3 — derived, no schema
    change). Prerequisite/onboarding topics go to *Prerequisites*; explicit deep topics go
    to *Going deeper*; otherwise high-confidence claims are foundational (*Start here*) and
    the remainder are *Going deeper*. No ``datetime.now()``, no dict-iteration order — the
    same claim always lands in the same layer.
    """
    topics = _topic_set(claim)
    if topics & _PREREQUISITE_TOPICS:
        return "Prerequisites"
    if topics & _DEEPER_TOPICS:
        return "Going deeper"
    if claim.confidence >= _START_HERE_CONFIDENCE:
        return "Start here"
    return "Going deeper"


def _defines(claim: Claim, term: str) -> bool:
    """True iff ``claim`` reads as a DEFINING statement for ``term`` ("X is …"/"X are …").

    A faithful, deterministic match: the claim must be traced AND its text must contain the
    term followed by a copula ("is"/"are"/"means"/"refers to"). This refuses to gloss a term
    from a claim that merely MENTIONS it (e.g. "we migrated Flux jobs"), so a term with no
    genuine defining claim falls through to ``missing[]`` rather than being mis-glossed.
    """
    if not claim.is_traced:
        return False
    text = claim.text.casefold()
    needle = term.casefold()
    if needle not in text:
        return False
    for copula in (" is ", " are ", " means ", " refers to "):
        if f"{needle}{copula}" in text:
            return True
    return False


def learning_surface(
    distillation: Distillation,
    *,
    surface_id: str,
    title: str,
    audience: Corpus | None = None,
    glossary_terms: list[str] | None = None,
    prerequisites: list[str] | None = None,
    author: str | None = None,
    eyebrow: str = "",
) -> Surface:
    """Re-cut a reviewed ``Distillation`` into a FAITHFUL learning ``Surface`` (LEARN-01/02).

    SELECTS / ORDERS / LINKS existing traced claims only — emits NO invented prose. Steps:

    1. ``claims = distillation.claims_for(audience)`` — reuse the personalization re-cut
       (same facts, newcomer emphasis); do NOT hand re-sort the global order.
    2. Layer the claims into *Start here* / *Prerequisites* / *Going deeper* via
       :func:`_layer_for`, preserving the ``claims_for`` order WITHIN each layer (which is a
       total, stable key) so identical input gives identical assignment every run.
    3. Build the glossary: resolve each requested term to its DEFINING traced ``Claim`` via
       :func:`_defines` (deterministic, first match by order). A resolved term becomes a
       ``GlossaryTerm``; an UNRESOLVED term is appended to ``surface.missing[]`` — never
       glossed with fabricated prose.
    4. Emit ONLY ``ClaimsBlock`` (one per non-empty layer) + a single ``GlossaryBlock`` —
       no free ``ProseBlock`` body.
    5. Return a ``Draft`` bound to the ``learning`` template; the CALLER publishes.

    ``prerequisites`` is carried through as ``surface`` data for Plan 04's render to resolve
    via ``Site.by_slug`` (links to prerequisite records), NOT as new exposition here.
    """
    ordered = distillation.claims_for(audience)

    # Stable layering: iterate the (already total+stable) claims_for order once, bucketing
    # each claim by its deterministic layer. Insertion order within a bucket == claims_for
    # order, so the assignment is reproducible.
    buckets: dict[str, list[Claim]] = {
        "Start here": [],
        "Prerequisites": [],
        "Going deeper": [],
    }
    for claim in ordered:
        buckets[_layer_for(claim)].append(claim)

    blocks: list[Block] = []
    for heading in ("Start here", "Prerequisites", "Going deeper"):
        layer = buckets[heading]
        if layer:
            blocks.append(ClaimsBlock(heading=heading, claims=layer))

    # Glossary: resolve each requested term to a defining traced claim, deterministically.
    terms: list[GlossaryTerm] = []
    unglossable: list[str] = []
    for term in glossary_terms or []:
        definition = next((c for c in ordered if _defines(c, term)), None)
        if definition is not None:
            terms.append(GlossaryTerm(term=term, definition=definition))
        else:
            unglossable.append(term)

    # The glossary block sits between Prerequisites and Going deeper per the template slots
    # ("start_here", "prerequisites", "glossary", "going_deeper"). Always emit it (even when
    # empty) so the honesty panel / un-glossed routing is visible at the slot.
    insert_at = len(blocks)
    for i, b in enumerate(blocks):
        if isinstance(b, ClaimsBlock) and b.heading == "Going deeper":
            insert_at = i
            break
    blocks.insert(insert_at, GlossaryBlock(terms=terms))

    # missing[] = the record's own unsubstantiated material + the un-glossable terms. Strings
    # only (invariant 3). The un-glossed terms are SHOWN to the reviewer, never fabricated.
    missing = [
        *distillation.missing,
        *(f"Glossary term {t!r} has no traceable defining claim" for t in unglossable),
    ]

    return Surface(
        id=surface_id,
        template=LEARNING,
        title=title,
        eyebrow=eyebrow,
        blocks=blocks,
        traces=list(distillation.traces),
        missing=missing,
        audience_label=audience.name if audience is not None else None,
        review=Review(policy=LEARNING.review_policy, author=author),
        # Carry prerequisite slug refs as lineage data (links, not exposition) for Plan 04
        # to resolve via Site.by_slug. NOT new prose on the surface.
        lineage=Lineage(derived_from=list(prerequisites or [])),
    )


# --------------------------------------------------------------------------- #
# L4 — OnboardingPath / OnboardingStep: ordered slug refs, NOT a Surface
# --------------------------------------------------------------------------- #


class OnboardingStep(BaseModel):
    """One step in an onboarding track: a slug ref to an already-gated surface.

    ``slug`` is required (the cross-link key resolved at render time via ``Site.by_slug``);
    ``label`` is an optional caller-supplied label — it defaults to ``""``, in which case
    ``render_path()`` (Plan 04) resolves the human title from the target page.
    """

    slug: str
    label: str = ""


class OnboardingPath(BaseModel):
    """An ORDERED learning track: a sequence of :class:`OnboardingStep` slug refs.

    This is NAVIGATION over surfaces that ALREADY passed the review gate — it is **not** a
    ``Surface``: it carries no claims and **no own review gate / publish()** (it publishes
    nothing new, so the no-auto-publish invariant is not implicated — A5). The ``steps``
    list ORDER is the track order (prev/next). ``render_path()`` is Plan 04.
    """

    id: str
    title: str
    audience_label: str = "A new contributor"
    steps: list[OnboardingStep] = Field(default_factory=list)
