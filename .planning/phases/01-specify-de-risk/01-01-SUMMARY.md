---
phase: 01-specify-de-risk
plan: 01
subsystem: testing
tags: [python-pptx, zipfile, opc, determinism, reproducible-builds, sha256, pytest]

# Dependency graph
requires:
  - phase: (none — wave 1, no dependencies)
    provides: the pre-existing `[pptx]` extra and `adapters/_timestamps.EPOCH_ZERO`
provides:
  - "The measured determinism outcome: BYTE-STABLE via a declared post-save OPC-zip normalization, with the implementation-independent `part_digest` as the cross-environment assertion"
  - "`normalize_opc_zip` / `part_digest` / `differing_parts` / `differing_zipinfo_fields` — the ONE stdlib-only normalizer + content-digest contract Phase 2 moves to `src/newsletters/_pptx_writer.py`"
  - "A fabricated `template.pptx` carrying four `NL_` slots plus one deliberately unprefixed `Footer`, so the D-03 fail-loud contract has a fixture to test in both directions"
  - "A durable pytest module re-proving assertions A (part digest), B (byte equality after normalization) and C (the negative control) on every run"
  - "A committed, re-verifiable evidence artifact with a `--check` mode that fails on drift"
affects: [02-renderer, 03-weekly-compose, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []  # no new dependency — python-pptx 1.0.2 installed from the pre-existing [pptx] extra
  patterns:
    - "Save to BytesIO -> normalize the OPC zip -> write once (never save-then-rewrite-in-place)"
    - "Two-level determinism assertion: full-file bytes in-process, part-content digest across environments"
    - "Committed measurement + a rerunnable --check recorder as the anti-fabrication mitigation"

key-files:
  created:
    - tests/fixtures/weekly/_determinism.py
    - tests/fixtures/weekly/_author_template.py
    - tests/fixtures/weekly/template.pptx
    - tests/test_pptx_determinism.py
    - tests/fixtures/weekly/_record_determinism_evidence.py
    - .planning/notes/2026-08-29-pptx-determinism-evidence.json
  modified: []

key-decisions:
  - "Recorded determinism outcome is BYTE-STABLE via a declared post-save zip normalization — not the content-stable fallback the roadmap allowed for"
  - "The byte-identity claim is scoped, in writing, to a fixed (python-pptx, zlib) pair; `part_digest` is the implementation-independent assertion a committed==fresh gate must use"
  - "The normalizer preserves python-pptx's emitted entry order rather than sorting — `[Content_Types].xml` stays first by construction, not by sort luck"
  - "The negative control is a first-class test, not a comment: an un-normalized double write across a DOS-time boundary is asserted NOT byte-equal, which makes the determinism claim falsifiable"
  - "The template's reserved-prefix shape contract is settled by construction: four `NL_` slots plus one unprefixed `Footer` (D-03 needs both directions)"

patterns-established:
  - "One normalizer, stdlib-only, no pptx import — importable on a bare install, needs no skip guard"
  - "The `pptx` import in tests/ sits behind `pytestmark = pytest.mark.skipif(find_spec(\"pptx\") is None, ...)` with `# noqa: E402` post-guard imports — the only sanctioned way tests touch the extra"
  - "Evidence artifacts record implementation-dependent hashes but never assert them across environments"

requirements-completed: []  # Phase 1 carries no WKLY requirement; this plan de-risks WKLY-01

# Metrics
duration: 12min
completed: 2026-08-29
---

# Phase 1 Plan 01: The `.pptx` determinism spike Summary

**A real python-pptx double write, 3 seconds apart, measured and committed: the deck is BYTE-STABLE after a 15-line stdlib zip normalization, and the result is now re-proved by five tests including a negative control that can fail.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-29T03:30:30Z
- **Completed:** 2026-08-29T03:42:00Z
- **Tasks:** 3
- **Files created:** 6 (0 modified)

## The measured outcome (verbatim — plan 01-02 must not re-measure this)

From `.planning/notes/2026-08-29-pptx-determinism-evidence.json`, produced by a real double
write with a 3-second gap and re-verified live by `--check`:

| Key | Value |
|-----|-------|
| `raw_bytes_equal` | `false` |
| `varying_parts` | `[]` |
| `varying_zip_fields` | `["date_time"]` |
| `normalized_bytes_equal` | `true` |
| `part_digest_a` | `606c24642c74bed9a3514f053489067b7479a12b2212738338066c1cc2822ab9` |
| `part_digest_b` | `606c24642c74bed9a3514f053489067b7479a12b2212738338066c1cc2822ab9` |
| `raw_a_sha256` | `68eaa4d42cd8781a7ab6ee6ee96528697cac0e7ce8f1c394cc462704a1755a97` |
| `raw_b_sha256` | `1d0d0eae3ef3dcb78bb586e7ba2d26144bc3ab3b9281757f4da433b725882515` |
| `normalized_a_sha256` | `56fa2a61d4993ded9139fafd0cb17f4d30435fdc5ca59efc61acdc812eb6869a` |
| `normalized_b_sha256` | `56fa2a61d4993ded9139fafd0cb17f4d30435fdc5ca59efc61acdc812eb6869a` |
| `python_pptx` | `1.0.2` |
| `zlib` | `1.3` |
| `python` | `3.11.15` |
| `platform` | `Linux-6.18.44-fc-v22-x86_64-with-glibc2.39` |
| `template_sha256` | `4461a6329aa4e74c25e3879a5212d646d7b7816c12e772b15befa70c2e722618` |
| `seconds_between_writes` | `3` |

**`outcome` (verbatim):**

> BYTE-STABLE via a declared post-save zip normalization: two real python-pptx writes 3s apart
> differ ONLY in zip ['date_time'], every unzipped part is byte-identical, and normalize_opc_zip
> makes the files byte-identical. Scoped to a fixed (python-pptx, zlib) pair; the
> implementation-independent assertion is part_digest.

Note that `raw_a_sha256 != raw_b_sha256` while `normalized_a_sha256 == normalized_b_sha256`.
That pair of facts *is* the finding: the deck's content never moved, only the container's clock.

## Accomplishments

- **The measurement exists and is real.** Two writes 3 seconds apart, un-normalized, differ — and
  the ONLY thing that differs is the zip `date_time` field. All unzipped parts are byte-identical
  (`varying_parts == []`). RESEARCH predicted this from a scratch session; this plan re-measured it
  in the repo, in a committed, rerunnable form.
- **The determinism claim is falsifiable.** `test_unnormalized_double_write_differs_only_in_zip_date_time`
  asserts `raw_a != raw_b`. Without it, `render() == render()` passes trivially whenever both writes
  land in one wall-clock second (measured in RESEARCH E2: they do), which is a green test proving
  nothing. The green in assertion B is now attributable to the normalizer.
- **The honest scope caveat is written down, not discovered later.** DEFLATE output is
  zlib-implementation-dependent, so full-file byte identity holds only for a fixed (python-pptx,
  zlib) pair. `part_digest` — sha256 over sorted `(part name, sha256(part bytes))` — is the
  implementation-independent assertion, and both the module docstring and the evidence recorder say
  so explicitly, so a Phase 4 committed==fresh gate cannot accidentally assert a full-file hash.
- **The evidence cannot be faked.** `--check` re-runs the whole measurement and compares every
  implementation-independent field, exiting 1 with a teaching message on drift. Hand-typed numbers
  survive neither `--check` nor `test_pptx_determinism.py`, which re-derives the same invariants
  independently. (Threat T-01-03.)
- **Zero production surface.** `src/newsletters/`, `pyproject.toml`, `.github/workflows/ci.yml`,
  `.importlinter` and `tests/fixtures/pptx/` are all byte-unchanged; `lint-imports` reports both
  contracts KEPT; there is no column-0 `pptx` import under `src/`. The whole spike lives in `tests/`
  and `.planning/notes/`.

## Task Commits

1. **Task 1: Environment + the one normalizer contract + the fabricated template** — `4be9827` (test)
2. **Task 2: The spike as a durable test — assertions A, B, and the negative control C** — `ee41c4a` (test)
3. **Task 3: Record the committed evidence + the SC-5 no-production-surface sweep** — `cc5959a` (docs)

## Files Created

- `tests/fixtures/weekly/_determinism.py` — the ONE normalizer + content-digest contract:
  `DOS_EPOCH`, `normalize_opc_zip`, `part_digest`, `differing_parts`, `differing_zipinfo_fields`.
  Stdlib only (`hashlib`, `io`, `zipfile`); no `pptx` import, so it is importable on a bare install
  and needs no skip guard. The docstring carries WHY (python-pptx passes a **str** arcname to
  `zipfile.writestr`, so stdlib stamps `time.localtime()` — `pptx/opc/serialized.py:234-242`),
  THE FIX, the zlib scope caveat, and the zip-slip property (T-01-06: `ZipFile.read` →
  `ZipFile.writestr`, both in memory, so no member name ever reaches the filesystem).
- `tests/fixtures/weekly/_author_template.py` — rerunnable provenance for the fabricated template.
  Scrubs the stock python-pptx template's third-party core properties (`"Steve Canny"`,
  `"generated using python-pptx"`, 2013 dates) and routes the saved bytes through
  `normalize_opc_zip` before writing, so the committed binary is already normalized and a re-run is
  byte-identical (verified).
