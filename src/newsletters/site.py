"""The Library's identity core — typed ``Site / Collection / Page`` + stable IDs (SITE-01).

This module moves *identity* OUT of the presentation tier (the old positional
``enumerate(surfaces, 1)`` in ``render.py``) and INTO a deterministic, AI-free core model.
Identity is a **pure function of content + an append-only ledger**: the same surfaces and
the same ledger always produce the same IDs, regardless of list order.

Three pieces:

* :func:`slugify` — a 4-line, dependency-free slug (the canonical link key). [L4]
* :class:`Ledger` — the committed, append-only ``slug -> {ref, type, issue, date}`` map at
  ``content/rev1/ids.json``. An existing slug keeps its recorded ref forever (IMMUTABLE);
  a new slug gets the next per-type ordinal (``max + 1``). This append-only discipline IS
  the stability mechanism behind ROADMAP success criterion 2. [L5]
* :class:`Site` / :class:`Collection` / :class:`Page` — the typed content model. ``Page``
  WRAPS a ``Surface`` (it never mutates it); ``Collection`` groups Pages by surface TYPE
  (ordered by ``template.distance``); ``Site.by_slug`` is the cross-link RESOLVER. [L6]

IMPORT-GRAPH NOTE (load-bearing — the AI-optional-core boundary): this module imports ONLY
stdlib (``re``, ``unicodedata``, ``json``, ``datetime``, ``pathlib``) + ``pydantic`` + the
sibling core modules ``.semantic`` / ``.templates``. It must NEVER import the ``.distill``
package or any AI/LLM dependency — ``lint-imports`` enforces this, and
``tests/test_site.py::test_imports_are_ai_free`` is the runtime belt-and-braces.

Anti-pattern (forbidden): deriving any visible identifier from list position. Order is data;
identity is content + the ledger. Positions shift, refs don't.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date as _date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .semantic import ReviewState, Surface
from .templates import SignalColor, get_template


# --------------------------------------------------------------------------- #
# slugify (L4) — pure, deterministic, dependency-free, filename-safe
# --------------------------------------------------------------------------- #


def slugify(text: str) -> str:
    """Return a deterministic, ASCII-only, filename-safe slug for ``text``.

    NFKD-normalize → drop combining marks (ASCII-fold accents) → lowercase → collapse every
    run of non-``[a-z0-9]`` characters to a single ``-`` → strip leading/trailing ``-``.

    Pure (no I/O). The output is restricted to ``[a-z0-9-]`` so it is safe to interpolate
    into ``f"{slug}.html"`` — it can never contain ``/``, ``.``, ``\\`` or whitespace, which
    closes the path-traversal threat T-08-01.
    """
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")


# --------------------------------------------------------------------------- #
# Ledger (L5) — append-only per-type sequential refs, byte-stable JSON
# --------------------------------------------------------------------------- #

# Per-type ref format (L1 ID conventions). Reports/Articles/Learning are 3-digit; Shows are
# 2-digit episode numbers. Newsletters are CADENCED — keyed by issue + date, no sequential
# ref — so they are deliberately absent here (``ref_for`` returns "" for them).
_REF_FORMAT: dict[str, str] = {
    "report": "R-{:03d}",
    "article": "A-{:03d}",
    "show": "EP{:02d}",
    "learning": "L-{:03d}",
}

# Surfaces whose identity is a cadence (issue + date), not a sequential ordinal.
_CADENCED: frozenset[str] = frozenset({"newsletter"})

_TRAILING_DIGITS = re.compile(r"(\d+)$")


class Ledger:
    """The append-only ID ledger: ``slug -> {ref, type, issue, date}`` persisted as JSON.

    The ledger is the SINGLE source of truth for refs and the SINGLE writer of
    ``content/rev1/ids.json``. ``render.py`` must never touch it. An existing slug's ref is
    immutable; a new slug for a sequential type gets ``max(per-type ordinal) + 1`` (never
    ``count + 1`` — that would let a deleted surface's number be reused; append-only by A4).
    """

    def __init__(self, path: Path, data: dict[str, dict]):
        self.path = path
        self._data = data

    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        """Load the ledger from ``path`` (or start empty if the file does not exist)."""
        p = Path(path)
        data = json.loads(p.read_text("utf-8")) if p.exists() else {}
        return cls(p, data)

    def slugs(self) -> list[str]:
        """Every slug currently recorded (sorted, for deterministic iteration)."""
        return sorted(self._data)

    def entry(self, slug: str) -> dict | None:
        """The raw recorded entry for ``slug`` (``{ref, type, issue, date}``) or ``None``."""
        e = self._data.get(slug)
        return dict(e) if e is not None else None

    def ref_for(
        self,
        slug: str,
        kind: str | None,
        *,
        issue: int | None = None,
        date: _date | None = None,
    ) -> str:
        """Return the stable ref for ``slug``, assigning one on first sight (append-only).

        An EXISTING slug returns its recorded ref unchanged — never recomputed — so a reorder
        or insert can never renumber it (the stability invariant). ``kind`` may be ``None``
        when querying a slug already known to exist (read-only lookup).

        A NEW slug of a sequential type is assigned ``max(existing ordinals of that type)+1``,
        formatted per :data:`_REF_FORMAT`. A new CADENCED slug (newsletter) is recorded with
        its ``issue``/``date`` and an empty ref (cadence is its identity, not an ordinal).
        """
        if slug in self._data:
            return self._data[slug]["ref"]  # EXISTING — immutable, never recomputed.

        if kind is None:
            raise KeyError(f"unknown slug {slug!r} and no kind given to assign a new ref")

        if kind in _CADENCED:
            ref = ""
        else:
            n = self._next_ordinal(kind)
            fmt = _REF_FORMAT.get(kind)
            ref = fmt.format(n) if fmt else f"{kind.upper()}-{n:03d}"

        self._data[slug] = {
            "ref": ref,
            "type": kind,
            "issue": issue,
            "date": date.isoformat() if date else None,
        }
        return ref

    def _next_ordinal(self, kind: str) -> int:
        """``max(trailing-digit ordinal of every entry of this type) + 1`` (default 1)."""
        ordinals = [
            int(m.group(1))
            for e in self._data.values()
            if e.get("type") == kind
            for m in (_TRAILING_DIGITS.search(e.get("ref") or ""),)
            if m
        ]
        return (max(ordinals) + 1) if ordinals else 1

    def save(self) -> None:
        """Write the ledger as byte-stable JSON (``sort_keys`` + trailing newline) — L5/T-08-03."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


# --------------------------------------------------------------------------- #
# Site / Collection / Page (E) — the typed content model
# --------------------------------------------------------------------------- #


class Page(BaseModel):
    """One published surface within a collection, carrying its stable identity.

    ``Page`` WRAPS its :class:`~newsletters.semantic.Surface` (held in ``surface``); it never
    modifies it. ``slug`` is the canonical link key (== ``Surface.id`` for the Rev1 corpus,
    L3 backward-compat); ``ref`` is the human per-type ordinal read from the ledger; ``gate``
    is CARRIED only (no gate-state board here — that is Phase 9/10, L6).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    slug: str
    ref: str
    title: str
    kind: str
    gate: ReviewState
    signal_color: SignalColor
    href: str
    issue: int | None = None
    date: _date | None = None
    surface: Surface


class Collection(BaseModel):
    """A grouping of Pages by surface TYPE (the natural board column) — grouping only, L6."""

    kind: str
    display_name: str
    pages: list[Page] = Field(default_factory=list)


class Site(BaseModel):
    """The whole Library: ordered :class:`Collection`s, with a slug-keyed cross-link resolver."""

    collections: list[Collection] = Field(default_factory=list)

    def pages(self) -> list[Page]:
        """Every Page across all collections (flattened, in collection order)."""
        return [p for c in self.collections for p in c.pages]

    def by_slug(self, slug: str) -> Page | None:
        """Resolve a slug to its Page (L6 cross-link RESOLVER) — ``None`` if unknown."""
        for c in self.collections:
            for p in c.pages:
                if p.slug == slug:
                    return p
        return None

    @classmethod
    def from_surfaces(cls, surfaces: list[Surface], *, ledger: Ledger) -> "Site":
        """Build a ``Site`` from ``surfaces`` + a ``ledger``, assigning/reading stable IDs.

        Pure given a ledger: it reads (and, for new slugs, extends) the in-memory ledger but
        does NOT call ``ledger.save()`` — the CALLER owns persistence, so tests using
        ``tmp_path`` stay isolated and the committed ledger is never written as a side effect.

        For each surface (in input order): ``slug = surface.id`` (L3 backward-compat;
        ``slugify(title)`` only if the id is not slug-clean), ``ref`` comes from the ledger,
        and a :class:`Page` is built. Pages are then grouped by surface kind into
        :class:`Collection`s ordered by ``template.distance`` (show 0, report 1, article 2,
        newsletter 3). Reorder-safe because refs come from the ledger, never from enumerate.
        """
        # Stable per-kind buckets in first-seen order; sorted by distance at the end.
        buckets: dict[str, list[Page]] = {}
        for surface in surfaces:
            slug = surface.id if surface.id == slugify(surface.id) else slugify(surface.title)
            ref = ledger.ref_for(slug, surface.kind)
            page = Page(
                slug=slug,
                ref=ref,
                title=surface.title,
                kind=surface.kind,
                gate=surface.gate,
                signal_color=surface.signal_color,
                href=f"{slug}.html",
                issue=None,
                date=None,
                surface=surface,
            )
            buckets.setdefault(surface.kind, []).append(page)

        collections = [
            Collection(
                kind=kind,
                display_name=get_template(kind).display_name,
                pages=pages,
            )
            for kind, pages in buckets.items()
        ]
        collections.sort(key=lambda c: get_template(c.kind).distance)
        return cls(collections=collections)
