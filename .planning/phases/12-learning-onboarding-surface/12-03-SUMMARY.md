---
phase: 12-learning-onboarding-surface
plan: 03
subsystem: api
tags: [pydantic, learning-surface, faithfulness, glossary, onboarding-path, progressive-disclosure]

# Dependency graph
requires:
  - phase: 12-learning-onboarding-surface
    plan: 01
    provides: "learning SurfaceTemplate (LEARNING, distance=4) + typed GlossaryBlock/GlossaryTerm (definition = traced Claim)"
  - phase: 02-typed-semantic-model
    provides: "Surface / Distillation / Claim / Trace / claims_for / Corpus.emphasis / ClaimsBlock / Lineage / Review gate"
provides:
  - "learning_surface() — the FAITHFUL newcomer re-cut: selects/orders/links existing traced claims into three deterministic layers; emits only ClaimsBlock + GlossaryBlock; returns a Draft"
  - "Glossary builder: each requested term resolves to its DEFINING traced Claim; un-glossable terms route to surface.missing[] (never fabricated)"
  - "OnboardingPath / OnboardingStep — typed ordered slug refs (navigation over already-gated surfaces); NOT a Surface, no review gate"
affects: [12-04-render, 12-05-dogfood]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Faithfulness-by-construction in logic: the preset only re-arranges existing Claim.text / traced defining Claims — asserted by a set-membership test (every rendered string ∈ source claims) and the no-ProseBlock assertion"
    - "Deterministic layering via a pure function of (topics, confidence) over the already-total+stable claims_for() order — same input, same layer assignment, byte-stable"
    - "Un-resolvable concept → honesty panel (missing[]), never invented — the defining-claim matcher (_defines) refuses a mere mention"

key-files:
  created:
    - src/newsletters/learning.py
  modified:
    - tests/test_learning.py

key-decisions:
  - "Section routing is topic-first (onboarding/vision/prereq/foundation -> Prerequisites; deep/advanced/detail -> Going deeper) with a confidence>=0.7 fallback for Start here — derived from existing fields (A3), no schema change, fully deterministic"
  - "Within a layer, claim order == claims_for(audience) order (already a total+stable key), so layering is reproducible without a re-sort"
  - "Glossary resolution = first traced claim whose text reads 'term is/are/means/refers to ...' (a DEFINING statement); a claim that only mentions the term is refused, so the term falls through to missing[]"
  - "OnboardingPath co-located with the preset in one cohesive learning.py (the plan objective itself directs 'a NEW cohesive module'); it is a plain BaseModel with no review/publish/claims — navigation, not a Surface (A5)"
  - "prerequisites carried as Lineage.derived_from (slug refs), NOT as new exposition — Plan 04 resolves them via Site.by_slug"

patterns-established:
  - "A teaching preset that cannot invent: the no-invented-prose test is set-membership of every rendered string in the source claims + a zero-ProseBlock assertion"

requirements-completed: [LEARN-01, LEARN-02, LEARN-03]

# Metrics
duration: 5min
completed: 2026-06-19
---

# Phase 12 Plan 03: Faithful learning_surface() preset + OnboardingPath model Summary

**`learning_surface()` re-cuts a reviewed `Distillation` into a newcomer surface by SELECTING, ORDERING, and LINKING existing traced claims into three deterministic layers (Start here / Prerequisites / Going deeper) plus a traced-definition glossary — it cannot invent prose (proven by set-membership), routes un-glossable terms to `missing[]`, and returns a Draft; `OnboardingPath`/`OnboardingStep` are typed ordered slug refs that are NOT a Surface and carry no review gate.**

## Performance
- **Duration:** ~5 min
- **Started:** 2026-06-19T05:18:26Z
- **Completed:** 2026-06-19T05:23Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 2 (1 created: src/newsletters/learning.py; 1 modified: tests/test_learning.py)

## Accomplishments
- **LEARN-01 (logic):** `learning_surface()` re-cuts a reviewed record into ordered Start here / Prerequisites / Going deeper layers built from existing traced claims — no invented prose; deterministic layering keyed by `topics` + `confidence` over the `claims_for(audience)` order.
- **LEARN-02 (logic):** the in-context glossary's definitions are traced `Claim`s (the defining claim's evidence IS the definition); un-traceable terms route to `surface.missing[]`, never fabricated. The faithfulness boundary is proven NEGATIVELY: `"Flux"` is mentioned but never defined → it is absent from the GlossaryBlock and present in `missing[]`.
- **LEARN-03 (model):** `OnboardingPath(id, title, audience_label, steps=[OnboardingStep(slug, label)])` — an ordered list of slug refs; it is NOT a Surface (`isinstance(path, Surface) is False`), has no `review`/`publish`/`claims`, and preserves step order. `render_path()` is deferred to Plan 04.
- `learning.py` is import-clean (stdlib + pydantic + `.semantic`/`.templates` only — AI-free, acyclic); full suite green; no new mypy errors; zero new dependency.

