---
phase: 04-sample-corpus-recipe
verified: 2026-08-29T10:39:09Z
status: human_needed
score: 5/5 (5 automatic must-haves verified; 2 items require human verification, both pre-recorded
  as deferred to the PR review, not phase gaps)
overrides_applied: 0
human_verification:
  - test: "Open the real committed .pptx in actual PowerPoint (or LibreOffice Impress) and visually confirm the DRAFT watermark renders on every slide with no overflow, and that Selection-Pane `NL_` shapes are correctly filled."
    expected: "Deck opens cleanly in the real application; DRAFT watermark visible on every slide; no silent text overflow (P-07 risk)."
    why_human: "XML-level inspection (done in this verification) proves the watermark text and contentStatus=draft byte are present, but only opening the file in the real renderer proves it displays correctly — a claim no grep or zipfile read can make."
  - test: "Watch the GitHub Actions `weekly` and `site-integrity` (pptx-installing) CI jobs run green on first push/PR for this phase's branch."
    expected: "Both jobs pass on GitHub's runners, confirming the [pptx]/[excel] extras install cleanly and tests/test_weekly_golden.py's [pptx]-gated tier-2 gate fires as designed in that environment."
    why_human: "This is a CI-environment observation (runner OS, extras resolution, network egress in Actions) that cannot be reproduced by local .venv execution; recorded as an open item in WHERE-WE-ARE.md and 04-CONTEXT.md's deferred list — carried to the PR review, not a phase gap."
---

# Phase 4: Sample corpus + recipe — Verification Report

