"""Rev1 dogfood content — Newsletters reporting on building Newsletters.

We are the first corpus. The work sessions below are *our own*: the kickoff, the data-model
design conversation, and this Rev1 build. They are captured into **Reports** (the
investigations we approved), one is promoted into a peer-review **Article** (awaiting JJ),
the week is re-cut per reader as a **Newsletter**, and the whole process is recorded as a
**Show**. ``build_site()`` renders them all to standalone HTML.

Sample content is illustrative of the *shapes and voice*; wire real values to real data.
"""

from __future__ import annotations

from pathlib import Path

from .capture import Decision, WorkSession, build_report
from .promote import promote_report_to_article
from .render import render_library, render_surface
from .semantic import (
    Claim,
    ClaimsBlock,
    Corpus,
    FanoutBlock,
    FanoutLink,
    ItemsBlock,
    KpiItem,
    KpiStripBlock,
    LetterItem,
    ProseBlock,
    PromptBlock,
    QuoteBlock,
    RationaleBlock,
    Review,
    Source,
    Surface,
    Trace,
)
from .templates import NEWSLETTER, SHOW

AUTHOR = "Claude"
PEER = "JJ Airuoyo"

# --------------------------------------------------------------------------- #
# Readers — the corpora (private; used for emphasis, never serialized out)
# --------------------------------------------------------------------------- #

READERS = {
    "jj": Corpus(
        name="JJ Airuoyo", role="Founder · architect", initials="JJ",
        owned=["Vision", "Articles"],
        weights={"vision": 1.0, "process": 0.8, "design": 0.5},
    ),
    "nate": Corpus(
        name="Nate Neibauer", role="Maintainer · core", initials="NN",
        owned=["Core", "Packaging"],
        weights={"core": 1.0, "measurement": 0.7, "design": 0.4},
    ),
    "newcomer": Corpus(
        name="New Contributor", role="First week", initials="NC",
        owned=[],
        weights={"onboarding": 1.0, "vision": 0.5},
    ),
}


# --------------------------------------------------------------------------- #
# Sources + sessions — our actual journey
# --------------------------------------------------------------------------- #

