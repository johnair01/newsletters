# Phase 1: Distill Socket Contract - Research

**Researched:** 2026-06-14
**Domain:** Python ports-and-adapters contract design (typed Pydantic v2 Protocol + registry + conformance suite), zero-AI deterministic spine
**Confidence:** HIGH (the entire phase is in-repo Python design over an already-merged, fully-read spine; no new external deps; standard library + Pydantic patterns)

## Summary

Phase 1 is a **pure-design, zero-dependency** phase: it formalizes the one boundary (`DistillPort`) that every distill backend speaks through, ships a backend **registry**, a deterministic **`ManualBackend`** wrapping the existing `capture.capture_session()`, the **coverage / `unextracted[]`** contract, and a **conformance suite** (SOCK-01..05). Nothing here installs an external package; everything is `stdlib + Pydantic v2`, which is exactly what the AI-optional-core hard rule requires. The work is overwhelmingly a matter of choosing the right *typed shapes* and the right *seams* so Phases 3–7 (provenance, faithfulness gate, format adapters) and the v2 AI track drop in without breaking the contract.

The repo already gives us almost everything to copy: `src/newsletters/templates.py` is a working **registry exemplar** (a module-level `dict` + `register()`/`get_template()`/`all_templates()` — `templates.py:165-184`), and `src/newsletters/semantic.py` already defines the discriminated-union pattern we should reuse for the `Locator` union (`Block = Annotated[Union[...], Field(discriminator="kind")]` — `semantic.py:273-287`). The existing `Trace.locator` is a bare `str` (`semantic.py:57-61`); Phase 1 must *widen* it to a structured, discriminated `Locator` union in a **backward-compatible** way (string stays valid via a `FreeLocator` variant) so the merged Rev1 tests and `capture_session()` keep passing.

**Primary recommendation:** Add a new `src/newsletters/distill/` package (`ports.py`, `registry.py`, `manual.py`, `coverage.py`, `locators.py`) plus a `conformance.py`. Define `DistillPort` as a `@runtime_checkable typing.Protocol` with one method `distill(sources: list[Source]) -> DistillationResult`, where `DistillationResult` wraps the existing `Distillation` and adds a `Coverage` manifest (so `Distillation` itself stays untouched and Rev1-compatible). Widen `Trace.locator` to a discriminated `Locator` union with a backward-compatible `FreeLocator` default. Leave a deterministic, no-AI **entailment seam** (`FaithfulnessCheck` Protocol) that Phase 3 fills with span-containment — in Phase 1 it defaults to a permissive/structural check. Build the conformance suite as a parametrized pytest module any backend can be run through (SOCK-05).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `DistillPort` contract (the socket) | Core domain (`core`/`distill` import-light) | — | The pipeline depends on the Protocol only; ARCHITECTURE.md makes this the central boundary. |
| Backend registry (name → backend) | Core domain | — | Pure lookup; mirrors the existing `templates.py` registry — no heavy deps. |
| `ManualBackend` | Adapter (deterministic, no AI) | Core (`capture.py`) | Wraps `capture_session()`; first-class path, not a fallback (ARCHITECTURE.md Component table). |
| Coverage manifest / `unextracted[]` | Core domain (typed model) | Adapter (populates it) | The *contract* is core; each backend *reports* into it. |
| `Locator` union (verbatim span) | Core domain (typed model) | Adapter (constructs variants) | The trust anchor must be a core type so every backend and the renderer speak it. |
| Entailment / faithfulness seam | Core domain (Protocol) | Phase 3 (deterministic impl) | Phase 1 leaves the seam; Phase 3 fills the no-AI span-containment check. |
| Conformance suite | Test tier | — | Verifies any registered backend honors the contract (SOCK-05). |
| Review gate / publish | Core domain (`semantic.py`, already built) | — | Untouched — the socket emits a `Distillation`; it must NOT add an auto-publish path. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `typing` (`Protocol`, `runtime_checkable`, `Annotated`, `Literal`) | 3.12 | The socket contract + discriminated unions | `typing.Protocol` is the canonical structural-interface mechanism; ARCHITECTURE.md Pattern 1 prescribes it. [CITED: .planning/research/ARCHITECTURE.md:130-162] |
| Pydantic v2 | `>=2` (already a core dep) | All typed models: `Coverage`, `Locator` union, `DistillationResult` | The whole project's typed-auditable contract is Pydantic; reuse the existing discriminated-union idiom from `semantic.py:273-287`. [VERIFIED: src/newsletters/semantic.py:33] |
| `importlib.metadata` (stdlib) | 3.12 | *Optional* entry-point backend discovery (ARCHITECTURE.md Pattern 2) | Lets third-party packages register a backend with no core change. **Recommend deferring** the entry-point layer; a module-level dict registry (the `templates.py` shape) is sufficient and simpler for Phase 1. [CITED: .planning/research/ARCHITECTURE.md:164-184] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | (in `[dev]`/`[test]`) | The conformance suite (SOCK-05) + phase tests | Parametrize over registered backends; mirror the existing `tests/test_semantic.py` style. [VERIFIED: tests/test_semantic.py:1-30] |
| mypy | configured (`pyproject.toml [tool.mypy] python_version="3.12"`) | Static check that backends satisfy the Protocol shape | ARCHITECTURE.md Pattern 1 trade-off: Protocols fail at call time, so a mypy gate catches malformed backends statically. [VERIFIED: pyproject.toml] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `typing.Protocol` (structural) | `abc.ABC` base class (nominal) | ABC forces backends to import + inherit a base class; Protocol lets an operator drop in a backend by *shape* only. ARCHITECTURE.md explicitly chose Protocol. Keep Protocol. [CITED: .planning/research/ARCHITECTURE.md:130-142] |
| Module-level dict registry (the `templates.py` shape) | `importlib.metadata` entry points | Entry points enable third-party plugin packages but add runtime-discovery failure modes and pyproject wiring. For Phase 1's in-tree backends, the dict registry is simpler and proven in-repo. Add entry points later (a non-breaking extension) if/when a fork ships an out-of-tree backend. |
| Wrap `Distillation` in a new `DistillationResult` (coverage alongside) | Add `coverage` field directly onto `Distillation` | Adding a field to `Distillation` mutates a Rev1 type used throughout `semantic.py`/`render.py`/tests. A wrapper keeps `Distillation` stable AND lets `unextracted[]` live next to `missing[]` cleanly (D-05). **Decide in plan-check** — see Open Question 1. |

