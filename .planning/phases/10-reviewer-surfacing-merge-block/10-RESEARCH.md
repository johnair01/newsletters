# Phase 10: Reviewer Surfacing & Merge-Block Gate — Research

**Researched:** 2026-06-18
**Domain:** Trust-core — reviewer-facing honesty surfacing + a deterministic CI merge-block gate
**Confidence:** HIGH (all findings grounded in the live codebase with file:line citations)

## Summary

Phase 10 makes the review gate *real*: it surfaces `Distillation.missing[]` and
`Coverage.unextracted[]` (carried as `Source.extraction`) on every surface, renders each claim
next to its verbatim `Trace.span` so unfaithfulness is visible without a click, and adds a
deterministic, AI-free `review_blockers(...)` function + a `newsletters check` CLI + a CI job that
blocks merge while any *published* surface has a STALE / un-entailed / open-`missing[]` claim.

The single most important finding: **the live dogfood corpus is all-clean and has nothing for the
gate to fire on.** Reports content-address every trace to the verbatim claim text
(`_address_report`, `dogfood.py:191-209`) so claims entail trivially and are never STALE; the
`_plan_report` claims use un-addressed traces (`dogfood.py:565-578`) which entail via the
structural fallback (`faithfulness.py:68-70`); `Distillation.missing[]` is never populated; and
`Source.extraction` is `None` everywhere (no adapter runs in dogfood). **A crafted blocker FIXTURE
is therefore mandatory** — both to prove the renderer surfaces real `missing[]`/`unextracted[]`
content (PROV-03), and to prove the gate actually BLOCKS (PROV-04). This mirrors the Phase-7 lesson:
a proof corpus authored around clean cases proves nothing.

The second structural finding: **`Surface` carries no `missing[]` field** — only `Distillation`
does (`semantic.py:300`; `Surface` has `blocks` + `traces: list[Source]`, `semantic.py:464-485`).
So the renderer/checker reach honesty data via two distinct paths: claims live in `ClaimsBlock`s
inside `surface.blocks`; `unextracted[]` is reachable as `surface.traces[i].extraction.unextracted`.
`Distillation.missing[]` does NOT currently flow onto a `Surface` at all — the planner must decide
the carrier (recommendation below: add an optional `missing: list[str]` to `Surface`, populated by
`capture`/`promote`, kept out of the corpus invariant set).

**Primary recommendation:** Build a new pure module `src/newsletters/review.py` exposing a typed
`Blocker` + `review_blockers(surface, sources) -> list[Blocker]` (PUBLISHED-only scope), wire a
`newsletters check` Typer command (exit nonzero on any blocker), add a third CI job, render an
amber "What's not here / not verified" panel + inline claim-beside-`span` view in `render.py`, and
prove every path with a crafted STALE / un-entailed / open-`missing[]` fixture. **Zero new
dependencies** — everything reuses stdlib + Pydantic + the already-core `typer[all]`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Surface honesty panel (`missing[]`+`unextracted[]`) | Renderer (`render.py`) | Semantic model (`Surface` carrier) | Rendered from typed data; no JS, deterministic (SITE-06) |
| Claim-beside-`span` review view | Renderer (`render.py`) | — | Pure render of `Trace.span`/`is_addressed` already on the model |
| STALE / un-entailed / open-missing detection | New `review.py` (pure fn) | `semantic.py` + `distill/faithfulness.py` (reused predicates) | One trust rule, one place; reuses `stale_claims` + `entails` |
| Exit-code contract + per-surface report | CLI (`cli.py`) | `review.py` | CLI is the operator entry; logic stays in the pure fn |
| Merge-block enforcement | CI (`.github/workflows/ci.yml`) | CLI | A third job runs the CLI on the corpus, AI-free |

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROV-03 | `missing[]` and `unextracted[]` surfaced to the reviewer on every surface, never hidden | Q-B — exact amber panel design + claim-beside-`span` view; `render.py:434-504` is the seam. Requires a `Surface` carrier for `missing[]` (see Q-A finding) |
| PROV-04 | CI blocks merge of any surface with a STALE / un-entailed / open-`missing[]` claim | Q-C/D/E/F — `review_blockers` + `Blocker` shape, PUBLISHED-only scope, CLI exit-code, CI job, gate-fires fixture test |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`hashlib`, `html`, `sys`) | 3.12 | Hashing (already used by `content_hash`), HTML escaping (`render._e`), exit codes | AI-free, zero-dep — the hard rule |
| Pydantic | >=2 | The typed `Blocker` model (mirror `Unextracted`/`Claim`) | Already core (`pyproject.toml:18`) |
| Typer | `typer[all]` (already core) | The `newsletters check` command | Already a CORE dep (`pyproject.toml:19`); the existing `cli.py` uses it — a new `@app.command()` is AI-free and bare-install-safe |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | (test extra) | The gate-fires negative test | `pip install .[test]` — already the CI bare-install runner (`ci.yml:34`) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typer subcommand `newsletters check` | A standalone `python -m newsletters.review` script | Typer is already core + already the CLI; a subcommand is the lowest-friction, discoverable path. No reason to diverge |
| New `src/newsletters/review.py` | Adding to `distill/faithfulness.py` | `review.py` is the right home: blocking spans STALE (a `semantic` concern) + un-entailed (a `distill` concern) + open-missing; putting it in `distill` couples a surface/review concern into the adapter tier. Keep it a top-level sibling of `render.py` |

