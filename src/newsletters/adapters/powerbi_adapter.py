r"""The Power BI ``PowerBiAdapter`` (ADAPT-05) — the fourth file-extraction ``DistillPort`` backend.

A Power BI **PBIP** project (a folder of plain-text TMDL + PBIR JSON) -> one ``Source`` whose
``transcript`` is a canonical multi-file serialization: one line ``<prefix>\t<verbatim value>\n``
per emitted unit, files walked in SORTED order, objects in declaration order within a file. The
``prefix`` carries the file + object path (e.g. ``Model/Table[Sales]/Measure[Total Sales].expression``,
``Report/Page[Overview]/Visual[topProducts].title``) and is NOT part of the claim value — the value
after the tab is the verbatim unit the shared ``normalize()`` (ADAPT-01) locates and content-addresses.
The adapter hand-mints NO hashes; the faithful-extraction rule lives only in ``normalize()``.

WHAT IS EXTRACTED (faithful model/report TEXT — never data). From TMDL (via ``_tmdl.parse_tmdl``):
table/column/measure/relationship/hierarchy names, column ``dataType``/``summarizeBy``/etc., ``///``
descriptions, and a measure's DAX ``expression`` TEXT (a formula, NEVER a computed value — the Excel
formula-cache crux restated). From PBIR JSON (via ``_pbir.extract_report``): page display names,
visual titles, text-box runs, field references, and persisted filter LITERAL values (config text the
reviewer sees, never silently treated as query-result data).

FAIL LOUD (criterion 2 / L3). PBIP/TMDL/PBIR is a DEFINITION format — it contains the model and
report definition, NOT data rows. Every row-cap / aggregation signal is disclosed to ``unextracted[]``
so a clipped/aggregated export can never read as complete: ``_R_TOPN`` (Top-N filter), ``_R_FILTER``
(restricting filter), ``_R_AGGREGATED`` (Sum/Avg/... aggregation), ``_R_MEASURE_VALUE`` (a measure is
an aggregate formula — its value is absent, never fabricated), ``_R_DIRECTQUERY`` (a DirectQuery
partition stores no rows), ``_R_ROWLIMIT`` (a visual data-reduction/maxRows cap). And — categorically
— a whole-source ``_R_NO_DATA_ROWS`` is emitted ONCE whenever a model is extracted, so ANY non-trivial
export forces ``Coverage.complete=False`` (Pitfall 3 / success criterion 2).

ENTRYPOINTS (L4). ``parse_path(path)`` walks a PBIP FOLDER tree (sorted, deterministic) and returns
the same ``(Source, units, drops)`` triple as the byte ``parse(raw, path)``; both converge on ONE
serializer (``_serialize``). ``parse(raw, path)`` handles a single dropped file (``.tmdl`` / ``.json``
/ ``.bim``) and routes a ``.pbix`` / ZIP-OLE binary byte input to the whole-source ``_R_PBIX_BINARY``
deferral (L1 — pbixray DEFERRED, ZERO new dependency: "export to PBIP/PBIR for faithful extraction").
``parse(raw, path)`` is also what lets the adapter JOIN the existing parity + determinism matrices.

DETERMINISM (L4 / Q-F / Pitfall 4). PBIP has no single intrinsic date, so ``timestamp`` is ALWAYS
``deterministic_timestamp(None)`` -> ``EPOCH_ZERO`` (NEVER filesystem mtime). Every directory listing
is ``sorted()``. Two parses of the same tree yield byte-identical Sources.

HARD RULE (mirrors ``manual.py`` / ``excel_adapter.py`` / ``pptx_adapter.py``): this returns truth
only. It NEVER calls ``Surface.publish``, sets ``ReviewState.PUBLISHED``, or builds a published
``Review``.

SECURITY (V5 / T-07-08..13). PBIP input is UNTRUSTED. Every per-file read/parse is wrapped in
try/except -> a ``_R_UNREADABLE`` disclosure, never an unhandled crash. A ``.pbix`` ZIP is NEVER
decompressed (no zip-bomb surface — it routes to the binary deferral). The folder walk resolves only
files WITHIN the project root and rejects symlinks that escape it (path-traversal mitigation). No
network, no external-link following, no clock read.

STDLIB ONLY. This module imports only ``json`` / ``pathlib`` / ``re`` from the standard library plus
the in-repo spine (``normalize`` / ``_coverage_codec`` / ``_timestamps`` / ``..distill`` /
``..locators`` / ``..semantic``) and the Wave-1 parsers (``_tmdl`` / ``_pbir``). There is NO optional
extra — ``register(PowerBiAdapter())`` runs on a bare install, and ``lint-imports`` / AI-isolation
stay green with zero new dependency.
"""