**Installation:**
```bash
# No new runtime dependencies. Phase 1 is stdlib + Pydantic v2 (already a core dep).
# Ensure the dev/test toolchain is present in the active interpreter (see Environment Availability):
pip install -e ".[dev,test]"
```

**Version verification:** No external packages are added by this phase, so there is nothing to verify against PyPI. The only stack note is the **interpreter version** (see Environment Availability — the project targets Python 3.12; `StrEnum` and modern `typing` features are used in `semantic.py`).

## Package Legitimacy Audit

> Phase 1 installs **no external packages**. It uses only the Python standard library and Pydantic v2, which is already a declared core dependency (`pyproject.toml [project].dependencies = ["pydantic>=2", ...]`).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| pydantic (already present) | PyPI | mature | very high | github.com/pydantic/pydantic | OK | Pre-existing core dep — not introduced by this phase |
| (none added) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*No package-legitimacy gate run was required because no new package is introduced. The AI-optional-core hard rule is satisfied trivially: nothing in this phase can make an AI import reachable from core.*

## Architecture Patterns

### System Architecture Diagram

```
   author-by-hand          generic file extraction        agentic interview
   (BUILT in Phase 1)        (Phases 4–7, future)          (v2 AI track, future)
        │                          │                              │
        ▼                          ▼                              ▼
   WorkSession +              raw file bytes               interview turns
   Decision[]                 (.eml/.xlsx/.pptx)           (human/code/work)
        │                          │                              │
        │  capture_session()       │ extract→RawExtraction        │ lazy-import LLM
        ▼                          ▼  (+Locator)                  ▼  INSIDE method only
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  DistillPort (Protocol)   name: str   distill(sources)->DistillationResult  │
 │     ── the ONE boundary; the pipeline never knows which backend ran ──      │
 └───────────────────────────────────────────────────────────────────────────┘
        │ registry.resolve("manual"|"email"|"ai") → backend instance
        ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  [FaithfulnessCheck seam]  ── Phase 1: deterministic/permissive default ──  │
 │   Phase 3 fills: each Claim's text must be span-contained in its Trace span │
 └───────────────────────────────────────────────────────────────────────────┘
        ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  DistillationResult                                                         │
 │    .distillation : Distillation  (claims[]+Trace, missing[] = UNPROVABLE)   │
 │    .coverage     : Coverage      (unextracted[] = UNREADABLE,  +cost/effort)│
 └───────────────────────────────────────────────────────────────────────────┘
        ▼   serialize losslessly to/from JSON sidecar (D-04: model_dump_json / model_validate_json)
 ┌───────────────────────────────────────────────────────────────────────────┐
 │  EXISTING, UNTOUCHED:  Distillation → Surface(Draft) → Review gate          │
 │  (Draft › In Review › Published, recorded reviewer).  NO auto-publish seam. │
 └───────────────────────────────────────────────────────────────────────────┘
```

The single load-bearing boundary is `DistillPort`. Manual (built now), format-adapter (4–7), and AI (v2) backends all satisfy the same shape; downstream review/render/promote stay backend-agnostic. [CITED: .planning/research/ARCHITECTURE.md:61-63, 294-326]

### Recommended Project Structure
```
src/newsletters/
├── semantic.py        # EXISTING spine — widen Trace.locator only (backward-compatible)
├── capture.py         # EXISTING — ManualBackend wraps capture_session()
├── distill/           # NEW package (the socket + adapters); import-light, ZERO AI
│   ├── __init__.py    # re-export DistillPort, registry fns, ManualBackend, Coverage, Locator
│   ├── ports.py       # DistillPort (Protocol), DistillationResult, FaithfulnessCheck (Protocol)
│   ├── coverage.py    # Coverage + Unextracted models (the unextracted[] contract, D-05)
│   ├── locators.py    # Locator discriminated union (D-06), extensible to adapter phases
│   ├── registry.py    # register/resolve/available — mirrors templates.py registry
│   ├── manual.py      # ManualBackend (deterministic, no AI) — SOCK-03
│   └── conformance.py # reusable conformance assertions any backend is run through — SOCK-05
└── ...
tests/
└── test_distill_socket.py   # parametrized over registered backends; the SOCK-01..05 checks
```

> NOTE: ARCHITECTURE.md proposes a larger `core/` re-layout (`core/ports.py`, `core/models.py`, …). That is a *future* refactor across many phases. For Phase 1, **do not move existing modules** — adding a `distill/` package beside the current flat layout is the smallest change that ships the contract without disturbing the merged spine. Flag the `core/` re-layout as a planner decision (see Open Questions).

