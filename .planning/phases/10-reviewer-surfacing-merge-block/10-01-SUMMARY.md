---
phase: 10-reviewer-surfacing-merge-block
plan: 01
subsystem: provenance
tags: [merge-block, faithfulness, stale, review-gate, pydantic, ai-optional]

# Dependency graph
requires:
  - phase: 03-distill-socket
    provides: "Claim.is_stale / Trace.from_source / SpanContainmentFaithfulness.entails / Distillation.missing"
  - phase: 01-foundation
    provides: "Surface model + Review gate (no-auto-publish, ReviewState)"
provides:
  - "Surface.missing: list[str] carrier (optional, additive, invariant-3-safe)"
  - "src/newsletters/review.py — BlockerKind + Blocker + review_blockers(surface, sources)"
  - "Published-only merge-block scope (Draft/In-Review exempt)"
  - "Three proven gate-fires negatives (STALE / UNENTAILED / OPEN_MISSING)"
affects: [10-02 (CLI newsletters check + CI job imports review_blockers), 10-03 (renderer uses Surface.missing + faithfulness predicate)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One-trust-rule-one-place: review_blockers reuses is_stale + entails, derives no new trust logic"
    - "Published-only checker scope: publication is the trust boundary"
    - "STALE-first elif-guard: a drifted addressed claim reports the truer STALE diagnosis, never double-reported"
    - "Prove-the-gate-fires: crafted negative fixtures, never clean-only testing (Phase-7 lesson)"

key-files:
  created:
    - src/newsletters/review.py
    - tests/test_review.py
  modified:
    - src/newsletters/semantic.py

key-decisions:
  - "Surface.missing is additive only — it never touches the publish/review gate (invariant 2 unchanged)"
  - "review.py is a top-level sibling of render.py, NOT inside distill/ (which stays modality-agnostic)"
  - "Blocker.locator carries the first trace's source_id; detail = claim.text[:80] for claim blockers, verbatim entry for OPEN_MISSING"
  - "review.py imports only .semantic + .distill.faithfulness (both AI-free), keeping lint-imports green"

patterns-established:
  - "Pure AI-free checker function as the single CLI+CI trust entrypoint"
  - "Inline negative fixtures in tests/ (never poison the dogfood corpus)"

requirements-completed: [PROV-04]

# Metrics
duration: 5min
completed: 2026-06-18
---

# Phase 10 Plan 01: The merge-block CHECKER core Summary

**Deterministic, AI-free `review_blockers()` that blocks any PUBLISHED surface carrying a STALE, un-entailed, or open-`missing[]` claim — proven to FIRE by three crafted negative fixtures — plus the additive `Surface.missing` carrier.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-06-18T12:44:10Z
- **Completed:** 2026-06-18T12:48:34Z
- **Tasks:** 3
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments
- Added the optional, invariant-3-safe `Surface.missing: list[str]` carrier — the surface-level mirror of `Distillation.missing`, defaulting to `[]` (backward-compat) and leaving the publish gate untouched.
- Built `src/newsletters/review.py`: `BlockerKind` (`stale`/`unentailed`/`open_missing`), the `Blocker` model, and the pure `review_blockers(surface, sources) -> list[Blocker]` — published-only scope, STALE-first elif, reusing `Claim.is_stale` + `SpanContainmentFaithfulness().entails` with zero new trust logic.
- Proved the gate FIRES with three crafted PUBLISHED negatives (STALE / UNENTAILED / OPEN_MISSING), plus Draft/In-Review exemption, a clean-published-returns-`[]` test, and a subprocess no-AI-import guard — 11 tests total, all green.

## Task Commits

Each task was committed atomically (TDD) and pushed:

1. **Task 1: Add the optional Surface.missing carrier (L1)** — `a8f4359` (feat)
2. **Task 2: Build review.py — Blocker + review_blockers (L2, L3)** — `d5e35d2` (feat)
3. **Task 3: Prove the gate FIRES — three PUBLISHED negatives + no-AI guard (L7)** — `6d13b3a` (test)

## Files Created/Modified
- `src/newsletters/semantic.py` — added `Surface.missing: list[str] = Field(default_factory=list)` near `traces`/`audience_label` (additive, invariant-3-safe carrier; no gate change).
- `src/newsletters/review.py` (new) — `BlockerKind` + `Blocker` + `review_blockers()`; the single AI-free trust entrypoint the CLI (10-02) and renderer (10-03) reuse.
- `tests/test_review.py` (new) — carrier round-trip/backward-compat (Task 1) + the gate-fires negatives, exemptions, clean case, and no-AI guard (Task 3).

## The checker API (for Wave 2 — 10-02 CLI/CI, 10-03 renderer)

**`Surface.missing: list[str]`** — optional, default `[]`. Plain-string carrier of unsubstantiated material to show the reviewer; the surface-level mirror of `Distillation.missing`. Additive — does NOT alter the publish/review gate. Invariant-3-safe (no Corpus/Source object).

**`from newsletters.review import BlockerKind, Blocker, review_blockers`**

- `BlockerKind(StrEnum)`: `STALE="stale"`, `UNENTAILED="unentailed"`, `OPEN_MISSING="open_missing"`.
- `Blocker(surface_id: str, kind: BlockerKind, detail: str, locator: str = "")` — Pydantic model. `detail` = `claim.text[:80]` for claim blockers, the verbatim entry for OPEN_MISSING. `locator` = the first trace's `source_id` (claim blockers) or `""`.
- `review_blockers(surface: Surface, sources: dict[str, Source] | None = None) -> list[Blocker]`:
  - **Published-only (L3):** returns `[]` immediately when `not surface.is_published`.
  - When `sources is None`, self-builds `{s.id: s for s in surface.traces}`.
  - Collects claims from every `ClaimsBlock` in `surface.blocks`. For each claim: **STALE first** (`claim.is_stale(sources)` -> STALE blocker), **`elif`** `not SpanContainmentFaithfulness().entails(claim)` -> UNENTAILED blocker (so a drifted addressed claim is never double-reported).
  - Then one OPEN_MISSING blocker per `surface.missing` entry.
  - PURE: never mutates the surface, never routes to `missing[]` (that is `route_unfaithful_to_missing`'s job at the distill boundary).

**How each blocker kind is detected (for CLI + renderer to reuse):**
- **STALE** — `claim.is_stale(sources)` is True (a trace's pinned `content_hash` != the live `source.content_hash()`).
- **UNENTAILED** — `SpanContainmentFaithfulness().entails(claim)` is False (addressed trace whose normalized span omits the normalized claim text; un-addressed Rev1 traces pass structurally).
- **OPEN_MISSING** — `surface.missing` is non-empty on a published surface.

## Actual gate output (re-run independently via `.venv/bin/python`)

- `pytest tests/test_review.py -q` → **11 passed** (3 negatives + draft/in-review exempt + clean + no-AI guard + 4 carrier tests).
- `pytest -q` → **513 passed, 1 xfailed** (baseline was 502 passed, 1 xfailed; +11 new; no regression — no-auto-publish + provenance tests stay green).
- `mypy src/newsletters` → **12 errors, all pre-existing** in `capture.py`/`dogfood.py`/`render.py` (the documented baseline). `mypy src/newsletters/review.py src/newsletters/semantic.py` → **Success: no issues found** (both typed clean).
- `lint-imports` → **1 contract kept, 0 broken** (review.py is AI-free).
- `python -c "import newsletters; import newsletters.review"` → **exit 0**; core stays AI-free (langchain/langgraph/langsmith/pydantic_ai/openai/anthropic absent).

## The three proven blockers (L7 — gate FIRES)
1. **STALE** — mint `Trace.from_source(src, 0, len(transcript))`, publish, then mutate `src.transcript` so the live hash drifts → exactly one `Blocker(kind=STALE)`.
2. **UNENTAILED** — an addressed trace over a transcript that does NOT contain the claim text → exactly one `Blocker(kind=UNENTAILED)`.
3. **OPEN_MISSING** — a published surface with `missing=[...]` → one `Blocker(kind=OPEN_MISSING)` per entry.
Plus: the same defects on a Draft and an In-Review surface return `[]` (published-only scope); a clean published surface returns `[]`.

## Decisions Made
- None beyond the plan/CONTEXT-locked choices (L1/L2/L3/L7). `Field` was dropped from the review.py imports after switching `Blocker` to plain attributes (lint-clean) — a trivial tidy, not a behavior change.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## Known Stubs
None. `Surface.missing` is an intentional carrier that later plans populate at the capture/promote seam (documented in its field docstring); it is not a UI-facing stub.

## User Setup Required
None - no external service configuration required. Zero new dependency.

## Next Phase Readiness
- **10-02** can import `review_blockers` for the `newsletters check` CLI (exit nonzero on any blocker) and the CI merge-block job.
- **10-03** can read `Surface.missing` for the amber "what's not here / not verified" panel and reuse `SpanContainmentFaithfulness().entails` / `Claim.is_stale` for the inline STALE/unfaithful badges.
- The trust core is a single pure function — both consumers reuse it rather than re-deriving trust logic.

## Self-Check: PASSED
- FOUND: src/newsletters/review.py
- FOUND: tests/test_review.py
- FOUND: .planning/phases/10-reviewer-surfacing-merge-block/10-01-SUMMARY.md
- FOUND: Surface.missing field in semantic.py
- FOUND commits: a8f4359, d5e35d2, 6d13b3a

---
*Phase: 10-reviewer-surfacing-merge-block*
*Completed: 2026-06-18*