- `tests/fixtures/weekly/template.pptx` — the synthetic template: `NL_WEEK_TITLE`, `NL_MODULE`,
  `NL_HIGHLIGHTS`, `NL_LOWLIGHTS` plus one deliberately unprefixed `Footer`. 28,557 bytes.
- `tests/test_pptx_determinism.py` — five tests: the negative control (C), byte equality after
  normalization (B), part-digest stability (A), the read-back assertion (idempotence, `testzip()`,
  `[Content_Types].xml` first, marker/gate/`EPOCH_ZERO` core properties and the five shape names
  read off the WRITTEN bytes), and a corpus guard.
- `tests/fixtures/weekly/_record_determinism_evidence.py` — the evidence recorder with `--check`.
- `.planning/notes/2026-08-29-pptx-determinism-evidence.json` — the committed measurement, with a
  `notes` mapping carrying one explanatory note per non-obvious key.

## Decisions Made

- **Outcome recorded as BYTE-STABLE, not content-stable.** The roadmap allowed either. The
  measurement supports the stronger one, so the stronger one is recorded — with its scope stated.
- **Preserve emitted entry order, do not sort.** python-pptx's order is already deterministic and
  puts `[Content_Types].xml` first by construction. Sorting keeps it first only incidentally
  (`[` = 0x5B sorts before `_`), which would be a second guarantee to defend for no gain. The test
  asserts `names[0] == "[Content_Types].xml"` explicitly either way.
