"""Diagrams — inline SVG that renders the story, not just the text.

Editorial diagrams in the Signals language: hard corners, hairline strokes, the 3px
left-accent device, the three-font type system. They are **theme-aware** — every fill and
stroke is a CSS token (`var(--…)`), so the same diagram flips with light/dark like the rest
of the page. No image files, no external calls; the SVG ships inside the HTML.

These are the first 'representational' visuals — a foundation to grow toward richer,
illustrated explainers.
"""

from __future__ import annotations

from xml.sax.saxutils import quoteattr as _quoteattr


def _xe(value: str) -> str:
    """Escape a string for a single-quoted SVG/XML attribute (stdlib-only, no new dep).

    ``quoteattr`` returns the value WITH surrounding quotes; we strip them because the
    callers supply their own ``'…'`` delimiters. Defensive even though hrefs are slug-safe
    (``{slug}.html``) — free text never reaches an attribute unescaped (T-09-08).
    """
    return _quoteattr(value, {'"': "&quot;"})[1:-1]


# Surface accent colors (match templates.SignalColor.css_var)
_SHOW = "var(--color-accent)"
_REPORT = "var(--color-brand-primary)"
_ARTICLE = "var(--color-ink)"
_NEWS = "var(--color-amber)"
_BRAND = "var(--color-brand-primary)"


def _defs(uid: str) -> str:
    return (
        f"<defs><marker id='ah{uid}' markerWidth='9' markerHeight='9' refX='6' refY='3' "
        f"orient='auto'><path d='M0,0 L6,3 L0,6 Z' style='fill:var(--text-dim)'/></marker></defs>"
    )


def _arrow(x1: float, y1: float, x2: float, y2: float, uid: str, dash: bool = False) -> str:
    d = " stroke-dasharray='4 4'" if dash else ""
    return (
        f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
        f"style='stroke:var(--text-dim);stroke-width:1.4'{d} marker-end='url(#ah{uid})'/>"
    )


def _box(x: float, y: float, w: float, h: float, label: str, sub: str = "", accent: str = "var(--line)") -> str:
    out = (
        f"<rect x='{x}' y='{y}' width='{w}' height='{h}' "
        f"style='fill:var(--card);stroke:var(--line);stroke-width:1.4'/>"
        f"<rect x='{x}' y='{y}' width='3' height='{h}' style='fill:{accent}'/>"
    )
    ly = y + h / 2 + (5 if not sub else -3)
    out += (
        f"<text x='{x + w / 2}' y='{ly}' text-anchor='middle' "
        f"style='font-family:var(--font-display);font-size:16px;fill:var(--text)'>{label}</text>"
    )
    if sub:
        out += (
            f"<text x='{x + w / 2}' y='{y + h / 2 + 14}' text-anchor='middle' "
            f"style='font-family:var(--font-mono);font-size:8.5px;letter-spacing:1px;"
            f"fill:var(--text-dim)'>{sub}</text>"
        )
    return out


def _eyebrow(x: float, y: float, text: str, color: str = "var(--text-dim)", anchor: str = "start") -> str:
    return (
        f"<text x='{x}' y='{y}' text-anchor='{anchor}' style='font-family:var(--font-mono);"
        f"font-size:9.5px;letter-spacing:1.6px;fill:{color}'>{text}</text>"
    )


def _svg(uid: str, vb: str, inner: str) -> str:
    return (
        f"<svg viewBox='{vb}' role='img' xmlns='http://www.w3.org/2000/svg'>"
        f"{_defs(uid)}{inner}</svg>"
    )


