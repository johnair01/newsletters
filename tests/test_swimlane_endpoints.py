"""COMP-02 endpoint-pairing proof — SectionBinding.kpi_endpoints is reference-only and aligned.

This is the executable contract for the ADDITIVE ``kpi_endpoints`` field (Plan 02-01): it drives the
LIVE loader (``src/newsletters/swimlane.py``) over the SAME two committed fixtures the Phase-1 suite
uses and proves the invariants Phase-2's composer relies on to derive Δ from two INDEPENDENTLY
content-addressed endpoints. Following ``test_swimlane.py``'s discipline, it imports the loader's OWN
constants/models (no inline literal duplication -> no drift) and asserts STRUCTURE and INVARIANTS,
reading every concrete count/value from the SAME parsed fixture the loader read (never a frozen magic
value; Pitfall 8).

The invariants proven here:

1. **Alignment** — for every binding, ``len(kpi_endpoints) == len(kpi_items)`` (element i pairs
   kpi_items[i]).
2. **Reference-not-re-mint** — every ``Claim`` in ``kpi_endpoints`` is ``is``-identical to a ``Claim``
   in that binding's ``claims`` list (object identity), so no scalar is double-counted.
3. **Coverage identity intact** — ``len(all_claims) + len(all_unextracted) == scalars_walked`` still
   holds on both fixtures (the field added ZERO new mints).
4. **Ordering** — a ``values:``-list KPI's entry carries its endpoint Claims in FILE ORDER (start
   before close), each ``.text`` equal to the raw endpoint token, each trace ``is_addressed``.
5. **No fabricated endpoint** — a KPI whose ``values:`` was disclosed (the trap's mapping-shaped
   slot) contributes FEWER than two references — never a placeholder.

This file does NOT edit ``tests/test_swimlane.py`` or ``tests/test_abstraction_guard.py``.
"""

from __future__ import annotations

import pathlib
from typing import Any

