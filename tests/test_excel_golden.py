"""Golden-file corpus for the Excel adapter (ADAPT-06; ROADMAP Phase 5 success criterion 3).

This is the phase's *proof of correctness*. Eight tiny, committed, byte-reproducible `.xlsx`
fixtures (`tests/fixtures/xlsx/*.xlsx`, authored by `_author_fixtures.py`) drive `ExcelAdapter`
end-to-end across its full extract-vs-disclose fork — a formula WITH a cached value, the natural
openpyxl formula with NO cache (the faithfulness crux), merged cells, multiple sheets, mixed value
types, empty cells, an error cell, and a chart (the silent-loss disclosure). For EVERY fixture the
test asserts the load-bearing invariants:

1. **Zero silent drops** — the accounting identity ``len(claims) + len(unextracted) == units walked``
   (ADAPT-06). A silent drop is, by construction, a TEST FAILURE (threat T-05-10). Every non-empty,
   extractable cell is a claim; every uncomputed-formula / error cell and every chart/image is an
   ``unextracted[]`` disclosure; empty cells and merge-covered (non-anchor) cells are correctly NOT
   counted (they are nothing lost), so they never inflate the ledger.
2. **Faithful spans** — every claim is verbatim: ``claim.text == trace.span`` AND re-slicing the
   live transcript at ``[trace.start:trace.end]`` reproduces it.
3. **Content-addressed** — every claim's trace ``is_addressed`` (minted via ``Trace.from_source``).
4. **Coverage honesty** — ``coverage.complete == (len(coverage.unextracted) == 0)``.
5. **Conformance + round-trip** — ``assert_conforms(ExcelAdapter(), [source])`` passes per fixture;
   ``DistillationResult`` round-trips losslessly through JSON.
6. **Determinism** — parsing the same fixture twice yields an EQUAL ``DistillationResult``.
7. **Round-trip coverage parity** (threat T-05-12, the Plan-01 hardening proven on Excel) —
   ``model_dump_json`` the Source, reload it, distill on a FRESH adapter -> coverage EQUALS the
   original. Drops travel on ``Source.extraction``, so coverage survives persistence.

Plus targeted per-fixture ROUTING assertions: ``formula_no_cache`` routes its formula cell to
``unextracted[]`` and emits NO ``"0"``/``""`` claim (the criterion-2 faithfulness proof);
``error_cell`` routes to ``unextracted[]``; ``chart_or_image`` discloses the chart; ``merged_cells``
emits the anchor exactly once.

The expected per-fixture counts/reasons below were derived by driving the LIVE adapter (not
assumed); they are the executable contract that the fork holds across the whole matrix. The whole
module is skipped cleanly when the optional ``[excel]`` extra (openpyxl) is absent, so the
bare-install gate is unaffected.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("openpyxl") is None,
    reason="optional [excel] extra (openpyxl) not installed",
)

from newsletters.distill import DistillationResult, assert_conforms  # noqa: E402
from newsletters.semantic import Source  # noqa: E402

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "xlsx"


def _adapter():
    """A FRESH ExcelAdapter (imported lazily so this module imports without the [excel] extra)."""
    from newsletters.adapters.excel_adapter import ExcelAdapter

    return ExcelAdapter()


class Expected:
    """The pinned expectation for one fixture — the golden contract, encoded inline.

    ``n_claims`` = the number of extractable cells minted as verbatim claims (in transcript order).
    ``unextracted_reasons`` = the EXACT, ordered ``Coverage.unextracted[].reason`` strings the
    adapter must emit. The accounting identity is then ``n_claims + len(unextracted_reasons) ==
    units walked`` — and ``len(claims) + len(unextracted)`` from the live result must equal that same
    total, with zero unaccounted units (no silent drop, nothing invented).
    """

    def __init__(self, *, n_claims: int, unextracted_reasons: list[str]) -> None:
        self.n_claims = n_claims
        self.unextracted_reasons = unextracted_reasons

    @property
    def total_units(self) -> int:
        return self.n_claims + len(self.unextracted_reasons)


# The exact unextracted reason strings (copied verbatim from 05-03-SUMMARY / excel_adapter.py,
# confirmed against the LIVE adapter over each committed fixture).
R_FORMULA_NO_CACHE = (
    "formula cell A2 has no cached value (uncomputed: '=A1*10') — not faithfully extractable"
)
R_ERROR_CELL = "error cell A2: #DIV/0!"
R_CHART = "Charted: chart not extracted (chart content is out of scope)"

# fixture name -> pinned expectation (every fixture's full routing, by construction).
EXPECTED: dict[str, Expected] = {
    # A formula whose cache IS present (XML-injected): A1 literal + A2 cache -> 2 claims, complete.
    "formula_with_cache.xlsx": Expected(n_claims=2, unextracted_reasons=[]),
    # THE crux: an openpyxl formula has NO cache -> A1 emits "2", A2 routes to unextracted
    # (NEVER a "0"/"" claim). 1 claim + 1 disclosure.
    "formula_no_cache.xlsx": Expected(n_claims=1, unextracted_reasons=[R_FORMULA_NO_CACHE]),
    # A 2x2 merge: the anchor "merged header" is emitted ONCE, the 3 covered cells are blank and
    # skipped (NOT drops); plus "below". 2 claims, complete.
    "merged_cells.xlsx": Expected(n_claims=2, unextracted_reasons=[]),
    # Two sheets, workbook order: "first one","first two","second one". 3 claims, complete.
    "multi_sheet.xlsx": Expected(n_claims=3, unextracted_reasons=[]),
    # One cell per value->string rule (text/int/float/bool/date/datetime). 6 claims, complete.
    "mixed_types.xlsx": Expected(n_claims=6, unextracted_reasons=[]),
    # Sparse cells with genuine blanks between them: blanks are skipped, NOT drops. 2 claims.
    "empty_cells.xlsx": Expected(n_claims=2, unextracted_reasons=[]),
    # An error cell (data_type 'e'): A1 emits "real value", A2 routes to unextracted. 1 claim + 1.
    "error_cell.xlsx": Expected(n_claims=1, unextracted_reasons=[R_ERROR_CELL]),
    # A chart over a 4-cell data table: 4 data claims + 1 chart disclosure (content out of scope).
    "chart_or_image.xlsx": Expected(n_claims=4, unextracted_reasons=[R_CHART]),
}

FIXTURE_NAMES = sorted(EXPECTED)


def _distill(name: str) -> tuple[Source, DistillationResult]:
    """Parse a fixture with a FRESH adapter and distill it; return (source, result)."""
    adapter = _adapter()
    raw = (FIXTURE_DIR / name).read_bytes()
    source, _units, _adapter_unx = adapter.parse(raw, str(FIXTURE_DIR / name))
    return source, adapter.distill([source])


def test_corpus_is_eight_committed_fixtures() -> None:
    """The corpus is exactly the 8 committed `.xlsx` fixtures the golden table expects.

    A missing or extra fixture (a corpus that silently shrank or grew) is a failure.
    """
    on_disk = sorted(p.name for p in FIXTURE_DIR.glob("*.xlsx"))
    assert on_disk == FIXTURE_NAMES, on_disk
    assert len(FIXTURE_NAMES) == 8


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_zero_silent_drops(name: str) -> None:
    """The headline assertion (ADAPT-06, T-05-10): #claims + #unextracted == #units walked, exactly.

    Every cell/object the adapter touches is on EXACTLY one side of the ledger — minted as a claim
    or recorded in unextracted[]. Empty + merge-covered cells are nothing lost and are not counted.
    Nothing is silently dropped, and nothing is invented.
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
    """Every claim is faithful (verbatim transcript span) and content-addressed."""
    source, result = _distill(name)
    claims = result.distillation.claims
    assert claims, f"{name}: expected at least one claim"
    for claim in claims:
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
    """Parsing the same fixture twice yields an EQUAL result — no time/random leaks in."""
    _s1, first = _distill(name)
    _s2, second = _distill(name)
    assert first == second, f"{name}: non-deterministic distillation"


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_roundtrip_coverage_parity(name: str) -> None:
    """THE Task-Zero property (T-05-12): persist the Source, distill on a FRESH adapter -> coverage
    UNCHANGED.

    Drops travel on ``Source.extraction``, so a JSON-round-tripped Source distills with IDENTICAL
    coverage on an adapter that never ``parse()``d it. Without the carrier a fresh adapter would
    silently lose every formula-cache-gap / error / chart drop and falsely report complete=True.
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


def test_formula_no_cache_routes_to_unextracted_never_zero() -> None:
    """The criterion-2 crux: an uncomputed formula is disclosed, NEVER fabricated as 0/empty."""
    source, result = _distill("formula_no_cache.xlsx")
    claims = result.distillation.claims
    # the formula cell is NOT emitted as a "0" or "" claim
    assert all(c.text not in ("0", "") for c in claims), (
        f"formula_no_cache fabricated a value: {[c.text for c in claims]}"
    )
    # only the literal A1="2" is a claim; the formula A2 is disclosed
    assert [c.text for c in claims] == ["2"]
    assert [u.reason for u in result.coverage.unextracted] == [R_FORMULA_NO_CACHE]
    # the unextracted entry names the A2 cell (Sheet!coord locator)
    assert result.coverage.unextracted[0].locator.display == "Calc!A2"
    assert result.coverage.complete is False


def test_formula_with_cache_emits_the_cached_value() -> None:
    """The contrast case: a formula WITH a cache emits the cached value as a verbatim claim."""
    _src, result = _distill("formula_with_cache.xlsx")
    assert [c.text for c in result.distillation.claims] == ["2", "20"]
    assert result.coverage.unextracted == []
    assert result.coverage.complete is True


def test_error_cell_routes_to_unextracted() -> None:
    """An error cell (data_type 'e') is disclosed, not emitted; the literal beside it is extracted."""
    _src, result = _distill("error_cell.xlsx")
    assert [u.reason for u in result.coverage.unextracted] == [R_ERROR_CELL]
    assert any(c.text == "real value" for c in result.distillation.claims)
    assert all(c.text != "#DIV/0!" for c in result.distillation.claims)


def test_chart_is_disclosed_not_extracted() -> None:
    """A chart surfaces as a single silent-loss disclosure; no chart content leaks into a claim."""
    _src, result = _distill("chart_or_image.xlsx")
    assert [u.reason for u in result.coverage.unextracted] == [R_CHART]
    assert result.coverage.complete is False
    # only the 4 data-table cells are claims (the chart content is never extracted)
    assert sorted(c.text for c in result.distillation.claims) == ["5", "cat", "val", "x"]


def test_merged_anchor_emitted_exactly_once() -> None:
    """A merged range emits its top-left anchor ONCE; the covered cells are blank, not phantoms."""
    _src, result = _distill("merged_cells.xlsx")
    texts = [c.text for c in result.distillation.claims]
    assert texts.count("merged header") == 1, texts
    assert "below" in texts
    assert len(texts) == 2  # exactly the anchor + the below cell, no phantom blanks
    assert result.coverage.unextracted == []  # a faithful merge is nothing lost


def test_mixed_types_value_to_string_rules() -> None:
    """Each Python value type renders by the locked value->string rule, verbatim in the transcript."""
    source, result = _distill("mixed_types.xlsx")
    texts = [c.text for c in result.distillation.claims]
    assert texts == [
        "hello text",  # str verbatim
        "42",  # int -> str(int), never "42.0"
        "3.14",  # float -> repr(float)
        "TRUE",  # bool -> TRUE/FALSE (checked before int)
        "2026-06-17T00:00:00",  # a date cell comes back as a datetime -> .isoformat()
        "2026-06-17T09:30:00",  # datetime -> .isoformat()
    ], texts
    # every rendered value is verbatim in the transcript
    for t in texts:
        assert t in source.transcript


def test_multi_sheet_workbook_order() -> None:
    """Claims appear in workbook order, sheet by sheet, row-major within each sheet."""
    _src, result = _distill("multi_sheet.xlsx")
    assert [c.text for c in result.distillation.claims] == [
        "first one",
        "first two",
        "second one",
    ]
