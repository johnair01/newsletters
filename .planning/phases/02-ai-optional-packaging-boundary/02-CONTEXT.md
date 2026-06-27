# Phase 2: AI-Optional Packaging Boundary - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning
**Mode:** Smart-discuss → classified pure-infrastructure (no user-facing behavior; all success criteria technical). Grey-area Q&A skipped per smart-discuss infra rule; decisions below are informed discretion grounded in CLAUDE.md, REQUIREMENTS (PKG-01..04), and the Phase-1 leak finding.

<domain>
## Phase Boundary

Make the deterministic spine install and run with **zero AI dependencies**, and turn that into a
standing CI invariant every later phase must keep green. In scope: dependency reorganisation in
`pyproject.toml` (AI deps behind an `[ai]` extra, lazy-imported only inside the AI backend), a
bare-install CI gate, and an import-linter contract. OUT of scope: implementing the AI backend
itself (AI-01/02 are v2) and any runtime AI behaviour.
</domain>

<decisions>
## Implementation Decisions

### Dependency reorganisation (PKG-01, PKG-02)
- Core `dependencies` must contain only stdlib-adjacent runtime needs — currently `pydantic>=2`
  and `typer[all]`. Keep those; they are not AI.
- Move `pydantic-ai` OUT of core `dependencies` and into a new `[project.optional-dependencies]`
  `ai` extra. This is the direct fix for the Phase-1 logfire leak: `pydantic-ai` transitively
  pulls `logfire`, which only contaminates the import graph because it is a *core* dep today.
- **Drop `langsmith` entirely** — CLAUDE.md Out-of-Scope explicitly bars telemetry / external
  calls on content ("drop langsmith"). It must not appear in core OR the `[ai]` extra.
- **`langchain[anthropic]`**: the planned AI backend is pydantic-ai (AI-01), not langchain.
  Planner must verify there is no real usage and, if none, remove it. If some use exists, it goes
  in the `[ai]` extra, never core. Default expectation: remove.
- Resulting shape (planner to finalise): core = non-AI only; `[ai]` = `pydantic-ai` (+ any genuine
  AI-backend needs); `dev`/`test` unchanged except removing AI cruft.

### Enforcement — the gate is plugin-aware (PKG-03, PKG-04)
- **Source of truth = the bare no-extras install gate (PKG-03):** a CI job does `pip install .`
  (no extras), runs the full capture→review→render pipeline, and asserts no AI module is reachable
  from core. On a bare install logfire/pydantic-ai are simply absent, so the pydantic-plugin
  auto-activation path cannot fire.
- **Import-linter (PKG-04) is necessary-but-not-sufficient:** it catches static `import` edges
  from `core` → AI packages, but it will MISS plugin-based activation (there is no import edge).
  Document this limitation in the contract; do not rely on it alone.
- **Add a runtime guard for the plugin path:** after `import newsletters` on a bare install,
  assert `importlib.metadata.entry_points(group="pydantic")` contains no AI-provider plugins and
  `sys.modules` has no `logfire/pydantic_ai/openai/anthropic/langsmith`. See
  `.planning/notes/ai-optional-pydantic-plugin-leak.md` — this finding is the reason the gate must
  test runtime activation, not just static imports.

### Tooling / CI
- Keep the existing PEP 621 `pyproject.toml` + current build backend; do not switch packaging
  systems. Dev env stays uv-managed (`.venv` already is).
- CI: add the bare-install + import-linter jobs. If no CI workflow exists yet, create a minimal
  GitHub Actions workflow scoped to these gates (the planner confirms presence first).

### Claude's Discretion
- Exact extra naming beyond `ai`, import-linter config layout, and CI workflow file structure are
  at Claude's discretion, provided the four success criteria and the plugin-aware guard hold.
</decisions>

<code_context>
## Existing Code Insights

### Current state (scouted)
- `pyproject.toml` declares AI deps in CORE `dependencies`: `pydantic-ai` (L15), `langsmith` (L19),
  `langchain[anthropic]` (L20). These are the boundary violations to fix.
- Existing extras: `panel`, `dev` (pytest/black/ipdb/ipython/isort/mypy), `test`.
- Phase 1 established a clean `src/newsletters/distill/` with zero AI imports and a registry/port
  pattern; the future AI backend will register here behind the `[ai]` extra (lazy import).
- `.venv` is uv-managed and currently has `logfire` installed (ambient, from pydantic-ai as a core
  dep) — the contamination this phase removes.

### Integration Points
- The distill backend registry (`src/newsletters/distill/registry.py`) is where an AI backend will
  later plug in; this phase only ensures it CAN be optional, not that it exists.
</code_context>

<specifics>
## Specific Ideas

- Honour CLAUDE.md hard rule verbatim: "AI/LLM deps live behind an `[ai]` extra, lazy-imported
  inside the AI backend only; CI fails if any AI import is reachable from core."
- The Phase-1 leak note (`.planning/notes/ai-optional-pydantic-plugin-leak.md`) is a required input
  — the gate must catch pydantic-plugin activation, not only static imports.
</specifics>

<deferred>
## Deferred Ideas

- The actual `AIBackend` implementation and claim-level evidence UX (AI-01/AI-02) — v2, out of
  scope here. This phase only proves the spine runs without them.
</deferred>
