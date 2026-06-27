# Phase 8: Site Content Model & Stable IDs - Research

**Researched:** 2026-06-18
**Domain:** Static-site content modelling + deterministic, position-independent identifiers (pure Python / Pydantic, AI-free)
**Confidence:** HIGH (this is a codebase + spec grounding task; all findings cite live files and lines)

---

<user_constraints>
## User Constraints (from 08-CONTEXT.md)

### Locked Decisions
1. **`Site / Collection / Page` content model** (new, typed, AI-free — likely `src/newsletters/site.py`).
   - `Site` = the whole library; holds ordered `Collection`s.
   - `Collection` = a grouping by surface TYPE/cadence (Reports, Articles, Newsletters, Shows, Learning) — the natural board columns.
   - `Page` = one published surface within a collection; carries the stable IDs + metadata (title, slug, ref, issue/date, gate state, signal color) and points at its `Surface`/`Distillation`.
   - Order is data (an explicit list), NEVER the source of identity.
2. **Stable IDs are content-derived or ledger-assigned — NEVER position-derived (the invariant).** Each `Page` carries `slug` (content-derived from title; the canonical link target), `ref` (per-type sequential id `R-001`/`EP01`/`A-003` assigned ONCE from a persisted append-only ledger keyed by slug), and `issue`/`date` for cadenced surfaces.
3. **The ID ledger** = a committed, human-readable file (e.g. `content/ids.json` or `content/rev1/ids.json`) mapping `slug -> {ref, issue, date, type}`. Read at build; a surface missing from the ledger is assigned the next ref for its type and the ledger is updated (append-only — existing entries immutable). Deterministic: same content → same ledger.
4. **Cross-links resolve by slug/ref, not position.** Renderer (`render.py`) consumes the `Site` model instead of an enumerated list.
5. **Backward-compat + scope.** Keep existing `Surface.id`s working (slug can default from/align with them). This phase = CONTENT MODEL + stable IDs + ledger + wiring the existing renderer; full Rev2 site IA / nav / real Home is **Phase 9**. Board STATUS columns by gate state are Phase 9/10 — here just the `Collection` grouping + stable IDs. No new dependency (slugify is ~10 lines of stdlib; do NOT add `python-slugify`).

### Claude's Discretion
- Exact `site.py` module shape and Pydantic field names (validate against the live renderer).
- Slugify implementation details (within the stdlib-only, deterministic constraint).
- Ledger file path (`content/ids.json` vs `content/rev1/ids.json`) and JSON key ordering.
- Minimal renderer-wiring approach.

### Deferred Ideas (OUT OF SCOPE — Phase 9 / 10)
- Real marketing Home separate from Library (SITE-02..06).
- Four-destination nav with breadcrumbs; working source links into the repo.
- Library status-board with columns BY GATE STATE (the kanban). Here: only the `Collection` *grouping by type* + stable IDs.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SITE-01 | A `Site/Collection/Page` content model carries stable per-surface IDs (`EP01`, `R-001`, slug, issue/date) independent of list position | Q-E gives the exact Pydantic field list; Q-D gives the ledger shape + append-only assignment algorithm that makes refs position-independent; Q-C gives the deterministic stdlib slugify; Q-A documents the rot points this replaces; Q-D + Q-A give the stability test design that proves criterion 2. |

**Success criteria (ROADMAP, verbatim):**
1. The `Site/Collection/Page` model carries stable per-surface IDs generated from content, independent of list position.
2. Inserting or reordering surfaces does not change any existing surface's ID or break its cross-links.
</phase_requirements>

---

## Summary

Phase 8 is a **pure-Python content-model + identifier** phase grounded entirely in the live codebase. There is **no third-party dependency** — every tool needed (`re`, `unicodedata`, `json`, `pathlib`) is stdlib, and Pydantic is already a core dependency. There is **no Package Legitimacy Audit, no Environment Availability audit, and no Security Domain** beyond the existing import-linter boundary (all confirmed below). [VERIFIED: pyproject.toml + .importlinter]

The single bug this phase fixes is concrete and cited: `render_library()` numbers surfaces with `enumerate(surfaces, 1)` at `render.py:373`, and the visible index `{i:02d}` (`render.py:376`) is **purely positional**. Reorder or insert one surface in `build_surfaces()` (`dogfood.py:640-647`) and every downstream display number renumbers — the Library says "07" today, "08" tomorrow, with no content change. The href itself (`{s.id}.html`, `render.py:375`) is *already* content-stable (it uses `Surface.id`), so links to existing pages do **not** rot today — but the **human-visible refs do**, and the model has no `Site/Collection/Page` layer, no per-type sequential ref (`R-001`/`EP01`), no slug-as-canonical-key, and no persistence to guarantee a ref never moves. [VERIFIED: render.py, dogfood.py]

The spec (`docs/surfaces.md`, `docs/architecture.md`) does **NOT** define an `EP01`/`R-001`/issue/date ID scheme — those forms appear only in the requirement (`REQUIREMENTS.md:45`), the ROADMAP (`ROADMAP.md:227`), and the prior research doc (`.planning/research/ARCHITECTURE.md:258-286`). This is a **spec gap, not a spec conflict**: there is nothing to contradict, so per the "specs are source of truth" rule the planner should **add the ID convention to `docs/surfaces.md` (or `docs/architecture.md`) in the same change** that introduces it, and say why. [VERIFIED: grep of docs/]

