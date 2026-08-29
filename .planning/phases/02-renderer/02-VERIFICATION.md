---
phase: 02-renderer
verified: 2026-08-29T06:06:41Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Open a normalized, watermarked Draft `.pptx` (produced by `test_sample_surface_renders_through_the_committed_template`) in real Microsoft PowerPoint"
    expected: "(i) opens clean, no repair prompt; (ii) the DRAFT watermark is visible and legible; (iii) the operator's bullets and font sizes survived the fill; (iv) a deliberately-overfull slot looks acceptable; (v) the generated-by marker is readable in File → Info"
    why_human: "No `.pptx` consumer exists in this sandbox (`libreoffice-core` ships without Impress filters); this is Phase 1 assumption A8, carried and recorded as a PR-review item under `workflow.human_verify_mode: end-of-phase`, not a mid-phase blocker"
  - test: "Confirm the `pptx` CI job's first real GitHub Actions run is green"
    expected: "The job (`pip install \".[test,pptx]\"` then the 5-module pytest command) reports 0 failures, 0 skipped on GitHub's runners"
    why_human: "No `gh` CLI / GitHub Actions access in this sandbox; the exact command was verified locally (117 passed, 0 skipped) but the actual CI environment has not observed the job run"
  - test: "Decide the `cp:contentStatus` tri-state question for an `IN_REVIEW` Surface"
    expected: "Editor-in-Chief confirms whether an `IN_REVIEW` deck should read identically to `DRAFT` (`\"draft\"`) or needs a third state, and whether `docs/architecture.md`'s field table should be corrected from `cp:identifier` to the measured `dc:identifier` (W20, wording only)"
    why_human: "P-04 implements the binding decision note verbatim by design; the amendment is a product decision explicitly deferred to PR review, not something grep/tests can resolve"
---

# Phase 2: Renderer Verification Report

