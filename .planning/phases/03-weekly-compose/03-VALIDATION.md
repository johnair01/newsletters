---
phase: 3
slug: weekly-compose
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
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

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command
- **After every plan wave:** full suite + `.venv/bin/lint-imports`
- **Before verification:** full suite · lint-imports · `newsletters check` ×3 · committed==fresh
  (NO new CSS — proven constraint) · ADAPT-05 clean diff · determinism `--check`
- Run each gate once per check

---

## Per-Task Verification Map

*(Planner fills.)*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner fills) | | | WKLY-02/03/04 | — | provenance-less placement unrepresentable; no editorialization; gate functions source-hash-pinned | unit | pytest | — | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `pip install -e '.[excel]'` into .venv — openpyxl absent; ALL 64 baseline skips are excel
      skips; WKLY-04 cannot be proven without it (research finding, blocker-level)
- [ ] **CI coverage gap (blocker-level):** no CI job installs `[excel]`, and
      `test_casespec/test_compose/test_swimlane/test_abstraction_guard` run in NO job. The plan
      must extend CI additively (the Phase-2 `pptx` job precedent) so the weekly/compose/excel
      proofs actually execute in CI; `bare-install` stays byte-untouched.
- [ ] The semantic.py protection changes shape: the union addition is sanctioned, so the blanket
      byte-unchanged gate is replaced by (a) source-hash pins on the eight gate functions
      (research names them) and (b) a zero-deleted-lines diff-shape assertion against
      `git merge-base HEAD origin/main` — never `HEAD` (the working-tree gate is vacuous in CI,
      proven).

**Recorded discretionary decisions (log in plans/SUMMARY):**
- SC-5 deck scope = TEXT-ONLY render through Phase 2's writer (no image placement in the deck —
  the writer has no add_picture path and no criterion budgets it). Asset images live in the HTML
  surface; deck image placement is an honest "round two" open item for the PR.
- Diff base for shape gates = `git merge-base HEAD origin/main`.
- Empty weekly sections must BOTH disclose in `missing[]` AND leave the deck renderable
  (mechanism = planner's choice, consistent with faithful-not-suggestive and the writer's
  blank-content refusal; a factual "—" marker or an explicitly-allowed-empty slot both
  acceptable — no invented prose).
- Weekly fixture identifiers go on the abstraction-guard denylist (planner names them).
- ROADMAP's ".csv" wording: values enter as `.xlsx` exports (the live ADAPT-03 path); a CSV
  reader would be a new adapter WKLY-04 forbids — record as a wording clarification, not scope.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Composed weekly deck opens in real PowerPoint | WKLY-02 | carried A8 | EiC at PR review |
| Deck-image scope call (text-only accepted?) | WKLY-03 | product judgement | Raised in PR body as recorded decision + round-two item |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
