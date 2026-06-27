"""Golden-file corpus for the PowerPoint adapter (ADAPT-06; ROADMAP Phase-6 success criterion 3).

This is the phase's *proof of correctness*. Nine tiny, committed, byte-reproducible `.pptx`
fixtures (`tests/fixtures/pptx/*.pptx`, authored by `_author_fixtures.py`) drive `PptxAdapter`
end-to-end across its full extract-vs-disclose fork — a title+body slide, a free text box, a table,
speaker notes, a chart, an embedded image, a SmartArt diagram, a NESTED group of shapes, and an
empty slide. The SmartArt + nested-group pair is the explicit ROADMAP criterion-3 fixture. For
EVERY fixture the test asserts the load-bearing invariants:

1. **Zero silent drops** — the accounting identity ``len(claims) + len(unextracted) == units walked``
   (ADAPT-06). A silent drop is, by construction, a TEST FAILURE (threat T-06-10). Every non-empty,
   extractable paragraph/cell/note is a claim; every chart/picture/SmartArt is an ``unextracted[]``
   disclosure; empty paragraphs/cells and GROUP container nodes are correctly NOT counted (they are
   nothing lost), so they never inflate the ledger. The nested-group fixture is checked explicitly:
   the readable member IS extracted, the unreadable member IS disclosed, and the two group NODES
   contribute nothing (the L3 nested accounting).
2. **Faithful spans** — every claim is verbatim: ``claim.text == trace.span`` AND re-slicing the
   live transcript at ``[trace.start:trace.end]`` reproduces it.
3. **Content-addressed** — every claim's trace ``is_addressed`` (minted via ``Trace.from_source``).
4. **Coverage honesty** — ``coverage.complete == (len(coverage.unextracted) == 0)``.
5. **Conformance + round-trip** — ``assert_conforms(PptxAdapter(), [source])`` passes per fixture;
   ``DistillationResult`` round-trips losslessly through JSON.
6. **Determinism on the parsed Source (L5)** — parsing the same fixture twice yields an EQUAL
   ``DistillationResult`` AND a byte-identical Source (``s1.model_dump_json() == s2.model_dump_json()``).
   This is asserted on the PARSED ``Source`` — NOT on re-saved ``.pptx`` bytes — so it is immune to
   any python-pptx re-save byte drift (risk A3); the Source-determinism property is the one ADAPT-06
   needs.
7. **Round-trip coverage parity** (threat T-06-10, the Plan-01 hardening proven on email/excel) —
   ``model_dump_json`` the Source, reload it, distill on a FRESH adapter -> coverage EQUALS the
   original. Drops travel on ``Source.extraction``, so coverage survives persistence.

Plus targeted per-fixture ROUTING assertions: ``smartart`` discloses the diagram (shape_type None +
diagram URI) and emits NO text claim (criterion 3); ``nested_group`` extracts the readable member's
text and discloses the unreadable member; ``chart`` and ``image`` are disclosed not extracted;
``empty_slide`` yields zero claims and zero drops (nothing lost).

The expected per-fixture counts/reasons below were derived by driving the LIVE adapter (not
assumed); they are the executable contract that the fork holds across the whole matrix. The whole
module is skipped cleanly when the optional ``[pptx]`` extra (python-pptx) is absent, so the
bare-install gate is unaffected.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("pptx") is None,
    reason="optional [pptx] extra (python-pptx) not installed",
)

from newsletters.distill import DistillationResult, assert_conforms  # noqa: E402
from newsletters.semantic import Source  # noqa: E402

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "pptx"


def _adapter():
    """A FRESH PptxAdapter (imported lazily so this module imports without the [pptx] extra)."""
    from newsletters.adapters.pptx_adapter import PptxAdapter

    return PptxAdapter()


# The EXACT unextracted reason strings — imported from the adapter so a drift on EITHER side (the
# adapter's taxonomy or this golden contract) is a failure. (The xlsx golden copies them verbatim;
# here the strings are module constants in pptx_adapter.py, so we import them directly.)
from newsletters.adapters import pptx_adapter as _pa  # noqa: E402

R_CHART = _pa._R_CHART
R_PICTURE = _pa._R_PICTURE
R_SMARTART = _pa._R_SMARTART


class Expected:
    """The pinned expectation for one fixture — the golden contract, encoded inline.

    ``n_claims`` = the number of extractable paragraphs/cells/notes minted as verbatim claims (in
    transcript order). ``unextracted_reasons`` = the EXACT, ordered ``Coverage.unextracted[].reason``
    strings the adapter must emit. The accounting identity is then ``n_claims + len(unextracted) ==
    units walked`` — and ``len(claims) + len(unextracted)`` from the live result must equal that same
    total, with zero unaccounted units (no silent drop, nothing invented).
    """

    def __init__(self, *, n_claims: int, unextracted_reasons: list[str]) -> None:
        self.n_claims = n_claims
        self.unextracted_reasons = unextracted_reasons

    @property
    def total_units(self) -> int:
        return self.n_claims + len(self.unextracted_reasons)


# fixture name -> pinned expectation (every fixture's full routing, derived from the LIVE adapter).
EXPECTED: dict[str, Expected] = {
    # Two non-empty paragraphs + one empty paragraph (skipped). 2 claims, complete.
    "title_body.pptx": Expected(n_claims=2, unextracted_reasons=[]),
    # A free text box with three paragraphs. 3 claims, complete.
    "text_box.pptx": Expected(n_claims=3, unextracted_reasons=[]),
    # A 2x2 table, 3 filled + 1 empty cell (skipped). 3 claims, complete.
    "table.pptx": Expected(n_claims=3, unextracted_reasons=[]),
    # A single speaker note. 1 claim, complete.
    "notes.pptx": Expected(n_claims=1, unextracted_reasons=[]),
    # A chart -> the silent-loss disclosure (chart content out of scope). 0 claims + 1 disclosure.
    "chart.pptx": Expected(n_claims=0, unextracted_reasons=[R_CHART]),
    # An embedded 1x1 PNG -> disclosed, never extracted. 0 claims + 1 disclosure.
    "image.pptx": Expected(n_claims=0, unextracted_reasons=[R_PICTURE]),
    # A SmartArt diagram (criterion 3) -> disclosed, no fabricated text. 0 claims + 1 disclosure.
    "smartart.pptx": Expected(n_claims=0, unextracted_reasons=[R_SMARTART]),
    # A NESTED group (criterion 3): the readable member -> 1 claim; the unreadable picture member ->
    # 1 disclosure; both group NODES contribute nothing. 1 claim + 1 disclosure (the L3 accounting).
    "nested_group.pptx": Expected(n_claims=1, unextracted_reasons=[R_PICTURE]),
    # An empty slide -> nothing extracted AND nothing lost. 0 claims, 0 unextracted, complete.
    "empty_slide.pptx": Expected(n_claims=0, unextracted_reasons=[]),
}

FIXTURE_NAMES = sorted(EXPECTED)


def _distill(name: str) -> tuple[Source, DistillationResult]:
    """Parse a fixture with a FRESH adapter and distill it; return (source, result)."""
    adapter = _adapter()
    raw = (FIXTURE_DIR / name).read_bytes()
    source, _units, _adapter_unx = adapter.parse(raw, str(FIXTURE_DIR / name))
    return source, adapter.distill([source])


def test_corpus_is_nine_committed_fixtures() -> None:
    """The corpus is exactly the 9 committed `.pptx` fixtures the golden table expects.

    A missing or extra fixture (a corpus that silently shrank or grew) is a failure. The criterion-3
    pair (SmartArt + a nested group) is asserted present by name.
    """
    on_disk = sorted(p.name for p in FIXTURE_DIR.glob("*.pptx"))
    assert on_disk == FIXTURE_NAMES, on_disk
    assert len(FIXTURE_NAMES) == 9
    assert "smartart.pptx" in FIXTURE_NAMES  # ROADMAP criterion 3: SmartArt
    assert "nested_group.pptx" in FIXTURE_NAMES  # ROADMAP criterion 3: grouped shapes


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_zero_silent_drops(name: str) -> None:
    """The headline assertion (ADAPT-06, T-06-10): #claims + #unextracted == #units walked, exactly.

    Every paragraph/cell/note/object the adapter touches is on EXACTLY one side of the ledger —
    minted as a claim or recorded in unextracted[]. Empty paragraphs/cells and GROUP container nodes
    are nothing lost and are not counted. Nothing is silently dropped, and nothing is invented.
    """
    exp = EXPECTED[name]
    _src, result = _distill(name)
    claims = result.distillation.claims
    unextracted = result.coverage.unextracted

    assert len(claims) == exp.n_claims, (
        f"{name}: expected {exp.n_claims} claims, got {len(claims)}: {[c.text for c in claims]}"
    )
    # the unextracted reasons match the pinned contract, in order
    assert [u.reason for u in unextracted] == exp.unextracted_reasons, (
        f"{name}: unextracted reasons drifted from the contract: {[u.reason for u in unextracted]}"
    )
    # THE accounting identity — the executable form of "no silent drops"
    assert len(claims) + len(unextracted) == exp.total_units, (
        f"{name}: silent drop detected — {len(claims)} claims + {len(unextracted)} "
        f"unextracted != {exp.total_units} units walked"
    )


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_claims_are_verbatim_and_content_addressed(name: str) -> None:
    """Every claim is faithful (verbatim transcript span) and content-addressed.

    (Fixtures with zero claims — chart/image/smartart/empty_slide — pass vacuously; their disclosure
    is asserted by ``test_zero_silent_drops`` and the targeted routing tests.)
    """
    source, result = _distill(name)
    for claim in result.distillation.claims:
        assert claim.is_traced, f"{name}: claim {claim.text!r} is untraced"
        trace = claim.evidence[0]
        # faithful: the stored span IS the claim text
        assert claim.text == trace.span, f"{name}: claim.text != trace.span for {claim.text!r}"
        # re-slice the LIVE transcript at the recorded window -> reproduces the text
        assert trace.start is not None and trace.end is not None
        assert source.transcript[trace.start : trace.end] == claim.text, (
            f"{name}: transcript[{trace.start}:{trace.end}] != claim.text {claim.text!r}"
        )
        # content-addressed: minted through Trace.from_source (pinned a content hash)
        assert trace.is_addressed, f"{name}: trace for {claim.text!r} is not content-addressed"


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_coverage_honesty(name: str) -> None:
    """coverage.complete is True IFF nothing was dropped (the honesty invariant, asserted)."""
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
    adapter = _adapter()
    adapter.parse((FIXTURE_DIR / name).read_bytes(), source.id)
    result = assert_conforms(adapter, [source])
    assert isinstance(result, DistillationResult)
    # belt-and-braces: explicit lossless round-trip
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_determinism(name: str) -> None:
    """Parsing the same fixture twice yields an EQUAL result + a byte-identical Source (L5).

    The determinism property ADAPT-06 needs is asserted on the PARSED Source — identical bytes ->
    byte-identical ``model_dump_json`` — NOT on re-saved ``.pptx`` bytes, so it is immune to any
    python-pptx re-save byte drift (risk A3). No time/random leaks in.
    """
    s1, first = _distill(name)
    s2, second = _distill(name)
    assert first == second, f"{name}: non-deterministic distillation"
    assert s1.model_dump_json() == s2.model_dump_json(), (
        f"{name}: two parses of identical bytes produced non-identical Sources (L5 determinism)"
    )


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_roundtrip_coverage_parity(name: str) -> None:
    """THE Task-Zero property (T-06-10): persist the Source, distill on a FRESH adapter -> coverage
    UNCHANGED.

    Drops travel on ``Source.extraction``, so a JSON-round-tripped Source distills with IDENTICAL
    coverage on an adapter that never ``parse()``d it. Without the carrier a fresh adapter would
    silently lose every chart/picture/SmartArt drop and falsely report complete=True.
    """
    adapter_a = _adapter()
    raw = (FIXTURE_DIR / name).read_bytes()
    source, _units, _drops = adapter_a.parse(raw, str(FIXTURE_DIR / name))
    original = adapter_a.distill([source])

    reloaded = Source.model_validate_json(source.model_dump_json())
    adapter_b = _adapter()  # never parsed this source
    replayed = adapter_b.distill([reloaded])

    def sig(cov: object) -> tuple[bool, list[tuple[str, str]]]:
        return (
            cov.complete,  # type: ignore[attr-defined]
            [(u.locator.display, u.reason) for u in cov.unextracted],  # type: ignore[attr-defined]
        )

    assert sig(replayed.coverage) == sig(original.coverage), (
        f"{name}: coverage drifted across a Source round-trip on a fresh adapter"
    )


# --- targeted per-fixture routing assertions (the matrix is exercised, not just counted) ----- #


def test_smartart_is_disclosed_never_extracted() -> None:
    """ROADMAP criterion 3: a SmartArt diagram surfaces as ONE disclosure, emitting NO text claim.

    The frame is detected by ``shape_type is None`` + the diagram URI (no high-level API); its
    content is never editorialised into a fabricated claim.
    """
    _src, result = _distill("smartart.pptx")
    assert result.distillation.claims == []  # no fabricated SmartArt text
    assert [u.reason for u in result.coverage.unextracted] == [R_SMARTART]
    assert result.coverage.complete is False


def test_nested_group_member_text_extracted_unreadable_member_disclosed() -> None:
    """ROADMAP criterion 3: a NESTED group's readable member IS extracted; the unreadable member is
    disclosed; the GROUP nodes are neither a claim nor a drop (the L3 nested accounting).
    """
    source, result = _distill("nested_group.pptx")
    texts = [c.text for c in result.distillation.claims]
    # the readable text-box member (inside the inner group) IS extracted verbatim
    assert texts == ["grouped text"], texts
    assert "grouped text" in source.transcript
    # the unreadable picture member IS disclosed (never silently dropped)
    assert [u.reason for u in result.coverage.unextracted] == [R_PICTURE]
    # the two group container nodes contribute nothing: exactly 1 claim + 1 drop, no phantom nodes
    assert len(result.distillation.claims) + len(result.coverage.unextracted) == 2


def test_chart_is_disclosed_not_extracted() -> None:
    """A chart surfaces as a single silent-loss disclosure; no chart content leaks into a claim."""
    _src, result = _distill("chart.pptx")
    assert result.distillation.claims == []
    assert [u.reason for u in result.coverage.unextracted] == [R_CHART]
    assert result.coverage.complete is False


def test_image_is_disclosed_not_extracted() -> None:
    """An embedded picture surfaces as a single disclosure; no image bytes leak into a claim."""
    _src, result = _distill("image.pptx")
    assert result.distillation.claims == []
    assert [u.reason for u in result.coverage.unextracted] == [R_PICTURE]
    assert result.coverage.complete is False


def test_empty_slide_yields_nothing_and_loses_nothing() -> None:
    """An empty slide is not a silent drop — zero claims AND zero unextracted (nothing there)."""
    _src, result = _distill("empty_slide.pptx")
    assert result.distillation.claims == []
    assert result.coverage.unextracted == []
    assert result.coverage.complete is True


def test_table_emits_cells_row_major() -> None:
    """Table cells are extracted verbatim, row-major; the empty cell is skipped, not a phantom."""
    _src, result = _distill("table.pptx")
    assert [c.text for c in result.distillation.claims] == ["r0c0", "r0c1", "r1c0"]
    assert result.coverage.unextracted == []


def test_notes_emit_with_notes_locator() -> None:
    """A speaker note is extracted with the `Slide N / notes` locator (emitted last per slide)."""
    source, result = _distill("notes.pptx")
    assert [c.text for c in result.distillation.claims] == ["Speaker note line"]
    assert "Slide 1 / notes" in source.transcript
