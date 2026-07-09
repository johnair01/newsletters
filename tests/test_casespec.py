"""Case Spec authoring path — proof suite (style of ``test_swimlane.py``).

Two committed fixtures under ``tests/fixtures/casespec/`` drive the LIVE loader/builder
(``src/newsletters/casespec.py``) end to end. Assertions are on STRUCTURE and INVARIANTS;
where a concrete value is needed it is read from the SAME parsed fixture the loader reads,
so the test tracks the config rather than freezing a magic string.

* ``case-shuttle-turnaround.yml`` — well-formed: every narrative field authored, a
  block-scalar ``reasoning``, and a ``config:`` section whose values must NEVER become claims.
* ``case-sparse.yml`` — only ``case`` + ``problem``: every other field must be disclosed in
  ``Distillation.missing[]``, never fabricated.

The invariants proven here:

1. **Schema validation** — teaching errors on a non-mapping doc, an unknown field, a
   type-coerced narrative field, an unknown design slot.
2. **Trace faithfulness** — every claim content-addressed via ``Trace.from_source``,
   non-stale, re-sliceable from the live transcript, and entailed by the LIVE
   ``SpanContainmentFaithfulness`` gate (the strict half — never the structural fallback).
3. **missing[] honesty** — absent fields are disclosed, and no claim exists for them.
4. **Reasoning is first-class** — carried VERBATIM into the surface as a quote block.
5. **Draft + gate** — the surface ships Draft and cannot publish without the recorded
   approval the REPORT policy demands.
6. **Config never in claims** — no ``config:`` value appears in any claim or block text.
7. **Lossless round-trip / determinism** — transcript is the raw file verbatim; double
   loads, JSON round-trips, and double builds are byte-identical.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters._yaml_loader import load_config
from newsletters.casespec import CaseSpecLoad, build_case_report, load_case_spec
from newsletters.distill.faithfulness import SpanContainmentFaithfulness, _normalize
from newsletters.semantic import ClaimsBlock, QuoteBlock, ReviewState, Surface

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "casespec"
FULL = "case-shuttle-turnaround.yml"
SPARSE = "case-sparse.yml"
FIXTURES = [FULL, SPARSE]
AUTHOR = "author-x"


def _load(name: str) -> CaseSpecLoad:
    return load_case_spec(FIXTURE_DIR / name, root=REPO_ROOT)


def _parsed(name: str) -> dict:
    return load_config((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _build(name: str) -> Surface:
    return build_case_report(_load(name), author=AUTHOR)


def _block_texts(surface: Surface) -> list[str]:
    """Every human-readable string a block renders (prose/quote text, headings, claim texts)."""
    texts: list[str] = [surface.title, surface.eyebrow]
    for block in surface.blocks:
        heading = getattr(block, "heading", None)
        if heading:
            texts.append(heading)
        if hasattr(block, "text"):
            texts.append(block.text)
        if isinstance(block, ClaimsBlock):
            texts.extend(c.text for c in block.claims)
    return texts


# --------------------------------------------------------------------------- #
# 1 — schema validation: teaching errors, never a silent drop
# --------------------------------------------------------------------------- #


def test_schema_validation(tmp_path: pathlib.Path) -> None:
    """A malformed spec fails LOUDLY with a teaching error; a good spec tracks its file."""

    def write(text: str) -> pathlib.Path:
        p = tmp_path / "spec.yml"
        p.write_text(text, encoding="utf-8")
        return p

    # Non-mapping document.
    with pytest.raises(ValueError, match="YAML mapping"):
        load_case_spec(write("- just\n- a list\n"), root=tmp_path)
    # Unknown top-level field (a typo must not drop authored content silently).
    with pytest.raises(ValueError, match="unknown Case Spec field"):
        load_case_spec(write("case: X\nproblme: typo\n"), root=tmp_path)
    # A YAML-coerced narrative field (quote your scalars).
    with pytest.raises(ValueError, match="must be a string"):
        load_case_spec(write("case: X\nproblem: 42\n"), root=tmp_path)
    # Unknown design slot.
    with pytest.raises(ValueError, match="unknown design slot"):
        load_case_spec(write("case: X\ndesign:\n  widgets: nope\n"), root=tmp_path)
    # Non-string portable item.
    with pytest.raises(ValueError, match="portable"):
        load_case_spec(write("case: X\nportable:\n  - 7\n"), root=tmp_path)

    # The good fixture loads, and the typed spec tracks the parsed file (no magic strings).
    load = _load(FULL)
    parsed = _parsed(FULL)
    assert load.spec.case == parsed["case"]
    assert load.spec.problem == parsed["problem"]
    assert load.spec.reasoning == parsed["reasoning"]
    assert load.spec.design == parsed["design"]
    assert load.spec.portable == parsed["portable"]
    assert load.spec.config == parsed["config"]


# --------------------------------------------------------------------------- #
# 2 — trace faithfulness: content-addressed spans, entailed by the LIVE gate
# --------------------------------------------------------------------------- #


def test_trace_faithfulness() -> None:
    """Every claim is content-addressed, non-stale, re-sliceable, and STRICTLY entailed.

    Because every trace ``is_addressed``, ``SpanContainmentFaithfulness`` takes its strict
    branch (normalized claim text contained in the normalized span) — the structural
    un-addressed fallback is provably not what passes here.
    """
    gate = SpanContainmentFaithfulness()
    for name in FIXTURES:
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


# --------------------------------------------------------------------------- #
# 3 — missing[] honesty: absent fields disclosed, never fabricated
# --------------------------------------------------------------------------- #


def test_missing_honesty_for_absent_fields() -> None:
    """Sparse spec: each unauthored field is named in ``missing[]`` and yields NO claim."""
    load = _load(SPARSE)
    parsed = _parsed(SPARSE)
    absent = ["current_state", "imagined_state", "design", "reasoning", "portable"]
    assert all(key not in parsed for key in absent), "fixture must omit these fields"

    for key in absent:
        assert any(
            f"{key!r}" in note for note in load.distillation.missing
        ), f"absent field {key} not disclosed in missing[]: {load.distillation.missing}"

    # No fabrication: every claim's topic is a field the author actually wrote.
    authored = set(parsed)
    for claim in load.distillation.claims:
        assert claim.topics and claim.topics[0].split(".")[0] in authored

    # The disclosure flows through to the surface's honesty panel.
    surface = _build(SPARSE)
    for note in load.distillation.missing:
        assert note in surface.missing


# --------------------------------------------------------------------------- #
# 4 — reasoning is first-class: verbatim into the surface, never summarized
# --------------------------------------------------------------------------- #


def test_reasoning_verbatim_into_surface() -> None:
    """The author's reasoning survives BYTE-VERBATIM as a quote block, and is traced."""
    load = _load(FULL)
    parsed = _parsed(FULL)
    surface = _build(FULL)

    quotes = [b for b in surface.blocks if isinstance(b, QuoteBlock)]
    assert len(quotes) == 1, "the reasoning quote block is missing"
    assert quotes[0].text == parsed["reasoning"], "reasoning was altered — must be verbatim"
    assert quotes[0].attr == AUTHOR

    # The reasoning is ALSO a traced claim in the truth layer (its span is the raw block
    # region of the authored file), but it is not duplicated into the ClaimsBlock.
    reasoning_claims = [
        c for c in load.distillation.claims if c.topics == ["reasoning"]
    ]
    assert len(reasoning_claims) == 1 and reasoning_claims[0].is_traced
    for block in surface.blocks:
        if isinstance(block, ClaimsBlock):
            assert parsed["reasoning"] not in [c.text for c in block.claims]


