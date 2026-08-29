"""The ONE span minter: pinning an authored spec value to a real span of its own file.

WHY THIS MODULE EXISTS (Phase 3 / WKLY-02, promoting ``casespec._SpanMinter``). The Case Spec
loader proved the mechanism; the Weekly Spec loader needs exactly the same one. Copying it would
give this repo **two** implementations of "pin a claim to a span honestly", and two such
implementations drift precisely as two normalizers do — the recorded reason
``src/newsletters/pptx_writer.py`` exists at all ("**ONE normalizer contract**"; a second
implementation drifts from the first and the drift is invisible until a gate that trusted both
goes red). So the minter is PROMOTED, not forked and not privately cross-imported: one
implementation, imported by ``casespec`` and ``weeklyspec`` alike.

THE MOVE IS A MOVE. ``SpanMinter`` and ``absent`` arrived here VERBATIM from ``casespec.py`` —
bodies, docstrings and comments unchanged — so a reviewer diffing the move can see that nothing
was "tidied" on the way. The only edits are the two names losing their leading underscore: a name
two modules import is not private (the ``pptx_writer`` promotion precedent, which promoted five
names the same way).

THE CONTRACT.

* This is the ONE place a claim is pinned to a real span of an authored spec file. Every span in
  the record comes from ``Trace.from_source`` here, so the strict half of
  ``SpanContainmentFaithfulness`` has teeth on every emitted claim.
* **The cursor is FORWARD-ONLY, so callers MUST walk their parsed document in FILE ORDER.** This
  is a correctness condition, not a style preference. ``.planning/phases/03-weekly-compose/
  03-RESEARCH.md`` §Pitfall 1 proved by execution that minting a *later* field before an earlier
  one silently SWAPS the spans of a value duplicated across two sections (a person named in both
  ``recognitions:`` and ``team:``), and that **both claims still pass the faithfulness gate**
  because the text is identical. No gate can catch this; only file-order iteration prevents it.
* ``mint`` returns EITHER a gate-entailed ``Claim`` OR a ``str`` disclosure destined for the
  caller's ``Distillation.missing[]``. It never returns a claim the live gate rejects, and it
  never silently drops a value.
* ``GATE`` below is the ONE live gate instance both loaders share — public for the same reason
  the two names above are: a name two modules import is not private. Constructing a second
  ``SpanContainmentFaithfulness`` elsewhere would be the same fork this module exists to prevent.

AI-OPTIONAL / BARE-INSTALL DISCIPLINE. Module level here is stdlib + pydantic + ``semantic`` /
``distill`` only — no column-0 ``import yaml`` (parsing is the caller's job, through the lazy
``[config]`` boundary), and nothing from an AI extra.
"""

from __future__ import annotations

from typing import Optional, Union

from .distill.faithfulness import SpanContainmentFaithfulness
from .semantic import Claim, Source, Trace

__all__ = ["GATE", "SpanMinter", "absent"]

# ONE definition of "faithful" — the live gate, reused, never reimplemented.
GATE = SpanContainmentFaithfulness()


def _comment_start(line: str) -> Optional[int]:
    """The column where ``line``'s YAML comment starts, or ``None`` when it carries no comment.

    A ``#`` begins a comment when it sits at column 0 or after whitespace, outside a single- or
    double-quoted scalar. This is a span-strategy heuristic, not a full YAML lexer (inside a
    block scalar a ``#`` is content): a line it misclassifies only makes the exact-find decline
    a match, and the value then falls through to the gate-checked REGION strategies — an honest,
    wider span. The heuristic can therefore never drop a value, only refuse to pin one to text
    nobody authored as a value.
    """
    quote: Optional[str] = None
    for index, char in enumerate(line):
        if quote is not None:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1] in " \t"):
            return index
    return None