### Pattern 1: `DistillPort` as a runtime-checkable Protocol (SOCK-01)
**What:** One structural interface; backends satisfy it by shape, not inheritance.
**When to use:** This is the central contract of the phase.
**Recommended shape:**
```python
# src/newsletters/distill/ports.py
from __future__ import annotations
from typing import Protocol, runtime_checkable
from pydantic import BaseModel, Field
from ..semantic import Source, Distillation
from .coverage import Coverage


class DistillationResult(BaseModel):
    """What every backend returns: the traced synthesis + an explicit coverage manifest.

    Wrapping Distillation (rather than mutating it) keeps the Rev1 type stable and puts the
    two kinds of honesty side by side: Distillation.missing[] = UNPROVABLE; coverage.unextracted[]
    = UNREADABLE (D-05). Serializes losslessly to/from a JSON sidecar (D-04)."""
    distillation: Distillation
    coverage: Coverage = Field(default_factory=Coverage)
    backend: str = ""            # which backend produced this (audit trail; NOT a behavior switch)


@runtime_checkable
class DistillPort(Protocol):
    name: str
    def distill(self, sources: list[Source]) -> DistillationResult: ...
```
Rationale: `distill(sources) -> DistillationResult` matches SOCK-01 verbatim while carrying coverage (SOCK-04). `@runtime_checkable` lets `registry.register()` do a cheap `isinstance`/attribute check at registration; mypy enforces the full shape statically (Pattern 1 trade-off mitigation). [CITED: .planning/research/ARCHITECTURE.md:144-162]

### Pattern 2: Backend registry — copy the `templates.py` shape (SOCK-02)
**What:** A module-level `dict[str, DistillPort]` + `register`/`resolve`/`available`.
**When to use:** From day one; mirrors the proven in-repo registry exemplar.
**Recommended shape:**
```python
# src/newsletters/distill/registry.py
from __future__ import annotations
from .ports import DistillPort

_BACKENDS: dict[str, DistillPort] = {}

def register(backend: DistillPort) -> DistillPort:
    if not isinstance(backend, DistillPort):       # runtime_checkable structural check
        raise TypeError(f"{backend!r} does not satisfy DistillPort (needs name + distill()).")
    _BACKENDS[backend.name] = backend
    return backend

def resolve(name: str) -> DistillPort:
    try:
        return _BACKENDS[name]
    except KeyError:
        raise KeyError(f"No distill backend named {name!r}. Known: {sorted(_BACKENDS)}") from None

def available() -> list[str]:
    return sorted(_BACKENDS)
```
This is line-for-line the structure of `templates.py:165-184` (`_REGISTRY`, `register`, `get_template`, `all_templates`). Reusing a proven in-repo pattern minimizes review surface and keeps the contract recognizable. [VERIFIED: src/newsletters/templates.py:165-184]

### Pattern 3: `Locator` discriminated union — extensible without breaking the contract (D-06)
**What:** A Pydantic discriminated union keyed on a `kind` literal, exactly like `Block` in `semantic.py:273-287`. Phase 1 ships only the variants it needs (`FreeLocator` for backward-compat + `SessionLocator` for the manual path), but the *union mechanism* is the extensibility point: adapter phases add `CellLocator`/`SlideLocator`/`MessageLocator`/`CodeLocator`/`TurnLocator` variants without touching the `Trace` contract.
**Recommended shape:**
```python
# src/newsletters/distill/locators.py
from __future__ import annotations
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class FreeLocator(BaseModel):
    """Backward-compatible free-text locator (what Trace.locator was in Rev1)."""
    kind: Literal["free"] = "free"
    text: str = ""

class SessionLocator(BaseModel):
    """The manual/by-hand modality anchor: a Source + an optional human note."""
    kind: Literal["session"] = "session"
    source_id: str
    note: str = ""

# --- future variants (declared in adapter phases 4–7 / v2; shown here as the contract's reach) ---
# class MessageLocator: kind="message"; message_id: str; part: int          # Phase 4 (email)
# class CellLocator:    kind="cell";    workbook: str; sheet: str; ref: str  # Phase 5 (excel)
# class SlideLocator:   kind="slide";   deck: str; slide: int; shape: str    # Phase 6 (pptx)
# class CodeLocator:    kind="code";    path: str; start: int; end: int      # work-surface
# class TurnLocator:    kind="turn";    interview_id: str; turn: int         # v2 interview

Locator = Annotated[Union[FreeLocator, SessionLocator], Field(discriminator="kind")]
```
**Carrying the verbatim span (D-06):** add a `span: str | None` (the exact source text) onto `Trace` (or onto each locator variant) so "faithful, not suggestive" is *visible* at author/review time, per D-06. The verbatim span is also what the Phase-3 deterministic entailment check consumes (span-containment). Recommend: put `span: str = ""` on `Trace` itself (one place, all modalities), and let the `Locator` carry the *address*; together they answer "what was said" + "where it lives".
[CITED: .planning/research/ARCHITECTURE.md:226-256] [VERIFIED: src/newsletters/semantic.py:273-287]

### Pattern 4: Widen `Trace.locator` backward-compatibly
**What:** `Trace.locator` is currently `str = ""` (`semantic.py:57-61`) and is constructed as a bare string in `capture.py:70` (`Trace(source_id=d.source_id, locator=d.locator)`). To avoid breaking Rev1, make `locator` accept **either** the old string **or** a `Locator` union, defaulting to `FreeLocator`.
**Two options (decide in plan-check, Open Question 1):**
- **(a) Non-breaking widen on `Trace`:** change `Trace.locator: str` → `locator: Locator = Field(default_factory=FreeLocator)` and add a `field_validator` that coerces a plain `str` into `FreeLocator(text=...)`. Pro: one type everywhere. Con: touches the Rev1 `Trace` model and its JSON shape (migration concern for any persisted sidecars — none exist yet, so low risk now).
- **(b) Additive field:** keep `locator: str` as-is; add a new optional `anchor: Locator | None = None`. Pro: zero risk to Rev1 serialization/tests. Con: two locator fields (string + structured) is muddy and invites drift.
**Recommendation:** Option (a) with the coercion validator — there are no persisted sidecars yet (D-04 introduces them this phase), so this is the cleanest moment to widen, and a `field_validator` keeps `capture_session()` and existing tests passing unchanged. Verify by running the full Rev1 suite (`tests/test_semantic.py`) green after the change.

