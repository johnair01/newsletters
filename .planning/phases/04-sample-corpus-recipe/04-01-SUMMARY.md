---
phase: 04-sample-corpus-recipe
plan: 01
subsystem: content
tags: [weekly, corpus, pptx, part_digest, ledger, honesty-panel, cli, typer, email-adapter]

# Dependency graph
requires:
  - phase: 02-renderer
    provides: "pptx_writer.render_surface_pptx / render_surface_pptx_bytes / part_digest (stdlib-only) and the committed synthetic template"
  - phase: 03-weekly-compose
    provides: "weeklyspec.load_weekly_spec / build_weekly_report / weekly_slots, the four weekly block kinds and their render branches, swimlane.load_swimlanes"
provides:
  - "content/weekly/ — a fourth self-contained committed corpus (spec · .eml · PNG · template copy · R-001 ledger · site/ · deck/ + digest)"
  - "src/newsletters/weeklysite.py — build_weekly_surfaces / build_weekly_site / build_weekly_deck, the corpus builder seam"
  - "`newsletters weekly` — the one operator command that renders a deck + its integrity sidecar"
  - "tests/_corpus_scan.py — the promoted synthetic-content scanner, shared by the module and weekly corpora"
  - "tests/test_weeklysite.py — the stdlib-only weekly corpus suite (13 tests, no [pptx] anywhere)"
