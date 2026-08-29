"""The `.pptx` determinism spike, as a durable test (ROADMAP Phase-1 criterion 2; de-risks WKLY-01).

THE DECISION THIS MODULE ENFORCES: `.planning/notes/2026-08-29-pptx-determinism-decision.md`
(BYTE-STABLE via a declared post-save zip normalization, scoped to a fixed (python-pptx, zlib)
pair; `part_digest` is the implementation-independent committed==fresh assertion). Its measured
evidence is `.planning/notes/2026-08-29-pptx-determinism-evidence.json`.

A determinism decision without evidence is a vibe, and a determinism decision whose evidence ran
once in a scratch shell is a vibe with a longer half-life. This module is the spike made
reproducible: it performs a REAL python-pptx double write, separated by a real 3-second gap, on
every run, and asserts the three load-bearing properties the recorded decision rests on.

**(A) Part-content digest equality** — `part_digest(a) == part_digest(b)` on the UN-normalized
bytes. Sorted ``(part name, sha256(part bytes))`` rows are implementation-INDEPENDENT: they ignore
zip metadata entirely and are unaffected by which zlib built the archive. This is the assertion the
Phase 4 committed==fresh gate must use, because a committed artifact and a CI re-render may cross
zlib implementations (01-RESEARCH §Pitfall 1) — a full-file hash there would be green locally and
red in CI with byte-identical part content.

**(B) Full-file byte equality after `normalize_opc_zip`** — the recorded determinism definition.
Scoped, honestly, to a fixed (python-pptx, zlib) pair, which is exactly the scope of an in-process
double render. Neither this assertion nor (A) normalizes any XML: a definition that reformatted
whitespace or reordered attributes would be unfalsifiable, since a renderer bug that reordered
attributes would pass it.

**(C) The negative control** — an un-normalized double write across a DOS-time boundary is asserted
to be NOT byte-equal, while all its unzipped parts ARE byte-identical and the ONLY differing zip
metadata field is ``date_time``. Without (C), `render() == render()` passes trivially whenever both
writes land in the same wall-clock second — measured, they do (01-RESEARCH E2: two same-second
writes were byte-identical at 28,265 B). That is a green test proving nothing. (C) is what makes the
green in (B) attributable to the normalizer rather than to luck, and it is what makes the whole
determinism claim falsifiable.

**The 3-second sleep is load-bearing.** DOS timestamps inside a ZIP have 2-second granularity, so a
1-second gap is not guaranteed to cross a representable boundary. Three seconds is. The suite sleeps
ONCE (module-scoped fixture) and shares the two payloads across all assertions.

`_render_bytes` is the Phase 2 writer in miniature — open the template, fill the `NL_`-named shapes,
pin the marker + gate core properties + `EPOCH_ZERO` timestamps, save to `BytesIO`. It lives in
`tests/` deliberately and NEVER in `src/`: this phase produces measurement, not production surface
(ROADMAP criterion 5). The `pptx` import sits behind `pytest.importorskip`, the only sanctioned way
for `tests/` to touch the optional extra at module scope — that is what keeps the bare-install CI
gate green. A `pytestmark` skipif can NOT guard a module-level import: the marker is evaluated per
collected test item, AFTER pytest has already imported the module, so a bare install would error at
collection instead of skipping (the sibling pptx tests all use `importorskip` or lazy in-function
imports for exactly this reason).
"""

from __future__ import annotations

import io
import pathlib
import sys
import time
import zipfile

import pytest

# `importorskip` raises Skipped at module level, which pytest converts into a module skip — so a
# bare install (no [pptx] extra) SKIPS this file instead of erroring at collection. Same pattern
# as tests/test_pptx_loader.py.
pptx = pytest.importorskip(
    "pptx", reason="optional [pptx] extra (python-pptx) not installed"
)
Presentation = pptx.Presentation

from newsletters.adapters._timestamps import EPOCH_ZERO  # noqa: E402

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "weekly"
TEMPLATE = FIXTURE_DIR / "template.pptx"

sys.path.insert(0, str(FIXTURE_DIR))

from _determinism import (  # noqa: E402
    differing_parts,
    differing_zipinfo_fields,
    normalize_opc_zip,
    part_digest,
)

