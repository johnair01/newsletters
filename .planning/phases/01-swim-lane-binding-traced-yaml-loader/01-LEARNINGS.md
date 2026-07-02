---
phase: 1
phase_name: "Swim-lane binding + traced YAML loader"
project: "Newsletters"
generated: "2026-07-02"
counts:
  decisions: 7
  lessons: 5
  patterns: 5
  surprises: 4
missing_artifacts:
  - "01-UAT.md (no conversational UAT was run this phase)"
---

# Phase 1 Learnings: Swim-lane binding + traced YAML loader

> Retroactively extracted (2026-07-02) from the phase paper trail (01-CONTEXT, 01-PATTERNS, four
> PLANs/SUMMARYs), the live code (`swimlane.py`, `_yaml_loader.py`, the three test suites), and git
> history (`63fa496`…`e56f93e`, merged as `07f1a60` PR #4; plus the Phase-2-era `e3554ed`/`619b76e`/
> `efb635a` modifications to `swimlane.py`).

## Decisions

### PyYAML behind a `[config]` extra, not a core dependency
PyYAML was placed behind a new optional `[config]` extra and lazy-imported inside a single boundary
module, so a bare `pip install .` runs the deterministic spine with zero PyYAML. This overrode one
RESEARCH ARCHITECTURE line that had suggested `[project] dependencies`.

**Rationale:** The AI-optional / minimal-core invariant demands that `import newsletters` works and
the spine runs with only stdlib + Pydantic; a third-party parser (even a non-AI one) must not be
reachable from a bare install. Mirrors the hardened `[excel]`/`[pptx]` precedent beat-for-beat.
**Source:** 01-01-SUMMARY.md, 01-CONTEXT.md §Packaging, 01-PATTERNS.md "No Analog Found" divergence table

### Bind lanes at the parsed-dict level, never instantiate `models.py` types
The loader emits a kind-agnostic `SectionBinding` (heading + `KpiItem`s + `Claim`s + missing +
unextracted) reusing existing `KpiItem`/`Claim`; it never constructs `models.FunctionalGroup`/`Kpi`
and `models.py` is byte-unchanged.

**Rationale:** A live type tension (`owner: str` idsid vs `TeamMember`; the `Ownable.owner`
validator) means YAML idsids would not validate against the domain models. Binding at the dict level
sidesteps the tension entirely and keeps the phase's blast radius to one new module.
**Source:** 01-02-SUMMARY.md §Decisions, 01-CONTEXT.md §Module placement, swimlane.py:39-48 (NON-GOALS docstring)

### The raw YAML file text IS `Source.transcript` (YAML-as-transcript)
The transcript is `path.read_text()` verbatim, never a re-serialized `yaml.dump`. Parsing is used
ONLY to learn which scalars exist and in what file order; every value is then located in the RAW
text by a forward-only cursor.

**Rationale:** Content-addressing against a re-serialized dump would drift offsets (Pitfall 3);
addressing against the bytes the human actually wrote is the only faithful provenance.
**Source:** swimlane.py:474-482, 01-CONTEXT.md §Tracing

### A single global forward-only cursor over the whole document
One `_Minter` cursor spans the entire config (not per-lane), so duplicate values get distinct,
forward-only offsets and consumed text is never re-pointed at.

**Rationale:** Two identical scalars would both resolve to the FIRST occurrence without an advancing
cursor, mis-attributing the second's provenance (normalize.py precedent).
**Source:** swimlane.py:185-201, 01-02-SUMMARY.md §patterns-established

### `Trace.from_source` is the sole minting path; every trace `is_addressed`
The loader never hand-mints a `content_hash` or fabricates an offset; a non-locatable scalar is
routed to `unextracted[]` with a reason code, never a guessed claim.

**Rationale:** Closes Hole B upstream — no un-addressed free-pass trace ever leaves the loader, so
downstream gates inherit an already-honest input.
**Source:** swimlane.py:227-229, 01-02-SUMMARY.md, 01-CONTEXT.md §Tracing

### Read-anchored coverage, enforced by construction
`len(all_claims) + len(all_unextracted) == scalars_walked`, anchored to scalars actually READ (a
`None` slot is absent, not read). A mismatch raises `RuntimeError` inside `load_swimlanes`.

