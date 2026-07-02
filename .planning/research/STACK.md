# Stack Research — v1.1 Swim-Lane Module Report Composer

**Domain:** Config-driven, traced YAML loader + deterministic Report composer (brownfield, added to `src/newsletters/`)
**Researched:** 2026-07-02
**Confidence:** HIGH

## TL;DR (the opinionated answer)

**Add exactly one dependency: `PyYAML>=6.0.3`, behind a NEW `[config]` optional extra**, wired
through a lazy `_yaml_loader.py` boundary module that mirrors the already-hardened
`_openpyxl_loader.py` discipline. **Do not add PyYAML to core. Do not add `ruamel.yaml`. Do not add
anything for tracing** — the char-offset trace model already in `semantic.py` needs zero new code
beyond PyYAML's own source-mark metadata.

The single most important discovery: **the existing `sample_team/*.yml` files are orphaned** — no
Python in `src/` or `tests/` imports `yaml` or reads them (the only `.yml` hit in `render.py` is the
string `".yml"` inside `_SOURCE_EXTS`). So there is **no existing reader to mirror or preserve**;
this milestone introduces the first real YAML consumer. That frees the decision to be made on
principle rather than compatibility.

## The core question: stdlib-only vs `[config]` extra vs PyYAML-in-core

Three genuine options were weighed. The decision hinges on one fact and one principle:

- **Fact:** Python's stdlib has **no YAML parser** (only `json` and `tomllib`). A hand-rolled YAML
  subset parser is a footgun (the Norway problem, anchors, coercion, multiline scalars) and violates
  the repo's "no vibing" rule. Rejected outright.
- **Principle:** the hardened invariant is *"core = pydantic/typer/sqlmodel ONLY, enforced by
  import-linter + bare-install CI"* (milestone context; `pyproject.toml` L13-21). Third-party,
  non-AI deps that serve an **optional path** live behind an extra and are **lazy-imported inside a
  boundary module** (the `[excel]`/`[pptx]` pattern, `_openpyxl_loader.py`). PyYAML fits that mold.

| Option | Verdict | Why |
|--------|---------|-----|
| **stdlib-only parse** (hand-roll, or switch config to TOML/JSON) | ❌ Reject | No stdlib YAML; hand-rolling is unsafe; switching format churns the existing `sample_team` fixtures and loses YAML's human-authoring ergonomics. |
| **PyYAML in core** (4th core dep) | ⚠️ Viable alternative | Cleanest *if* compose runs inside the bare-install `newsletters build` pipeline. Cost: rewrites the "core = 3 deps" invariant the reviewer explicitly wants preserved. |
| **PyYAML behind `[config]` extra + lazy loader** | ✅ **Recommend** | Preserves the literal core-is-3-deps invariant, reuses the exact discipline CI already understands, keeps the bare spine YAML-free. |

The recommendation assumes **compose is an author-time step** (like `capture.py`): `newsletters
compose <config>` reads YAML → mints a Draft `Surface` → persists it; the render/check spine then
reads persisted artifacts and needs zero YAML. This keeps the bare-install CI job green (it never
imports `yaml`) while the composer is exercised in a separate CI step under `.[config]` — exactly how
`import-linter` runs under `.[dev]`. **If instead the team decides compose must run inside
`newsletters build` on a bare install, switch to "PyYAML in core"** (see Stack Patterns below).

## Recommended Stack

### Core Technologies (NEW for this milestone)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| PyYAML | `>=6.0.3` | Parse swim-lane / KPI / objective config YAML into dicts, and expose per-scalar **source marks** for tracing | Industry-standard, MIT, non-AI, pure-Python-capable (libyaml C-ext optional), Python ≥3.8. Its low-level node API yields exact char offsets — parse *and* trace from one dep. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| *(none)* | — | Tracing needs no new library | `Trace.from_source(source, start, end)` + PyYAML node marks cover it; see Integration. |

### What is REUSED (no new dependency)

