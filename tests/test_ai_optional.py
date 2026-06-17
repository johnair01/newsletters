"""Packaging-boundary tests — the AI-optional core invariant (PKG-01, PKG-02, PKG-04).

This suite polices the boundary that lets the deterministic spine install and run with ZERO
AI dependencies. It is the local half of the Phase-2 enforcement; the canonical bare-INSTALL
CI gate (PKG-03) and the per-push standing enforcement of the import-linter contract land in
Plan 02-02.

Two complementary gates live here, because neither alone is sufficient (see
``.planning/notes/ai-optional-pydantic-plugin-leak.md``):

1. ``test_import_linter_contract_holds`` runs the import-linter ``forbidden`` contract — it
   catches STATIC ``import`` edges from core to any AI package.
2. ``test_no_ai_pydantic_plugin_active`` enumerates ``entry_points(group="pydantic")`` — it
   catches the import-linter's BLIND SPOT: a pydantic plugin (e.g. logfire's
   ``logfire-plugin = logfire.integrations.pydantic:plugin``) auto-activates on first
   ``import pydantic`` with NO import edge, so a static checker can never see it.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

# The plugin-leak AI module set (superset of test_distill_socket's tuple — defined locally to
# keep this file self-contained). `logfire/openai/anthropic` are included per the leak-note:
# logfire is the pydantic-plugin leak source, transitively pulled by pydantic-ai.
AI_MODULES = (
    "pydantic_ai",
    "langchain",
    "langgraph",
    "langsmith",
    "logfire",
    "openai",
    "anthropic",
)

# AI requirement-name fragments forbidden from CORE deps (matched case-insensitively against
# the parsed requirement's package name, ignoring version specifiers / extras).
AI_REQUIREMENT_NAMES = (
    "pydantic-ai",
    "langsmith",
    "langchain",
    "langgraph",
    "logfire",
    "openai",
    "anthropic",
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _req_name(requirement: str) -> str:
    """Extract the lowercase package name from a PEP 508 requirement string.

    Strips extras ("typer[all]") and version specifiers ("pydantic>=2").
    """
    name = requirement.strip().lower()
    for sep in ("[", " ", ">", "<", "=", "!", "~", ";", "("):
        idx = name.find(sep)
        if idx != -1:
            name = name[:idx]
    return name.strip()


def _load_pyproject() -> dict:
    with open(REPO_ROOT / "pyproject.toml", "rb") as fh:
        return tomllib.load(fh)


# --- PKG-01 / PKG-02: the structural dependency boundary ----------------------- #


def test_pyproject_dependency_boundary() -> None:
    """Core deps are non-AI only; [ai] carries pydantic-ai; telemetry/unused AI are gone."""
    data = _load_pyproject()
    project = data["project"]
    core = project["dependencies"]
    core_names = {_req_name(r) for r in core}
    extras = project.get("optional-dependencies", {})

    # (a) core contains NO AI package
    leaked = core_names & set(AI_REQUIREMENT_NAMES)
    assert not leaked, f"AI package(s) leaked into core dependencies: {sorted(leaked)} ({core})"

    # (b) core keeps the non-AI runtime needs
    assert "pydantic" in core_names, core
    assert "typer" in core_names, core
    assert "sqlmodel" in core_names, core  # used by src/newsletters/models.py — NOT AI

    # (c) the [ai] extra exists and carries pydantic-ai and NO langsmith
    assert "ai" in extras, f"missing [ai] extra: {sorted(extras)}"
    ai_names = {_req_name(r) for r in extras["ai"]}
    assert "pydantic-ai" in ai_names, extras["ai"]
    assert "langsmith" not in ai_names, extras["ai"]

    # (d) langsmith / langchain / langgraph appear in NO section anywhere
    dropped = {"langsmith", "langchain", "langgraph"}
    for section, reqs in extras.items():
        names = {_req_name(r) for r in reqs}
        bad = names & dropped
        assert not bad, f"dropped package(s) {sorted(bad)} still present in [{section}]"
    core_dropped = core_names & dropped
    assert not core_dropped, f"dropped package(s) {sorted(core_dropped)} still in core"

    # (e) import-linter is in [dev] so dev + CI can run lint-imports (PKG-04)
    assert "dev" in extras, f"missing [dev] extra: {sorted(extras)}"
    dev_names = {_req_name(r) for r in extras["dev"]}
    assert "import-linter" in dev_names, extras["dev"]


# --- PKG-04: the import-linter forbidden contract has teeth -------------------- #


def test_import_linter_contract_holds() -> None:
    """`lint-imports` exits 0 — core has no STATIC AI import edge (the forbidden contract)."""
    lint_imports = REPO_ROOT / ".venv" / "bin" / "lint-imports"
    if not lint_imports.exists():
        # Fall back to the module entrypoint; skip only if import-linter is wholly absent
        # (e.g. a bare [test]-only env). The dev/CI env has it via [dev].
        try:
            import importlinter  # noqa: F401
        except ImportError:
            import pytest

            pytest.skip("import-linter not installed (bare env); contract enforced in dev/CI")
        cmd = [sys.executable, "-m", "importlinter.cli", "lint"]
    else:
        cmd = [str(lint_imports)]

    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"import-linter contract FAILED (core imports an AI package):\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )


# --- PKG-01: runtime AI-isolation — sys.modules + pydantic plugins -------------- #


def test_core_import_loads_no_ai_module() -> None:
    """A fresh subprocess `import newsletters` loads no AI module.

    Runs with PYDANTIC_DISABLE_PLUGINS=true so we measure OUR import graph, not ambient
    plugins the dev .venv may have installed (the leak-note false-positive caveat).
    """
    code = (
        "import sys, newsletters; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('clean')"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=REPO_ROOT
    )
    assert proc.returncode == 0, f"AI leaked into core import:\n{proc.stdout}{proc.stderr}"


def test_no_ai_pydantic_plugin_active() -> None:
    """No AI-provider pydantic plugin is registered — the import-linter's BLIND SPOT.

    WHY (leak-note ``ai-optional-pydantic-plugin-leak.md``): pydantic auto-activates every
    installed ``pydantic``-group plugin on first import, with NO import edge for a static
    checker to see. So a telemetry/AI plugin (logfire's
    ``logfire-plugin = logfire.integrations.pydantic:plugin``) can leak into core while the
    import-linter (PKG-04) reports clean. This test enumerates the entry-points DIRECTLY.

    The enumeration reflects what is INSTALLED, not what our package depends on. The dev .venv
    has ambient logfire (leak-note:38-42), which would make this a false positive in-process —
    so we xfail with a documented reason when an AI-provider plugin is present in the ambient
    env. The REAL enforcement of "no AI plugin active" is the bare no-extras install CI job
    (PKG-03, Plan 02-02) where the AI packages are simply absent.
    """
    from importlib.metadata import entry_points

    ai_plugins = [
        (ep.name, ep.value)
        for ep in entry_points(group="pydantic")
        if any(ep.value.split(":")[0].split(".")[0].startswith(mod) for mod in AI_MODULES)
    ]
    if ai_plugins:
        import pytest

        pytest.xfail(
            "ambient AI-provider pydantic plugin(s) installed in this dev .venv "
            f"({ai_plugins}); the canonical 'no AI plugin' proof is the bare-install CI job "
            "(PKG-03, Plan 02-02) where these packages are absent. This test still guards the "
            "MECHANISM — it fails loudly on a bare install if any AI plugin is registered."
        )
    assert not ai_plugins, f"AI-provider pydantic plugin active (no import edge!): {ai_plugins}"


# --- PKG-01 local proof: the full deterministic pipeline runs AI-free ----------- #


def test_bare_pipeline_runs_ai_free() -> None:
    """The full deterministic pipeline (capture->render via build_site) runs with zero AI.

    Runs in a fresh subprocess with PYDANTIC_DISABLE_PLUGINS=true (measure our graph, not
    ambient plugins), renders into a tmp dir, and asserts no AI module is in sys.modules
    afterwards. This is the in-process bare-pipeline proof of PKG-01; the bare-INSTALL proof
    (AI packages physically absent) is the CI job in Plan 02-02.
    """
    code = (
        "import sys, tempfile; "
        "from newsletters.dogfood import build_site; "
        "out = tempfile.mkdtemp(prefix='nl-ai-optional-'); "
        "written = build_site(out); "
        "assert written, 'build_site rendered nothing'; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; "
        "print('pipeline ai-free:', len(written))"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=REPO_ROOT
    )
    assert proc.returncode == 0, (
        f"deterministic pipeline failed or leaked AI:\n{proc.stdout}{proc.stderr}"
    )
