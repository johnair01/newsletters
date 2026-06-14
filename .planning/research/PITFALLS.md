# Pitfalls Research

**Domain:** Semantic information distillation framework — faithful structured extraction (PPTX/XLSX/Power BI/Email) → claim-level provenance → human review gate → multi-surface fan-out, with a swappable distill backend (manual / OSS / AI)
**Researched:** 2026-06-14
**Confidence:** MEDIUM-HIGH (extraction-fidelity and faithfulness pitfalls are HIGH — corroborated by official library docs and summarization-faithfulness research; provenance-integrity and review-gate pitfalls are MEDIUM — inferred from data-lineage and HITL literature applied to this specific architecture)

> **Framing.** This project's stated core value is "the trust-and-publish layer IS the product."
> Every pitfall below is scored by one question: *does it let an unfaithful claim reach a reader,
> or let an "optional" AI quietly become load-bearing?* Those are the two failure modes that
> destroy the thesis. Everything else is secondary.

---

## Critical Pitfalls

### Pitfall 1: Silent extraction loss — the file said more than the adapter captured

**What goes wrong:**
Format adapters (python-pptx, openpyxl, Power BI export, email lib) silently drop content that the
human author considered part of the message. python-pptx does not expose **SmartArt text** and
**grouped-shape text** through its normal shape API (the text lives in OOXML the high-level API
skips). openpyxl: when a workbook was last saved by openpyxl rather than opened in Excel, **formula
cells have no cached value** — `data_only=True` returns `None`; **images and charts are dropped on
load**; **merged cells** return a value only in the top-left cell and `None` everywhere else.
Power BI "summarized" export gives **aggregated rows, not the underlying data**, and truncates at
fixed row caps (30k CSV / 150k Excel / 16 MB DirectQuery) — the export looks complete but is a
ceiling-clipped aggregate. Email: nested `message/rfc822` (forwarded mail), charset mismatches
(header says ISO-8859-1, body is UTF-8), and `is_multipart()` lying on non-compliant messages all
drop or mangle body text. **The data that drives the decision is often in the chart/image/notes the
text-only extractor never sees.** A claim built on a partial extraction is unfaithful even though
no AI touched it.

**Why it happens:**
Adapters are written and tested against clean, simple fixtures. The high-level library API "returns
text," so it feels complete. Loss is invisible because the adapter has no concept of "what it
*didn't* read" — there is no error, just absence.

**How to avoid:**
- **Extract with a completeness contract, not best-effort.** Every adapter emits, alongside its
  `Claim(+Trace)` output, a **coverage manifest**: shape/cell/part counts seen vs. skipped, and an
  explicit `unextracted[]` list (SmartArt, grouped shapes, charts, images, formula-cells-with-no-cache,
  truncated-export warnings). Route `unextracted[]` into the existing `missing[]` reviewer channel —
  the reviewer must SEE that the slide had a diagram the extractor couldn't read.
- For PPTX, **walk OOXML as a fallback** for SmartArt/grouped shapes; recurse group shapes explicitly.
- For XLSX, **detect openpyxl-saved-without-cache** and surface "formula values unavailable — reopen
  in Excel" rather than emitting `None` as if it were data. Unmerge-and-fill or record merge ranges.
- For Power BI, **require underlying-data export** (not summarized) and **fail loud on row-cap hit**.
- For email, decode by declared charset with fallback + replacement logging; handle `message/rfc822`
  recursively; never trust `is_multipart()` alone.
- **Round-trip fidelity test in CI:** known fixture → extract → assert every authored unit is either
  captured or explicitly listed in `unextracted[]`. Zero silent drops.

**Warning signs:**
- Adapter code has no notion of "skipped" — only returns content.
- Extracted text from a deck/sheet is suspiciously short vs. the source.
- `data_only=True` returning `None` for cells that clearly show numbers in Excel.
- No fixtures containing SmartArt, grouped shapes, merged cells, charts, or forwarded email.

**Phase to address:**
Format-adapters phase. **The coverage manifest / `unextracted[]` contract must be designed at the
distill-socket interface phase (before any adapter is built)**, because retrofitting it after three
adapters exist means rewriting all three.

---

### Pitfall 2: Provenance that points at a moving target (traceability rot)

