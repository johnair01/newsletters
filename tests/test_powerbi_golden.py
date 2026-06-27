r"""Golden-file corpus for the Power BI adapter (ADAPT-06; ROADMAP Phase-7 success criterion 3).

This is the phase's *proof of correctness*. A tiny, committed, byte-reproducible PBIP project
(``tests/fixtures/powerbi/sample.PBIP-tree/``, authored by ``_author_fixtures.py`` with stdlib
``write_text`` — NO authoring dependency, the headline advantage over the Excel/PPTX goldens) plus a
few-byte ``.pbix`` deferral byte fixture drive the LIVE ``PowerBiAdapter`` end-to-end across its full
extract-vs-disclose fork — a TMDL semantic model (tables, columns with ``dataType``, a ``///``
description, a measure whose VERBATIM DAX is extracted as text never a value, a relationship) and a
PBIR report (a page, a PLAIN visual, and a Top-N-filtered + Sum-summarized + ``maxRows``-capped
visual). The Top-N/summarized visual is the explicit ROADMAP criterion-3 fixture: it must surface the
row-cap/aggregation taxonomy, never read as complete.

Unlike the pptx/excel goldens (which ``skipif`` the optional extra), this module has NO skip-mark: the
Power BI adapter is STDLIB-ONLY (pbixray DEFERRED, zero new dependency), so the corpus runs on a bare
install — that is itself part of the contract.

For the model+report fixture the suite asserts the load-bearing invariants:

1. **Zero silent drops** (ADAPT-06, T-07-14) — the accounting identity ``len(claims) + #normalize-
   misses == #units walked``. Every walked transcript unit is EITHER a content-addressed claim or an
   honest ``normalize()`` miss; a silent drop is, by construction, a TEST FAILURE. (The adapter-side
   ``_R_*`` taxonomy drops — measure-value / row-cap / no-data-rows — are ADDITIONAL honest
   disclosures ON TOP of the unit ledger, not units lost; they are pinned separately below.)
2. **The exact ``_R_*`` taxonomy** (T-07-15) — the Top-N/Sum/maxRows visual emits EXACTLY
   ``_R_TOPN`` + ``_R_AGGREGATED`` + ``_R_ROWLIMIT``; the measure emits ``_R_MEASURE_VALUE``; and the
   categorical whole-source ``_R_NO_DATA_ROWS`` is emitted ONCE -> ``Coverage.complete is False``
   (criterion 2, fail loud). The constants are IMPORTED from the adapter so a drift on EITHER side
   fails.
3. **Faithful spans** — every claim is verbatim: ``claim.text == trace.span`` AND re-slicing the live
   transcript at ``[trace.start:trace.end]`` reproduces it; the measure DAX is a verbatim claim.
4. **Content-addressed** — every claim's trace ``is_addressed``.
5. **Coverage honesty** — ``coverage.complete == (len(coverage.unextracted) == 0)``.
6. **Conformance + JSON round-trip** — ``assert_conforms(PowerBiAdapter(), [source])`` per fixture.
7. **Determinism on the parsed Source (L5)** — two parses -> an EQUAL result AND a byte-identical
   Source (``s1.model_dump_json() == s2.model_dump_json()``); ``timestamp == EPOCH_ZERO``.
8. **Round-trip coverage parity** (T-07-14) — persist the Source, distill on a FRESH adapter ->
   coverage UNCHANGED (drops travel on ``Source.extraction``).

Plus the ``.pbix`` deferral fixture: exactly ``_R_PBIX_BINARY``, empty transcript, ``complete is
False``, no crash (L1).

The expected per-fixture units/claims/reasons below were derived by DRIVING the LIVE adapter (A1
resolution — never assumed); they are the executable contract the fork must hold.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters.adapters import powerbi_adapter as _pb
from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.adapters.normalize import normalize
from newsletters.adapters.powerbi_adapter import PowerBiAdapter
from newsletters.distill import DistillationResult, assert_conforms
from newsletters.semantic import Source

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "powerbi"
PBIP_TREE = FIXTURE_DIR / "sample.PBIP-tree"
FAKE_PBIX = FIXTURE_DIR / "fake.pbix"

# The EXACT _R_* reason strings — IMPORTED from the adapter so a drift on EITHER side (the adapter's
# taxonomy OR this golden contract) is a failure (T-07-15). The golden NEVER hand-copies the strings.
R_TOPN = _pb._R_TOPN
R_AGGREGATED = _pb._R_AGGREGATED
R_ROWLIMIT = _pb._R_ROWLIMIT
R_MEASURE_VALUE = _pb._R_MEASURE_VALUE
R_NO_DATA_ROWS = _pb._R_NO_DATA_ROWS
R_PBIX_BINARY = _pb._R_PBIX_BINARY

# The verbatim measure DAX (extracted as TEXT, never a value — the hard rule). Mirrors the generator.
MEASURE_DAX = "SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])"


def _adapter() -> PowerBiAdapter:
    """A FRESH adapter (the adapter is stateless across parse/distill)."""
    return PowerBiAdapter()


def _distill_tree() -> tuple[Source, list[str], DistillationResult]:
    """Parse the committed PBIP tree with a FRESH adapter and distill it -> (source, units, result)."""
    adapter = _adapter()
    source, units, _drops = adapter.parse_path(str(PBIP_TREE))
    return source, units, adapter.distill([source])


def _reasons(unextracted: object) -> list[str]:
    return [u.reason for u in unextracted]  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# The pinned contract for the model+report tree (derived by driving the LIVE adapter)
# --------------------------------------------------------------------------- #

# Every one of the 21 walked transcript units is a content-addressed claim (zero normalize misses).
# 26 = the prior 21 + the 5 model.tmdl units (Model.name/culture/defaultPowerBIDataSourceVersion +
# two `ref table` references) that were SILENTLY DROPPED before the Phase-7 no-silent-drops hardening
# (the `model` object type + `ref` extraction were added; see RETRO 2026-06-18).
EXPECTED_N_UNITS = 26
# The adapter-side disclosures, in emission order: the measure's absent value, the Top-N/Sum/maxRows
# row-cap taxonomy, and the categorical whole-source no-data-rows truth (once).
EXPECTED_TREE_REASONS = [
    R_MEASURE_VALUE,
    R_TOPN,
    R_AGGREGATED,
    R_ROWLIMIT,
    R_NO_DATA_ROWS,
]


def test_corpus_files_exist() -> None:
    """The committed corpus is exactly the PBIP tree + the .pbix deferral the golden expects.

    A missing fixture (a corpus that silently shrank) is a failure. The criterion-3 Top-N/summarized
    visual is asserted present by name.
    """
    assert PBIP_TREE.is_dir(), "the sample.PBIP-tree fixture is missing"
    assert FAKE_PBIX.is_file(), "the fake.pbix deferral fixture is missing"
    topn = PBIP_TREE / "sample.Report/definition/pages/Overview/visuals/topProducts/visual.json"
    assert topn.is_file(), "the ROADMAP criterion-3 Top-N/summarized visual is missing"
    sales = PBIP_TREE / "sample.SemanticModel/definition/tables/Sales.tmdl"
    assert sales.is_file(), "the Sales TMDL table (the measure + columns) is missing"


# --------------------------------------------------------------------------- #
# 1. Zero silent drops (the headline assertion, ADAPT-06 / T-07-14)
# --------------------------------------------------------------------------- #


def test_zero_silent_drops() -> None:
    """#claims + #normalize-misses == #units walked, exactly — no silent drop, nothing invented.

    Every walked transcript unit is on EXACTLY one side of the ledger: a content-addressed claim or an
    honest ``normalize()`` miss. The adapter-side ``_R_*`` taxonomy (measure-value / row-cap /
    no-data-rows) is ADDITIONAL disclosure, asserted separately — it is not a unit lost.
    """
    source, units, _result = _distill_tree()
    claims, norm_misses = normalize(source, units)
    assert len(units) == EXPECTED_N_UNITS, (
        f"the corpus walked {len(units)} units, expected {EXPECTED_N_UNITS} "
        "(the committed tree changed — re-pin against the live adapter)"
    )
    assert len(claims) + len(norm_misses) == len(units), (
        f"silent drop detected — {len(claims)} claims + {len(norm_misses)} normalize-misses "
        f"!= {len(units)} units walked"
    )
    # this corpus is fully locatable: every unit is a verbatim claim, zero normalize misses
    assert len(norm_misses) == 0, (
        f"every authored unit must be a content-addressed claim; got {len(norm_misses)} misses: "
        f"{[u.locator.display for u in norm_misses]}"
    )


def test_no_line_is_read_but_undisclosed() -> None:
    """Guard the blind spot the unit-count identity structurally CANNOT see (RETRO 2026-06-18).

    ``#claims + #misses == #units`` only accounts for lines that BECAME units; it cannot catch a line
    the parser READS and then drops without emitting a unit OR a disclosure (the original ``model``/
    ``ref table`` silent-drop bug lived precisely here, inside this proof corpus). So we anchor to the
    source: every non-blank, non-``///`` line in each ``.tmdl`` must be accounted for as a unit, a
    structural continuation (fenced/indented expression body), or an explicit ``unparsed:`` disclosure
    — and the curated corpus must contain ZERO ``unparsed:`` (it is fully, faithfully handled).
    """
    from newsletters.adapters._tmdl import parse_tmdl

    for tmdl in sorted(PBIP_TREE.rglob("*.tmdl")):
        text = tmdl.read_text(encoding="utf-8")
        units, signals = parse_tmdl(text)
        unparsed = [s for s in signals if s.startswith("unparsed:")]
        assert unparsed == [], (
            f"{tmdl.name}: lines READ but neither extracted nor disclosed as a unit would silently "
            f"leak; the parser disclosed {unparsed} — every line must be a unit or a known signal"
        )
        # The previously-leaked model metadata is now positively present (regression anchor).
        if tmdl.name == "model.tmdl":
            values = {v for _p, v in units}
            assert "en-US" in values and "powerBI_V3" in values, "model culture/version leaked again"
            assert "table Sales" in values, "model `ref table` membership leaked again"


# --------------------------------------------------------------------------- #
# 2. The exact _R_* taxonomy + fail-loud completeness (T-07-15 / criterion 2)
# --------------------------------------------------------------------------- #


def test_row_cap_taxonomy_pinned_and_complete_is_false() -> None:
    """The Top-N/Sum/maxRows visual + the measure + the no-data-rows truth pin the EXACT taxonomy.

    The disclosures are asserted in emission order so a re-ordering or an added/dropped reason fails.
    ``_R_NO_DATA_ROWS`` fires exactly once -> ``complete is False`` (criterion 2, fail loud).
    """
    _source, _units, result = _distill_tree()
    reasons = _reasons(result.coverage.unextracted)
    assert reasons == EXPECTED_TREE_REASONS, (
        f"the unextracted taxonomy drifted from the pinned contract: {reasons}"
    )
    assert reasons.count(R_NO_DATA_ROWS) == 1, (
        "the categorical no-data-rows truth must be emitted exactly once per model export"
    )
    assert result.coverage.complete is False, (
        "a model export with row caps + no data rows must read as incomplete (fail loud)"
    )


def test_measure_dax_is_a_verbatim_claim_value_disclosed_absent() -> None:
    """The measure's DAX is a VERBATIM claim (text, never a value); its value is disclosed absent."""
    _source, _units, result = _distill_tree()
    texts = [c.text for c in result.distillation.claims]
    assert MEASURE_DAX in texts, "the measure DAX expression must be a verbatim claim, never a value"
    assert R_MEASURE_VALUE in _reasons(result.coverage.unextracted), (
        "the measure's absent computed value must be disclosed via _R_MEASURE_VALUE"
    )


