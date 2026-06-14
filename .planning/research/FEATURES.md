# Feature Research

**Domain:** Semantic information distillation framework — one reviewed, evidence-traced record fanned out into audience-specific surfaces (report / article / newsletter / show), with claim-level provenance, a human review gate (review = a git PR), per-reader personalization from a local corpus, and a pluggable distill backend (manual / OSS tool / AI).
**Researched:** 2026-06-14
**Confidence:** MEDIUM (cross-checked across 5 comparable categories via web sources; no single OSS competitor implements the integrated whole, so the *combination* is inferred rather than observed — LOW on the integrated UX, MEDIUM/HIGH on individual category norms)

> **Scope note.** This is a *brownfield Rev2* study. Rev1 already ships the typed spine
> (`Source → Claim(+Trace) → Distillation → Surface`), the `Draft → InReview → Published` gate with
> no auto-publish, surfaces-as-presets, human-gated promotions, deterministic `capture.py`, and the
> token-faithful no-JS HTML renderer. Those are marked **[Rev1 ✓]** below so the table reads as a
> landscape, not a backlog. New Rev2 scope is marked **[Rev2]**.

## Comparable categories surveyed

The brief names five adjacent slices; the integrated product spans all of them. Per-category norms:

| Category | Representative tools | What they set as the bar |
|----------|----------------------|--------------------------|
| Private ingest + grounded answers | Onyx/Danswer, RAGFlow | Cited answers linked to originals; permission-respecting retrieval; 40+ connectors; self-host |
| Claim→evidence provenance | GenProve, Valsci, sciwrite-lint, PaperTrail (CHI'26), CiteCheck, TROVE | Sentence-level attribution; supported / unsupported / *omitted* signalling; faithfulness ≠ correctness |
| Changelog / release-notes automation | ReleaseNotes.io, LaunchNotes, Release Drafter | One source of truth → web changelog + in-app widget + email digest; audience segmentation; two-stage (raw → curated) |
| Internal-comms / editorial | Planable, Contentful, Simpplr, Hootsuite | Author→editor→legal/HR→sign-off; calendar/cadence; tasks & comments; scheduled publish |
| Personalized digest | Rasa.io, Ittybrief, Digest | Per-reader interest profile; relevance ranking; learn-from-engagement |

## Feature Landscape

### Table Stakes (Users Expect These)

Missing any of these makes the product feel incomplete for *this* category. Most are already in Rev1 — the category bar is high, but Rev1 cleared most of it.

| Feature | Why Expected | Complexity | Notes / Dependencies |
|---------|--------------|------------|----------------------|
| **Per-claim citation linking source → claim** | Onyx/RAGFlow/PaperTrail all link every assertion back to a retrievable original; without it the "trust layer" claim is empty | LOW (Rev1) | **[Rev1 ✓]** `Claim(+Trace)` exists. Rev2 must make cited sources *real clickable links* (brief: `vision.md` → repo file). Depends on: per-surface IDs. |
| **Draft → review → publish gate** | Every editorial/internal-comms tool gates publish behind an explicit sign-off step | LOW (Rev1) | **[Rev1 ✓]** `Draft → InReview → Published`. Bar is met; the *mechanism* (review = git PR) is a differentiator (below). |
| **Self-hostable, no phone-home** | Onyx/RAGFlow/listmonk users self-host for data residency; an audit tool that exfiltrates content is a contradiction | LOW (Rev1) | **[Rev1 ✓]** MIT, no telemetry, no external calls on content. Constraint, not a build item. |
| **Multi-format ingest (PPT/Excel/Email/docs)** | Unstructured/RAGFlow set the expectation that "any office artifact goes in." Operators won't pre-convert files by hand | MEDIUM | **[Rev2]** Format adapters (python-pptx, openpyxl, email libs, Power BI export). Depends on: distill socket contract. The *common case is deterministic structure-pull*, AI only for residue. |
| **Multi-surface output from one record** | Changelog tools generate web + widget + email + community from one source; users won't maintain N copies | LOW (Rev1) | **[Rev1 ✓]** Surfaces-as-presets over one `SurfaceTemplate`. Bar met. Rev2 adds cross-links between surfaces. |
| **Renders/exports a readable artifact** | Every tool produces a publishable surface (web page, email, PDF) | LOW (Rev1) | **[Rev1 ✓]** Token-faithful standalone HTML, light/dark, no-JS, WCAG AA. |
| **"Unsupported / missing" surfaced to reviewer** | PaperTrail's core finding: showing *omitted* and *unsupported* claims is what makes provenance trustworthy (not just showing the supported ones) | LOW (Rev1) | **[Rev1 ✓]** `missing[]` shown to reviewer, never published silently. This is now table stakes in the provenance category, not a differentiator. |
| **Cadence / scheduling config per surface** | Editorial calendars + digest tools treat cadence as a first-class field | LOW (Rev1) | **[Rev1 ✓]** Cadence is typed config on the surface preset. |
| **Status board by gate state** | Editorial/internal-comms tools show a kanban/calendar of what's in-flight by stage | MEDIUM | **[Rev2]** Library reframed as a status board (columns by gate state). Brief item. Depends on: per-surface IDs, IA split. |

### Differentiators (Competitive Advantage)

Where Newsletters competes. These align with PROJECT.md Core Value: *"the trust-and-publish layer is the product."* No surveyed tool ships the full set.

| Feature | Value Proposition | Complexity | Notes / Dependencies |
|---------|-------------------|------------|----------------------|
| **Review = a real git PR (merge publishes)** | Editorial tools gate with in-app comments; nobody makes the review a *version-controlled, diffable, attributable PR*. Gives free audit trail, blame, rollback, and reviewer identity | LOW (Rev1) | **[Rev1 ✓]** This is the strongest differentiator — it reframes "approval workflow" as "code review" and inherits Git's auditability for free. |
| **Pluggable distill socket: by-hand / OSS / AI behind one interface** | Onyx/RAGFlow *are* the AI; they can't degrade to no-AI. A swappable backend that all emit the same typed `Distillation` lets a token-constrained operator run the whole spine with zero AI | HIGH | **[Rev2]** The contract shape is **[OPEN]**. Hardest + highest-value Rev2 item. Enabler for: format adapters, AI backend, no-AI mode. |
| **Faithful, not suggestive (extract + trace, never editorialize)** | Every AI generation tool editorializes by design; that is exactly what breaks auditability. A distill step *forbidden* from emphasis/narrative is unique and is what makes the trace meaningful | MEDIUM | **[Rev2]** Enforcement rule on the socket output (extraction must map to source spans; no synthesized claims). Depends on: distill socket. Cross-listed as the discipline behind the **anti-feature** "editorializing distillation." |
| **Manual capture as a first-class, deterministic path** | Digest/changelog tools assume automation; none treat "operator structured this by hand, no LLM" as the primary, supported workflow | LOW (Rev1) | **[Rev1 ✓]** `capture.py`: finished work session → Draft Report, no LLM. Primary path for the token-constrained operator, not a fallback. |
| **Claim-level provenance UX (supported / unsupported / omitted, brushing-and-linking)** | PaperTrail (CHI'26) shows this UX *lowers misplaced trust* and supports overview→zoom→details-on-demand. Bringing that interaction model to a *publishing* tool (not just Q&A) is novel | MEDIUM | **[Rev2]** Renderer/template work: hover/highlight claim↔source span, gate badge, margin annotations (brief mentions margin annotations + color-coded SVG). Depends on: real source links, per-surface IDs. |
| **One parameterized `SurfaceTemplate`, operators register their own surfaces** | Changelog tools hardcode channels; here report/article/newsletter/show are *configs*, and an operator can add a new surface without new classes | MEDIUM (Rev1 base) | **[Rev1 ✓]** Extensibility is the edge. Rev2: per-surface IDs (`EP01`, `R-001`, slug, issue/date) fix the numbering-collision bug. |
| **Human-gated promotions (`Claim → KPI`, `Report → Article`)** | Promotion-with-peer-review across artifact types is unusual; it models how knowledge actually graduates (a finding becomes a metric; a report becomes a published article) | LOW (Rev1) | **[Rev1 ✓]** Already typed and gated. |
| **Per-reader personalization from a *local* corpus** | Rasa.io/Ittybrief personalize via cloud engagement tracking; doing it from a self-hosted corpus (no telemetry) is rare and on-brand | HIGH | **[v2+ / boundary]** Personalization is typed config on the surface today; the *learning* engine is explicitly **V3 PulseIQ (out of scope)**. Keep the hook, defer the engine. |
| **Token-faithful, no-JS, WCAG-AA standalone artifact** | Most tools require a hosted runtime/JS; emitting a self-contained accessible HTML file is a portability + trust differentiator | LOW (Rev1) | **[Rev1 ✓]** Renders without JavaScript; full light/dark via tokens. |

### Anti-Features (Deliberately NOT Built)

Documented to prevent scope creep and to protect the Core Value. The first two are non-negotiable per PROJECT.md.

| Feature | Why Requested | Why Problematic | Alternative (what we do instead) |
|---------|---------------|-----------------|----------------------------------|
| **Auto-publish (any kind)** | "Just ship it on merge/schedule without a human" feels efficient; every changelog/digest tool offers scheduled auto-send | Violates the human-in-the-loop core; a single ungated mistake destroys the trust thesis that *is* the product | **No auto-publish path, ever.** Publish requires a human-merged PR. Scheduling sets cadence, never bypasses the gate. |
| **Editorializing / suggestive distillation** | "Make the AI write a punchy narrative / pick the highlights" is the default ask for any generation tool | Synthesized emphasis can't be traced to a source span → breaks auditability; the trace becomes decorative | **Faithful extract + trace only.** Emphasis/narrative is the human's job (later, the configured corpus's). Distill output must map to source spans. |
| **LLM as authority / required dependency** | "Just let the model decide what's true / always run the AI" | Couples the trust spine to a non-deterministic, token-costly, potentially-offline dependency; excludes the token-constrained primary user | **AI-optional.** `langchain` → optional extra; spine runs with zero AI. AI is one swappable socket, never the spine. |
| **Telemetry / cloud engagement tracking for personalization** | Rasa.io-style "learn from clicks" is the standard personalization mechanism | Phone-home on content contradicts self-host + no-external-calls constraint | **Local corpus personalization** now (typed config); learning engine deferred to **V3 PulseIQ** (private, out of OSS scope). |
| **Owning the problem-solving / working agent** | "Also let it *do* the work, not just report it" | Massive scope; not the trust-layer thesis; the working agent is the operator's | Newsletters owns **capture + trust + publish** only. Integrate with, don't replace, the operator's working agent. |
| **Heavy in-app WYSIWYG editor + comment threads** | Editorial tools (Planable/Contentful) make this table stakes for *their* category | Re-implements what Git/PR review already gives for free; pulls toward a hosted SaaS shape and away from self-host portability | **Review happens in the PR.** Optional live editor/preview in the rendered Library is a *read/preview* affordance (brief: graft blog's live editor/preview pattern), not a parallel approval system. |
| **Connector sprawl (40+ source integrations like Onyx)** | "Ingest from everything" looks competitive vs RAGFlow/Onyx | Each connector is maintenance + a place for un-traced data to leak in; dilutes the deterministic-extraction focus | **Format adapters first** (PPT / Power BI / Excel / Email) — deterministic, low-token, structure already in the file. Add connectors only behind the distill socket, demand-driven. |

## Feature Dependencies

```
Distill socket (one interface, swappable backends)        [Rev2, OPEN contract]
    ├──enables──> Format adapters (PPT/Excel/Email/Power BI)   [Rev2]
    ├──enables──> AI distill backend (optional extra)          [Rev2]
    ├──enables──> By-hand backend = capture.py                 [Rev1 ✓]
    └──constrained-by──> "Faithful, not suggestive" rule       [Rev2]
                              └──guarantees──> meaningful Claim(+Trace)

Per-surface IDs (EP01 / R-001 / slug / issue-date)        [Rev2]
    ├──requires──> nothing (foundational fix)
    ├──enables──> Real traceable source links                  [Rev2]
    ├──enables──> Status board by gate state                   [Rev2]
    └──enables──> Cross-links between surfaces                 [Rev2]

Real source links  ──enables──>  Claim-level provenance UX     [Rev2]
                                  (supported/unsupported/omitted,
                                   brushing-and-linking, margin annotations)

IA split (Home vs Library status-board)  ──requires──> per-surface IDs
                                          ──enables──> real navigation (4 links → 4 destinations)

Review = git PR  [Rev1 ✓]  ──conflicts──>  in-app approval workflow / WYSIWYG  [anti-feature]
AI-optional core ──conflicts──>  LLM-as-required-dependency                    [anti-feature]
Human review gate ──conflicts──>  auto-publish / scheduled auto-send           [anti-feature]
Faithful extraction ──conflicts──>  editorializing distillation                [anti-feature]
```

### Dependency Notes

- **Distill socket gates almost all Rev2 backend work.** Its contract is **[OPEN]** in the brief; it must be designed before format adapters or an AI backend can be built against a stable interface. It is the critical-path Rev2 item.
- **Per-surface IDs are the foundational renderer fix.** The numbering-collision bug (IDs derived from list position) blocks real source links, the status board, and cross-links. Cheap to do, unblocks several Rev2 site items.
- **"Faithful, not suggestive" is a constraint on the socket, not a separate component.** It must be enforced where backend output enters the pipeline (every emitted claim maps to a source span; nothing synthesized). It is what makes `Claim(+Trace)` worth trusting.
- **Provenance UX depends on real source links existing first.** The PaperTrail-style supported/unsupported/omitted interaction (and margin annotations) needs clickable, addressable sources and claim IDs underneath it.
- **The four hard conflicts are the anti-features.** Each competing-category "table stake" (in-app approval, required AI, auto-send, editorialized copy) directly conflicts with a Newsletters differentiator. Keeping them out is a feature.

## MVP Definition

> "MVP" here = the **Rev2 milestone slice**, since Rev1 already ships the spine.

### Launch With (Rev2 core)

- [ ] **Distill socket interface** — defines the backend contract; everything else hangs off it. *Critical path; resolve the [OPEN] contract shape first.*
- [ ] **By-hand backend formalized as a socket backend** — `capture.py` reframed to emit `Distillation` through the socket; proves the no-AI path end-to-end.
- [ ] **"Faithful, not suggestive" enforcement** — output validation that claims map to source spans; cheap to state, defines the product.
- [ ] **Per-surface IDs** — fixes numbering collisions; unblocks links, board, cross-links.
- [ ] **Real traceable source links** — cited sources become clickable repo/file links; the minimum credible provenance UX.
- [ ] **AI-optional packaging** — move `langchain` to an optional extra; spine installs and runs with zero AI deps. *Validates the whole thesis.*
- [ ] **Rev2 site IA fix** — split real Home from Library status-board; four nav links → four destinations.

### Add After Validation (Rev2.x)

- [ ] **Format adapters (PPT / Excel / Email / Power BI)** — once the socket contract is stable; start with the format with the most structure-already-in-the-file (Excel/openpyxl is the cleanest deterministic win). *Trigger: socket proven with by-hand + AI backends.*
- [ ] **Claim-level provenance UX** (supported/unsupported/omitted, brushing-and-linking, margin annotations) — *trigger: real source links shipped and a reviewer asks "show me what's NOT covered."*
- [ ] **AI distill backend** behind the socket — *trigger: deterministic backends shipped; AI used only for the messy residue.*
- [ ] **Status board + cross-links + clickable fan-out diagram** — *trigger: per-surface IDs landed.*

### Future Consideration (v2+ / explicit boundary)

- [ ] **Per-reader corpus personalization engine (learning over runs)** — *defer: this is V3 PulseIQ, private + out of OSS scope. Keep the typed personalization hook on surfaces; do not build the learning engine in V2.*
- [ ] **Additional ingest connectors (Slack/Confluence/etc.)** — *defer: connector sprawl is an anti-feature until demand-driven; format adapters cover the primary case.*

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Distill socket interface | HIGH | HIGH | P1 |
| AI-optional packaging (langchain → extra) | HIGH | LOW | P1 |
| "Faithful, not suggestive" enforcement | HIGH | MEDIUM | P1 |
| Per-surface IDs | MEDIUM | LOW | P1 |
| Real traceable source links | HIGH | LOW | P1 |
| Rev2 site IA split (Home / Library board) | MEDIUM | MEDIUM | P1 |
| By-hand backend through socket | HIGH | LOW | P1 |
| Format adapters (PPT/Excel/Email/Power BI) | HIGH | MEDIUM | P2 |
| Claim-level provenance UX | HIGH | MEDIUM | P2 |
| AI distill backend | MEDIUM | MEDIUM | P2 |
| Status board / cross-links / fan-out diagram | MEDIUM | MEDIUM | P2 |
| Corpus personalization *engine* | HIGH | HIGH | P3 (V3 boundary) |
| Extra source connectors | LOW | MEDIUM | P3 |

**Priority key:** P1 = Rev2 must-have · P2 = add after Rev2 core validates · P3 = defer / out of OSS scope.

## Competitor Feature Analysis

| Feature | Onyx / RAGFlow (grounded answers) | ReleaseNotes.io / LaunchNotes (changelog) | PaperTrail / GenProve (provenance) | Rasa.io / Ittybrief (digest) | **Newsletters approach** |
|---------|-----------------------------------|-------------------------------------------|------------------------------------|------------------------------|--------------------------|
| Provenance | Cited answer, doc-level link | Minimal / none | Sentence-level, supported/unsupported/**omitted** | None | **Claim(+Trace) + `missing[]`**, PaperTrail-style UX in a *publishing* tool |
| Review/approval | None (chat) | In-app draft→sign-off | N/A (research UI) | None | **Review = git PR; merge publishes** |
| Multi-surface fan-out | Single chat surface | One source → web/widget/email | N/A | One digest | **One record → report/article/newsletter/show via one `SurfaceTemplate`** |
| Personalization | Permission-scoped retrieval | Segment by plan/region | N/A | ML on cloud engagement | **Local-corpus config now; learning = V3, out of scope** |
| Extraction backend | LLM-required RAG | Git history / manual | LLM-required | LLM-required | **Pluggable socket: by-hand / OSS / AI; degrades to no-AI** |
| Editorializing | Yes (generates prose) | Yes (rewrites for audience) | No (extracts) | Yes | **No — faithful extract + trace only** |
| Auto-publish | N/A | Scheduled auto-send | N/A | Scheduled auto-send | **Never — human-merged PR only** |
| Hosting / privacy | Self-host option | Mostly SaaS | Research prototype | SaaS, telemetry | **Self-host, MIT, no telemetry, no calls on content** |

## Sources

Web-sourced (provider seam disabled in this environment → built-in WebSearch; confidence MEDIUM where a finding is corroborated across categories, LOW where single-source). No OSS competitor implements the integrated whole, so the *combined* product UX is inferred.

- Onyx/Danswer — grounded cited answers, self-host, connectors: https://onyx.app/ , https://github.com/eea/danswer , https://www.seaflux.tech/blogs/onyx-ai-enterprise-search-assistant/
- RAGFlow / Unstructured — pluggable document extraction, format parsers, connectors: https://deepwiki.com/infiniflow/ragflow , https://github.com/Unstructured-IO/unstructured , https://docs.unstructured.io/open-source/introduction/overview
- DocPipeline — pluggable extraction-backend abstraction (swap engines without changing logic): https://www.docpipeline.net/
- Changelog/release-notes multi-audience fan-out, segmentation, two-stage curation: https://www.releasenotes.io/ , https://www.appcues.com/blog/changelog-vs-release-notes , https://userorbit.com/blog/best-product-changelog-and-release-notes-software
- Internal-comms / editorial approval workflows & cadence: https://www.contentful.com/blog/tasks-and-comments-supercharge-your-content-approval-workflow/ , https://planable.io/blog/communications-calendar/ , https://www.prdaily.com/how-to-create-an-internal-email-editorial-calendar-for-your-comms-team/
- Claim/evidence provenance UX (supported/unsupported/**omitted**, brushing-and-linking, details-on-demand; trust calibration): PaperTrail, CHI'26 — https://arxiv.org/abs/2602.21045 , https://dl.acm.org/doi/10.1145/3772318.3791101
- Provenance research norms (sentence-level attribution; faithfulness ≠ correctness; citation hallucination): GenProve https://arxiv.org/html/2601.04932v2 , CiteCheck https://arxiv.org/html/2605.27700v1 , "Correctness is not Faithfulness" https://arxiv.org/pdf/2412.18004 , TROVE https://arxiv.org/pdf/2503.15289
- Personalized digest norms (interest profile, relevance ranking, learn-from-engagement): https://www.junia.ai/blog/ai-tools-newsletters , https://www.sciencedirect.com/science/article/pii/S187705092401408X
- Internal project context: .planning/PROJECT.md , .planning/brief.md

---
*Feature research for: semantic information distillation framework (Newsletters Rev2)*
*Researched: 2026-06-14*
