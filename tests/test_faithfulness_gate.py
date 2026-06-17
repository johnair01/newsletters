"""PROV-02 — the deterministic span-containment faithfulness gate at the socket seam.

This suite proves the Phase-3 faithfulness gate (D-3, D-4; ROADMAP Phase-3 criteria 2 & 3):

* ``SpanContainmentFaithfulness`` entails a claim iff its NORMALIZED text is contained in a
  NORMALIZED trace span — deterministic, stdlib-only, no AI, no mutation (faithful, not suggestive).
* It is the DEFAULT check at the single-place ``_enforce`` seam (and therefore at
  ``assert_conforms``), so EVERY backend inherits the gate with zero backend change.
* ``route_unfaithful_to_missing`` is the non-raising companion: it relocates an unfaithful claim's
  text VERBATIM into ``Distillation.missing[]`` and removes it from ``claims[]`` — never surfaced
  as a fact, never silently dropped, never rewritten.

OPTION A (the resolved design decision, mirroring the 03-01 STALE rule "un-addressed => not
content-addressed => never a false positive"): a claim entails iff it has >=1 trace AND at least
one trace either (a) is UN-ADDRESSED (the Rev1/capture structural-fallback path — span-containment
is not applicable without content-addressed evidence) OR (b) IS content-addressed and its
normalized span contains the normalized claim text. So span-containment has teeth exactly where
there is real content-addressed evidence; legacy un-addressed traces keep the structural guarantee.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from newsletters.distill import (
    DistillationResult,
    FaithfulnessCheck,
    SpanContainmentFaithfulness,
    route_unfaithful_to_missing,
)
from newsletters.semantic import Claim, Distillation, Source, Trace

AI_MODULES = ("langchain", "langgraph", "langsmith", "pydantic_ai")


# --------------------------------------------------------------------------- #
# Builders — content-addressed traces (the path span-containment actually checks)
# --------------------------------------------------------------------------- #


def _addressed_trace(transcript: str, start: int, end: int) -> Trace:
    """A CONTENT-ADDRESSED trace (is_addressed True) whose span = transcript[start:end]."""
    return Trace.from_source(Source(id="s1", transcript=transcript), start, end)


def _unaddressed_trace(span: str = "") -> Trace:
    """An UN-ADDRESSED trace (the Rev1/capture path) — no content hash; span-containment N/A."""
    return Trace(source_id="s1", locator="line 3", span=span)


# --------------------------------------------------------------------------- #
# Task 1 — SpanContainmentFaithfulness: normalized, deterministic, stdlib-only
# --------------------------------------------------------------------------- #


def test_entails_true_when_normalized_claim_in_addressed_span() -> None:
    """A content-addressed span that contains the (normalized) claim text => entailed."""
    transcript = "intro ... we   SHIPPED x ... outro"
    trace = _addressed_trace(transcript, 0, len(transcript))
    assert trace.is_addressed
    claim = Claim(text="We shipped X", evidence=[trace])
    assert SpanContainmentFaithfulness().entails(claim) is True


def test_entails_false_when_addressed_span_does_not_contain_claim() -> None:
    """A content-addressed span that does NOT contain the claim text => not entailed."""
    transcript = "we discussed the roadmap and the budget"
    trace = _addressed_trace(transcript, 0, len(transcript))
    claim = Claim(text="we shipped the mobile app", evidence=[trace])
    assert SpanContainmentFaithfulness().entails(claim) is False


def test_entails_false_for_untraced_claim() -> None:
    """An untraced claim is unfaithful — parity with the Phase-1 structural default."""
    claim = Claim(text="bare unsubstantiated claim", evidence=[])
    assert SpanContainmentFaithfulness().entails(claim) is False


def test_normalization_collapses_whitespace_and_case_on_both_sides() -> None:
    """Casing + runs of whitespace differ between claim and span, yet containment still matches."""
    transcript = "   We    Shipped\n\tThe   FEATURE   today  "
    trace = _addressed_trace(transcript, 0, len(transcript))
    claim = Claim(text="we shipped the feature", evidence=[trace])
    assert SpanContainmentFaithfulness().entails(claim) is True


def test_entails_never_mutates_claim_or_traces() -> None:
    """The checker is pure: claim.text and trace.span are byte-identical before/after (D-3)."""
    transcript = "   We    Shipped\n\tThe   FEATURE   today  "
    trace = _addressed_trace(transcript, 0, len(transcript))
    claim = Claim(text="We Shipped The FEATURE", evidence=[trace])
    text_before, span_before = claim.text, claim.evidence[0].span
    SpanContainmentFaithfulness().entails(claim)
    assert claim.text == text_before
    assert claim.evidence[0].span == span_before


def test_unaddressed_trace_is_structural_fallback_entailed() -> None:
    """OPTION A: an UN-ADDRESSED trace (Rev1/capture) entails structurally — never a false positive.

    Span-containment is not applicable without content-addressed evidence, so a traced-but-
    un-addressed claim (the capture path, which builds empty-span traces) passes — this is what
    keeps test_conformance_passes_manual_backend / test_socket_end_to_end green.
    """
    claim = Claim(text="we decided X", evidence=[_unaddressed_trace(span="")])
    assert SpanContainmentFaithfulness().entails(claim) is True


def test_any_one_trace_entails_the_claim() -> None:
    """Multi-trace rule: a claim is faithful if ANY one of its traces entails it."""
    transcript = "totally unrelated source text"
    bad = _addressed_trace(transcript, 0, len(transcript))
    good = _addressed_trace("we shipped the thing", 0, len("we shipped the thing"))
    claim = Claim(text="we shipped the thing", evidence=[bad, good])
    assert SpanContainmentFaithfulness().entails(claim) is True


def test_addressed_non_containing_overrides_nothing_when_no_other_trace() -> None:
    """A claim whose ONLY trace is content-addressed and non-containing => not entailed."""
    transcript = "we discussed budget"
    claim = Claim(text="we shipped X", evidence=[_addressed_trace(transcript, 0, len(transcript))])
    assert SpanContainmentFaithfulness().entails(claim) is False


def test_satisfies_faithfulness_check_protocol() -> None:
    """SpanContainmentFaithfulness satisfies the existing FaithfulnessCheck protocol seam."""
    check = SpanContainmentFaithfulness()
    assert isinstance(check, FaithfulnessCheck)


def test_faithfulness_module_imports_no_ai() -> None:
    """A fresh subprocess importing the faithfulness gate loads no AI module (AI-optional core)."""
    code = (
        "import sys, newsletters.distill.faithfulness; "
        f"bad=[m for m in {AI_MODULES!r} if m in sys.modules]; "
        "assert not bad, bad; print('clean')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"AI leaked: {proc.stdout}{proc.stderr}"


# --------------------------------------------------------------------------- #
# Task 2 — the seam defaults to span-containment; every backend inherits it
# --------------------------------------------------------------------------- #


def _addressed_result(transcript: str, claim_text: str) -> DistillationResult:
    trace = _addressed_trace(transcript, 0, len(transcript))
    return DistillationResult(
        distillation=Distillation(claims=[Claim(text=claim_text, evidence=[trace])])
    )


def test_enforce_default_now_rejects_addressed_unentailed_claim() -> None:
    """_enforce() with NO explicit check uses span-containment: a content-addressed, non-containing
    claim now RAISES — where the Phase-1 structural default (traced => ok) would have passed it."""
    from newsletters.distill.ports import _enforce

    result = _addressed_result("we discussed budget", "we shipped X")
    with pytest.raises(ValueError):
        _enforce(result)


def test_enforce_default_passes_addressed_contained_claim() -> None:
    """_enforce() PASSES a content-addressed claim whose span contains it (positive)."""
    from newsletters.distill.ports import _enforce

    result = _addressed_result("we shipped X today", "we shipped X")
    assert _enforce(result) is result


def test_enforce_seam_stays_injectable() -> None:
    """An explicit permissive check still overrides the new default — the seam stays injectable."""
    from newsletters.distill.ports import _enforce

    class _AlwaysFaithful:
        def entails(self, claim: Claim) -> bool:  # noqa: ARG002
            return True

    result = _addressed_result("we discussed budget", "we shipped X")
    assert _enforce(result, _AlwaysFaithful()) is result


def test_enforce_default_still_rejects_untraced() -> None:
    """The existing untraced-rejection behaviour is preserved under the new default (OPTION A)."""
    from newsletters.distill.ports import _enforce

    result = DistillationResult(
        distillation=Distillation(claims=[Claim(text="bare", evidence=[])])
    )
    with pytest.raises(ValueError):
        _enforce(result)


def test_assert_conforms_inherits_span_containment_default(sources: list[Source]) -> None:
    """assert_conforms inherits span-containment with NO signature change: a backend emitting a
    content-addressed, non-containing claim is now FAILED by conformance."""
    from newsletters.distill.conformance import assert_conforms

    class _AddressedUnentailedBackend:
        name = "addressed-unentailed"

        def distill(self, sources: list[Source]) -> DistillationResult:
            return _addressed_result("we discussed budget", "we shipped X")

    with pytest.raises((AssertionError, ValueError)):
        assert_conforms(_AddressedUnentailedBackend(), sources)


def test_assert_conforms_still_passes_manual_backend(
    work_session, sources: list[Source]
) -> None:
    """Regression: the ManualBackend still conforms under span-containment — its capture-derived
    claims are un-addressed traces (OPTION A structural fallback), so the gate does not reject them.
    """
    from newsletters.capture import WorkSession  # noqa: F401  (type only)
    from newsletters.distill import ManualBackend, assert_conforms

    result = assert_conforms(ManualBackend(session=work_session), sources)
    assert isinstance(result, DistillationResult)


# --------------------------------------------------------------------------- #
# Task 3 — route_unfaithful_to_missing: relocate to missing[], never as a fact
# --------------------------------------------------------------------------- #


def test_route_moves_unfaithful_claim_text_to_missing() -> None:
    """An unentailed claim's TEXT moves out of claims[] and into missing[] (verbatim)."""
    transcript = "we discussed budget"
    bad = Claim(text="we shipped X", evidence=[_addressed_trace(transcript, 0, len(transcript))])
    result = DistillationResult(distillation=Distillation(claims=[bad]))

    routed = route_unfaithful_to_missing(result)

    texts = [c.text for c in routed.distillation.claims]
    assert "we shipped X" not in texts
    assert "we shipped X" in routed.distillation.missing