## Task Commits
Each task committed atomically (TDD; commit + push after each):
1. **RED scaffold (both tasks):** `cc5d14d` (test) — failing tests for the faithful preset + OnboardingPath
2. **GREEN — learning_surface preset + glossary builder (L2) + OnboardingPath/OnboardingStep models (L4):** `61e429b` (feat)

_No REFACTOR commit needed — the GREEN implementation was minimal and clean (one mypy invariance fix folded in before commit: annotated `blocks` as `list[Block]`)._

## Files Created/Modified
- `src/newsletters/learning.py` (created) — `learning_surface()` preset + `_layer_for`/`_defines` helpers + `OnboardingStep`/`OnboardingPath` models. Imports stdlib + pydantic + `.semantic`/`.templates` only.
- `tests/test_learning.py` (modified) — added 6 logic tests: faithful-no-invented-prose, deterministic disclosure, glossary-defs-traced, un-glossed→missing[], onboarding-path-ordered-not-a-surface, onboarding-step-slug+optional-label.

## Downstream contract (for Wave 3 — Plan 04 render, and Wave 4 — Plan 05 dogfood)

**`learning_surface()` signature:**
```python
def learning_surface(
    distillation: Distillation,
    *,
    surface_id: str,
    title: str,
    audience: Corpus | None = None,
    glossary_terms: list[str] | None = None,
    prerequisites: list[str] | None = None,
    author: str | None = None,
    eyebrow: str = "",
) -> Surface
```
- Returns a **Draft** `Surface` bound to the `learning` template (`template.name == "learning"`). The caller publishes (no auto-publish).
- **Blocks emitted (in slot order):** `ClaimsBlock(heading="Start here")`, `ClaimsBlock(heading="Prerequisites")`, `GlossaryBlock`, `ClaimsBlock(heading="Going deeper")` — empty `ClaimsBlock` layers are omitted; the `GlossaryBlock` is always emitted (so the honesty-panel slot is visible). NO `ProseBlock`.
- **Section-ordering rule (deterministic, `_layer_for`):** a claim's layer is a pure function of its fields — `topics ∩ {onboarding, vision, prerequisite(s), prereq, foundation}` → **Prerequisites**; `topics ∩ {deep, deeper, advanced, detail, appendix}` → **Going deeper**; else `confidence >= 0.7` → **Start here**; else → **Going deeper**. Within a layer the order is the `claims_for(audience)` order (already total+stable), so the assignment is byte-stable.
- **Glossary resolution (`_defines`):** for each requested term, the definition is the FIRST traced claim (in `claims_for` order) whose text contains `"{term} is|are|means|refers to ..."`. A claim that merely mentions the term does NOT qualify.
- **Un-glossable term routing:** a requested term with no defining traced claim is appended to `surface.missing[]` as `"Glossary term '{term}' has no traceable defining claim"` — NEVER glossed. (Render reuses the Phase 9–11 honesty panel.)
- **prerequisites:** carried as `surface.lineage.derived_from` (slug refs) — Plan 04 resolves each via `Site.by_slug` and links to the prerequisite record. NOT new exposition.

**`OnboardingPath` / `OnboardingStep` (models):**
```python
class OnboardingStep(BaseModel):
    slug: str          # required — the cross-link key resolved via Site.by_slug (Plan 04)
    label: str = ""    # optional; render resolves the title from the target page when ""

class OnboardingPath(BaseModel):
    id: str
    title: str
    audience_label: str = "A new contributor"
    steps: list[OnboardingStep] = Field(default_factory=list)   # list ORDER = track order
```
- The path is **navigation over already-gated surfaces**: NO `review`, NO `publish()`, NO claims of its own. `render_path()` (Plan 04) resolves each step via `Site.by_slug` and reuses the Phase-9 `_prevnext` device.

## Decisions Made
- **Topic-first routing with a confidence fallback** keeps layering deterministic and derived from existing fields (no schema change, A3). Documented the exact topic sets above so Plan 05's dogfood can author claims that land in the intended layers.
- **`_defines` requires a copula** (`is`/`are`/`means`/`refers to`) so a claim that only *mentions* a term cannot mis-gloss it — this is what makes the un-glossable→`missing[]` path real and testable (proven with `"Flux"`).
- **Both L2 (preset) and L4 (models) landed in one `learning.py`** — the plan objective itself directs "a NEW cohesive module"; the OnboardingPath models are tiny typed data and naturally co-locate with the preset that a track sequences. (See Deviations.)

