r"""Author the byte-reproducible Power BI golden corpus (ADAPT-06; ROADMAP Phase-7 criterion 3).

THE HEADLINE ADVANTAGE over the Excel/PPTX golden corpora: a PBIP project is **plain text** —
TMDL (a YAML-like indent format) for the semantic model and PBIR JSON for the report. So this
generator writes the entire fixture tree with stdlib ``pathlib.write_text`` / ``write_bytes`` ONLY —
NO third-party authoring dependency (no openpyxl, no python-pptx). Because nothing reads a clock or
``random`` and every byte is a literal in this file, ``sha256(tree)`` is stable across processes and
the committed ``sample.PBIP-tree/`` is a clean, reviewable git diff. (The load-bearing property the
golden test asserts is determinism on the PARSED ``Source`` — see ``test_powerbi_golden.py`` — but
byte-reproducible source files make the corpus auditable.)

THE CORPUS (one PBIP tree + one ``.pbix`` deferral byte fixture):

``sample.PBIP-tree/`` — a minimal but complete PBIP project authored against the documented
microsoft/json-schemas PBIR ``visualContainer`` + Power BI filter shape (07-RESEARCH Assumption A1).
It is driven END-TO-END by the LIVE ``PowerBiAdapter.parse_path`` in the golden. It contains:

  * ``sample.pbip`` + ``definition.pbism`` — the PBIP entry pointer + dataset settings (pointer JSON;
    not walked for units — they carry no model/report text — but committed so the tree is a real PBIP).
  * ``sample.SemanticModel/definition/`` (TMDL, the model):
      - ``model.tmdl``         — the model header (culture; ``ref`` table lines, which the parser skips).
      - ``relationships.tmdl`` — ONE relationship Sales->Product (``fromColumn`` / ``toColumn`` units).
      - ``tables/Sales.tmdl``  — a table with a ``///`` description, two columns
        (``Quantity`` int64 / ``Net Price`` decimal, each with ``dataType`` + ``summarizeBy``), and a
        measure ``'Total Sales'`` whose VERBATIM DAX ``= SUMX(...)`` is extracted as TEXT (never a
        value) and additionally discloses ``_R_MEASURE_VALUE``; plus a ``formatString``.
      - ``tables/Product.tmdl`` — a one-column key table (the relationship's other endpoint).
  * ``sample.Report/definition/`` (PBIR, the report):
      - ``definition.pbir``        — the report->dataset byPath reference (pointer JSON; not walked).
      - ``report.json``            — report-level metadata.
      - ``pages/pages.json``       — the page-order pointer (pointer JSON; not walked).
      - ``pages/Overview/page.json`` — a page with ``displayName`` "Overview" (-> a page claim).
      - ``pages/Overview/visuals/plainTable/visual.json``  — a PLAIN table visual: a literal title +
        a column field projection -> verbatim claims, NO row-cap (the extract side of the fork).
      - ``pages/Overview/visuals/topProducts/visual.json`` — a Top-N-filtered + Sum-summarized visual
        with a ``maxRows`` cap: ``filterType: TopN`` (-> ``_R_TOPN``), a ``Sum`` ``Aggregation``
        (-> ``_R_AGGREGATED``), and ``maxRows`` (-> ``_R_ROWLIMIT``) — the disclose side of the fork.

``fake.pbix`` — a few-byte NON-PBIP binary (the ZIP local-file magic + filler). It need NOT be a real
``.pbix``: pbixray is DEFERRED (L1 / zero new dependency), so only the ``_R_PBIX_BINARY`` deferral is
tested — the ZIP is NEVER decompressed. Written via ``write_bytes``.

Every JSON shape here mirrors the shapes the 07-03 unit suite already proved drive the LIVE
detectors (``_pbir.detect_row_caps`` / ``extract_report``), so the golden pins the ``_R_*`` taxonomy
by DRIVING the adapter, never by hand-guessing (A1 resolution method).

Run:  .venv/bin/python tests/fixtures/powerbi/_author_fixtures.py
"""

from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent
TREE = HERE / "sample.PBIP-tree"

# --------------------------------------------------------------------------- #
# The verbatim DAX measure expression — extracted as TEXT, never evaluated (Pitfall 1 / the hard
# rule "Faithful, not suggestive"). The golden asserts THIS exact string is a claim.
# --------------------------------------------------------------------------- #
MEASURE_DAX = "SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])"

# TMDL is single-tab-indented (the parser tracks relative indent depth). Author tabs explicitly.
_SALES_TMDL = (
    "table Sales\n"
    "\n"
    "\t/// The fact table of sales transactions\n"
    f"\tmeasure 'Total Sales' = {MEASURE_DAX}\n"
    "\t\tformatString: $ #,##0\n"
    "\n"
    "\tcolumn Quantity\n"
    "\t\tdataType: int64\n"
    "\t\tsummarizeBy: sum\n"
    "\n"
    "\tcolumn 'Net Price'\n"
    "\t\tdataType: decimal\n"
    "\t\tsummarizeBy: none\n"
)

_PRODUCT_TMDL = (
    "table Product\n"
    "\n"
    "\tcolumn 'Product Key'\n"
    "\t\tdataType: int64\n"
)

_RELATIONSHIPS_TMDL = (
    "relationship abc-123\n"
    "\tfromColumn: Sales.'Product Key'\n"
    "\ttoColumn: Product.'Product Key'\n"
)

