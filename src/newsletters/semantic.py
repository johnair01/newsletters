"""The typed semantic model — the spine of Newsletters.

Implements ``architecture.md §1``: ``Source`` is distilled into a ``Distillation``,
which renders per-``Corpus`` into a ``Surface`` gated by a ``Review``.

    Source ──distill──▶ Distillation ──render(kind, Corpus)──▶ Surface
      ▲                      │                                    │
      └────── traces ────────┴──────── Review gate ───────────────┘

The three architectural invariants are enforced *in code*, not just documented:

1. A ``Surface`` may not reach ``Published`` without a ``Review`` whose state is
   ``Published`` and a recorded ``reviewer``. There is no auto-publish path.
2. Every ``Claim`` in a *published* ``Distillation`` has at least one ``Trace``.
   Unsubstantiated material lives in ``missing`` and blocks nothing, but is shown
   to the reviewer.
3. A ``Corpus`` is never serialized into a ``Surface`` or a ``Source``. Personalization
   reads it at render time; the output carries emphasis, not the corpus.

The agentic ``distill()`` step (the one LLM boundary) is intentionally **not**
implemented here — it lands in Phase 4. This module is the typed, auditable data
model plus the package-API surface around it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Surface kinds and the review gate
# --------------------------------------------------------------------------- #


class SurfaceKind(StrEnum):
    """The four reader-facing surfaces one record fans out into."""

    SHOW = "show"
    NEWSLETTER = "newsletter"
    ARTICLE = "article"
    REPORT = "report"


class ReviewState(StrEnum):
    """The human-in-the-loop publish gate: ``Draft › InReview › Published``."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"


# --------------------------------------------------------------------------- #
# Evidence atoms
# --------------------------------------------------------------------------- #


class Source(BaseModel):
    """A record of something that happened. Embeddings power semantic search."""

    id: str = Field(..., description="Stable identifier for the event/source record")
    timestamp: datetime = Field(default_factory=_utcnow)
    context: str = Field("", description="Where this came from / surrounding situation")
    transcript: str = Field("", description="The raw material distilled from")
    embeddings: Optional[list[float]] = Field(
        default=None, description="Vector embedding; populated by the index, optional here"
    )


class Trace(BaseModel):
    """A pointer from a claim to its evidence: a ``Source`` and a location within it."""

    source_id: str = Field(..., description="Id of the Source this claim rests on")
    locator: str = Field(
        "", description="Where in the source (line range, span, timestamp, …)"
    )


class Claim(BaseModel):
    """The atom of auditability: a statement, its evidence, and a confidence."""

    text: str
    evidence: list[Trace] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)

    @property
    def is_traced(self) -> bool:
        return len(self.evidence) > 0


# --------------------------------------------------------------------------- #
# Reader profile (personalization) — local, encrypted, never serialized out
# --------------------------------------------------------------------------- #


class Corpus(BaseModel):
    """A reader's private profile. **Local and encrypted; never leaves the operator's env.**

    Drives personalization at render time. Per invariant 3 it is never embedded into a
    ``Surface`` or ``Source`` — ``render`` reads it to weight emphasis and discards it.
    """

    name: str
    role: str = ""
    owned: list[str] = Field(default_factory=list, description="Services/areas this reader owns")
    read: list[str] = Field(default_factory=list, description="Surface ids already seen")
    weights: dict[str, float] = Field(default_factory=dict, description="Topic emphasis")

    @classmethod
    def load(cls, name: str) -> "Corpus":
        """Load a reader/audience profile from local config.

        Phase 5 wires this to encrypted on-disk corpora. Until then it returns a
        minimal named profile so the package API is callable end to end.
        """
        return cls(name=name)


# --------------------------------------------------------------------------- #
# Review gate
# --------------------------------------------------------------------------- #


class Review(BaseModel):
    """The gate that governs publication. ``reviewer`` is required to publish."""

    state: ReviewState = ReviewState.DRAFT
    reviewer: Optional[str] = None
    pr_url: Optional[str] = None
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _published_requires_reviewer(self) -> "Review":
        # Invariant 1 (gate side): you cannot record a Published review with no reviewer.
        if self.state is ReviewState.PUBLISHED and not self.reviewer:
            raise ValueError(
                "A Published review requires a recorded reviewer — no auto-publish path."
            )
        return self


# --------------------------------------------------------------------------- #
# Distillation — the agent's synthesis
# --------------------------------------------------------------------------- #


