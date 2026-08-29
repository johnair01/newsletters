---
phase: 04-sample-corpus-recipe
plan: 02
subsystem: publish
tags: [weekly, corpus, publish, cli, records-strip, pptx, part_digest, ci, merge-block]

# Dependency graph
requires:
  - phase: 04-sample-corpus-recipe
    provides: "plan 04-01's committed content/weekly/ corpus, weeklysite.py builder seam and the committed deck + digest sidecar"
  - phase: 02-renderer
    provides: "pptx_writer.render_surface_pptx / render_surface_pptx_bytes / part_digest / differing_parts and the writer's contract constants"
  - phase: 03-weekly-compose
    provides: "weeklyspec.weekly_slots — the load-and-surface-derived NL_ slot mapping"
provides:
  - "publish._CORPUS_LAYOUT fourth row — the weekly record reaches the published tree at /weekly/"
  - "`newsletters build|check --corpus weekly` — the fourth corpus on the SAME unforked merge-block gate, proven to FIRE"
  - "the Records strip on all four corpora, each naming its three neighbours"
  - "tests/test_weekly_golden.py — the [pptx]-gated tier-2 committed==fresh deck gate + the SC-3 Draft/watermark read-back"
  - "four-corpus gate lines in ci.yml (merge-block) and deploy-pages.yml (gate 1)"