**Rationale:** The RETRO Phase-7 silent-drop lesson: anchor coverage to what was read, and enforce
the invariant in code rather than asserting it in prose.
**Source:** swimlane.py:33-37, 545-553, 01-02-SUMMARY.md

### Endpoint pairing carries the movement (`values:`) form ONLY (post-phase, `efb635a`)
The Phase-2-era `kpi_endpoints` addition was refined so a point-in-time `value:` KPI contributes NO
endpoint reference — only a `values:` list KPI pairs its start/close endpoints.

**Rationale:** A `value:` promises no movement; pairing it as a "declared-but-single endpoint" would
let the composer falsely flag point-in-time KPIs. Movement-only pairing keeps the disclosure faithful
(COMP-02).
**Source:** commit `efb635a`, swimlane.py:364-368 (inline comment)

---

## Lessons

### The abstraction guard fired on real leaks — the invariant needed teeth, not a comment
JJ's "ABSTRACT EVERYTHING" principle became a source-scanning denylist test that fails the suite on
any config-specific token in `src/`. It was proven live: planting `owner-1` into `swimlane.py` turned
the suite red, then green on revert.

**Context:** A principle stated only in prose drifts; encoded as a guard that demonstrably fires, it
holds for every future edit. The guard scans `src/` only (never `tests/`) so its own denylist literal
isn't mistaken for a leak (self-invalidation guard).
**Source:** 01-04-SUMMARY.md, tests/test_abstraction_guard.py:189-214

### Declared-but-malformed must disclose exactly like declared-but-absent
A mid-phase fix (`40976cc`) made a mapping-shaped `values:` slot (declared, but not a list of period
endpoints) emit an EMPTY display value AND a `missing[]` note — never an empty value with no note.

**Context:** Honesty is not just "route non-locatable scalars"; a slot that is present but unusable
for its declared purpose is its own disclosure class. The trap fixture and
`test_no_yaml_scalar_is_read_but_undisclosed` case (d) pin it.
**Source:** commit `40976cc`, swimlane.py:384-391, tests/test_swimlane.py:110-129

### Cross-check the coverage tally against an INDEPENDENT yardstick
The identity test does not trust the loader's own `scalars_walked`; it independently walks the parsed
doc (`_count_scalar_leaves`) and asserts equality, catching a loader that walked too few OR too many.

**Context:** A self-consistent-but-wrong internal tally would pass a naive `claims+unextracted==walked`
check. The independent count is what makes the identity meaningful.
**Source:** tests/test_swimlane.py:73-105, 01-03-SUMMARY.md

### Fixtures authored by DRIVING the live loader, then pinning its actual output
Every expected count/reason was recorded from a real loader run and then checked to be HONEST
routing, not a fixture authored around a loader gap.

**Context:** The RETRO Phase-7 lesson inverted: don't write the test to match a bug. No loader bug
surfaced; each of the 3 trap `unextracted` reasons was validated as genuinely correct.
**Source:** 01-03-SUMMARY.md §"Pinned counts and how they were validated as RIGHT"

### `isort` must run with `--profile black`; the package has no `py.typed`
Bare `isort` disagrees with the repo's black-vertical style and falsely flags existing files; and
every test importing `newsletters.*` emits an ambient `import-untyped` note because the package ships
no `py.typed` marker.

**Context:** Two recurring tooling frictions that must be understood to read gate output correctly —
neither is a defect introduced by this phase.
**Source:** 01-03-SUMMARY.md §"Concerns / notes for downstream", 01-04-SUMMARY.md §Issues

---

## Patterns

### Lazy-extra boundary clone
A one-module optional-dependency boundary (`_yaml_loader.py`) mirroring `_openpyxl_loader.py`:
in-function import, teaching `ImportError` naming the extra, `safe_load`-only parse, a
`MISSING_*_MESSAGE` constant tests assert against (no string drift).
**When to use:** Any new third-party dependency that must stay out of the bare/minimal-core install.
**Source:** src/newsletters/_yaml_loader.py, 01-PATTERNS.md, 01-01-SUMMARY.md

### Read-anchored coverage identity (excel-golden ported to YAML)
`claims + unextracted == scalars_walked`, cross-checked against an independent scalar-leaf count,
with exact ordered reason codes pinned via the loader's OWN module constants.
**When to use:** Any faithful extraction/ingest where silent drops are the failure mode.
**Source:** tests/test_swimlane.py, 01-03-SUMMARY.md, RETRO Phase-7 lesson