# The generated-by marker and the review-gate state, carried in OPC core properties (0 extra parts,
# survives a PowerPoint round-trip). The exact strings are Phase 2's to ratify; what THIS module
# proves is that both round-trip through a real write and read back off the written file.
MARKER = "generated-by:newsletters"
GATE_STATE = "draft"

# The renderer slots the fabricated template carries. `Footer` is deliberately NOT here: it has no
# `NL_` prefix, so it is a decorative shape, not a slot.
SLOT_NAMES = ("NL_WEEK_TITLE", "NL_MODULE", "NL_HIGHLIGHTS", "NL_LOWLIGHTS")
ALL_SHAPE_NAMES = sorted(SLOT_NAMES + ("Footer",))


def _render_bytes(title: str) -> bytes:
    """The Phase 2 writer in miniature: fill the named slots, pin the marker, save to memory.

    Binds over ``slide.shapes`` and NOT ``slide.placeholders`` — the template's slots are operator
    textboxes, which are absent from the placeholders collection entirely (01-RESEARCH
    §Anti-Patterns). Every value written here is a fixed literal or an argument: no clock, no
    randomness. The ONLY non-determinism in the whole function enters at ``prs.save()``.
    """
    prs = Presentation(str(TEMPLATE))
    slide = prs.slides[0]

    content = {
        "NL_WEEK_TITLE": title,
        "NL_MODULE": "module-a",
        "NL_HIGHLIGHTS": "shipped the thing",
        "NL_LOWLIGHTS": "the other thing slipped",
    }
    by_name = {shape.name: shape for shape in slide.shapes}
    for name, text in content.items():
        by_name[name].text_frame.text = text

    cp = prs.core_properties
    cp.category = MARKER
    cp.content_status = GATE_STATE
    # EPOCH_ZERO is tz-AWARE UTC; `dcterms:created` reads back tz-NAIVE (01-RESEARCH §Pitfall 5),
    # so the sentinel is stripped of its tzinfo here and compared the same way on read-back. One
    # epoch sentinel for the whole repo — never mint a second.
    cp.created = EPOCH_ZERO.replace(tzinfo=None)
    cp.modified = EPOCH_ZERO.replace(tzinfo=None)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


@pytest.fixture(scope="module")
def time_separated_writes() -> tuple[bytes, bytes]:
    """Two REAL writes of identical content, separated by a real 3-second gap.

    Module-scoped so the suite sleeps once, not once per assertion.
    """
    raw_a = _render_bytes("2026-W35")
    # DOS timestamps have 2-SECOND granularity, so 3 seconds guarantees the boundary is crossed.
    # A shorter gap is the false-green trap: two same-second writes are already byte-identical.
    time.sleep(3)
    raw_b = _render_bytes("2026-W35")
    return raw_a, raw_b


def test_unnormalized_double_write_differs_only_in_zip_date_time(
    time_separated_writes: tuple[bytes, bytes],
) -> None:
    """(C) THE NEGATIVE CONTROL — the determinism assertion must be able to FAIL.

    Un-normalized, across a DOS-time boundary: the raw bytes differ, every unzipped part is
    byte-identical, and ``date_time`` is the ONLY differing zip metadata field. This is the measured
    shape of python-pptx's single non-determinism, re-proved on every run.
    """
    raw_a, raw_b = time_separated_writes

    assert raw_a != raw_b, (
        "the negative control has stopped controlling: two un-normalized writes "
        "3s apart are byte-equal. Either the writes landed inside one DOS "
        "timestamp tick, or python-pptx stopped stamping the clock. Until this inequality "
        "holds, the byte-equality result in test_normalized_double_write_is_byte_identical "
        "is NOT attributable to the normalizer and proves nothing."
    )
    assert differing_parts(raw_a, raw_b) == [], (
        "unzipped part CONTENT differs across two writes of identical input — that is a real "
        "non-determinism in the writer (a clock, an unstable part order, or an unstable rel id), "
        "not a zip-metadata artefact the normalizer can fix"
    )
    assert differing_zipinfo_fields(raw_a, raw_b) == ["date_time"], (
        "a zip metadata field other than date_time drifted across two writes; the normalizer "
        "pins date_time, compress_type, create_system and external_attr, so a new offender here "
        "means the recorded determinism mechanism is incomplete"
    )


