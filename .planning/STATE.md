---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: milestone
status: executing
stopped_at: "Completed 02-01-PLAN.md (renderer foundation: normalizer promoted, guards, deck builders); next: 02-02-PLAN.md (the writer)"
last_updated: "2026-08-29T05:15:00.000Z"
last_activity: 2026-08-29 — Phase 2 plan 02-01 executed (renderer foundation)
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 6
  completed_plans: 4
  percent: 67
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-29)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Phase 2 — Renderer (WKLY-01)

## Current Position

Phase: Phase 2: Renderer (WKLY-01) — executing (3 plans)
Plan: 02-01 complete (1/3); next 02-02 (the writer), then 02-03 (proof + CI job)
Status: Ready to execute 02-02
Last activity: 2026-08-29 — Phase 2 plan 02-01 executed (renderer foundation)

## Performance Metrics

**Velocity:**

- v1.3: 3 plans complete (roadmap defined 2026-08-29; 4 phases). Phase 1 executed in 3 waves, ~48min total.
- v1.2: 2 plans across 2 phases (closed 2026-08-29, archived).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Specify + de-risk | 3/3 | Plans complete — awaiting phase verification |
| 2. Renderer (WKLY-01) | 1/3 | Executing — 02-01 (foundation) complete |
| 3. Weekly compose (WKLY-02/03/04) | 0/0 (unplanned) | Not started |
| 4. Sample corpus + recipe (WKLY-05/06) | 0/0 (unplanned) | Not started |

**Per-plan execution:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 1 P01 | 12min | 3 tasks | 6 files |
| Phase 1 P02 | 14min | 2 tasks | 3 files |
| Phase 1 P03 | 22min | 3 tasks | 5 files |
| Phase 2 P01 | 12min | 3 tasks | 8 files |

**Recent Trend:**

- v1.3 opened from a committed seed (`.planning/seeds/v1.3-weekly-one-shot.md`) whose
  current-state claims were verified against the live repo first. Fully autonomous run
  authorized by the EiC (2026-08-29): no between-phase human stop; the human gate is the
  final PR. The ONE discussion round is done — new questions are decided per the recorded
  recommendations and logged.

- Roadmap mirrors the seed's approved 4-phase table; phase numbering resets to 1–4 (prior
  phase dirs archived under `.planning/milestones/`, `.planning/phases/` empty — no collision).

- Plan 01-01 landed the `.pptx` determinism spike as a durable test rather than scratch code:
  the measurement is committed evidence, re-verifiable by `--check`, and the determinism
  assertion carries a negative control so it can actually fail. Zero production surface touched.

- Plan 01-02 turned that measurement into the recorded decision (one outcome, one scope, one
  normalizer contract) and closed the two places where the repo said something different — the
  ADAPT-06 golden-fixture docstring's byte-stability claim was measurably false and is corrected
  and superseded in writing, not silently contradicted.

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Decisions taken at v1.3 open
(Editor-in-Chief, structured question round, 2026-08-29 — the ONE round; recorded also in
WHERE-WE-ARE.md):

