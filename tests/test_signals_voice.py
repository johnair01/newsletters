"""VOICE-01/02 — the ship workflow's PR bodies are Signals dispatches, proven by guard test.

Why this test exists: ``.claude/gsd-core/`` is managed by the GSD installer — an update can
silently overwrite ``ship.md``/``summary-standard.md`` and revert the Signals voice to the old
PRD boilerplate. These guards make that reversion a RED test instead of a quiet drift. They are
purely additive (no existing check is touched or weakened — VOICE-02).

The dispatch contract (VOICE-01, from the milestone seed §8): exactly five core sections —
The signal / What we learned / What's verified / What's not here yet / How to verify — generated
FROM the diff + gate output, gate output quoted verbatim, no AI framing, no fact-asserting
fallback boilerplate.
"""

from __future__ import annotations

import json
import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SHIP = _ROOT / ".claude" / "gsd-core" / "workflows" / "ship.md"
_SUMMARY_TPL = _ROOT / ".claude" / "gsd-core" / "templates" / "summary-standard.md"
_CONFIG = _ROOT / ".planning" / "config.json"

# The dispatch sections, in prescribed order. "Start here" is the client section (JJ's
# 2026-07-02 review: the reviewer is a client being taught — plain terms, clickable links,
# the rendered artifact first). It leads every body.
_DISPATCH_SECTIONS = [
    "## Start here",
    "## The signal",
    "## What we learned",
    "## What's verified",
    "## What's not here yet",
    "## How to verify",
]


def _pr_body_step(text: str) -> str:
    """The generate_pr_body step's text — the surface under contract."""
    m = re.search(r'<step name="generate_pr_body">(.*?)</step>', text, flags=re.DOTALL)
    assert (
        m
    ), "ship.md no longer has a generate_pr_body step — the voice contract is gone"
    return m.group(1)


def test_ship_pr_body_is_a_signals_dispatch() -> None:
    """The five dispatch sections exist in the prescribed order (VOICE-01)."""
    step = _pr_body_step(_SHIP.read_text(encoding="utf-8"))
    positions = []
    for heading in _DISPATCH_SECTIONS:
        pos = step.find(heading)
        assert pos != -1, f"ship.md generate_pr_body lost the {heading!r} section"
        positions.append(pos)
    assert positions == sorted(positions), (
        "the dispatch sections are out of order: "
        f"{[h for _, h in sorted(zip(positions, _DISPATCH_SECTIONS))]}"
    )


def test_ship_mandates_verbatim_gate_output_and_forbids_hype() -> None:
    """The evidence + voice rules are present: verbatim gates, no AI framing (VOICE-01)."""
    step = _pr_body_step(_SHIP.read_text(encoding="utf-8"))
    lowered = step.lower()
    assert "verbatim" in lowered, "the verbatim-gate-output mandate is gone"
    assert (
        "never paraphrased" in lowered or "never paraphrase" in lowered
    ), "the never-paraphrase rule is gone"
    assert "no ai framing" in lowered, "the no-AI-framing prohibition is gone"
    # The body must be tied to evidence, not intention.
    assert (
        "evidence rule" in lowered
    ), "the evidence rule (numerals/claims only from gates/diff/artifacts) is gone"


def test_ship_forbids_fact_asserting_fallbacks() -> None:
    """Configured-section fallbacks may not assert unverified facts (VOICE-01)."""
    step = _pr_body_step(_SHIP.read_text(encoding="utf-8"))
    assert (
        "may not assert a fact" in step.lower()
    ), "the configured-section evidence rule is gone"
    # The canonical offender must not reappear as an *example to follow*.
    assert (
        "No known high-risk rollout dependencies" not in step.split("forbidden")[-1]
    ), "the fact-asserting fallback example returned as guidance"


def test_ship_requires_the_client_section() -> None:
    """The client section's three mandatory parts survive (JJ review, 2026-07-02)."""
    step = _pr_body_step(_SHIP.read_text(encoding="utf-8"))
    for marker in ("What we built", "Why it matters to you", "How to review it"):
        assert marker in step, f"the client section lost its {marker!r} part"
    lowered = step.lower()
    assert "client" in lowered, "the reviewer-is-a-client framing is gone"
    assert (
        "rendered" in lowered and "link" in lowered
    ), "the link-the-rendered-artifact rule is gone"


def test_summary_template_feeds_the_dispatch() -> None:
    """summary-standard.md carries the two dispatch-feeding sections (VOICE-01)."""
    tpl = _SUMMARY_TPL.read_text(encoding="utf-8")
    assert "## The signal" in tpl, "summary template lost '## The signal'"
    assert (
        "## What's not here yet" in tpl
    ), 'summary template lost "## What\'s not here yet"'


def test_config_carries_no_boilerplate_pr_sections() -> None:
    """ship.pr_body_sections holds no fact-asserting fallback boilerplate (VOICE-01)."""
    cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
    sections = cfg.get("ship", {}).get("pr_body_sections", [])
    for section in sections:
        fallback = str(section.get("fallback", "")).lower()
        assert (
            "no known" not in fallback and "are covered" not in fallback
        ), f"pr_body_sections fallback asserts an unverified fact: {fallback!r}"
