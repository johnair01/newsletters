"""The typed semantic model — the spine of Newsletters (Rev1).

Implements the two-layer model we settled on:

* **Truth layer** — what is real, and its evidence:
  ``Source → Claim(+Trace) → Distillation``. One reviewed record.
* **Surface layer** — how a truth is presented: a ``Surface`` is a
  ``SurfaceTemplate`` (the parameterized shape — see ``templates.py``) bound to a
  ``Distillation`` and rendered into typed content ``blocks``, gated by a ``Review``.

Three invariants are enforced *in code*:

1. A ``Surface`` cannot publish without satisfying its template's ``ReviewPolicy``
   (a recorded approval; for peer-reviewed surfaces, an approver who is not the
   author). There is no auto-publish path.
2. Every ``Claim`` rendered into a *published* surface has at least one ``Trace``.
   Unsubstantiated material lives in ``missing`` and is shown to the reviewer.
3. The private ``Corpus`` (its ``weights`` / ``read`` / ``owned``) is never
   serialized into a ``Surface`` or ``Source``. Personalization reads it at render
   time; the output carries *emphasis*, not the corpus.

The agentic *problem-solving* step is **external** to Newsletters (operator-owned;
see ``capture.py``). What this module models is the capture, the trust, and the
publish — agent-agnostic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .templates import ReviewPolicy, SignalColor, SurfaceTemplate


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Truth layer — evidence atoms
# --------------------------------------------------------------------------- #


class Source(BaseModel):
    """A record of something that happened — the raw material a Report is built from."""

    id: str
    timestamp: datetime = Field(default_factory=_utcnow)
    context: str = Field("", description="Where this came from (tool, system, channel)")
    transcript: str = Field("", description="The raw material distilled from")
    embeddings: Optional[list[float]] = None


class Trace(BaseModel):
    """A pointer from a claim to its evidence: a ``Source`` and a locator within it."""

    source_id: str
    locator: str = ""


class Claim(BaseModel):
    """The atom of auditability: a statement, its evidence, and a confidence."""

    text: str
    evidence: list[Trace] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    topics: list[str] = Field(default_factory=list, description="For personalization weighting")

    @property
    def is_traced(self) -> bool:
        return len(self.evidence) > 0


# --------------------------------------------------------------------------- #
# Reader profile — private, never serialized out (invariant 3)
# --------------------------------------------------------------------------- #


class Corpus(BaseModel):
    """A reader's **private** profile. Local and encrypted; never leaves the operator's env.

    Drives personalization at render time. Its private fields (``weights`` / ``read`` /
    ``owned``) are never embedded in a ``Surface`` or ``Source``.
    """

    name: str
    role: str = ""
    initials: str = ""
    owned: list[str] = Field(default_factory=list)
    read: list[str] = Field(default_factory=list)
    weights: dict[str, float] = Field(default_factory=dict)

    @classmethod
    def load(cls, name: str) -> "Corpus":
        """Load a reader profile from local config (Phase 5 wires encrypted on-disk corpora)."""
        return cls(name=name)

    def emphasis(self, claim: "Claim") -> float:
        """How strongly this reader cares about a claim — read at render time, then discarded."""
        if not self.weights:
            return 0.0
        return max((self.weights.get(t, 0.0) for t in claim.topics), default=0.0)


# --------------------------------------------------------------------------- #
# Review gate — policy carried per template (Report = light, Article = peer)
# --------------------------------------------------------------------------- #


class ReviewState(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"


class Review(BaseModel):
    """The gate that governs publication, against the template's ``ReviewPolicy``."""

    state: ReviewState = ReviewState.DRAFT
    policy: ReviewPolicy = Field(default_factory=ReviewPolicy)
    author: Optional[str] = None
    approvals: list[str] = Field(default_factory=list)
    pr_url: Optional[str] = None
    notes: list[str] = Field(default_factory=list)

    @property
    def reviewer(self) -> Optional[str]:
        """The approving reviewer (last approval), if any."""
        return self.approvals[-1] if self.approvals else None

    def satisfied(self) -> bool:
        """Does the recorded approval set satisfy the policy?"""
        if len(self.approvals) < self.policy.min_approvals:
            return False
        if self.policy.require_peer and not any(a != self.author for a in self.approvals):
            return False
        return True

    @model_validator(mode="after")
    def _published_requires_satisfied_policy(self) -> "Review":
        if self.state is ReviewState.PUBLISHED and not self.satisfied():
            raise ValueError(
                "Cannot be Published: the review policy is not satisfied "
                f"(need {self.policy.describe()}; have approvals={self.approvals!r}, "
                f"author={self.author!r}). No auto-publish path."
            )
        return self


