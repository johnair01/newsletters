r"""Unit suite for the ``PowerBiAdapter`` (Plan 07-03, ADAPT-05) — RED-first.

This suite is the executable contract for the registered ``"powerbi"`` backend that composes the
Wave-1 stdlib TMDL parser (``_tmdl.parse_tmdl``) and PBIR reader (``_pbir.extract_report`` /
``detect_row_caps``) onto the shared faithful spine (``normalize()`` / coverage codec /
``deterministic_timestamp``). It mirrors ``test_pptx_golden.py`` / ``test_excel_golden.py``
invariants but uses tiny INLINE fixtures (``write_text`` into ``tmp_path``) — the committed corpus
is Plan 07-04, not here.

Cases (derived directly from the plan's success criteria + the L3 ``_R_*`` taxonomy):

* criterion 1 — ``parse_path()`` over a minimal PBIP folder yields content-addressed claims via
  ``normalize()`` (``claim.text == trace.span == transcript[start:end]`` and ``trace.is_addressed``).
* L2 / Pitfall 1 — the measure's DAX is a VERBATIM claim; ``_R_MEASURE_VALUE`` discloses the absent
  computed value (never fabricated).
* criterion 2 — row-cap routing: Top-N -> ``_R_TOPN``, Sum aggregation -> ``_R_AGGREGATED``,
  DirectQuery partition -> ``_R_DIRECTQUERY``, a visual ``maxRows`` -> ``_R_ROWLIMIT``.
* L3 / Pitfall 3 — the categorical whole-source ``_R_NO_DATA_ROWS`` fires ONCE per model export, so
  ``Coverage.complete`` is False for any non-trivial export (fail loud).
* L1 — ``.pbix`` deferral: ``parse(raw, "fake.pbix")`` -> empty transcript + ONE ``_R_PBIX_BINARY``
  whole-source disclosure, ``complete`` False, no crash.
* V5 — a malformed ``.tmdl``/``.json`` (or undecodable bytes) is disclosed (never an unhandled crash).
* zero silent drops — ``len(claims) + len(unextracted) == units walked``.
* determinism — ``parse_path`` twice yields byte-identical Sources; ``timestamp == EPOCH_ZERO``.
* round-trip parity — drops survive a Source JSON round-trip on a FRESH adapter.
* conformance — ``assert_conforms(PowerBiAdapter(), [source])`` passes.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.adapters.powerbi_adapter import (
    _R_AGGREGATED,
    _R_DIRECTQUERY,
    _R_MEASURE_VALUE,
    _R_NO_DATA_ROWS,
    _R_PBIX_BINARY,
    _R_ROWLIMIT,
    _R_TOPN,
    _R_UNREADABLE,
    PowerBiAdapter,
)
from newsletters.distill.conformance import assert_conforms
from newsletters.semantic import Source


# --------------------------------------------------------------------------- #
# Inline PBIP fixture authoring (stdlib write_text into a tmp_path tree)
# --------------------------------------------------------------------------- #

_SALES_TMDL = """\
table Sales

\t/// The fact table of sales transactions
\tmeasure 'Total Sales' = SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])
\t\tformatString: $ #,##0

\tcolumn Quantity
\t\tdataType: int64
\t\tsummarizeBy: sum

\tcolumn 'Net Price'
\t\tdataType: decimal
"""

_PRODUCT_TMDL = """\
table Product

\tcolumn 'Product Key'
\t\tdataType: int64
"""

_RELATIONSHIPS_TMDL = """\
relationship abc-123
\tfromColumn: Sales.'Product Key'
\ttoColumn: Product.'Product Key'
"""

# A DirectQuery partition -> the TMDL "directQuery" signal -> _R_DIRECTQUERY.
_DQ_TABLE_TMDL = """\
table Live

