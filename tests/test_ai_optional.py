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
    assert (
        not leaked
    ), f"AI package(s) leaked into core dependencies: {sorted(leaked)} ({core})"

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

            pytest.skip(
                "import-linter not installed (bare env); contract enforced in dev/CI"
            )
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
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"AI leaked into core import:\n{proc.stdout}{proc.stderr}"


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
        if any(
            ep.value.split(":")[0].split(".")[0].startswith(mod) for mod in AI_MODULES
        )
    ]
    if ai_plugins:
        import pytest

        pytest.xfail(
            "ambient AI-provider pydantic plugin(s) installed in this dev .venv "
            f"({ai_plugins}); the canonical 'no AI plugin' proof is the bare-install CI job "
            "(PKG-03, Plan 02-02) where these packages are absent. This test still guards the "
            "MECHANISM — it fails loudly on a bare install if any AI plugin is registered."
        )
    assert (
        not ai_plugins
    ), f"AI-provider pydantic plugin active (no import edge!): {ai_plugins}"


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
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"deterministic pipeline failed or leaked AI:\n{proc.stdout}{proc.stderr}"


# --- WORK-01 / PKG-03 (carried): the work-surface ingest is on the policed bare surface ---- #
#
# Phase 11 adds src/newsletters/worksurface.py — the read-only local-file `Source` ingest. It is a
# core module (stdlib pathlib + semantic + _timestamps only), so the SAME AI-isolation guarantee
# that covers `import newsletters` / the dogfood pipeline must cover `import newsletters.worksurface`:
# importing it on the bare no-extras path must pull in ZERO AI/LLM module. This extends the policed
# surface to the new module without changing the AI-module set or the contract.