**Installation:** None — zero new dependencies (confirmed below).

## Package Legitimacy Audit

> Not applicable — this phase installs **no external packages**. Every capability reuses the
> Python stdlib, Pydantic (already core), and `typer[all]` (already core, `pyproject.toml:19`).
> **Zero new dependency confirmed.** The CI job and checker are stdlib-only / AI-free, preserving
> the bare-install (PKG-03) and import-linter (PKG-04) invariants.

## Architecture Patterns

### System Architecture Diagram

```
                          ┌─────────────────────────────────────────────┐
   dogfood.build_surfaces │ Surfaces (blocks: ClaimsBlock[], traces:     │
   (clean corpus)  ─────► │ Source[]; review.state; optional missing[])  │
   + crafted FIXTURE      └───────────────┬─────────────────────────────┘
   (STALE/un-entailed/                    │
    open-missing)                         │
                            ┌─────────────┴──────────────┐
                            ▼                             ▼
              ┌──────────────────────────┐   ┌──────────────────────────────┐
              │ RENDER PATH (PROV-03)     │   │ CHECK PATH (PROV-04)          │
              │ render.py:_block_html     │   │ review.py:review_blockers(    │
              │  - amber honesty panel    │   │   surface, sources)           │
              │    (missing[] +           │   │  is_published? ──no──► []      │
              │    Source.extraction      │   │       │yes                     │
              │    .unextracted[])        │   │  for each claim in            │
              │  - claim row + inline     │   │   surface ClaimsBlocks:       │
              │    verbatim Trace.span    │   │   ├ stale_claims  → STALE      │
              │    + STALE/unfaithful     │   │   ├ not entails() → UNENTAILED │
              │    badge                  │   │   └ missing[]≠[]   → OPEN_MISS │
              └────────────┬─────────────┘   │  → list[Blocker]              │
                           ▼                  └──────────────┬───────────────┘
                  standalone HTML                            ▼
                  (content/rev1/site)            cli.py: newsletters check
                                                  any Blocker → exit 1 + report
                                                            ▼
                                            ci.yml job: merge-block (3rd job)
                                              runs `newsletters check` → fails build
```

Honesty data flows two ways onto a surface: claims via `ClaimsBlock` inside `surface.blocks`;
`unextracted[]` via `surface.traces[i].extraction` (an `ExtractionRecord`, `locators.py:113`).
`Distillation.missing[]` (`semantic.py:300`) has no `Surface` carrier today — see Q-A.

### Component Responsibilities

| File | Responsibility |
|------|----------------|
| `src/newsletters/review.py` *(new)* | `Blocker` model + `review_blockers()` pure fn — the one place blocking is decided |
| `src/newsletters/render.py` *(extend)* | The amber honesty panel + the claim-beside-`span` inline view; extend `_block_html` (`render.py:434`) + `render_surface` (`render.py:666`) |
| `src/newsletters/cli.py` *(extend)* | A `check` Typer command — exit nonzero + per-surface report (`cli.py:9` app, mirror `build` at `cli.py:26`) |
| `src/newsletters/semantic.py` *(extend, minimal)* | Optional `Surface.missing: list[str]` carrier (the recommended path for PROV-03 `missing[]` on a surface) |
| `.github/workflows/ci.yml` *(extend)* | A third job `merge-block` running `newsletters check`, AI-free |
| `tests/test_review.py` + fixtures *(new)* | The gate-fires negative test (STALE / un-entailed / open-missing) |

### Recommended Project Structure
```
src/newsletters/
├── review.py            # NEW: Blocker + review_blockers() — pure, AI-free
├── render.py            # EXTEND: honesty panel + claim-beside-span view
├── cli.py               # EXTEND: `check` command
└── semantic.py          # EXTEND: optional Surface.missing carrier
tests/
├── test_review.py       # NEW: gate-FIRES negative tests
└── fixtures/            # NEW: crafted blocker surfaces (or build inline)
.github/workflows/ci.yml # EXTEND: merge-block job
```