# --------------------------------------------------------------------------- #
# Distillation — the synthesis (truth), the thing a Surface renders
# --------------------------------------------------------------------------- #


class Distillation(BaseModel):
    """The synthesis of a work session's ``Source`` records into traced claims."""

    narrative: str = ""
    claims: list[Claim] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    traces: list[Source] = Field(default_factory=list)
    # The intended default audience is referenced by name only — the private Corpus
    # is passed to render() and never stored here (invariant 3).
    audience_name: Optional[str] = None

    @property
    def untraced_claims(self) -> list[Claim]:
        return [c for c in self.claims if not c.is_traced]

    def claims_for(self, audience: Optional[Corpus]) -> list[Claim]:
        """Claims ordered by a reader's emphasis — same facts, new emphasis."""
        if audience is None:
            return list(self.claims)
        return sorted(self.claims, key=audience.emphasis, reverse=True)


# --------------------------------------------------------------------------- #
# Content blocks — the typed "slots" a surface is composed of
# --------------------------------------------------------------------------- #


class KpiItem(BaseModel):
    label: str
    value: str
    delta: Optional[str] = None
    dir: Optional[Literal["up", "down"]] = None


class Chapter(BaseModel):
    time: str
    title: str
    body: str = ""


class LetterItem(BaseModel):
    tag: Optional[str] = None
    title: str
    body: str = ""


class FanoutLink(BaseModel):
    kind: str  # report / article / newsletter / show
    title: str
    href: Optional[str] = None


class ProseBlock(BaseModel):
    kind: Literal["prose"] = "prose"
    heading: Optional[str] = None
    text: str = ""


class ClaimsBlock(BaseModel):
    kind: Literal["claims"] = "claims"
    heading: Optional[str] = "Findings — every claim traced"
    claims: list[Claim] = Field(default_factory=list)


class KpiStripBlock(BaseModel):
    kind: Literal["kpi"] = "kpi"
    heading: Optional[str] = None
    items: list[KpiItem] = Field(default_factory=list)


class QuoteBlock(BaseModel):
    kind: Literal["quote"] = "quote"
    text: str
    attr: Optional[str] = None


class ChaptersBlock(BaseModel):
    kind: Literal["chapters"] = "chapters"
    heading: Optional[str] = "Chapters"
    chapters: list[Chapter] = Field(default_factory=list)


class ItemsBlock(BaseModel):
    kind: Literal["items"] = "items"
    heading: Optional[str] = None
    items: list[LetterItem] = Field(default_factory=list)


class PromptBlock(BaseModel):
    kind: Literal["prompt"] = "prompt"
    label: str = "shell"
    body: str = ""


class FanoutBlock(BaseModel):
    kind: Literal["fanout"] = "fanout"
    heading: Optional[str] = "What this produced"
    links: list[FanoutLink] = Field(default_factory=list)


class RationaleBlock(BaseModel):
    kind: Literal["rationale"] = "rationale"
    heading: Optional[str] = "Why you're seeing this"
    text: str = ""


class DiagramBlock(BaseModel):
    """An inline SVG diagram — renders the story visually, theming with the page."""

    kind: Literal["diagram"] = "diagram"
    title: Optional[str] = None
    svg: str = ""
    caption: Optional[str] = None


Block = Annotated[
    Union[
        ProseBlock,
        ClaimsBlock,
        KpiStripBlock,
        QuoteBlock,
        ChaptersBlock,
        ItemsBlock,
        PromptBlock,
        FanoutBlock,
        RationaleBlock,
        DiagramBlock,
    ],
    Field(discriminator="kind"),
]


# --------------------------------------------------------------------------- #
# Provenance & lineage — tracking the process (agent-agnostic)
# --------------------------------------------------------------------------- #