**Primary recommendation:** Add `src/newsletters/site.py` with Pydantic `Site/Collection/Page`, a stdlib `slugify()`, and a `Ledger` that reads/writes `content/rev1/ids.json` (append-only, keyed by slug, per-type sequential refs). Rewrite `render_library()`'s `enumerate` loop to read `Page.ref` instead of the positional index, keeping `{s.id}.html` hrefs unchanged for backward compatibility. Prove stability with a test that builds the Site, reorders/inserts the input surface list, rebuilds against the same ledger, and asserts every existing `(slug, ref)` is byte-identical and every existing `.html` link target still resolves. Do **not** build nav, a real Home, or the gate-state board (Phase 9).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Identity assignment (slug, ref, issue/date) | Core model (`site.py`) | Persistence (ledger JSON) | Identity must be deterministic, typed, and AI-free; it is content/domain logic, not presentation. |
| Append-only ref persistence | Persistence (ledger file) | Core model (reads/writes it) | The stability guarantee requires a committed source of truth; the model is the only writer. |
| Grouping surfaces into collections | Core model (`Site`/`Collection`) | — | Grouping by surface TYPE is domain structure (mirrors `templates.py` presets), not a render concern. |
| Rendering refs/links into HTML | Presentation (`render.py`) | Core model (supplies `Page`) | `render.py` already owns all HTML; it should *consume* the model, never compute identity. |
| Cross-link resolution | Core model (`Page.slug`/`ref`) | Presentation | Links resolve through the model so reorder can't break them; render only emits the resolved href. |

**Why this matters:** today identity is computed *inside the presentation tier* (`enumerate` in `render.py`). The whole phase is moving identity OUT of presentation and INTO a deterministic core model — the responsibility map makes that boundary explicit for the planner and plan-checker.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `re` | 3.12 (bundled) | Collapse non-alphanumeric runs to `-` in slugify | Zero dependency; deterministic. [VERIFIED: stdlib] |
| Python stdlib `unicodedata` | 3.12 (bundled) | ASCII-fold accents (NFKD + drop combining marks) | The canonical dependency-free way to fold Unicode → ASCII. [VERIFIED: stdlib] |
| Python stdlib `json` | 3.12 (bundled) | Read/write the ID ledger with `sort_keys=True` | Stable, git-friendly serialization; no dep. [VERIFIED: stdlib] |
| Python stdlib `pathlib` | 3.12 (bundled) | Ledger file path handling | Matches existing `dogfood.build_site()` usage (`dogfood.py:15,650-653`). [VERIFIED: dogfood.py] |
| `pydantic` | already a core dep | `Site`/`Collection`/`Page` typed models | The project's typed-everything spine is Pydantic (`semantic.py:34`, `templates.py:15`). [VERIFIED: semantic.py] |

### Supporting
None. This phase introduces **no new package.**

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib slugify (~12 lines) | `python-slugify` | **Forbidden by 08-CONTEXT decision 5.** Adds a dependency for ~12 lines of code, and would need vetting against the AI-optional-core boundary. Reject. |
| append-only JSON ledger | derive refs from a content hash (e.g. first 7 chars of slug SHA) | Hash refs are stable and need no persisted file, BUT they are NOT human-sequential (`R-001`, `EP01`) — the requirement explicitly wants human ordinals. Ledger is required. |
| JSON ledger | a per-surface `ref` field hand-set in `dogfood.py` | Pushes the stability burden onto authors (easy to collide/skip); the ledger automates "next free per type" and is the single source of truth. Reject hand-setting. |

**Installation:** None required. No `npm`/`pip`/`cargo` install in this phase.

**Version verification:** N/A — no external packages. The only "versions" are the bundled Python 3.12 stdlib (project targets py3.12 per `.venv/lib/python3.12`, [VERIFIED: filesystem]) and the already-present Pydantic.

---

## Package Legitimacy Audit

