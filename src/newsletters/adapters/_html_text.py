"""Deterministic, dependency-free HTML -> text stripper for HTML-only email bodies (Q4).

When a ``.eml`` carries ONLY a ``text/html`` body (no ``text/plain`` alternative), the Email
adapter (CONTEXT decision 6, "emit both") strips it to plain text with THIS helper, makes that
stripped text the transcript body, emits best-effort paragraph claims from it, AND records a
``U5`` ``unextracted[]`` entry disclosing the strip was lossy.

WHY stdlib ``html.parser`` (and nothing else): the AI-optional / minimal-dependency ethos
(CONTEXT decision 5) forbids ``html2text`` / ``BeautifulSoup`` / ``lxml`` — they are either
non-deterministic, opinionated, or C-extensions that break the bare-install gate. ``html.parser``
is event-driven, fully deterministic, and ships with CPython.

WHY ``lossy`` is ALWAYS True: tag-stripping discards structure, links (hrefs), tables, and
emphasis BY CONSTRUCTION. So an HTML-only body's text is never the faithful body of record — it
is offered as best-effort claims AND always flagged in ``unextracted[]`` (U5). The caller never
has to decide lossiness; it is a property of the operation.

Determinism: ``convert_charrefs=True`` resolves entities (``&amp;`` -> ``&``) the same way every
run; the block/skip tag sets are fixed; ``"".join`` of the collected parts is byte-identical
across calls for identical input.
"""

from __future__ import annotations

from html.parser import HTMLParser

# Block-level tags inject a newline boundary on open AND close so adjacent blocks (``<p>A</p>``
# ``<p>B</p>``) do not run together into one paragraph — this is what lets the caller's
# blank-line paragraph segmentation find paragraph boundaries in the stripped text.
_BLOCK = {
    "p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "section", "article", "header", "footer", "ul", "ol", "table",
}

# Non-content tags whose text must be dropped entirely (scripts/styles are active/markup, not
# prose; head metadata is not body text). Skipping these is the injection mitigation (T-04-06):
# no ``<script>`` content survives into a claim.
_SKIP = {"script", "style", "head"}


class _TextExtractor(HTMLParser):
    """Collect visible text, inserting newline boundaries at block edges, dropping skip tags."""

    def __init__(self) -> None:
        # convert_charrefs=True: &amp; -> & deterministically, before handle_data sees it.
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP:
            self._skip_depth += 1
        if tag in _BLOCK:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP and self._skip_depth:
            self._skip_depth -= 1
        if tag in _BLOCK:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)


def strip_html(html: str) -> tuple[str, bool]:
    """Strip ``html`` to plain text. Return ``(text, lossy)``; ``lossy`` is ALWAYS ``True``.

    The text is deterministic (same input -> byte-identical output). ``lossy=True`` is the
    standing signal that the caller must record a ``U5`` ``unextracted[]`` entry: structure,
    links, and emphasis were discarded.
    """
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return "".join(parser._parts), True
