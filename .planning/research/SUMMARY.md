# Project Research Summary

**Project:** Newsletters — v1.1 Swim-Lane Module Report Composer
**Domain:** Config-driven, traced YAML loader + deterministic swim-lane Report composer (brownfield addition to an existing typed trust pipeline)
**Researched:** 2026-07-02
**Confidence:** HIGH

## Executive Summary

This milestone bolts a new, config-driven capability onto an already-shipped trust spine: a YAML
loader that turns per-module swim-lane config into content-addressed traced `Claim`/`KpiItem`s, and
a composer that arranges those traced inputs into a module-scope `Surface(REPORT, Draft)` — one
`KpiStripBlock` + `ClaimsBlock` per swim lane, with owner attribution, a sourced owner quote, a
start→close Δ, and honest routing of anything unprovable to `Surface.missing[]`. The composer is
strictly a *selector/orderer/linker* — it may never author factual prose, invent a baseline, or
flag a lane "at risk" by inference. Two existing structural gaps in the spine (the faithfulness
gate only scans `ClaimsBlock`; an un-addressed trace passes entailment trivially) make this
milestone's #1 risk **smuggled, un-gated facts** — a computed delta, a prose sentence, or a KPI
value that looks traced but isn't actually checked. The plan closes both gaps with new adversarial
tests rather than touching the gate itself.

The recommended approach: add exactly one new dependency, `PyYAML>=6.0.3`, behind a `[config]`
extra with a lazy-imported boundary module (mirroring the `_openpyxl_loader.py` precedent), so the
bare-install spine stays YAML-free and the "core = pydantic/typer/sqlmodel" invariant holds. Split
the new code into two top-level siblings of `worksurface.py` — `swimlane.py` (the loader; owns the
only new I/O and third-party edge) and `compose.py` (the composer; pure in-memory semantic assembly,
kind-agnostic via a generic `SectionBinding` abstraction so project/interview report kinds can slot
in later without composer changes). The worked example lands as a third corpus (`module`) with its
own ledger, not an extension of the existing `work` corpus, preserving the sample/real/config
boundary the codebase already draws.

The key risk is *faithfulness erosion by convenience*: a computed delta that has no trace story of
its own, a "helpful" summary sentence with an un-sourced numeral, or an un-addressed trace minted to
dodge span-checking. All three are structurally invisible to the existing gate and must be closed by
new, explicit tests (delta-reproducibility, numeral-free-prose guard, all-claims-content-addressed)
rather than by editing `faithfulness.py`/`coverage.py`, which are out of scope and must not be
touched this milestone. A second risk class is determinism (timestamps, dict/set ordering) and
ledger discipline (ref collisions across the now-three ledgers) — both have exact, hardened
precedents in the codebase (`_timestamps.py`, `Ledger.ref_for`) that this milestone must reuse, not
reinvent.

## Key Findings

### Recommended Stack

