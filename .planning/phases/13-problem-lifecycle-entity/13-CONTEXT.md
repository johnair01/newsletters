# Phase 13 — Context & Decisions (Problem Lifecycle Entity) — THE FINAL PHASE (this UAT cut)

**Goal:** Add a first-class `Problem` entity *above* `Source` that makes the scattered
`problem → owned → solution → verified` lifecycle a legible, queryable home — **a legibility layer,
NOT a second tracker.** Problem-SOLVING stays external/operator-owned; Signals models the *record* of
the lifecycle, never executes it.

**Requirements:** PROB-01 (the entity + ladder, distinct from the review gate + fan-out), PROB-03
(hard constraint: legibility-only — no write-back to Jira/ADO; human-gated transitions; spine boundary
preserved + proven by test). **PROB-02 (queryable portfolio) and PROB-04 (board surface) are Phase 14
— OUT of scope for this phase / this UAT cut.**
**Depends on:** the typed spine (`semantic.py` Source/Trace), the A2 decision note, the terminology guard.

## The terminology guard (resolved FIRST, per the seed) — three distinct state axes
1. **Surface review gate** — `Draft → In Review → Published` (verbs: review / publish). The publish
   trust gate in `semantic.py`. Do NOT overload.
2. **Surface fan-out chain** — one reviewed record → report/article/newsletter/episode/learning (verbs:
   fan-out / derive). NOT "promotion" (already renamed). [Note: `promote_claim_to_kpi`/
   `promote_report_to_article` are the EXISTING within-truth promotions — a 4th, narrower grammar;
   the Problem ladder must avoid "promote" too.]
3. **Problem lifecycle ladder (NEW)** — `Identified → Owned → In Progress → Resolved → Verified`.
   **Reserved verb: `transition`** (e.g. `Problem.transition(to, by, ...)`). Axis-3 must NOT use
   promote / publish / advance / fan-out / derive. No enum member, field, or label shared across axes.

## Decisions (design — research to validate against the spine)
1. **A new typed module `src/newsletters/problem.py`** (Pydantic, AI-free, imports `semantic.Source`/
   `Trace` only — keep the leaf/acyclic boundary; NOT in semantic.py to keep the spine focused; NEVER
   imports distill-AI/network). `Problem` is a first-class entity ABOVE Source.
2. **`ProblemState` enum** = IDENTIFIED → OWNED → IN_PROGRESS → RESOLVED → VERIFIED — a DISTINCT type
   from `ReviewState` (the review gate). A test proves the two enums share no member values and are
   different types (terminology-guard enforcement).