| Existing piece | Role in the new capability |
|----------------|----------------------------|
| `Source.transcript` + `content_hash()` (`semantic.py`) | The **raw YAML file text becomes the transcript** — the content-address anchor. |
| `Trace.from_source(source, start, end)` (`semantic.py`) | Mints content-addressed, self-verifying traces from char offsets into the YAML text. **This is the whole tracing mechanism.** |
| `Claim` / `KpiItem` / `ClaimsBlock` / `KpiStripBlock` (`semantic.py`) | Every loaded value becomes one of these; delta computed at compose time into `KpiItem.delta`. |
| `Surface.missing[]` (`semantic.py`) | Honesty routing for unsubstantiated / unresolvable config values. |
| `FunctionalGroup` / `Kpi` / `Objective` / `TeamMember` (`models.py`) | The typed targets the loader binds config onto (validation, e.g. `ensure_owners_are_team_members`, runs for free). |
| `FreeLocator` / a future `ConfigLocator` (`locators.py`) | Anchor kind for "this claim came from file X". Reuse `FreeLocator` v1; a `ConfigLocator{path,key_path}` is a clean future addition to the union (stubbed already in `locators.py`). |
| R-NNN ledger (`site.py`) | Stable IDs for the composed report — unchanged. |

## Installation

```bash
# Core is UNCHANGED — still pydantic / typer / sqlmodel only:
pip install .

# The new config path (author-time compose + tests that exercise it):
pip install ".[config]"          # brings PyYAML
pip install ".[config,test]"     # config path + pytest, for the new CI step
```

`pyproject.toml` change (mirrors the `excel`/`pptx` stanzas verbatim in spirit):

```toml
# YAML config loader dep (v1.1). PyYAML is NON-AI, MIT, pure-Python-capable, spec-named for the
# swim-lane config path. It lives behind an extra and is lazy-imported inside the config loader only
# (mirror the [ai]/[excel]/[pptx] discipline), so bare `pip install .` still runs the deterministic
# capture -> review -> render spine with zero PyYAML and zero AI. Use yaml.safe_load ONLY.
config = ["PyYAML>=6.0.3"]
```

## Integration with the existing discipline (the load-bearing part)

**1. Lazy boundary module — copy `_openpyxl_loader.py` exactly.** Create
`src/newsletters/config/_yaml_loader.py` (or `adapters/_yaml_loader.py`) with:
- **No top-level `import yaml`.** The import lives inside `_load_yaml()`.
- A `MISSING_PYYAML_MESSAGE` constant naming `pip install '.[config]'` and stating the spine runs
  without it (so a test can assert the message without string drift).
- **`yaml.safe_load` ONLY** — never `yaml.load` (the latter can construct arbitrary Python objects;
  a hard "faithful, not suggestive / no surprises" boundary).
- Return typed as `Any` (PyYAML 6.x ships inline types, but keep the boundary opaque and do **not**
  add a `types-*` package — mirror the openpyxl Any-typing decision).

**2. import-linter (`.importlinter`, PKG-04): no change needed, but consider one guard.** The
`forbid-ai-in-core` contract only forbids AI packages, so PyYAML is untouched. To keep the
"lazy boundary only" property *enforced* (not vibed), optionally add a small `forbidden` contract:
`source_modules = newsletters` / `forbidden_modules = yaml`, then whitelist the single loader module
— OR (simpler, matching the openpyxl precedent) rely on the bare-install grep-style test. The
openpyxl boundary is guarded by `tests/test_ai_optional.py` asserting grep-count 0 for top-level
`import openpyxl`; add the analogous assertion for `import yaml`.

**3. Bare-install CI (PKG-03): stays green untouched.** The `bare-install` job installs `.[test]`
(no `[config]`) and runs `newsletters build`. As long as **compose is author-time** and `build`
renders persisted surfaces, `import newsletters` and the full pipeline never touch `yaml`. Add a
**new CI step/job** that installs `.[config,test]` and runs the composer + its tests (mirror the
`import-linter` job that installs `.[dev]`). The belt-and-suspenders "no AI importable" assertion is
unaffected.

**4. Tracing — the char-offset insight, made exact.** The YAML text *is* the `Source.transcript`.
Two ways to get offsets, in order of fidelity:
- **Preferred — PyYAML source marks.** `yaml.compose(text)` (or a mark-recording `SafeLoader`
  subclass) returns a node graph where **every scalar node carries `start_mark.index` and
  `end_mark.index`** — absolute character offsets into the raw text. Feed those straight into
  `Trace.from_source(source, start_mark.index, end_mark.index)`. Exact, faithful, no heuristics.
