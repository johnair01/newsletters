"""Rev1 dogfood content — Newsletters reporting on building Newsletters.

We are the first corpus. The work sessions below are *our own*: the kickoff, the data-model
design conversation, and this Rev1 build. They are captured into **Reports** (the
investigations we approved), one is promoted into a peer-review **Article** (awaiting JJ),
the week is re-cut per reader as a **Newsletter**, and the whole process is recorded as a
**Show**. ``build_site()`` renders them all to standalone HTML.

Sample content is illustrative of the *shapes and voice*; wire real values to real data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .capture import Decision, WorkSession, build_report
from .diagrams import personalization, two_layer
from .learning import OnboardingPath, OnboardingStep, learning_surface
from .promote import promote_report_to_article
from .render import render_home, render_library, render_path, render_surface
from .semantic import (
    Claim,
    ClaimsBlock,
    Corpus,
    DiagramBlock,
    Distillation,
    FanoutBlock,
    FanoutLink,
    ItemsBlock,
    KpiItem,
    KpiStripBlock,
    LetterItem,
    ProseBlock,
    PromptBlock,
    Provenance,
    QuoteBlock,
    RationaleBlock,
    Review,
    Source,
    Surface,
    Trace,
)
from .site import Ledger, Site
from .templates import NEWSLETTER, REPORT, SHOW

AUTHOR = "Claude"
PEER = "JJ Airuoyo"


# --------------------------------------------------------------------------- #
# Provenance migration (PROV-01 / D-4) — content-address the Rev1 corpus IN PLACE
# --------------------------------------------------------------------------- #
#
# The Rev1 sample corpus is "Newsletters reporting on building Newsletters" — our first
# corpus. PROV-01 is only real if the SHIPPED corpus practices the trust property it
# preaches, so we migrate it in place: for each trace whose ``span`` is a *verbatim*
# substring of its live ``Source.transcript``, we locate the span with ``str.find`` and
# re-mint the trace via ``Trace.from_source`` (03-01) so it carries a content hash + the
# character offsets. We re-use the one canonical pinning constructor — we do not
# re-implement hashing or offset logic here.
#
# The migration is FAITHFUL, not suggestive: it changes neither the claim text nor the
# span string; it only ADDS the content-address metadata. A span it cannot locate (empty,
# or not a substring) is REPORTED — ``_address_trace`` raises a teaching ValueError naming
# the span + source; the corpus-level ``address_corpus_traces`` collects it into a
# ``MigrationReport.unlocated`` list instead of fabricating an offset or silently dropping it.


@dataclass
class MigrationReport:
    """The outcome of content-addressing a corpus's traces, faithfully (D-4).

    ``addressed`` counts the traces that carried a locatable verbatim span and were pinned.
    ``unlocated`` lists, in human-readable form, every span that could NOT be located
    (empty span, or not a substring of its source) — reported, never silently dropped and
    never given fabricated offsets. ``skipped_no_span`` counts traces with no span at all
    (the Rev1 structural-locator path): nothing to locate, so they stay un-addressed and
    are simply never stale.
    """

    addressed: int = 0
    skipped_no_span: int = 0
    unlocated: list[str] = field(default_factory=list)


def _address_trace(source: Source, trace: Trace) -> Trace:
    """Content-address ONE trace by locating its verbatim ``span`` in ``source.transcript``.

    Faithful, not suggestive: finds the existing ``trace.span`` via ``str.find`` and, if
    present, re-mints the trace through ``Trace.from_source`` so it pins
    ``content_hash`` + character offsets while keeping the span string and locator
    byte-identical. It NEVER edits the claim or invents evidence — it only adds metadata
    to content that already exists.

    Reports rather than fabricates: an empty span, or a span that is not a substring of
    the transcript, raises a teaching ``ValueError`` naming the span and the source id —
    never a bogus ``0:0`` offset.
    """
    span = trace.span
    if not span:
        raise ValueError(
            f"_address_trace: trace on source {source.id!r} has an empty span — there is "
            "no evidence text to locate; refusing to fabricate an offset (faithful, not "
            "suggestive)."
        )
    start = source.transcript.find(span)
    if start < 0:
        raise ValueError(
            f"_address_trace: span {span!r} was not found verbatim in source "
            f"{source.id!r}'s transcript; refusing to fabricate an offset. Report it as "
            "unlocatable rather than mis-attributing it."
        )
    end = start + len(span)
    return Trace.from_source(source, start, end, locator=trace.locator)


def address_corpus_traces(
    sources: dict[str, Source],
    traces: list[Trace],
) -> MigrationReport:
    """Content-address every locatable trace IN PLACE, reporting what cannot be located.

    For each trace with a non-empty span whose source is known, pin it via
    ``_address_trace`` and copy the resulting content-address fields back onto the live
    trace object (in-place migration). Traces with no span are skipped (never stale).
    Traces whose span is not a verbatim substring — or whose source is unknown — are
    collected into ``MigrationReport.unlocated`` and left UN-addressed: that is the
    faithful outcome, not an error to swallow.
    """
    report = MigrationReport()
    for trace in traces:
        if not trace.span:
            report.skipped_no_span += 1
            continue
        source = sources.get(trace.source_id)
        if source is None:
            report.unlocated.append(
                f"{trace.span!r} (source {trace.source_id!r} not available to verify)"
            )
            continue
        try:
            addressed = _address_trace(source, trace)
        except ValueError as exc:
            report.unlocated.append(str(exc))
            continue
        # In-place pin: copy the additive content-address metadata onto the live trace.
        trace.content_hash = addressed.content_hash
        trace.start = addressed.start
        trace.end = addressed.end
        report.addressed += 1
    return report


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

def _record_transcript(lead: str, decisions: list[Decision]) -> str:
    """Build a Source transcript that is the verbatim record of a session's decisions.

    The session ``Source`` IS the record of what was decided in that session, so its
    transcript faithfully contains each decision statement verbatim. This is what lets the
    migration content-address each decision's trace by locating its span — we are not
    inventing evidence, we are recording (and then pinning) the decisions that were made.
    """
    return lead + "\n\n" + "\n".join(f"- {d.text}" for d in decisions)


def _address_report(report: Surface, sources: list[Source]) -> MigrationReport:
    """Set each ClaimsBlock trace's span to its claim text and content-address it.

    A captured decision becomes a Claim whose single Trace points back at the session
    Source (``capture.py``). Here we pin that trace to the verbatim claim text inside the
    source transcript — the span IS the decision statement, which the transcript records
    verbatim — and content-address it via the migration helper. Faithful: the claim text
    is unchanged; we only add the span + hash + offsets.
    """
    lookup = {s.id: s for s in sources}
    traces: list[Trace] = []
    for block in report.blocks:
        if isinstance(block, ClaimsBlock):
            for claim in block.claims:
                for trace in claim.evidence:
                    if not trace.span:
                        trace.span = claim.text  # the verbatim decision statement
                    traces.append(trace)
    return address_corpus_traces(lookup, traces)


def _sources_and_reports() -> list[Surface]:
    kickoff_decisions = [
        Decision(text="Land the spec set + design references as the source of truth, "
                 "rather than dumping the zip.", source_id="session-kickoff",
                 locator="docs/", topics=["process", "vision"]),
        Decision(text="Keep the Python core at src/newsletters and document the "
                 "architecture §4 repo-shape mapping in CLAUDE.md.",
                 source_id="session-kickoff", locator="CLAUDE.md", topics=["core"]),
        Decision(text="Implement the typed spine with all three invariants enforced "
                 "in code, agentic distill left an honest stub.",
                 source_id="session-kickoff", locator="src/newsletters/semantic.py",
                 topics=["core", "design"]),
        Decision(text="Neutralize the GSD.md supply-chain redirect to 'verify any "
                 "install against its official source' and flag it for review.",
                 source_id="session-kickoff", locator="GSD.md", topics=["process"]),
    ]
    src_kickoff = Source(
        id="session-kickoff", context="claude-code",
        transcript=_record_transcript(
            "Foundation pass: spec set, repo shape, typed semantic spine, tests.",
            kickoff_decisions,
        ),
    )

    kickoff = build_report(
        WorkSession(
            id="session-kickoff", title="Kicking off the build", tool="Claude Code",
            artifacts=["docs/", "src/newsletters/semantic.py", "tests/"],
            sources=[src_kickoff],
            decisions=kickoff_decisions,
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

    datamodel_decisions = [
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
    ]
    src_datamodel = Source(
        id="session-datamodel", context="claude-code · design conversation",
        transcript=_record_transcript(
            "Reasoning over the core data models with JJ — two layers, templates, "
            "Report vs Article, the agent boundary, capture modes, promotions.",
            datamodel_decisions,
        ),
    )

    datamodel = build_report(
        WorkSession(
            id="session-datamodel", title="Getting the data models right", tool="Claude Code",
            artifacts=["docs/vision.md"], sources=[src_datamodel],
            decisions=datamodel_decisions,
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
    datamodel.blocks.insert(2, DiagramBlock(
        title="The shape we settled on",
        svg=two_layer(),
        caption="Two layers, not five peers. Truth (Source → Claim → Distillation) is one "
        "reviewed record; the four surfaces are presets that render it, each through the same "
        "review gate. report / article / newsletter / show are not sibling classes — they are "
        "parameterizations of one template.",
    ))
    datamodel.blocks.insert(3, ProseBlock(heading="What we considered, and why we didn't", text=(
        "Five co-equal models (report, article, newsletter, show, claim) was the obvious "
        "first cut — and the wrong one. It scatters the same truth across four schemas and "
        "makes personalization, promotion, and provenance each a special case. Collapsing to "
        "two layers makes them fall out for free: personalization is a render-time projection "
        "of one Distillation; promotion is a typed transform between surfaces; provenance is a "
        "field on the record, not a fifth noun.\n\n"
        "We also weighed making the problem-solving agent part of the core. We didn't: the "
        "agent is the one thing every operator already has and wants to keep. Drawing the "
        "boundary at capture — not cognition — is what makes Newsletters adoptable by a "
        "factory line, a platform team, or a solo maintainer without ripping out their tools.")))
    datamodel.blocks.append(QuoteBlock(
        text="Spend time. Write it down well. Make it traceable. That is how we get closer to "
        "where the issues are — and how the city learns.",
        attr="— docs/vision.md"))
    datamodel.blocks.append(FanoutBlock(links=[
        FanoutLink(kind="article", title="Designing the semantic spine (promoted from this report)"),
        FanoutLink(kind="newsletter", title="The Weekly Signal — Rev1 is live"),
    ]))
    datamodel.publish(reviewer=AUTHOR)

    rev1_decisions = [
        Decision(text="Surfaces compose from typed content blocks — the blocks ARE the "
                 "slots; only prose is templated, structure stays typed.",
                 source_id="session-rev1", locator="blocks", topics=["core", "design"]),
        Decision(text="A self-contained HTML renderer ports the design tokens 1:1 so "
                 "Rev1 is viewable with no server.", source_id="session-rev1",
                 locator="src/newsletters/render.py", topics=["design"]),
        Decision(text="Per-template review policy is enforced at publish: Report "
                 "self-approves, the Article requires a peer.", source_id="session-rev1",
                 locator="ReviewPolicy", topics=["core", "process"]),
        Decision(text="Provenance + lineage track the process on every surface — which "
                 "tool, which session, what it derived from / produced.",
                 source_id="session-rev1", locator="Provenance", topics=["process", "measurement"]),
    ]
    src_rev1 = Source(
        id="session-rev1", context="claude-code",
        transcript=_record_transcript(
            "Rev1 end-to-end: refactor to templates + policy + capture + promotion, "
            "a token-faithful HTML renderer, and this dogfood content.",
            rev1_decisions,
        ),
    )

    rev1 = build_report(
        WorkSession(
            id="session-rev1", title="Rev1 — rendering the surfaces", tool="Claude Code",
            artifacts=["src/newsletters/templates.py", "src/newsletters/render.py",
                       "src/newsletters/capture.py", "src/newsletters/promote.py"],
            sources=[src_rev1],
            decisions=rev1_decisions,
        ),
        surface_id="report-rev1", title="Rev1 — rendering the surfaces end to end",
        eyebrow="Report · in review", author=AUTHOR,
        narrative="This report is itself in review — you are reading it inside the PR that "
        "produced it. Rev1 bakes our decisions into the typed core (templates, per-template "
        "review policy, the capture boundary, the two promotions) and renders every surface "
        "to faithful HTML so the range of what the core supports is visible, not just described.",
    )
    rev1.blocks.insert(0, KpiStripBlock(items=[
        KpiItem(label="Core modules", value="7"),
        KpiItem(label="Surfaces rendered", value="9"),
        KpiItem(label="Surface kinds", value="4", delta="from 1 template", dir="up"),
    ]))
    rev1.blocks.insert(2, ProseBlock(heading="How it's built", text=(
        "`templates.py` carries the four presets and a registry, so an operator adds their own "
        "surface without touching core. `semantic.py` composes each surface from typed content "
        "blocks — prose, claims, kpi, quote, chapters, items, prompt, fanout, rationale, and "
        "now diagram — the blocks are the slots, and only the prose inside them is templated. "
        "`render.py` ports tokens.css 1:1 into self-contained HTML; the diagrams are inline "
        "SVG whose every stroke is a token, so they flip with light/dark like everything else. "
        "`capture.py` lifts a finished session into a traced Draft Report; `promote.py` carries "
        "the two reviewed promotions. The gate is enforced at `publish()` — the Article you are "
        "about to peer-review literally cannot self-approve.")))
    rev1.blocks.append(PromptBlock(label="build the library", body="$ newsletters build\n"
        "rendered 6 surfaces + the library index -> content/rev1/site/"))
    rev1.blocks.append(FanoutBlock(links=[
        FanoutLink(kind="show", title="Episode 01 — Building Newsletters in the open"),
    ]))
    rev1.open_pull_request(pr_url="(this PR)")  # left In Review on purpose

    # PROV-01 / D-4: content-address the Rev1 corpus IN PLACE. Each report's claim traces
    # are pinned to their verbatim decision statement inside the session Source transcript,
    # so the shipped sample corpus is itself content-addressed and drift-aware. Faithful:
    # spans/claim text are unchanged; only hash+offsets are added. Anything unlocatable would
    # be reported on the MigrationReport (here every decision is recorded verbatim, so the
    # corpus addresses cleanly and is never stale at capture time).
    _address_report(kickoff, [src_kickoff])
    _address_report(datamodel, [src_datamodel])
    _address_report(rev1, [src_rev1])

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
            DiagramBlock(title="Why your copy differs", svg=personalization(),
                         caption="The same reviewed record reaches every reader; only the "
                         "emphasis is re-cut, from each reader's own private corpus."),
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


def _plan_report() -> Surface:
    """The GSD discuss → plan output, delivered as a Report JJ reviews (In Review)."""
    roadmap = Source(id="doc-roadmap", context="docs/roadmap.md",
                     transcript="The phased, dependency-ordered build plan (phases 0–6).")
    phases = [
        LetterItem(tag="phase 0 · next", title="Foundations — tokens, component kit, Next.js shell",
                   body="Port tokens.css to :root + [data-theme=dark], self-host the three "
                   "fonts, build the atoms (Eyebrow … GateBadge … ThemeToggle) and chrome "
                   "(NLNav / NLFooter), wire light/dark end to end. Accept: a blank themed page "
                   "renders in both themes with no console errors; a kitchen-sink route shows "
                   "every component; tokens match design-system.md exactly."),
        LetterItem(tag="phase 1", title="The Home (V1) — the approved front door",
                   body="Build sections 1–8 of surfaces.md, the three-persona personalization "
                   "demo with the sg-fade re-cut, and the responsive collapses. Accept: "
                   "pixel-matches Newsletters - Home.html in both themes; renders without JS."),
        LetterItem(tag="phase 3", title="The four surfaces, from Surface objects",
                   body="Recreate Newsletter / Article / Report / Show in the real stack, each "
                   "rendering from a typed Surface with a real GateBadge — our Rev1 renderer is "
                   "the seed. Accept: matches each reference; gate is real, not hardcoded; the "
                   "Article prints clean to PDF."),
        LetterItem(tag="phase 4", title="The publish loop — human in the loop",
                   body="Ingest adapters → the agentic distill() behind one swappable boundary "
                   "→ open the draft as a real PR against /content → merge renders to the "
                   "Library and sends per-reader. Accept: a fixture event flows end to end; no "
                   "auto-publish path exists."),
        LetterItem(tag="phase 5", title="Library, private corpora & MCP",
                   body="The Hub archive; encrypted-at-rest corpora that never transmit; one "
                   "MCP server per source system so data and corpora stay in the operator's "
                   "environment. Accept: a corpus round-trips locally encrypted; the distiller "
                   "reads sources only through MCP."),
        LetterItem(tag="phase 6", title="Open-source release",
                   body="Slot-marked templating for operator repopulation, MIT + self-host "
                   "docs, verified no-telemetry / no-JS / WCAG AA. Accept: a fresh operator "
                   "clones, repopulates slots, self-hosts, and publishes their first surface "
                   "from the README alone."),
    ]
    claims = [
        Claim(text="Phase 2 (the typed core) is done and green; the dependency-correct next "
              "step is Phase 0 — tokens + component kit — so every later surface is consistent.",
              evidence=[Trace(source_id="doc-roadmap", locator="Phase 0 / Phase 2")],
              confidence=0.9, topics=["process", "design"]),
        Claim(text="Phase 3 surfaces must render from Surface objects, not static copy — the "
              "Rev1 renderer already proves this and becomes the seed.",
              evidence=[Trace(source_id="doc-roadmap", locator="Phase 3 acceptance")],
              confidence=0.9, topics=["core", "design"]),
        Claim(text="Phase 4 keeps the gate load-bearing: agent drafts, PR reviews, merge "
              "publishes — there is no auto-publish path.",
              evidence=[Trace(source_id="doc-roadmap", locator="Phase 4 acceptance")],
              confidence=0.95, topics=["process"]),
        Claim(text="Every phase keeps docs in sync and holds the visual contract — flat "
              "editorial, radius 0, the 3px accent, the three-font system.",
              evidence=[Trace(source_id="doc-roadmap", locator="Cross-cutting")],
              confidence=0.9, topics=["design", "process"]),
    ]
    plan = Surface(
        id="report-plan", template=REPORT,
        title="The build plan — GSD discuss → plan, phases 0–6",
        eyebrow="Report · the plan you review",
        byline=[AUTHOR],
        blocks=[
            KpiStripBlock(items=[
                KpiItem(label="Phases", value="2 / 7", delta="core done", dir="up"),
                KpiItem(label="Up next", value="Phase 0"),
                KpiItem(label="Open for review", value="this plan"),
            ]),
            ProseBlock(text="This is the GSD discuss → plan output, delivered the way you asked "
                       "— as a Report you fully review before any code is cut. It reads the spec "
                       "set as the source of truth and sequences the remaining phases in "
                       "dependency order. The typed core (Phase 2) is already done; the "
                       "dependency-correct next move is Phase 0, the design foundation every "
                       "later surface sits on. Approve, amend, or send it back."),
            DiagramBlock(title="What the phases build toward", svg=two_layer(),
                         caption="Every remaining phase serves this picture: the typed truth "
                         "(done), the surfaces that render it (Phase 0/1/3), and the human-gated "
                         "loop that publishes them (Phase 4+)."),
            ItemsBlock(heading="The phases, in order", items=phases),
            ClaimsBlock(heading="Plan claims — traced to the roadmap", claims=claims),
            FanoutBlock(heading="On approval, this produces", links=[
                FanoutLink(kind="report", title="Phase 0 — atomic task plan (next GSD cut)"),
            ]),
        ],
        traces=[roadmap],
        review=Review(policy=REPORT.review_policy, author=AUTHOR),
        provenance=Provenance(tool="GSD", session_id="gsd-discuss-plan",
                              artifacts=["docs/roadmap.md", "docs/architecture.md"]),
    )
    plan.open_pull_request(pr_url="(awaiting your review)")  # In Review on purpose
    return plan


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
# Learning re-cut + onboarding path (LEARN-01/02/03) — the newcomer surface
# --------------------------------------------------------------------------- #
#
# This is the END-TO-END dogfood of Phase 12: we re-cut the richest reviewed record
# (report-datamodel) into a newcomer-shaped learning surface, and sequence it into an
# ordered onboarding track. FAITHFUL, not suggestive: the re-cut SELECTS / ORDERS / LINKS
# the report's EXISTING traced claims (and their content-addressed traces) — it authors NO
# new factual prose. A glossary term with no genuine DEFINING claim in the record routes to
# the honesty panel (missing[]) instead of being fabricated. Here, the record's claims
# define "Report", "Article" and "capture" ("X is/are …"), so those gloss; "Distillation",
# "Surface" and "the review gate" are concepts the datamodel decisions USE but never DEFINE,
# so they are shown to the reader as gaps, never invented.

# The glossary terms a newcomer most wants to look up while reading the data-model guide.
# Mix of glossable + un-glossable on purpose — the un-glossable ones prove the honesty panel.
_LEARNING_GLOSSARY = ["Report", "Article", "capture", "Distillation", "Surface", "the review gate"]


def _datamodel_distillation(datamodel_report: Surface) -> Distillation:
    """Recover the reviewed Distillation behind report-datamodel, to re-cut FAITHFULLY.

    We do NOT hand-author new claims: we lift the report's existing traced ``Claim``s
    straight off its ``ClaimsBlock``s (they carry the content-addressed traces minted by
    ``_address_report``), and carry the report's ``Source`` traces through. The result is the
    SAME reviewed truth — so the learning re-cut's glossary definitions render with the exact
    working provenance links the report shows. (We rebuild a Distillation rather than thread
    one out of ``build_report`` because ``build_report`` returns the Surface, not its
    Distillation; the claims it carries ARE that Distillation's claims.)
    """
    claims: list[Claim] = []
    for block in datamodel_report.blocks:
        if isinstance(block, ClaimsBlock):
            claims.extend(block.claims)
    return Distillation(
        narrative="",
        claims=claims,
        traces=list(datamodel_report.traces),
    )


def _learning_recut(datamodel_report: Surface) -> Surface:
    """Re-cut report-datamodel into the newcomer learning surface (Draft → published gate)."""
    surface = learning_surface(
        _datamodel_distillation(datamodel_report),
        surface_id="learning-datamodel",
        title="How the data model works — a newcomer's guide",
        eyebrow="Learning · for your first week",
        audience=READERS["newcomer"],
        glossary_terms=_LEARNING_GLOSSARY,
        # Prerequisite context = LINKS to the records this builds on (resolved via
        # Site.by_slug at render time), NOT new exposition.
        prerequisites=["show-ep01", "report-datamodel"],
        author=AUTHOR,
    )
    # No auto-publish: the learning surface passes the SAME gate as every surface. Its
    # template carries a light review policy (self-approve), so the author can approve — but
    # it goes through publish() explicitly, exactly like the dogfood reports (CLAUDE.md).
    surface.publish(reviewer=AUTHOR)
    return surface


def _onboarding_path() -> OnboardingPath:
    """The newcomer track: watch the build → read the decisions → read the newcomer guide.

    An ORDERED sequence of slug refs over surfaces that ALREADY passed the review gate
    (show-ep01, report-datamodel, learning-datamodel). It is navigation, not a Surface — it
    publishes nothing new (A5). ``render_path`` resolves each step via ``Site.by_slug``.
    """
    return OnboardingPath(
        id="onboarding-newcomer",
        title="Start here — a new contributor's first week",
        audience_label="A new contributor",
        steps=[
            OnboardingStep(slug="show-ep01", label="Watch the build (Episode 01)"),
            OnboardingStep(slug="report-datamodel", label="Read the decisions (the data model)"),
            OnboardingStep(slug="learning-datamodel", label="Read the newcomer's guide"),
        ],
    )


# --------------------------------------------------------------------------- #
# Assemble + render
# --------------------------------------------------------------------------- #

def build_surfaces() -> list[Surface]:
    """Assemble the full Rev1 surface set (ordered by distillation distance)."""
    kickoff, datamodel, rev1 = _sources_and_reports()
    plan = _plan_report()
    article = _article(datamodel)
    show = _show()
    newsletters = [_newsletter_for(k) for k in ("jj", "nate", "newcomer")]
    # The learning surface re-cuts report-datamodel for newcomers — it joins the Site as the
    # 5th surface type and the ledger assigns it L-001 (do NOT hardcode the ref).
    learning = _learning_recut(datamodel)
    return [show, kickoff, datamodel, rev1, plan, article, *newsletters, learning]


def build_site(out_dir: str | Path = "content/rev1/site") -> list[Path]:
    """Render every surface + the Library index to standalone HTML. Returns written paths.

    Page-driven (SITE-01): identity comes from the append-only ledger
    (``content/rev1/ids.json``) via the ``Site`` model, not from list position. Each
    page is written to ``out / page.href`` (== ``{slug}.html`` == ``{surface.id}.html``
    for the Rev1 corpus, L3 backward-compat — filenames stay byte-stable), and the
    Library index is rendered from a ``Site`` so its row labels are the stable refs
    (``R-001`` / ``EP01`` / ``A-001``), never a positional index.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_surfaces()
    # The ledger is the source of truth for refs; load it, build the full Site, and
    # persist any newly-assigned refs (append-only — existing entries are immutable).
    ledger = Ledger.load("content/rev1/ids.json")
    site = Site.from_surfaces(surfaces, ledger=ledger)
    ledger.save()
    written: list[Path] = []
    for page in site.pages():
        p = out / page.href
        # Pass the resolved Site + this Page so the nav resolves to four real
        # destinations and the breadcrumb/prev-next can find this page's neighbors.
        p.write_text(render_surface(page.surface, site=site, page=page), encoding="utf-8")
        written.append(p)
    # Route split (SITE-02 / N4): the marketing Home owns index.html; the Library archive
    # moves to library.html. Per-surface {slug}.html filenames stay byte-stable (Phase-8 L3).
    index = out / "index.html"
    index.write_text(render_home(site), encoding="utf-8")
    written.append(index)
    # The onboarding path (LEARN-03) renders to its OWN page — an ordered track over
    # already-gated surfaces (show-ep01 → report-datamodel → learning-datamodel), resolved
    # against the full Site so each step links to its real {slug}.html with in-track prev/next.
    path = _onboarding_path()
    path_page = out / "onboarding-newcomer.html"
    path_page.write_text(render_path(path, site=site), encoding="utf-8")
    written.append(path_page)

    # Library lists one representative newsletter (the rest are its per-reader re-cuts).
    listed = [s for s in surfaces if not (s.kind == "newsletter" and s.id != "newsletter-jj")]
    library = Site.from_surfaces(listed, ledger=ledger)
    library_page = out / "library.html"
    # Surface the onboarding track from the Library (per RESEARCH Open-Q2: a track is NOT a
    # gate-state board column — it has no review state — so it is offered as a callout link
    # above the board, NOT mixed into Draft/In Review/Published). We add this here, in the
    # build (which owns content/rev1/), rather than in render.py: it is a deterministic,
    # render-output-derived injection at a STABLE anchor (the end of the Library masthead),
    # so the regen stays byte-stable and render.py keeps its disjoint ownership.
    library_html = render_library(library)
    library_html = library_html.replace(
        _LIBRARY_MAST_ANCHOR,
        _LIBRARY_MAST_ANCHOR + _onboarding_callout(path),
        1,
    )
    library_page.write_text(library_html, encoding="utf-8")
    written.append(library_page)
    return written


# The stable anchor that closes the Library masthead in render.render_library's output. The
# onboarding-track callout is injected immediately AFTER it (deterministic → byte-stable).
_LIBRARY_MAST_ANCHOR = (
    "One reviewed record, four surfaces — the Newsletter re-cuts per "
    "reader from their own private corpus.</figcaption></figure></div>"
)


def _onboarding_callout(path: OnboardingPath) -> str:
    """A small, no-JS Library callout linking to the onboarding track page.

    Honest navigation only: it reuses the existing masthead/prose styling, adds no external
    asset and no script, and points at the rendered ``onboarding-newcomer.html``. The track
    is a learning path (no review state), so it lives ABOVE the gate-state board, not in it.
    """
    return (
        '<div class="masthead" style="margin-top:8px">'
        '<div class="sg-eyebrow">New here? &middot; an ordered track</div>'
        '<div class="prose"><p>'
        f'<a href="onboarding-newcomer.html">{path.title}</a> — '
        f'{len(path.steps)} steps, in order: watch the build, read the decisions, '
        'then read the newcomer&rsquo;s guide. Every step links to its already-reviewed surface.'
        '</p></div></div>'
    )
