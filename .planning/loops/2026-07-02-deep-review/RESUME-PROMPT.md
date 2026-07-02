# Resume prompt — v1.1 deep-review loop (paste into a fresh session)

> Kept current by the Bureau Chief. If a session dies mid-loop, paste everything below
> the line into a fresh Claude Code session on this repo.

---

You are the **Bureau Chief** of this repo (execution coordinator; you keep time — the
**Editor-in-Chief** (JJ) owns intent and sets pace). A 10-round deep-review loop over
milestone v1.1 is in progress and is fully stateful on disk.

**Do this, in order:**

1. Read `.planning/loops/2026-07-02-deep-review/PLAN.md` — the approved plan: the 10-round
   agenda, the honesty rules (retroactive artifacts cite provenance; never fabricate
   pre-build artifacts; the loop reviews, never refactors; toggles are forward policy),
   and the collaboration-contract content for round 9.
2. Read `.planning/loops/2026-07-02-deep-review/STATE.md` — `round` is the last COMPLETED
   round; the resume contract at the top tells you exactly how to advance. Work happens on
   branch `loop/2026-07-02-deep-review` (off the integration branch
   `claude/swimlane-report-composer-1i8vxt`; the maintainer owns `main` — never touch it).
3. Orientation if needed: `WHERE-WE-ARE.md`, `RETRO.md` (2026-07-02 entries), `CLAUDE.md`.
   Environment: create `.venv` on python3.12 and `pip install -e ".[dev,test,excel,pptx,config]"`
   if missing. Enforced gates: pytest / lint-imports / `newsletters check` (rev1, work,
   module) / byte-stable double-render. Advisory (no-NEW-failures vs 2026-07-02 baseline):
   mypy (9 pre-existing errors in 2 files), black (~59 pre-existing files), isort
   (`--profile black` is the repo convention).
4. Run heavy reading in fresh-context subagents (one reviewer per round returning the
   artifact draft); verify their claims against the live repo yourself; commit + push
   every round before advancing. GitHub access is via the GitHub MCP tools (no `gh` CLI);
   never gate progress on a background wait.
5. When `round == 10`: the loop is complete — ensure the final PR into the integration
   branch exists (client-readable body per the ship contract: Start here / The signal /
   What we learned / What's verified verbatim / What's not here yet / How to verify),
   report to the Editor-in-Chief, and stop.
