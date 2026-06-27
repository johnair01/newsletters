---
phase: 12-learning-onboarding-surface
plan: 01
subsystem: api
tags: [pydantic, surface-template, glossary, faithfulness, learning-surface]

# Dependency graph
requires:
  - phase: 02-typed-semantic-model
    provides: "Surface / SurfaceTemplate / Claim / Trace / Block discriminated union"
  - phase: 08-site-ledger
    provides: "Site.from_surfaces + Ledger with the kind-generic L-{:03d} learning ref format"
provides:
  - "The 5th `learning` SurfaceTemplate (registered, distance=4) flowing through Site/ledger as L-NNN with zero site.py edits"
  - "Typed GlossaryTerm + GlossaryBlock — a glossary definition is a traced Claim, never a str (faithfulness in the type system)"
  - "GlossaryBlock added to the Block discriminated union (kind=glossary), round-trips via model_dump_json"
affects: [12-03-learning-preset, 12-04-render, 12-02-spec]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Faithfulness-by-type: a teaching artifact's definition field is typed Claim (carries evidence: list[Trace]), so invented prose literally cannot be constructed"
    - "5th surface as pure config: a new reader surface is a SurfaceTemplate in _REGISTRY; the Site/ledger/board wiring is kind-generic and picks it up unchanged"

key-files:
  created:
    - tests/test_learning.py
  modified:
    - src/newsletters/templates.py
    - src/newsletters/semantic.py

key-decisions:
  - "LEARNING added to the _REGISTRY tuple (not register()) so all_templates() stays deterministic and built-in; register() stays for operator templates"
  - "GlossaryTerm.definition is a Claim (the DEFINING claim — its evidence IS the definition); an un-traceable term is NOT glossed (routed to missing[] by the Plan-03 preset), never a string gloss"
  - "No render branch for GlossaryBlock here — that is Plan 04; semantic.py keeps its stdlib+pydantic+leaf import boundary"

patterns-established:
  - "Faithfulness enforced at construction time via the type, asserted by a ValidationError test on a str definition"

requirements-completed: [LEARN-01]

# Metrics
duration: 3min
completed: 2026-06-19
---

# Phase 12 Plan 01: Learning Template + Typed GlossaryBlock Summary

**The 5th `learning` SurfaceTemplate (registered, distance=4, flows through Site/ledger as L-001 with no site.py edit) plus a typed GlossaryBlock whose every term's definition is a traced Claim — faithfulness locked into the schema before any preset/render logic exists.**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-06-19T05:09:51Z
- **Completed:** 2026-06-19T05:13Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments
- Added the `learning` SurfaceTemplate as the 5th preset; `all_templates()` now returns 5, ordered by distance, learning last (distance=4).
- Confirmed (by test) a learning Surface lands in its own Collection with ledger ref `L-001` via the kind-generic Site/ledger wiring — zero `site.py` edits.
- Added typed `GlossaryTerm` + `GlossaryBlock`: a glossary definition is a `Claim` (carrying `evidence: list[Trace]`), never a bare `str`. A str definition raises `ValidationError`.
- `GlossaryBlock` added to the `Block` discriminated union (`kind="glossary"`); round-trips through `model_dump_json()`/`model_validate_json()` preserving the traced definition.

## Task Commits

Each task committed atomically (TDD; commit + push after each):

1. **RED scaffold (both tasks):** `3f706ad` (test) — failing tests for the learning template + GlossaryBlock
2. **Task 1: learning SurfaceTemplate (L1)** — `aa47402` (feat)
3. **Task 2: typed GlossaryBlock (L2)** — `b9b3777` (feat)

_No REFACTOR commit needed — GREEN implementations were minimal and clean._

