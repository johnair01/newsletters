"""RED-first unit suite for the stdlib TMDL line/indent parser (plan 07-01, ADAPT-05).

These tests pin every grammar fork of ``newsletters.adapters._tmdl.parse_tmdl`` BEFORE the
parser exists (TDD RED). The contract under test:

    parse_tmdl(text: str) -> tuple[list[tuple[str, str]], list[str]]
        -> (units, signals)
    units   : ordered (object_path_prefix, verbatim_value) pairs, in declaration order.
    signals : non-extractable findings (e.g. "directQuery") routed to Wave-2's unextracted[].

The load-bearing faithfulness rule (CONTEXT decision 3 / Pitfall 1): a measure's DAX
``expression`` is a FORMULA — it is extracted as TEXT, VERBATIM, and is NEVER evaluated to a
number. Every emitted value must be a verbatim substring of the source TMDL text so that Wave-2's
transcript line ``prefix\tvalue`` stays locatable by the shared ``normalize()``.

Cases are driven from 07-RESEARCH.md Q-B / Pattern 2 (the verbatim Microsoft-Learn TMDL example).
"""

from __future__ import annotations

import pytest

# The parser does not exist yet — this import is the RED trigger.
from newsletters.adapters._tmdl import parse_tmdl


def _values_for(units, prefix_suffix):
    """All verbatim values whose prefix ends with ``prefix_suffix``."""
    return [v for (p, v) in units if p.endswith(prefix_suffix)]


def _value_under(units, prefix):
    """The single verbatim value emitted under an exact prefix."""
    matches = [v for (p, v) in units if p == prefix]
    assert len(matches) == 1, f"expected exactly one unit at {prefix!r}, got {matches!r}"
    return matches[0]


# --------------------------------------------------------------------------------------------
# Object headers + names (single-quote un-escaping)
# --------------------------------------------------------------------------------------------


def test_table_header_emits_verbatim_name():
    units, signals = parse_tmdl("table Sales\n")
    assert _value_under(units, "Model/Table[Sales].name") == "Sales"
    assert signals == []


def test_quoted_column_name_unescapes_doubled_single_quote():
    # 'Joe''s Net Price'  ->  Joe's Net Price  (L2 quoting: '' -> ')
    text = "table Sales\n\tcolumn 'Joe''s Net Price'\n"
    units, _ = parse_tmdl(text)
    name = _value_under(units, "Model/Table[Sales]/Column[Joe's Net Price].name")
    assert name == "Joe's Net Price"


def test_quoted_measure_name_with_space_unescapes():
    text = "table Sales\n\tmeasure 'Sales Amount' = SUM('Sales'[Net Price])\n"
    units, _ = parse_tmdl(text)
    assert _value_under(units, "Model/Table[Sales]/Measure[Sales Amount].name") == "Sales Amount"


# --------------------------------------------------------------------------------------------
# Properties (colon-delimited, double-quote un-escaping, optional surrounding quotes)
# --------------------------------------------------------------------------------------------


def test_column_properties_emit_verbatim_values():
    text = (
        "table Sales\n"
        "\tcolumn 'Net Price'\n"
        "\t\tdataType: int64\n"
        "\t\tsummarizeBy: none\n"
        "\t\tformatString: $ #,##0\n"
    )
    units, _ = parse_tmdl(text)
    base = "Model/Table[Sales]/Column[Net Price]"
    assert _value_under(units, f"{base}.dataType") == "int64"
    assert _value_under(units, f"{base}.summarizeBy") == "none"
    assert _value_under(units, f"{base}.formatString") == "$ #,##0"


def test_double_quoted_property_value_strips_quotes_and_unescapes():
    # sourceColumn: "Joe""s Col"  ->  Joe"s Col
    text = (
        "table Sales\n"
        "\tcolumn 'Net Price'\n"
        '\t\tsourceColumn: "Joe""s Col"\n'
    )
    units, _ = parse_tmdl(text)
    val = _value_under(units, "Model/Table[Sales]/Column[Net Price].sourceColumn")
    assert val == 'Joe"s Col'


# --------------------------------------------------------------------------------------------
# /// descriptions accumulate onto the NEXT object
# --------------------------------------------------------------------------------------------


def test_single_line_description_attaches_to_next_object():
    text = (
        "table Sales\n"
        "\t/// This is the Measure Description\n"
        "\tmeasure 'Sales Amount' = SUM('Sales'[Net Price])\n"
    )
    units, _ = parse_tmdl(text)
    desc = _value_under(units, "Model/Table[Sales]/Measure[Sales Amount].description")
    assert desc == "This is the Measure Description"


def test_multi_line_description_joins_verbatim_lines():
    text = (
        "table Sales\n"
        "\t/// line one\n"
        "\t/// line two\n"
        "\tcolumn Quantity\n"
    )
    units, _ = parse_tmdl(text)
    descs = _values_for(units, "Column[Quantity].description")
    # Each description line is emitted verbatim (so each is a transcript substring).
    assert "line one" in descs
    assert "line two" in descs


# --------------------------------------------------------------------------------------------
# Default-property DAX after `=` — the faithfulness crux (NEVER a value)
# --------------------------------------------------------------------------------------------


