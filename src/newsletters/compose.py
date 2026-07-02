"""COMP-01/02/03 — the module-scope Report composer (Phase 2).

This module assembles the traced ``SectionBinding[]`` that Phase 1's swim-lane loader produces into
ONE ``Surface(REPORT, Draft)`` per module: per-section ``KpiStripBlock`` (with a compose-time Δ) +
``ClaimsBlock``, honest ``missing[]`` routing, deterministic identity. It is where the milestone's
trust risk concentrates (deltas, ordering, prose), so its four properties are enforced *in code*:

* PURE / DETERMINISTIC. ``compute_delta`` is a pure function of its two argument strings — no clock,
  no state — so identical endpoints always derive the identical Δ. ``compose_module_report`` passes
  ``Surface.created = EPOCH_ZERO`` EXPLICITLY (never the ``now()`` default — the confirmed
  determinism trap, 02-PATTERNS.md) and iterates sections/KPIs in FILE ORDER (no ``set()``, no
  non-total sort), so the same load always produces a byte-identical ``model_dump_json``.
* AI-FREE / MINIMAL-CORE. Imports only stdlib + pydantic + the core ``semantic`` / ``swimlane`` /
  ``templates`` / ``adapters._timestamps`` modules. NO ``yaml`` import (the composer is
  loader-agnostic — it consumes ``SwimlaneLoad``, never a config file), NO ``distill``, NO
  ``render``, NO ``models``, no AI package.
* FAITHFUL — SELECTS / ORDERS / LINKS, NEVER AUTHORS. The composer only places already-traced
  ``Claim``s and derives Δ from two independently content-addressed endpoints. Any unprovable thing
  (an untraced claim, an uncomputable movement, a KPI-less section, an empty section set) is routed
  to the module-level ``Surface.missing[]`` — never fabricated. The optional connective
  ``ProseBlock`` carries NO numerals/facts (COMP-03; the numeral-free-prose guard lands in 02-04).
* Δ IS A DERIVATION, NEVER A CLAIM. The delta lives ONLY in ``KpiItem.delta``/``.dir``; it is a
  derivation over two traced endpoints, never itself a ``Claim``, never traced, never rendered as a
  claim. Both endpoints must exist and be numeric BEFORE any delta is computed — either
  absent/non-numeric → ``(delta=None, dir=None)`` + a ``missing[]`` note (NEVER a fabricated 0).
  ``Δ == 0`` is a distinct, honest "no change" (``dir=None``, delta rendered as the computed zero).

IDENTITY & STRUCTURE (Plan 02-03, same file): the sourced-or-omit owner-quote slot, the fan-out
stub (declared kinds, every ``href=None``), and the stable ``R-NNN`` identity via the REUSED,
append-only ``site.Ledger`` against the module's OWN ``content/module/ids.json`` (read/assign-only —
compose never ``save()``s; the caller owns persistence). None of these author a fact: the quote is
rendered only from a traced claim, the fan-out is a declared stub, and the ref comes solely from
``Ledger.ref_for``. The surface still ships ``Draft``.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Literal, Optional

from .adapters._timestamps import EPOCH_ZERO
from .semantic import (
    Claim,
    ClaimsBlock,
    FanoutBlock,
    FanoutLink,
    KpiItem,
    KpiStripBlock,
    ProseBlock,
    QuoteBlock,
    Review,
    Surface,
)
from .site import Ledger, slugify
from .swimlane import SectionBinding, SwimlaneLoad
from .templates import REPORT

__all__ = ["compute_delta", "compose_module_report"]

# --------------------------------------------------------------------------- #
# compute_delta — the pure Δ derivation (COMP-02).
#
# No in-repo delta precedent exists (02-PATTERNS.md "No Analog Found"); this mirrors the pure,
# stateless, argument-only discipline of ``adapters._timestamps.deterministic_timestamp`` — a
# function of its arguments alone, no clock and no state, so repeat calls on identical input are
# byte-identical. The "undefined-as-first-class" logic (either endpoint non-numeric -> None, never a
# fabricated 0) is the genuinely new part and lives here and nowhere else.
# --------------------------------------------------------------------------- #

# A numeric endpoint token: an optional sign + integer/decimal magnitude, then (optionally) a
# trailing non-numeric unit (e.g. "10", "-3.5", "20%"). A token with NO numeric magnitude (``abc``,
# the empty string) does not match -> it is treated as absent (never a fabricated delta).
_NUMBER_RE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(\S*)\s*$")


def _parse_endpoint(token: object) -> Optional[tuple[Decimal, bool, str]]:
    """Parse a numeric endpoint into ``(value, is_float, unit)`` — or ``None`` when non-numeric.

    A pure helper: a non-``str`` or a token carrying no numeric magnitude yields ``None`` (the
    caller discloses the gap; a delta is NEVER derived from an unparseable endpoint). ``is_float`` is
    True iff the magnitude carried a decimal point (so an int pair renders ``"+10"``, not
    ``"+10.0"``). ``unit`` is any trailing non-numeric text, preserved verbatim.
    """
    if not isinstance(token, str):
        return None
    match = _NUMBER_RE.match(token)
    if match is None:
        return None
    number_text, unit = match.group(1), match.group(2)
    try:
        value = Decimal(number_text)
    except InvalidOperation:
        return None
    return value, ("." in number_text), unit


def _format_magnitude(diff: Decimal, is_float: bool) -> str:
    """Format the difference ONCE (no rounding inside a format string; arithmetic already done)."""
    if not is_float:
        return str(int(diff))
    text = format(diff, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def compute_delta(
    start: object, close: object
) -> tuple[Optional[str], Optional[Literal["up", "down"]]]:
    """Derive a signed Δ + direction from two traced numeric endpoints — the LOCKED contract.

    * Both endpoints numeric -> ``(signed_delta, dir)`` where ``dir`` is ``"up"`` for a positive
      difference, ``"down"`` for a negative one, and ``None`` for ``Δ == 0`` (honest no-change; the
      delta is rendered as the computed zero form ``"0"``).
    * Either endpoint absent / non-numeric -> ``(None, None)`` — the caller discloses the gap in
      ``missing[]``; NEVER a fabricated 0.
    * Unit-preserving (discretion): when both tokens carry the SAME trailing non-numeric unit it is
      appended to the delta; a unit is never invented.

    A PURE function of its two arguments — no clock, no state — so repeat calls on identical input
    always return the identical value.
    """
    left = _parse_endpoint(start)
    right = _parse_endpoint(close)
    if left is None or right is None:
        return None, None

    start_val, start_is_float, start_unit = left
    close_val, close_is_float, close_unit = right
    diff = close_val - start_val
    is_float = start_is_float or close_is_float

    direction: Optional[Literal["up", "down"]]
    if diff > 0:
        direction = "up"
    elif diff < 0:
        direction = "down"
    else:
        direction = None

    body = _format_magnitude(diff, is_float)
    if diff > 0:
        body = "+" + body  # negatives already carry their sign; zero stays bare
    unit = start_unit if (start_unit and start_unit == close_unit) else ""
    return (body + unit if unit else body), direction


# --------------------------------------------------------------------------- #
# compose_module_report — kind-agnostic per-section assembly (COMP-01/03).
#
# The composer consumes ``SwimlaneLoad.bindings`` (``SectionBinding[]``) with NO knowledge that
# lanes exist — it iterates them in FILE ORDER as generic sections (prove the seam by composing any
# other ``SectionBinding`` kind with zero composer change). It SELECTS already-traced content and
# ROUTES everything unprovable to a module-level ``missing[]`` (never fabricates), mirroring the
# traced-or-missing policy of ``worksurface.build_work_report`` — but, unlike that analog, it passes
# ``created`` EXPLICITLY so the output is byte-stable.
# --------------------------------------------------------------------------- #


def _slug(source_id: str) -> str:
    """Derive a deterministic, config-derived slug from the load's ``Source.id`` (data, not hardcoded).

    Reuses ``site.slugify`` (never a forked slug rule) over the config identity's filename stem, so
    the composed surface's slug is the SAME key ``site.Site.from_surfaces`` reads later in Phase 3.
    """
    stem = source_id.rsplit("/", 1)[-1]
    if "." in stem:
        stem = stem.rsplit(".", 1)[0]
    return slugify(stem) or "module"


def _title(source_id: str) -> str:
    """A structural, config-derived module label (no computed numerals authored)."""
    stem = source_id.rsplit("/", 1)[-1]
    if "." in stem:
        stem = stem.rsplit(".", 1)[0]
    label = stem.replace("-", " ").replace("_", " ").strip()
    return label.title() if label else "Module"


def _dedup_in_order(items: list[str]) -> list[str]:
    """Order-preserving union (file order preserved; NO ``set()`` -> no non-total ordering)."""
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def _addressed(claim: Claim) -> bool:
    """True iff the claim is traced AND every trace is content-addressed (the trust gate)."""
    return claim.is_traced and all(trace.is_addressed for trace in claim.evidence)


def _compose_kpi_item(
    item: KpiItem, endpoints: list[Claim], missing: list[str]
) -> KpiItem:
    """Emit one display ``KpiItem`` — deriving Δ ONLY from two content-addressed numeric endpoints.

    * ≥2 endpoints, both content-addressed AND numeric -> ``delta``/``dir`` from ``compute_delta``.
    * ≥2 endpoints that are not both computable -> ``delta=None`` + a ``missing[]`` note (a declared
      movement that could not be computed — NEVER a fabricated 0).
    * a single (or zero) endpoint -> a point-in-time value, emitted value-only with NO note.
    """
    delta: Optional[str] = None
    direction: Optional[Literal["up", "down"]] = None
    if len(endpoints) >= 2:
        first, last = endpoints[0], endpoints[-1]
        if _addressed(first) and _addressed(last):
            delta, direction = compute_delta(first.text, last.text)
        if delta is None:
            missing.append(
                f"KPI {item.label!r} declares a movement whose two endpoints are not both "
                "content-addressed numeric values — no delta derived (never a fabricated 0)"
            )
    return KpiItem(label=item.label, value=item.value, delta=delta, dir=direction)


# --------------------------------------------------------------------------- #
# The owner-quote slot (sourced-or-omit) and the fan-out stub (COMP-04 identity/
# structure). Both author NO facts: the quote is rendered ONLY from a claim that
# was already traced from config (verbatim text, owner id as attribution); the
# fan-out is a declared stub whose targets do not exist yet (every href=None).
# --------------------------------------------------------------------------- #

# The audience surfaces this module report declares it will fan out into. STRUCTURAL,
# numeral-free descriptive labels only (the numeral-free-prose guard, 02-04) — never a
# computed fact. ``href`` stays None: the targets do not exist yet, so a fan-out link is
# a declared intent, never a dead/fabricated link (T-02-12; mirrors worksurface's stub).
_FANOUT_STUB: tuple[tuple[str, str], ...] = (
    ("article", "The story behind this module, in prose"),
    ("newsletter", "This module, re-cut for the weekly read"),
    ("learning", "Onboarding: read the module before the config"),
)

# The honesty-panel note disclosed when no traced owner/manager quote was provided — the
# omission is shown to the reviewer, the slot is left empty, and NOTHING is fabricated.
_QUOTE_ABSENT_NOTE = (
    "owner/manager quote not provided — quote slot omitted (never fabricated)"
)

# The attribution used when a quote exists but its lane is unowned: an honesty marker, not
# an invented name (02-CONTEXT.md "unowned lane → 'unassigned'-style honesty").
_UNASSIGNED_ATTR = "unassigned"


def _fanout_stub() -> FanoutBlock:
    """The always-present fan-out stub: declared audience kinds, every ``href=None``."""
    return FanoutBlock(
        heading="What this module produces",
        links=[FanoutLink(kind=kind, title=title) for kind, title in _FANOUT_STUB],
    )


def _quote_block(quote: Optional[Claim], owner: Optional[str]) -> Optional[QuoteBlock]:
    """Return a ``QuoteBlock`` ONLY from a traced+addressed quote claim — else ``None``.

    Sourced-or-omit (T-02-10): a quote is rendered only when ``quote`` is a content-addressed
    ``Claim`` (traced from config); its ``text`` is the claim's verbatim text and its ``attr`` is
    the owner id (a config value) — or the ``"unassigned"`` honesty marker for an unowned lane.
    A missing/untraced/unaddressed quote yields ``None`` (the caller discloses the gap); quote text
    is NEVER fabricated.
    """
    if quote is None or not _addressed(quote):
        return None
    return QuoteBlock(text=quote.text, attr=owner or _UNASSIGNED_ATTR)


def compose_module_report(
    load: SwimlaneLoad,
    *,
    author: str = "operator",
    quote: Optional[Claim] = None,
    owner: Optional[str] = None,
    ledger: Optional[Ledger] = None,
    ledger_path: str = "content/module/ids.json",
) -> Surface:
    """Compose one deterministic ``Surface(REPORT, Draft)`` from a module's ``SectionBinding[]``.

    Per COMP-01 the composer treats each binding as a generic section (kind-agnostic seam): in FILE
    ORDER it emits one ``KpiStripBlock`` (with a compose-time Δ per KPI) then one ``ClaimsBlock`` of
    the section's already-traced claims. Per COMP-03 everything unprovable — an untraced/unaddressed
    claim, an uncomputable movement, a KPI-less section, an empty section set — is routed to the
    module-level ``Surface.missing[]`` (the honesty panel), never fabricated. The surface ships
    ``Draft`` (no ``publish()``, no gate advance) with ``created=EPOCH_ZERO`` and
    ``traces=[load.source]`` so two composes of the same load are byte-identical and Phase-3
    claim-beside-trace rendering works.

    ``author`` names the byline/review author. ``quote`` (a traced owner/manager quote ``Claim``)
    and ``owner`` (the owner id used as its attribution) drive the sourced-or-omit quote slot: a
    ``QuoteBlock`` is emitted ONLY when ``quote`` is content-addressed; otherwise the omission is
    disclosed in ``missing[]`` and the slot stays empty (never a fabricated quote). A fan-out stub
    (declared kinds, every ``href=None``) is always appended.

    ``ledger`` (defaulting to ``Ledger.load(ledger_path)`` over the module's OWN
    ``content/module/ids.json``) is the sequential-ref identity authority: the surface slug is
    recorded via the reused, append-only ``site.Ledger.ref_for`` (immutable on re-sight; the first
    report gets the first ordinal), the SOLE ref source — compose never formats a ref itself, never
    a count-based ordinal. compose does NOT call ``ledger.save()``; persistence is the CALLER's job
    (Phase 3), keeping compose disk-write-free.
    """
    blocks: list = []
    missing: list[str] = []

    # Stable identity: the config-derived slug is BOTH the Surface id and the ledger key, so the
    # ref Site.from_surfaces reads in Phase 3 is the one assigned here. The ref itself comes ONLY
    # from the reused, append-only site.Ledger (never formatted inline, never a count-based ordinal)
    # and lives in the ledger, never in authored prose (a bare ref in prose would trip the numeral guard).
    # compose is READ/ASSIGN-only on the in-memory ledger: it does NOT call ledger.save() —
    # persistence is the CALLER's job (Phase 3's build_module_site mirrors build_work_site:
    # Ledger.load → compose → ledger.save()), keeping compose disk-write-free so tests stay isolated.
    slug = f"report-{_slug(load.source.id)}"
    if ledger is None:
        ledger = Ledger.load(ledger_path)
    ledger.ref_for(slug, "report")  # append-only assign/read; immutable on re-sight.

    # A connective ProseBlock (COMP-03): transitions only — NO numerals, NO facts. Emitted only when
    # there is something to introduce, so an empty module stays honestly bare.
    if load.bindings:
        blocks.append(
            ProseBlock(
                heading="How this module is tracking",
                text=(
                    "Each section below reports only what its record can prove; anything the "
                    "record cannot substantiate is listed in the honesty panel."
                ),
            )
        )

    for (
        binding
    ) in load.bindings:  # FILE ORDER — never a set / non-total sort (Pitfall 6)
        endpoints_by_kpi = binding.kpi_endpoints
        items: list[KpiItem] = []
        for index, kpi in enumerate(binding.kpi_items):
            endpoints = endpoints_by_kpi[index] if index < len(endpoints_by_kpi) else []
            items.append(_compose_kpi_item(kpi, endpoints, missing))

        if binding.kpi_items:
            blocks.append(KpiStripBlock(heading=binding.heading, items=items))
        else:
            missing.append(
                f"section {binding.heading!r} declares no KPIs — strip omitted"
            )

        # Traced-or-missing: SELECT content-addressed claims; route the rest to missing[].
        kept: list[Claim] = []
        for claim in binding.claims:
            if _addressed(claim):
                kept.append(claim)
            else:
                missing.append(claim.text)
        blocks.append(ClaimsBlock(claims=kept))

        # Union in every section's own declared gaps (file order).
        missing.extend(binding.missing)

    if not load.bindings:
        missing.append(
            "module config declares no sections — nothing to compose (Draft with no blocks)"
        )

    # Sourced-or-omit owner/manager quote: emit a QuoteBlock ONLY from a traced claim; otherwise
    # disclose the omission in missing[] and leave the slot empty (never a fabricated quote).
    quote_block = _quote_block(quote, owner)
    if quote_block is not None:
        blocks.append(quote_block)
    else:
        missing.append(_QUOTE_ABSENT_NOTE)

    # The fan-out stub is ALWAYS present (a declared intent, every href=None).
    blocks.append(_fanout_stub())

    return Surface(
        id=slug,
        template=REPORT,
        title=_title(load.source.id),
        eyebrow="Report · module scope",
        blocks=blocks,
        traces=[load.source],
        missing=_dedup_in_order(missing),
        byline=[author],
        review=Review(policy=REPORT.review_policy, author=author),
        created=EPOCH_ZERO,
    )
