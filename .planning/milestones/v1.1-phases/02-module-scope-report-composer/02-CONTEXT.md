# Phase 2: Module-scope Report composer - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Source:** Stage-A milestone seed + v1.1 research reconciliation + Phase-1 as-built reality
(discuss skipped — decisions LOCKED, approved by JJ at milestone start)

<domain>
## Phase Boundary

Given the traced bindings Phase 1 produces, compose **one `Surface(REPORT, Draft)` per module**:
per-lane `KpiStripBlock` (Δ computed at compose time) + `ClaimsBlock`, honest `missing[]` routing,
stable `R-NNN`, owner quote slot, fanout stub. The composer SELECTS/ORDERS/LINKS traced material
only — it authors no facts. No rendering into `content/`, no worked `module-a` (Phase 3).
Requirements: COMP-01..04.

</domain>

<decisions>
## Implementation Decisions (LOCKED)

### Module shape
- New top-level `src/newsletters/compose.py` — pure in-memory assembly, no disk I/O beyond what
  the loader already did; consumes `swimlane.SwimlaneLoad`/`SectionBinding`. AI-free, stdlib+
  pydantic (+ existing package modules) only. No yaml import (compose is loader-agnostic).
- Kind-agnostic seam: the composer consumes `SectionBinding[]` without knowing lanes exist —
  prove with a seam test composing a second, non-lane binding kind with zero composer change.
- Phase 1's `swimlane.py` MAY be extended **additively** if endpoint-pairing needs it (e.g. a
  field carrying each KPI's traced period-endpoint claims), under two hard conditions: every
  existing Phase-1 test stays byte-untouched AND green; the abstraction guard still passes.
  Read the LIVE `swimlane.py` first — prefer deriving endpoints from what it already emits.

### The Δ contract (research reconciliation #2 — the combined contract)
- One pure function `compute_delta(start, close)` — deterministic, reproducible by test
  (recompute every rendered delta; assert byte-equality).
- Δ lives ONLY in `KpiItem.delta` (+ `dir`); it is a *derivation over two independently traced
  endpoints*, never itself a Claim, never traced, never rendered as a claim.
- Either endpoint absent → `delta=None`, `dir=None`, a `missing[]` note — NEVER a fabricated 0.
  Δ==0 is a distinct, honest "no change" (dir=None, delta rendered as the computed zero form).
- NO `Kpi` start/baseline model change (DEF-10).

### Trust guards this phase lands (closes research Holes A+B at the composer)
- Zero-trace-claim test: composer emitting ANY claim with zero traces → test fails.
- All-content-addressed test: ANY emitted trace with `is_addressed == False` → test fails.
- Numeral-free-prose guard: any non-ClaimsBlock text block (prose/rationale) carrying a digit
  run not drawn verbatim from a traced claim's text → test fails. The composer's own prose slot
  is connective tissue ONLY (headings/transitions, no facts, no numerals).
- `faithfulness.py` / `coverage.py` / `semantic.py` / existing gates UNTOUCHED.
- No-auto-publish proven ON THE COMPOSED SURFACE: publish() without satisfied policy raises;
  composed review state is Draft; adversarial bypass attempt (direct state assignment is
  possible on Review — prove the gate the model actually enforces: publish path raises).

### Identity & structure
- `R-NNN` via the existing `site.Ledger` against a NEW `content/module/ids.json` (own ledger,
  research reconciliation #3; first entry R-001). Ledger file created by compose-time helper;
  append-only semantics preserved (reuse site.py API — do not fork it).
- Surface template = `templates.REPORT` (slots hero/kpi/prose/claims/quote/fanout).
- Deterministic output: `Surface.created` must NOT default to now() — pass the deterministic
  timestamp (EPOCH_ZERO helper or the Source's timestamp). Same input → byte-identical
  `model_dump_json` across two composes (test).
- Lane order = config order (SectionBinding order in). Per lane: KpiStripBlock(heading=lane
  heading) then ClaimsBlock(lane claims). Module-level missing[] = union of lane missing +
  compose-found gaps.
- Quote slot: sourced-or-omit — if the config carried a traced owner/manager quote claim, render
  a QuoteBlock from it (attr = owner id); if absent, OMIT the block and add a missing[] note.
  Never fabricate a quote. Unowned lane → attribution "unassigned"-style honesty, no quote.
- Fanout stub: FanoutBlock with declared kinds (article/newsletter/learning) and href=None.
- Edge cases (FEATURES research contract): zero-KPI lane → KpiStripBlock omitted or empty +
  disclosed; empty lane set → still a valid Draft Surface with populated missing[]; never None.
- `Surface.traces` carries the loader's Source(s) so claim-beside-trace rendering works in
  Phase 3 (mirror how dogfood/worksurface populate `traces`).

### Claude's Discretion
- compose.py public API shape (e.g. `compose_module_report(load: SwimlaneLoad, *, ledger_path)`).
- Exact missing[] message wording; delta string format (signed, unit-preserving; keep simple).
- Where the ledger-helper lives (compose.py vs reuse of site.py helpers) — do not fork site.py.
- Whether quote/owner metadata flows via SectionBinding extension or a parallel structure —
  additive-only rule above applies.

</decisions>

<canonical_refs>
## Canonical References

### Live code (read before planning/implementing)
- `src/newsletters/swimlane.py` — AS-BUILT Phase 1 (SectionBinding, SwimlaneLoad, _R_* codes)
- `src/newsletters/semantic.py` — Surface/Review/blocks; `Review._published_requires_satisfied_policy`; `open_pull_request` untraced-claim refusal
- `src/newsletters/templates.py` — REPORT preset
- `src/newsletters/site.py` — Ledger/ref_for (the R-NNN authority)
- `src/newsletters/worksurface.py` — build_work_report: the closest composed-surface precedent (incl. how it populates traces/lineage/ledger)
- `src/newsletters/capture.py` — build_report precedent
- `src/newsletters/adapters/_timestamps.py` — EPOCH_ZERO
- `.planning/phases/01-swim-lane-binding-traced-yaml-loader/01-PATTERNS.md` + 01-0*-SUMMARY.md — Phase-1 as-built notes

### Research
- `.planning/research/SUMMARY.md` (reconciliations 2/3/4), `PITFALLS.md` (Phase-2 owns: delta
  reproducibility, numeral-free prose, Hole A/B closure, Surface.created determinism, ledger
  collision, gate-weakening temptations), `FEATURES.md` (edge-case contract table)

### Rules
- `CLAUDE.md` hard rules; `RETRO.md` (enforce invariants in code + adversarial test)

</canonical_refs>

<specifics>
## Specific Ideas

- Milestone gate policy as Phase 1 (enforced set green; advisory = no new failures; isort
  convention = `--profile black`).
- One task = one atomic commit; push every task.
- This is the phase most exposed to "go green" gate-weakening (PITFALLS #11) — the forbidden
  list is absolute: no edits to conftest/existing tests/importlinter/ci.yml/faithfulness/
  coverage/semantic/templates/models/render/site (site.py READ-ONLY reuse).

</specifics>

<deferred>
## Deferred Ideas

- Rendering/`content/` output, Library visibility, `--corpus module` CLI — Phase 3.
- Owner-audit review routing (DEF-04); project/interview binding producers (DEF-02/03).

</deferred>

---

*Phase: 02-module-scope-report-composer*
*Context gathered: 2026-07-02 from the approved Stage-A seed + research + Phase-1 as-built*
