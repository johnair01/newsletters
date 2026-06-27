# Phase 1: Distill Socket Contract - Pattern Map

**Mapped:** 2026-06-14
**Files analyzed:** 8 (7 new + 1 widened existing)
**Analogs found:** 8 / 8 (every new file maps to a verified in-repo analog)

All analog line numbers below are **verified against the live branch** (read this session),
not taken on trust from RESEARCH.md.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/newsletters/distill/ports.py` (`DistillPort` Protocol, `DistillationResult`, `FaithfulnessCheck` seam) | contract / model | transform | `src/newsletters/semantic.py` (typed models) + `templates.py` (module conventions) | role-match (Protocol is net-new to repo) |
| `src/newsletters/distill/registry.py` (`register`/`resolve`/`available`) | registry | request-response (lookup) | `src/newsletters/templates.py:165-184` (`_REGISTRY` + register/get/all) | **exact** |
| `src/newsletters/locators.py` (`Locator` discriminated union — TOP-LEVEL LEAF module, NOT under `distill/`) | model | transform | `src/newsletters/semantic.py:273-287` (`Block` discriminated union) | **exact** |
| `src/newsletters/distill/coverage.py` (`Coverage` + `Unextracted`) | model | transform | `src/newsletters/semantic.py` `Claim`/`Distillation` + `Review` validator (`:142-150`) | role-match |
| `src/newsletters/distill/manual.py` (`ManualBackend`) | adapter / service | transform | `src/newsletters/capture.py:58-78` (`capture_session`) wrapped by `build_report` `:81-113` | **exact** (thin wrapper) |
| `src/newsletters/distill/conformance.py` (reusable assertions) | test-utility | transform | `tests/test_semantic.py` (assertion style) | role-match |
| `src/newsletters/distill/__init__.py` (re-export public API) | config / barrel | — | `src/newsletters/__init__.py:14-75` (imports + `__all__`) | **exact** |
| `src/newsletters/semantic.py` — **widen `Trace.locator`** | model (modify) | transform | self: `Trace` `:57-61`, `Block` validator idiom `:273-287`, coercion via `model_validator` `:142-150` | in-place |
| `tests/test_distill_socket.py` | test | — | `tests/test_semantic.py:1-55` | **exact** |

## Shared Conventions (apply to every new file)

Verified from the live modules — the planner should encode these in every plan's action section:
- **`from __future__ import annotations`** as the first import (see `capture.py:17`, `semantic.py` imports).
- **Pydantic v2** models: `BaseModel`, `Field(default_factory=...)`, `model_validator(mode="after")`,
  `Literal`, `Annotated`, `Union`, `Field(discriminator="kind")`. Imports: `from pydantic import ...`
  (`semantic.py:33`), domain imports relative (`from .semantic import ...`, `from ..semantic import ...`).
- **Banner comment dividers** between sections: `# ----...---- #` (used throughout `semantic.py`,
  `templates.py`, `capture.py`).
- **Docstrings carry the *why*** and cite the invariant/decision they serve (project teaching norm;
  see `capture.py:58-64`, `semantic.py:142-150`).
- **Python 3.12 target** (`pyproject.toml [tool.mypy] python_version="3.12"`); base shell is 3.11 —
  Wave 0 must stand up a 3.12 venv with `pip install -e ".[dev,test]"`.

---

## Pattern Assignments

### `src/newsletters/distill/registry.py` (registry, lookup) — SOCK-02

**Analog:** `src/newsletters/templates.py:165-184` (EXACT — copy this structure line-for-line).

**Core registry pattern** (`templates.py:165-184`, verbatim from live code):
```python
_REGISTRY: dict[str, SurfaceTemplate] = {t.name: t for t in (SHOW, REPORT, ARTICLE, NEWSLETTER)}

def register(template: SurfaceTemplate) -> SurfaceTemplate:
    """Register an operator-defined template (forkability — no core change needed)."""
    _REGISTRY[template.name] = template
    return template

def get_template(name: str) -> SurfaceTemplate:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"No surface template named {name!r}. Known: {sorted(_REGISTRY)}"
        ) from None

def all_templates() -> list[SurfaceTemplate]:
    return sorted(_REGISTRY.values(), key=lambda t: t.distance)
```

