---
phase: 10-reviewer-surfacing-merge-block
plan: 02
subsystem: provenance
tags: [merge-block, cli, ci, prov-04, exit-code, ai-optional, typer]

# Dependency graph
requires:
  - phase: 10-reviewer-surfacing-merge-block
    plan: 01
    provides: "review_blockers(surface, sources) -> list[Blocker] + BlockerKind + Surface.missing"
  - phase: 01-foundation
    provides: "Surface model + Review gate (publish/is_published)"
provides:
  - "newsletters check — the operator/CI entry: published-only per-surface report, exit 0 clean / exit 1 on any blocker"
  - ".github/workflows/ci.yml merge-block gate (PROV-04) — third job, bare .[test], runs newsletters check"
  - "Exit-code contract proven both directions (clean corpus -> 0; crafted blocked corpus -> nonzero)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Exit-code-is-the-contract: the CLI raises typer.Exit(1) on any blocker; the CI job's failure IS the merge block"
    - "Independently-red CI job: merge-block is separate from bare-install so it gives its own red signal (RESEARCH A2)"
    - "Bare-.[test] AI-free CI runtime: the merge-block job keeps PKG-03/PKG-04 the source of truth"
    - "Prove-the-gate-fires at the CLI boundary: monkeypatch the corpus builder to inject a blocker, assert exit != 0 (Phase-7 lesson)"

key-files:
  created:
    - tests/test_review_cli.py
  modified:
    - src/newsletters/cli.py
    - .github/workflows/ci.yml

key-decisions:
  - "check builds a corpus-WIDE {source_id: Source} lookup from every surface's traces, so a claim is checked against the live source even when that Source lives on another surface"
  - "Report line format: BLOCK [<kind>] <surface_id>: <detail>, then a summary count, then raise typer.Exit(1)"
  - "Lazy-import build_surfaces + review_blockers inside check (matches the existing build/version pattern; keeps a bare CLI import light + AI-free)"
  - "merge-block is a SEPARATE third CI job (not a step in bare-install) for an independently-red merge signal"

patterns-established:
  - "The CLI/CI exit code is the enforced PROV-04 contract; review_blockers is the shared logic both reuse"

requirements-completed: [PROV-04]

# Metrics
duration: 6min
completed: 2026-06-18
---

# Phase 10 Plan 02: The `newsletters check` CLI + the merge-block CI job Summary

**A `newsletters check` Typer command that runs the AI-free `review_blockers` across the corpus's PUBLISHED surfaces, prints a per-surface report, and exits nonzero on any STALE / un-entailed / open-`missing[]` claim (0 when clean) — plus a third `merge-block` CI job that runs it on the bare `.[test]` install so an unsafe surface cannot merge (PROV-04 enforced, exit-code contract proven both ways).**

## Performance
- **Duration:** ~6 min
- **Started:** 2026-06-18T12:52:57Z
- **Completed:** 2026-06-18T12:59:00Z
- **Tasks:** 2
- **Files modified:** 3 (2 modified, 1 created)

## Accomplishments
- Added the `check` `@app.command()` to `cli.py`: it builds the dogfood corpus via `build_surfaces()`, builds a corpus-wide `{source_id: Source}` lookup from every surface's traces, collects `review_blockers(surf, sources)` across all surfaces, prints one `BLOCK [<kind>] <surface_id>: <detail>` line per blocker plus a summary count, and `raise typer.Exit(1)` on any blocker; echoes `All published surfaces clean — no blockers.` and returns (exit 0) when clean. Zero new dependency (reuses `typer`, already core).
- Added the third `merge-block gate (PROV-04)` job to `ci.yml`, mirroring `bare-install`: `checkout@v4` + `setup-python@v5` (3.12) + bare `pip install ".[test]"` (NO `[ai]`/`[dev]`/`[panel]`) + `newsletters check`. A SEPARATE, independently-red job whose exit code fails the build on any blocker. The two existing jobs are untouched.
- Proved the exit-code contract BOTH directions in `tests/test_review_cli.py` via Typer's `CliRunner`: the real clean corpus → exit 0 (clean message); a monkeypatched corpus with one crafted blocked published surface → exit != 0 with the surface named — plus a CLI no-AI subprocess guard and a command-registered check.

## Task Commits
Each task was committed atomically and pushed:

1. **Task 1: the `newsletters check` command + exit-code e2e tests (L4, L7)** — `49d5472` (feat)
2. **Task 2: the third merge-block CI job (L5)** — `506ede6` (feat)