- **`differing_zipinfo_fields` compares `CRC` too, not just the four pinned fields.** A CRC drift
  with identical part bytes would be a zlib-implementation signal, and hiding it would make the
  evidence quieter than the truth.
- **The marker strings (`cp:category = "generated-by:newsletters"`, `cp:contentStatus = "draft"`)
  are exercised here but ratified in Phase 2.** This plan proves they round-trip through a real
  write and read back off the written file; it does not claim to settle the naming.
- **`EPOCH_ZERO` is imported from `adapters/_timestamps.py`, never re-minted.** The tz-naive
  comparison (`EPOCH_ZERO.replace(tzinfo=None)`) is written into the test so Phase 2 copies it
  rather than rediscovering Pitfall 5.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `time.sleep(SLEEP_SECONDS)` replaced with the literal `time.sleep(3)`**
- **Found during:** Task 2
- **Issue:** The first draft used a named `SLEEP_SECONDS = 3` constant. The plan's acceptance
  criterion greps for the literal `time.sleep(3)`, so the named constant would have failed a gate
  that exists to prove the load-bearing delay is present.
- **Fix:** Used the literal with an inline comment explaining the 2-second DOS granularity, and
  wrote "3s" into the assertion message. One literal, no drift risk.
- **Files modified:** `tests/test_pptx_determinism.py`
- **Verification:** `grep -c 'time.sleep(3)'` returns 1; 5 tests still pass in 3.14s.
- **Committed in:** `ee41c4a`

**2. [Rule 3 - Blocking] Three over-length lines reflowed to satisfy `black`**
- **Found during:** Tasks 1–3
- **Issue:** Several comment/message lines exceeded the project's 88-char `black` line length.
- **Fix:** Reflowed comments above their statements and moved two long assertion messages into
  local variables (rather than accepting black's parenthesized-condition rewrite, which reads
  worse). `_record_determinism_evidence.py` was formatted with `black` directly.
- **Files modified:** all four new `.py` files
- **Verification:** `black --check` on all four new files → "4 files would be left unchanged".
- **Committed in:** `4be9827`, `ee41c4a`, `cc5959a`

**Note on the pre-existing black/isort baseline:** the installed `black 26.5.1` / `isort 9.0.1`
also want to reformat pre-existing files (`tests/test_pptx_golden.py`,
`tests/fixtures/pptx/_author_fixtures.py`). Those were left alone — the standard is "no NEW
failures vs the 2026-07-02 baseline", and reformatting unrelated files would be scope creep and
would pollute the diff. The four new files are clean under both.

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking a gate)
**Impact on plan:** Neither changed behaviour or scope. No architectural change; no Rule 4 trigger.