Python's stdlib has no YAML parser, so a real dependency is required; the only two live questions
were *which* YAML lib and *which layer* it lives in. **PyYAML>=6.0.3**, `yaml.safe_load`/`compose`
only, is the clear pick — MIT, pure-Python-capable, and its low-level node API yields exact
char-offset source marks, which is also the entire tracing mechanism (no new tracing library
needed; `Trace.from_source` + PyYAML node marks is sufficient). `ruamel.yaml` was rejected as
overkill (round-trip/comment-preservation features this read-only loader doesn't need); TOML/stdlib
was rejected because it churns existing YAML fixtures and gives no per-value source marks.

**Core technologies:**
- PyYAML `>=6.0.3` — parse config YAML and expose per-scalar source marks — sole new dependency, MIT, non-AI, offset-exact for tracing.
- `Source.transcript` + `Trace.from_source` (existing, `semantic.py`) — the entire pinning/tracing mechanism; YAML file text becomes the transcript, no new library required.
- `adapters/normalize.py` (existing) — the cursor-advancing, file-order verbatim-locate + `unextracted[]` routing logic; reuse rather than reinvent scalar location.

### Expected Features

The composer's job is to assemble a standard practitioner artifact — a per-lane status report with
ownership, KPI movement, traced findings, and visible gaps — entirely from an existing traced-claim
substrate, without ever authoring new facts.

**Must have (table stakes):**
- Per-lane section grouping (one `KpiStripBlock` + `ClaimsBlock` per configured lane, config order)
- Start→close Δ computed at compose time into `KpiItem.delta`/`dir` (no `Kpi.start` model field)
- Traced findings per lane via pure reuse of `ClaimsBlock`
- Owner attribution + sourced owner quote per lane (never composer-authored)
- Config-driven lanes/modules/owners (YAML) — the milestone's whole premise
- `missing[]` routing + honesty panel for anything unprovable
- Stable `R-NNN` from the ledger; `Draft`-only, no gate involvement
- Deterministic, byte-stable output (double-render equality)

**Should have (competitive):**
- Every KPI Δ and finding traces to its YAML source — no comparable status-report tool does this
- Undefined-Δ as a first-class honest state (`delta=None, dir=None` → "—"/"new", never a fake 0)
- Generic `ReportSection` abstraction so project/interview report kinds slot in later
- Composer as pure select/order/link, audit-clean by construction

**Defer (v2+):**
- Relative Δ (%) — only once both start and close exist
- Per-lane risk/dependency section — must be sourced claims, not composer verdicts
- Project-kind / interview-kind reports; cross-lane rollup to a weekly Newsletter
- `Kpi.start`/baseline as a real model field — only if compose-time derivation proves insufficient

### Architecture Approach

Two new top-level modules sibling to `worksurface.py`: **`swimlane.py`** (loader — the only module
touching disk/`yaml`, converts each config file into a `Source` and each configured lane into a
`SectionBinding`, minting `Claim`/`KpiItem`s via `Trace.from_source` or routing to `missing[]`) and
**`compose.py`** (composer — pure in-memory, kind-agnostic assembly of `SectionBinding[]` into
`Surface(REPORT, Draft)`, computing Δ at compose time and requesting `R-NNN` from a **new, own**
`content/module/ids.json` ledger). The worked example wires in as a **third `CorpusName.module`**
alongside `rev1`/`work` (not an extension of `work`, to preserve the sample/real/config boundary),
reusing `review.review_blockers`, `render.render_surface/render_library`, and `templates.REPORT`
completely unchanged.

**Major components:**
1. `swimlane.py` (loader) — YAML → `Source(transcript=raw file text)`, config → `SectionBinding[]`, verbatim trace-or-missing routing, deterministic timestamps
2. `compose.py` (composer) — `SectionBinding[] → Surface(REPORT, Draft)`, compose-time Δ, `R-NNN` via `Ledger.ref_for`, `build_module_site`
3. `content/module-a/*.yml` fixture — the synthetic worked example, fabricated naming, config only (never in `src/`)
4. Existing spine (`site.Ledger`, `render.py`, `review.py`, `cli.py --corpus`) — reused with a new `module` branch in `build`/`check`, gate itself untouched

### Critical Pitfalls

1. **Computed delta invents an un-gated fact (Hole A: gate only scans `ClaimsBlock`; `KpiItem.delta` is a bare str)** — never compute a delta unless BOTH start and close endpoints are content-addressed traced Claims; derive via one pure `compute_delta()` function; prove reproducibility with a byte-equality test; if either endpoint is missing, ship value-only and route the gap to `missing[]`.
2. **Un-addressed traces pass faithfulness trivially (Hole B)** — every claim this milestone mints must have `trace.is_addressed is True`; add an adversarial test that a bypass (an un-addressed trace) is caught/fails.
3. **Prose/rationale slots accumulate un-traced numerals** — composer may select/order/link/label only, never author factual prose; add a guard test scanning every non-`ClaimsBlock` block's text for un-sourced digit runs.
4. **Tracing against re-serialized YAML instead of raw file text** — `Source.transcript` must be `path.read_text()` verbatim, never a `safe_dump`/re-stringify; reuse `adapters/normalize.py` for cursor-advancing, file-order scalar location.
5. **Non-deterministic timestamps / ordering break byte-stable re-render** — reuse `adapters/_timestamps.deterministic_timestamp()`/`EPOCH_ZERO`; preserve file order for lanes/KPIs (no `set()`, no non-total sort keys); prove with double-render byte-equality.

## Implications for Roadmap

The milestone's four phases are already fixed by scope (loader → composer → worked example →
Signals-voice PR bodies) and dependencies are strictly linear for 1→2→3, with phase 4 low-coupling
and ordered last. Research confirms this structure is correct and adds the specific guard tests each
phase must land to close the structural holes.