**Phase Goal:** The weekly is proven and repeatable by someone who is not the author — a synthetic
sample weekly composes and renders in CI under the full gate set, and `docs/weekly.md` walks an
operator through the loop on their own data, read-only and local.
**Verified:** 2026-08-29T10:39:09Z
**Status:** human_needed (all 5 ROADMAP success criteria independently re-verified TRUE against
the live repo; two items — real-PowerPoint open and first CI-runner green — are pre-recorded,
known, deferred-to-PR items, not gaps found by this verification)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (mapped 1:1 to ROADMAP Phase 4 Success Criteria)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | A synthetic weekly in the `content/module` lineage composes/renders to `.pptx`, exercising the honesty path (no-KPI lane, no-source recognition, no-provenance asset) end to end, none silently dropped | ✓ VERIFIED | `content/weekly/weekly-2374-w41.yml` plants all three absences with explanatory header comments. Read the **committed** `content/weekly/site/weekly-2374-w41.html` directly: the `.honesty` panel contains all three disclosure lines verbatim — `field 'recognitions[1].source' is absent or empty`, `asset 'manifest-annex-photo': provenance field 'folder' is absent`, and `section 'MOR/IQ tools & defect projects' declares no KPIs — strip omitted`. Recognition #2 (Elim Garak, no source) still renders in the "Recognitions" block — not dropped. `tests/test_weeklysite.py` (13 tests) + `tests/test_weekly_golden.py` (12 tests) — ran independently, 32 passed. |
| 2 | Full enforced gate set green over all corpora, re-run independently: pytest, lint-imports, `newsletters check` (rev1/work/module/weekly), committed==fresh double-render incl. `.pptx`, bare-install untouched, mypy/black/isort no-new-failures; every `content/*/ids.json` ledger unchanged | ✓ VERIFIED | Independently re-ran (not trusted from SUMMARY): `pytest -q` → **871 passed, 0 skipped** (exact match to claimed count). `lint-imports` → 2 kept, 0 broken. `newsletters check --corpus {rev1,work,module,weekly}` → all exit 0, "no blockers". Fresh `newsletters build --corpus {work,module,weekly}` into scratch dirs → `diff -rq` against committed `content/*/site` → **zero differences**. Deck: independently computed `part_digest` of the committed `.pptx` == committed `.digest` sidecar == freshly-rendered deck's digest (all three match: `d61ce632...`). `mypy src/` → 15 errors/5 files (matches recorded baseline exactly). `black --check` → 69 would-reformat/33 unchanged (matches DEF-15 baseline exactly). `git status --porcelain content/` clean after every fresh-render probe — no ledger mutated. |
| 3 | Sample ships Draft and watermarked: no sample/script/CI step publishes, advances the gate, pushes to main, or makes an external call — proven by test and by reading workflow diffs | ✓ VERIFIED | Independently unzipped the committed `content/weekly/deck/weekly-2374-w41.pptx`: `docProps/core.xml` → `<cp:contentStatus>draft</cp:contentStatus>` and `<cp:category>generated-by:newsletters</cp:category>`; `ppt/slides/slide1.xml` contains DRAFT watermark text. `grep` across `weeklysite.py`, `cli.py`, `publish.py`, `weeklyspec.py`, `swimlane.py`, `compose.py` for `.publish(`/`.approve(`/`open_pull_request(` → zero hits outside docstring prose. No `requests`/`urllib`/`socket` import in the weekly path. `deploy-pages.yml`/`ci.yml` read directly — no push to main from these jobs; deploy workflow's force-push step is gated to `main`-triggered runs only (pre-existing, unchanged by this phase). |
| 4 | `docs/weekly.md` takes a non-author operator through authoring/composing/rendering/reviewing with copy-pasteable commands matching the shipped CLI, verified by executing them against the synthetic corpus | ✓ VERIFIED | Read `docs/weekly.md` in full (238 lines, 8 numbered steps). Independently re-ran every fenced `newsletters …` command against the live CLI and the committed corpus: `newsletters weekly --help`, `newsletters build --corpus weekly`, the 5-arg `newsletters weekly --spec ... --lanes ... --template ... --author ... --out ...` (produced a deck byte-digest-identical to the committed one), `newsletters check --corpus weekly` (exit 0), `newsletters assemble --out ...`. `--help` output for `weekly`/`build`/`check`/`assemble` matches every flag named in the doc exactly. Doc-contract tests (`test_recipe_commands_match_the_shipped_cli`, `test_recipe_carries_the_load_bearing_anchors`, `test_docs_describe_four_corpora`) pass independently. |
| 5 | Spec and compass stay honest: `docs/architecture.md`/`docs/surfaces.md` reflect shipped block kinds/renderer, `WHERE-WE-ARE.md` updated, milestone friction logged in `RETRO.md` with durable fixes as rules/guards | ✓ VERIFIED | `docs/architecture.md` §"four corpora" names `weekly`/`weeklysite.py`/`content/weekly/site` and `content/weekly/ids.json` explicitly (dated 2026-08-29 note on the 15-block-kind union). `docs/surfaces.md` names "The weekly record (v1.3)" among the four published corpora. `WHERE-WE-ARE.md` top entry: "2026-08-29 (newest) — v1.3 PHASE 4 IS DONE" with load-bearing truths and a "Still open" note naming exactly the two items in this report's human-verification section. `RETRO.md` top entry "W27: the milestone's frictions" logs 6 numbered frictions each with a hardened rule (doc-contract tests, gate-location-in-docstring convention, etc.) — durable guards, not narrative. |

**Score:** 5/5 truths verified against live code, independently re-executed (no claim taken from SUMMARY.md or 04-REVIEW.md without re-derivation).

### Code-Review Fix Verification (WR-01..05, IN-03, IN-05 — independently re-checked in live files, not trusted from 04-REVIEW.md)

