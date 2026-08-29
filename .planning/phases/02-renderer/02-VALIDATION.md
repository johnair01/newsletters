---
phase: 2
slug: renderer
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-29
updated: 2026-08-29
---

# Phase 2 — Validation Strategy

> Per-phase validation contract. Per-task map filled by the planner from 02-RESEARCH.md's
> 25-row requirements→test map.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (venv exists at `.venv`; python-pptx 1.0.2 installed) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_pptx_writer.py tests/test_pptx_determinism.py -x -q` |
| **Full suite command** | `.venv/bin/python -m pytest -q` (baseline 567 passed / 64 skipped) |
| **Estimated runtime** | ~15s quick · ~60–120s full (the 3-second determinism sleep is module-scoped and happens once) |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command
- **After every plan wave:** full suite + `.venv/bin/lint-imports`
- **Before verification:** full suite · lint-imports KEPT · `newsletters check` ×3 ·
  `git diff --exit-code -- content/ tests/fixtures/pptx/*.pptx tests/fixtures/weekly/template.pptx src/newsletters/semantic.py` ·
  determinism `--check`
- **Max feedback latency:** 120 seconds; run each gate once per check

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement / SC | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|------------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-T1 | 02-01 | 1 | WKLY-01 / SC-2, SC-5 | T-02-01, T-02-02, T-02-11 | Duplicate zip-member refusal and the in-memory (no-path-join) zip-slip property survive the promotion verbatim; `sys.path` shadowing mechanism removed (IN-03) | integration + regression | `.venv/bin/python -m pytest tests/test_pptx_determinism.py tests/test_pptx_golden.py tests/test_pptx_adapter.py -q` · `.venv/bin/python tests/fixtures/weekly/_record_determinism_evidence.py --check` · `git diff --exit-code -- tests/fixtures/pptx/ tests/fixtures/weekly/template.pptx src/newsletters/semantic.py` | ✅ retarget | ⬜ pending |
| 02-01-T2 | 02-01 | 1 | WKLY-01 / SC-5 | T-02-04 | Writer module has zero column-0 `pptx` imports and imports under a `sys.meta_path` block; `[pptx]` extra holds exactly one requirement (floor-pinned) | guard | `.venv/bin/python -m pytest tests/test_ai_optional.py -q` · `.venv/bin/lint-imports` | ✅ extend | ⬜ pending |
| 02-01-T3 | 02-01 | 1 | WKLY-01 / SC-1 | T-02-03, T-02-10 | Pathological decks are authored in `tmp_path` only; no XML parser constructed; committed fixture corpus unchanged | unit (self-test) | `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` · `git diff --exit-code -- tests/fixtures/weekly/template.pptx` | ❌ new (this task) | ⬜ pending |
| 02-02-T1 | 02-02 | 2 | WKLY-01 / **SC-1** | T-02-04, T-02-05, T-02-12, T-02-13 | Fail loud BOTH directions naming the offender; duplicate shape name refused; group-nested slot bound not dropped; non-text slot gets a teaching `ValueError`, never `AttributeError`; reserved watermark name refused | unit | `.venv/bin/python -m pytest tests/test_pptx_writer.py -x -q` · `.venv/bin/lint-imports` | ❌ new (this task) | ⬜ pending |
| 02-02-T2 | 02-02 | 2 | WKLY-01 (fidelity) | T-02-14, T-02-15 | Operator `rPr`/`pPr` inherited, never constructed; XML metacharacters escaped by python-pptx and round-tripped; `fit_text` banned by name (machine-dependent font lookup) | integration | `.venv/bin/python -m pytest tests/test_pptx_writer.py -x -q` | ❌ new (this task) | ⬜ pending |
| 02-02-T3 | 02-02 | 2 | WKLY-01 / **SC-3, SC-4** | T-02-06, T-02-07, T-02-08 | Marker + gate state read back off the WRITTEN file (Draft and Published halves); no assignment to any `Surface` field; `out_path` never derived from `surface.id` | integration + guard | `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` · `git diff --exit-code -- src/newsletters/semantic.py` · `.venv/bin/lint-imports` | ❌ new (this task) | ⬜ pending |
| 02-03-T1 | 02-03 | 3 | WKLY-01 / **SC-2** | T-02-18 | Byte equality across a real 3-second gap WITH the negative control (assertion C) and the implementation-independent `part_digest` (assertion A); no render-vs-template comparison anywhere | integration | `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` · `.venv/bin/python -m pytest tests/test_pptx_determinism.py -q` | ❌ new (this task) | ⬜ pending |
| 02-03-T2 | 02-03 | 3 | WKLY-01 / **SC-5** (sample renders) | T-02-10 | A real `Surface(REPORT, Draft)` renders through the committed synthetic template; unprefixed `Footer` untouched; Draft vs Published digests differ | integration (acceptance) | `.venv/bin/python -m pytest tests/test_pptx_writer.py -q` · `git diff --exit-code -- tests/fixtures/ src/newsletters/semantic.py` · determinism `--check` | ❌ new (this task) | ⬜ pending |
| 02-03-T3 | 02-03 | 3 | WKLY-01 / **SC-5** (in CI) | T-02-16, T-02-17, T-02-SC | A CI job installs `.[test,pptx]` and RUNS the pptx tests (0 skipped); `bare-install` byte-untouched and still extras-free | CI + static | `.venv/bin/python -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/ci.yml')); sys.exit(0 if 'pptx' in d['jobs'] else 1)"` · `.venv/bin/python -m pytest tests/test_pptx_writer.py tests/test_pptx_determinism.py tests/test_pptx_golden.py tests/test_pptx_adapter.py tests/test_pptx_loader.py -q` | ❌ new (this task) | ⬜ pending |

**Sampling continuity:** every one of the nine tasks carries an `<automated>` verify; there is no
run of three tasks without one. The four assertion letters are all placed: **A** `part_digest`
(02-03-T1, inherited by Phase 4), **B** full-byte double render (02-03-T1), **C** the negative
control (02-03-T1, plus the untouched Phase 1 module), **D** formatting fidelity (02-02-T2 — the
only automated way to see Pitfall 1's silent downgrade).

---

## Wave 0 Requirements

- [x] **CI gap (W21, blocker-level):** planned as `02-03-T3` — a new `pptx` job installing
      `.[test,pptx]` and running the five pptx test modules. The `bare-install` job stays
      byte-untouched; this is the phase's only authorized CI change and is not widened.
- [x] Writer module `src/newsletters/pptx_writer.py` — planned as `02-01-T1` (stdlib normalizer
      promoted verbatim, module level, bare-importable) and `02-02-T1..T3` (the writer half, lazy
      python-pptx through the existing `adapters._pptx_loader._load_pptx()` boundary).
- [x] `tests/test_pptx_writer.py` — planned as `02-01-T3` (scaffold + in-test deck builders) then
      extended by `02-02-T1..T3` and `02-03-T1..T2`.
- [x] Sample `Surface(REPORT)` fixture for the CI render — `_sample_weekly_surface()` helper in
      `02-02-T3`, exercised end to end in `02-03-T2`.
- [x] Recorded discretionary decisions (P-01..P-08, logged in `02-01-PLAN.md`): module name
      `pptx_writer.py` without the underscore; entry points `render_surface_pptx_bytes` /
      `render_surface_pptx` (not `render_weekly_deck` — D-01 keeps the semantic kind out of the
      format layer); explicit `slots` mapping API (block-kind derivation is Phase 3's job); the
      decision note implemented verbatim including the binary `contentStatus`, with the tri-state
      amendment raised at PR review; **IN-04 REJECTED** — the fixture instant stays non-epoch as a
      falsifiability control, with a comment saying so.
- [x] **Template fixture: deliberately NOT regenerated (P-06).** `02-RESEARCH` proposed upgrading
      the committed `template.pptx`; the planner rejected that on evidence.
      `.planning/notes/2026-08-29-pptx-determinism-evidence.json` records `part_digest_a`/
      `part_digest_b` computed from that template and both are in the recorder's `CHECKED_FIELDS`,
      so regenerating turns this phase's own `determinism --check` gate red and makes the recorded
      decision note's cited digests stale — retiring committed evidence for test convenience. The
      rich and pathological decks live in `tmp_path`, authored by named builders in `02-01-T3`,
      which is how the research measured W17/W14 in the first place.
- [x] Retarget `tests/test_pptx_determinism.py`, `_author_template.py`,
      `_record_determinism_evidence.py` and delete the three `sys.path.insert` lines — `02-01-T1`
      (closes IN-03).
- [x] `python-pptx>=1.0.2` floor pin — `02-01-T2` (safe; W19 closes A7 by execution).

### Deliberately NOT in this phase (surfaced, not dropped)

| Item | Disposition | Reason | Carried to |
|------|-------------|--------|-----------|
| `tests/fixtures/pptx/_author_fixtures._normalize_zip` delegates to the promoted `normalize_opc_zip` (IN-02's ADAPT-06 half) | **deferred** (P-08) | Delegation swaps `_FIXED_ZIP_DATE_TIME` (2026-01-01) for `DOS_EPOCH` and adds `create_system=0`, so the nine ADAPT-06 binaries stay correct only if regenerated — which this phase's own pre-verification gate `git diff --exit-code -- tests/fixtures/pptx/*.pptx` forbids and which the orchestrator constrained explicitly. A byte-neutral delegation would mean parameterizing the promoted module on the exact axes the promotion exists to pin. **IN-02's second half is satisfied the other way CONTEXT permits** — the weekly fixture normalizer is *superseded* (deleted) and the promoted module already carries the `create_system=0` pin. `02-01-T1` fixes the stale pointer in `_author_fixtures.py`'s docstring so the repo does not silently disagree with itself. | Phase 4 (where the committed==fresh `.pptx` gate lives) |
| `word_wrap=True` / `auto_size=NONE` on the **shipped** operator template (Pitfall 3 mitigation 1) | **deferred** (P-07) | Follows from P-06 — applying it means regenerating the committed template. Applied to the in-test decks now; mitigations 2 and 3 (document the limit; cover it in the human look) are already in place. | Phase 4 `docs/weekly.md` operator recipe |
| Bare-runnable normalizer tests (duplicate-member refusal + idempotence on the `bare-install` job) | **out of scope** | A real payoff of the promotion, but it needs a new non-`importorskip` test module and is not required by any Phase 2 success criterion. Scope discipline: renderer + tests + CI job only. | Phase 4 |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Normalized deck opens in real PowerPoint | WKLY-01 | No `.pptx` consumer in this environment (`libreoffice-core` has no Impress filters) | EiC opens the deck produced by `test_sample_surface_renders_through_the_committed_template` at PR review and confirms: opens clean (no repair prompt) · DRAFT watermark visible and legible · operator bullets/fonts survived the fill · a deliberately-overfull slot looks acceptable (Pitfall 3) · marker readable in File → Info. Closes A8, A4 and Pitfall 3 together. Carried from Phase 1. |
| `cp:contentStatus` binary vs 3-state `ReviewState` | WKLY-01 | Spec amendment is the EiC's call | Implemented verbatim per P-04; raised in the PR body as an open item, never deviated from silently |
| Decision note wording: `cp:identifier` → `dc:identifier` (W20) | WKLY-01 | Doc amendment | Raised in the PR body; no code consequence — python-pptx's attribute name and the read-back assertion are both already correct |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 9/9
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (writer module, test module, CI job, sample Surface)
- [x] No watch-mode flags
- [x] Feedback latency < 120s (quick command ~15s; the one 3-second sleep is module-scoped)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner-signed 2026-08-29 (pending execution)