### Phase 1: Traced YAML Loader (`swimlane.py`)
**Rationale:** Everything downstream (composer, worked example) consumes its output; it is the only module touching `yaml`/disk and must be proven deterministic and honest before anything is built on it.
**Delivers:** `Source(transcript=raw file text)` per config file; `SectionBinding[]` (kind-agnostic: `heading`, `kpi_items`, `claims`, `missing`) per configured lane; verbatim trace-or-missing routing via reused `adapters/normalize.py`; deterministic `Source.timestamp`.
**Addresses:** Config-driven lanes/modules/owners (FEATURES table stakes); traced findings substrate.
**Avoids:** Pitfall 3 (re-serialized-YAML tracing), Pitfall 4 (scalar-location traps — duplicates/quotes/coercion/anchors), Pitfall 9 (silent drops — read-anchored coverage), Pitfall 5 (non-deterministic `Source.timestamp`), Pitfall 8 (abstraction-guard test authored here so later phases can't regress it).

### Phase 2: Module-Scope Report Composer (`compose.py`)
**Rationale:** Once traced bindings exist, this is where the milestone's core trust risk concentrates (deltas, prose, ordering) — build the enforcement tests alongside the composer, not after.
**Delivers:** Per-lane `KpiStripBlock`(compose-time Δ) + `ClaimsBlock`; owner attribution + sourced quote slot; `missing[]` union; `Surface(REPORT, Draft)` with `R-NNN` via `Ledger.ref_for` against a new, dedicated `content/module/ids.json` ledger.
**Uses:** `templates.REPORT`, `semantic.KpiStripBlock/ClaimsBlock/Surface`, `site.Ledger` (all reused unchanged).
**Implements:** The `SectionBinding[] → Surface` seam; the generic, kind-agnostic section abstraction (question d in ARCHITECTURE.md) so project/interview kinds slot in later with zero composer change.
**Avoids:** Pitfall 1 (delta-reproducibility test), Pitfall 2 (numeral-free-prose guard), Pitfall 6 (lane/dict ordering determinism), Pitfall 7 (ledger ref collisions — via `ref_for`, never hardcoded), Pitfall 10 (adversarial bypass tests), Pitfall 11 (the gate-weakening forbidden list — `faithfulness.py`/`coverage.py`/golden tests stay untouched).

### Phase 3: Worked Synthetic Module Report (`module-a`)
**Rationale:** Proves the full path end-to-end (loader → composer → ledger → render → Library) against a real, committed, fabricated-naming fixture — nothing before this phase is provably real.
**Delivers:** `content/module-a/*.yml` fixture; `CorpusName.module` wired into `cli.py build`/`check`; `content/module/ids.json` (first entry `R-001`, its own ledger); rendered, Library-visible surface with claim-beside-trace + honesty panel; double-render byte-equality verified.
**Addresses:** "Worked synthetic Module Report" (FEATURES P1); proves config-only re-shaping.
**Avoids:** Pitfall 5 (byte-stable committed render), Pitfall 7 (correct, deliberately-chosen ledger — own ledger, not appended to `work`/`rev1`), Pitfall 8 (synthetic-name check on committed content — public-repo confidentiality).

### Phase 4: Signals-Voice PR Bodies (`ship` workflow)
**Rationale:** Structurally independent of 1–3 (edits the ship workflow/script, not the composer); ordered last per milestone scope and because it *quotes* the `check` gate output the earlier phases produce.
**Delivers:** PR/summary bodies generated from `git diff` + verbatim `newsletters check` output, in Signals voice.
**Addresses:** FEATURES "Signals-voice PR/summary bodies" (in-milestone stretch).
**Avoids:** Pitfall 12 (invented facts / laundered gate) — gate output must be byte-verbatim in the body, never paraphrased or softened; same numeral-free-unless-sourced rule as Pitfall 2 applies to dispatch prose.

### Phase Ordering Rationale

- Strict data dependency 1→2→3: the composer needs traced bindings (phase 1's output); the worked example needs a working composer (phase 2's output).
- Phase 4 has almost no shared surface with 1–3 beyond shelling out to `check` — it is ordered last by milestone scope, not by a hard dependency.
- Grouping mirrors the codebase's own module-splitting logic (loader vs composer as two modules with different import edges) rather than an arbitrary task split — this keeps each phase's testable surface small (the loader is testable with hand-built fixtures, no `Surface` needed; the composer is testable with hand-built `SectionBinding`s, no YAML needed).
- The two structural gate holes (A: gate scans only `ClaimsBlock`; B: un-addressed traces pass trivially) are closed by NEW tests landed in Phase 1 (abstraction-guard, read-anchored coverage) and Phase 2 (delta-reproducibility, numeral-free-prose guard, all-claims-content-addressed) — never by editing `faithfulness.py` or `coverage.py`, which stay out of scope for the whole milestone.

### Research Flags

Needs deeper research during planning:
- **Phase 1 (Loader):** the scalar-location trap fixture (duplicates, quoting, type coercion, anchors/aliases, block scalars) needs care to design so it proves honest routing without becoming an unmaintainable fixture; worth a short research-phase pass on `normalize()`'s exact cursor semantics before writing the trap tests.
- **Phase 2 (Composer):** the delta-reproducibility contract ("delta = f(start-trace, close-trace)") is a genuinely new trace pattern not previously used in the codebase — worth confirming the honesty-panel rendering (how two endpoint traces are surfaced beside one delta) against `render.py`'s existing claim-beside-span device before committing to an API shape.

Standard patterns (skip research-phase):
- **Phase 3 (Worked example):** near-exact mirror of `worksurface.py`'s `build_work_site` — `Ledger.load → Site.from_surfaces → ledger.save → render each page → render_library`; no new pattern.
- **Phase 4 (PR bodies):** shells out to an existing `check` command and quotes its output verbatim; low architectural novelty.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Single dependency decision, grounded in a live repo audit confirming no existing YAML consumer plus verified PyPI metadata; the extras/lazy-loader pattern is an exact, already-hardened precedent (`_openpyxl_loader.py`). |
| Features | HIGH (composer contract) / MEDIUM (external practitioner norms) | The edge-case contract is derived directly from the live model and hard rules (HIGH); general swim-lane report expectations are cross-checked against consistent but generic PM sources (MEDIUM). |
| Architecture | HIGH | Every recommendation is grounded in live code with file:line citations; the one open tension (raw-dict vs typed `FunctionalGroup` instantiation) is resolved with a concrete, cited type mismatch in `models.py`. |
| Pitfalls | HIGH | Grounded in live code (`semantic.py`, `faithfulness.py`, `normalize.py`, `coverage.py`) plus `RETRO.md`'s prior incidents of the same failure classes recurring in this codebase. |

**Overall confidence:** HIGH

### Reconciled Open Questions

**1. YAML dependency layer — RECONCILED: `[config]` extra, not core.** STACK's default recommendation
and ARCHITECTURE's "add to core `dependencies`" framing appear to conflict; they don't. STACK's
own fallback clause names the exact condition under which core placement is correct: *if compose
must run inside `newsletters build` on a bare install*. This milestone's design (compose is an
author-time step, like `capture.py`; `build`/`check` render/gate already-persisted `Surface`s) means
that condition does not hold — bare-install `newsletters build` never needs to parse YAML.
**Recommendation: PyYAML behind a NEW `[config]` extra, lazy-imported inside `swimlane.py` only**,
mirroring `_openpyxl_loader.py` exactly, with a new `.[config,test]` CI step (parallel to the
`import-linter` job) and a grep-style bare-install assertion (mirroring `test_ai_optional.py`) that
`import yaml` does not appear reachable from a bare install. This keeps the literal "core = 3 deps"
invariant intact. If a future milestone needs compose to run inside bare `newsletters build`,
promote PyYAML to core then (documented as the explicit fallback path), not now.