### Adversarial "prove-it-fires" guard halves
A guard test has two halves: the positive (every real output satisfies the predicate) and the
adversarial (a hand-built bad object is REJECTED by the SAME predicate), so the positive pass is
provably non-vacuous. Used for both Hole B (un-addressed trace) and the abstraction guard (planted
leak).
**When to use:** Any invariant whose whole value is that it catches violations.
**Source:** tests/test_swimlane.py:214-249, tests/test_abstraction_guard.py:189-214

### Trap fixture as executable contract
A tiny committed adversarial fixture packing every routing trap (anchor/alias, block scalar,
type-coercion, duplicate, quoted, mapping-shaped slot) whose exact scalar set IS the contract —
paired with a clean-path fixture.
**When to use:** Proving honest routing across a taxonomy of edge inputs.
**Source:** tests/fixtures/swimlane/module-trap.yml, 01-PATTERNS.md

### Config-tracking assertions (never freeze a magic value)
Value assertions read from the SAME parsed fixture the loader read, so tests track the config rather
than hardcoding a lane name/value (Pitfall 8) — and never assert an org-specific string.
**When to use:** Testing an abstraction that must generalize over arbitrary config.
**Source:** tests/test_swimlane.py, tests/test_swimlane_endpoints.py, 01-03-SUMMARY.md §key-decisions

---

## Surprises

### `models.py` type tension made the "obvious" binding impossible
The natural reading of the goal ("bind each lane to its `FunctionalGroup`/`Kpi`s") could not be done
by instantiating the domain models — YAML idsids fail the `Ownable.owner` validator. The ROADMAP goal
wording and the LOCKED CONTEXT decision reconcile only because "FunctionalGroup/Kpi/Objective" are
conceptual roles realized as `SectionBinding`/`KpiItem`/`Claim`, not literal `models.py` types.

**Impact:** Shaped the whole phase toward parsed-dict binding and a new display-type seam; kept
`models.py` untouched and deferred the tension to a future milestone.
**Source:** 01-CONTEXT.md §Module placement, 01-PATTERNS.md Anti-Pattern 1, swimlane.py NON-GOALS

### `sample_team/*.yml` was an orphaned shape, not a consumed input
CONTEXT pointed at `sample_team/*.yml` as "the existing YAML shape the loader generalizes over," but
the loader consumes neither it nor its schema — the phase committed its own generic
`module-x`/`module-trap` fixtures instead, and `sample_team` names appear only in the abstraction
guard's denylist (as things that must NOT leak into `src/`).

**Impact:** The real deliverable was generalization over an *arbitrary* shape, so the sample corpus
served as a naming-hazard reference rather than a fixture. No coupling to `sample_team` was created.
**Source:** 01-CONTEXT.md §Canonical References, tests/test_abstraction_guard.py:76-112

### A `value:` KPI displays a coerced value with no backing claim
In the trap fixture, `value: yes` displays as `KpiItem.value == "True"` while its scalar is routed to
`unextracted[]` (the coerced `"True"` is not verbatim in the raw text). The display string is the
real parsed value; its provenance lives in the disclosure, not in a trace — `KpiItem` has no evidence
field by design.

**Impact:** Reinforced that `KpiItem.value` is a display projection and the traced atoms live in
`SectionBinding.claims`/`unextracted`; honesty is preserved by disclosure, not by a trace on the
display string.
**Source:** live loader drive (module-trap "coerced flag" → value `"True"`, `_R_TYPE_COERCED`), swimlane.py:285-308

### A stale docstring outlived the behavior it described (found this round)
The `efb635a` movement-form-only fix changed a `value:` KPI to contribute 0 endpoints and added an
inline comment saying so — but left the `SectionBinding` docstring ("one entry for a single `value:`
KPI") and the `_bind_kpis` docstring ("the single `value:` Claim") describing the OLD behavior.

**Impact:** Documentation-only drift (runtime behavior is correct and verified), surfaced because no
test pins the `value:` → 0-endpoints behavior directly. Logged in 01-VERIFICATION Anti-Patterns for a
future doc-only fix; the loop reviews, it does not refactor.
**Source:** git diff `07f1a60`→HEAD on swimlane.py; swimlane.py:131-132 & ~331 vs 364-368; live drive
