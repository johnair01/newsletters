"""Abstraction-guard — no fixture/org/config-specific name may live in ``src/newsletters/`` (LANE-03).

WHY THIS TEST EXISTS (CONTEXT "ABSTRACT EVERYTHING", JJ's fundamental principle 2026-07-02 +
threat T-04-01): data MODELS live in code; module/lane/owner/metric SPECIFICS live in YAML config
ONLY. A concrete fixture id (``lane-a``, ``module-x``, ``owner-1``) or — worse — a real-looking
org/crew/metric name (``jean-luc``, ``Starfleet Division``, ``Warp Core Stability``) hardcoded into
``src/newsletters/`` is BOTH an abstraction breach (the loader would stop generalizing over an
arbitrary org's team shape) AND a confidentiality risk (source is public). This guard fails the
suite the instant such a token leaks into source — the invariant enforced IN CODE, not in a comment.

MECHANIC (mirrors ``test_ai_optional.py:284-304``'s "read the module text, assert a forbidden
pattern is absent" shape, different needle set): walk every ``*.py`` under ``src/newsletters/``, read
its text, and assert NONE of a self-contained denylist of config-specific tokens appears. The
denylist is a module-level constant in THIS file (never regressed silently) and we scan ``src/`` —
never ``tests/`` — so the denylist literal itself is not mistaken for a leak (self-invalidation
guard). Tokens match as WORDS / quoted literals (regex word boundaries, case-sensitive), not as
substrings of unrelated identifiers, so a structural key like ``module`` / ``area`` / ``owner`` (the
GENERIC shape the loader keys on, which is legitimately in source) never trips the guard — only the
concrete VALUES (``module-x``, ``area-1``, ``owner-1``) do.

The guard's failing behavior IS the deliverable: ``test_guard_detects_planted_leak`` proves the
scanner actually fires on a synthetic planted token, so the clean-source pass of
``test_no_config_specific_name_in_src`` is provably non-vacuous.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src" / "newsletters"

# --------------------------------------------------------------------------- #
# The denylist — a self-contained module constant (cannot be silently regressed).
# Every entry is a CONFIG-SPECIFIC value: a fixture id, a real-looking crew/org
# name, or an org metric name. None of these is a GENERIC structural key
# (``lanes``/``heading``/``kpis``/``owner``/``module``/``area``) — those are the
# shape the loader legitimately keys on in source and must NOT be listed here.
# --------------------------------------------------------------------------- #

# (1) Swim-lane fixture ids — tests/fixtures/swimlane/{module-x,module-trap}.yml. Generic-by-design
#     synthetic ids, but they are CONFIG values and must never be hardcoded into the loader.
_FIXTURE_IDS = frozenset(
    {
        "module-x",
        "module-trap",
        "area-1",
        "area-trap",
        "lane-a",
        "lane-b",
        "lane-t1",
        "group-1",
        "group-2",
        "owner-1",
        "owner-2",
        "owner-anchored",
        "shared-owner",
        "shared-value",
        "single-quoted-id",
        "double-quoted-id",
        "eng-01",
        "eng-02",
        "eng-03",
        "objective-1",
        "objective-2",
        "objective-3",
        "Lane Trap One",
    }
)

# (2) sample_team/*.yml identifiers + names — real-LOOKING (Star Trek) org/crew data. These are the
#     confidentiality-risk class: a real org's equivalents must never be baked into public source.
#     NB: the bare word "Data" (a crew member's name) is deliberately EXCLUDED — it is far too
#     generic and would false-positive on ordinary source ("data", "Data") without indicating a leak.
_SAMPLE_TEAM_NAMES = frozenset(
    {
        # idsids
        "jean-luc",
        "williamr",
        "geordila",
        "dataf606",
        "beverlyc",
        "deannatr",
        "worf9e03",
        # full names
        "Jean-Luc Picard",
        "William Riker",
        "Geordi La Forge",
        "Beverly Crusher",
        "Deanna Troi",
        "Worf",
        # functional-group / org / module names
        "Bridge Operations",
        "Engineering Corps",
        "Medical & Wellbeing",
        "Tactical Response",
        "Starfleet Division",
        "USS Enterprise",
        "starfleet.int",
        # a representative set of org KPI/metric names (metric-specific = CONFIG)
        "Dilithium Efficiency Index",
        "Warp Core Stability",
        "Crew Morale Rating",
        "Holodeck Safety Metric",
        "Diagnostic Uptime",
        "Anomaly Detection Rate",
        "Shuttlecraft Launch Efficiency",
        "Systems Integration Lag",
        "Medical Readiness Score",
    }
)

# (3) The Stage-A milestone seed's fabricated worked-example scheme (the `module-a` example itself is
#     Phase 3 — none of it may appear in Phase-1 source). Kept explicit so a future paste of the
#     worked config into source is caught here, not in review.
_SEED_SCHEME = frozenset(
    {
        "area-bem",
        "module-a",
        "owner-safety",
        "owner-ma",
        "owner-quality",
        "owner-vf",
        "owner-mor",
    }
)

# All literal tokens, longest-first so an alternation prefers the most specific match.
_DENY_LITERALS = tuple(
    sorted(_FIXTURE_IDS | _SAMPLE_TEAM_NAMES | _SEED_SCHEME, key=len, reverse=True)
)

# (4) Pattern-based ids from the seed scheme: `eng-NN` (numbered engineers) and `toolset-N`. These
#     cover the whole family without enumerating every index.
_DENY_PATTERNS = (
    re.compile(r"\beng-\d{2,}\b"),
    re.compile(r"\btoolset-\d+\b"),
)

# One compiled, case-SENSITIVE, word-bounded alternation for the literals. Case-sensitive on purpose:
# the crew/fixture tokens have a fixed casing, and a case-insensitive scan would false-positive on
# common words (e.g. "data", "worf"->none, but "Lane"/"module" fragments) — the honest guard matches
# the tokens as authored. `\b` around each literal prevents substring hits inside longer identifiers.
_LITERAL_RE = re.compile(
    "|".join(r"\b" + re.escape(tok) + r"\b" for tok in _DENY_LITERALS)
)


def _scan_text(text: str) -> set[str]:
    """Return the set of denylisted config-specific tokens found in ``text`` (empty == clean).

    Shared by the real-source scan and the planted-leak self-test so both exercise the SAME
    matcher — the self-test therefore proves the exact logic the guard relies on actually fires.
    """
    hits: set[str] = set(_LITERAL_RE.findall(text))
    for pattern in _DENY_PATTERNS:
        hits.update(pattern.findall(text))
    return hits


def _iter_src_py_files() -> list[Path]:
    """Every ``*.py`` under ``src/newsletters/`` (the policed surface — never ``tests/``)."""
    return sorted(SRC_DIR.rglob("*.py"))


def test_no_config_specific_name_in_src() -> None:
    """No fixture/org/config-specific token appears anywhere in ``src/newsletters/`` (LANE-03).

    Walks every source ``*.py``, scans its text against the self-contained denylist, and fails with
    the file + offending token(s) on ANY hit. A future edit that hardcodes a lane/module/owner id or
    a real-looking crew/metric name into the loader turns this red — that is the whole point.
    """
    src_files = _iter_src_py_files()
    assert src_files, f"no source files found under {SRC_DIR} — guard would be vacuous"

    leaks: dict[str, set[str]] = {}
    for path in src_files:
        hits = _scan_text(path.read_text(encoding="utf-8"))
        if hits:
            leaks[str(path.relative_to(REPO_ROOT))] = hits

    assert not leaks, (
        "config-specific name(s) leaked into src/newsletters/ (ABSTRACT EVERYTHING — LANE-03): "
        + "; ".join(f"{f}: {sorted(toks)}" for f, toks in sorted(leaks.items()))
    )


def test_guard_detects_planted_leak() -> None:
    """The scanner FIRES on a synthetic planted token — proving the clean pass above is non-vacuous.

    Constructs realistic source-looking text carrying one literal token, one full crew name, and one
    pattern-matched id (``eng-07``), and asserts the SAME ``_scan_text`` used against real source
    catches each — while a benign line using only GENERIC structural keys stays clean. Nothing is
    written to ``src/``; the leak lives only in this in-memory string.
    """
    planted = (
        "HEADING_KEY = 'heading'  # generic structural key — must stay clean\n"
        "DEFAULT_OWNER = 'owner-1'  # planted fixture-id leak\n"
        "AUTHOR = 'Jean-Luc Picard'  # planted real-name leak\n"
        "REVIEWER = 'eng-07'  # planted pattern-id leak\n"
    )
    hits = _scan_text(planted)
    assert "owner-1" in hits, hits
    assert "Jean-Luc Picard" in hits, hits
    assert "eng-07" in hits, hits

    # The generic structural keys the loader legitimately uses must NOT be flagged (no false positive
    # that would make real source impossible to write).
    clean = (
        "_LANES_KEY = 'lanes'\n_HEADING_KEY = 'heading'\n_OWNER_KEY = 'owner'\n"
        "context = f'module-config:{rel}'\narea_id = parsed.get('area')\n"
    )
    assert _scan_text(clean) == set(), _scan_text(clean)
