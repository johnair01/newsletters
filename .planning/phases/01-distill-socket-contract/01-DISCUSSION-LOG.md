# Phase 1: Distill Socket Contract - Discussion Log

**Date:** 2026-06-14 · Human reference only (not consumed by downstream agents).

## How the discussion went

Started with builder-level forks (input types, registries). User corrected: ask
*vision-level* questions; the code plumbing is the builder's. Reseeded four readable forks —
authoring-by-hand feel, how gaps are shown, how little it asks to start, seeing evidence as
you write — and the user selected all four.

Mid-discussion the user delivered the decisive reframe:

- **Not "no AI" — "low token."** AI is in the loop at work but tightly budgeted (cheapest
  models, minimal reasoning). Manual is the floor, not the default.
- **Generic, not template-specific.** (MBPS reports are PowerPoints; a bespoke 8D parser
  would be wrong.) The generic adapter roadmap stands.
- **The engine, in their own words:** Sources (emails, chats, M365 transcripts/summaries,
  SQL, PowerPoints, code, **live interviews**) → robots gather faithfully + cheaply →
  **Report** (reviewed) → promote → **Article** (peer-reviewed) → promote → **Newsletter**
  (audience-cut). **Agents are interviewers** — of you, your work, your codebase.
- **Five worked contexts:** work quality-event investigations; work weeklies by swim lane;
  interns; PulseIQ; Newsletters itself.

User confirmed: "we are aligned."

## Decisions captured → see `01-CONTEXT.md`

D-01 three modalities (hand / generic low-token extraction / agentic interview) → one
`Distillation`; D-02 Phase 1 = contract + registry + manual backend; D-03 low-token is
first-class; D-04 JSON-serializable output; D-05 two gap kinds (unreadable vs unprovable);
D-06 evidence shown next to claims at draft time.

## Deferred
Swim-lane/KPI unit; templates-as-scaffold learning; interview-agent tooling; the five
deployment contexts (corpora/config, not Phase-1 code).
