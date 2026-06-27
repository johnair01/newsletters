"""Phase 13 (PROB-01) — the Problem lifecycle entity, its ladder, and human-gated transition.

These tests pin the entity half of the final phase:

* a ``Problem`` aggregates >=1 traced ``Source`` (zero evidence is refused) and starts at
  ``ProblemState.IDENTIFIED``;
* the typed ladder ``IDENTIFIED -> OWNED -> IN_PROGRESS -> RESOLVED -> VERIFIED`` advances one
  rung at a time, with explicit re-open (Resolved/Verified -> In Progress) the only backward edge;
* ``transition(to, by, note)`` is the SOLE mutator — it refuses an empty actor (human-gated) and
  an illegal ladder move, never auto-advances, and records each move on an immutable log;
* ``source_ids`` gives the distinct constituent Source ids (single-entity traceability — NOT the
  Phase-14 cross-Problem query);
* a dogfood Problem aggregating a real Source runs end-to-end with no rendering.

The no-write-back / spine-boundary proofs (PROB-03) live in Plan 02; this file proves the entity.
"""

from __future__ import annotations

import pytest

from newsletters import Problem, ProblemState, TransitionEvent
from newsletters.semantic import Source, Trace


# --------------------------------------------------------------------------- #
# small helpers — a real-shaped Source + a content-addressed Trace to it
# --------------------------------------------------------------------------- #


def _src() -> Source:
    return Source(
        id="session-rev1",
        context="claude-code",
        transcript="Rev1 end-to-end: the Locator union risked a circular import "
        "semantic->distill->semantic; resolved by making locators a leaf module.",
    )


def _evidence(src: Source) -> list[Trace]:
    span = "the Locator union risked a circular import"
    start = src.transcript.find(span)
    assert start >= 0
    return [Trace.from_source(src, start, start + len(span))]


# --------------------------------------------------------------------------- #
# PROB-01 — evidence aggregation (>=1 traced Source)
# --------------------------------------------------------------------------- #


def test_problem_requires_at_least_one_source() -> None:
    """A Problem with zero evidence is refused; >=1 Trace constructs and starts IDENTIFIED."""
    with pytest.raises(ValueError):
        Problem(id="p-empty", title="no evidence", evidence=[])

    src = _src()
    prob = Problem(id="p1", title="circular import", evidence=_evidence(src))
    assert prob.state is ProblemState.IDENTIFIED
    assert prob.log == []


# --------------------------------------------------------------------------- #
# PROB-01 — the ladder: sequential forward + explicit re-open
# --------------------------------------------------------------------------- #


def test_ladder_forward_and_reopen() -> None:
    """The full forward sequence advances state + logs one event per step; re-open is allowed."""
    src = _src()
    prob = Problem(id="p1", title="circular import", evidence=_evidence(src))

    prob.transition(ProblemState.OWNED, by="Claude")
    prob.transition(ProblemState.IN_PROGRESS, by="Claude")
    prob.transition(ProblemState.RESOLVED, by="Claude")
    prob.transition(ProblemState.VERIFIED, by="JJ Airuoyo")
    assert prob.state is ProblemState.VERIFIED
    assert [e.to_state for e in prob.log] == [
        ProblemState.OWNED,
        ProblemState.IN_PROGRESS,
        ProblemState.RESOLVED,
        ProblemState.VERIFIED,
    ]
    # from_state / by are recorded on each event (the legible record)
    assert prob.log[0].from_state is ProblemState.IDENTIFIED
    assert prob.log[-1].by == "JJ Airuoyo"

    # re-open from VERIFIED (regression) is allowed and logged
    prob.transition(ProblemState.IN_PROGRESS, by="Claude", note="regression found")
    assert prob.state is ProblemState.IN_PROGRESS
    assert prob.log[-1].from_state is ProblemState.VERIFIED
    assert prob.log[-1].note == "regression found"

    # re-open from RESOLVED is also allowed
    prob.transition(ProblemState.RESOLVED, by="Claude")
    prob.transition(ProblemState.IN_PROGRESS, by="Claude", note="failed verification")
    assert prob.state is ProblemState.IN_PROGRESS
    assert prob.log[-1].from_state is ProblemState.RESOLVED


def test_transition_refuses_illegal_move() -> None:
    """A skip and an arbitrary backward jump each raise; state is unchanged on refusal."""
    src = _src()
    prob = Problem(id="p1", title="circular import", evidence=_evidence(src))

    # skip forward (IDENTIFIED -> RESOLVED) is refused
    with pytest.raises(ValueError):
        prob.transition(ProblemState.RESOLVED, by="Claude")
    assert prob.state is ProblemState.IDENTIFIED
    assert prob.log == []

    # walk up to VERIFIED, then attempt an arbitrary backward jump VERIFIED -> IDENTIFIED
    prob.transition(ProblemState.OWNED, by="Claude")
    prob.transition(ProblemState.IN_PROGRESS, by="Claude")
    prob.transition(ProblemState.RESOLVED, by="Claude")
    prob.transition(ProblemState.VERIFIED, by="Claude")
    log_len = len(prob.log)
    with pytest.raises(ValueError):
        prob.transition(ProblemState.IDENTIFIED, by="Claude")
    assert prob.state is ProblemState.VERIFIED
    assert len(prob.log) == log_len  # no event appended on refusal