def _sources_and_reports() -> list[Surface]:
    src_kickoff = Source(
        id="session-kickoff", context="claude-code",
        transcript="Foundation pass: spec set, repo shape, typed semantic spine, tests.",
    )
    src_datamodel = Source(
        id="session-datamodel", context="claude-code · design conversation",
        transcript="Reasoning over the core data models with JJ — two layers, templates, "
        "Report vs Article, the agent boundary, capture modes, promotions.",
    )
    src_rev1 = Source(
        id="session-rev1", context="claude-code",
        transcript="Rev1 end-to-end: refactor to templates + policy + capture + promotion, "
        "a token-faithful HTML renderer, and this dogfood content.",
    )

    kickoff = build_report(
        WorkSession(
            id="session-kickoff", title="Kicking off the build", tool="Claude Code",
            artifacts=["docs/", "src/newsletters/semantic.py", "tests/"],
            sources=[src_kickoff],
            decisions=[
                Decision(text="Land the spec set + design references as the source of truth, "
                         "rather than dumping the zip.", source_id="session-kickoff",
                         locator="docs/", topics=["process", "vision"]),
                Decision(text="Keep the Python core at src/newsletters and document the "
                         "architecture §4 repo-shape mapping in CLAUDE.md.",
                         source_id="session-kickoff", locator="CLAUDE.md", topics=["core"]),
                Decision(text="Implement the typed spine with all three invariants enforced "
                         "in code, agentic distill left an honest stub.",
                         source_id="session-kickoff", locator="semantic.py",
                         topics=["core", "design"]),
                Decision(text="Neutralize the GSD.md supply-chain redirect to 'verify any "
                         "install against its official source' and flag it for review.",
                         source_id="session-kickoff", locator="GSD.md", topics=["process"]),
            ],
        ),
        surface_id="report-kickoff", title="Kicking off the build — spec set, repo shape, typed spine",
        eyebrow="Report · how we solved it", author=AUTHOR,
        narrative="The repo was effectively empty. Instead of shipping the starter zip as-is, "
        "we landed a real foundation: the spec set as source of truth, the architecture §4 "
        "repo shape, and a typed semantic spine with the review gate enforced in code — so "
        "later phases have spec, structure, and working tests to build against.",
    )
    kickoff.blocks.insert(0, KpiStripBlock(items=[
        KpiItem(label="Files landed", value="32"),
        KpiItem(label="Invariant tests", value="9 / 9", delta="all green", dir="up"),
        KpiItem(label="Roadmap", value="0 → 2", delta="spine done", dir="up"),
    ]))
    kickoff.blocks.append(QuoteBlock(
        text="Agents draft, humans decide. The review gate is part of the product, not scaffolding.",
        attr="— the one rule we kept"))
    kickoff.blocks.append(FanoutBlock(links=[
        FanoutLink(kind="article", title="Designing the semantic spine (peer review)"),
        FanoutLink(kind="show", title="Episode 01 — Building in the open"),
    ]))
    kickoff.publish(reviewer=AUTHOR)

    datamodel = build_report(
        WorkSession(
            id="session-datamodel", title="Getting the data models right", tool="Claude Code",
            artifacts=["docs/vision.md"], sources=[src_datamodel],
            decisions=[
                Decision(text="Two layers, not five peers: a Truth layer (Source→Claim→"
                         "Distillation) and a Surface layer over it.", source_id="session-datamodel",
                         locator="layers", topics=["design", "core"], confidence=0.95),
                Decision(text="The four surfaces are one parameterized template, not four "
                         "classes — cadence, personalization, signal color, review policy are "
                         "config.", source_id="session-datamodel", locator="templates",
                         topics=["design", "core"], confidence=0.95),
                Decision(text="The Report is the investigation you approve (light PR); the "
                         "Article is the durable, peer-reviewed lesson promoted from it.",
                         source_id="session-datamodel", locator="report-vs-article",
                         topics=["design", "process"], confidence=0.95),
                Decision(text="Problem-solving agents are external and operator-owned; "
                         "Newsletters owns capture + trust + publish, never the agent.",
                         source_id="session-datamodel", locator="agent-boundary",
                         topics=["process", "vision"], confidence=0.9),
                Decision(text="Default capture is post-session and reads the workspace "
                         "(tool-agnostic); push-integration is the operator add-on.",
                         source_id="session-datamodel", locator="capture",
                         topics=["process", "core"], confidence=0.9),
                Decision(text="Two human-gated promotions form the system's grammar: "
                         "Claim→KPI (measurable) and Report→Article (durable).",
                         source_id="session-datamodel", locator="promotions",
                         topics=["design", "measurement"], confidence=0.9),
            ],
        ),
        surface_id="report-datamodel", title="Getting the data models right",
        eyebrow="Report · how we solved it", author=AUTHOR,
        narrative="A long design conversation. The load-bearing move was seeing that report, "
        "article, newsletter, show and claim are not peers — they sit on two layers, and the "
        "four surfaces are one parameterized template. From there the rest fell out: the "
        "Report/Article split, the external-agent boundary, and two reviewed promotions.",
    )
    datamodel.blocks.insert(0, KpiStripBlock(items=[
        KpiItem(label="Decisions captured", value="6"),
        KpiItem(label="Surfaces unified", value="4 → 1", delta="one template", dir="up"),
        KpiItem(label="Promotions defined", value="2"),
    ]))
    datamodel.blocks.append(QuoteBlock(
        text="Spend time. Write it down well. Make it traceable. That is how we get closer to "
        "where the issues are — and how the city learns.",
        attr="— docs/vision.md"))
    datamodel.blocks.append(FanoutBlock(links=[
        FanoutLink(kind="article", title="Designing the semantic spine (promoted from this report)"),
        FanoutLink(kind="newsletter", title="The Weekly Signal — Rev1 is live"),
    ]))
    datamodel.publish(reviewer=AUTHOR)

    rev1 = build_report(
        WorkSession(
            id="session-rev1", title="Rev1 — rendering the surfaces", tool="Claude Code",
            artifacts=["src/newsletters/templates.py", "src/newsletters/render.py",
                       "src/newsletters/capture.py", "src/newsletters/promote.py"],
            sources=[src_rev1],
            decisions=[
                Decision(text="Surfaces compose from typed content blocks — the blocks ARE the "
                         "slots; only prose is templated, structure stays typed.",
                         source_id="session-rev1", locator="blocks", topics=["core", "design"]),
                Decision(text="A self-contained HTML renderer ports the design tokens 1:1 so "
                         "Rev1 is viewable with no server.", source_id="session-rev1",
                         locator="render.py", topics=["design"]),
                Decision(text="Per-template review policy is enforced at publish: Report "
                         "self-approves, the Article requires a peer.", source_id="session-rev1",
                         locator="ReviewPolicy", topics=["core", "process"]),
                Decision(text="Provenance + lineage track the process on every surface — which "
                         "tool, which session, what it derived from / produced.",
                         source_id="session-rev1", locator="Provenance", topics=["process", "measurement"]),
            ],
        ),
        surface_id="report-rev1", title="Rev1 — rendering the surfaces end to end",
        eyebrow="Report · in review", author=AUTHOR,
        narrative="This report is itself in review — you are reading it inside the PR that "
        "produced it. Rev1 bakes our decisions into the typed core (templates, per-template "
        "review policy, the capture boundary, the two promotions) and renders every surface "
        "to faithful HTML so the range of what the core supports is visible, not just described.",
    )
    rev1.blocks.insert(0, KpiStripBlock(items=[
        KpiItem(label="Core modules", value="6"),
        KpiItem(label="Surfaces rendered", value="6"),
        KpiItem(label="Surface kinds", value="4", delta="from 1 template", dir="up"),
    ]))
    rev1.blocks.append(PromptBlock(label="build the library", body="$ newsletters build\n"
        "rendered 6 surfaces + the library index -> content/rev1/site/"))
    rev1.blocks.append(FanoutBlock(links=[
        FanoutLink(kind="show", title="Episode 01 — Building Newsletters in the open"),
    ]))
    rev1.open_pull_request(pr_url="(this PR)")  # left In Review on purpose

    return [kickoff, datamodel, rev1]


