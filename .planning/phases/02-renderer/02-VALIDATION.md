---
phase: 2
slug: renderer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
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
| **Estimated runtime** | ~15s quick · ~60–120s full |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` command
- **After every plan wave:** full suite + `.venv/bin/lint-imports`
- **Before verification:** full suite · lint-imports KEPT · `newsletters check` ×3 ·
  `git diff --exit-code -- content/ tests/fixtures/pptx/*.pptx` · determinism `--check`
- **Max feedback latency:** 120 seconds; run each gate once per check

---

## Per-Task Verification Map

*(Planner fills from 02-RESEARCH.md's requirements→test map.)*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner fills) | | | WKLY-01 | — | writer never mutates review state; fail-loud both directions incl. grouped/textless shapes | unit | pytest | — | ⬜ pending |

---

## Wave 0 Requirements

- [ ] **CI gap (research finding, blocker-level):** no CI job installs `[pptx]` — SC-5's
      "sample Surface renders through it in CI" requires a CI change. The plan must add a
      pptx-enabled test job (or extend an existing non-bare job) WITHOUT touching the
      bare-install job (which must stay extras-free and AI-free). This is a deliberate,
      scoped exception to "CI untouched" — the bare-install gate itself is untouched.
- [ ] Writer module `src/newsletters/pptx_writer.py` (lazy pptx import; stdlib-importable at
      module level) + normalizer promotion per decision note (IN-02 create_system pin lands here)
- [ ] Recorded discretionary decisions (log in plan/SUMMARY): explicit `slots` mapping API;
      decision note implemented verbatim (contentStatus binary — amendment raised at PR review);
      IN-04 rejected — fixture instant stays non-epoch as a falsifiability control

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Normalized deck opens in real PowerPoint | WKLY-01 | No `.pptx` consumer in this environment | EiC opens the sample deck at PR review (carried from Phase 1) |
| `cp:contentStatus` binary vs 3-state ReviewState | WKLY-01 | Spec amendment is EiC's call | Raised in the PR body as an open item |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