\tpartition Live-DQ = m
\t\tmode: directQuery
\t\tsource: let Source = ... in Source
"""


def _plain_visual() -> dict:
    """A plain table visual: a title + a field projection -> verbatim claims, NO row-cap."""
    return {
        "name": "plainTable",
        "visual": {
            "visualType": "tableEx",
            "title": {
                "properties": {
                    "text": {"expr": {"Literal": {"Value": "'Sales by product'"}}}
                }
            },
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "Sales"}},
                                        "Property": "Quantity",
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        },
    }


def _topn_visual() -> dict:
    """A Top-5 + Sum-aggregated visual -> _R_TOPN + _R_AGGREGATED + a maxRows -> _R_ROWLIMIT."""
    return {
        "name": "topProducts",
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Aggregation": {
                                        "Expression": {
                                            "Column": {
                                                "Expression": {
                                                    "SourceRef": {"Entity": "Sales"}
                                                },
                                                "Property": "Quantity",
                                            }
                                        },
                                        "Function": 0,
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            "objects": {
                "general": [{"properties": {"maxRows": 30}}],
            },
        },
        "filterConfig": {
            "filters": [
                {
                    "filterType": "TopN",
                    "operator": "Top",
                    "itemCount": 5,
                }
            ]
        },
    }


def _write_pbip(root: pathlib.Path, *, with_dq: bool = False) -> pathlib.Path:
    """Author a minimal PBIP folder tree under ``root`` (stdlib write_text, byte-reproducible)."""
    sm_def = root / "sample.SemanticModel" / "definition"
    tables = sm_def / "tables"
    tables.mkdir(parents=True)
    (root / "sample.pbip").write_text(
        json.dumps({"version": "1.0", "artifacts": []}), encoding="utf-8"
    )
    (sm_def / "model.tmdl").write_text("model Model\n\tculture: en-US\n", encoding="utf-8")
    (sm_def / "relationships.tmdl").write_text(_RELATIONSHIPS_TMDL, encoding="utf-8")
    (tables / "Sales.tmdl").write_text(_SALES_TMDL, encoding="utf-8")
    (tables / "Product.tmdl").write_text(_PRODUCT_TMDL, encoding="utf-8")
    if with_dq:
        (tables / "Live.tmdl").write_text(_DQ_TABLE_TMDL, encoding="utf-8")

    rpt_def = root / "sample.Report" / "definition"
    overview = rpt_def / "pages" / "Overview"
    plain = overview / "visuals" / "plainTable"
    topn = overview / "visuals" / "topProducts"
    plain.mkdir(parents=True)
    topn.mkdir(parents=True)
    (root / "sample.Report" / "definition.pbir").write_text(
        json.dumps({"version": "4.0", "datasetReference": {}}), encoding="utf-8"
    )
    (rpt_def / "report.json").write_text(json.dumps({"name": "Report"}), encoding="utf-8")
    (overview / "page.json").write_text(
        json.dumps({"name": "Overview", "displayName": "Overview"}), encoding="utf-8"
    )
    (plain / "visual.json").write_text(json.dumps(_plain_visual()), encoding="utf-8")
    (topn / "visual.json").write_text(json.dumps(_topn_visual()), encoding="utf-8")
    return root


def _reasons(drops) -> list[str]:
    return [u.reason for u in drops]


# --------------------------------------------------------------------------- #
# criterion 1 — content-addressed extraction via the shared normalize()
# --------------------------------------------------------------------------- #


def test_parse_path_yields_content_addressed_claims(tmp_path: pathlib.Path) -> None:
    """Every claim is a verbatim, content-addressed span: text == trace.span == transcript slice."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _units, _drops = adapter.parse_path(str(root))
    result = adapter.distill([source])

    assert result.distillation.claims, "expected at least one extracted claim from the model"
    for claim in result.distillation.claims:
        assert claim.evidence, "every claim must carry >=1 evidence Trace"
        trace = claim.evidence[0]
        assert trace.is_addressed, "claim's trace must be content-addressed"
        assert claim.text == trace.span, "claim text must equal its trace span (verbatim)"
        assert source.transcript[trace.start : trace.end] == claim.text, (
            "the trace span must be the exact transcript slice"
        )


