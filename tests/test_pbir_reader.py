r"""RED-first unit suite for the stdlib PBIR/report reader (plan 07-02, ADAPT-05).

Drives the contract of ``newsletters.adapters._pbir`` — the PURE functions that turn an already-
parsed PBIR ``report.json`` / ``page.json`` / ``visual.json`` object into

  (a) ordered ``(object_path, verbatim_value)`` text units — page display names, visual titles,
      text-box runs, field references, AND filter LITERAL values (the information-disclosure caveat:
      a persisted ``'Contoso'`` filter value is part of the report DEFINITION and is surfaced to the
      reviewer as config text, never silently treated as query-result data); and

  (b) a list of TYPED row-cap/aggregation ``Detection`` records — the L3 taxonomy
      (07-RESEARCH.md Q-D): TopN filters, restricting filters, aggregated/measure field bindings,
      DirectQuery, and visual row/data limits. Wave-2's ``PowerBiAdapter`` (07-03) maps each
      ``Detection`` to its precise ``_R_*`` ``unextracted[]`` reason string; this module returns
      STRUCTURE, never the final reason prose.

The fixtures here are inline JSON literals authored against the documented PowerBI filter model
(``filterType: TopN`` + ``operator`` + ``itemCount``) and the ``microsoft/json-schemas``
visualContainer shape (resolves research Assumption A1 at the fixture level). KEY-LENIENCY: a filter
object whose exact sub-keys are unrecognized still degrades to a generic ``filter`` detection rather
than a miss — asserted below.
"""

from __future__ import annotations

import json

from newsletters.adapters._pbir import Detection, detect_row_caps, extract_report

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _kinds(dets: list[Detection]) -> list[str]:
    return [d.kind for d in dets]


# --------------------------------------------------------------------------- #
# TEXT extraction — page names, visual titles, text boxes, field refs
# --------------------------------------------------------------------------- #


def test_page_display_name_is_a_verbatim_unit() -> None:
    page = {"name": "ReportSection1", "displayName": "Sales Overview"}
    units = extract_report(page, "Report")
    values = [v for _, v in units]
    assert "Sales Overview" in values
    # the displayName value appears VERBATIM in the source JSON text (Wave-2 locatability)
    assert "Sales Overview" in json.dumps(page)
    # the page name is carried in the object path, not minted into the value
    assert any("Sales Overview" == v and "Page[Sales Overview]" in p for p, v in units)


def test_visual_title_text_is_a_verbatim_unit() -> None:
    visual = {
        "name": "abc123",
        "visual": {
            "visualType": "tableEx",
            "title": {"properties": {"text": {"expr": {"Literal": {"Value": "'Top Products'"}}}}},
        },
    }
    units = extract_report(visual, "Report/Page[Overview]/Visual[abc123]")
    values = [v for _, v in units]
    assert "Top Products" in values
    assert any(p.endswith(".title") for p, v in units if v == "Top Products")


def test_text_box_runs_are_verbatim_units() -> None:
    visual = {
        "name": "tb1",
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {"textRuns": [{"value": "Quarterly summary"}]},
                                {"textRuns": [{"value": "see notes"}]},
                            ]
                        }
                    }
                ]
            },
        },
    }
    units = extract_report(visual, "Report/Page[P]/Visual[tb1]")
    values = [v for _, v in units]
    assert "Quarterly summary" in values
    assert "see notes" in values
    assert all(p.endswith(".textbox") for p, v in units if v in {"Quarterly summary", "see notes"})


def test_field_reference_binding_is_a_verbatim_unit() -> None:
    # A query projection binding a column and a measure to the visual.
    visual = {
        "name": "v9",
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Region"}}}
                        ]
                    },
                    "Y": {
                        "projections": [
                            {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Total Sales"}}}
                        ]
                    },
                }
            },
        },
    }
    units = extract_report(visual, "Report/Page[P]/Visual[v9]")
    values = [v for _, v in units]
    assert "Sales.Region" in values
    assert "Sales.Total Sales" in values
    assert all(p.endswith(".field") for p, v in units if v in {"Sales.Region", "Sales.Total Sales"})


def test_plain_visual_yields_units_and_zero_detections() -> None:
    visual = {
        "name": "plain",
        "visual": {
            "visualType": "tableEx",
            "title": {"properties": {"text": {"expr": {"Literal": {"Value": "'Detail'"}}}}},
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "OrderId"}}}
                        ]
                    }
                }
            },
        },
    }
    units = extract_report(visual, "Report/Page[P]/Visual[plain]")
    values = [v for _, v in units]
    assert "Detail" in values
    assert "Sales.OrderId" in values
    assert detect_row_caps(visual, "Report/Page[P]/Visual[plain]") == []


# --------------------------------------------------------------------------- #
# DETECTION — the L3 row-cap / aggregation taxonomy
# --------------------------------------------------------------------------- #


def test_topn_filter_detection_carries_operator_and_count() -> None:
    visual = {
        "name": "top5",
        "filterConfig": {
            "filters": [
                {
                    "name": "f1",
                    "field": {"Column": {"Property": "Product"}},
                    "filter": {},
                    "type": "TopN",
                    "filterType": "TopN",
                    "operator": "Top",
                    "itemCount": 5,
                }
            ]
        },
    }
    dets = detect_row_caps(visual, "Report/Page[P]/Visual[top5]")
    topn = [d for d in dets if d.kind == "topn"]
    assert len(topn) == 1
    assert topn[0].params["operator"] == "Top"
    assert topn[0].params["itemCount"] == "5"
    assert "Visual[top5]" in topn[0].path


