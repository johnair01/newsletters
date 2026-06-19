"""The PROB-03 no-write-back boundary + the PROB-01 terminology-distinctness proof.

These are MANDATORY GATES — the legibility-layer-not-a-tracker guarantee made durable, proven
exactly the way no-auto-publish is proven (by test, not asserted). They mirror the idioms in
``tests/test_ai_optional.py`` (the AI-isolation guard this phase is patterned on): a static
import-linter contract (Task 1, covered by ``test_import_linter_contract_holds``) PLUS a runtime
``sys.modules`` subprocess guard PLUS an API allow-list PLUS a spine-unchanged / import-direction
check.

The hard constraint (CLAUDE.md + Phase-13 PROB-03): a ``Problem`` is a LEGIBILITY LAYER, NOT an
execution tracker. Problem-*solving* stays external/operator-owned, so ``problem.py`` must never
reach a network/external surface, expose a write-back/export path, or mutate the ``semantic.py``
spine. The Problem lifecycle ladder is a THIRD state axis that must share no type, member value,
member name, or verb with the review gate or the fan-out chain (the terminology guard, L6).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pydantic import BaseModel

from newsletters.problem import Problem, ProblemState
from newsletters.semantic import ReviewState, Source, Surface, Trace

# The network / external-system / would-be-tracker module set the Problem layer must never reach
# (mirrors the Task-1 .importlinter forbidden_modules; RESEARCH Q.C(a) / Assumption A3). Kept as a
# local constant so this file is self-contained, exactly like AI_MODULES in test_ai_optional.py.
FORBIDDEN_MODULES = (
    "socket",
    "http",
    "urllib",
    "ftplib",
    "smtplib",
    "subprocess",
    "requests",
    # would-be external tracker SDKs — named explicitly so a future `import jira` trips at runtime
    "jira",
    "ado",
)

# Substrings that would name a write-back / export / sync path on the public API surface. ANY
# public callable/attribute whose name contains one of these fails the allow-list (L5b): a future
# `export_to_jira` / `push` / `sync_remote` method fails this test loudly.
WRITE_BACK_SUBSTRINGS = (
    "export",
    "push",
    "sync",
    "write",
    "send",
    "post",
    "upload",
    "save",
    "jira",
    "ado",
    "devops",
    "remote",
    "publish",
)

# The review-gate / fan-out / promote verbs the Problem ladder's `transition` must NOT collide with
# (the terminology guard, L6). `transition` belongs to axis-3 ALONE.
OTHER_AXIS_VERBS = frozenset(
    {
        "publish",
        "approve",
        "open_pull_request",
        "promote_claim_to_kpi",
        "promote_report_to_article",
        "fan_out",
        "derive",
        "review",
    }
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _source() -> Source:
    """A real, non-trivial Source whose content_hash is non-empty (for the spine-unchanged proof)."""
    return Source(
        id="prob-boundary-src",
        context="phase-13 boundary proof",
        transcript="A scattered problem record: ticket + passdown + RCA, made legible.",
    )


# --- L5a (runtime): no network/external module is reachable from problem.py ---- #


def test_problem_loads_no_external_module() -> None:
    """A fresh subprocess proves `import newsletters.problem` adds ZERO network/external module
    over the AI-free spine it sits on.

    The RUNTIME complement to the Task-1 `forbid-external-write-in-problem` import-linter contract
    (the static half). Runs with PYDANTIC_DISABLE_PLUGINS=true and cwd=REPO_ROOT so we measure OUR
    import graph, not the ambient .venv — the same discipline as test_core_import_loads_no_ai_module.

    WHY a baseline-DELTA, not a raw `sys.modules` membership check (the load-bearing subtlety):
    pydantic itself pulls `socket`/`subprocess` (and its deps pull `http`/`urllib`) into `sys.modules`
    on import, so a raw "no forbidden module present" assertion would fail on FRAMEWORK noise, not on
    anything problem.py reaches. So we import the spine `newsletters.semantic` FIRST as the baseline
    (problem.py's only in-repo dependency — already AI-free + boundary-policed), then import
    `newsletters.problem` and assert it introduces NO forbidden module beyond that baseline. This
    isolates problem.py's OWN marginal footprint, which is the real claim. The real tracker SDKs
    (`jira`/`ado`) and `requests`/`ftplib`/`smtplib` are absent from the baseline, so the delta keeps
    full teeth: a future `import requests`/`import jira` inside problem.py trips it. The static
    no-direct-EDGE guarantee is the import-linter contract (Task 1).
    """
    code = (
        "import sys\n"
        "import newsletters.semantic\n"  # baseline: the AI-free spine problem.py depends on
        f"forbidden = {FORBIDDEN_MODULES!r}\n"
        "baseline = {m for m in forbidden if m in sys.modules}\n"
        "import newsletters.problem\n"
        "introduced = {m for m in forbidden if m in sys.modules} - baseline\n"
        "assert not introduced, sorted(introduced)\n"
        "print('problem boundary clean — introduced:', sorted(introduced))\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=REPO_ROOT
    )
    assert proc.returncode == 0, (
        f"a network/external module was pulled in by newsletters.problem (over the spine "
        f"baseline):\n{proc.stdout}{proc.stderr}"
    )


# --- L5b: the public API exposes no write-back path; transition is the sole mutator --- #


def test_problem_api_has_no_write_back_method() -> None:
    """`Problem`'s public surface has NO export/push/sync/write/... path; `transition` IS present.

    A STANDING allow-list guard (the API half of the no-write-back boundary): a future
    `export_to_jira` / `push_to_ado` / `sync_remote` method fails this loudly. `transition` — the
    one sanctioned, human-gated mutator (Plan 01) — must remain present.
    """
    # The pydantic BaseModel framework surface (model_*, construct, copy, dict, json, parse_*,
    # schema*) is inherited machinery, NOT Problem's own declared API — exclude it so a generic
    # name like `model_post_init` (a pydantic lifecycle hook, not an HTTP POST / write-back path)
    # does not false-positive. The allow-list polices what THIS entity adds, not BaseModel.
    pydantic_surface = {n for n in dir(BaseModel) if not n.startswith("_")}
    public = {n for n in dir(Problem) if not n.startswith("_")} - pydantic_surface

    offenders = {
        name
        for name in public
        for frag in WRITE_BACK_SUBSTRINGS
        if frag in name.lower()
    }
    assert not offenders, (
        f"Problem exposes a write-back/export path — PROB-03 forbids it: {sorted(offenders)}"
    )

    assert "transition" in public, (
        f"`transition` (the sole sanctioned mutator) is missing from Problem's public surface: "
        f"{sorted(public)}"
    )

    # And no foreign-axis mutator slipped in (set_state / advance / auto_advance / publish / approve).
    for forbidden_mutator in ("set_state", "advance", "auto_advance", "publish", "approve"):
        assert forbidden_mutator not in public, (
            f"Problem must mutate state ONLY via transition; found `{forbidden_mutator}`"
        )


# --- L5c: the semantic.py spine is unchanged by Problem ------------------------- #


def test_spine_unchanged_by_problem() -> None:
    """A full transition sequence leaves the constituent Source byte-identical; deps stay one-way.

    (i)  No mutation by construction: a Problem aggregates Traces to a Source but never mutates it.
         Capture `source.content_hash()` (and the addressed fields) BEFORE, run the FULL ladder
         IDENTIFIED -> OWNED -> IN_PROGRESS -> RESOLVED -> VERIFIED, and assert the hash + fields
         are byte-identical AFTER.
    (ii) Import-direction unchanged: semantic.py never imports problem (the edge stays one-way
         problem -> semantic), mirroring test_openpyxl_loader_has_no_toplevel_openpyxl_import.
    """
    # (i) content_hash byte-identical across a full transition sequence ------------
    source = _source()
    hash_before = source.content_hash()
    transcript_before = source.transcript
    id_before = source.id

    problem = Problem(
        id="prob-spine",
        title="A legible problem record",
        evidence=[Trace(source_id=source.id, content_hash=hash_before)],
    )
    (
        problem.transition(ProblemState.OWNED, by="JJ Airuoyo")
        .transition(ProblemState.IN_PROGRESS, by="JJ Airuoyo")
        .transition(ProblemState.RESOLVED, by="JJ Airuoyo")
        .transition(ProblemState.VERIFIED, by="A. Peer")
    )
    assert problem.state is ProblemState.VERIFIED  # the sequence actually ran

    assert source.content_hash() == hash_before, (
        "Problem mutated its constituent Source — the spine is NOT unchanged (PROB-03 violated)"
    )
    assert source.transcript == transcript_before
    assert source.id == id_before
    # The Trace's pinned content_hash is still the live hash — evidence stays non-stale.
    assert problem.evidence[0].content_hash == source.content_hash()

    # (ii) semantic.py never imports problem — dependency stays one-way ------------
    semantic_src = (REPO_ROOT / "src" / "newsletters" / "semantic.py").read_text()
    offending = [
        line
        for line in semantic_src.splitlines()
        if (line.startswith("import ") or line.startswith("from ")) and "problem" in line
    ]
    assert not offending, (
        f"semantic.py imports `problem` — the spine must not depend on the lifecycle layer "
        f"(cycle / inverted dependency): {offending}"
    )


# --- L4 (reinforced): transitions are human-gated, never auto-mutated ----------- #


def test_transition_human_gated_empty_actor_raises() -> None:
    """An empty/whitespace actor `by` raises and does NOT change state — no auto-advance path.

    The boundary file's standing copy of the human-gated invariant (the direct analog of
    test_published_without_approval_is_rejected): no code path advances a Problem's state without
    an explicit recorded human.
    """
    import pytest

    problem = Problem(
        id="prob-gate",
        title="Human-gated proof",
        evidence=[Trace(source_id="prob-boundary-src")],
    )
    for empty_actor in ("", "   ", "\t\n"):
        with pytest.raises(ValueError):
            problem.transition(to=ProblemState.OWNED, by=empty_actor)
        assert problem.state is ProblemState.IDENTIFIED, "state advanced despite a refused move"
        assert problem.log == [], "a refused transition was recorded in the log"


# --- L6: terminology-distinctness — three distinct state axes ------------------- #


def test_problemstate_distinct_from_reviewstate() -> None:
    """ProblemState is a distinct type from ReviewState with disjoint member VALUES and NAMES.

    The load-bearing check (IN_PROGRESS="in_progress" vs IN_REVIEW="in_review" are adjacent but
    must be disjoint): a shared value/name across axes could corrupt the publish trust gate.
    """
    assert ProblemState is not ReviewState
    assert not issubclass(ProblemState, ReviewState)
    assert not issubclass(ReviewState, ProblemState)

    problem_values = {m.value for m in ProblemState}
    review_values = {m.value for m in ReviewState}
    assert problem_values.isdisjoint(review_values), (
        f"ProblemState and ReviewState share a member VALUE: "
        f"{sorted(problem_values & review_values)}"
    )
    # Explicit adjacency assertion — the close pair must be different strings.
    assert ProblemState.IN_PROGRESS.value == "in_progress"
    assert ReviewState.IN_REVIEW.value == "in_review"
    assert ProblemState.IN_PROGRESS.value != ReviewState.IN_REVIEW.value

    problem_names = {m.name for m in ProblemState}
    review_names = {m.name for m in ReviewState}
    assert problem_names.isdisjoint(review_names), (
        f"ProblemState and ReviewState share a member NAME: "
        f"{sorted(problem_names & review_names)}"
    )


def test_lifecycle_verb_collides_with_no_axis_verb() -> None:
    """The verb `transition` collides with no review-gate / fan-out / promote verb (L6).

    Conversely, neither `Surface` (the review-gate/fan-out surface) carries a `transition`, nor does
    `Problem` carry a gate verb (publish/approve/open_pull_request) — the axes do not bleed.
    """
    assert "transition" not in OTHER_AXIS_VERBS, (
        "the Problem ladder verb `transition` collides with a review-gate/fan-out/promote verb"
    )

    # Surface (the review-gate + fan-out axis) must not expose the lifecycle verb.
    assert not hasattr(Surface, "transition"), (
        "Surface exposes `transition` — the lifecycle verb bled into the review-gate axis"
    )

    # Problem must not expose any review-gate verb.
    problem_public = {n for n in dir(Problem) if not n.startswith("_")}
    for gate_verb in ("publish", "approve", "open_pull_request"):
        assert gate_verb not in problem_public, (
            f"Problem exposes the review-gate verb `{gate_verb}` — the axes bled together"
        )
