# Walking Skeleton — Newsletters (Distill Socket)

**Phase:** 1
**Generated:** 2026-06-14
**Revised:** 2026-06-14 (cross-AI review: Locator union relocated to a top-level leaf module to fix a circular import — see the Layout / Evidence-anchor rows)

> This is a **library** walking skeleton, not a web app. "End-to-end" here means a caller
> can go from raw inputs all the way to a valid, JSON-round-trippable `DistillationResult`
> through the `DistillPort` boundary, with the pipeline never knowing which backend ran —
> all with zero AI. The "deployment" is the importable `newsletters.distill` package plus a
> green test suite that exercises the full path.

## Capability Proven End-to-End

An operator can register a distill backend by name, call `resolve("manual").distill(sources)`
through the `DistillPort` boundary, and receive a valid `DistillationResult` (a traced
`Distillation` + a `Coverage` manifest) that serializes losslessly to/from a JSON sidecar —
with zero AI imports reachable from `newsletters.distill`.

## Architectural Decisions

> These are the contract every later phase (adapters 4–7, AI backend v2, provenance/faithfulness 3,
> site 8–9) builds on **without renegotiating**. Changing one is a conversation, not a commit.

| Decision | Choice | Rationale |
|---|---|---|
| The one boundary | `DistillPort` = `@runtime_checkable typing.Protocol` with `name: str` + `distill(sources: list[Source]) -> DistillationResult` | SOCK-01. Structural interface: an operator drops in a backend by *shape*, no base-class inheritance. ARCHITECTURE.md Pattern 1. The runtime conformance suite (not mypy) is the malformed-backend guard, since `@runtime_checkable` only checks attribute presence. |
| Backend selection | Module-level `dict[str, DistillPort]` registry (`register`/`resolve`/`available`), namespaced under `newsletters.distill.registry` | SOCK-02. Copies the proven in-repo `templates.py:165-184` idiom; zero deps; entry points are a later non-breaking extension. NOT re-exported as bare top-level `register`/`resolve` — the package root already exports `templates.register` (src/newsletters/__init__.py:69) and a distill `register` at root would shadow it. (There is no `templates.resolve`; only `register` collides.) |
| Return shape | New `DistillationResult` wrapper = existing `Distillation` + new `Coverage` + `backend: str` (audit only) | SOCK-04, D-04, D-05. Wrapping (not mutating `Distillation`) keeps the Rev1 type and its tests/serialization stable, and puts the two honesties side by side. Resolves RESEARCH Open Q1. |
| Two kinds of honesty | `Distillation.missing[]` (UNPROVABLE, reused) stays distinct from `Coverage.unextracted[]` (UNREADABLE, new) | D-05. Never collapse them. A `model_validator` makes "complete but with unextracted content" impossible. |
| Evidence anchor | `Trace.locator` widened from bare `str` to a discriminated `Locator` union (`FreeLocator` + `SessionLocator` now; adapter variants stubbed), backward-compatible via an idempotent `str → FreeLocator` coercion; plus a verbatim `span: str` on `Trace`. The `Locator` union lives in a **top-level leaf module `src/newsletters/locators.py`** (a sibling of `semantic.py`), NOT inside the `distill` package. | D-06. Typed, extensible to every source type with no contract churn; carries the verbatim span so "faithful, not suggestive" is visible at author/review time and feeds the Phase-3 span-containment check. **Leaf placement is load-bearing:** if the union lived under `distill/`, `semantic.py` importing it would trigger `distill/__init__.py` → `ports` → `..semantic` mid-init → circular import (caught by cross-AI review). A top-level leaf both `semantic` and `distill` import keeps the graph acyclic — mirroring the existing `semantic → templates` leaf import. |
| Manual backend | `ManualBackend(name="manual")` wraps the existing deterministic `capture.capture_session()`; the `WorkSession` is **constructor-injected** so `distill(sources)` stays signature-exact | SOCK-03, D-01(a), D-02. Reuse, don't reimplement (RESEARCH Pitfall 2 / Open Q2). Zero AI, zero network. |
| Faithfulness seam | `FaithfulnessCheck` Protocol + `StructuralFaithfulness` default (claim is OK iff traced), **injectable**, enforced in ONE place at the socket boundary (`_enforce`) | Leaves the seam for Phase 3 (PROV-02) to fill with deterministic span-containment by swapping the injected checker — no backend change. RESEARCH Pattern 5 / Open Q5. |
| Cost/effort posture | `Coverage.cost_hint` + `Coverage.effort_hint` | D-03. Carries the low-token-preference signal so an operator can choose the cheap path; generic, not bespoke. |
| Layout | Add a NEW `src/newsletters/distill/` package beside the flat layout, PLUS a top-level leaf module `src/newsletters/locators.py` for the `Locator` union; do NOT do the larger `core/` re-layout | Smallest change that ships the contract without disturbing the merged Rev1 spine. The leaf `locators.py` is the acyclic-import fix (see Evidence anchor). RESEARCH A6 / Open Q (re-layout deferred). |
| `synthesize()` | Left untouched as the external/AI stub (still raises `NotImplementedError`) | Open Q3. The socket sits beside it; `test_synthesize_is_external_stub` stays green. |
| Interpreter | Python 3.12 venv (`pip install -e ".[dev,test]"`, `mypy` added to `[dev]`) | Project targets 3.12 (`[tool.mypy] python_version`); base shell is 3.11 and lacks pydantic/pytest. Wave 0 stands up the venv. |