class SpanMinter:
    """Locate each authored value in the RAW file text and mint it — or disclose it.

    A forward-only cursor (the ``swimlane._Minter`` precedent) so duplicate values get
    distinct offsets. Two strategies, in order: (1) exact verbatim ``str.find`` — the span
    IS the value — skipping any match that starts inside a YAML comment, because a comment
    is never-minted text and pinning a claim to one would mis-attribute its evidence
    (WR-01, 03-review); (2) for a block scalar (whose folded value is not a verbatim substring),
    a raw BLOCK REGION located by a forward line scan — the field's value block for a
    mapping value, the ITEM's own region (after its ``-`` marker) for a sequence item, so
    one block-scalar item never swallows its siblings' spans — kept only if the live
    span-containment gate entails the claim against that region. A value neither strategy
    can honestly pin is returned as a disclosure string (verbatim, for ``missing[]``).
    """

    def __init__(self, source: Source) -> None:
        self._source = source
        self._raw = source.transcript
        self._cursor = 0
        self._lines = self._raw.splitlines(keepends=True)
        offsets, pos = [], 0
        for line in self._lines:
            offsets.append(pos)
            pos += len(line)
        self._line_offsets = offsets
        self._line_cursor = 0
        # WR-01 (03-review): the raw (start, end) interval of every YAML comment, computed once,
        # so the forward exact-find can refuse a match that starts inside text nobody authored
        # as a value. See ``_find_authored``.
        self._comment_spans: list[tuple[int, int]] = []
        for index, line in enumerate(self._lines):
            column = _comment_start(line)
            if column is not None:
                self._comment_spans.append(
                    (offsets[index] + column, offsets[index] + len(line))
                )

    def _find_authored(self, value: str, start: int) -> int:
        """``str.find`` over the raw text, SKIPPING matches that start inside a YAML comment.

        The whole-text forward find searches everything after the cursor — including comments,
        which are never-minted text. A value appearing verbatim in a comment between the cursor
        and its own field would pin the claim's span to the COMMENT — a mis-attribution the
        faithfulness gate provably cannot catch, because the text is identical (WR-01; the
        span-swap failure's sibling). A skipped comment match does NOT advance the cursor, so
        the authored occurrence further down still receives its own span.
        """
        index = self._raw.find(value, start)
        while index != -1 and any(a <= index < b for a, b in self._comment_spans):
            index = self._raw.find(value, index + 1)
        return index

    def mint(
        self, key: str, value: str, topic: str, *, list_item: bool = False
    ) -> Union[Claim, str]:
        idx = self._find_authored(value, self._cursor)
        if idx != -1:
            end = idx + len(value)
            claim = Claim(
                text=value,
                evidence=[Trace.from_source(self._source, idx, end)],
                topics=[topic],
            )
            self._advance(end)
            return claim
        region = self._item_region() if list_item else self._field_region(key)
        if region is not None:
            start, end = region
            claim = Claim(
                text=value,
                evidence=[Trace.from_source(self._source, start, end)],
                topics=[topic],
            )
            if GATE.entails(claim):
                self._advance(end)
                return claim
        return (
            f"field {topic!r} could not be located as a span of the authored file — "
            f"its text is disclosed here, never rendered as a traced claim: {value!r}"
        )

    def _advance(self, pos: int) -> None:
        """Move both cursors past ``pos`` (forward-only; duplicates stay distinct)."""
        self._cursor = max(self._cursor, pos)
        while (
            self._line_cursor + 1 < len(self._lines)
            and self._line_offsets[self._line_cursor + 1] <= self._cursor
        ):
            self._line_cursor += 1

    def _field_region(self, key: str) -> Optional[tuple[int, int]]:
        """The raw span of ``key:``'s value block: after the colon through deeper-indented lines."""
        needle = key + ":"
        for i in range(self._line_cursor, len(self._lines)):
            line = self._lines[i]
            stripped = line.lstrip()
            if not stripped.startswith(needle):
                continue
            indent = len(line) - len(stripped)
            start = self._line_offsets[i] + indent + len(needle)
            j = i + 1
            while j < len(self._lines):
                nxt = self._lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) > indent:
                    j += 1
                    continue
                break
            end = self._line_offsets[j] if j < len(self._lines) else len(self._raw)
            return start, end
        return None

    def _item_region(self) -> Optional[tuple[int, int]]:
        """The raw span of the next UNCONSUMED sequence item's value: after its ``-``
        marker through deeper-indented lines. Per-item — never the whole list — so a
        block-scalar item's region cannot swallow sibling items or advance the cursor
        past them."""
        for i in range(self._line_cursor, len(self._lines)):
            line = self._lines[i]
            stripped = line.lstrip()
            if not (stripped.startswith("- ") or stripped.rstrip() == "-"):
                continue
            indent = len(line) - len(stripped)
            start = self._line_offsets[i] + indent + 1  # after the '-' marker
            if start < self._cursor:
                continue  # this item is already consumed — never re-trace it
            j = i + 1
            while j < len(self._lines):
                nxt = self._lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) > indent:
                    j += 1
                    continue
                break
            end = self._line_offsets[j] if j < len(self._lines) else len(self._raw)
            return start, end
        return None


def absent(field: str) -> str:
    return f"field {field!r} is absent or empty — disclosed, never fabricated"
