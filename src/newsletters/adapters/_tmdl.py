r"""The stdlib TMDL line/indent parser (plan 07-01, ADAPT-05) — a PURE tokenizer.

WHAT. One ``*.tmdl`` file's text -> an ordered list of ``(object_path_prefix, verbatim_value)``
units plus a list of non-extractable signals. TMDL (Tabular Model Definition Language) is the
YAML-like, single-tab-indented text serialization of a Power BI semantic model: object headers
(``table Sales``), ``property: value`` lines, ``=``-introduced default-property expressions
(single-line / indent-deeper multi-line / ```` ``` ````-fenced verbatim), and ``///`` descriptions.
This parser walks the file BY PHYSICAL LINE, tracks relative indent depth, and emits every
faithful artifact — table/column/measure NAME, properties, descriptions, the DAX/M ``expression``
text, relationship endpoints, hierarchy refs, annotation values — VERBATIM. The ``object_path``
prefix (e.g. ``Model/Table[Sales]/Measure[Sales Amount].expression``) is carried OUT of the parser
as the unit's first element; it is NOT part of the value (Wave-2's adapter uses it as the transcript
record prefix so ``normalize()`` can locate the verbatim value).

WHY a stdlib parser (NO third-party TMDL dep). TMDL's grammar is line-regular and indent-structured
(07-RESEARCH.md Q-B verdict: stdlib is sufficient — no mature/permissive/lightweight Python TMDL
parser exists; the official ``TmdlSerializer`` is .NET-only). The whole module imports only ``re``
from the standard library, which keeps the bare install, AI-isolation, and ``lint-imports`` green
with zero new dependency.

HARD RULE — "Faithful, not suggestive" (CONTEXT decision 3 / Pitfall 1). A ``measure``'s default
property is a DAX FORMULA. This parser extracts the expression TEXT verbatim and NEVER evaluates it,
never derives a numeric value. There is no DAX/M evaluation path in this module by construction; the
Wave-2 adapter discloses the absent computed value via ``_R_MEASURE_VALUE``.

PURITY / DETERMINISM (T-07-03). ``parse_tmdl`` is a pure function: no clock, no random, no I/O, no
mutation of its argument. Units are emitted in declaration order, so parsing the same text twice
yields identical output. Indent depth is a COUNTER over an explicit stack — never call recursion on
untrusted depth — so a pathological file cannot blow the stack (T-07-02); unknown lines are skipped,
never crash (the whole-file try/except lives in the Wave-2 adapter, V5).

OUTPUT CONTRACT (consumed by plan 07-03's ``PowerBiAdapter``)::

    parse_tmdl(text: str) -> tuple[list[tuple[str, str]], list[str]]
        units   : ordered (prefix, verbatim_value); prefix is the object path described above.
        signals : non-extractable findings; currently {"directQuery"} for a DQ partition mode.
"""

from __future__ import annotations

import re

__all__ = ["parse_tmdl"]

# Object types whose header line is ``type name`` (optionally ``= expr``). Order is irrelevant;
# this is a membership set used to classify the first token of a header line.
_OBJECT_TYPES = frozenset(
    {
        "model",
        "table",
        "column",
        "measure",
        "hierarchy",
        "level",
        "partition",
        "relationship",
        "annotation",
        "role",
        "expression",
        "calculationGroup",
        "calculationItem",
    }
)

# Object types that, when seen on a table, become a child in the path (Table[..]/Child[..]).
# ``relationship`` is a top-level Model child, handled separately.
_CHILD_TYPES = frozenset(
    {"column", "measure", "hierarchy", "partition", "annotation"}
)