### Pattern 1: The pure blocking function (mirror `route_unfaithful_to_missing`)
**What:** A pure function over a `Surface` + a `{source_id: Source}` lookup that returns a typed
`list[Blocker]`. No mutation, no I/O, no AI — exactly the shape of `stale_claims`
(`semantic.py:310`) and `route_unfaithful_to_missing` (`faithfulness.py:77`).
**When to use:** Always — the CLI and CI both call it; tests call it directly.
**Example:**
```python
# Source: pattern composed from semantic.py:310-319 + faithfulness.py:62-74 (live)
from enum import StrEnum
from pydantic import BaseModel
from .semantic import Surface, Source, Claim, ClaimsBlock
from .distill.faithfulness import SpanContainmentFaithfulness

class BlockerKind(StrEnum):
    STALE = "stale"
    UNENTAILED = "unentailed"
    OPEN_MISSING = "open_missing"

class Blocker(BaseModel):
    surface_id: str
    kind: BlockerKind
    detail: str            # the offending claim text (truncated) or the missing[] entry
    locator: str = ""      # source_id / trace locator display when applicable

def review_blockers(surface: Surface, sources: dict[str, Source]) -> list[Blocker]:
    # PUBLISHED-only scope — Draft/In-Review may legitimately have gaps (Q-D)
    if not surface.is_published:                       # semantic.py:501
        return []
    check = SpanContainmentFaithfulness()
    out: list[Blocker] = []
    claims = [c for b in surface.blocks if isinstance(b, ClaimsBlock) for c in b.claims]
    for c in claims:
        if c.is_stale(sources):                        # semantic.py:199
            out.append(Blocker(surface_id=surface.id, kind=BlockerKind.STALE,
                               detail=c.text[:80]))
        elif not check.entails(c):                     # faithfulness.py:62
            out.append(Blocker(surface_id=surface.id, kind=BlockerKind.UNENTAILED,
                               detail=c.text[:80]))
    for m in getattr(surface, "missing", []):          # the new Surface.missing carrier
        out.append(Blocker(surface_id=surface.id, kind=BlockerKind.OPEN_MISSING, detail=m))
    return out
```
Note the STALE-vs-unentailed ordering: STALE is checked first and `elif`-guards un-entailed, so a
drifted claim reports the more specific STALE kind (a stale addressed trace would also fail
`entails` once the span no longer contains the claim — STALE is the truer diagnosis).

### Anti-Patterns to Avoid
- **Re-deriving STALE or faithfulness here.** Reuse `Claim.is_stale` (`semantic.py:199`) and
  `SpanContainmentFaithfulness.entails` (`faithfulness.py:62`) — "one trust rule, one place".
- **Mutating the surface / routing in the checker.** `review_blockers` is a *read-only* diagnosis;
  `route_unfaithful_to_missing` (`faithfulness.py:77`) is the relocation tool and lives at the
  distill boundary, not the review gate.
- **Hand-editing HTML for the panel.** SITE-06 holds: surface honesty is rendered from data via
  `_block_html`/`render_surface`, proved by the byte-stable regen test.
- **Blocking Draft/In-Review surfaces.** The gate protects the *Published* state (Q-D).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| STALE detection | A new hash-diff | `Claim.is_stale(sources)` / `Distillation.stale_claims` | Already computed from live source hashes (`semantic.py:199, 310`) |
| Un-entailed detection | A new span check | `SpanContainmentFaithfulness().entails(claim)` | The Phase-3 deterministic gate (`faithfulness.py:62`); Option-A handles un-addressed traces without false positives |
| HTML escaping in the panel | `str.replace` | `render._e` (`render.py:332`) | Already the renderer's escape helper; consistent + safe |
| CLI scaffolding / exit codes | `argparse` + `sys.exit` by hand | A Typer `@app.command()` + `raise typer.Exit(1)` | Typer is core; the existing `cli.py` is the pattern (`cli.py:26`) |

**Key insight:** Every predicate the gate needs already exists and is tested
(`tests/test_faithfulness_gate.py`, `tests/test_provenance_migration.py`). Phase 10 is *composition
+ surfacing + enforcement*, not new trust logic.

## Per-Question Findings

### Q-A. What real content is there to surface? (the corpus is all-clean — fixture required)

**Finding: there is essentially NOTHING to surface in the live dogfood corpus, and NO surface is
STALE or un-entailed. A crafted blocker FIXTURE is mandatory.**

- **`Distillation.missing[]` is never populated.** No dogfood surface sets `missing`. `grep` for
  `missing` across `capture.py`/`promote.py`/`site.py`/`dogfood.py` yields nothing. Moreover
  `Surface` has **no `missing` field at all** — only `Distillation` does (`semantic.py:300`;
  `Surface` fields are `semantic.py:474-485`). So even if a `Distillation` carried `missing[]`, it
  would not reach the rendered `Surface` today. *(This is the central PROV-03 plumbing gap.)*
