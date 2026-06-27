"""Author the byte-reproducible golden `.pptx` corpus (ADAPT-06; ROADMAP Phase-6 criterion 3).

These fixtures stand in for untrusted real-world decks. Each is tiny, programmatic, and uses
EXPLICIT shapes/text so the PowerPoint adapter's extract-vs-disclose fork is exercised, not
incidental. Mirrors `tests/fixtures/xlsx/_author_fixtures.py`: the committed `.pptx` files ARE the
corpus; this script is the documented, rerunnable provenance and lets anyone regenerate them
byte-for-byte.

THE CORPUS (9 fixtures). The two ROADMAP criterion-3 fixtures are `smartart.pptx` (a SmartArt
diagram) and `nested_group.pptx` (a nested group of shapes); the rest cover the full extract/disclose
fork — a title+body slide, a free text box, a table, speaker notes, a chart, an embedded image, and an
empty slide. The docstring of each builder pins the EXPECTED adapter routing (claims vs unextracted);
`test_pptx_golden.py` asserts those expectations against the LIVE adapter.

BYTE-REPRODUCIBILITY (threat T-06-11). Unlike openpyxl, python-pptx does NOT stamp the save-time
wall-clock into the OOXML zip — it writes a fixed zip-entry `date_time` and only embeds a timestamp
when we set `core_properties.created`/`.modified`. We pin those to a FIXED datetime, so a plain
`prs.save()` is already byte-stable across runs (probed against python-pptx 1.0.2). For the
SmartArt fixture (which rebuilds the zip after XML injection) we additionally route through
`_normalize_zip`, which rewrites every entry's `date_time` to a fixed constant and re-deflates in
entry order — belt-and-braces so the injected-XML path stays byte-stable too. The generator uses no
`now()` and no `random`, so `sha256(file)` is stable across processes.

NOTE on the DETERMINISM ASSERTION (06-04 Task 2): the load-bearing property ADAPT-06 needs is
determinism on the PARSED `Source` (identical bytes -> byte-identical `model_dump_json`, L5), NOT
byte-identical re-saved `.pptx` files. Byte-reproducible fixtures are a nice-to-have for a clean
`git diff`; the Source-determinism property is the one the golden test asserts.

THE 1x1 PNG (Pillow-free, gotcha A2). `add_picture` needs valid image bytes but does not require us
to call Pillow: we embed a constant ~68-byte 1x1 transparent PNG byte literal via `io.BytesIO`, so
the image fixture is deterministic with no Pillow dependency in the authoring path.

THE GROUP-AUTHORING ORDER (gotcha L4). `add_group_shape([...])` requires its members to ALREADY
exist on the slide — it MOVES (re-parents) them into the group. So we author members FIRST, capture
their handles, THEN group. A NESTED group is an inner group fed into an outer `add_group_shape`.

SMARTART (the silent-drop trap, L2 / gotcha 3). python-pptx exposes NO SmartArt authoring API. The
MINIMUM to be DETECTED as SmartArt (not rendered) is a `graphicFrame` whose `a:graphicData/@uri` is
the diagram namespace. We anchor on a real graphic frame (a 1x1 table), rewrite its `graphicData`
`@uri` to the diagram namespace, and strip the table payload — yielding a frame python-pptx reports
as `shape_type is None` with the diagram URI (resolved via BOTH the adapter's primary accessor and
its lxml fallback; probed against python-pptx 1.0.2). 06-03's unit suite already proved the adapter
detects exactly this injected frame.

Run:  .venv/bin/python tests/fixtures/pptx/_author_fixtures.py
"""

from __future__ import annotations

import io
import pathlib
import re
import zipfile
from datetime import datetime

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Emu

HERE = pathlib.Path(__file__).parent

# A fixed timestamp pinned into docProps/core.xml so the OOXML bytes embed no wall-clock
# (byte-reproducibility, threat T-06-11). Any fixed instant works; this one is arbitrary + stable.
_FIXED = datetime(2026, 1, 1, 0, 0, 0)
# The fixed ZIP local-header date_time (year, month, day, hour, minute, second) for every entry.
_FIXED_ZIP_DATE_TIME = (2026, 1, 1, 0, 0, 0)

# The OOXML DrawingML diagram namespace — a SmartArt graphicFrame's ``a:graphicData/@uri``.
_DIAGRAM_URI = "http://schemas.openxmlformats.org/drawingml/2006/diagram"

# A constant, valid 1x1 transparent PNG byte literal — embeds via ``add_picture`` WITHOUT a Pillow
# call (deterministic), per 06-RESEARCH Fixture gotcha 1. (Same literal as the 06-03 unit suite.)
_PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000100ffff0300000600"
    "0557bfabd40000000049454e44ae426082"
)


_FIXED_W3CDTF = "2026-01-01T00:00:00Z"


