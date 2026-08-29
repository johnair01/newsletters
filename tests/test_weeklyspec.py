"""Weekly Spec authoring path — proof suite (ported from ``tests/test_casespec.py``).

Two committed fixtures under ``tests/fixtures/weekly/`` drive the LIVE validator/loader
(``src/newsletters/weeklyspec.py``) end to end. Assertions are on STRUCTURE and INVARIANTS; where
a concrete value is needed it is read from the SAME parsed fixture the loader reads, so the test
tracks the corpus rather than freezing a magic string.

* ``weekly-full.yml`` — all eight keys: an ordinary quoted highlight AND a block-scalar one, a
  lowlight, two recognitions (one sourced, one not), two team members, three assets (complete /
  deep-link-required / provenance-incomplete), and a ``config:`` subtree whose values must NEVER
  become claims. One person string appears in BOTH ``recognitions:`` and ``team:`` — the
  span-swap regression's non-vacuity.
* ``weekly-sparse.yml`` — only ``week`` + ``module``: every other key must be disclosed in
  ``Distillation.missing[]``, never fabricated.

The invariants proven here (the Case Spec's eight, plus two the weekly earns):

1. **Schema validation** — teaching errors on a non-mapping doc, an unknown TOP-LEVEL key, an
   unknown key inside a recognition / a team member / an asset, and a type-coerced scalar.
2. **Trace faithfulness** — every claim content-addressed via ``Trace.from_source``, non-stale,
   re-sliceable from the live transcript, and entailed by the LIVE
   ``SpanContainmentFaithfulness`` gate (the strict half — never the structural fallback).
3. **The block-scalar item region** — asserted as the gate's own rule
   (``_normalize(text) in _normalize(span)``), never ``transcript[start:end] == text``.
4. **The span-swap regression** — a value duplicated across two sections traces to ITS OWN LINE.
5. **missing[] honesty** — every absent key is disclosed, in schema order, including "no
   lowlights"; no claim exists for an absent field.
6. **Narrative verbatim** — authored lines reach the typed spec byte-identical to the parsed YAML.
7. **Config never claimed** — no ``config:`` leaf appears in any claim; the subtree is carried.
8. **Recognition evidence** — absent / unresolvable ``source:`` ⇒ ``evidence == []`` + a named
   disclosure; a resolved one ⇒ exactly one SPAN-LESS ``Trace``. Never a fabricated span.
9. **Root containment** — a path outside ``root`` RAISES (a refusal, not a ``missing[]`` entry).
10. **Determinism + read-only** — two loads are byte-identical, the JSON round-trips, and the
    fixture's mtime and size are unchanged after a load.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters._yaml_loader import load_config
from newsletters.distill.faithfulness import SpanContainmentFaithfulness, _normalize
from newsletters.semantic import Source
from newsletters.weeklyspec import (
    AuthoredAsset,
    AuthoredMember,
    AuthoredRecognition,
    WeeklySpec,
    WeeklySpecLoad,
    _validate,
    load_weekly_spec,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "weekly"
FULL = "weekly-full.yml"
SPARSE = "weekly-sparse.yml"
FIXTURES = [FULL, SPARSE]
AUTHOR = "author-x"

# The eight keys, in schema order. Duplicated here ON PURPOSE: importing the module's own
# ``_KNOWN_KEYS`` would make this assertion vacuous (it would compare the constant to itself).
SCHEMA_KEYS = [
    "week",
    "module",
    "highlights",
    "lowlights",
    "recognitions",
    "team",
    "assets",
    "config",
]


def _load(name: str, **kwargs) -> WeeklySpecLoad:
    return load_weekly_spec(FIXTURE_DIR / name, root=REPO_ROOT, **kwargs)


def _parsed(name: str) -> dict:
    return load_config((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _line_of(transcript: str, offset: int) -> int:
    """1-based line number of a character offset — the unit the span-swap proof asserts in."""
    return transcript[:offset].count("\n") + 1


def _line_containing(transcript: str, needle: str) -> int:
    """1-based number of the FIRST line containing ``needle`` (the fixture authors it once)."""
    for index, line in enumerate(transcript.splitlines(), start=1):
        if needle in line:
            return index
    raise AssertionError(f"{needle!r} is not on any line of the fixture")


def _validated(text: str) -> dict:
    """Parse + validate one authored document, the way the loader will."""
    return _validate(load_config(text))


# --------------------------------------------------------------------------- #
# 1 — schema validation: teaching errors at BOTH levels, never a silent drop
# --------------------------------------------------------------------------- #


def test_non_mapping_document_names_the_eight_key_schema() -> None:
    """A document that is not a mapping fails loudly, naming the schema and the spec doc."""
    with pytest.raises(ValueError) as excinfo:
        _validated("- just\n- a list\n")
    message = str(excinfo.value)
    assert "YAML mapping" in message
    assert "docs/weekly-spec.md" in message
    for key in SCHEMA_KEYS:
        assert repr(key) in message, f"{key} not named in the schema error: {message}"


def test_unknown_top_level_key_refuses_to_drop_authored_content() -> None:
    """``highlight:`` for ``highlights:`` fails loudly — a typo must not lose a lowlight."""
    with pytest.raises(ValueError) as excinfo:
        _validated('week: "W1"\nhighlight:\n  - "one"\n')
    message = str(excinfo.value)
    assert "unknown Weekly Spec field" in message
    assert "'highlight'" in message
    assert "Refusing to drop authored content silently." in message
    for key in SCHEMA_KEYS:
        assert repr(key) in message


@pytest.mark.parametrize(
    ("document", "container", "offender"),
    [
        (
            'recognitions:\n  - person: "P"\n    resaon: "typo"\n',
            "recognitions[0]",
            "resaon",
        ),
        (
            'team:\n  - name: "N"\n    rol: "typo"\n',
            "team[0]",
            "rol",
        ),
        (
            'assets:\n  k:\n    file: "f"\n    fodler: "typo"\n',
            "assets['k']",
            "fodler",
        ),
    ],
)
def test_unknown_nested_key_fails_loud_naming_container_and_key(
    document: str, container: str, offender: str
) -> None:
    """A mistyped field INSIDE a container earns the same refusal as a top-level typo.

    Rule 1 names the top level, but a dropped ``resaon:`` loses authored content exactly as
    silently as a dropped ``lowlight:`` would. Same teaching voice, same refusal.
    """
    with pytest.raises(ValueError) as excinfo:
        _validated(document)
    message = str(excinfo.value)
    assert repr(offender) in message
    assert container in message
    assert "Refusing to drop authored content silently." in message


@pytest.mark.parametrize(
    ("document", "field", "actual"),
    [
        ("week: 42\n", "week", "int"),
        ("module: yes\n", "module", "bool"),
        ('highlights:\n  - "ok"\n  - 42\n', "highlights[1]", "int"),
        ('recognitions:\n  - person: yes\n', "recognitions[0].person", "bool"),
        ('team:\n  - name: "N"\n    lines:\n      - 42\n', "team[0].lines[0]", "int"),
        ('assets:\n  k:\n    sha256: 42\n', "assets['k'].sha256", "int"),
    ],
)
def test_type_coerced_scalar_names_the_field_its_type_and_the_fix(
    document: str, field: str, actual: str
) -> None:
    """A bare ``yes`` / ``42`` stops being the author's text, so the loader refuses it."""
    with pytest.raises(ValueError) as excinfo:
        _validated(document)
    message = str(excinfo.value)
    assert repr(field) in message
    assert f"got {actual}" in message
    assert "quote the value so YAML cannot type-coerce it" in message


