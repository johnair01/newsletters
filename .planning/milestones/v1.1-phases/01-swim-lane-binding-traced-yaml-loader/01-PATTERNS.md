# Phase 1: Swim-lane binding + traced YAML loader - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 8 (2 source, 1 helper, 1 packaging, 3 test suites, 1 fixture set)
**Analogs found:** 8 / 8 (every file has a strong live analog in-repo)

> Every new file this phase creates has a direct, recent, load-bearing precedent already merged
> on this branch. This is a **copy-the-precedent** phase, not a greenfield one. The planner should
> anchor each plan's actions to the file:line excerpts below, not to RESEARCH.md abstractions.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/newsletters/swimlane.py` | loader (top-level module) | file-I/O → transform (read-only ingest + verbatim minting) | `src/newsletters/worksurface.py` (`capture_files`) + `adapters/normalize.py` (cursor mint) | exact (two-analog composite) |
| `src/newsletters/_yaml_loader.py` *(or inline in swimlane.py)* | utility (lazy-extra boundary) | transform (guarded import) | `src/newsletters/adapters/_openpyxl_loader.py` | exact |
| `tests/fixtures/<generic-module>.yml` (+ trap fixture) | config/test data | file-I/O (byte-reproducible committed fixture) | `sample_team/*.yml` (shape) + `tests/fixtures/xlsx/` (committed-fixture discipline) | exact |
| `tests/test_swimlane.py` (trap + coverage-identity + adversarial + determinism) | test | file-I/O + transform | `tests/test_worksurface.py` + `tests/test_excel_golden.py` | exact |
| `pyproject.toml` `[config]` extra | config | n/a | existing `[excel]` / `[pptx]` extras | exact |
| `tests/test_ai_optional.py` (extend: `[config]`/yaml unreachable) | test | transform (subprocess boundary probe) | existing `[excel]` / `[pptx]` blocks in same file | exact (same file, add a parallel block) |

**Read-only constraint reminder for the planner:** `swimlane.py` performs `Path.read_text` ONLY
(mirror `capture_files`). No writes to the scanned tree, no network, no `datetime.now()`.

---

## Pattern Assignments

### `src/newsletters/swimlane.py` (loader, file-I/O → transform)

This module is a **composite** of two proven precedents:
1. `worksurface.capture_files` — the read-only, content-addressed `Source` ingest edge policy.
2. `adapters/normalize.py` — the forward-only cursor verbatim-mint-or-route-to-unextracted loop.

**Analog A — `src/newsletters/worksurface.py`**

*Module-docstring rationale to mirror (worksurface.py:7-35):* it documents WHY a hand-authored,
file-backed corpus is a top-level module (not `adapters/`, not `dogfood.py`) and states the
READ-ONLY / CONTENT-ADDRESSABLE / DETERMINISTIC / AI-FREE contract. `swimlane.py` should open with
the same four-property contract, adapted to "config YAML → Source(transcript=file text)".

*Source construction + edge policy (worksurface.py:100-119)* — copy verbatim, swap `context`:
```python
root_path = (root or Path.cwd()).resolve()
sources: list[Source] = []
for raw in sorted(str(p) for p in paths):
    candidate = Path(raw)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(root_path).as_posix()  # ValueError if escapes root
    sources.append(
        Source(
            id=rel,
            context=f"module-config:{rel}",              # swimlane's context stamp
            transcript=resolved.read_text(encoding="utf-8"),  # READ ONLY
            timestamp=EPOCH_ZERO,
        )
    )
sources.sort(key=lambda s: s.id)
```
Edge policy to inherit verbatim (worksurface.py:85-98): missing file → raise `FileNotFoundError`;
non-UTF-8 → raise `UnicodeDecodeError` (no lossy decode); path escaping root → `ValueError`. Never
skip-silently — "a curated list cites real files".

*Verbatim-or-missing minting device (worksurface.py:196-221)* — the shape the loader reuses, but
note the honesty routing here goes to `SectionBinding.missing` / `unextracted[]`, not a Surface:
```python
start = src.transcript.find(claim.text) if src is not None else -1
if src is not None and start >= 0:
    claim.evidence[0] = Trace.from_source(
        src, start, start + len(claim.text), locator=FreeLocator(text=src.id)
    )
    kept.append(claim)
else:
    report.missing.append(claim.text)  # NEVER fabricate an offset
```

