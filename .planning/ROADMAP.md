# Roadmap: Newsletters — Milestone v1.1 (Swim-Lane Module Report)

> **Fresh file for v1.1.** The v1.0 (Rev2) roadmap and its Phases 1–14 are **archived in git
> history** — the v1.0 phase directories are archived, so numbering **resets to Phase 1–4** for
> this milestone with no collision. The milestone seed, branch naming (`phase-01..04`), and the
> run plan (`/gsd autonomous --to 4`) all assume the 1–4 numbering used here.

**Milestone:** v1.1 Swim-Lane Module Report
**Defined:** 2026-07-02
**Granularity:** fine
**Phases:** 4 (locked by approved milestone scope — not to be added to or split)
**Coverage:** 12/12 v1.1 requirements mapped ✓

## Overview

The trust spine already ships (`Source → Claim(+Trace) → Distillation → Surface`, the review gate,
the renderer, the merge-block gate). This milestone bolts on the **missing composer**: the smallest
fully-real, config-driven machine that cuts one owned module across its swim lanes into a reviewed,
evidence-traced Report. The journey is strictly linear for the core: a traced YAML **loader** turns
per-module swim-lane config into content-addressed `Claim`/`KpiItem`s (Phase 1); a **composer**
arranges those traced inputs into a module-scope `Surface(REPORT, Draft)` with compose-time deltas
and honest `missing[]` routing (Phase 2); a **worked synthetic example** (`module-a`, fabricated
naming) proves the whole path end-to-end into the Library (Phase 3). A fourth, independent phase
makes the `ship` workflow's PR bodies read as faithful Signals dispatches (Phase 4). The overriding
principle — **ABSTRACT EVERYTHING** — is enforced from Phase 1: models in code, module/lane/owner
specifics in config, no fixture names in `src/`.

## Enforced gate set (definition of "green" for every phase)

A phase is green only when **all** of the following pass, re-run independently (agent "green" ≠ green):

1. **pytest** — full suite, including the new adversarial guard tests each phase lands
2. **lint-imports** — import-linter contracts (AI-optional core + no-external-write held)
3. **`newsletters check`** — the unforked merge-block gate, run over **all corpora** (`rev1`, `work`, and, from Phase 3, `module`)
4. **byte-stable double-render** — SITE-06 invariant holds over every rendered output
5. **bare-install CI** — `pip install .` runs the spine with zero YAML / zero AI reachable

`mypy` / `black` / `isort` are held to a **no-NEW-failures** standard versus the recorded
**2026-07-02 baseline** (the repo pre-dates a global format pass: ~59 files, 9 pre-existing mypy
errors). Cleanup of that debt is out of scope for this milestone.

> **Phase-1 circuit breaker:** If Phase 1 does not finish **cleanly green** on the enforced gate
> set above, the run **STOPS**. Everything downstream consumes the loader's traced output; an
> un-honest or non-deterministic loader must not be built upon.

## Phases

- [ ] **Phase 1: Swim-lane binding + traced YAML loader** - config → content-addressed traced `Claim`/`KpiItem`s, honest routing, abstraction guard (`swimlane.py`)
- [ ] **Phase 2: Module-scope Report composer** - traced bindings → `Surface(REPORT, Draft)`, compose-time Δ, faithfulness holes closed by new tests (`compose.py`)
- [ ] **Phase 3: Worked synthetic Module Report** - `module-a` config renders into the Library as a third `module` corpus with its own ledger
- [ ] **Phase 4: Signals-voice PR/summary** - `ship` workflow PR bodies read as evidence-first Signals dispatches

## Phase Details

### Phase 1: Swim-lane binding + traced YAML loader

**Goal**: An operator can declare a module's swim lanes in YAML, and a deterministic, lazy-loaded
loader binds each lane to its `FunctionalGroup`/`Kpi`s/`Objective`s as content-addressed traced
inputs — no `models.py` change, no fixture names in `src/`, zero silent drops.
**Depends on**: Nothing (first phase). **Gates the whole milestone — circuit breaker applies.**
**Requirements**: LANE-01, LANE-02, LANE-03, LANE-04
**Success Criteria** (what must be TRUE):

  1. Loading an arbitrary configured lane set produces one `SectionBinding` per lane bound to its `FunctionalGroup`+`Kpi`s/`Objective`s at the parsed-dict level, with zero changes to `models.py` (proven by test).
  2. Every value the loader reads becomes a `Claim`/`KpiItem` minted **only** via `Trace.from_source` against the raw file text (`Source.transcript == path.read_text()` verbatim), and `trace.is_addressed is True` for every one (adversarial test proves an un-addressed trace is caught, not silently passed — closes Hole B upstream).
  3. The read-anchored coverage identity holds: every scalar **read** is either content-addressed or routed to `unextracted[]`/`missing` — `len(claims) + len(unextracted) == scalars walked`, with no silent drops on the trap fixture (duplicates/quotes/coercion/anchors/block scalars).
  4. The abstraction-guard test **fails the suite** if any fixture/org-specific name (lane, module, owner id) appears in `src/newsletters/` — lane sets are proven config, not code.
  5. `pip install .` (bare) imports the spine with `import yaml` unreachable; PyYAML lives behind a `[config]` extra, lazy-imported inside `swimlane.py` only.

**Plans**: 4 plans

  - [x] 01-01-PLAN.md — Lazy PyYAML boundary + `[config]` extra (LANE-04)
  - [x] 01-02-PLAN.md — Swim-lane loader `swimlane.py`: config YAML → Source + traced SectionBinding[] (LANE-01, LANE-02)
  - [x] 01-03-PLAN.md — Trap fixture + `test_swimlane.py`: coverage identity, Hole-B adversarial, determinism (LANE-01, LANE-02)
  - [ ] 01-04-PLAN.md — Abstraction-guard test + bare-install yaml-unreachable tests (LANE-03, LANE-04)

