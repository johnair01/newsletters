"""LANE-01/LANE-02 proof suite — the swim-lane loader is honest and deterministic (Plan 01-03).

This module is the phase's circuit-breaker *proof*: two tiny committed fixtures under
``tests/fixtures/swimlane/`` drive the LIVE loader (``src/newsletters/swimlane.py``) end to end and
assert its load-bearing invariants — never asserting a specific lane name/value (Pitfall 8), always
STRUCTURE and INVARIANTS. Where a concrete value is needed it is read from the SAME parsed fixture
the loader reads, so the assertion tracks the config rather than freezing a magic string.

* ``module-x.yml`` — a well-formed module config: N lanes in -> N dict-level ``SectionBinding``s out
  (LANE-01), every scalar verbatim-locatable (24 claims, 0 unextracted).
* ``module-trap.yml`` — an adversarial fixture packing each scalar-location trap (anchor/alias,
  block scalar, ``yes``->True coercion, a value repeated across two KPIs, quoted scalars, a
  mapping-shaped ``values:`` slot). Its exact scalar set is the executable contract.

The invariants proven here:

1. **Read-anchored coverage identity** (LANE-02, Pitfall 9 / the Phase-7 silent-drop lesson):
   ``len(all_claims) + len(all_unextracted) == scalars_walked`` on the trap fixture, cross-checked
   against an INDEPENDENT scalar-leaf count of the parsed structure, with the EXACT ordered ``_R_*``
   reasons pinned via the loader's OWN constants (no inline string duplication -> no drift).
2. **Faithful spans** — every emitted claim is verbatim: ``claim.text == trace.span`` AND re-slicing
   ``source.transcript[start:end]`` reproduces it, content-addressed and non-stale.
3. **Hole B closed upstream** (LANE-02) — every trace the loader emits ``is_addressed``; an
   adversarial un-addressed trace is CAUGHT by the same guard, not silently passed.
4. **Determinism** (SITE-06) — two loads of the same file are byte-identical.

The expected trap counts/reasons below were derived by DRIVING the live loader (never assumed) and
validated as HONEST behavior (not authored around a loader gap — the RETRO Phase-7 lesson).
"""

from __future__ import annotations

import pathlib
from typing import Any