## Stack Touched in Phase 1

Library adaptation of the standard skeleton checklist:

- [x] Project scaffold — Python 3.12 venv, editable install with dev/test extras, `mypy` added to `[dev]`, pytest configured (Wave 0)
- [x] "Routing" → the `DistillPort` boundary + registry (`resolve(name).distill(...)`)
- [x] "Database read/write" → lossless JSON sidecar round-trip (`model_dump_json` / `model_validate_json`)
- [x] "UI interaction wired to API" → `ManualBackend` (author-by-hand) called through the socket end-to-end
- [x] "Deployment / full-stack run" → importable `newsletters.distill` package + green `pytest -q` (Rev1 + new suite) exercising the full path, with a fresh-interpreter import-order check guarding the acyclic graph

## Out of Scope (Deferred to Later Slices)

> Explicit so later phases do not re-litigate Phase 1's minimalism.

- The **extraction backends** (email/excel/pptx/power-bi adapters) — Phases 4–7. Their `Locator`
  variants (`MessageLocator`/`CellLocator`/`SlideLocator`/`CodeLocator`) are stubbed as commented
  contract reach only (in the leaf `locators.py`).
- The **agentic interview / AI backend** — v2 AI track (AI-01/02). Its `TurnLocator` is stubbed.
- **Content-addressed traces** (hash + offset) and the **real span-containment faithfulness gate** —
  Phase 3 (PROV-01/02). Phase 1 leaves the injectable seam with a permissive structural default.
- **AI-optional packaging boundary / import-linter / bare-install CI** — Phase 2 (PKG-01..04).
  Phase 1 only guarantees `distill/` imports no AI; it does NOT fix `pyproject.toml`'s core deps.
- **Reviewer surfacing** of `missing[]`/`unextracted[]` on rendered surfaces — Phase 10 (PROV-03).
  Phase 1 only guarantees the contract *carries* them.
- The larger `core/` package re-layout from ARCHITECTURE.md — a dedicated later refactor.
- Entry-point backend discovery (`importlib.metadata`) — a later non-breaking extension; the dict
  registry suffices now.

## Subsequent Slice Plan

Each later phase adds one slice on top of this skeleton without altering its architectural decisions:

- Phase 2: AI-optional packaging boundary — make `pip install .` (no extras) run the spine with zero AI; CI-enforce it.
- Phase 3: Content-address every `Trace` (hash + offset) and fill the faithfulness seam with deterministic span-containment.
- Phase 4: Shared `normalize()` + Email adapter — the first extraction backend through the same `DistillPort`.
- Phases 5–7: Excel / PowerPoint / Power BI adapters — each a new `Locator` variant + backend, same contract.
- Phases 8–9: `Site/Collection/Page` model + Rev2 site IA (depends only on Phase 1 type shapes).