def _pin_core_xml(data: bytes) -> bytes:
    """Rewrite a `docProps/core.xml` part's `dcterms:created`/`modified` to the fixed instant.

    python-pptx packages a CHART by embedding a real `.xlsx` of the chart data (built via openpyxl),
    and openpyxl stamps that inner workbook's `docProps/core.xml` with a wall-clock `created`/
    `modified` at build time — the ONE remaining cross-process nondeterminism in the chart fixture.
    We pin those elements to a fixed W3CDTF instant so the embedded workbook (and thus the whole
    `.pptx`) is byte-reproducible across runs (threat T-06-11).
    """
    data = re.sub(
        rb"(<dcterms:created[^>]*>)[^<]*(</dcterms:created>)",
        rb"\g<1>" + _FIXED_W3CDTF.encode() + rb"\g<2>",
        data,
    )
    data = re.sub(
        rb"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)",
        rb"\g<1>" + _FIXED_W3CDTF.encode() + rb"\g<2>",
        data,
    )
    return data


def _normalize_zip(raw: bytes) -> bytes:
    """Rewrite every ZIP entry's date_time to a fixed constant, preserving entry order + content.

    python-pptx already writes a fixed zip date_time, but two paths still drift cross-process and are
    pinned here (belt-and-braces, threat T-06-11): (1) the SmartArt fixture rebuilds the archive
    after XML injection; forcing a fixed `date_time` on every member keeps it stable; (2) the chart
    fixture embeds a nested `.xlsx` (chart data) whose own `docProps/core.xml` carries an openpyxl
    wall-clock — we recurse into any embedded `.xlsx` and pin its core props too.
    """
    zin = zipfile.ZipFile(io.BytesIO(raw))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():  # original entry order -> deterministic
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = _pin_core_xml(data)
            elif item.filename.endswith(".xlsx"):
                # An embedded workbook (e.g. a chart's data) is itself a zip with its own core.xml.
                data = _normalize_embedded_xlsx(data)
            info = zipfile.ZipInfo(item.filename, date_time=_FIXED_ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = item.external_attr
            zout.writestr(info, data)
    return out.getvalue()


def _normalize_embedded_xlsx(raw: bytes) -> bytes:
    """Recurse into an embedded `.xlsx` zip: pin its `docProps/core.xml` + fix its entry mtimes."""
    zin = zipfile.ZipFile(io.BytesIO(raw))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                data = _pin_core_xml(data)
            info = zipfile.ZipInfo(item.filename, date_time=_FIXED_ZIP_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = item.external_attr
            zout.writestr(info, data)
    return out.getvalue()


def _new_presentation() -> "Presentation":  # type: ignore[valid-type]
    """A fresh Presentation with pinned doc timestamps (no embedded wall-clock)."""
    prs = Presentation()
    prs.core_properties.created = _FIXED
    prs.core_properties.modified = _FIXED
    return prs


def _blank_slide(prs):
    """Add and return a slide on the blank layout (index 6 in the default template)."""
    return prs.slides.add_slide(prs.slide_layouts[6])


def _finalize(prs) -> bytes:
    """Save a presentation to byte-reproducible `.pptx` bytes (pinned timestamps + zip mtimes)."""
    buf = io.BytesIO()
    prs.save(buf)
    return _normalize_zip(buf.getvalue())


# --------------------------------------------------------------------------- #
# Each builder returns the exact committed bytes for one fixture. The docstring
# pins the EXPECTED adapter routing (claims vs unextracted) — the golden test
# in test_pptx_golden.py asserts these against the LIVE adapter.
# --------------------------------------------------------------------------- #


def _title_body_bytes() -> bytes:
    """A text frame with two non-empty paragraphs + one EMPTY paragraph (skipped, not a drop).

    Routing: 2 claims ["First paragraph", "Second paragraph"]; the empty paragraph is skipped-empty
             (no unit, no drop). #claims=2, #unextracted=0.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    tf = slide.shapes.add_textbox(Emu(0), Emu(0), Emu(1000), Emu(1000)).text_frame
    tf.text = "First paragraph"
    tf.add_paragraph().text = "Second paragraph"
    tf.add_paragraph().text = ""  # empty paragraph -> skipped-empty (not emitted, not a drop)
    return _finalize(prs)


def _text_box_bytes() -> bytes:
    """A standalone text box with multiple paragraphs (the free-text-frame path).

    Routing: 3 claims ["alpha line", "beta line", "gamma line"]. #claims=3, #unextracted=0.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    tf = slide.shapes.add_textbox(Emu(0), Emu(0), Emu(2000), Emu(1000)).text_frame
    tf.text = "alpha line"
    tf.add_paragraph().text = "beta line"
    tf.add_paragraph().text = "gamma line"
    return _finalize(prs)


def _table_bytes() -> bytes:
    """A 2x2 table with 3 filled cells + 1 empty cell (the empty cell is skipped, not a drop).

    Routing: 3 claims ["r0c0", "r0c1", "r1c0"] (row-major); cell (1,1) is empty -> skipped-empty.
             #claims=3, #unextracted=0.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    table = slide.shapes.add_table(2, 2, Emu(0), Emu(0), Emu(2000), Emu(2000)).table
    table.cell(0, 0).text = "r0c0"
    table.cell(0, 1).text = "r0c1"
    table.cell(1, 0).text = "r1c0"
    table.cell(1, 1).text = ""  # empty cell -> skipped-empty
    return _finalize(prs)


def _notes_bytes() -> bytes:
    """A slide whose only content is a speaker note (the notes path, emitted with `/ notes`).

    Routing: 1 claim ["Speaker note line"] with the `Slide 1 / notes` locator. #claims=1,
             #unextracted=0.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    slide.notes_slide.notes_text_frame.text = "Speaker note line"
    return _finalize(prs)


def _chart_bytes() -> bytes:
    """A chart -> the silent-loss disclosure (chart content is NEVER extracted, out of scope).

    Routing: 0 claims; the chart -> 1 unextracted disclosure. #claims=0, #unextracted=1.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    data = CategoryChartData()
    data.categories = ["a", "b"]
    data.add_series("s", (1, 2))
    slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, Emu(0), Emu(0), Emu(2000), Emu(2000), data
    )
    return _finalize(prs)


def _image_bytes() -> bytes:
    """An embedded 1x1 PNG -> the silent-loss disclosure (picture content out of scope, Pillow-free).

    Routing: 0 claims; the picture -> 1 unextracted disclosure. #claims=0, #unextracted=1.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    slide.shapes.add_picture(io.BytesIO(_PNG_1x1), Emu(0), Emu(0))
    return _finalize(prs)


def _smartart_bytes() -> bytes:
    """A SmartArt diagram (ROADMAP criterion 3) -> disclosed, never a fabricated text claim.

    XML-inject a `graphicFrame` whose `a:graphicData/@uri` is the diagram namespace + an empty
    `graphicData` (the MINIMUM to be DETECTED as SmartArt — `shape_type is None` + the diagram URI —
    not rendered; L2 / gotcha 3). 06-03's unit suite proved the adapter detects exactly this frame.
    Routing: 0 claims; the SmartArt -> 1 unextracted disclosure. #claims=0, #unextracted=1.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    # Anchor on a real graphic frame (a 1x1 table), rewrite its graphicData URI to the diagram
    # namespace, then strip the table payload -> a frame python-pptx sees as shape_type None with
    # the diagram URI (no high-level SmartArt authoring API exists).
    gf = slide.shapes.add_table(1, 1, Emu(0), Emu(0), Emu(1000), Emu(1000))
    graphic_data = gf._element.graphic.graphicData
    graphic_data.set("uri", _DIAGRAM_URI)
    for child in list(graphic_data):
        graphic_data.remove(child)
    return _finalize(prs)


def _nested_group_bytes() -> bytes:
    """A NESTED group (ROADMAP criterion 3) with a readable member AND an unreadable member.

    Author members FIRST (a text box + a picture), then group the text box into an INNER group, then
    group that inner group + the picture into an OUTER group (`add_group_shape` MOVES its members;
    L4). The group NODES themselves are containers — neither a claim nor a drop.
    Routing: the text box -> 1 claim ["grouped text"]; the picture -> 1 unextracted disclosure; both
             group nodes contribute nothing. #claims=1, #unextracted=1 — the L3 nested accounting.
    """
    prs = _new_presentation()
    slide = _blank_slide(prs)
    tb = slide.shapes.add_textbox(Emu(0), Emu(0), Emu(500), Emu(500))
    tb.text_frame.text = "grouped text"
    pic = slide.shapes.add_picture(io.BytesIO(_PNG_1x1), Emu(600), Emu(0))
    inner = slide.shapes.add_group_shape([tb])  # inner group holds the readable member
    slide.shapes.add_group_shape([inner, pic])  # outer group nests the inner group + the picture
    return _finalize(prs)


def _empty_slide_bytes() -> bytes:
    """A single blank slide with NO shapes -> nothing extracted AND nothing lost.

    Routing: 0 claims, 0 unextracted (an empty slide is not a silent drop — there is nothing there).
             #claims=0, #unextracted=0.
    """
    prs = _new_presentation()
    _blank_slide(prs)
    return _finalize(prs)


# fixture filename -> the bytes-builder for it. Keys define the committed corpus.
FIXTURES: dict[str, "callable[[], bytes]"] = {  # type: ignore[type-arg]
    "title_body.pptx": _title_body_bytes,
    "text_box.pptx": _text_box_bytes,
    "table.pptx": _table_bytes,
    "notes.pptx": _notes_bytes,
    "chart.pptx": _chart_bytes,
    "image.pptx": _image_bytes,
    "smartart.pptx": _smartart_bytes,
    "nested_group.pptx": _nested_group_bytes,
    "empty_slide.pptx": _empty_slide_bytes,
}


def main() -> None:
    for name, builder in FIXTURES.items():
        data = builder()
        (HERE / name).write_bytes(data)
        print(f"wrote {name} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