# The model header. ``ref table`` lines are NOT object headers the parser extracts (``ref`` is not a
# known object type) — they are skipped, contributing no units (and so no silent drop: they name
# nothing extractable that the per-table files don't already carry).
_MODEL_TMDL = (
    "model Model\n"
    "\tculture: en-US\n"
    "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
    "\n"
    "ref table Sales\n"
    "ref table Product\n"
)


def _plain_visual() -> dict:
    """A plain table visual: a literal title + a Column field projection -> verbatim claims, NO cap.

    Authored against the PBIR ``visualContainer`` shape: ``visual.title.properties.text.expr.Literal``
    for the title and ``visual.query.queryState.<role>.projections[].field.Column`` for the field ref.
    """
    return {
        "name": "plainTable",
        "position": {"x": 0, "y": 0, "width": 400, "height": 300},
        "visual": {
            "visualType": "tableEx",
            "title": {
                "properties": {"text": {"expr": {"Literal": {"Value": "'Sales by product'"}}}}
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
    """A Top-5-filtered + Sum-summarized visual with a maxRows cap (the disclose side of the fork).

    Authored against the documented Power BI filter shape (``filterConfig.filters[].filterType: TopN``)
    and the ``QueryAggregateFunction`` enum (``Aggregation.Function: 0`` == Sum). The LIVE
    ``detect_row_caps`` turns these into ``topn`` + ``aggregated`` + ``rowlimit`` detections, which the
    adapter maps to ``_R_TOPN`` + ``_R_AGGREGATED`` + ``_R_ROWLIMIT`` (pinned in the golden).
    """
    return {
        "name": "topProducts",
        "position": {"x": 0, "y": 320, "width": 400, "height": 300},
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
                                                "Expression": {"SourceRef": {"Entity": "Sales"}},
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
            "objects": {"general": [{"properties": {"maxRows": 30}}]},
        },
        "filterConfig": {
            "filters": [{"filterType": "TopN", "operator": "Top", "itemCount": 5}]
        },
    }


def _dumps(obj: object) -> str:
    """Deterministic, human-reviewable JSON (sorted keys, 2-space indent, trailing newline)."""
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_tree(root: pathlib.Path = TREE) -> pathlib.Path:
    """Write the committed PBIP fixture tree under ``root`` with stdlib write_text only."""
    sm_def = root / "sample.SemanticModel" / "definition"
    tables = sm_def / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    # --- PBIP entry pointers (committed so the tree is a real PBIP; not walked for units) ---
    (root / "sample.pbip").write_text(
        _dumps(
            {
                "version": "1.0",
                "artifacts": [{"report": {"path": "sample.Report"}}],
                "settings": {},
            }
        ),
        encoding="utf-8",
    )
    (root / "definition.pbism").write_text(
        _dumps({"version": "4.0", "settings": {}}), encoding="utf-8"
    )

    # --- Semantic model (TMDL) ---
    (sm_def / "model.tmdl").write_text(_MODEL_TMDL, encoding="utf-8")
    (sm_def / "relationships.tmdl").write_text(_RELATIONSHIPS_TMDL, encoding="utf-8")
    (tables / "Sales.tmdl").write_text(_SALES_TMDL, encoding="utf-8")
    (tables / "Product.tmdl").write_text(_PRODUCT_TMDL, encoding="utf-8")

    # --- Report (PBIR enhanced definition tree) ---
    rpt_def = root / "sample.Report" / "definition"
    overview = rpt_def / "pages" / "Overview"
    plain = overview / "visuals" / "plainTable"
    topn = overview / "visuals" / "topProducts"
    plain.mkdir(parents=True, exist_ok=True)
    topn.mkdir(parents=True, exist_ok=True)

    (root / "sample.Report" / "definition.pbir").write_text(
        _dumps(
            {
                "version": "4.0",
                "datasetReference": {"byPath": {"path": "../sample.SemanticModel"}},
            }
        ),
        encoding="utf-8",
    )
    (rpt_def / "report.json").write_text(
        _dumps({"name": "Report", "themeCollection": {}}), encoding="utf-8"
    )
    (rpt_def / "pages" / "pages.json").write_text(
        _dumps({"pageOrder": ["Overview"], "activePageName": "Overview"}), encoding="utf-8"
    )
    (overview / "page.json").write_text(
        _dumps({"name": "Overview", "displayName": "Overview"}), encoding="utf-8"
    )
    (plain / "visual.json").write_text(_dumps(_plain_visual()), encoding="utf-8")
    (topn / "visual.json").write_text(_dumps(_topn_visual()), encoding="utf-8")
    return root


# A few-byte NON-PBIP binary: ZIP local-file magic (a .pbix is a ZIP) + filler. NEVER decompressed —
# only the _R_PBIX_BINARY deferral is exercised (pbixray DEFERRED, L1 / zero new dependency).
_FAKE_PBIX_BYTES = b"PK\x03\x04" + b"\x00" * 24 + b"not-a-real-pbix"


def write_pbix(path: pathlib.Path = HERE / "fake.pbix") -> pathlib.Path:
    """Write the few-byte .pbix deferral byte fixture via stdlib write_bytes."""
    path.write_bytes(_FAKE_PBIX_BYTES)
    return path


def main() -> None:
    write_tree()
    n = sum(1 for p in TREE.rglob("*") if p.is_file())
    print(f"wrote {TREE.relative_to(HERE.parent.parent)} ({n} files)")
    pbix = write_pbix()
    print(f"wrote {pbix.relative_to(HERE.parent.parent)} ({len(_FAKE_PBIX_BYTES)} bytes)")


if __name__ == "__main__":
    main()