### Pattern 5: The entailment / faithfulness seam (deterministic, no-AI in Phase 1)
**What:** A narrow `FaithfulnessCheck` Protocol that the socket calls before returning a result, so unfaithful claims are *structurally* unable to pass. Phase 1 ships a **permissive/structural default** (every published claim has ≥1 Trace — which the gate already enforces — plus an optional span-presence check); **Phase 3 (PROV-02)** swaps in deterministic **span-containment** (claim text must be substring/normalized-substring of its traced `span`), and the v2 AI path can add an entailment model behind `[ai]`.
**Recommended seam:**
```python
# src/newsletters/distill/ports.py  (seam only — Phase 3 fills the real check)
from typing import Protocol
from ..semantic import Claim

class FaithfulnessCheck(Protocol):
    def entails(self, claim: Claim) -> bool: ...

class StructuralFaithfulness:
    """Phase-1 default: a claim is 'faithful enough to pass the socket' iff it is traced.
    Phase 3 replaces this with deterministic span-containment (PROV-02)."""
    def entails(self, claim: Claim) -> bool:
        return claim.is_traced
```
**Where it hooks:** inside the socket's post-distill normalization (a single `_enforce(result, check)` function the registry/pipeline calls), NOT inside each backend — so the rule lives in exactly one place (mirrors ARCHITECTURE.md Pattern 4's "one trust rule, one place"). The seam must be a **constructor/parameter injection point** (default `StructuralFaithfulness()`), so Phase 3 injects the span-containment checker without changing any backend. [CITED: .planning/research/ARCHITECTURE.md:226-253] [VERIFIED: src/newsletters/semantic.py:72-74]

### Pattern 6: `ManualBackend` adapts `capture_session()` (SOCK-03)
**What:** The manual backend is the thinnest possible adapter: it accepts the by-hand inputs and delegates structuring to the *existing, deterministic* `capture_session()`, then wraps the result with a (fully-covered) coverage manifest.
**Recommended shape:**
```python
# src/newsletters/distill/manual.py
from __future__ import annotations
from ..semantic import Source, Distillation
from ..capture import WorkSession, capture_session
from .ports import DistillationResult
from .coverage import Coverage

class ManualBackend:
    """Author-by-hand modality. Zero AI, zero network. Wraps capture_session()."""
    name = "manual"

    def distill(self, sources: list[Source]) -> DistillationResult:
        # The by-hand path: the human has already asserted claims+traces via a WorkSession.
        # capture_session() deterministically lifts decisions -> traced Claims (capture.py:58-78).
        # For the socket signature, accept the session via construction or a sources->session map.
        ...
        distillation: Distillation = capture_session(self._session)
        return DistillationResult(
            distillation=distillation,
            coverage=Coverage.fully_covered(reason="hand-authored: nothing extracted, nothing dropped"),
            backend=self.name,
        )
```
**The signature mismatch to resolve (Open Question 2):** `DistillPort.distill` takes `list[Source]`, but `capture_session()` takes a `WorkSession` (sources + `Decision[]`). The by-hand modality's *input* is richer than raw sources. Recommended resolution: `ManualBackend` is constructed with the `WorkSession` (or a `Decision[]`) and `distill(sources)` validates/uses those; OR the socket's input type is widened to a `DistillInput` that can carry either raw sources or a pre-authored session. **Recommend constructor injection of the `WorkSession`** for Phase 1 (smallest change, keeps the Protocol signature exactly `distill(sources) -> ...` per SOCK-01); the planner should confirm. [VERIFIED: src/newsletters/capture.py:47-78]

### Anti-Patterns to Avoid
- **Adding an auto-publish path through the socket.** The socket returns a `Distillation`/`DistillationResult` ONLY. It must never call `Surface.publish()`, set `ReviewState.PUBLISHED`, or construct a published `Review`. The merged gate (`semantic.py:142-150`) is the only path to Published. [VERIFIED: src/newsletters/semantic.py:142-150] (HARD RULE — non-negotiable.)
- **Importing any AI/LLM library anywhere reachable from `distill/` core.** Phase 1 ships zero AI; the AI backend is v2 and must lazy-import inside its own method behind `[ai]`. Nothing in `ports.py`/`registry.py`/`manual.py`/`coverage.py`/`locators.py` may import an AI package. [CITED: CLAUDE.md hard rules]
- **Collapsing `missing[]` and `unextracted[]` into one list.** D-05 requires them DISTINCT: `missing[]` = *unprovable* claim (no entailed evidence, already on `Distillation`); `unextracted[]` = *unreadable* raw content a backend could not extract (new, on `Coverage`). Keep two fields.
- **Editorializing in the backend.** `ManualBackend` (and every backend) extracts + traces; it must not summarize/rank/emphasize. `capture_session()` already obeys this ("it structures what happened, it does not invent" — `capture.py:62-64`).
- **Mutating `Distillation` to add coverage.** Prefer the `DistillationResult` wrapper so the Rev1 type and its tests/serialization stay stable.
- **IDs/anchors derived from list position.** Locators must be content/address anchors (source_id, message-id, sheet!cell), never array offsets — this is the seam that Phase 3 (PROV-01, content-addressed traces) builds on. [CITED: .planning/research/ARCHITECTURE.md:404-409]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structuring a finished by-hand session into traced claims | A new manual-distill routine | EXISTING `capture.capture_session()` | Already deterministic, tested (`test_capture_session_traces_every_decision`), and obeys faithful-not-suggestive. The ManualBackend is a *thin wrapper*, not a reimplementation. [VERIFIED: src/newsletters/capture.py:58-78] |
| Name → backend lookup | A bespoke plugin loader / entry-point machinery now | The `templates.py` dict-registry shape | Proven in-repo, zero deps; entry points are a *later, non-breaking* extension. [VERIFIED: src/newsletters/templates.py:165-184] |
| Discriminated union over heterogeneous locators | Stringly-typed `"deck:3/shape:body"` anchors | Pydantic `Annotated[Union[...], Field(discriminator="kind")]` | The repo already uses exactly this for `Block`; it gives typed, validated, JSON-round-trippable variants. [VERIFIED: src/newsletters/semantic.py:273-287] |
| JSON sidecar (de)serialization (D-04) | A custom encoder | Pydantic v2 `model_dump_json()` / `model_validate_json()` | Lossless round-trip is free and tested at the framework level; just assert round-trip equality in conformance. |
| The structural-interface contract | An `abc.ABC` base every backend must inherit | `typing.Protocol` (`@runtime_checkable`) | ARCHITECTURE.md Pattern 1 — duck-typed flexibility + mypy-checkable; operators add a backend by shape. [CITED: .planning/research/ARCHITECTURE.md:130-162] |