@pytest.mark.parametrize("name", FIXTURES)
def test_both_committed_fixtures_parse_and_validate(name: str) -> None:
    """The corpus every later Phase-3 proof is written against is itself schema-clean."""
    parsed = _validate(_parsed(name))
    assert isinstance(parsed, dict) and parsed
    assert all(key in SCHEMA_KEYS for key in parsed), sorted(parsed)
    # File order IS schema order in the corpus — the forward cursor depends on the walk being
    # able to follow the document; a fixture authored out of schema order would hide that.
    assert list(parsed) == [k for k in SCHEMA_KEYS if k in parsed]


def test_full_fixture_carries_the_shapes_the_phase_is_proved_against() -> None:
    """Non-vacuity: the full fixture really does carry every shape the later tests need.

    Without this, a fixture that quietly lost its block scalar or its duplicated person would
    leave the block-scalar and span-swap proofs passing for the wrong reason.
    """
    parsed = _parsed(FULL)
    assert list(parsed) == SCHEMA_KEYS, "the full fixture must author all eight keys"

    # Two highlights: one an ordinary scalar, one a BLOCK scalar (multi-line, so its folded
    # value is not a verbatim substring of the file).
    highlights = parsed["highlights"]
    assert len(highlights) == 2
    assert "\n" not in highlights[0], "the first highlight must be an ordinary scalar"
    assert "\n" in highlights[1], "the second highlight must be a block scalar"

    assert len(parsed["lowlights"]) == 1

    # Two recognitions — exactly one of them sourced (rule 6's both-halves case).
    sourced = [r for r in parsed["recognitions"] if r.get("source")]
    assert len(parsed["recognitions"]) == 2 and len(sourced) == 1

    # The duplicated person string: named in BOTH recognitions and team.
    people = {r["person"] for r in parsed["recognitions"]}
    members = {m["name"] for m in parsed["team"]}
    assert people & members, "a person must appear in BOTH sections for the span-swap proof"

    # Three assets: complete / deep-link-required / provenance-incomplete.
    assets = parsed["assets"]
    assert len(assets) == 3
    complete = [
        k for k, r in assets.items() if all(r.get(f) for f in ("folder", "date", "event"))
    ]
    assert len(complete) == 2
    values_no_link = [
        k
        for k, r in assets.items()
        if r.get("stands_in_for") == "values" and not r.get("link")
    ]
    assert len(values_no_link) == 1, "the deep-link row must be exercised"
    incomplete = [
        k
        for k, r in assets.items()
        if not all(r.get(f) for f in ("folder", "date", "event"))
    ]
    assert len(incomplete) == 1, "one asset must be missing a provenance minimum"

    assert parsed["config"], "config must be non-empty or the never-claimed guard is vacuous"


