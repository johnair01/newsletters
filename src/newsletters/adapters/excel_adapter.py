"""The Excel ``.xlsx`` adapter (ADAPT-03) — the second file-extraction ``DistillPort`` backend.

One ``.xlsx`` workbook -> one ``Source`` whose ``transcript`` is a canonical text serialization
of the workbook: one line ``Sheet!A1<sep>value`` per non-empty *extractable* cell, sheets in
workbook order, row-major. The adapter slices the verbatim cell-value units out of that transcript
and hands them — IN TRANSCRIPT ORDER — to the shared ``normalize()`` (ADAPT-01), which mints
content-addressed ``Claim(+Trace)``. The adapter hand-mints NO hashes; the faithful-extraction rule
lives only in ``normalize()`` (CONTEXT decision 2).

THE FAITHFULNESS CRUX (ADAPT-03 criterion 2). A spreadsheet's formulas are not evaluated by
openpyxl. The double-load (R3, via ``load_workbook_pair``) gives two views of the same bytes:

* the FORMULA view (``data_only=False``): ``cell.data_type == 'f'`` identifies a formula cell;
* the DATA view (``data_only=True``): ``cell.value`` is the cached computed value, or ``None`` if
  Excel never wrote a cache (an openpyxl-saved file NEVER writes one).

A formula cell whose data-view value is ``None`` is therefore indistinguishable from a genuinely
blank cell UNLESS you decide formula-ness from the FORMULA view. The rule: a formula cell with a
``None`` cache routes to ``unextracted[]`` (naming the cell + formula) — it is NEVER emitted as
``0`` or ``""``. A genuinely blank cell is simply skipped. "Faithful, not suggestive."

ZERO SILENT DROPS. Every cell is either an emitted claim, a skipped blank, or an ``unextracted[]``
disclosure; every workbook-level object openpyxl could read but we do not extract (charts, images)
is disclosed too. A merged range emits its anchor value ONCE (the covered cells are ``None`` and
skipped) and is NOT a drop — nothing is lost. A malformed/unreadable ``.xlsx`` is caught and
disclosed as a whole-source ``unextracted[]`` entry, never an unhandled crash (V5 input validation).

HARD RULE (mirrors ``manual.py`` / ``email_adapter.py``): this returns truth only. It NEVER calls
``Surface.publish``, sets ``ReviewState.PUBLISHED``, or builds a published ``Review``.

LAZY OPENPYXL. openpyxl is the optional ``[excel]`` extra. It is imported ONLY through
``_openpyxl_loader`` (never at module top), so ``import newsletters`` / ``import
newsletters.adapters`` — which ``adapters/__init__.py`` runs to ``register()`` this adapter — stays
extra-free. The deterministic spine runs with zero openpyxl (AI-optional / minimal-core).
"""

from __future__ import annotations

import io
import re
import zipfile
from datetime import date, datetime, time, timezone
from xml.etree import ElementTree

from ..distill.coverage import Coverage, Unextracted
from ..distill.ports import DistillationResult
from ..locators import FreeLocator
from ..semantic import Distillation, Source
from ._coverage_codec import (
    decode_coverage,
    encode_coverage,
    not_reconstructable_marker,
)
from ._openpyxl_loader import load_workbook_pair
from ._timestamps import deterministic_timestamp
from .normalize import normalize

# The transcript separator (CONTEXT R3 / RESEARCH recommendation: a tab). It only needs to be
# unambiguous for a HUMAN reader of the transcript — ``normalize()`` does pure substring matching,
# so a cell value that itself contains a tab or newline is still emitted VERBATIM (never escaped)
# and stays locatable; the transcript line simply spans more than one physical line. Escaping the
# value would break ``claim.text == transcript slice`` (the Phase-3 span-containment gate).
SEP = "\t"

# The seven Excel error codes openpyxl maps to cell type ``'e'`` (and a formula's cache can itself
# be one of these strings). Source: openpyxl cell module ERROR_CODES.
_ERROR_CODES = frozenset(
    {"#NULL!", "#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#N/A"}
)

# ---- reason strings (the unextracted[] contract; Plan 04's golden corpus pins these) --------
_R_FORMULA_NO_CACHE = (
    "formula cell {coord} has no cached value (uncomputed: {formula!r}) — "
    "not faithfully extractable"
)
_R_FORMULA_ERROR = "formula cell {coord} evaluates to error {err}"
_R_ERROR_CELL = "error cell {coord}: {err}"
_R_CHART = "{sheet}: chart not extracted (chart content is out of scope)"
_R_IMAGE = "{sheet}: image not extracted (drawing content is out of scope)"
_R_UNREADABLE = "workbook could not be read by openpyxl ({error}) — not extractable"

