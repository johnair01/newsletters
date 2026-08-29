---
phase: 02-renderer
plan: 03
subsystem: renderer
tags: [pptx, determinism, negative-control, part-digest, ci, github-actions, optional-extra]

# Dependency graph
requires:
  - phase: 02-renderer
    provides: "plan 02-02's two entry points (render_surface_pptx_bytes / render_surface_pptx), _sample_weekly_surface(state), the in-test deck builders and RICH_SLOTS"
  - phase: 02-renderer
    provides: "plan 02-01's promoted normalizer + the four determinism primitives (normalize_opc_zip, part_digest, differing_parts, differing_zipinfo_fields)"
  - phase: 01-specify-de-risk
    provides: "the recorded determinism decision (assertions A/B/C) and the committed synthetic template tests/fixtures/weekly/template.pptx"
provides:
  - "SC-2 proved against the WRITER: two renders across a real 3-second gap are byte-identical, with the negative control asserting the un-normalized pair differs in exactly `date_time`"
  - "assertion A on the writer's un-normalized output — the implementation-independent digest Phase 4's committed==fresh gate inherits"
  - "the end-to-end acceptance test: a real Surface(REPORT, Draft) rendered through the COMMITTED synthetic template, every phase criterion asserted against the reopened written file"
  - "the `pptx` CI job — the first CI job in this repo that installs the `[pptx]` extra (closes W21)"
  - "fill order proved not to be a determinism variable (W18), so Phase 3 knows image ADD order is the one that is"
affects: [03-weekly-compose, 04-sample-corpus-recipe, the v1.3 PR review]

# Tech tracking
tech-stack:
  added: []   # nothing installed; `[test,pptx]` are both pre-existing declared extras
  patterns:
    - "capture-don't-duplicate: the raw (pre-normalization) pair is obtained by wrapping the module-level `normalize_opc_zip` the writer calls, so the control measures the WRITER's own bytes instead of a second implementation of it"
    - "a shared module-scoped fixture pays the load-bearing 3-second sleep ONCE and hands every assertion the same two renders"
    - "a failure message that diagnoses itself: the byte-equality red prints `differing_parts` and `differing_zipinfo_fields` off the raw pair, which separates 'the content moved' from 'the normalizer pins too little'"
    - "one acceptance test asserts ALL FIVE phase criteria against ONE artifact rendered from the SHIPPED template"
    - "a new CI job is additive and isolated: the diff contains no removed line inside any existing job body"

key-files:
  created: []
  modified:
    - tests/test_pptx_writer.py
    - .github/workflows/ci.yml

key-decisions:
  - "The raw pair for the negative control is INTERCEPTED from the writer (a temporary wrapper around `newsletters.pptx_writer.normalize_opc_zip` records the payload `prs.save(BytesIO)` produced) rather than rebuilt in the fixture. The plan allowed either; rebuilding would have been a second writer, drifting from the first exactly as a second normalizer would."
  - "The fixture fails LOUD if it captures anything other than two raw payloads — a writer that stopped routing through the module-level normalizer would otherwise silently turn the negative control into a test of nothing."
  - "`test_draft_and_published_renders_differ` compares `part_digest`, not raw bytes: the implementation-independent comparison, so a red means the CONTENT is identical rather than that two zips happened to compress alike."
  - "The `pptx` CI job is SEPARATE from `bare-install` on the `merge-block` precedent — `[pptx]` is a non-AI optional extra, and `bare-install` stays the canonical AI-free, extra-free source of truth (PKG-03), byte-untouched."

patterns-established:
  - "A determinism green is only worth what its negative control is worth — and the control carries, in its own failure message, the sentence explaining why deleting it as 'redundant' would silently downgrade the proof next to it"
  - "No test may compare a rendered deck to the template: python-pptx's LOAD path re-serializes empty core properties (`<cp:keywords></cp:keywords>` → `<cp:keywords/>`) and emits parts in a different order. Recorded as a comment block in the battery, because Phase 4's golden deck must come from the writer"
  - "A CI job that installs an extra must prove its own command runs 0 skipped locally, or the job is a green that means 'not run'"

requirements-completed: [WKLY-01]

# Metrics
duration: 12min
completed: 2026-08-29
---

# Phase 2 Plan 03: The proof in CI Summary

**The determinism battery that makes the writer's green attributable — two renders three seconds
apart, byte-identical, with the un-normalized pair proved to differ in exactly `date_time` — plus a
sample `Surface(REPORT, Draft)` rendered end to end through the shipped synthetic template, and the
first CI job in this repo that installs `[pptx]` so all five pptx modules run instead of skipping.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-29T05:31:00Z
- **Completed:** 2026-08-29T05:43:00Z
- **Tasks:** 3
- **Files modified:** 2 (0 created)