**Not applicable.** This phase installs **no external packages**. All capabilities use the Python standard library (`re`, `unicodedata`, `json`, `pathlib`) plus the already-vendored `pydantic`. No registry lookup, slopsquat check, or postinstall audit is needed.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
  build_surfaces()  ──►  list[Surface]   (ORDER is incidental, not identity)
   (dogfood.py)              │
                            ▼
              ┌──────────────────────────────┐
              │  Site.from_surfaces(surfaces, │   ← reads content/rev1/ids.json
              │     ledger=Ledger.load(path)) │      (append-only ID ledger)
              └──────────────────────────────┘
                            │
            ┌───────────────┼────────────────────────────┐
            ▼               ▼                             ▼
   for each Surface:   slugify(title)            Ledger.ref_for(slug, type)
            │          (stdlib, pure)            • existing slug → SAME ref
            │                                    • new slug → next free per-type ref
            │                                    • write back (append-only)
            ▼
   Page(slug, ref, issue/date, title,
        gate, signal_color, surface)
            │
            ▼
   group by Surface.kind ──► Collection(kind, pages=[...])
            │
            ▼
   Site(collections=[...])
            │
            ▼
   render_library(site)  ──►  uses Page.ref (NOT enumerate index)
   render_surface(...)        href = f"{page.slug}.html"  (== Surface.id today)
            │
            ▼
   content/rev1/site/*.html   (links resolve by slug/ref, reorder-proof)
```

File-to-implementation mapping is in the Component Responsibilities note below; the diagram shows data flow only.

### Recommended Project Structure
```
src/newsletters/
├── site.py          # NEW: Site / Collection / Page + slugify + Ledger (stdlib + pydantic only)
├── render.py        # EDIT: render_library() reads Page.ref, not enumerate index
├── dogfood.py       # EDIT: build_site() builds a Site and passes it to the renderer
└── __init__.py      # EDIT: export Site, Collection, Page, slugify (mirror existing export style)
content/rev1/
└── ids.json         # NEW: the committed, append-only ID ledger
tests/
└── test_site.py     # NEW: slugify determinism + ledger append-only + reorder/insert stability
```

**Component responsibilities:**
- `site.py::slugify` — pure function, no I/O.
- `site.py::Ledger` — the ONLY reader/writer of `ids.json`; owns "next free per-type ref".
- `site.py::Site.from_surfaces` — orchestrates slugify + ledger + grouping; pure given a ledger.
- `render.py` — consumes `Site`/`Page`, emits HTML; computes **no** identity.

### Pattern 1: Content-model SSG (Site → Collection → Page)
**What:** Model the library as `Site` → `Collection`s (by surface type) → `Page`s (one per surface), where each `Page` carries its own stable identity. Identity comes from the model, never from list position. This is the documented Rev2 pattern. [CITED: .planning/research/ARCHITECTURE.md:258-286]
**When to use:** Now — it is the exact fix for the positional-numbering bug.
**Example:**
```python
# src/newsletters/site.py  — Source: derived from .planning/research/ARCHITECTURE.md:276-286,
# adapted to the LIVE Surface API (semantic.py:464-502) and AI-free constraint.
from __future__ import annotations
from datetime import date as _date
from pydantic import BaseModel, Field
from .semantic import ReviewState, Surface
from .templates import SignalColor

class Page(BaseModel):
    slug: str                      # canonical link key, content-derived from title
    ref: str                       # per-type human ordinal, ledger-assigned (R-001 / EP01 / A-003)
    title: str
    kind: str                      # surface.kind (report/article/newsletter/show/...)
    gate: ReviewState              # surface.gate — Collection grouping is by kind; gate is carried, not yet a column (Phase 9)
    signal_color: SignalColor      # surface.signal_color (for the --signal CSS var)
    href: str                      # f"{slug}.html" — kept == Surface.id today for backward-compat
    issue: int | None = None       # cadenced surfaces only (newsletter/show)
    date: _date | None = None      # cadenced surfaces only
    surface: Surface               # the rendered Surface this Page points at

class Collection(BaseModel):
    kind: str                      # the surface type that groups these pages
    display_name: str              # from template.display_name
    pages: list[Page] = Field(default_factory=list)

class Site(BaseModel):
    collections: list[Collection] = Field(default_factory=list)

    def pages(self) -> list[Page]:
        return [p for c in self.collections for p in c.pages]
```

### Pattern 2: Append-only ledger keyed by content slug
**What:** A committed JSON file maps `slug -> {ref, type, issue, date}`. On build, an existing slug **keeps its recorded ref**; a new slug is assigned the next free ref for its type and written back. Existing entries are immutable. This is the mechanism that makes a *sequential* ref position-independent. [CITED: 08-CONTEXT decision 3]
**When to use:** Whenever refs must be both human-sequential AND stable across reorders.

### Anti-Patterns to Avoid
- **Deriving any visible identifier from list index** (`enumerate(surfaces, 1)`, `render.py:373`). This is the exact bug. Identity comes from `Page`, never from enumeration order.
- **Recomputing an existing ref.** The ledger is read-then-extend; never rebuild it from scratch — that would renumber on reorder and break criterion 2.
- **Letting `render.py` slugify or assign refs.** Identity is a core-model concern; the presentation tier only consumes resolved values.
- **Building the gate-state kanban board now.** That is Phase 9/10. Here `Collection` groups by *type* only; `Page.gate` is merely carried.
- **Changing the href scheme.** Hrefs are `{s.id}.html` today (`render.py:375`); keep `href == slug == Surface.id` so existing `content/rev1/site/*.html` links never rot.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Unicode → ASCII folding | A hand-maintained accent→letter dict | `unicodedata.normalize("NFKD", s)` then drop combining marks | The stdlib already encodes the full Unicode decomposition table; a hand dict is incomplete and non-deterministic across inputs. |
| Stable JSON output for git | Custom key-sorting/serializer | `json.dumps(..., sort_keys=True, indent=2, ensure_ascii=False)` | One stdlib call gives a byte-stable, human-diffable, git-friendly ledger. |
| Slug generation | `python-slugify` (new dep) | ~12-line stdlib `slugify()` (below) | Forbidden by 08-CONTEXT; the stdlib version is fully sufficient for ASCII titles. |

**Key insight:** Everything this phase needs is in the stdlib. The *hard part is not the code, it is the invariant* — "an existing ref never changes" — which is enforced by the append-only ledger discipline and proven by a test, not by a library.

---

## Question-by-Question Findings

### A. Current ID + linking reality (what breaks on reorder)

**How display numbers are assigned — POSITIONAL (the bug):**
```python
# render.py:369-381 (render_library)
for i, s in enumerate(surfaces, 1):          # render.py:373  ← positional index
    rows.append(
        f'<a class="lib-surface" href="{_e(s.id)}.html" ...>'   # render.py:375  ← href uses Surface.id (content-stable)
        f'<span class="lib-idx">{i:02d}</span>'                 # render.py:376  ← VISIBLE number == position
        ...
```
[VERIFIED: render.py:369-381]

**How hrefs are built — content-stable already:**
- Library row link: `href="{_e(s.id)}.html"` (`render.py:375`).
- File written per surface: `out / f"{s.id}.html"` (`dogfood.py:657`).
- Index written as `index.html` (`dogfood.py:662-663`).
[VERIFIED: render.py:375, dogfood.py:657-663]

**How each `Surface.id` is set in `dogfood.py`** (all hand-authored string ids):
| Surface | `id` | Set at |
|---------|------|--------|
| Report (kickoff) | `report-kickoff` | `dogfood.py:242` (`surface_id=`) |
| Report (datamodel) | `report-datamodel` | `dogfood.py:303` |
| Report (rev1) | `report-rev1` | `dogfood.py:375` |
| Report (plan) | `report-plan` | `dogfood.py:580` |
| Article | `article-semantic-spine` | `dogfood.py:619` |
| Show | `show-ep01` | `dogfood.py:492` |
| Newsletters | `newsletter-{reader_key}` (`-jj`/`-nate`/`-newcomer`) | `dogfood.py:456` |
[VERIFIED: dogfood.py]

**The build order that feeds `enumerate`:**
```python
# dogfood.py:640-647 (build_surfaces) — ORDER here drives the visible numbers
return [show, kickoff, datamodel, rev1, plan, article, *newsletters]
```
And the Library lists a filtered subset (one representative newsletter):
```python
# dogfood.py:661 — only newsletter-jj is listed; the other two are its re-cuts
listed = [s for s in surfaces if not (s.kind == "newsletter" and s.id != "newsletter-jj")]
```
[VERIFIED: dogfood.py:640-647, 661]

**Concrete rot points the phase must fix:**
1. **`render.py:376` `{i:02d}` is the displayed identity and is purely positional.** Reorder `build_surfaces()`'s return list, or insert a surface, and every row below the change renumbers. This is the literal SITE-01 / success-criterion-2 failure. **FIX:** display `Page.ref` instead of `i`.
2. **`render.py:373` `enumerate` is the source of that positional number.** **FIX:** iterate `site.pages()` (or per `Collection`) and read `page.ref`.
3. **No per-type sequential ref exists** (`R-001`, `EP01`, `A-003`). Nothing in the model produces them. **FIX:** ledger-assigned `ref` on `Page`.
4. **No slug-as-canonical-key layer.** Links happen to be stable because `Surface.id` is hand-authored and unique, but there is no *model* guaranteeing it; if an author reuses or renames an id, links rot silently. **FIX:** `Page.slug` (defaulting from `Surface.id` for backward-compat) becomes the canonical key, persisted in the ledger.
5. **`FanoutLink` cross-links carry NO href** — they are title-only today (`FanoutLink.href` defaults `None`, `semantic.py:355`; the renderer ignores it, `render.py:266-271`). So "cross-links" in the fan-out diagram are *display strings*, not real links. **NOTE for scope:** wiring `FanoutLink.href` to resolve through `Page.slug` is the natural Phase-8 cross-link fix, but emitting them as real `<a href>` is arguably Phase-9 (SITE-04 source/cross links). **Recommendation:** Phase 8 should make the resolution *possible* (give `Site` a `slug`/`ref` lookup) but the planner should confirm with the user whether to also render fan-out anchors now or defer to Phase 9. [VERIFIED: semantic.py:352-356, render.py:266-273] **(See Assumption A1.)**

### B. Spec conventions for IDs

**Finding: the spec does NOT define an `EP01`/`R-001`/issue/date ID scheme.** Grepping `docs/surfaces.md` and `docs/architecture.md` for `EP01`, `R-001`, `slug`, `issue`, `Collection`, `Site`, `Page`, `ref`, `permalink`, `href` returns **no ID-convention matches** in either spec. [VERIFIED: Grep docs/surfaces.md, docs/architecture.md]

What the spec *does* say (closest material):
- `docs/surfaces.md:84` — the Show is "an episode page … new episode every other week" and "Structurally: episode hero" — implies an **episode number** but defines no format. [CITED: docs/surfaces.md:83-86]
- `docs/surfaces.md:96` — "Each issue carries a `GateBadge`" — implies a newsletter **issue** concept, no format. [CITED: docs/surfaces.md:96]
- `docs/architecture.md:20` — `kind ∈ { show, newsletter, article, report }` — the surface types that become the `Collection`s. [CITED: docs/architecture.md:20]

The `EP01` / `R-001` / slug / issue-date forms appear ONLY in non-spec planning artifacts:
- `REQUIREMENTS.md:45` (SITE-01) and `ROADMAP.md:227`. [VERIFIED]
- The prior research `.planning/research/ARCHITECTURE.md:258-286` ("a `Page` is one instance with a stable per-surface ID (`R-001`, `EP01`)"). [VERIFIED]

**Conclusion — gap, not conflict.** There is nothing in the spec to contradict the 08-CONTEXT decisions, so the model can adopt the requirement's forms freely. **Per the "specs are source of truth" hard rule, the planner MUST add the chosen ID convention to `docs/surfaces.md` (or `docs/architecture.md`) in the SAME change** — documenting: the per-type prefixes (`R-` Report, `EP` Show/episode, `A-` Article, newsletter by `issue`), the zero-pad width, the slug rule, and the ledger as source of truth. Recommended canonical forms (consistent with `REQUIREMENTS.md:45`):

| Surface kind | `template.name` | ref prefix | example | cadenced? |
|--------------|-----------------|------------|---------|-----------|
| Report | `report` | `R-` + 3-digit | `R-001` | no |
| Article | `article` | `A-` + 3-digit | `A-003` | no |
| Show | `show` | `EP` + 2-digit | `EP01` | yes (issue = episode no., date) |
| Newsletter | `newsletter` | (issue-based) | issue `12` + date | yes |

[ASSUMED] — the exact prefix/width mapping is inferred from `REQUIREMENTS.md:45`'s examples, not specified. Confirm with the user before locking. **(See Assumption A2.)**

### C. Slugify (stdlib, no dependency)

**Recommended rule (deterministic, dependency-free):**
1. Unicode-normalize to NFKD and drop combining marks (ASCII-fold): `unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")`.
2. Lowercase.
3. Replace every run of non-`[a-z0-9]` characters with a single `-` (`re.sub(r"[^a-z0-9]+", "-", s)`).
4. Strip leading/trailing `-`.
5. Collision policy: if the resulting slug already exists for a *different* surface, append `-2`, `-3`, … (deterministic, ledger-checked). For Rev1 the existing `Surface.id`s are already unique, so no collision occurs.

```python
# src/newsletters/site.py  — Source: stdlib re + unicodedata (no python-slugify).
import re, unicodedata

def slugify(text: str) -> str:
    """Deterministic, dependency-free slug: ASCII-fold, lowercase, non-alnum → '-', strip."""
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")
```
[VERIFIED: stdlib re/unicodedata behavior]

**`python-slugify` is NOT needed** — confirmed forbidden by 08-CONTEXT decision 5; the four-line function above covers every Rev1 title. Default each `Page.slug` from the existing `Surface.id` (which is already slug-shaped, e.g. `report-kickoff`) for backward-compat, falling back to `slugify(title)` only when constructing a Page from a surface whose `id` is not slug-clean.

**Backward-compat tactic:** for the Rev1 corpus, set `Page.slug = surface.id` directly. This guarantees `href == {surface.id}.html` (unchanged from `render.py:375`), so **no existing `content/rev1/site/*.html` link rots.** `slugify(title)` is the rule for *new* surfaces lacking a hand-set id.

### D. The append-only ID ledger (the stability mechanism)

**File location:** `content/rev1/ids.json` (recommended over `content/ids.json` — it sits beside the Rev1 rendered output it indexes, `content/rev1/site/`, and matches how `build_site()` already writes under `content/rev1/`, `dogfood.py:650`). [VERIFIED: dogfood.py:650]

**JSON shape** (keyed by slug; `sort_keys=True` for stable git diffs):
```json
{
  "article-semantic-spine": { "ref": "A-001", "type": "article", "issue": null, "date": null },
  "report-datamodel":       { "ref": "R-002", "type": "report",  "issue": null, "date": null },
  "report-kickoff":         { "ref": "R-001", "type": "report",  "issue": null, "date": null },
  "report-plan":            { "ref": "R-004", "type": "report",  "issue": null, "date": null },
  "report-rev1":            { "ref": "R-003", "type": "report",  "issue": null, "date": null },
  "show-ep01":              { "ref": "EP01",  "type": "show",    "issue": 1,    "date": "2026-06-14" }
}
```

**Assignment algorithm (append-only, deterministic):**
```
load ledger (or {} if file absent)
for each surface, in build order:
    slug = surface.slug   # == surface.id for Rev1
    if slug in ledger:
        ref = ledger[slug]["ref"]            # EXISTING → immutable, never recomputed
    else:
        n = 1 + max(parsed ordinal of every ledger entry whose type == surface.kind, default 0)
        ref = format_ref(surface.kind, n)    # e.g. f"R-{n:03d}", f"EP{n:02d}"
        ledger[slug] = {ref, type, issue, date}   # APPEND only
write ledger back with json.dumps(sort_keys=True, indent=2, ensure_ascii=False)
```
Key properties:
- **Existing slug → identical ref, always** (read, never recompute) → satisfies success criterion 2.
- **Per-type sequence** derived as `max(existing ordinals of that type) + 1` — robust to gaps and to insertion order, because new numbers are only ever appended above the current max.
- **Deterministic & git-friendly** via `sort_keys=True` — same content → byte-identical file.
- Newsletter `issue` and Show episode/date are **content-supplied** (carried on the Page / ledger entry), not derived from position.

**Edge cases / determinism notes:**
- The "next free" is `max+1`, NOT `count+1` — so deleting a surface does not let a future surface reuse a retired number (append-only). The planner should decide whether deletion is in scope (likely not for Rev1).
- Ordinal parsing must tolerate both widths (`R-001`, `EP01`); parse trailing digits with `re.search(r"(\d+)$", ref)`.
- The ledger is the **single writer**; `render.py` must never touch it.

**Stability test design (proves success criterion 2):**
```
test_reorder_and_insert_preserve_ids():
    surfaces = build_surfaces()
    site1 = Site.from_surfaces(surfaces, ledger=Ledger.load(tmp_path/"ids.json"))
    ids1  = {p.slug: p.ref for p in site1.pages()}
    links1 = {p.href for p in site1.pages()}

    reordered = list(reversed(surfaces))            # reorder
    reordered.insert(0, make_new_report("brand new"))  # insert one
    site2 = Site.from_surfaces(reordered, ledger=Ledger.load(tmp_path/"ids.json"))
    ids2  = {p.slug: p.ref for p in site2.pages()}

    # 1. every PRE-EXISTING slug keeps its EXACT ref
    for slug, ref in ids1.items():
        assert ids2[slug] == ref
    # 2. every pre-existing link target still exists
    assert links1 <= {p.href for p in site2.pages()}
    # 3. the new surface got a fresh, non-colliding per-type ref
    assert ids2["brand-new"] not in ids1.values()

test_slugify_is_deterministic():       # same input → same output, ASCII-fold, lowercase, collapse
test_ledger_is_append_only():          # existing entries byte-identical after a rebuild
test_ledger_json_is_stable():          # json round-trips with sort_keys → identical bytes
```
The reorder+insert assertion is the literal encoding of ROADMAP success criterion 2. `nyquist_validation` is ON (`config.json`), and `pytest` is the framework (`pyproject.toml [tool.pytest.ini_options] testpaths=["tests"]`), so this belongs in `tests/test_site.py`. [VERIFIED: config.json, pyproject.toml]

### E. Site / Collection / Page shape

**Validated against the live renderer.** Everything `render_library()` reads off a surface today maps cleanly onto a `Page` field:
| `render.py` usage | line | Page field |
|-------------------|------|-----------|
| `s.id` (href + filename) | 375, dogfood 657 | `Page.slug` / `Page.href` |
| `{i:02d}` (the bug) | 376 | **replaced by** `Page.ref` |
| `s.title` | 377 | `Page.title` |
| `s.template.tagline` | 378 | (read from `Page.surface.template`) |
| `s.template.signal_color.css_var` | 375 | `Page.signal_color` |
| `s.template.display_name` | 379 | `Collection.display_name` |
| `s.template.cadence.label` | 379 | (read from `Page.surface.template`) |
| `s.gate.value` | 380 | `Page.gate` |
[VERIFIED: render.py:373-381]

**Recommended Pydantic fields** (see Pattern 1 code block above for the full definition):
- `Page`: `slug: str`, `ref: str`, `title: str`, `kind: str`, `gate: ReviewState`, `signal_color: SignalColor`, `href: str`, `issue: int | None`, `date: datetime.date | None`, `surface: Surface`.
- `Collection`: `kind: str`, `display_name: str`, `pages: list[Page]`.
- `Site`: `collections: list[Collection]`, plus helper methods `pages()` and a `by_slug(slug) -> Page | None` lookup for cross-link resolution.

**Grouping:** group surfaces by `surface.kind` (== `template.name`, `semantic.py:489`) into Collections, ordered by `template.distance` (`templates.py:101,184` already give a canonical ordering: Show 0, Report 1, Article 2, Newsletter 3). This is the natural board-column order without building the board. [VERIFIED: templates.py:101-158,184; semantic.py:488-490]

**Minimal renderer wiring change (no Phase-9 IA):**
- `render_library(surfaces)` → `render_library(site)`. Replace the `enumerate` loop with iteration over `site.pages()` (or nested `for collection in site.collections: for page in collection.pages`), rendering `page.ref` in place of `{i:02d}` and `page.href` (== `{slug}.html`) for the link. Keep the existing intro/fan-out markup verbatim.
- `build_site()` (`dogfood.py:650-665`): build the `Site` from `build_surfaces()` via `Site.from_surfaces(...)`, keep writing `{page.slug}.html` per page (identical filenames to today, `dogfood.py:657`), and pass the `Site` (or the filtered listing) to `render_library`.
- `__init__.py`: export `Site`, `Collection`, `Page`, `slugify` mirroring the existing alphabetized export blocks (`__init__.py:17-56`).
[VERIFIED: render.py:369-395, dogfood.py:650-665, __init__.py:14-56]

**Backward-compat guarantees:**
- `Page.slug = surface.id` for Rev1 → all `{surface.id}.html` filenames and hrefs are **unchanged** → existing `content/rev1/site/*.html` links do not rot.
- `Surface.id` stays a string field on `Surface` (`semantic.py:474`); nothing about the existing model is removed. The Site layer wraps, it does not replace.

### F. Scope boundary (Phase 8 vs Phase 9)

**Phase 8 (this phase) — IN:**
- New `site.py`: `Site`/`Collection`/`Page` model, `slugify`, `Ledger`.
- `content/rev1/ids.json` committed ledger.
- Wire the **existing** `render_library` to consume the Site model (refs instead of enumerate).
- Group Pages into Collections **by surface type** (`Collection`).
- Tests: slugify determinism, ledger append-only, reorder/insert stability.
- Add the ID convention to the spec (`docs/surfaces.md`/`architecture.md`) in the same change.

**Phase 9 (NOT here) — OUT:**
- Real marketing Home separate from the Library (SITE-02). [VERIFIED: ROADMAP.md:233-238]
- Four-destination nav + breadcrumbs (SITE-03/04). The current `_NAV_ITEMS` has 3 dead `None` hrefs (`render.py:164`) — **leave them**; wiring nav is Phase 9.
- Library status-board with **columns BY GATE STATE** (the kanban). 08-CONTEXT decision 5 is explicit: "board STATUS columns by gate state are Phase 9/10 — here just the `Collection` grouping + stable IDs."
- Rendering real source/cross links into the repo (SITE-04/05/06).

**Phase-9 pull-in risks to flag for the planner:**
1. **The gate-state board.** `Page.gate` is carried, and it is tempting to add `Site.library_board() -> dict[gate, pages]` now (the prior research even sketches it, `.planning/research/ARCHITECTURE.md:282`). **Do NOT render columns-by-gate in Phase 8** — carrying the field is fine; building the board view is Phase 9/10.
2. **Fan-out cross-links as real anchors.** Resolving `FanoutLink` → `Page.slug` is natural here, but *emitting* them as `<a href>` blurs into SITE-04. Recommend: build the resolver (`Site.by_slug`), defer anchor rendering unless the user asks. **(Assumption A1.)**
3. **Nav.** Don't touch `_NAV_ITEMS`/`_nav()` — that's the four-destination nav of Phase 9.

---

## Runtime State Inventory

> This phase ADDS a new persisted file (the ledger) and changes how an existing rendered artifact is produced — so the rename/refactor-style inventory applies to the *new* persisted state and the *existing* links.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **New:** `content/rev1/ids.json` — the append-only ID ledger (slug → ref/type/issue/date). It becomes committed source of truth for refs. | Create + commit it; seed it from the first `build_site()` run so Rev1 refs are locked. **Code edit + data file**, both. |
| Live service config | None — no external service, UI, or remote config holds these IDs. (Verified: this is a static-HTML renderer, `render.py` docstring lines 1-9; no server.) | None. |
| OS-registered state | None — no Task Scheduler / pm2 / systemd / launchd involvement. | None. |
| Secrets/env vars | None — no secret or env var references a surface id. | None. |
| Build artifacts | **Existing:** `content/rev1/site/*.html` (10 files: `report-*.html`, `article-semantic-spine.html`, `show-ep01.html`, `newsletter-*.html`, `index.html`). These are re-rendered by `build_site()`. | Re-render after wiring; **link targets (`{id}.html`) must stay byte-identical** so no link rots — guaranteed by `slug == surface.id`. [VERIFIED: ls content/rev1/site/] |

**The canonical question — after the repo is updated, what still has the old identity cached?** Only the rendered `content/rev1/site/*.html` files, which are regenerated by `build_site()`; keeping `slug == surface.id` means their filenames and internal hrefs are unchanged.

---

## Common Pitfalls

### Pitfall 1: Rebuilding the ledger instead of extending it
**What goes wrong:** A naive `Site.from_surfaces` recomputes all refs from scratch each build → reorder renumbers → criterion 2 fails.
**Why it happens:** Treating the ledger as derived output rather than persisted source of truth.
**How to avoid:** Read the ledger first; existing slug → read its ref (never recompute); only *new* slugs get `max(type ordinal)+1`; write back the union. The append-only test catches regressions.
**Warning signs:** `git diff content/rev1/ids.json` shows changed (not just added) entries after a reorder-only build.

### Pitfall 2: `slug != surface.id` for the Rev1 corpus
**What goes wrong:** If `slug = slugify(title)` is used for existing surfaces, `slugify("Kicking off the build — spec set, repo shape, typed spine")` ≠ `report-kickoff`, so the href changes and every existing `content/rev1/site/report-kickoff.html` link rots.
**Why it happens:** Applying the new-surface rule to legacy surfaces.
**How to avoid:** Default `Page.slug = surface.id`; only `slugify(title)` when `surface.id` is absent/non-slug. Assert in the stability test that all 10 current filenames still resolve.
**Warning signs:** A diff in the set of written `*.html` filenames vs the current `content/rev1/site/` listing.

### Pitfall 3: Non-deterministic ledger JSON (git churn)
**What goes wrong:** `json.dump` without `sort_keys` reorders entries by insertion → noisy diffs and non-determinism.
**How to avoid:** `json.dumps(ledger, sort_keys=True, indent=2, ensure_ascii=False) + "\n"`.
**Warning signs:** `ids.json` diff churns on a no-op rebuild.

### Pitfall 4: Importing an AI package into `site.py`
**What goes wrong:** `lint-imports` fails the AI-optional-core contract.
**How to avoid:** `site.py` imports only stdlib (`re`, `unicodedata`, `json`, `pathlib`, `datetime`) + `pydantic` + sibling `.semantic`/`.templates`. None are on the forbidden list (`.importlinter:28-36`). [VERIFIED: .importlinter]
**Warning signs:** Any `import` beyond those in `site.py`.

---

## Code Examples

### Ledger read → assign → write (the heart of the phase)
```python
# src/newsletters/site.py — stdlib only. Source: derived from 08-CONTEXT decision 3.
import json, re
from pathlib import Path

_REF_FMT = {"report": "R-{:03d}", "article": "A-{:03d}", "show": "EP{:02d}", "newsletter": "N-{:03d}"}

class Ledger:
    def __init__(self, path: Path, data: dict[str, dict]):
        self.path, self._data = path, data

    @classmethod
    def load(cls, path: str | Path) -> "Ledger":
        p = Path(path)
        data = json.loads(p.read_text("utf-8")) if p.exists() else {}
        return cls(p, data)

    def ref_for(self, slug: str, kind: str, *, issue=None, date=None) -> str:
        if slug in self._data:
            return self._data[slug]["ref"]                 # EXISTING — immutable
        ordinals = [
            int(m.group(1))
            for e in self._data.values() if e["type"] == kind
            for m in [re.search(r"(\d+)$", e["ref"])] if m
        ]
        n = (max(ordinals) + 1) if ordinals else 1
        ref = _REF_FMT.get(kind, "{}-{:03d}").format(n) if "{:" in _REF_FMT.get(kind, "") else _REF_FMT[kind].format(n)
        self._data[slug] = {"ref": ref, "type": kind, "issue": issue,
                            "date": date.isoformat() if date else None}
        return ref

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, sort_keys=True, indent=2, ensure_ascii=False) + "\n", "utf-8"
        )
```
(The planner should simplify the `_REF_FMT` lookup — shown verbose here only to make the per-type formatting explicit.)

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Positional `enumerate(surfaces,1)` visible index (`render.py:373-376`) | Ledger-assigned, content-keyed `Page.ref` | This phase (Rev2) | Refs stop renumbering on reorder. |
| Identity computed in the presentation tier | Identity computed in a deterministic core model (`site.py`) | This phase | Honors the tier-responsibility map; testable in isolation. |
| No site content model (flat `list[Surface]`) | `Site → Collection → Page` | This phase | Matches the documented Rev2 SSG pattern (`.planning/research/ARCHITECTURE.md:258`). |

**Deprecated/outdated:** the `enumerate`-based numbering in `render_library` (`render.py:373,376`) is replaced — but the function signature and surrounding markup are preserved to minimize churn.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Rendering `FanoutLink` cross-links as real `<a href>` anchors is deferable to Phase 9; Phase 8 only needs to make resolution *possible* (`Site.by_slug`). | Q-A pt5, Q-F | If the user wants clickable fan-out links now, the planner must add an anchor-rendering task + `FanoutLink.href` wiring in Phase 8. Low risk (resolver is cheap; rendering is additive). |
| A2 | The per-type ref forms — `R-NNN` (report), `A-NNN` (article), `EP NN` (show), newsletter by `issue` — and their zero-pad widths are the intended convention. | Q-B | The spec defines no convention; if the user prefers different prefixes/widths, change `_REF_FMT` before the ledger is seeded (changing it after seeding would renumber). Confirm BEFORE first `build_site()`. Medium risk — seeding locks it in. |
| A3 | Ledger lives at `content/rev1/ids.json` (beside the Rev1 output) rather than `content/ids.json`. | Q-D | Cosmetic; a path change is trivial pre-seed. Low risk. |
| A4 | Surface deletion is out of scope for Rev1 (append-only `max+1` never reuses retired numbers). | Q-D | If deletion+renumber is ever wanted it needs a separate decision; append-only is the safe default. Low risk. |

---

## Open Questions

1. **Clickable fan-out cross-links now or Phase 9?**
   - What we know: `FanoutLink.href` exists but is unused (`semantic.py:355`, `render.py:266-273`); resolving it through `Page.slug` is easy.
   - What's unclear: whether emitting real anchors is Phase 8 or SITE-04 (Phase 9).
   - Recommendation: build the resolver (`Site.by_slug`) in Phase 8; defer anchor *rendering* to Phase 9 unless the user asks. (Assumption A1.)
2. **Exact ref prefixes/widths.**
   - What we know: only example forms exist (`R-001`, `EP01`) in `REQUIREMENTS.md:45`.
   - What's unclear: the canonical mapping for article/newsletter and pad widths.
   - Recommendation: the discuss/plan step should confirm `_REF_FMT` with the user **before** seeding the ledger. (Assumption A2.)

---

## Environment Availability

**SKIPPED (no external dependencies).** This phase is pure Python (stdlib + already-present Pydantic) and writes a local JSON file plus local HTML. No CLI tool, runtime, service, database, or network dependency is introduced. The only runtime is Python 3.12, already in use (`.venv/lib/python3.12`). [VERIFIED: filesystem]

---

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json` — section included. [VERIFIED: config.json]

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (declared in `pyproject.toml` `[tool.pytest.ini_options]`) [VERIFIED] |
| Config file | `pyproject.toml` (`testpaths = ["tests"]`) [VERIFIED] |
| Quick run command | `pytest tests/test_site.py -x -q` |
| Full suite command | `pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SITE-01 | Model carries stable per-surface IDs (slug/ref/issue/date) from content | unit | `pytest tests/test_site.py::test_page_ids_are_content_derived -x` | ❌ Wave 0 |
| SITE-01 | slugify is deterministic, ASCII-folded, collapses non-alnum | unit | `pytest tests/test_site.py::test_slugify_is_deterministic -x` | ❌ Wave 0 |
| SITE-01 (criterion 2) | Reorder + insert do not change any existing ref or break any link | unit | `pytest tests/test_site.py::test_reorder_and_insert_preserve_ids -x` | ❌ Wave 0 |
| SITE-01 | Ledger is append-only; existing entries immutable | unit | `pytest tests/test_site.py::test_ledger_is_append_only -x` | ❌ Wave 0 |
| SITE-01 | Ledger JSON is byte-stable (sort_keys) for git | unit | `pytest tests/test_site.py::test_ledger_json_is_stable -x` | ❌ Wave 0 |
| (regression) | Existing `content/rev1/site/*.html` filenames/hrefs unchanged | unit | `pytest tests/test_site.py::test_existing_links_do_not_rot -x` | ❌ Wave 0 |
| (boundary) | `site.py` imports no AI package | static | `lint-imports` (existing `.importlinter` contract) | ✅ exists |

### Sampling Rate
- **Per task commit:** `pytest tests/test_site.py -x -q`
- **Per wave merge:** `pytest -q && lint-imports`
- **Phase gate:** Full suite green + `lint-imports` green before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_site.py` — all SITE-01 tests above (none exist yet).
- [ ] No new fixtures needed — `build_surfaces()` (`dogfood.py:640`) is the corpus; use `tmp_path` for the ledger.
- [ ] Framework install: none — pytest already present.

---

## Security Domain

> `security_enforcement` is `true`, `security_asvs_level: 1` in config. Section included. [VERIFIED: config.json]

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface in this phase. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | no | No access control; static content model. |
| V5 Input Validation | yes (minor) | Pydantic validates `Site/Collection/Page`; `slugify` sanitizes titles to `[a-z0-9-]` (no path-traversal chars reach a filename). |
| V6 Cryptography | no | No crypto. The ledger is plaintext committed config — not a secret. |

### Known Threat Patterns for {static Python renderer}
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Slug → filename path traversal (`../`) | Tampering | `slugify` strips everything outside `[a-z0-9-]` before it is used in `f"{slug}.html"`; assert in a test that no slug contains `/`, `.`, or `\`. |
| HTML injection via title in rendered ref/link | Tampering / XSS | The renderer already escapes via `_e()`/`html.escape` (`render.py:167-168`); continue escaping all Page fields rendered into HTML. [VERIFIED: render.py:167] |
| Untrusted ledger contents | Tampering | The ledger is a committed, human-reviewed file (`content/rev1/ids.json`), not user input. Treat as trusted config; still load via `json.loads` (no `eval`). |

**No high-severity findings.** Nothing in this phase blocks on `security_block_on: high`.

---

## Sources

### Primary (HIGH confidence)
- `src/newsletters/render.py:164,167-168,266-273,369-396` — the `enumerate` numbering bug, href construction, escaping, fan-out rendering.
- `src/newsletters/dogfood.py:242,303,375,456,492,580,619,640-665` — how each `Surface.id` is set, build order, `build_site()` write loop.
- `src/newsletters/semantic.py:352-356,464-502` — `FanoutLink.href`, `Surface` shape, `kind`/`gate`/`signal_color` properties.
- `src/newsletters/templates.py:89-158,184` — surface presets, `display_name`, `distance` ordering, `SignalColor`.
- `.importlinter:17-36` — the AI-optional-core forbidden-import contract.
- `pyproject.toml` `[tool.pytest.ini_options]` + dev/test extras — pytest + import-linter.
- `.planning/config.json` — nyquist_validation, security_enforcement, ASVS L1.
- `docs/surfaces.md:80-117` and `docs/architecture.md:20` — surface types; NO ID convention (the gap).
- `ls content/rev1/site/` — the 10 existing rendered files that must not rot.

### Secondary (MEDIUM confidence — curated planning artifacts, not spec)
- `.planning/research/ARCHITECTURE.md:258-286` — the Site/Collection/Page SSG pattern + `R-001`/`EP01` examples.
- `.planning/REQUIREMENTS.md:45,125` and `.planning/ROADMAP.md:219-231` — SITE-01 wording + Phase 8 goal/criteria.

### Tertiary (LOW confidence)
- None. (No WebSearch used — this is a closed codebase+spec task.)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all stdlib + already-present Pydantic, verified against `pyproject.toml`/`.importlinter`.
- Architecture (Site/Collection/Page + ledger): HIGH — validated field-by-field against the live `render_library` usages; pattern matches the prior curated research.
- Pitfalls: HIGH — each derived from a specific live line.
- Spec ID convention: MEDIUM — the *forms* are assumed (spec gap, A2); the *gap itself* is HIGH-confidence verified.

**Research date:** 2026-06-18
**Valid until:** stable domain (no fast-moving deps) — ~30 days, or until `render.py`/`dogfood.py`/`semantic.py` change shape.