# Header forms:
#   ``measure 'Sales Amount' = SUMX(...)``  (quoted name + inline default-property expression)
#   ``column Quantity``                      (bare name)
#   ``annotation Foo = Bar``                 (name + ``=`` value, treated specially below)
# A name is either a single-quoted string (with doubled '' for a literal ') or a bare token.
_QUOTED_NAME = r"'(?:[^']|'')*'"
_BARE_NAME = r"[^\s=]+"
_HEADER_RE = re.compile(
    rf"^(?P<type>\w+)\s+(?P<name>{_QUOTED_NAME}|{_BARE_NAME})\s*(?:=\s*(?P<expr>.*))?$"
)

# A ``property: value`` line. The value is taken verbatim (after a single delimiting space-trim);
# values may themselves contain ``:`` so we split on the FIRST colon only.
_PROPERTY_RE = re.compile(r"^(?P<key>\w+):\s?(?P<value>.*)$")

# An ``annotation name = value`` is a header whose ``=`` carries a Text value, not a DAX expression.
_FENCE = "```"


def _indent_width(line: str) -> int:
    """Count leading whitespace characters (lenient on tabs-vs-spaces *kind*, Pitfall 5).

    We measure relative depth via an explicit indent stack in :func:`parse_tmdl`; this returns the
    raw count of leading whitespace chars so the stack can compare increases/decreases. A tab and a
    run of spaces both count by character, which is sufficient because TMDL never mixes the two
    *within a single child step* in practice — and we only ever compare counts at the same level.
    """
    return len(line) - len(line.lstrip(" \t"))


def _unquote_name(token: str) -> str:
    """Un-escape a TMDL object name: ``'Joe''s'`` -> ``Joe's``; a bare token is returned as-is."""
    if len(token) >= 2 and token[0] == "'" and token[-1] == "'":
        return token[1:-1].replace("''", "'")
    return token


def _unquote_value(value: str) -> str:
    r"""Un-escape a TMDL property value.

    A double-quoted value strips its surrounding quotes and un-escapes doubled ``""`` -> ``"``
    (``"Joe""s Col"`` -> ``Joe"s Col``). Any other value is returned verbatim (so ``int64``,
    ``$ #,##0`` and ``Sales.'Product Key'`` stay exactly as written).
    """
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].replace('""', '"')
    return value