3. **`Problem` aggregates ≥1 traced `Source`** — it carries references/Traces to its constituent
   Sources (scattered ticket / passdown / RCA), so every Problem stays traceable to evidence
   (PROB-04's "links back to constituent Source records" is prepared here; rendering is Phase 14).
   A Problem with zero sources is invalid (≥1 required).
4. **Human-gated `transition(to, by, note=...)`** — records each lifecycle transition (from→to, actor,
   timestamp/note) on the Problem; refuses an invalid ladder jump or a transition with no actor; NEVER
   auto-mutates (no code path advances a Problem's state without an explicit human actor). The
   transition log is the legible record. Distinct from the review gate's publish/review API.
5. **NO write-back / spine boundary (PROB-03, the hard constraint — like no-auto-publish):** `problem.py`
   has ZERO external-system/network imports; there is NO method that writes to Jira/ADO or mutates any
   external state. Solving is external; Signals only models the record. PROVEN BY TEST: (a) no
   network/external import reachable from `problem.py` (lint-imports / a no-AI-style guard), (b) the
   Problem API exposes no write-back/export-to-tracker path, (c) the `semantic.py` spine is unchanged
   (Problem sits above it; it does not alter Source/Distillation/Surface or the review gate).
6. **Scope:** the typed Problem entity + ProblemState ladder + human-gated transition + the boundary +
   the terminology-distinctness + no-write-back tests. A small dogfood Problem example (aggregating ≥1
   real Source) is OK to prove it end-to-end, but the queryable portfolio (PROB-02) + the board surface
   (PROB-04) are **Phase 14** — do NOT build rendering/aggregation here. No AI; no new dependency.

## Research-locked choices (13-RESEARCH.md accepted 2026-06-18, HIGH confidence)

- **L1 — `src/newsletters/problem.py`** mirrors `promote.py` (imports `semantic` only) + `locators.py`
  leaf style; acyclic confirmed (`semantic.py` imports only `.locators`/`.templates`, never `problem`);
  AI-free. Export `Problem`/`ProblemState` from `__init__.py` (recommended yes).
- **L2 — `Problem`** (Pydantic): `id`, `title`, `state: ProblemState = IDENTIFIED`,
  `evidence: list[Trace]` (reuse the existing evidence-pointer type — gives content-addressing for free;
  validated **≥1**), `log: list[TransitionEvent]`, `opened`. Plus a `source_ids` property
  (single-entity traceability; the cross-problem query is Phase 14).
- **L3 — `ProblemState`** = StrEnum `IDENTIFIED → OWNED → IN_PROGRESS → RESOLVED → VERIFIED`.
- **L4 — `transition(to, by, note="")`** — the SOLE mutator: appends a `TransitionEvent(from,to,by,
  note,at)` + sets state; RAISES on empty `by` (human-gated) and on an illegal move; NEVER auto-advances.
  Ladder rule = **sequential forward + explicit RE-OPEN** (`Resolved → In Progress`, `Verified → In
  Progress`) — A1 resolved: a legible record of the REAL lifecycle must allow reopening a bottleneck;
  re-open is still a recorded human transition.
- **L5 — No-write-back proof (PROB-03, three sub-proofs):** (a) a NEW `.importlinter` contract
  `forbid-external-write-in-problem` (forbids socket/http/urllib/ftplib/smtplib/subprocess/requests from
  `problem`), covered by the existing `lint-imports` test, PLUS a runtime `sys.modules` subprocess check
  (mirrors test_ai_optional.py:143-158); (b) API allow-list test — `Problem`'s public surface has NO
  export/push/sync/write/jira/ado method, `transition` is the only mutator; (c) spine unchanged —
  `Source.content_hash()` byte-identical before/after a full transition sequence, and `semantic.py`
  never imports `problem`. NOTE: adding a 2nd import-linter contract → `lint-imports` becomes "2 kept,
  0 broken"; update any test asserting "1 kept".
- **L6 — Terminology-distinctness test:** `ProblemState` is a DISTINCT type from `ReviewState` with NO
  shared member VALUES (explicitly incl. `IN_PROGRESS="in_progress"` vs `IN_REVIEW="in_review"`); the
  verb `transition` collides with no review-gate/fan-out/`promote` verb.
- **L7 — Dogfood:** ONE real `Problem` aggregating the real `session-rev1` Source + a couple of
  human-gated transitions — proves the entity end-to-end. NO rendering.
- **L8 — Scope:** Phase 13 = entity + ladder + boundary + tests + 1 dogfood Problem. OUT (Phase 14):
  any `list[Problem]` query/aggregation, portfolio container, grouping taxonomy, and ANY `render.py`/
  `site.py`/`templates.py` touch. Zero new dependency; no AI; no external calls.

## Hard rules in play
- **Legibility layer, not a tracker (PROB-03)** — NO write-back to external systems; solving stays
  external; the `semantic.py` spine boundary is preserved. Proven by test.
- **Human-gated, never auto-mutated** — like no-auto-publish: a Problem's state only changes via an
  explicit human `transition`. No automatic advancement.
- **Three axes stay distinct (terminology guard)** — the Problem ladder shares no term/type with the
  review gate or the fan-out; reserved verb `transition`.
- **Typed everything / AI-optional** — `problem.py` stdlib + Pydantic + `semantic` only; `lint-imports`
  + bare-install stay green; acyclic imports.
- **Every problem traces to evidence** — a Problem aggregates ≥1 traced Source (≥1 required).

## Research note (dispatch BEFORE planning)
Validate against the LIVE codebase: where `Problem` fits relative to `Source`/`semantic.py` (new module,
acyclic, AI-free); the exact `ProblemState` ladder + the human-gated `transition` API (recording
from→to/actor, refusing invalid jumps/no-actor/auto-mutation); how to PROVE the no-write-back / spine-
boundary constraint by test (no network/external import; no write path; semantic.py unchanged); the
terminology-distinctness test (ProblemState ≠ ReviewState, no shared verb); a minimal dogfood Problem
aggregating ≥1 real Source; and confirm PROB-02/04 (portfolio + board) are correctly deferred to Phase
14. Confirm zero new dependency + no external calls + no AI. Record in 13-RESEARCH.md.
