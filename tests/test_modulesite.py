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