def test_tmdl_model_text_extracted() -> None:
    """Table/column/measure names, the column dataType, the ``///`` description, and the relationship
    endpoints are all verbatim claims (the extract side of the fork)."""
    _source, _units, result = _distill_tree()
    texts = [c.text for c in result.distillation.claims]
    for expected in (
        "Sales",  # table name
        "Product",  # the other table
        "Total Sales",  # measure name
        "int64",  # a column dataType
        "The fact table of sales transactions",  # the /// description
        "Sales.'Product Key'",  # the relationship fromColumn
        "Product.'Product Key'",  # the relationship toColumn
    ):
        assert expected in texts, f"expected verbatim model claim {expected!r} not found"


def test_report_text_extracted() -> None:
    """The page display name, the plain visual's literal title, and a field reference are claims."""
    _source, _units, result = _distill_tree()
    texts = [c.text for c in result.distillation.claims]
    assert "Overview" in texts, "the page display name must be a claim"
    assert "Sales by product" in texts, "the plain visual's literal title must be a claim"
    assert "Sales.Quantity" in texts, "a visual field reference must be a claim"


# --------------------------------------------------------------------------- #
# 3-4. Faithful + content-addressed spans
# --------------------------------------------------------------------------- #


def test_claims_are_verbatim_and_content_addressed() -> None:
    """Every claim is faithful (verbatim transcript span) and content-addressed (minted via Trace)."""
    source, _units, result = _distill_tree()
    assert result.distillation.claims, "expected claims from the model+report tree"
    for claim in result.distillation.claims:
        assert claim.is_traced, f"claim {claim.text!r} is untraced"
        trace = claim.evidence[0]
        assert claim.text == trace.span, f"claim.text != trace.span for {claim.text!r}"
        assert trace.start is not None and trace.end is not None
        assert source.transcript[trace.start : trace.end] == claim.text, (
            f"transcript[{trace.start}:{trace.end}] != claim.text {claim.text!r}"
        )
        assert trace.is_addressed, f"trace for {claim.text!r} is not content-addressed"