**2. Delta trace story — RECONCILED, both researchers were describing the same contract.**
ARCHITECTURE is right that the delta itself is **not** a `Claim` — `KpiItem.delta` is a free `str`
computed at compose time and never appears verbatim in the YAML, so it cannot be pinned by
`Trace.from_source` directly. PITFALLS is right that this makes the delta the milestone's single
biggest faithfulness risk (Hole A: `KpiItem.delta` sits outside `ClaimsBlock` and is completely
un-gated). **The combined, single contract:** the delta is not itself evidence — it is a
*derivation over two pieces of evidence*. Both the start value and the close value must exist as
independently content-addressed `Claim`/`KpiItem`s (`trace.is_addressed is True`, pinned to their
own YAML spans) **before** any delta is computed. The delta is produced by one pure function,
`compute_delta(start, close)`, never authored inline in a format string. A test must recompute every
rendered delta from its two endpoint values and assert byte-equality (the "reproducibility" proof
standing in for a trace, since no span exists to check). The honesty panel/evidence chip for a delta
must display **both** endpoint traces so a reviewer can redo the subtraction by hand. If either
endpoint is missing or untraceable, the delta is **not computed** — `delta=None, dir=None`, and the
gap is routed to `Surface.missing[]`. This closes Hole A for deltas specifically without touching
`faithfulness.py`.