## Files Created/Modified
- `src/newsletters/cli.py` — added the `check` command (lazy-imports `build_surfaces` + `review_blockers`; corpus-wide sources lookup; per-surface report; `typer.Exit(1)` on any blocker; clean message + exit 0 otherwise). Typed clean under mypy.
- `.github/workflows/ci.yml` — added the `merge-block` job (3 jobs total now: `bare-install`, `merge-block`, `import-linter`).
- `tests/test_review_cli.py` (new) — `CliRunner` e2e: clean-corpus-passes (exit 0), exits-nonzero-on-blocker (monkeypatched `build_surfaces`, exit != 0, names the surface), the CLI no-AI subprocess guard, and a command-registered assertion.

## The `check` command behavior + exit codes
- **Scope:** PUBLISHED surfaces only — `review_blockers` returns `[]` for Draft / In-Review (publication is the trust boundary, L3). In the shipped corpus the published surfaces are the two kickoff/datamodel Reports, the Show, and the three per-reader Newsletters; the In-Review Rev1 report, plan, and article are exempt.
- **Sources lookup:** corpus-wide `{s.id: s for surf in surfaces for s in surf.traces}` — so a claim's trace is checked against the live source even if that `Source` object lives on a different surface's traces.
- **Report format:** one line per blocker — `BLOCK [<kind>] <surface_id>: <detail>` where `<kind>` ∈ `stale` / `unentailed` / `open_missing` and `<detail>` is `claim.text[:80]` (claim blockers) or the verbatim `missing[]` entry — followed by `\n<N> blocker(s) across the corpus — merge blocked (PROV-04).`
- **Exit codes:** **0** when clean (prints `All published surfaces clean — no blockers.`); **1** (`typer.Exit(1)`) when any published surface has a blocker. The exit code IS the CI contract.
- **AI-free:** the command lazy-imports only `review.py` + `dogfood`; no AI module is reachable; `lint-imports` stays 1 kept / 0 broken.

## The new CI job
`merge-block gate (PROV-04)` — third job in `ci.yml` on the existing `[push, pull_request]` trigger. Steps: `actions/checkout@v4`; `actions/setup-python@v5` (python 3.12); install with NO AI extras (`pip install ".[test]"`); run `newsletters check`. Its value is the EXIT CODE — a blocker fails the build so an unsafe surface cannot merge. Kept SEPARATE from `bare-install` (RESEARCH A2) for an independently-red merge-block signal; runs on the bare AI-free install so PKG-03/PKG-04 stay the source of truth.

## Actual gate output (re-run independently via `.venv/bin/python`)
- `pytest tests/test_review_cli.py -q` → **4 passed** (clean→0, blocked→nonzero, CLI no-AI guard, check-registered).
- `.venv/bin/newsletters check; echo exit=$?` → prints `All published surfaces clean — no blockers.` then **`exit=0`** (clean corpus, gate green on main).
- Blocked direction (proven in-test): monkeypatched `build_surfaces` → one crafted blocked published surface → `result.exit_code != 0`, report contains `sfc-blocked` + `BLOCK` + `merge blocked`. The gate FIRES, not just passes clean.
- `pytest -q` → **517 passed, 1 xfailed** (Plan-01 baseline 513 passed + 1 xfailed; +4 from this plan's new file; no regression — no-auto-publish + provenance tests stay green). Concurrent Plan 10-03's tests were not yet in this tree.
- `mypy src/newsletters` → **12 errors, all pre-existing** in `capture.py`/`render.py`/`dogfood.py` (the documented baseline). `mypy src/newsletters/cli.py` → **Success: no issues found** (no NEW errors).
- `lint-imports` → **1 contract kept, 0 broken** (the `check` CLI path stays AI-free).
- YAML: `ci.yml` parses; jobs are `['bare-install', 'merge-block', 'import-linter']`; `merge-block` runs `newsletters check`, installs bare `.[test]`, no `[ai]`.

## Decisions Made
- Built the sources lookup corpus-wide (not per-surface) so a claim whose `Source` lives on another surface is still checked against the live source — robust to how the dogfood corpus shares `Source` objects across surfaces. (Within the plan's L4 spec; documented for clarity.)

## Deviations from Plan
None - plan executed exactly as written. (Both tasks' file sets matched the plan; the command + tests landed in one Task-1 commit per the plan's task grouping.)

## Issues Encountered
None.

## Known Stubs
None. `newsletters check` is a complete, wired CLI entry point over the real corpus and the real `review_blockers`; the CI job invokes it directly.

## User Setup Required
None - zero new dependency (`typer[all]` is already a core dep). No external service configuration.

## Self-Check: PASSED
- FOUND: src/newsletters/cli.py (check command)
- FOUND: tests/test_review_cli.py
- FOUND: .github/workflows/ci.yml (merge-block job)
- FOUND: .planning/phases/10-reviewer-surfacing-merge-block/10-02-SUMMARY.md
- FOUND commits: 49d5472, 506ede6

---
*Phase: 10-reviewer-surfacing-merge-block*
*Completed: 2026-06-18*
