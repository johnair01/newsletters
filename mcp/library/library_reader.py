"""Read one newsletters Library from disk. Read-only, stdlib only.

A Library is the folder the engine already writes (see docs/runs/2026-11-07/lanes/D-connector/spec.md):

    <library>/ids.json          ledger: slug -> {ref, type, issue, date}
    <library>/site/<slug>.html  one rendered edition per ledger slug

This module never writes, never touches the network, and never joins user input into a path:
a slug is looked up in the ledger first, and only ledger keys reach the filesystem.
Only Published editions are served (decision D2): the review gate stays the gate.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

PUBLISHED = "published"

# render._status_tag emits exactly these classes; "peer" is an Article in review.
_STATUS_CLASSES = {
    "published": "published",
    "review": "in_review",
    "peer": "in_review",
    "draft": "draft",
}
_SKIP_TAGS = {"script", "style", "nav", "svg", "noscript", "template"}
_BLOCK_TAGS = {
    "p", "div", "section", "article", "header", "footer", "aside", "li", "ul", "ol",
    "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "table", "blockquote", "pre",
    "figure", "figcaption", "dl", "dt", "dd", "hr",
}
_SNIPPET_CHARS = 240


class LibraryError(Exception):
    """A request the Library cannot answer (unknown slug, unpublished edition, bad folder)."""


class _EditionParser(HTMLParser):
    """Pull title, status and the readable text of <main> out of one rendered edition."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = 0
        self.skip = 0
        self.in_title_h1 = False
        self.title_parts: list[str] = []
        self.status: str | None = None
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = (dict(attrs).get("class") or "").split()
        if tag == "main":
            self.in_main += 1
            return
        if not self.in_main:
            return
        if tag in _SKIP_TAGS:
            self.skip += 1
            return
        if tag == "span" and "sg-tag" in classes and self.status is None:
            for cls in classes:
                if cls in _STATUS_CLASSES:
                    self.status = _STATUS_CLASSES[cls]
                    break
        if tag == "h1" and "mast-title" in classes and not self.title_parts:
            self.in_title_h1 = True
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
            return
        if not self.in_main:
            return
        if tag in _SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag == "h1":
            self.in_title_h1 = False
        if tag in _BLOCK_TAGS:
            self.parts.append("\n")
        elif tag in ("span", "a", "strong", "em", "code", "td", "th"):
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.in_main or self.skip:
            return
        if self.in_title_h1:
            self.title_parts.append(data)
        self.parts.append(data)


def _clean(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    out: list[str] = []
    for line in lines:
        if line:
            out.append(line)
        elif out and out[-1] != "":
            out.append("")
    return "\n".join(out).strip()


def parse_edition_html(html: str) -> dict[str, str | None]:
    """Return {title, status, text} for one rendered edition page."""
    parser = _EditionParser()
    parser.feed(html)
    parser.close()
    return {
        "title": _clean("".join(parser.title_parts)) or None,
        "status": parser.status,
        "text": _clean("".join(parser.parts)),
    }


def _entry(ledger: dict, slug: str) -> dict:
    entry = ledger.get(slug)
    return entry if isinstance(entry, dict) else {}


class Library:
    """One Library folder. Cheap to build; reads files on demand."""

    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.ledger_path = self.root / "ids.json"
        self.site = self.root / "site"
        if not self.ledger_path.is_file() or not self.site.is_dir():
            raise LibraryError(
                f"{self.root} is not a Library: expected ids.json and a site/ folder"
            )

    @property
    def name(self) -> str:
        return self.root.name

    def _ledger(self) -> dict[str, dict]:
        data = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise LibraryError("ids.json is not a slug -> entry mapping")
        return data

    def _load(self, slug: str, entry: dict) -> dict | None:
        """Parse one ledger edition; None if its HTML is not on disk."""
        page = self.site / f"{slug}.html"
        if not page.is_file():
            return None
        parsed = parse_edition_html(page.read_text(encoding="utf-8"))
        return {
            "slug": slug,
            "ref": entry.get("ref") or "",
            "type": entry.get("type") or "",
            "title": parsed["title"] or slug,
            "status": parsed["status"] or "unknown",
            "issue": entry.get("issue"),
            "date": entry.get("date"),
            "text": parsed["text"],
        }

    def _all(self) -> list[dict]:
        ledger = self._ledger()
        out = []
        for slug in sorted(ledger):
            ed = self._load(slug, _entry(ledger, slug))
            if ed is not None:
                out.append(ed)
        return out

    # ---- the three tools -------------------------------------------------------------

    def list_editions(self) -> dict:
        editions = self._all()
        published = [e for e in editions if e["status"] == PUBLISHED]
        return {
            "library": self.name,
            "editions": [{k: v for k, v in e.items() if k != "text"} for e in published],
            "withheld_unpublished": len(editions) - len(published),
        }

    def read_edition(self, slug: str) -> dict:
        ledger = self._ledger()
        if not isinstance(slug, str) or slug not in ledger:
            raise LibraryError(f"No edition with slug {slug!r} in this Library")
        ed = self._load(slug, _entry(ledger, slug))
        if ed is None:
            raise LibraryError(f"Edition {slug!r} is in the ledger but has no page on disk")
        if ed["status"] != PUBLISHED:
            raise LibraryError(
                f"Edition {slug!r} is not published (status: {ed['status']}); "
                "only published editions are served"
            )
        return ed

    def search(self, query: str, limit: int = 10) -> dict:
        words = [w for w in re.split(r"\s+", (query or "").lower()) if w]
        if not words:
            raise LibraryError("Search query is empty")
        limit = max(1, min(int(limit), 50))
        results = []
        for ed in self._all():
            if ed["status"] != PUBLISHED:
                continue
            haystack = ed["text"]  # the title h1 sits inside <main>, so it is already here
            low = haystack.lower()
            counts = [low.count(w) for w in words]
            if not all(counts):
                continue
            first = min(low.find(w) for w in words)
            start = max(0, first - _SNIPPET_CHARS // 3)
            snippet = re.sub(r"\s+", " ", haystack[start : start + _SNIPPET_CHARS]).strip()
            results.append(
                {
                    "slug": ed["slug"],
                    "ref": ed["ref"],
                    "type": ed["type"],
                    "title": ed["title"],
                    "hits": sum(counts),
                    "snippet": ("..." if start else "") + snippet + "...",
                }
            )
        results.sort(key=lambda r: (-r["hits"], r["slug"]))
        return {"query": query, "results": results[:limit]}
