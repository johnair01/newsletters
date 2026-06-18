# Phase 12: Learning & Onboarding Surface — Research

**Researched:** 2026-06-18
**Domain:** Typed semantic-model extension (a 5th SurfaceTemplate + a faithful learning re-cut + an ordered onboarding path), self-contained static render, zero-AI, zero new dependency.
**Confidence:** HIGH (every finding is grounded in the live codebase with file:line citations; this is an internal-architecture phase, not an external-ecosystem one).

## Summary

Phase 12 adds a fifth reader-facing surface — **Learning** — and the machinery to re-cut a reviewed record for a newcomer, plus an **OnboardingPath** that sequences ≥2 records into an ordered track. The crux is **faithfulness**: a teaching surface wants to explain, but the hard rule "faithful, not suggestive" forbids inventing prose. The entire design therefore rests on a single discipline already proven in the codebase — **select, order, and link existing traced claims; never author new factual prose.** Progressive disclosure is *ordering* of existing claims; the glossary is *term → its defining traced claim*; prerequisite context is *links*. A term with no traced definition is omitted or routed to `missing[]`, never fabricated.

The good news from the live repo: the seam is already cut. `templates.py` is a registry (`register()`, `_REGISTRY`) explicitly designed for new presets without core changes [templates.py:165-184]. The `L-NNN` ref format **already exists** in the ledger (`"learning": "L-{:03d}"`) [site.py:73]. The board groups by **gate state, not surface type** [render.py:891-901], and `Site.from_surfaces` groups by `template.distance` generically [site.py:256-265] — both pick up a `learning` kind automatically. The nav (`_NAV_KIND`, `_active_for`) uses `.get(..., "Start here")` fallbacks [render.py:568,665-668], so a learning surface degrades gracefully (lands under "Start here") with zero changes — and `FanoutLink(kind="learning", ...)` is **already authored** in worksurface.py:338. Nothing assumes *exactly* four types in a way that breaks; the four-item nav *spine* is a deliberate design choice (N1), not a structural limit.

**Primary recommendation:** Add a `LEARNING` `SurfaceTemplate` (`name="learning"`, `distance=4`, `signal_color=SignalColor.GREEN`, `scope=AudienceScope.INDIVIDUAL`) and register it; build `learning_surface(distillation, *, audience, ...) -> Surface` that emits ordered `ClaimsBlock`s (Start here / Prerequisites / Going deeper) selected from existing traced claims via `claims_for`/emphasis, plus a new `GlossaryBlock` (term → defining traced claim) and a `ProseBlock`-free prerequisite-links block; add a typed `OnboardingPath` model + `render_path()` reusing the prev/next device; author one dogfood learning re-cut of an existing reviewed Report + a ≥2-step path; fill the `docs/surfaces.md` learning spec gap. Reuse `link_for_source` + `_claim_spans` + `_honesty_panel` verbatim for LEARN-02. **Zero new dependency, no external calls, no AI — confirmed.**

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| The `learning` template (typed config) | Core (`templates.py`) | — | A SurfaceTemplate is typed config; registry already supports new presets [templates.py:165] |
| Faithful learning re-cut (select/order/link) | Core (`semantic.py` or new `learning.py`) | — | Operates on `Distillation`/`Claim`/`Trace` + `claims_for`; pure data transform, no I/O, no AI |
| In-context glossary (term→traced claim) | Core (new `GlossaryBlock` + builder) | Render (`render.py`) | A new typed block; rendering follows the existing block dispatch pattern |
| Concept→source provenance (LEARN-02) | Render (`link_for_source`, `_claim_spans`, `_honesty_panel`) | — | Devices already exist; reuse, do not rebuild |
| OnboardingPath model | Core (`semantic.py` or `site.py`) | — | An ordered list of slug/Page refs; pure typed model |
| OnboardingPath render (sequenced track + prev/next) | Render (`render.py`, reuse `_prevnext`) | Site (`Page.href` resolution) | Reuse the SITE-04 prev/next device; minimal new rendering |
| Dogfood learning surface + path | `dogfood.py` | `render.py` build_site | The sample corpus authors a real re-cut of an existing reviewed record |
| Spec | `docs/surfaces.md` | — | Fill the L-NNN spec gap (CONTEXT decision; specs are source of truth) |

## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **A `learning` SurfaceTemplate** (templates.py) — `name="learning"`, display_name e.g. "Learning", high `distance` (a re-cut, most-distilled), a newcomer audience scope. Register it (so the Site Collection + `L-NNN` ledger + the 4-destination nav/board pick it up). Research the exact fields.
2. **The learning preset** — a function (e.g. `learning_surface(distillation/record, ...) -> Surface`) that re-cuts a reviewed record into a learning surface: ordered progressive-disclosure sections (Start here / Prerequisites / Going deeper), an in-context glossary block (term → traced defining claim), prerequisite-context links — ALL traced. No JS (progressive disclosure is ordered sections, not interactive toggles).
3. **Concept→source provenance (LEARN-02)** — reuse Phase 9–11 devices: each concept/glossary term/step renders a claim→source link (`link_for_source`) + verbatim trace; un-traceable → not taught / honesty panel.
4. **The onboarding path (LEARN-03)** — a new typed `OnboardingPath`/`Track`: an ORDERED sequence of records/surfaces (steps) for a newcomer/cohort, with step order + prev/next. Rendered as a sequenced track page. Research the cleanest model (a list of Page/surface refs in order + a title/audience).
5. **Renderer + dogfood** — render the learning surface + the onboarding path (reuse render.py devices; minimal new rendering, design-system tokens, no JS, deterministic, self-contained/no external calls). Author a learning surface in the dogfood corpus + one onboarding path sequencing ≥2 records. Build into content/rev1/site (byte-stable, SITE-06).
6. **Scope:** the learning preset + onboarding path + the surface/template + renderer + a dogfood example + the spec section. NOT the V3 PulseIQ learning engine (out of scope). NO AI. Read-only/no-auto-publish/all prior contracts hold.

### Claude's Discretion
- The exact `distance` value and signal color (validate against the 4 existing templates).
- The exact deterministic ordering rule for progressive disclosure (claim topics? confidence? an explicit order field?) WITHOUT inventing.
- Where the `OnboardingPath` model lives (`semantic.py` vs `site.py` vs a new module).
- Whether an un-glossed term is omitted vs routed to `missing[]`.

### Deferred Ideas (OUT OF SCOPE)
- The V3 PulseIQ learning engine (only the typed re-cut/preset is in scope).
- Any AI/LLM involvement.
- Auto-publish (the gate stays intact).
- Per-reader *learning* personalization beyond the existing `Corpus.emphasis` config hook.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LEARN-01 | Learning preset re-cuts a reviewed record for a newcomer — progressive disclosure + prerequisite context + in-context glossary | `learning_surface()` design below; reuse `claims_for`/`Corpus.emphasis` [semantic.py:321-325,238-242]; new `GlossaryBlock`; ordering rule (Q-B) |
| LEARN-02 | Every concept links back to its source record/claim (trace explanation→evidence) | Reuse `link_for_source` [render.py:70-97], `_claim_spans` [render.py:475-486], `_honesty_panel` [render.py:726-760]; un-traceable → `missing[]`/honesty panel (Q-C) |
| LEARN-03 | An onboarding path sequences multiple records into an ordered learning track | New typed `OnboardingPath` model + `render_path()` reusing `_prevnext` [render.py:696-723] (Q-D) |

## Standard Stack

This phase introduces **no external packages**. It extends the existing in-repo stack:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`enum`, `typing`, `html`, `pathlib`) | 3.11+ | Template enums, typed blocks, escaping, file write | The AI-optional core imports only stdlib + Pydantic (CLAUDE.md hard rule) |
| Pydantic | (already pinned) | `SurfaceTemplate`, `Block` union, `OnboardingPath` typed model | The entire spine is Pydantic; new models follow suit [semantic.py:34] |

**Installation:** None. Confirmed zero new dependency.

**Version verification:** N/A — no package added. The AI-optional-core import boundary is enforced by `tests/test_ai_optional.py` and `lint-imports`; any new module (`learning.py`) must import only stdlib + Pydantic + sibling core modules (`.semantic`/`.templates`/`.site`), never `.distill` [site.py:19-23].

## Package Legitimacy Audit

Not applicable — this phase installs **no external packages**. All work is internal to `src/newsletters/`.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
                       reviewed Distillation (Source→Claim+Trace→Distillation)
                                          │  (already gated, already traced)
                                          ▼
            ┌──────────────────── learning_surface(distillation, *, audience) ───────────────────┐
            │  SELECT + ORDER existing traced claims (NO new prose)                                │
            │                                                                                       │
            │   claims_for(audience)  ──►  bucket by layer  ──►  Start here / Prereqs / Going deeper│
            │        (emphasis)             (deterministic ordering rule, Q-B)                      │
            │                                                                                       │
            │   build glossary:  term ──► its DEFINING traced Claim  (no traced def ⇒ missing[])    │
            │   build prereq links: prerequisite record/claim ──► link_for_source                   │
            └──────────────────────────────────────────┬────────────────────────────────────────┘
                                                        ▼
                          Surface(template=LEARNING, blocks=[ClaimsBlock(Start here),
                                  ClaimsBlock(Prerequisites), GlossaryBlock, ClaimsBlock(Going deeper)],
                                  traces=[...], missing=[untraced terms], review=Review(...))
                                                        │
                         ┌──────────────────────────────┼──────────────────────────────┐
                         ▼                               ▼                               ▼
                 render_surface()                 publish() gate                   Site.from_surfaces
                 (reuses link_for_source,         (no auto-publish;               (collection by distance;
                  _claim_spans, _honesty_panel,    invariant 2 holds)              L-NNN ref from ledger;
                  _prevnext, masthead)                                             board groups by gate)
                         │
                         ▼
            content/rev1/site/{slug}.html  (byte-stable, self-contained, no JS, no external call)

   OnboardingPath(title, audience, steps=[slug-or-Page refs in order])
            │
            ▼
   render_path()  ──►  sequenced track page; each step links to its surface;
                       prev/next WITHIN the track (reuse _prevnext device)