# The OOXML core-properties `created` element (Dublin Core terms namespace).
_DCTERMS_NS = "http://purl.org/dc/terms/"
_CREATED_TAG = f"{{{_DCTERMS_NS}}}created"


def intrinsic_created(raw: bytes) -> datetime | None:
    """Read the workbook's docProps `created` from the RAW OOXML — faithfully None when absent.

    WHY this exists and does NOT use ``openpyxl`` properties: openpyxl's ``DocumentProperties``
    descriptor does ``self.created = created or now()`` — it FABRICATES a wall-clock ``created``
    whenever the source ``docProps/core.xml`` has no ``dcterms:created`` element (verified against
    openpyxl 3.1.5 ``packaging/core.py``). Trusting ``wb.properties.created`` would therefore make
    the timestamp NON-deterministic for any document genuinely missing a creation date — exactly the
    determinism bug the L1 front-fix exists to kill. So we read the intrinsic value straight from the
    raw ``.xlsx`` zip (stdlib ``zipfile`` + ``xml.etree``; no new dependency): the element's text when
    present (parsed as a W3CDTF ISO-8601 instant, tz-naive coerced to UTC), else ``None`` —
    faithfully reflecting that the document carried no creation date, which ``deterministic_timestamp``
    then maps to ``EPOCH_ZERO``.

    Total + robust to hostile input (V5): any failure to open the zip, find/parse the part, or parse
    the date returns ``None`` (the unreadable-source path handles a truly broken workbook separately).
    """
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            core_xml = zf.read("docProps/core.xml")
    except (KeyError, zipfile.BadZipFile, OSError):
        return None
    try:
        root = ElementTree.fromstring(core_xml)
    except ElementTree.ParseError:
        return None
    el = root.find(_CREATED_TAG)
    if el is None or el.text is None or not el.text.strip():
        return None
    text = el.text.strip()
    # OOXML W3CDTF instants commonly end in 'Z'; Python's fromisoformat handles +00:00, not 'Z',
    # before 3.11 — normalize defensively so the parse is deterministic across runtimes.
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def value_to_str(v: object) -> str:
    """Canonical, deterministic, LOSSLESS value -> string (R3, the locked rule).

    The ordering is load-bearing:

    * ``bool`` BEFORE ``int`` — ``bool`` is an ``int`` subclass, so a ``True`` checked as an int
      would wrongly become ``"1"``. ``TRUE``/``FALSE`` (upper-case, Excel's literal form).
    * ``int`` -> ``str(int)`` — ``1`` -> ``"1"``, NEVER ``"1.0"`` (an int is not a float).
    * ``float`` -> ``repr(float)`` — the shortest round-tripping decimal (deterministic in
      CPython >= 3.1): ``1.0`` -> ``"1.0"``, ``0.1 + 0.2`` -> the exact shortest form. NO
      fixed-precision formatting (no ``f"{v:.2f}"``) — that would silently round/reformat.
    * ``datetime``/``date``/``time`` -> ``.isoformat()`` — lossless, locale-free, deterministic.
    * everything else (``str``) -> verbatim passthrough.
    """
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, time):
        return v.isoformat()
    return str(v)


def _cell_decision(cell_f: object, cell_d: object) -> tuple[str, str | None]:
    """The faithful per-cell fork. Returns ``('emit', text) | ('skip', None) | ('unextracted', reason)``.

    Formula-ness is decided from the FORMULA view's ``data_type``, NEVER from the data view (a
    data-view formula cell shows only its cache/None, never the ``'='``). The cache is read from
    the DATA view.

    * formula (``data_type == 'f'``) with a ``None`` cache -> ``unextracted`` (the crux: NEVER
      ``"0"``/``""``).
    * formula whose cache is itself an error code -> ``unextracted``.
    * formula with a real cached value -> ``emit`` the value->string of the cache.
    * error cell (``data_type == 'e'``) -> ``unextracted``.
    * blank (formula-view value is ``None`` and not a formula; incl. merge-covered cells) -> ``skip``.
    * literal (str/int/float/bool/datetime) -> ``emit`` the value->string of the value.
    """
    coord = cell_f.coordinate  # type: ignore[attr-defined]
    if cell_f.data_type == "f":  # type: ignore[attr-defined]
        cached = cell_d.value  # type: ignore[attr-defined]
        if cached is None:
            return (
                "unextracted",
                _R_FORMULA_NO_CACHE.format(coord=coord, formula=cell_f.value),  # type: ignore[attr-defined]
            )
        if isinstance(cached, str) and cached in _ERROR_CODES:
            return ("unextracted", _R_FORMULA_ERROR.format(coord=coord, err=cached))
        return ("emit", value_to_str(cached))
    if cell_f.data_type == "e":  # type: ignore[attr-defined]
        return ("unextracted", _R_ERROR_CELL.format(coord=coord, err=cell_f.value))  # type: ignore[attr-defined]
    if cell_f.value is None:  # type: ignore[attr-defined]
        return ("skip", None)
    return ("emit", value_to_str(cell_f.value))  # type: ignore[attr-defined]