def test_table_and_measure_names_extracted_verbatim(tmp_path: pathlib.Path) -> None:
    """The table name, the measure name, and the column dataType are verbatim claims."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    texts = [c.text for c in adapter.distill([source]).distillation.claims]
    assert "Sales" in texts
    assert "Total Sales" in texts
    assert "int64" in texts


# --------------------------------------------------------------------------- #
# L2 / Pitfall 1 — DAX is a verbatim claim; the computed value is disclosed absent
# --------------------------------------------------------------------------- #


def test_measure_dax_is_verbatim_and_value_disclosed_absent(
    tmp_path: pathlib.Path,
) -> None:
    """The measure's DAX text is a verbatim claim; _R_MEASURE_VALUE discloses the absent value."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    result = adapter.distill([source])
    dax = "SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])"
    assert dax in [c.text for c in result.distillation.claims], (
        "the measure DAX expression must be extracted verbatim, never a value"
    )
    assert _R_MEASURE_VALUE in _reasons(result.coverage.unextracted), (
        "a measure's absent computed value must be disclosed via _R_MEASURE_VALUE"
    )


# --------------------------------------------------------------------------- #
# criterion 2 — the row-cap / aggregation taxonomy routes to unextracted[]
# --------------------------------------------------------------------------- #


def test_topn_and_aggregation_and_rowlimit_routed(tmp_path: pathlib.Path) -> None:
    """The Top-N + Sum-aggregated + maxRows visual drives _R_TOPN, _R_AGGREGATED, _R_ROWLIMIT."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    reasons = _reasons(adapter.distill([source]).coverage.unextracted)
    assert _R_TOPN in reasons
    assert _R_AGGREGATED in reasons
    assert _R_ROWLIMIT in reasons


def test_directquery_partition_routed(tmp_path: pathlib.Path) -> None:
    """A DirectQuery partition (TMDL mode signal) routes to _R_DIRECTQUERY."""
    root = _write_pbip(tmp_path / "p", with_dq=True)
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    reasons = _reasons(adapter.distill([source]).coverage.unextracted)
    assert _R_DIRECTQUERY in reasons


# --------------------------------------------------------------------------- #
# L3 / Pitfall 3 — the categorical whole-source _R_NO_DATA_ROWS forces complete=False
# --------------------------------------------------------------------------- #


def test_no_data_rows_emitted_once_and_forces_incomplete(
    tmp_path: pathlib.Path,
) -> None:
    """Extracting a model emits _R_NO_DATA_ROWS exactly once and forces Coverage.complete=False."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    coverage = adapter.distill([source]).coverage
    reasons = _reasons(coverage.unextracted)
    assert reasons.count(_R_NO_DATA_ROWS) == 1, (
        "the categorical no-data-rows truth must be emitted exactly once per model export"
    )
    assert coverage.complete is False, (
        "any non-trivial model export must read as incomplete (fail loud)"
    )


# --------------------------------------------------------------------------- #
# L1 — the .pbix binary deferral (whole-source disclosure, no crash)
# --------------------------------------------------------------------------- #


def test_pbix_binary_deferral() -> None:
    """A few-byte non-PBIP binary via parse(raw, 'fake.pbix') -> one _R_PBIX_BINARY, no crash."""
    adapter = PowerBiAdapter()
    raw = b"PK\x03\x04this-is-not-a-real-pbix"
    source, units, drops = adapter.parse(raw, "fake.pbix")
    assert source.transcript == "", "the .pbix deferral carries an empty transcript"
    assert units == []
    assert _reasons(drops) == [_R_PBIX_BINARY]
    coverage = adapter.distill([source]).coverage
    assert _R_PBIX_BINARY in _reasons(coverage.unextracted)
    assert coverage.complete is False


def test_zip_bytes_route_to_pbix_branch_even_without_extension() -> None:
    """Raw ZIP/OLE bytes (a .pbix is a zip) route to the binary deferral regardless of path."""
    adapter = PowerBiAdapter()
    raw = b"PK\x03\x04" + b"\x00" * 20  # ZIP magic
    source, _units, drops = adapter.parse(raw, "mystery.bin")
    assert _R_PBIX_BINARY in _reasons(drops)


