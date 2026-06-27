"""The Phase-3 deterministic faithfulness gate — span-containment, stdlib-only, no AI (PROV-02).

This is the Phase-3 (D-3, D-4) implementation of the injectable ``FaithfulnessCheck`` seam
declared in :mod:`newsletters.distill.ports`. It swaps the Phase-1 STRUCTURAL default (a claim is
faithful iff it is traced) for SPAN-CONTAINMENT: a claim is faithful iff its NORMALIZED text is
contained in the NORMALIZED text of one of its traced evidence spans.

OPTION A — the resolved design decision, mirroring the 03-01 STALE rule
("un-addressed => not content-addressed => never a false positive").

A claim ``entails`` iff it has >=1 trace AND at least one of its traces satisfies:

  (a) the trace is UN-ADDRESSED (``trace.is_addressed is False`` — the Rev1/capture path):
      STRUCTURAL fallback. It counts as entailed because it is traced; span-containment is
      NOT APPLICABLE without content-addressed evidence (the capture path builds empty-span,
      un-addressed traces, so strict containment would falsely reject every Rev1 claim and
      violate "faithful, not suggestive — no false positives"); OR

  (b) the trace IS content-addressed (``trace.is_addressed is True``) AND ``_normalize(claim.text)``
      is contained in ``_normalize(trace.span)``.

A claim with NO traces is never entailed (untraced => unfaithful), preserving the Phase-1
structural rejection of untraced claims.

The consequence: span-containment has teeth exactly where there is real content-addressed evidence
to check against; legacy un-addressed traces keep the structural guarantee and never produce a
false positive. The gate SELF-STRENGTHENS as the pipeline adopts content-addressing — once sources
are migrated to ``Trace.from_source`` (Plan 03-02), those claims fall under strict containment (b).

HARD RULE — AI-optional core: this module imports only ``..semantic`` and stdlib string ops
(``str.casefold`` / ``str.split``). No new dependency, no regex, no AI. FAITHFUL, NOT SUGGESTIVE:
normalization operates on TRANSIENT copies for comparison only — it NEVER mutates the stored
``claim.text`` or ``trace.span``.
"""

from __future__ import annotations

from ..semantic import Claim, Distillation
from .ports import DistillationResult, FaithfulnessCheck


def _normalize(text: str) -> str:
    """Return a comparison-only normal form: case-folded, with runs of whitespace collapsed.

    ``str.split()`` with no argument splits on ANY run of whitespace (spaces, tabs, newlines) and
    drops leading/trailing whitespace; ``" ".join(...)`` rejoins with a single space. ``casefold``
    is the aggressive, locale-independent lowercasing used for caseless matching. This is a pure
    function over a transient copy — it never touches the stored claim text or span.
    """
    return " ".join(text.casefold().split())


class SpanContainmentFaithfulness:
    """Deterministic, no-AI faithfulness check: normalized claim text contained in a trace span.

    Implements the :class:`FaithfulnessCheck` protocol (``entails(claim) -> bool``). See the module
    docstring for OPTION A: un-addressed traces are a structural fallback (never a false positive);
    content-addressed traces get strict normalized span-containment. A claim is faithful if ANY ONE
    of its traces entails it (the multi-trace rule).
    """

    def entails(self, claim: Claim) -> bool:
        if not claim.evidence:
            # Untraced => unfaithful (parity with the Phase-1 structural default).
            return False
        normalized_claim = _normalize(claim.text)
        for trace in claim.evidence:
            if not trace.is_addressed:
                # OPTION A (a): un-addressed/Rev1 trace — span-containment N/A; structural pass.
                return True
            # OPTION A (b): content-addressed — strict normalized containment has teeth here.
            if normalized_claim in _normalize(trace.span):
                return True
        return False


def route_unfaithful_to_missing(
    result: DistillationResult,
    check: FaithfulnessCheck = SpanContainmentFaithfulness(),
) -> DistillationResult:
    """Relocate every unfaithful claim's text into ``Distillation.missing[]`` — never as a fact.

    The non-raising companion to :func:`newsletters.distill.ports._enforce`: where ``_enforce`` is
    the HARD conformance gate (a backend must not EMIT an unfaithful claim), this is the
    reviewer-facing relocation that GUARANTEES an unfaithful claim is surfaced in ``missing[]``,
    never silently dropped and never presented in the body as a fact (ROADMAP Phase-3 criterion 3).

    It keeps only the claims that pass ``check.entails`` and appends each FAILING claim's ``text``
    — VERBATIM, unchanged — to ``missing[]``. Uses the SAME default ``check`` as ``_enforce`` so
    there is exactly one definition of "faithful". FAITHFUL, NOT SUGGESTIVE: it relocates, it does
    not rewrite — surviving claims and the routed text are byte-identical to the input.

    A fresh ``Distillation`` / ``DistillationResult`` is built via ``model_copy(update=...)`` rather
    than mutating the input in place.
    """
    distillation = result.distillation
    kept: list[Claim] = []
    routed_missing: list[str] = list(distillation.missing)
    for claim in distillation.claims:
        if check.entails(claim):
            kept.append(claim)
        else:
            routed_missing.append(claim.text)  # verbatim — relocate, do not rewrite
    new_distillation: Distillation = distillation.model_copy(
        update={"claims": kept, "missing": routed_missing}
    )
    return result.model_copy(update={"distillation": new_distillation})