**3. Ledger — RECONCILED: own, dedicated ledger (`content/module/ids.json`).** ARCHITECTURE
recommends a third `module` corpus with its own ledger; PITFALLS raises the choice as open ("own
ledger vs unified") because the codebase already has two independent `R-001`s (`content/rev1/`,
`content/work/`) and warns that refs are unique only *within* a ledger. **Recommendation: own
ledger**, for two convergent reasons. First, precedent: `work` already has its own ledger for the
identical reason (`worksurface.py`'s "this is how *this build* was done" vs `dogfood.py`'s synthetic
sample) — a config-driven, synthetic module report is the same category of artifact as `work`, not a
`rev1`/`work` variant, so it earns the same treatment. Second, safety: appending to an existing
ledger (`rev1` or `work`) risks conflating a synthetic fixture's identity with real content's
identity space, and offers no benefit since refs are already ledger-scoped everywhere in this
codebase (the Library assembles across ledgers by corpus, not by a single global ref-space). The
cost — three independent `R-001`s existing simultaneously if all corpora are surfaced together — is
accepted as the existing, already-tolerated status quo (two `R-001`s already coexist today), not a
new problem this milestone introduces. Concretely: `Ledger.ref_for(slug, "report")` against
`content/module/ids.json`, `_next_ordinal = max(existing)+1`, `ledger.save()` called explicitly by
`build_module_site` (mirroring `build_work_site` beat for beat) — never a hardcoded `"R-NNN"` string.

**4. The two structural faithfulness holes — closed by NEW tests, in the phases below, without
touching the gate.**
- **Hole A (gate scans only `ClaimsBlock`; `KpiItem`/`ProseBlock` content is un-gated):** closed in
  **Phase 2 (Composer)** by a numeral-free-prose guard test that scans every non-`ClaimsBlock` block's
  rendered text for un-sourced digit runs (allow-listing only config-derived structural labels), plus
  the delta-reproducibility test described above for the one legitimate case where a derived number
  (the delta) is allowed to appear outside `ClaimsBlock`. Neither test modifies `faithfulness.py` or
  `Surface._published_claims()` — they are new, additive guards that run before/alongside the
  existing gate.