from __future__ import annotations

import json
import pathlib
import re

from ..distill.coverage import Coverage, Unextracted
from ..distill.ports import DistillationResult
from ..locators import FreeLocator
from ..semantic import Distillation, Source
from ._coverage_codec import (
    decode_coverage,
    encode_coverage,
    not_reconstructable_marker,
)
from ._pbir import Detection, detect_row_caps, extract_report
from ._timestamps import deterministic_timestamp
from ._tmdl import parse_tmdl
from .normalize import normalize

# The transcript separator (mirror Excel/PPTX). It only needs to be unambiguous for a HUMAN reader —
# ``normalize()`` does pure substring matching, so a value that itself contains a tab/newline/colon
# is still emitted VERBATIM and stays locatable; escaping it would break ``claim.text == slice``.
SEP = "\t"


# --------------------------------------------------------------------------- #
# The unextracted[] reason taxonomy (L3 / 07-RESEARCH Q-D). These EXACT strings are the contract
# Plan 04's golden corpus imports and pins — do NOT reword them without updating the golden.
# --------------------------------------------------------------------------- #
_R_TOPN = "Top-N filter restricts the row set — rows beyond the top N are clipped, not in the export"
_R_FILTER = "a restricting filter limits the row set — full detail not represented in the export"
_R_AGGREGATED = "a field is shown aggregated — underlying detail rows are not in the export"
_R_MEASURE_VALUE = (
    "measure: aggregate formula extracted; the computed value is not present (never fabricated)"
)
_R_DIRECTQUERY = "a DirectQuery partition stores no rows in the model — no data rows are extractable"
_R_TMDL_UNPARSED = "a TMDL line was read but not faithfully extractable ({line!r}) — disclosed, not dropped"
_R_ROWLIMIT = "a visual data-reduction/row limit is set — displayed data may be truncated"
_R_NO_DATA_ROWS = (
    "PBIP/TMDL/PBIR is a definition format — it contains no data rows; "
    "measure/column values are not present and are never fabricated"
)
_R_PBIX_BINARY = (
    "binary .pbix not extractable by the text adapter — export to PBIP/PBIR "
    "(File > Save as Power BI project) for faithful extraction"
)
_R_UNREADABLE = "Power BI project file ({path}) could not be read ({error}) — not extractable"
_R_BINARY_FILE = "binary/non-text artifact ({path}) not extracted"

# How a Detection.kind maps to its reason string. ``measure_value`` is owned here too (a measure is
# an aggregate formula; its value is absent). Unknown kinds degrade to the generic filter reason
# rather than a silent miss (key-leniency inherited from _pbir).
_DETECTION_REASON: dict[str, str] = {
    "topn": _R_TOPN,
    "filter": _R_FILTER,
    "aggregated": _R_AGGREGATED,
    "measure_value": _R_MEASURE_VALUE,
    "directquery": _R_DIRECTQUERY,
    "rowlimit": _R_ROWLIMIT,
}