def two_layer() -> str:
    """The headline: two layers (Truth / Surface) with the review gate between them."""
    u = "tl"
    p = []
    # Truth layer
    p.append(_eyebrow(24, 26, "TRUTH — WHAT IS REAL", _BRAND))
    p.append(_box(24, 40, 200, 66, "Source", "EVENT CAPTURED", _BRAND))
    p.append(_box(280, 40, 200, 66, "Claim + Trace", "STATEMENT + EVIDENCE", _BRAND))
    p.append(_box(536, 40, 200, 66, "Distillation", "THE REVIEWED SYNTHESIS", _BRAND))
    p.append(_arrow(224, 73, 278, 73, u))
    p.append(_arrow(480, 73, 534, 73, u))
    # Gate
    p.append(f"<line x1='24' y1='168' x2='736' y2='168' style='stroke:var(--color-amber);"
             f"stroke-width:1.2' stroke-dasharray='5 5'/>")
    p.append(_eyebrow(380, 150, "REVIEW GATE — DRAFT › IN REVIEW › PUBLISHED",
                      "var(--color-amber)", anchor="middle"))
    # Surface layer
    p.append(_eyebrow(24, 206, "SURFACE — HOW IT'S SHOWN"))
    surf = [("The Show", "RECORDED · BIWEEKLY", _SHOW), ("The Report", "APPROVED · PER EVENT", _REPORT),
            ("The Article", "PEER · ON DEMAND", _ARTICLE), ("Newsletters", "RE-CUT · WEEKLY", _NEWS)]
    xs = [24, 206, 388, 570]
    for (lbl, sub, acc), x in zip(surf, xs):
        p.append(_box(x, 222, 164, 66, lbl, sub, acc))
    # Fan from the one distillation down through the gate to every surface
    for x in xs:
        p.append(_arrow(636, 108, x + 82, 220, u, dash=True))
    return _svg(u, "0 0 760 300", "".join(p))


def fanout(links: dict[str, str] | None = None) -> str:
    """One reviewed record fans out into the four surfaces.

    When ``links`` (a ``label -> href`` map) is supplied, each surface box is wrapped in an
    SVG ``<a href=…>`` anchor so the diagram is navigable with NO JavaScript (SVG anchors are
    valid SVG). ``None`` (the default) keeps the current static behavior — no anchors.
    """
    u = "fo"
    p = [_eyebrow(24, 24, "ONE RECORD → FOUR SURFACES", _BRAND)]
    p.append(_box(24, 96, 220, 88, "One reviewed record", "SOURCE → CLAIM → DISTILLATION", _BRAND))
    rows = [("The Show", "BIWEEKLY", _SHOW, 20), ("The Report", "PER EVENT", _REPORT, 86),
            ("The Article", "ON DEMAND", _ARTICLE, 152), ("Newsletters", "WEEKLY · PER READER", _NEWS, 218)]
    for lbl, sub, acc, y in rows:
        box = (
            _box(470, y, 226, 48, lbl, "", acc)
            + _eyebrow(470 + 113, y + 40, sub, "var(--text-dim)", anchor="middle")
        )
        href = (links or {}).get(lbl)
        if href:
            box = f"<a href='{_xe(href)}'>{box}</a>"
        p.append(box)
        p.append(_arrow(244, 140, 466, y + 24, u, dash=True))
    return _svg(u, "0 0 720 290", "".join(p))


def personalization() -> str:
    """One newsletter record, re-cut per reader — same facts, new emphasis."""
    u = "pz"
    p = [_eyebrow(24, 24, "SAME RECORD · RE-CUT PER READER", _NEWS)]
    p.append(_box(24, 78, 210, 72, "The Weekly Signal", "ONE REVIEWED RECORD", _NEWS))
    readers = [("JJ · Architect", "LEADS WITH: VISION", 18), ("Nate · Engineer", "LEADS WITH: CORE", 84),
               ("New Contributor", "LEADS WITH: START HERE", 150)]
    for lbl, sub, y in readers:
        p.append(_box(456, y, 240, 50, lbl, sub, _NEWS))
        p.append(_arrow(234, 114, 452, y + 25, u, dash=True))
    p.append(_eyebrow(24, 232, "PRIVATE CORPUS READ AT RENDER, THEN DISCARDED — NEVER SERIALIZED",
                      "var(--text-dim)"))
    return _svg(u, "0 0 720 250", "".join(p))