```

### Recommended Project Structure
```
src/newsletters/
├── templates.py        # ADD: LEARNING preset + register() it
├── semantic.py         # ADD: GlossaryBlock (+ GlossaryTerm) to the Block union;
│                       #      OPTION: OnboardingPath here (it is a typed truth-ish model)
├── learning.py         # NEW (recommended): learning_surface() preset + glossary builder
│                       #      (keeps semantic.py lean; the faithful re-cut is its own concern)
├── render.py           # ADD: _block_html branch for GlossaryBlock; render_path()
├── dogfood.py          # ADD: a learning re-cut of an existing reviewed Report + a ≥2-step path
└── site.py             # (no change needed — L-NNN ref + grouping already generic)
docs/surfaces.md        # ADD: the learning-surface + onboarding-path spec section (fill the gap)
tests/test_learning.py  # NEW: faithfulness + LEARN-02 + LEARN-03 + byte-stable tests
```

> **Discretion call — where `OnboardingPath` lives:** Recommend **`semantic.py`** (it is a typed model over reviewed records, peer to `Distillation`/`Surface`) OR a small `learning.py` alongside the preset. Avoid `site.py` — that module's docstring restricts it to *identity* (Site/Collection/Page/Ledger) and its import boundary is load-bearing [site.py:19-27]. Putting an OnboardingPath there muddies that concern. Recommend `learning.py` for both the preset and the path, so the whole learning concern is one cohesive, import-clean module.

### Pattern 1: A new SurfaceTemplate via the registry (no core change)
**What:** Define a `SurfaceTemplate` constant and `register()` it — exactly how SHOW/REPORT/ARTICLE/NEWSLETTER are defined, plus a registry call.
**When to use:** Always for the learning template.
**Example:**
```python
# Source: templates.py:108-171 (existing pattern) + the register() seam
LEARNING = SurfaceTemplate(
    name="learning",
    display_name="Learning",
    tagline="the reviewed record, re-cut for someone new",
    cadence=Cadence.ON_DEMAND,
    personalized=True,           # honors a newcomer Corpus via emphasis (config hook only)
    signal_color=SignalColor.GREEN,   # the "new contributor" accent (design-system.md:27)
    scope=AudienceScope.INDIVIDUAL,   # addressed to one learner; cohort is the OnboardingPath
    review_policy=ReviewPolicy.light(),
    slots=["start_here", "prerequisites", "glossary", "going_deeper"],
    distance=4,                  # most distilled re-cut, beyond newsletter(3)
)
register(LEARNING)               # [templates.py:168] — picked up by ledger/board/collection
```
> The four built-ins are registered at module load via the comprehension `_REGISTRY = {t.name: t for t in (SHOW, REPORT, ARTICLE, NEWSLETTER)}` [templates.py:165]. **Recommend ADDING `LEARNING` to that tuple** rather than calling `register()` separately — it keeps `all_templates()` deterministic and matches the existing built-in style. `register()` remains for *operator* templates.

### Pattern 2: A new typed Block joins the discriminated union
**What:** Add `GlossaryBlock` (and a `GlossaryTerm` sub-model) with a `kind: Literal["glossary"]` discriminator, append it to the `Block` union, and add a `_block_html` branch.
**Example:**
```python
# Source: semantic.py:358-435 (block pattern + Block union) — same shape as ClaimsBlock
class GlossaryTerm(BaseModel):
    term: str
    definition: Claim          # the DEFINING claim — MUST be traced (its evidence IS the def)

class GlossaryBlock(BaseModel):
    kind: Literal["glossary"] = "glossary"
    heading: Optional[str] = "Glossary — every term traced to its definition"
    terms: list[GlossaryTerm] = Field(default_factory=list)
