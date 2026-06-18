# Phase 8 — Context & Decisions (Site Content Model & Stable IDs)

**Goal:** Replace position-derived numbering with a `Site/Collection/Page` content model carrying
stable per-surface IDs (`EP01`, `R-001`, slug, issue/date) generated from content, independent of list
position — so links and boards stop rotting when surfaces reorder/insert.

**Requirement:** SITE-01. **Depends on:** the typed semantic model (`Surface`/`SurfaceTemplate`),
`render.py` (the Rev1 renderer + Library) and `dogfood.py` (the sample surfaces).

## Current state (verified)
- Surfaces already carry a string `Surface.id` (e.g. `"session-kickoff"`, `"newsletter-{reader}"`),
  and links use `{s.id}.html`. **But** the Library display numbers via `enumerate(surfaces, 1)`
  (`render.py:373`) — position-derived; reorder renumbers. No `Site/Collection/Page` model exists.

## Decisions (design — research to validate against the live renderer)

1. **`Site / Collection / Page` content model (new, typed, AI-free — likely `src/newsletters/site.py`).**
   - `Site` = the whole library; holds ordered `Collection`s.
   - `Collection` = a grouping by surface TYPE/cadence (Reports, Articles, Newsletters, Shows,
     Learning) — the natural board columns.
   - `Page` = one published surface within a collection; carries the stable IDs + metadata (title,
     slug, ref, issue/date, gate state, signal color) and points at its `Surface`/`Distillation`.
   - Order is data (an explicit list), NEVER the source of identity.

2. **Stable IDs are content-derived or ledger-assigned — NEVER position-derived (the invariant).**
   Each `Page` carries:
   - `slug` — content-derived from the title (deterministic slugify; the URL + cross-link key). Stable
     unless the title changes. This is the canonical link target (replaces `{enumerate}`-based refs).
   - `ref` — a human, per-type sequential id (`R-001`, `EP01`, `A-003`, …) assigned ONCE from a
     **persisted append-only ledger** keyed by slug, so inserting/reordering never renumbers existing
     surfaces (the mechanism that makes sequential refs position-independent). New surface → next free
     number for its type; existing assignments are read, never recomputed.
   - `issue` / `date` — for cadenced surfaces (Newsletters/Shows): a stable issue number + date,
     content-supplied, not positional.

3. **The ID ledger** = a committed, human-readable file (e.g. `content/ids.json` or
   `content/rev1/ids.json`) mapping `slug -> {ref, issue, date, type}`. Read at build; a surface
   missing from the ledger is assigned the next ref for its type and the ledger is updated
   (append-only — existing entries are immutable). This is the single source of truth for refs and the
   proof of stability. Deterministic: same content → same ledger.

4. **Cross-links resolve by slug/ref, not position.** The fan-out diagram, Library board, and any
   surface→surface link resolve through the `Page` (slug/ref), so reordering/inserting cannot break a
   link. Renderer (`render.py`) consumes the `Site` model instead of an enumerated list.

5. **Backward-compat + scope.** Keep existing `Surface.id`s working (slug can default from/align with
   them). This phase is the CONTENT MODEL + stable IDs + ledger + wiring the existing renderer to use
   them; the full Rev2 site IA / navigation / real Home is **Phase 9** (don't build it here). The
   board STATUS columns by gate state are Phase 9/10 — here just the `Collection` grouping + stable IDs.
   No new dependency (slugify is ~10 lines of stdlib; do NOT add `python-slugify`).

## Success criteria (ROADMAP)
1. The `Site/Collection/Page` model carries stable per-surface IDs (`EP01`/`R-001`/slug/issue-date)
   generated from content, independent of list position.
2. Inserting or reordering surfaces does not change any existing surface's ID or break its cross-links.

## Research-locked choices (08-RESEARCH.md accepted 2026-06-18, HIGH confidence)

- **L1 — ID conventions (locked now, BEFORE any ledger seeding; matches REQUIREMENTS `R-001`/`EP01`).**
  Reports `R-NNN` (3-digit → `R-001`); Articles `A-NNN`; Shows/episodes `EPNN` (2-digit → `EP01`);
  Newsletters keyed by `issue` (NN) + `date` (cadenced, not a sequential ref); Learning `L-NNN`. These
  are a naming default consistent with the documented examples — chosen deliberately because changing
  prefixes/widths AFTER the ledger is seeded would renumber (research A2). If the reviewer ever wants
  different prefixes, that's a one-time ledger reset.
- **L2 — Spec is the source of truth → FILL THE GAP.** `docs/surfaces.md`/`docs/architecture.md`
  currently specify NO ID convention (verified: zero matches). The plan MUST add the L1 convention +
  the Site/Collection/Page model to the spec **in the same change** (not a silent drift).
- **L3 — Backward-compat:** for Rev1, `Page.slug` defaults to the existing `Surface.id`, so the 10
  committed `content/rev1/site/*.html` hrefs do NOT rot (hrefs are already content-stable at
  `render.py:375`; the rot point is only the positional VISIBLE number at `render.py:373`/`{i:02d}`).
- **L4 — Slugify:** 4-line stdlib (`unicodedata` NFKD ASCII-fold → lower → `re.sub(r"[^a-z0-9]+","-")`
  → strip). NO `python-slugify` dep.
- **L5 — Ledger:** `content/rev1/ids.json`, `slug -> {ref, type, issue, date}`, written
  `json.dumps(sort_keys=True, indent=2)` (byte-stable git diff). Append-only: existing slug keeps its
  ref (immutable); new slug → `max(per-type ordinal)+1`. This append-only discipline IS the stability
  mechanism. Deterministic: same content → same ledger.
- **L6 — Scope boundary (resist Phase-9 pull-in):** `Collection` groups by surface TYPE only; `Page`
  merely CARRIES `gate` (NO gate-state kanban — that's Phase 10). Build the `Site.by_slug` cross-link
  RESOLVER here, but rendering real clickable fan-out anchors + nav + the real Home is **Phase 9**
  (SITE-04/02). Wire the existing renderer to be Page-driven (replace the enumerate numbering); do not
  build new IA.
- **L7 — Stability test (success criterion 2):** `test_reorder_and_insert_preserve_ids` — build Site →
  reverse the surface list + insert a new surface → rebuild against the same ledger → assert every
  pre-existing `slug→ref` is byte-identical, every pre-existing `.html` target still resolves, and the
  new surface got a fresh per-type ref.

## Hard rules in play
- **Typed everything** — `Site/Collection/Page` are Pydantic, auditable, AI-free (core imports only
  stdlib + Pydantic; keep `lint-imports` green).
- **Specs are source of truth** — align with `docs/surfaces.md` ID conventions if specified; update
  the spec in the same change if behavior differs.
- **Determinism** — IDs are a pure function of content + the append-only ledger; same input → same IDs.
- **No silent renumber** — reordering/inserting MUST NOT mutate an existing surface's ref/slug (prove
  by test: build, reorder the input list, rebuild → identical IDs + working links).

## Research note (dispatch BEFORE planning)
Validate against the LIVE codebase: how `render.py` + `dogfood.py` currently assign `Surface.id`,
build the Library, and render cross-links / the fan-out diagram (what reorder would break today);
the cleanest slugify (stdlib `re`/`unicodedata`, no dep); the ledger shape + append-only assignment
algorithm; how `docs/surfaces.md`/`docs/architecture.md` specify IDs (`EP01`/`R-001`/issue/date) so we
match the spec; and how to wire the `Site` model into the existing renderer with minimal churn (this
phase is the model + IDs, NOT the Phase-9 IA). Record in 08-RESEARCH.md.
