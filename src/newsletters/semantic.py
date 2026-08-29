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

import hashlib
from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# A separate import statement ON PURPOSE (WR-02, 03-review): this phase's semantic.py changes
# are policed by an insertion-only diff gate (test_semantic_gate_frozen.py, Half B) — extending
# the line above would register as a rewrite of an existing line, so the widening is appended.
from pydantic import ValidationInfo

from .locators import ExtractionRecord, FreeLocator, Locator
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
    # The TYPED coverage carrier (R1, TASK ZERO). An adapter records, at parse() time, the raw
    # content it could NOT faithfully extract (its ``unextracted[]`` determination) HERE, so the
    # determination travels WITH the Source through ``model_dump_json``. A fresh adapter
    # re-``distill()``ing a persisted Source reconstructs the SAME coverage — "no silent drops"
    # holds across persistence, not just same-instance. Defaults to ``None`` so every Rev1/Phase-4
    # Source (which has no ``extraction`` key) still validates and round-trips natively.
    # NOTE: excluded from ``content_hash()`` (see below) — it is metadata ABOUT extraction, not the
    # addressed content; preserving the hash keeps every existing Trace addressed and non-stale.
    extraction: Optional[ExtractionRecord] = Field(
        default=None,
        description="Adapter coverage carrier (R1): the unextracted[] determination, carried "
        "with the Source so coverage survives a JSON round-trip. NOT in content_hash().",
    )

    def content_hash(self) -> str:
        """The SHA-256 hex digest of the FULL source content (``transcript``), stdlib only (D-1).

        This is the content-address a ``Trace`` pins at capture time. STALE is computed by
        comparing this *live* digest against the digest the Trace recorded — see
        ``Trace.is_stale_against``. Deterministic: an empty transcript hashes to the SHA-256
        of the empty byte string, no special-casing. No AI, no new dependency.

        Addresses ``transcript`` ONLY: the ``extraction`` coverage carrier is deliberately
        excluded — it is metadata about *what an adapter dropped*, not the content being
        addressed. Folding it in would re-key every existing Trace and falsely mark them stale.
        """
        return hashlib.sha256(self.transcript.encode("utf-8")).hexdigest()


class Trace(BaseModel):
    """A pointer from a claim to its evidence: a ``Source`` and a locator within it.

    ``locator`` is a typed ``Locator`` discriminated union (D-06). A bare ``str`` still
    coerces to ``FreeLocator(text=...)`` so the Rev1 capture path (``capture.py``) and
    existing tests stay green — the widening is backward-compatible. ``span`` carries the
    verbatim source snippet so "faithful, not suggestive" is *visible* at draft time (D-06).
    """

    source_id: str
    locator: Locator = Field(default_factory=FreeLocator)
    span: str = ""
    # --- content-address fields (D-1, OPTIONAL for backward-compat D-4) ----------
    # These pin a Trace to the *content* of its Source, not a fragile position. They
    # default to None so every Rev1 Trace (and the bare-string-locator coercion path)
    # stays valid. A Trace with content_hash=None is "un-addressed" (``is_addressed``
    # is False) and can never be STALE — it was never pinned.
    content_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hex digest of the FULL Source content at capture time (D-1).",
    )
    start: Optional[int] = Field(
        default=None, description="Character offset (inclusive) of the span in Source.transcript."
    )
    end: Optional[int] = Field(
        default=None, description="Character offset (exclusive) of the span in Source.transcript."
    )

    @field_validator("locator", mode="before")
    @classmethod
    def _coerce_locator(cls, v: object) -> object:
        """Coerce a bare ``str`` into ``FreeLocator(text=...)``; pass everything else through.

        Idempotent: a ``FreeLocator``/``SessionLocator`` instance, or a discriminator dict
        like ``{"kind": "free", "text": ...}``, passes through UNCHANGED (no double-wrap).
        """
        if isinstance(v, str):
            return FreeLocator(text=v)
        return v

    @classmethod
    def from_source(
        cls,
        source: "Source",
        start: int,
        end: int,
        *,
        locator: Optional[Locator] = None,
    ) -> "Trace":
        """Mint a content-addressed, self-verifying Trace from a live Source (D-1).

        Pins ``content_hash = source.content_hash()``, the character ``start``/``end``
        window, and ``span = source.transcript[start:end]`` so the stored span is
        re-checkable against the offset window of the live source. This is the SINGLE
        constructor later phases (the adapters, Plan 02's migration) use to mint
        content-addressed traces — the pinning logic lives here and nowhere else.

        Offsets are validated BEFORE slicing — faithful, not suggestive: a bad range
        is refused with a teaching ValueError rather than silently clipped to an empty
        or truncated span.
        """
        n = len(source.transcript)
        if start < 0:
            raise ValueError(
                f"Trace.from_source: start={start} is negative; offsets are character "
                f"positions into a {n}-char transcript and must be >= 0."
            )
        if end < start:
            raise ValueError(
                f"Trace.from_source: end={end} is before start={start}; the span window "
                "is inverted. Pass start <= end."
            )
        if end > n:
            raise ValueError(
                f"Trace.from_source: end={end} runs past the transcript length ({n}); "
                "refusing to clip rather than silently mis-attribute."
            )
        return cls(
            source_id=source.id,
            locator=locator if locator is not None else FreeLocator(),
            span=source.transcript[start:end],
            content_hash=source.content_hash(),
            start=start,
            end=end,
        )

    @property
    def is_addressed(self) -> bool:
        """True iff this Trace pinned a content hash (i.e. was minted content-addressed)."""
        return self.content_hash is not None

    def is_stale_against(self, source: "Source") -> bool:
        """STALE is COMPUTED (D-2): the live source hash != the hash this Trace recorded.

        An un-addressed Trace (``content_hash is None``) is NEVER stale — it was never
        pinned, so there is nothing to drift against. This refuses a false positive and
        never raises on the Rev1 path.
        """
        return self.is_addressed and source.content_hash() != self.content_hash