def test_single_line_dax_expression_is_verbatim_text_never_a_value():
    dax = "SUMX('Sales', 'Sales'[Quantity] * 'Sales'[Net Price])"
    text = f"table Sales\n\tmeasure 'Sales Amount' = {dax}\n\t\tformatString: $ #,##0\n"
    units, _ = parse_tmdl(text)
    expr = _value_under(units, "Model/Table[Sales]/Measure[Sales Amount].expression")
    # Verbatim formula text — operators + identifiers present, NOT a number.
    assert expr == dax
    assert "SUMX" in expr
    assert "*" in expr
    with pytest.raises(ValueError):
        float(expr)  # a DAX formula is NOT a numeric value (Pitfall 1)
    # formatString still parsed as a sibling property after the single-line expression.
    assert _value_under(units, "Model/Table[Sales]/Measure[Sales Amount].formatString") == "$ #,##0"


def test_multi_line_indented_dax_expression_extracts_verbatim():
    text = (
        "table Sales\n"
        "\tmeasure 'Sales (ly)' =\n"
        "\t\t\tvar ly = CALCULATE([Sales Amount])\n"
        "\t\t\treturn ly\n"
        "\t\tformatString: $ #,##0\n"
    )
    units, _ = parse_tmdl(text)
    expr = _value_under(units, "Model/Table[Sales]/Measure[Sales (ly)].expression")
    assert "var ly = CALCULATE([Sales Amount])" in expr
    assert "return ly" in expr
    # The deeper-indented block is the expression; formatString at property depth is NOT in it.
    assert "formatString" not in expr
    assert _value_under(units, "Model/Table[Sales]/Measure[Sales (ly)].formatString") == "$ #,##0"


def test_fenced_verbatim_dax_block_extracts_until_closing_fence():
    text = (
        "table Sales\n"
        "\tmeasure 'Fenced' = ```\n"
        "\t\tSUMX('Sales', 'Sales'[Qty])\n"
        "\t\t// a comment inside the fence: value 42\n"
        "\t\t```\n"
    )
    units, _ = parse_tmdl(text)
    expr = _value_under(units, "Model/Table[Sales]/Measure[Fenced].expression")
    assert "SUMX('Sales', 'Sales'[Qty])" in expr
    # Content inside the fence is verbatim, including a comment — but never evaluated to 42.
    assert "// a comment inside the fence" in expr
    assert expr.strip() != "42"


# --------------------------------------------------------------------------------------------
# relationship / hierarchy / annotation
# --------------------------------------------------------------------------------------------


def test_relationship_emits_both_endpoints():
    text = (
        "relationship cdb6e6a9-c9d1-42b9-b9e0-484a1bc7e123\n"
        "\tfromColumn: Sales.'Product Key'\n"
        "\ttoColumn: Product.'Product Key'\n"
    )
    units, _ = parse_tmdl(text)
    rid = "cdb6e6a9-c9d1-42b9-b9e0-484a1bc7e123"
    assert _value_under(units, f"Model/Relationship[{rid}].fromColumn") == "Sales.'Product Key'"
    assert _value_under(units, f"Model/Relationship[{rid}].toColumn") == "Product.'Product Key'"


def test_hierarchy_emits_level_column_refs():
    text = (
        "table Date\n"
        "\thierarchy Calendar\n"
        "\t\tlevel Year\n"
        "\t\t\tcolumn: Year\n"
        "\t\tlevel Month\n"
        "\t\t\tcolumn: Month\n"
    )
    units, _ = parse_tmdl(text)
    cols = _values_for(units, ".column")
    assert "Year" in cols
    assert "Month" in cols


def test_annotation_emits_value():
    text = "table Sales\n\tannotation PBI_ResultType = Table\n"
    units, _ = parse_tmdl(text)
    val = _value_under(units, "Model/Table[Sales]/Annotation[PBI_ResultType].value")
    assert val == "Table"


# --------------------------------------------------------------------------------------------
# DirectQuery partition -> non-extractable SIGNAL (not a value unit)
# --------------------------------------------------------------------------------------------


def test_directquery_partition_surfaces_signal_not_a_unit():
    text = (
        "table Sales\n"
        "\tpartition Sales-DQ = m\n"
        "\t\tmode: directQuery\n"
        "\t\tsource = let Source = Sql.Database(...) in Source\n"
    )
    units, signals = parse_tmdl(text)
    assert "directQuery" in signals
    # The mode is a signal, NOT emitted as a value unit.
    assert _values_for(units, ".mode") == []


# --------------------------------------------------------------------------------------------
# Determinism + tabs-vs-spaces leniency
# --------------------------------------------------------------------------------------------


def test_parsing_is_deterministic():
    text = (
        "table Sales\n"
        "\t/// desc\n"
        "\tmeasure 'Sales Amount' = SUM('Sales'[Net Price])\n"
        "\tcolumn Quantity\n"
        "\t\tdataType: int64\n"
    )
    first, sig1 = parse_tmdl(text)
    second, sig2 = parse_tmdl(text)
    assert first == second
    assert sig1 == sig2


def test_space_indented_input_groups_children_like_tabs():
    tab_text = (
        "table Sales\n"
        "\tcolumn 'Net Price'\n"
        "\t\tdataType: int64\n"
    )
    space_text = (
        "table Sales\n"
        "    column 'Net Price'\n"
        "        dataType: int64\n"
    )
    tab_units, _ = parse_tmdl(tab_text)
    space_units, _ = parse_tmdl(space_text)
    # Relative depth — same child grouping regardless of whitespace kind (Pitfall 5).
    assert tab_units == space_units