- **`Source.extraction` / `unextracted[]` is `None` everywhere.** No adapter runs in dogfood;
  every dogfood `Source` is constructed without `extraction` (`dogfood.py:228, 289, 359, 455, 491`),
  so `Source.extraction` defaults to `None` (`semantic.py:65`). There is no `unextracted[]` content
  to surface from the shipped corpus.
- **No claim is STALE.** Reports content-address each trace to the verbatim claim text via
  `_address_report` → `address_corpus_traces` (`dogfood.py:191-209, 116-150`), and the source
  transcripts record those decisions verbatim (`_record_transcript`, `dogfood.py:180-188`). Because
  the corpus is addressed at capture and the transcripts are never re-edited, `Claim.is_stale`
  (`semantic.py:199`) is `False` for all of them — confirmed by the comment at `dogfood.py:405-410`
  ("the corpus addresses cleanly and is never stale at capture time").
- **No claim is un-entailed.** The Report claims have `span == claim.text` (addressed), so
  `entails` is `True` by containment (`faithfulness.py:71-72`). The `_plan_report` claims use bare
  `Trace(source_id=..., locator=...)` with **no span** (`dogfood.py:565-578`) → un-addressed →
  entail via the Option-A(a) structural fallback (`faithfulness.py:68-70`). All faithful.

**Recommendation (mandatory):** Author a crafted blocker fixture surface (a published `Surface`
with a `ClaimsBlock`) that exercises each blocking path, so PROV-03's panel has real content to
render and PROV-04's gate is proven to fire. Build all three negatives (see Q-F). Do **not** add a
blocker to the shipped dogfood corpus — that would (correctly) fail the new CI gate; keep the
fixture in `tests/`.

### Q-B. Renderer surfacing (PROV-03)

**How claims + evidence render today:** `_block_html` handles `ClaimsBlock` at
`render.py:439-452`. Each claim becomes an `<li class="claim">` (or `claim untraced` when
`not c.is_traced`, `render.py:446` / CSS `.claim.untraced{border-left-color:var(--color-amber)}` at
`render.py:189`). Evidence chips come from `_ev_chip` (`render.py:395-406`) — a mono
`source_id:locator.display` chip, linked when `link_for_source` resolves. The **only** missing
surfacing today is `render.py:444`: an untraced claim shows a single inline amber chip
`unsubstantiated → missing[]`. It does **not** show `Trace.span` and does **not** surface
`Distillation.missing[]` or `unextracted[]` per surface.

**Recommended design (two parts, both no-JS, token-driven, deterministic):**

1. **The "What's not here / not verified" honesty panel** — a new block rendered once per surface
   (inside `render_surface`, after `blocks`, `render.py:703/717`). It lists:
   - `surface.missing[]` (the new carrier) — each an unsubstantiated/un-entailed item.
   - every `surface.traces[i].extraction.unextracted[]` entry (`ExtractionRecord`,
     `locators.py:113-121`) — each `Unextracted`'s `locator.display` + `reason`.
   Style it like the existing `.rationale` inset (`render.py:201-202`) but amber: a `3px` left
   border in `--color-amber` (`#c8860a` light / `#d99a2a` dark, design-system §1/§2), a mono
   uppercase header ("What's not here / not verified"). **Never collapsed for blocking items**
   (CONTEXT decision 1). When both lists are empty, render a small "Fully traced — nothing
   outstanding" confirmation (positive, non-blocking) so the panel's presence is itself the proof.
   Reuse `_e` for all interpolation.
2. **Claim-beside-verbatim-trace view** — extend the `ClaimsBlock` branch (`render.py:441-450`):
   under each claim's text, render each `Trace`'s `span` inline (verbatim, `_e`-escaped) beside its
   chip, so an unfaithful claim (text not contained in its span) is visible without a click
   (CONTEXT decision 2; ROADMAP SC3). Flag STALE/unfaithful inline with a small badge:
   - STALE badge when `claim.is_stale(sources)` — but note `_block_html` has no `sources` today;
     the renderer must thread the surface's `{s.id: s for s in surface.traces}` lookup down into
     `_block_html` (a new optional param, mirroring how `site` is threaded at `render.py:434`).
   - unfaithful badge when `not SpanContainmentFaithfulness().entails(claim)`.
   Use `--color-amber` for the badge (design-system §6: amber = caution/In-Review; the project's
   single status-warning token). Only addressed traces (`trace.is_addressed`, `semantic.py:172`)
   carry a meaningful span; for un-addressed Rev1 traces (empty span) show the chip alone (no empty
   span box) — faithful, not suggestive.