class Claim(BaseModel):
    """The atom of auditability: a statement, its evidence, and a confidence."""

    text: str
    evidence: list[Trace] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    topics: list[str] = Field(default_factory=list, description="For personalization weighting")

    @property
    def is_traced(self) -> bool:
        return len(self.evidence) > 0

    def is_stale(self, sources: dict[str, "Source"]) -> bool:
        """STALE is COMPUTED (D-2): True iff ANY trace is stale against its live source.

        ``sources`` is a ``{source_id: Source}`` lookup. A trace whose ``source_id`` is
        absent from the lookup is skipped (not raised) — we cannot judge drift without
        the live source, so we never claim a false STALE. Un-addressed traces are never
        stale (see ``Trace.is_stale_against``).
        """
        return any(
            t.is_stale_against(sources[t.source_id])
            for t in self.evidence
            if t.source_id in sources
        )


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

    def stale_claims(self, sources: Optional[dict[str, "Source"]] = None) -> list["Claim"]:
        """The claims that have drifted from their evidence — STALE is COMPUTED (D-2).

        When ``sources`` is None the lookup is built from this Distillation's own
        ``traces`` (the ``Source[]`` it carries), so a self-contained Distillation can
        report its own drift. Returns ``[]`` when nothing drifted. No stored stale flag
        anywhere — this is recomputed from live source hashes every call.
        """
        lookup = sources if sources is not None else {s.id: s for s in self.traces}
        return [c for c in self.claims if c.is_stale(lookup)]

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


class NarrativeItem(BaseModel):
    """One authored highlight/lowlight line, plus the traced ``Claim`` carrying that same text.

    ``text`` is what the author typed, byte-verbatim — the composer never summarises, reorders
    or merges lines (``docs/weekly-spec.md`` rule 3). ``claim`` is that identical text minted as
    a traced ``Claim``, so the rendered line and its evidence cannot drift apart. It is
    ``Optional`` because a line may be carried before (or without) a mintable span; an untraced
    line is disclosed, never dressed up as sourced.
    """

    text: str
    claim: Optional[Claim] = None


class Recognition(BaseModel):
    """Credit for one person, in the author's words — carried with or without a source.

    ``evidence`` deliberately defaults to EMPTY and may legitimately stay empty
    (``docs/weekly-spec.md`` rule 6): when no ``source:`` was authored, the author's own word is
    the evidence, traced to a real span of the spec file, and the absent external evidence is
    disclosed in ``Surface.missing[]``. Both halves matter — dropping the recognition would erase
    credit, and publishing it as if sourced would be a lie. This is the deliberate CONTRAST to
    ``AssetBlock.evidence`` (``min_length=1``): a recognition without a source is still credit
    owed; an asset without a trace is a picture nobody vouched for.
    """

    person: str
    reason: str
    evidence: list[Trace] = Field(default_factory=list)