from newsletters import models
from newsletters._yaml_loader import load_config
from newsletters.semantic import Claim, KpiItem, Source, Trace
from newsletters.swimlane import (
    _HEADING_KEY,
    _KPIS_KEY,
    _LABEL_KEY,
    _R_ANCHOR_ALIAS,
    _R_BLOCK_SCALAR,
    _R_TYPE_COERCED,
    _VALUES_KEY,
    SectionBinding,
    SwimlaneLoad,
    load_swimlanes,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "swimlane"
FIXTURES = ["module-x.yml", "module-trap.yml"]

# The EXACT ordered unextracted reasons the loader emits for module-trap.yml, pinned via the
# loader's OWN module-level constants (import, never inline-duplicate -> no drift). The order is
# the FILE/WALK order: the aliased reviewer, then the multi-line block-scalar note, then the
# ``yes``->True coerced KPI value. Derived by driving the live loader; each is honest routing.
EXPECTED_TRAP_REASONS = [_R_ANCHOR_ALIAS, _R_BLOCK_SCALAR, _R_TYPE_COERCED]


def _load(name: str) -> SwimlaneLoad:
    """Load one committed fixture through the LIVE loader, rooted at the repo (stable ``Source.id``)."""
    return load_swimlanes(FIXTURE_DIR / name, root=REPO_ROOT)


def _parsed(name: str) -> Any:
    """Parse the same fixture the loader reads, so value assertions track the config (safe_load)."""
    return load_config((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _count_scalar_leaves(node: object) -> int:
    """Independently count the non-null scalar leaves in a parsed doc (mirrors the loader's walk).

    Mapping VALUES and list items are recursed; mapping KEYS are structure (never counted); a
    ``None`` leaf is a declared-but-absent slot (nothing READ, not counted). This is the INDEPENDENT
    yardstick the loader's ``scalars_walked`` must equal — proving the coverage identity is anchored
    to what actually exists in the config, not to a self-consistent-but-wrong internal tally.
    """
    if isinstance(node, dict):
        return sum(_count_scalar_leaves(v) for v in node.values())
    if isinstance(node, list):
        return sum(_count_scalar_leaves(v) for v in node)
    if node is None:
        return 0
    return 1


def test_no_yaml_scalar_is_read_but_undisclosed() -> None:
    """LANE-02: every scalar READ off the trap fixture is a claim or a disclosed gap — zero drops.

    The read-anchored coverage identity, cross-checked against an INDEPENDENT scalar-leaf count of
    the parsed structure (so a loader that walked too few *or* too many scalars is caught), plus the
    EXACT ordered ``_R_*`` reasons via the loader's own constants, plus the mapping-shaped ``values:``
    disclosure (loader commit 40976cc): an empty display value AND a ``missing[]`` note.
    """
    load = _load("module-trap.yml")
    parsed = _parsed("module-trap.yml")

    # (a) the loader walked EXACTLY the scalar leaves present in the config — no more, no fewer.
    assert load.scalars_walked == _count_scalar_leaves(parsed)

    # (b) THE identity: every walked scalar landed on exactly one side of the ledger (no silent drop).
    assert len(load.all_claims) + len(load.all_unextracted) == load.scalars_walked

    # (c) the exact ordered routing reasons, pinned via the loader's OWN constants (no inline dup).
    assert [u.reason for u in load.all_unextracted] == EXPECTED_TRAP_REASONS

    # (d) ADDITIONAL REQUIRED CASE (loader commit 40976cc): a mapping-shaped `values:` slot yields
    #     an EMPTY display value AND a missing[] disclosure — never an empty value with no note.
    lanes = parsed["lanes"]
    mapping_trap = [
        (li, kpi[_LABEL_KEY])
        for li, lane in enumerate(lanes)
        for kpi in lane.get(_KPIS_KEY, [])
        if isinstance(kpi, dict) and isinstance(kpi.get(_VALUES_KEY), dict)
    ]
    assert mapping_trap, "trap fixture must contain a mapping-shaped values: slot"
    expected_missing = (
        f"KPI declares '{_VALUES_KEY}' but not as a list of period endpoints"
    )
    for li, label in mapping_trap:
        binding = load.bindings[li]
        assert expected_missing in binding.missing
        hit = [k for k in binding.kpi_items if k.label == label]
        assert hit and all(
            k.value == "" for k in hit
        ), f"mapping-shaped values KPI {label!r} must display empty, got {[k.value for k in hit]}"

    # (e) the forward-only cursor gives DUPLICATE values DISTINCT offsets (never re-points at the
    #     first occurrence) — proven generically over any claim text that appears more than once.
    starts_by_text: dict[str, list[int | None]] = {}
    for claim in load.all_claims:
        for trace in claim.evidence:
            starts_by_text.setdefault(claim.text, []).append(trace.start)
    duplicates = {t: s for t, s in starts_by_text.items() if len(s) > 1}
    assert (
        duplicates
    ), "trap fixture must repeat at least one value to exercise the forward cursor"
    for text, starts in duplicates.items():
        assert len(set(starts)) == len(
            starts
        ), f"duplicate value {text!r} got a re-pointed (non-distinct) offset: {starts}"


def test_faithful_spans() -> None:
    """Every emitted claim is FAITHFUL: verbatim span, content-addressed, non-stale (both fixtures).

    ``claim.text == trace.span`` AND re-slicing the LIVE transcript at ``[start:end]`` reproduces it;
    the trace pinned the source's content hash and is not stale. (KpiItem carries display strings
    only; the traced provenance for every KPI value lives in the binding's ``claims`` asserted here.)
    """
    for name in FIXTURES:
        load = _load(name)
        source: Source = load.source
        assert load.all_claims, f"{name}: expected at least one minted claim"
        for claim in load.all_claims:
            assert claim.is_traced, f"{name}: claim {claim.text!r} is untraced"
            for trace in claim.evidence:
                # content-addressed (minted via Trace.from_source, which pins content_hash)
                assert (
                    trace.is_addressed
                ), f"{name}: {claim.text!r} trace not content-addressed"
                # faithful: the stored span IS the claim text
                assert (
                    claim.text == trace.span
                ), f"{name}: text != span for {claim.text!r}"
                # re-slice the live transcript at the recorded window -> reproduces the text
                assert trace.start is not None and trace.end is not None
                assert (
                    source.transcript[trace.start : trace.end] == claim.text
                ), f"{name}: transcript[{trace.start}:{trace.end}] != {claim.text!r}"
                # content-address matches the live source, and is not stale against it
                assert trace.content_hash == source.content_hash()
                assert not trace.is_stale_against(source)


def test_lanes_bind_at_dict_level() -> None:
    """LANE-01: N configured lanes -> N dict-level ``SectionBinding``s, in file order, no models types.

    Asserts on STRUCTURE and counts read from the SAME fixture (never a hardcoded lane name): each
    lane's heading and KPI count flow 1:1 into its binding, and the bound objects are the display
    types (``SectionBinding``/``KpiItem``/``Claim`` from swimlane/semantic), NEVER the domain
    ``models.FunctionalGroup``/``models.Kpi`` — proving the lane is bound at the parsed-dict level.
    """
    load = _load("module-x.yml")
    parsed = _parsed("module-x.yml")
    lanes = parsed["lanes"]

    # N lanes in -> N bindings out, in file order.
    assert len(load.bindings) == len(lanes)

    for lane, binding in zip(lanes, load.bindings):
        # heading tracked from the parsed fixture (config-tracking, not a frozen magic string).
        assert binding.heading == lane[_HEADING_KEY]
        # each lane's KPI entries become kpi_items 1:1.
        assert len(binding.kpi_items) == len(lane.get(_KPIS_KEY, []))
        # a lane binds actual traced content.
        assert binding.claims

        # bound at DICT level: display types only, never domain models (LANE-01 / CONTEXT decision).
        assert isinstance(binding, SectionBinding)
        assert type(binding).__module__ == "newsletters.swimlane"
        assert not isinstance(binding, (models.FunctionalGroup, models.Kpi))
        for kpi in binding.kpi_items:
            assert isinstance(kpi, KpiItem)
            assert not isinstance(kpi, (models.FunctionalGroup, models.Kpi))
        for claim in binding.claims:
            assert isinstance(claim, Claim)
            assert not isinstance(claim, (models.FunctionalGroup, models.Kpi))


def test_every_emitted_trace_is_addressed() -> None:
    """LANE-02 / Hole B: every loader trace is content-addressed, and an un-addressed one is CAUGHT.

    Positive half: across BOTH fixtures, every trace on every emitted claim ``is_addressed`` — no
    un-addressed free-pass trace ever leaves the loader (Hole B closed upstream, not merely trusted
    to the downstream gate). Adversarial half: hand-build a ``Claim`` carrying a bare ``Trace`` with
    ``content_hash=None`` (un-addressed) and prove the SAME predicate that passes for every loader
    claim REJECTS it — so the guard demonstrably distinguishes addressed from un-addressed, rather
    than passing vacuously (the RETRO Phase-7 "prove it FIRES" discipline).
    """

    def all_addressed(claim: Claim) -> bool:
        """The guard: True iff every trace on this claim pinned a content hash (is_addressed)."""
        return bool(claim.evidence) and all(t.is_addressed for t in claim.evidence)

    # Positive: no un-addressed trace escapes the loader, on either fixture.
    for name in FIXTURES:
        load = _load(name)
        assert load.all_claims, f"{name}: expected at least one claim to guard"
        for claim in load.all_claims:
            assert all_addressed(
                claim
            ), f"{name}: {claim.text!r} carries an un-addressed trace"

    # Adversarial: an un-addressed trace (content_hash=None) is CAUGHT by that same guard.
    source = _load("module-x.yml").source
    bad_trace = Trace(source_id=source.id, span="fabricated")  # never content-addressed
    assert bad_trace.is_addressed is False
    bad_claim = Claim(text="fabricated", evidence=[bad_trace])
    assert (
        all_addressed(bad_claim) is False
    ), "the guard must REJECT an un-addressed trace"

    # ...and the identical guard PASSES for a real loader claim — it is not vacuously false.
    real_claim = _load("module-trap.yml").all_claims[0]
    assert all_addressed(real_claim) is True


def test_load_is_byte_stable() -> None:
    """SITE-06 determinism: two loads of the same file are byte-identical (Source + bindings + load).

    Proves the ``EPOCH_ZERO`` timestamp, file-order iteration, and no ``set()``-induced reordering:
    ``model_dump_json`` of the Source, of each SectionBinding, and of the whole ``SwimlaneLoad`` are
    equal across two independent loads (mirrors test_worksurface.py's byte-identical double-load).
    """
    for name in FIXTURES:
        first = _load(name)
        second = _load(name)
        assert first.source.model_dump_json() == second.source.model_dump_json()
        assert [b.model_dump_json() for b in first.bindings] == [
            b.model_dump_json() for b in second.bindings
        ]
        # whole-load byte equality (Source + bindings + module-level claims/unextracted + count).
        assert first.model_dump_json() == second.model_dump_json()
