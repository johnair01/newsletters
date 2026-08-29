"""WKLY-04 — BI values reach a composed weekly through the EXISTING ADAPT-03 excel adapter.

THE CONTRACT THIS MODULE PROVES. A weekly that needs numbers does not get a new ingestion path:
the operator exports the BI view to a workbook, and that ``.xlsx`` goes through the adapter this
repo already has (``newsletters.adapters.excel_adapter``, registered as ``"excel"``) — parse into a
content-addressed ``Source``, distill into span-traced ``Claim``s, carry those claims into the
weekly on a ``swimlane.SectionBinding``, and let the composer's existing trust predicate
(``compose.addressed``) decide which of them may reach a reviewed block. **No new adapter module
exists**, ADAPT-05's Power BI *definition* reader stays exactly what it was — a definition-side
reader, byte-unchanged — and the weekly loader never learns to parse a workbook. Those three
absences are asserted here as structural guards, because "we did not add one" is a claim like any
other and deserves evidence rather than a promise.

THE ``.csv`` WORDING, CLARIFIED (v1.3 Phase 3, recorded not reopened). The milestone's prose says
values arrive "as a `.csv`/`.xlsx` export". The live ADAPT-03 adapter is ``.xlsx``-ONLY: a CSV path
would need a new adapter module, which is precisely what WKLY-04 forbids. So the clarification is a
wording fix and not a scope cut — values enter as ``.xlsx`` exports, and nobody should read the old
sentence as authorising a CSV reader.

FIXTURE POLICY, copied from ``tests/test_excel_adapter.py`` (its stated policy, followed exactly):
tiny workbooks authored **programmatically** with openpyxl and serialized through ``io.BytesIO`` —
never a committed binary. The workbook is the thing under test's *input*, not a golden artifact.

``importorskip`` ALONE IS NOT PROOF. Without the ``[excel]`` extra this module skips itself, and a
module that skips itself in every CI run is green because it never ran (v1.3 W21, already paid for
once in this repo). The durable half is the ``weekly`` job in ``.github/workflows/ci.yml``, which
installs ``[excel]``, names this module, and fails if the run reports any skip at all.
"""

from __future__ import annotations

import io
import pathlib
import subprocess

import pytest

openpyxl = pytest.importorskip("openpyxl")  # skip cleanly without the [excel] extra

from newsletters.adapters.excel_adapter import SEP  # noqa: E402
from newsletters.compose import addressed, compute_delta  # noqa: E402
from newsletters.distill import available, resolve  # noqa: E402
from newsletters.distill.faithfulness import SpanContainmentFaithfulness  # noqa: E402
from newsletters.semantic import Claim, KpiItem, Trace  # noqa: E402
from newsletters.swimlane import SectionBinding  # noqa: E402
from newsletters.weeklyspec import build_weekly_report, load_weekly_spec  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "weekly"
FULL = "weekly-full.yml"
AUTHOR = "author-x"

# The exported view, authored in-test. Fabricated, Star-Trek-flavored, LANE-03-safe: a generic
# sheet with a labelled measure and two period endpoints — the smallest workbook that can carry a
# KPI with a real, derivable delta.
SHEET = "Bay Cycle"
MEASURE = "Bay turnaround minutes"
PERIOD_START = "41"
PERIOD_CLOSE = "29"
EXPORT_PATH = "exports/bay-cycle-export.xlsx"

_GATE = SpanContainmentFaithfulness()


# --------------------------------------------------------------------------- #
# The export: a tiny workbook, authored in memory, never committed
# --------------------------------------------------------------------------- #


