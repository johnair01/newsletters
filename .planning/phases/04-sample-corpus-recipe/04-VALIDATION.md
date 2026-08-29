---
phase: 4
slug: sample-corpus-recipe
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
---

# Phase 4 — Validation Strategy

> Per-task map filled by the planner from 04-RESEARCH.md's 17-row requirements→test map.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (.venv; baseline 837 passed / 0 skipped) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `.venv/bin/python -m pytest tests/test_weeklysite.py tests/test_publish.py -x -q` |
| **Full suite command** | `.venv/bin/python -m pytest -q` |
| **Measured baselines (no-NEW-failures reference, this branch, 2026-08-29)** | 837/0 · lint-imports 2 kept · mypy 15 errors in 5 files · black 69 would-reformat · isort DEF-15 set |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command
- **After every plan wave:** full suite + lint-imports
- **Before verification:** the FULL carried gate set — pytest · lint-imports · `newsletters check`
  over ALL FOUR corpora · committed==fresh for all four (incl. the committed deck via the
  stdlib digest tier + the `[pptx]` fresh==committed tier) · bare-install untouched ·
  mypy/black/isort no-NEW-failures vs the measured baselines above
- Run each gate once per check

---

## Per-Task Verification Map

*(Planner fills from the research's 17-row map.)*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner fills) | | | WKLY-05/06 | — | sample ships Draft; nothing publishes; no external calls | — | — | — | ⬜ pending |

---

## Wave 0 Requirements

**Recorded discretionary decisions (implement, don't reopen):**
- Sibling corpus `content/weekly/` with new `weeklysite.py`; bindings reuse the committed
  `content/module/*.yml` (the "lineage"; supplies the KPI-less lane).
- Deck lives at `content/weekly/deck/` + `.digest` sidecar, NOT served by `assemble_site`
  (structural no-publish). No download link on the page — recorded with the research's costed
  one-task reversal (FanoutBlock route) for round two.
- `check --corpus weekly` wired AND proven to BLOCK on a planted blocker (never vacuously
  green) — the v1.2 "gate that only sees clean input proves nothing" rule.
- Phase 3 code untouched (`build_weekly_report` traces behavior measured harmless).
- `.xlsx` values stay OUT of the corpus build path (merge-block and deploy-pages don't install
  `[excel]`); the values proof lives in the `weekly` CI job's tests only.
- The synthetic `.eml`'s From: header must not trip `test_modulesite`'s `_EMAIL_RE`
  confidentiality scanner (research-flagged collision — design the fixture around it and test).
- All 16 integration sites from the research checklist covered; the four Records-strip HTML
  files regenerate; ledgers stay append-only.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Deck opens in real PowerPoint | WKLY-05 | carried A8 | EiC at PR review (deck committed in-repo) |
| Recipe passes the not-the-author bar | WKLY-06 | prose judgement | EiC reads docs/weekly.md cold at PR review; commands were machine-executed in-phase as SC-4 proof |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] No watch-mode flags
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