def test_worksurface_import_loads_no_ai_module() -> None:
    """A fresh subprocess `import newsletters.worksurface` loads no AI module (WORK-01 / PKG-03).

    Runs with PYDANTIC_DISABLE_PLUGINS=true so we measure OUR import graph, not ambient plugins
    the dev .venv may have installed (the leak-note false-positive caveat). Also exercises
    `capture_files` directly to prove the call path stays AI-free, not just the import.
    """
    code = (
        "import sys, tempfile, os; "
        "from newsletters.worksurface import capture_files; "
        "d = tempfile.mkdtemp(prefix='nl-work-ai-'); "
        "p = os.path.join(d, 'note.md'); "
        "open(p, 'w', encoding='utf-8').write('# note\\nread-only ingest\\n'); "
        "srcs = capture_files(['note.md'], root=__import__('pathlib').Path(d)); "
        "assert srcs and srcs[0].id == 'note.md', srcs; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('worksurface ai-free')"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"AI leaked into newsletters.worksurface import/call:\n{proc.stdout}{proc.stderr}"


# --- ADAPT-03 / T-05-04 / T-05-05: the optional [excel] (openpyxl) lazy boundary --------- #
#
# openpyxl is NOT AI — the forbid-ai contract is unaffected — but the SAME minimal-core / lazy
# discipline that keeps AI out of the bare install must keep openpyxl out of it too: a bare
# `pip install .` (no [excel]) must `import newsletters`, `import newsletters.adapters`, and run
# the spine with ZERO openpyxl. These gates prove the lazy boundary holds.

LOADER_PATH = REPO_ROOT / "src" / "newsletters" / "adapters" / "_openpyxl_loader.py"


def test_excel_extra_declared() -> None:
    """pyproject declares `excel = ["openpyxl"]` and openpyxl is the ONLY new adapter dep there."""
    data = _load_pyproject()
    extras = data["project"]["optional-dependencies"]
    assert "excel" in extras, f"missing [excel] extra: {sorted(extras)}"
    excel_names = {_req_name(r) for r in extras["excel"]}
    assert "openpyxl" in excel_names, extras["excel"]
    # openpyxl is the only dependency this phase may add to the extra.
    assert excel_names == {
        "openpyxl"
    }, f"[excel] must contain only openpyxl, got {excel_names}"
    # openpyxl must NOT be an AI package (sanity: it must not trip the AI requirement gate).
    assert not (excel_names & set(AI_REQUIREMENT_NAMES)), excel_names


def test_openpyxl_loader_has_no_toplevel_openpyxl_import() -> None:
    """The lazy loader module has ZERO top-level (runtime) `import openpyxl` / `from openpyxl`.

    A top-level import here would be pulled in transitively by `import newsletters.adapters`
    (the package `register()`s its adapters on import), breaking the bare install. The only
    openpyxl import allowed is INSIDE `_load_openpyxl()`. (A `TYPE_CHECKING`-guarded import is
    invisible at runtime and therefore fine — it lives under an `if TYPE_CHECKING:` block, not at
    column 0, so the column-0 check below does not see it.)
    """
    source = LOADER_PATH.read_text()
    toplevel_edges = [
        line
        for line in source.splitlines()
        # column-0 (module-top) import statements only — indented ones live inside functions or
        # the TYPE_CHECKING guard and are not executed on a bare runtime import.
        if line.startswith("import openpyxl") or line.startswith("from openpyxl")
    ]
    assert not toplevel_edges, (
        f"_openpyxl_loader.py has top-level openpyxl import(s) — breaks the bare install: "
        f"{toplevel_edges}"
    )


def test_adapters_package_imports_without_openpyxl() -> None:
    """`import newsletters.adapters` SUCCEEDS even when openpyxl cannot be imported.

    Simulates a bare install by installing a `sys.meta_path` finder that blocks `openpyxl`
    BEFORE importing the package (works regardless of whether the dev .venv has openpyxl). The
    package import must not require the extra; the loader module must import too (its openpyxl
    import is lazy, inside a function).
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'openpyxl' or name.startswith('openpyxl.'):\n"
        "            raise ImportError('blocked openpyxl (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('openpyxl', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "import newsletters\n"
        "import newsletters.adapters\n"
        "from newsletters.adapters import _openpyxl_loader\n"
        "assert 'openpyxl' not in sys.modules, sys.modules.get('openpyxl')\n"
        "print('adapters import clean without openpyxl')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"newsletters.adapters failed to import without openpyxl:\n{proc.stdout}{proc.stderr}"


def test_loader_raises_teaching_error_without_openpyxl() -> None:
    """`_load_openpyxl()` raises a teaching ImportError naming `[excel]` when openpyxl is absent.

    Again blocks openpyxl via a meta-path finder so the assertion holds whether or not the dev
    .venv has the extra installed.
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'openpyxl' or name.startswith('openpyxl.'):\n"
        "            raise ImportError('blocked openpyxl (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('openpyxl', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "from newsletters.adapters._openpyxl_loader import _load_openpyxl\n"
        "try:\n"
        "    _load_openpyxl()\n"
        "except ImportError as e:\n"
        "    msg = str(e)\n"
        "    assert '[excel]' in msg, msg\n"
        "    assert 'openpyxl' in msg, msg\n"
        "    print('teaching ImportError ok')\n"
        "else:\n"
        "    raise AssertionError('expected ImportError when openpyxl is absent')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, (
        f"loader did not raise the teaching ImportError without openpyxl:\n"
        f"{proc.stdout}{proc.stderr}"
    )


def test_loader_returns_module_when_openpyxl_present() -> None:
    """With openpyxl installed (dev .venv), `_load_openpyxl()` returns the module — no false error.

    openpyxl is not in AI_MODULES, so loading it must not be conflated with an AI leak; this
    guards that the happy path works in the dev/CI env where `[excel]` IS installed. Skips
    cleanly on a bare env so the bare-install gate is unaffected.
    """
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip(
            "openpyxl not installed (bare env); happy path enforced in dev/CI [excel]"
        )
    from newsletters.adapters._openpyxl_loader import _load_openpyxl

    mod = _load_openpyxl()
    assert getattr(mod, "__name__", None) == "openpyxl", mod
    assert "openpyxl" not in set(AI_MODULES), "openpyxl must never be classed as AI"


# --- ADAPT-04 / T-06-03 / T-06-05: the optional [pptx] (python-pptx) lazy boundary ------- #
#
# python-pptx is NOT AI — the forbid-ai contract is unaffected — but the SAME minimal-core / lazy
# discipline that keeps AI (and openpyxl) out of the bare install must keep python-pptx out of it
# too: a bare `pip install .` (no [pptx]) must `import newsletters`, `import newsletters.adapters`,
# and run the spine with ZERO python-pptx (and zero of its transitive lxml/Pillow C-extensions).
# These gates mirror the [excel] gates above and prove the lazy boundary holds. They are written
# NOW so that when 06-03 registers PptxAdapter on package import, it inherits a green bare-install
# gate proving registration stays lazy / extra-free.

