---
phase: 01-specify-de-risk
verified: 2026-08-29T05:00:00Z
status: human_needed
score: 5/5 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Package legitimacy confirmation (T-01-SC): confirm python-pptx is pre-existing (pyproject.toml:43), not a newly added dependency"
    expected: "Editor-in-Chief confirms at PR review that the `[pptx]` extra was installed for the first time in this workspace, not added to pyproject.toml — `git diff --exit-code -- pyproject.toml` (re-verified below, exit 0) is the machine-checkable half; the SUS/unknown-downloads PyPI-API verdict adjudication is the human half."
    why_human: "Package-legitimacy adjudication of a PyPI supply-chain flag is a judgment call the plan explicitly reserves for the Editor-in-Chief, not a grep."
  - test: "Read docs/weekly-spec.md cold (no casespec.py, no RESEARCH.md, no questions) and attempt to hand-author a valid Weekly Spec from it alone"
    expected: "Every key's rule is understood from the doc's own text and a valid spec file could be written without opening another file — this is ROADMAP SC-1's actual bar, stated verbatim in 01-03-PLAN.md's own human-check."
    why_human: "Hand-authorability from a document is a comprehension judgment, not a machine-checkable property. All grep/YAML-parse-level checks pass (verified below), but they only prove the words are present and the YAML is valid, not that a first-time reader could act on them unaided."
---

# Phase 1: Specify + de-risk Verification Report

**Phase Goal:** The two things that would be expensive to discover late are settled before any code
depends on them — the Weekly Spec schema and the new block kinds exist in the docs, and `.pptx`
determinism has a recorded definition backed by evidence from a real write. Nothing is discovered
in Validate.
**Verified:** 2026-08-29T05:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Phase 1 success criteria — the contract)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---------------------|--------|----------|
| 1 | SC-1: `docs/architecture.md` + a Weekly Spec section define the four new block kinds field by field with union placement; a reader can hand-author a valid Weekly Spec from the doc alone | ✓ VERIFIED (machine-checkable parts); comprehension bar needs human sign-off | `docs/weekly-spec.md` (304 lines) exists live with `## Writing one`, `## Rules the loader enforces`, `## What happens to it`, `## The four block kinds`, `## Assets — the evidence record`, `## Determinism, and the extras it needs`. `NarrativeBlock`/`RecognitionsBlock`/`TeamBlock`/`AssetBlock` each defined with `kind: Literal[...]` discriminators (`"narrative"`, `"recognitions"`, `"team"`, `"asset"`), matching `semantic.py`'s live union idiom. First fenced YAML block parses with `yaml.safe_load` (independently re-verified). `docs/architecture.md`'s pre-existing `diagram`/`glossary` drift is fixed in the same edit (line 197 lists all 15 kinds). Pointers wired: `architecture.md:33,197` and `case-spec.md:9` both link `weekly-spec.md`. |
| 2 | SC-2: a determinism spike runs a REAL python-pptx write of a minimal template twice and records ONE outcome as a decision with committed evidence | ✓ VERIFIED | Re-ran `_record_determinism_evidence.py --check` independently: exit 0, "6 implementation-independent fields re-verified against a live measurement" — `part_digest_a == part_digest_b: True`, `raw_bytes_equal: False` (negative control holds), `varying_zip_fields: ['date_time']`, `normalized_bytes_equal: True`. `.planning/notes/2026-08-29-pptx-determinism-decision.md` exists (`status: decided`, exactly one `## Decision` heading) and states the outcome as BYTE-STABLE, scoped to a fixed (python-pptx, zlib) pair, citing the evidence JSON and the test module by path. |
| 3 | SC-3: recorded milestone decisions (D-01/D-02/D-03) + marker mechanism written with a testable consequence and a stated read-back assertion | ✓ VERIFIED | Decision note contains D-01 (1), D-02 (1), D-03 (3 occurrences) each with a stated consequence; marker table present (`cp:category`, `content_status` ×2, `cp:identifier` ×3, `replace(tzinfo=None)` ×2 — the tz-naive read-back comparison stated literally). `tests/test_pptx_determinism.py::test_normalized_archive_is_valid_and_reopens_with_marker_intact` implements exactly this read-back against the written bytes (independently read, live in repo) and passes (part of the 567-pass full-suite re-run below). |
| 4 | SC-4: asset-evidence record shape specified with exact field names, provenance minimum, deep-link-required condition, content-addressed identity, exact `missing[]` routing | ✓ VERIFIED | `docs/weekly-spec.md:231-293` (`## Assets — the evidence record`) names all ten `AssetRecord` fields (`key, file, sha256, folder, date, event, link, stands_in_for, caption, alt`); routing table has 4 condition rows plus the success row, verified live (`disclosed, never placed` occurs; `root` escape as a raise, not `missing[]`, is stated). `AssetBlock.asset` is `AssetRecord` (required, not `Optional`) and `evidence: list[Trace] = Field(min_length=1)` (line 181) — both independently confirmed in the live file, closing WR-06 from the code review. |
| 5 | SC-5: no production surface left behind — `[pptx]` extra unchanged, `lint-imports` KEPT, bare-install CI untouched, no scratch code | ✓ VERIFIED | Independently re-run: `git diff --exit-code -- src/newsletters/ pyproject.toml .github/workflows/ci.yml .importlinter tests/fixtures/pptx/*.pptx content/` → exit 0 (all byte-unchanged, corpus and content ledgers untouched). `.venv/bin/lint-imports` → "Contracts: 2 kept, 0 broken". `Block` union in `src/newsletters/semantic.py:449-464` still has exactly 11 members (no `semantic.py` kind change — D-01 held). `grep -rn '^import pptx\|^from pptx' src/newsletters/` → 0 matches. All spike code lives under `tests/` and `.planning/notes/`. |