class Distillation(BaseModel):
    """The synthesis of one or more ``Source`` records for a target ``Corpus``.

    Every published claim must be traced; whatever could not be substantiated lives in
    ``missing`` and is surfaced to the reviewer rather than published silently.
    """

    claims: list[Claim] = Field(default_factory=list)
    narrative: str = ""
    audience: Optional[Corpus] = Field(
        default=None, description="Whom this was distilled for (read at render time only)"
    )
    missing: list[str] = Field(
        default_factory=list, description="What the agent could not substantiate"
    )
    traces: list[Source] = Field(
        default_factory=list, description="The source records this distillation rests on"
    )

    @property
    def untraced_claims(self) -> list[Claim]:
        return [c for c in self.claims if not c.is_traced]

    def render(self, kind: SurfaceKind | str, audience: Optional[Corpus] = None) -> "Surface":
        """Produce a specific ``Surface`` from this synthesis, re-cut for ``audience``.

        Enforces invariant 2: a published-quality surface cannot be rendered while
        untraced claims remain — they must be moved to ``missing`` first. The surface
        starts in ``Draft`` and never embeds the ``Corpus`` (invariant 3).
        """
        kind = SurfaceKind(kind)
        corpus = audience or self.audience
        if self.untraced_claims:
            offenders = ", ".join(repr(c.text[:40]) for c in self.untraced_claims)
            raise ValueError(
                "Cannot render a surface with untraced claims; move them to `missing` "
                f"first. Untraced: {offenders}"
            )
        body = self._compose_body(kind, corpus)
        return Surface(
            kind=kind,
            body=body,
            review=Review(state=ReviewState.DRAFT),
            traces=list(self.traces),
        )

    def _compose_body(self, kind: SurfaceKind, corpus: Optional[Corpus]) -> str:
        """Deterministic placeholder composition.

        Real per-surface rendering (matching `surfaces.md`) lands in Phase 3. This keeps
        the pipeline runnable end to end and reads `corpus` for emphasis *without*
        serializing it into the output (invariant 3).
        """
        lead = self.narrative.strip()
        if corpus and corpus.weights:
            # Reorder claims by the reader's topic weights — emphasis, not content.
            def weight(claim: Claim) -> float:
                return max((corpus.weights.get(w, 0.0) for w in corpus.weights), default=0.0)

            ordered = sorted(self.claims, key=weight, reverse=True)
        else:
            ordered = self.claims
        lines = [f"# {kind.value.title()}", "", lead, ""]
        lines += [f"- {c.text}" for c in ordered]
        return "\n".join(lines).strip()


# --------------------------------------------------------------------------- #
# Surface — the published artifact + its gate
# --------------------------------------------------------------------------- #


class Surface(BaseModel):
    """A reader-facing artifact and the review state that gates it.

    Invariant 3 is enforced structurally: a ``Surface`` has no ``Corpus`` field, so a
    corpus can never be serialized into one.
    """

    model_config = ConfigDict(validate_assignment=True)

    kind: SurfaceKind
    body: str = ""
    review: Review = Field(default_factory=Review)
    traces: list[Source] = Field(default_factory=list)

    @property
    def gate(self) -> ReviewState:
        """The current gate state of this surface."""
        return self.review.state

    @property
    def is_published(self) -> bool:
        return self.review.state is ReviewState.PUBLISHED

    def open_pull_request(self, pr_url: Optional[str] = None) -> "Surface":
        """Drive the review loop: move the draft into review as a real PR.

        Merging that PR (a human action) is what publishes — see ``publish``.
        """
        self.review = Review(
            state=ReviewState.IN_REVIEW,
            reviewer=self.review.reviewer,
            pr_url=pr_url or self.review.pr_url,
            notes=list(self.review.notes),
        )
        return self

    def publish(self, reviewer: str) -> "Surface":
        """Publish the surface. Requires a ``reviewer`` — invariant 1, no auto-publish.

        A real deployment reaches this only on PR merge; the ``reviewer`` is the human
        who approved it.
        """
        if not reviewer:
            raise ValueError("publish() requires a reviewer — no auto-publish path exists.")
        self.review = Review(
            state=ReviewState.PUBLISHED,
            reviewer=reviewer,
            pr_url=self.review.pr_url,
            notes=list(self.review.notes),
        )
        return self


# --------------------------------------------------------------------------- #
# Package API (architecture.md §2)
# --------------------------------------------------------------------------- #


def synthesize(
    event: str,
    sources: list[str],
    audience: Corpus,
) -> Distillation:
    """Ingest + distill in one call — the advertised public API.

    The agentic distillation (the one LLM boundary) lands in Phase 4. This is the typed
    entrypoint and contract; calling it today raises rather than fabricating untraced
    claims, which would violate the auditability guarantee.
    """
    raise NotImplementedError(
        "synthesize() — the agentic distill step — is implemented in Phase 4 "
        "(see docs/roadmap.md). The typed model, the review gate, and render() are "
        "live now; distillation over a real Source is the next phase."
    )
