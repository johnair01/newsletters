"""PROV-04 (enforcement) — the ``newsletters check`` CLI exit-code contract + CLI no-AI guard.

Plan 10-01 built the pure ``review_blockers`` checker and proved it FIRES on crafted negatives.
This suite proves the OPERATOR + CI entry point that turns that logic into an enforced merge gate:

* **L4 — the exit-code contract, both directions.** ``newsletters check`` runs ``review_blockers``
  across the corpus's PUBLISHED surfaces and the EXIT CODE is the CI contract:
    - the real (clean) shipped dogfood corpus -> **exit 0** (the gate is green on main); and
    - a corpus containing ONE blocked published surface -> **exit nonzero**, with the report naming
      the offending surface. A gate that only ever sees clean input proves nothing (Phase-7 lesson),
      so we monkeypatch the corpus builder to inject a blocker and assert the gate actually blocks.

* **L7 — the CLI is AI-free.** A fresh subprocess importing ``newsletters.cli`` pulls no AI module
  into the bare-install runtime (PKG-03 / PKG-04), mirroring tests/test_faithfulness_gate.py.

Tests drive ONLY the public CLI surface — Typer's ``CliRunner`` and a subprocess — never an internal
probe.
"""

from __future__ import annotations

import subprocess
import sys

from typer.testing import CliRunner

import newsletters.cli as cli
from newsletters.cli import app
from newsletters.semantic import Claim, ClaimsBlock, Source, Surface, Trace
from newsletters.templates import REPORT

runner = CliRunner()

AI_MODULES = ("langchain", "langgraph", "langsmith", "pydantic_ai", "openai", "anthropic")


def _blocked_published_surface() -> Surface:
    """One PUBLISHED Report surface with an un-entailed claim — a single, deterministic blocker.

    Mirrors Plan 10-01's UNENTAILED fixture (tests/test_review.py): an addressed trace over a
    transcript that does NOT contain the claim text. Not stale (the hash matches), so the checker
    reports exactly one UNENTAILED blocker — enough to flip the exit code.
    """
    transcript = "we discussed the roadmap and the budget"
    src = Source(id="s-blocked", transcript=transcript)
    trace = Trace.from_source(src, 0, len(transcript))  # addressed, but span omits the claim text
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    surface = Surface(
        id="sfc-blocked",
        template=REPORT,
        title="Crafted blocked surface",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
    )
    surface.publish(reviewer="reviewer-a")
    assert surface.is_published
    return surface


def test_cli_check_clean_corpus_passes() -> None:
    """``newsletters check`` on the real (clean) shipped corpus exits 0 with a clean report.

    The shipped dogfood corpus is content-addressed and never stale at capture time, so the gate
    MUST be green on main — the exit-0 half of the contract (RESEARCH Q-E).
    """
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "All published surfaces clean" in result.output


def test_cli_check_exits_nonzero_on_blocker(monkeypatch) -> None:
    """``newsletters check`` exits nonzero when the corpus carries a blocked published surface.

    Monkeypatch the corpus builder the command imports (``newsletters.dogfood.build_surfaces``) to
    return ONE crafted blocked surface, then assert the gate actually blocks: exit code != 0 and the
    report names the offending surface. This proves the gate FIRES — not just that it passes clean.
    """
    import newsletters.dogfood as dogfood

    monkeypatch.setattr(dogfood, "build_surfaces", lambda: [_blocked_published_surface()])

    result = runner.invoke(app, ["check"])
    assert result.exit_code != 0, result.output
    assert "sfc-blocked" in result.output
    assert "BLOCK" in result.output
    assert "merge blocked" in result.output


def test_cli_imports_no_ai() -> None:
    """A fresh subprocess importing ``newsletters.cli`` loads no AI module (AI-optional CLI runtime).

    Copies the test_faithfulness_gate.py no-AI subprocess guard, swapping in the CLI module — the
    merge-block CI job runs the CLI on the bare ``.[test]`` install, so importing the CLI must not
    pull any AI module into sys.modules.
    """
    code = (
        "import sys, newsletters.cli; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('clean')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"AI leaked: {proc.stdout}{proc.stderr}"


def test_cli_module_exposes_check_command() -> None:
    """The ``check`` command is registered on the Typer app (the CI entry point exists)."""
    names = {c.callback.__name__ for c in app.registered_commands}
    assert "check" in names
    assert callable(cli.check)
