"""The ``Problem`` lifecycle entity — a first-class record ABOVE ``Source`` (PROB-01).

A ``Problem`` makes the scattered ``problem -> owned -> solution -> verified`` lifecycle a
legible, evidence-traced home — **a legibility layer, NOT a second tracker**. Problem-*solving*
stays external/operator-owned; this module models only the *record* of the lifecycle and never
executes it.

IMPORT-GRAPH NOTE (load-bearing — the leaf/acyclic rule): this module imports ONLY stdlib +
pydantic + ``.semantic`` (``Source``, ``Trace`` — the spine's evidence types). It must NEVER
import the AI/``distill`` package, ``capture``, ``render``, ``site``, or any network/external-
system package. It sits one tier ABOVE the leaf (``locators.py``): the edge is

    problem -> semantic -> {locators, templates}

which is acyclic — ``semantic.py`` imports only ``.locators`` + ``.templates`` and NEVER imports
``problem`` (the dependency is strictly one-way). This mirrors how ``promote.py`` imports from
``.semantic`` (the import-pattern precedent) while staying AI-free.

Three invariants are enforced *in code*:

1. **Every Problem traces to evidence** — a Problem aggregates ``>=1`` ``Trace`` to its
   constituent ``Source`` records (the scattered ticket / passdown / RCA). A Problem with zero
   sources is refused at construction (it is not legible).
2. **Human-gated, never auto-mutated** — state changes ONLY through ``transition(to, by, ...)``,
   which refuses a transition with no recorded actor. There is no public setter and no
   auto-advance path. This mirrors the no-auto-publish gate in ``semantic.py``.
3. **Ladder-enforced** — ``transition`` refuses an illegal ladder move (a skip, or an arbitrary
   backward jump); only sequential-forward moves plus the two explicit re-open edges
   (Resolved/Verified -> In Progress) are allowed. The lifecycle's bumps are *recorded*, never
   erased.

The verb is ``transition`` (NOT promote / publish / advance / fan-out / derive — the three-axis
terminology guard reserves those for the review gate and the fan-out chain).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from .semantic import Source, Trace  # the ONLY non-stdlib/pydantic import — acyclic, AI-free

# ``Source`` is imported for its role as the entity this Problem sits above (it is the type a
# ``Trace`` points back at); referenced in this docstring/typing context to keep the spine edge
# explicit. ``Trace`` is the evidence-pointer reused as ``Problem.evidence``.
__all__ = ["ProblemState", "TransitionEvent", "Problem"]

# Re-exported for callers that want the spine type at hand without a second import line; this is a
# pure re-reference of an already-imported symbol (no new edge).
_ = Source


def _utcnow() -> datetime:
    """tz-aware UTC now — a two-line local copy of ``semantic._utcnow`` (keep the leaf clean)."""
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# The lifecycle ladder — a typed axis DISTINCT from the review gate (terminology guard)
# --------------------------------------------------------------------------- #


class ProblemState(StrEnum):
    """The Problem lifecycle rungs, bottom to top.

    A ``StrEnum`` exactly like ``semantic.ReviewState``, but a DISTINCT type with member VALUES
    that share nothing with the review gate's ``"draft"/"in_review"/"published"``. Note
    ``IN_PROGRESS = "in_progress"`` is deliberately a different string from ``IN_REVIEW =
    "in_review"`` — close but disjoint (the distinctness PROOF is Plan 02's job).
    """

    IDENTIFIED = "identified"
    OWNED = "owned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"


# The allowed-moves table: forward one rung at a time, with re-open the ONLY backward edge, and
# only from the two "done" rungs (a Resolved problem fails verification; a Verified fix regresses).
# Every other move — a skip (Identified -> Resolved) or an arbitrary backward jump
# (Verified -> Identified) — is refused. Re-open is still a *recorded* human transition.
_LADDER: dict[ProblemState, set[ProblemState]] = {
    ProblemState.IDENTIFIED: {ProblemState.OWNED},
    ProblemState.OWNED: {ProblemState.IN_PROGRESS},
    ProblemState.IN_PROGRESS: {ProblemState.RESOLVED},
    ProblemState.RESOLVED: {ProblemState.VERIFIED, ProblemState.IN_PROGRESS},  # re-open
    ProblemState.VERIFIED: {ProblemState.IN_PROGRESS},  # regression re-open
}


class TransitionEvent(BaseModel):
    """An immutable record of ONE lifecycle move: from -> to, by whom, when, and why.

    The ``log`` of these on a ``Problem`` IS the legible record of the lifecycle — who moved a
    problem to which rung, and when. Mirrors the ``by`` + ``at`` accountability of an approval.
    """

    from_state: ProblemState
    to_state: ProblemState
    by: str
    note: str = ""
    at: datetime = Field(default_factory=_utcnow)


# --------------------------------------------------------------------------- #
# The entity — a Problem aggregating >=1 traced Source, with a human-gated ladder
# --------------------------------------------------------------------------- #


class Problem(BaseModel):
    """A first-class problem record ABOVE ``Source`` — its evidence + its lifecycle, made legible.

    Aggregates ``>=1`` ``Trace`` to its constituent ``Source`` records (reusing the spine's
    evidence-pointer type, so the evidence is content-addressed + drift-aware for free). State
    starts at ``IDENTIFIED`` and advances ONLY through the human-gated ``transition``; every move
    appends a ``TransitionEvent`` to ``log``.
    """

    id: str
    title: str
    state: ProblemState = ProblemState.IDENTIFIED
    evidence: list[Trace] = Field(default_factory=list)
    log: list[TransitionEvent] = Field(default_factory=list)
    opened: datetime = Field(default_factory=_utcnow)

    # A private gate: ``state``/``log`` may be assigned ONLY while ``transition`` holds this open.
    # Without it, a bare ``p.state = VERIFIED`` would bypass the actor check, the ladder, AND the log
    # — making the human-gate a lie. Construction sets fields through pydantic's core (not __setattr__),
    # so initial state + round-trip deserialization are unaffected; only POST-construction assignment
    # is guarded. (Found by the Phase-13 verifier; closed so "transition is the sole mutator" is literal.)
    _via_transition: bool = PrivateAttr(default=False)

    def __setattr__(self, name: str, value: object) -> None:
        """Refuse direct assignment to ``state``/``log`` outside ``transition`` (human-gate integrity).

        The lifecycle ladder is only meaningful if it cannot be sidestepped: ``p.state = ...`` and
        ``p.log = ...`` are refused unless ``transition`` is actively applying a recorded, human-gated,
        ladder-legal move. Mirrors the no-auto-publish gate — the rung never moves without a human.
        """
        if name in ("state", "log") and not getattr(self, "_via_transition", False):
            raise AttributeError(
                f"Problem.{name} is human-gated: it changes ONLY through transition(to, by). Direct "
                "assignment is refused so the actor check, the ladder, and the log cannot be bypassed "
                "(mirrors no-auto-publish). To move the lifecycle, call transition()."
            )
        super().__setattr__(name, value)

    @field_validator("evidence")
    @classmethod
    def _at_least_one_source(cls, v: list[Trace]) -> list[Trace]:
        """Refuse a Problem with no evidence — every Problem traces to >=1 constituent Source."""
        if not v:
            raise ValueError(
                "A Problem must aggregate >=1 traced Source — every problem traces to "
                "evidence. A Problem with zero sources is not legible; add a Trace to a "
                "constituent Source record."
            )
        return v

    @property
    def source_ids(self) -> list[str]:
        """The distinct, de-duplicated Source ids this Problem aggregates (single-entity).

        Single-entity traceability — the back-links the Phase-14 board will render. NOT a
        cross-Problem query (that aggregation is PROB-02 / Phase 14).
        """
        return list(dict.fromkeys(t.source_id for t in self.evidence))

    def transition(self, to: ProblemState, by: str, note: str = "") -> "Problem":
        """Record a human-gated lifecycle move. The SOLE mutator of ``state``; never auto-advances.

        Refuses (raises ``ValueError``) on:

        * an empty/whitespace actor ``by`` — like the publish gate, every move is human-gated;
          a Problem's state never advances without a recorded human.
        * an illegal ladder move (``to`` not reachable from the current ``state`` per ``_LADDER``)
          — a skip or an arbitrary backward jump; the teaching message lists the allowed moves.

        On success: appends ``TransitionEvent(from_state, to_state=to, by, note)`` to ``log`` and
        sets ``state = to``. There is no public setter and no auto-advance path — this method is
        the only way ``state`` changes. State is unchanged when the move is refused.
        """
        if not by or not by.strip():
            raise ValueError(
                "transition() requires an explicit human actor (`by`). A Problem's state "
                "never auto-advances — like the publish gate, every move is human-gated."
            )
        if to not in _LADDER[self.state]:
            allowed = sorted(s.value for s in _LADDER[self.state])
            raise ValueError(
                f"Illegal lifecycle move {self.state.value!r} -> {to.value!r}. "
                f"Allowed from {self.state.value!r}: {allowed}. The ladder is sequential "
                "forward plus explicit re-open (Resolved/Verified -> In Progress)."
            )
        # Open the private gate for exactly the two guarded writes, then close it (even on error),
        # so ``transition`` is the ONLY path that can move ``state`` / append to ``log``.
        object.__setattr__(self, "_via_transition", True)
        try:
            self.log = [*self.log, TransitionEvent(from_state=self.state, to_state=to, by=by, note=note)]
            self.state = to
        finally:
            object.__setattr__(self, "_via_transition", False)
        return self
