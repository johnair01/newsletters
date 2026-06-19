"""The capture boundary — turning a finished work session into a traced Report.

Newsletters does **not** do the problem-solving. An external, operator-owned agent
(Claude Code, Copilot, PulseIQ's own swarm, a human with a notebook) does the work; this
module captures *what happened* into the trust layer. Two modes:

* **Capture / observe (default, universal):** runs *after* a session and reads its
  artifacts/decisions — no cooperation from the external agent required. This is the
  deterministic, agent-agnostic path implemented here.
* **Emit / integrate (operator add-on):** an external agent pushes a Report via the
  package API directly. That path just constructs the same objects.

A "work session" is intentionally lightweight: a named bundle of ``Source`` records plus
the decisions captured from them. No heavyweight ``Session`` type yet.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .semantic import (
    Claim,
    ClaimsBlock,
    Distillation,
    ProseBlock,
    Provenance,
    Review,
    Source,
    Surface,
    Trace,
)
from .templates import REPORT, SurfaceTemplate


class Decision(BaseModel):
    """A decision captured from a session, with the source it was made in."""

    text: str
    source_id: str
    locator: str = ""
    topics: list[str] = Field(default_factory=list)
    confidence: float = 0.85


class WorkSession(BaseModel):
    """A named bundle of sources + the decisions captured from them."""

    id: str
    title: str
    tool: str = "unknown"
    artifacts: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)


def capture_session(session: WorkSession) -> Distillation:
    """Deterministically lift a finished session into a traced ``Distillation``.

    Each captured decision becomes a ``Claim`` traced back to the ``Source`` it was made
    in. This is real today (no LLM) — it *structures* what already happened, it does not
    invent. The agentic synthesis over raw sources is the external Phase-4 step.
    """
    claims = [
        Claim(
            text=d.text,
            evidence=[Trace(source_id=d.source_id, locator=d.locator)],
            confidence=d.confidence,
            topics=d.topics,
        )
        for d in session.decisions
    ]
    narrative = (
        f"Captured from session {session.id!r} ({session.tool}): "
        f"{len(claims)} decision(s) across {len(session.sources)} source(s)."
    )
    return Distillation(narrative=narrative, claims=claims, traces=list(session.sources))


def build_report(
    session: WorkSession,
    *,
    surface_id: str,
    title: str,
    eyebrow: str = "",
    author: str,
    narrative: Optional[str] = None,
    template: SurfaceTemplate = REPORT,
) -> Surface:
    """Capture a session into a Draft ``Report`` surface (the operational, light-gate record).

    Convenience over ``capture_session`` for the common case: produces a surface with a
    prose lead + a traced ``ClaimsBlock`` + provenance, ready to open as a PR.
    """
    distillation = capture_session(session)
    blocks: list = []
    if narrative:
        blocks.append(ProseBlock(heading=None, text=narrative))
    blocks.append(ClaimsBlock(claims=distillation.claims))
    return Surface(
        id=surface_id,
        template=template,
        title=title,
        eyebrow=eyebrow or "Report · how we solved it",
        blocks=blocks,
        traces=distillation.traces,
        byline=[author],
        review=Review(policy=template.review_policy, author=author),
        provenance=Provenance(
            tool=session.tool, session_id=session.id, artifacts=session.artifacts
        ),
    )
