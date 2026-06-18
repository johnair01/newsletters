---
phase: 08-site-content-model-stable-ids
plan: 01
subsystem: api
tags: [pydantic, slugify, ledger, stable-ids, content-model, ssg, ai-optional-core]

# Dependency graph
requires:
  - phase: rev1 typed semantic spine
    provides: Surface / SurfaceTemplate (id, title, kind, gate, signal_color, template.distance) + ReviewState + SignalColor
  - phase: dogfood corpus
    provides: build_surfaces() — the real Rev1 Surface set that seeds the ledger
provides:
  - "src/newsletters/site.py — slugify() + append-only Ledger + typed Site/Collection/Page + Site.from_surfaces + Site.by_slug"
  - "content/rev1/ids.json — the seeded, committed, append-only ID ledger (slug -> {ref,type,issue,date})"
  - "Package exports: Site, Collection, Page, Ledger, slugify"
  - "tests/test_site.py — slugify/ledger/model unit tests incl. the L7 reorder+insert stability proof"
affects: [08-02, "phase-9 site IA / nav / Home", "renderer Page-driven wiring", "cross-link resolution"]

# Tech tracking
tech-stack:
  added: []  # zero new dependencies — pure stdlib (re/unicodedata/json/pathlib/datetime) + already-present pydantic
  patterns:
    - "Identity as a pure function of content + an append-only ledger (never list position)"
    - "Append-only ledger discipline: existing slug ref IMMUTABLE; new slug = max(per-type ordinal)+1"
    - "Page WRAPS Surface (carries identity), never mutates it — Site layer wraps, does not replace"
    - "Pure builder (Site.from_surfaces) — caller owns ledger persistence so tmp_path tests stay isolated"

key-files:
  created:
    - src/newsletters/site.py
    - tests/test_site.py
    - content/rev1/ids.json
    - .planning/phases/08-site-content-model-stable-ids/deferred-items.md
  modified:
    - src/newsletters/__init__.py

key-decisions:
  - "Ledger lives at content/rev1/ids.json (beside the Rev1 rendered output); json.dumps(sort_keys=True, indent=2, ensure_ascii=False)+newline for byte-stable git diffs (L5)"
  - "L1 ID conventions locked at seeding: reports R-NNN (3-digit), articles A-NNN (3-digit), shows EPNN (2-digit), learning L-NNN; newsletters cadenced (issue+date, empty sequential ref)"
  - "slug defaults to Surface.id for the Rev1 corpus (L3 backward-compat — no committed *.html href rots); slugify(title) only for new non-slug-clean ids"
  - "Next per-type ref is max(ordinal)+1, NOT count+1 — append-only, deletion out of scope (A4)"
  - "Site.from_surfaces does NOT call ledger.save() — caller owns persistence (test isolation)"
  - "AI-free runtime test measured in a subprocess with PYDANTIC_DISABLE_PLUGINS=true to avoid the ambient-logfire pydantic-plugin false positive"

patterns-established:
  - "Append-only content-keyed ID ledger as the single source of truth for human refs"
  - "Leaf-core module discipline: site.py imports only stdlib + pydantic + .semantic/.templates (lint-imports green)"
  - "TDD RED→GREEN with the load-bearing invariant encoded as test_reorder_and_insert_preserve_ids"

requirements-completed: [SITE-01]

# Metrics
duration: ~30min
completed: 2026-06-18
---

# Phase 8 Plan 01: Site Content Model & Stable IDs Summary

**Deterministic, AI-free identity core for the Library: a stdlib `slugify()`, an append-only `slug -> {ref,type,issue,date}` ledger (`content/rev1/ids.json`), and the typed `Site/Collection/Page` model with `from_surfaces`/`by_slug` — proven reorder/insert-stable by the L7 TDD test.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-06-18T10:30Z (approx)
- **Completed:** 2026-06-18T10:59:14Z
- **Tasks:** 2 (Task 1 was TDD: RED→GREEN)
- **Files modified:** 5 (4 created, 1 modified)

## Accomplishments
- Moved identity OUT of the presentation tier (`enumerate` in render.py) and INTO a deterministic core model — identity is now a pure function of content + the append-only ledger.
- Proved ROADMAP success criterion 2 with `test_reorder_and_insert_preserve_ids`: reverse the surface list + insert a brand-new report, rebuild against the same ledger → every pre-existing slug→ref is byte-identical, every link still resolves, the new report gets a fresh `R-005`.
- Seeded and committed `content/rev1/ids.json` from the real dogfood corpus, locking the Rev1 refs (R-001..R-004, EP01, A-001) before any future surface is added. Verified deterministic (re-seed is byte-identical).
- Zero new dependencies; `lint-imports` stays 1 kept / 0 broken; full suite 457 passed / 1 xfailed (up from 448 baseline, +9 new tests, no regression).