- **Fallback — `str.find`.** For a simple flat scalar, locate the raw token in the transcript with
  stdlib string search. **Caveat:** match the *raw* token as written, not PyYAML's coerced Python
  value — `safe_load` strips quotes, folds multiline scalars, and coerces `2025-05-05...` to a
  `datetime` and applies bareword rules. A coerced value may not appear verbatim; the node-mark
  path sidesteps this entirely, which is the second reason to prefer PyYAML over any
  stdlib/hand-rolled approach.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PyYAML behind `[config]` extra | **PyYAML in core** (4th core dep) | If compose must run inside `newsletters build` on a bare install, or if the team decides config is so central it belongs beside `sqlmodel`. Justified precedent: `sqlmodel` is a non-AI core dep kept because `models.py` uses it. Trade-off: rewrites the "core = 3 deps" invariant statement. |
| PyYAML behind `[config]` extra | **Switch config format to TOML (`tomllib`, stdlib)** | If the team wants **zero** new deps and is willing to migrate `sample_team/*.yml`. `tomllib` is stdlib in 3.11+, but it is read-only, less pleasant for nested OKR trees, and gives no per-value source marks (tracing falls back to `str.find`). Reject unless dep-count is an absolute constraint. |
| PyYAML | **ruamel.yaml** | Only if the milestone needed **round-trip editing / comment preservation** (writing YAML back). It does not — the loader is read-only. ruamel is heavier and its round-trip API is overkill here. |

## What NOT to Use / What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `yaml.load(...)` (unsafe loader) | Can construct arbitrary Python objects from input — a trust/security hole and an editorializing surface | `yaml.safe_load` / `yaml.compose` only |
| PyYAML in core (as the default choice) | Grows the deliberately-minimal core; contradicts the preserved "core = pydantic/typer/sqlmodel" invariant | `[config]` extra + lazy loader |
| `ruamel.yaml` | Round-trip/comment features unused; heavier | PyYAML |
| `types-PyYAML` stub package | PyYAML 6.x ships inline types; a stub is redundant, and the boundary is intentionally `Any` | Type the loader return as `Any` (openpyxl precedent) |
| A new tracing library / offset framework | `Trace.from_source` + PyYAML node marks already give exact content-addressed traces | Reuse `semantic.py` |
| A stored `start`/`baseline` field on `Kpi` | Milestone decision: Δ is **computed at compose time** into `KpiItem.delta`; the model stays untouched | Compute delta in the composer |
| Hardcoding lane/module/owner names in `src/` | Violates the milestone's fundamental principle; a test must fail on fixture-name leakage | Everything specific lives in the YAML config |

## Stack Patterns by Variant

**If compose is an author-time step (RECOMMENDED — mirrors `capture.py`):**
- PyYAML behind `[config]`; lazy `_yaml_loader.py`; new `.[config,test]` CI step.
- Bare-install `newsletters build` renders persisted surfaces, never imports `yaml` → PKG-03 green.
- Because: keeps core literally 3 deps and reuses the hardened extras discipline.

**If compose must run inside `newsletters build` on a bare install:**
- Move PyYAML into `dependencies` (core, 4th dep) — the `sqlmodel` precedent.
- Update the milestone's "core = 3 deps" invariant statement and the bare-install job to install it.
- Because: bare-install exercises the composer, so its parser must be present bare.

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `PyYAML>=6.0.3` | Python 3.12 (repo target) | `requires_python >=3.8`; latest is 6.0.3, MIT. Pure-Python fallback always works; libyaml C-extension is an optional speedup, not required. |
| `PyYAML` | pydantic 2 / typer / sqlmodel | No interaction — PyYAML produces plain dicts that pydantic validates into `FunctionalGroup`/`Kpi`/`Objective`. |
| `PyYAML` | import-linter `forbid-ai-in-core` | Not an AI package; contract unaffected. |

## Sources

- Local repo audit (HIGH): `pyproject.toml`, `src/newsletters/semantic.py`, `models.py`,
  `locators.py`, `adapters/_openpyxl_loader.py`, `.importlinter`, `.github/workflows/ci.yml`,
  `sample_team/*.yml` — confirmed no existing `yaml` importer; confirmed the extras + lazy-loader
  discipline and the char-offset `Trace.from_source` model.
- PyPI PyYAML metadata (HIGH): latest 6.0.3, license MIT, `requires_python >=3.8` —
  https://pypi.org/pypi/PyYAML/json
- PyYAML API (HIGH, standard docs): `safe_load`, `compose`, and node `start_mark`/`end_mark`
  (`.index`) offsets — https://pyyaml.org/wiki/PyYAMLDocumentation

---
*Stack research for: config-driven traced YAML loader + Report composer (v1.1)*
*Researched: 2026-07-02*