**Token references (design-system §1/§2/§6):** `--color-amber` `#c8860a`/`#d99a2a` (status caution,
`design-system.md:26,52,134`); `--radius:0`; the `3px` left-accent device; mono eyebrow at 10px /
0.20em. All already in `_CSS` (`render.py:101-319`); the panel adds one `.honesty` rule mirroring
`.rationale`.

### Q-C. The merge-block checker (PROV-04) — `review_blockers` + `Blocker`

See Pattern 1 above for the full design. Summary:

- **Shape:** `review_blockers(surface: Surface, sources: dict[str, Source]) -> list[Blocker]`,
  pure, AI-free. A typed `Blocker(surface_id, kind: BlockerKind, detail, locator)` where
  `BlockerKind ∈ {stale, unentailed, open_missing}` — mirrors the `Unextracted`/`Claim` Pydantic
  style (`coverage.py:30`).
- **Reuses:** `surface.is_published` (`semantic.py:501`), `Claim.is_stale` (`semantic.py:199`),
  `SpanContainmentFaithfulness.entails` (`faithfulness.py:62`). No new trust logic.
- **WHERE it lives:** a **new top-level module `src/newsletters/review.py`** — a sibling of
  `render.py`. Rationale: blocking spans a `semantic` concern (STALE) + a `distill` concern
  (entailment) + a surface/review concern (published scope, open-missing); it belongs at the
  review/surface tier, NOT inside `distill/` (which is the adapter tier and must stay
  modality-agnostic). It imports `..semantic` + `.distill.faithfulness` (both AI-free), keeping the
  import graph acyclic and the bare-install green.
- **The sources lookup:** the checker needs live sources to judge STALE. A `Surface` carries
  `traces: list[Source]` (`semantic.py:479`), so the natural default is
  `{s.id: s for s in surface.traces}` — exactly how `Distillation.stale_claims` self-builds its
  lookup when `sources is None` (`semantic.py:318`). Provide an optional `sources` override for the
  corpus-wide CLI run. **Caveat:** the dogfood newsletter/show carry only a stub `Source(id=...)`
  with an empty transcript (`dogfood.py:455, 491`) — a stale check against a stub would mis-hash;
  but those surfaces also have no `ClaimsBlock`, so there are no claims to judge. The checker is
  safe (no claims → no blockers), but the planner should note: STALE judgement is only meaningful
  where the surface carries the real content-addressed sources its claims point at.

### Q-D. Scope of "blocking" — PUBLISHED-only (recommended, justified)

**Recommendation: YES — block only PUBLISHED surfaces; Draft/In-Review are exempt.**

Justification, grounded in the gate semantics:

- The no-auto-publish invariant (`semantic.py:279-287`) makes *publication* the trust boundary.
  Drafts legitimately have gaps — indeed `open_pull_request` (`semantic.py:511-523`) refuses
  untraced claims into review but does **not** require zero `missing[]`; gaps are expected
  mid-review. Blocking In-Review would punish exactly the honest in-progress state the gate is meant
  to allow.
- A STALE/un-entailed/open-missing item on a *published* surface is a trust violation: it was
  approved and is outward-facing while carrying an unverified claim. That is the precise thing
  PROV-04 exists to stop. The CONTEXT decision 3 wording — "a STALE published surface is always a
  block" — is correct and matches `surface.is_published` (`semantic.py:501`) as the gate.
- **Un-entailed claims and `route_unfaithful_to_missing`:** the router (`faithfulness.py:77`) MOVES
  an unfaithful claim's text into `missing[]` *at distill time* (the distill boundary). By the time
  a surface is PUBLISHED, an unfaithful claim should already have been routed → it shows up as an
  open-`missing[]` blocker, not as a live un-entailed claim. But the checker must still test
  `entails` directly: a surface authored by hand (the manual backend) or hand-mutated could carry
  an addressed-but-non-containing claim that never passed through the router. So **both** kinds are
  checked (un-entailed AND open-missing) — they catch the same trust failure at two different
  lifecycle points. They are not redundant; un-entailed catches what the router missed/bypassed.

### Q-E. The CLI + CI job

