r"""Stdlib PBIR / Power BI report-definition reader (plan 07-02, ADAPT-05).

PURE, deterministic functions that turn an already-parsed PBIR object (``report.json`` /
``page.json`` / ``visual.json``, or a model storage-mode signal) into:

  * ``extract_report(obj, object_path) -> list[(object_path, verbatim_value)]`` — ordered text units:
    page display names, visual titles, text-box runs, field references, and filter LITERAL values.
    The information-disclosure caveat (07-RESEARCH Q-C): a persisted filter literal (e.g. ``'Contoso'``)
    is part of the report DEFINITION, so it is surfaced verbatim as config text to the reviewer — never
    silently dropped, and never treated as query-result data.

  * ``detect_row_caps(obj, object_path) -> list[Detection]`` — the L3 row-cap/aggregation taxonomy:
    ``topn`` / ``filter`` / ``aggregated`` / ``measure_value`` / ``directquery`` / ``rowlimit``.
    This module returns STRUCTURE only; Wave-2's ``PowerBiAdapter`` (07-03) maps each ``Detection`` to
    its precise ``_R_*`` ``unextracted[]`` reason string and forces ``Coverage.complete=False``.

stdlib only (``json`` is the caller's; here just ``dataclasses``/``typing``). No DAX/data is ever
evaluated — text is extracted verbatim, faithful to the source. Key-lenient: an unrecognized filter
shape degrades to a generic ``filter`` detection rather than a silent miss (research A1 mitigation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator

# Power BI QueryAggregateFunction enum (Microsoft) — Function int -> name.
_AGG_FN: dict[int, str] = {
    0: "Sum",
    1: "Avg",
    2: "Min",
    3: "Max",
    4: "Count",
    5: "CountNonNull",
    6: "Median",
    7: "StandardDeviation",
    8: "Variance",
}


@dataclass
class Detection:
    """A typed row-cap / aggregation finding: a ``kind``, the object ``path``, and string ``params``."""

    kind: str
    path: str
    params: dict[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Small faithful helpers
# --------------------------------------------------------------------------- #


def _unquote_literal(value: Any) -> str:
    """A PBIR literal value is text like ``'Contoso'`` or ``2024``; strip ONE layer of wrapping
    single quotes if present, otherwise return the text unchanged. Never reformats the inner text."""
    s = str(value)
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1]
    return s


def _ref(binding: dict[str, Any]) -> str:
    """``{Expression:{SourceRef:{Entity}}, Property}`` -> ``Entity.Property`` (or just Property)."""
    if not isinstance(binding, dict):
        return ""
    entity = (
        binding.get("Expression", {}).get("SourceRef", {}).get("Entity", "")
        if isinstance(binding.get("Expression"), dict)
        else ""
    )
    prop = binding.get("Property", "")
    return f"{entity}.{prop}" if entity else str(prop)


def _ref_of_field(fld: dict[str, Any]) -> str | None:
    """A query projection ``field`` -> its ``Entity.Property`` ref (Column / Measure / Aggregation)."""
    if not isinstance(fld, dict):
        return None
    if "Column" in fld:
        return _ref(fld["Column"])
    if "Measure" in fld:
        return _ref(fld["Measure"])
    if "Aggregation" in fld:
        inner = fld["Aggregation"].get("Expression", {}) if isinstance(fld["Aggregation"], dict) else {}
        return _ref(inner.get("Column", {})) if isinstance(inner, dict) else None
    return None


def _iter_projection_fields(visual: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Walk ``visual.query.queryState.<role>.projections[].field`` in deterministic source order."""
    query = visual.get("query", {})
    state = query.get("queryState", {}) if isinstance(query, dict) else {}
    if not isinstance(state, dict):
        return
    for role in state.values():
        projections = role.get("projections", []) if isinstance(role, dict) else []
        for proj in projections:
            fld = proj.get("field") if isinstance(proj, dict) else None
            if isinstance(fld, dict):
                yield fld


def _visual_title(visual: dict[str, Any]) -> str | None:
    """``visual.title.properties.text.expr.Literal.Value`` (a literal) -> unquoted title text."""
    try:
        lit = visual["title"]["properties"]["text"]["expr"]["Literal"]["Value"]
    except (KeyError, TypeError):
        return None
    return _unquote_literal(lit)


def _textbox_runs(visual: dict[str, Any]) -> list[str]:
    """``visual.objects.general[].properties.paragraphs[].textRuns[].value`` -> verbatim run texts."""
    runs: list[str] = []
    objects = visual.get("objects", {})
    if not isinstance(objects, dict):
        return runs
    for group in objects.values():
        if not isinstance(group, list):
            continue
        for item in group:
            props = item.get("properties", {}) if isinstance(item, dict) else {}
            for para in props.get("paragraphs", []) if isinstance(props, dict) else []:
                for run in para.get("textRuns", []) if isinstance(para, dict) else []:
                    if isinstance(run, dict) and "value" in run:
                        runs.append(str(run["value"]))
    return runs