- [Milestone]: Weekly deck reuses `Surface(REPORT)` — the PPTX renderer is an output format, not a new semantic kind.
- [Milestone]: Asset provenance minimum = folder + date + event label; deep link optional EXCEPT a BI screenshot standing in for values (WKLY-04), where it is required. No provenance → `missing[]`, never placed silently.
- [Milestone]: Template contract = named placeholders; missing/unknown names fail loud. The renderer never invents layout.
- [Milestone]: v1.2 formally closed on live evidence (EiC pages review 2026-08-29).
- [Run]: Fully autonomous through all v1.3 phases; the human gate is the final PR. Branch: `claude/new-session-gw8tik` serves the seed's `gsd/v1.3-*` integration-branch role (harness-designated; v1.1 precedent). Never touch `main`.
- [Run]: Milestone-level ecosystem research skipped — the seed encodes it and phase-level research + the Phase 1 determinism spike cover the real unknowns (logged per the no-more-questions contract).
- [Roadmap, 2026-08-29]: Phase 1 carries no WKLY requirement — it de-risks WKLY-01/02 and ships spec + a recorded determinism decision with evidence. WKLY-01→P2, WKLY-02/03/04→P3, WKLY-05/06→P4.
- [Phase 1-01]: Determinism outcome recorded as BYTE-STABLE via a declared post-save OPC-zip normalization (not the content-stable fallback), measured on a real 3s-separated python-pptx 1.0.2 double write — raw_bytes_equal=false with varying_parts=[] and varying_zip_fields=[date_time]; normalized_bytes_equal=true. Evidence committed at .planning/notes/2026-08-29-pptx-determinism-evidence.json and re-verifiable via --check.
- [Phase 1-01]: Byte-identity is scoped in writing to a fixed (python-pptx, zlib) pair; part_digest (sorted name+sha256 of each unzipped part) is the implementation-independent assertion a committed==fresh gate must use — DEFLATE output is zlib-implementation-dependent (zlib vs zlib-ng); a full-file hash across environments would be green locally and red in CI with identical part content.
- [Phase 01-specify-de-risk]: Determinism recorded as BYTE-STABLE via a declared post-save OPC-zip normalization, scoped in writing to a fixed (python-pptx, zlib) pair; the committed==fresh gate asserts the implementation-independent part_digest, never a full-file hash
- [Phase 01-specify-de-risk]: Generated-by marker lives in OPC core properties (cp:category / cp:contentStatus / dcterms EPOCH_ZERO / cp:identifier), not a notes slide — zero new parts, asserted by reopening the WRITTEN file
- [Phase 01-specify-de-risk]: Template contract: fill existing template slides (add_slide regenerates placeholder names); NL_ reserved prefix; the name-to-shape map raises on duplicate names; bind over slide.shapes
- [Phase 01-specify-de-risk]: ONE normalizer contract: _determinism.normalize_opc_zip is canonical and _author_fixtures._normalize_zip delegates to it in Phase 2, not in a spec phase that would rebuild the golden corpus
- [Phase 1]: The Weekly Spec's home is a new docs/weekly-spec.md — a sibling document AND a sibling loader — The casespec mechanism is reused verbatim (safe_load only, normalized file text as evidence, Trace.from_source spans, root containment, config bound but never claimed); the key set stays separate, because widening casespec's exactly-eight-key validator would make each format silently accept the other's fields (Q1)
- [Phase 1]: AssetBlock.asset is REQUIRED — a provenance-less asset placement is unrepresentable, not merely policed — The type carries the invariant instead of a check somebody can forget to call, the same move GlossaryTerm.definition: Claim already makes in this codebase (D-02, threat T-01-18)
- [Phase 2-01]: The OPC normalizer is promoted VERBATIM to `src/newsletters/pptx_writer.py` (no leading underscore — it carries the phase's public entry point) and `tests/fixtures/weekly/_determinism.py` is DELETED. Exactly one `normalize_opc_zip` is reachable from the writer path; git records the move as a rename so a reviewer can diff it and see nothing was tidied. Module level is stdlib-only, so it imports on a bare install; the writer half reaches python-pptx lazily via the existing `adapters._pptx_loader._load_pptx()` boundary.
- [Phase 2-01]: The writer's public API will be `render_surface_pptx_bytes` / `render_surface_pptx`, NOT `render_weekly_deck`, and it takes an explicit `slots` mapping — the Surface→slots derivation is Phase 3's, because only the composer knows which authored block belongs in which Selection-Pane name (P-02/P-03).
- [Phase 2-01]: IN-04 REJECTED and IN-02's second half satisfied the other way CONTEXT permits. `_author_template._FIXED` stays `2026-01-01` as a *falsifiability control* (consolidating onto EPOCH_ZERO would make 02-02's marker read-back pass on a deck the writer never touched); `_author_fixtures._normalize_zip` is not delegated this phase — the weekly copy is SUPERSEDED instead, and the ADAPT-06 delegation is carried to Phase 4 with its cost (it would force all nine golden binaries to be regenerated) (P-05/P-08).
- [Phase 2-01]: The committed `tests/fixtures/weekly/template.pptx` is NOT regenerated by Phase 2 — its `part_digest_a`/`part_digest_b` are the committed determinism evidence and sit in the recorder's CHECKED_FIELDS. The realistic and pathological decks are authored in-test into `tmp_path` (P-06).
- [Phase 2-01]: The `[pptx]` extra carries a FLOOR pin `python-pptx>=1.0.2` — the exercised version, scoping the determinism claim — not a ceiling; `test_pptx_extra_declared` passes unmodified because `_req_name` strips specifiers (W19 closed by execution, not by reading the test).
- [Phase 1]: An asset path that escapes the project root RAISES; it is never routed to missing[] — missing[] is for content that is absent, never for a request the loader will not serve. Collapsing the two would let a future implementer 'disclose' a path traversal (T-01-16)

### Pending Todos

None. (B1–B20 fix-batch backlog remains parked in `reviews/2026-07-02-deep-review/07-tests-as-promises.md`, maintainer-gated.)

### Blockers/Concerns

- [v1.3 Phase 1 — RETIRED 2026-08-29]: The `.pptx` byte-stability risk is closed. Measured on a real 3s-separated double write (`.planning/notes/2026-08-29-pptx-determinism-evidence.json`) and recorded as BYTE-STABLE via a declared post-save OPC-zip normalization, scoped to a fixed (python-pptx, zlib) pair; re-proved every run by `tests/test_pptx_determinism.py` (negative control included).
- [v1.3 Phase 2 — OPEN]: No CI job installs `[pptx]`, so every pptx test module — including
  `tests/test_pptx_writer.py`, added by 02-01 — is `s`-skipped in CI today (02-RESEARCH Pitfall 7 /
  W21). Until plan 02-03 adds the job, Phase 2's green is a LOCAL green. Stated, not assumed.