**Copy guidance:** Same shape, renamed: `_BACKENDS: dict[str, DistillPort]`, `register(backend)` keyed
on `backend.name`, `resolve(name)` mirroring `get_template` (same `KeyError ... from None` + `sorted()`
known-keys message), `available()` mirroring `all_templates` (return `sorted(_BACKENDS)`). Per RESEARCH
Pattern 2, add a `isinstance(backend, DistillPort)` structural check in `register()` (enabled by
`@runtime_checkable`). Note the analog's `register` is **export-public** (`__init__.py:55`) — do the same.

---

### `src/newsletters/locators.py` (model, discriminated union — TOP-LEVEL LEAF) — D-06

**Analog:** `src/newsletters/semantic.py:273-287` (EXACT — `Block` is the discriminated-union exemplar).

**PLACEMENT (load-bearing — circular-import fix from cross-AI review):** put this union in a TOP-LEVEL leaf
module `src/newsletters/locators.py` (sibling of `semantic.py`), NOT under the `distill` package. The file
must import ONLY stdlib + pydantic — nothing from `semantic`, `distill`, or `capture`. Reason: if the union
lived at `distill/locators.py`, `semantic.py` importing it would first run `distill/__init__.py` → eager
`ports` import → `from ..semantic import ...` while `semantic` is mid-init → ImportError. A top-level leaf
that both `semantic` and `distill` import keeps the graph acyclic, mirroring the existing `semantic →
templates` leaf import (semantic.py:35).

**Discriminated-union pattern** (`semantic.py:273-287`, verbatim):
```python
Block = Annotated[
    Union[
        ProseBlock,
        ClaimsBlock,
        KpiStripBlock,
        # ... more variants ...
        DiagramBlock,
    ],
    Field(discriminator="kind"),
]
```

**Variant shape** (each block model carries a `kind: Literal[...]` discriminator — confirm against
`ProseBlock`/`ClaimsBlock` in `semantic.py`; same idiom applies to each `Locator` variant).

**Imports already proven in-repo** (`semantic.py:31,33`):
```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field
```

**Copy guidance:** Ship only the Phase-1 variants — `FreeLocator(kind="free", text="")` (backward-compat
for the old bare-string locator) and `SessionLocator(kind="session", source_id, note="")` — then
`Locator = Annotated[Union[FreeLocator, SessionLocator], Field(discriminator="kind")]`. Leave the
adapter-phase variants (`MessageLocator`/`CellLocator`/`SlideLocator`/`CodeLocator`/`TurnLocator`) as
commented stubs documenting the contract's reach (RESEARCH Pattern 3). Anti-pattern: never derive a
locator from list position — anchors are content/address only.

---

### `src/newsletters/distill/coverage.py` (model, transform) — SOCK-04, D-05, D-03

**Analog:** `src/newsletters/semantic.py` — `Claim`/`Distillation` for the typed-list + property shape,
and the `Review` validator (`:142-150`) for the **self-consistency-raises** idiom.

