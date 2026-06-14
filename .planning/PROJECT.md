# Newsletters

## What This Is

Newsletters is an open-source framework for **semantic information distillation**: it turns one
reviewed, evidence-traced record into multiple audience-specific communication surfaces (report,
article, newsletter, recorded show). It is for teams that need to collect, structure, and present
what they know — faithfully and auditably — to the right reader at the right time.

## Core Value

**The trust-and-publish layer is the product.** A deterministic, auditable pipeline that traces
every published claim to evidence and never auto-publishes — AI is an optional accelerator, never
an authority. If everything else fails, *this* must hold.

## Requirements

### Validated

<!-- Already built and working in Rev1 (src/newsletters/). Existing capability. -->

- ✓ Typed semantic model `Source → Claim(+Trace) → Distillation → Surface` — existing
- ✓ Review gate `Draft → InReview → Published`, no auto-publish path — existing
- ✓ Surfaces as presets over one parameterized `SurfaceTemplate` (report/article/newsletter/show) — existing
- ✓ Human-gated promotions: `Claim → KPI`, `Report → Article` — existing
- ✓ Deterministic capture: finished work session → Draft Report with no LLM (`capture.py`) — existing
- ✓ Token-faithful standalone HTML renderer (light/dark, signal colors, gate badge; no JS) — existing

### Active

<!-- Current scope. Hypotheses until shipped and validated. -->

- [ ] Make the core **AI-optional**: move `langchain` to an optional extra; the spine runs with zero AI deps
- [ ] Formalize **distill as a swappable socket** — one interface, backends: by-hand / OSS tool / AI
- [ ] **Format adapters** as the first borrowable backends: PowerPoint, Power BI, Excel, Email → faithful structured extraction → `Claim(+Trace)`
- [ ] Enforce **faithful, not suggestive** extraction (extract + trace, never editorialize)
- [ ] **Rev2 site fix** in the renderer/templates: split real Home from a Library status-board; real navigation; per-surface IDs; traceable source links
- [ ] **Work-surface installation**: install on a real work codebase; author Reports by hand; the Library shows how the work was done

### Out of Scope

- Owning the problem-solving agent — Newsletters owns capture + trust + publish; the working agent is the operator's
- Auto-publish of any kind — violates the human-in-the-loop core
- The V3 private learning layer (PulseIQ) — separate, proprietary; not in the open-source scope
- Telemetry / external calls on content — self-hostable, no phone-home

## Context

- **Brownfield.** Rev1 exists in `src/newsletters/` (models, capture, render, promote, semantic,
  templates, diagrams, dogfood) plus a deployed HTML Library on the `gh-pages` branch.
- **Token-constrained operator.** The immediate user builds reports by hand at work (few AI tokens);
  the deterministic, manual-first path is the primary workflow, not a fallback.
- **Open-core trajectory.** V2 = this open-source framework (speed-first, the industry play). V3 =
  PulseIQ, a private layer that learns over runs from captured usage ("manage by usage, not heavy
  reasoning"). V3 is documented here only as a boundary.
- **Prior art:** Onyx/Danswer & RAGFlow (private ingest), GenProve/Valsci/sciwrite-lint (claim
  provenance, science-focused), listmonk/Keila (delivery). No OSS does the integrated whole — that
  gap is the opportunity.

## Constraints

- **Tech stack**: Python 3.12 + Pydantic-style typed models — keeps outputs typed/auditable.
- **Security/Privacy**: self-hostable, MIT, no telemetry, no external calls on content.
- **Accessibility**: renders without JavaScript; WCAG AA; full light/dark via tokens.
- **Governance**: human-in-the-loop by design — no auto-publish, ever; every published claim traces to evidence.
- **AI**: provider-agnostic; one `distill()` boundary; the system must degrade gracefully to a no-AI mode.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| AI-optional, deterministic core | The trust layer is the product; AI must never hold authority | — Pending |
| Manual capture is first-class | The token-constrained operator is the primary user | — Pending |
| Distill is a swappable socket (hand / OSS / AI) | Decouples the pipeline from any backend; enables no-AI mode | — Pending |
| Format adapters first (PPT/Power BI/Excel/Email) | Deterministic, low-token; pulls structure already in the file | — Pending |
| Faithful, not suggestive | Editorializing breaks auditability; emphasis is the human's job | — Pending |
| Open-core: V2 Newsletters / V3 PulseIQ | Give away the trust framework, keep the learning engine | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-14 after initialization*
