---
phase: 12-learning-onboarding-surface
plan: 02
subsystem: docs
tags: [surfaces-spec, learning, onboarding-path, faithfulness, provenance, glossary]

# Dependency graph
requires:
  - phase: 08-site-collection-page
    provides: "the L-NNN Learning id convention + the ID-conventions table in docs/surfaces.md"
  - phase: 09-11-renderer-provenance
    provides: "the provenance devices (link_for_source, honesty panel, claim-beside-trace, prev/next) the learning spec reuses"
provides:
  - "docs/surfaces.md Learning-surface spec section (faithfulness contract, three progressive-disclosure layers, traced glossary, prerequisite links, LEARN-02 provenance, GREEN/L-NNN/distance-4 placement)"
  - "docs/surfaces.md OnboardingPath spec (ordered track, prev/next, NOT a Surface, no own review gate)"
affects: [12-01-learning-foundation, learning-preset, learning-renderer, learning-dogfood]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Specs-as-source-of-truth: the spec lands in the same phase as the implementing code (CLAUDE.md), so later plans implement against it without drift."

key-files:
  created: []
  modified:
    - "docs/surfaces.md - added the Learning + OnboardingPath spec section between The Report and the review-view section"

key-decisions:
  - "The learning re-cut SELECTS/ORDERS/LINKS already-reviewed traced claims; it never authors new factual prose (the faithfulness crux, locked L2)."
  - "Glossary definitions ARE traced defining Claims (GlossaryBlock); an un-traceable term routes to missing[]/honesty panel, never fabricated."
  - "OnboardingPath is NOT a Surface and has no own review gate — it sequences surfaces that already passed the gate (locked L4/A5)."

patterns-established:
  - "Progressive disclosure = deterministic ordering of traced claims (Start here / Prerequisites / Going deeper) by confidence + topics, no JS."

requirements-completed: [LEARN-01, LEARN-02, LEARN-03]

# Metrics
duration: 2min
completed: 2026-06-19
---

# Phase 12 Plan 02: Learning + OnboardingPath Spec Summary

**docs/surfaces.md now documents the fifth surface (Learning) and the OnboardingPath navigation model — the faithfulness contract (select/order/link, never invent), the three progressive-disclosure layers, the traced glossary, and the no-gate ordered track — filling the L-NNN spec gap.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-06-19T05:12:08Z
- **Completed:** 2026-06-19T05:13:39Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added a "Learning — the reviewed record, re-cut for someone new" spec section to `docs/surfaces.md`, mirroring the existing per-surface spec style, between "The Report" and "The review view".
- Documented the faithfulness contract explicitly: the learning re-cut SELECTS, ORDERS, and LINKS already-reviewed traced claims and never authors new factual prose; un-traceable material is not taught and surfaces in the honesty panel.
- Specified the three ordered progressive-disclosure layers (Start here / Prerequisites / Going deeper), no JS, ordered deterministically by `confidence` + `topics` (byte-stable).
- Specified the in-context glossary as `GlossaryBlock` where each term's definition IS a traced defining `Claim`; un-traceable terms route to `surface.missing[]` / honesty panel.
- Documented prerequisite-context links, LEARN-02 provenance as pure reuse of the Phase 9–11 devices, and the GREEN / `L-NNN` / distance-4 / INDIVIDUAL / ON_DEMAND / light-review placement (referencing the existing L-NNN id row at line 176).
- Documented the OnboardingPath (LEARN-03): an ordered track of slug refs with prev/next, explicitly NOT a Surface and with NO own review gate.

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Add the Learning-surface + OnboardingPath spec section to docs/surfaces.md (L7)** - `caa7fa1` (docs) — pushed to `claude/youthful-fermi-dly6mi`

**Plan metadata:** committed in the final docs commit below.

## Files Created/Modified
- `docs/surfaces.md` - Added the Learning surface + OnboardingPath spec section (59 insertions, 0 deletions; existing L-NNN id row and other sections untouched).

## Decisions Made
None beyond the locked decisions L1–L7 in 12-CONTEXT.md. The spec was written strictly against those locked choices (faithful select/order/link; glossary = traced Claim; OnboardingPath = no-gate ordered track).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None. Note: the concurrent plan 12-01 (templates.py / semantic.py / test_learning.py) was running in parallel; this plan touched only `docs/surfaces.md` and staged it by explicit path, so there was no interference. The test suite shows 541 passed / 1 xfailed (baseline was 537 passed / 1 xfailed — the +4 are plan 12-01's new learning tests already landed); the docs-only change broke nothing.

## Gate Output (re-run independently)

- **Plan grep gate** (`faithful`, `Start here`, `Prerequisites`, `Going deeper`, `glossary`, `OnboardingPath`, `prev`, `honesty` all present in docs/surfaces.md): **PASSED** — all 8 keys FOUND.
- **`git diff docs/surfaces.md`**: 59 insertions, 0 deletions — additions only; the L-NNN id row at line 176 and the other surface specs are unchanged.
- **`.venv/bin/python -m pytest -q`**: **541 passed, 1 xfailed in 11.71s** (no failures; docs-only change cannot affect tests).
- No phase-12 docs gate script exists (`tools/check_docs_11.py` is phase-11 specific; not applicable here).
- Internal consistency confirmed: the new section uses the same `**File:** / **Signal color:** / **Purpose:**` editorial style as the four existing surface specs and references the already-reserved `L-NNN` id row.

## User Setup Required
None - documentation-only change. No external service configuration required.

## Next Phase Readiness
- The Learning + OnboardingPath spec is now the contract the preset/render/dogfood plans implement against (specs-as-source-of-truth honored within the phase).
- No blockers. Zero new dependency; no code touched.

## Self-Check: PASSED

- FOUND: docs/surfaces.md
- FOUND: .planning/phases/12-learning-onboarding-surface/12-02-SUMMARY.md
- FOUND: commit caa7fa1

---
*Phase: 12-learning-onboarding-surface*
*Completed: 2026-06-19*
