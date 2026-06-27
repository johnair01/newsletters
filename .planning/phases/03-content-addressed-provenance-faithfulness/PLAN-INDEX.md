# Phase 3 — Plan Index (Content-Addressed Provenance & Faithfulness Gate)

**Goal:** Make traces resistant to source drift and make unfaithful claims structurally
unable to pass as audited — content-address every trace; enforce entailment at the socket
boundary for all backends.

**Requirements:** PROV-01 (content-addressed traces), PROV-02 (faithfulness/entailment gate).

**Decisions implemented:** D-1 (SHA-256 of full Source + char offsets + verbatim span),
D-2 (STALE = computed property), D-3 (normalized span-containment at the Phase-1 seam; route to
`missing[]`), D-4 (optional fields for backward-compat + migration helper; AI entailment out of
scope; stdlib-only).

## Plans & waves

| Plan | Wave | Depends on | Type | Tasks | Req | Files (exclusive ownership) |
|------|------|-----------|------|-------|-----|------------------------------|
| 03-01 | 1 | — | tdd | 3 | PROV-01 | `src/newsletters/semantic.py`, `tests/test_provenance.py` |
| 03-02 | 2 | 03-01 | tdd | 2 | PROV-01 | `src/newsletters/dogfood.py`, `tests/test_provenance_migration.py` |
| 03-03 | 2 | 03-01 | tdd | 3 | PROV-02 | `src/newsletters/distill/{faithfulness,ports,conformance,__init__}.py`, `tests/test_faithfulness_gate.py` |

- **Wave 1:** {03-01} — the data-model foundation (content-address + STALE in the spine).
- **Wave 2:** {03-02, 03-03} — run in PARALLEL (zero file overlap: `dogfood.py` vs `distill/`);
  both depend only on 03-01's `Trace.from_source` / verbatim-span pinning.

## Task → success-criterion / requirement mapping

ROADMAP Phase 3 success criteria:
1. Trace content-addressed (hash+offset+verbatim span); source edits flip claims to STALE.
2. Faithfulness gate entails each claim by its trace span via deterministic span-containment (no-AI).
3. An unentailed claim is routed to `missing[]`, never surfaced as a fact.

| Plan / Task | Maps to |
|-------------|---------|
| 03-01 / T1 — Source.content_hash() + optional Trace hash/offset fields | Criterion 1 · PROV-01 · D-1, D-4 |
| 03-01 / T2 — self-verifying `Trace.from_source` (pins hash+offsets+verbatim span) | Criterion 1 · PROV-01 · D-1 |
| 03-01 / T3 — STALE computed property (trace/claim/distillation) | Criterion 1 (STALE half) · PROV-01 · D-2 |
| 03-02 / T1 — migration helper content-addresses a sample source's traces | Criterion 1 (corpus) · PROV-01 · D-4 |
| 03-02 / T2 — apply migration in dogfood build; corpus addressed + not stale | Criterion 1 (corpus) · PROV-01 · D-4 |
| 03-03 / T1 — `SpanContainmentFaithfulness` (normalized, stdlib-only) | Criterion 2 · PROV-02 · D-3, D-4 |
| 03-03 / T2 — default the seam (`_enforce`/`assert_conforms`) to span-containment | Criterion 2 · PROV-02 · D-3 (all backends inherit) |
| 03-03 / T3 — `route_unfaithful_to_missing` (relocate, never edit) | Criterion 3 · PROV-02 · D-3, faithful-not-suggestive |

## Dependency notes

- The injectable faithfulness seam already exists from Phase 1: `_enforce(result, check)` in
  `src/newsletters/distill/ports.py` takes a `FaithfulnessCheck` (`entails(claim) -> bool`).
  Plan 03 swaps the Phase-1 `StructuralFaithfulness` default for `SpanContainmentFaithfulness`
  WITHOUT touching any backend (D-3) and WITHOUT changing the `_enforce`/`assert_conforms`
  signatures — the seam stays injectable (existing seam tests stay green).
- Plan 03 depends on Plan 01 because span-containment checks the **verbatim span** that
  `Trace.from_source` pins (Wave 1 → Wave 2).
- Plan 02 depends on Plan 01 because the migration helper mints traces via `Trace.from_source`.
- Plans 02 and 03 have disjoint file ownership → safe to execute in parallel within Wave 2.

## Checkpoints

None. `human_verify_mode: end-of-phase` (no in-plan `checkpoint:human-verify`), every task is
`tdd`/`auto`, and there are no package installs (stdlib `hashlib` + string ops only) — so no
Package Legitimacy checkpoint is required. Standing invariants the executor must keep green every
plan: full `pytest`, `mypy src/newsletters/distill`, `lint-imports` (AI-optional contract), and the
bare-install AI-free property.

## Standing-invariant guard (every plan, every task)

Stdlib-only (`hashlib`, `str.casefold`, `str.split`, `str.find`) — ZERO AI. The plans add NO new
dependency. If an executor finds it needs one, STOP and flag a Package Legitimacy checkpoint; do
not assume.