def test_restricting_filter_detection_carries_level_and_target() -> None:
    page = {
        "name": "ReportSection2",
        "displayName": "Filtered",
        "filterConfig": {
            "filters": [
                {
                    "name": "f2",
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Year"}},
                    "type": "Categorical",
                    "filter": {"Where": [{"Condition": {"In": {"Values": [[{"Literal": {"Value": "2024"}}]]}}}]},
                }
            ]
        },
    }
    dets = detect_row_caps(page, "Report/Page[Filtered]")
    filt = [d for d in dets if d.kind == "filter"]
    assert len(filt) == 1
    assert filt[0].params["level"] == "page"
    assert "Sales.Year" in filt[0].params["target"]


def test_unknown_filter_keys_degrade_to_generic_filter_detection() -> None:
    # KEY-LENIENCY (research A1 mitigation): an unrecognized filter shape must still be reported
    # as a restricting filter "present", never silently missed.
    visual = {
        "name": "weird",
        "filterConfig": {
            "filters": [
                {"name": "f3", "someFutureKey": {"nested": "value"}, "restrict": True}
            ]
        },
    }
    dets = detect_row_caps(visual, "Report/Page[P]/Visual[weird]")
    assert "filter" in _kinds(dets)


def test_aggregated_field_binding_detection_carries_ref_and_fn() -> None:
    visual = {
        "name": "agg",
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Aggregation": {
                                        "Function": 0,
                                        "Expression": {
                                            "Column": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Amount"}
                                        },
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        },
    }
    dets = detect_row_caps(visual, "Report/Page[P]/Visual[agg]")
    agg = [d for d in dets if d.kind == "aggregated"]
    assert len(agg) == 1
    assert "Sales.Amount" in agg[0].params["ref"]
    assert agg[0].params["fn"] == "Sum"  # Function 0 == Sum


def test_measure_projection_detection_carries_name() -> None:
    visual = {
        "name": "m1",
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "Sales"}}, "Property": "Total Sales"}}}
                        ]
                    }
                }
            },
        },
    }
    dets = detect_row_caps(visual, "Report/Page[P]/Visual[m1]")
    mv = [d for d in dets if d.kind == "measure_value"]
    assert len(mv) == 1
    assert mv[0].params["name"] == "Sales.Total Sales"


def test_directquery_signal_yields_a_detection() -> None:
    # The model storage mode is handed in as a signal object (Wave-2 reads it from TMDL/model).
    model_signal = {"mode": "directQuery"}
    dets = detect_row_caps(model_signal, "Model")
    assert "directquery" in _kinds(dets)


def test_row_limit_detection_carries_count() -> None:
    visual = {
        "name": "lim",
        "visual": {
            "visualType": "tableEx",
            "objects": {"general": [{"properties": {"maxRows": 30}}]},
        },
    }
    dets = detect_row_caps(visual, "Report/Page[P]/Visual[lim]")
    rl = [d for d in dets if d.kind == "rowlimit"]
    assert len(rl) == 1
    assert rl[0].params["limit"] == "30"


# --------------------------------------------------------------------------- #
# INFORMATION-DISCLOSURE CAVEAT (Q-C): filter literals are extracted, not hidden
# --------------------------------------------------------------------------- #


def test_filter_literal_value_is_extracted_as_config_text_and_recorded_in_detection() -> None:
    visual = {
        "name": "leak",
        "filterConfig": {
            "filters": [
                {
                    "name": "f4",
                    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Company"}}, "Property": "Name"}},
                    "type": "Categorical",
                    "filter": {
                        "Where": [
                            {"Condition": {"In": {"Values": [[{"Literal": {"Value": "'Contoso'"}}]]}}}
                        ]
                    },
                }
            ]
        },
    }
    path = "Report/Page[P]/Visual[leak]"
    units = extract_report(visual, path)
    values = [v for _, v in units]
    # the literal 'Contoso' IS surfaced as a verbatim config-text unit (never silently dropped)
    assert "Contoso" in values
    assert all(p.endswith(".filter") for p, v in units if v == "Contoso")
    # ...AND the literal is recorded in the filter detection so the reviewer sees it
    dets = detect_row_caps(visual, path)
    filt = [d for d in dets if d.kind == "filter"]
    assert len(filt) == 1
    assert "Contoso" in filt[0].params.get("literals", "")


# --------------------------------------------------------------------------- #
# DETERMINISM
# --------------------------------------------------------------------------- #


def test_parsing_same_object_twice_is_deterministic() -> None:
    obj = {
        "name": "det",
        "visual": {
            "visualType": "barChart",
            "title": {"properties": {"text": {"expr": {"Literal": {"Value": "'T'"}}}}},
            "query": {
                "queryState": {
                    "Y": {
                        "projections": [
                            {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "S"}}, "Property": "M"}}}
                        ]
                    }
                }
            },
        },
        "filterConfig": {
            "filters": [
                {"name": "f", "field": {"Column": {"Property": "P"}}, "filterType": "TopN", "operator": "Top", "itemCount": 3}
            ]
        },
    }
    p = "Report/Page[P]/Visual[det]"
    assert extract_report(obj, p) == extract_report(obj, p)
    assert detect_row_caps(obj, p) == detect_row_caps(obj, p)


def test_detection_is_a_typed_record_with_kind_path_params() -> None:
    d = Detection(kind="topn", path="Report/Page[P]/Visual[x]", params={"operator": "Top", "itemCount": "5"})
    assert d.kind == "topn"
    assert d.path.endswith("Visual[x]")
    assert d.params["operator"] == "Top"
