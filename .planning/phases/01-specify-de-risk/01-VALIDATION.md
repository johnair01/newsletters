---
phase: 1
slug: specify-de-risk
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing suite; 639 green at v1.2 close + Case Spec additions) |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `python -m pytest tests/ -x -q -k "spike or casespec"` (scope to touched areas) |
| **Full suite command** | `python -m pytest tests/ -q` |
| **Estimated runtime** | ~60–120 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run the quick command scoped to the task's test file
- **After every plan wave:** Run the full suite command
- **Before verification:** Full suite green + `lint-imports` KEPT + bare-install untouched
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

*(Filled by the planner — Phase 1 tasks are spec + spike; the spike's evidence file and its
read-back assertions are the automatable core.)*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner fills) | | | de-risks WKLY-01/02 | — | no core→pptx import edge | unit | `lint-imports` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `python-pptx` is NOT installed in this environment — spike tasks must `pip install '.[pptx]'`
      (or a scratch venv) as an explicit first step (research finding, blocker-level)
- [ ] Spike evidence lands as a committed artifact (hashes + varying-part listing) under the phase
      dir or `.planning/notes/`; scratch code deleted or converted to a test fixture

*Existing pytest infrastructure covers everything else.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| A normalized deck opens in real PowerPoint/Impress | de-risks WKLY-01 | No `.pptx` consumer in this environment (libreoffice-core lacks Impress filters — measured) | EiC opens the Phase-4 sample deck at PR review; flagged as an open item in the PR |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
