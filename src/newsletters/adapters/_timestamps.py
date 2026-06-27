"""The shared deterministic-timestamp helper for ALL file adapters (CONTEXT decision 0 / L1).

WHY this exists. Every file adapter sets ``Source.timestamp`` from the document's INTRINSIC date —
the email ``Date`` header, the xlsx docProps ``created``, the pptx ``core_properties.created``. When
that intrinsic date is absent, the old code let ``Source.timestamp`` fall back to its default
factory (``semantic._utcnow()`` — wall-clock ``datetime.now(utc)``). That fallback is
NON-DETERMINISTIC: two parses of the SAME bytes of a real document with no intrinsic date produce
different timestamps, and therefore non-equal Sources — silently breaking the determinism and
round-trip-parity property the whole adapter contract depends on (a persisted Source must
re-distill identically).

THE FIX. Replace the wall-clock fallback with a FIXED, deterministic sentinel: ``EPOCH_ZERO``
(1970-01-01T00:00:00Z). Why a fixed sentinel rather than ``now()`` or a content-derived value:

* Deterministic — identical bytes always map to the identical Source (the property we need).
* Obvious to a reviewer — ``1970-01-01`` reads unmistakably as "no intrinsic date was present",
  not as a real publication time that could mislead. (Threat T-06-02: accepted; a sentinel is an
  honest "unknown date" marker, intrinsic dates are preserved verbatim.)
* Free of side effects — no clock read, no hashing, no new dependency.

CLAIMS ARE PROVABLY UNAFFECTED. ``Source.content_hash()`` addresses the TRANSCRIPT only (see
``semantic.py`` — timestamp is excluded from the hash); changing the timestamp fallback therefore
cannot change any ``Claim``/``Trace`` content address. The round-trip parity matrix and the email
Date-header test stay green.

Adapters MUST always pass ``timestamp=deterministic_timestamp(<intrinsic>)`` explicitly so NO code
path relies on the ``Source`` default factory. ``semantic.py`` is intentionally NOT modified
(``Source.timestamp`` stays non-optional with its ``_utcnow`` default — L1 option iii, making it
Optional, was rejected as an out-of-scope spine change). The fix lives entirely in the adapters.

Stdlib only (``datetime``); no Pydantic, no AI, no new dependency — safe to import from the bare,
AI-free core path.
"""

from __future__ import annotations

from datetime import datetime, timezone

__all__ = ["EPOCH_ZERO", "deterministic_timestamp"]

# The deterministic "no intrinsic date" sentinel: tz-aware UTC 1970-01-01T00:00:00+00:00.
EPOCH_ZERO = datetime(1970, 1, 1, tzinfo=timezone.utc)


def deterministic_timestamp(intrinsic: datetime | None) -> datetime:
    """Return a DETERMINISTIC ``Source.timestamp`` from a document's intrinsic date.

    * ``intrinsic is None`` -> ``EPOCH_ZERO`` (the deterministic sentinel; NEVER ``now()``).
    * a tz-aware ``intrinsic`` -> returned unchanged (the document's date, preserved verbatim).
    * a tz-naive ``intrinsic`` -> coerced to UTC via ``replace(tzinfo=timezone.utc)`` so the result
      is always tz-aware and deterministic regardless of the parser's tz handling (openpyxl, for
      example, returns ``created`` tz-naive).

    A pure function of its argument — no clock, no state — so repeated calls on identical input
    always return the identical value.
    """
    if intrinsic is None:
        return EPOCH_ZERO
    if intrinsic.tzinfo is None:
        return intrinsic.replace(tzinfo=timezone.utc)
    return intrinsic