class TeamMember(BaseModel):
    """One member of the module this week: their name, role, authored lines and photo KEY.

    ``photo`` holds an ``assets:`` mapping key, never a file path, so a team photo goes through
    the same provenance routing as every other placed image instead of around it. A key that
    names no placed asset is a ``missing[]`` disclosure: the member and their lines are carried,
    the photo is not (``docs/weekly-spec.md`` §"The routing").
    """

    name: str
    role: str = ""
    lines: list[str] = Field(default_factory=list)
    photo: Optional[str] = None


class AssetRecord(BaseModel):
    """A content-addressed file plus its provenance. A missing minimum ⇒ ``missing[]``, not a slide.

    Why the RECORD is the evidence and not the image: ``Source.transcript`` is a ``str`` and
    ``Source.content_hash()`` hashes that string, so an image can never itself be a ``Source``.
    Instead the record text is the source, and the image's identity lives inside it as the
    ``sha256`` hex string — a literal substring of the record, so it traces verbatim like any
    other field via ``Trace.from_source`` and the span-containment gate keeps its teeth over the
    provenance claims.

    ``folder`` / ``date`` / ``event`` are the provenance minimum (decision D-02). ``link`` is
    REQUIRED iff ``stands_in_for == "values"`` — a screenshot standing in for numbers must point
    at the report those numbers came from. ``stands_in_for`` is AUTHOR-DECLARED and never
    inferred from a filename, a folder or the image: inferring it would be the composer forming
    an opinion about content, which faithful-not-suggestive forbids. Those two conditional rules
    are the loader's to enforce (they depend on values, not shape); the shape below is what the
    type can carry.
    """

    key: str
    file: str
    sha256: str
    folder: str
    date: str
    event: str
    link: Optional[str] = None
    stands_in_for: Optional[Literal["values"]] = None
    caption: Optional[str] = None
    alt: Optional[str] = None

    # WR-02 (03-review): the docstring above claims a provenance-less asset is UNREPRESENTABLE,
    # but a bare ``str`` annotation enforces presence, not non-emptiness — the review proved
    # ``AssetRecord(..., folder="", date="", event="")`` constructed fine, leaving the whole
    # D-02 claim to one loader-side ``.strip()`` check any other code path (a future composer,
    # a hand-built Surface, a tampered JSON round-trip) could bypass. These two validators make
    # the claim true at the TYPE level, in every code path, both directions tested.
    @field_validator("key", "file", "sha256", "folder", "date", "event")
    @classmethod
    def _required_provenance_is_non_blank(cls, value: str, info: ValidationInfo) -> str:
        if not value.strip():
            raise ValueError(
                f"AssetRecord.{info.field_name} must be non-blank: it is part of the record "
                "that vouches for the placed file (decision D-02 — provenance-less placement "
                "is unrepresentable at the type level, never merely policed at load time). "
                "An absent minimum belongs in missing[], not blanked onto a record."
            )
        return value

    @field_validator("link", "caption", "alt")
    @classmethod
    def _optional_text_is_none_or_real(
        cls, value: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError(
                f"AssetRecord.{info.field_name} is optional but may not be a BLANK string: "
                "pass None for an absent value. An empty string is neither authored text nor "
                "a disclosed absence — it would render as content that asserts nothing."
            )
        return value


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


class GlossaryTerm(BaseModel):
    """A glossary entry: a term mapped to its DEFINING reviewed, traced ``Claim``.

    Faithfulness enforced *by the type*: ``definition`` is a ``Claim`` (carrying
    ``evidence: list[Trace]``), never a bare ``str``. The defining claim's evidence IS the
    definition — a term cannot be glossed with invented prose, only with a reviewed claim
    that points back to its source. A term with no traceable defining claim is NOT glossed
    here; the learning preset routes it to ``surface.missing[]`` (the honesty panel), never
    a fabricated string. This is the LEARN-01 faithfulness crux, locked at construction time.
    """

    term: str
    definition: Claim


class GlossaryBlock(BaseModel):
    """An in-context glossary block — each term traced to its defining ``Claim``.

    A valid Surface block (its ``kind`` discriminator is ``"glossary"``), so it round-trips
    through the typed ``Block`` union. Holds only ``GlossaryTerm``s, so every definition is a
    traced claim by construction. The render branch is deliberately NOT here (that is Plan 04).
    """

    kind: Literal["glossary"] = "glossary"
    heading: Optional[str] = "Glossary — every term traced to its definition"
    terms: list[GlossaryTerm] = Field(default_factory=list)


class NarrativeBlock(BaseModel):
    """Authored highlights / lowlights — the author's voice, never summarized.

    One block per tone, so a weekly's highlights and its lowlights are separately addressable
    (and a weekly with NO lowlights discloses that absence rather than hiding it behind a merged
    block). The composer carries ``NarrativeItem.text`` byte-verbatim: emphasis and narrative are
    the human's job (``docs/weekly-spec.md`` rule 3).
    """

    kind: Literal["narrative"] = "narrative"
    heading: Optional[str] = None
    tone: Literal["highlight", "lowlight"] = "highlight"
    items: list[NarrativeItem] = Field(default_factory=list)


class RecognitionsBlock(BaseModel):
    """Credit where it is owed — one entry per person, sourced or not.

    See ``Recognition``: an entry with empty ``evidence`` is legal by design and its absent
    source is disclosed, because dropping the recognition would erase the credit.
    """

    kind: Literal["recognitions"] = "recognitions"
    heading: Optional[str] = "Recognitions"
    recognitions: list[Recognition] = Field(default_factory=list)


class TeamBlock(BaseModel):
    """Who the module is, this week."""

    kind: Literal["team"] = "team"
    heading: Optional[str] = "The team"
    members: list[TeamMember] = Field(default_factory=list)


class AssetBlock(BaseModel):
    """One placed asset. It is here ONLY because its provenance record was complete.

    Faithfulness enforced *by the type*, the same move ``GlossaryTerm.definition: Claim`` makes:

    - ``asset`` is REQUIRED with no default. There is no ``AssetBlock`` without an
      ``AssetRecord``, and no ``AssetRecord`` without its provenance minimums — so "an asset
      without provenance reached a ``Surface``" is *unrepresentable* rather than merely policed
      by a check somebody can forget to call.
    - ``evidence`` carries ``min_length=1``. An ``AssetBlock`` with zero traces fails Pydantic
      validation at construction, so a code path that tries to place a picture nobody vouched for
      gets a teaching ``ValidationError`` naming the empty field, never a traceless block on a
      surface. The loader satisfies the minimum by minting the trace into the asset record at
      placement time.

    This is the type-level half of decision **D-02**. Note the deliberate contrast with
    ``Recognition.evidence``, which may legitimately be empty (``docs/weekly-spec.md`` rule 6).
    """

    kind: Literal["asset"] = "asset"
    heading: Optional[str] = None
    asset: AssetRecord
    caption: Optional[str] = None
    evidence: list[Trace] = Field(min_length=1)

    # WR-02 (03-review), the same move as ``AssetRecord`` above: ``heading`` (the authored
    # ``alt``) and ``caption`` are legitimately optional, but a PRESENT empty string is neither
    # authored text nor a disclosed absence — blank stays unrepresentable in either shape.
    @field_validator("heading", "caption")
    @classmethod
    def _optional_text_is_none_or_real(
        cls, value: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError(
                f"AssetBlock.{info.field_name} is optional but may not be a BLANK string: "
                "pass None for an absent value. An empty string is neither authored text nor "
                "a disclosed absence — it would render as content that asserts nothing."
            )
        return value


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
        GlossaryBlock,
        NarrativeBlock,
        RecognitionsBlock,
        TeamBlock,
        AssetBlock,
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
    # The PROV-03 carrier (L1): the surface-level mirror of ``Distillation.missing``. Carries the
    # unsubstantiated/un-entailed material that must be SHOWN to the reviewer, populated at the
    # capture/promote seam in a later plan. OPTIONAL and additive — defaults to ``[]`` so every
    # existing Surface (which has no ``missing`` key) still validates and round-trips, mirroring the
    # optional-additive style of ``Source.extraction`` (above). It carries PLAIN STRINGS ONLY — never
    # a Corpus / Source / Distillation object — so invariant 3 (private corpus never serialized) is
    # preserved, and it does NOT touch the publish/review gate (the carrier is pure).
    missing: list[str] = Field(
        default_factory=list,
        description="PROV-03 carrier: unsubstantiated material to show the reviewer. Additive, "
        "invariant-3-safe (str entries only); does not alter the publish gate.",
    )
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
            # WR-03 (03-review): NarrativeBlock items carry real published claims too — the
            # weekly's highlights/lowlights. Invariant 2 inspects every claim CARRIER, not one
            # block kind of the four; an item whose claim is None was disclosed to missing[]
            # at load time and stays a disclosure, never dressed up as a claim here.
            # (AssetBlock carries bare Traces whose >=1 minimum the type enforces; its drift
            # check lives in review.review_blockers beside this one.)
            if isinstance(b, NarrativeBlock):
                out.extend(i.claim for i in b.items if i.claim is not None)
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