### Phase 2: Module-scope Report composer

**Goal**: Given traced bindings, the composer assembles one `Surface(REPORT, Draft)` per module —
per-lane KPI strip (Δ at compose time) + traced claims, honest `missing[]` routing, stable `R-NNN` —
selecting/ordering/linking traced material only, never authoring facts.
**Depends on**: Phase 1 (consumes its `SectionBinding[]` output).
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04
**Success Criteria** (what must be TRUE):

  1. The composer builds one `Surface(REPORT)` from an arbitrary configured lane set via a kind-agnostic `SectionBinding` seam (per lane: `KpiStripBlock` + `ClaimsBlock`) — project/interview report kinds could slot in with zero composer change (proven by a seam/second-kind test).
  2. Start→close Δ is computed by one pure `compute_delta(start, close)` from two independently content-addressed endpoints into `KpiItem.delta`; a reproducibility test recomputes every rendered delta and asserts byte-equality; if either endpoint is absent, `delta=None`/`dir=None` + a `missing[]` note — never a fabricated `0`; no `Kpi` start/baseline field is added.
  3. A test fails if the composer emits any claim with zero traces or any un-content-addressed trace (closes Hole B), and a numeral-free-prose guard fails if any non-`ClaimsBlock` block's text carries a digit run not drawn from a traced claim (closes Hole A) — `faithfulness.py`/`coverage.py` untouched.
  4. The composed surface carries a stable `R-NNN` from `Ledger.ref_for` against its own `content/module/ids.json`, lands in `Draft` with an owner/manager quote slot and a `fanout` stub, and a no-auto-publish test proves it cannot reach `Published` without the gate.

**Plans**: TBD

### Phase 3: Worked synthetic Module Report

**Goal**: A committed synthetic `module-a` config composes and renders end-to-end (loader → composer
→ ledger → render → Library) as a third `module` corpus with its own ledger, gate-visible and
byte-stable.
**Depends on**: Phase 2 (needs a working composer).
**Requirements**: MODA-01, MODA-02
**Success Criteria** (what must be TRUE):

  1. A synthetic `module-a` config (fabricated naming only — `area-bem`, `module-a`, `owner-*`, `eng-NN`, `toolset-N`; nothing resembling real org/tool/metric nomenclature) composes and renders into `content/`, is visible in the Library with claim-beside-verbatim-trace and a populated honesty panel, and passes the synthetic-name check on committed content.
  2. `newsletters check --corpus module` runs the **same unforked** merge-block gate on the `module` corpus (exit 0 clean; nonzero on a planted blocker) against a dedicated `content/module/ids.json` ledger whose first entry is `R-001`.
  3. The SITE-06 byte-stable double-render invariant holds over the new `module` output (regenerates identically from `render.py`).

**Plans**: TBD
**UI hint**: yes

### Phase 4: Signals-voice PR/summary

**Goal**: The `ship` workflow generates PR/summary bodies that read as faithful, evidence-first
Signals dispatches — built from the diff + verbatim gate output, weakening no gate.
**Depends on**: Independent of Phases 1–3 (edits the ship workflow/script, not the composer);
**ordered last** per milestone scope and because it *quotes* the `check` gate output the earlier
phases produce.
**Requirements**: VOICE-01, VOICE-02
**Success Criteria** (what must be TRUE):

  1. PR-body generation + `summary-standard.md` produce dispatches with exactly the sections: The signal / What we learned / What's verified (verbatim gate output) / What's not here yet / How to verify — generated **from** the diff + gate output, with no AI framing and no hype.
  2. Gate output appears **byte-verbatim** in the body (never paraphrased or softened), and the same numeral-free-unless-sourced rule applies to dispatch prose.
  3. The voice change is proven by a test/snapshot and **weakens no existing check** (no gate edited or relaxed).

**Plans**: TBD

## Progress

**Execution Order:** Phases execute in numeric order: 1 → 2 → 3 → 4 (core is strictly linear
1→2→3; Phase 4 is independent but ordered last).

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Swim-lane binding + traced YAML loader | 3/4 | In Progress|  |
| 2. Module-scope Report composer | 0/TBD | Not started | - |
| 3. Worked synthetic Module Report | 0/TBD | Not started | - |
| 4. Signals-voice PR/summary | 0/TBD | Not started | - |

## Deferred — un-scheduled

> The following 12 items are **recorded, not built** (§7 of the milestone seed). They have **no
> phase number and no checkbox** — they are explicitly NOT scheduled work for v1.1.

- **DEF-01** — Area roll-up scope (multi-module aggregation)
- **DEF-02** — Project-kind report sections
- **DEF-03** — Interview/sit-down-kind report sections
- **DEF-04** — Owner-audit workflow (report routed to its swim-lane owner for review)
- **DEF-05** — Quarter-editorial (ARTICLE) template in the Signal-01 shape (generic, synthetic)
- **DEF-06** — Report→newsletter persona re-cut
- **DEF-07** — Self-assessment leadership re-cut (`mapped_objective` spine)
- **DEF-08** — Learning re-cut of the module report
- **DEF-09** — MOR/IQ defect-project ↔ `Problem` tie-in
- **DEF-10** — Any `Kpi` start/baseline model change
- **DEF-11** — DistillPort AI backend (the robot journalist — designed separately, eval-first)
- **DEF-12** — Problem Board Portfolio Surface (v1.0 Phase 14 carry-over, PROB-02/04)

---
*Roadmap created: 2026-07-02 for milestone v1.1. v1.0 Phases 1–14 archived in git history.*