**Score:** 5/5 truths verified at the machine-checkable level. Two items require human sign-off before the phase can be called fully closed (see Human Verification below) — both explicitly deferred to PR review by the plans themselves (`workflow.human_verify_mode = end-of-phase`), not gaps in the work.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/fixtures/weekly/_determinism.py` | stdlib-only normalizer + digest contract | ✓ VERIFIED | Exports `DOS_EPOCH`, `normalize_opc_zip`, `part_digest`, `differing_parts`, `differing_zipinfo_fields`; no `pptx` import; duplicate-member-name refusal (WR-01 fix) present in all four functions, live-read and confirmed. |
| `tests/fixtures/weekly/_author_template.py` | rerunnable, scrubbed template provenance | ✓ VERIFIED (exists; not re-read line-by-line, but its output `template.pptx` and the scrub guard are independently proven by the live test) | `test_committed_template_is_scrubbed_and_normalized` passes against the committed binary. |
| `tests/fixtures/weekly/template.pptx` | fabricated named-placeholder template | ✓ VERIFIED | `test_weekly_fixture_corpus_is_exactly_the_committed_template` passes (part of full-suite re-run); shape names asserted live in `test_normalized_archive_is_valid_and_reopens_with_marker_intact`. |
| `tests/test_pptx_determinism.py` | durable spike test, assertions A/B/C | ✓ VERIFIED | Read in full live. CR-01 fix confirmed: `pptx = pytest.importorskip("pptx", ...)` replaces the non-guarding `pytestmark`. 6 tests present (5 planned + 1 review-added duplicate-name regression + 1 review-added scrub-guard test = 7 total functions, all passing). |
| `tests/fixtures/weekly/_record_determinism_evidence.py` | evidence recorder with `--check` | ✓ VERIFIED | Read in full live. WR-03 (EPOCH_ZERO derived, not re-minted), WR-04 (`--check` fail-loud on unknown argv), IN-01 (`date.today()` not hardcoded) all confirmed present in the live file. |
| `.planning/notes/2026-08-29-pptx-determinism-evidence.json` | committed measurement | ✓ VERIFIED | `--check` re-run independently: exit 0, all 6 implementation-independent fields match a fresh measurement. |
| `.planning/notes/2026-08-29-pptx-determinism-decision.md` | recorded decision, evidence-cited | ✓ VERIFIED | `status: decided`, exactly one `## Decision` heading, all required strings (D-01/02/03, Q1-Q5, marker fields, NL_DRAFT_WATERMARK) present — independently grepped. |
| `docs/weekly-spec.md` | hand-authorable schema + block kinds + asset record | ✓ VERIFIED | 304 lines live; all sections present; YAML block independently parses; all four block kinds + AssetRecord fields present. |
| `docs/architecture.md` | block list corrected + extended, pointer added | ✓ VERIFIED | Live §7 sentence lists all 15 kinds (`diagram`, `glossary` pre-existing drift fixed; 4 new v1.3 kinds added); §1 pointer at line 33; `kind ∈ { show, newsletter, article, report }` unchanged (D-01 held). |
| `docs/case-spec.md` | sibling pointer | ✓ VERIFIED | 1-line pointer at line 9, confined edit. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `tests/test_pptx_determinism.py` | `tests/fixtures/weekly/_determinism.py` | import of `normalize_opc_zip`/`part_digest` | ✓ WIRED | Live `from _determinism import (...)` at line 74. |
| `tests/test_pptx_determinism.py` | `tests/fixtures/weekly/template.pptx` | `Presentation(str(TEMPLATE))` | ✓ WIRED | Live, `TEMPLATE = FIXTURE_DIR / "template.pptx"`, used in `_render_bytes`. |
| `tests/fixtures/weekly/_record_determinism_evidence.py` | `.planning/notes/...evidence.json` | `json.dump` + `--check` | ✓ WIRED | Independently re-ran `--check`, exit 0. |
| `tests/test_pptx_determinism.py` | `src/newsletters/adapters/_timestamps.py` | `EPOCH_ZERO` import | ✓ WIRED | Live `from newsletters.adapters._timestamps import EPOCH_ZERO`. |
| `.planning/notes/...decision.md` | `.planning/notes/...evidence.json` | Decision cites evidence by path | ✓ WIRED | `grep -c` ≥ 1, confirmed. |
| `.planning/notes/...decision.md` | `tests/test_pptx_determinism.py` | names the re-proving module | ✓ WIRED | Confirmed. |
| `tests/fixtures/pptx/_author_fixtures.py` | `.planning/notes/...decision.md` | docstring supersession pointer | ✓ WIRED | Live docstring reads "SUPERSEDED for the WRITER side by `.planning/notes/2026-08-29-pptx-determinism-decision.md`". |
| `docs/architecture.md` | `docs/weekly-spec.md` | §1/§7 pointers | ✓ WIRED | Confirmed at lines 33 and 197. |
| `docs/case-spec.md` | `docs/weekly-spec.md` | sibling pointer | ✓ WIRED | Confirmed at line 9. |
| `docs/weekly-spec.md` | `.planning/notes/...decision.md` | cites recorded decisions | ✓ WIRED | Present in `## Determinism, and the extras it needs`. |

