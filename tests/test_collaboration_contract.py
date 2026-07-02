"""The collaboration contract is canonical and guarded (deep-review Round 9).

Presence guard, mirroring ``test_signals_voice.py``: the roles and load-bearing engagement
rules locked with the Editor-in-Chief (2026-07-02) must survive in CLAUDE.md and
``docs/collaboration.md``. Reverting the contract — by edit, installer clobber, or doc
rewrite — turns the suite RED instead of drifting silently ("rules become tests", the
contract's own rule 8). This is a presence check on load-bearing phrases, not prose police.
"""

from __future__ import annotations

import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CLAUDE_MD = _ROOT / "CLAUDE.md"
_CONTRACT = _ROOT / "docs" / "collaboration.md"

# The role vocabulary locked with the Editor-in-Chief — hats, not people.
_ROLES = ["Editor-in-Chief", "Bureau Chief", "Reporters", "Maintainer", "Contributor"]

# Load-bearing contract phrases (verbatim anchors, chosen to be stable).
_CONTRACT_ANCHORS = [
    "Roles are hats, not people",
    "owns intent",
    "sets pace",
    "keeps time",
    "The reviewer is a client being taught",
    "If the deliverable is visual, deploy it",
    "Everybody learns everywhere all the time",
    "a conversation, not a commit",
    "Rules become tests",
]

_CLAUDE_MD_ANCHORS = [
    "Editor-in-Chief",
    "Bureau Chief",
    "hats, not people",
    "docs/collaboration.md",
    "Everybody learns everywhere all the time",
]


def test_contract_document_exists_with_roles() -> None:
    """docs/collaboration.md exists and names every locked role."""
    assert (
        _CONTRACT.exists()
    ), "docs/collaboration.md (the collaboration contract) is gone"
    text = _CONTRACT.read_text(encoding="utf-8")
    for role in _ROLES:
        assert role in text, f"the contract lost the {role!r} role"


def test_contract_carries_the_load_bearing_rules() -> None:
    """The engagement rules locked with the Editor-in-Chief survive verbatim."""
    text = _CONTRACT.read_text(encoding="utf-8")
    for anchor in _CONTRACT_ANCHORS:
        assert anchor in text, f"the contract lost its load-bearing phrase {anchor!r}"


def test_claude_md_carries_the_roles_map() -> None:
    """CLAUDE.md (the map) names the roles and links the contract (the territory)."""
    text = _CLAUDE_MD.read_text(encoding="utf-8")
    for anchor in _CLAUDE_MD_ANCHORS:
        assert anchor in text, f"CLAUDE.md lost its roles-section anchor {anchor!r}"
