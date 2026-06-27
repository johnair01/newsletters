---
phase: 06-powerpoint-adapter
verified: 2026-06-17T17:01:12Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: null  # initial verification
human_verification: []
---

# Phase 6: PowerPoint Adapter Verification Report

**Phase Goal:** Extract slide and shape text from decks via python-pptx, explicitly reporting the shapes the high-level API cannot read.
**Verified:** 2026-06-17T17:01:12Z
**Status:** passed
**Re-verification:** No — initial verification

Verification was performed against the LIVE codebase on branch `claude/youthful-fermi-dly6mi`,
not against SUMMARY claims. All four gates were re-run independently with the project venv
(`.venv/bin/python`), and three independent live probes were built and executed to confirm the
two behavioral criteria + the L1 front-fix end-to-end (probes are in `/tmp`, never committed).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The PowerPoint adapter extracts slide/shape text into `Claim(+Trace)` with slide/shape locators | ✓ VERIFIED | Live probe: title/body deck → claims `'Quarterly Review'`, `'Revenue grew 12 percent'`; `claim.text == trace.span` (verbatim), `trace.is_addressed == True` (content-addressed), `transcript[start:end]` reproduces the text. Locator string `"Slide 1 / Title 1"` is in `source.transcript` (`pptx_adapter.py:163,187,249`). See observation below re: typed `Trace.locator`. |
| 2 | Shapes the adapter cannot read (SmartArt, grouped shapes, chart, picture, media, OLE) are reported in `unextracted[]` | ✓ VERIFIED | Live probe on a hand-built deck (nested group {readable text-box + picture} + chart-only group + connector + empty autoshape): readable members extracted, picture + chart routed to `unextracted[]`, group nodes neither claim nor drop, zero group leakage. SmartArt fixture → `'SmartArt/diagram not extracted (no high-level API)'`. `_classify_unreadable` + `_graphic_data_uri` (`pptx_adapter.py:113-140`). |
| 3 | A golden-file test covers the adapter against a fixture containing SmartArt AND grouped shapes, asserting zero silent drops | ✓ VERIFIED | `tests/fixtures/pptx/smartart.pptx` + `nested_group.pptx` exist among 9 committed fixtures; `test_pptx_golden.py` asserts `len(claims)+len(unextracted)==units` for all 9, plus targeted `test_smartart_is_disclosed_never_extracted` + `test_nested_group_member_text_extracted_unreadable_member_disclosed`. 84 passed (pptx adapter+golden+loader). |
| 4 | L1 front-fix: ALL adapters deterministic — no `now()` fallback; email+excel+pptx source intrinsic-or-EPOCH_ZERO; matrix covers all three | ✓ VERIFIED | Independent live probe: no-intrinsic `.eml`/`.xlsx`/`.pptx` each parse to byte-identical Sources twice with `timestamp == 1970-01-01T00:00:00+00:00`. `deterministic_timestamp` (`_timestamps.py:45-61`). Determinism matrix runs (not skips) `[email]/[excel]/[pptx]` × {no-intrinsic, preserved}: 6 PASSED. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/adapters/_timestamps.py` | EPOCH_ZERO + deterministic_timestamp | ✓ VERIFIED | Stdlib-only pure function; None→EPOCH_ZERO, tz-naive→UTC, tz-aware→verbatim. Imported by all 3 file adapters. |
| `src/newsletters/adapters/_pptx_loader.py` | Lazy python-pptx boundary | ✓ VERIFIED | No top-level `import pptx`; `_load_pptx()` lazy + teaching ImportError; `load_presentation(raw)`. Bare `import newsletters` confirmed to NOT import pptx (`sys.modules` check). |
| `src/newsletters/adapters/pptx_adapter.py` | PptxAdapter: walk/recurse/taxonomy/distill | ✓ VERIFIED | 436 lines, substantive; recursive `_walk` (group recursion), `_emit_or_report` leaf fork, full unreadable taxonomy, transcript serialize + round-trip split, `distill()` via `normalize()`. No stubs/TODO. |
| `src/newsletters/adapters/__init__.py` | register("pptx") | ✓ VERIFIED | `register(PptxAdapter())` line 30; `resolve("pptx")` returns `PptxAdapter` live. |
| `tests/fixtures/pptx/*.pptx` (9 incl. smartart+nested_group) | byte-reproducible corpus | ✓ VERIFIED | All 9 present on disk; `_author_fixtures.py` generator committed. |
| `tests/test_pptx_*.py`, `test_timestamp_determinism.py`, `test_coverage_roundtrip.py`, `test_ai_optional.py` | golden + determinism + parity + AI-isolation | ✓ VERIFIED | All run green (see Behavioral Spot-Checks). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `adapters/__init__.py` | distill registry | `register(PptxAdapter())` | ✓ WIRED | `resolve("pptx")` resolves live (probe). |
| `pptx_adapter.parse` | python-pptx | `load_presentation` (lazy) | ✓ WIRED | Parses real `.pptx` bytes into a Source; no top-level import. |
| `pptx_adapter.distill` | `normalize()` | shared faithful gate | ✓ WIRED | Claims minted via `normalize()` → `Trace.from_source`; adapter mints no hash. |
| `pptx_adapter` | `Source.extraction` | `encode_coverage(drops)` | ✓ WIRED | Round-trip coverage parity test passes on a FRESH adapter. |
| email/excel/pptx | `deterministic_timestamp` | `timestamp=` (explicit, every path) | ✓ WIRED | grep confirms every `timestamp=` routes through helper incl. error paths; no `now()`/`_utcnow` fallback reachable. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `PptxAdapter` claims | `units` from `_serialize(prs)` | live `Presentation` slide/shape walk | ✓ Yes — live deck yields real verbatim claims | ✓ FLOWING |
| `unextracted[]` | `drops` from `_classify_unreadable` | live shape_type + graphicData @uri | ✓ Yes — picture/chart/SmartArt produce real reasons | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite | `.venv/bin/python -m pytest -q` | 383 passed, 1 xfailed (8.5s) | ✓ PASS |
| pptx adapter+golden+loader | `pytest tests/test_pptx_adapter.py tests/test_pptx_golden.py tests/test_pptx_loader.py -q` | 84 passed | ✓ PASS |
| timestamp determinism matrix | `pytest tests/test_timestamp_determinism.py -v` | 11 passed; `[email]/[excel]/[pptx]` params RAN | ✓ PASS |
| AI-isolation / bare-install | `pytest tests/test_ai_optional.py -q` | 14 passed, 1 xfailed | ✓ PASS |
| round-trip coverage parity | `pytest tests/test_coverage_roundtrip.py -q` | 20 passed | ✓ PASS |
| mypy | `mypy src/newsletters/adapters src/newsletters/distill` | Success, 17 files | ✓ PASS |
| import-linter | `.venv/bin/lint-imports` | 1 kept, 0 broken (forbid-ai-in-core) | ✓ PASS |
| renderer build | `newsletters build` | rendered 9 surfaces + library index, no errors | ✓ PASS |
| bare import lazy | `import newsletters` → assert pptx not in sys.modules | OK (lazy) | ✓ PASS |
| live criterion 1+2 probe | custom `/tmp/verify_pptx.py` | verbatim+addressed claims, nested-group + chart-only-group + SmartArt all reported, no group leakage | ✓ PASS |
| live L1 probe (3 adapters) | custom `/tmp/verify_l1.py` | email/excel/pptx all EPOCH_ZERO + byte-identical twice | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` declared for this phase. The phase's verification contract is its
golden corpus + determinism/parity matrices, all run above. N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ADAPT-04 | 06-01/02/03 | PowerPoint adapter via python-pptx, slide/shape text → Claim(+Trace), unreadable shapes reported | ✓ SATISFIED | Criteria 1+2 verified live; lazy `[pptx]` extra. |
| ADAPT-06 | 06-04 | Golden-file test, zero silent drops | ✓ SATISFIED | 9-fixture golden corpus incl. SmartArt+nested-group; identity asserted for all. |

ROADMAP maps Phase 6 to `ADAPT-04`; the plans additionally completed `ADAPT-06` (the golden-test
requirement, shared across adapter phases). No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| pptx_adapter.py | 18,118,181,199 | word "placeholder" | ℹ️ Info | False positive — refers to PowerPoint *placeholder shapes* (a real pptx concept), not a stub. No TODO/FIXME/XXX/TBD anywhere in phase source. |

No debt markers, no stub returns, no hardcoded-empty data flowing to output. The `return None`
paths in `_classify_unreadable`/`_graphic_data_uri` are intentional control flow (skipped-empty /
crash-free fallback), each covered by tests.

### Observations (non-blocking)

**O-1 — Typed `Trace.locator` is empty; slide/shape locator lives in the transcript prefix.**
Criterion 1 says "with slide/shape locators." The adapter encodes the locator as the transcript
line prefix `Slide N / <shape>\t<text>` (`Slide N / <shape> [r{c}]` for cells, `Slide N / notes`
for notes), and `normalize()` mints the claim's `Trace` via `Trace.from_source(source, idx, end)`
**without** passing a `locator=`, so `claim.evidence[0].locator == FreeLocator(text='')`. The
slide/shape identity is therefore recoverable from `source.transcript` around `trace.start/end`
(deterministic, content-addressed), but it is NOT carried on the typed `Locator` object.

This is verified to be the **established, accepted project pattern across ALL adapters** — the
Excel adapter (Phase 5, already verified/complete) does the identical thing: `Sheet!A1\thello`
transcript prefix with an empty `Trace.locator`. The PPTX adapter faithfully follows the
Phase-4/5 convention rather than diverging. The golden test even named
`test_notes_emit_with_notes_locator` asserts the locator against the **transcript** string, not
the trace. Because the locator IS present and deterministic at the transcript layer (the same bar
Phase 5's "sheet!cell locators" met and shipped), criterion 1 is satisfied. Flagged here for
visibility: if a future phase needs the locator queryable as a typed field on the claim's trace,
that is a cross-adapter normalize() enhancement, not a Phase-6 gap.

### SmartArt + Nested-Group Accounting Robustness Assessment

The objective asked for a skeptical hunt for a shape walked past WITHOUT being counted as a claim
or an unextracted entry. Findings from live probes:

- **Nested group, mixed members** — `_walk` recurses `GroupShape.shapes` (`pptx_adapter.py:219`);
  the readable text-box member is extracted, the picture member is disclosed, and BOTH group
  container nodes contribute nothing (no claim, no drop, no leakage). Confirmed live + by
  `test_nested_group_member_text_extracted_unreadable_member_disclosed`.
- **Group containing only a chart** — recursion reaches the chart leaf; `_emit_or_report` →
  `shape.has_chart` → `_R_CHART` drop. Confirmed live: `chart drops: 1`. NOT silently dropped.
- **Connector / line shape** — `shape_type == LINE`, `has_text_frame=False`, not in the unreadable
  taxonomy → skipped-empty. Probed: a connector carries no text, so skipping it loses no text
  content (the goal is slide/shape TEXT). Faithful.
- **Empty placeholder / empty auto-shape** — `has_text_frame=True` but its only paragraph is `''`
  → skipped-empty. Probed directly; no content lost.
- **Auto-shape WITH text (WordArt-like)** — probed a 5-point star with text `'IMPORTANT'`: it IS
  extracted as a claim (not skipped). So the skip path only fires when there is genuinely no text.
- **Unknown graphic frame** — any `graphicData @uri` other than the diagram URI on a
  `shape_type is None` frame → `_R_UNKNOWN_FRAME` (reported, never dropped), with an lxml fallback
  so a python-pptx rename degrades to "reported" rather than crashing.

**Verdict on accounting:** Airtight for the phase's contract (slide/shape **text**). Every leaf
shape is exactly one of {≥1 verbatim claim, skipped-empty with no text payload, one
`unextracted[]` disclosure}; group nodes are containers that contribute nothing. No shape with
extractable text and no recognized non-text object is walked past silently. The one nuance — a
textless decorative LINE/connector being skipped-empty rather than disclosed — is faithful to a
*text*-extraction goal and matches the Excel blank-cell precedent; it is not a silent drop of
content.

### L1 Front-Fix Confirmation (all three adapters deterministic)

- `deterministic_timestamp` (`_timestamps.py`) maps `None → EPOCH_ZERO` (1970-01-01Z), never
  `now()`; tz-naive → UTC; tz-aware preserved. Pure function (no clock/state).
- **email** sources the `Date` header datetime or None → helper (`email_adapter.py:208`).
- **excel** sources `intrinsic_created(raw)` — a stdlib raw-OOXML read of `dcterms:created` that
  returns None faithfully when absent, defeating openpyxl's fabricated `created or now()` trap
  (`excel_adapter.py:87-127,321,333`); unreadable path passes `deterministic_timestamp(None)`.
- **pptx** sources `core_properties.created` (guarded `isinstance datetime`) → helper
  (`pptx_adapter.py:309-312`); unreadable path passes `deterministic_timestamp(None)`
  (`pptx_adapter.py:296`).
- grep confirms NO adapter `timestamp=` path bypasses the helper and no reachable `now()`/`_utcnow`
  fallback remains.
- Independent live probe: a no-intrinsic `.eml`, a stripped-`created` `.xlsx`, and a
  stripped-`created` `.pptx` each parse to byte-identical Sources twice with `timestamp ==
  EPOCH_ZERO`. The excel raw-XML `intrinsic_created` workaround works (stripped → EPOCH_ZERO).
- The cross-adapter determinism matrix runs (not skips) all three adapters in both no-intrinsic and
  intrinsic-preserved cases (6 params PASSED).

### Hard-Rule Status

| Hard Rule | Status | Evidence |
|-----------|--------|----------|
| No auto-publish | ✓ INTACT | pptx_adapter has no `publish`/`PUBLISHED`/`Review()` calls (only docstring references the rule); returns truth only. |
| Faithful, not suggestive | ✓ INTACT | Only verbatim shape text → claims; unreadable shapes → `unextracted[]`, never fabricated. SmartArt/chart/picture emit NO text claim. |
| AI-optional / minimal core | ✓ INTACT | python-pptx behind `[pptx]` extra, lazy; bare `import newsletters` does not pull pptx; `lint-imports` 1 kept/0 broken; transitive lxml/Pillow do not trip forbid-ai. 14 AI-isolation tests pass. |
| Every claim traces to evidence | ✓ INTACT | Claims content-addressed via shared `normalize()` → `Trace.from_source`; `is_addressed == True` live. |
| Determinism | ✓ INTACT | L1 front-fix verified across all 3 adapters; Source-determinism (L5) asserted per fixture. |
| Only python-pptx added as new direct dep | ✓ INTACT | `[pptx] = ["python-pptx"]`; core deps unchanged (pydantic/typer/sqlmodel); `.importlinter` forbid-ai-in-core unaffected. |

### Human Verification Required

None. All three success criteria are programmatically verifiable and were verified via independent
live probes + the full gate suite. (Phase 6 has no UI surface — `UI hint` not set for this phase;
the adapter is a deterministic library backend with executable golden proof.)

### Gaps Summary

No gaps. All four must-haves (3 ROADMAP success criteria + the carried L1 front-fix) are verified
in live code with independent evidence. The full test suite (383 passed, 1 xfailed), mypy,
import-linter, and the renderer build all pass on a re-run. The single observation (O-1: empty
typed `Trace.locator`) is an accepted cross-adapter project convention inherited from Phase 5, not
a Phase-6 regression, and the slide/shape locator is present and deterministic at the transcript
layer — so criterion 1 is met.

---

_Verified: 2026-06-17T17:01:12Z_
_Verifier: Claude (gsd-verifier)_