# ZIP / OLE-compound magic bytes. A ``.pbix`` is a ZIP; legacy OLE is the compound-document magic.
# We sniff the leading bytes so a dropped binary (even mislabelled) routes to the deferral, and we
# NEVER decompress it (no zip-bomb surface, L1 / T-07-10).
_ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
_OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _drop(prefix: str, reason: str) -> Unextracted:
    """Build one ``Unextracted`` with a ``FreeLocator`` content anchor (the object-path / file)."""
    return Unextracted(locator=FreeLocator(text=prefix), reason=reason)


def _looks_binary(raw: bytes, path: str) -> bool:
    """True if ``raw`` is a ``.pbix``/ZIP/OLE binary (route to the deferral; NEVER decompress)."""
    lower = path.lower()
    if lower.endswith(".pbix"):
        return True
    head = raw[:8]
    if head.startswith(_ZIP_MAGIC):
        return True
    if head == _OLE_MAGIC:
        return True
    return False


# --------------------------------------------------------------------------- #
# Serialization: walk a list of (prefix, value) units + a list of drops -> transcript
# --------------------------------------------------------------------------- #


def _emit(
    pairs: list[tuple[str, str]],
    lines: list[str],
    units: list[str],
) -> None:
    """Append ``<prefix>\\t<value>\\n`` transcript lines + the SAME ``value`` strings to ``units``.

    The value is the SAME string in BOTH the transcript line and ``units``, so every unit is, by
    construction, an exact substring of the transcript at its own offset (``normalize()`` locates it).
    """
    for prefix, value in pairs:
        lines.append(f"{prefix}{SEP}{value}\n")
        units.append(value)


def _detections_to_drops(dets: list[Detection]) -> list[Unextracted]:
    """Map each ``Detection`` to its ``_R_*`` ``unextracted[]`` reason (the L3 taxonomy)."""
    return [
        _drop(d.path, _DETECTION_REASON.get(d.kind, _R_FILTER)) for d in dets
    ]


# --------------------------------------------------------------------------- #
# The single, shared folder-tree serializer (parse_path + a single .tmdl/.json both feed this)
# --------------------------------------------------------------------------- #


def _serialize_tmdl_text(
    text: str, file_prefix: str, lines: list[str], units: list[str], drops: list[Unextracted]
) -> bool:
    """Parse one TMDL ``text`` into transcript lines + units + drops. Returns True iff a model was read.

    The ``directQuery`` TMDL signal maps to ``_R_DIRECTQUERY``; a measure's DAX is emitted verbatim
    (with a ``.expression`` prefix) and ALSO drives a ``_R_MEASURE_VALUE`` disclosure so the absent
    computed value is never mistaken for present.
    """
    pairs, signals = parse_tmdl(text)
    _emit(pairs, lines, units)
    if "directQuery" in signals:
        drops.append(_drop(file_prefix, _R_DIRECTQUERY))
    # Any line the parser READ but could not extract is disclosed, never silently dropped.
    for sig in signals:
        if sig.startswith("unparsed:"):
            drops.append(_drop(file_prefix, _R_TMDL_UNPARSED.format(line=sig[len("unparsed:"):].strip())))
    # A measure's DAX expression is an aggregate formula — disclose the absent value once per measure.
    for prefix, _value in pairs:
        if prefix.endswith(".expression") and "/Measure[" in prefix:
            drops.append(_drop(prefix, _R_MEASURE_VALUE))
    return bool(pairs)


def _serialize_report_json(
    obj: object, object_path: str, lines: list[str], units: list[str], drops: list[Unextracted]
) -> None:
    """Extract one PBIR JSON object's text units + map its row-cap detections to ``_R_*`` drops."""
    if not isinstance(obj, dict):
        return
    _emit(extract_report(obj, object_path), lines, units)
    drops.extend(_detections_to_drops(detect_row_caps(obj, object_path)))