## Deviations from Plan
### Process deviations (no user permission needed)

**1. [Process] Task 1 and Task 2 GREEN committed in a single feat commit (`61e429b`)**
- **Found during:** Task 2.
- **Issue:** The plan lists Task 1 (preset) and Task 2 (OnboardingPath models) as two TDD tasks, both touching the same new file `learning.py`. The cohesive-module write (per the plan's own objective: "a NEW cohesive module") placed both in one file; the models are tiny pure-data BaseModels.
- **Resolution:** One RED commit (`cc5d14d`) covered both tasks' tests; one GREEN feat commit (`61e429b`) landed the whole module. Splitting a single file's first commit into two artificial partial-stages would add churn without value. Both tasks' done-criteria and verify commands were run and pass independently.
- **Files:** `src/newsletters/learning.py`, `tests/test_learning.py`. **Commit:** `61e429b`.

**2. [Rule 3 - Blocking] Annotated `blocks` as `list[Block]` to satisfy mypy invariance**
- **Found during:** Task 1 GREEN gate (mypy).
- **Issue:** `blocks: list[ClaimsBlock | GlossaryBlock]` triggered a NEW mypy error at the `Surface(blocks=...)` call (list invariance vs. the full `Block` union) — one error over the 12-error baseline.
- **Fix:** imported `Block` from `.semantic` and annotated `blocks: list[Block]`. mypy back to 12 errors (0 in learning.py).
- **Files:** `src/newsletters/learning.py`. **Folded into commit:** `61e429b`.

**3. [Rule 1 - Bug] Removed a broken line in the test fixture**
- **Found during:** Task 1 GREEN (first test run).
- **Issue:** the `_record()` fixture had a leftover `sources = [t.evidence[0] for ...]` line treating a `Trace` as if it had `.evidence` (it doesn't) → `AttributeError`.
- **Fix:** removed the dead line (the `srcs` list already builds the `traces`).
- **Files:** `tests/test_learning.py`. **Folded into commit:** `61e429b`.

## Issues Encountered
None beyond the deviations above.

## User Setup Required
None — no external service configuration, zero new dependency.

## Known Stubs
None. `render_path()` and the GlossaryBlock/learning render branches are deliberately deferred to Plan 04 (documented above and in 12-01-SUMMARY), not stubs — the logic this plan owns is complete and tested.

## Verification (re-run independently per CLAUDE.md — actual output)
- `pytest tests/test_learning.py -x -q` → **10 passed** (4 from Plan 01 + 6 new logic tests)
- `pytest -q` (full) → **547 passed, 1 xfailed** (baseline 541+1; +6 new; **0 regressions**)
- `mypy src/newsletters` → **12 errors in 3 files** (capture.py/dogfood.py/render.py — all pre-existing; **0 in learning.py**)
- `lint-imports` → **1 contract kept, 0 broken** (core never imports AI; learning.py keeps the stdlib+pydantic+sibling boundary)
- `pytest tests/test_ai_optional.py -x -q` → **15 passed, 1 xfailed** (no AI import reachable from core after adding learning.py)
- `python -c "import newsletters; import newsletters.learning"` → **exit 0** (acyclic, AI-free)

## The proven faithfulness negative
`test_unglossed_term_routes_to_missing`: the fixture's claim `"We later migrated Flux jobs onto the shared runner."` MENTIONS `"Flux"` but does not DEFINE it. The preset's `_defines` (requires a copula) refuses it → `"Flux"` is absent from the `GlossaryBlock` and present in `surface.missing[]`. `test_learning_surface_is_faithful_no_invented_prose` proves the positive: every rendered string (each ClaimsBlock claim text + each GlossaryTerm definition text) is set-member of the source Distillation's claim texts, and zero `ProseBlock` is emitted.

## Next Phase Readiness
- LEARN-01/02/03 logic complete: the preset + path are the spine Plan 04 (render the learning surface + GlossaryBlock + `render_path`) and Plan 05 (dogfood a real re-cut + a ≥2-record path) build against. Signatures + the section-ordering rule + the missing[]-routing contract are documented above for those waves.
- No blockers. Zero new dependency. The faithfulness guarantee is now enforced in LOGIC (set-membership + no-ProseBlock), complementing the type-level guarantee from Plan 01.

## Self-Check: PASSED
- `src/newsletters/learning.py` exists on disk; `tests/test_learning.py` modified.
- Both task commits exist in git history (`cc5d14d` test RED, `61e429b` feat GREEN), pushed to origin.

---
*Phase: 12-learning-onboarding-surface*
*Completed: 2026-06-19*
