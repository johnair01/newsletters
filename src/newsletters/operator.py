"""The operator view's data model ("my view") — clients, their Library, editions, interactions.

The person running the engine for several clients needs one place that answers: who are my
clients, what is in each client's Library, which editions went out, and what came in, went
out, or is still pending. This module is the typed, read-only data side of that view; the
HTML lives in :func:`newsletters.render.render_operator_view` (one engine renders what a
tester sees and what ships; see the lane decisions in
``docs/runs/2026-11-07/lanes/B-operator-view/decisions.md``).

Shape of a client on disk: a directory holding ``client.json``. The loader only ever OPENS
FOR READING; it never writes, never creates files, and never touches the committed ledger.

* **Library** — the client's surfaces, built with the existing :meth:`Site.from_surfaces`
  and an in-memory :class:`Ledger` (no file path is ever saved), so refs follow the same
  rules as the public Library.
* **Editions** — dated issues delivered to the client; each points at a Library surface by
  id, and a dangling id fails loud at load time.
* **Interactions** — a typed log with direction ``received`` / ``sent`` / ``pending``.
  Pending comes only from the log; the view never infers a fact the record does not hold.

Gate states are reached through the real gate (:meth:`Surface.open_pull_request` and
:meth:`Surface.publish` with a recorded reviewer), so a fixture cannot claim "Published"
without a reviewer: the no-auto-publish invariant holds here too.

IMPORT-GRAPH NOTE: stdlib + pydantic + sibling core modules only. No AI imports
(``lint-imports`` and ``tests/test_operator.py`` guard this).
"""

from __future__ import annotations

import json
from datetime import date as _date
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .semantic import ProseBlock, ReviewState, Surface
from .site import Ledger, Site, slugify
from .templates import get_template

# Fixed timestamp for loaded surfaces: the view must render byte-identically on every run.
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

Direction = Literal["received", "sent", "pending"]
DIRECTIONS: tuple[Direction, ...] = ("received", "sent", "pending")


class SurfaceEntry(BaseModel):
    """One Library item as written in ``client.json`` (before it becomes a Surface)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    title: str
    summary: str = ""
    gate: ReviewState = ReviewState.DRAFT
    author: str | None = None
    reviewer: str | None = None


class Edition(BaseModel):
    """A dated issue delivered to a client, pointing at a Library surface by id."""

    model_config = ConfigDict(extra="forbid")

    issue: int = Field(ge=1)
    date: _date
    surface_id: str
    note: str = ""


class Interaction(BaseModel):
    """One entry in the client interaction log: what came in, went out, or is pending."""

    model_config = ConfigDict(extra="forbid")

    direction: Direction
    date: _date
    channel: str
    summary: str
    surface_id: str | None = None


class Client(BaseModel):
    """One client of the operator: identity, Library surfaces, editions, interactions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    name: str
    fixture: bool = False
    note: str = ""
    surfaces: list[Surface] = Field(default_factory=list)
    editions: list[Edition] = Field(default_factory=list)
    interactions: list[Interaction] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _slug_clean(cls, v: str) -> str:
        # The id becomes a directory name and an HTML anchor in the preview.
        if v != slugify(v) or not v:
            raise ValueError(f"client id must be slug-clean ([a-z0-9-]), got {v!r}")
        return v

    def site(self) -> Site:
        """The client's Library as a :class:`Site` (in-memory ledger; nothing is saved)."""
        return Site.from_surfaces(self.surfaces, ledger=Ledger(Path("<in-memory>"), {}))

    def editions_newest_first(self) -> list[Edition]:
        return sorted(self.editions, key=lambda e: (e.date, e.issue), reverse=True)

    def interactions_by_direction(self) -> dict[Direction, list[Interaction]]:
        out: dict[Direction, list[Interaction]] = {d: [] for d in DIRECTIONS}
        for i in sorted(self.interactions, key=lambda i: i.date, reverse=True):
            out[i.direction].append(i)
        return out

    def surface_title(self, surface_id: str) -> str:
        for s in self.surfaces:
            if s.id == surface_id:
                return s.title
        raise KeyError(surface_id)


class OperatorView(BaseModel):
    """Everything the operator view shows: the ordered client list."""

    clients: list[Client] = Field(default_factory=list)

    @property
    def has_fixture(self) -> bool:
        return any(c.fixture for c in self.clients)


def _to_surface(entry: SurfaceEntry) -> Surface:
    """Build a Surface and walk it through the real gate to its recorded state."""
    surface = Surface(
        id=entry.id,
        template=get_template(entry.kind),
        title=entry.title,
        blocks=[ProseBlock(text=entry.summary)] if entry.summary else [],
        byline=[entry.author] if entry.author else [],
        created=_EPOCH,
    )
    if entry.author:
        surface.review = surface.review.model_copy(update={"author": entry.author})
    if entry.gate in (ReviewState.IN_REVIEW, ReviewState.PUBLISHED):
        surface.open_pull_request()
    if entry.gate is ReviewState.PUBLISHED:
        if not entry.reviewer:
            raise ValueError(
                f"surface {entry.id!r} claims Published with no reviewer; "
                "nothing reaches Published without a recorded reviewer"
            )
        surface.publish(entry.reviewer)
    return surface


def load_client(directory: str | Path) -> Client:
    """Read ``<directory>/client.json`` into a :class:`Client`. Read-only; fails loud."""
    path = Path(directory) / "client.json"
    with path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)

    entries = [SurfaceEntry.model_validate(s) for s in raw.get("surfaces", [])]
    ids = [e.id for e in entries]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate surface ids")
    editions = [Edition.model_validate(e) for e in raw.get("editions", [])]
    interactions = [Interaction.model_validate(i) for i in raw.get("interactions", [])]

    known = set(ids)
    dangling = [e.surface_id for e in editions if e.surface_id not in known] + [
        i.surface_id for i in interactions if i.surface_id and i.surface_id not in known
    ]
    if dangling:
        raise ValueError(f"{path}: references to unknown surface ids {sorted(set(dangling))}")

    return Client(
        id=raw["id"],
        name=raw["name"],
        fixture=bool(raw.get("fixture", False)),
        note=raw.get("note", ""),
        surfaces=[_to_surface(e) for e in entries],
        editions=editions,
        interactions=interactions,
    )


def load_operator_view(directories: list[str | Path]) -> OperatorView:
    """Load each client directory, in the order given (the first row is the first dir)."""
    return OperatorView(clients=[load_client(d) for d in directories])
