---
title: "Terminology guard — lock the three state axes before Phase 13 code"
trigger_condition: "Phase 13 (Problem Lifecycle Entity) planning starts"
planted_date: 2026-06-17
---

# Terminology guard: three distinct state axes

A2 (the Problem Lifecycle Layer) introduces a **third** state axis to Signals. Before any Phase 13
code is written, lock the naming so the axes never collide in code, types, or UI copy.

## The three axes (must stay distinct)

1. **Surface review gate** — `Draft → In Review → Published`. The publish trust gate
   (`semantic.py`). The single most important invariant; do not overload its terms.
2. **Surface fan-out chain** — one reviewed record → audience-tuned surfaces
   (report / article / newsletter / episode / learning). A *fan-out*, not a *promotion*.
3. **Problem lifecycle ladder** *(NEW, A2)* — `Identified → Owned → In Progress → Resolved →
   Verified`. The real-world tooling-graduation lifecycle the product makes legible.

## The collision risk

The word **"promotion"** is ambiguous across axes 2 and 3 (surface fan-out chain vs. tooling
graduation ladder). It also risks bleeding into axis 1 ("promote to Published").

## The guard

- **Reserve one verb per axis.** Suggested: axis 1 = *advance / publish* (existing gate verbs);
  axis 2 = *fan out / derive*; axis 3 = *transition / advance the lifecycle*. Do **not** use
  "promote/promotion" for axis 2 — the roadmap already renamed it "fan-out" (SITE-05).
- Pick the axis-3 verb explicitly during Phase 13 discuss/plan and write it into the SPEC.
- No enum member, field name, or UI label may be shared across two axes.
- Add a test (or lint/naming check) asserting the lifecycle ladder type is distinct from the
  surface-gate type.

## Why this is a seed, not a todo

It is inert until Phase 13 planning begins — at which point it must be resolved *first*, before the
`Problem` entity is typed. See `.planning/notes/a2-problem-lifecycle-decision.md`.
