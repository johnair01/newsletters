"""MODA-01/02 — the end-to-end + trust-guard + determinism + confidentiality suite for the
synthetic ``module`` corpus (Phase 3, Plan 03-03).

The worked example is only PROOF if it is gate-visible and honest, so every assertion here is on
STRUCTURE and INVARIANTS, never on a specific lane/metric string (Pitfall 8 / the abstraction
guard): wherever a concrete value must be checked, it is READ from the same composed surface the
code produced, so the assertion tracks the config instead of hardcoding it.

What this suite proves against ``modulesite.build_module_surfaces`` / ``build_module_site`` and the
committed ``content/module/`` corpus:

* every claim on the built module surface is traced AND content-addressed (Hole B closed) and
  everything unprovable is disclosed in ``surface.missing[]`` (never a bare/untraced claim);
* the rendered module Library shows claim-beside-verbatim-trace (PROV-03) and a POPULATED honesty
  panel — the planted single-endpoint disclosure is VISIBLE in the HTML;
* the sourced-or-omit owner quote renders from a real traced claim (not fabricated, not omitted);
* the module output auto-loads ZERO external resources (self-hosted fonts);
* the build is byte-stable across two renders (SITE-06 / MODA-02), R-001 is stable across a rebuild
  (append-only proven by rebuild), committed ``content/module/`` == a fresh build, and everything is
  reproducible (``created`` / ``timestamp`` are ``EPOCH_ZERO``, no wall clock);
* committed ``content/module/`` carries only synthetic fabricated names (a denylist/allowlist
  confidentiality check per PITFALLS #confidentiality).

SHARED-LEDGER-PATH CAVEAT (plan-checker warning, from 03-01): ``build_module_site`` loads and saves
its ledger at the FIXED committed path ``content/module/ids.json`` (NOT ``out_dir``), so building
into a ``tmp_path`` re-saves that committed file. The committed ledger already holds R-001 and the
save is byte-stable (``sort_keys`` + trailing newline), so every rebuild is IDEMPOTENT — the tests
below that call ``build_module_site`` snapshot / rely on that idempotence and never mutate the
committed ledger.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.modulesite import build_module_site, build_module_surfaces
from newsletters.semantic import ClaimsBlock, QuoteBlock
from newsletters.site import Ledger, Site

# The committed corpus lives under the repo root (mirror test_worksurface's anchor).
REPO_ROOT = Path(__file__).resolve().parent.parent

# The composer's single-endpoint phrasing (composer SOURCE wording, not a lane name) — used only to
# LOCATE the planted disclosure inside surface.missing so the assertion reads the real entry text.
_SINGLE_ENDPOINT_PHRASE = "only one endpoint is usable"


def _report_page_name() -> str:
    """The report page's filename, DERIVED from the composed surface identity (config-tracked).

    ``Site.from_surfaces`` uses ``surface.id`` as the slug for a slug-clean id and writes
    ``{slug}.html`` — so the report page name follows the config's own identity, never a hardcode.
    """
    return f"{build_module_surfaces()[0].id}.html"


def _build_and_read_report(out: Path) -> str:
    """Build the module site into ``out`` and return the rendered report page HTML."""
    written = build_module_site(out)
    report = out / _report_page_name()
    assert report in written, "build_module_site did not emit the module report page"
    return report.read_text(encoding="utf-8")


def test_every_claim_traced_and_addressed() -> None:
    """Every ClaimsBlock claim on the module surface is traced AND content-addressed (Hole B).

    The trust gate over the composed worked example: every claim that survives onto a ``ClaimsBlock``
    is ``is_traced`` and every one of its traces ``is_addressed`` — anything unprovable was routed to
    ``surface.missing[]``, never left as a bare/untraced claim. Also asserts the honesty panel is
    GENUINELY populated (``missing`` non-empty) AND the body is real (≥1 kept claim), so this is not
    an empty body dumped into ``missing[]`` (Pitfall 11).
    """
    surface = build_module_surfaces()[0]

    claim_count = 0
    for block in surface.blocks:
        if not isinstance(block, ClaimsBlock):
            continue
        for claim in block.claims:
            assert claim.is_traced, (
                f"claim {claim.text[:40]!r} is untraced — it should have been routed to "
                "missing[], never left on a ClaimsBlock"
            )
            for trace in claim.evidence:
                assert trace.is_addressed, (
                    f"claim {claim.text[:40]!r} carries an un-addressed trace (Hole B free pass)"
                )
            claim_count += 1

    assert claim_count >= 1, "no kept claim on any ClaimsBlock — the body is empty (Pitfall 11)"
    assert surface.missing, "the honesty panel is empty — the worked example must disclose real gaps"


def test_single_endpoint_disclosure_visible_in_html(tmp_path: Path) -> None:
    """PROV-03: the rendered report shows claim-beside-trace + the VISIBLE single-endpoint disclosure.

    Reads the planted single-endpoint disclosure text from the composed ``surface.missing`` (located
    by the composer's phrasing, never a hardcoded lane name), builds the site, and asserts the
    honesty panel is present AND the exact disclosure text is rendered (escaped) in the HTML — the
    populated honesty panel is proven ON THE SURFACE, not just in the model. Also asserts a
    ``claim-span`` renders (claim-beside-verbatim-trace, PROV-03).
    """
    surface = build_module_surfaces()[0]
    disclosures = [m for m in surface.missing if _SINGLE_ENDPOINT_PHRASE in m]
    assert disclosures, (
        "fixture invariant: the corpus must declare a single-endpoint KPI so the honesty panel "
        "carries the single-endpoint disclosure"
    )

    page = _build_and_read_report(tmp_path)
    assert 'class="honesty"' in page, "no honesty panel rendered on the module report"
    assert 'class="claim-span"' in page, "no verbatim claim-span (claim-beside-trace) rendered"
    for entry in disclosures:
        assert html.escape(entry) in page, (
            "the single-endpoint disclosure is not visible in the rendered honesty panel"
        )


def test_owner_quote_rendered_from_sourced_path(tmp_path: Path) -> None:
    """The sourced-or-omit path rendered a real, traced owner quote (not fabricated, not omitted).

    Reads the composed ``QuoteBlock`` text from the surface and asserts that verbatim text appears
    (escaped) in the rendered report — proving the module-owner quote came through the sourced path.
    """
    surface = build_module_surfaces()[0]
    quotes = [b for b in surface.blocks if isinstance(b, QuoteBlock)]
    assert quotes, "the sourced-or-omit path must render a traced owner quote for this corpus"
    quote_text = quotes[0].text

    page = _build_and_read_report(tmp_path)
    assert html.escape(quote_text) in page, "the sourced owner quote is not rendered in the report"


def test_no_external_calls(tmp_path: Path) -> None:
    """A2 / T-03-05: the module output auto-loads ZERO external resources (self-hosted fonts).

    Mirrors ``test_no_external_calls_in_work_output`` over the module corpus: no Google-Fonts host,
    no ``@import url(http``, no ``src="http"``, no CSS ``url(http`` (@font-face), no
    ``<link href="http">`` — and the self-hosted ``fonts/*.woff2`` the relative @font-face urls
    reference must actually be present (the module Library is genuinely self-contained).
    """
    written = build_module_site(tmp_path)
    pages = sorted(p for p in written if p.suffix == ".html")
    assert pages, "build_module_site produced no HTML to scan"

    forbidden = (
        "fonts.googleapis.com",
        "fonts.gstatic.com",
        "@import url('http",
        '@import url("http',
        "@import url(http",
        'src="http',
        "src='http",
    )
    css_url_fetch = re.compile(r"url\(\s*['\"]?https?://")
    link_href_http = re.compile(r"<link\b[^>]*\bhref\s*=\s*['\"]https?://", re.IGNORECASE)

    for page in pages:
        text = page.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, (
                f"{page.name} bakes an auto-loading external resource: {needle!r}"
            )
        assert not css_url_fetch.search(text), (
            f"{page.name} has a CSS url(http...) fetch — module fonts must be self-hosted"
        )
        assert not link_href_http.search(text), (
            f'{page.name} has a <link href="http..."> auto-loaded resource'
        )

    fonts_dir = tmp_path / "fonts"
    assert fonts_dir.is_dir(), "build_module_site did not emit the self-hosted fonts/ dir"
    assert any(fonts_dir.glob("*.woff2")), "no woff2 fonts in the module output fonts/ dir"


# --------------------------------------------------------------------------- #
# Plan 03-03 Task 2 — determinism, ledger-stability, committed==fresh-build, and
# the synthetic-name confidentiality check over the committed corpus.
# --------------------------------------------------------------------------- #


def test_byte_stable_double_render(tmp_path: Path) -> None:
    """SITE-06 / MODA-02: build_module_site is byte-stable across two renders (no datetime.now()).

    Two independent builds into separate dirs must produce the IDENTICAL file set and byte-identical
    contents for EVERY file (HTML + self-hosted fonts). Shared-ledger caveat: both builds re-save the
    committed ``content/module/ids.json`` (idempotent — R-001 already recorded, append-only,
    byte-stable save), so the double render is stable and leaves the committed ledger unchanged.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    build_module_site(a)
    build_module_site(b)

    files_a = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    assert files_a == files_b, "the two module renders produced a different file set"
    for rel in files_a:
        assert (a / rel).read_bytes() == (b / rel).read_bytes(), (
            f"{rel} is not byte-identical across renders (nondeterminism in the module output)"
        )


def test_r001_stable_across_rebuild(tmp_path: Path) -> None:
    """R-001 is stable across a rebuild — the append-only ledger never renumbers on re-sight.

    Uses a FRESH tmp ``ids.json`` (never the committed path) so nothing leaks: a fresh ledger assigns
    the first report ``R-001``; reloading that populated ledger and rebuilding returns the SAME ref.
    The stability is PROVEN by rebuild (append-only immutability), not by asserting a literal twice.
    """
    ids = tmp_path / "ids.json"

    ledger = Ledger.load(ids)  # fresh / empty
    site = Site.from_surfaces(build_module_surfaces(), ledger=ledger)
    ledger.save()
    first_ref = site.pages()[0].ref
    assert first_ref == "R-001", (
        f"a fresh ledger must assign the first report ref R-001, got {first_ref!r}"
    )

    reloaded = Ledger.load(ids)  # re-sight the same, now-populated, ledger
    site_again = Site.from_surfaces(build_module_surfaces(), ledger=reloaded)
    reloaded.save()
    assert site_again.pages()[0].ref == first_ref, (
        "the append-only ledger renumbered R-001 on rebuild — it must be immutable on re-sight"
    )


def test_committed_equals_fresh_build(tmp_path: Path) -> None:
    """The committed content/module/ == a fresh build (the committed==fresh-build norm, Phase 11/12).

    A fresh build into ``tmp_path`` must reproduce every committed ``content/module/site/`` file
    (HTML + fonts) BYTE-for-BYTE — this is WHY Plan 01 committed a byte-stable render. Shared-ledger
    caveat: ``build_module_site`` writes its ledger to the FIXED committed
    ``content/module/ids.json`` (not ``tmp_path``); the committed ledger already holds R-001 and the
    save is byte-stable, so we snapshot its bytes and assert the build leaves it UNCHANGED
    (committed==fresh at the ledger layer, and no accidental mutation of a tracked file).
    """
    committed_site = REPO_ROOT / "content" / "module" / "site"
    committed_ledger = REPO_ROOT / "content" / "module" / "ids.json"
    assert committed_site.is_dir(), "committed content/module/site/ is missing (Plan 01 output)"

    ledger_before = committed_ledger.read_bytes()
    build_module_site(tmp_path)
    assert committed_ledger.read_bytes() == ledger_before, (
        "the fresh build mutated the committed ledger — the rebuild must be idempotent (R-001 held)"
    )

    committed_files = sorted(
        p for p in committed_site.rglob("*") if p.is_file()
    )
    assert committed_files, "no committed module site files to compare against"
    for src in committed_files:
        rel = src.relative_to(committed_site)
        built = tmp_path / rel
        assert built.exists(), f"fresh build is missing committed file {rel}"
        assert built.read_bytes() == src.read_bytes(), (
            f"{rel} differs between the committed corpus and a fresh build"
        )


def test_no_datetime_now_reachable() -> None:
    """Determinism (Pitfall 5): the composed surface + its source carry EPOCH_ZERO, no wall clock.

    ``Surface.created`` and every ``Source.timestamp`` are the fixed ``EPOCH_ZERO`` sentinel — proof
    that no ``datetime.now()`` is reachable through the module build (the byte-stability precondition).
    """
    surface = build_module_surfaces()[0]
    assert surface.created == EPOCH_ZERO, (
        "Surface.created must be EPOCH_ZERO (no datetime.now() in the module build)"
    )
    assert surface.traces, "the surface must carry its config source trace"
    for src in surface.traces:
        assert src.timestamp == EPOCH_ZERO, (
            "Source.timestamp must be EPOCH_ZERO (the loader must not read the wall clock)"
        )


# --------------------------------------------------------------------------- #
# Confidentiality (T-03-03 / Pitfall 8): committed public content carries ONLY
# fabricated synthetic names. The denylist is a GENERIC real-name-SHAPE set (not a
# list of secrets): representative real-looking org/crew/metric tokens — here the
# repo's own Star-Trek sample-team names stand in as canonical "real-looking"
# nomenclature — plus an email-address shape. The allowlist positively asserts the
# fabricated scheme is the naming actually used.
# --------------------------------------------------------------------------- #

# Representative real-looking nomenclature that must NEVER appear in committed public content.
# Multi-word / distinctive tokens only, so a substring scan cannot false-positive on ordinary
# words or the design-system's font-family names.
_REAL_LOOKING_LITERALS = frozenset(
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
_EMAIL_RE = re.compile(r"\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b")

# The fabricated worked-example scheme (seed §5) — the naming that SHOULD be present.
_FABRICATED_MARKERS = ("module-a", "area-bem", "owner-", "eng-", "toolset-")


def _scan_real_looking(text: str) -> set[str]:
    """Return the real-looking nomenclature found in ``text`` (empty == clean/synthetic)."""
    hits = {tok for tok in _REAL_LOOKING_LITERALS if tok in text}
    hits.update(_EMAIL_RE.findall(text))
    return hits


def test_committed_content_is_synthetic() -> None:
    """T-03-03: every committed content/module/ file carries only synthetic fabricated names.

    Scans the committed config (``*.yml``), the rendered ``site/*.html``, and the ledger
    (``ids.json``) against the real-name-shape denylist and asserts NONE appear; then positively
    asserts the fabricated scheme markers ARE the naming used. A planted-leak self-check proves the
    SAME scanner fires on a real-looking name/email — so the clean pass is non-vacuous (Phase-7 norm:
    prove it blocks, not just passes).
    """
    module_dir = REPO_ROOT / "content" / "module"
    files = (
        sorted(module_dir.glob("*.yml"))
        + sorted((module_dir / "site").glob("*.html"))
        + [module_dir / "ids.json"]
    )

    corpus = ""
    for f in files:
        assert f.exists(), f"expected committed module content file {f.relative_to(REPO_ROOT)}"
        text = f.read_text(encoding="utf-8")
        corpus += text
        leaks = _scan_real_looking(text)
        assert not leaks, (
            f"real-looking nomenclature in committed {f.relative_to(REPO_ROOT)}: {sorted(leaks)} "
            "— committed public content must be synthetic (T-03-03 / Pitfall 8)"
        )

    for marker in _FABRICATED_MARKERS:
        assert marker in corpus, (
            f"expected the fabricated scheme marker {marker!r} in committed content — the corpus "
            "must use the synthetic naming scheme"
        )

    # Non-vacuous: the SAME scanner catches a planted real-looking name + email.
    planted = "owner: Jean-Luc Picard\ncontact: ops@starfleet.int\n"
    planted_hits = _scan_real_looking(planted)
    assert "Jean-Luc Picard" in planted_hits, planted_hits
    assert any("@" in h for h in planted_hits), planted_hits