**Analog B — `src/newsletters/adapters/normalize.py`** (the cursor semantics — CONTEXT decision
"Locate values with a forward-only cursor")

*The forward-only cursor mint loop (normalize.py:88-117)* — this is the exact algorithm the loader
walks each scalar through. Copy the cursor discipline; route non-locatable scalars honestly:
```python
transcript = source.transcript
claims, unextracted, cursor = [], [], 0
for unit in units:
    idx = transcript.find(unit, cursor)
    if idx == -1:
        unextracted.append(
            Unextracted(locator=FreeLocator(text=unit[:_PREVIEW_CHARS]),
                        reason=_NOT_LOCATABLE_REASON)
        )
        continue
    end = idx + len(unit)
    trace = Trace.from_source(source, idx, end)   # SOLE minting path
    claims.append(Claim(text=unit, evidence=[trace], confidence=0.0))
    cursor = end   # advance -> duplicates get DISTINCT, forward-only offsets
```
*Why the cursor matters (normalize.py:17-20, docstring):* two identical scalars (the trap fixture's
duplicate values) would both resolve to the FIRST occurrence without a forward-advancing cursor —
giving the second claim wrong provenance. The cursor is the mechanism that makes duplicate/quoted/
coerced scalars route honestly instead of mis-attributing.

*Reason-code + content-preview convention (normalize.py:42-47):* `_PREVIEW_CHARS = 60` truncated
content anchor + a fixed `_NOT_LOCATABLE_REASON` constant. Mirror the `_R_*` naming (see
`test_excel_golden.py:83-87` `R_FORMULA_NO_CACHE`) for swimlane's reason codes
(e.g. `_R_NOT_VERBATIM`, `_R_TYPE_COERCED`, `_R_ANCHOR_ALIAS`, `_R_BLOCK_SCALAR`).

**Imports pattern** (mirror worksurface.py:37-56, minus render/site — the loader is a near-leaf):
```python
from __future__ import annotations
from pathlib import Path
from .adapters._timestamps import EPOCH_ZERO
from .locators import FreeLocator
from .semantic import Claim, KpiItem, Source, Trace
# yaml is NOT imported at top level — it comes via the lazy boundary (see _yaml_loader)
```
Import-edge constraint (RESEARCH `.importlinter:23-36`): `yaml` is not on the forbidden-AI list, so
`lint-imports` stays green — but the `[config]`-extra/lazy discipline still forbids a top-level
`import yaml` (bare-install gate). Do NOT import `distill/`, `render`, `site`, or any AI package.