def _feature_drops(wb_formula: object) -> list[Unextracted]:
    """Disclose workbook-level objects openpyxl read but we do not extract (charts/images).

    Uses the R4-confirmed attribute names (``ws._charts`` / ``ws._images``, openpyxl 3.1.5; see
    05-02-SUMMARY). They are present ONLY in standard mode (``read_only=False``, which
    ``load_workbook_pair`` guarantees). ``getattr(..., [])`` is a conservative fallback if a future
    openpyxl renames them — worst case we disclose nothing here rather than crash, and the
    per-cell accounting still holds.
    """
    out: list[Unextracted] = []
    for ws in wb_formula.worksheets:  # type: ignore[attr-defined]
        title = ws.title
        for _chart in getattr(ws, "_charts", []):
            out.append(
                Unextracted(
                    locator=FreeLocator(text=title),
                    reason=_R_CHART.format(sheet=title),
                )
            )
        for _image in getattr(ws, "_images", []):
            out.append(
                Unextracted(
                    locator=FreeLocator(text=title),
                    reason=_R_IMAGE.format(sheet=title),
                )
            )
    return out


def _serialize(wb_formula: object, wb_data: object) -> tuple[str, list[str], list[Unextracted]]:
    """Walk both views cell-by-cell and build ``(transcript, units, cell_drops)`` deterministically.

    Sheets in workbook order; within a sheet, row-major (``iter_rows``). Each emitted cell yields a
    transcript line ``Sheet!A1<sep>value\\n`` and appends the SAME value string to ``units`` (so
    every unit is, by construction, an exact substring of the transcript at its own offset — the
    ``Sheet!A1<sep>`` prefix separates adjacent values, so duplicate values get distinct, ordered,
    locatable spans via ``normalize()``'s forward-only cursor). Per-cell ``unextracted`` decisions
    (formula-cache gap, error cells) are collected into ``cell_drops`` naming the ``Sheet!A1`` cell.
    """
    lines: list[str] = []
    units: list[str] = []
    cell_drops: list[Unextracted] = []

    for ws_f, ws_d in zip(wb_formula.worksheets, wb_data.worksheets):  # type: ignore[attr-defined]
        sheet = ws_f.title
        for row_f, row_d in zip(ws_f.iter_rows(), ws_d.iter_rows()):
            for cell_f, cell_d in zip(row_f, row_d):
                kind, payload = _cell_decision(cell_f, cell_d)
                if kind == "skip":
                    continue
                if kind == "emit":
                    assert payload is not None
                    lines.append(f"{sheet}!{cell_f.coordinate}{SEP}{payload}\n")
                    units.append(payload)
                else:  # 'unextracted'
                    cell_drops.append(
                        Unextracted(
                            locator=FreeLocator(text=f"{sheet}!{cell_f.coordinate}"),
                            reason=payload or "",
                        )
                    )
    return "".join(lines), units, cell_drops