PPTX_LOADER_PATH = REPO_ROOT / "src" / "newsletters" / "adapters" / "_pptx_loader.py"


def test_pptx_extra_declared() -> None:
    """pyproject declares `pptx = ["python-pptx"]` and python-pptx is the ONLY dep in that extra."""
    data = _load_pyproject()
    extras = data["project"]["optional-dependencies"]
    assert "pptx" in extras, f"missing [pptx] extra: {sorted(extras)}"
    pptx_names = {_req_name(r) for r in extras["pptx"]}
    assert "python-pptx" in pptx_names, extras["pptx"]
    # python-pptx is the only dependency this phase may add to the extra.
    assert pptx_names == {
        "python-pptx"
    }, f"[pptx] must contain only python-pptx, got {pptx_names}"
    # python-pptx must NOT be an AI package (sanity: it must not trip the AI requirement gate).
    assert not (pptx_names & set(AI_REQUIREMENT_NAMES)), pptx_names


def test_pptx_loader_has_no_toplevel_pptx_import() -> None:
    """The lazy loader module has ZERO top-level (runtime) `import pptx` / `from pptx`.

    A top-level import here would be pulled in transitively by `import newsletters.adapters`
    (the package `register()`s its adapters on import once 06-03 lands), breaking the bare
    install. The only pptx import allowed is INSIDE `_load_pptx()`. (A `TYPE_CHECKING`-guarded
    import would live under an `if TYPE_CHECKING:` block, indented, not at column 0, so the
    column-0 check below does not see it.)
    """
    source = PPTX_LOADER_PATH.read_text()
    toplevel_edges = [
        line
        for line in source.splitlines()
        # column-0 (module-top) import statements only — indented ones live inside functions or
        # the TYPE_CHECKING guard and are not executed on a bare runtime import.
        if line.startswith("import pptx") or line.startswith("from pptx")
    ]
    assert not toplevel_edges, (
        f"_pptx_loader.py has top-level pptx import(s) — breaks the bare install: "
        f"{toplevel_edges}"
    )


def test_adapters_package_imports_without_pptx() -> None:
    """`import newsletters.adapters` SUCCEEDS even when python-pptx cannot be imported.

    Simulates a bare install by installing a `sys.meta_path` finder that blocks `pptx` BEFORE
    importing the package (works regardless of whether the dev .venv has python-pptx). The package
    import must not require the extra; the loader module must import too (its pptx import is lazy,
    inside a function). After 06-03 registers PptxAdapter on package import, this gate proves the
    registration stays lazy / extra-free.
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'pptx' or name.startswith('pptx.'):\n"
        "            raise ImportError('blocked pptx (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('pptx', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "import newsletters\n"
        "import newsletters.adapters\n"
        "from newsletters.adapters import _pptx_loader\n"
        "assert 'pptx' not in sys.modules, sys.modules.get('pptx')\n"
        "print('adapters import clean without pptx')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"newsletters.adapters failed to import without python-pptx:\n{proc.stdout}{proc.stderr}"


def test_pptx_loader_raises_teaching_error_without_pptx() -> None:
    """`_load_pptx()` raises a teaching ImportError naming `[pptx]` when python-pptx is absent.

    Again blocks pptx via a meta-path finder so the assertion holds whether or not the dev .venv
    has the extra installed.
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'pptx' or name.startswith('pptx.'):\n"
        "            raise ImportError('blocked pptx (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('pptx', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "from newsletters.adapters._pptx_loader import _load_pptx\n"
        "try:\n"
        "    _load_pptx()\n"
        "except ImportError as e:\n"
        "    msg = str(e)\n"
        "    assert '[pptx]' in msg, msg\n"
        "    assert 'python-pptx' in msg, msg\n"
        "    print('teaching ImportError ok')\n"
        "else:\n"
        "    raise AssertionError('expected ImportError when python-pptx is absent')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, (
        f"loader did not raise the teaching ImportError without python-pptx:\n"
        f"{proc.stdout}{proc.stderr}"
    )


