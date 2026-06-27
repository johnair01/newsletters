"""Unit coverage for the shared faithful ``normalize()`` (ADAPT-01, Phase 4 Plan 01).

``normalize()`` is the ONE place the faithful-extraction rule lives: it mints a typed
``Claim(+Trace)`` for every raw "unit" it can locate VERBATIM in ``Source.transcript`` via a
cursor-advancing ``str.find``, content-addressing each trace through ``Trace.from_source``.
Anything not verbatim-locatable is routed to a returned ``unextracted[]`` list — never
fabricated, never paraphrased ("faithful, not suggestive").

These tests exercise every behavior in the plan's ``<behavior>`` block plus the gate-survival
property that makes the phase work: normalize's output must PASS the Phase-3
``SpanContainmentFaithfulness`` gate it will be held to downstream.
"""

from __future__ import annotations

from newsletters.adapters import normalize
from newsletters.distill.coverage import Coverage, Unextracted
from newsletters.distill.faithfulness import SpanContainmentFaithfulness
from newsletters.locators import FreeLocator
from newsletters.semantic import Claim, Source


# --------------------------------------------------------------------------- #
# Happy path — N units -> N claims, 0 unextracted; claim.text == unit == span
# --------------------------------------------------------------------------- #


def test_happy_path_two_units_two_claims() -> None:
    source = Source(id="x", transcript="Hello.\n\nWorld.")
    claims, unextracted = normalize(source, ["Hello.", "World."])

    assert len(claims) == 2
    assert unextracted == []
    assert [c.text for c in claims] == ["Hello.", "World."]
    for claim in claims:
        trace = claim.evidence[0]
        # claim.text == the located span == the re-slice of the transcript
        assert claim.text == trace.span
        assert source.transcript[trace.start : trace.end] == claim.text
        assert trace.is_addressed is True


def test_happy_path_offsets_are_the_real_positions() -> None:
    source = Source(id="x", transcript="Hello.\n\nWorld.")
    claims, _ = normalize(source, ["Hello.", "World."])

    # "Hello." at 0..6; "World." after the "\n\n" separator at 8..14.
    assert (claims[0].evidence[0].start, claims[0].evidence[0].end) == (0, 6)
    assert (claims[1].evidence[0].start, claims[1].evidence[0].end) == (8, 14)


# --------------------------------------------------------------------------- #
# Duplicate disambiguation — the advancing cursor gives DISTINCT offsets
# --------------------------------------------------------------------------- #


def test_duplicate_units_resolve_to_distinct_offsets() -> None:
    source = Source(id="x", transcript="ab\n\nab")
    claims, unextracted = normalize(source, ["ab", "ab"])

    assert len(claims) == 2
    assert unextracted == []
    # The cursor advances past the first occurrence, so the SECOND "ab" resolves to the
    # later occurrence (start 4), not back to start 0 — correct per-claim provenance.
    assert claims[0].evidence[0].start == 0
    assert claims[1].evidence[0].start == 4
    assert claims[0].evidence[0].start != claims[1].evidence[0].start


# --------------------------------------------------------------------------- #
# Non-locatable routing — never fabricate, route to unextracted[] with a CONTENT anchor
# --------------------------------------------------------------------------- #


def test_unit_not_present_routes_to_unextracted() -> None:
    source = Source(id="x", transcript="Hello world.")
    claims, unextracted = normalize(source, ["Goodbye."])

    assert claims == []
    assert len(unextracted) == 1
    entry = unextracted[0]
    assert isinstance(entry, Unextracted)
    assert "not verbatim-locatable" in entry.reason
    # Locator is a CONTENT anchor (FreeLocator with a preview), NEVER an ordinal index.
    assert isinstance(entry.locator, FreeLocator)
    assert entry.locator.text  # carries a preview of the unit
    assert "Goodbye." in entry.locator.text


def test_unit_already_consumed_before_cursor_routes_to_unextracted() -> None:
    # "ab" appears once; asking for it twice with only one occurrence means the second
    # find (from the advanced cursor) returns -1 -> unextracted, never re-pointed at the first.
    source = Source(id="x", transcript="ab")
    claims, unextracted = normalize(source, ["ab", "ab"])

    assert len(claims) == 1
    assert claims[0].evidence[0].start == 0
    assert len(unextracted) == 1
    assert "not verbatim-locatable" in unextracted[0].reason


def test_unextracted_locator_preview_is_truncated() -> None:
    long_unit = "Z" * 200  # not in transcript, longer than the 60-char preview
    source = Source(id="x", transcript="nothing here")
    _, unextracted = normalize(source, [long_unit])

    assert len(unextracted) == 1
    # Preview is a truncated content anchor, not the full (possibly huge) unit.
    assert len(unextracted[0].locator.text) <= 60


