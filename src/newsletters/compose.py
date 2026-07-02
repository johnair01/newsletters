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

NON-GOALS (deferred to Plan 02-03, same file, next wave): the owner-quote slot, the fanout stub, and
the ``R-NNN`` identity ledger (``from .site import Ledger``). This plan lands ``compute_delta`` and
``compose_module_report`` core only.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Literal, Optional

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
