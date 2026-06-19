"""Static HTML renderer — Surface objects → token-accurate, self-contained pages.

This is the "show" layer: it takes typed ``Surface`` objects and renders them with the
exact tokens from ``design-reference/signals/tokens.css`` (flat editorial, hard corners,
the 3px left-accent device, the three-font system, light + dark). No server, no build —
each page is a standalone HTML file you can open or send.

Typed config drives the structure; only the prose lives in templated strings (Decision 2).
"""

from __future__ import annotations

import html
from typing import Iterable

from .diagrams import fanout as _fanout_svg
from .semantic import (
    ChaptersBlock,
    ClaimsBlock,
    DiagramBlock,
    FanoutBlock,
    ItemsBlock,
    KpiStripBlock,
    ProseBlock,
    PromptBlock,
    QuoteBlock,
    RationaleBlock,
    ReviewState,
    Surface,
)

# --------------------------------------------------------------------------- #
# Tokens — ported 1:1 from signals/tokens.css, plus chrome + layout + blocks
# --------------------------------------------------------------------------- #

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:ital,wght@0,400;0,500;1,400&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');
*,*::before,*::after{box-sizing:border-box}
.signals{
  --color-ink:#0a0a0f;--color-paper:#f5f3ee;--color-white:#fff;
  --color-brand-primary:#0068b5;--color-brand-mid:#005a9e;--color-brand-light:#e8f2fb;--color-brand-dark:#003d6b;
  --color-accent:#d4622a;--color-amber:#c8860a;--color-green:#2f7d4f;
  --color-rule:#c8c4bb;--color-muted:#6b6860;--color-surface-low:#f0ede8;--color-surface-mid:#e8e4de;
  --bg:var(--color-paper);--card:var(--color-white);--text:var(--color-ink);--text-dim:var(--color-muted);--line:var(--color-rule);
  --chrome-bg:#0a0a0f;--chrome-fg:#f5f3ee;--chrome-dim:rgba(245,243,238,.62);--chrome-line:rgba(255,255,255,.12);
  --font-display:'DM Serif Display',Georgia,serif;--font-body:'Instrument Sans',system-ui,sans-serif;--font-mono:'DM Mono','Courier New',monospace;
  --radius:0px;--dur-base:200ms;--dur-slow:380ms;--ease-out:cubic-bezier(0,0,.2,1);--signal:var(--color-brand-primary);
  background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  min-height:100vh;
}
.signals[data-theme=dark]{
  --color-ink:#f0ede8;--color-paper:#0f0f14;--color-white:#1a1a22;
  --color-brand-primary:#3f9ae0;--color-brand-mid:#5aa9e6;--color-brand-light:#15293a;--color-brand-dark:#0c1b29;
  --color-accent:#e07a45;--color-amber:#d99a2a;--color-green:#4fa873;
  --color-rule:rgba(240,237,232,.16);--color-muted:rgba(240,237,232,.55);--color-surface-low:#16161d;--color-surface-mid:#20202a;
  --chrome-bg:#07070b;--chrome-line:rgba(255,255,255,.10);
}
.signals h1,.signals h2,.signals h3,.signals h4,.signals p,.signals ul,.signals figure{margin:0}
.signals ul{padding:0;list-style:none}.signals a{color:inherit;text-decoration:none}.signals em{font-style:italic}
.signals ::selection{background:var(--color-brand-primary);color:#fff}
.sg-display{font-family:var(--font-display);font-weight:400;line-height:1.08;letter-spacing:-.02em;color:var(--text)}
.sg-eyebrow{font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:.20em;color:var(--signal);display:inline-flex;align-items:center;gap:10px}
.sg-mono{font-family:var(--font-mono);font-size:11px;letter-spacing:.02em;color:var(--text-dim)}
.sg-rule{height:1px;background:var(--line);border:0;flex:1}
.sg-divider{display:flex;align-items:center;gap:16px;margin:8px 0 22px}
.sg-tag{font-family:var(--font-mono);font-size:10px;text-transform:uppercase;letter-spacing:.12em;padding:4px 8px;line-height:1;display:inline-flex;align-items:center;gap:6px;border:1px solid transparent;white-space:nowrap}
.sg-tag.cat{background:var(--color-surface-low);color:var(--text-dim)}
.sg-tag.live{background:var(--color-accent);color:#fff}
.sg-tag.published{background:var(--color-brand-primary);color:#fff}
.sg-tag.draft{background:transparent;color:var(--text-dim);border-color:var(--line)}
.sg-tag.review{background:transparent;color:var(--color-amber);border-color:var(--color-amber)}
.sg-tag.peer{background:var(--color-brand-light);color:var(--color-brand-primary)}
.sg-tag.featured{background:var(--color-ink);color:var(--color-paper)}
.sg-dot{width:6px;height:6px;border-radius:50%;background:currentColor;display:inline-block}
.sg-gate{display:inline-flex;align-items:center;font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:.14em}
.sg-gate-step{padding:4px 10px;color:var(--text-dim);opacity:.4}
.sg-gate-step.done{opacity:1;color:var(--text)}
.sg-gate-step.current{opacity:1;font-weight:500}
.sg-gate-step.current.s-in_review{color:var(--color-amber)}
.sg-gate-step.current.s-published{color:var(--color-brand-primary)}
.sg-gate-step.current.s-draft{color:var(--text)}
.sg-gate-sep{color:var(--line);padding:0 2px}
.sg-btn{font-family:var(--font-mono);font-size:11px;text-transform:uppercase;letter-spacing:.10em;padding:11px 18px;border:1px solid var(--color-brand-primary);background:var(--color-brand-primary);color:#fff;cursor:pointer;display:inline-flex;align-items:center;gap:8px}
.sg-btn.ghost{background:transparent;color:var(--text);border-color:var(--line)}
.sg-chip{display:inline-flex;align-items:center;gap:10px}
.sg-avatar{width:32px;height:32px;border-radius:50%;background:var(--color-brand-dark);color:#fff;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-size:14px;flex:0 0 auto}
.sg-chip-name{font-weight:600;font-size:13px;line-height:1.2;color:var(--text)}
.sg-chip-role{font-family:var(--font-mono);font-size:10px;color:var(--text-dim);letter-spacing:.04em}
.sg-card{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--signal);padding:20px}
.sg-kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));background:var(--color-surface-low);border-left:3px solid var(--signal)}
.sg-kpi-cell{padding:16px 20px;border-right:1px solid var(--line)}
.sg-kpi-cell:last-child{border-right:0}
.sg-kpi-label{font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:.14em;color:var(--text-dim);margin-bottom:8px}
.sg-kpi-value{font-family:var(--font-display);font-size:34px;line-height:1;color:var(--text)}
.sg-kpi-delta{font-family:var(--font-mono);font-size:11px;margin-top:6px}
.sg-kpi-delta.up{color:var(--color-green)}.sg-kpi-delta.down{color:var(--color-accent)}
.sg-prompt{background:#0c0c12;border-left:3px solid var(--signal);color:#d8d6cf;font-family:var(--font-mono);font-size:12px;line-height:1.7}
.sg-prompt-head{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,.08)}
.sg-prompt-label{font-size:9.5px;text-transform:uppercase;letter-spacing:.18em;color:rgba(255,255,255,.5)}
.sg-prompt-body{padding:16px;white-space:pre-wrap;margin:0}
.sg-quote{background:var(--color-brand-light);border-left:3px solid var(--signal);padding:28px 32px 24px;position:relative}
.sg-quote-mark{font-family:var(--font-display);font-size:90px;line-height:.6;color:var(--signal);opacity:.18;position:absolute;top:24px;left:18px}
.sg-quote-text{font-family:var(--font-display);font-style:italic;font-size:22px;line-height:1.35;color:var(--text);position:relative}
.sg-quote-attr{font-family:var(--font-mono);font-size:11px;color:var(--text-dim);margin-top:14px;letter-spacing:.04em}
/* chrome */
.nl-nav{position:sticky;top:0;z-index:50;background:var(--chrome-bg);color:var(--chrome-fg);height:60px;display:flex;align-items:center;justify-content:space-between;padding:0 28px;border-bottom:1px solid var(--chrome-line)}
.nl-brand{font-family:var(--font-display);font-size:18px;color:var(--chrome-fg);display:flex;align-items:center;gap:10px}
.nl-brand .sub{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--chrome-dim)}
.nl-links{display:flex;gap:22px;align-items:center}
.nl-links a{font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--chrome-dim);padding:4px 0;border-bottom:2px solid transparent}
.nl-links a.active{color:var(--chrome-fg);border-bottom-color:var(--signal)}
.nl-toggle{font-family:var(--font-mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--chrome-dim);background:transparent;border:1px solid var(--chrome-line);padding:6px 10px;cursor:pointer}
/* layout */
.wrap{max-width:1180px;margin:0 auto;padding:56px 44px 40px}
.masthead{border-top:3px solid var(--signal);padding-top:26px;margin-bottom:30px}
.masthead .tags{display:flex;gap:8px;align-items:center;margin:14px 0}
.mast-title{font-size:46px;max-width:900px;margin:10px 0 16px}
.mast-meta{display:flex;flex-wrap:wrap;gap:18px;align-items:center;margin-top:14px;font-family:var(--font-mono);font-size:11px;color:var(--text-dim);letter-spacing:.03em}
.byline{display:flex;gap:16px;flex-wrap:wrap;margin-top:8px}
.block{margin:30px 0}
.block-h{font-family:var(--font-display);font-size:26px;margin-bottom:16px;color:var(--text)}
.prose p{font-size:16px;line-height:1.65;max-width:680px;margin:0 0 14px;color:var(--text)}
.claim{padding:14px 0 14px 18px;border-left:2px solid var(--line);max-width:760px;margin-bottom:6px}
.claim.untraced{border-left-color:var(--color-amber)}
.claim-text{font-size:15.5px;line-height:1.55;color:var(--text)}
.claim-ev{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;align-items:center}
.ev-chip{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.06em;color:var(--text-dim);background:var(--color-surface-low);padding:3px 7px}
.conf{font-family:var(--font-mono);font-size:9.5px;color:var(--text-dim)}
.chapter{display:grid;grid-template-columns:64px 1fr;gap:18px;padding:14px 0;border-top:1px solid var(--line)}
.chapter .t{font-family:var(--font-mono);font-size:11px;color:var(--signal)}
.chapter .ti{font-family:var(--font-display);font-size:18px;color:var(--text)}
.chapter .bo{font-size:14px;color:var(--text-dim);margin-top:4px}
.item{padding:18px 0;border-top:1px solid var(--line)}
.item .ti{font-family:var(--font-display);font-size:21px;margin:8px 0 6px}
.item .bo{font-size:15px;line-height:1.6;color:var(--text);max-width:700px}
.rationale{background:var(--color-brand-light);border-left:3px solid var(--signal);padding:18px 22px;max-width:760px}
.rationale .h{font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:.14em;color:var(--signal);margin-bottom:8px}
.diagram{border:1px solid var(--line);border-left:3px solid var(--signal);background:var(--card);padding:24px 26px}
.diagram svg{width:100%;height:auto;display:block;overflow:visible}
.diagram .dh{font-family:var(--font-mono);font-size:9.5px;text-transform:uppercase;letter-spacing:.16em;color:var(--signal);margin-bottom:16px}
.diagram figcaption{font-family:var(--font-mono);font-size:10.5px;color:var(--text-dim);margin-top:16px;letter-spacing:.03em;line-height:1.5}
.fanout{display:flex;flex-direction:column;gap:0;border-top:1px solid var(--line)}
.fan-row{display:grid;grid-template-columns:120px 1fr;gap:18px;padding:14px 0;border-bottom:1px solid var(--line);align-items:baseline}
.nl-foot{background:var(--chrome-bg);color:var(--chrome-dim);border-top:3px solid var(--color-brand-primary);padding:40px 44px;margin-top:50px;font-family:var(--font-mono);font-size:11px;letter-spacing:.04em}
.nl-foot .row{max-width:1180px;margin:0 auto;display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px}
.nl-foot a{color:var(--chrome-fg)}
/* library */
.lib-surface{display:grid;grid-template-columns:64px 1fr 220px;gap:24px;align-items:baseline;padding:20px 0;border-bottom:1px solid var(--line)}
.lib-idx{font-family:var(--font-display);font-size:30px;color:var(--signal)}
.lib-title{font-family:var(--font-display);font-size:23px;color:var(--text)}
.lib-tail{font-style:italic;color:var(--text-dim);font-size:14px}
.lib-meta{text-align:right;font-family:var(--font-mono);font-size:10px;color:var(--text-dim);letter-spacing:.04em}
@media(max-width:820px){.wrap{padding:40px 22px}.mast-title{font-size:34px}.lib-surface{grid-template-columns:44px 1fr}.lib-meta{grid-column:1/-1;text-align:left}.nl-links{display:none}}
"""

_TOGGLE_JS = (
    "<script>(function(){var r=document.getElementById('root'),b=document.getElementById('tg');"
    "if(!b)return;function sync(){var dark=r.getAttribute('data-theme')==='dark';"
    "b.textContent=dark?'\\u263e Dark':'\\u2600 Light';}sync();"
    "b.addEventListener('click',function(){var dark=r.getAttribute('data-theme')==='dark';"
    "r.setAttribute('data-theme',dark?'light':'dark');sync();});})();</script>"
)

_NAV_ITEMS = [("Start here", "index.html"), ("Newsletters", None), ("Articles", None), ("The Show", None)]


def _e(s: str) -> str:
    return html.escape(s or "")


def _gate_badge(state: ReviewState) -> str:
    steps = [("Draft", ReviewState.DRAFT), ("In Review", ReviewState.IN_REVIEW), ("Published", ReviewState.PUBLISHED)]
    order = [ReviewState.DRAFT, ReviewState.IN_REVIEW, ReviewState.PUBLISHED]
    cur = order.index(state)
    out = ['<span class="sg-gate">']
    for i, (label, st) in enumerate(steps):
        cls = "sg-gate-step"
        if i < cur:
            cls += " done"
        elif i == cur:
            cls += f" current s-{st.value}"
        out.append(f'<span class="{cls}">{label}</span>')
        if i < len(steps) - 1:
            out.append('<span class="sg-gate-sep">&rsaquo;</span>')
    out.append("</span>")
    return "".join(out)


def _status_tag(surface: Surface) -> str:
    state = surface.gate
    if surface.kind == "article" and state is ReviewState.IN_REVIEW:
        return '<span class="sg-tag peer"><span>&#10003;</span> Peer review</span>'
    cls = {ReviewState.DRAFT: "draft", ReviewState.IN_REVIEW: "review", ReviewState.PUBLISHED: "published"}[state]
    label = {ReviewState.DRAFT: "Draft", ReviewState.IN_REVIEW: "In Review", ReviewState.PUBLISHED: "Published"}[state]
    return f'<span class="sg-tag {cls}">{label}</span>'


def _chip(name: str) -> str:
    initials = "".join(p[0] for p in name.split()[:2]).upper() or name[:2].upper()
    return (
        f'<span class="sg-chip"><span class="sg-avatar">{_e(initials)}</span>'
        f'<span><span class="sg-chip-name">{_e(name)}</span></span></span>'
    )


def _block_html(b) -> str:
    if isinstance(b, ProseBlock):
        paras = "".join(f"<p>{_e(p)}</p>" for p in b.text.split("\n\n") if p.strip())
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block prose">{h}{paras}</div>'
    if isinstance(b, ClaimsBlock):
        rows = []
        for c in b.claims:
            ev = "".join(
                f'<span class="ev-chip">{_e(t.source_id)}{(":" + _e(t.locator)) if t.locator else ""}</span>'
                for t in c.evidence
            ) or '<span class="ev-chip" style="color:var(--color-amber)">unsubstantiated &rarr; missing[]</span>'
            conf = f'<span class="conf">conf {c.confidence:.2f}</span>'
            cls = "claim" if c.is_traced else "claim untraced"
            rows.append(
                f'<li class="{cls}"><div class="claim-text">{_e(c.text)}</div>'
                f'<div class="claim-ev">{ev}{conf}</div></li>'
            )
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block">{h}<ul>{"".join(rows)}</ul></div>'
    if isinstance(b, KpiStripBlock):
        cells = "".join(
            f'<div class="sg-kpi-cell"><div class="sg-kpi-label">{_e(i.label)}</div>'
            f'<div class="sg-kpi-value">{_e(i.value)}</div>'
            + (f'<div class="sg-kpi-delta {i.dir}">{_e(i.delta)}</div>' if i.delta else "")
            + "</div>"
            for i in b.items
        )
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block">{h}<div class="sg-kpi">{cells}</div></div>'
    if isinstance(b, QuoteBlock):
        attr = f'<div class="sg-quote-attr">{_e(b.attr)}</div>' if b.attr else ""
        return (
            f'<div class="block"><figure class="sg-quote"><span class="sg-quote-mark">&ldquo;</span>'
            f'<div class="sg-quote-text">{_e(b.text)}</div>{attr}</figure></div>'
        )
    if isinstance(b, ChaptersBlock):
        rows = "".join(
            f'<div class="chapter"><div class="t">{_e(c.time)}</div>'
            f'<div><div class="ti">{_e(c.title)}</div><div class="bo">{_e(c.body)}</div></div></div>'
            for c in b.chapters
        )
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block">{h}{rows}</div>'
    if isinstance(b, ItemsBlock):
        rows = "".join(
            f'<div class="item">'
            + (f'<span class="sg-tag cat">{_e(i.tag)}</span>' if i.tag else "")
            + f'<div class="ti">{_e(i.title)}</div><div class="bo">{_e(i.body)}</div></div>'
            for i in b.items
        )
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block">{h}{rows}</div>'
    if isinstance(b, PromptBlock):
        return (
            f'<div class="block"><div class="sg-prompt"><div class="sg-prompt-head">'
            f'<span class="sg-prompt-label">{_e(b.label)}</span>'
            f'<span class="sg-prompt-label">copy</span></div>'
            f'<pre class="sg-prompt-body">{_e(b.body)}</pre></div></div>'
        )
    if isinstance(b, FanoutBlock):
        rows = "".join(
            f'<div class="fan-row"><span class="sg-tag cat">{_e(l.kind)}</span>'
            f'<span class="lib-title" style="font-size:18px">{_e(l.title)}</span></div>'
            for l in b.links
        )
        h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
        return f'<div class="block">{h}<div class="fanout">{rows}</div></div>'
    if isinstance(b, RationaleBlock):
        h = f'<div class="h">{_e(b.heading)}</div>' if b.heading else ""
        return f'<div class="block"><div class="rationale">{h}<div class="bo">{_e(b.text)}</div></div></div>'
    if isinstance(b, DiagramBlock):
        h = f'<div class="dh">{_e(b.title)}</div>' if b.title else ""
        cap = f"<figcaption>{_e(b.caption)}</figcaption>" if b.caption else ""
        return f'<div class="block"><figure class="diagram">{h}{b.svg}{cap}</figure></div>'
    return ""


def _nav(active: str, theme: str = "light") -> str:
    links = "".join(
        f'<a href="{href or "index.html"}" class="{"active" if label == active else ""}">{label}</a>'
        for label, href in _NAV_ITEMS
    )
    # Label reflects the CURRENT theme (sun = light, moon = dark); JS keeps it in sync on
    # toggle, and this static default is correct even with JavaScript disabled.
    label = "&#9790; Dark" if theme == "dark" else "&#9728; Light"
    return (
        '<nav class="nl-nav"><div class="nl-brand">Newsletters '
        '<span class="sub">working in the open</span></div>'
        f'<div class="nl-links">{links}</div>'
        f'<button class="nl-toggle" id="tg">{label}</button></nav>'
    )


def _footer() -> str:
    return (
        '<footer class="nl-foot"><div class="row">'
        '<div>Turn information into conversation. Conversation into action.</div>'
        '<div>Open source &middot; MIT &middot; self-hostable &middot; human-in-the-loop by design</div>'
        '<div>Renders without JavaScript &middot; WCAG AA</div>'
        '</div></footer>'
    )


def _page(*, title: str, signal_css: str, body: str, active: str, theme: str = "light") -> str:
    return (
        f"<!doctype html><html lang=en><head><meta charset=utf-8>"
        f'<meta name=viewport content="width=device-width,initial-scale=1">'
        f"<title>{_e(title)} — Newsletters</title><style>{_CSS}</style></head><body>"
        f'<div class="signals" id="root" data-theme="{theme}" style="--signal:{signal_css}">'
        f"{_nav(active, theme)}{body}{_footer()}</div>{_TOGGLE_JS}</body></html>"
    )


def _active_for(surface: Surface) -> str:
    return {"newsletter": "Newsletters", "article": "Articles", "show": "The Show"}.get(
        surface.kind, "Start here"
    )


def render_surface(surface: Surface, *, theme: str = "light") -> str:
    """Render one ``Surface`` to a complete, standalone HTML page."""
    t = surface.template
    meta_bits = [
        f"{t.display_name} &middot; {t.cadence.label}",
        f"scope: {t.scope.value}",
        f"gate policy: {t.review_policy.describe()}",
    ]
    if surface.provenance:
        meta_bits.append(f"captured via {_e(surface.provenance.tool)}")
    if surface.lineage.derived_from:
        meta_bits.append("derived from " + ", ".join(_e(x) for x in surface.lineage.derived_from))
    byline = (
        '<div class="byline">' + "".join(_chip(b) for b in surface.byline) + "</div>"
        if surface.byline
        else ""
    )
    audience = (
        f'<div class="mast-meta">Re-cut for <strong style="color:var(--signal)">'
        f"{_e(surface.audience_label)}</strong></div>"
        if surface.audience_label
        else ""
    )
    blocks = "".join(_block_html(b) for b in surface.blocks)
    masthead = (
        f'<div class="masthead"><div class="sg-eyebrow">{_e(surface.eyebrow)}</div>'
        f'<div class="tags"><span class="sg-tag featured">{_e(t.display_name)}</span>'
        f"{_status_tag(surface)}</div>"
        f'<h1 class="sg-display mast-title">{_e(surface.title)}</h1>'
        f"{byline}{audience}"
        f'<div class="mast-meta">{" &middot; ".join(meta_bits)}</div>'
        f'<div class="mast-meta">{_gate_badge(surface.gate)}</div></div>'
    )
    body = f'<main class="wrap">{masthead}{blocks}</main>'
    return _page(
        title=surface.title,
        signal_css=t.signal_color.css_var,
        body=body,
        active=_active_for(surface),
        theme=theme,
    )


def render_library(surfaces: Iterable[Surface], *, theme: str = "light") -> str:
    """Render the Library/Hub index — the durable archive of every surface."""
    surfaces = list(surfaces)
    rows = []
    for i, s in enumerate(surfaces, 1):
        rows.append(
            f'<a class="lib-surface" href="{_e(s.id)}.html" style="--signal:{s.template.signal_color.css_var}">'
            f'<span class="lib-idx">{i:02d}</span>'
            f'<span><span class="lib-title">{_e(s.title)}</span> '
            f'<span class="lib-tail">— {_e(s.template.tagline)}</span></span>'
            f'<span class="lib-meta">{_e(s.template.display_name)}<br>{_e(s.template.cadence.label)}'
            f'<br>{_e(s.gate.value)}</span></a>'
        )
    intro = (
        '<div class="masthead"><div class="sg-eyebrow">The Library &middot; working in the open</div>'
        '<h1 class="sg-display mast-title">One reviewed record, fanned out.</h1>'
        '<div class="prose"><p>Every surface below is cut from the same traced, reviewed truth — '
        'built in the open as we built Newsletters itself. Reports are the investigations we '
        'approved; the Article is a lesson awaiting peer review; the Newsletter re-cuts the week '
        'per reader; the Show records the process.</p></div>'
        '<figure class="diagram" style="margin-top:24px">'
        '<div class="dh">How it fans out</div>' + _fanout_svg()
        + '<figcaption>One reviewed record, four surfaces — the Newsletter re-cuts per '
        'reader from their own private corpus.</figcaption></figure></div>'
    )
    body = f'<main class="wrap">{intro}{"".join(rows)}</main>'
    return _page(title="The Library", signal_css="var(--color-brand-primary)", body=body, active="Start here", theme=theme)