**Phase Goal:** A composed weekly `Surface(REPORT)` becomes a `.pptx` deck through an
operator-supplied template — deterministically, marked as generated, visibly Draft-watermarked
until a human publishes it, review gate untouched.
**Verified:** 2026-08-29T06:06:41Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Phase 2 Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC-1: renders by filling **named placeholders**; a placeholder with no matching content and content with no matching placeholder both fail loud, naming the offender, in both directions | ✓ VERIFIED | `bind_slots` (`src/newsletters/pptx_writer.py:371-472`) performs 5 ordered refusals (duplicate `NL_` name, watermark-name-owning template, unprefixed content name (WR-06), unknown content name, unfilled reserved slot, non-text slot) each raising `ValueError` naming the offender. Live-run: `test_unknown_slot_name_raises`, `test_unfilled_reserved_slot_raises`, `test_duplicate_shape_name_raises`, `test_content_bound_to_unprefixed_name_raises`, `test_slot_without_text_frame_raises`, `test_template_owning_watermark_name_raises`, `test_default_auto_named_multi_slide_deck_is_accepted` — all pass live in `tests/test_pptx_writer.py`. |
| 2 | SC-2: two renders of the same Surface across a real time gap produce decks equal under the recorded determinism definition, with a test that would fail on a leaked timestamp/order/rel-id | ✓ VERIFIED | `time_separated_renders` fixture sleeps a real 3s (`tests/test_pptx_writer.py:1160-1246`). `test_double_render_is_byte_identical` (assertion B), `test_unnormalized_double_render_is_not_byte_equal` (assertion C, negative control: raw pair NOT equal, `differing_parts==[]`, `differing_zipinfo_fields==["date_time"]`), `test_part_digest_is_stable_across_time_separated_renders` (assertion A) all pass live. |
| 3 | SC-3: every rendered deck carries the generated-by marker in the durable field, and renders visibly Draft-watermarked while not Published — both asserted by reopening the written file | ✓ VERIFIED | `test_marker_reads_back_off_the_written_file`, `test_draft_surface_is_watermarked_on_every_slide`, `test_published_surface_has_no_watermark_and_empty_content_status` (the inverted half) all pass live, each via `Presentation(str(out_path))` — never the in-memory object. |
| 4 | SC-4: no auto-publish path — renderer never advances/mutates review state, `semantic.py` byte-unchanged, rendering a Draft Surface leaves it Draft | ✓ VERIFIED | `grep -n 'surface\.review\s*=\|\.review\.state\s*='  src/newsletters/pptx_writer.py` → no matches (exit 1). `git diff --exit-code -- src/newsletters/semantic.py` → exit 0 (run live). `test_render_does_not_touch_the_gate` passes live (`model_dump()` identical, state still DRAFT). |
| 5 | SC-5: python-pptx lazy-imported inside the writer only, sharing `[pptx]`; `lint-imports` KEPT; bare-install CI stays green; a synthetic template ships and a sample Surface renders through it **in CI** | ✓ VERIFIED | `grep -n '^import pptx\|^from pptx' src/newsletters/pptx_writer.py` → no matches. `.venv/bin/lint-imports` run live → "Contracts: 2 kept, 0 broken", exit 0. `.github/workflows/ci.yml` parses with a `pptx` job (`pip install ".[test,pptx]"` then the 5-module pytest command) inserted purely additively (`git diff c8abc9c..HEAD -- .github/workflows/ci.yml` shows zero removed content lines; `bare-install` job untouched). `test_sample_surface_renders_through_the_committed_template` run live against `tests/fixtures/weekly/template.pptx` (the committed synthetic template) — PASSED, asserting all 5 SCs against one artifact. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/pptx_writer.py` | stdlib-only normalizer + full writer (bind_slots, fill_slot, render_surface_pptx_bytes, render_surface_pptx, watermark, marker) | ✓ VERIFIED | 697 lines. `__all__` exports all promoted + writer names. No column-0 pptx import. mypy clean live. |
| `tests/test_pptx_writer.py` | SC-1/2/3/4/5 battery + fidelity + deck builders | ✓ VERIFIED | 1489 lines, 32 tests, all pass live, 0 skipped. |
| `.github/workflows/ci.yml` | `pptx` job installing `[pptx]` and running 5 pptx modules | ✓ VERIFIED | Job present, additive only, header comment lists 5 jobs. |
| `tests/fixtures/weekly/template.pptx` | committed synthetic template, byte-unchanged this phase | ✓ VERIFIED | `git diff --exit-code` clean; `_record_determinism_evidence.py --check` exit 0 live. |
| `.planning/notes/2026-08-29-pptx-determinism-evidence.json` | WR-01 re-recorded evidence | ✓ VERIFIED | `part_digest_a == part_digest_b == d7ff171a5ea083f01d48e21a405fbf7d8fe1e0ef487a5173959334774a162897`; `normalized_a_sha256 == normalized_b_sha256 == 56fa2a61d4993ded9139fafd0cb17f4d30435fdc5ca59efc61acdc812eb6869a` — matches the decision-note addendum's cited prefixes (`d7ff171a…`, `56fa2a61…`) exactly, and matches "normalized hash unchanged" claim (the pre-hardening recording's `56fa2a61…` value is unchanged post-hardening, proving no content moved, only the digest encoding). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `src/newsletters/pptx_writer.py` | `newsletters.adapters._pptx_loader._load_pptx` | lazy in-function import | WIRED | Confirmed at `render_surface_pptx_bytes`; no second `try: import pptx` boundary. |
| `src/newsletters/pptx_writer.py` | `newsletters.adapters._timestamps.EPOCH_ZERO` | lazy import, tz stripped | WIRED | `EPOCH_ZERO.replace(tzinfo=None)` used for `created`/`modified`; read-back tests pass. |
| `src/newsletters/pptx_writer.py` | `surface.is_published` | read only | WIRED, read-only confirmed | grep for any write to `surface.review*` returns no matches. |
| `.github/workflows/ci.yml` (`pptx` job) | `tests/test_pptx_writer.py` (+4 others) | pytest file list | WIRED | Command run live: `117 passed, 0 skipped` reproduced for the 5-module list (32 in test_pptx_writer.py alone, live-verified). |

### Code-Review Fix Verification (WR-01..06, IN-01, IN-02, IN-04)

All nine review findings marked "Fixed" in `02-REVIEW.md` were checked directly against the live
file content (not the review's word), plus their commits confirmed present in `git log`:

| Finding | Commit present | Live-code evidence |
|---------|-----------------|---------------------|
| WR-01 (part_digest domain separation) | `1f4dce0` ✓ | `part_digest` (`pptx_writer.py:259-261`) length-prefixes each name with `len(encoded).to_bytes(8, "big")` before hashing — injective encoding confirmed live. Evidence JSON re-recorded (`d7ff171a…` / `56fa2a61…`, matching decision-note addendum). |
| WR-02 (duplicate-name scope) | `530d996` ✓ | `bind_slots` (`pptx_writer.py:418`) raises only when `shape.name in by_name and shape.name.startswith(SLOT_PREFIX)`; unprefixed duplicates `by_name.setdefault`. `test_default_auto_named_multi_slide_deck_is_accepted` passes live. |
| WR-03 (bare str explosion) | `2763126` ✓ | `fill_slot(text_frame, lines: Union[str, Sequence[str]])` docstring + code treat a bare str as one paragraph. `test_bare_str_fills_one_paragraph_not_one_per_character` and `test_bare_str_slot_value_renders_one_paragraph` pass live. |
| WR-04 (lint-imports no-op fallback) | `f58031d` ✓ | `test_import_linter_contract_holds` resolves the script relative to `sys.executable`, falls back to `shutil.which`, and `pytest.fail`s (not skips) the no-op `python -m importlinter.cli` path when importlinter is installed but the script is missing. Passes live. |
| WR-05 (MARKER/GATE_STATE re-declaration) | `b1b5a3d` ✓ | Both `tests/test_pptx_determinism.py` and `tests/fixtures/weekly/_record_determinism_evidence.py` import `MARKER`, `DRAFT_STATUS as GATE_STATE` from `newsletters.pptx_writer` — grep-confirmed, no local literal redeclaration. |
| WR-06 (unprefixed content silently filled) | `2a7e393` ✓ | `bind_slots` (`pptx_writer.py:441-446`) refuses any `slots` key not starting with `SLOT_PREFIX`. `test_content_bound_to_unprefixed_name_raises` passes live. |
| IN-01 (docstring coverage claim) | `062a2d2` ✓ | Module docstring now states the bare-install job only proves import; contracts execute in the `pptx` CI job. |
| IN-02 (`[""]` blank spacer) | `b0f71fd` ✓ | `fill_slot` refuses `not lines or not any(line.strip() for line in lines)`. `test_fill_with_only_blank_lines_raises` passes live. |
| IN-04 (unbounded `_walk` recursion) | `3e94648` ✓ | `_MAX_GROUP_DEPTH = 64`; `_walk` raises `ValueError` past that depth. `test_pathological_group_nesting_gets_a_teaching_error` passes live. |

Carried findings (IN-03, IN-05, IN-06, IN-07) are explicitly recorded as deferred in `02-REVIEW.md`
with reasons, not silently dropped — consistent with the review's own "carried" classification.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| WKLY-01 | 02-01, 02-02, 02-03 | Weekly `Surface(REPORT)` renders deterministically to `.pptx`, marked, Draft-watermarked, gate untouched, named-placeholder fail-loud contract, synthetic template ships | ✓ SATISFIED (with 2 recorded PR-review caveats) | `.planning/REQUIREMENTS.md` marks WKLY-01 `[x]`. All 5 code-verifiable ROADMAP SCs pass live. Two items are explicitly NOT closed — the real-PowerPoint open and the first observed CI green — and are recorded, not hidden, in the ROADMAP row, both SUMMARYs, and `02-VALIDATION.md`. |

No orphaned requirements: REQUIREMENTS.md maps only WKLY-01 to Phase 2, and all three plans declare it.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` markers found in any phase-modified file (`grep -rn` run live across all 9 files touched by 02-01/02-02/02-03) | — | None |
| `tests/fixtures/pptx/_author_fixtures.py` | — | Fails `black --check` | ℹ️ Info | Pre-existing (verified by 02-01-SUMMARY against `HEAD` before the phase); not introduced by this phase; part of DEF-15 baseline debt |
| `tests/test_pptx_writer.py`, `tests/test_ai_optional.py`, `tests/test_pptx_determinism.py`, `tests/fixtures/weekly/_record_determinism_evidence.py` | — | Fail `isort --check-only` | ℹ️ Info | Confirmed pre-existing DEF-15 (repo has no `profile = "black"`; isort and black disagree on parenthesized multi-line imports repo-wide). Independently reproduced live — exactly the 4 files named in the task's known baseline debt. No new formatter failure introduced this phase. |