**`SectionBinding` shape** (Claude's discretion, kept minimal/generic — RESEARCH question d):
a small AI-free Pydantic `BaseModel`: `{ heading: str, kpi_items: list[KpiItem], claims: list[Claim],
missing: list[str] }`. Reuse the existing `KpiItem` (semantic.py:333-337, fields `label/value/
delta/dir`) and `Claim` (semantic.py:187-197) — add NO new block type and do NOT modify `models.py`.
Bind at the **parsed-dict level** (never instantiate `FunctionalGroup`/`Kpi` — see Anti-Pattern 1).

**Timestamp** (never `now()`): `Source.timestamp=EPOCH_ZERO` directly, or via
`deterministic_timestamp(None)` (`adapters/_timestamps.py:42,45-61`). `EPOCH_ZERO` is the honest
"no intrinsic date" sentinel; content_hash excludes timestamp (_timestamps.py:21-24), so this cannot
perturb any claim address.

---

### `src/newsletters/_yaml_loader.py` (utility, lazy-extra boundary)

**Analog:** `src/newsletters/adapters/_openpyxl_loader.py` — copy beat-for-beat.

*Module docstring contract (_openpyxl_loader.py:1-15):* state that `yaml` is NOT AI (import-linter
unaffected) but the minimal-core invariant still demands a bare `pip install .` (no `[config]`) can
`import newsletters` and run the spine with zero PyYAML; achieved by never importing yaml at module
top level.

*Teaching-message constant + lazy import fn (_openpyxl_loader.py:30-59):*
```python
MISSING_YAML_MESSAGE = (
    "The module-config loader requires the optional 'PyYAML' dependency. "
    "Install it with: pip install '.[config]'  (or: pip install newsletters[config]). "
    "The deterministic spine runs without it — PyYAML is needed only for YAML config loading "
    "(AI-optional / minimal-core: third-party deps live behind extras)."
)

def _load_yaml() -> Any:
    try:
        import yaml  # noqa: PLC0415  (lazy on purpose, optional [config] extra)
    except ImportError as exc:
        raise ImportError(MISSING_YAML_MESSAGE) from exc
    return yaml
```
**CRITICAL — CONTEXT decision:** the parse call is `yaml.safe_load` ONLY, never `yaml.load`
(config files are data, not code). Wrap `safe_load` in the loader function; expose
`MISSING_YAML_MESSAGE` as a module constant so tests assert against it without string drift
(mirrors `_openpyxl_loader.py:29-30`, `test_ai_optional.py:361`).

*Placement note (Claude's discretion):* CONTEXT says "`_yaml_loader.py`-style boundary inside the
swimlane module only." Two acceptable shapes — (a) a sibling helper `src/newsletters/_yaml_loader.py`
directly mirroring `_openpyxl_loader.py`, or (b) the same `_load_yaml()`/`MISSING_YAML_MESSAGE`
defined privately inside `swimlane.py`. Prefer (a) for a clean test target and to mirror the
established `_*_loader.py` naming; either keeps the bare-install gate satisfiable.

---

### `tests/fixtures/<generic-module>.yml` + trap fixture (config/test data)

**Analog A — shape:** `sample_team/q2_okrs.yml`, `functional_groups.yml`, `team_members.yml`.
The loader must generalize over THIS shape without hardcoding any of it:
- `functional_groups.yml:1-9` — `functional_groups: [{name, description, module, owner, team_members:[idsid...]}]`
- `q2_okrs.yml:3-8` — `kpis: [{title, description, status, owner, ...}]` + `objectives: {idsid: [...]}`
- `team_members.yml:1-6` — `team_members: [{name, title, bio, idsid, image_url}]`

Note the **live type tension the loader must sidestep** (Anti-Pattern 1): `owner:` and
`team_members:` carry string idsids (`functional_groups.yml:5-9`), which will NOT validate against
`models.FunctionalGroup` — so bind at dict level.

**Fixture naming discipline (CONTEXT + LANE-03):** generic ids ONLY (`lane-a`, `owner-1`,
`module-x`) or the seed's fabricated scheme. Nothing resembling real org/tool/metric nomenclature.
The worked `module-a` example is Phase 3; this phase commits only a small generic fixture.

**Analog B — committed byte-reproducible fixture discipline:** `tests/test_excel_golden.py:1-35`
documents "tiny, committed, byte-reproducible fixtures authored by `_author_fixtures.py`". For YAML,
the fixture is just a committed `.yml` (no authoring script needed), but adopt the same principle: a
small, hand-checked fixture whose EXACT scalar set is the executable contract.

**Trap fixture (CONTEXT testing decision):** must contain — duplicate values, quoted scalars,
type-coerced forms (`yes`, `1.0`, dates), block scalars, anchors/aliases — so the test proves each
either verbatim-locates or routes to `unextracted[]` with a reason code. This is the direct analog
of the excel golden's adversarial fixtures (`formula_no_cache`, `error_cell`, `chart_or_image` —
`test_excel_golden.py:26-29`).

---

### `tests/test_swimlane.py` (test — trap, coverage-identity, adversarial, determinism)

**Analog A — `tests/test_worksurface.py`**

*Read-only + content-addressed + determinism structure (test_worksurface.py:70-118):* the three
locked assertions to replicate — (a) transcript is verbatim file text, (b) `Trace.from_source` over
a real span round-trips (`tr.span == needle`, `tr.is_addressed`, `tr.content_hash ==
src.content_hash()`, `not tr.is_stale_against`), (c) two loads are byte-identical via
`model_dump_json()`:
```python
first = load(...); second = load(...reversed inputs...)
assert [s.model_dump_json() for s in first] == [s.model_dump_json() for s in second]
```
Copy the byte-identical-double-load determinism test (test_worksurface.py:111-118) directly.

*Adversarial "prove it blocks, not just passes" pattern (test_worksurface.py:373-427):* the Phase-7
lesson made executable — a crafted blocked surface proves the gate FIRES. For swimlane, the
adversarial test is CONTEXT's "an un-addressed trace emitted by the loader is CAUGHT": assert every
emitted trace `is_addressed is True` (closes Hole B), and craft a case that WOULD produce an
un-addressed trace to prove the test catches it.

**Analog B — `tests/test_excel_golden.py`** (the read-anchored coverage identity)

*The zero-silent-drops accounting identity (test_excel_golden.py:8-14, 62-78):* this is the exact
model for `test_no_yaml_scalar_is_read_but_undisclosed`:
```python
# ADAPT-06 identity, ported to YAML scalars:
#   len(claims) + len(unextracted) == scalars_walked
class Expected:
    @property
    def total_units(self) -> int:
        return self.n_claims + len(self.unextracted_reasons)
```
CONTEXT states the identity verbatim: `len(claims) + len(unextracted) == scalars walked`, anchored
to what was READ (RETRO Phase-7 lesson). Pin the EXACT ordered reason strings per trap-fixture
scalar (mirror `test_excel_golden.py:83-90` `R_*` constants + `EXPECTED` dict), derived by driving
the LIVE loader — never assumed.

*Faithful-span assertion (test_excel_golden.py:16-17):* `claim.text == trace.span` AND re-slicing
`transcript[trace.start:trace.end]` reproduces it — port directly.

**Abstraction-guard test (CONTEXT LANE-03):** grep-style test over `src/newsletters/` that fails if
any fixture-specific name (`lane-a`, `module-x`, an owner id, or any sample_team name) appears in
source. Closest in-repo precedents for the "scan source text and assert absence" shape:
`test_ai_optional.py:284-304` (`test_openpyxl_loader_has_no_toplevel_openpyxl_import` reads the
module text and asserts a forbidden pattern is absent) — same mechanic, different needle set.

---

### `pyproject.toml` — add the `[config]` extra (config, MODIFIED)

**Analog:** the existing `[excel]` / `[pptx]` extra declarations (pyproject.toml:30-43).
```toml
# PyYAML (>=6.0.3) — module-config loader dep. NON-AI, pure-data parse (safe_load only). Lives
# behind an extra + lazy-imported inside the swimlane loader only (mirror [excel]/[pptx]), so bare
# `pip install .` runs the deterministic spine with zero PyYAML and zero AI.
config = ["PyYAML>=6.0.3"]
```
Do NOT add yaml to `[project] dependencies` (that would break the bare-install gate — this differs
from an early RESEARCH note that suggested core deps; CONTEXT LOCKED it to a `[config]` extra).

---

### `tests/test_ai_optional.py` — extend for the `[config]`/yaml boundary (test, MODIFIED)

**Analog:** the `[excel]` block already in this file (test_ai_optional.py:261-394) — add a parallel
`[config]`/yaml block. Port each test one-for-one:

| Excel test (copy from) | New yaml test |
|------------------------|---------------|
| `test_excel_extra_declared` (271-281) | `test_config_extra_declared` — assert `config` extra exists, contains PyYAML only, not AI |
| `test_openpyxl_loader_has_no_toplevel_openpyxl_import` (284-304) | assert `_yaml_loader.py` (or swimlane.py) has zero top-level `import yaml` / `from yaml` |
| `test_adapters_package_imports_without_openpyxl` (307-337) | `import newsletters.swimlane` succeeds with yaml blocked via a `sys.meta_path` finder |
| `test_loader_raises_teaching_error_without_openpyxl` (340-374) | `_load_yaml()` raises teaching `ImportError` naming `[config]` when yaml blocked |
| `test_loader_returns_module_when_openpyxl_present` (377-394) | `_load_yaml()` returns the module in the dev env; skip on bare env |

The meta-path-finder block-then-subprocess idiom (test_ai_optional.py:315-337) is the exact recipe —
swap `openpyxl` → `yaml`, `_openpyxl_loader` → `_yaml_loader`, `[excel]` → `[config]`. Also mirror
`test_worksurface_import_loads_no_ai_module` (test_ai_optional.py:234-258) for a
`test_swimlane_import_loads_no_ai_module` guard proving the new top-level module stays AI-free.

---

## Shared Patterns

### Content-addressing (the SOLE trace-minting path)
**Source:** `src/newsletters/semantic.py:126-170` (`Trace.from_source`)
**Apply to:** every value the loader mints.
`Trace.from_source(source, start, end)` validates `0 <= start <= end <= len(transcript)` BEFORE
slicing (raises a teaching `ValueError` on a bad range), pins `content_hash = source.content_hash()`,
and stores `span = transcript[start:end]`. NEVER hand-mint a `content_hash` or fabricate an offset
(worksurface.py:25-26 calls hand-minting an anti-pattern). Every emitted trace must have
`is_addressed is True` (semantic.py:172-175) — CONTEXT's Hole-B closure.

### Read-only, deterministic file ingest
**Source:** `src/newsletters/worksurface.py:100-119` + `adapters/_timestamps.py:42`
**Apply to:** `swimlane.py` Source construction.
`Path.read_text("utf-8")` only; `sorted()` inputs; `EPOCH_ZERO` timestamp; posix-relpath `id`. Same
byte-stability property `test_worksurface.py:319-330` proves (SITE-06).

### Honest routing (faithful, not suggestive)
**Source:** `adapters/normalize.py:94-105` + `worksurface.py:216-220`
**Apply to:** every scalar that does not verbatim-locate.
Non-locatable → append to `missing[]`/`unextracted[]` with a fixed reason code + truncated content
preview (`_PREVIEW_CHARS = 60`, content anchor NOT ordinal index — `locators.py:17-19`). Never a
fabricated claim, never a guessed offset.

### Lazy optional-dependency boundary
**Source:** `src/newsletters/adapters/_openpyxl_loader.py:38-59` + the `[excel]` tests
(`test_ai_optional.py:261-394`)
**Apply to:** the yaml boundary + its bare-install tests.
Import inside a function only; teaching `ImportError` naming the extra; `safe_load` only.

### Reason-code naming convention
**Source:** `adapters/normalize.py:47` (`_NOT_LOCATABLE_REASON`) + `test_excel_golden.py:83-87`
(`R_FORMULA_NO_CACHE`, `R_ERROR_CELL`, `R_CHART`)
**Apply to:** swimlane's unextracted reason codes — module-level `_R_*` constants asserted verbatim
by the coverage-identity test (no inline string duplication → no drift).

---

## No Analog Found

None. Every file has a strong in-repo precedent. Two deliberate *differences* from the closest
analogs the planner must hold (not gaps, but divergences):

| Aspect | Analog behavior | This phase's divergence |
|--------|-----------------|--------------------------|
| yaml dependency placement | RESEARCH ARCHITECTURE §(a) suggested `[project] dependencies` | CONTEXT LOCKED it to a `[config]` extra (bare install stays yaml-free) — follow CONTEXT, not that one RESEARCH line |
| honesty sink | `worksurface` routes to `Surface.missing[]` | swimlane routes to `SectionBinding.missing[]` / `unextracted[]` (no Surface this phase — composition is Phase 2) |
| model binding | adapters build Sources from a modality | swimlane binds at the **parsed-dict level**, never instantiating `FunctionalGroup`/`Kpi` (models.py untouched — live type tension, Anti-Pattern 1) |

---

## Metadata

**Analog search scope:** `src/newsletters/` (worksurface, adapters/normalize, adapters/_timestamps,
adapters/_openpyxl_loader, semantic), `tests/` (test_worksurface, test_excel_golden,
test_ai_optional), `sample_team/`, `pyproject.toml`, `.importlinter`.
**Files scanned:** 12 read in full or in targeted ranges.
**Pattern extraction date:** 2026-07-02
</content>
</invoke>