def parse_tmdl(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Parse one TMDL file's ``text`` into ``(units, signals)``.

    ``units`` is an ordered list of ``(object_path_prefix, verbatim_value)`` pairs in declaration
    order; ``signals`` lists non-extractable findings (currently ``"directQuery"`` for a
    DirectQuery partition mode). Pure and deterministic; never evaluates DAX (see module docstring).
    """
    units: list[tuple[str, str]] = []
    signals: list[str] = []

    lines = text.split("\n")

    # The path stack of (indent_width, kind, name) frames describing the current ancestry.
    # ``kind`` is "Table" | "Relationship" | "Hierarchy" | "Measure" | "Column" | ... used to
    # build the prefix; only container-like frames (Table/Hierarchy) carry children.
    stack: list[tuple[int, str, str]] = []
    pending_descriptions: list[str] = []

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        stripped = raw.strip()

        # Blank line: a separator only; it does not reset pending descriptions (TMDL forbids blank
        # lines between a /// block and its object, so in practice none accrue across a blank).
        if stripped == "":
            i += 1
            continue

        width = _indent_width(raw)

        # /// description — accumulates for the NEXT object (verbatim, one unit per line later).
        if stripped.startswith("///"):
            pending_descriptions.append(stripped[3:].lstrip())
            i += 1
            continue

        # Pop stack frames that are not ancestors of this line (dedent).
        while stack and width <= stack[-1][0]:
            stack.pop()

        # ``property: value`` at the current depth belongs to the nearest enclosing object.
        prop = _PROPERTY_RE.match(stripped)
        header = _HEADER_RE.match(stripped)
        # A line like ``dataType: int64`` matches both regexes; prefer the property reading when the
        # first token is NOT a known object type (so ``column Quantity`` stays a header).
        first_token = stripped.split(None, 1)[0].rstrip(":")
        is_header = header is not None and first_token in _OBJECT_TYPES

        if not is_header and prop is not None:
            key = prop.group("key")
            value = _unquote_value(prop.group("value"))
            owner_prefix = _current_prefix(stack)
            # DirectQuery partition mode is a SIGNAL, not a value unit (routed to _R_DIRECTQUERY).
            if key == "mode" and value == "directQuery":
                if "directQuery" not in signals:
                    signals.append("directQuery")
            elif owner_prefix is not None:
                units.append((f"{owner_prefix}.{key}", value))
            else:
                # A property with no enclosing object is content we READ but cannot attribute — it
                # must be DISCLOSED, never silently dropped (the no-silent-drops invariant).
                signals.append(f"unparsed: {stripped}")
            i += 1
            continue

        if is_header:
            assert header is not None  # for type-checkers; guarded by is_header
            obj_type = header.group("type")
            name = _unquote_name(header.group("name"))
            inline_expr = header.group("expr")

            kind = obj_type[0].upper() + obj_type[1:]

            if obj_type == "model":
                # The ``model`` header IS the implicit ``Model`` root: its properties attach directly
                # (``Model.culture``), so push a sentinel frame (empty kind => no path segment) rather
                # than a redundant ``Model[name]`` frame. Drain descriptions + emit the name verbatim.
                for desc in pending_descriptions:
                    units.append(("Model.description", desc))
                pending_descriptions = []
                units.append(("Model.name", name))
                stack.append((width, "", name))
                i += 1
                continue

            prefix = _build_prefix(stack, obj_type, name)

            # Drain any pending /// descriptions onto this object (each line a verbatim unit).
            for desc in pending_descriptions:
                units.append((f"{prefix}.description", desc))
            pending_descriptions = []

            if obj_type == "annotation":
                # ``annotation name = value`` — the ``=`` carries a Text value, not DAX.
                if inline_expr is not None:
                    units.append((f"{prefix}.value", _unquote_value(inline_expr.strip())))
                # An annotation has no children; do not push a container frame.
                i += 1
                continue

            # Emit the object NAME as a verbatim unit (so the name itself is locatable).
            units.append((f"{prefix}.name", name))

            # Push this object as a frame so its properties/children attach correctly.
            stack.append((width, kind, name))

            if inline_expr is not None:
                expr = inline_expr.strip()
                if expr == _FENCE:
                    # ``measure X = ``` `` opens a fenced verbatim block on the header line.
                    block, i = _read_fenced_block(lines, i + 1)
                    units.append((f"{prefix}.expression", block))
                    continue
                if expr == "":
                    # ``measure X =`` with nothing after ``=`` -> a multi-line default-property
                    # expression indented deeper than the object's properties (verbatim DAX/M).
                    multi, i = _read_indented_expression(lines, i + 1, width)
                    if multi is not None:
                        units.append((f"{prefix}.expression", multi))
                    continue
                # Single-line default-property expression (verbatim DAX/M text — NEVER a value).
                units.append((f"{prefix}.expression", expr))
                i += 1
                continue

            # No inline ``=``: properties/children follow on deeper lines (handled by their own
            # branches). Just advance.
            i += 1
            continue

        if first_token == "ref":
            # ``ref table Sales`` — a model's table-membership reference (a normal, ubiquitous TMDL
            # construct). Extract the referenced object verbatim rather than disclose it as a skip.
            owner = _current_prefix(stack) or "Model"
            units.append((f"{owner}.ref", stripped[len(first_token):].strip()))
            i += 1
            continue

        # Unknown / unrecognized line: content we READ but cannot classify. DISCLOSE it (never a
        # silent drop) so a reviewer sees the extractor skipped something, then advance.
        signals.append(f"unparsed: {stripped}")
        i += 1

    return units, signals


def _current_prefix(stack: list[tuple[int, str, str]]) -> str | None:
    """The object-path prefix of the nearest enclosing object (the property/desc owner)."""
    if not stack:
        return None
    return _prefix_from_stack(stack)


def _prefix_from_stack(stack: list[tuple[int, str, str]]) -> str:
    """Build ``Model/Table[Sales]/Measure[Sales Amount]`` from the full frame stack.

    A frame with an empty ``kind`` is the sentinel ``model`` root: it contributes the implicit
    ``Model`` prefix but no ``Kind[name]`` segment, so a ``model`` file's properties attach directly
    as ``Model.culture`` rather than ``Model/Model[..].culture``.
    """
    parts = ["Model"]
    for _width, kind, name in stack:
        if kind:
            parts.append(f"{kind}[{name}]")
    return "/".join(parts)


def _build_prefix(stack: list[tuple[int, str, str]], obj_type: str, name: str) -> str:
    """The prefix for a NEW object of ``obj_type``/``name`` declared under the current ``stack``."""
    kind = obj_type[0].upper() + obj_type[1:]
    parts = ["Model"]
    for _width, frame_kind, frame_name in stack:
        if frame_kind:
            parts.append(f"{frame_kind}[{frame_name}]")
    parts.append(f"{kind}[{name}]")
    return "/".join(parts)


def _read_fenced_block(lines: list[str], start: int) -> tuple[str, int]:
    """Read a ```` ``` ````-fenced verbatim block beginning at ``start`` until the closing fence.

    Returns ``(verbatim_block_text, next_index)``. The block content is the inner lines with their
    common leading indentation stripped (TMDL fenced blocks preserve relative indentation; we strip
    the shared prefix so the emitted text is the author's verbatim expression). The fence markers
    themselves are not included.
    """
    body: list[str] = []
    i = start
    n = len(lines)
    while i < n:
        if lines[i].strip() == _FENCE:
            i += 1
            break
        body.append(lines[i])
        i += 1
    text = _dedent_block(body)
    return text, i


def _read_indented_expression(
    lines: list[str], start: int, header_width: int
) -> tuple[str | None, int]:
    """Read a multi-line default-property expression indented deeper than its properties.

    A multi-line expression body sits one level deeper than the object's properties (which sit one
    level deeper than the header). We collect contiguous lines whose indent is STRICTLY greater than
    ``header_width + 1`` worth of one step — concretely, deeper than the first property depth — and
    stop at the first line that dedents to property depth or shallower (e.g. ``formatString:``).

    Returns ``(verbatim_expression_text | None, next_index)``.
    """
    n = len(lines)
    i = start
    # Skip leading blank lines.
    while i < n and lines[i].strip() == "":
        i += 1
    if i >= n:
        return None, i

    first_width = _indent_width(lines[i])
    # The expression body must be indented deeper than the header. Property lines also sit deeper;
    # the expression body is the DEEPEST contiguous run. We take the first non-blank deeper line's
    # width as the expression depth and consume while indent >= that depth.
    if first_width <= header_width:
        return None, start  # nothing deeper — not a multi-line expression

    expr_width = first_width
    body: list[str] = []
    while i < n:
        line = lines[i]
        if line.strip() == "":
            body.append(line)
            i += 1
            continue
        w = _indent_width(line)
        if w < expr_width:
            break
        body.append(line)
        i += 1

    # Trim trailing blank lines we may have greedily collected.
    while body and body[-1].strip() == "":
        body.pop()

    text = _dedent_block(body)
    return text, i


def _dedent_block(body: list[str]) -> str:
    """Strip the common leading-whitespace prefix from ``body`` and join verbatim with ``\\n``."""
    non_blank = [ln for ln in body if ln.strip() != ""]
    if not non_blank:
        return ""
    common = min(_indent_width(ln) for ln in non_blank)
    out = []
    for ln in body:
        if ln.strip() == "":
            out.append("")
        else:
            out.append(ln[common:])
    return "\n".join(out)