def _page_path(page_dir: pathlib.Path) -> str:
    """The object-path prefix for a PBIR page dir (``Report/Page[<dirname>]``)."""
    return f"Report/Page[{page_dir.name}]"


def _serialize_tree(root: pathlib.Path) -> tuple[str, list[str], list[Unextracted]]:
    """Walk a PBIP folder deterministically -> ``(transcript, units, drops)``.

    Every directory listing is ``sorted()`` (determinism, T-07-12). TMDL model files are walked
    first (``*.SemanticModel/definition/**/*.tmdl`` and legacy ``model.bim`` TMSL JSON), then the
    PBIR report tree (``*.Report/definition/**/*.json``, page/visual aware). Each per-file read/parse
    is wrapped in try/except -> a ``_R_UNREADABLE`` disclosure (V5 / T-07-11), never a crash. When a
    model is extracted, the categorical whole-source ``_R_NO_DATA_ROWS`` is emitted ONCE (L3).
    """
    lines: list[str] = []
    units: list[str] = []
    drops: list[Unextracted] = []
    model_seen = False

    # ---- Semantic model: TMDL (primary) + model.bim (TMSL JSON, secondary) ----
    for sm_dir in sorted(root.glob("*.SemanticModel")):
        for tmdl in sorted((sm_dir / "definition").rglob("*.tmdl")):
            rel = tmdl.relative_to(root).as_posix()
            try:
                text = tmdl.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                drops.append(_drop(rel, _R_UNREADABLE.format(path=rel, error=type(exc).__name__)))
                continue
            if _serialize_tmdl_text(text, rel, lines, units, drops):
                model_seen = True
        # TMSL model.bim (only present when saved as TMSL) — the same artifacts as JSON.
        bim = sm_dir / "model.bim"
        if bim.is_file():
            rel = bim.relative_to(root).as_posix()
            try:
                tmsl = json.loads(bim.read_text(encoding="utf-8"))
                model_seen = _serialize_tmsl(tmsl, lines, units) or model_seen
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                drops.append(_drop(rel, _R_UNREADABLE.format(path=rel, error=type(exc).__name__)))

    # ---- Report: PBIR enhanced definition tree ----
    for rpt_dir in sorted(root.glob("*.Report")):
        definition = rpt_dir / "definition"
        # report.json (report-level metadata + filters)
        report_json = definition / "report.json"
        if report_json.is_file():
            _read_report_json(report_json, root, "Report", lines, units, drops)
        # pages/<page>/page.json + visuals/<visual>/visual.json
        pages_dir = definition / "pages"
        for page_dir in sorted(p for p in pages_dir.glob("*") if p.is_dir()):
            page_prefix = _page_path(page_dir)
            page_json = page_dir / "page.json"
            if page_json.is_file():
                _read_report_json(page_json, root, page_prefix, lines, units, drops)
            visuals_dir = page_dir / "visuals"
            for visual_dir in sorted(v for v in visuals_dir.glob("*") if v.is_dir()):
                visual_json = visual_dir / "visual.json"
                if visual_json.is_file():
                    vprefix = f"{page_prefix}/Visual[{visual_dir.name}]"
                    _read_report_json(visual_json, root, vprefix, lines, units, drops)

    # The categorical truth: a model export contains NO data rows. Emit once -> complete=False.
    if model_seen:
        drops.append(_drop(str(root), _R_NO_DATA_ROWS))

    return "".join(lines), units, drops


def _read_report_json(
    file: pathlib.Path,
    root: pathlib.Path,
    object_path: str,
    lines: list[str],
    units: list[str],
    drops: list[Unextracted],
) -> None:
    """Read + parse one PBIR JSON file -> units + drops, disclosing an unreadable file (V5)."""
    rel = file.relative_to(root).as_posix()
    try:
        obj = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        drops.append(_drop(rel, _R_UNREADABLE.format(path=rel, error=type(exc).__name__)))
        return
    _serialize_report_json(obj, object_path, lines, units, drops)