class ExcelAdapter:
    """Parse ``.xlsx`` bytes into a ``Source`` + verbatim units, then ``normalize()`` -> result.

    Registered under the name ``"excel"`` (see ``adapters/__init__.py``). ``distill(sources)`` is
    signature-exact with ``DistillPort``; ``parse(raw, path)`` is the public entrypoint that turns
    raw ``.xlsx`` bytes into the ``Source`` this backend distills. The adapter is STATELESS across
    ``parse()``/``distill()`` (TASK ZERO, R1): per-Source ``unextracted[]`` travels on the Source
    itself (``Source.extraction`` via the shared codec), never in instance memory.
    """

    name = "excel"

    # ------------------------------------------------------------------ #
    # Parse: raw .xlsx bytes -> (Source, transcript-order units, partial unextracted[])
    # ------------------------------------------------------------------ #
    def parse(
        self, raw: bytes, path: str
    ) -> tuple[Source, list[str], list[Unextracted]]:
        """Parse ``raw`` ``.xlsx`` bytes into a ``Source`` + transcript-order units + drops.

        Double-loads the bytes (formula view + data view, ``read_only=False``) via
        ``load_workbook_pair``, builds the canonical transcript + units, collects per-cell drops
        (formula-cache gap, error cells) and workbook-level feature drops (charts/images), and sets
        ``source.extraction = encode_coverage(drops)`` so the drops travel WITH the Source (R1).

        Robust to hostile input (V5): a malformed/unreadable ``.xlsx`` (openpyxl raises) is caught
        and disclosed as a SINGLE whole-source ``unextracted[]`` entry — never an unhandled crash.
        Both workbooks are always closed (no resource leak).
        """
        try:
            wb_formula, wb_data = load_workbook_pair(raw)
        except Exception as exc:  # noqa: BLE001 — untrusted input; disclose, never crash
            # A whole-source disclosure: we faithfully admit we could not read it.
            drop = Unextracted(
                locator=FreeLocator(text=path),
                reason=_R_UNREADABLE.format(error=type(exc).__name__),
            )
            source = Source(
                id=path,
                context=path,
                transcript="",
                extraction=encode_coverage([drop]),
                # An unreadable workbook has no intrinsic timestamp; pass the deterministic sentinel
                # explicitly (L1) so even this error path never falls back to wall-clock now().
                timestamp=deterministic_timestamp(None),
            )
            return source, [], [drop]

        try:
            transcript, units, cell_drops = _serialize(wb_formula, wb_data)
            feature_drops = _feature_drops(wb_formula)
        finally:
            wb_formula.close()
            wb_data.close()

        # A deterministic, document-intrinsic timestamp (mirrors EmailAdapter sourcing it from the
        # Date header, NOT now()). The workbook's OOXML docProps `created` is the analog: a
        # spreadsheet has no Date header, so we use docProps/core.xml's creation time WHEN PRESENT.
        #
        # We read it from the RAW bytes via `intrinsic_created`, NOT from `wb.properties.created`:
        # openpyxl FABRICATES a wall-clock `created` (`created or now()`) whenever the part lacks the
        # element, which would re-introduce the very non-determinism this front-fix removes. Reading
        # the raw XML yields None faithfully when the document carried no creation date, which
        # `deterministic_timestamp` then maps to the EPOCH_ZERO sentinel — so an .xlsx with no
        # intrinsic `created` parses to a byte-identical Source twice.
        created = intrinsic_created(raw)

        drops = cell_drops + feature_drops
        # ALWAYS pass an explicit deterministic timestamp (L1): the workbook's docProps `created`
        # when present, else the EPOCH_ZERO sentinel — NEVER the wall-clock Source default factory,
        # so an .xlsx with no `created` parses to a byte-identical Source twice. deterministic_timestamp
        # also coerces openpyxl's tz-naive `created` to UTC. See adapters/_timestamps.py for WHY.
        source = Source(
            id=path,
            context=path,
            transcript=transcript,
            extraction=encode_coverage(drops),
            timestamp=deterministic_timestamp(created),
        )
        return source, units, drops

    # ------------------------------------------------------------------ #
    # The DistillPort entrypoint
    # ------------------------------------------------------------------ #
    def distill(self, sources: list[Source]) -> DistillationResult:
        """Mint claims via ``normalize()`` and merge adapter-drops with normalize-drops.

        Each ``Source`` was produced by ``parse()`` (transcript + carried ``extraction``). We
        re-derive the units from the transcript the SAME deterministic way ``parse`` did, so a
        ``Source`` that round-tripped through JSON still distills identically on a FRESH adapter.
        Returns truth only — never publishes (HARD RULE, ``manual.py``).
        """
        all_claims = []
        merged_unextracted: list[Unextracted] = []
        traces: list[Source] = []

        for source in sources:
            # R2 safety-net (belt-and-suspenders): a Source this adapter did not produce carries no
            # ``extraction`` record, and its adapter-side drops are NOT reconstructable from the
            # transcript alone (a formula-cache gap leaves no transcript line). Record an explicit
            # 'coverage-not-reconstructable' marker (forces Coverage.complete=False) — honest
            # uncertainty over a false complete=True. A Source this adapter parse()d has
            # ``extraction`` set, so the marker does NOT fire.
            if source.extraction is None:
                merged_unextracted.append(not_reconstructable_marker(source.id))

            units, adapter_unx = self._units_for(source)
            claims, norm_unx = normalize(source, units)
            all_claims.extend(claims)
            merged_unextracted.extend(adapter_unx)
            merged_unextracted.extend(norm_unx)
            traces.append(source)

        coverage = Coverage(
            complete=(len(merged_unextracted) == 0),
            unextracted=merged_unextracted,
            cost_hint="free",
            effort_hint="deterministic",
        )
        return DistillationResult(
            distillation=Distillation(claims=all_claims, traces=traces),
            coverage=coverage,
            backend=self.name,
        )

    def _units_for(self, source: Source) -> tuple[list[str], list[Unextracted]]:
        """Re-derive the cell-value units from a built transcript ``Source`` + recover its drops.

        ``parse()`` put the canonical transcript on the ``Source`` as ``Sheet!A1<sep>value\\n``
        lines. Here we recover the verbatim value units by splitting each line on the FIRST
        separator and taking the value (the part after ``Sheet!A1<sep>``), stripping the single
        trailing ``\\n`` the serializer added. This is the SAME serialization rule ``parse`` used,
        so each unit stays an exact substring of ``source.transcript`` and ``normalize()`` locates
        every one. A value containing an embedded ``\\n``/``<sep>`` still round-trips: we split only
        on the FIRST separator and strip only the serializer's single terminal newline.

        The adapter-side ``unextracted[]`` (formula-cache gap, error cells, charts/images) is NOT
        reconstructable from the transcript alone, so it is recovered from the typed carrier
        ``parse()`` set on the Source (``source.extraction``) via the shared codec — so a
        round-tripped Source distills with identical coverage on a FRESH adapter (R1).
        """
        units = _split_transcript_units(source.transcript)
        adapter_unx = decode_coverage(source.extraction)
        return units, adapter_unx


