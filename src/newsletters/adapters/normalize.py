"""The shared faithful ``normalize()`` — the ONE place the faithful-extraction rule lives (ADAPT-01).

Every present and future adapter (Email today; Excel, PPTX, Power BI later) does its own
format-specific raw extraction into intermediate "units" (verbatim strings it sliced from the
transcript it built), then hands those units to THIS function. ``normalize()`` is the single
faithfulness gate they all pass through — so the trust rule is defined once and inherited
everywhere, never reimplemented per adapter (CONTEXT decision 1).

The rule, stated once:

    Each unit must be located VERBATIM in ``source.transcript`` by a cursor-advancing
    ``str.find``. A locatable unit is minted into a content-addressed ``Claim(+Trace)`` via
    ``Trace.from_source`` — the SOLE trace-minting path (adapters never compute a hash). A unit
    that is NOT verbatim-locatable is routed to the returned ``unextracted[]`` list, NEVER
    fabricated and NEVER paraphrased. "Faithful, not suggestive."

WHY a cursor (not ``find`` from 0 every time): two identical units (e.g. duplicate paragraphs)
would otherwise both resolve to the FIRST occurrence's offset, giving the second claim wrong
provenance. Advancing ``cursor`` past each match means duplicate units get DISTINCT, correct
offsets, and consumed text is never re-pointed at (forward-only, non-overlapping provenance).

WHY this output survives the Phase-3 gate: every emitted ``claim.text == unit == transcript[idx:end]
== trace.span``, so ``SpanContainmentFaithfulness._normalize(claim.text) in _normalize(trace.span)``
is trivially True (``faithfulness.py:62-74``). And a non-empty ``unextracted[]`` forces a wrapping
``Coverage`` to ``complete=False`` (the validator makes the alternative unrepresentable,
``coverage.py:54-67``).

HARD RULE — AI-optional core / format-agnostic: this module imports ONLY ``..semantic``,
``..locators``, and ``..distill.coverage`` (all stdlib + Pydantic underneath). It MUST NOT import
``email`` (or any adapter-specific module), compute any SHA-256, or hand-mint a ``content_hash`` —
``Trace.from_source`` already validates offsets before slicing and pins the hash
(``semantic.py:109-153``). It uses a FreeLocator content preview for unextracted units, never an
ordinal/positional anchor (forbidden, ``locators.py:17-19``).
"""

from __future__ import annotations

from ..distill.coverage import Unextracted
from ..locators import FreeLocator
from ..semantic import Claim, Source, Trace

# How many characters of a non-locatable unit to keep as the content-anchor preview. A content
# preview (not an ordinal index) is what `locators.py:17-19` requires; truncation keeps the
# locator small even for a pathologically long unit.
_PREVIEW_CHARS = 60

_NOT_LOCATABLE_REASON = "unit not verbatim-locatable in transcript (faithful, not suggestive)"


def normalize(source: Source, units: list[str]) -> tuple[list[Claim], list[Unextracted]]:
    """Mint a content-addressed ``Claim(+Trace)`` for every unit locatable VERBATIM in ``source``.

    This is the single shared faithful-extraction gate (ADAPT-01). It is the leaf dependency the
    Email adapter (Plan 02) — and every future adapter — calls after format-specific extraction.

    Args:
        source: The ``Source`` whose ``transcript`` the units were sliced from. ``transcript`` is
            the single source of truth: each unit MUST be an exact substring of it, or it is routed
            to ``unextracted[]``. Traces are content-addressed against ``source.content_hash()``.
        units: An ordered list of raw unit strings the adapter extracted, IN TRANSCRIPT ORDER
            (a header value, a body paragraph, …). Order matters: the cursor advances monotonically,
            so units must be presented in the order they appear in the transcript. Each is treated
            as a verbatim candidate span — the adapter does NOT pass offsets; ``normalize`` locates
            them. (Units the adapter ALREADY knows are unreadable — a PDF attachment, a forwarded
            message — are the adapter's own ``unextracted[]`` entries and are NOT passed here; this
            function only handles the verbatim-locate decision.)

    Returns:
        A ``(claims, unextracted)`` 2-tuple:
          * ``claims`` — one ``Claim`` per locatable unit, in input order. Each has exactly one
            evidence ``Trace`` minted via ``Trace.from_source`` (``is_addressed is True``,
            ``span == claim.text == transcript[start:end]``).
          * ``unextracted`` — one ``Unextracted`` per non-locatable unit, with a ``FreeLocator``
            carrying a truncated content preview and a fixed ``reason``. NEVER a fabricated claim.

    Edge-case behavior (documented for the 04-02 adapter author):
        * Empty ``units`` -> ``([], [])``.
        * Empty unit ``""`` -> ``str.find("", cursor)`` returns ``cursor``, so an empty unit is a
          locatable ZERO-WIDTH span: it mints a ``Claim(text="", span="")`` (faithful — "" is a
          substring of anything). It does NOT advance the cursor.
        * Unit longer than the remaining transcript, or simply absent -> ``find == -1`` -> routed
          to ``unextracted[]``.
        * Overlapping / out-of-order units -> the cursor is forward-only: a unit that begins BEFORE
          the cursor (already consumed) is not re-located backwards and routes to ``unextracted[]``.
        * Duplicate identical units -> resolved to DISTINCT, increasing offsets via the cursor.

    Offsets are CHARACTER-based (matching ``Trace.from_source``), not byte-based.
    """
    transcript = source.transcript
    claims: list[Claim] = []
    unextracted: list[Unextracted] = []
    cursor = 0

    for unit in units:
        idx = transcript.find(unit, cursor)
        if idx == -1:
            # Not verbatim-locatable from here -> NEVER fabricate. Account for it honestly with a
            # CONTENT anchor (a truncated preview), never an ordinal index (locators.py:17-19).
            unextracted.append(
                Unextracted(
                    locator=FreeLocator(text=unit[:_PREVIEW_CHARS]),
                    reason=_NOT_LOCATABLE_REASON,
                )
            )
            continue

        end = idx + len(unit)
        # Trace.from_source is the SOLE minting path: it validates 0 <= start <= end <= len before
        # slicing (so a bad range raises rather than silently mis-attributing), pins the content
        # hash, and stores span = transcript[idx:end] verbatim. Adapters never hash here.
        trace = Trace.from_source(source, idx, end)
        claims.append(Claim(text=unit, evidence=[trace]))
        cursor = end  # advance so duplicates get distinct, forward-only offsets

    return claims, unextracted