affects: [04-03 docs/weekly.md recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-object import in a CLI branch as a TESTABILITY contract, not a style choice (`from . import weeklysite`) — the only form a monkeypatched builder can reach"
    - "Two-tier deck integrity completed: tier 1 (stdlib sidecar, every install) + tier 2 (committed==fresh under part_digest, the [pptx] job only)"
    - "In-test sha256 fingerprint over content/ as the git-free witness that a planted blocker left no trace"
    - "Pure-INSERTION workflow edits (a new line placed mid-continuation) so the zero-deletion diff invariant survives a module-list change"

key-files:
  created:
    - tests/test_weekly_golden.py
  modified:
    - src/newsletters/publish.py
    - src/newsletters/cli.py
    - src/newsletters/dogfood.py
    - src/newsletters/worksurface.py
    - src/newsletters/modulesite.py
    - tests/test_publish.py
    - tests/test_render.py
    - tests/test_weeklysite.py
    - .github/workflows/ci.yml
    - .github/workflows/deploy-pages.yml
    - content/rev1/site/index.html
    - content/rev1/site/library.html
    - content/work/site/library.html
    - content/module/site/library.html

key-decisions:
  - "[Phase 4-02]: The `check --corpus weekly` branch imports the MODULE OBJECT and resolves the builder at CALL time. This is a testability contract written into the source and stated in the docstring: binding the function at import time would leave the blocking proof's monkeypatch patching a name nobody reads, and the test would go green while the gate stayed unproven. A gate that cannot be shown to fire is not a gate."
  - "[Phase 4-02]: T-04-10 ('no blocked/Published state leaks into the committed corpus') is asserted IN THE TEST via a sha256-per-file fingerprint over content/, not left to a reviewer running `git status`. Hashing keeps it cheap over the vendored fonts, and a path-keyed map fails on a file that APPEARED or VANISHED, not only on an edit."
  - "[Phase 4-02]: Tier 2 renders through `build_weekly_deck` — the shipped entry point `newsletters weekly` calls and the one that produced the committed binary — rather than reassembling load → slots → writer in the test. A test that rebuilds the pipeline asserts against its own copy of it and keeps passing after the shipped one changes."
  - "[Phase 4-02]: A SECOND tier-2 arm asserts the freshly written .digest equals the COMMITTED sidecar. Tier 1 ties the committed deck to the committed sidecar; without this arm a deck and a digest that drifted TOGETHER would still pass as a matched pair."
  - "[Phase 4-02]: Both workflow module-list additions are placed MID-CONTINUATION (a new backslash-continued line inserted before the last one) so the edit is a pure insertion. The `zero deleted lines` invariant over .github/workflows/ is what makes T-04-12 reviewable at a glance, and appending to the final line would have cost it for no gain."
  - "[Phase 4-02]: deploy-pages.yml's header comment still enumerates three corpora. Left deliberately stale to hold the plan's `exactly one added line, zero deletions` criterion, and RECORDED here rather than fixed silently — see Deviations."

patterns-established:
  - "A corpus's committed==fresh drift check lives beside its BUILDER's suite (test_modulesite.py, test_weeklysite.py), not in test_publish.py; test_publish.py owns the ASSEMBLED-tree guarantees for all four"
  - "The clean-exit-zero CLI gate test carries a docstring naming its own vacuity and pointing at the two tests that carry the real trust"

requirements-completed: [WKLY-05]

# Metrics
duration: 28min
completed: 2026-08-29
---

# Phase 4 Plan 02: Corpus integration + the deck gate Summary

**The fourth corpus is registered in every place that knew about three — publish layout, CLI selector, both workflow gates, the Records strip on all four builders — and the two things the corpus could not prove about itself are now proven: `check --corpus weekly` FIRES on a planted blocker, and the committed deck equals a fresh render under `part_digest`.**

## Performance

- **Duration:** ~28 min
- **Tasks:** 3, each an atomic commit, each pushed
- **Files created/modified:** 15 (1 created + 14 modified, of which 4 are builder-regenerated HTML)

## Task Commits

1. **Task 1: corpus registration — publish layout, CLI selector, gate lines, blocking proof** — `7401d44` (feat)
2. **Task 2: the Records strip's fourth record + the four regenerated chrome pages** — `1437bc3` (feat)
3. **Task 3: the [pptx]-gated deck proof (tier 2 + SC-3 read-back) and the weekly CI job** — `2699916` (test)

## The integration checklist — every row, with its evidence

| # | Site | File | Evidence |
|---|------|------|----------|
| 1–2 | corpus + builder | `content/weekly/`, `weeklysite.py` | landed in 04-01 |
| 3 | `_CORPUS_LAYOUT` | `publish.py` | fourth row `("content/weekly/site", "weekly")`; `assemble` now writes **61 files / 20 pages** |
| 4 | `CorpusName` + docstring | `cli.py` | `weekly = "weekly"` + a bullet naming `weeklysite.py` and the `content/module` bindings source |
| 5 | `_DEFAULT_OUT` | `cli.py` | `CorpusName.weekly: "content/weekly/site"` |
| 6 | `build` branch | `cli.py` | `elif corpus is CorpusName.weekly:` → `build_weekly_site`, `index_name = "library.html"`; both `--corpus` help strings now name four |
| 7 | `check` branch (module-object form) | `cli.py` | `from . import weeklysite` then `weeklysite.build_weekly_surfaces()` — read, not assumed; the blocking test can only pass because of it |
| 8 | Records strip — rev1 | `dogfood.py` | `_REV1_RECORDS` += `("The weekly record", "weekly/library.html")` (root corpus, no `../`) |
| 9 | Records strip — work | `worksurface.py` | += `("The weekly record", "../weekly/library.html")` |
| 10 | Records strip — module | `modulesite.py` | += `("The weekly record", "../weekly/library.html")` |
| 11 | Records strip — weekly | `weeklysite.py` | unchanged — its tuple already named three neighbours (04-01) |
| 12 | Regenerate the chrome pages | 4 committed HTML | `git status` named **exactly those four**, 1 line changed in each; regenerated by `newsletters build --corpus rev1\|work\|module` |
| 13 | Records-strip shape test | `test_render.py` | third assertion `href="weekly/library.html"`; the per-surface-page refusal is unchanged and green |
| 14 | Published-tree tests | `test_publish.py` | test renamed to `..._four_corpora_...`; `weekly/library.html` + the report page (name DERIVED from `build_weekly_surfaces()[0].id`) asserted; `out / "weekly/fonts"` joined the OFL tuple |
| 15 | CI merge-block + deploy gate 1 | both workflows | a fourth `newsletters check --corpus weekly` in each |
| 16 | CI test-module lists | `ci.yml` | `tests/test_weeklysite.py` → `site-integrity` (stdlib-only); `tests/test_weekly_golden.py` → `weekly` (the `[pptx]` + fail-on-skip job) |
| **17** | **cross-corpus href allow-list** | `test_render.py` | **not in the plan's sixteen** — found by a red test, see Deviations |

## The `weekly` CI job's exact command, run locally

Verbatim from `ci.yml`, including the fail-on-skip grep:

```
$ set -o pipefail
$ .venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_weekly_blocks.py \
                   tests/test_weekly_values.py tests/test_semantic_gate_frozen.py \
                   tests/test_casespec.py tests/test_compose.py \
                   tests/test_swimlane.py tests/test_abstraction_guard.py \
                   tests/test_weekly_golden.py \
                   tests/test_excel_adapter.py -q | tee "$RUNNER_TEMP/weekly.log"
189 passed in 4.35s
EXIT=0
$ grep -Eq '[0-9]+ skipped' "$RUNNER_TEMP/weekly.log"   # → no match
SKIP GUARD PASSES (0 skipped)
```

**189 passed / 0 skipped** (183 before this plan, +6 from `test_weekly_golden.py`). A test suite and the job that runs it are two different artifacts; this is the second one.

## Workflow diff line counts

| File | Insertions | **Deletions** | `bare-install` |
|---|---|---|---|
| `.github/workflows/deploy-pages.yml` | **1** | **0** | n/a |
| `.github/workflows/ci.yml` (this plan) | 15 | **0** | **byte-unchanged** |
| `.github/workflows/*` since the milestone base | — | **0** (`git diff $BASE -- … \| grep -c '^-[^-]'` → `0`, both files) | byte-unchanged |

`deploy-pages.yml`'s entire diff is the single line `          newsletters check --corpus weekly`. Gate 2, the `main`-only condition, the preflight and the publish step are untouched; this phase pushes nothing to `main` (T-04-12).

## `git status --porcelain -- content/` after the blocking-proof run

```
$ .venv/bin/python -m pytest tests/test_weeklysite.py -q     # includes the planted-blocker test
16 passed
$ git status --porcelain -- content/
                                        # (empty — 0 lines)
```

The planted blocker exists only inside `monkeypatch`'s scope. The test asserts this itself, via a sha256-per-file fingerprint over `content/` taken before and compared after, so T-04-10 is executable in CI rather than a promise a reviewer has to check by hand. `test_build_weekly_smoke` carries the same fingerprint assertion, which is what turns the shared-ledger-path caveat ("`build_weekly_site` re-saves the committed `ids.json` even for a `tmp_path` build") from an assumption about idempotence into a check of it.

## Measured numbers against the recorded baselines

| Gate | Baseline (post-04-01) | After this plan |
|---|---|---|
| `pytest -q` | 850 passed / **0 skipped** | **859 passed / 0 skipped** (+9: 3 CLI gate + 6 golden) |
| the `weekly` CI job's exact command | 183 passed / 0 skipped | **189 passed / 0 skipped** |
| `newsletters check --corpus …` | 3 cleans | **4 cleans** (rev1, work, module, weekly) |
| `assemble` output | 3 corpora | **61 files, 20 pages, 180 internal links** (the resolver's `> 100` floor rose on its own, as predicted) |
| `lint-imports` | 2 kept / 0 broken | **2 kept / 0 broken** |
| `mypy src/newsletters` | 15 errors in 5 files | **15 errors in 5 files** (0 new) |
| `black --check src tests` | 69 reformat / 32 clean | **69 reformat / 33 clean** (+1 = the new golden module; no pre-existing file reformatted) |
| `isort --check-only` | pre-existing failures (DEF-15) | **no new failure** — clean on `test_weekly_golden.py`, `test_weeklysite.py`, `test_publish.py`; `cli.py` / `publish.py` / `dogfood.py` / `worksurface.py` / `test_render.py` unchanged from their baseline failures |
| `git diff -- content/*/ids.json` | clean | **clean** (all four ledgers byte-unchanged) |
| lazy-extra boundary | `pptx` absent after importing `cli` | **`pptx`, `yaml`, `openpyxl` ALL absent** after importing `cli` + `weeklysite` + `publish` |
| `git status --porcelain` (whole tree) | clean | **clean** |

## Files Created/Modified

- `tests/test_weekly_golden.py` — **new**, 6 tests, `requires_pptx` skipif idiom. Tier 2 (committed deck == fresh render under `part_digest`), the sidecar arm, the 3-second real-time double render, the SC-3 read-back from the reopened file, the whole-`model_dump()` no-mutation check, and the source-level no-gate-call guard (the last one deliberately NOT extra-gated).
- `src/newsletters/publish.py` — the fourth `_CORPUS_LAYOUT` row; the comment now says WHY only `content/*/site` is copied (the deck is unpublishable by LAYOUT, T-04-08); "three committed corpora" → "four" in the module docstring.
- `src/newsletters/cli.py` — `CorpusName.weekly`, `_DEFAULT_OUT`, the `build` and `check` branches, four help strings, and a docstring paragraph recording the module-object import as load-bearing.
- `src/newsletters/{dogfood,worksurface,modulesite}.py` — one Records tuple entry each, in each corpus's own relative shape. `render.py` was NOT touched: the builder owns its corpus's position in the strip (01-CONTEXT d3).
- `content/{rev1/site/index.html,rev1/site/library.html,work/site/library.html,module/site/library.html}` — regenerated by their builders, one line each.
- `tests/test_publish.py` — four-corpus assertions, the derived report-page name, `weekly/fonts` in the OFL tuple, and the guarantee-(b) comment now names both corpus-local drift suites.
- `tests/test_weeklysite.py` — the three CLI gate tests + `_content_fingerprint()`.
- `tests/test_render.py` — the strip's third assertion + the allow-list fix (see Deviations).
- `.github/workflows/{ci,deploy-pages}.yml` — four-corpus gates, two module-list additions, two explanatory comments. Zero deletions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A SEVENTEENTH integration site the checklist did not enumerate**
- **Found during:** Task 2, immediately after the regen
- **Issue:** `tests/test_render.py::test_no_dead_link_every_internal_href_resolves` pins cross-corpus Records hrefs to a known-prefix allow-list — `href.startswith(("work/", "module/", "../"))` — because such links point outside the corpus being rendered and cannot resolve locally. It was a THREE-corpus tuple, so the new `weekly/library.html` href on the rev1 chrome pages correctly failed it.
- **Fix:** `"weekly/"` added to the tuple. The resolver of record for those hrefs is unchanged — `test_publish.py`'s assembled-tree link test, which now resolves 180 links including the four new ones.
- **Files modified:** `tests/test_render.py`
- **Commit:** `1437bc3`
- **Worth reading twice:** this is exactly the risk the plan named ("the technical risk is *which* integration point gets missed"), and it behaved exactly as the plan wanted it to — **loud and immediate**, a red test in the same command as the change, not a late CI or deploy surprise. The enumerated sixteen were right about the *kind* of failure; the count was one short.

### Measured corrections to the plan's own numbers

**2. The Records strip is on FIVE committed pages, not four — but exactly FOUR change**
- The plan states `grep -rl '<section class="nl-records"' content/` returns 4. It returns **5**: `content/weekly/site/library.html` also carries the strip, because 04-01 committed the weekly Library with its three-neighbour tuple already in place. The plan's measurement predates that commit.
- **Four** files change, exactly as the plan's regen scope says, because the weekly's own tuple is unchanged: `content/{rev1/site/index.html, rev1/site/library.html, work/site/library.html, module/site/library.html}`. `git status --porcelain -- content/` named exactly those four and nothing else, so the stop-the-line condition ("if any other committed file moved, STOP") never triggered.
- The naive `grep -rl nl-records content/` count is likewise **19**, not the plan's 17, for the same reason (the two weekly pages style `.nl-records` in their inline CSS). Neither number was used to size the regen.

### Recorded, deliberately not fixed

**3. `deploy-pages.yml`'s header comment still enumerates three corpora**
- Its "WHAT PUBLISHES" block names `content/rev1/site` at the ROOT, `content/work/site` at `/work/` and `content/module/site` at `/module/`, and does not mention `content/weekly/site` at `/weekly/`.
- **Not fixed**, because updating that sentence means rewriting a line, and the plan's acceptance criterion — `deploy-pages.yml`'s diff is exactly one added line and zero deletions — is the thing that makes T-04-12 (tampering with the publish channel) reviewable at a glance. Trading a provably-inert one-line diff for a comment refresh is a bad trade in the one file where the diff *is* the evidence.
- **Surfaced, not silent** (CLAUDE.md: never let code and docs drift silently). This is a one-line follow-up for the PR review or plan 04-03, whichever the Editor-in-Chief prefers.

---

**Total deviations:** 1 auto-fixed (blocking) + 2 recorded-only.
**Impact on plan:** No scope creep, no architectural change, no package install. Every plan acceptance criterion is met or is met with the measured correction recorded above.

## Issues Encountered

- **DEF-15 bit once, in the expected place.** `test_weekly_golden.py` needed five names from `pptx_writer`; isort wants that as a parenthesized multi-line import and black wants a different shape of one. Resolved the way 04-01 resolved it — module-level access (`from newsletters import pptx_writer`, then five one-line bindings) — so every import in this plan's new file is single-line and both tools are clean on it. No repo-wide reformat; DEF-15 stays maintainer-gated.
- **Two black line-length nits in the new `test_weeklysite.py` tests** were fixed by shortening the source lines rather than by accepting black's wrapping, so the file stays in the *clean* set it entered this plan in.
- **Nothing else surprised.** The committed deck matched a fresh render on the first attempt (defaults reproduce the recorded `newsletters weekly` invocation exactly: `--author "Tora Ziyal"` equals the spec's `config: author:`, and both discovery globs find a single file), and the four regenerated pages each moved exactly one line.

## Known Stubs

None. Every artifact this plan declares exists on disk, every code path it adds is exercised by a test, and no placeholder or hardcoded-empty value was introduced.

## Threat Flags

None. This plan adds no network endpoint, no auth path, no file-access pattern and no schema change at a trust boundary. It narrows one surface rather than widening any: `check --corpus weekly` puts a previously ungated corpus under the same unforked merge-block gate as the other three.

## Carried Forward

Unchanged from 04-01, and still PR-review items (no `.pptx` consumer and no `gh` CLI in this environment): opening the committed deck in real PowerPoint, and the first live CI green of the `pptx` and `weekly` jobs. The `weekly` job's exact command has now been run locally with 0 skipped, which is the strongest local evidence available for the second.

Ready for plan 04-03 (`docs/weekly.md`, the operator recipe).

## Self-Check: PASSED

- `tests/test_weekly_golden.py` exists on disk; all four regenerated chrome pages exist and each contains an href to `weekly/library.html`.
- All three commit hashes (`7401d44`, `1437bc3`, `2699916`) resolve in `git log` and are pushed to `origin/claude/new-session-gw8tik`.
- `git status --porcelain` (whole tree) is empty; all four `ids.json` ledgers are byte-unchanged.

---
*Phase: 04-sample-corpus-recipe*
*Completed: 2026-08-29*
