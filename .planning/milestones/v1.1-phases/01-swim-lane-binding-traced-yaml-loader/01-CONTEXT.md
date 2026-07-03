# Phase 1: Swim-lane binding + traced YAML loader - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Source:** Stage-A milestone seed + JJ's locked directive + v1.1 research reconciliation
(discuss-phase deliberately skipped — `workflow.skip_discuss=true`; decisions below are LOCKED,
approved by JJ at milestone start)

<domain>
## Phase Boundary

Bind a configured swim lane to its `FunctionalGroup` + `Kpi`s/`Objective`s and load
`sample_team`-style YAML so each value becomes a `Claim`/`KpiItem` **traced to its YAML source**
(or a declared slot routed honestly). **No composition yet** — Phase 2 consumes this phase's
output. Requirements: LANE-01, LANE-02, LANE-03, LANE-04.

</domain>

<decisions>
## Implementation Decisions (LOCKED)

### Abstraction (JJ's fundamental principle, 2026-07-02)
- ABSTRACT EVERYTHING: data models in code, module/lane/owner specifics in YAML config ONLY.
- No fixture/org-specific name (lane, module, owner id) may appear in `src/newsletters/` —
  enforced by an abstraction-guard test that fails the suite on a leak (LANE-03).
- The loader must work for an arbitrary lane set / any org's team shape with zero source change.

### Module placement & shape (research ARCHITECTURE, reconciled)
- New top-level module `src/newsletters/swimlane.py` — sibling of `worksurface.py`, mirroring its
  precedent (read-only ingest, content-addressed Sources). Loader only; NO `compose.py` this phase.
- Loader emits a kind-agnostic `SectionBinding` per lane (heading + KpiItems + Claims + missing) —
  the seam Phase 2's composer consumes and future project/interview kinds produce into. Keep it a
  small typed Pydantic model, AI-free, stdlib+pydantic only.
- Bind at the **parsed-dict level** — do NOT instantiate `FunctionalGroup`/`Kpi` from YAML and do
  NOT modify `models.py` (live type tension: `owner: str` idsid vs `TeamMember`; `Ownable.owner`
  validator; deferred by design).

### Tracing (research STACK + PITFALLS, reconciled)
- The raw YAML file text IS `Source.transcript` (`path.read_text()` verbatim); `Source.id` is the
  repo-relative POSIX path (mirror `worksurface.capture_files` edge policy: missing/non-utf8 raise;
  never hand-mint `content_hash`).
- Every loaded value is minted ONLY via `Trace.from_source` against the raw text — every trace
  `is_addressed` (closes Hole B upstream: no un-addressed free-pass traces from this loader, ever).
- Locate values in the RAW file text with a forward-only cursor (reuse/mirror
  `adapters/normalize.py` semantics) — never against a re-serialized YAML dump (offset drift).
- Zero silent drops, anchored to scalars READ: `len(claims) + len(unextracted) == scalars walked`.
  Duplicate values, quoted scalars, type-coerced forms (`yes`, `1.0`, dates), block scalars,
  anchors/aliases → if not verbatim-locatable, route to `unextracted[]` with a reason code —
  NEVER fabricate an offset (RETRO Phase-7 lesson: anchor coverage to what was READ).
- `Source.timestamp` via the existing `deterministic_timestamp`/`EPOCH_ZERO` helper — never now().

### Packaging (research STACK, locked)
- PyYAML >= 6.0.3 behind a NEW `[config]` extra; lazy `_yaml_loader.py`-style boundary inside
  the swimlane module only (copy the `_openpyxl_loader` pattern: `yaml.safe_load` only, teaching
  ImportError, no top-level `import yaml`). Bare `pip install .` keeps the spine YAML-free.
- Extend the existing bare-install AI-isolation gate so `yaml` is asserted unreachable from core.
- `yaml.safe_load` ONLY (never `yaml.load`); config files are data, not code.

### Config schema (Claude's discretion, within these rails)
- A module config YAML declares: module id, area id, lane list — each lane with a heading/id, its
  functional-group binding, owner id, member ids, KPI entries (label + period values), objective
  refs. Exact key names are Claude's discretion; keep them generic (`lanes:`, `kpis:` …), document
  in the file and in a committed generic example under `tests/fixtures/` (synthetic names only —
  the worked `module-a` example itself is Phase 3, but a small generic test fixture lives here).