- [v1.3 Phase 2 — OPEN]: "A normalized deck opens correctly in real PowerPoint" is still unproven
  here (no `.pptx` consumer in this environment). It is the recorded `checkpoint:human-verify` for
  the PR review, owned by plan 02-03 — not a phase gap.
- [v1.3 Phase 3]: `render.py`'s block dispatch ends in a bare `return ""`. It is UNREACHABLE today (all eleven union members have a branch), but adding four kinds without four branches makes it reachable and silent. The contract is now written in `docs/weekly-spec.md` §The four block kinds: Phase 3 adds four branches AND converts the fall-through into a teaching `raise` naming `block.kind`.
- [Carried]: `v1.1`/`v1.2` tags exist locally only — the environment's git proxy drops tag pushes; maintainer creates them via the Releases UI.
- [Carried]: ledgers (`content/*/ids.json`) are append-only — any diff on regenerate is a stop-the-line bug.

## Deferred Items

Carried from v1.1 (full list in `.planning/milestones/v1.1-ROADMAP.md`): DEF-01..12.
New at v1.2 open: DEF-13 (wire `web/` to real data), DEF-14 (adopt the environment deploy
channel iff maintainer aligns repo settings). Plus the B1–B20 fix-batch (maintainer-gated) and,
new at v1.3 open, the ADAPT-05 value-side extension (values come via export this milestone).

New at v1.3 Phase 2 (2026-08-29): **DEF-15 — give `isort` a `profile = "black"` and reformat once.**
The repo declares `isort` in `[dev]` with no profile, so isort and black disagree on every
parenthesized multi-line import; several committed files already fail `isort --check-only` and one
fails `black --check`. Until it is fixed, every plan that adds an import pays a "is this failure
mine?" tax. Maintainer-gated because the fix is a repo-wide reformat.

## Session Continuity

Last session: 2026-08-29 — Phase 2 plan 02-01 executed (the renderer's foundation, no rendering
yet). The Phase 1 spike's OPC normalizer moved VERBATIM into `src/newsletters/pptx_writer.py`
(git recorded a rename) and `tests/fixtures/weekly/_determinism.py` was deleted, leaving exactly one
normalizer in the writer path; all three `sys.path.insert` lines and the stale `__pycache__` went
with it (IN-03 closed at the mechanism). Two bare-install guards for the writer were added to
`tests/test_ai_optional.py` — deliberately NOT to `test_pptx_writer.py`, which skips itself without
the extra — and the `[pptx]` extra took a floor pin `python-pptx>=1.0.2`. `tests/test_pptx_writer.py`
landed with five in-test deck builders (group nesting, duplicate names, template-owned watermark,
non-text `NL_` slot, empty-run slot), `RICH_SLOTS`, and a self-test that re-proves W17 in-repo.
Full suite 571 passed / 64 skipped (baseline 567/64); `lint-imports` KEPT; the determinism evidence
`--check` exits 0 and ZERO committed binary changed. All five builders were smoke-verified
independently, not accepted on the tests' green.
Stopped at: Completed 02-01-PLAN.md; next: 02-02-PLAN.md (the writer itself)
Resume file: `.planning/phases/02-renderer/02-01-SUMMARY.md` + `02-02-PLAN.md` +
`.planning/notes/2026-08-29-pptx-determinism-decision.md` (binding input, not open questions)

Preceding session: 2026-08-29 — Phase 1 plan 01-03 executed: `docs/weekly-spec.md` written (281
lines — the eight-key annotated schema, the seven loader rules, the four block kinds field by
field, the asset-evidence record and its `missing[]` routing), `docs/architecture.md`'s
pre-existing `diagram`/`glossary` block-list drift fixed in the same edit that added the four new
kinds, the sibling pointer added to `docs/case-spec.md`, and the compass + RETRO brought current.
Phase 1 has no production surface: `git diff --exit-code -- src/newsletters/` exits 0.

Earlier: 2026-08-29 — plan 01-02 turned plan 01-01's committed measurement into
the recorded decision (`.planning/notes/2026-08-29-pptx-determinism-decision.md`, 340 lines) —
BYTE-STABLE via a declared post-save OPC-zip normalization, scoped to a fixed (python-pptx, zlib)
pair; the core-properties marker with its literal read-back assertion; the fill-existing-slides
template contract with the `NL_` prefix and the duplicate-name raise; D-01/D-02/D-03 each with a
testable consequence; Q1–Q5 closed. The two contradicting claims in
`tests/fixtures/pptx/_author_fixtures.py` were corrected and superseded in place (docstring only —
no golden binary regenerated). Full suite 565 passed, 64 skipped.
(That session stopped at 01-02-PLAN.md and resumed into 01-03; both are now closed.)