# --------------------------------------------------------------------------- #
# Content-addressing — every emitted trace came through Trace.from_source
# --------------------------------------------------------------------------- #


def test_every_trace_is_content_addressed() -> None:
    source = Source(id="x", transcript="alpha\n\nbeta\n\ngamma")
    claims, _ = normalize(source, ["alpha", "beta", "gamma"])

    assert len(claims) == 3
    for claim in claims:
        trace = claim.evidence[0]
        assert trace.is_addressed is True
        assert trace.content_hash == source.content_hash()
        # re-slice identity: the stored span is re-checkable against the live source window
        assert source.transcript[trace.start : trace.end] == claim.text
        assert claim.text == trace.span


# --------------------------------------------------------------------------- #
# Gate survival — normalize's output PASSES the Phase-3 span-containment gate
# --------------------------------------------------------------------------- #


def test_emitted_claims_pass_span_containment_gate() -> None:
    source = Source(id="x", transcript="alpha\n\nbeta\n\ngamma")
    claims, _ = normalize(source, ["alpha", "beta", "gamma"])
    gate = SpanContainmentFaithfulness()

    assert claims  # guard: we are actually checking something
    for claim in claims:
        # claim.text == trace.span ⇒ normalized containment is trivially True.
        assert gate.entails(claim) is True


# --------------------------------------------------------------------------- #
# unextracted[] composes with the Coverage honesty validator
# --------------------------------------------------------------------------- #


def test_unextracted_feeds_a_non_complete_coverage() -> None:
    source = Source(id="x", transcript="present")
    claims, unextracted = normalize(source, ["present", "absent"])

    assert len(claims) == 1
    assert len(unextracted) == 1
    # A backend wrapping this output must mark coverage incomplete — the validator
    # makes "complete with dropped content" unrepresentable; this asserts our shape fits.
    coverage = Coverage(complete=False, unextracted=unextracted)
    assert coverage.complete is False
    assert coverage.unextracted == unextracted


# --------------------------------------------------------------------------- #
# Edge cases — empty list, empty unit, unit longer than transcript
# --------------------------------------------------------------------------- #


def test_empty_units_returns_empty_tuple() -> None:
    source = Source(id="x", transcript="anything")
    claims, unextracted = normalize(source, [])

    assert claims == []
    assert unextracted == []


def test_empty_unit_is_located_as_a_zero_width_span() -> None:
    # str.find("", cursor) returns cursor for any cursor <= len, so an empty unit is
    # "locatable" as a zero-width span. Documented behavior: it mints a zero-width,
    # content-addressed Claim (text == "" == span). It is faithful (empty IS a substring).
    source = Source(id="x", transcript="abc")
    claims, unextracted = normalize(source, [""])

    assert len(claims) == 1
    assert unextracted == []
    trace = claims[0].evidence[0]
    assert claims[0].text == ""
    assert trace.start == trace.end  # zero-width
    assert trace.span == ""
    assert trace.is_addressed is True


def test_unit_longer_than_remaining_transcript_routes_to_unextracted() -> None:
    source = Source(id="x", transcript="short")
    claims, unextracted = normalize(source, ["short but actually much longer than the transcript"])

    assert claims == []
    assert len(unextracted) == 1
    assert "not verbatim-locatable" in unextracted[0].reason


def test_overlapping_units_second_starts_after_first_ends() -> None:
    # Overlapping requested units: the cursor advances past the first match's END, so an
    # overlapping second unit (which begins inside the first) is NOT re-located backwards.
    # "abcabc" with units ["abc", "bca"] -> "abc" at 0..3; "bca" only exists at 1..4 which is
    # before the cursor (3) -> not locatable from the cursor -> unextracted. Documented:
    # the cursor enforces non-overlapping, forward-only provenance.
    source = Source(id="x", transcript="abcabc")
    claims, unextracted = normalize(source, ["abc", "bca"])

    assert len(claims) == 1
    assert claims[0].evidence[0].start == 0
    assert len(unextracted) == 1
    assert "not verbatim-locatable" in unextracted[0].reason


def test_return_type_is_a_two_tuple_of_lists() -> None:
    source = Source(id="x", transcript="x")
    result = normalize(source, ["x"])

    assert isinstance(result, tuple)
    assert len(result) == 2
    claims, unextracted = result
    assert isinstance(claims, list)
    assert isinstance(unextracted, list)
    assert all(isinstance(c, Claim) for c in claims)