**CLI:** add a `check` command to the existing Typer app (`cli.py:9`, mirror `build` at
`cli.py:26-37`):
```python
# Source: pattern from cli.py:26-37 (live)
@app.command()
def check(
    out: str = typer.Option("content/rev1/site", help="(unused for now) site dir"),
) -> None:
    """Block-check every PUBLISHED surface; exit nonzero on any STALE/un-entailed/open-missing claim."""
    from .dogfood import build_surfaces
    from .review import review_blockers
    surfaces = build_surfaces()
    sources = {s.id: s for surf in surfaces for s in surf.traces}
    blockers = [b for surf in surfaces for b in review_blockers(surf, sources)]
    for b in blockers:
        typer.echo(f"  BLOCK [{b.kind}] {b.surface_id}: {b.detail}")
    if blockers:
        typer.echo(f"\n{len(blockers)} blocker(s) — merge blocked.")
        raise typer.Exit(1)               # nonzero exit — the CI contract
    typer.echo("All published surfaces clean — no blockers.")
```
**Exit-code contract:** `0` = clean (the clean dogfood corpus passes — important, so the gate is
green on `main`); `1` = ≥1 blocker, with a clear per-surface, per-kind report to stdout. Use
`raise typer.Exit(1)` (Typer's idiom) not `sys.exit`.

**CI job:** add a third job `merge-block` to `.github/workflows/ci.yml` (alongside `bare-install`
and `import-linter`, `ci.yml:18-93`). Compose it like `bare-install` (`ci.yml:19-73`):
```yaml
  merge-block:
    name: merge-block gate (PROV-04)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install with NO AI extras (test runner only)
        run: |
          python -m pip install --upgrade pip
          pip install ".[test]"
      - name: Run the merge-block checker on the corpus (AI-free)
        run: newsletters check
```
- **Composes cleanly** with the existing two jobs: independent, all on `[push, pull_request]`
  (`ci.yml:16`), all using the bare `.[test]` install so the AI-optional contract (PKG-03) stays
  the source of truth — `newsletters check` is stdlib + Pydantic + Typer only, no AI import, so the
  bare interpreter runs it. Keep the existing "assert no AI importable" step style if the planner
  wants belt-and-suspenders, but the third job's value is the *exit code*, so the minimal form
  above is sufficient. (Optionally fold the check into the existing `bare-install` job as one more
  step — but a separate job gives a clear, independently-red signal on a blocker.)

### Q-F. The test that proves the gate FIRES (negative test + crafted fixture)

**This is the load-bearing test — it must prove the gate BLOCKS, not just that the clean corpus
passes.** Mirror the Phase-3 fixture patterns in `tests/test_faithfulness_gate.py:46-51` and the
STALE-drift pattern in `tests/test_provenance_migration.py`.

Three crafted blocker surfaces (build each inline in `tests/test_review.py`, published via
`surface.publish(reviewer=...)`):

1. **STALE fixture:** mint an addressed trace via `Trace.from_source(src, 0, len(transcript))`
   (`semantic.py:126`), put it on a published claim, then **mutate `src.transcript`** so the live
   hash drifts → `claim.is_stale({src.id: src})` is `True` → a `BlockerKind.STALE`. (Pattern: the
   drift test that re-edits a source after addressing.)
2. **Un-entailed fixture:** an addressed trace whose `span` does NOT contain the claim text —
   `Trace.from_source(Source(id="s1", transcript="totally different text"), 0, n)` with a claim
   whose text isn't in that span → `entails` is `False` (`faithfulness.py:73`, mirrors
   `test_entails_false_when_addressed_span_does_not_contain_claim`,
   `test_faithfulness_gate.py:68`) → `BlockerKind.UNENTAILED`.
3. **Open-missing fixture:** a published surface with a non-empty `missing[]` (the new
   `Surface.missing` carrier) → `BlockerKind.OPEN_MISSING`.

Assertions:
- `review_blockers(fixture, sources)` returns exactly the expected `Blocker(kind=...)` for each.
- The clean dogfood corpus returns `[]` (happy path, but secondary).
- **End-to-end exit code:** invoke the CLI on a corpus containing a blocker fixture and assert it
  exits nonzero (use Typer's `CliRunner`, or a subprocess mirroring
  `test_faithfulness_module_imports_no_ai` at `test_faithfulness_gate.py:140-143`). This proves the
  CI contract, not just the function.
- **No-AI guard:** a subprocess `import newsletters.review` asserting no AI module entered
  `sys.modules` (copy `test_faithfulness_gate.py:134-143` verbatim, swapping the module).

**The trap to avoid (Phase-7 lesson, in CONTEXT):** do not test only that the clean corpus passes —
that proves nothing about the gate. The negative fixtures above are the actual proof PROV-04 holds.

## Runtime State Inventory

Not a rename/refactor/migration phase — omitted.

## Common Pitfalls

### Pitfall 1: Surfacing `missing[]` that never reaches the Surface
**What goes wrong:** PROV-03 says surface `missing[]` "on every surface", but `Surface` has no
`missing` field (`semantic.py:464-485`) — only `Distillation` does (`semantic.py:300`). Rendering
"from the Distillation" is impossible because `Surface` holds no `Distillation`.
**Why it happens:** the Rev1 surface layer deliberately omits the Distillation (invariant 3 —
private corpus never serialized; `semantic.py:464-470`).
**How to avoid:** add an optional `Surface.missing: list[str] = Field(default_factory=list)` and
populate it in `capture`/`promote` from the Distillation's `missing[]` (a one-line copy at the
draft-build seam). It carries no corpus data, so it is invariant-3-safe. The checker + renderer
read `surface.missing`.
**Warning signs:** the panel renders empty on every surface even after wiring — because nothing
populates the carrier.

