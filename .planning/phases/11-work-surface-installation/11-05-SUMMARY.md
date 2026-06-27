---
phase: 11-work-surface-installation
plan: 05
subsystem: cli
tags: [typer, cli, corpus-selector, merge-block-gate, review_blockers, docs, work-surface]

# Dependency graph
requires:
  - phase: 11-work-surface-installation (Plan 11-04)
    provides: build_work_site / build_work_surfaces (the work corpus + its content/work/ids.json ledger)
  - phase: 11-work-surface-installation (Plan 11-03)
    provides: build_work_report (hand-authored, content-addressed Draft Report)
  - phase: 10 (Plan 10-01/10-02)
    provides: corpus-agnostic review.review_blockers + the `check` CLI exit-code contract
provides:
  - "--corpus {rev1|work} selector on `newsletters build` and `newsletters check` (default rev1, backward-compat)"
  - "the work corpus runs through the SAME corpus-agnostic merge-block gate (review_blockers) — exit 0 clean / nonzero on a blocker"
  - "the completed operator-flow e2e (ingest -> report -> publish -> render -> check --corpus work exit 0)"
  - "the documented install/work-surface flow (architecture.md §8, product-spec.md §6) + the executed self-host-fonts note (design-system.md)"
affects: [phase-12, work-corpus-publishing, ci-merge-gate]

# Tech tracking
tech-stack:
  added: []  # ZERO new dependency — reused typer[all] (already a core dep)
  patterns:
    - "Corpus selector routes the BUILDER, never forks the gate (one trust rule, one place)"
    - "Lazy-import the selected corpus builder so the bare install stays light + AI-free"
    - "module-level import (from . import worksurface) so monkeypatch.setattr on the builder works at call time"

key-files:
  created: []
  modified:
    - src/newsletters/cli.py
    - tests/test_worksurface.py
    - docs/architecture.md
    - docs/design-system.md
    - docs/product-spec.md

key-decisions:
  - "Default --corpus rev1 + `out=None` sentinel resolving to a per-corpus default dir, so existing build/check behavior and tests are byte-for-byte unchanged"
  - "check imports the corpus MODULE (from . import worksurface/dogfood), not the function, so the e2e test can monkeypatch build_work_surfaces and prove the gate FIRES on the work corpus"
  - "build --corpus work points the index hint at library.html (work emits library.html, not index.html)"

patterns-established:
  - "Corpus selector: --corpus routes the builder, the SAME review_blockers gates either corpus (T-11-13)"
  - "Doc gate (tools/check_docs_11.py) makes 'the specs were updated' a checkable, non-vibey assertion"

requirements-completed: [WORK-03]

# Metrics
duration: ~18min
completed: 2026-06-18
---

# Phase 11 Plan 05: Work-corpus CLI selector + install-flow docs Summary

**`newsletters build|check --corpus {rev1|work}` wires the real work corpus through the SAME corpus-agnostic merge-block gate (exit 0 clean / nonzero on a planted blocker), with the install/work-surface flow + self-host-fonts mandate documented in the specs.**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-06-18 (RED commit 4ecd0a9)
- **Completed:** 2026-06-18 (docs commit 86e1ed6)
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Added a `CorpusName{rev1,work}` enum + `--corpus` option to BOTH `build` and `check` (default `rev1`, fully backward-compatible).
- `check --corpus work` runs the **identical** corpus-agnostic `review.review_blockers` over `worksurface.build_work_surfaces()` — proven in BOTH directions (clean work corpus → exit 0; a planted blocked PUBLISHED surface → nonzero, naming the surface).
- `build --corpus work` renders the real corpus to `content/work/site` (via `build_work_site`); `--corpus rev1` is unchanged (`content/rev1/site`).
- Completed the previously-skipped operator-flow e2e scaffold's final stage (`check --corpus work` exit 0) — the full WORK happy path (ingest → report → publish → render → check) now passes end to end.
- Documented the install/work-surface flow (architecture.md §8, product-spec.md §6) and recorded the self-host-fonts mandate as EXECUTED (design-system.md); `tools/check_docs_11.py` passes.

## The --corpus flag behavior (the CLI shape)

```
newsletters build  [--corpus {rev1|work}] [--out DIR]
newsletters check  [--corpus {rev1|work}]
```

| Command                      | Routes to                                   | Default out / scope          | Behavior |
| ---------------------------- | ------------------------------------------- | ---------------------------- | -------- |
| `build` / `build --corpus rev1` | `dogfood.build_site`                     | `content/rev1/site`          | UNCHANGED (legacy) |
| `build --corpus work`        | `worksurface.build_work_site`               | `content/work/site`          | renders the real corpus Library |
| `check` / `check --corpus rev1` | `dogfood.build_surfaces` → `review_blockers` | rev1 PUBLISHED surfaces   | UNCHANGED (legacy) |
| `check --corpus work`        | `worksurface.build_work_surfaces` → `review_blockers` | work PUBLISHED surfaces | SAME gate, exit 0/nonzero |

The selector routes the **builder**; `review_blockers` is never forked (T-11-13). The work corpus keeps its OWN append-only ledger (`content/work/ids.json`), preserving the sample/real boundary at the ledger layer. Zero new runtime dependency; lazy imports keep the bare install light + AI-free.

## Proven exit directions for the work corpus

