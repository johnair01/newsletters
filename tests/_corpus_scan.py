"""The shared synthetic-content scanner for every committed corpus (promoted, Phase 4 plan 04-01).

PROMOTED, NOT COPIED. ``_REAL_LOOKING_LITERALS`` / ``_EMAIL_RE`` / ``_scan_real_looking`` were
written for ``tests/test_modulesite.py`` and are MOVED here verbatim (their comments carried
unchanged) the moment a second committed corpus — ``content/weekly/`` — needs the same
confidentiality guard. This repo's norm is promotion over a second copy: ``specspan.SpanMinter``,
``compose.compose_kpi_item`` and ``pptx_writer.normalize_opc_zip`` were each promoted for exactly
this reason, because two copies of a trust predicate drift. One scanner, two corpora.

The leading underscore keeps pytest from collecting this module as a test module, so no CI job's
test-module list changes. Corpus-SPECIFIC vocabulary stays with its corpus: the module corpus's
``_FABRICATED_MARKERS`` allowlist remains in ``tests/test_modulesite.py``, and the weekly corpus's
``@example.invalid`` allowance remains in ``tests/test_weeklysite.py`` — an allowance is only
legible next to the corpus that earns it.
"""

from __future__ import annotations

import re

__all__ = ["EMAIL_RE", "REAL_LOOKING_LITERALS", "scan_real_looking"]

# Representative real-looking nomenclature that must NEVER appear in committed public content.
# Multi-word / distinctive tokens only, so a substring scan cannot false-positive on ordinary
# words or the design-system's font-family names.
REAL_LOOKING_LITERALS = frozenset(
    {
        "Jean-Luc Picard",
        "William Riker",
        "Geordi La Forge",
        "Beverly Crusher",
        "Starfleet Division",
        "USS Enterprise",
        "Warp Core Stability",
        "Dilithium Efficiency Index",
        "starfleet.int",
    }
)

# A real-name SHAPE: an email address (the committed corpus declares none — its presence would be a
# confidentiality leak). Bounded so CSS at-rules (@font-face / @media) never match (no word char
# precedes their '@').
EMAIL_RE = re.compile(r"\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b")


def scan_real_looking(text: str) -> set[str]:
    """Return the real-looking nomenclature found in ``text`` (empty == clean/synthetic)."""
    hits = {tok for tok in REAL_LOOKING_LITERALS if tok in text}
    hits.update(EMAIL_RE.findall(text))
    return hits
