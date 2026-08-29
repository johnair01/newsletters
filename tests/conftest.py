"""Shared fixtures for the distill-socket test suite.

Mirrors the module-local ``_session()`` builder in ``tests/test_semantic.py`` but
exposes the builders as pytest fixtures, named DISTINCTLY (``work_session`` / ``sources``,
never ``_session``) to avoid shadowing that local helper (review LOW-1).

Also home to ``milestone_base_ref`` — the ONE definition of the base commit every diff-shape
gate in this repo compares against. Two copies of a base ref drift exactly as two copies of a
normalizer do.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from newsletters import Decision, Source, WorkSession

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def milestone_base_ref() -> str:
    """The milestone base: ``git merge-base HEAD origin/main`` — never ``HEAD`` itself.

    Every diff-shape gate resolves its base here, because ``git diff HEAD`` compares the WORKING
    TREE to the last commit: such a gate goes red on an uncommitted edit and green the instant it
    is committed, so in CI's clean checkout it can never fail. That bug shipped once in this repo
    (``test_compose.py``'s byte-freeze) and is fixed by routing every caller through this fixture.

    Unresolvable ⇒ **FAIL**, never skip. The usual cause is a shallow checkout; the fix is
    ``fetch-depth: 0`` on the job that runs the gate. A gate that is green because it never ran is
    not a gate (v1.3 W21, paid for once already).
    """
    result = subprocess.run(
        ["git", "merge-base", "HEAD", "origin/main"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        pytest.fail(
            "cannot resolve the milestone base ref `git merge-base HEAD origin/main` "
            f"(exit {result.returncode}): {result.stderr.strip()!r}. The usual cause is a shallow "
            "checkout — set `fetch-depth: 0` on the CI job that runs this gate. This is a FAILURE "
            "and never a skip."
        )
    return result.stdout.strip()


@pytest.fixture
def work_session() -> WorkSession:
    """A minimal WorkSession: one Source, one hand-authored Decision."""
    return WorkSession(
        id="s1",
        title="t",
        tool="Claude Code",
        sources=[Source(id="s1", context="ctx", transcript="we did X")],
        decisions=[Decision(text="we decided X", source_id="s1", locator="line 3", topics=["core"])],
    )


@pytest.fixture
def sources(work_session: WorkSession) -> list[Source]:
    """The Source[] a caller passes through ``distill(sources)``."""
    return list(work_session.sources)