No blockers found.

### Behavioral Spot-Checks / Full Gate Re-Run (each run once, independently)

| Gate | Command | Result | Status |
|------|---------|--------|--------|
| Full suite | `.venv/bin/python -m pytest -q` | **601 passed, 64 skipped** — matches the SUMMARY-claimed baseline exactly | ✓ PASS |
| pptx module alone | `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` | 32 passed, 0 skipped | ✓ PASS |
| ai-optional guards | `.venv/bin/python -m pytest tests/test_ai_optional.py -q` | 23 passed, 1 skipped | ✓ PASS |
| lint-imports | `.venv/bin/lint-imports` | "Contracts: 2 kept, 0 broken", exit 0 | ✓ PASS |
| determinism evidence `--check` | `.venv/bin/python tests/fixtures/weekly/_record_determinism_evidence.py --check` | OK, 6 fields re-verified, `part_digest_a == part_digest_b`, `raw_bytes_equal: False` | ✓ PASS |
| protected-file diff | `git diff --exit-code -- src/newsletters/semantic.py content/ tests/fixtures/pptx/ tests/fixtures/weekly/template.pptx` | exit 0 | ✓ PASS |
| mypy on writer | `.venv/bin/mypy src/newsletters/pptx_writer.py` | "Success: no issues found in 1 source file" | ✓ PASS |
| CI job diff scope | `git diff c8abc9c..HEAD -- .github/workflows/ci.yml \| grep '^-'` | no output (zero removed content lines) | ✓ PASS |
| end-to-end acceptance test | `pytest ...::test_sample_surface_renders_through_the_committed_template ...::test_draft_and_published_renders_differ` | 2 passed | ✓ PASS |