- Fixture naming discipline (even in tests): generic ids only (`lane-a`, `owner-1`, `module-x`) or
  the seed's fabricated scheme; nothing resembling real org/tool/metric/site/program nomenclature.

### Testing (research PITFALLS → Phase-1 test load)
- Trap fixture: duplicates / quotes / coercion / anchors / block scalars — prove honest routing.
- `test_no_yaml_scalar_is_read_but_undisclosed` — the read-anchored coverage identity.
- Adversarial: an un-addressed trace emitted by the loader is CAUGHT by test, not passed.
- Abstraction guard: grep-style test over `src/newsletters/` for fixture-specific names.
- Bare-install: `import yaml` unreachable from core; `[config]` extra lazy-loads.
- Determinism: same file → byte-identical Source + bindings across two loads/processes.

### Claude's Discretion
- Exact `SectionBinding` field names/shape (keep minimal + generic).
- Reason-code naming for unextracted routing (mirror the `_R_*` adapter convention).
- Whether KPI period endpoints live as two claims or a claim-pair structure — Phase 2 needs both
  endpoints independently traced; do not compute Δ here (that is Phase 2, `compute_delta`).
- Test file layout; fixture authoring helper (committed byte-reproducible fixtures per repo norm).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone research (the reconciled design)
- `.planning/research/SUMMARY.md` — reconciled decisions (YAML dep, delta contract, ledger, Holes A/B)
- `.planning/research/ARCHITECTURE.md` — module placement, YAML-as-transcript mechanism, file:line grounding
- `.planning/research/PITFALLS.md` — the 12 pitfalls; Phase-1 owns the loader set
- `.planning/research/STACK.md` — PyYAML/[config]-extra decision detail

### Live code precedents (read the LIVE code, not just docs)
- `src/newsletters/worksurface.py` — capture_files edge policy, content-addressed local-file Sources
- `src/newsletters/adapters/normalize.py` — the single faithful-extraction site; cursor semantics
- `src/newsletters/adapters/_timestamps.py` — EPOCH_ZERO / deterministic_timestamp
- `src/newsletters/adapters/_openpyxl_loader.py` (and `_pptx_loader.py`) — the lazy-extra boundary pattern to copy
- `src/newsletters/semantic.py` — Trace.from_source offset validation; Claim/KpiItem shapes
- `src/newsletters/models.py` — the domain models being bound AT DICT LEVEL (do not modify)
- `sample_team/*.yml` — the existing YAML shape the loader generalizes over
- `pyproject.toml` + `.importlinter` + `.github/workflows/ci.yml` — extras + contract discipline (ci.yml MUST NOT be weakened; extending the bare-install assertion list is allowed)

### Rules
- `CLAUDE.md` — hard rules (no auto-publish, AI-optional core, faithful-not-suggestive)
- `RETRO.md` — Phase-7 silent-drop + Phase-13 mutable-model lessons (enforce invariants in code + adversarial test)

</canonical_refs>

<specifics>
## Specific Ideas

- Milestone gate policy: enforced set = pytest / lint-imports / `newsletters check` (all corpora) /
  byte-stable double-render / bare-install; mypy+black+isort = no-NEW-failures vs the 2026-07-02
  baseline — new files must be clean.
- One task = one atomic commit; commit + push after every task (ephemeral container).
- PHASE-1 CIRCUIT BREAKER: if this phase is not cleanly green on the enforced gate set, the
  overnight run STOPS (do not build Phase 2 on a shaky loader).

</specifics>

<deferred>
## Deferred Ideas

- Composition/rendering of any Surface — Phase 2/3.
- `module-a` worked example config — Phase 3 (this phase commits only generic test fixtures).
- Typed `ConfigLocator` union variant — reuse `FreeLocator` this milestone; clean future addition.
- All DEF-01..12 milestone deferrals (see ROADMAP).

</deferred>

---

*Phase: 01-swim-lane-binding-traced-yaml-loader*
*Context gathered: 2026-07-02 from the approved Stage-A seed + committed v1.1 research*