## The CI job Phase 4 extends

```yaml
  pptx:
    name: pptx renderer + adapter (WKLY-01)
    # ... checkout, setup-python 3.12 ...
      - run: pip install ".[test,pptx]"
      - run: |
          python -m pytest tests/test_pptx_writer.py tests/test_pptx_determinism.py \
                           tests/test_pptx_golden.py tests/test_pptx_adapter.py \
                           tests/test_pptx_loader.py -q
```

**Phase 4 extends THIS job** with the golden `.pptx` committed==fresh gate — it is the only job on
which a pptx test executes rather than skips. Placed after `site-integrity` and before
`import-linter`; the `ci.yml` header comment block now enumerates all five jobs.

## Accomplishments

- **SC-2 is now proved against the writer, not against a spike.** `time_separated_renders` renders
  the same Draft Surface through the same template twice with a real `time.sleep(3)` between them
  (module-scoped, so the suite sleeps once) and hands four payloads to the battery: the two
  normalized renders and the two raw ones.
- **The negative control is re-implemented against the writer's OWN output.** The raw pair is the
  bytes `prs.save(BytesIO)` produced *inside* `render_surface_pptx_bytes`, intercepted one call
  before the normalizer. Asserted: the raw pair is **not** byte-equal, `differing_parts` is `[]`
  (the deck's content never moved — only the container's clock did) and `differing_zipinfo_fields`
  is exactly `["date_time"]`. The failure message says, in so many words, that until this
  inequality holds the byte equality next door proves nothing — and that this is the test most
  likely to be deleted as redundant.
- **Assertion A is computed on the un-normalized pair**, with the reason in the docstring: DEFLATE
  output is zlib-implementation-dependent, so Phase 4's committed==fresh gate must compare
  `part_digest`, never a full-file hash that would be green locally and red in CI on identical
  content.
- **The byte-equality failure diagnoses itself.** A red prints `differing_parts` and
  `differing_zipinfo_fields` computed off the raw pair — the two lists separate "a clock, an
  unstable part order or an unstable rel id leaked into the writer" from "the normalizer is pinning
  too little".
- **Fill order is proved not to be a determinism variable** (W18): the same slots in reversed key
  order produce byte-identical output, which is why the writer iterates `slots.items()` directly.
  The comment names the ordering variable that IS real — image ADD order, Phase 3's to pin.
- **One test asserts all five phase criteria against one artifact from the SHIPPED template.**
  `test_sample_surface_renders_through_the_committed_template` renders a real
  `Surface(REPORT, Draft)` through `tests/fixtures/weekly/template.pptx` into `tmp_path`, reopens
  the written file, and checks: the file exists and is non-empty; `testzip() is None`; the four
  slots read back line for line; **`Footer` is byte-for-byte the template's** (an unprefixed shape
  is not a slot and the renderer must not have touched it); `category` / `content_status` /
  `created` / `modified` / `identifier`; `NL_DRAFT_WATERMARK` present and **last** in z-order; and
  the Surface still `ReviewState.DRAFT`.
- **`test_draft_and_published_renders_differ` is the cheap falsifiability check on the gate
  wiring.** Same template, same content, two gate states, different `part_digest`. If a refactor
  stopped reading `surface.is_published`, every Draft assertion in the module would stay green and
  this is the one test that notices.
- **W21 is closed at the mechanism.** Before this plan, no CI job installed `[pptx]`, so all four
  (now five) pptx modules `importorskip`-skipped themselves on every run — a log with `s` where a
  `.` was expected. The job's exact pytest command was run locally: **117 passed, 0 skipped.**

## Task Commits

1. **Task 1: the determinism battery — double render, negative control, `part_digest`, archive
   validity** — `e2e81b3` (test)
2. **Task 2: a sample Surface renders end to end through the committed template** — `6c6c5dd` (test)
3. **Task 3: the `pptx` CI job** — `c55571e` (ci)

All pushed to `origin/claude/new-session-gw8tik`.

## Files Created/Modified

- `tests/test_pptx_writer.py` — **957 → 1,304 lines.** Gained `COMMITTED_SLOTS`, the `_Renders`
  NamedTuple, the module-scoped `time_separated_renders` fixture, five SC-2 tests and two SC-5
  tests, plus the comment block recording the never-compare-a-render-to-the-template constraint.
  New stdlib imports: `time`, `zipfile`, `typing.NamedTuple`; new package imports:
  `newsletters.pptx_writer` (for the capture) and `differing_parts` / `differing_zipinfo_fields`.