def test_sparse_fixture_authors_only_the_two_scalars() -> None:
    """The sparse fixture's whole job is ABSENCE — six keys unwritten, including lowlights."""
    parsed = _parsed(SPARSE)
    assert list(parsed) == ["week", "module"]
    for key in SCHEMA_KEYS[2:]:
        assert key not in parsed


# --------------------------------------------------------------------------- #
# 2 — the authored-side models: permissive by design, so absences are disclosable
# --------------------------------------------------------------------------- #


def test_authored_models_are_permissive_so_an_incomplete_entry_is_disclosable() -> None:
    """An incomplete authored entry must be REPRESENTABLE long enough to be disclosed.

    This is the load half of the load/place seam. A recognition with no source is still credit
    owed; an asset missing a provenance minimum must be carried far enough to NAME the missing
    field. The strict shape (``semantic.AssetRecord``, whose minimums are non-optional) is
    deliberately not used here — that one guards PLACEMENT, where an incomplete record must be
    unrepresentable. Both directions are asserted so neither can be quietly relaxed.
    """
    # Permissive on the authored side: nothing is required, everything defaults empty.
    assert AuthoredRecognition().model_dump() == {
        "person": "",
        "reason": "",
        "source": "",
        "evidence": [],
    }
    assert AuthoredMember().lines == []
    assert AuthoredAsset(key="k").folder == ""

    # ...and the strict shape refuses exactly what the permissive one carries.
    from pydantic import ValidationError

    from newsletters.semantic import AssetRecord

    with pytest.raises(ValidationError) as excinfo:
        AssetRecord(key="k", file="f", sha256="s")  # no folder / date / event
    missing_fields = {
        error["loc"][0] for error in excinfo.value.errors() if error["type"] == "missing"
    }
    assert {"folder", "date", "event"} <= missing_fields, missing_fields