- **Hole B (an un-addressed trace passes `entails` trivially):** closed in **Phase 1 (Loader) and
  reinforced in Phase 2 (Composer)** by requiring every `Trace` this milestone mints to go through
  `Trace.from_source` exclusively (never a hand-built `Trace` with `content_hash=None`), plus an
  explicit adversarial test asserting `trace.is_addressed is True` for every `Claim`/`KpiItem` the
  loader and composer produce, and a second adversarial test proving that a deliberately un-addressed
  trace is caught (raises or fails a check) rather than silently passing.
  `SpanContainmentFaithfulness.entails` itself is untouched — the fix is "never hand it an
  un-addressed trace in the first place," enforced upstream of the gate.

### Gaps to Address

- **Typed lane objects vs raw-dict binding:** the loader deliberately works at the parsed-dict level
  rather than instantiating `FunctionalGroup`/`Kpi` (a live type mismatch in `models.py` makes direct
  instantiation fail today — `owner: str` vs `TeamMember`, `idsid` key not in `TeamMember`). This is
  correctly scoped out of v1.1, but flag it for planning: if a future milestone wants typed lane
  objects, `idsid → TeamMember` resolution must be designed first.
  - Handle during planning: note as an explicit non-goal in the Phase 1 plan; do not let an
    executor "helpfully" fix the `models.py` mismatch as a side quest.
- **Fallback surface area (one module vs two):** ARCHITECTURE offers a fallback of merging
  loader+composer into one `modulereport.py` (mirroring `worksurface.py`'s single-file shape) if
  minimal surface area is preferred over the loader/composer testability split. Recommend keeping the
  two-module split (it is the researched default and enables the phase-1/phase-2 boundary this
  roadmap relies on) — but flag it as a deliberate choice for the roadmapper to confirm, not an
  unexamined default.
  - Handle during planning: confirm the two-module split explicitly in the Phase 1 plan's stated
    scope, so Phase 2 has a known, stable import boundary to build against.

## Sources

### Primary (HIGH confidence)
- Live repo audit — `src/newsletters/semantic.py`, `models.py`, `locators.py`, `site.py`, `cli.py`, `review.py`, `templates.py`, `worksurface.py`, `capture.py`, `adapters/normalize.py`, `adapters/_openpyxl_loader.py`, `adapters/_timestamps.py`, `distill/faithfulness.py`, `distill/coverage.py`, `.importlinter`, `pyproject.toml`, `sample_team/*.yml`, `content/rev1/ids.json`, `content/work/ids.json`
- `.planning/PROJECT.md` — milestone scope, Key Decisions (delta-at-compose-time, no `Kpi.start`, no fixture names in `src/`, Draft-only, PR body may not weaken a gate)
- `RETRO.md` — Phase-7 silent-drop lesson, Phase-13 mutable-model-bypass lesson, "agent says green ≠ green," both-orders import acceptance check
- PyPI PyYAML metadata (latest 6.0.3, MIT, `requires_python >=3.8`) — https://pypi.org/pypi/PyYAML/json
- PyYAML documentation (`safe_load`, `compose`, node `start_mark`/`end_mark`) — https://pyyaml.org/wiki/PyYAMLDocumentation

### Secondary (MEDIUM confidence)
- SlideTeam — workstream status report templates (per-lane KPIs, ownership, risks as expected content)
- Atlassian — swimlane diagrams and RACI ownership convention
- ProjectManager — swimlane diagram template (lane = responsibility grouping)
- Ahrefs / Datadog — Δ = close − start dashboard convention; no-stable-baseline handling as a recognised concern

---
*Research completed: 2026-07-02*
*Ready for roadmap: yes*
