---
title: "A2 — Problem Lifecycle Layer: routed decision"
date: 2026-06-17
context: "/gsd-explore design pass — the A1-vs-A2 lifecycle decision for Signals"
status: decided
---

# A2 — Problem Lifecycle Layer (routed decision)

## The question

Model A is locked: Signals is a **surface of the Engineering OS** — a legibility membrane, not a
standalone media platform. The Rev2 12-phase roadmap already implements **A1**: `Source → Claim(+Trace)
→ Distillation → Surface`, the review gate, the gate-state board (Phase 9), agentic-interview capture
(Phase 1), real-content install (Phase 11), learning surface (Phase 12).

The user's `problem → owned → solution → promoted` lifecycle is **scattered** across Jira/Azure DevOps,
passdowns, and people's heads — no single coherent home, but not nothing. So:

- **A1** — stay a pure capture→trust→publish membrane. Each scattered ticket/passdown/RCA is captured
  as a traced `Source` and surfaced on the existing gate-state board; lifecycle state lives in the
  external tools.
- **A2** — add a NET-NEW first-class Problem/Solution lifecycle entity *above* `Source`, plus a problem
  board surface. Signals becomes where the scattered lifecycle is consolidated into legible, queryable
  state.

## The hinge (why the decision came down to one test)

The whole fork collapses to one job-to-be-done: **does anyone need to query or aggregate *across*
problems?**

- A1 can tell *each* problem's story beautifully and move it through review one at a time.
- A1 **structurally cannot** answer "every open bottleneck across the intern groups" or "which
  problem-type recurs this quarter" — *you cannot aggregate over state you do not model.* A1 models
  surfaces, not problem state.

The user confirmed the **portfolio view has a real consumer** (watching bottlenecks across modules;
the leadership pattern view). That is the A2 justification.

## Decision

**A2 — scoped as a *legibility layer*, not an execution tracker.**

A2's failure mode is the one CLAUDE.md already warns against: becoming a second Jira. The scoping that
keeps it honest:

> Signals models the problem **lifecycle** as legible, queryable, aggregatable state — it does **not**
> execute the work. The problem-SOLVING step stays external/operator-owned (the `semantic.py:22-24`
> boundary holds). Scattered tickets/passdowns/RCAs are captured as traced `Source`s; the new
> `Problem` entity sits *above* them as the consolidation + narration layer. **No write-back** to
> Jira/ADO — Signals is the system of *record-legibility*, not the system of *execution*.

This resolves the central tension — "don't build a second tracker" vs. "the scatter IS the problem
the product exists to solve": we consolidate the *record* into one legible home; we do not relocate
the *work*.

## How it slots into the roadmap

A clean extension after Phase 12 — not a rewrite. The spine, gate, and Source capture (Phases 1, 3,
9, 11) are exactly the substrate it builds on:

- **Phase 13 — Problem Lifecycle Entity**: a first-class `Problem` above `Source` (aggregates ≥1 traced
  `Source`; lifecycle ladder `Identified → Owned → In Progress → Resolved → Verified`), human-gated,
  no external write-back, spine boundary proven by test. (PROB-01, PROB-03)
- **Phase 14 — Problem Board Portfolio Surface**: queryable portfolio view (group/count/age by
  node/area, recurrence), every problem traced to its sources, rendered alongside the gate-state
  board. (PROB-02, PROB-04)

## Three distinct axes — do not collide them

A2 introduces a third state axis. All three must stay distinct in code and UI:

1. **Surface review gate** — `Draft → In Review → Published` (the publish trust gate).
2. **Surface fan-out chain** — one reviewed record → audience-tuned surfaces (report/article/episode/…).
3. **Problem lifecycle ladder** — `Identified → Owned → In Progress → Resolved → Verified` (NEW).

The word **"promotion"** is the collision risk (surface fan-out vs. tooling-graduation ladder).
Reserve one word per axis; lock the naming before Phase 13 code. See
`.planning/seeds/promotion-terminology-guard.md`.

## Truths checked (still honest)

- **No second tracker / lazy-by-design** — honored: legibility layer, no write-back, solving stays
  external.
- **Spine boundary (`semantic.py:22-24`)** — preserved: Signals models capture→trust→publish + now
  the *legibility of* the lifecycle; never its execution.
- **Every published claim traces to evidence** — extended: every `Problem` traces to its `Source`s.
