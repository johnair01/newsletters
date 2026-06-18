"""Static HTML renderer — Surface objects → token-accurate, self-contained pages.

This is the "show" layer: it takes typed ``Surface`` objects and renders them with the
exact tokens from ``design-reference/signals/tokens.css`` (flat editorial, hard corners,
the 3px left-accent device, the three-font system, light + dark). No server, no build —
each page is a standalone HTML file you can open or send.

Typed config drives the structure; only the prose lives in templated strings (Decision 2).
"""

from __future__ import annotations

import html
from typing import TypedDict

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
from .site import Page, Site

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
/* eyebrow variants (Home accent/brand dividers) */
.sg-eyebrow.brand{color:var(--color-brand-primary)}
.sg-eyebrow.accent{color:var(--color-accent)}
/* Home — section shells + per-section grids (tokens only, --radius:0 throughout) */
.home-sec{max-width:1180px;margin:0 auto;padding:72px 44px 0;scroll-margin-top:80px}
.home-hero{padding:78px 44px 56px;border-bottom:1px solid var(--line)}
.home-h1{font-size:72px;line-height:1.03;max-width:960px;margin-top:26px}
.home-lead{font-size:18.5px;line-height:1.6;color:var(--text-dim);max-width:620px;margin-top:28px}
.home-btns{display:flex;gap:14px;margin-top:34px;flex-wrap:wrap}
.home-mono-line{margin-top:26px}
.nl-2col{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
.home-why-stmt{font-family:var(--font-display);font-size:30px;line-height:1.28;margin-top:22px;max-width:460px}
.home-why-body p{font-size:16.5px;line-height:1.72;color:var(--text);max-width:560px}
.home-why-body p+p{color:var(--text-dim);margin-top:16px}
.home-h2{font-size:44px;line-height:1.08;margin-top:22px;max-width:760px}
.home-sec-lead{font-size:16.5px;line-height:1.62;color:var(--text-dim);max-width:620px;margin-top:16px}
.nl-demo-grid{display:grid;grid-template-columns:300px 1fr;gap:36px;align-items:start;margin-top:32px}
.demo-pick{position:sticky;top:88px}
.demo-pick-label{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--text-dim);margin-bottom:14px}
.demo-persona{text-align:left;padding:14px 16px;border:1px solid var(--line);border-left:3px solid var(--line);display:flex;align-items:center;gap:12px;margin-bottom:8px}
.demo-persona.on{background:var(--card);box-shadow:0 4px 18px rgba(0,0,0,.07)}
.demo-persona .pn{display:block;font-size:14px;font-weight:600;color:var(--text)}
.demo-persona .pr{display:block;font-family:var(--font-mono);font-size:10.5px;color:var(--text-dim);margin-top:2px}
.demo-same{margin-top:18px;border:1px solid var(--line);border-left:3px solid var(--color-ink);padding:14px 16px;background:var(--color-surface-low)}
.demo-same p{font-size:12.5px;line-height:1.5;color:var(--text);margin-top:7px}
.demo-letter{background:var(--card);border:1px solid var(--line)}
.demo-letter-head{padding:22px 30px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.demo-kicker{font-family:var(--font-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase}
.demo-letter-title{font-family:var(--font-display);font-size:22px;margin-top:4px}
.demo-letter-body{padding:28px 30px 0}
.demo-letter-h3{font-size:30px;line-height:1.16;margin-top:14px;max-width:560px}
.demo-letter-lead{font-size:15.5px;line-height:1.65;color:var(--text-dim);margin-top:14px;max-width:560px}
.demo-items{padding:24px 30px 0}
.demo-item{padding:16px 0;border-top:1px solid var(--line)}
.demo-item .t{font-size:15px;font-weight:600;color:var(--text)}
.demo-item p{font-size:13.5px;line-height:1.55;color:var(--text-dim);margin-top:4px}
.demo-why{margin:8px 30px 30px;background:var(--color-brand-light);padding:14px 18px}
.demo-why .h{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase}
.demo-why p{font-size:13.5px;line-height:1.55;color:var(--text);margin-top:6px}
.nl-how-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:30px}
.home-card-num{font-family:var(--font-display);font-size:28px;color:var(--line)}
.home-card-t{font-family:var(--font-display);font-size:20px;margin-top:6px}
.home-card-d{font-size:13.5px;line-height:1.6;color:var(--text-dim);margin-top:10px}
.nl-pipe{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid var(--line)}
.pipe-cell{padding:24px 24px 28px;border-right:1px solid var(--line);position:relative}
.pipe-cell:last-child{border-right:0}
.pipe-cell.first{border-left:3px solid var(--color-brand-primary)}
.pipe-k{font-family:var(--font-mono);font-size:11px;color:var(--color-accent);letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px}
.pipe-t{font-family:var(--font-display);font-size:19px;line-height:1.15}
.pipe-d{font-size:13px;line-height:1.55;color:var(--text-dim);margin-top:10px}
.home-gate-row{margin-top:18px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.nl-surface-list{border-top:1px solid var(--line)}
.nl-surface-row{display:grid;grid-template-columns:76px 1fr 240px;gap:28px;align-items:baseline;padding:26px 0;border-bottom:1px solid var(--line)}
.surface-idx{font-family:var(--font-display);font-size:36px;color:var(--line)}
.surface-name{font-family:var(--font-display);font-size:26px;color:var(--text)}
.surface-name em{color:var(--text-dim);font-size:19px}
.surface-body{font-size:14.5px;line-height:1.6;color:var(--text-dim);margin-top:10px;max-width:540px}
.surface-meta{text-align:right}
.surface-meta .m{font-family:var(--font-mono);font-size:11px;color:var(--text-dim);letter-spacing:.02em;margin-bottom:14px}
.surface-enter{font-family:var(--font-mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--color-brand-primary);display:inline-flex;align-items:center;gap:7px}
.nl-practice-grid{display:grid;grid-template-columns:repeat(5,1fr);margin-top:26px;border-top:1px solid var(--line);border-left:1px solid var(--line)}
.practice-cell{padding:20px 18px 22px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}
.practice-num{font-family:var(--font-display);font-size:22px;color:var(--line)}
.practice-t{font-family:var(--font-display);font-size:17px;line-height:1.14;margin-top:8px}
.practice-d{font-size:12.5px;line-height:1.5;color:var(--text-dim);margin-top:8px}
.dev-lockup{display:flex;align-items:center;gap:10px;color:var(--text-dim);font-family:var(--font-mono);font-size:13px;flex-wrap:wrap}
.dev-lockup .org{color:var(--text)}
.dev-lockup .repo{color:var(--color-brand-primary);font-weight:500}
.dev-lockup .pub{margin-left:6px;padding:2px 8px;border:1px solid var(--line);font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.dev-grid{display:grid;grid-template-columns:1fr 1.05fr;gap:40px;margin-top:26px;align-items:start}
.dev-copy p{font-size:16px;line-height:1.68;color:var(--text);margin-top:18px;max-width:460px}
.dev-copy p.dim{font-size:14.5px;line-height:1.65;color:var(--text-dim);margin-top:14px}
.dev-prompts{display:grid;gap:14px}
.home-invite{max-width:1180px;margin:0 auto;padding:64px 44px 8px}
.home-invite-panel{background:var(--color-surface-low);border-left:3px solid var(--color-accent);padding:40px 44px}
.home-invite-cta{font-family:var(--font-display);font-style:italic;font-size:27px;line-height:1.32;max-width:640px}
.home-invite-btns{display:flex;gap:14px;margin-top:26px;flex-wrap:wrap}
@media(max-width:820px){.wrap{padding:40px 22px}.mast-title{font-size:34px}.lib-surface{grid-template-columns:44px 1fr}.lib-meta{grid-column:1/-1;text-align:left}.nl-links{display:none}}
@media(max-width:980px){.nl-2col,.nl-demo-grid,.nl-how-grid{grid-template-columns:1fr}.demo-pick{position:static}.nl-practice-grid,.nl-pipe{grid-template-columns:1fr 1fr}.nl-surface-row{grid-template-columns:56px 1fr}.nl-surface-row .surface-meta{grid-column:1/-1;text-align:left}.home-h1{font-size:52px}}
@media(max-width:720px){.nl-links{display:none}.nl-practice-grid,.nl-pipe{grid-template-columns:1fr}.dev-grid{grid-template-columns:1fr}.home-h1{font-size:40px}}
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


# Inline stroked SVG glyphs (no icon font — design-system.md §5). aria-hidden: decorative.
_ICON_GIT = (
    '<svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" '
    'style="vertical-align:-1px"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17'
    ".55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52"
    "-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64"
    "-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 "
    "1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 "
    '3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
)
_ICON_ARROW = "&rarr;"


def _section_divider(label: str, variant: str = "") -> str:
    """SectionDivider — a mono eyebrow + trailing hairline rule.

    ``variant`` ∈ {"", "brand", "accent"} selects the eyebrow color (default = the
    page ``--signal``); the Home accent dividers use the new ``.sg-eyebrow.accent``
    / ``.brand`` variants added to ``_CSS``.
    """
    cls = "sg-eyebrow" + (f" {variant}" if variant else "")
    return f'<div class="sg-divider"><span class="{cls}">{_e(label)}</span><span class="sg-rule"></span></div>'


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
                f'<span class="ev-chip">{_e(t.source_id)}{(":" + _e(t.locator.display)) if t.locator.display else ""}</span>'
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


def _lib_ref_label(page: Page) -> str:
    """The stable, content-derived label for a Library row's lead slot.

    Replaces the old positional ``{i:02d}``. Returns the ledger-assigned ``ref``
    (``R-001`` / ``EP01`` / ``A-001``) when present. Newsletters are cadenced —
    their identity is issue+date, not a sequential ref — so when ``ref`` is empty
    we fall back to ``#{issue}`` if known, else a short kind abbreviation. In every
    case the label is a pure function of the Page's content identity, never its
    position in the list — that positional index was the rot point (SITE-01).
    """
    if page.ref:
        return page.ref
    if page.issue is not None:
        return f"#{page.issue:02d}"
    # cadenced surface with no recorded issue (e.g. Rev1 newsletters) — abbreviate the kind.
    return page.kind[:2].upper()


def render_library(site: Site, *, theme: str = "light") -> str:
    """Render the Library/Hub index — the durable archive of every surface.

    Page-driven (SITE-01): each row's lead label is the Page's stable ref/identity
    (via :func:`_lib_ref_label`), not a positional ``enumerate`` index, and the link
    target is ``page.href`` (== ``{slug}.html``). Reordering the surfaces no longer
    renumbers the Library or rots a link.
    """
    rows = []
    for page in site.pages():
        s = page.surface
        rows.append(
            f'<a class="lib-surface" href="{_e(page.href)}" style="--signal:{page.signal_color.css_var}">'
            f'<span class="lib-idx">{_e(_lib_ref_label(page))}</span>'
            f'<span><span class="lib-title">{_e(page.title)}</span> '
            f'<span class="lib-tail">— {_e(s.template.tagline)}</span></span>'
            f'<span class="lib-meta">{_e(s.template.display_name)}<br>{_e(s.template.cadence.label)}'
            f'<br>{_e(page.gate.value)}</span></a>'
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


# --------------------------------------------------------------------------- #
# Home (SITE-02) — the 8-section marketing front door
#
# Canonical copy is `docs/surfaces.md` §"Home — Start here (V1, approved)" +
# `design-reference/newsletters/home.jsx` (the `LETTERS`/`NL_*` data — preserved
# verbatim, surfaces.md L46). The prototype's React `who`/`theme` state becomes a
# no-JS-faithful static default: the DEFAULT persona = the maintainer (home.jsx
# `useState('maintainer')`), whose letter renders inline (N6). The only JS on the
# page is the existing theme toggle (`_TOGGLE_JS`).
# --------------------------------------------------------------------------- #

# The three demo personas (home-atoms.jsx NL_PERSONAS) + the per-persona accent token.
_HOME_PERSONAS = [
    ("maintainer", "MK", "A maintainer", "Owns the service", "var(--color-brand-primary)"),
    ("contributor", "NC", "A new contributor", "First month", "var(--color-green)"),
    ("lead", "EL", "An eng lead", "Sponsors the team", "var(--color-accent)"),
]

class _HomeLetter(TypedDict):
    """One persona's re-cut weekly letter (home.jsx ``LETTERS`` entry)."""

    kicker: str
    tag: str
    title: str
    body: str
    items: list[tuple[str, str]]
    why: str


# The re-cut letters (home.jsx LETTERS — same reviewed record, different emphasis).
_HOME_LETTERS: dict[str, _HomeLetter] = {
    "maintainer": {
        "kicker": "Your weekly · checkout-svc",
        "tag": "Root cause",
        "title": "Connection-pool saturation under the new retry policy",
        "body": "The p99 climb traced to retries exhausting the pool during a downstream blip — "
        "invisible on the APM average, obvious once the four sources were on one timeline.",
        "items": [
            ("The fix that shipped", "Bounded retries + a pool-pressure guardrail. Diff and the reusable record are linked."),
            ("Watch this week", "Pool-wait p99 and retry-rate on the dashboard you own."),
        ],
        "why": "You own checkout-svc — surfaced because the regression hit your service during your on-call window.",
    },
    "contributor": {
        "kicker": "Your weekly · onboarding edition",
        "tag": "Start here",
        "title": "How we debug latency here, walked through end to end",
        "body": "A real regression, narrated: how four observability sources get reconciled into one "
        "story. The clearest map of our tooling you’ll find in week one.",
        "items": [
            ("The reusable record", "Open the RCA template — the shape you’ll inherit next time, not a blank page."),
            ("Glossary", "APM, traces, RUM, p99 — the terms in this letter, defined."),
        ],
        "why": "You’re in your first month — your corpus weights orientation and context over deep internals.",
    },
    "lead": {
        "kicker": "Your weekly · the signal",
        "tag": "Impact",
        "title": "Time-to-cause fell from ~2 shifts to 2.5 hours",
        "body": "One reconciled timeline replaced two days of cross-referencing. Work content down, "
        "energy up — and the method ports to the next incident without starting over.",
        "items": [
            ("What it unblocks", "On-call hours returned to feature work; the pattern is now a template."),
            ("Across the quarter", "Third regression resolved with the reusable record. The trend is the story."),
        ],
        "why": "You sponsor the team — your corpus leads with outcomes, cost, and cross-case patterns.",
    },
}

# The personalization "how it works" cards (home.jsx) — accented in the 3 persona colors.
_HOME_HOW = [
    ("Codify once", "The event is reviewed and recorded a single time, every claim traced to its source."),
    ("Tune to a corpus", "Each reader carries a private corpus — role, owned services, what they’ve read. It stays local."),
    ("Re-cut on send", "The agent reorders, reframes, and trims the same record against that corpus. No new facts — new emphasis."),
]

# The publish loop (home-atoms.jsx NL_PIPELINE).
_HOME_PIPELINE = [
    ("Ingest", "A conversation or event", "A recorded walk-through, an incident, a merged change — structured into a record."),
    ("Distill", "An agent drafts", "The agentic journalist synthesizes the record into surfaces, tuned to each audience corpus."),
    ("Review", "Opened as a pull request", "A human reviews the draft in a PR — edits, questions, approves. Rigor as the way it earns trust."),
    ("Publish", "Merged & relayed", "On merge it ships to the Show, the Letters, the Articles — and the Library remembers it."),
]

# The four surfaces (home-atoms.jsx NL_SURFACES) — presentation order per surfaces.md L59.
_HOME_SURFACES = [
    ("01", "The Show", "recorded conversations", "Practitioners walking through real work they did — and the reasoning behind it. The raw material everything else is distilled from.", "New episode every other week"),
    ("02", "Newsletters", "the weekly signal, per reader", "A level-headed digest of what changed and why it matters — automatically re-cut for each reader from their own corpus. One shared edition, many personal ones.", "Sent weekly · ~6-min read"),
    ("03", "The Articles", "peer-reviewed write-ups", "Durable write-ups generated from conversations and system outputs — every claim traced to a source, human-validated before publish.", "Published to the Library"),
    ("04", "The Report", "the reusable record", "The structured record a surface is built on — regenerated per event so the next person inherits the shape instead of a blank page.", "One record per event"),
]

# Five practices of working in the open (home-atoms.jsx NL_PRACTICES).
_HOME_PRACTICES = [
    ("Public storytelling", "Set context in the open — what we are doing and why, as we do it."),
    ("Community contribution", "Make it easy for anyone to pick up, fork, and add to the work."),
    ("Prototyping in the wild", "Ship rough, learn fast, in view of the people it is for."),
    ("Reflection & documentation", "Talk openly about mistakes, changes, and what we learned."),
    ("Remixable products", "Leave behind records others can reuse — not heroics they can only admire."),
]

# The synthesize.py API example (architecture.md §2; home.jsx PromptBlock).
_HOME_SYNTHESIZE = (
    "# one conversation → record, article, letter, episode\n"
    "from newsletters import synthesize, Corpus\n\n"
    "out = synthesize(\n"
    '    event="latency-regression-2026-06-12",\n'
    '    sources=["apm", "traces", "logs", "rum"],\n'
    '    audience=Corpus.load("maintainers"),\n'
    ")\n"
    "out.open_pull_request()  # human reviews before publish"
)


def _home_hero() -> str:
    """§1 Hero (#start) — eyebrow, 72px H1 (italic emphasis nouns), lead, two buttons, mono line."""
    return (
        '<section id="start" class="home-sec home-hero">'
        '<div class="sg-eyebrow brand">An open framework for working in the open</div>'
        '<h1 class="sg-display home-h1">Turn information into <em>conversation.</em><br>'
        "Conversation into <em>action.</em></h1>"
        '<p class="home-lead">Newsletters distills structured knowledge into audience-tuned reports, '
        "articles, and letters — drafted by agents, approved by humans, published in the open. A "
        "learning surface for teams that want to learn everywhere, all the time.</p>"
        '<div class="home-btns">'
        f'<a href="#newsletters" class="sg-btn">See it in action {_ICON_ARROW}</a>'
        f'<a href="#developers" class="sg-btn ghost">{_ICON_GIT} View on GitHub</a>'
        "</div>"
        '<p class="sg-mono home-mono-line">Open source &middot; MIT &middot; self-hostable &middot; '
        "human-in-the-loop by design</p></section>"
    )


def _home_why() -> str:
    """§2 Why this exists — two-col 1fr/1fr: serif statement + two body paragraphs."""
    return (
        '<section class="home-sec"><div class="nl-2col">'
        "<div>" + _section_divider("Why this exists")
        + '<p class="home-why-stmt">In a world flooded with information, <em>relevance wins.</em></p></div>'
        '<div class="home-why-body" style="padding-top:6px">'
        "<p>Most of what a team learns evaporates. It lives in a thread, a call nobody recorded, a "
        "dashboard only one person reads. The knowledge is there — it just never gets distilled, "
        "attributed, or relayed to the people it would help.</p>"
        "<p>Newsletters is the semantic bridge between structured data and human understanding: a "
        "publishing layer that captures the work as it happens and hands each person exactly what "
        "matters to them.</p></div></div></section>"
    )


def _home_demo() -> str:
    """§3 Personalization demo (#newsletters) — the no-JS-faithful default persona letter."""
    default_id = _HOME_PERSONAS[0][0]  # 'maintainer' (home.jsx useState default)
    # The persona picker (static, no-JS): the default is marked .on; others are styled labels.
    buttons = []
    for pid, initials, name, role, accent in _HOME_PERSONAS:
        on = pid == default_id
        cls = "demo-persona on" if on else "demo-persona"
        avatar_style = (
            f"background:{accent};color:#fff" if on else "background:var(--color-surface-mid);color:var(--text-dim)"
        )
        border = f"border-left-color:{accent}" if on else ""
        buttons.append(
            f'<div class="{cls}" style="{border}">'
            f'<span class="sg-avatar" style="width:34px;height:34px;font-size:14px;{avatar_style}">{_e(initials)}</span>'
            f'<span><span class="pn">{_e(name)}</span><span class="pr">{_e(role)}</span></span></div>'
        )
    picker = (
        '<div class="demo-pick"><div class="demo-pick-label">Viewing as</div>'
        + "".join(buttons)
        + '<div class="demo-same"><div class="sg-mono">Same source</div>'
        "<p>All three letters are cut from one reviewed record — the latency-regression RCA.</p></div></div>"
    )
    # The default persona's letter, rendered inline (the wow, with JS disabled).
    _, initials, name, role, accent = _HOME_PERSONAS[0]
    letter = _HOME_LETTERS[default_id]
    items = "".join(
        f'<div class="demo-item"><div class="t">{_e(t)}</div><p>{_e(d)}</p></div>'
        for t, d in letter["items"]
    )
    chip = (
        f'<span class="sg-chip"><span class="sg-avatar">{_e(initials)}</span>'
        f'<span><span class="sg-chip-name">{_e(name)}</span> '
        f'<span class="sg-chip-role">{_e(role)}</span></span></span>'
    )
    letter_html = (
        f'<div class="demo-letter" style="border-top:3px solid {accent}">'
        '<div class="demo-letter-head"><div>'
        f'<div class="demo-kicker" style="color:{accent}">{_e(letter["kicker"])}</div>'
        '<div class="demo-letter-title">The weekly signal</div></div>'
        f"{chip}</div>"
        '<div class="demo-letter-body">'
        f'<span class="sg-tag cat">{_e(letter["tag"])}</span>'
        f'<h3 class="sg-display demo-letter-h3">{_e(letter["title"])}</h3>'
        f'<p class="demo-letter-lead">{_e(letter["body"])}</p></div>'
        f'<div class="demo-items">{items}</div>'
        f'<div class="demo-why" style="border-left:3px solid {accent}">'
        f'<span class="h" style="color:{accent}">Why you&rsquo;re seeing this</span>'
        f'<p>{_e(letter["why"])}</p></div></div>'
    )
    cards = "".join(
        f'<div class="sg-card" style="border-left-color:{_HOME_PERSONAS[i][4]}">'
        f'<span class="home-card-num">{i + 1:02d}</span>'
        f'<div class="home-card-t">{_e(t)}</div>'
        f'<p class="home-card-d">{_e(d)}</p></div>'
        for i, (t, d) in enumerate(_HOME_HOW)
    )
    return (
        '<section id="newsletters" class="home-sec">'
        + _section_divider("See it in action · audience-aware by design", "accent")
        + '<h2 class="sg-display home-h2">Everyone gets the newsletter that&rsquo;s <em>about them.</em></h2>'
        '<p class="home-sec-lead">One source event. One review. Then the agent re-cuts the weekly '
        "letter from each reader&rsquo;s own corpus. Same facts — different emphasis. Switch readers "
        "and watch it change:</p>"
        f'<div class="nl-demo-grid">{picker}{letter_html}</div>'
        f'<div class="nl-how-grid">{cards}</div></section>'
    )


def _home_engine() -> str:
    """§4 The publishing engine (#engine) — 4-cell pipeline + the In Review gate badge."""
    cells = []
    for i, (k, t, d) in enumerate(_HOME_PIPELINE):
        cls = "pipe-cell first" if i == 0 else "pipe-cell"
        cells.append(
            f'<div class="{cls}"><div class="pipe-k">{i + 1:02d} · {_e(k)}</div>'
            f'<h4 class="sg-display pipe-t">{_e(t)}</h4>'
            f'<p class="pipe-d">{_e(d)}</p></div>'
        )
    return (
        '<section id="engine" class="home-sec">'
        + _section_divider("How it publishes · human in the loop")
        + '<p class="home-sec-lead" style="max-width:640px">Agents do the drafting. People do the '
        "deciding. Nothing publishes without passing through review — the same gate that makes the "
        "output worth trusting.</p>"
        f'<div class="nl-pipe">{"".join(cells)}</div>'
        '<div class="home-gate-row"><span class="sg-mono">The review gate, on every artifact:</span>'
        f"{_gate_badge(ReviewState.IN_REVIEW)}</div></section>"
    )


def _home_surfaces() -> str:
    """§5 The four surfaces (#surfaces) — bordered rows with an "Enter →" affordance."""
    rows = []
    for idx, name, tail, body, meta in _HOME_SURFACES:
        rows.append(
            '<div class="nl-surface-row">'
            f'<span class="surface-idx">{_e(idx)}</span>'
            f'<div><h3 class="surface-name">{_e(name)} <em>— {_e(tail)}</em></h3>'
            f'<p class="surface-body">{_e(body)}</p></div>'
            '<div class="surface-meta">'
            f'<div class="m">{_e(meta)}</div>'
            f'<a href="#" class="surface-enter">Enter {_ICON_ARROW}</a></div></div>'
        )
    return (
        '<section id="surfaces" class="home-sec">'
        + _section_divider("One conversation, many surfaces", "accent")
        + '<p class="home-sec-lead" style="max-width:600px">A single record fans out into everything a '
        "reader might need — each surface a different distance from the raw work.</p>"
        f'<div class="nl-surface-list">{"".join(rows)}</div></section>'
    )


def _home_thesis() -> str:
    """§6 The thesis — a 5-col bordered grid of practices."""
    cells = "".join(
        f'<div class="practice-cell"><span class="practice-num">{i + 1:02d}</span>'
        f'<div class="practice-t">{_e(t)}</div><p class="practice-d">{_e(d)}</p></div>'
        for i, (t, d) in enumerate(_HOME_PRACTICES)
    )
    return (
        '<section class="home-sec">'
        + _section_divider("The thesis · five practices of working in the open")
        + f'<div class="nl-practice-grid">{cells}</div></section>'
    )


def _home_developers() -> str:
    """§7 For developers (#developers) — repo lockup + two PromptBlock panels."""
    install = (
        '<div class="sg-prompt"><div class="sg-prompt-head">'
        '<span class="sg-prompt-label">install</span><span class="sg-prompt-label">copy</span></div>'
        f'<pre class="sg-prompt-body">{_e("# from PyPI")}\npip install newsletters</pre></div>'
    )
    synth = (
        '<div class="sg-prompt"><div class="sg-prompt-head">'
        '<span class="sg-prompt-label">synthesize.py</span><span class="sg-prompt-label">copy</span></div>'
        f'<pre class="sg-prompt-body">{_e(_HOME_SYNTHESIZE)}</pre></div>'
    )
    return (
        '<section id="developers" class="home-sec">'
        + _section_divider("For developers · clone it, point it at your work", "accent")
        + '<div class="dev-grid"><div class="dev-copy">'
        f'<div class="dev-lockup">{_ICON_GIT} <span class="org">nneibaue</span> / '
        '<span class="repo">newsletters</span><span class="pub">public</span></div>'
        "<p>Everything is a typed, type-safe model so outputs stay consistent and auditable. Three "
        "core objects carry the whole system: a <strong>Source</strong> (what happened), a "
        "<strong>Distillation</strong> (the agent&rsquo;s synthesis, every claim traced), and a "
        "<strong>Surface</strong> (the published artifact + its review gate).</p>"
        '<p class="dim">Deploy modular MCP servers so private corpora stay local and encrypted. Every '
        "surface is a slot-marked template — fork it, repopulate with your specifics, ship.</p>"
        '<div class="home-btns">'
        f'<a href="#" class="sg-btn">{_ICON_GIT} Clone the repo</a>'
        '<a href="#" class="sg-btn ghost">Read the spec</a></div></div>'
        f'<div class="dev-prompts">{install}{synth}</div></div></section>'
    )


def _home_invitation() -> str:
    """§8 Invitation — surface-low panel with a 3px accent left-border + serif italic CTA."""
    return (
        '<section class="home-invite"><div class="home-invite-panel">'
        '<p class="home-invite-cta">Clone it, point it at your own work, and start publishing what '
        "you learn — for your team, your org, or the world.</p>"
        '<div class="home-invite-btns">'
        f'<a href="#" class="sg-btn">{_ICON_GIT} Get started on GitHub</a>'
        '<a href="#newsletters" class="sg-btn ghost">Replay the demo</a></div></div></section>'
    )


def render_home(site: Site, *, theme: str = "light") -> str:
    """Render the marketing Home (SITE-02) → ``index.html``.

    The 8-section front door per ``docs/surfaces.md`` §"Home" and the approved
    ``design-reference/Newsletters - Home.html`` prototype, recreated in hand-rolled
    HTML strings (zero new dependency). The persona/theme React state cannot run
    statically, so the DEFAULT persona's letter (the maintainer) renders inline — the
    page is fully faithful with JavaScript disabled (N6). ``site`` is accepted so later
    waves can resolve §5 "Enter →" / §7 links to real hub hrefs; this wave uses anchors
    / ``#`` placeholders. ``active="Start here"``.
    """
    body = "".join(
        (
            _home_hero(),
            _home_why(),
            _home_demo(),
            _home_engine(),
            _home_surfaces(),
            _home_thesis(),
            _home_developers(),
            _home_invitation(),
        )
    )
    return _page(
        title="Start here",
        signal_css="var(--color-brand-primary)",
        body=body,
        active="Start here",
        theme=theme,
    )