# --------------------------------------------------------------------------- #
# 5. Coverage honesty
# --------------------------------------------------------------------------- #


def test_coverage_honesty() -> None:
    """coverage.complete is True IFF nothing was dropped (the honesty invariant)."""
    _source, _units, result = _distill_tree()
    cov = result.coverage
    assert cov.complete == (len(cov.unextracted) == 0), (
        f"coverage.complete={cov.complete} but unextracted has {len(cov.unextracted)}"
    )


# --------------------------------------------------------------------------- #
# 6. Conformance + lossless JSON round-trip
# --------------------------------------------------------------------------- #


def test_conformance_and_json_roundtrip() -> None:
    """assert_conforms drives span-containment + the lossless JSON round-trip for the tree."""
    adapter = _adapter()
    source, _units, _drops = adapter.parse_path(str(PBIP_TREE))
    result = assert_conforms(adapter, [source])
    assert isinstance(result, DistillationResult)
    assert DistillationResult.model_validate_json(result.model_dump_json()) == result


# --------------------------------------------------------------------------- #
# 7. Determinism on the parsed Source (L5)
# --------------------------------------------------------------------------- #


def test_determinism_and_epoch_zero() -> None:
    """Two parses yield an EQUAL result + a byte-identical Source; timestamp == EPOCH_ZERO."""
    a1, u1, r1 = _distill_tree()
    a2, u2, r2 = _distill_tree()
    assert u1 == u2, "two parses produced different unit orderings (non-deterministic walk)"
    assert r1 == r2, "non-deterministic distillation"
    assert a1.model_dump_json() == a2.model_dump_json(), (
        "two parses of the identical tree produced non-identical Sources (L5 determinism)"
    )
    assert a1.timestamp == EPOCH_ZERO, "PBIP has no intrinsic date -> timestamp must be EPOCH_ZERO"


