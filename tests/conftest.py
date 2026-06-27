"""Shared fixtures for the distill-socket test suite.

Mirrors the module-local ``_session()`` builder in ``tests/test_semantic.py`` but
exposes the builders as pytest fixtures, named DISTINCTLY (``work_session`` / ``sources``,
never ``_session``) to avoid shadowing that local helper (review LOW-1).
"""

from __future__ import annotations

import pytest

from newsletters import Decision, Source, WorkSession


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