def _serialize_tmsl(tmsl: object, lines: list[str], units: list[str]) -> bool:
    """Extract TMSL (``model.bim``) table/column/measure text — the JSON analog of TMDL.

    Returns True iff at least one model artifact was emitted. Key-lenient (missing keys degrade,
    never crash). Faithful: a measure's ``expression`` is emitted verbatim, never a value.
    """
    if not isinstance(tmsl, dict):
        return False
    model = tmsl.get("model", {})
    tables = model.get("tables", []) if isinstance(model, dict) else []
    emitted = False
    for table in tables if isinstance(tables, list) else []:
        if not isinstance(table, dict):
            continue
        tname = str(table.get("name", ""))
        tprefix = f"Model/Table[{tname}]"
        if tname:
            _emit([(f"{tprefix}.name", tname)], lines, units)
            emitted = True
        for col in table.get("columns", []) if isinstance(table.get("columns"), list) else []:
            if not isinstance(col, dict):
                continue
            cname = str(col.get("name", ""))
            cprefix = f"{tprefix}/Column[{cname}]"
            if cname:
                _emit([(f"{cprefix}.name", cname)], lines, units)
            if "dataType" in col:
                _emit([(f"{cprefix}.dataType", str(col["dataType"]))], lines, units)
        for meas in table.get("measures", []) if isinstance(table.get("measures"), list) else []:
            if not isinstance(meas, dict):
                continue
            mname = str(meas.get("name", ""))
            mprefix = f"{tprefix}/Measure[{mname}]"
            if mname:
                _emit([(f"{mprefix}.name", mname)], lines, units)
            expr = meas.get("expression")
            if isinstance(expr, str):
                _emit([(f"{mprefix}.expression", expr)], lines, units)
            elif isinstance(expr, list):
                _emit([(f"{mprefix}.expression", "\n".join(str(e) for e in expr))], lines, units)
    return emitted