**Key insight:** Phase 1 is *almost entirely* an exercise in reusing two existing in-repo patterns (the `templates.py` registry and the `semantic.py` discriminated-union `Block`) and one existing function (`capture_session()`). The only genuinely new typed models are `Coverage`/`Unextracted` and the `Locator` variants. Hand-rolling anything beyond that is a smell.

## Runtime State Inventory

> Phase 1 is greenfield-in-a-brownfield: it *adds* a `distill/` package and *widens one field* on an existing type. The one change that touches existing state is `Trace.locator`.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **None** — no on-disk Distillation sidecars exist yet. D-04 introduces JSON sidecars *in this phase*; there is no legacy persisted `Trace.locator` string to migrate. Verified: no `content/` distillation JSON, persistence is unbuilt (ARCHITECTURE.md: `persist/` is deferred). | None (greenfield for sidecars) |
| Live service config | **None** — no external services, no telemetry, no running daemons. | None |
| OS-registered state | **None** — no scheduled tasks, no installed CLIs beyond the `newsletters` entry point (unaffected). | None |
| Secrets/env vars | **None** — Phase 1 has zero network/AI; no secrets referenced. | None |
| Build artifacts / in-memory shape | `Trace.locator: str` is referenced in `capture.py:70` and constructed bare-string; widening it to a `Locator` union changes the in-memory + JSON shape of `Trace`. Rev1 tests (`tests/test_semantic.py`) construct `Trace(source_id=...)` (no locator) and `Trace(source_id="s1")` — these stay valid with a defaulted union. | Add a `field_validator` coercing `str → FreeLocator`; re-run the full Rev1 suite green to confirm no regression. |

**Canonical question — after every file is updated, what runtime systems still hold the old shape?** Only persisted JSON Distillations would — and there are none yet. The risk is purely in-process type compatibility, fully covered by re-running `tests/test_semantic.py`.

## Common Pitfalls

### Pitfall 1: Breaking the Rev1 spine by widening `Trace.locator`
**What goes wrong:** Changing `locator: str` to a union breaks `capture.py:70` and every test that passes a string (or omits it).
**Why it happens:** Pydantic v2 will reject a bare `str` for a `Locator` union field unless coerced.
**How to avoid:** Add a `field_validator(mode="before")` on `Trace` that wraps a plain `str` into `FreeLocator(text=...)` and leaves `Locator` instances/dicts alone. Keep `locator` defaulted so `Trace(source_id="s1")` still works.
**Warning signs:** Any failure in `tests/test_semantic.py` after the change — that suite is the regression tripwire and MUST be green.

### Pitfall 2: The socket signature vs. the manual modality's richer input
**What goes wrong:** `DistillPort.distill(sources: list[Source])` cannot, by signature alone, carry the human's pre-authored `Decision[]` that `capture_session()` needs.
**Why it happens:** SOCK-01 fixes the signature to `distill(sources) -> Distillation`, but the by-hand modality's input is a `WorkSession`, not raw sources.
**How to avoid:** Inject the `WorkSession`/`Decision[]` via the `ManualBackend` constructor (state on the backend instance), keeping `distill(sources)` signature-exact. Document that `sources` is the backing evidence set; the authored decisions live on the backend.
**Warning signs:** A `distill()` that ignores its `sources` argument entirely, or a temptation to change the Protocol signature (which would violate SOCK-01).

### Pitfall 3: Coverage that lies by omission
**What goes wrong:** A backend returns an empty `unextracted[]` when it actually skipped content, silently dropping it.
**Why it happens:** Coverage is opt-in unless the conformance suite forces honesty.
**How to avoid:** Conformance (SOCK-05) must assert that a backend declares its coverage posture explicitly — e.g., a `Coverage` carries a `complete: bool` and, when not complete, a non-empty `unextracted[]`; the suite fails a backend that claims completeness while input clearly contained more. For `ManualBackend`, `complete=True` is honest (the human authored everything).
**Warning signs:** Any backend whose `Coverage` is the default-empty value on non-trivial input.

### Pitfall 4: The faithfulness seam becoming AI-coupled or a no-op
**What goes wrong:** Either the seam is left so permissive it never blocks anything (then Phase 3 has nothing to attach to), or it's accidentally wired to need an AI model.
**Why it happens:** Under-specifying the seam.
**How to avoid:** Ship `StructuralFaithfulness` (traced-claim check) as a *named, injectable* default and add one conformance test that a deliberately-untraced claim is rejected by the seam — proving the seam is live and deterministic. Phase 3 then injects span-containment by swapping the injected checker, no backend change.
**Warning signs:** No test exercises the faithfulness seam; the seam is a free function rather than an injectable dependency.

