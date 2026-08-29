---
phase: 3
slug: weekly-compose
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-29
planned: 2026-08-29
plans: 4
waves: 4
---

# Phase 3 — Validation Strategy

> Per-task map filled by the planner from 03-RESEARCH.md's Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (.venv; baseline 601 passed / 64 skipped — the 64 are ALL excel skips) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_compose.py tests/test_casespec.py -x -q` |
| **Full suite command** | `.venv/bin/python -m pytest -q` |
| **Estimated runtime** | ~20s quick · ~60–120s full |
| **Target at phase close** | full suite green with **`0 skipped`** (the 64 excel skips become passes once plan 03-04 installs `[excel]`) |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command
- **After every plan wave:** full suite + `.venv/bin/lint-imports`, **reading the skip count**, not just the colour
- **Before verification:** full suite · lint-imports · `newsletters check` ×3 · committed==fresh
  (NO new CSS — proven constraint) · ADAPT-05 clean diff · determinism `--check`
- Run each gate once per check

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| T1 — union insertion + docs tense | 03-01 | 1 | WKLY-02, WKLY-03 | T-03-16 | provenance-less `AssetBlock` unrepresentable (`asset` required, `evidence` min_length=1), asserted in both directions plus a constructing non-vacuity arm | unit (type-level) | `.venv/bin/python -m pytest tests/test_weekly_blocks.py tests/test_semantic.py -q` | ❌ created by task | ⬜ pending |
| T2 — four render branches + fail-loud dispatch | 03-01 | 1 | WKLY-02 | T-03-07, T-03-14, T-03-17 | no block silently dropped; every interpolation escaped via `_e()`; zero `_CSS` bytes changed | unit (adversarial) + regression | `.venv/bin/python -m pytest tests/test_weekly_blocks.py tests/test_render.py tests/test_publish.py tests/test_modulesite.py -q` | ❌ created by task | ⬜ pending |
| T3 — gate freeze replacement | 03-01 | 1 | WKLY-02 | T-03-08 | eight gate functions source-hash pinned; `semantic.py` diff vs `git merge-base HEAD origin/main` deletes zero lines; base-ref unavailable ⇒ FAIL, never skip | structural + mutation-observed | `.venv/bin/python -m pytest tests/test_semantic_gate_frozen.py tests/test_compose.py -q` | ❌ created by task | ⬜ pending |
| T1 — promote the span minter | 03-02 | 2 | WKLY-02 | T-03-18 | exactly one honest-span implementation; `tests/test_casespec.py` passes **unmodified** | regression + structural | `.venv/bin/python -m pytest tests/test_casespec.py tests/test_compose.py -q && .venv/bin/lint-imports` | ✅ test_casespec exists | ⬜ pending |
| T2 — eight-key schema + fixtures + denylist | 03-02 | 2 | WKLY-02 | T-03-04, T-03-13 | `safe_load` only via the lazy `[config]` boundary; unknown keys fail loud at both levels; fixture vocabulary joins the abstraction-guard denylist with a firing arm | unit + structural | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_abstraction_guard.py -q` | ❌ created by task | ⬜ pending |
| T3 — `load_weekly_spec` | 03-02 | 2 | WKLY-02 | T-03-01, T-03-06, T-03-11, T-03-12 | root containment before read; file-order minting (span-swap regression asserted on line numbers); no fabricated Trace for an unresolvable `source:`; gate sweep raises rather than emits | unit (adversarial) + determinism | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_casespec.py -q` | ❌ created by task | ⬜ pending |
| T1 — asset routing (7 rows) | 03-03 | 3 | WKLY-03 | T-03-02, T-03-03, T-03-05, T-03-10, T-03-19 | containment before any filesystem call; symlink target tested; sha256 re-checked at placement; image hashed never decoded; escape raises and never discloses | unit (adversarial, parametrized ≥7 cases) | `.venv/bin/python -m pytest tests/test_weeklyspec.py -q` | ❌ created by task | ⬜ pending |
| T2 — `build_weekly_report` + editorialization guard | 03-03 | 3 | WKLY-02 | T-03-09, T-03-11 | zero gate-advancing calls in the module; every block string is a transcript substring or a declared connective constant; planted paraphrase observed firing | unit (adversarial) + determinism | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_compose.py tests/test_casespec.py -q` | ❌ created by task | ⬜ pending |
| T1 — `weekly_slots` + deck render | 03-04 | 4 | WKLY-02 | T-03-20, T-03-09, T-03-21 | every slide line is authored text or a `surface.missing` member (self-checked, raises otherwise); Surface `model_dump()` identical after render and still DRAFT; marker + watermark read from the WRITTEN bytes | integration + determinism | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_pptx_writer.py -q` | ❌ created by task | ⬜ pending |
| T2 — values via ADAPT-03 | 03-04 | 4 | WKLY-04 | T-03-22, T-03-23 | no new adapter file; ADAPT-05 byte-unchanged vs merge-base; hostile workbook handling stays the adapter's (transferred, not re-implemented) | integration + structural (git) | `.venv/bin/python -m pytest tests/test_weekly_values.py tests/test_excel_adapter.py tests/test_powerbi_adapter.py -q` | ❌ created by task | ⬜ pending |
| T3 — the `weekly` CI job + compass/RETRO | 03-04 | 4 | WKLY-04, WKLY-02 | T-03-15 | nine previously-unrun modules execute in CI with `0 skipped` asserted and `fetch-depth: 0` so the base-ref gates can run; `bare-install` byte-untouched | CI (verified by running the job's exact command locally) | `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_weekly_blocks.py tests/test_weekly_values.py tests/test_semantic_gate_frozen.py tests/test_casespec.py tests/test_compose.py tests/test_swimlane.py tests/test_abstraction_guard.py tests/test_excel_adapter.py -q` | ❌ created by task | ⬜ pending |

**Sampling continuity:** every one of the eleven tasks carries an `<automated>` command. No three
consecutive tasks pass without an automated verify; no watch-mode flags anywhere.

**Non-vacuity is mandatory** (RETRO rule "assert the inversion, or you have not asserted the
condition"). Five mutation observations are required by acceptance criteria and must be recorded in
the owning SUMMARY, not merely claimed:

| # | Mutation | Owning task | Expected |
|---|----------|-------------|----------|
| 1 | append a line inside `Surface.publish` | 03-01 T3 | gate-freeze test RED, green after `git checkout --` |
| 2 | reverse two mint calls for the duplicated person | 03-02 T3 | span-swap regression RED |
| 3 | delete the asset path containment check | 03-03 T1 | root-escape case RED |
| 4 | plant a paraphrase into a composed surface | 03-03 T2 | editorialization guard RED |
| 5 | make `weekly_slots` emit a literal `"—"` for an empty section | 03-04 T1 | membership self-check RED |

---

## Wave 0 Requirements

- [ ] `.venv/bin/pip install -e '.[excel]'` — **owned by plan 03-04 Task 2** (its first action).
      openpyxl is absent; ALL 64 baseline skips are excel skips; WKLY-04 cannot be proven without
      it. The task's acceptance criteria require reading the skip count before (64) and after (0).
- [ ] **CI coverage gap (blocker-level)** — **owned by plan 03-04 Task 3.** No CI job installs
      `[excel]`, and `test_casespec` / `test_compose` / `test_swimlane` / `test_abstraction_guard`
      run in NO job. The new `weekly` job installs `.[test,config,excel,pptx]`, names the nine
      compose-path modules, asserts `0 skipped`, and sets `fetch-depth: 0`. `bare-install` stays
      byte-untouched (PKG-03).
- [ ] **The semantic.py protection changes shape** — **owned by plan 03-01 Task 3.** The union
      addition is sanctioned, so the blanket byte-unchanged gate is replaced by (a) source-hash
      pins on the eight gate functions and (b) a zero-deleted-lines diff-shape assertion against
      `git merge-base HEAD origin/main` — never `HEAD`. `tests/test_compose.py`'s existing gate is
      repaired to the base ref and drops `semantic.py` from its list, saying where the protection
      moved.

**Recorded discretionary decisions — RESOLVED by the plans (implement, do not reopen):**

| Decision | Resolution | Owning plan |
|----------|-----------|-------------|
| SC-5 deck scope | **TEXT-ONLY** render through Phase 2's writer; no image placement (the writer has no `add_picture` path and no criterion budgets it). Asset images live on the HTML surface. Recorded in `docs/weekly-spec.md`; raised in the PR body as a round-two item | 03-04 T1 |
| Diff base for shape gates | `git merge-base HEAD origin/main`; **fail, never skip**, if unresolvable — a skip here recreates W21. Requires `fetch-depth: 0` on the job | 03-01 T3, 03-04 T2/T3 |
| Empty-section handling | `weekly_slots` always emits all four `NL_` keys; an empty section's single line **is** that section's own `missing[]` disclosure, with a membership self-check that raises otherwise. Needs no writer change and invents no prose. Supersedes 03-RESEARCH's "omit empty slots" for slots the template declares | 03-04 T1 |
| Weekly fixture identifiers on the abstraction-guard denylist | `"Shuttlebay Operations"`, `"Miles O'Brien"`, `"Kira Nerys"`, `"Julian Bashir"`, `"bay-cycle-throughput"`, `"crew-rota-board"`, `"Bay Rotation Registry Delta"`, `"Docking Clamp Cycle Count"` — added as `_WEEKLYSPEC_FIXTURE_VALUES` and unioned into `_DENY_LITERALS`, with a firing arm | 03-02 T2 |
| ROADMAP's `.csv` wording | Values enter as `.xlsx` exports (the live ADAPT-03 path); a CSV reader would be a new adapter WKLY-04 forbids. Recorded as a wording clarification in `tests/test_weekly_values.py`'s docstring — not scope | 03-04 T2 |

**Planner discretion exercised (logged here so the SUMMARYs can cite one place):**

| Choice | Resolution | Reason |
|--------|-----------|--------|
| Module layout | `specspan.py` (promoted minter) + `weeklyspec.py`; no `assets.py`; block models in `semantic.py` | every block sub-model already lives in `semantic.py`; a separate module would have to stay semantic-free to avoid a cycle, for no gain |
| Span minter reuse | **Promoted** (`_SpanMinter` → `specspan.SpanMinter`), not forked and not privately cross-imported | `pptx_writer.py` exists because two normalizers drift; two span minters drift identically. No test references the private name |
| Compose reuse | `compose._addressed` promoted to public `compose.addressed`, imported by the weekly composer; `compute_delta` imported unchanged; `compose_module_report` NOT called (it is a whole-Surface builder with its own id/Ledger/fanout) | one trust predicate, policed by `compose`'s 20+ existing tests |
| Surface identity | `title = spec.week`, `eyebrow = spec.module`, each carried **verbatim, never joined** | a join would be composer-authored connective text |
| Empty blocks | omitted rather than emitted empty; the absence is in `missing[]` | an empty `div.block` renders noise and asserts nothing |
| Nested unknown keys | fail loud, same voice as the top level | a mistyped `resaon:` would otherwise drop authored content silently |
| Recognition evidence | resolved `source:` ⇒ one **span-less** `Trace(source_id=…)`; absent or unresolvable ⇒ `evidence=[]` + disclosure | the loader has not read the external source's text; minting a span for it would be fabrication |
| Asset record location | in-document (`assets:` subtree is the record, the spec file is its `Source`) | `Source.transcript` is a `str`, so a binary can never be a `Source`; the `sha256` hex traces verbatim. Standalone record files stay possible later with a second `Source` |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Composed weekly deck opens in real PowerPoint | WKLY-02 | carried A8 — no `.pptx` consumer in this environment | EiC at PR review |
| Deck-image scope call (text-only accepted?) | WKLY-03 | product judgement | Raised in the PR body as a recorded decision + round-two item (03-04 T1 writes it into `docs/weekly-spec.md` first) |
| First observed CI green for the new `weekly` job | WKLY-04 | no `gh` CLI in this environment | PR review; the job's exact command is proved locally in 03-04 T3 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (each assigned to an owning task)
- [x] No watch-mode flags
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planned 2026-08-29 — 4 plans, 4 waves, 11 tasks.