# --------------------------------------------------------------------------- #
# 8. Round-trip coverage parity (T-07-14)
# --------------------------------------------------------------------------- #


def test_roundtrip_coverage_parity_on_fresh_adapter() -> None:
    """Persist the Source, distill on a FRESH adapter -> coverage UNCHANGED.

    Drops travel on ``Source.extraction``, so a JSON-round-tripped Source distills with IDENTICAL
    coverage on an adapter that never ``parse()``d it. Without the carrier a fresh adapter would
    silently lose every row-cap / measure-value / no-data-rows drop and falsely report complete=True.
    """
    adapter_a = _adapter()
    source, _units, _drops = adapter_a.parse_path(str(PBIP_TREE))
    original = adapter_a.distill([source])

    reloaded = Source.model_validate_json(source.model_dump_json())
    replayed = _adapter().distill([reloaded])  # never parsed this source

    def sig(cov: object) -> tuple[bool, list[tuple[str, str]]]:
        return (
            cov.complete,  # type: ignore[attr-defined]
            [(u.locator.display, u.reason) for u in cov.unextracted],  # type: ignore[attr-defined]
        )

    assert sig(replayed.coverage) == sig(original.coverage), (
        "coverage drifted across a Source round-trip on a fresh adapter"
    )


# --------------------------------------------------------------------------- #
# The .pbix deferral fixture (L1)
# --------------------------------------------------------------------------- #


def test_pbix_deferral() -> None:
    """The few-byte .pbix -> exactly _R_PBIX_BINARY, empty transcript, complete is False, no crash."""
    adapter = _adapter()
    raw = FAKE_PBIX.read_bytes()
    source, units, drops = adapter.parse(raw, str(FAKE_PBIX))
    assert source.transcript == "", "the .pbix deferral carries an empty transcript"
    assert units == [], "the .pbix deferral extracts no units (the ZIP is never decompressed)"
    assert _reasons(drops) == [R_PBIX_BINARY], "the .pbix deferral pins exactly _R_PBIX_BINARY"
    result = adapter.distill([source])
    assert _reasons(result.coverage.unextracted) == [R_PBIX_BINARY]
    assert result.coverage.complete is False, "a deferred .pbix must read as incomplete (fail loud)"
    assert result.distillation.claims == [], "the deferral fabricates no claims"


def test_pbix_deferral_round_trips_on_fresh_adapter() -> None:
    """The .pbix deferral's disclosure survives a Source JSON round-trip on a FRESH adapter."""
    adapter_a = _adapter()
    source, _units, _drops = adapter_a.parse(FAKE_PBIX.read_bytes(), str(FAKE_PBIX))
    original = adapter_a.distill([source])
    reloaded = Source.model_validate_json(source.model_dump_json())
    replayed = _adapter().distill([reloaded])
    assert _reasons(replayed.coverage.unextracted) == _reasons(original.coverage.unextracted)
    assert replayed.coverage.complete is False