| Finding | Claimed commit | Verified live? | Evidence |
|---|---|---|---|
| WR-01 (root-relative ledger/fonts) | `623851d` | ✓ | `weeklysite.py` `build_weekly_site`: `root_path = (Path(root) if root is not None else Path.cwd()).resolve()`; fonts dir checked and refused loud before any write; `Ledger.load(root_path / _LEDGER_PATH)`. |
| WR-02 (ambiguous *.yml) | `f492110` | ✓ | `_discover_one_yml` raises `FileExistsError` naming every candidate when `len(candidates) > 1`. |
| WR-03 (`--author` on `build`) | `d666dc6` | ✓ | `cli.py build` command exposes `--author` typer.Option, refuses it for non-weekly corpora with a named error; live `--help` output confirms the flag exists. |
| WR-04 (binary scanner blind spot) | `3f11647` | ✓ | `test_committed_binaries_and_asset_names_are_synthetic` exists and passes (independently re-run). |
| WR-05 (`.nojekyll`-only clobber guard) | `5d8766e` | ✓ | `publish.py` `_is_previous_assembly` now requires BOTH `.nojekyll` AND `GENERATED_MARKER` in `index.html`; `force=True` explicit override present. |
| IN-03 (symlink-escape refusal voice) | `d7bd0fb` | ✓ | `_load_inbox_sources` catches the raw `ValueError` and re-raises in the corpus's teaching voice; `test_inbox_symlink_escape_is_refused_before_the_read` passes. |
| IN-05 (`.yaml` discovery) | `d0cfa14` | ✓ | `_discover_one_yml` globs both `*.yml` and `*.yaml`. |

All 7 claimed fix commits are present in `git log` for the touched files and their code is live and test-covered — not merely described in the review's "fix outcomes" table.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `src/newsletters/weeklysite.py` | corpus builder seam | ✓ VERIFIED | `build_weekly_surfaces`/`build_weekly_site`/`build_weekly_deck` present, substantive (>250 lines), wired from `cli.py` and `publish.py`. |
| `content/weekly/weekly-2374-w41.yml` | authored synthetic spec, 3 planted absences | ✓ VERIFIED | Present, all 3 absences confirmed by direct read. |
| `content/weekly/ids.json` | own append-only ledger, R-001 | ✓ VERIFIED | Present; `git status` clean after repeated fresh-build probes (ledger not mutated). |
| `content/weekly/deck/weekly-2374-w41.pptx` + `.digest` | committed deck + tier-1 sidecar | ✓ VERIFIED | Both present; digest independently recomputed and matched. |
| `content/weekly/site/*.html` | committed HTML incl. honesty panel | ✓ VERIFIED | Read directly; matches fresh render byte-for-byte. |
| `tests/_corpus_scan.py` | promoted synthetic-content scanner | ✓ VERIFIED | `REAL_LOOKING_LITERALS`/`EMAIL_RE`/`scan_real_looking` exported and imported by `test_weeklysite.py`/`test_abstraction_guard.py`. |
| `docs/weekly.md` | 8-step operator recipe | ✓ VERIFIED | Present, 238 lines, all commands independently re-executed. |
| `.github/workflows/ci.yml` / `deploy-pages.yml` | 4-corpus gate wiring | ✓ VERIFIED | `--corpus weekly` present in both `check` gate loops; `weekly` job runs `test_weekly_golden.py` under `[pptx]` with a fail-on-skip guard. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `weeklysite.py` | `content/module/*.yml` | `load_swimlanes` over sorted glob | WIRED | `_discover_lanes` resolves the module corpus's config; the rendered HTML's claim-evidence chips cite `content/module/module-a.yml`. |
| `weeklysite.py` | `newsletters.weeklyspec` | `load_weekly_spec`/`build_weekly_report`/`weekly_slots` | WIRED | Imported and called in `_load_and_compose`; the honesty panel's disclosure sentences are produced by the composer's own format strings (independently observed in the rendered HTML). |
| `cli.py build --corpus weekly` | `weeklysite.build_weekly_site` | module-object import (testability contract) | WIRED | Live-executed; produced HTML identical to committed. |
| `cli.py weekly` | `weeklysite.build_weekly_deck` | direct call, `--out` required | WIRED | Live-executed; produced a deck whose digest matches the committed sidecar exactly. |
| `publish._CORPUS_LAYOUT` | `content/weekly/site` → `/weekly/` | tuple row | WIRED | Present as the 4th row; deck dir NOT in the layout (confirmed by `test_deck_is_not_in_the_published_tree`, passed). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Deck command reproduces committed deck byte-for-byte | `newsletters weekly --spec ... --lanes ... --template ... --author "Tora Ziyal" --out <scratch>` | digest `d61ce632baf2...` == committed sidecar == freshly recomputed committed-file digest | ✓ PASS |
| Merge-block gate fires clean on weekly corpus | `newsletters check --corpus weekly` | "All published surfaces clean — no blockers." exit 0 | ✓ PASS |
| HTML build reproduces committed site byte-for-byte | `newsletters build --corpus weekly --out <scratch>` then diff | no diff | ✓ PASS |
| Full suite has no regression | `.venv/bin/pytest -q` | 871 passed, 0 skipped | ✓ PASS |
| Style/type baselines hold exactly (DEF-15) | `mypy src/`, `black --check` | 15 errors/5 files; 69/33 | ✓ PASS (matches recorded baseline, no NEW failures) |
| No gate-advancing call reachable from weekly path | `grep -rn ".publish(\|.approve(\|open_pull_request(" ...` | 0 hits outside docstrings | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| WKLY-05 | 04-01, 04-02 | Synthetic sample weekly composes/renders under the full gate set | ✓ SATISFIED | See Truths #1, #2, #3 above. |
| WKLY-06 | 04-03 | `docs/weekly.md` operator recipe, non-author, read-only, matching shipped CLI | ✓ SATISFIED | See Truth #4 above. |