# A record prefix is exactly ``{sheet}!{coord}{SEP}`` at a line start. A sheet name cannot contain
# ``\n`` (Excel forbids it) and a coordinate is ``[A-Z]+[0-9]+`` (column letters + 1-based row), so
# the prefix never contains a ``\n``. The ``SEP`` ends the prefix. This anchored pattern is how we
# tell a TRUE record start from a value's own continuation line (a wrapped value line begins with
# the value's own text, not a ``sheet!coord<SEP>`` prefix — see _split_transcript_units).
_RECORD_PREFIX = re.compile(rf"[^\n]+?![A-Z]+[0-9]+{re.escape(SEP)}")


def _split_transcript_units(transcript: str) -> list[str]:
    """Recover the ordered value units from a serialized transcript (the inverse of ``_serialize``).

    The transcript is the concatenation of ``"{sheet}!{coord}{SEP}{value}\\n"`` records. A value may
    itself contain ``\\n`` and/or ``SEP`` (faithfulness — values are NEVER escaped), so we cannot
    split on ``\\n`` or ``SEP`` alone. We instead split on the unambiguous RECORD BOUNDARY: a record
    starts at a line whose prefix matches ``{sheet}!{coord}{SEP}`` (the anchored ``_RECORD_PREFIX``).
    A value's wrapped continuation line never matches that prefix (it begins with the value's own
    text), so each unit is exactly the text from after its prefix's ``SEP`` up to the ``\\n`` that
    immediately precedes the NEXT record prefix (or end of transcript). Each recovered unit is thus
    a verbatim substring of the transcript, in order — so ``normalize()`` locates every one and
    duplicates get distinct, forward-only offsets.

    Returns ``[]`` for an empty transcript (a whole-source-unreadable Source carries no units).
    """
    if not transcript:
        return []
    # Find the byte offset where every TRUE record starts (a line-start prefix match).
    starts: list[int] = []
    for m in _RECORD_PREFIX.finditer(transcript):
        at_line_start = m.start() == 0 or transcript[m.start() - 1] == "\n"
        if at_line_start:
            starts.append(m.start())
    units: list[str] = []
    for i, start in enumerate(starts):
        sep_idx = transcript.find(SEP, start)
        value_start = sep_idx + len(SEP)
        # The value runs up to the '\n' that precedes the NEXT record start (or to end-of-text for
        # the last record); strip exactly the serializer's single terminal '\n'.
        next_start = starts[i + 1] if i + 1 < len(starts) else len(transcript)
        value_end = next_start
        if value_end > value_start and transcript[value_end - 1] == "\n":
            value_end -= 1
        units.append(transcript[value_start:value_end])
    return units