**Honesty-invariant validator pattern** (`semantic.py:142-150`, verbatim — copy this *shape* for
Coverage's `complete` vs `unextracted[]` check):
```python
@model_validator(mode="after")
def _published_requires_satisfied_policy(self) -> "Review":
    if self.state is ReviewState.PUBLISHED and not self.satisfied():
        raise ValueError(
            "Cannot be Published: the review policy is not satisfied "
            f"(need {self.policy.describe()}; have approvals={self.approvals!r}, "
            f"author={self.author!r}). No auto-publish path."
        )
    return self
```

**Typed-list-with-property pattern** (`Distillation`, `semantic.py:162-171`):
```python
claims: list[Claim] = Field(default_factory=list)
missing: list[str] = Field(default_factory=list)   # <- the UNPROVABLE list (reuse; do NOT merge)
...
@property
def untraced_claims(self) -> list[Claim]:
    return [c for c in self.claims if not c.is_traced]
```

**Copy guidance:** `Unextracted(locator: Locator, reason: str = "")`; `Coverage(complete: bool = True,
unextracted: list[Unextracted] = Field(default_factory=list), cost_hint: str = "free",
effort_hint: str = "deterministic")` with a `model_validator(mode="after")` that raises if
`complete and unextracted` (the D-05 honesty invariant — mirror the `Review` validator above, including a
teaching-style message). `unextracted[]` (UNREADABLE) lives here and stays **distinct** from
`Distillation.missing[]` (UNPROVABLE, `semantic.py:163`) — keep two fields (anti-pattern: collapsing them).
Add `cost_hint`/`effort_hint` for D-03 low-token preference.

---

### `src/newsletters/distill/ports.py` (contract + models) — SOCK-01

**Analog:** `src/newsletters/semantic.py` for the Pydantic model conventions; the `Protocol` itself is
net-new to the repo (no existing Protocol analog — flagged in "No Analog Found"). Follow ARCHITECTURE.md
Pattern 1 (`@runtime_checkable typing.Protocol`).

**Model conventions to mirror** (from `Distillation`/`Claim`, `semantic.py:64-74,158-167`): docstring
states the *why*, `Field(default_factory=...)` for collections/sub-models, `@property` for derived facts.

**Recommended shape** (RESEARCH Pattern 1 + 5 — net-new, no verbatim analog):
```python
from __future__ import annotations
from typing import Protocol, runtime_checkable
from pydantic import BaseModel, Field
from ..semantic import Source, Distillation, Claim
from .coverage import Coverage

class DistillationResult(BaseModel):
    distillation: Distillation
    coverage: Coverage = Field(default_factory=Coverage)
    backend: str = ""   # audit trail, NOT a behavior switch

@runtime_checkable
class DistillPort(Protocol):
    name: str
    def distill(self, sources: list[Source]) -> DistillationResult: ...

class FaithfulnessCheck(Protocol):
    def entails(self, claim: Claim) -> bool: ...

class StructuralFaithfulness:           # Phase-1 default; Phase 3 swaps in span-containment
    def entails(self, claim: Claim) -> bool:
        return claim.is_traced          # reuses Claim.is_traced (semantic.py:72-74)
```

**Copy guidance:** Wrap `Distillation` (don't mutate it) so the Rev1 type and its tests stay stable
(RESEARCH Open Q1 — confirm in plan-check). `StructuralFaithfulness` reuses the **verified** existing
`Claim.is_traced` property (`semantic.py:72-74`). The seam must be **injectable** (default
`StructuralFaithfulness()`), hooked in one place (`_enforce(result, check)`), never inside each backend.

---

### `src/newsletters/distill/manual.py` (adapter) — SOCK-03

**Analog:** `src/newsletters/capture.py:58-78` (`capture_session`) — the deterministic no-AI engine to
wrap; and `capture.py:81-113` (`build_report`) for the "thin wrapper that calls `capture_session()` then
constructs a result" shape.

**Engine being wrapped** (`capture.py:58-78`, verbatim — DO NOT reimplement, delegate to it):
```python
def capture_session(session: WorkSession) -> Distillation:
    claims = [
        Claim(
            text=d.text,
            evidence=[Trace(source_id=d.source_id, locator=d.locator)],
            confidence=d.confidence,
            topics=d.topics,
        )
        for d in session.decisions
    ]
    ...
    return Distillation(narrative=narrative, claims=claims, traces=list(session.sources))
```

**Wrapper-shape analog** (`build_report`, `capture.py:96`): `distillation = capture_session(session)`
then construct/return — exactly the `ManualBackend.distill` body.

**Copy guidance:** `name = "manual"`; `distill(sources)` returns `DistillationResult(distillation=
capture_session(self._session), coverage=Coverage.fully_covered(...), backend=self.name)`.
**Signature mismatch (RESEARCH Pitfall 2 / Open Q2):** `DistillPort.distill(sources)` is fixed by SOCK-01,
but `capture_session()` needs a `WorkSession` (`capture.py:47-55`, sources + `Decision[]`). Resolution:
**constructor-inject** the `WorkSession` into `ManualBackend`, keep `distill(sources)` signature-exact.
Zero AI, zero network. Must not editorialize (the engine already obeys "structures, does not invent",
`capture.py:62-64`).

---

### `src/newsletters/distill/conformance.py` (test-utility) — SOCK-05

**Analog:** `tests/test_semantic.py:1-55` (assertion style, helper-fixture builders like `_session()`/
`_report()`).

**Copy guidance:** A reusable `assert_conforms(backend, sources) -> DistillationResult` that asserts:
`isinstance(backend, DistillPort)`; return type is `DistillationResult`; coverage present + internally
honest (the validator does the heavy lifting); every emitted claim passes `StructuralFaithfulness`;
lossless JSON round-trip `DistillationResult.model_validate_json(r.model_dump_json()) == r` (D-04, free in
Pydantic v2 — see Shared Patterns); and the socket produced no published anything (hard rule). Keep this in
`distill/` (importable by any backend's tests), distinct from `tests/test_distill_socket.py` which *drives* it.

---

### `src/newsletters/distill/__init__.py` (barrel) — public API

**Analog:** `src/newsletters/__init__.py:14-75` (EXACT — module docstring → relative imports → `__all__`).

**Pattern** (`__init__.py:14-17,58-75`):
```python
"""<module purpose, citing docs>."""
from .capture import Decision, WorkSession, build_report, capture_session
from .semantic import (Claim, ClaimsBlock, ... )
__all__ = [ "Source", "Trace", "Claim", ... ]
```

**Copy guidance:** Re-export `DistillPort`, `DistillationResult`, `FaithfulnessCheck`,
`StructuralFaithfulness`, `register`/`resolve`/`available`, `ManualBackend`, `Coverage`, `Unextracted`,
`Locator` (+ variants), with a docstring citing the socket contract. Optionally surface the socket from the
package root `src/newsletters/__init__.py` too — but **leave `synthesize()` as the external stub**
(`semantic.py:407-419`; `test_synthesize_is_external_stub` must stay green — RESEARCH Open Q3).

---

### `src/newsletters/semantic.py` — widen `Trace.locator` (in-place modify) — D-06

**Current shape** (`semantic.py:57-61`, verified live):
```python
class Trace(BaseModel):
    """A pointer from a claim to its evidence: a ``Source`` and a locator within it."""
    source_id: str
    locator: str = ""
```

**Constraint:** `capture.py:68` constructs `Trace(source_id=d.source_id, locator=d.locator)` with a bare
`str`, and `tests/test_semantic.py` builds `Trace`/omits locator. Widening MUST stay backward-compatible.

**Copy guidance (RESEARCH Pattern 4, Option a + Pitfall 1):** change `locator: str` →
`locator: Locator = Field(default_factory=FreeLocator)` and add a `field_validator(mode="before")` (or
`model_validator(mode="before")`) that coerces a plain `str` into `FreeLocator(text=...)` and passes
`Locator` instances/dicts through. Add `span: str = ""` to `Trace` (the verbatim source text, D-06 — one
place, all modalities). Import `Locator`/`FreeLocator` from `.locators` — the **top-level leaf module**
`src/newsletters/locators.py` (NOT `.distill.locators`; importing from the distill package would run
`distill/__init__.py` → eager-import `ports` → `..semantic` mid-init and re-introduce the cycle). This
mirrors the existing `from .templates import ...` leaf import and stays genuinely acyclic because
`locators.py` imports nothing from `semantic.py` or `distill`. **Regression tripwire:**
`pytest tests/test_semantic.py -q` MUST be green after the change.

---

### `tests/test_distill_socket.py` (test) — all SOCK reqs + hard rules

**Analog:** `tests/test_semantic.py:1-55` (EXACT — import-from-`newsletters` style, small helper builders,
one focused `test_*` per behavior).

**Pattern** (`test_semantic.py:1-40`):
```python
import pytest
from newsletters import (Claim, Source, Trace, WorkSession, Decision, ...)

def _session() -> WorkSession:
    return WorkSession(id="s1", title="t", tool="Claude Code", sources=[Source(id="s1")],
        decisions=[Decision(text="we decided X", source_id="s1", topics=["core"])])
```

**Copy guidance:** One test per RESEARCH Test Map row — `test_distillport_is_backend_agnostic`,
`test_registry_register_resolve`, `test_manual_backend_zero_ai_traced`,
`test_coverage_unextracted_distinct_from_missing`, `test_conformance_fails_bad_backend`,
`test_sidecar_roundtrip`, `test_locator_union_and_backward_compat`, `test_socket_never_auto_publishes`,
`test_distill_package_imports_no_ai` (assert no `langchain`/`langgraph`/`langsmith`/`pydantic_ai` in
`sys.modules` after `import newsletters.distill`). Reuse `_session()`-style builders; add a tiny
intentionally-broken backend fixture (untraced claim / lying coverage) for the SOCK-05 negative test.

---

## Shared Patterns

### Discriminated union (for `Locator`)
**Source:** `src/newsletters/semantic.py:273-287` (`Block`)
**Apply to:** `locators.py` (and any future locator variants in adapter phases)
`Annotated[Union[...], Field(discriminator="kind")]` with each variant carrying `kind: Literal[...]`.

### Module-level dict registry
**Source:** `src/newsletters/templates.py:165-184`
**Apply to:** `registry.py`
`_REGISTRY: dict[str, T]` + `register`/`resolve`/`available`, `KeyError(... Known: {sorted(...)}) from None`.

### Self-consistency validator that raises (honesty / gate invariants)
**Source:** `src/newsletters/semantic.py:142-150` (`Review._published_requires_satisfied_policy`)
**Apply to:** `coverage.py` (`complete` vs non-empty `unextracted[]`); the no-auto-publish hard rule it
enforces is what the socket must NOT route around.

### Lossless JSON sidecar round-trip (D-04)
**Source:** Pydantic v2 framework (`model_dump_json()` / `model_validate_json()`) — no custom encoder.
**Apply to:** `DistillationResult` persistence + the conformance round-trip assertion.

### Public-API barrel
**Source:** `src/newsletters/__init__.py:14-75`
**Apply to:** `distill/__init__.py` — docstring, relative imports, explicit `__all__`.

### Test conventions
**Source:** `tests/test_semantic.py:1-55`
**Apply to:** `tests/test_distill_socket.py` and `conformance.py` assertions.

### Reuse, don't reimplement
- `capture.capture_session()` (`capture.py:58-78`) — the manual modality engine.
- `Claim.is_traced` (`semantic.py:72-74`) — the `StructuralFaithfulness` default.
- `Distillation.missing[]` (`semantic.py:163`) — the UNPROVABLE gap (distinct from `unextracted[]`).

---

## No Analog Found

| File/Construct | Role | Reason | Planner Guidance |
|------|------|--------|------------------|
| `DistillPort` / `FaithfulnessCheck` (`typing.Protocol`) | contract | No `Protocol` exists in the repo yet — all current interfaces are concrete Pydantic models. | Use ARCHITECTURE.md Pattern 1 (`@runtime_checkable Protocol`) + RESEARCH Pattern 1/5. Add a `mypy src/newsletters/distill` gate since Protocols fail at call-time. |
| `DistillationResult` wrapper | model | No existing "wraps a domain type + adds a manifest" type. | Follow `Distillation`/`Claim` model conventions; resolve wrapper-vs-field in plan-check (RESEARCH Open Q1). |

---

## Metadata

**Analog search scope:** `src/newsletters/` (semantic.py, capture.py, templates.py, __init__.py), `tests/`
**Files scanned:** 6 (all read this session; all RESEARCH-cited line numbers verified live)
**Pattern extraction date:** 2026-06-14
