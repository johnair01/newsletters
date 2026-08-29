"""The `.pptx` writer's foundation: the ONE OPC-zip normalizer + the writer's shared constants.

WHY THIS MODULE EXISTS (Phase 2 / WKLY-01, promoting `tests/fixtures/weekly/_determinism.py`).
The Phase 1 determinism spike proved its finding inside `tests/`, which was right for a spike and
wrong for a renderer: the normalizer is the mechanism the *writer* depends on, so leaving it under
`tests/fixtures/weekly/` forced three importers to mutate `sys.path` to reach it (IN-03) and left
the repo one careless copy-paste away from a second implementation of "make this deterministic".
`.planning/notes/2026-08-29-pptx-determinism-decision.md` records the rule this promotion enforces:
**ONE normalizer contract.** A second implementation drifts from the first exactly as a second
epoch sentinel would, and the drift is invisible until a gate that trusted both goes red.

THE FIX. The five public names below moved here VERBATIM — bodies, comments and the explanatory
prose unchanged — so a reviewer can diff the move against the deleted fixture module and see that
nothing was "tidied". Nothing was parameterized either: `date_time` and `create_system` are the
exact axes the promotion exists to pin, so making them arguments would dissolve the contract while
appearing to generalize it.

SCOPE OF THE CLAIM (unchanged by the move). Full-file byte identity holds for a fixed
(python-pptx, zlib) pair; `part_digest` is the implementation-independent, cross-environment
assertion. The paragraphs below state this in full and are the canonical explanation in this repo.

AI-OPTIONAL / BARE-INSTALL DISCIPLINE. Everything at module level here is **stdlib only**
(`hashlib`, `io`, `zipfile`), so `newsletters.pptx_writer` imports on a bare `pip install .` with no
`[pptx]` extra — which is what lets the duplicate-member and idempotence contracts run on the
bare-install CI job. The writer half (plan 02-02) obtains python-pptx **lazily**, inside its render
function, through the existing boundary `newsletters.adapters._pptx_loader._load_pptx()` — it does
not re-implement that boundary and it does not widen it. There must therefore NEVER be a column-0
``import pptx`` / ``from pptx ...`` line in this file. That is not a convention; it is enforced by
`tests/test_ai_optional.py::test_pptx_writer_has_no_toplevel_pptx_import` (column-0 match) and
`tests/test_ai_optional.py::test_pptx_writer_imports_without_pptx` (a real subprocess import with
`pptx` blocked on `sys.meta_path`). This module is deliberately NOT re-exported from
`newsletters/__init__.py`: that module imports its members eagerly, so widening it would widen the
bare-install blast radius for zero benefit (the `adapters` precedent — callers say
``from newsletters.pptx_writer import ...``).

--- the promoted contract, verbatim from the Phase 1 spike ---------------------------------------

WHY this exists. `python-pptx`'s `Presentation.save()` is deterministic in every respect the
ROADMAP worried about — part traversal order, rId allocation, media dedup, core properties — with
exactly ONE exception: `_ZipPkgWriter.write()` calls
``self._zipf.writestr(pack_uri.membername, blob)`` with a **str** arcname
(``pptx/opc/serialized.py:234-242``). When `zipfile` is handed a string rather than a `ZipInfo`, it
manufactures the `ZipInfo` itself and stamps ``date_time=time.localtime()[:6]``. So two saves of
IDENTICAL content, taken more than two seconds apart (DOS timestamps have 2-second granularity),
produce different bytes — while every unzipped part stays byte-identical. There is no python-pptx
API to override the arcname; post-processing the archive is the only API-level route (monkeypatching
the private `_ZipPkgWriter` was considered and rejected: it breaks silently on upgrade).

THE FIX. `normalize_opc_zip` rewrites the package with FIXED zip metadata — every entry gets a fresh
``ZipInfo(filename, date_time=DOS_EPOCH)``, ``compress_type=ZIP_DEFLATED``, ``create_system=0``
(0 = MS-DOS; the stdlib default is platform-dependent, 3 on unix) — while preserving each entry's
``external_attr`` and, deliberately, the **emitted entry order**. Part BYTES are never touched: no
XML is reformatted, no whitespace is normalized, no attribute is reordered. A determinism definition
that normalized XML would be unfalsifiable — a renderer bug that reordered attributes would pass.

WHY PRESERVE ORDER RATHER THAN SORT. python-pptx's emitted order is already deterministic (measured:
identical name order across time-separated writes) and it puts ``[Content_Types].xml`` first *by
construction*, which the OPC convention expects. Sorting happens to keep it first too (``[`` = 0x5B
sorts before ``_`` and all lowercase) — but only incidentally, which would be a second guarantee to
defend for no gain.

SCOPE OF THE BYTE-IDENTITY CLAIM. DEFLATE output is **implementation-dependent**: reproducible-builds
documented Fedora 40 (zlib-ng) and Debian (zlib) emitting different compressed streams — and
different CRCs — for identical input. Full-file byte identity therefore holds for a fixed
(python-pptx, zlib) pair, which is exactly the scope of an in-process double-render assertion. It is
NOT safe to assert across environments. That is what `part_digest` is for: sorted
``(part name, sha256(part bytes))`` rows are implementation-independent and strictly stronger than
"the zips look the same", because they address the CONTENT and ignore the container entirely. A
committed-artifact-vs-fresh-render gate must use `part_digest`; a double-render test may use bytes.

SECURITY PROPERTY (threat T-01-06, zip-slip). The normalizer NEVER joins an archive member name to
the filesystem. It reads with ``ZipFile.read(name)`` and writes with ``ZipFile.writestr(ZipInfo,
data)``, both entirely in memory — no ``open()``, no ``Path`` join, no ``extract``/``extractall``.
A malicious ``../../etc/passwd`` member in an operator-supplied template is carried through as an
opaque *name string* and cannot reach disk through this function. Phase 2 inherits that property by
reusing this module rather than rediscovering it.

DUPLICATE MEMBER NAMES ARE REFUSED, LOUDLY. The ZIP format permits multiple entries under one name,
and ``ZipFile.read(name)`` resolves to the LAST one — so a by-name pass over a shadowed archive
would silently rewrite part bytes (violating the contract above) and two archives with different
first-entry content would share a `part_digest` (a collision in the Phase-4 trust assertion).
Duplicate-name shadowing is a classic archive-smuggling trick precisely because different consumers
pick different entries. python-pptx never emits duplicates, so the only way one arrives is a
hand-crafted or malicious archive — every function here raises ``ValueError`` naming the duplicated
members rather than picking a winner. This mirrors the template contract's duplicate-SHAPE-name
raise: refuse the ambiguity, never resolve it silently.

Stdlib only (``hashlib``, ``io``, ``zipfile``) — this module must NOT import `pptx`, so it stays
importable on a bare install and needs no skip guard. `tests/test_pptx_determinism.py` carries the
`pptx` import behind the standard `pytestmark` skip.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from collections.abc import Iterator, Mapping, Sequence
from typing import Any

__all__ = [
    "DOS_EPOCH",
    "normalize_opc_zip",
    "part_digest",
    "differing_parts",
    "differing_zipinfo_fields",
    "SLOT_PREFIX",
    "WATERMARK_NAME",
    "MARKER",
    "DRAFT_STATUS",
    "WATERMARK_TEXT",
    "bind_slots",
]

# The earliest timestamp the DOS date format used inside a ZIP can represent. Any fixed instant
# would do; 1980-01-01 is the reproducible-builds convention and is unmistakably "not a real time".
DOS_EPOCH = (1980, 1, 1, 0, 0, 0)

# The ZipInfo fields compared by `differing_zipinfo_fields`. `date_time` is the one python-pptx
# leaves unstable; the rest are pinned so a future drift in ANY of them is reported, not hidden.
_COMPARED_FIELDS = (
    "date_time",
    "compress_type",
    "create_system",
    "external_attr",
    "CRC",
)

# --- the template contract's shared strings (decision note: "The template contract") ------------
#
# These are module constants for the same anti-drift reason `_pptx_loader.MISSING_PPTX_MESSAGE` is
# one: the writer, its tests and the fixture authors must assert against ONE spelling of each, not
# against a string literal copied into four files that silently diverge.

# The reserved shape-name prefix: only shapes named `NL_*` are renderer slots, so an operator's
# logo, footer and page number are not mistaken for unfilled slots (decision note, D-03).
SLOT_PREFIX = "NL_"

# The watermark shape's name — owned by the renderer, refused if the template already defines it
# (measured W14: python-pptx writes two shapes with one name and raises nothing).
WATERMARK_NAME = "NL_DRAFT_WATERMARK"

# The generated-by marker, written to `cp:category` (decision note: provenance, NOT authenticity —
# `cp:category` is operator-editable and an unmarked deck proves nothing).
MARKER = "generated-by:newsletters"

# The review-gate state written to `cp:contentStatus` while the Surface is not published (P-04:
# implemented verbatim per the decision note — `"draft"` if not published else `""`).
DRAFT_STATUS = "draft"

# The watermark's text. A fixed literal, like every other watermark property, so the watermark
# contributes nothing to non-determinism.
WATERMARK_TEXT = "DRAFT"


def _reject_duplicate_member_names(archive: zipfile.ZipFile) -> None:
    """Raise ``ValueError`` if the archive shadows any member name (see the module docstring).

    Every by-name read below is only unambiguous because this ran first: ``ZipFile.read(name)``
    silently resolves a duplicated name to its LAST entry, which would rewrite part bytes in
    `normalize_opc_zip` and collide `part_digest` — the two contracts this module exists to keep.
    """
    names = [info.filename for info in archive.infolist()]
    duplicated = sorted({name for name in names if names.count(name) > 1})
    if duplicated:
        raise ValueError(
            f"duplicate member names in archive: {duplicated!r} — ZIP permits shadowed "
            "entries and ZipFile.read(name) silently picks the last one, so a by-name pass "
            "would rewrite part bytes and collide part_digest. Refusing to touch this "
            "archive; if it is an operator-supplied template, rebuild it without duplicate "
            "entries."
        )


def normalize_opc_zip(raw: bytes) -> bytes:
    """Rewrite an OPC package with FIXED zip metadata. Part BYTES are untouched.

    Fully in memory: no member name ever reaches the filesystem (see the module docstring's
    zip-slip note). Idempotent — ``normalize_opc_zip(normalize_opc_zip(x)) == normalize_opc_zip(x)``.
    Raises ``ValueError`` on duplicate member names rather than silently keeping the last entry.
    """
    with zipfile.ZipFile(io.BytesIO(raw)) as zin:
        _reject_duplicate_member_names(zin)
        infos = zin.infolist()
        # preserve the EMITTED entry order — it is already deterministic
        names = [i.filename for i in infos]
        attrs = {i.filename: i.external_attr for i in infos}
        data = {n: zin.read(n) for n in names}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            info = zipfile.ZipInfo(filename=name, date_time=DOS_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            # 0 = MS-DOS; the stdlib default is platform-dependent (3 on unix)
            info.create_system = 0
            info.external_attr = attrs[name]  # preserve python-pptx's value verbatim
            zout.writestr(info, data[name])
    return buf.getvalue()


def part_digest(raw: bytes) -> str:
    """CONTENT identity of an OPC package: sha256 over sorted ``(name, sha256(part bytes))`` rows.

    No zip metadata, no XML normalization. This is the implementation-INDEPENDENT assertion: it is
    unaffected by which zlib built the archive, by entry order, and by every timestamp — while still
    failing loudly if one byte of one part changed. Raises ``ValueError`` on duplicate member
    names: a digest that silently read only the LAST of two shadowed entries would report two
    different-content archives as identical — the exact spoof the Phase-4 trust gate must catch.
    """
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        _reject_duplicate_member_names(archive)
        rows = sorted(
            (name, hashlib.sha256(archive.read(name)).hexdigest())
            for name in archive.namelist()
        )
    digest = hashlib.sha256()
    for name, part in rows:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(part.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def differing_parts(a: bytes, b: bytes) -> list[str]:
    """Sorted names of parts whose unzipped BYTES differ between two packages.

    A name present in only one package is reported too — a part that appeared or vanished is a
    content difference, not a metadata one. Raises ``ValueError`` if either package shadows a
    member name (a by-name comparison over duplicates would compare only the LAST entries).
    """
    with zipfile.ZipFile(io.BytesIO(a)) as za, zipfile.ZipFile(io.BytesIO(b)) as zb:
        _reject_duplicate_member_names(za)
        _reject_duplicate_member_names(zb)
        names_a, names_b = set(za.namelist()), set(zb.namelist())
        differing = set(names_a ^ names_b)
        for name in names_a & names_b:
            if za.read(name) != zb.read(name):
                differing.add(name)
    return sorted(differing)


def differing_zipinfo_fields(a: bytes, b: bytes) -> list[str]:
    """Sorted names of the ZIP METADATA fields that differ between two packages.

    Compares ``date_time``, ``compress_type``, ``create_system``, ``external_attr`` and ``CRC``
    entry by entry, plus ``filename`` order (reported as ``"filename"`` when the emitted entry-name
    sequences differ). Returns ``[]`` when the two archives carry identical metadata — and
    ``["date_time"]`` for a raw python-pptx double write across a DOS-time boundary, which is the
    measured shape of the ONE non-determinism. Raises ``ValueError`` if either package shadows a
    member name (the by-name pairing below is last-wins over duplicates).
    """
    with zipfile.ZipFile(io.BytesIO(a)) as za, zipfile.ZipFile(io.BytesIO(b)) as zb:
        _reject_duplicate_member_names(za)
        _reject_duplicate_member_names(zb)
        infos_a, infos_b = za.infolist(), zb.infolist()
        names_a = [i.filename for i in infos_a]
        names_b = [i.filename for i in infos_b]
        differing: set[str] = set()
        if names_a != names_b:
            differing.add("filename")
        by_name_b = {i.filename: i for i in infos_b}
        for info_a in infos_a:
            info_b = by_name_b.get(info_a.filename)
            if info_b is None:
                continue  # a missing entry is a CONTENT difference — differing_parts reports it
            for field in _COMPARED_FIELDS:
                if getattr(info_a, field) != getattr(info_b, field):
                    differing.add(field)
    return sorted(differing)


# ==================================================================================================
# EVERYTHING ABOVE THIS LINE IS STDLIB AND BARE-IMPORTABLE.
# EVERYTHING BELOW REQUIRES THE OPTIONAL ``[pptx]`` EXTRA **AT CALL TIME** — never at import time.
#
# The functions below take/return python-pptx objects, but they never import `pptx` at column 0.
# The one lazy import per render lives inside `bind_slots` (the `MSO_SHAPE_TYPE` recursion
# predicate); `render_surface_pptx_bytes` obtains the `pptx` module itself through the EXISTING
# boundary `newsletters.adapters._pptx_loader._load_pptx()` rather than re-implementing it. Keep it
# that way: `tests/test_ai_optional.py::test_pptx_writer_imports_without_pptx` imports this module
# in a subprocess with `pptx` blocked on `sys.meta_path`, and it must keep passing.
#
# python-pptx `Presentation` and shape objects are typed `Any` throughout: python-pptx ships no
# stubs and this repo deliberately does not add a `types-*` package (the `_pptx_loader.py`
# precedent). Everything else here is fully annotated.
# ==================================================================================================


def _walk(shapes: Any, group_type: Any) -> Iterator[Any]:
    """Every shape in a shapes collection, DESCENDING into group shapes.

    The recursion is load-bearing, not defensive. `slide.shapes` is **top-level only** (measured,
    02-RESEARCH W17, and re-proved in this repo by
    `tests/test_pptx_writer.py::test_group_nesting_hides_a_slot_from_slide_shapes`): a textbox named
    `NL_INSIDE_GROUP` nested inside a group is simply absent from it. So a flat
    ``{shape.name: shape for shape in slide.shapes}`` comprehension is BLIND to a slot the operator
    can see in their Selection Pane — content bound to that name would be rejected as *unknown*, and
    the unfilled-slot refusal would never fire for it. Grouping boxes is ordinary PowerPoint
    hygiene, so this is not an exotic case.

    `group_type` is `MSO_SHAPE_TYPE.GROUP`, passed in rather than imported here so the predicate is
    MEASURED (an enum comparison) rather than duck-typed, and so there is exactly ONE lazy
    python-pptx import per render — in `bind_slots`, its only caller.
    """
    for shape in shapes:
        yield shape
        if shape.shape_type == group_type:
            yield from _walk(shape.shapes, group_type)


def bind_slots(prs: Any, slots: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    """Map every shape name in the deck to its shape, refusing every ambiguity rather than guessing.

    Binds over ``slide.shapes`` (recursively — see :func:`_walk`) and NOT ``slide.placeholders``:
    the latter holds only real placeholders keyed by ``idx``, and operator-added textboxes and
    pictures are absent from it entirely (decision note, "The template contract").

    Five refusals, in this order, each a ``ValueError`` in the house three-part teaching voice —
    what was found, why it cannot be resolved silently, what the operator does next:

    1. a **duplicate shape name** (legal in OOXML; copy-paste is how an operator makes one — a
       last-wins map would silently DROP a slot, the exact failure D-03 exists to prevent);
    2. the template already defining **WATERMARK_NAME** (the renderer owns that name and adds the
       watermark itself; leaving it in the template writes two shapes under one name — measured,
       W14, with no error — and defeats this map on the next render);
    3. an **unknown content name** — content bound to a name the template does not contain;
    4. an **unfilled reserved slot** — an ``NL_``-prefixed shape with no matching content (a
       reserved-prefix slot left empty would ship a blank box to a reader). The ``NL_`` prefix is
       what keeps this direction usable on a real deck: without it every operator logo, footer and
       page number would be rejected;
    5. a **slot that cannot hold text** — a group or a picture reports ``has_text_frame == False``,
       so filling it would raise ``AttributeError``: a stack trace instead of a teaching error.

    Returns the name→shape map. Mutates nothing.
    """
    # Lazy on purpose: `pptx` is the optional [pptx] extra and this module must stay importable on
    # a bare install (see the banner above). One import per render, here, for `_walk`'s predicate.
    from pptx.enum.shapes import MSO_SHAPE_TYPE  # type: ignore[import-untyped]  # noqa: PLC0415

    by_name: dict[str, Any] = {}
    for slide in prs.slides:
        for shape in _walk(slide.shapes, MSO_SHAPE_TYPE.GROUP):
            if shape.name in by_name:
                raise ValueError(
                    f"template has two shapes named {shape.name!r} — the name->shape binding is "
                    "ambiguous. Duplicate shape names are legal in OOXML and copy-pasting a box in "
                    "PowerPoint is how one is made, so a last-wins map would silently DROP a slot. "
                    "Rename one in PowerPoint's Selection Pane (Alt+F10). Refusing to guess which "
                    "slot the content belongs in."
                )
            by_name[shape.name] = shape

    if WATERMARK_NAME in by_name:
        raise ValueError(
            f"the template already defines {WATERMARK_NAME!r}. That name is owned by the renderer, "
            "which adds the Draft watermark itself; leaving it in the template would produce two "
            "shapes with one name (measured: python-pptx writes both and raises nothing) and would "
            "defeat the name->shape binding on the next render. Remove it from the template."
        )

    unknown = sorted(set(slots) - set(by_name))
    if unknown:
        raise ValueError(
            f"Surface content is bound to placeholder name(s) {unknown!r} that this template does "
            f"not contain. Named shapes in this template: {sorted(by_name)!r}. The renderer never "
            "invents layout — add the shape to the template (name it in the Selection Pane, "
            "Alt+F10) or fix the name in the content mapping."
        )

    unfilled = sorted(
        name for name in by_name if name.startswith(SLOT_PREFIX) and name not in slots
    )
    if unfilled:
        raise ValueError(
            f"template placeholder(s) {unfilled!r} have no matching Surface content. A "
            f"{SLOT_PREFIX!r}-prefixed slot left empty would ship a blank box to a reader — "
            "refusing. Either populate it or remove the reserved prefix from the shape's name "
            "(unprefixed shapes are the operator's: logos, footers, page numbers are never slots)."
        )

    for name in slots:
        shape = by_name[name]
        if not getattr(shape, "has_text_frame", False):
            raise ValueError(
                f"slot {name!r} is a {shape.shape_type} and cannot hold text (measured: group and "
                "picture shapes report has_text_frame == False, so filling one raises "
                "AttributeError rather than anything a reader of the traceback could act on). "
                "Point the slot at a text box, or place this content as an asset."
            )

    return by_name