# --------------------------------------------------------------------------- #
# Newsletter — one record, re-cut per reader (same facts, new emphasis)
# --------------------------------------------------------------------------- #

_LETTER_ITEMS = [
    ("vision", LetterItem(tag="vision", title="The north star is on the record",
        body="docs/vision.md names the thing we're really building — the public square of a "
        "co-learning city, where truth is traceable and reviewed.")),
    ("core", LetterItem(tag="core", title="The typed spine is real and green",
        body="Source → Claim → Distillation → Surface, with the review gate and all three "
        "invariants enforced in code. Nine tests and counting.")),
    ("design", LetterItem(tag="design", title="Four surfaces became one template",
        body="Cadence, personalization, signal color and review policy are now config — the "
        "Report, Article, Newsletter and Show are presets over one SurfaceTemplate.")),
    ("process", LetterItem(tag="process", title="Agents draft; the boundary is drawn",
        body="Problem-solving agents stay external and operator-owned. Newsletters captures, "
        "traces, gates and publishes — it never owns the agent.")),
    ("measurement", LetterItem(tag="measurement", title="Two promotions you can measure",
        body="Claim → KPI makes a finding measurable; Report → Article makes a lesson durable. "
        "Both are human-gated.")),
    ("onboarding", LetterItem(tag="start here", title="New here? Start with the Show",
        body="Episode 01 walks the whole build. Then read a Report to see an approved "
        "investigation, and the Library to see how it all fans out.")),
]


def _newsletter_for(reader_key: str) -> Surface:
    reader = READERS[reader_key]
    ordered = sorted(_LETTER_ITEMS, key=lambda ti: reader.weights.get(ti[0], 0.0), reverse=True)
    items = [it for _, it in ordered]
    lead = items[0]
    focus = ", ".join(sorted(reader.weights, key=lambda k: reader.weights[k], reverse=True)[:2])
    rationale = (
        f"You're seeing “{lead.title}” first because your focus is {focus}. "
        "Same reviewed record as everyone else — only the emphasis is yours; your private "
        "corpus stayed in your environment and was read at render time, then discarded."
    )
    src = Source(id="session-rev1")
    nl = Surface(
        id=f"newsletter-{reader_key}", template=NEWSLETTER,
        title="The Weekly Signal — Rev1 is live",
        eyebrow="Newsletters · the weekly signal",
        audience_label=f"{reader.name} · {reader.role}",
        byline=[AUTHOR],
        blocks=[
            ProseBlock(heading=lead.title, text=lead.body),
            KpiStripBlock(items=[
                KpiItem(label="Surfaces live", value="6"),
                KpiItem(label="Phase", value="0 → 2", delta="spine done", dir="up"),
                KpiItem(label="Reviews open", value="2", delta="1 peer", dir="up"),
            ]),
            ItemsBlock(heading="Also this week", items=items[1:]),
            QuoteBlock(text="One reviewed record, fanned out — each re-cut per reader from "
                       "their own corpus.", attr="— the signature interaction"),
            RationaleBlock(text=rationale),
        ],
        traces=[src],
        review=Review(policy=NEWSLETTER.review_policy, author=AUTHOR),
    )
    nl.publish(reviewer=AUTHOR)
    return nl