def test_weekly_spec_defaults_are_empty_never_fabricated() -> None:
    """A ``WeeklySpec`` built from nothing carries nothing — no placeholder, no invented value."""
    spec = WeeklySpec()
    assert spec.week == "" and spec.module == ""
    assert spec.highlights == [] and spec.lowlights == []
    assert spec.recognitions == [] and spec.team == [] and spec.assets == []
    assert spec.config == {}


# --------------------------------------------------------------------------- #
# 3 — trace faithfulness: content-addressed spans, entailed by the LIVE gate
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", FIXTURES)
def test_trace_faithfulness(name: str) -> None:
    """Every claim is content-addressed, non-stale, re-sliceable, and STRICTLY entailed.

    Because every trace ``is_addressed``, ``SpanContainmentFaithfulness`` takes its strict branch
    (normalized claim text contained in the normalized span) — the structural un-addressed
    fallback is provably not what passes here.
    """
    gate = SpanContainmentFaithfulness()
    load = _load(name)
    source = load.source
    assert load.distillation.claims, f"{name}: expected at least one claim"
    for claim in load.distillation.claims:
        assert claim.is_traced, f"{name}: {claim.text!r} is untraced"
        assert gate.entails(claim), f"{name}: {claim.text!r} fails the live gate"
        for trace in claim.evidence:
            assert trace.is_addressed, f"{name}: {claim.text!r} not content-addressed"
            assert trace.start is not None and trace.end is not None
            # the recorded window re-slices the LIVE transcript to the stored span
            assert source.transcript[trace.start : trace.end] == trace.span
            # the span REALLY contains the claim (the strict rule, asserted directly)
            assert _normalize(claim.text) in _normalize(trace.span)
            assert trace.content_hash == source.content_hash()
            assert not trace.is_stale_against(source)


def test_block_scalar_highlight_is_traced_to_its_own_item_region() -> None:
    """The block-scalar highlight's span is the raw ITEM REGION — asserted as the gate's rule.

    A block scalar's FOLDED value is not a substring of the file at all (the raw text carries the
    indentation the folding removed), so "a real span" here means "the region that CONTAINS your
    text", not "the exact bytes of your text". The honest assertion is therefore the gate's own —
    ``_normalize(text) in _normalize(span)`` — plus ``transcript[start:end] == span``. Asserting
    ``transcript[start:end] == text`` would be false for a correct implementation.

    The regression this pins (inherited from the Case Spec): the block item's region must not
    swallow its sibling, so the ordinary highlight is still located verbatim and minted, never
    falsely disclosed as unlocatable.
    """
    load = _load(FULL)
    transcript = load.source.transcript
    plain, block = _parsed(FULL)["highlights"]
    claims = [c for c in load.distillation.claims if c.topics == ["highlights"]]
    texts = [c.text for c in claims]

    assert texts == [plain, block], "both highlights must be traced claims, in file order"
    assert not any("could not be located" in note for note in load.distillation.missing)

    plain_trace = claims[0].evidence[0]
    assert transcript[plain_trace.start : plain_trace.end] == plain, "exact-find span"

    block_trace = claims[1].evidence[0]
    span = transcript[block_trace.start : block_trace.end]
    assert span == block_trace.span
    assert _normalize(block) in _normalize(span)
    assert span != block, "a block scalar's folded value is NOT its raw region"
    assert plain not in span, "the item region must not swallow its sibling"


# --------------------------------------------------------------------------- #
# 4 — the span-swap regression: a duplicated value traces to ITS OWN line
# --------------------------------------------------------------------------- #