def test_route_leaves_faithful_claims_untouched() -> None:
    """Faithful (span-contained) claims stay in claims[] with byte-identical text."""
    good = Claim(
        text="we shipped X",
        evidence=[_addressed_trace("we shipped X today", 0, len("we shipped X today"))],
    )
    result = DistillationResult(distillation=Distillation(claims=[good]))

    routed = route_unfaithful_to_missing(result)

    assert [c.text for c in routed.distillation.claims] == ["we shipped X"]
    assert routed.distillation.missing == []


def test_route_is_faithful_not_suggestive() -> None:
    """Routing relocates verbatim and rewrites nothing — surviving + routed text is unchanged."""
    transcript = "we discussed budget"
    bad = Claim(text="We Shipped X!", evidence=[_addressed_trace(transcript, 0, len(transcript))])
    good = Claim(
        text="we shipped Y",
        evidence=[_addressed_trace("we shipped Y now", 0, len("we shipped Y now"))],
    )
    result = DistillationResult(distillation=Distillation(claims=[bad, good]))

    routed = route_unfaithful_to_missing(result)

    assert "We Shipped X!" in routed.distillation.missing  # verbatim, not normalized
    assert [c.text for c in routed.distillation.claims] == ["we shipped Y"]


def test_route_accepts_injected_check_same_default_as_enforce() -> None:
    """route uses the SAME default rule as the gate; an injected check overrides it."""

    class _AlwaysFaithful:
        def entails(self, claim: Claim) -> bool:  # noqa: ARG002
            return True

    bad = Claim(
        text="we shipped X",
        evidence=[_addressed_trace("we discussed budget", 0, len("we discussed budget"))],
    )
    result = DistillationResult(distillation=Distillation(claims=[bad]))

    routed = route_unfaithful_to_missing(result, _AlwaysFaithful())
    assert [c.text for c in routed.distillation.claims] == ["we shipped X"]
    assert routed.distillation.missing == []


def test_routed_result_passes_enforce() -> None:
    """After routing, every surviving claim is entailed — the routed result passes _enforce."""
    from newsletters.distill.ports import _enforce

    bad = Claim(
        text="we shipped X",
        evidence=[_addressed_trace("we discussed budget", 0, len("we discussed budget"))],
    )
    good = Claim(
        text="we shipped Y",
        evidence=[_addressed_trace("we shipped Y now", 0, len("we shipped Y now"))],
    )
    result = DistillationResult(distillation=Distillation(claims=[bad, good]))

    routed = route_unfaithful_to_missing(result)
    assert _enforce(routed) is routed
