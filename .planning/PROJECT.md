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

## Shipped Milestone: v1.1 Swim-Lane Module Report (Shipped 2026-07-02)

**Delivered:** The smallest fully-real, config-driven Report composer that cuts one owned module
across its swim lanes — the spine existed; v1.1 built the missing composer. 4 phases, 12 plans,
12/12 requirements, PRs #4–#8 (build) + #9–#16 (deep-review close). Formally closed per GSD at
deep-review Round 10; see `.planning/v1.1-MILESTONE-AUDIT.md` and `.planning/MILESTONES.md`.

**Shipped features:**
- Swim-lane binding + traced YAML loader — lane → `FunctionalGroup`+`Kpi`s/`Objective`s; every
  loaded value becomes a `Claim`/`KpiItem` traced to its YAML source (or a declared slot)
- Module-scope Report composer — per-lane `KpiStripBlock` (start→close Δ computed at compose time
  into `KpiItem.delta`; NO start/baseline field on `Kpi`) + `ClaimsBlock`; unsubstantiated →
  `Surface.missing[]`; stable `R-NNN` from the ledger; `Draft` state
- Worked synthetic Module Report (`module-a`, fabricated naming scheme) rendered into `content/`,
  Library-visible and gate-visible (method-docs sub-task skipped — companion files absent)
- Signals-voice PR/summary — `ship` workflow PR bodies read as Signals dispatches, generated from
  diff + verbatim gate output; may not weaken any gate

**Fundamental principle (JJ, 2026-07-02):** ABSTRACT EVERYTHING. Core code carries data models
only; module/lane/owner specifics are **configs** (YAML), never hardcoded. Any org's team shape
must fit without touching `src/`. Enforced by a test that fails if fixture-specific names leak
into source code.

**Unit-of-work model:** a Report is a swim lane, a project/initiative, or an interview — audited
by its owner. This milestone builds the swim-lane kind ONLY; the section abstraction stays generic
enough for the other kinds to slot in later.

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

<!-- Next-milestone scope. Set 2026-07-03 by the Editor-in-Chief: v1.2 The Published Record. -->

- **Milestone v1.2 — The Published Record: one channel, production-ready** (opened 2026-07-03;
  set by the Editor-in-Chief after live publish forensics found the deployed site is a stale
  hand-pushed snapshot and the automated deploy has failed 4/4 runs while building the wrong
  artifact — see `.planning/research/2026-07-03-pages-publish-forensics.md`). Scope: PUB-01..05
  (`.planning/REQUIREMENTS.md`) — the rendered record IS the published site (rev1 root +
  /work/ + /module/, cross-linked, styled 404); one deploy channel republishes exactly what a
  human merged to main (gate-checked, force-push to gh-pages); linkability/drift/gating become
  PR-blocking tests. The fix-batch PR (B1–B20) and DEF-04/05/11 remain queued behind it.

### Validated in v1.1 (2026-07-02, Phases 1–4)

- ✓ **Swim-lane binding + traced YAML loader** — lane → `SectionBinding` at the parsed-dict level;
  every scalar minted via `Trace.from_source` or routed to `unextracted[]` under a read-anchored
  coverage identity enforced in code (LANE-01/02) — v1.1
- ✓ **Module-scope Report composer** — one `Surface(REPORT, Draft)` per module: per-lane KPI strip
  (Δ at compose time into `KpiItem.delta`) + traced claims; `missing[]` honesty routing; stable
  `R-NNN`; Holes A+B closed at the composer (COMP-01..04) — v1.1
- ✓ **Worked synthetic Module Report** — `module-a` synthetic config renders end-to-end into a
  self-contained `content/module/` corpus, Library-visible + gate-visible, byte-stable (MODA-01/02) — v1.1
- ✓ **Signals-voice PR bodies** — `ship` workflow emits six-section evidence-first dispatches
  (Start here / signal / learned / verified-verbatim / not-here / how-to-verify), guarded against
  silent reversion (VOICE-01/02) — v1.1
- ✓ **Abstraction guard** — no fixture/org-specific name in `src/`; fired 3× on real leaks and
  out-enforced the plan's own suggested defaults (LANE-03) — v1.1

### Validated in v1.0 (2026-06, Phases 1–13)

- ✓ AI-optional core — `[ai]` extra, import-linter contract, bare-install CI gate (Phase 2)
- ✓ Distill as a swappable socket — `DistillPort` + registry + manual backend + conformance suite (Phase 1)
- ✓ Format adapters: Email, Excel, PPTX, Power BI — faithful extraction, zero silent drops (Phases 4–7)
- ✓ Faithful-not-suggestive enforcement — content-addressed traces + span-containment gate (Phase 3)
- ✓ Rev2 site fix — Home/Library split, nav, stable IDs, source links (Phases 8–9)
- ✓ Reviewer surfacing + merge-block gate — honesty panel, `newsletters check` CI (Phase 10)
- ✓ Work-surface installation — dogfooded on this repo (Phase 11)
- ✓ Learning/onboarding surface + Problem lifecycle entity (Phases 12–13)

