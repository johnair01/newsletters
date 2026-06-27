"""The ``Locator`` discriminated union — a TOP-LEVEL LEAF module (D-06).

A ``Locator`` is a content/address anchor: it says *where inside a Source* a claim's
evidence lives. It is the typed replacement for ``Trace``'s old bare-string ``locator``.

IMPORT-GRAPH NOTE (load-bearing — the circular-import fix): this module imports ONLY
stdlib + pydantic. It must NEVER import from ``.semantic``, the ``.distill`` package, or
``.capture``. That leaf property is what keeps the import graph acyclic:

    semantic -> locators   (leaf, mirrors the existing `from .templates import ...`)
    distill  -> locators   (leaf, re-exported by distill/__init__.py)

If this union lived *inside* the distill package, ``semantic`` importing it would run
``distill/__init__.py`` -> eager-import ``ports`` -> ``from ..semantic import ...`` while
``semantic`` is only partially initialized -> ImportError. Keeping it here avoids that.

Anti-pattern (forbidden): a locator derived from list position. Anchors are content /
address only, never an ordinal index — positions shift, addresses don't.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Phase-1 locator variants
# --------------------------------------------------------------------------- #


class FreeLocator(BaseModel):
    """A free-text anchor — the backward-compatible home of the old bare-string locator."""

    kind: Literal["free"] = "free"
    text: str = ""

    @property
    def display(self) -> str:
        """A human-readable address string (used by the renderer's evidence chip)."""
        return self.text


class SessionLocator(BaseModel):
    """An anchor into a captured work session: a Source plus an optional note."""

    kind: Literal["session"] = "session"
    source_id: str
    note: str = ""

    @property
    def display(self) -> str:
        """A human-readable address string (used by the renderer's evidence chip)."""
        return f"{self.source_id}{f' ({self.note})' if self.note else ''}"


# --------------------------------------------------------------------------- #
# Adapter-/v2-phase variants (documented contract reach — NOT built in Phase 1)
# --------------------------------------------------------------------------- #
#
# These are the anchors the extraction (Phases 4-7) and interview (v2 AI) backends
# will add against the SAME discriminated-union contract — listed here as stubs to
# show the contract's reach. Build NONE of them now.
#
# class MessageLocator(BaseModel):  kind: Literal["message"]; message_id: str; ...
# class CellLocator(BaseModel):     kind: Literal["cell"];    sheet: str; ref: str  # Excel A1
# class SlideLocator(BaseModel):    kind: Literal["slide"];   slide_no: int; shape_id: str  # PPTX
# class CodeLocator(BaseModel):     kind: Literal["code"];    path: str; span: str  # file:line-range
# class TurnLocator(BaseModel):     kind: Literal["turn"];    session_id: str; turn_no: int  # interview


# --------------------------------------------------------------------------- #
# The union — copies the `Block` discriminated-union idiom (semantic.py:273-287)
# --------------------------------------------------------------------------- #

Locator = Annotated[
    Union[FreeLocator, SessionLocator],
    Field(discriminator="kind"),
]


# --------------------------------------------------------------------------- #
# The extraction-coverage carrier — a TYPED carrier that travels WITH a Source
# --------------------------------------------------------------------------- #
#
# TASK ZERO / R1 (Phase 5). An adapter (Email, Excel, ...) determines, at parse() time, which
# raw content it could NOT faithfully extract (a forwarded part, an attachment, a charset
# fallback, an uncomputed formula cell). Pre-fix, that determination lived in adapter INSTANCE
# memory keyed by ``source.id``, so re-``distill()``ing a *persisted* Source on a fresh adapter
# silently lost it and falsely reported ``complete=True`` (04-VERIFICATION.md LIMITATION).
#
# The fix makes coverage a pure function of the Source by carrying the determination on the
# Source itself via ``Source.extraction: Optional[ExtractionRecord]`` (semantic.py). These carrier
# types are FIELD-IDENTICAL to ``distill.coverage.Unextracted`` ({locator, reason}) but MUST live
# HERE in the leaf, NOT in ``distill.coverage`` — because ``semantic`` imports them and ``semantic``
# must never import the ``distill`` package (the leaf rule above that keeps the import graph
# acyclic). The adapters-tier ``_coverage_codec`` bridges ``Unextracted <-> ExtractionRecord``.


class ExtractedDrop(BaseModel):
    """One piece of raw content an adapter could NOT extract — carried on a Source (R1).

    Field-identical to ``distill.coverage.Unextracted`` ({``locator``, ``reason``}); it lives in
    this leaf so ``semantic.Source`` can carry it without an acyclic-import violation. The shared
    ``_coverage_codec`` maps it to/from ``Unextracted`` losslessly.
    """

    locator: Locator
    reason: str = ""


class ExtractionRecord(BaseModel):
    """An adapter's full ``unextracted[]`` determination for one Source — the typed carrier (R1).

    ``Source.extraction`` holds this (default ``None``). Because it round-trips natively through
    ``model_dump_json``, the drops travel with the Source: a fresh adapter re-``distill()``ing a
    persisted Source reconstructs the SAME coverage. AI-free (stdlib + pydantic only).
    """

    unextracted: list[ExtractedDrop] = Field(default_factory=list)