- `.github/workflows/ci.yml` — **156 → 194 lines.** Two purely additive hunks
  (`git diff -U0` shows `@@ -12,0 +13,8 @@` and `@@ -136,0 +145,31 @@`): the header comment block
  now lists five jobs, and the `pptx` job was inserted between `site-integrity` and
  `import-linter`. **No removed line inside any existing job body**; `bare-install` is
  byte-untouched.

## Decisions Made

- **The raw pair is intercepted, not rebuilt.** The plan permitted either route but required the
  raw pair to come from the writer's own code path and to be provably un-normalized. Wrapping
  `newsletters.pptx_writer.normalize_opc_zip` inside a `pytest.MonkeyPatch.context()` satisfies both
  literally: the recorded bytes are the writer's `prs.save(BytesIO)` output, one call before the
  normalizer. Rebuilding an "identical" presentation in the fixture would have been a second
  implementation of the writer, drifting from the first exactly as a second normalizer would — the
  `EPOCH_ZERO` argument applied to test doubles.
- **The interception fails loud.** If the fixture captures anything other than two payloads it
  raises with a message saying the writer no longer routes through the module-level normalizer and
  the control must be retargeted. Without that, a refactor would quietly leave the negative control
  measuring nothing.
- **`part_digest`, not raw bytes, for the Draft-vs-Published comparison** — implementation
  independent, so a red means the content is genuinely identical.
- **The CI job is separate from `bare-install`**, on the `merge-block` precedent recorded in its
  own comment.

## Deviations from Plan

**None — plan executed exactly as written.** The one latitude the plan explicitly offered ("whichever
route is used") was exercised and is documented under Decisions Made above, with the reason.

## Amendments carried to the PR body (NOT resolved here)

Both are raised from 02-02 and remain open by design; they are decisions for the Editor-in-Chief,
not for the writer:

1. **P-04, the `cp:contentStatus` tri-state.** The decision note's mapping is binary (`"draft"` if
   not published else `""`) and is implemented verbatim. `ReviewState` has **three** members, so an
   `IN_REVIEW` Surface produces a deck labelled exactly like a `DRAFT` one. Arguably correct (both
   are "not approved for a reader"); arguably a lost distinction for a reviewer looking at
   File → Info.
2. **W20, `cp:identifier` → `dc:identifier`.** Measured: `core_properties.identifier` serializes as
   `dc:identifier`, not `cp:identifier` as the decision note's field table says. Wording only, no
   code consequence — fix the sentence when the note is next touched.

## The human check that remains open (recorded, not a blocker)

