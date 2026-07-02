---
phase: 03-worked-synthetic-module-report
plan: 02
subsystem: cli-gate
tags: [cli, corpus-selector, review-gate, moda-02]
requires:
  - "src/newsletters/modulesite.py::build_module_site (03-01)"
  - "src/newsletters/modulesite.py::build_module_surfaces (03-01)"
  - "src/newsletters/review.py::review_blockers (10-01, unforked)"
provides:
  - "newsletters build --corpus module (additive routing to build_module_site)"
  - "newsletters check --corpus module (same unforked review_blockers gate)"
affects:
  - "src/newsletters/cli.py (additive: enum member + default-out + 2 dispatch branches)"
tech-stack:
  added: []
  patterns:
    - "Additive corpus-selector branch (elif) — router routes the BUILDER, never forks the gate"
    - "Gate-both-ways proof: clean exit 0 (Draft-vacuous) + monkeypatched in-memory PUBLISHED blocker nonzero"
key-files:
  created:
    - "tests/test_module_cli.py"
  modified:
    - "src/newsletters/cli.py"
decisions:
  - "cli.py extended ADDITIVELY only — rev1/work code paths byte-untouched; review.py untouched"
  - "Planted blocker is an in-memory TEST fixture (monkeypatch), never a committed dirty corpus (T-03-07)"
  - "Config-specific name 'module-a' kept OUT of src/ (LANE-03 abstraction guard) — generic docstring phrasing"
metrics:
  duration: "~20 min"
  completed: "2026-07-02"
  tasks: 2
  commits: 3
  files: 2
---

# Phase 3 Plan 02: Module corpus CLI + gate wiring Summary

Wired the synthetic `module` corpus into the LIVE CLI additively — `newsletters build --corpus
module` routes to `modulesite.build_module_site` and `newsletters check --corpus module` runs the
SAME unforked `review_blockers` merge gate — and proved the gate fires BOTH ways (exit 0 on the
clean Draft corpus, nonzero on a planted in-memory PUBLISHED blocker). This is the CLI/gate half
of MODA-02.

## What was built

**Task 1 — additive `--corpus module` routing (`src/newsletters/cli.py`)**
- Added `module = "module"` to the `CorpusName` enum with a docstring note.
- Added `CorpusName.module: "content/module/site"` to `_DEFAULT_OUT`.
- `build`: new `elif corpus is CorpusName.module:` branch lazy-importing `build_module_site`
  (index name `library.html`, matching work).
- `check`: new `elif corpus is CorpusName.module:` branch lazy-importing `modulesite` and setting
  `surfaces = modulesite.build_module_surfaces()`. The rest of `check` (the `{source_id: Source}`
  lookup, `review_blockers`, the report + exit code) is UNCHANGED and corpus-agnostic — the
  selector routes only the builder (T-11-13).
- Build/check help strings + the check docstring now mention `module`.
- rev1 (`else`) and work (`if`) code paths are byte-for-byte unchanged; `review.py` untouched.

**Task 2 — gate-both-ways proof (`tests/test_module_cli.py`, new)**
- `test_check_module_clean_exits_zero` — clean committed corpus exits 0 (Draft-vacuous caveat
  noted in the test docstring: the composed report ships Draft → exempt; publication is the trust
  boundary).
- `test_check_module_blocks_on_planted_blocker` — an in-memory PUBLISHED Report carrying one
  UNENTAILED blocker (addressed `Trace.from_source` whose span omits the claim text),
  monkeypatched onto `newsletters.modulesite.build_module_surfaces`; asserts nonzero exit,
  `BLOCK`, the surface id, and `merge blocked` in the report.
- `test_build_module_smoke(tmp_path)` — `build --corpus module --out <tmp>` exits 0 and writes
  `report-module-a.html` + `library.html`.

## Verbatim gate tails

Live CLI, clean corpus:
```
$ newsletters check --corpus module
All published surfaces clean — no blockers.
exit=0
```

Live CLI, planted in-memory PUBLISHED blocker (monkeypatched builder):
```
BLOCK [unentailed] sfc-module-blocked: the module corpus auto-published itself

1 blocker(s) across the corpus — merge blocked (PROV-04).
exit= 1
```

All corpora green (enforced gate, re-run independently):
```
check --corpus rev1   -> All published surfaces clean — no blockers. (exit 0)
check --corpus work   -> All published surfaces clean — no blockers. (exit 0)
check --corpus module -> All published surfaces clean — no blockers. (exit 0)
check (default rev1)  -> All published surfaces clean — no blockers. (exit 0)
```

Full suite + import contract:
```
608 passed in 17.40s          # 605 baseline + 3 new
Contracts: 2 kept, 0 broken.  # lint-imports (AI-free core intact)
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Config-specific name `module-a` leaked into `src/` via the cli docstring**
- **Found during:** Task 2 full-suite run (`test_abstraction_guard.py::test_no_config_specific_name_in_src` failed).
- **Issue:** The initial Task-1 `CorpusName.module` docstring read "the swim-lane module-a config",
  which the LANE-03 abstraction guard denylists — the concrete `module-a` name must live ONLY in
  the YAML config + rendered content, never in source.
- **Fix:** Generic phrasing ("the swim-lane config"); no behavior change.
- **Files modified:** `src/newsletters/cli.py`
- **Commit:** e566bfb

## Advisory gate notes (no NEW failures vs baseline)

- **black / isort on `cli.py`:** `cli.py` was ALREADY black-dirty and isort-dirty at BASELINE
  (pre-existing wrapping on lines 45, 94-99, 154-161 that I did not touch). Per the SCOPE BOUNDARY
  rule and "existing branches byte-untouched," I did NOT reformat those pre-existing lines; my
  additions themselves are black/isort-clean. mypy on `cli.py`: clean.
- **black / isort / mypy on `tests/test_module_cli.py`:** black-clean (applied one wrap black
  requested), isort-clean. mypy shows only the baseline `import-untyped` notes for the un-`py.typed`
  `newsletters` package — identical to the existing `tests/test_worksurface.py` baseline, so no new
  failures.

## Threat surface

No new security-relevant surface introduced. The plan's threat register is satisfied:
- **T-03-06 (bypass):** the selector routes only the builder; the SAME unforked `review_blockers`
  runs (`review.py` untouched), proven by the both-ways test.
- **T-03-07 (tampering):** the blocker is an in-memory TEST fixture (monkeypatch); the committed
  `content/module/` corpus stays clean + Draft (working tree clean after all commits).

## Concerns

- The clean-corpus "exit 0" is DRAFT-VACUOUS (the only committed module surface is Draft →
  exempt). This is intentional and matches the work corpus (Phase 11 caveat), and the blocking
  direction is what actually exercises the gate — but it should be called out honestly in the PR
  body (same as Phase 11).

## Commits

- c324cbc feat(03-02): additive --corpus module routing for build + check
- e566bfb fix(03-02): drop config-specific 'module-a' from cli docstring (LANE-03)
- b19ce3b test(03-02): gate-both-ways proof over the module corpus (MODA-02)

## Self-Check: PASSED
- FOUND: src/newsletters/cli.py (modified, additive)
- FOUND: tests/test_module_cli.py (created)
- FOUND commit c324cbc, e566bfb, b19ce3b