## Public API (for Plan 02 — renderer wiring)

`from newsletters import Site, Collection, Page, Ledger, slugify`

**`slugify(text: str) -> str`** — stdlib only (L4). NFKD ASCII-fold → lower → `re.sub(r"[^a-z0-9]+","-")` → `strip("-")`. Pure, no I/O. Output is restricted to `[a-z0-9-]` (no `/`, `.`, `\`, whitespace) → safe in `f"{slug}.html"` (closes T-08-01).

**`Ledger`** (the single reader/writer of `content/rev1/ids.json`):
- `Ledger.load(path) -> Ledger` — reads the JSON or starts empty.
- `ledger.ref_for(slug, kind, *, issue=None, date=None) -> str` — existing slug returns its recorded ref UNCHANGED (immutable; `kind` may be `None` for a read-only lookup of a known slug); a new sequential-type slug gets `max(per-type ordinal)+1` formatted per L1; a new newsletter (cadenced) is recorded with issue/date and an empty ref.
- `ledger.slugs() -> list[str]` (sorted), `ledger.entry(slug) -> dict | None`.
- `ledger.save()` — `json.dumps(_data, sort_keys=True, indent=2, ensure_ascii=False) + "\n"` (byte-stable, L5/T-08-03).

**`Page(BaseModel)`** (wraps a Surface): `slug, ref, title, kind, gate: ReviewState, signal_color: SignalColor, href, issue: int|None=None, date: date|None=None, surface: Surface`. `href == f"{slug}.html"`.

**`Collection(BaseModel)`**: `kind, display_name, pages: list[Page]`.

**`Site(BaseModel)`**: `collections: list[Collection]`.
- `Site.from_surfaces(surfaces, *, ledger) -> Site` (classmethod) — for each surface in input order: `slug = surface.id` (L3; `slugify(title)` only if id is not slug-clean), `ref = ledger.ref_for(slug, surface.kind)`, build a Page; group by kind into Collections ordered by `template.distance` (show 0, report 1, article 2, newsletter 3). **Pure given a ledger — does NOT call `ledger.save()`** (caller owns persistence).
- `site.pages() -> list[Page]` (flatten in collection order).
- `site.by_slug(slug) -> Page | None` — the L6 cross-link RESOLVER (resolver only; no anchor rendering — Phase 9).

## Ledger format, path & assignment algorithm

- **Path:** `content/rev1/ids.json` (beside the Rev1 rendered output it indexes).
- **Shape:** `{ slug: { "ref": str, "type": str, "issue": int|null, "date": str|null } }`, top-level keys sorted, trailing newline.
- **Assignment (append-only, deterministic):** load → for each surface in order: if slug present, read its ref (never recompute); else compute `n = max(trailing-digit ordinal of every entry whose type == kind) + 1` (default 1), format per L1, append. `max+1` not `count+1` (deletion never reuses a retired number, A4). Ordinals parsed with `re.search(r"(\d+)$", ref)` so both widths (`R-001`, `EP01`) work.

## Slugify rule (L4)

`unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode("ascii")` → `.lower()` → `re.sub(r"[^a-z0-9]+","-", ...)` → `.strip("-")`. No `python-slugify` dependency.

## Seeded refs (content/rev1/ids.json)

| slug | ref | type |
|------|-----|------|
| report-kickoff | R-001 | report |
| report-datamodel | R-002 | report |
| report-rev1 | R-003 | report |
| report-plan | R-004 | report |
| show-ep01 | EP01 | show |
| article-semantic-spine | A-001 | article |
| newsletter-jj | (empty — cadenced) | newsletter |
| newsletter-nate | (empty — cadenced) | newsletter |
| newsletter-newcomer | (empty — cadenced) | newsletter |

## Task Commits

1. **Task 1 (TDD RED): failing SITE-01 identity-core tests** — `d734f3b` (test)
2. **Task 1 (TDD GREEN): slugify + Ledger + Site/Collection/Page** — `1ceee08` (feat)
   - (plus `4ae9bc3` docs: log out-of-scope mypy errors to deferred-items)
3. **Task 2: seed committed ledger + export public API** — `c99f341` (feat)

**Plan metadata:** committed separately with STATE/ROADMAP/REQUIREMENTS updates.

## Files Created/Modified
- `src/newsletters/site.py` — slugify, Ledger, Site/Collection/Page, from_surfaces, by_slug (AI-free core).
- `tests/test_site.py` — 9 tests incl. the L7 stability proof.
- `content/rev1/ids.json` — seeded append-only ID ledger.
- `src/newsletters/__init__.py` — exports Site, Collection, Page, Ledger, slugify.
- `.planning/phases/08-site-content-model-stable-ids/deferred-items.md` — pre-existing out-of-scope mypy errors.

## Decisions Made
See `key-decisions` frontmatter. Notably: ledger at `content/rev1/ids.json`; L1 ref widths locked at seeding; `slug == Surface.id` for backward-compat; `from_surfaces` is a pure builder (no save side-effect).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] AI-free runtime test produced a logfire false positive**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** My initial `test_imports_are_ai_free` measured `sys.modules` IN-PROCESS after `import newsletters.site`. The dev `.venv` has ambient `logfire`, which pydantic auto-activates as a `pydantic`-group plugin on first model import — with NO import edge — so the in-process check flagged 66 logfire modules even though `site.py` has zero AI import edges (`lint-imports` confirms 1 kept / 0 broken, and `import newsletters.semantic` alone triggers the same logfire load). This is the documented blind spot in `.planning/notes/ai-optional-pydantic-plugin-leak.md`.
- **Fix:** Rewrote the test to measure in a FRESH subprocess with `PYDANTIC_DISABLE_PLUGINS=true` — the exact technique the canonical `tests/test_ai_optional.py` gates use — so it measures site.py's own import graph, not ambient plugins.
- **Files modified:** tests/test_site.py
- **Verification:** test passes; `lint-imports` 1 kept / 0 broken; the established `test_no_ai_pydantic_plugin_active` (the canonical plugin-leak guard) is unaffected.
- **Committed in:** 1ceee08 (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug, in my own test, not in shipped src).
**Impact on plan:** No scope creep; the fix aligns the new test with the repo's established AI-isolation measurement pattern.

## Issues Encountered
- **Pre-existing mypy errors (out of scope).** `mypy src/newsletters` reports 12 errors, ALL in untouched files (render.py, capture.py, dogfood.py), verified present on clean HEAD before site.py existed. `mypy src/newsletters/site.py` → "Success: no issues found". Logged to `deferred-items.md`; NOT fixed (executor scope boundary). Recommend a dedicated typing-cleanup task.
- During the pre-existing-error verification I used `git stash`. This is the MAIN working tree (not a Claude Code worktree — `.git` is a directory, `refs/stash` is local), so the shared-stash hazard did not apply; the stash popped cleanly and the working tree was verified intact. Avoided thereafter.

## TDD Gate Compliance
- RED gate present: `d734f3b` (`test(08-01)`) — tests failed on missing module before implementation.
- GREEN gate present: `1ceee08` (`feat(08-01)`) after RED.
- No REFACTOR commit — implementation was clean as written; none needed.

## Gate Results (re-run independently)
- `pytest tests/test_site.py -q` → **9 passed** (incl. test_reorder_and_insert_preserve_ids).
- `pytest -q` → **457 passed, 1 xfailed** (baseline 448 + 9 new; no regression).
- `lint-imports` → **1 kept, 0 broken** (site.py AI-free; no distill/AI edge).
- `mypy src/newsletters/site.py` → **Success, no issues**. (`mypy src/newsletters` shows 12 PRE-EXISTING errors in other files — deferred.)
- Fresh interpreter: `python -c "import newsletters; import newsletters.site"` → **exit 0**.
- Ledger seeded refs verified: R-001 / EP01 / A-001; sorted; newline-terminated; re-seed byte-identical (deterministic).

## Next Phase Readiness
- **Ready for Plan 08-02** (wire render.py to be Page-driven, replace the `enumerate` numbering with `Page.ref`, keep `{slug}.html` hrefs; update the spec with the L1 ID convention). The public API + ledger format + slugify rule + seeded refs are all documented above.
- **Out of scope (Phase 9/10), deliberately not built:** nav, real Home, gate-state kanban board, clickable fan-out anchors. `by_slug` is the resolver only.

## Known Stubs
None. The model is fully wired to the real dogfood corpus; the ledger is seeded from real surfaces, not mock data. (Newsletters carry an empty `ref` by design — cadence/issue is their identity, not a sequential ordinal — this is intentional per L1, not a stub.)

## Self-Check: PASSED
- Files: src/newsletters/site.py, tests/test_site.py, content/rev1/ids.json, 08-01-SUMMARY.md — all FOUND.
- Commits: d734f3b (RED), 1ceee08 (GREEN), c99f341 (Task 2) — all FOUND.

---
*Phase: 08-site-content-model-stable-ids*
*Completed: 2026-06-18*