class Provenance(BaseModel):
    """How a surface was captured. The *tool* is metadata — Newsletters is agnostic to it."""

    tool: str = "unknown"
    session_id: Optional[str] = None
    artifacts: list[str] = Field(default_factory=list)
    captured_at: datetime = Field(default_factory=_utcnow)


class Lineage(BaseModel):
    """Fan-out: what this surface was derived from, and what it produced."""

    derived_from: list[str] = Field(default_factory=list)
    produced: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Surface — a template bound to a truth, rendered into blocks, gated by a review
# --------------------------------------------------------------------------- #


class Surface(BaseModel):
    """A reader-facing artifact: ``template`` + composed ``blocks`` + the ``Review`` gate.

    Holds no ``Corpus`` and no ``Distillation`` object — only an ``audience_label`` string
    and the rendered blocks/claims — so a private corpus can never be serialized into it
    (invariant 3).
    """

    model_config = ConfigDict(validate_assignment=True)

    id: str
    template: SurfaceTemplate
    title: str
    eyebrow: str = ""
    blocks: list[Block] = Field(default_factory=list)
    traces: list[Source] = Field(default_factory=list)
    audience_label: Optional[str] = None
    byline: list[str] = Field(default_factory=list)
    review: Review = Field(default_factory=Review)
    provenance: Optional[Provenance] = None
    lineage: Lineage = Field(default_factory=Lineage)
    created: datetime = Field(default_factory=_utcnow)

    # -- gate helpers --------------------------------------------------------
    @property
    def kind(self) -> str:
        return self.template.name

    @property
    def signal_color(self) -> SignalColor:
        return self.template.signal_color

    @property
    def gate(self) -> ReviewState:
        return self.review.state

    @property
    def is_published(self) -> bool:
        return self.review.state is ReviewState.PUBLISHED

    def _published_claims(self) -> list[Claim]:
        out: list[Claim] = []
        for b in self.blocks:
            if isinstance(b, ClaimsBlock):
                out.extend(b.claims)
        return out

    def open_pull_request(self, pr_url: Optional[str] = None) -> "Surface":
        """Move the draft into review as a real PR (invariant 2 enforced here)."""
        untraced = [c for c in self._published_claims() if not c.is_traced]
        if untraced:
            offenders = ", ".join(repr(c.text[:40]) for c in untraced)
            raise ValueError(
                f"Cannot open a review with untraced claims; move them to `missing`. "
                f"Untraced: {offenders}"
            )
        self.review = self.review.model_copy(
            update={"state": ReviewState.IN_REVIEW, "pr_url": pr_url or self.review.pr_url}
        )
        return self

    def approve(self, reviewer: str) -> "Surface":
        """Record an approval against the gate. Does not itself publish."""
        if not reviewer:
            raise ValueError("approve() requires a reviewer.")
        self.review = self.review.model_copy(
            update={"approvals": [*self.review.approvals, reviewer]}
        )
        return self

    def publish(self, reviewer: Optional[str] = None) -> "Surface":
        """Publish — only if the template's ``ReviewPolicy`` is satisfied. No auto-publish.

        ``reviewer`` is a convenience: it records one approval, then publishes. For a
        peer-reviewed surface (the Article), the approver must differ from the author.
        """
        approvals = list(self.review.approvals)
        if reviewer:
            approvals.append(reviewer)
        candidate = self.review.model_copy(
            update={"state": ReviewState.PUBLISHED, "approvals": approvals}
        )  # validator raises if policy unsatisfied
        self.review = candidate
        return self


# --------------------------------------------------------------------------- #
# Package API (architecture.md §2) — the agentic distill stays external (Phase 4)
# --------------------------------------------------------------------------- #


def synthesize(event: str, sources: list[str], audience: Corpus) -> Distillation:
    """Ingest + LLM-distill in one call — the advertised public API.

    The *agentic* distillation is an external, operator-owned problem-solving step
    (Phase 4). Deterministic capture of a finished work session is real today —
    see ``newsletters.capture.capture_session``. This entrypoint refuses rather than
    fabricating untraced claims.
    """
    raise NotImplementedError(
        "synthesize() — the agentic (LLM) distill step — is external/Phase 4. "
        "Deterministic capture of a finished session is available now via "
        "newsletters.capture.capture_session()."
    )
