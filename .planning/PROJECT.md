# Newsletters

## What This Is

Newsletters makes how work gets done **legible** — it turns the messy record of an organization or
codebase into clear, audience-specific stories people can read, trust, and act on. One reviewed,
evidence-traced record fans out into audience-tuned surfaces (report, article, newsletter, recorded
show, and a learning/onboarding surface for newcomers). The aim: **turn information into
conversation, and conversation into action** — work made transparent, digestible, and traceable to
its sources.

Mechanically it is a typed distillation pipeline (`Source → Claim(+Trace) → Distillation → Surface`)
with claim-level provenance and a human review gate. But the pipeline is the means; **sense-making
for people is the point.**

## Core Value

**Make work legible and trustworthy to people** — distil what happened into clear, audience-tuned
surfaces where every claim traces to its evidence and nothing publishes without a human. The
deterministic, auditable trust layer is what makes that legibility *believable*; AI is an optional
accelerator, never an authority. If everything else fails, *this* must hold.

## How it's used

One engine, every context: **Sources → Report (reviewed) → Article (peer-reviewed) → Newsletter
(audience-cut)** — each arrow a human-gated promotion. Sources span emails, chats, M365
transcripts/summaries, SQL, PowerPoints, code, and **live interviews**. The robots are
**interviewers** — they interview you, your work, and your codebase — and run **low-token by
default** (cheapest models; format consistency keeps extraction cheap). Distill is **generic**, not
template-specific.

| Context | Report (reviewed) | → Article (peer-reviewed) | → Newsletter |
|---|---|---|---|
| Work — quality event | investigation → filled template-report; engine finds gaps, interviews you | faithful event article, reviewed by your boss | rolls into the weekly |
| Work — weeklies | per **swim lane** (its KPIs/topics): robots pull emails/M365/SQL; stream owner reviews | swim-lane weekly summary | your weekly, cut across all swim lanes |
| Work — interns | interns interview people, find bottlenecks → validated reports | good ideas promoted up | shared up the org |
| PulseIQ | interviews + code/business changes → tracked reports | victories / losses / decisions | team newsletter |
| Newsletters itself | choices, growth, adoption → reports | the decisions | the open build story |

An Article can also explain an **artifact** (e.g., a code file) in human terms — the robot deciding
what matters.

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
- [ ] **Learning / onboarding surface**: re-cut reviewed records for newcomers and training cohorts — digestible, traceable, sequenced

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
- **Versioning vs phases.** "V2 / V3" are *product lines* (V2 = this open-source Newsletters; V3 =
  PulseIQ, private). The GSD 12-phase roadmap is the *current build of V2* — a different axis from
  the product-line versions; don't conflate them.
- **Usage narrative.** See **How it's used** above. In short: a token-constrained lead's real work
  (PowerPoints, email, M365, SQL, code, interviews) is gathered **low-token and generically** into
  traced Reports, promoted through peer review to Articles and Newsletters — a Library that shows how
  the work was done, for teammates, stakeholders, and newcomers. **Design the surface first, then
  gather the data.**
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
| Design the surface first, then gather data | Decide what the artifact should look like, then go find the inputs | — Pending |
| Learning/onboarding is a first-class surface | Teaching newcomers / training cohorts is a primary use, not an afterthought | — Pending |
| Connection/relationship view — parked | "Make sense of how things connect" is real but deferred until after core V2 | — Pending |
| Low-token, generic extraction (not no-AI, not per-template) | Cheapest models + format consistency; manual is the floor | — Pending |
| Agents are interviewers (a distill modality) | Interview you / your work / your codebase to fill gaps faithfully | — Pending |
| Promotion chain Report → Article → Newsletter is the spine | Each human-gated; the real-world shape of the model's promotions | — Pending |

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