class PowerBiAdapter:
    """Parse a PBIP folder / a single dropped file into a ``Source`` + units, then ``normalize()``.

    Registered under the name ``"powerbi"`` (see ``adapters/__init__.py``). ``distill(sources)`` is
    signature-exact with ``DistillPort``. The adapter is STATELESS across ``parse``/``distill`` (R1):
    per-Source ``unextracted[]`` travels on the Source itself (``Source.extraction`` via the shared
    codec), never in instance memory.
    """

    name = "powerbi"

    # ------------------------------------------------------------------ #
    # Folder entrypoint: a PBIP tree -> (Source, transcript-order units, drops)
    # ------------------------------------------------------------------ #
    def parse_path(self, path: str) -> tuple[Source, list[str], list[Unextracted]]:
        """Walk a PBIP FOLDER tree (sorted, deterministic) into a ``Source`` + units + drops.

        A single dropped file path (``.tmdl`` / ``.json`` / ``.bim``) is delegated to ``parse`` so
        both entrypoints share ONE serializer. A ``.pbix`` path routes to the binary deferral. Any
        whole-tree read failure is disclosed as a single ``_R_UNREADABLE`` whole-source entry.
        """
        p = pathlib.Path(path)
        if p.is_file():
            try:
                return self.parse(p.read_bytes(), str(p))
            except OSError as exc:
                return self._unreadable_source(str(p), type(exc).__name__)
        if not p.is_dir():
            return self._unreadable_source(path, "path is neither a file nor a directory")
        try:
            transcript, units, drops = _serialize_tree(p)
        except Exception as exc:  # noqa: BLE001 — untrusted tree; disclose, never crash (V5)
            return self._unreadable_source(path, type(exc).__name__)
        source = self._build_source(path, transcript, drops)
        return source, units, drops

    # ------------------------------------------------------------------ #
    # Byte entrypoint: a single dropped file (.tmdl/.json/.bim) or a .pbix binary deferral
    # ------------------------------------------------------------------ #
    def parse(self, raw: bytes, path: str) -> tuple[Source, list[str], list[Unextracted]]:
        """Parse a single dropped file's ``raw`` bytes into a ``Source`` + units + drops.

        A ``.pbix`` / ZIP / OLE binary (the bytes are sniffed, the path suffix is honoured) routes to
        the whole-source ``_R_PBIX_BINARY`` deferral (L1 — pbixray DEFERRED, the ZIP is NEVER
        decompressed). Otherwise the bytes are decoded as UTF-8 text and routed by suffix: ``.tmdl``
        through the TMDL parser, ``.json`` / ``.bim`` through the JSON path. A decode/parse failure is
        disclosed as a single whole-source ``_R_UNREADABLE`` entry — never an unhandled crash (V5).
        """
        if _looks_binary(raw, path):
            drop = _drop(path, _R_PBIX_BINARY)
            return self._build_source(path, "", [drop]), [], [drop]

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            return self._unreadable_source(path, type(exc).__name__)

        lines: list[str] = []
        units: list[str] = []
        drops: list[Unextracted] = []
        lower = path.lower()
        model_seen = False
        try:
            if lower.endswith(".tmdl"):
                model_seen = _serialize_tmdl_text(text, path, lines, units, drops)
            elif lower.endswith(".bim"):
                model_seen = _serialize_tmsl(json.loads(text), lines, units)
            elif lower.endswith(".json"):
                obj = json.loads(text)
                # A dropped report JSON (report/page/visual) — use the file name as the object path.
                _serialize_report_json(obj, path, lines, units, drops)
            else:
                # Unknown text artifact — try TMDL first (lenient), else disclose as binary/non-text.
                model_seen = _serialize_tmdl_text(text, path, lines, units, drops)
                if not model_seen:
                    drops.append(_drop(path, _R_BINARY_FILE.format(path=path)))
        except json.JSONDecodeError as exc:
            return self._unreadable_source(path, type(exc).__name__)

        if model_seen:
            drops.append(_drop(path, _R_NO_DATA_ROWS))

        source = self._build_source(path, "".join(lines), drops)
        return source, units, drops

    # ------------------------------------------------------------------ #
    # Source construction helpers (timestamp is ALWAYS EPOCH_ZERO — PBIP has no intrinsic date)
    # ------------------------------------------------------------------ #
    def _build_source(
        self, path: str, transcript: str, drops: list[Unextracted]
    ) -> Source:
        """Build a ``Source`` with the carried drops and the deterministic EPOCH_ZERO timestamp.

        ``deterministic_timestamp(None)`` -> EPOCH_ZERO unconditionally (L4 / Q-F — PBIP has no single
        intrinsic date; the adapter NEVER reads filesystem mtime). ``source.extraction`` carries the
        drops so they travel WITH the Source through ``model_dump_json`` (R1 round-trip parity).
        """
        return Source(
            id=path,
            context=path,
            transcript=transcript,
            extraction=encode_coverage(drops),
            timestamp=deterministic_timestamp(None),
        )

    def _unreadable_source(
        self, path: str, error: str
    ) -> tuple[Source, list[str], list[Unextracted]]:
        """The whole-source-unreadable branch (V5): an empty transcript + a single _R_UNREADABLE."""
        drop = _drop(path, _R_UNREADABLE.format(path=path, error=error))
        return self._build_source(path, "", [drop]), [], [drop]

    # ------------------------------------------------------------------ #
    # The DistillPort entrypoint
    # ------------------------------------------------------------------ #
    def distill(self, sources: list[Source]) -> DistillationResult:
        """Mint claims via ``normalize()`` and merge adapter-drops with normalize-drops.

        Each ``Source`` was produced by ``parse``/``parse_path`` (transcript + carried
        ``extraction``). Units are re-derived from the transcript the SAME deterministic way, so a
        ``Source`` that round-tripped through JSON distills identically on a FRESH adapter (R1).
        Returns truth only — never publishes (HARD RULE).
        """
        all_claims = []
        merged_unextracted: list[Unextracted] = []
        traces: list[Source] = []

        for source in sources:
            # R2 safety-net: a Source this adapter did not produce carries no ``extraction`` record,
            # and its adapter-side drops are NOT reconstructable from the transcript alone. Record an
            # explicit 'coverage-not-reconstructable' marker (forces complete=False) — honest
            # uncertainty over a false complete=True. A Source this adapter parse()d has ``extraction``
            # set (even an empty record), so the marker does NOT fire for our own Sources.
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
        """Re-derive the verbatim units from the transcript + recover the carried drops.

        Units are recovered by splitting on the anchored ``_RECORD_PREFIX`` (a ``<prefix>\\t`` at a
        line start) — NOT on ``\\n``/``\\t``/``:``, because a value (multi-line DAX, a JSON literal)
        may contain those verbatim (faithfulness — values are never escaped). This is the SAME
        serialization rule ``_serialize`` used, so each unit stays an exact substring of
        ``source.transcript`` and ``normalize()`` locates every one. The adapter-side ``unextracted[]``
        (row-cap / no-data-rows / measure-value / unreadable) is NOT reconstructable from the
        transcript, so it is recovered from the typed carrier ``source.extraction`` via the shared
        codec — a round-tripped Source distills with identical coverage on a FRESH adapter (R1).
        """
        units = _split_transcript_units(source.transcript)
        adapter_unx = decode_coverage(source.extraction)
        return units, adapter_unx