# --------------------------------------------------------------------------- #
# The Show — recording this build process
# --------------------------------------------------------------------------- #

def _show() -> Surface:
    from .semantic import Chapter, ChaptersBlock

    src = Source(id="session-datamodel")
    show = Surface(
        id="show-ep01", template=SHOW,
        title="Episode 01 — Building Newsletters in the open",
        eyebrow="The Show · recorded session",
        byline=[PEER, AUTHOR],
        blocks=[
            ProseBlock(text="The raw conversation everything above was distilled from: a "
                       "founder and a trusted agent reasoning the product into existence, in "
                       "the open. This is the rawest surface — closest to the work."),
            ChaptersBlock(chapters=[
                Chapter(time="00:00", title="Kickoff", body="An empty repo, a starter kit, and "
                        "a supply-chain redirect we refused to run. Landing a real foundation."),
                Chapter(time="06:30", title="The vision", body="The city, the co-learning "
                        "economy, and what 'truth' means here — provenance and review, not decree."),
                Chapter(time="18:10", title="Reports vs Articles", body="The Report is the "
                        "investigation you approve; the Article is the durable, peer-reviewed lesson."),
                Chapter(time="27:40", title="The agent boundary", body="Problem-solving agents "
                        "are external and pluggable; Newsletters owns capture, trust, and publish."),
                Chapter(time="34:00", title="Rev1", body="Templates, per-template review policy, "
                        "promotions, and a token-faithful renderer — built end to end."),
            ]),
            FanoutBlock(heading="What this episode produced", links=[
                FanoutLink(kind="report", title="Getting the data models right"),
                FanoutLink(kind="article", title="Designing the semantic spine"),
                FanoutLink(kind="newsletter", title="The Weekly Signal — Rev1 is live"),
            ]),
        ],
        traces=[src],
        review=Review(policy=SHOW.review_policy, author=AUTHOR),
    )
    show.publish(reviewer=AUTHOR)
    return show


def _article(datamodel_report: Surface) -> Surface:
    article = promote_report_to_article(
        datamodel_report,
        surface_id="article-semantic-spine",
        title="Designing the semantic spine: two layers, parameterized surfaces, and promotion gates",
        author=AUTHOR,
        lead="A durable write-up of the data-model design — promoted from the Report, now "
        "awaiting peer review. Where the Report says 'here is how we decided, just now,' this "
        "Article says 'here is what anyone building a trust-first publishing layer should take "
        "away.' It is In Review until a peer (not the author) approves it — JJ, that's you.",
    )
    article.blocks.append(PromptBlock(label="the shape that made it work", body=(
        "SurfaceTemplate(\n"
        "    name='report', cadence=Cadence.PER_EVENT, personalized=False,\n"
        "    signal_color=SignalColor.BRAND, review_policy=ReviewPolicy.light(),\n"
        ")\n"
        "# the four surfaces are presets over one template — structure is typed,\n"
        "# only the prose is templated.")))
    return article


# --------------------------------------------------------------------------- #
# Assemble + render
# --------------------------------------------------------------------------- #

def build_surfaces() -> list[Surface]:
    """Assemble the full Rev1 surface set (ordered by distillation distance)."""
    kickoff, datamodel, rev1 = _sources_and_reports()
    article = _article(datamodel)
    show = _show()
    newsletters = [_newsletter_for(k) for k in ("jj", "nate", "newcomer")]
    return [show, kickoff, datamodel, rev1, article, *newsletters]


def build_site(out_dir: str | Path = "content/rev1/site") -> list[Path]:
    """Render every surface + the Library index to standalone HTML. Returns written paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_surfaces()
    written: list[Path] = []
    for s in surfaces:
        p = out / f"{s.id}.html"
        p.write_text(render_surface(s), encoding="utf-8")
        written.append(p)
    # Library lists one representative newsletter (the rest are its per-reader re-cuts).
    listed = [s for s in surfaces if not (s.kind == "newsletter" and s.id != "newsletter-jj")]
    index = out / "index.html"
    index.write_text(render_library(listed), encoding="utf-8")
    written.append(index)
    return written
