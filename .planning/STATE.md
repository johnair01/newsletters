---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: The Published Record
status: in_progress
stopped_at: "Phase 1 (Site IA & linkability) SHIPPED & VERIFIED 5/5 (PUB-03). Next: Phase 2 (One publish channel)."
last_updated: "2026-07-03T00:45:00.000Z"
last_activity: 2026-07-03 — Phase 1 shipped & verified (Records strip + 404; 629 tests)
progress:
  total_phases: 2
  completed_phases: 1
  total_plans: 2
  completed_plans: 1
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-02)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Milestone v1.2 — The Published Record: one channel, production-ready. The site a reader sees is exactly the reviewed record a human merged to main, republished by one automated channel, no dead link, no drift, no manual step.

## Current Position

Phase: 2 of 2 (One publish channel) — not started
Plan: 02-01 — not started
Status: Milestone v1.2 OPENED. Working branch `claude/github-pages-production-ready-du9ptu`
(fast-forwarded onto the v1.1 integration branch — contains all of PR #20; sequencing note
travels in the PR). Baseline gates re-run independently at open: 626 passed, lint-imports
2 kept / 0 broken.
Last activity: 2026-07-03 — milestone capture (research/requirements/roadmap)

## Performance Metrics

**Velocity:**

- v1.2: 0 plans complete (2 planned).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Site IA & linkability | 1/1 | Complete |
| 2. One publish channel | 0/1 | Not started |

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

Last session: 2026-07-03 — v1.2 milestone open (this session also ran the publish forensics)
Stopped at: Milestone captured; Phase 1 next (context → plan → execute → verify per GSD).
Resume file: this file + `.planning/ROADMAP.md` + `.planning/research/2026-07-03-pages-publish-forensics.md`