def test_duplicated_person_traces_to_its_own_line_not_its_twins() -> None:
    """The person named in BOTH ``recognitions:`` and ``team:`` gets two claims on two LINES.

    03-RESEARCH proved by execution that minting a later field before an earlier one silently
    SWAPS the spans of a duplicated value — and that BOTH claims still pass the faithfulness
    gate, because the text is identical. No gate can catch it. So this test asserts on LINE
    NUMBERS, which is the only thing that differs, and it was observed RED once against a
    deliberately reversed walk order (recorded in 03-02-SUMMARY.md).
    """
    load = _load(FULL)
    transcript = load.source.transcript
    parsed = _parsed(FULL)

    duplicated = {r["person"] for r in parsed["recognitions"]} & {
        m["name"] for m in parsed["team"]
    }
    assert len(duplicated) == 1, "the fixture must name exactly one person in both sections"
    person = duplicated.pop()

    recognition_claims = [
        c
        for c in load.distillation.claims
        if c.topics == ["recognitions.person"] and c.text == person
    ]
    team_claims = [
        c
        for c in load.distillation.claims
        if c.topics == ["team.name"] and c.text == person
    ]
    assert len(recognition_claims) == 1 and len(team_claims) == 1

    recognition_line = _line_of(transcript, recognition_claims[0].evidence[0].start)
    team_line = _line_of(transcript, team_claims[0].evidence[0].start)

    assert recognition_line == _line_containing(transcript, f'person: "{person}"')
    assert team_line == _line_containing(transcript, f'name: "{person}"')
    assert recognition_line < team_line, "the spans are swapped — file order was not honored"


def test_claim_spans_ascend_strictly_in_document_order() -> None:
    """The forward cursor's signature: every claim's span starts after the previous one ends.

    The whole-document version of the assertion above — it catches an out-of-order walk anywhere,
    not only where the corpus happens to duplicate a value.
    """
    load = _load(FULL)
    previous_end = -1
    for claim in load.distillation.claims:
        trace = claim.evidence[0]
        assert trace.start >= previous_end, (
            f"claim {claim.text[:40]!r} starts at {trace.start}, before the previous claim "
            f"ended at {previous_end} — the walk left file order"
        )
        previous_end = trace.end


# --------------------------------------------------------------------------- #
# 5 — missing[] honesty: every absence disclosed, in schema order
# --------------------------------------------------------------------------- #


def test_sparse_spec_discloses_every_absent_key_in_schema_order() -> None:
    """Six unwritten keys, disclosed by name and in schema order — including "no lowlights".

    Rule 4 singles out lowlights as "precisely the absence a weekly is tempted to hide", so the
    assertion names it rather than trusting a loop to have covered it.
    """
    load = _load(SPARSE)
    parsed = _parsed(SPARSE)
    absent_keys = [k for k in SCHEMA_KEYS if k not in parsed]
    assert absent_keys == SCHEMA_KEYS[2:], "the sparse fixture must omit six keys"

    disclosed_order = [
        key
        for key in SCHEMA_KEYS
        if any(f"{key!r} is absent" in note for note in load.distillation.missing)
    ]
    # `config` absence is NOT a gap — a weekly with no org slots is simply fully portable.
    assert disclosed_order == [k for k in absent_keys if k != "config"]
    assert any(
        "'lowlights' is absent" in note for note in load.distillation.missing
    ), load.distillation.missing

    # No fabrication: every claim's topic is a key the author actually wrote.
    authored = set(parsed)
    for claim in load.distillation.claims:
        assert claim.topics and claim.topics[0].split(".")[0] in authored


def test_full_spec_discloses_its_per_item_absences() -> None:
    """Absences INSIDE a carried entry are disclosed too — the entry is kept, the gap is named."""
    load = _load(FULL)
    notes = load.distillation.missing
    # The second team member authors no photo; the member and their lines are still carried.
    assert any("'team[1].photo' is absent" in note for note in notes), notes
    assert load.spec.team[1].name and load.spec.team[1].lines
    # ...and nothing was invented to fill the gap.
    assert load.spec.team[1].photo == ""


