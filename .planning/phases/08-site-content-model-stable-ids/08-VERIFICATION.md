---
phase: 08-site-content-model-stable-ids
status: passed
score: 2/2 success criteria verified (SITE-01)
verified_by: orchestrator (independent gate re-run + live stability probe, not trusted from SUMMARYs)
date: 2026-06-18
---

# Phase 8 Verification — Site Content Model & Stable IDs

**Status: PASSED** (2/2 success criteria). Verified by independently re-running gates + a live
reorder/insert probe against the built code, not by trusting the executor SUMMARYs.

## Success criteria
1. **`Site/Collection/Page` model with stable per-surface IDs generated from content, not position** —
   ✅ `src/newsletters/site.py`: typed Pydantic `Site/Collection/Page`; `slugify` (stdlib NFKD fold,
   probed `"Rev1 — café & Co!!" → "rev1-cafe-co"`); append-only `Ledger` at `content/rev1/ids.json`.
   Live probe: refs are `R-001..R-004` (reports), `EP01` (show), `A-001` (article) — per-type,
   content-derived, matching the locked L1 convention + the REQUIREMENTS examples.
2. **Insert/reorder does not change any existing ID or break cross-links** — ✅ Independent probe:
   built the Site, reversed the surface list + inserted a new surface, rebuilt against the same
   ledger → every pre-existing `slug→ref` byte-identical, new surface got a fresh per-type ref.
   Encoded as `tests/test_site.py::test_reorder_and_insert_preserve_ids` (the literal criterion-2
   proof) + `test_existing_links_do_not_rot`. The positional rot point (`enumerate`/`{i:02d}` at the
   old `render.py:373/376`) is removed — the Library now renders `Page.ref`.

## Hard rules
- **Specs are source of truth** — ✅ the convention was a SPEC GAP (zero prior matches); filled IN THIS
  PHASE: `docs/surfaces.md` (ID-convention table) + `docs/architecture.md` (Site→Collection→Page model
  + append-only ledger + position-independence guarantee). No silent drift.
- **Typed everything / AI-optional** — ✅ `site.py` imports only stdlib + Pydantic + siblings;
  `lint-imports` 1 kept/0 broken; `mypy src/newsletters/site.py` clean.
- **Determinism** — ✅ IDs are a pure function of content + the append-only ledger; rebuild leaves
  `content/rev1/ids.json` and all 10 `content/rev1/site/*.html` filenames byte-identical (only the
  Library `index.html` visible labels changed `01..07` → `R-001`/`EP01`/… — the intended fix).

## Gates (orchestrator re-run, actual)
- `pytest -q` → 458 passed, 1 xfailed. `tests/test_site.py` → 10 passed.
- `lint-imports` → 1 kept, 0 broken. `mypy site.py` → clean. `newsletters build` → renders; filenames byte-stable.

## Gaps / notes
- None blocking. The typed-`Trace.locator` forward note (Phases 4–7) and pre-existing mypy errors in
  `render.py`/`capture.py`/`dogfood.py` (logged `deferred-items.md`, genuinely pre-existing) remain
  out of scope. Clickable fan-out anchors + real Home/nav/gate-state board are correctly deferred to
  Phase 9/10 (L6 scope held — `Collection` groups by type only; `Page.gate` merely carried).