def _export_bytes() -> bytes:
    """Author the exported BI view as ``.xlsx`` bytes (the operator's export, in miniature)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = SHEET
    ws["A1"] = MEASURE
    ws["B1"] = PERIOD_START
    ws["C1"] = PERIOD_CLOSE
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _distilled():
    """Drive the REGISTERED backend end to end: parse -> distill. Returns (source, claims)."""
    adapter = resolve("excel")  # the registry's backend, never a hand-constructed adapter
    source, _units, drops = adapter.parse(_export_bytes(), EXPORT_PATH)
    assert drops == [], f"the synthetic export should extract cleanly; dropped: {drops}"
    result = adapter.distill([source])
    return source, list(result.distillation.claims)


def _claim_for(claims: list[Claim], text: str) -> Claim:
    for claim in claims:
        if claim.text == text:
            return claim
    raise AssertionError(f"no claim carries {text!r}; got {[c.text for c in claims]}")


def _binding(claims: list[Claim]) -> SectionBinding:
    """Carry the exported claims into the weekly on the seam the composer already consumes.

    ``kpi_endpoints[0]`` holds the two INDEPENDENTLY content-addressed endpoint claims, in file
    order (start before close), so the composer derives the delta from two traced cells rather
    than from a text match or a guess — the ``SectionBinding`` contract, unchanged.
    """
    return SectionBinding(
        heading=MEASURE,
        kpi_items=[KpiItem(label=MEASURE, value=PERIOD_CLOSE)],
        kpi_endpoints=[
            [_claim_for(claims, PERIOD_START), _claim_for(claims, PERIOD_CLOSE)]
        ],
        claims=list(claims),
    )


def _weekly(bindings) -> object:
    load = load_weekly_spec(FIXTURE_DIR / FULL, root=REPO_ROOT)
    return build_weekly_report(load, author=AUTHOR, bindings=list(bindings))


def _blocks_of(surface, kind: str) -> list:
    return [b for b in surface.blocks if b.kind == kind]


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
    )


# --------------------------------------------------------------------------- #
# 1 — the export path: the EXISTING adapter, its canonical transcript, traced claims
# --------------------------------------------------------------------------- #


def test_the_excel_backend_under_test_is_the_registered_one() -> None:
    """WKLY-04's first word is "existing": the test drives the registry, not a private class."""
    assert "excel" in available(), available()
    assert resolve("excel").name == "excel"


def test_exported_workbook_becomes_the_adapters_canonical_transcript() -> None:
    """The transcript is the adapter's own ``Sheet!A1<SEP>value`` shape, one line per cell.

    Asserted on the shape rather than on a frozen blob, so the test tracks the adapter's
    contract instead of freezing a magic string.
    """
    source, _claims = _distilled()
    lines = source.transcript.splitlines()
    assert lines == [
        f"{SHEET}!A1{SEP}{MEASURE}",
        f"{SHEET}!B1{SEP}{PERIOD_START}",
        f"{SHEET}!C1{SEP}{PERIOD_CLOSE}",
    ], source.transcript
    assert source.id == EXPORT_PATH


def test_every_exported_value_is_a_traced_content_addressed_claim() -> None:
    """Each cell VALUE becomes a claim standing on its own span of the export's transcript.

    Note the shape carefully: the claim's TEXT is the cell value, and the ``Sheet!A1<SEP>``
    prefix is what separates adjacent values in the transcript so that two cells carrying the
    same number still get distinct, ordered, locatable spans. Re-slicing the live transcript at
    the trace's own offsets is the assertion that this is a real address and not a decoration.
    """
    source, claims = _distilled()
    assert [claim.text for claim in claims] == [MEASURE, PERIOD_START, PERIOD_CLOSE]
    for claim in claims:
        assert claim.is_traced, claim
        assert addressed(claim), f"{claim.text!r} is not content-addressed"
        assert _GATE.entails(claim), f"{claim.text!r} fails the LIVE faithfulness gate"
        for trace in claim.evidence:
            assert trace.source_id == source.id
            assert source.transcript[trace.start : trace.end] == claim.text


def test_two_parses_of_one_export_are_identical() -> None:
    """Determinism at the seam: the same export bytes distill to the same record, twice."""
    first_source, first_claims = _distilled()
    second_source, second_claims = _distilled()
    assert first_source.model_dump_json() == second_source.model_dump_json()
    assert [c.model_dump_json() for c in first_claims] == [
        c.model_dump_json() for c in second_claims
    ]


# --------------------------------------------------------------------------- #
# 2 — the values reach the weekly: KPI strip + claims block
# --------------------------------------------------------------------------- #


def test_exported_values_reach_the_weekly_kpi_strip_with_a_derived_delta() -> None:
    """SC-4: an exported workbook's cells become the weekly's KPI strip.

    The delta is not authored anywhere — it is derived by ``compose.compute_delta`` from the two
    traced endpoint cells, which is why the strip can be trusted: both ends of the comparison are
    addresses into the export, not numbers somebody typed into a weekly.
    """
    _source, claims = _distilled()
    surface = _weekly([_binding(claims)])

    strips = _blocks_of(surface, "kpi")
    assert len(strips) == 1, [b.kind for b in surface.blocks]
    assert strips[0].heading == MEASURE
    item = strips[0].items[0]
    assert item.label == MEASURE
    assert item.value == PERIOD_CLOSE
    expected_delta, expected_dir = compute_delta(PERIOD_START, PERIOD_CLOSE)
    assert (item.delta, item.dir) == (expected_delta, expected_dir)
    assert item.delta is not None, "the two traced endpoints must yield a delta"