# A record prefix is exactly ``<object-path>\t`` at a LINE START. The object path is built from file
# paths + object names; in practice it contains no ``\n`` and no tab (the FIRST tab on the line ends
# the prefix and begins the verbatim value). ``[^\n]*?`` is non-greedy up to the first ``SEP`` on the
# line. A wrapped continuation line of a multi-line value never matches this prefix (it begins with
# the value's own text), so this anchored pattern distinguishes a TRUE record start from a value's
# own continuation — see _split_transcript_units.
_RECORD_PREFIX = re.compile(rf"[^\n]*?{re.escape(SEP)}")


def _split_transcript_units(transcript: str) -> list[str]:
    r"""Recover the ordered verbatim units from a serialized transcript (inverse of ``_serialize``).

    The transcript is the concatenation of ``"<prefix>{SEP}{value}\n"`` records. A value may itself
    contain ``\n``/``\t``/``:`` (faithfulness — never escaped), so we cannot split on those. We split
    on the unambiguous RECORD BOUNDARY: a record starts at a LINE whose prefix matches
    ``<prefix>{SEP}`` (the anchored ``_RECORD_PREFIX`` at a line start). A value's wrapped
    continuation line never matches (it begins with the value's own text), so each unit is exactly
    the text from after its prefix's ``SEP`` up to the ``\n`` that precedes the NEXT record prefix (or
    end of transcript). Each recovered unit is thus a verbatim substring of the transcript, in order.

    Returns ``[]`` for an empty transcript (a whole-source-unreadable / .pbix-deferral Source).
    """
    if not transcript:
        return []
    starts: list[int] = []
    for m in _RECORD_PREFIX.finditer(transcript):
        at_line_start = m.start() == 0 or transcript[m.start() - 1] == "\n"
        if at_line_start:
            starts.append(m.start())
    units: list[str] = []
    for i, start in enumerate(starts):
        match = _RECORD_PREFIX.match(transcript, start)
        assert match is not None  # found via the same pattern
        value_start = match.end()
        next_start = starts[i + 1] if i + 1 < len(starts) else len(transcript)
        value_end = next_start
        if value_end > value_start and transcript[value_end - 1] == "\n":
            value_end -= 1
        units.append(transcript[value_start:value_end])
    return units