## Files Created/Modified
- `tests/test_learning.py` — 4 tests: template fields match the locked decision; template registered + lands in Site as L-001; definition rejects a str / accepts a traced Claim; GlossaryBlock in the union round-trips.
- `src/newsletters/templates.py` — `LEARNING = SurfaceTemplate(...)` constant; added to the `_REGISTRY` tuple.
- `src/newsletters/semantic.py` — `GlossaryTerm` + `GlossaryBlock` models; `GlossaryBlock` appended to the `Block` union.

## Downstream contract (for Waves 2/3 — Plans 03/04)

**The `learning` SurfaceTemplate fields (templates.py):**
| field | value |
|-------|-------|
| `name` | `"learning"` |
| `display_name` | `"Learning"` |
| `tagline` | `"the newcomer re-cut — every concept traced to its record"` |
| `cadence` | `Cadence.ON_DEMAND` |
| `personalized` | `True` |
| `signal_color` | `SignalColor.GREEN` |
| `scope` | `AudienceScope.INDIVIDUAL` |
| `review_policy` | `ReviewPolicy.light()` |
| `slots` | `["start_here", "prerequisites", "glossary", "going_deeper"]` |
| `distance` | `4` |

Resolve via `get_template("learning")`. Ledger ref format `L-{:03d}` already exists (site.py); first learning surface gets `L-001`.

**The GlossaryBlock / GlossaryEntry shape (semantic.py) — the traced-Claim-definition contract:**
```python
class GlossaryTerm(BaseModel):
    term: str
    definition: Claim          # the DEFINING traced claim — NOT a str, NOT invented prose

class GlossaryBlock(BaseModel):
    kind: Literal["glossary"] = "glossary"
    heading: Optional[str] = "Glossary — every term traced to its definition"
    terms: list[GlossaryTerm] = Field(default_factory=list)
```
- **Plan 03 (preset):** emit `GlossaryBlock(terms=[GlossaryTerm(term=..., definition=<a reviewed traced Claim>)])`. A term whose defining claim cannot be traced MUST be routed to `surface.missing[]` (honesty panel) — never glossed with a string. (Note: the entry type is named `GlossaryTerm`, not `GlossaryEntry`.)
- **Plan 04 (render):** add the render branch for `kind == "glossary"` (deliberately NOT added here). The block is already in the union and round-trips; reuse the Phase 9–11 `link_for_source` / `_claim_*` provenance devices on each term's `definition` Claim (LEARN-02).

## Decisions Made
- Added `LEARNING` to the `_REGISTRY` built-in tuple rather than calling `register()`, so `all_templates()` stays deterministic and the built-in style is preserved; `register()` remains for operator templates.
- `GlossaryTerm.definition` is typed `Claim` (not `str`, not a new wrapper) — the defining claim's evidence IS the definition. This is the LEARN-01 faithfulness crux, enforced at construction and asserted by a `ValidationError` test.
- No render logic and no `site.py` change — strictly the typed config + model, as the plan scoped.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Verification (re-run independently per CLAUDE.md, actual output)
- `pytest tests/test_learning.py -q` → **4 passed**
- `pytest -q` (full) → **541 passed, 1 xfailed** (537 baseline + 4 new; no regressions)
- `mypy src/newsletters` → **12 errors, all pre-existing** in dogfood.py/locators; **0 in templates.py or semantic.py** (confirmed by grep)
- `lint-imports` → **1 contract kept, 0 broken** (core never imports AI; semantic.py keeps its leaf boundary)
- fresh import `get_template('learning').display_name` → **`Learning`**

## Next Phase Readiness
- LEARN-01 foundation complete: the typed config + traced-glossary contract is the spine Plans 03 (preset) and 04 (render) build against.
- No blockers. Zero new dependency. The faithfulness guarantee (definition = traced Claim) is locked in the type system.

## Self-Check: PASSED
- All created/modified files exist on disk (tests/test_learning.py, templates.py, semantic.py, 12-01-SUMMARY.md).
- All task commits exist in git history (3f706ad test, aa47402 feat L1, b9b3777 feat L2).

---
*Phase: 12-learning-onboarding-surface*
*Completed: 2026-06-19*