### Pitfall 2: STALE check against a stub Source
**What goes wrong:** the newsletter/show dogfood surfaces carry `Source(id=...)` with an empty
transcript (`dogfood.py:455, 491`); hashing a stub differs from the real source.
**Why it happens:** those surfaces re-reference a source by id only for lineage, not evidence.
**How to avoid:** the checker is safe because those surfaces have no `ClaimsBlock` (no claims to
judge). But document that STALE is only meaningful where the surface carries the actual
content-addressed sources its claims cite. Don't add claims to a stub-source surface.

### Pitfall 3: Threading `sources` into `_block_html` for the STALE badge
**What goes wrong:** `_block_html` (`render.py:434`) has no access to the source lookup, so it
can't compute `claim.is_stale` for the inline badge.
**How to avoid:** thread an optional `sources` lookup param down through `render_surface` →
`_block_html` (mirroring how `site` is already threaded, `render.py:434, 703`). Build it from
`{s.id: s for s in surface.traces}`.

## Code Examples

(See Pattern 1 for `Blocker`/`review_blockers`, Q-E for the CLI command + CI job, Q-F for the
fixture construction. All grounded in live `semantic.py`/`faithfulness.py`/`cli.py`/`ci.yml`.)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single inline "unsubstantiated → missing[]" chip per untraced claim | Per-surface honesty panel (missing[] + unextracted[]) + inline claim-beside-`span` view | Phase 10 | Reviewer sees every gap + every verbatim span without a click |
| STALE/faithfulness checked only at distill time | Re-checked at the publish/merge boundary in CI | Phase 10 | An unsafe surface cannot merge |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The cleanest carrier for `missing[]` on a `Surface` is a new optional `Surface.missing` field populated at the capture/promote seam | Q-A, Pitfall 1 | If the planner prefers carrying a `Distillation` reference or a coverage object on the Surface instead, the renderer/checker read path changes (but the blocking logic is identical). LOW risk — both reach the same data |
| A2 | A separate CI job (vs. a step in `bare-install`) is preferred for an independently-red signal | Q-E | Cosmetic; folding into `bare-install` also satisfies PROV-04. LOW risk |

**Note:** A1/A2 are design *recommendations*, not external facts. Every technical claim about the
live code (corpus is clean, `Surface` has no `missing`, predicates exist, typer is core) is VERIFIED
against the repo with file:line citations above.

## Open Questions

1. **Carrier for `missing[]` on a Surface (A1).**
   - What we know: `Surface` has no `missing` field; `Distillation.missing[]` is the source of truth
     but never reaches a Surface today.
   - What's unclear: whether to add `Surface.missing` or carry it differently.
   - Recommendation: add optional `Surface.missing: list[str]`, populate at capture/promote. Cheap,
     invariant-3-safe.

2. **Does the gate also run on the BUILT site, or only the in-memory corpus?**
   - What we know: `newsletters check` can call `build_surfaces()` (in-memory) — simplest, AI-free.
   - Recommendation: run on the in-memory corpus (`build_surfaces()`); it is the canonical data the
     site is rendered from (SITE-06 byte-stable). No need to parse HTML back.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.12 (CI pin, `ci.yml:28`) | — |
| Pydantic | Blocker model | ✓ | >=2 (`pyproject.toml:18`) | — |
| Typer | `newsletters check` | ✓ | `typer[all]` core (`pyproject.toml:19`) | — |
| pytest | gate-fires test | ✓ | `.[test]` extra (`pyproject.toml:47`) | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none. Zero new dependency confirmed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (`pyproject.toml:65-67`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`pythonpath=["src"]`, `testpaths=["tests"]`) |
| Quick run command | `python -m pytest tests/test_review.py -x -q` |
| Full suite command | `python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROV-03 | Honesty panel renders missing[]+unextracted[] | unit | `pytest tests/test_render.py::test_honesty_panel_lists_missing_and_unextracted -x` | ❌ Wave 0 |
| PROV-03 | Claim renders beside its verbatim span + STALE/unfaithful badge | unit | `pytest tests/test_render.py::test_claim_renders_inline_span_and_flags -x` | ❌ Wave 0 |
| PROV-04 | `review_blockers` returns STALE on a drifted published claim | unit | `pytest tests/test_review.py::test_blocks_stale_published_claim -x` | ❌ Wave 0 |
| PROV-04 | `review_blockers` returns UNENTAILED on a non-containing addressed claim | unit | `pytest tests/test_review.py::test_blocks_unentailed_published_claim -x` | ❌ Wave 0 |
| PROV-04 | `review_blockers` returns OPEN_MISSING on a non-empty missing[] | unit | `pytest tests/test_review.py::test_blocks_open_missing_published_surface -x` | ❌ Wave 0 |
| PROV-04 | Draft/In-Review exempt | unit | `pytest tests/test_review.py::test_draft_surface_is_exempt -x` | ❌ Wave 0 |
| PROV-04 | CLI exits nonzero on a blocker | integration | `pytest tests/test_review.py::test_cli_check_exits_nonzero_on_blocker -x` | ❌ Wave 0 |
| PROV-04 | clean corpus passes (exit 0) | integration | `pytest tests/test_review.py::test_cli_check_clean_corpus_passes -x` | ❌ Wave 0 |
| (invariant) | `review.py` imports no AI | unit (subprocess) | `pytest tests/test_review.py::test_review_module_imports_no_ai -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_review.py tests/test_render.py -x -q`
- **Per wave merge:** `python -m pytest -q`
- **Phase gate:** Full suite green + `newsletters check` exits 0 on the clean corpus, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_review.py` — covers PROV-04 (the gate-fires negatives + exit code + no-AI)
- [ ] `tests/test_render.py` additions — covers PROV-03 (panel + inline span)
- [ ] Crafted blocker fixtures (inline in `test_review.py` or `tests/fixtures/`) — STALE / un-entailed / open-missing
- [ ] Framework install: already present (`.[test]`)