# --------------------------------------------------------------------------- #
# 6 — narrative reaches the typed spec byte-verbatim
# --------------------------------------------------------------------------- #


def test_authored_narrative_is_carried_byte_verbatim() -> None:
    """Every authored line equals the parsed YAML value exactly — never summarised or merged."""
    load = _load(FULL)
    parsed = _parsed(FULL)

    assert load.spec.week == parsed["week"]
    assert load.spec.module == parsed["module"]
    assert load.spec.highlights == parsed["highlights"]
    assert load.spec.lowlights == parsed["lowlights"]

    for authored, carried in zip(parsed["recognitions"], load.spec.recognitions):
        assert carried.person == authored["person"]
        assert carried.reason == authored["reason"]
    for authored, carried in zip(parsed["team"], load.spec.team):
        assert carried.name == authored["name"]
        assert carried.role == authored.get("role", "")
        assert carried.lines == authored.get("lines", [])

    # The assets keep their authored key AND their file order.
    assert [a.key for a in load.spec.assets] == list(parsed["assets"])
    for asset in load.spec.assets:
        authored_record = parsed["assets"][asset.key]
        for field, value in authored_record.items():
            assert getattr(asset, field) == value

    # Every carried line is also a traced claim — the record and its evidence cannot drift.
    claim_texts = {c.text for c in load.distillation.claims}
    for line in parsed["highlights"] + parsed["lowlights"]:
        assert line in claim_texts


# --------------------------------------------------------------------------- #
# 7 — config values are org slots: carried, NEVER claimed
# --------------------------------------------------------------------------- #


def _config_leaves(node: object) -> list[str]:
    if isinstance(node, dict):
        return [leaf for v in node.values() for leaf in _config_leaves(v)]
    if isinstance(node, list):
        return [leaf for v in node for leaf in _config_leaves(v)]
    return [] if node is None else [str(node)]


def test_config_never_in_claims_but_always_carried() -> None:
    """No ``config:`` leaf appears in any claim text; the subtree is carried exactly (non-vacuous)."""
    load = _load(FULL)
    leaves = _config_leaves(_parsed(FULL)["config"])
    assert leaves, "fixture must declare config values for this guard to be non-vacuous"

    for leaf in leaves:
        for claim in load.distillation.claims:
            assert leaf not in claim.text, f"config value {leaf!r} leaked into {claim.text!r}"
        for note in load.distillation.missing:
            assert leaf not in note, f"config value {leaf!r} leaked into a disclosure"

    # ...but the slots are carried (not lost) — they stay CONFIG, available for binding.
    assert load.spec.config == _parsed(FULL)["config"]


# --------------------------------------------------------------------------- #
# 8 — recognition evidence: a pointer, a disclosure, or both halves. Never a lie.
# --------------------------------------------------------------------------- #


def test_recognition_without_source_is_carried_and_disclosed() -> None:
    """Rule 6, both halves: the credit survives AND its missing evidence is named."""
    load = _load(FULL)
    parsed = _parsed(FULL)
    index, authored = next(
        (i, r) for i, r in enumerate(parsed["recognitions"]) if not r.get("source")
    )
    carried = load.spec.recognitions[index]

    assert carried.person == authored["person"] and carried.reason == authored["reason"]
    assert carried.evidence == [], "no source ⇒ no evidence, never a fabricated Trace"
    assert any(
        f"'recognitions[{index}].source' is absent" in note
        for note in load.distillation.missing
    ), load.distillation.missing
    # The author's own word IS separately evidenced — as claims at real spans of this file.
    claim_texts = {c.text for c in load.distillation.claims}
    assert authored["person"] in claim_texts and authored["reason"] in claim_texts


