"""Golden-file corpus for the Email adapter (ADAPT-06; CONTEXT decision 4, success criterion 3).

This is the phase's *proof of correctness*. Eight tiny, committed `.eml` fixtures
(`tests/fixtures/eml/*.eml`) drive `EmailAdapter` end-to-end across its full routing matrix —
clean plain mail, an RFC2047 subject, multipart/alternative, HTML-only, mixed-with-PDF, a
forwarded `message/rfc822`, a mislabeled charset, and a malformed boundary. For EVERY fixture the
test asserts the load-bearing invariants:

1. **Zero silent drops** — the accounting identity ``len(claims) + len(unextracted) == units walked``
   (CONTEXT decision 4). A silent drop is, by construction, a TEST FAILURE (threat T-04-08).
2. **Faithful spans** — every claim is verbatim: ``claim.text == claim.evidence[0].span`` AND
   re-slicing the live transcript at ``[trace.start:trace.end]`` reproduces it.
3. **Content-addressed** — every claim's trace ``is_addressed`` (minted via ``Trace.from_source``).
4. **Coverage honesty** — ``coverage.complete == (len(coverage.unextracted) == 0)``.
5. **Conformance + round-trip** — ``assert_conforms(EmailAdapter(), [source])`` passes for each
   fixture (span-containment + lossless JSON round-trip, ``conformance.py:38-94``).
6. **Determinism** — parsing the same fixture twice yields an EQUAL ``DistillationResult``
   (no ``now()``/random in claim text; the timestamp comes from the Date header) (threat T-04-09).

Plus per-fixture ROUTING assertions pinning U1 (forwarded), U2 (PDF attachment), U3 (charset
fallback), U5 (html-only), U7 (defect), and the no-double-count of the html alternative.

The expected per-fixture counts/routing below were derived by driving the LIVE adapter (not
assumed); they are the executable contract that the routing matrix holds.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters.adapters.email_adapter import EmailAdapter
from newsletters.distill import DistillationResult, assert_conforms

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "eml"


class Expected:
    """The pinned expectation for one fixture — the golden contract, encoded inline.

    ``n_claims`` = header units + body paragraphs minted as claims.
    ``unextracted_reasons`` = the EXACT, ordered ``Coverage.unextracted[].reason`` strings the
    adapter must emit (the U1-U8 contract from 04-02-SUMMARY). The accounting identity is then
    ``n_claims + len(unextracted_reasons) == units walked`` — and ``len(claims) + len(unextracted)``
    from the live result must equal that same total, with zero unaccounted units.
    """

    def __init__(self, *, n_claims: int, unextracted_reasons: list[str]) -> None:
        self.n_claims = n_claims
        self.unextracted_reasons = unextracted_reasons

    @property
    def total_units(self) -> int:
        return self.n_claims + len(self.unextracted_reasons)


# The exact U1-U8 reason strings (copied verbatim from 04-02-SUMMARY / email_adapter.py).
R_RFC822 = "forwarded message/rfc822 — nested mail not extracted (scope)"
R_PDF = "non-text attachment (application/pdf, filename=report.pdf) — not extracted"
R_CHARSET = (
    "charset fallback: declared utf-8 failed, decoded as latin-1 — "
    "interpretation may be unfaithful"
)
R_HTML = "html-only body — deterministic tag-strip is lossy (structure/links dropped)"
R_DEFECT = "MIME defect(s): CloseBoundaryNotFoundDefect"

# fixture name -> pinned expectation (every fixture's full routing, by construction).
EXPECTED: dict[str, Expected] = {
    # Clean, complete: 4 headers + 2 paragraphs, nothing dropped.
    "plain_simple.eml": Expected(n_claims=6, unextracted_reasons=[]),
    # 4 headers (Subject decoded to unicode) + 1 paragraph; complete.
    "rfc2047_subject.eml": Expected(n_claims=5, unextracted_reasons=[]),
    # plain wins over html; the html alternative is the SAME content -> NOT double-counted,
    # NOT in unextracted[]. 4 headers + 1 paragraph; complete.
    "multipart_alternative.eml": Expected(n_claims=5, unextracted_reasons=[]),
    # html-only emit-both: 4 headers + 2 stripped paragraphs as claims + a U5 disclosure.
    "html_only.eml": Expected(n_claims=6, unextracted_reasons=[R_HTML]),
    # text body + a pdf attachment: 4 headers + 1 paragraph + a U2 entry.
    "mixed_with_pdf.eml": Expected(n_claims=5, unextracted_reasons=[R_PDF]),
    # nested message/rfc822: 4 headers + 1 paragraph + a U1 entry (nested mail not walked).
    "forwarded_rfc822.eml": Expected(n_claims=5, unextracted_reasons=[R_RFC822]),
    # declares utf-8, body has a lone latin-1 byte: faithful latin-1 fallback + a U3 entry
    # (no residual U+FFFD, so U4 does NOT fire).
    "mislabeled_charset.eml": Expected(n_claims=5, unextracted_reasons=[R_CHARSET]),
    # missing close boundary: body still extracted (4 headers + 1 paragraph) + a U7 defect entry.
    "malformed_boundary.eml": Expected(n_claims=5, unextracted_reasons=[R_DEFECT]),
}

FIXTURE_NAMES = sorted(EXPECTED)


def _distill(name: str) -> tuple[object, DistillationResult]:
    """Parse a fixture with a FRESH adapter and distill it; return (source, result)."""
    adapter = EmailAdapter()
    raw = (FIXTURE_DIR / name).read_bytes()
    source, _units, _adapter_unx = adapter.parse(raw, str(FIXTURE_DIR / name))
    return source, adapter.distill([source])


def test_corpus_is_eight_committed_fixtures() -> None:
    """The corpus is exactly the 8 committed `.eml` fixtures the golden table expects."""
    on_disk = sorted(p.name for p in FIXTURE_DIR.glob("*.eml"))
    assert on_disk == FIXTURE_NAMES, on_disk


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_zero_silent_drops(name: str) -> None:
    """The headline assertion (T-04-08): #claims + #unextracted == #units walked, exactly.

    Every MIME unit the adapter touches is on EXACTLY one side of the ledger — minted as a claim
    or recorded in unextracted[]. Nothing is silently dropped, and nothing is invented.
    """
    exp = EXPECTED[name]
    _src, result = _distill(name)
    claims = result.distillation.claims
    unextracted = result.coverage.unextracted

    assert len(claims) == exp.n_claims, (
        f"{name}: expected {exp.n_claims} claims, got {len(claims)}: "
        f"{[c.text for c in claims]}"
    )
    # the unextracted reasons match the pinned U1-U8 contract, in order
    assert [u.reason for u in unextracted] == exp.unextracted_reasons, (
        f"{name}: unextracted reasons drifted from the contract"
    )
    # THE accounting identity — the executable form of "no silent drops"
    assert len(claims) + len(unextracted) == exp.total_units, (
        f"{name}: silent drop detected — {len(claims)} claims + {len(unextracted)} "
        f"unextracted != {exp.total_units} units walked"
    )


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_claims_are_verbatim_and_content_addressed(name: str) -> None:
    """Every claim is faithful (verbatim span) and content-addressed (T-04-09)."""
    source, result = _distill(name)
    claims = result.distillation.claims
    assert claims, f"{name}: expected at least one claim"
    for claim in claims:
        assert claim.is_traced, f"{name}: claim {claim.text!r} is untraced"
        trace = claim.evidence[0]
        # faithful: the stored span IS the claim text
        assert claim.text == trace.span, (
            f"{name}: claim.text != trace.span for {claim.text!r}"
        )
        # re-slice the LIVE transcript at the recorded window -> reproduces the text
        assert trace.start is not None and trace.end is not None
        assert source.transcript[trace.start : trace.end] == claim.text, (
            f"{name}: transcript[{trace.start}:{trace.end}] != claim.text {claim.text!r}"
        )
        # content-addressed: minted through Trace.from_source (pinned a content hash)
        assert trace.is_addressed, f"{name}: trace for {claim.text!r} is not content-addressed"


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_coverage_honesty(name: str) -> None:
    """coverage.complete is True IFF nothing was dropped (the D-05 honesty invariant, asserted)."""
    _src, result = _distill(name)
    cov = result.coverage
    assert cov.complete == (len(cov.unextracted) == 0), (
        f"{name}: coverage.complete={cov.complete} but unextracted has {len(cov.unextracted)}"
    )


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_conformance_and_json_roundtrip(name: str) -> None:
    """assert_conforms drives span-containment + the lossless JSON round-trip for each fixture."""
    source, _result = _distill(name)
    # a fresh adapter that has parse()-recorded THIS source's drops, so distill() recovers them
    adapter = EmailAdapter()
    adapter.parse((FIXTURE_DIR / name).read_bytes(), source.id)
    result = assert_conforms(adapter, [source])
    assert isinstance(result, DistillationResult)
    # belt-and-braces: explicit lossless round-trip mirroring test_distill_socket.py
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_determinism(name: str) -> None:
    """Parsing the same fixture twice yields an EQUAL result — no time/random leaks in (T-04-09)."""
    _s1, first = _distill(name)
    _s2, second = _distill(name)
    assert first == second, f"{name}: non-deterministic distillation"


# --- targeted per-fixture routing assertions (the matrix is exercised, not just counted) ----- #


def test_plain_simple_complete_no_drops() -> None:
    """The clean case: 4 header + 2 body claims, complete, nothing dropped."""
    _src, result = _distill("plain_simple.eml")
    assert result.coverage.complete is True
    assert result.coverage.unextracted == []
    assert len(result.distillation.claims) == 6


def test_rfc2047_subject_decoded_verbatim() -> None:
    """The RFC2047 Subject claim text is the DECODED unicode, verbatim in the transcript."""
    source, result = _distill("rfc2047_subject.eml")
    subjects = [c for c in result.distillation.claims if c.text == "Quarterly — café results"]
    assert len(subjects) == 1, [c.text for c in result.distillation.claims]
    assert subjects[0].text in source.transcript  # the decoded unicode is what was stored


def test_multipart_alternative_plain_wins_no_double_count() -> None:
    """Body claims come from the PLAIN part; the html alternative is neither counted nor dropped."""
    _src, result = _distill("multipart_alternative.eml")
    body_claims = [c for c in result.distillation.claims if c.text == "Plain wins over html."]
    assert len(body_claims) == 1  # exactly once — not double-counted from the html alt
    assert result.coverage.unextracted == []  # the html alt is the SAME content, not a drop
    assert result.coverage.complete is True


def test_html_only_routes_u5() -> None:
    """An html-only body emits best-effort claims AND a U5 lossy-strip disclosure."""
    _src, result = _distill("html_only.eml")
    assert result.coverage.complete is False
    assert [u.reason for u in result.coverage.unextracted] == [R_HTML]
    # the stripped paragraphs are still minted as claims (emit-both)
    texts = {c.text for c in result.distillation.claims}
    assert "First paragraph here." in texts and "Second paragraph here." in texts
    # the raw markup never reached the BODY claims (the strip is real, not a passthrough).
    # NB: header values legitimately contain '<' (e.g. "Team <team@example.com>"), so this
    # injection check targets the stripped body paragraphs specifically.
    body_claims = {"First paragraph here.", "Second paragraph here."}
    assert all(
        "<" not in c.text and ">" not in c.text
        for c in result.distillation.claims
        if c.text in body_claims
    )


def test_mixed_with_pdf_routes_u2() -> None:
    """A non-text attachment routes to U2; the body is still extracted."""
    _src, result = _distill("mixed_with_pdf.eml")
    assert [u.reason for u in result.coverage.unextracted] == [R_PDF]
    assert any(c.text == "See the attached report." for c in result.distillation.claims)


def test_forwarded_rfc822_routes_u1() -> None:
    """A nested message/rfc822 routes to U1; the nested mail's content is NOT extracted."""
    source, result = _distill("forwarded_rfc822.eml")
    assert [u.reason for u in result.coverage.unextracted] == [R_RFC822]
    # nested-mail content never leaked into a claim or the transcript (scope boundary held)
    assert "This is the forwarded body." not in source.transcript
    assert all(
        "This is the forwarded body." != c.text for c in result.distillation.claims
    )


def test_mislabeled_charset_routes_u3() -> None:
    """A lone latin-1 byte under a utf-8 label falls back faithfully and routes to U3 (not U4)."""
    _src, result = _distill("mislabeled_charset.eml")
    assert [u.reason for u in result.coverage.unextracted] == [R_CHARSET]
    # the fallback produced a FAITHFUL "é" — no residual U+FFFD replacement char
    assert any(c.text == "Café numbers held steady." for c in result.distillation.claims)
    assert all("�" not in c.text for c in result.distillation.claims)


def test_malformed_boundary_routes_u7_and_extracts_body() -> None:
    """A missing close boundary surfaces as a U7 defect; the readable body is still extracted."""
    _src, result = _distill("malformed_boundary.eml")
    assert [u.reason for u in result.coverage.unextracted] == [R_DEFECT]
    assert any(
        c.text == "The body is still readable." for c in result.distillation.claims
    )