# --------------------------------------------------------------------------- #
# PROB-03 (entity half) — human-gated: empty actor refused, no auto-advance path
# --------------------------------------------------------------------------- #


def test_transition_human_gated() -> None:
    """An empty/whitespace actor is refused; transition is the only way state changes."""
    src = _src()
    prob = Problem(id="p1", title="circular import", evidence=_evidence(src))

    with pytest.raises(ValueError):
        prob.transition(ProblemState.OWNED, by="")
    with pytest.raises(ValueError):
        prob.transition(ProblemState.OWNED, by="   ")
    assert prob.state is ProblemState.IDENTIFIED
    assert prob.log == []

    # there is no public setter / auto-advance verb — transition is the sole mutator
    public = {n for n in dir(prob) if not n.startswith("_")}
    assert "transition" in public
    for auto in ("advance", "auto_advance", "set_state", "publish", "approve"):
        assert auto not in public


def test_source_ids_property() -> None:
    """source_ids returns the distinct, de-duplicated source_id list from evidence."""
    src = _src()
    # two traces to the SAME source -> source_ids de-duplicates to one id
    span1 = "the Locator union risked a circular import"
    span2 = "resolved by making locators a leaf module"
    s1 = src.transcript.find(span1)
    s2 = src.transcript.find(span2)
    evidence = [
        Trace.from_source(src, s1, s1 + len(span1)),
        Trace.from_source(src, s2, s2 + len(span2)),
    ]
    prob = Problem(id="p1", title="circular import", evidence=evidence)
    assert prob.source_ids == ["session-rev1"]


# --------------------------------------------------------------------------- #
# L7 dogfood — one real Problem, end to end through human-gated transitions
# --------------------------------------------------------------------------- #


def test_dogfood_problem_end_to_end() -> None:
    """A real Problem aggregating the session-rev1 Source runs Identified -> Verified, no render."""
    # A genuine build problem: the Locator union risked a circular import (locators.py:5-16).
    src = _src()
    evidence = _evidence(src)

    prob = Problem(
        id="prob-circular-import",
        title="Locator union risked a circular import",
        evidence=evidence,  # >=1 source enforced at construction
    )
    assert prob.state is ProblemState.IDENTIFIED

    # human-gated sequence, with a PEER actor on the VERIFIED step (the review ethos, NOT the gate API)
    prob.transition(ProblemState.OWNED, by="Claude", note="picked up during Rev1")
    prob.transition(ProblemState.IN_PROGRESS, by="Claude")
    prob.transition(ProblemState.RESOLVED, by="Claude", note="moved Locator to a leaf module")
    prob.transition(ProblemState.VERIFIED, by="JJ Airuoyo", note="import graph acyclic; tests green")

    assert prob.state is ProblemState.VERIFIED
    assert [e.to_state for e in prob.log] == [
        ProblemState.OWNED,
        ProblemState.IN_PROGRESS,
        ProblemState.RESOLVED,
        ProblemState.VERIFIED,
    ]
    assert prob.source_ids == ["session-rev1"]  # traceable to evidence (PROB-04 prep)
    # the evidence stays content-addressed + non-stale against the live source (drift-aware, free)
    assert evidence[0].is_addressed
    assert not evidence[0].is_stale_against(src)


def test_transition_event_is_a_typed_record() -> None:
    """TransitionEvent carries from/to/by/note/at as a typed, immutable record of one move."""
    ev = TransitionEvent(
        from_state=ProblemState.IDENTIFIED, to_state=ProblemState.OWNED, by="Claude"
    )
    assert ev.from_state is ProblemState.IDENTIFIED
    assert ev.to_state is ProblemState.OWNED
    assert ev.by == "Claude"
    assert ev.note == ""
    assert ev.at is not None


def test_state_and_log_cannot_be_set_directly_outside_transition() -> None:
    """The human-gate is real, not advisory: ``transition`` is the SOLE mutator of ``state``/``log``.

    A bare ``p.state = VERIFIED`` would bypass the actor check, the ladder, AND the log — so it is
    refused (AttributeError). Found by the Phase-13 verifier; this guards against reopening it.
    """
    from newsletters.semantic import Source, Trace

    src = Source(id="S", transcript="The deploy queue stalls under load badly.")
    p = Problem(id="P", title="stall", evidence=[Trace.from_source(src, 0, 20)])
    p.transition(ProblemState.OWNED, by="JJ")

    import pytest

    with pytest.raises(AttributeError):
        p.state = ProblemState.VERIFIED  # bypass attempt — refused
    assert p.state is ProblemState.OWNED  # unchanged

    with pytest.raises(AttributeError):
        p.log = []  # erasing the legible record — refused
    assert len(p.log) == 1

    # transition remains the working, in-place mutator + round-trips with state preserved.
    p.transition(ProblemState.IN_PROGRESS, by="JJ")
    assert p.state is ProblemState.IN_PROGRESS
    reloaded = Problem.model_validate_json(p.model_dump_json())
    assert reloaded.state is ProblemState.IN_PROGRESS and len(reloaded.log) == 2
