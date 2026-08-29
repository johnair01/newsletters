---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: The Published Record
status: Awaiting next milestone
stopped_at: "v1.2 closed & archived (EiC pages review approved 2026-08-29). Next: /gsd-new-milestone → v1.3 The Weekly, One Shot (seed committed at .planning/seeds/v1.3-weekly-one-shot.md)."
last_updated: "2026-08-29T02:39:41.935Z"
last_activity: 2026-08-29 — Milestone v1.2 completed and archived
progress:
  total_phases: 2
  completed_phases: 0
  total_plans: 2
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-02)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Milestone v1.2 — The Published Record: one channel, production-ready. The site a reader sees is exactly the reviewed record a human merged to main, republished by one automated channel, no dead link, no drift, no manual step.

## Current Position

Phase: Milestone v1.2 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-08-29 — Milestone v1.2 completed and archived

## Performance Metrics

**Velocity:**

- v1.2: 0 plans complete (2 planned).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Site IA & linkability | 1/1 | Complete |
| 2. One publish channel | 1/1 | Complete |

**Recent Trend:**

- Milestone opened from a live forensic investigation (see research doc) rather than a seed —
  the publish system's failure was discovered by curling the live site and reading the
  Actions run history, not from the repo's own record (which believed the site was fine).

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Decisions taken at v1.2 open
(Editor-in-Chief, via structured question, 2026-07-03 — full rationale in
`.planning/research/2026-07-03-pages-publish-forensics.md`):

- [Milestone]: Site root = the rendered record (rev1 at root, /work/, /module/, cross-linked); `web/` is NOT deployed until it consumes real data (DEF-13).
- [Milestone]: One publish channel = the deploy workflow force-pushes an assembled tree to `gh-pages` (the branch-serving channel proven live); the `actions/deploy-pages` environment channel is deferred to a maintainer settings decision (DEF-14).
- [Milestone]: The workflow republishes committed bytes only (what was reviewed is what publishes); it re-runs `newsletters check` ×3 + the drift/link/fonts/marker tests before any push.
- [Milestone]: Design authority for new UI (Records strip, 404) = `docs/design-system.md` + the Claude design handoffs in `design-reference/` (esp. `signals-navigation/`: no surface a dead-end).
- [Milestone]: Base = the v1.1 integration branch (verified fast-forward); PR #20 sequencing is the maintainer's call, stated plainly in the PR body.

### Pending Todos

None. (B1–B20 fix-batch backlog remains parked in `reviews/2026-07-02-deep-review/07-tests-as-promises.md`, maintainer-gated.)

### Blockers/Concerns

- [Phase 2]: The gh-pages force-push erases the 3 manual UAT commits on that branch — intended (main is the record), but the PR must ask consent explicitly.
- [Phase 2]: If the maintainer ever flips Pages source to "GitHub Actions", gh-pages pushes go dark — the workflow carries a warn-only preflight (`gh api repos/…/pages`) to surface it.
- [Phase 1]: Corpora regenerate with new chrome — the ledgers (`content/*/ids.json`) MUST show no diff; any ledger change is a stop-the-line bug (append-only invariant).

## Deferred Items

Carried from v1.1 (full list in `.planning/milestones/v1.1-ROADMAP.md`): DEF-01..12.
New at v1.2 open: DEF-13 (wire `web/` to real data), DEF-14 (adopt the environment deploy
channel iff maintainer aligns repo settings).

## Session Continuity

Last session: 2026-07-03 — v1.2 merged & live; post-merge UAT PASSED (evidence on PR #21)
Stopped at: Pages review (EiC), then /gsd-complete-milestone (audit → archive → retrospective).
Resume file: this file + `.planning/ROADMAP.md` + `.planning/research/2026-07-03-pages-publish-forensics.md`

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