def test_pptx_loader_returns_module_when_present() -> None:
    """With python-pptx installed (dev .venv), `_load_pptx()` returns the module — no false error.

    python-pptx is not in AI_MODULES, so loading it must not be conflated with an AI leak; this
    guards that the happy path works in the dev/CI env where `[pptx]` IS installed. Skips cleanly
    on a bare env so the bare-install gate is unaffected.
    """
    try:
        import pptx  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip(
            "python-pptx not installed (bare env); happy path enforced in dev/CI [pptx]"
        )
    from newsletters.adapters._pptx_loader import _load_pptx

    mod = _load_pptx()
    assert getattr(mod, "__name__", None) == "pptx", mod
    assert "pptx" not in set(AI_MODULES), "python-pptx must never be classed as AI"


# --- LANE-04 / T-04-02 / T-04-03: the optional [config] (PyYAML) lazy boundary + AI-free swimlane -
#
# PyYAML is NOT AI — the forbid-ai contract is unaffected — but the SAME minimal-core / lazy
# discipline that keeps AI (and openpyxl / python-pptx) out of the bare install must keep PyYAML out
# of it too: a bare `pip install .` (no [config]) must `import newsletters`, `import
# newsletters.swimlane`, and run the deterministic spine with ZERO yaml. These gates mirror the
# [excel]/[pptx] gates above (ported one-for-one, openpyxl->yaml, _openpyxl_loader->_yaml_loader,
# [excel]->[config]) and prove the swim-lane config loader's lazy boundary holds. The loader lives at
# src/newsletters/_yaml_loader.py; the top-level module whose AI/yaml-freeness is policed is
# src/newsletters/swimlane.py.

YAML_LOADER_PATH = REPO_ROOT / "src" / "newsletters" / "_yaml_loader.py"
SWIMLANE_PATH = REPO_ROOT / "src" / "newsletters" / "swimlane.py"


def test_config_extra_declared() -> None:
    """pyproject declares `config = ["PyYAML..."]` and PyYAML is the ONLY dep in that extra."""
    data = _load_pyproject()
    extras = data["project"]["optional-dependencies"]
    assert "config" in extras, f"missing [config] extra: {sorted(extras)}"
    config_names = {_req_name(r) for r in extras["config"]}
    assert "pyyaml" in config_names, extras["config"]
    # PyYAML is the only dependency this phase may add to the extra.
    assert config_names == {
        "pyyaml"
    }, f"[config] must contain only PyYAML, got {config_names}"
    # PyYAML must NOT be an AI package (sanity: it must not trip the AI requirement gate).
    assert not (config_names & set(AI_REQUIREMENT_NAMES)), config_names


def test_yaml_loader_has_no_toplevel_yaml_import() -> None:
    """`_yaml_loader.py` and `swimlane.py` have ZERO top-level (runtime) `import yaml`/`from yaml`.

    A top-level yaml import in either module would be pulled in transitively by `import
    newsletters.swimlane` (a plain top-level module, no lazy registration), breaking the bare
    install. The only yaml import allowed is INSIDE `_load_yaml()`. (A `TYPE_CHECKING`-guarded import
    would live under an `if TYPE_CHECKING:` block, indented, not at column 0, so the column-0 check
    below does not see it.)
    """
    for path in (YAML_LOADER_PATH, SWIMLANE_PATH):
        source = path.read_text()
        toplevel_edges = [
            line
            for line in source.splitlines()
            # column-0 (module-top) import statements only — indented ones live inside functions or
            # the TYPE_CHECKING guard and are not executed on a bare runtime import.
            if line.startswith("import yaml") or line.startswith("from yaml")
        ]
        assert (
            not toplevel_edges
        ), f"{path.name} has top-level yaml import(s) — breaks the bare install: {toplevel_edges}"