## Security Domain

> `security_enforcement` not explicitly disabled — included.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface in this phase |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | All rendered honesty text (`missing[]`, `Unextracted.reason`, `Trace.span`) MUST pass through `render._e` (`render.py:332`) before HTML interpolation — these strings can carry user/source content. The existing renderer already `_e`-escapes every interpolation; the new panel/inline-span must too |
| V6 Cryptography | no | STALE reuses the existing SHA-256 content hash (`semantic.py:71-83`); no new crypto |

### Known Threat Patterns for {Python static renderer + CLI gate}
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| HTML/script injection via an unescaped `Trace.span` or `Unextracted.reason` in the panel | Tampering | `render._e` on every interpolation (mirror `render.py:402-406`); never put raw span text in an `href` (the SITE-05 rule already forbids free text in hrefs, `render.py:80`) |
| A blocker silently swallowed → unsafe surface merges | Repudiation / Tampering | The CLI exits nonzero + prints a per-surface report; the CI job fails the build. The negative gate-fires test proves this can't regress |
| AI import leaking into the gate (breaks PKG-03) | — | `review.py` imports only `..semantic` + `.distill.faithfulness` (both AI-free); a subprocess no-AI test guards it; the job runs on the bare `.[test]` install |

## Sources

### Primary (HIGH confidence) — live codebase
- `src/newsletters/semantic.py` — `Surface` (no `missing` field), `Distillation.missing/stale_claims`, `Claim.is_stale`, `Trace.from_source/is_addressed/is_stale_against`, `Source.extraction/content_hash`, the Review gate (lines cited inline)
- `src/newsletters/distill/faithfulness.py` — `SpanContainmentFaithfulness.entails`, `route_unfaithful_to_missing`, Option-A
- `src/newsletters/distill/coverage.py` + `src/newsletters/locators.py` — `Unextracted`, `ExtractionRecord` carrier
- `src/newsletters/distill/ports.py` — `DistillationResult`, `_enforce` (one-place enforcement pattern)
- `src/newsletters/render.py` — `_block_html` (ClaimsBlock at 439-452, missing chip 444), `_ev_chip`, `render_surface`, `_e`, tokens
- `src/newsletters/dogfood.py` — the corpus is clean (`_address_report`, `_record_transcript`, stub sources, no `missing[]`)
- `src/newsletters/cli.py` — Typer app + `build` command pattern
- `.github/workflows/ci.yml` — the two existing jobs to extend
- `pyproject.toml` — `typer[all]`/pydantic are CORE; `[test]` extra
- `docs/design-system.md` §1/§2/§6 — `--color-amber`, status colors, the 3px accent device
- `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` — Phase 10 goal + 3 success criteria, PROV-03/04
- `tests/test_faithfulness_gate.py`, `tests/test_render.py` — fixture + no-AI-import patterns to mirror

### Secondary (MEDIUM) — none required
### Tertiary (LOW) — none

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new deps; everything reused is in the live tree and tested
- Architecture: HIGH — every predicate (`is_stale`, `entails`, `is_published`) verified at file:line
- Pitfalls: HIGH — the `Surface`-has-no-`missing` gap and the all-clean corpus are verified facts, not guesses
- The fixture requirement: HIGH — confirmed by reading `dogfood.py` end to end

**Research date:** 2026-06-18
**Valid until:** 2026-07-18 (stable internal codebase; re-verify if `semantic.py`/`render.py`/`dogfood.py` change)
