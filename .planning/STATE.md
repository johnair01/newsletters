---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: The Weekly, One Shot
status: planning
last_updated: "2026-08-29T02:43:46.208Z"
last_activity: 2026-08-29
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-29)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Milestone v1.3 — The Weekly, One Shot: the recurring module weekly deck becomes a product output — weekly composer + Weekly Spec + asset evidence + a deterministic template-driven PPTX renderer, through the untouched review gate.

## Current Position

Phase: Phase 1: Specify + de-risk — not started (ready to plan)
Plan: — (plans created at plan-phase time)
Status: Roadmap created (4 phases, 6/6 requirements mapped) — ready for `/gsd-plan-phase 1`
Last activity: 2026-08-29 — v1.3 roadmap written (`.planning/ROADMAP.md`); traceability mapped

## Performance Metrics

**Velocity:**

- v1.3: 0 plans complete (roadmap defined 2026-08-29; 4 phases).
- v1.2: 2 plans across 2 phases (closed 2026-08-29, archived).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Specify + de-risk | 0/0 (unplanned) | Not started |
| 2. Renderer (WKLY-01) | 0/0 (unplanned) | Not started |
| 3. Weekly compose (WKLY-02/03/04) | 0/0 (unplanned) | Not started |
| 4. Sample corpus + recipe (WKLY-05/06) | 0/0 (unplanned) | Not started |

**Recent Trend:**

- v1.3 opened from a committed seed (`.planning/seeds/v1.3-weekly-one-shot.md`) whose
  current-state claims were verified against the live repo first. Fully autonomous run
  authorized by the EiC (2026-08-29): no between-phase human stop; the human gate is the
  final PR. The ONE discussion round is done — new questions are decided per the recorded
  recommendations and logged.
- Roadmap mirrors the seed's approved 4-phase table; phase numbering resets to 1–4 (prior
  phase dirs archived under `.planning/milestones/`, `.planning/phases/` empty — no collision).

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Decisions taken at v1.3 open
(Editor-in-Chief, structured question round, 2026-08-29 — the ONE round; recorded also in
WHERE-WE-ARE.md):

- [Milestone]: Weekly deck reuses `Surface(REPORT)` — the PPTX renderer is an output format, not a new semantic kind.
- [Milestone]: Asset provenance minimum = folder + date + event label; deep link optional EXCEPT a BI screenshot standing in for values (WKLY-04), where it is required. No provenance → `missing[]`, never placed silently.
- [Milestone]: Template contract = named placeholders; missing/unknown names fail loud. The renderer never invents layout.
- [Milestone]: v1.2 formally closed on live evidence (EiC pages review 2026-08-29).
- [Run]: Fully autonomous through all v1.3 phases; the human gate is the final PR. Branch: `claude/new-session-gw8tik` serves the seed's `gsd/v1.3-*` integration-branch role (harness-designated; v1.1 precedent). Never touch `main`.
- [Run]: Milestone-level ecosystem research skipped — the seed encodes it and phase-level research + the Phase 1 determinism spike cover the real unknowns (logged per the no-more-questions contract).
- [Roadmap, 2026-08-29]: Phase 1 carries no WKLY requirement — it de-risks WKLY-01/02 and ships spec + a recorded determinism decision with evidence. WKLY-01→P2, WKLY-02/03/04→P3, WKLY-05/06→P4.

### Pending Todos

None. (B1–B20 fix-batch backlog remains parked in `reviews/2026-07-02-deep-review/07-tests-as-promises.md`, maintainer-gated.)

### Blockers/Concerns

- [v1.3 Phase 1]: The `.pptx` determinism spike must retire the byte-stability risk (zips embed timestamps/ordering) BEFORE anything depends on the renderer — byte-stable, or a recorded content-stable definition with evidence.
- [v1.3 Phase 3]: `render.py`'s block dispatch currently `return ""`s on an unrecognized block — new block kinds could be silently dropped from the HTML surface. Must be closed (render each kind, or fail loud) as a Phase 3 criterion.
- [Carried]: `v1.1`/`v1.2` tags exist locally only — the environment's git proxy drops tag pushes; maintainer creates them via the Releases UI.
- [Carried]: ledgers (`content/*/ids.json`) are append-only — any diff on regenerate is a stop-the-line bug.

## Deferred Items

Carried from v1.1 (full list in `.planning/milestones/v1.1-ROADMAP.md`): DEF-01..12.
New at v1.2 open: DEF-13 (wire `web/` to real data), DEF-14 (adopt the environment deploy
channel iff maintainer aligns repo settings). Plus the B1–B20 fix-batch (maintainer-gated) and,
new at v1.3 open, the ADAPT-05 value-side extension (values come via export this milestone).

## Session Continuity

Last session: 2026-08-29 — v1.2 formally closed; v1.3 opened from seed; ONE discussion round done; v1.3 roadmap written (4 phases, 6/6 mapped)
Stopped at: Roadmap created. Next: `/gsd-plan-phase 1` (Specify + de-risk), then /gsd-autonomous through all phases.
Resume file: this file + `.planning/ROADMAP.md` + `.planning/seeds/v1.3-weekly-one-shot.md` + WHERE-WE-ARE.md (kickoff contract)
