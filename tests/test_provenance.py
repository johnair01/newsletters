"""Content-addressed provenance + STALE tests (PROV-01, Phase 3 Plan 01).

Proves the trust property PROV-01: every Trace CAN be content-addressed (SHA-256 of the
FULL Source content + character offsets + verbatim span), the pinning is self-verifying,
and source drift becomes a deterministic, COMPUTED STALE signal (never a stored flag).
Backward-compat (D-4): the content-address fields are optional, so every Rev1 Trace and the
bare-string-locator coercion path stay valid.

Decisions: D-1 (SHA-256 of full Source.transcript + char offsets + verbatim span),
D-2 (STALE is computed, never a stored flag), D-4 (fields optional for backward-compat).
"""

from __future__ import annotations

import hashlib

import pytest

from newsletters.locators import FreeLocator, SessionLocator
from newsletters.semantic import Claim, Distillation, Source, Trace

# Known stdlib SHA-256 digests for fixed inputs (independent re-computation in-test).
HASH_WE_DID_X = hashlib.sha256("we did X".encode("utf-8")).hexdigest()
HASH_EMPTY = hashlib.sha256(b"").hexdigest()


# --- Task 1: Source.content_hash() + optional Trace fields -------------------- #


def test_source_content_hash_matches_stdlib_sha256() -> None:
    """Source.content_hash() == stdlib hashlib.sha256(transcript.utf-8).hexdigest()."""
    src = Source(id="s1", transcript="we did X")
    assert src.content_hash() == HASH_WE_DID_X
    # equals an independent re-computation, not a hardcoded magic string only
    assert src.content_hash() == hashlib.sha256("we did X".encode("utf-8")).hexdigest()


def test_source_content_hash_empty_transcript_is_sha256_of_empty_bytes() -> None:
    """An empty transcript hashes to SHA-256 of b'' — deterministic, no special-casing."""
    src = Source(id="s1")  # transcript defaults to ""
    assert src.content_hash() == HASH_EMPTY


def test_trace_content_address_fields_are_optional_default_none() -> None:
    """A Rev1-path Trace (no content-address args) is valid; new fields default to None."""
    t = Trace(source_id="s1")
    assert t.content_hash is None
    assert t.start is None
    assert t.end is None


def test_trace_bare_string_locator_coerces_and_new_fields_default_none() -> None:
    """Bare-string locator still coerces to FreeLocator AND new fields default to None."""
    t = Trace(source_id="s1", locator="line 3")
    assert isinstance(t.locator, FreeLocator)
    assert t.locator.text == "line 3"
    assert t.content_hash is None and t.start is None and t.end is None


def test_trace_json_roundtrip_with_and_without_content_address() -> None:
    """A Trace round-trips losslessly through JSON with the new fields populated AND absent."""
    populated = Trace(
        source_id="s1",
        locator=SessionLocator(source_id="s1", note="kickoff"),
        span="did X",
        content_hash=HASH_WE_DID_X,
        start=3,
        end=8,
    )
    assert Trace.model_validate_json(populated.model_dump_json()) == populated

    bare = Trace(source_id="s1", locator="line 3")
    assert Trace.model_validate_json(bare.model_dump_json()) == bare


# --- Task 2: self-verifying Trace.from_source() ------------------------------- #


def test_from_source_pins_hash_offsets_and_verbatim_span() -> None:
    """from_source sets content_hash, start/end, and span = transcript[start:end]."""
    src = Source(id="s1", transcript="we did X")
    t = Trace.from_source(src, 3, 8)  # "did X"
    assert t.content_hash == src.content_hash()
    assert t.start == 3 and t.end == 8
    assert t.span == "did X"
    assert t.span == src.transcript[3:8]


def test_from_source_is_self_verifying() -> None:
    """The stored span re-checks against the offset window of the SAME live source."""
    src = Source(id="s1", transcript="we did X")
    t = Trace.from_source(src, 0, 2)  # "we"
    assert t.span == src.transcript[t.start : t.end]