## Issues Encountered

- **The environment was bare as the plan predicted.** No `.venv`, no `pytest`, no `python-pptx`.
  `python -m venv .venv` + `pip install -e '.[dev,test,pptx,config]'` succeeded first try; the
  RETRO 2026-07-09 debian-PyYAML friction did NOT recur (a fresh venv without
  `--system-site-packages` avoids it, as recorded). No `--ignore-installed PyYAML` fallback needed.
- **No package legitimacy checkpoint fired**, correctly: nothing was added. `python-pptx` 1.0.2 came
  from the pre-existing `[pptx]` extra and `git diff --exit-code -- pyproject.toml` exits 0. The
  `SUS`/`unknown-downloads` verdict stands adjudicated in `pyproject.toml`'s own comment; the EiC
  confirmation is the end-of-phase PR review (T-01-SC).

## Verification (each gate run once, independently)

| Gate | Result |
|------|--------|
| `pytest tests/test_pptx_determinism.py -x -q` | **5 passed** in 3.14s |
| `pytest tests/test_ai_optional.py -x -q` | **21 passed, 1 skipped** in 4.41s |
| `pytest -q` (full suite) | **565 passed, 64 skipped** in 13.48s — no failures |
| `lint-imports` | **2 kept, 0 broken** (both contracts KEPT) |
| `_record_determinism_evidence.py --check` | **exit 0** — 6 implementation-independent fields re-verified |
| `git diff --exit-code -- src/newsletters/ pyproject.toml .github/workflows/ci.yml .importlinter tests/fixtures/pptx/` | **exit 0** — all byte-unchanged |
| `grep -rn '^import pptx\|^from pptx' src/newsletters/ \| wc -l` | **0** |
| `black --check` on the four new `.py` files | **clean** |
| Template regeneration | **byte-identical** on re-run |

The 64 skips are the pre-existing optional-extra skips (no `[excel]`, `[ai]`, `[panel]` installed),
not new.

## Known Stubs

None. Every artifact this plan produced is live: the normalizer is exercised by five tests and by
the evidence recorder, the template is rendered through on every test run, and the evidence JSON is
re-derived by `--check`.

## Threat Flags

None. No new network endpoint, auth path, file-access pattern or schema change at a trust boundary
was introduced. The one security-relevant surface — the normalizer's handling of operator-supplied
archives — was already in the plan's threat register (T-01-06) and its mitigation (no filesystem
path is ever constructed from a member name) is stated in the module docstring so Phase 2 inherits
it.

## User Setup Required

None — no external service configuration. The `.venv` created by Task 1 is gitignored
(`.gitignore:132`) and is a local build environment, not user setup.

## Next Phase Readiness

**Ready for plan 01-02** (which turns this measurement into the recorded decision):

- The measured outcome is committed verbatim above and in the JSON — 01-02 must NOT re-measure it.
- The read-back assertion pattern Phase 2 copies is already written and passing in
  `test_normalized_archive_is_valid_and_reopens_with_marker_intact`.
- The reserved-prefix template contract shape (D-03) is settled by construction: four `NL_` slots,
  one unprefixed decorative shape.

**Carried to Phase 2:**

- `_determinism.py` moves to `src/newsletters/_pptx_writer.py` behind the `[pptx]` extra, with the
  lazy-import discipline `adapters/_pptx_loader.py` already establishes.
- **The one unverified link (from RESEARCH, unchanged by this plan):** no real `.pptx` consumer
  exists in this environment — `libreoffice-core` is installed without the Impress filter, so it
  cannot open any `.pptx`, normalized or not. What IS proven: `testzip()` passes and python-pptx
  reopens the normalized bytes with shape names and core properties intact. Phase 2 should carry a
  `checkpoint:human-verify` — open one normalized deck in real PowerPoint — before the renderer is
  accepted.
- Consider the `python-pptx>=1.0.2` floor pin (Pitfall 4). `test_pptx_extra_declared` parses out
  version specifiers, so a pin does not break it — but verify rather than assume.

## Self-Check: PASSED

All 6 planned artifacts exist on disk (plus this SUMMARY); all 3 task commits
(`4be9827`, `ee41c4a`, `cc5959a`) are present in the git log and pushed to
`origin/claude/new-session-gw8tik`.

---
*Phase: 01-specify-de-risk*
*Completed: 2026-08-29*