**What goes wrong:**
A `Trace` links a `Claim` to evidence — but the link is by file path, line number, slide index, or
list position rather than to **immutable, content-addressed evidence**. The Rev2 brief already names
one instance: **"numbering collision — per-list-position IDs"** that shift when a list reorders. Same
class of bug at the evidence layer: the source PPTX gets re-saved (slide 4 becomes slide 5), the
spreadsheet gets a new row, the cited `vision.md` line moves — and every `Trace` now points at the
wrong evidence while still *looking* valid. "If you cannot trace it, you cannot trust it." A trace
that resolves to the wrong span is worse than a missing trace: it launders an unfaithful claim as
audited.

**Why it happens:**
Positional/path references are the easy thing to capture at extraction time. Nobody re-validates
traces after the source changes, because there's no mechanism that detects drift — the link still
"resolves," just to different content.

**How to avoid:**
- **Content-address evidence, not position.** A `Trace` should pin (a) a hash of the source artifact
  *version* and (b) a hash or stable anchor of the **exact extracted span**, not "slide 4 / row 12 /
  line 30." Store the verbatim evidence text inside the Trace so the claim is verifiable even if the
  source disappears or mutates.
- **Stable per-surface and per-evidence IDs** (the brief's `EP01`/`R-001`/slug fix) — generated from
  content, never from collection index.
- **Re-validation on rebuild:** `newsletters build` recomputes source hashes; if a cited source
  changed, the affected claims are flagged STALE and **bounced back to InReview**, never silently
  re-rendered as Published.
- **Forbid a Published claim with an unresolvable or hash-mismatched Trace** at the type/validation
  layer — make it impossible to render, not just discouraged.

**Warning signs:**
- `Trace` stores `slide_index`, `row`, `line_number`, or `path` but no content hash and no verbatim
  span.
- Re-running `build` on a changed source produces no diff in claim status.
- IDs derived from `enumerate()` / list position anywhere in render or promote.
- No test that mutates a source and asserts dependent claims go STALE.

**Phase to address:**
Semantic-model / provenance phase (define `Trace` as content-addressed from the start). Re-validation
hook belongs in the renderer/build phase. The ID-collision slice is already scoped in Rev2 — extend
that fix down to the evidence layer, not just surface IDs.

---

### Pitfall 3: The "optional" AI quietly becomes required (dependency creep)

**What goes wrong:**
The thesis is "spine runs with zero AI deps; AI is one swappable socket." It erodes in small,
invisible steps. The classic mechanisms (well-documented in the Python packaging community):
**a top-level `import langchain` anywhere on the import path of the core** makes `pip install
newsletters` (without `[ai]`) raise `ModuleNotFoundError` on startup — the spine no longer runs
AI-free. **Poetry/PEP-621 misconfiguration:** a dependency marked optional but not actually wired
into an `extras`/optional-group gets resolved as a hard dependency. **Type leakage:** core models
importing an LLM library's types "just for a type hint" pulls it in. **Behavioral creep:** a default
config that selects the AI backend, or a code path that *assumes* distill produced AI-grade prose,
so the manual/OSS backends produce visibly worse output and users feel forced onto AI.

**Why it happens:**
It's frictionless. The dev machine has `[ai]` installed, so a stray top-level import never errors
locally. CI runs the full install. Nobody tests the bare install path, so the regression ships.

**How to avoid:**
- **CI gate: install the bare package (no extras) in a clean venv and run the full deterministic
  pipeline — capture → structure → review → render → fan-out — end to end.** This single test is the
  single most important guardrail for the project's core value. It must be a release blocker.
- **Lazy / function-local imports** for every AI backend; a top-level `try/except ImportError` that
  sets the backend to unavailable, never crashes the spine.
- **Architecture test:** assert that no module reachable from the core import graph imports
  `langchain` / any LLM SDK (e.g. an import-linter contract). Core models must not reference AI types.
- **Default backend = manual (or OSS), never AI.** AI is opt-in by explicit config.
- **Backend parity tests:** the same Source through hand / OSS / AI backends produces the same
  *typed shape* and all must pass the faithfulness checks — the AI path gets no structural privilege.

**Warning signs:**
- `import langchain` (or any LLM SDK) at module top level outside the `distill/backends/ai` subtree.
- No CI job runs `pip install .` (without `[ai]`) and exercises the pipeline.
- Core/model modules type-hint against AI-library classes.
- Default config or quickstart docs assume the AI backend.
- Manual/OSS backend output is treated as second-class anywhere downstream.

**Phase to address:**
The AI-optional refactor phase (moving langchain to an extra) — but the **bare-install CI gate and
import-linter contract must land in that same phase and stay green for every subsequent phase**,
because this regresses silently and continuously. Treat it as a permanent invariant, not a one-time task.

---

### Pitfall 4: The distiller editorializes — "faithful, not suggestive" leaks (hallucination & emphasis injection)

**What goes wrong:**
Distill is supposed to *extract and trace*, never editorialize — emphasis is the human's job. The
AI backend (and even an over-clever deterministic one) violates this. Summarization-faithfulness
research is unambiguous: **abstractive generation introduces information not in the source**
(extrinsic hallucination) and **contradicts the source** (intrinsic hallucination); higher
abstractiveness correlates *negatively* with faithfulness. Subtler than invented facts is
**editorializing**: the distiller adds emphasis, ordering, framing, adjectives ("strong growth,"
"concerning trend") that constitute a *claim the source never made*. Critically, **standard quality
metrics don't catch this — a summary full of hallucination can score high on ROUGE.** A claim that
reads well, traces to a real source, but says something the source didn't = the exact unfaithfulness
this product exists to prevent, now wearing a green gate badge.

**Why it happens:**
LLMs are trained to be fluent and helpful; "make it readable" and "extract verbatim" pull in opposite
directions. Developers reach for abstractive summarization because it produces nicer prose, and grade
it on fluency, not faithfulness. Emphasis injection feels like value-add, not a violation.

**How to avoid:**
- **Default to extractive, not abstractive.** Extractive selection is "inherently faithful" by
  construction. Reserve abstraction for an explicitly-flagged, separately-reviewed step.
- **Entailment gate:** every emitted claim must be *entailed by its traced evidence span* — verify
  with a faithfulness/NLI check (claim ⊑ evidence). Claims that aren't entailed go to `missing[]`,
  never to the reviewer as facts.
- **Verbatim-or-flagged rule:** a claim is either a verbatim/near-verbatim span (faithful by
  construction) or it is explicitly marked "interpreted" and routed for human emphasis decisions.
  No silent paraphrase.
- **Strip emphasis at the distill boundary.** The distiller may not introduce evaluative adjectives,
  ordering-as-priority, or framing. Emphasis is applied by the human in the surface layer, downstream
  of the gate.
- **Adversarial faithfulness fixtures:** sources designed to tempt the distiller into adding facts /
  emphasis; assert the output stays flat and traced. Run on every backend.
- **Never grade distill output on ROUGE/fluency alone** — those reward hallucination.

**Warning signs:**
- Distill backend uses an abstractive "summarize this" prompt with no entailment check.
- Output prose is more polished than the source (a tell for paraphrase/hallucination).
- Claims contain evaluative language ("significant," "worrying") absent from the source.
- Faithfulness measured only by similarity/ROUGE, never by entailment against the trace.
- A claim's text cannot be located in or entailed by its own Trace.

**Phase to address:**
Distill-socket interface phase — the **faithfulness/entailment contract is part of the backend
*interface*, enforced for all backends (hand/OSS/AI alike)**, not bolted onto the AI backend only.
Adversarial fixtures land with the first backend and gate every backend added after.

---

### Pitfall 5: The review gate becomes a rubber stamp (oversight theatre)

**What goes wrong:**
"No auto-publish; review = a real git PR; merge publishes" is structurally sound but behaviorally
fragile. HITL research is blunt: human oversight reliably degrades into **rubber-stamping** under
volume, time pressure, and automation bias — "reviewers approve without meaningful engagement,
creating illusion-of-safety rather than real control," and adding a human can *increase* throughput
while *decreasing* accuracy. If the gate shows the reviewer a polished draft and a green "looks good"
affordance, they merge without checking traces — especially as fan-out scales the number of surfaces
needing review. The gate exists in code, but the *trust* it's supposed to confer is fake.

**Why it happens:**
The PR-merge gate is easy to satisfy mechanically (click merge). Nothing forces the reviewer to
inspect the claim→evidence links. As volume grows, scrutiny numbs. The system's own polish induces
automation bias ("it's probably fine").

**How to avoid:**
- **Surface evidence at the point of review, not behind a click.** The PR diff / review view must
  show each claim *next to its verbatim Trace* and its `missing[]`/`unextracted[]` items — make the
  unfaithful thing visible by default.
- **Forcing functions over "approve":** require the reviewer to act on each `missing[]` /
  STALE / `unextracted[]` flag (acknowledge or reject), so a draft with unresolved provenance gaps
  *cannot* be merged silently. Ask "what would change this claim?" not "approve?".
- **Block merge on unresolved provenance state** in code (CI check on the PR), so "Published" is
  impossible while any claim is STALE, un-entailed, or has unresolved `missing[]` — same rigor as
  Pitfall 3's bare-install gate.
- **Keep review batches small** and prefer rotating/peer review for the `Report → Article`
  promotion (the brief already calls it peer-reviewed — enforce it).
- **Audit for rubber-stamping:** track approval latency / flag-resolution rate; near-instant approvals
  on flag-heavy drafts are the signal.

**Warning signs:**
- Review view shows prose but not the underlying traces / `missing[]`.
- Merge is possible while claims are STALE or have unresolved gaps.
- Approval is a single low-friction action with no per-flag acknowledgement.
- Approval times trending toward instant as volume grows.

**Phase to address:**
Review-gate / renderer phase — the **review view must be evidence-first**, and the merge-block CI
check on provenance state must ship with it. Reinforce during the fan-out phase (more surfaces =
more review load = more rubber-stamp pressure).

---

### Pitfall 6: Backend divergence — three distill backends, three different `Distillation` shapes

**What goes wrong:**
The socket promises "all three backends emit the same typed `Distillation`; the rest of the pipeline
is backend-agnostic." In practice the AI backend gets richer fields, the hand backend omits Trace
detail, the OSS adapter normalizes slightly differently — and downstream code grows quiet
`if backend == "ai"` branches. The "swappable socket" abstraction leaks; you no longer have one
pipeline with three backends, you have three pipelines. Manual capture (the *primary* path for the
token-constrained operator) silently becomes the worst-supported one.

**Why it happens:**
The AI backend is built/tested first because it's exciting; the interface ossifies around its output.
The manual path is "obvious" so it's under-tested. Normalization rules live in each adapter instead of
at the boundary.

**How to avoid:**
- **One normalization point + one conformance test suite that every backend must pass** (same typed
  `Distillation`, same Trace completeness, same faithfulness gate). A backend that can't pass doesn't
  ship.
- **Build the manual backend first** (it's the primary user and the zero-dep baseline); make AI conform
  to it, not vice-versa.
- **No `if backend ==` branches downstream** — assert this with an architecture test.

**Warning signs:**
- Downstream code inspects which backend produced a Distillation.
- Manual-capture path has thinner tests than the AI path.
- New backend required pipeline changes to integrate (the abstraction leaked).

**Phase to address:**
Distill-socket interface phase — define the conformance suite *with the interface*, before the second
backend exists.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Trace by position/path (slide idx, row, line) instead of content hash + verbatim span | Trivial to capture | Traceability rot (Pitfall 2); silent mis-attribution that launders bad claims | **Never** for Published claims — this is the product's core promise |
| Top-level `import langchain` in core "for now" | Code is simpler | Bare install breaks; "optional" AI becomes required (Pitfall 3) | **Never** — must be lazy/guarded from day one |
| Best-effort extraction (return text, ignore skips) | Adapters ship faster | Silent loss (Pitfall 1); unfaithful claims with no error | Only behind a coverage manifest that lists `unextracted[]` |
| Abstractive "summarize" in distill for nicer prose | Readable output | Hallucination/editorializing (Pitfall 4) graded as faithful | Only as an explicitly-flagged, separately-reviewed step |
| Build AI backend first, manual later | Demos well | Backend divergence (Pitfall 6); primary user underserved | **Never** — manual is the baseline backends conform to |
| Single-click "approve" with no flag resolution | Fast review | Rubber-stamping (Pitfall 5) | Only for drafts with zero open flags |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| python-pptx | Assuming `.text` covers everything | Recurse grouped shapes; OOXML fallback for SmartArt; capture notes slides; list anything skipped in `unextracted[]` |
| openpyxl | `data_only=True` and trusting the value | Detect openpyxl-saved-without-cache → `None` is *missing*, not zero; preserve merge ranges; flag dropped images/charts |
| Power BI export | Exporting "summarized" data | Require underlying-data export; fail loud on 30k/150k/16MB row caps; record that it's an aggregate if unavoidable |
| Python `email` | Trusting `is_multipart()` / default charset | Decode by declared charset with logged fallback; recurse `message/rfc822`; handle non-compliant multipart |
| LLM SDK (langchain) | Importing at top level / type-hinting core against it | Function-local guarded imports confined to `distill/backends/ai`; import-linter contract |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Re-hashing/re-validating every source on each build | Slow `newsletters build` | Cache source hashes; only re-validate changed sources | Hundreds of sources / large decks |
| Buffering whole emails/attachments in memory | Memory spikes on large mail | `BytesFeedParser` streaming | Large mailboxes / big attachments |
| Review load scales with surfaces × cadence | Reviewer fatigue → rubber-stamping (Pitfall 5) | Small batches, dedupe shared claims across surfaces | As fan-out grows past a handful of surfaces |

> Scale note: the primary user is a single token-constrained operator on one work codebase. Do **not**
> over-engineer for thousands of sources. The real "scale" pressure here is **review load**, not data volume.

## Security / Trust Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| AI backend phones home (provider API) on content | Violates "no external calls on content," breaks self-hostable/MIT promise | Confine network egress to the opt-in AI backend; deterministic spine makes zero external calls; document boundary |
| Telemetry slipping into the spine | Violates no-phone-home constraint | No telemetry in core; CI/network test on bare install |
| Trusting extracted content as safe to render | Malicious formula/macro/markup from source files in output | Treat all extracted source content as untrusted; the no-JS renderer already mitigates; sanitize before render |
| Evidence text not stored in Trace | Audit fails when source is deleted/changed | Store verbatim evidence span in the Trace (also fixes Pitfall 2) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| `missing[]` / `unextracted[]` hidden from reviewer | Gaps invisible → unfaithful publish | Show gaps prominently at review (Pitfall 5) |
| Manual capture feels second-class vs AI | Primary (token-constrained) user demoralized → drifts to AI | First-class manual UX; same surface quality (Pitfall 6) |
| Numbering collisions / broken nav (Rev2) | Wrong links; lost trust in the Library | Per-surface content IDs; real nav, breadcrumbs, traceable source links |
| Polished draft + one-click approve | Automation bias → rubber-stamp | Evidence-first review view; per-flag forcing functions |

## "Looks Done But Isn't" Checklist

- [ ] **Format adapter:** Often missing `unextracted[]`/coverage manifest — verify SmartArt, grouped shapes, charts, merged cells, forwarded email are either captured or *listed as skipped*.
- [ ] **AI-optional:** Often still has a top-level AI import — verify `pip install .` (no extras) in a clean venv runs capture→render end-to-end.
- [ ] **Provenance:** Often by-position — verify Trace stores a content hash + verbatim span, and that mutating a source flips dependent claims to STALE.
- [ ] **Distill faithfulness:** Often graded on fluency — verify every claim is entailed by its Trace and carries no injected emphasis; adversarial fixtures pass.
- [ ] **Review gate:** Often a clickable approve — verify merge is *blocked* while any claim is STALE/un-entailed/has open `missing[]`.
- [ ] **Backend parity:** Often AI-only tested — verify hand and OSS backends pass the same conformance + faithfulness suite.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Silent extraction loss (1) | MEDIUM | Add coverage manifest; re-extract corpus; route skips to `missing[]`; backfill fixtures |
| Traceability rot (2) | HIGH | Migrate Traces to content-addressed + verbatim span; re-validate corpus; many claims bounce to InReview |
| AI dependency creep (3) | LOW–MEDIUM if caught by CI early; HIGH if discovered post-release | Make AI imports lazy; fix extras; add import-linter + bare-install gate |
| Editorializing/hallucination (4) | HIGH | Switch default to extractive; add entailment gate; re-review all AI-distilled published claims |
| Rubber-stamp gate (5) | MEDIUM | Rebuild review view to evidence-first; add merge-block CI on provenance state; audit past approvals |
| Backend divergence (6) | MEDIUM | Extract one normalization point + conformance suite; make backends conform |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Silent extraction loss | Distill-socket interface (design manifest) → Format-adapters (implement) | Round-trip CI: every authored unit captured or in `unextracted[]`; zero silent drops |
| 2. Traceability rot | Semantic-model/provenance (Trace = content-addressed) → Renderer/build (re-validate) | Mutate-source test flips dependent claims to STALE; no positional IDs in render/promote |
| 3. AI dependency creep | AI-optional refactor (and a *standing invariant* every phase after) | Bare `pip install .` + full-pipeline CI green; import-linter contract green |
| 4. Editorializing / hallucination | Distill-socket interface (entailment contract for all backends) | Adversarial faithfulness fixtures pass on every backend; every claim entailed by its Trace |
| 5. Rubber-stamp review gate | Review-gate/renderer (evidence-first view + merge block); reinforce in fan-out | Merge blocked while any claim STALE/un-entailed/open `missing[]`; approval-latency audit |
| 6. Backend divergence | Distill-socket interface (conformance suite with the interface) | All 3 backends pass one conformance + faithfulness suite; no `if backend ==` downstream |

> **Phase-ordering implication for the roadmap:** the **distill-socket interface phase must precede
> any adapter or backend work**, because Pitfalls 1, 4, and 6 are all prevented by contracts defined
> at that boundary (coverage manifest, entailment gate, conformance suite). Building adapters first
> means retrofitting all of them. Likewise, the **AI-optional CI gate (Pitfall 3) should land with
> the langchain-extraction phase and then never be allowed to regress** — it is a permanent
> invariant, not a one-time deliverable.

## Sources

Extraction fidelity (HIGH — official library docs + corroborating guides):
- python-pptx Notes/structure docs and SmartArt/grouped-shape limitation discussions — https://python-pptx.readthedocs.io/en/latest/user/notes.html ; https://medium.com/@alice.yang_10652/extract-text-from-powerpoint-ppt-or-pptx-with-python-shapes-tables-notes-smartart-and-more-18e1381018e0
- openpyxl merged-cell / `data_only` / cached-value / dropped-image behavior — https://openpyxl.readthedocs.io/en/3.1/tutorial.html ; https://groups.google.com/g/openpyxl-users/c/g3PQIpqzBnA ; https://github.com/airbytehq/airbyte/issues/48774
- Power BI export row caps (30k/150k/16MB) and summarized-vs-underlying — https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-export-data ; https://wearecommunity.io/communities/ta_data/articles/7321
- Python `email` MIME/charset/`message/rfc822`/`is_multipart` pitfalls — https://docs.python.org/3/library/email.parser.html ; https://lobstermail.ai/blog/mime-multipart-email-parsing-in-python-and-node-js-a-practical-comparison

Provenance integrity (MEDIUM — data-lineage/provenance literature applied to this architecture):
- Data provenance vs lineage; "if you cannot trace it, you cannot trust it" — https://www.infobelpro.com/en/blog/data-provenance-vs-data-lineage ; https://www.acceldata.io/blog/data-provenance
- Claim-granularity provenance (nanopublications) — https://link.springer.com/article/10.1007/s00799-025-00431-x

Optional-AI creep (HIGH — Python packaging community):
- Optional-dependency-becomes-required mechanisms (top-level imports, poetry extras) — https://github.com/python-poetry/poetry/issues/8248 ; https://github.com/pypa/pip/issues/8916 ; https://medium.com/@hieutrantrung.it/designing-modular-python-packages-with-adapters-and-optional-dependencies-63efd8b07715

Faithful-not-suggestive (HIGH — summarization-faithfulness research):
- Extractive "inherently faithful" vs abstractive hallucination; ROUGE hides hallucination; abstractiveness ↔ faithfulness tension — https://arxiv.org/html/2406.11289v1 ; https://www.nature.com/articles/s41598-025-31075-1 ; https://arxiv.org/pdf/2202.03629

Human-in-the-loop review gate (MEDIUM-HIGH — HITL/oversight literature):
- Rubber-stamp risk, automation bias, reviewer fatigue, forcing functions — https://www.techtarget.com/searchcio/feature/Human-in-the-loop-shouldnt-rubber-stamp-decisions ; https://sloanreview.mit.edu/article/ai-explainability-how-to-avoid-rubber-stamping-recommendations/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10857587/

Project context:
- `.planning/PROJECT.md`, `.planning/brief.md`, `src/newsletters/models.py` (Rev1 skeleton)

---
*Pitfalls research for: semantic information distillation framework (faithful extraction → claim provenance → human review gate → multi-surface fan-out)*
*Researched: 2026-06-14*