## Code Examples

### Coverage / `unextracted[]` contract (SOCK-04, D-05, D-03 cost/effort)
```python
# src/newsletters/distill/coverage.py
from __future__ import annotations
from pydantic import BaseModel, Field
from .locators import Locator

class Unextracted(BaseModel):
    """A piece of raw content a backend could NOT extract — UNREADABLE (distinct from
    Distillation.missing[], which is UNPROVABLE). Never silently dropped (D-05)."""
    locator: Locator                      # where the unread content lives
    reason: str = ""                      # e.g. "SmartArt shape unreadable", "formula uncomputed"

class Coverage(BaseModel):
    """A backend's honest report of what it did and did not read."""
    complete: bool = True                 # did the backend read everything it was given?
    unextracted: list[Unextracted] = Field(default_factory=list)
    # D-03: carry a cheap-path signal so operators can prefer low-token backends.
    cost_hint: str = "free"               # "free" | "low" | "medium" | "high"
    effort_hint: str = "deterministic"    # "deterministic" | "low-token" | "agentic"

    @classmethod
    def fully_covered(cls, reason: str = "") -> "Coverage":
        return cls(complete=True, unextracted=[])

    def model_post_init(self, _ctx) -> None:
        # Honesty invariant: cannot claim completeness while reporting unread content.
        if self.complete and self.unextracted:
            raise ValueError("Coverage.complete=True is inconsistent with non-empty unextracted[].")
```

### JSON sidecar round-trip (D-04) — lossless, via Pydantic v2
```python
# write a Distillation/result to a diffable sidecar, and read it back identically
from pathlib import Path
from newsletters.distill.ports import DistillationResult

def write_sidecar(result: DistillationResult, path: Path) -> None:
    path.write_text(result.model_dump_json(indent=2))          # lossless serialize (D-04)

def read_sidecar(path: Path) -> DistillationResult:
    return DistillationResult.model_validate_json(path.read_text())  # lossless deserialize

# conformance asserts: read_sidecar(write_sidecar(r)) == r  (round-trip equality)
```