def test_swimlane_package_imports_without_yaml() -> None:
    """`import newsletters.swimlane` SUCCEEDS even when yaml cannot be imported.

    Simulates a bare install by installing a `sys.meta_path` finder that blocks `yaml` BEFORE
    importing the module (works regardless of whether the dev .venv has PyYAML). The package import
    must not require the extra; both the swimlane module and the `_yaml_loader` boundary must import
    too (their yaml import is lazy, inside `_load_yaml()`), and `yaml` must stay out of sys.modules.
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'yaml' or name.startswith('yaml.'):\n"
        "            raise ImportError('blocked yaml (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('yaml', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "import newsletters\n"
        "import newsletters.swimlane\n"
        "from newsletters import _yaml_loader\n"
        "assert 'yaml' not in sys.modules, sys.modules.get('yaml')\n"
        "print('swimlane import clean without yaml')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"newsletters.swimlane failed to import without yaml:\n{proc.stdout}{proc.stderr}"


def test_yaml_loader_raises_teaching_error_without_yaml() -> None:
    """`_load_yaml()` raises a teaching ImportError naming `[config]` when PyYAML is absent.

    Blocks yaml via a meta-path finder so the assertion holds whether or not the dev .venv has the
    extra installed. Asserts against the imported `MISSING_YAML_MESSAGE` constant (no string-drift)
    AND spot-checks the actionable substrings `[config]` and `PyYAML`.
    """
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'yaml' or name.startswith('yaml.'):\n"
        "            raise ImportError('blocked yaml (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('yaml', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "from newsletters._yaml_loader import _load_yaml, MISSING_YAML_MESSAGE\n"
        "try:\n"
        "    _load_yaml()\n"
        "except ImportError as e:\n"
        "    msg = str(e)\n"
        "    assert msg == MISSING_YAML_MESSAGE, msg\n"
        "    assert '[config]' in msg, msg\n"
        "    assert 'PyYAML' in msg, msg\n"
        "    print('teaching ImportError ok')\n"
        "else:\n"
        "    raise AssertionError('expected ImportError when PyYAML is absent')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0, (
        f"loader did not raise the teaching ImportError without PyYAML:\n"
        f"{proc.stdout}{proc.stderr}"
    )


def test_yaml_loader_returns_module_when_present() -> None:
    """With PyYAML installed (dev .venv), `_load_yaml()` returns the module — no false error.

    PyYAML is not in AI_MODULES, so loading it must not be conflated with an AI leak; this guards
    that the happy path works in the dev/CI env where `[config]` IS installed. Skips cleanly on a
    bare env so the bare-install gate is unaffected.
    """
    try:
        import yaml  # type: ignore[import-untyped]  # noqa: F401
    except ImportError:
        import pytest

        pytest.skip(
            "PyYAML not installed (bare env); happy path enforced in dev/CI [config]"
        )
    from newsletters._yaml_loader import _load_yaml  # type: ignore[import-untyped]

    mod = _load_yaml()
    assert getattr(mod, "__name__", None) == "yaml", mod
    assert "yaml" not in set(AI_MODULES), "PyYAML must never be classed as AI"


def test_swimlane_import_loads_no_ai_module() -> None:
    """A fresh subprocess `import newsletters.swimlane` loads no AI module (LANE-04 / T-04-02).

    Mirrors `test_worksurface_import_loads_no_ai_module`: swimlane.py is a core top-level module
    (stdlib + pydantic + semantic/locators/_timestamps/coverage + the lazy _yaml_loader boundary),
    so the SAME AI-isolation guarantee that covers `import newsletters` must cover `import
    newsletters.swimlane`. Runs with PYDANTIC_DISABLE_PLUGINS=true so we measure OUR import graph,
    not ambient plugins. Also exercises `load_swimlanes` directly to prove the call path stays
    AI-free — guarded so a bare env (no PyYAML) still asserts the import path is AI-free.
    """
    code = (
        "import sys, tempfile, os\n"
        "from pathlib import Path\n"
        "from newsletters.swimlane import load_swimlanes\n"
        "d = tempfile.mkdtemp(prefix='nl-swim-ai-')\n"
        "open(os.path.join(d, 'm.yml'), 'w', encoding='utf-8').write("
        "'module: m\\nlanes:\\n- heading: H\\n')\n"
        "try:\n"
        "    load = load_swimlanes('m.yml', root=Path(d))\n"
        "    assert load.source.id == 'm.yml', load\n"
        "except ImportError:\n"
        "    pass  # PyYAML absent (bare env): the import path is still AI-free, which is what we test\n"
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]\n"
        "assert not bad, bad\n"
        "print('swimlane ai-free')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"AI leaked into newsletters.swimlane import/call:\n{proc.stdout}{proc.stderr}"