# --------------------------------------------------------------------------- #
# 5 — the output is Draft; the review gate is the ONLY path to Published
# --------------------------------------------------------------------------- #


def test_surface_is_draft_and_cannot_publish_without_gate() -> None:
    """Draft on arrival; publish() without the policy's approval raises; gate still works."""
    surface = _build(FULL)
    assert surface.review.state is ReviewState.DRAFT
    assert not surface.is_published
    assert surface.review.author == AUTHOR

    with pytest.raises(ValueError, match="No auto-publish"):
        surface.publish()  # no recorded approval -> the policy validator refuses
    assert surface.review.state is ReviewState.DRAFT, "failed publish must not advance"

    # The gate — a recorded approval — is the one legitimate path (proving the refusal
    # above is the policy, not a broken publish).
    surface.publish(reviewer=AUTHOR)  # REPORT is light-gate: author approval suffices
    assert surface.is_published and surface.review.reviewer == AUTHOR


# --------------------------------------------------------------------------- #
# 6 — config values are org slots: NEVER in claim text, NEVER rendered
# --------------------------------------------------------------------------- #


def _config_leaves(node: object) -> list[str]:
    if isinstance(node, dict):
        return [leaf for v in node.values() for leaf in _config_leaves(v)]
    if isinstance(node, list):
        return [leaf for v in node for leaf in _config_leaves(v)]
    return [] if node is None else [str(node)]


def test_config_never_in_claims() -> None:
    """No ``config:`` value appears in any claim or any rendered block text (non-vacuous)."""
    load = _load(FULL)
    surface = _build(FULL)
    leaves = _config_leaves(_parsed(FULL)["config"])
    assert leaves, "fixture must declare config values for this guard to be non-vacuous"

    claim_texts = [c.text for c in load.distillation.claims]
    rendered = _block_texts(surface)
    for leaf in leaves:
        for text in claim_texts:
            assert leaf not in text, f"config value {leaf!r} leaked into claim {text!r}"
        for text in rendered:
            assert leaf not in text, f"config value {leaf!r} leaked into block {text!r}"

    # ...but the slots are carried (not lost) — they stay CONFIG, available for binding.
    assert load.spec.config == _parsed(FULL)["config"]


# --------------------------------------------------------------------------- #
# 7 — lossless round-trip + determinism
# --------------------------------------------------------------------------- #


def test_lossless_roundtrip_and_determinism() -> None:
    """Raw file carried verbatim; loads, JSON round-trips, and builds are byte-identical."""
    for name in FIXTURES:
        # Lossless: the Source transcript IS the authored file, byte for byte.
        raw = (FIXTURE_DIR / name).read_text(encoding="utf-8")
        first = _load(name)
        assert first.source.transcript == raw

        # Deterministic: two independent loads are byte-identical (EPOCH_ZERO, file order).
        second = _load(name)
        assert first.model_dump_json() == second.model_dump_json()

        # Lossless JSON round-trip: validate(dump) re-dumps byte-identically.
        dumped = first.model_dump_json()
        assert CaseSpecLoad.model_validate_json(dumped).model_dump_json() == dumped

        # Deterministic surface: two builds of the same spec are byte-identical.
        s1 = build_case_report(first, author=AUTHOR)
        s2 = build_case_report(second, author=AUTHOR)
        assert s1.model_dump_json() == s2.model_dump_json()
        assert s1.review.state is ReviewState.DRAFT