def test_resolved_source_becomes_exactly_one_span_less_trace() -> None:
    """A ``source:`` that names a KNOWN Source is a POINTER — one Trace, deliberately span-less.

    The loader has not read that source's text, so minting a span for it would be fabrication.
    """
    parsed = _parsed(FULL)
    source_id = next(r["source"] for r in parsed["recognitions"] if r.get("source"))
    known = Source(id=source_id, context="test:known", transcript="unread by the loader")

    load = _load(FULL, known_sources=[known])
    index = next(i for i, r in enumerate(parsed["recognitions"]) if r.get("source"))
    evidence = load.spec.recognitions[index].evidence

    assert len(evidence) == 1
    trace = evidence[0]
    assert trace.source_id == source_id
    assert trace.span == "" and trace.start is None and trace.end is None
    assert not trace.is_addressed, "a pointer is not a content-addressed span"
    assert not any(
        "does not resolve" in note for note in load.distillation.missing
    ), "a resolved id must not also be disclosed as unresolvable"


def test_unresolvable_source_is_disclosed_by_name_never_traced() -> None:
    """An id that names nothing gets the ABSENT-source treatment plus the id in the disclosure."""
    load = _load(FULL)  # no known_sources — the authored id resolves to nothing
    parsed = _parsed(FULL)
    index, authored = next(
        (i, r) for i, r in enumerate(parsed["recognitions"]) if r.get("source")
    )

    assert load.spec.recognitions[index].evidence == []
    note = next(n for n in load.distillation.missing if "does not resolve" in n)
    assert repr(authored["source"]) in note, note
    assert repr(authored["person"]) in note, note
    # The recognition itself is fully carried — dropping it would erase credit.
    assert load.spec.recognitions[index].person == authored["person"]
    assert load.spec.recognitions[index].reason == authored["reason"]


# --------------------------------------------------------------------------- #
# 9 — root containment is a REFUSAL, not an absence
# --------------------------------------------------------------------------- #


def test_spec_outside_root_raises_and_never_lands_in_missing(
    tmp_path: pathlib.Path,
) -> None:
    """A path escaping ``root`` raises. ``missing[]`` is for absent content, not refused requests.

    Rule 7: "This is not a ``missing[]`` case; it is a refusal." Proven by pairing the raise with
    a CONSTRUCTING arm — the same file loads cleanly once ``root`` legitimately contains it, so
    the refusal is the containment check and not a broken loader.
    """
    outside = tmp_path / "outside.yml"
    outside.write_text('week: "W1"\nmodule: "M"\n', encoding="utf-8")
    inner = tmp_path / "inner"
    inner.mkdir()

    with pytest.raises(ValueError):
        load_weekly_spec(outside, root=inner)

    load = load_weekly_spec(outside, root=tmp_path)
    assert load.spec.week == "W1"
    assert not any("outside" in note for note in load.distillation.missing)


# --------------------------------------------------------------------------- #
# 10 — determinism, lossless round-trip, and a loader that writes nothing
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", FIXTURES)
def test_lossless_roundtrip_and_determinism(name: str) -> None:
    """Raw file carried verbatim; two loads and the JSON round-trip are byte-identical."""
    raw = (FIXTURE_DIR / name).read_text(encoding="utf-8")
    first = _load(name)
    assert first.source.transcript == raw
    assert first.source.context == f"weekly-spec:tests/fixtures/weekly/{name}"

    second = _load(name)
    assert first.model_dump_json() == second.model_dump_json()

    dumped = first.model_dump_json()
    assert WeeklySpecLoad.model_validate_json(dumped).model_dump_json() == dumped


@pytest.mark.parametrize("name", FIXTURES)
def test_the_loader_writes_nothing(name: str) -> None:
    """READ-ONLY, asserted on the filesystem: the fixture's mtime and size survive a load."""
    path = FIXTURE_DIR / name
    before = path.stat()
    _load(name)
    after = path.stat()
    assert (after.st_mtime_ns, after.st_size) == (before.st_mtime_ns, before.st_size)