### Reusable conformance assertions (SOCK-05)
```python
# src/newsletters/distill/conformance.py
from __future__ import annotations
from .ports import DistillPort, DistillationResult, StructuralFaithfulness
from ..semantic import Source, Claim

def assert_conforms(backend: DistillPort, sources: list[Source]) -> DistillationResult:
    """Run ANY backend through the socket contract. Fails it on contract violations."""
    assert isinstance(backend, DistillPort), "must satisfy DistillPort (name + distill())"
    result = backend.distill(sources)
    assert isinstance(result, DistillationResult), "distill() must return DistillationResult"
    # SOCK-04: coverage is reported and internally honest (validator already enforces consistency)
    assert result.coverage is not None
    # Faithfulness seam is live and deterministic: every emitted claim is traced
    check = StructuralFaithfulness()
    for c in result.distillation.claims:
        assert check.entails(c), f"unfaithful claim slipped the socket: {c.text[:40]!r}"
    # D-04: lossless JSON round-trip
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result
    # HARD RULE: the socket must not have produced a published anything (it returns truth only)
    return result
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `synthesize()` as the single distill entrypoint (raises `NotImplementedError`, `semantic.py:407-419`) | A `DistillPort` socket with named backends; `synthesize()` can later resolve to a registry backend | This phase | The "one agent step" framing in docs/architecture §3 becomes "one *port* with peer backends" — AI is one adapter, not the path. ARCHITECTURE.md Anti-Pattern 1. |
| `Trace.locator: str` (free text) | `Trace` carries a discriminated `Locator` union + verbatim `span` | This phase | Auditability anchor becomes typed and extensible to every source type without contract churn (D-06). |
| Gaps tracked only as `missing[]` (unprovable) | Two distinct honesties: `missing[]` (unprovable) + `Coverage.unextracted[]` (unreadable) | This phase | "No content silently dropped" becomes enforceable (D-05). |

**Deprecated/outdated:**
- `pyproject.toml` currently lists `langchain[anthropic]`, `langgraph`, `langsmith`, `pydantic-ai` in core `dependencies`. **Phase 1 does not fix this** (that is Phase 2 / PKG-01..04), but Phase 1 MUST NOT add to it and MUST NOT import any of them from the new `distill/` code. `langsmith` in particular phones home (telemetry hard-rule violation) and is slated for removal. [VERIFIED: pyproject.toml] [CITED: .planning/research/STACK.md:72, 90]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Wrapping `Distillation` in a `DistillationResult` (vs. adding `coverage` to `Distillation`) is the cleaner choice | Standard Stack / Pattern 1 | Low — both are viable; if the planner prefers a field on `Distillation`, the coverage model + seam are unaffected. Decide in plan-check. |
| A2 | Constructor-injecting the `WorkSession` into `ManualBackend` (keeping `distill(sources)` signature-exact) is acceptable | Pattern 6 / Pitfall 2 | Medium — if a reviewer insists `distill(sources)` must be self-contained, the input type must widen to a `DistillInput`. Surface to user/planner. |
| A3 | Widening `Trace.locator` in place (Option a) is safe because no persisted sidecars exist yet | Pattern 4 / Runtime State | Low — verified no sidecar data exists; the only risk is in-process, covered by re-running Rev1 tests. |
| A4 | A module-level dict registry (no entry points) is sufficient for Phase 1 | Pattern 2 | Low — entry points are an additive, non-breaking later extension. |
| A5 | The Phase-1 faithfulness default should be the traced-claim structural check (not span-containment) | Pattern 5 | Low — Phase 3 (PROV-02) owns span-containment; Phase 1 only needs a live, injectable, deterministic seam. |
| A6 | The project's larger `core/` re-layout from ARCHITECTURE.md should NOT happen in Phase 1 | Recommended Project Structure | Low — minimizing churn protects the merged spine; the re-layout can be a dedicated later refactor. |

## Open Questions (RESOLVED)

*All three questions were resolved during Phase-1 planning (plan-check, 2026-06-14). Resolutions are encoded in `SKELETON.md` and the plans.*

1. **`DistillationResult` wrapper vs. `coverage` field on `Distillation`.**
   - What we know: D-05 wants `unextracted[]` distinct from `missing[]`; `Distillation` already has `missing[]`.
   - What's unclear: Whether to keep `Distillation` immutable-in-shape (wrapper) or extend it (field).
   - Recommendation: Wrapper (`DistillationResult`) to protect Rev1 stability; confirm in plan-check.
   - **RESOLVED:** `DistillationResult` wrapper (existing `Distillation` + new `Coverage` manifest). Encoded in `SKELETON.md` and `01-01-PLAN.md` (Task 2) — keeps the Rev1 `Distillation` shape stable.

2. **The `distill(sources)` signature vs. the by-hand richer input.**
   - What we know: SOCK-01 fixes `distill(sources) -> Distillation`; the manual modality needs `Decision[]`.
   - What's unclear: Constructor-inject the session vs. widen the input to a `DistillInput`.
   - Recommendation: Constructor injection for Phase 1 (signature-exact); revisit if/when adapter phases need a uniform input.
   - **RESOLVED:** Constructor injection of the `WorkSession` into `ManualBackend`, keeping `distill(sources)` signature-exact (SOCK-01). Encoded in `01-01-PLAN.md` (Task 3).

3. **Does `synthesize()` get rewired to the registry now, or stay a stub?**
   - What we know: `synthesize()` raises `NotImplementedError` and `test_synthesize_is_external_stub` asserts that.
   - What's unclear: Whether Phase 1 should make `synthesize()` resolve a backend (which would break that test) or leave it untouched.
   - Recommendation: Leave `synthesize()` as the external/AI stub; expose the socket via the new `distill/` API and a possible `distill(sources, backend="manual")` convenience. Keep the existing test green. Decide in plan-check.
   - **RESOLVED:** Leave `synthesize()` untouched as the external/AI stub (`test_synthesize_is_external_stub` stays green); the socket is exposed via the new `newsletters.distill` API. Encoded in `SKELETON.md` and `01-01-PLAN.md`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python interpreter | All Phase-1 code | ✓ (probe) but **3.11.15** in the base shell | 3.11.15 | Project targets **3.12** (`pyproject.toml [tool.mypy] python_version="3.12"`). `StrEnum`/`Annotated`/discriminated unions used here work on 3.11+, but the planner should pin/confirm a 3.12 venv to match the declared target. |
| Pydantic v2 | All typed models | ✗ in base interpreter probe | — | Install into the active venv: `pip install -e ".[dev,test]"`. (Declared core dep; absent only from this bare probe shell.) |
| pytest | Conformance suite (SOCK-05) | ✗ in base interpreter probe | — | `pip install -e ".[dev,test]"` |
| mypy | Static Protocol-shape gate | ✗ in base interpreter probe | — | `pip install -e ".[dev,test]"` (mypy is in `[tool.mypy]` config but not declared in `[dev]` — planner should add it to `[dev]`). |
| ruff | Lint | ✓ | 0.15.8 | — |

**Missing dependencies with no fallback:** none — everything is `pip install -e ".[dev,test]"` into a 3.12 venv.
**Missing dependencies with fallback:**
- The base shell interpreter is 3.11 and lacks pydantic/pytest. **Wave 0 must establish a Python 3.12 virtualenv with the project installed editable** before any Phase-1 code can run or be tested. Note: `mypy` is referenced by config but not listed in `[dev]` extras — add it.

## Validation Architecture

> nyquist_validation is enabled (`config.json workflow.nyquist_validation: true`). This is a foundational contract gating all later phases, so validation is mandatory.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (declared in `[dev]` and `[test]`; configured in `pyproject.toml [tool.pytest.ini_options]` with `pythonpath=["src"]`, `testpaths=["tests"]`) |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/test_distill_socket.py -x -q` |
| Full suite command | `pytest -q` (runs Rev1 `test_semantic.py` + new `test_distill_socket.py` — Rev1 must stay green) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SOCK-01 | `DistillPort` Protocol; pipeline calls `distill(sources)->DistillationResult` without knowing the backend | unit | `pytest tests/test_distill_socket.py::test_distillport_is_backend_agnostic -x` | ❌ Wave 0 |
| SOCK-02 | Registry registers/resolves a backend by name; unknown name errors clearly | unit | `pytest tests/test_distill_socket.py::test_registry_register_resolve -x` | ❌ Wave 0 |
| SOCK-03 | `ManualBackend` emits a valid `Distillation` with zero AI; every claim traced | unit | `pytest tests/test_distill_socket.py::test_manual_backend_zero_ai_traced -x` | ❌ Wave 0 |
| SOCK-04 | Coverage manifest with `unextracted[]`; `complete=True` inconsistent with non-empty `unextracted` rejected; distinct from `missing[]` | unit | `pytest tests/test_distill_socket.py::test_coverage_unextracted_distinct_from_missing -x` | ❌ Wave 0 |
| SOCK-05 | Conformance suite passes a conforming backend; fails one with untraced claims / unreported coverage / faithfulness violation | unit | `pytest tests/test_distill_socket.py::test_conformance_fails_bad_backend -x` | ❌ Wave 0 |
| D-04 | `DistillationResult` JSON sidecar round-trips losslessly | unit | `pytest tests/test_distill_socket.py::test_sidecar_roundtrip -x` | ❌ Wave 0 |
| D-06 | `Trace` carries a discriminated `Locator` + verbatim `span`; bare-string locator still coerces | unit | `pytest tests/test_distill_socket.py::test_locator_union_and_backward_compat -x` | ❌ Wave 0 |
| HARD-RULE (no auto-publish) | Socket returns truth only; produces no published `Surface`/`Review` | unit | `pytest tests/test_distill_socket.py::test_socket_never_auto_publishes -x` | ❌ Wave 0 |
| HARD-RULE (AI-optional) | No AI import reachable from `distill/`; `ManualBackend` runs with zero AI deps | unit | `pytest tests/test_distill_socket.py::test_distill_package_imports_no_ai -x` (assert no `langchain`/`langgraph`/`langsmith`/`pydantic_ai` in `sys.modules` after importing `newsletters.distill`) | ❌ Wave 0 |
| REGRESSION | Rev1 spine unaffected by `Trace.locator` widening | unit | `pytest tests/test_semantic.py -q` | ✅ exists |

