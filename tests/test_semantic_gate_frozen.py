"""The review gate, frozen by something that can actually fail in CI.

`src/newsletters/semantic.py` is the one file whose behaviour decides whether anything can reach
`Published`. Until v1.3 Phase 3 its protection was
`test_compose.py::test_faithfulness_coverage_semantic_templates_site_are_untouched`, which shells
`git diff HEAD -- <gate files>`. `git diff HEAD` compares the **working tree** to HEAD, so it goes
red on an *uncommitted* edit and green the moment that edit is committed. In CI — always a clean
checkout — it has never been capable of failing. It was an uncommitted-edit tripwire, not a
protection of the gate.

Phase 3 is also the phase that legitimately *extends* `semantic.py` (four block kinds join the
`Block` union), so the blanket byte-freeze had to go. It is replaced here, in the same phase that
makes it obsolete, by two INDEPENDENT halves — they fail for different reasons and one must
survive the other being unavailable:

**Half A — source-hash pins.** The eight functions that *are* the gate are pinned by the sha256 of
their own source text. Needs no git, so it runs in any checkout, any tarball, any wheel-installed
environment.

**Half B — diff shape.** Every `semantic.py` change in this phase is an ADDITION; a deleted line
means something was rewritten rather than extended. The base is `git merge-base HEAD origin/main`
— the milestone base, never `HEAD` — resolved through the `milestone_base_ref` fixture
(`tests/conftest.py`), which is the one definition of that ref in the suite. The fixture **FAILS**
rather than skips when it cannot resolve one: a gate that is green because it never ran is the
exact W21 failure this repo has already paid for once.
"""

from __future__ import annotations

import hashlib
import inspect
import subprocess
from pathlib import Path

import pytest

from newsletters.semantic import Review, Source, Surface, Trace

_REPO_ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# Half A — the eight gate functions, pinned by the sha256 of their source text
# --------------------------------------------------------------------------- #

# Each of these is load-bearing for "no auto-publish, ever" or for "every published claim traces
# to evidence" — the two hard rules in CLAUDE.md. They are frozen deliberately, not incidentally.
_GATE_FUNCTIONS = {
    "Source.content_hash": Source.content_hash,  # the content address every Trace pins
    "Trace.from_source": Trace.from_source,  # the SOLE content-addressed trace constructor
    "Review.satisfied": Review.satisfied,  # the policy arithmetic
    "Review._published_requires_satisfied_policy": (
        Review._published_requires_satisfied_policy
    ),  # the no-auto-publish validator
    "Surface._published_claims": Surface._published_claims,  # what invariant 2 inspects
    "Surface.open_pull_request": Surface.open_pull_request,  # the untraced-claim refusal
    "Surface.approve": Surface.approve,  # approval recording
    "Surface.publish": Surface.publish,  # the only path to Published
}

_FROZEN = {
    "Source.content_hash": "017520138e0d90aa89c11c0f9a47a6af4d48740718088dbd35210b8f65d67c0f",
    "Trace.from_source": "c7f05965d050300e03b48fb1a1a439f17811e630c727cd407fe3aac944c77191",
    "Review.satisfied": "77f91f1526613a8c84f2ac0e559925c9e03e866328cefd6fdd8de21d8db947e4",
    "Review._published_requires_satisfied_policy": (
        "ee1430360b5be0f91955747abcc76756b412eacf6e2318cf359414a4720391d2"
    ),
    # Updated in the SAME commit as the widening it pins (the discipline the test above
    # demands), sanctioned by 03-REVIEW WR-03: `_published_claims` now also walks
    # `NarrativeBlock` items' claims, so invariant 2 sees every claim carrier — the weekly's
    # highlights/lowlights were invisible to the PR gate before this. Pure insertion (Half B
    # verified); the planted-mutation observation was re-run after the update and still bites.
    "Surface._published_claims": "ea523ffe913c29956b1f38da5688c7a2a1a61498285ff9f1af66ce58c2bb5fa9",
    "Surface.open_pull_request": "878ceeeed00f310a77e27a9d100fb33b3f1ad4776600d205e142c609879d1fe4",
    "Surface.approve": "3af3e9238d8e21345b920838213795e586c80526e76f316f0b7d1da825c8d939",
    "Surface.publish": "539d5296d15a64eb7c8b53306f64227116a44350e9acb887ce572d77c732f9cf",
}


def _digest(text: str) -> str:
    """sha256 of a unit of source text. One definition, used by the pins AND their control."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_the_pin_set_covers_every_named_gate_function() -> None:
    """The two mappings cannot drift: a function added to one without the other fails here."""
    assert set(_GATE_FUNCTIONS) == set(_FROZEN)
    assert len(_FROZEN) == 8


@pytest.mark.parametrize("name", sorted(_FROZEN))
def test_gate_function_source_is_frozen(name: str) -> None:
    """The review gate's policy arithmetic is byte-frozen.

    A changed digest means the code that decides whether anything can be Published has moved.
    That is a conversation, not a commit (CLAUDE.md: "A change that breaks one is a conversation").
    If the change is intended: make it, update the pin in the SAME commit, and say why in the PR
    body. Never update the pin in a separate 'fix the test' commit — that is precisely the shape
    of a gate being relaxed to make a red go away.
    """
    actual = _digest(inspect.getsource(_GATE_FUNCTIONS[name]))
    assert actual == _FROZEN[name], (
        f"{name} changed: pinned {_FROZEN[name]}, live {actual}. The review gate moved. "
        "If that was deliberate, update the pin in the same commit and justify it in the PR body."
    )


def test_the_digest_discriminates() -> None:
    """Non-vacuity: prove `_digest` can tell two texts apart.

    Without this arm a broken `_digest` that returned a constant would satisfy all eight pins
    above and the gate would be green for the worst possible reason. Mutate one function's source
    text the way a careless edit would — a single appended blank line inside the body — and assert
    the digest moves.
    """
    real = inspect.getsource(Surface.publish)
    mutated = real.rstrip("\n") + "\n\n"
    assert mutated != real
    assert _digest(mutated) != _digest(real)
    assert _digest(real) == _FROZEN["Surface.publish"]


# --------------------------------------------------------------------------- #
# Half B — the diff shape: this phase EXTENDS semantic.py, it never rewrites it
# --------------------------------------------------------------------------- #


def test_semantic_py_diff_deletes_no_line(milestone_base_ref: str) -> None:
    """`semantic.py` grew by INSERTION this phase — nothing was rewritten.

    The four weekly block kinds are appended to the `Block` union and their models sit beside the
    existing block sub-models. A removed line against the milestone base means some existing
    definition was edited or reordered, which is exactly the change the Half-A pins exist to
    catch — asserted here structurally, so it is caught even for code no pin covers.

    `milestone_base_ref` (tests/conftest.py) is the ONE definition of that base and **FAILS**
    rather than skips when it cannot be resolved — see its docstring.
    """
    base = milestone_base_ref
    result = subprocess.run(
        ["git", "diff", base, "--", "src/newsletters/semantic.py"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    removed = [
        line
        for line in result.stdout.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]
    assert not removed, (
        f"{len(removed)} line(s) were REMOVED from src/newsletters/semantic.py against the "
        f"milestone base {base}. This phase only extends that file; a deletion means something "
        f"was rewritten rather than added:\n" + "\n".join(removed[:20])
    )