# --------------------------------------------------------------------------- #
# V5 — a malformed file is disclosed whole-source, never an unhandled crash
# --------------------------------------------------------------------------- #


def test_malformed_json_disclosed_not_crashed(tmp_path: pathlib.Path) -> None:
    """A single dropped, malformed .json is disclosed via _R_UNREADABLE, never a crash."""
    bad = tmp_path / "broken.json"
    bad.write_text("{not valid json", encoding="utf-8")
    adapter = PowerBiAdapter()
    source, _units, drops = adapter.parse(bad.read_bytes(), str(bad))
    assert any(_R_UNREADABLE.split("(")[0] in r for r in _reasons(drops)), (
        "a malformed JSON file must be disclosed, never crash"
    )


def test_single_tmdl_file_parses(tmp_path: pathlib.Path) -> None:
    """A single dropped .tmdl byte input parses through the same serializer."""
    f = tmp_path / "Sales.tmdl"
    f.write_text(_SALES_TMDL, encoding="utf-8")
    adapter = PowerBiAdapter()
    source, _units, _drops = adapter.parse(f.read_bytes(), str(f))
    texts = [c.text for c in adapter.distill([source]).distillation.claims]
    assert "Total Sales" in texts


# --------------------------------------------------------------------------- #
# Accounting, determinism, conformance, round-trip parity
# --------------------------------------------------------------------------- #


def test_zero_silent_drops_accounting(tmp_path: pathlib.Path) -> None:
    """len(claims) + len(unextracted) accounts for every walked unit (zero silent drops).

    Every walked unit is either a content-addressed claim or a not-locatable disclosure; the
    adapter-side taxonomy drops (row-cap / no-data-rows / measure-value) are ADDITIONAL honest
    disclosures, so claims + normalize-misses == units walked.
    """
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, units, _drops = adapter.parse_path(str(root))
    claims, norm_unx = __import__(
        "newsletters.adapters.normalize", fromlist=["normalize"]
    ).normalize(source, units)
    assert len(claims) + len(norm_unx) == len(units), (
        "every walked unit must be a claim or an honest normalize miss — zero silent drops"
    )


def test_determinism_and_epoch_zero(tmp_path: pathlib.Path) -> None:
    """parse_path twice yields byte-identical Sources; timestamp == EPOCH_ZERO (PBIP has no date)."""
    root = _write_pbip(tmp_path / "p")
    s1, _u1, _d1 = PowerBiAdapter().parse_path(str(root))
    s2, _u2, _d2 = PowerBiAdapter().parse_path(str(root))
    assert s1.timestamp == EPOCH_ZERO
    assert s1.model_dump_json() == s2.model_dump_json()


def test_conformance(tmp_path: pathlib.Path) -> None:
    """assert_conforms passes: span-containment + truth-only + JSON round-trip."""
    root = _write_pbip(tmp_path / "p")
    adapter = PowerBiAdapter()
    source, _u, _d = adapter.parse_path(str(root))
    assert_conforms(adapter, [source])


def test_roundtrip_coverage_parity_on_fresh_adapter(tmp_path: pathlib.Path) -> None:
    """Drops survive a Source JSON round-trip on a FRESH adapter (carried on Source.extraction)."""
    root = _write_pbip(tmp_path / "p")
    adapter_a = PowerBiAdapter()
    source, _u, _d = adapter_a.parse_path(str(root))
    original = adapter_a.distill([source])

    reloaded = Source.model_validate_json(source.model_dump_json())
    replayed = PowerBiAdapter().distill([reloaded])

    sig_a = (
        original.coverage.complete,
        sorted(_reasons(original.coverage.unextracted)),
    )
    sig_b = (
        replayed.coverage.complete,
        sorted(_reasons(replayed.coverage.unextracted)),
    )
    assert sig_a == sig_b, "coverage drifted across a Source round-trip on a fresh adapter"


def test_registered_under_powerbi() -> None:
    """The adapter resolves through the distill socket under the name 'powerbi'."""
    from newsletters.distill import resolve

    assert resolve("powerbi").name == "powerbi"
