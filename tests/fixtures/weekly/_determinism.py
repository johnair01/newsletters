"""The ONE OPC-zip normalizer + content-digest contract for the `.pptx` determinism spike.

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

Stdlib only (``hashlib``, ``io``, ``zipfile``) — this module must NOT import `pptx`, so it stays
importable on a bare install and needs no skip guard. `tests/test_pptx_determinism.py` carries the
`pptx` import behind the standard `pytestmark` skip.
"""

from __future__ import annotations

import hashlib
import io
import zipfile

__all__ = [
    "DOS_EPOCH",
    "normalize_opc_zip",
    "part_digest",
    "differing_parts",
    "differing_zipinfo_fields",
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


def normalize_opc_zip(raw: bytes) -> bytes:
    """Rewrite an OPC package with FIXED zip metadata. Part BYTES are untouched.

    Fully in memory: no member name ever reaches the filesystem (see the module docstring's
    zip-slip note). Idempotent — ``normalize_opc_zip(normalize_opc_zip(x)) == normalize_opc_zip(x)``.
    """
    with zipfile.ZipFile(io.BytesIO(raw)) as zin:
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
    failing loudly if one byte of one part changed.
    """
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
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
    content difference, not a metadata one.
    """
    with zipfile.ZipFile(io.BytesIO(a)) as za, zipfile.ZipFile(io.BytesIO(b)) as zb:
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
    measured shape of the ONE non-determinism.
    """
    with zipfile.ZipFile(io.BytesIO(a)) as za, zipfile.ZipFile(io.BytesIO(b)) as zb:
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