# then: add GlossaryBlock to the Annotated[Union[...], Field(discriminator="kind")] [semantic.py:421]
```
> **Why a `Claim` for the definition, not a `str`:** it forces the definition to carry `evidence: list[Trace]` and a `confidence`, so the renderer can reuse `_claim_spans`/`link_for_source`/`_claim_badge` unchanged and the faithfulness gate applies for free. A term whose definition is not a traced claim simply cannot be constructed faithfully — it goes to `missing[]`.

### Anti-Patterns to Avoid
- **Authoring new explanatory prose in the learning preset.** The whole crux. The preset must only *re-arrange* existing `Claim.text`/`Trace.span` — never synthesize a sentence. A `ProseBlock` with hand-written teaching copy is the trap; if used at all, its text must be a verbatim existing claim/narrative, not new exposition. Recommend: emit only `ClaimsBlock`/`GlossaryBlock`, no free `ProseBlock` body.
- **Inventing glossary definitions.** A term without a defining traced claim must be omitted/`missing[]`, never given a dictionary gloss.
- **Interactive JS toggles for "progressive disclosure."** The renderer is no-JS-faithful (only the theme toggle exists [render.py:342-348]). Progressive disclosure is *ordered sections in the DOM*, not `<details>`/click reveals.
- **Hand-minting `content_hash`/offsets.** Always go through `Trace.from_source` (the sole pinning constructor) [semantic.py:126-170]; the dogfood/worksurface precedents enforce this.
- **Putting OnboardingPath in `site.py`.** Violates that module's identity-only concern + import boundary.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Claim→source working link | A new URL builder | `link_for_source(trace, site=site)` [render.py:70-97] | Already handles file-path → repo blob, session → in-site anchor, neither → plain text (no dead links) |
| Showing the verbatim evidence span | A new span renderer | `_claim_spans(claim)` [render.py:475-486] | Already renders only addressed, non-empty spans, escaped |
| "What's not here / not verified" gap panel | A new honesty UI | `_honesty_panel(surface)` [render.py:726-760] | Renders `surface.missing[]` + extraction drops on every surface; the un-glossed-term gap goes straight in |
| Prev/next within an ordered sequence | A new pager | `_prevnext(site, page)` device [render.py:696-723] | Already does first-has-no-prev / last-has-no-next / single-item-neither |
| Per-type stable IDs (L-001…) | A new ID scheme | The ledger — `"learning": "L-{:03d}"` already present [site.py:73] | Append-only, immutable, byte-stable; assigned automatically by `Site.from_surfaces` |
| Surface→collection→board placement | New grouping logic | `Site.from_surfaces` (groups by `template.distance`) [site.py:256-265] + `_board` (groups by gate) [render.py:891-901] | Both are kind-generic; a `learning` kind flows through with no edit |
| Newcomer ordering of claims | A new sorter | `Distillation.claims_for(audience)` + `Corpus.emphasis` [semantic.py:321-325,238-242] | "Same facts, new emphasis" is already the re-cut primitive |
| Faithfulness check (claim entailed by span) | A new validator | `SpanContainmentFaithfulness().entails(claim)` [distill/faithfulness.py] | Deterministic, no-AI, already wired into `_claim_badge` |

**Key insight:** Phase 12 is **90% composition of existing devices**. The genuinely new code is small: the `LEARNING` template constant, a `GlossaryBlock` typed model + one render branch, the `learning_surface()` selector/orderer, the `OnboardingPath` model + `render_path()`, and dogfood content. Everything provenance/lineage/nav/board/ID-related already exists and is kind-generic.

## Runtime State Inventory

> Phase 12 is **additive code + new dogfood content**, not a rename/refactor/migration. There is no existing learning data to migrate. The one persistence touchpoint:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `content/rev1/ids.json` (the append-only ledger) will gain a new `L-001` entry for the dogfood learning surface, and possibly the onboarding path slug. | Code: just run `build_site()`; the ledger appends the new slug automatically [dogfood.py:666-668]. Append-only/immutable — existing refs untouched. Commit the regenerated `ids.json`. |
| Live service config | None — no external services. | None. |
| OS-registered state | None. | None. |
| Secrets/env vars | None. | None. |
| Build artifacts | `content/rev1/site/*.html` regenerates (new `l-…learning.html` + the path page); existing files must stay byte-identical except for intended additions (SITE-06 byte-stable test). | Code: regenerate + commit the new HTML; verify existing surfaces' bytes are unchanged. |

**Nothing found in categories Live service / OS-registered / Secrets:** None — verified by grep over `.planning` and the source tree; this phase touches only `src/newsletters/`, `docs/surfaces.md`, `content/rev1/`, and `tests/`.

## Common Pitfalls

### Pitfall 1: The learning re-cut drifts into invented prose (THE crux risk)
**What goes wrong:** A "teaching" surface naturally wants a friendly intro sentence, a simplified restatement, or a synthesized glossary definition — all of which are *new factual prose* and violate "faithful, not suggestive."
**Why it happens:** Onboarding UX intuition pushes toward explanation; the model *can* generate plausible copy.
**How to avoid:** Architecturally forbid it. The preset emits only `ClaimsBlock`/`GlossaryBlock` whose text is existing `Claim.text` and whose definitions are existing traced `Claim`s. No `ProseBlock` with hand-written body. A test asserts every rendered claim/term text equals some existing reviewed claim's text (no string in the learning surface that isn't a traced claim).
**Warning signs:** A `ProseBlock(text="In this guide we'll …")`; a glossary `definition` that is a `str` instead of a traced `Claim`; any claim text not present in the source `Distillation`.

### Pitfall 2: "Progressive disclosure" implemented as JS toggles
**What goes wrong:** `<details>`/accordion reveals break the no-JS-faithful renderer (only the theme toggle JS is allowed [render.py:342-348]) and byte-stability.
**How to avoid:** Progressive disclosure = three **ordered DOM sections** (Start here → Prerequisites → Going deeper), simplest/prerequisite first. Pure markup, no interactivity.
**Warning signs:** `<details>`, `onclick`, a second `<script>`.

### Pitfall 3: Non-deterministic layer ordering
**What goes wrong:** If "Start here vs Going deeper" depends on `Corpus.emphasis` floats with ties, or on dict iteration, the output isn't byte-stable (SITE-06 fails).
**How to avoid:** Use a **stable, total** ordering key (see Q-B). `claims_for` already uses `sorted(..., key=emphasis, reverse=True)` which is stable, but emphasis ties must break deterministically (e.g. by original claim index). Sources are `EPOCH_ZERO`; never call `datetime.now()` in the preset.
**Warning signs:** Flaky byte-stable test; different output across runs.

### Pitfall 4: Treating a term with no traced definition as a soft "TODO" gloss
**What goes wrong:** Fabricating or stubbing a definition.
**How to avoid:** Omit the term from the `GlossaryBlock` and append it to `surface.missing[]` so `_honesty_panel` shows the gap. Recommend **route to `missing[]`** (more honest than silent omission — the gap is visible).

### Pitfall 5: OnboardingPath in `site.py` breaking the import boundary
**What goes wrong:** `site.py` must never import `.distill` or anything AI [site.py:19-23]; piling unrelated models there invites accidental coupling.
**How to avoid:** Put `OnboardingPath` in `learning.py` (or `semantic.py`). Keep `site.py` identity-only.

## Code Examples

### LEARN-01 — the faithful learning re-cut (recommended function shape)
```python
# Source: composed from semantic.py:321-325 (claims_for) + the block pattern
def learning_surface(
    distillation: Distillation,
    *,
    surface_id: str,
    title: str,
    audience: Corpus | None = None,        # newcomer corpus → emphasis ordering (config hook only)
    glossary_terms: list[str] = (),        # the terms to gloss; each resolved to a DEFINING traced claim
    prerequisites: list[str] = (),         # prerequisite record/claim refs → links (traced)
    author: str,
) -> Surface:
    claims = distillation.claims_for(audience)              # same facts, newcomer emphasis
    start, prereq_layer, deeper = _bucket_by_layer(claims)  # deterministic ordering (Q-B)
    glossary = _build_glossary(glossary_terms, claims)      # term → defining traced Claim, or missing[]
    surface = Surface(
        id=surface_id, template=LEARNING, title=title,
        eyebrow="Learning · re-cut for someone new",
        audience_label=(audience.name if audience else "A new contributor"),
        byline=[author],
        blocks=[
            ClaimsBlock(heading="Start here", claims=start),
            ClaimsBlock(heading="Prerequisites", claims=prereq_layer),
            glossary.block,                                 # GlossaryBlock (traced defs only)
            ClaimsBlock(heading="Going deeper", claims=deeper),
            # prerequisite-context links: reuse FanoutBlock or a thin links block; each href via
            # link_for_source on the prerequisite's trace — NO new exposition.
        ],
        traces=list(distillation.traces),
        missing=[*distillation.missing, *glossary.untraced_terms],  # honesty panel shows the gaps
        review=Review(policy=LEARNING.review_policy, author=author),
    )
    return surface          # caller publishes through the gate — NO auto-publish
```

### Q-B — deterministic progressive-disclosure ordering (recommended rule)
```python
# RECOMMENDED: confidence-led, total + stable. Higher-confidence, broadly-traced claims are the
# foundation a newcomer starts from; lower-confidence/edge claims go deeper. Topics drive the
# prerequisite layer. NO new field required (uses existing Claim.confidence/topics) — but an
# OPTIONAL explicit Claim ordering hint can be added later without breaking this.
def _bucket_by_layer(claims: list[Claim]) -> tuple[list[Claim], list[Claim], list[Claim]]:
    # Stable key: (-confidence, original_index) — ties break by source order, fully deterministic.
    indexed = list(enumerate(claims))
    start = [c for i, c in indexed if c.confidence >= 0.9]
    prereq = [c for i, c in indexed if "onboarding" in c.topics or "vision" in c.topics]
    deeper = [c for i, c in indexed if c not in start and c not in prereq]
    return start, prereq, deeper
```
> **Discretion note:** three viable ordering signals exist — `confidence` (HIGH-confidence = foundational), `topics` (an `"onboarding"`/`"prerequisite"` topic tag), or a NEW explicit `order` field on `Claim`. Recommend **`confidence` + `topics`** (no schema change, uses existing fields) for Phase 12, with a `[ASSUMED]` flag that the planner/discuss may prefer an explicit per-claim `learning_layer` field if curators want manual control. Whatever is chosen, the key MUST be total + stable for byte-stability.

### LEARN-02 — provenance reuse (no new code)
```python
# Source: render.py — these run UNCHANGED for the learning surface's ClaimsBlock/GlossaryBlock:
#   _ev_chip(t, site)        -> linked evidence chip via link_for_source (working link or plain text)
#   _claim_spans(claim)      -> verbatim addressed span box
#   _claim_badge(claim, src) -> inline STALE / unfaithful badge
#   _honesty_panel(surface)  -> "What's not here / not verified" (un-glossed terms + missing[])
# The GlossaryBlock render branch reuses the SAME claim-rendering helpers for each term.definition.
```

### LEARN-03 — the OnboardingPath model + render (recommended)
```python
# Source: new model + reuse of _prevnext [render.py:696-723]
class OnboardingStep(BaseModel):
    slug: str                       # the canonical link key of the record/surface (Site.by_slug)
    label: str = ""                 # optional human label; defaults to the resolved Page.title

class OnboardingPath(BaseModel):
    id: str
    title: str
    audience_label: str = "A new contributor"
    steps: list[OnboardingStep] = Field(default_factory=list)   # ORDER is the track order

def render_path(path: OnboardingPath, *, site: Site, theme: str = "light") -> str:
    # Resolve each step via site.by_slug -> Page; render a numbered sequenced track (DiagramBlock-
    # style or a numbered list), each row an <a href=page.href>. A step that resolves to no Page
    # renders as plain text (faithful — never a dead link), mirroring _fanout_row. Reuse _prevnext
    # semantics across steps (first has no prev, last has no next).
```
> The OnboardingPath is **rendered as its own page** (e.g. `l-001-onboarding.html` or a dedicated `path-…html`); it is *not* a Surface (it has no claims of its own — it sequences existing surfaces). It needs no review gate (it publishes nothing new; it links to already-published records). Confirm during planning whether it should appear in the board (recommend: list it on the Library/Home as a track, not in the gate-state board, since it has no gate).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Four hardcoded surface types | One parameterized `SurfaceTemplate` + a registry | Rev1 (Phase 2) | A fifth surface is *config*, not a new class [templates.py:89-101] |
| Positional `enumerate` IDs | Append-only ledger with per-type ref formats | Phase 8 | `L-NNN` already reserved; new surface gets a stable ref free [site.py:69-74] |
| Per-surface gate UI | Gate-state board + honesty panel on every surface | Phase 9/10 | Learning surface inherits the board + honesty panel with no work [render.py:891,726] |
| In-repo only | Real codebase capture (`worksurface.py`) | Phase 11 | A learning surface can re-cut a *real* work record too; `FanoutLink(kind="learning")` already authored [worksurface.py:338] |

**Deprecated/outdated:** none relevant. The `synthesize()` agentic path remains an intentional stub [semantic.py:567-579] — the learning preset is deterministic capture, not agentic, so it does NOT touch that boundary.

## Dogfood Example Selection (Q-E)

The Rev1 corpus has three reviewed Reports + an Article + a Show + newsletters [dogfood.py:641-648]. For a **real** newcomer re-cut (claims trace to real evidence, not a stub):

**Recommended learning surface:** Re-cut **`report-datamodel`** ("Getting the data models right") [dogfood.py:298-343]. Why: it has the richest set of traced, content-addressed claims (6 decisions, each pinned to the session transcript via `_address_report` [dogfood.py:411-413]), spanning `design`/`core`/`process`/`vision` topics — ideal raw material for Start here / Prerequisites / Going deeper layering, and its claims are exactly the kind a newcomer needs ("two layers not five peers", "four surfaces are one template"). Its claims are already verbatim-traced, so the faithful re-cut has real evidence to select/order.

**Recommended glossary terms** (each MUST resolve to a defining traced claim in the corpus, else → `missing[]`): "Distillation", "Surface", "Claim/Trace", "the review gate", "report vs article". These map to existing traced decisions/claims; any term without a traced defining claim is routed to the honesty panel (proving the faithfulness discipline visibly).

**Recommended onboarding path (≥2 records, ordered):**
1. `show-ep01` (the recorded walk-through — rawest, distance 0) →
2. `report-datamodel` (the design decisions — distance 1) →
3. the new `learning` re-cut of report-datamodel (the newcomer-shaped distillation — distance 4).

This sequences a real beginner journey ("watch the build → read the decisions → read the newcomer guide") across ≥2 existing reviewed records, all already published, satisfying LEARN-03 with genuine content. The newcomer Corpus already exists for emphasis [dogfood.py:168-172] (`weights={"onboarding": 1.0, "vision": 0.5}`).

## docs/surfaces.md Spec to Add (Q-F)

The `L-NNN` id row already exists [surfaces.md:176]; the **spec section is the gap**. Add a "Learning — the reviewed record, re-cut for someone new" section covering: the faithfulness contract (select/order/link, never invent); the three progressive-disclosure layers; the in-context glossary (term → traced defining claim; un-traceable → honesty panel); the prerequisite-context links; the GREEN signal / `L-NNN` id / distance-4 placement; and the OnboardingPath (ordered track of record refs, prev/next, no own gate). Mirror the structure of the existing per-surface spec sections. **This must land in the same change** (CONTEXT decision; "specs are source of truth", CLAUDE.md).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `distance=4` is the right value (most distilled, beyond newsletter=3) | Pattern 1 | Low — only affects collection ordering; any value > 3 reads as "most distilled" |
| A2 | `SignalColor.GREEN` is the intended learning accent | Pattern 1 | Low — GREEN is design-system's "new contributor" accent [design-system.md:27] and unused as a signal_color; strong fit, but a curator may prefer another |
| A3 | `confidence` + `topics` is the best deterministic ordering signal (vs a new explicit `order`/`learning_layer` field) | Q-B | Medium — if curators need manual layer control, an explicit field is better; flagged for discuss |
| A4 | Un-glossed term → `missing[]` (vs silent omission) | Q-C/Pitfall 4 | Low — both are faithful; `missing[]` is more honest; reversible |
| A5 | OnboardingPath is NOT a Surface and needs no review gate (it publishes nothing new) | Q-D | Medium — if a curator wants the *path itself* reviewed before listing, it may need a light gate; flagged |
| A6 | `report-datamodel` is the best record to re-cut for newcomers | Q-E | Low — any reviewed Report with traced claims works; this one is richest |
| A7 | `personalized=True` on the learning template is appropriate (uses the existing emphasis hook only) | Pattern 1 | Low — the learning *engine* is V3/out of scope; only the typed `Corpus.emphasis` hook is used, consistent with PERS-01 |

## Open Questions

1. **Explicit per-claim learning order vs derived order?**
   - What we know: `confidence` + `topics` give a deterministic order with no schema change.
   - What's unclear: whether curators want manual control over which claim is "Start here".
   - Recommendation: ship derived ordering (A3) for Phase 12; add an optional `Claim.learning_layer` field only if discuss/usage demands it. Keep the key total+stable either way.

2. **Should the OnboardingPath appear in the gate-state board?**
   - What we know: the board groups by `ReviewState` [render.py:891]; a path has no review state.
   - What's unclear: where it surfaces in navigation (Home? Library? a "Start here" link?).
   - Recommendation: list it on the Library/Home as a "track", not in the gate board. Confirm in planning.

3. **One learning surface per record, or a curated multi-record learning surface?**
   - Recommendation: Phase 12 scope = one-record re-cut (LEARN-01) + a multi-record *path* (LEARN-03). A multi-record single learning surface is out of scope; the path covers cross-record sequencing.

## Environment Availability

> Phase 12 is pure in-repo Python + content generation. The only external dependency is the existing test/build toolchain.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | All core code | ✓ (project runs) | per repo | — |
| Pydantic | Typed models | ✓ (already a dep) | pinned | — |
| pytest | The new tests | ✓ (tests/ exist, 26 suites) | per repo | — |
| External network / AI runtime | — | ✗ (forbidden) | — | N/A — the whole phase is no-AI / no-external-call by design |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

## Validation Architecture

> `nyquist_validation` is `true` in `.planning/config.json` — this section is required.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (26 existing suites under `tests/`) |
| Config file | (project pyproject/pytest config; tests run via `pytest`) |
| Quick run command | `pytest tests/test_learning.py -x` |
| Full suite command | `pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LEARN-01 | Learning preset emits ordered Start here/Prerequisites/Going deeper from existing traced claims; no invented prose | unit | `pytest tests/test_learning.py::test_learning_surface_is_faithful_no_invented_prose -x` | ❌ Wave 0 |
| LEARN-01 | Glossary terms each resolve to a DEFINING traced claim; un-traceable term → missing[]/honesty panel | unit | `pytest tests/test_learning.py::test_glossary_definitions_are_traced -x` | ❌ Wave 0 |
| LEARN-01 | Progressive disclosure is no-JS ordered sections; output byte-stable | unit | `pytest tests/test_learning.py::test_learning_progressive_disclosure_no_js -x` | ❌ Wave 0 |
| LEARN-02 | Every concept/glossary term/step renders a working claim→source link (or plain text if untraceable); no dead links | unit | `pytest tests/test_learning.py::test_every_concept_traces_to_source -x` | ❌ Wave 0 |
| LEARN-03 | OnboardingPath renders an ordered track; prev/next within the track (first no-prev, last no-next) | unit | `pytest tests/test_learning.py::test_onboarding_path_ordered_with_prevnext -x` | ❌ Wave 0 |
| Cross | Template registered; learning surface gets L-001 ref; lands in a Collection; board picks it up | unit | `pytest tests/test_learning.py::test_learning_template_registered_and_lands_in_site -x` | ❌ Wave 0 |
| Cross | `build_site()` byte-stable (SITE-06): re-render produces identical bytes; existing surfaces unchanged | unit | `pytest tests/test_render.py -k byte_stable -x` (extend) | ⚠️ extend existing |
| Cross | No new external call / no AI import reachable | unit | `pytest tests/test_ai_optional.py -x` | ✅ exists (re-run after adding learning.py) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_learning.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** Full suite green + a manual visual check of the rendered learning surface + path before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_learning.py` — covers LEARN-01/02/03 + template registration + faithfulness
- [ ] Extend `tests/test_render.py` byte-stable assertions to include the new learning surface + path HTML
- [ ] (No framework install needed — pytest already present)

## Security Domain

> `security_enforcement` is not disabled; this section is included. Phase 12 is internal, read-only, no auth, no network, no user input parsed at runtime (curated dogfood content only).

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth in this phase |
| V3 Session Management | no | Static HTML, no sessions |
| V4 Access Control | no | No access control surface |
| V5 Input Validation | yes (low) | All rendered text goes through `_e()` HTML-escaping [render.py:353]; slugs restricted to `[a-z0-9-]` [site.py:48-59]; only the slug-safe locator value enters an `href` (free text never does, T-09-08) [render.py:82] |
| V6 Cryptography | no | `content_hash` (SHA-256) is integrity, not secret crypto; reuse `Trace.from_source`, never hand-roll |

### Known Threat Patterns for static-render core
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| HTML/script injection via claim/term text | Tampering | `_e()` escaping on every interpolation (existing pattern — apply to GlossaryBlock render) |
| Dead/`href="None"` links | Tampering/Info | `link_for_source` returns `None` → plain text (reuse; never emit a dead link) |
| Path traversal via slug | Tampering | `slugify` restricts to `[a-z0-9-]` (no `/`, `.`, `\`) [site.py:48-59] |
| Non-determinism leaking time/host | — | `EPOCH_ZERO` sources, no `datetime.now()` in the preset; byte-stable test enforces |

## Sources

### Primary (HIGH confidence)
- `src/newsletters/templates.py:89-184` — SurfaceTemplate shape, the 4 presets, `register()`/`_REGISTRY` (the registry seam), SignalColor enum (GREEN unused), distance/scope/cadence fields.
- `src/newsletters/semantic.py:187-211,295-325,358-435,464-559` — Claim/Trace, `Distillation.claims_for`, `Corpus.emphasis`, the typed Block union, Surface (blocks/missing/traces/review, publish gate).
- `src/newsletters/render.py:70-97,475-486,696-760,891-901` — `link_for_source`, `_claim_spans`, `_prevnext`, `_honesty_panel`, the board (groups by gate); `_NAV_KIND`/`_active_for` `.get` fallbacks (568,665-668).
- `src/newsletters/site.py:69-74,223-265` — `L-{:03d}` ref already present; `Site.from_surfaces` groups by `template.distance` (kind-generic).
- `src/newsletters/dogfood.py:157-173,298-343,488-523,641-688` — newcomer Corpus, report-datamodel (richest traced claims), show-ep01, build_surfaces/build_site (ledger append).
- `src/newsletters/worksurface.py:333-343` — `FanoutLink(kind="learning")` already authored (the learning kind is anticipated).
- `src/newsletters/distill/faithfulness.py` — `SpanContainmentFaithfulness().entails` (the no-AI faithfulness gate).
- `docs/product-spec.md:112-116` — the "A new contributor" audience ("How we debug here + the reusable record + glossary").
- `docs/surfaces.md:174-178` — the L-NNN id row (spec section is the gap to fill).
- `docs/design-system.md:27,53` — `--color-green` = the "new contributor" persona accent.
- `.planning/ROADMAP.md:325-338`, `.planning/REQUIREMENTS.md:58-62`, `.planning/phases/12-.../12-CONTEXT.md` — phase goal, LEARN-01/02/03, decisions.

### Secondary (MEDIUM confidence)
- `.planning/phases/08-…/08-*` — the L1 ID convention history confirming `L-NNN` was reserved for this phase.

### Tertiary (LOW confidence)
- None — all findings verified against the live codebase.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no external packages; the in-repo seam (registry, ledger, blocks, render devices) is read directly from source.
- Architecture: HIGH — the faithful re-cut, glossary-as-traced-claim, and OnboardingPath designs compose existing, verified primitives; the 4-type assumption is confirmed soft (verified by grep of every `kind ==`/`.get` site).
- Pitfalls: HIGH — the faithfulness crux and no-JS/byte-stable constraints are explicit hard rules with existing enforcing tests.

**Research date:** 2026-06-18
**Valid until:** ~2026-07-18 (stable internal architecture; only invalidated by refactors to templates.py/semantic.py/render.py/site.py).