Carried from Phase 1 assumption A8. No `.pptx` consumer exists in this environment
(`libreoffice-core` ships without the Impress filters), so **"a normalized, watermarked deck opens
correctly in real PowerPoint" is still unproven**. Under `workflow.human_verify_mode:
end-of-phase` this is a **PR-review item**, not a mid-phase stop. The Editor-in-Chief opens one deck
produced by `test_sample_surface_renders_through_the_committed_template` and confirms: (i) it opens
clean with no repair prompt; (ii) the DRAFT watermark is visible and legible; (iii) the operator's
bullets and font sizes survived the fill; (iv) a deliberately-overfull slot looks acceptable
(Pitfall 3 — python-pptx never recomputes geometry and `fit_text` is banned, so overflow is a
visual-only failure no automated check can see); (v) the generated-by marker is readable in
File → Info. That one look closes A8, A4 and Pitfall 3 together.

## Issues Encountered

- **`black` reformatted the task-2 additions.** Caught by running `black --check` as part of the
  gate rather than by trusting the test green; reformatted and re-run (26 passed) before the commit.
- **`tests/test_pptx_writer.py` still fails `isort --check-only`, exactly as it did before this
  plan.** Verified by extracting the file at `c8abc9c` (pre-plan) and diffing isort's proposed
  output against the current one: isort wants the SAME black-incompatible grid-wrapped form of the
  SAME two `from newsletters ...` statements in both. This is DEF-15 (the repo declares isort with
  no `profile = "black"`), not a new failure. Adding two names to an already-offending statement
  neither creates nor worsens it.
- **The `pptx` job's first CI green cannot be observed from here** — no `gh` CLI in this
  environment. What IS proven is the job's exact pytest command, run locally: 117 passed,
  **0 skipped**. The first green is a PR-review confirmation, stated rather than assumed.

## Verification (run once each, independently — "the agent says green" is not green)

| Gate | Result |
|------|--------|
| `.venv/bin/python -m pytest -q` | **595 passed, 64 skipped** (baseline 588/64; +7 tests, 0 regressions) |
| `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` | **26 passed, 0 skipped**, 3.89 s |
| the `pptx` job's exact command (5 modules) | **117 passed, 0 skipped** — the job runs the renderer, it does not skip it |
| `.venv/bin/python -m pytest tests/test_pptx_determinism.py -q` | **7 passed** — the Phase 1 negative control untouched and still green |
| `.venv/bin/lint-imports` | 2 contracts **KEPT**, 0 broken |
| `newsletters check --corpus rev1 / work / module` | all three: "All published surfaces clean — no blockers" |
| `_record_determinism_evidence.py --check` | **exit 0** — 6 fields re-verified; `raw_bytes_equal: False` |
| `git diff --exit-code -- src/newsletters/semantic.py content/ tests/fixtures/pptx/ tests/fixtures/weekly/template.pptx` | **exit 0** — the gate and every committed binary unchanged |
| `.venv/bin/mypy src/newsletters/pptx_writer.py` | Success, no issues |
| `.venv/bin/black --check tests/test_pptx_writer.py` | clean |
| `.venv/bin/isort --check-only tests/test_pptx_writer.py` | fails — **pre-existing DEF-15**, proved identical at `c8abc9c` |
| `python -c "yaml.safe_load(ci.yml)"` | jobs = `['bare-install', 'import-linter', 'merge-block', 'pptx', 'site-integrity']` |
| `git diff -- .github/workflows/ci.yml \| grep '^-'` | one line: the diff header `--- a/...`. **Zero removed content lines** |
| `grep -n "part_digest(COMMITTED_TEMPLATE\|part_digest(template" tests/test_pptx_writer.py` | no matches (exit 1) — no test compares a render to the template |
| `git status --porcelain` | clean; no stray `.pptx` anywhere |

## Known Stubs

None. Every test added here asserts against bytes or a reopened file; nothing is marked `xfail`,
skipped or left as a placeholder, and no assertion is written against a value the test itself
supplied.

## Threat Flags

None. No new network endpoint, auth path or schema change at a trust boundary. The plan's five
registered threats are all mitigated as planned:

- **T-02-16** (bare-install scope creep): `git diff -U0` shows two purely additive hunks; no removed
  line inside any existing job body; `bare-install` byte-untouched and still `.[test]` only.
- **T-02-17** (a green that never ran the renderer): the job's own command reports **0 skipped**
  locally, so a silently-skipping job cannot pass as green.
- **T-02-10** (operator data in the shipped template): the committed template is rendered
  *through*, never regenerated; `git diff --exit-code -- tests/fixtures/` exits 0, and both
  `test_committed_template_is_scrubbed_and_normalized` and the corpus guard now run in the new job.
- **T-02-18** (false determinism green): assertion C is re-implemented against the writer's own raw
  output, with a failure message stating that without it assertion B proves nothing.
- **T-02-SC** (package installs): the job installs only `.[test,pptx]` — both pre-existing,
  declared extras. No package entered the milestone; nothing `[ASSUMED]` or `[SLOP]` was installed.

## User Setup Required

None — no external service, no install, no credential.

## Next Phase Readiness

**Phase 2 is functionally complete; WKLY-01's five success criteria are met.** Phase 3 inherits:

- a writer whose determinism is proved *with a control*, so a Phase 3 change that introduces
  non-determinism (image add order is the live risk, and this plan proves fill order is not) gets a
  red that names which of the two causes it is;
- `part_digest` as the assertion Phase 4's committed==fresh gate uses, exercised on real writer
  output rather than on a spike's;
- the `pptx` CI job to extend with the golden-deck gate — the only job where a pptx test executes;
- an end-to-end acceptance test against the SHIPPED template, so "the repo ships a template a
  Surface renders through" is a test rather than a claim.

**Open, and deliberately so:** the real-PowerPoint open (A8, PR review), the P-04 tri-state
amendment and the W20 wording correction (both PR body), and the `pptx` job's first observed CI
green (no `gh` in this environment).

---
*Phase: 02-renderer*
*Completed: 2026-08-29*

## Self-Check: PASSED

Both modified files exist on disk at the stated sizes (`tests/test_pptx_writer.py` 1,304 lines,
`.github/workflows/ci.yml` 194 lines), and all three task commits (`e2e81b3`, `6c6c5dd`, `c55571e`)
are present in `git log` and pushed to `origin/claude/new-session-gw8tik`. No file was created by
this plan, and no committed binary changed.
