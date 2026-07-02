# Requirements: Newsletters — Milestone v1.1 (Swim-Lane Module Report)

**Defined:** 2026-07-02
**Core Value:** Make work legible and trustworthy — every published claim traces to evidence;
nothing publishes without a human. (v1.1 adds the COMPOSER: the machine that assembles a
module's swim-lane Report from config, faithfully.)

> v1.0 (Rev2, Phases 1–13) is **Validated and archived** — the full requirement set
> (SOCK/PKG/PROV/ADAPT/SITE/WORK/LEARN/PROB-01,03) lives in git history of this file
> (pre-2026-07-02) and in `.planning/PROJECT.md → Validated in v1.0`.

**Fundamental principle (JJ, locked at milestone start):** ABSTRACT EVERYTHING — data models in
code, specifics in config. No lane/module/owner name may be hardcoded in `src/`; any org's team
shape must fit without touching source. Enforced by test.

## v1.1 Requirements

### Swim-Lane Binding & Traced YAML Loader (LANE)

- [ ] **LANE-01**: An operator can declare a module's swim lanes in YAML config, and the loader
  binds each configured lane to its `FunctionalGroup` + `Kpi`s/`Objective`s at the parsed-dict
  level — no change to `models.py`, no hardcoded lane names in `src/`
- [ ] **LANE-02**: Every value the loader reads becomes a `Claim`/`KpiItem` content-addressed to
  its raw YAML source text via `Trace.from_source` (the YAML file text IS `Source.transcript`);
  anything readable-but-unlocatable routes to `unextracted[]`/`missing` — zero silent drops,
  anchored to scalars READ, not units emitted
- [ ] **LANE-03**: An abstraction-guard test fails the suite if any fixture/org-specific name
  (lane, module, owner id) appears in `src/newsletters/` — lane sets are config, proven generic
- [ ] **LANE-04**: PyYAML lives behind a `[config]` extra with a lazy loader boundary (mirroring
  `[excel]`/`[pptx]`); bare `pip install .` still runs the spine with zero YAML dependency

### Module-Scope Report Composer (COMP)

- [ ] **COMP-01**: The composer assembles one `Surface(REPORT)` per module from an arbitrary
  configured lane set — per lane a `KpiStripBlock` + `ClaimsBlock` via a kind-agnostic section
  seam (project/interview report kinds can slot in later with zero composer change)
- [ ] **COMP-02**: Start→close movement is computed at compose time from two independently-traced
  endpoints into `KpiItem.delta`; if either endpoint is absent, `delta=None` + a `missing[]`
  note — never a fabricated `0`; reproducibility proven by test; NO `Kpi` start/baseline field
- [ ] **COMP-03**: The composer SELECTS/ORDERS/LINKS traced claims only: a test fails if it emits
  any claim with zero traces or any un-content-addressed trace (closes the entailment free-pass
  hole), and the connective prose slot carries no numerals/facts not drawn from a traced claim
  (closes the ClaimsBlock-only gate hole) — `faithfulness.py`/`coverage.py` untouched
- [ ] **COMP-04**: The composed report carries a stable `R-NNN` ref from its own append-only
  `content/module/ids.json` ledger, lands in `Draft`, includes an owner/manager quote slot and a
  `fanout` stub; no-auto-publish proven by test on the composed surface

### Worked Synthetic Module Report (MODA)

- [ ] **MODA-01**: A synthetic `module-a` example config (fabricated naming scheme: `area-bem`,
  `module-a`, `owner-*`, `eng-NN`, `toolset-N`; nothing resembling real org/tool/metric/site/
  program nomenclature) composes and renders into `content/`, visible in the Library,
  gate-visible: claim beside verbatim trace + populated honesty panel
- [ ] **MODA-02**: `newsletters check --corpus module` runs the SAME unforked merge-block gate on
  the module corpus, and the byte-stable double-render invariant (SITE-06) holds over the new
  output

### Signals-Voice PR Bodies (VOICE)

- [ ] **VOICE-01**: The `ship` workflow's PR-body generation + `summary-standard.md` template
  produce Signals dispatches with exactly: The signal / What we learned / What's verified
  (verbatim gate output) / What's not here yet / How to verify — generated FROM the diff + gate
  output, no AI framing, no hype
- [ ] **VOICE-02**: The voice change is proven by a test/snapshot and weakens no existing check

## Deferred (un-scheduled — §7 of the milestone seed; recorded, not built)

- **DEF-01**: Area roll-up scope (multi-module aggregation)
- **DEF-02**: Project-kind report sections
- **DEF-03**: Interview/sit-down-kind report sections
- **DEF-04**: Owner-audit workflow (report routed to its swim-lane owner for review)
- **DEF-05**: Quarter-editorial (ARTICLE) template in the Signal-01 shape (generic, synthetic)
- **DEF-06**: Report→newsletter persona re-cut
- **DEF-07**: Self-assessment leadership re-cut (`mapped_objective` spine)
- **DEF-08**: Learning re-cut of the module report
- **DEF-09**: MOR/IQ defect-project ↔ `Problem` tie-in
- **DEF-10**: Any `Kpi` start/baseline model change
- **DEF-11**: DistillPort AI backend (the robot journalist — designed separately, eval-first)
- **DEF-12**: Problem Board Portfolio Surface (v1.0 Phase 14 carry-over, PROB-02/04)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Method docs into `docs/method/` | Companion files absent from workspace (`_incoming/` does not exist) — skipped per seed §6.3, noted in the Phase-3 PR |
| Real data, real names, real metrics | Public repo; the wall holds — tonight furnishes the tool on synthetic data only; JJ authors the real report inside the wall later |
| Typed-lane-object binding (`FunctionalGroup` instantiation from YAML) | Live type tension (`owner: str` vs `TeamMember`); loader binds at parsed-dict level by design — model change deferred |
| Editing existing gates/tests to go green | Hard rule: conftest, faithfulness/conformance/no-auto-publish/determinism tests, PKG-04, PROV-04, ci.yml untouched (VOICE work excepted, may not weaken) |
| Repo-wide black/isort reformat & pre-existing mypy debt | Pre-dates this milestone (59 files, 9 errors, recorded baseline); policy = no NEW failures; cleanup is its own future change |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LANE-01 | Phase 1 | Pending |
| LANE-02 | Phase 1 | Pending |
| LANE-03 | Phase 1 | Pending |
| LANE-04 | Phase 1 | Pending |
| COMP-01 | Phase 2 | Pending |
| COMP-02 | Phase 2 | Pending |
| COMP-03 | Phase 2 | Pending |
| COMP-04 | Phase 2 | Pending |
| MODA-01 | Phase 3 | Pending |
| MODA-02 | Phase 3 | Pending |
| VOICE-01 | Phase 4 | Pending |
| VOICE-02 | Phase 4 | Pending |

**Coverage:**
- v1.1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-02*
*Last updated: 2026-07-02 after research synthesis*