def _max_rows(visual: dict[str, Any]) -> list[int]:
    """Any ``visual.objects.*[].properties.maxRows`` -> the configured row limits."""
    limits: list[int] = []
    objects = visual.get("objects", {})
    if not isinstance(objects, dict):
        return limits
    for group in objects.values():
        if not isinstance(group, list):
            continue
        for item in group:
            props = item.get("properties", {}) if isinstance(item, dict) else {}
            if isinstance(props, dict) and "maxRows" in props:
                try:
                    limits.append(int(props["maxRows"]))
                except (TypeError, ValueError):
                    continue
    return limits


def _filters(obj: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = obj.get("filterConfig", {})
    filters = cfg.get("filters", []) if isinstance(cfg, dict) else []
    return [f for f in filters if isinstance(f, dict)]


def _filter_literals(flt: dict[str, Any]) -> list[str]:
    """Collect literal values from a filter's ``filter.Where[].Condition.In.Values`` (faithful, unquoted)."""
    out: list[str] = []
    where = flt.get("filter", {}).get("Where", []) if isinstance(flt.get("filter"), dict) else []
    for clause in where if isinstance(where, list) else []:
        cond = clause.get("Condition", {}) if isinstance(clause, dict) else {}
        values = cond.get("In", {}).get("Values", []) if isinstance(cond.get("In"), dict) else []
        for group in values if isinstance(values, list) else []:
            for entry in group if isinstance(group, list) else []:
                lit = entry.get("Literal", {}).get("Value") if isinstance(entry, dict) else None
                if lit is not None:
                    out.append(_unquote_literal(lit))
    return out


def _level_of(path: str) -> str:
    if "Visual[" in path:
        return "visual"
    if "Page[" in path:
        return "page"
    return "report"


# --------------------------------------------------------------------------- #
# Public: text extraction
# --------------------------------------------------------------------------- #


def extract_report(obj: dict[str, Any], object_path: str) -> list[tuple[str, str]]:
    """Turn one PBIR object into ordered ``(object_path, verbatim_value)`` text units."""
    units: list[tuple[str, str]] = []
    if not isinstance(obj, dict):
        return units

    # Page display name (a page is the object that has displayName but is not itself a visual).
    if "displayName" in obj and "visual" not in obj:
        dn = str(obj["displayName"])
        units.append((f"{object_path}/Page[{dn}]", dn))

    visual = obj.get("visual")
    if isinstance(visual, dict):
        title = _visual_title(visual)
        if title:
            units.append((f"{object_path}.title", title))
        for run in _textbox_runs(visual):
            units.append((f"{object_path}.textbox", run))
        for fld in _iter_projection_fields(visual):
            ref = _ref_of_field(fld)
            if ref:
                units.append((f"{object_path}.field", ref))

    # Filter literals — surfaced as config text wherever the filters live (page or visual).
    for flt in _filters(obj):
        for lit in _filter_literals(flt):
            units.append((f"{object_path}.filter", lit))

    return units


# --------------------------------------------------------------------------- #
# Public: row-cap / aggregation detection (L3 taxonomy)
# --------------------------------------------------------------------------- #


def detect_row_caps(obj: dict[str, Any], object_path: str) -> list[Detection]:
    """Detect the L3 row-cap/aggregation signals as typed ``Detection`` records (structure only)."""
    dets: list[Detection] = []
    if not isinstance(obj, dict):
        return dets

    # Model storage-mode signal (handed in by Wave-2 from the TMDL/model).
    if obj.get("mode") == "directQuery":
        dets.append(Detection("directquery", object_path, {"mode": "directQuery"}))

    # Filters: TopN -> topn; everything else (incl. unrecognized shapes) -> generic restricting filter.
    level = _level_of(object_path)
    for flt in _filters(obj):
        if flt.get("filterType") == "TopN" or flt.get("type") == "TopN":
            dets.append(
                Detection(
                    "topn",
                    object_path,
                    {"operator": str(flt.get("operator", "")), "itemCount": str(flt.get("itemCount", ""))},
                )
            )
        else:
            target = _ref(flt.get("field", {}).get("Column", {})) if isinstance(flt.get("field"), dict) else ""
            literals = ",".join(_filter_literals(flt))
            dets.append(Detection("filter", object_path, {"level": level, "target": target, "literals": literals}))

    # Query projections: measures and aggregations are clipped/summarized bindings.
    visual = obj.get("visual")
    if isinstance(visual, dict):
        for fld in _iter_projection_fields(visual):
            if "Measure" in fld:
                dets.append(Detection("measure_value", object_path, {"name": _ref(fld["Measure"])}))
            elif "Aggregation" in fld:
                agg = fld["Aggregation"] if isinstance(fld["Aggregation"], dict) else {}
                fn_code = agg.get("Function")
                fn = _AGG_FN.get(fn_code, str(fn_code)) if isinstance(fn_code, int) else str(fn_code)
                inner = agg.get("Expression", {}).get("Column", {}) if isinstance(agg.get("Expression"), dict) else {}
                dets.append(Detection("aggregated", object_path, {"ref": _ref(inner), "fn": fn}))
        for limit in _max_rows(visual):
            dets.append(Detection("rowlimit", object_path, {"limit": str(limit)}))

    return dets