### Sampling Rate
- **Per task commit:** `pytest tests/test_distill_socket.py -x -q`
- **Per wave merge:** `pytest -q` (both suites; Rev1 regression tripwire)
- **Phase gate:** Full suite green + `mypy src/newsletters/distill` clean (Protocol-shape gate) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_distill_socket.py` — the SOCK-01..05 + D-04/D-06 + hard-rule tests (above)
- [ ] Establish a **Python 3.12 venv** with `pip install -e ".[dev,test]"` (base shell is 3.11 and lacks pydantic/pytest)
- [ ] Add `mypy` to `[project.optional-dependencies].dev` (referenced in config, not declared)
- [ ] (Optional) a tiny intentionally-broken backend fixture (untraced claim / lying coverage) for the SOCK-05 negative test

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1`. Phase 1 ships no network, no auth, no I/O beyond local JSON sidecars and reading already-loaded `Source` objects. The relevant surface is **input validation of untrusted serialized data** (a JSON sidecar an operator might load).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth in this phase |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | Local library; the review gate (existing) governs publish, untouched |
| V5 Input Validation | yes | Pydantic v2 `model_validate_json` validates sidecars on load; discriminated unions reject unknown `kind`; `Coverage` validator rejects internally-inconsistent manifests |
| V6 Cryptography | no | No secrets/crypto in Phase 1 (private-corpus encryption is a later phase) |

### Known Threat Patterns for {Python / Pydantic / local file I/O}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed/hostile JSON sidecar loaded as a Distillation | Tampering | Always parse via `model_validate_json` (never `eval`/`pickle`); Pydantic rejects unknown discriminator `kind` and type-mismatched fields |
| Silent content drop disguised as success | Repudiation / Information disclosure | `Coverage.unextracted[]` + the `complete`/`unextracted` consistency validator make dropped content non-silent (D-05) |
| A backend smuggling an unfaithful (untraced) claim through the socket | Tampering | The faithfulness seam (`StructuralFaithfulness`) + conformance assertion reject untraced claims; Phase 3 hardens to span-containment |
| Path traversal when writing/reading sidecars | Tampering | Sidecar paths are operator-supplied local paths; validate/normalize with `pathlib` and write only within the intended output dir (planner should constrain) |

## Sources

### Primary (HIGH confidence)
- `/home/user/newsletters/src/newsletters/semantic.py` — the merged Rev1 spine: `Source/Trace/Claim/Distillation/Review/Surface`, the no-auto-publish validator (`:142-150`), the discriminated-union `Block` pattern (`:273-287`), the `synthesize()` stub (`:407-419`).
- `/home/user/newsletters/src/newsletters/capture.py` — `WorkSession`/`Decision`/`capture_session()` (`:47-78`), the deterministic no-AI path the ManualBackend wraps.
- `/home/user/newsletters/src/newsletters/templates.py` — the registry exemplar (`_REGISTRY` + `register`/`get_template`/`all_templates`, `:165-184`).
- `/home/user/newsletters/tests/test_semantic.py` — the regression tripwire + test conventions to mirror.
- `/home/user/newsletters/src/newsletters/__init__.py` — the public API surface to extend.
- `/home/user/newsletters/pyproject.toml` — deps (langchain/langsmith currently in core — Phase 2's problem, not Phase 1's), pytest config, mypy target 3.12.
- `/home/user/newsletters/.planning/phases/01-distill-socket-contract/01-CONTEXT.md` — D-01..D-06, the locked decisions.
- `/home/user/newsletters/.planning/REQUIREMENTS.md` — SOCK-01..05 verbatim.
- `/home/user/newsletters/docs/architecture.md` §1–§3 — typed model, package API, publish loop, invariants.

### Secondary (MEDIUM confidence)
- `/home/user/newsletters/.planning/research/ARCHITECTURE.md` — ports-and-adapters framing, Protocol + registry + lazy-AI + normalize-to-Claim + Locator-union patterns, anti-patterns. (Project's own prior research; defer to it where it decided things.)
- `/home/user/newsletters/.planning/research/STACK.md` — confirms zero new deps for Phase 1; langsmith telemetry / langchain removal is Phase 2; pydantic-ai is v2 only.

### Tertiary (LOW confidence)
- None — this phase is entirely in-repo design; no web/training-only claims were needed.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new deps; stdlib + Pydantic v2 already in core; patterns proven in-repo.
- Architecture: HIGH — `DistillPort` shape, registry, and `Locator` union are direct applications of existing in-repo patterns + the project's own ARCHITECTURE.md.
- Pitfalls: HIGH — derived from reading the actual Rev1 code paths that the changes touch (`Trace.locator`, `capture_session()` signature, the no-auto-publish validator).

**Research date:** 2026-06-14
**Valid until:** 2026-07-14 (stable — in-repo design over a merged spine; no fast-moving external deps)