def test_normalized_double_write_is_byte_identical(
    time_separated_writes: tuple[bytes, bytes],
) -> None:
    """(B) THE RECORDED DEFINITION — byte-identical after `normalize_opc_zip`.

    Scoped to a fixed (python-pptx, zlib) pair, which an in-process double render satisfies by
    construction. The negative control above is what makes this green meaningful.
    """
    raw_a, raw_b = time_separated_writes

    assert normalize_opc_zip(raw_a) == normalize_opc_zip(raw_b), (
        "two normalized writes of identical content are NOT byte-identical — the recorded "
        "determinism definition (byte-stable via post-save zip normalization) does not hold on "
        "this python-pptx/zlib pair"
    )


def test_part_digest_is_stable_across_time_separated_writes(
    time_separated_writes: tuple[bytes, bytes],
) -> None:
    """(A) CONTENT IDENTITY — implementation-independent, asserted on the UN-normalized bytes.

    Deliberately not normalized first: the point is that content identity holds WITHOUT any zip
    metadata fix, which is why the Phase 4 committed==fresh gate can use this digest across
    machines whose zlib implementations differ.
    """
    raw_a, raw_b = time_separated_writes

    assert part_digest(raw_a) == part_digest(raw_b), (
        "the part-content digest differs across two writes of identical content — the deck's "
        "CONTENT is non-deterministic, which no zip normalization can repair"
    )


def test_normalized_archive_is_valid_and_reopens_with_marker_intact(
    time_separated_writes: tuple[bytes, bytes],
) -> None:
    """The read-back assertion: assert from the WRITTEN FILE, never the writer's return value.

    Covers idempotence, archive integrity, the OPC ``[Content_Types].xml``-first convention, and
    that the marker / gate state / pinned timestamps / shape names all survive a real round trip.
    """
    raw_a, _raw_b = time_separated_writes
    normalized = normalize_opc_zip(raw_a)

    assert normalize_opc_zip(normalized) == normalized, (
        "normalize_opc_zip is not idempotent — normalizing an already-normalized package must be "
        "a no-op, or a second pass anywhere in the pipeline would change the bytes"
    )

    corrupt = "the normalized archive fails its own CRC check — normalization broke it"
    with zipfile.ZipFile(io.BytesIO(normalized)) as archive:
        assert archive.testzip() is None, corrupt
        names = archive.namelist()
    assert names[0] == "[Content_Types].xml", (
        "[Content_Types].xml is no longer the first entry; the OPC convention expects it there, "
        f"and preserving the emitted order is supposed to keep it there by construction. Got: "
        f"{names[0]!r}"
    )

    written = Presentation(io.BytesIO(normalized))  # reopen the WRITTEN bytes
    cp = written.core_properties
    assert cp.category == MARKER, cp.category
    assert cp.content_status == GATE_STATE, cp.content_status
    # dcterms:created serializes as W3CDTF and reads back tz-NAIVE (01-RESEARCH §Pitfall 5).
    assert cp.created == EPOCH_ZERO.replace(tzinfo=None), cp.created
    assert cp.modified == EPOCH_ZERO.replace(tzinfo=None), cp.modified

    read_back = sorted(shape.name for shape in written.slides[0].shapes)
    lost = f"named shapes did not survive the write/normalize round trip: {read_back}"
    assert read_back == ALL_SHAPE_NAMES, lost


def test_weekly_fixture_corpus_is_exactly_the_committed_template() -> None:
    """The weekly fixture corpus is exactly one committed deck — no stray spike artefact.

    Mirrors the golden corpus guard: a corpus that silently grew (an exploratory deck left behind)
    or shrank (the template deleted) is a failure. CONTEXT is explicit that spike scratch code is
    deleted or lands as a fixture; this is the executable form of that rule.
    """
    on_disk = sorted(p.name for p in FIXTURE_DIR.glob("*.pptx"))
    assert on_disk == ["template.pptx"], on_disk
    assert TEMPLATE.is_file()
