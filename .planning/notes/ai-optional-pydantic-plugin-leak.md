---
title: "AI-optional core can be silently broken by Pydantic plugin auto-activation"
date: 2026-06-17
context: "Found during Phase 1 Wave 1 independent gate re-run (autonomous run)"
severity: feeds-phase-2
consumed_by: Phase 2 (AI-Optional Packaging Boundary — PKG-01..04)
---

# Finding: pydantic plugin entry-points leak AI into "core"

## What happened

During independent verification of Phase 1 Wave 1, importing `newsletters.distill` in the
dev `.venv` pulled `logfire` (60+ modules) into `sys.modules` — apparently violating the
AI-optional-core rule.

## Root cause (localized, not assumed)

- **No source file imports logfire** (`grep -rn logfire src/` is empty). The core imports only
  stdlib + pydantic.
- `logfire` is installed in the `.venv` (`pip show logfire` → `Required-by:` empty — it's not a
  dependency of our package; it's ambient cruft in this environment).
- `logfire` registers a **Pydantic plugin** via entry-point group `pydantic`:
  `logfire-plugin = logfire.integrations.pydantic:plugin`.
- Pydantic **auto-activates every installed plugin** when `pydantic` is first imported. So any
  module that imports pydantic (i.e. all of core) transitively loads logfire — with zero static
  imports to show for it.
- Proof: `PYDANTIC_DISABLE_PLUGINS=true python -c "import newsletters.distill"` → **zero AI
  modules**. A bare interpreter that imports nothing of ours has no logfire.

## Why this matters for Phase 2 (PKG-01..04)

1. **A static import-linter (PKG-04) will NOT catch this** — there is no import edge. The rule
   "core imports only stdlib+pydantic" is statically true while being runtime-false.
2. The **bare no-extras install gate (PKG-03)** *does* catch it naturally — on a clean
   `pip install .` logfire isn't present, so pydantic finds no plugin. This is the real defense
   and must be the canonical gate.
3. The **runtime AI-isolation test** must not run in a dev venv that has AI tools installed, or it
   produces false positives/negatives depending on ambient packages. Run it on the bare install,
   OR harden it to assert no pydantic plugins from AI packages are active (e.g. enumerate
   `entry_points(group="pydantic")` and fail on known AI providers), OR run with
   `PYDANTIC_DISABLE_PLUGINS` to measure our own import graph specifically.

## Recommended Phase-2 guards (encode, don't vibe)

- Make PKG-03's bare-install CI job the source of truth for "no AI reachable from core."
- Add a complementary runtime assertion: after `import newsletters` on a bare install,
  `entry_points(group="pydantic")` contains no AI-provider plugins, and `sys.modules` has no
  `logfire/pydantic_ai/openai/anthropic/langsmith`.
- Document that the import-linter is necessary-but-not-sufficient (misses plugin activation).

## Phase-1 verdict

Not a Phase-1 defect. Phase-1 code is AI-clean. This is an environment + packaging concern that
Phase 2 owns. Logged so Phase-2 discuss/plan accounts for it.