Full suite run once per CLAUDE.md/task instruction; no repeated re-runs.

### Probe Execution

Not applicable — this phase is not a migration/tooling phase with declared probes; no `scripts/*/tests/probe-*.sh` exist for this phase.

### Human Verification Required

### 1. Real PowerPoint open

**Test:** Open a normalized, watermarked Draft `.pptx` (the artifact `test_sample_surface_renders_through_the_committed_template` produces) in real Microsoft PowerPoint.
**Expected:** Opens clean, no repair prompt; DRAFT watermark visible/legible; operator's bullets and font sizes survived the fill; a deliberately-overfull slot looks acceptable; the generated-by marker is readable in File → Info.
**Why human:** No `.pptx` consumer exists in this sandbox (`libreoffice-core` lacks Impress filters). Carried from Phase 1 assumption A8; consistently recorded (not hidden) in `02-CONTEXT.md`, `02-VALIDATION.md`, both SUMMARYs, and the `02-03-PLAN.md` `<human-check>` block.

### 2. First observed CI green

**Test:** Confirm the `pptx` GitHub Actions job's first real run is green.
**Expected:** `pip install ".[test,pptx]"` then the 5-module pytest command reports 0 failures, 0 skipped on GitHub's actual runners (not just locally).
**Why human:** No `gh` CLI / GitHub Actions access in this sandbox. The exact command was independently reproduced locally in this verification (`tests/test_pptx_writer.py` alone: 32 passed, 0 skipped) but the real CI environment has not yet observed the job execute.

### 3. `cp:contentStatus` tri-state amendment (product decision)

**Test:** Editor-in-Chief reviews whether an `IN_REVIEW` Surface should render `cp:contentStatus == "draft"` (current, verbatim per the binding decision note) or needs a distinct third value; also confirms the `cp:identifier` → `dc:identifier` wording correction (W20) should be applied to `docs/`.
**Expected:** A recorded decision (keep verbatim, or amend the decision note + implementation together).
**Why human:** This is a product/spec decision explicitly deferred to PR review by the plan and both SUMMARYs — not something code inspection can resolve, and P-04 is implemented exactly as instructed (not a defect).

### Gaps Summary

No gaps. All 5 ROADMAP Phase 2 success criteria are independently verified against live code and
passing tests (re-run, not trusted from SUMMARY.md). All nine "Fixed" review findings (WR-01..06,
IN-01, IN-02, IN-04) were checked directly in the live file content, not the review's narrative, and
all are genuinely present. The WR-01 evidence re-record is coherent: the committed evidence JSON's
`part_digest_a`/`part_digest_b` (`d7ff171a…`) and `normalized_a_sha256`/`normalized_b_sha256`
(`56fa2a61…`) match the decision-note addendum's citations exactly, and `--check` re-verifies live
against the current (hardened) encoding with `raw_bytes_equal: False` (negative control intact).

Status is `human_needed` rather than `passed` solely because three items require a human/external
channel this sandbox cannot exercise — the real-PowerPoint open, the first GitHub Actions CI
observation, and the tri-state product decision. All three are pre-existing, explicitly recorded
caveats in the phase's own plans/summaries/ROADMAP row (not new findings from this verification),
and per the task instructions these are "recorded, not closed" items, not gaps.

---

_Verified: 2026-08-29T06:06:41Z_
_Verifier: Claude (gsd-verifier)_