### Out of Scope

- Owning the problem-solving agent — Newsletters owns capture + trust + publish; the working agent is the operator's
- Auto-publish of any kind — violates the human-in-the-loop core
- The V3 private learning layer (PulseIQ) — separate, proprietary; not in the open-source scope
- Telemetry / external calls on content — self-hostable, no phone-home

## Context

- **Post-v1.1 state (2026-07-02).** The composer spine ships: `swimlane.py` (traced YAML loader),
  `compose.py` (pure composer), `modulesite.py` (module corpus builder), the `--corpus module` CLI,
  and the Signals-voice `ship` contract. 626 tests green (574 at v1.1 start), 2 import contracts
  KEPT, three byte-stable corpora (`rev1`/`work`/`module`). Carried forward: the B1–B20 unguarded-arm
  backlog (one fix-batch PR) and 12 deferred features (DEF-01..12). All v1.1 work lives on the
  integration branch; the maintainer decides the integration→main merge.
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
| AI-optional, deterministic core | The trust layer is the product; AI must never hold authority | ✓ Good — 2 import contracts KEPT every round; bare install runs the spine yaml-free (reviews/05 #8) |
| Manual capture is first-class | The token-constrained operator is the primary user | ✓ Good — the deterministic manual path is the whole v1.1 composer; no AI touched it |
| Distill is a swappable socket (hand / OSS / AI) | Decouples the pipeline from any backend; enables no-AI mode | ✓ Good — socket + conformance suite hold; the untrusted-producer hardening is DEF-11's job |
| Format adapters first (PPT/Power BI/Excel/Email) | Deterministic, low-token; pulls structure already in the file | ✓ Good — v1.0; the read-anchored coverage identity ported cleanly to the YAML loader |
| Faithful, not suggestive | Editorializing breaks auditability; emphasis is the human's job | ⚠ Revisit — the faithfulness gate's Option-A structural fallback is the chain's weakest link and Hole A is composer-only (reviews/05 verdict); harden before an untrusted producer |
| Open-core: V2 Newsletters / V3 PulseIQ | Give away the trust framework, keep the learning engine | ✓ Good — the boundary held; V3/PulseIQ stayed out of scope |
| Design the surface first, then gather data | Decide what the artifact should look like, then go find the inputs | ✓ Good — the worked `module-a` example proved surface-first end-to-end |
| Learning/onboarding is a first-class surface | Teaching newcomers / training cohorts is a primary use, not an afterthought | ✓ Good — shipped v1.0 Phase 12; unchanged this milestone |
| Connection/relationship view — parked | "Make sense of how things connect" is real but deferred until after core V2 | — Deferred (still parked) |
| Low-token, generic extraction (not no-AI, not per-template) | Cheapest models + format consistency; manual is the floor | ✓ Good — generic extraction, no per-template code |
| Agents are interviewers (a distill modality) | Interview you / your work / your codebase to fill gaps faithfully | — Deferred (DEF-11 — not built this milestone) |
| Promotion chain Report → Article → Newsletter is the spine | Each human-gated; the real-world shape of the model's promotions | ⚠ Revisit — ontology drift: this is a **fan-out** (axis 2), not a promotion; "promotion" is reserved for `Claim→KPI`/`Report→Article` (reviews/08 D2) |
| Abstract everything: models in code, specifics in config (v1.1) | Different modules/teams organize differently; hardcoded lanes = a fixed tool. JJ's fundamental principle, 2026-07-02 | ✓ Good — the strongest result of the milestone: the abstraction guard fired 3× on real leaks and out-enforced the plan's own defaults |
| Report unit-of-work: swim-lane kind first; project/interview kinds deferred | Close one loop fully before widening; keep the section abstraction generic | ✓ Good — the kind-agnostic seam is proven by a second-kind ("risk register") test; other kinds slot in with zero composer change |
| Δ computed at compose time into `KpiItem.delta`; no Kpi start/baseline field | Model change deferred deliberately; composer derives, model stays untouched | ✓ Good — `models.py` byte-unchanged; Δ reproducible from two content-addressed endpoints (DEF-10 deferred cleanly) |

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
*Last updated: 2026-07-02 after completing milestone v1.1 (Swim-Lane Module Report) — full evolution review at close (deep-review loop Round 10)*