def test_exported_claims_reach_the_weekly_claims_block_still_addressed() -> None:
    """Every exported claim that reaches a reviewed block is still traced and content-addressed."""
    _source, claims = _distilled()
    surface = _weekly([_binding(claims)])

    blocks = _blocks_of(surface, "claims")
    assert len(blocks) == 1, [b.kind for b in surface.blocks]
    kept = blocks[0].claims
    assert {c.text for c in kept} == {MEASURE, PERIOD_START, PERIOD_CLOSE}
    for claim in kept:
        assert addressed(claim), f"{claim.text!r} reached a block un-addressed"
        assert _GATE.entails(claim), f"{claim.text!r} reached a block un-entailed"
    # The weekly is still a Draft that has never touched the gate.
    assert not surface.is_published


def test_untraced_and_unaddressed_claims_never_reach_the_weekly() -> None:
    """NON-VACUITY: the trust predicate is doing work, not waving everything through.

    Two planted cheats on the SAME binding as the real export: one with no evidence at all, one
    whose trace names a source but addresses no content. Neither may reach a block, and both must
    be disclosed by text in the honesty panel — a filter that drops a claim silently is worse
    than one that lets it through, because nobody can see what was removed.
    """
    _source, claims = _distilled()
    binding = _binding(claims)
    untraced = Claim(text="planted untraced value never exported")
    unaddressed = Claim(
        text="planted value on an un-addressed trace",
        evidence=[Trace(source_id=EXPORT_PATH)],
    )
    assert not addressed(untraced) and not addressed(unaddressed)
    binding.claims.extend([untraced, unaddressed])

    surface = _weekly([binding])

    kept = {c.text for c in _blocks_of(surface, "claims")[0].claims}
    assert untraced.text not in kept, "an untraced claim leaked onto a weekly block"
    assert unaddressed.text not in kept, "an un-addressed claim leaked onto a weekly block"
    assert untraced.text in surface.missing
    assert unaddressed.text in surface.missing
    # ...and the real exported values are still there, so the filter is discriminating.
    assert {MEASURE, PERIOD_START, PERIOD_CLOSE} <= kept


# --------------------------------------------------------------------------- #
# 3 — the three structural guards: what WKLY-04 forbids, asserted rather than promised
#
# Each resolves the milestone base through the SHARED ``milestone_base_ref`` fixture
# (tests/conftest.py), which FAILS — never skips — when the ref cannot be resolved and names
# `fetch-depth: 0` as the fix. `git diff HEAD` would compare the WORKING TREE to the last commit:
# red on an uncommitted edit, green the instant it is committed, and therefore never capable of
# failing in CI's clean checkout. That bug shipped once here already.
# --------------------------------------------------------------------------- #


def test_the_adapters_directory_gained_no_file(milestone_base_ref: str) -> None:
    """WKLY-04: values arrive through the EXISTING adapter — so no adapter file may change."""
    result = _git(
        "diff",
        "--name-only",
        milestone_base_ref,
        "--",
        "src/newsletters/adapters/",
    )
    assert result.returncode == 0, result.stderr
    changed = [line for line in result.stdout.splitlines() if line.strip()]
    assert changed == [], (
        "the adapters directory changed against the milestone base — WKLY-04 routes BI values "
        f"through the EXISTING ADAPT-03 adapter and adds no ingestion path: {changed}"
    )


def test_the_powerbi_definition_reader_is_byte_unchanged(
    milestone_base_ref: str,
) -> None:
    """ADAPT-05 stays the DEFINITION-side reader it is; the value side came via an export.

    Named file by file rather than by directory, because this is the specific promise the
    milestone made: the Power BI reader was not quietly extended while nobody looked.
    """
    result = _git(
        "diff",
        "--exit-code",
        milestone_base_ref,
        "--",
        "src/newsletters/adapters/powerbi_adapter.py",
        "src/newsletters/adapters/_tmdl.py",
        "src/newsletters/adapters/_pbir.py",
    )
    assert result.returncode == 0, (
        "ADAPT-05's Power BI reader changed against the milestone base. The value-side extension "
        f"is a DEFERRED item, not this milestone's:\n{result.stdout}"
    )


def test_the_weekly_loader_never_parses_a_workbook() -> None:
    """The values path goes through the adapter, not through the loader.

    A ``load_workbook`` inside ``weeklyspec.py`` would be a second ingestion implementation with
    none of the adapter's coverage discipline — and it would import openpyxl into the authoring
    path, which must stay runnable without the ``[excel]`` extra.
    """
    source = (REPO_ROOT / "src" / "newsletters" / "weeklyspec.py").read_text(
        encoding="utf-8"
    )
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )
    for token in ("openpyxl", "xlsx", "load_workbook"):
        assert token not in code.lower(), (
            f"{token!r} appears in weeklyspec.py — the weekly loader must reach BI values "
            "through the registered excel backend, never by parsing a workbook itself"
        )