from newsletters._yaml_loader import load_config
from newsletters.semantic import Claim
from newsletters.swimlane import (
    _KPIS_KEY,
    _VALUES_KEY,
    SwimlaneLoad,
    load_swimlanes,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "swimlane"
FIXTURES = ["module-x.yml", "module-trap.yml"]


def _load(name: str) -> SwimlaneLoad:
    """Load one committed fixture through the LIVE loader, rooted at the repo (stable ``Source.id``)."""
    return load_swimlanes(FIXTURE_DIR / name, root=REPO_ROOT)


def _parsed(name: str) -> Any:
    """Parse the same fixture the loader reads, so value assertions track the config (safe_load)."""
    return load_config((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _dict_kpis(lane: Any) -> list[dict[str, Any]]:
    """The KPI entries the loader actually binds 1:1 into ``kpi_items``/``kpi_endpoints``.

    ``_bind_kpis`` appends one ``kpi_items``/``kpi_endpoints`` element per DICT entry (a non-dict
    entry is walked generically and skipped), so filtering the parsed lane's ``kpis`` to its dict
    entries — in file order — reproduces the binding's KPI ordering without duplicating loader logic.
    """
    return [k for k in lane.get(_KPIS_KEY, []) if isinstance(k, dict)]


def test_kpi_endpoints_align_with_kpi_items() -> None:
    """Alignment: every binding has exactly one endpoint list per KPI item, on BOTH fixtures.

    ``len(kpi_endpoints) == len(kpi_items)`` is the load-bearing lockstep guarantee — element i is
    kpi_items[i]'s ordered endpoint references — so the composer can index them together safely.
    """
    for name in FIXTURES:
        load = _load(name)
        assert load.bindings, f"{name}: expected at least one binding"
        for binding in load.bindings:
            assert len(binding.kpi_endpoints) == len(binding.kpi_items), (
                f"{name}: kpi_endpoints ({len(binding.kpi_endpoints)}) misaligned with "
                f"kpi_items ({len(binding.kpi_items)}) in lane {binding.heading!r}"
            )


def test_endpoints_are_references_not_re_mints() -> None:
    """Reference-not-re-mint: every endpoint Claim is ``is``-identical to a Claim in ``claims``.

    Object identity (``is``, not ``==``) proves the endpoint list re-references the SAME Claim objects
    the loader already appended to ``binding.claims`` — never a fresh mint. A re-mint would double
    count and the coverage identity would break (asserted separately below); this is the direct proof.
    """
    for name in FIXTURES:
        load = _load(name)
        for binding in load.bindings:
            for endpoints in binding.kpi_endpoints:
                for claim in endpoints:
                    assert isinstance(claim, Claim)
                    assert any(claim is c for c in binding.claims), (
                        f"{name}: endpoint {claim.text!r} in lane {binding.heading!r} is not "
                        "object-identical to any Claim in binding.claims — it was re-minted"
                    )


def test_coverage_identity_unaffected_by_endpoints() -> None:
    """The added field mints nothing: the read-anchored coverage identity still holds on both fixtures.

    ``len(all_claims) + len(all_unextracted) == scalars_walked`` — if populating ``kpi_endpoints`` had
    re-minted any endpoint (rather than referencing an existing Claim), this equation would drift.
    """
    for name in FIXTURES:
        load = _load(name)
        assert (
            len(load.all_claims) + len(load.all_unextracted) == load.scalars_walked
        ), f"{name}: coverage identity broken — endpoints added a mint"


def test_values_list_endpoints_ordered_and_addressed() -> None:
    """Ordering: a ``values:``-list KPI carries its endpoints in file order, each traced+addressed.

    Over the clean fixture (every endpoint verbatim-locatable), for each KPI declaring ``values:`` as
    a list, its ``kpi_endpoints`` entry has one Claim per endpoint whose ``.text`` equals the raw
    endpoint token IN FILE ORDER (start before close), with strictly increasing forward-cursor offsets
    and every trace content-addressed. Value tokens are read from the SAME parsed fixture (never
    frozen).
    """
    load = _load("module-x.yml")
    parsed = _parsed("module-x.yml")
    lanes = parsed["lanes"]

    checked = 0
    for lane, binding in zip(lanes, load.bindings):
        for kpi, endpoints in zip(_dict_kpis(lane), binding.kpi_endpoints):
            values = kpi.get(_VALUES_KEY)
            if not isinstance(values, list):
                continue
            expected = [str(v) for v in values]
            # One endpoint reference per declared endpoint (clean fixture: all locatable).
            assert [c.text for c in endpoints] == expected, (
                f"endpoints for KPI {kpi.get('label')!r} not in file order: "
                f"{[c.text for c in endpoints]} != {expected}"
            )
            assert len(endpoints) >= 2, "a period-endpoint KPI must pair >=2 endpoints"
            # Each endpoint is independently content-addressed, forward-only (start before close).
            starts = []
            for claim in endpoints:
                assert claim.evidence, f"endpoint {claim.text!r} is untraced"
                trace = claim.evidence[0]
                assert (
                    trace.is_addressed
                ), f"endpoint {claim.text!r} trace not addressed"
                assert trace.start is not None
                starts.append(trace.start)
            assert starts == sorted(starts) and len(set(starts)) == len(
                starts
            ), f"endpoint offsets not strictly forward-ordered: {starts}"
            checked += 1
    assert (
        checked
    ), "module-x.yml must declare at least one values:-list KPI to exercise ordering"


def test_disclosed_endpoints_yield_no_fabricated_reference() -> None:
    """No fabricated endpoint: a mapping-shaped ``values:`` KPI carries fewer than two references.

    The trap fixture's mapping-shaped ``values:`` slot is disclosed (its scalars are still traced into
    ``claims`` and a ``missing[]`` note is added) but is NOT a list of period endpoints — so its
    ``kpi_endpoints`` entry must hold FEWER than two references (no placeholder for an unpaired
    endpoint), guaranteeing a delta can never be derived from an invented endpoint.
    """
    load = _load("module-trap.yml")
    parsed = _parsed("module-trap.yml")
    lanes = parsed["lanes"]

    checked = 0
    for lane, binding in zip(lanes, load.bindings):
        for kpi, endpoints in zip(_dict_kpis(lane), binding.kpi_endpoints):
            if isinstance(kpi.get(_VALUES_KEY), dict):
                assert len(endpoints) < 2, (
                    f"mapping-shaped values KPI {kpi.get('label')!r} fabricated endpoint "
                    f"references: {[c.text for c in endpoints]}"
                )
                checked += 1
    assert (
        checked
    ), "module-trap.yml must contain a mapping-shaped values: slot to exercise the trap"