### Requirements Coverage

Phase 1 carries **no requirement of its own** — confirmed against `.planning/REQUIREMENTS.md`
line 90 ("Phase 1 (Specify + de-risk) carries no requirement of its own. It de-risks WKLY-01 ...
and WKLY-02 ..."). Both WKLY-01 and WKLY-02 remain correctly `Pending`, mapped to Phase 2 and
Phase 3 respectively (lines 81-82). No orphaned requirements for this phase.

### Anti-Patterns Found

None. Scanned all phase-modified files (`tests/fixtures/weekly/*.py`, `tests/test_pptx_determinism.py`,
`tests/fixtures/pptx/_author_fixtures.py`, `docs/weekly-spec.md`, `docs/architecture.md`,
`docs/case-spec.md`, `.planning/notes/2026-08-29-pptx-determinism-decision.md`) for
`TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|placeholder|coming soon|not yet implemented`. The only hits
are legitimate uses of "placeholder" in its PPTX-mechanics sense (named placeholders, `add_slide`
placeholder-name regeneration) and one deliberate line in `_author_template.py` explicitly labeling
its fabricated content "placeholder text, not sample content" (accurate self-description, not a
debt marker). No unreferenced `TBD`/`FIXME`/`XXX` found anywhere in the phase's files.

### Code Review Fixes — Independently Re-Verified

`01-REVIEW.md` records status `fixed` for 1 Critical + 7 Warning + 2 accepted Info findings across
commits `6150b4d..8c0fd12`. All ten fix commits exist in `git log`. Each fix was independently
re-read in the live file (not trusted from the review's own "Resolution" text) and confirmed present:

| Finding | Fix confirmed live in |
|---------|------------------------|
| CR-01 (skipif does not guard) | `tests/test_pptx_determinism.py:62` — `pytest.importorskip("pptx", ...)` |
| WR-01 (duplicate-member digest collision) | `tests/fixtures/weekly/_determinism.py` — `_reject_duplicate_member_names` in all 4 functions |
| WR-02 (missing scrub guard) | `tests/test_pptx_determinism.py::test_committed_template_is_scrubbed_and_normalized` |
| WR-03 (hand-minted second epoch) | `tests/fixtures/weekly/_record_determinism_evidence.py:74` — `_EPOCH_NAIVE = EPOCH_ZERO.replace(tzinfo=None)` |
| WR-04 (typo overwrites evidence) | `_record_determinism_evidence.py:main()` — refuses unknown argv, exits 2 |
| WR-05 (false docstring claim) | `tests/fixtures/pptx/_author_fixtures.py:_normalize_zip` docstring corrected |
| WR-06 (evidence not enforced) | `docs/weekly-spec.md:181` — `Field(min_length=1)` |
| WR-07 (two unrouted paths) | `docs/weekly-spec.md:272-273` — both rows added |
| IN-01 (hardcoded recorded date) | `_record_determinism_evidence.py:186` — `date.today().isoformat()` |
| IN-02 (leaked zip handles) | `tests/fixtures/pptx/_author_fixtures.py` — `with zipfile.ZipFile(...)` at lines 145, 165 |

Independent gate re-run after fixes matches the review's own claim exactly: `567 passed, 64
skipped` (full suite), `lint-imports` 2 kept / 0 broken, `--check` exit 0.

### Human Verification Required

### 1. Package legitimacy confirmation (T-01-SC)

**Test:** At PR review, the Editor-in-Chief confirms that `python-pptx` was installed for the first
time in this workspace (via the pre-existing `pyproject.toml:43` `[pptx]` extra) rather than newly
added, adjudicating the `SUS`/`unknown-downloads` PyPI-API false-positive verdict already recorded
in `pyproject.toml`.
**Expected:** Confirmation that no new package entered the dependency tree.
**Why human:** Supply-chain legitimacy adjudication is a judgment call the plan explicitly reserves
for the Editor-in-Chief (`01-01-PLAN.md` `<human-check>`), not a grep. The machine-checkable half —
`git diff --exit-code -- pyproject.toml` — was independently re-run here and exits 0.

### 2. Weekly Spec hand-authorability read-through (ROADMAP SC-1's real bar)

**Test:** The Editor-in-Chief reads `docs/weekly-spec.md` cold — without opening `casespec.py`,
`01-RESEARCH.md`, or asking a question — and answers: could you hand-author a valid Weekly Spec
from this document alone?
**Expected:** Yes. If no, the missing rule should be named and closed with a doc edit.
**Why human:** This is stated verbatim as the phase's own human-check (`01-03-PLAN.md`) and is
explicitly "not machine-checkable." All grep/YAML-parse-level checks in this verification pass
(every top-level key documented, the YAML parses, all seven loader rules present, all four block
kinds field-by-field, the asset routing table complete) — those checks prove the words exist and
are internally consistent, not that a first-time reader can act on them unaided.

### Gaps Summary

No gaps. Every ROADMAP Phase 1 success criterion is independently verified against the live
codebase — not merely claimed by SUMMARY.md — including the ten code-review fixes (commits
`6150b4d..8c0fd12`), which were each re-read in the live files rather than trusted from the
review's own resolution text. All independent gate re-runs (`pytest -q`: 567 passed/64 skipped;
`lint-imports`: 2 kept/0 broken; `--check`: exit 0; the four `git diff --exit-code` production-
surface guards: all exit 0; `newsletters check` over all three corpora: all exit 0) match the
SUMMARY's claims exactly. Status is `human_needed`, not `passed`, solely because two items the
plans themselves scheduled for end-of-phase PR review (package legitimacy, and the SC-1
hand-authorability comprehension bar) remain outstanding — neither is a defect in the work, both
are explicit, planned escalations to the Editor-in-Chief.

---

_Verified: 2026-08-29T05:00:00Z_
_Verifier: Claude (gsd-verifier)_