- **Clean → exit 0:** the hand-authored work-report is **Draft** (no auto-publish), so it is exempt from `review_blockers` (publication is the trust boundary). Verified live: `newsletters check --corpus work` → `All published surfaces clean — no blockers.` `exit=0`.
- **Planted blocker → nonzero:** `test_check_gates_work_corpus` monkeypatches `worksurface.build_work_surfaces` to inject ONE blocked PUBLISHED surface (an addressed-but-un-entailed claim) and asserts `exit_code != 0`, the offending surface id (`sfc-work-blocked`) is named, and `BLOCK` / `merge blocked` appear. This proves the gate FIRES on the work corpus, not just on rev1 (Phase-7 lesson).
- **rev1 unchanged → exit 0:** `newsletters check` (no flag) → clean, exit 0.

## Docs added (specs = source of truth)

- **docs/architecture.md §8** — the full install/dogfood flow: `pip install` → `capture_files` read-only local ingest (data stays local, no network) → hand-author a Report (zero-AI manual backend, claims content-addressed or routed to `missing[]`) → publish through the review gate → `build/check --corpus work` renders/gates a Library showing provenance (claim→file) + lineage (fan-out). Plus the `--corpus` selector + the separate `content/work/ids.json` ledger.
- **docs/design-system.md** (near the line-65 "self-host in production" mandate) — recorded the mandate as EXECUTED: `@font-face` relative `fonts/…woff2` urls, the renderer emits the OFL font set beside the HTML, DM-first font-stack fallback, **zero external font call**.
- **docs/product-spec.md §6** — the work-surface on-ramp at the product level (read-only local ingest, no external calls), cross-linking architecture.md §8.

## Task Commits

1. **Task 1: gate e2e test (RED)** - `4ecd0a9` (test) — `test_check_gates_work_corpus` (both exit directions), `test_check_rev1_default_unchanged`, `test_build_corpus_work_smoke`, and completed the operator-flow e2e stage 5.
2. **Task 2: --corpus selector on build + check (GREEN)** - `643f3bb` (feat) — `CorpusName` enum + `--corpus` on both commands, routing work → worksurface / rev1 → dogfood through the same `review_blockers`.
3. **Task 3: document the install/work-surface flow + self-host-fonts note** - `86e1ed6` (docs).

_TDD: Task 1 = RED, Task 2 = GREEN (no REFACTOR needed — the GREEN diff was already minimal). Each commit was pushed immediately._

## Files Created/Modified
- `src/newsletters/cli.py` - `CorpusName` enum, `_DEFAULT_OUT`, `--corpus` on `build` + `check`, lazy-imported corpus routing through the shared `review_blockers`.
- `tests/test_worksurface.py` - the work-corpus gate e2e (both directions), the rev1-unchanged + build-work smoke tests, and the completed operator-flow stage 5.
- `docs/architecture.md` - §8 the work-surface install/dogfood flow + the `--corpus` selector.
- `docs/design-system.md` - the self-host-fonts mandate recorded as executed.
- `docs/product-spec.md` - §6 the work-surface on-ramp.

## Decisions Made
- **Default rev1 + `out=None` sentinel:** existing `build`/`check` behavior is unchanged; the per-corpus default out dir is resolved from `_DEFAULT_OUT` so the legacy CLI tests stay green.
- **Import the corpus MODULE, not the function, in `check`:** `from . import worksurface` (then `worksurface.build_work_surfaces()`) so the e2e test can `monkeypatch.setattr` the builder and prove the gate fires — resolving the attribute at call time, mirroring the existing `test_review_cli.py` pattern.
- **`build --corpus work` index hint = `library.html`:** the work renderer emits `library.html` (no `index.html`), so the "open …" hint points at the right file per corpus.

## Deviations from Plan

None - plan executed exactly as written. All three tasks landed on their stated files; no Rule 1-4 deviations were required.

## Issues Encountered
None. RED failed as expected (no `--corpus` option), GREEN passed on the first implementation, and the doc gate passed after the additive edits.

## Gate Output (re-run independently via .venv)

- `pytest tests/test_review_cli.py tests/test_worksurface.py -q` → **15 passed**
- `newsletters check --corpus work` → `All published surfaces clean — no blockers.` **exit=0**
- `newsletters check` (rev1 default) → `All published surfaces clean — no blockers.` **exit=0**
- `python tools/check_docs_11.py` → `docs ok: install/work-surface flow + self-host-fonts note are documented.` **exit=0**
- `pytest -q` (full) → **537 passed, 1 xfailed** (baseline 534 + the 3 new tests)
- `mypy src/newsletters` → **12 errors** (all pre-existing in capture/dogfood/render; **0 in cli.py**, no NEW errors)
- `lint-imports` → **1 kept, 0 broken** (Core must not import any AI/LLM package — KEPT)

## Next Phase Readiness
- WORK-03's gate-wiring half is closed: the work corpus is rendered AND gated through the same trust spine as rev1. This was the LAST wave of Phase 11.
- The 3 CI jobs are unaffected (rev1 `build`/`check` behavior unchanged; lint-imports + AI-isolation green; zero new dependency).
- No blockers for Phase 12.

## Self-Check: PASSED

- Files: all 5 modified files FOUND (cli.py, test_worksurface.py, architecture.md, design-system.md, product-spec.md).
- Commits: `4ecd0a9`, `643f3bb`, `86e1ed6` all FOUND in git log and pushed to `claude/youthful-fermi-dly6mi`.

---
*Phase: 11-work-surface-installation*
*Completed: 2026-06-18*