affects: [04-02 publish/CLI corpus wiring, 04-03 docs/weekly.md recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Sibling corpus builder (weeklysite mirrors modulesite) — one builder per byte-stable corpus"
    - "Two-tier integrity for a committed binary: stdlib-only part_digest sidecar (tier 1) + [pptx]-gated fresh==committed (tier 2, plan 04-02)"
    - "Promotion over a second copy, extended to tests/ for the first time (tests/_corpus_scan.py)"

key-files:
  created:
    - src/newsletters/weeklysite.py
    - content/weekly/weekly-2374-w41.yml
    - content/weekly/inbox/berth-rota-thanks.eml
    - content/weekly/assets/ring-berth-utilisation.png
    - content/weekly/template.pptx
    - content/weekly/ids.json
    - content/weekly/site/ (weekly-2374-w41.html, library.html, fonts/)
    - content/weekly/deck/weekly-2374-w41.pptx
    - content/weekly/deck/weekly-2374-w41.pptx.digest
    - tests/_corpus_scan.py
    - tests/test_weeklysite.py
  modified:
    - src/newsletters/cli.py
    - tests/test_modulesite.py
    - tests/test_abstraction_guard.py

key-decisions:
  - "[Phase 4-01]: The load-and-compose sequence is ONE private helper (`weeklysite._load_and_compose`) shared by build_weekly_surfaces and build_weekly_deck, not two copies. weekly_slots(load, surface) checks its disclosure lines against surface.missing, so a deck composed from a separately-built load would be checking one record's slides against another record's honesty panel."
  - "[Phase 4-01]: build_weekly_surfaces / build_weekly_deck take an optional `lanes_path`, because the plan's own CLI surface declares `--lanes` and the documented builder signature had nowhere to put it. Additive keyword; structural discovery is still the default."
  - "[Phase 4-01]: The byline REFUSES rather than defaults. `_resolve_author` takes the explicit argument, else the spec's `config: author:`, else raises a teaching ValueError naming both. A fabricated default byline would be an abstraction-guard leak AND an unsigned record wearing somebody's name."
  - "[Phase 4-01]: The confidentiality scanner's ONE allowance is the RFC 6761 `@example.invalid` domain, and it carries TWO planted arms — a real-looking name, and a NON-reserved address (`ops@starfleet.int`) that must still trip THROUGH the allowance. Without the second arm the allowance could silently widen into 'ignore every address'."
  - "[Phase 4-01]: The deck digest assertion carries a non-vacuity arm that digests a DIFFERENT committed .pptx (content/weekly/template.pptx) and asserts it does NOT match — otherwise the tier-1 gate could be comparing a string to itself."
  - "[Phase 4-01]: isort/black hygiene was fixed on this plan's files ONLY (no repo-wide reformat, DEF-15 stays maintainer-gated): the multi-line `from newsletters.weeklyspec import (...)` was replaced by module-level access, because that parenthesized shape is exactly what isort and black disagree about."

patterns-established:
  - "Corpus builder seam: discovery by sorted non-recursive glob, ledger at the FIXED committed path (never out_dir), pages-then-library return order, reused worksurface._emit_fonts"
  - "Deck as a THIRD entry point with the [pptx] import inside its body — asserted by a sys.modules check after importing weeklysite AND cli"
  - "Disclosures located in tests by the composer's OWN format string (NO_KPIS / specspan.absent / _ASSET_PROVENANCE_ABSENT), never by a retyped sentence"

requirements-completed: [WKLY-05]

# Metrics
duration: 22min
completed: 2026-08-29
---

# Phase 4 Plan 01: Sample corpus + builder Summary

**A fourth committed corpus (`content/weekly/`) whose fabricated weekly composes to a Draft `Surface(REPORT)` at `R-001`, renders all three planted absences into the HTML honesty panel, and ships a `.pptx` deck whose `part_digest` sidecar is checkable on a bare install.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-29T09:16Z
- **Completed:** 2026-08-29T09:38Z
- **Tasks:** 3 (+1 hygiene commit)
- **Files created/modified:** 24 (11 created + 3 modified + 10 vendored font files under `content/weekly/site/fonts/`)

## Accomplishments

- **The sample is honest by construction.** All three planted absences reach the reviewer, not just the model: the KPI-less lane comes from the *already committed* `content/module` config (real content, not content invented to make a demo look honest), the source-less recognition sits beside a resolvable one so the absence row means something, and the provenance-incomplete asset is refused *before* the file read — so it needs no file on disk at all.
- **The deck's integrity is checkable without the optional extra.** `part_digest` is `zipfile` + `hashlib`, so the tier-1 tamper gate fires on every install including `bare-install` and `site-integrity`. The committed deck was produced by the same command the recipe will document.
- **One scanner, two corpora.** The synthetic-content scanner was PROMOTED (not copied) into `tests/_corpus_scan.py` — the first shared test helper in this repo — and `tests/test_modulesite.py` passes with the SAME test count across the move.
- **The lazy boundary is real, not documented.** Importing `newsletters.weeklysite` and `newsletters.cli` leaves `pptx` absent from `sys.modules`; `lint-imports` stays 2 kept / 0 broken and `mypy` reports 0 errors in the new module.

## Task Commits

1. **Task 1: the synthetic corpus fixtures + the promoted scanner** — `c323514` (feat)
2. **Task 2: weeklysite.py, the committed HTML corpus and its R-001 ledger** — `3e24f2a` (feat)
3. **Task 3: the committed deck, its digest sidecar, and `newsletters weekly`** — `d54f9f3` (feat)
4. **Hygiene: isort green on every file this plan touches** — `663e00b` (style)

## The three planted absences, verbatim from `surface.missing`

Captured by executing `build_weekly_surfaces()[0]`, not transcribed from the plan:

```
section 'MOR/IQ tools & defect projects' declares no KPIs — strip omitted
field 'recognitions[1].source' is absent or empty — disclosed, never fabricated
asset 'manifest-annex-photo': provenance field 'folder' is absent — the minimum is folder + date + event label; disclosed, never placed
```

Two more rows come along for free and make the panel read like a real week rather than a demo:

```
field 'team[1].photo' is absent or empty — disclosed, never fabricated
KPI 'defect-rate' declares period movement but only one endpoint is usable — no delta derived (never a fabricated 0)
```

Each of the three is asserted present in `missing[]` **and** `html.escape`d into the rendered page, located by the composer's own format string (`compose.NO_KPIS`, `specspan.absent`, `weeklyspec._ASSET_PROVENANCE_ABSENT`) — no disclosure sentence is typed into the test or the fixture.

## The exact `newsletters weekly` invocation and its output

The committed deck was produced by the shipped command, not by an ad-hoc script:

```
$ .venv/bin/newsletters weekly --spec content/weekly/weekly-2374-w41.yml \
                   --lanes content/module/module-a.yml \
                   --template content/weekly/template.pptx \
                   --author "Tora Ziyal" \
                   --out content/weekly/deck/weekly-2374-w41.pptx
  content/weekly/deck/weekly-2374-w41.pptx
  content/weekly/deck/weekly-2374-w41.pptx.digest

rendered 1 Draft deck + its part_digest -> content/weekly/deck (digest: d61ce632baf29e9115e833f88e97f55d84665d0e5930bdad66fc931cb7396259)
```

- deck: 28,885 bytes, sha256 `64d296e52598ad7d483af6268f387e3af6ed46cfaa227866823b34f2f921c147`
- sidecar: 65 bytes (64 hex + trailing newline), `d61ce632baf29e9115e833f88e97f55d84665d0e5930bdad66fc931cb7396259`

## Measured numbers against the recorded baselines

| Gate | Baseline (04-RESEARCH, measured 2026-08-29) | After this plan |
|---|---|---|
| `pytest -q` | 837 passed / **0 skipped** | **850 passed / 0 skipped** (+13, all new) |
| `tests/test_modulesite.py` across the scanner promotion | **9 passed** | **9 passed** (same count — a move, not a rewrite) |
| `lint-imports` | 2 kept / 0 broken | **2 kept / 0 broken** |
| `mypy src/newsletters` | 15 errors in 5 files | **15 errors in 5 files** (0 in `weeklysite.py`, 0 in `cli.py`) |
| `black --check src tests` | 69 would reformat / 29 clean | **69 would reformat / 32 clean** (the 3 new files are clean; no pre-existing file reformatted) |
| `isort --check-only` | fails on several pre-existing files (DEF-15) | **no new failure** — clean on `_corpus_scan.py`, `test_weeklysite.py`, `test_modulesite.py`, `weeklysite.py`; `cli.py`'s pre-existing failure is unchanged (this plan added no import to it) |
| `git diff -- content/{module,rev1,work}/ids.json` | clean | **clean** (append-only held; `content/weekly/ids.json` is the only added ledger) |
| `pytest tests/test_semantic_gate_frozen.py` | green | **11 passed** — `semantic.py` untouched |
| `newsletters check --corpus {rev1,work,module}` | all clean | **all clean** |
| `git diff --stat -- src/newsletters/` | — | **2 files** (`weeklysite.py` new, `cli.py` +69 insertions / 0 deletions) |

## Files Created/Modified

- `src/newsletters/weeklysite.py` — the builder seam: `build_weekly_surfaces` / `build_weekly_site` / `build_weekly_deck`, plus the shared `_load_and_compose` and the two structural discovery helpers. Module level is stdlib + in-package only.
- `src/newsletters/cli.py` — the flat `weekly` command (5 options, lazy import, three stated properties). Pure insertion: 69 added lines, 0 deleted.
- `content/weekly/weekly-2374-w41.yml` — the authored synthetic weekly; header comment names the three planted absences so a reader knows they are deliberate.
- `content/weekly/inbox/berth-rota-thanks.eml` — the resolvable recognition's source; every address `@example.invalid`, fixed `Date:` header.
- `content/weekly/assets/ring-berth-utilisation.png` — the one placed asset (byte-copy of the fixture PNG, re-hashed into the spec).
- `content/weekly/template.pptx` — byte-copy of `tests/fixtures/weekly/template.pptx` (P-06), guarded by a test.
- `content/weekly/ids.json` — the corpus's own append-only ledger, `R-001`.
- `content/weekly/site/` — the committed HTML (report page + library + self-hosted fonts incl. 3 OFL files).
- `content/weekly/deck/weekly-2374-w41.pptx` + `.digest` — the shipped deck and its tier-1 tamper sidecar, outside `site/` and therefore unreachable by `assemble_site`.
- `tests/_corpus_scan.py` — the promoted scanner (`REAL_LOOKING_LITERALS`, `EMAIL_RE`, `scan_real_looking`), comments carried verbatim.
- `tests/test_weeklysite.py` — 13 tests, stdlib only.
- `tests/test_modulesite.py` — imports the promoted names; only the module-specific `_FABRICATED_MARKERS` allowlist stayed.
- `tests/test_abstraction_guard.py` — `_WEEKLYSITE_CORPUS_VALUES` added to the deny union.

## Decisions Made

See `key-decisions` in the frontmatter. The two worth reading twice:

- **The byline refuses rather than defaults.** Every other absence in this system is *disclosed*; a byline is different, because a name on a record is a claim about who stands behind it. So `_resolve_author` raises a teaching `ValueError` naming both `config: author:` and `--author` rather than inventing anything.
- **The `config:` value that becomes the byline appears nowhere else in the corpus.** That is not decoration: `test_config_values_never_claimed` walks every `Claim` reachable from the surface structurally (not by naming block kinds, so a future block kind cannot escape the guard) and asserts no config leaf reached one. Authoring the byline into a highlight would have turned a metadata binding into a claim and correctly failed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `build_weekly_deck` had nowhere to put the plan's own `--lanes` option**
- **Found during:** Task 3 (the CLI command)
- **Issue:** The plan specifies a `--lanes` CLI option that "falls through to the builder's structural discovery", but the documented `build_weekly_deck` signature has no lanes parameter — the option would have been accepted and silently ignored, which is worse than not offering it.
- **Fix:** Added an optional `lanes_path` keyword to `build_weekly_surfaces` and `build_weekly_deck` (additive; discovery is still the default when it is `None`).
- **Files modified:** `src/newsletters/weeklysite.py`, `src/newsletters/cli.py`
- **Verification:** `newsletters weekly --lanes content/module/module-a.yml ...` produced the committed deck; `weekly --help` lists all five options and `test_weekly_command_is_registered` asserts it.
- **Committed in:** `d54f9f3`

**2. [Rule 2 - Missing Critical] One load-and-compose sequence, not two**
- **Found during:** Task 3
- **Issue:** The plan says `build_weekly_deck` should "rebuild the load exactly as `build_weekly_surfaces` does". Two literal copies of that sequence would drift exactly as two normalizers would — and the failure mode is not cosmetic: `weekly_slots(load, surface)` validates its disclosure lines against `surface.missing`, so two drifting loads would eventually check one record's slides against another record's honesty panel.
- **Fix:** Extracted the private `_load_and_compose(...) -> (WeeklySpecLoad, Surface)` used by both entry points, per this repo's promotion norm.
- **Files modified:** `src/newsletters/weeklysite.py`
- **Verification:** All 13 weekly tests green; deck rendered through the shared path; `mypy` 0 errors.
- **Committed in:** `d54f9f3`

**3. [Rule 3 - Blocking] Two NEW isort failures were attributable to this plan**
- **Found during:** the plan-level gate run
- **Issue:** `tests/test_modulesite.py` passed `isort --check-only` at the plan's base commit and my promoted-scanner import broke it; `tests/test_weeklysite.py` was new and failed. "No NEW failures" is only checkable if new files are clean.
- **Fix:** Moved the `_corpus_scan` import into the third-party block (where isort classifies it) and replaced the parenthesized `from newsletters.weeklyspec import (...)` with module-level access, so no import in this plan's files is a multi-line parenthesized one — the exact shape isort and black disagree about until DEF-15 is paid off. No repo-wide reformat.
- **Files modified:** `tests/test_weeklysite.py`, `tests/test_modulesite.py`
- **Verification:** `isort --check-only` and `black --check` both clean on all four files this plan creates or touches under `tests/`/`src/`; 22 tests still green.
- **Committed in:** `663e00b`

**4. [Ordering, not a rule] `build_weekly_deck` landed in the Task 2 commit**
- **Issue:** The plan assigns `build_weekly_deck` to Task 3, but it lives in `weeklysite.py`, which Task 2 creates. Splitting one new file across two commits would have committed a module whose docstring described an entry point it did not have.
- **Consequence:** none functional — the deck, its digest, the CLI command and the tier-1 gate are all in `d54f9f3` (Task 3), and `3e24f2a` (Task 2) is green on its own.

**5. [Scope discipline, worth recording] A `black` run reformatted two pre-existing `cli.py` lines; reverted**
- Running `black` on `cli.py` (which was already non-black-clean at baseline, part of the 69) reformatted two `typer.echo` lines I had not touched. Reverted by hand so the `cli.py` diff is a pure 69-line insertion with **0 deletions** — an unrelated reformat inside a reviewed file is noise a reviewer has to read past, and DEF-15 is maintainer-gated.

---

**Total deviations:** 3 auto-fixed (2 blocking, 1 missing-critical) + 2 recorded-only.
**Impact on plan:** No scope creep. Every auto-fix was needed to make a documented interface honest or a declared gate checkable; nothing outside this plan's files was changed.

## Issues Encountered

- **The `.eml` did trip the confidentiality scanner exactly as research predicted** — and the fix (`@example.invalid` + a documented, narrow allowance) was designed in before the first run, so it never went red. What *did* need care is the allowance's own non-vacuity: subtracting "hits ending in the reserved domain" is one refactor away from "ignore every address", so a second planted arm (`ops@starfleet.int`) asserts a non-reserved address still trips **through** the allowance.
- **Nothing else surprised.** The three absences appeared verbatim as research captured them; `R-001` was assigned on the first build; the committed HTML equalled a fresh build on the first attempt.

## Known Stubs

None. Every committed file in `content/weekly/` is produced or consumed by a shipped code path, and every artifact this plan declares exists on disk.

## Known Limitation (recorded, deliberately not patched)

`weeklyspec.build_weekly_report` sets `traces=[load.source]`, so claims contributed by the bindings and by the resolved `.eml` recognition reference `Source`s the `Surface` does not carry. Measured consequence: no rendering break, no false STALE, no `href="None"` in the rendered page (verified: 0 occurrences in both committed pages). It would matter only if this Draft sample were advanced to Published, where a lane-config drift would be invisible to `review_blockers`. Phase 3 source is frozen (W0-4); this is recorded in `weeklysite.py`'s module docstring, not patched.

## Next Phase Readiness

Ready for plan 04-02 (publish layout + `--corpus weekly` CLI wiring + the Records strips + the `[pptx]`-gated tier-2 golden gate + the CI/deploy lines). This plan was deliberately safe alone: `assemble_site` ignores a directory it does not know about, so `content/weekly/` is committed and green without any other file in the repo moving.

Carried, unchanged: the real-PowerPoint open and the first CI green of the `pptx`/`weekly` jobs remain PR-review items (no `.pptx` consumer and no `gh` CLI in this environment).

## Self-Check: PASSED

All 12 declared artifacts exist on disk (`content/weekly/site/fonts/` carries the three `OFL-*.txt`),
and all four commit hashes (`c323514`, `3e24f2a`, `d54f9f3`, `663e00b`) resolve in `git log`.

---
*Phase: 04-sample-corpus-recipe*
*Completed: 2026-08-29*