def test_from_source_preserves_source_id_and_locator_default() -> None:
    """from_source carries source.id; locator defaults to FreeLocator when none given."""
    src = Source(id="src-42", transcript="we did X")
    t = Trace.from_source(src, 3, 8)
    assert t.source_id == "src-42"
    assert isinstance(t.locator, FreeLocator)

    loc = SessionLocator(source_id="src-42", note="kickoff")
    t2 = Trace.from_source(src, 3, 8, locator=loc)
    assert t2.locator == loc


@pytest.mark.parametrize(
    "start,end",
    [
        (-1, 4),  # negative start
        (5, 3),  # inverted (end < start)
        (0, 99),  # end > len(transcript)
    ],
)
def test_from_source_bad_offsets_raise_valueerror(start: int, end: int) -> None:
    """Out-of-range / inverted offsets raise a teaching ValueError, never silently clip."""
    src = Source(id="s1", transcript="we did X")
    with pytest.raises(ValueError):
        Trace.from_source(src, start, end)


# --- Task 3: STALE as a computed property ------------------------------------- #


def test_trace_is_stale_against_flips_on_source_edit() -> None:
    """is_stale_against is False for the live source, True after the transcript is edited."""
    src = Source(id="s1", transcript="we did X")
    t = Trace.from_source(src, 3, 8)
    assert t.is_stale_against(src) is False

    edited = Source(id="s1", transcript="we did Y instead")
    assert t.is_stale_against(edited) is True


def test_unaddressed_trace_is_not_addressed_and_never_stale() -> None:
    """A content_hash=None Trace reports is_addressed=False and is never stale (no raise)."""
    src = Source(id="s1", transcript="we did X")
    t = Trace(source_id="s1", locator="line 3")  # Rev1, un-addressed
    assert t.is_addressed is False
    assert t.is_stale_against(src) is False  # never pinned => not stale, no raise


def test_claim_is_stale_when_any_trace_drifts() -> None:
    """Claim.is_stale flips True after one underlying source edit, given a source lookup."""
    src = Source(id="s1", transcript="we did X")
    claim = Claim(text="we did X", evidence=[Trace.from_source(src, 3, 8)])
    assert claim.is_stale({"s1": src}) is False

    edited = Source(id="s1", transcript="we did Y instead")
    assert claim.is_stale({"s1": edited}) is True


def test_claim_is_stale_skips_absent_source_ids() -> None:
    """A trace whose source_id is absent from the lookup does not raise and is not stale."""
    src = Source(id="s1", transcript="we did X")
    claim = Claim(text="we did X", evidence=[Trace.from_source(src, 3, 8)])
    assert claim.is_stale({}) is False  # unknown source skipped, no KeyError


def test_distillation_stale_claims_lists_drifted_claims() -> None:
    """Distillation.stale_claims returns drifted claims and [] when nothing drifted."""
    src = Source(id="s1", transcript="we did X")
    fresh = Claim(text="fresh", evidence=[Trace.from_source(src, 0, 2)])
    drifted = Claim(text="drifted", evidence=[Trace.from_source(src, 3, 8)])

    # Build a Distillation carrying the source as one of its `traces` (Source[]).
    dist = Distillation(claims=[fresh, drifted], traces=[src])
    assert dist.stale_claims() == []  # source unchanged => nothing stale

    edited = Source(id="s1", transcript="we did Y instead")
    dist_edited = Distillation(claims=[fresh, drifted], traces=[edited])
    stale = dist_edited.stale_claims()
    assert fresh in stale and drifted in stale  # both pin into s1


def test_stale_is_purely_computed_no_stored_flag() -> None:
    """STALE is computed — no settable boolean stale field on Trace/Claim/Distillation."""
    forbidden = {"is_stale", "stale", "is_stale_flag"}
    for model in (Trace, Claim, Distillation):
        assert not (forbidden & set(model.model_fields)), (
            f"{model.__name__} must not store a stale flag as a model field"
        )