No orphaned requirements found — `.planning/REQUIREMENTS.md` maps only WKLY-05/06 to Phase 4, both claimed by plans and both independently satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| — | — | none found | — | `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` grep across all phase-touched files returned zero hits. |

Three Info-severity findings from 04-REVIEW.md remain intentionally **carried** (IN-01 deploy-workflow prose wording, IN-02 no-gate scan is substring-only defense-in-depth, IN-04 `build_weekly_site` cannot override lane config) — all three are Info-level, explicitly disposed as carried follow-ups in the review's own fix-outcomes table, and none blocks any of the 5 ROADMAP success criteria. Not treated as gaps.

### Human Verification Required

#### 1. Real-PowerPoint / Impress open of the committed deck

**Test:** Open `content/weekly/deck/weekly-2374-w41.pptx` in actual Microsoft PowerPoint or LibreOffice Impress.
**Expected:** Deck opens without repair prompts; the DRAFT watermark is visibly present on every slide; no text silently overflows a text box (the P-07 risk the recipe itself calls out).
**Why human:** This verification confirmed the watermark text and `contentStatus=draft` byte exist inside the XML parts (a structural/byte check), but only a real rendering engine can confirm the file displays correctly to a human reader — no automated tool in this environment can substitute for that.

#### 2. First CI-runner green for the `weekly` and `site-integrity` jobs

**Test:** Push this phase's branch and watch GitHub Actions run the `weekly` job (installs `[pptx]`/`[excel]`, runs `tests/test_weekly_golden.py` with a fail-on-skip guard) and the `site-integrity` job (`tests/test_weeklysite.py`) to completion.
**Expected:** Both jobs report success on GitHub's hosted runners.
**Why human:** Local `.venv` execution (performed and green in this verification) cannot substitute for the actual CI runner environment — different OS image, extras-resolution, and the workflow YAML's own conditionals are only proven correct when GitHub actually runs them. This is explicitly pre-recorded as an open item in `WHERE-WE-ARE.md` ("nobody has watched the `pptx` or `weekly` CI jobs [green]") and in this task's own "known recorded PR-review items" list — carried to the PR review, not a phase gap.

### Gaps Summary

No gaps found. All 5 ROADMAP Phase 4 success criteria were independently re-derived against the live repository — re-running gates, re-executing recipe commands, re-computing the deck digest, and reading the committed HTML/pptx bytes directly rather than trusting SUMMARY.md or 04-REVIEW.md narrative. The 7 code-review findings recorded as "fixed" (WR-01..05, IN-03, IN-05) are confirmed live in the current file contents, not merely claimed in the review's fix-outcomes table. The only two open items are pre-recorded, expected, environment-bound observations (real-application open; first hosted-CI green) that this task explicitly named as known, non-gap PR-review carries — hence `status: human_needed` rather than `gaps_found`.

---

_Verified: 2026-08-29T10:39:09Z_
_Verifier: Claude (gsd-verifier)_
