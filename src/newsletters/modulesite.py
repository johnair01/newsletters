"""MODA-01 — the synthetic ``module`` corpus builder (Phase 3).

This module is the worked-example half of MODA-01: it composes and renders the committed
synthetic swim-lane config under ``content/module/`` end-to-end (loader → composer → ledger →
render → Library) into a self-contained ``content/module/`` corpus with its OWN append-only
ledger. It is deliberately a THIN seam that MIRRORS :mod:`newsletters.worksurface` exactly —
``Ledger.load`` → ``Site.from_surfaces`` → ``ledger.save()`` → ``render_surface`` per page →
``render_library`` → self-hosted fonts — reusing the Phase-1 loader, the Phase-2 composer, and
the Phase-9/10 render devices with ZERO edits to any existing module.

ABSTRACT EVERYTHING (LANE-03 / the abstraction guard): the concrete config-specific VALUES (the
module id, area, lane/owner/engineer/tool/metric names) live ONLY in the YAML config + the
rendered content, NEVER in this source. So this builder never hardcodes the fixture filename: it
DISCOVERS the single ``*.yml`` config under the corpus dir (a generic, structural default), and
the surface slug/title are DERIVED by the composer from the config's own identity at runtime.

WHY a new top-level module (a sibling of ``worksurface.py``, not code in ``compose.py``):
``compose.py`` is a LEAF (COMP contract: it must not import ``render``/``site``), so the
build-and-render seam cannot live there. Like ``worksurface.build_work_site``, this is a plain
corpus builder that wires the loader/composer to the renderer over a committed, hand-authored
config — the honest fit is a sibling builder module, not a fork of the renderer.

The four-property contract (mirrors ``worksurface.py`` / ``swimlane.py`` / ``compose.py``):

* READ-ONLY / NO NETWORK. The only writes are the ledger + the rendered output the caller asked
  for; no network call anywhere (the fonts are self-hosted via the reused ``_emit_fonts``).
* CONTENT-ADDRESSED / FAITHFUL. Every rendered claim is content-addressed by the loader and the
  owner quote is emitted via the SOURCED path only (a traced claim selected from the load) —
  never fabricated; the honesty panel shows every disclosed gap.
* DETERMINISTIC / BYTE-STABLE. Relies wholly on the loader/composer's ``EPOCH_ZERO`` + file
  order, a sorted config discovery, and the append-only ledger — no ``datetime.now()``, no
  ``set()``, no non-total sort — so the committed output equals a fresh build (SITE-06 extended
  to the module corpus).
* AI-FREE / MINIMAL-CORE. Imports only stdlib + sibling core modules (``swimlane``, ``compose``,
  ``site``, ``render``, ``worksurface`` for the shared ``_emit_fonts``) and the lazy
  ``_yaml_loader`` boundary. NO ``yaml`` at module top level, NO AI package — importable on a
  bare, no-extras install.
"""

from __future__ import annotations

from pathlib import Path

from . import worksurface
from ._yaml_loader import load_config as _parse_config
from .compose import compose_module_report
from .render import render_library, render_surface
from .semantic import Claim, Surface
from .site import Ledger, Site
from .swimlane import SwimlaneLoad, load_swimlanes

__all__ = ["build_module_surfaces", "build_module_site"]

# The committed synthetic corpus's fixed, GENERIC defaults (not user input — T-03-04 accept, and
# not a config-specific fixture name — LANE-03). The config, its OWN append-only ledger, and the
# rendered site all live self-contained under the corpus dir.
_CORPUS_DIR = "content/module"
_LEDGER_PATH = "content/module/ids.json"
_SITE_DIR = "content/module/site"

# The generic, module-level structural keys the loader already reads as scalars — the 02-03
# quote hand-off (generic keys only; the concrete owner/quote VALUES live in the config).
_QUOTE_KEY = "quote"
_OWNER_KEY = "owner"


def _discover_config(root: Path | None) -> Path:
    """Find the single committed ``*.yml`` config under the corpus dir (generic, deterministic).

    Keeps the config-specific FILENAME out of source (LANE-03 abstraction guard): rather than
    hardcode the fixture file, we discover it. The corpus is self-contained with exactly one config
    (like ``content/work/``), so a SORTED glob is deterministic and byte-stable; the first entry is
    chosen so the result never depends on filesystem order. Returned ABSOLUTE so it resolves cleanly
    under any ``root`` the loader is given.
    """
    corpus = (Path(root) if root is not None else Path.cwd()) / _CORPUS_DIR
    candidates = sorted(corpus.resolve().glob("*.yml"))
    if not candidates:
        raise FileNotFoundError(
            f"no module-config '*.yml' found under {corpus} — the corpus is not populated"
        )
    return candidates[0]


def _select_owner_quote(load: SwimlaneLoad) -> tuple[Claim | None, str | None]:
    """Select the traced module-owner quote Claim + owner id from a loaded config (02-03 hand-off).

    Re-reads the config's MODULE-LEVEL ``quote``/``owner`` scalars through the SAME lazy
    ``_yaml_loader.load_config`` boundary the loader used (``yaml.safe_load`` only — no second
    parse path), then selects from ``load.claims`` (the module-level claims) the ALREADY
    content-addressed Claim whose ``.text`` equals the quote value verbatim. The loader already
    minted+traced that scalar; here we merely SELECT it — never re-mint, never fabricate.

    Returns ``(quote_claim, owner_id)``. If the config declares no string ``quote`` scalar, or no
    module-level traced claim matches it verbatim, ``quote_claim`` is ``None`` and the composer
    discloses the omission in ``missing[]`` (sourced-or-omit — never a fabricated quote).
    """
    parsed = _parse_config(load.source.transcript)
    if not isinstance(parsed, dict):
        return None, None
    owner_value = parsed.get(_OWNER_KEY)
    owner = owner_value if isinstance(owner_value, str) else None
    quote_value = parsed.get(_QUOTE_KEY)
    if not isinstance(quote_value, str):
        return None, owner
    for claim in load.claims:  # module-level claims (outside any lane) in file order
        if claim.text == quote_value:
            return claim, owner
    return None, owner


def build_module_surfaces(
    config_path: str | Path | None = None, *, root: Path | None = None
) -> list[Surface]:
    """Load + compose the synthetic module corpus into one Draft REPORT Surface (MODA-01).

    Mirrors :func:`newsletters.worksurface.build_work_surfaces` (the corpus-assembly analog), but
    over the swim-lane config:

      1. Resolve the config (``config_path`` if given, else the single ``*.yml`` discovered under
         the corpus dir), then ``load = load_swimlanes(config, root=root)`` — the Phase-1
         read-only, deterministic, content-addressed load (lane bindings + module-level claims).
      2. Select the module-owner quote via :func:`_select_owner_quote` (the traced claim + owner id).
      3. ``compose_module_report(load, quote=..., owner=...)`` — the Phase-2 composer emits the
         per-lane KPI strips (with compose-time Δ) + claims, the sourced-or-omit QuoteBlock, and
         routes every unprovable thing to the honesty panel. Like ``build_work_surfaces`` this does
         NOT touch the ledger (compose defaults to a read/assign-only ``Ledger.load``, never saves).
      4. Return ``[surface]``.

    The surface ships ``Draft`` — there is no auto-publish path (the hard rule holds).
    """
    config = Path(config_path) if config_path is not None else _discover_config(root)
    load = load_swimlanes(config, root=root)
    quote, owner = _select_owner_quote(load)
    surface = compose_module_report(load, quote=quote, owner=owner)
    return [surface]


def build_module_site(
    out_dir: str | Path = _SITE_DIR,
    *,
    root: Path | None = None,
    config_path: str | Path | None = None,
) -> list[Path]:
    """Render the module corpus to standalone HTML at ``out_dir`` (MODA-01), mirroring build_work_site.

    Exactly mirrors :func:`newsletters.worksurface.build_work_site`, but over the module corpus and
    its OWN append-only ledger (``content/module/ids.json``, first ref ``R-001`` for the composed
    report slug), kept SEPARATE from the rev1 + work corpora:

      * ``Ledger.load("content/module/ids.json")`` → ``Site.from_surfaces(build_module_surfaces(),
        ledger=ledger)`` → ``ledger.save()`` — this builder is the SOLE ledger writer (compose only
        reads/assigns; the caller owns persistence, the 02-03 decision);
      * each page is written to ``out / page.href`` via ``render_surface(page.surface, site=site,
        page=page)`` — REUSING the PROV-03 devices with NO new renderer (claim-beside-verbatim-trace
        spans + the populated honesty panel come for free);
      * a Library index (``library.html``) is rendered from the Site;
      * the self-hosted fonts are emitted into ``out / fonts`` via the REUSED
        ``worksurface._emit_fonts`` (zero-edit reuse) so the module Library is self-contained —
        ZERO external call.

    Deterministic / byte-stable (SITE-06): sorted inputs, ``EPOCH_ZERO``, append-only ledger, no
    ``datetime.now()``. Zero AI, zero new runtime dependency. The report stays ``Draft``.

    Args:
        out_dir: where to write the module Library (default ``content/module/site``).
        root: the repo root the config path resolves against (default cwd).
        config_path: an explicit module-config to build (default: discover the single ``*.yml``
            under the corpus dir).

    Returns:
        The written paths (every ``{slug}.html`` + ``library.html``), in write order.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_module_surfaces(config_path, root=root)

    # The module corpus has its OWN ledger (R-001 starts fresh) — the corpus boundary is preserved
    # at the ledger layer. Load → build the Site → persist any newly-assigned refs (SOLE writer).
    ledger = Ledger.load(_LEDGER_PATH)
    site = Site.from_surfaces(surfaces, ledger=ledger)
    ledger.save()

    written: list[Path] = []
    for page in site.pages():
        p = out / page.href
        # Pass the resolved Site + this Page so nav/breadcrumb/prev-next resolve neighbors.
        p.write_text(
            render_surface(page.surface, site=site, page=page), encoding="utf-8"
        )
        written.append(p)

    # The Library index (the gate-state board) — the module corpus's own archive view.
    # Records strip (PUB-03): the module corpus lives at module/ in the assembled published
    # tree, so its neighbors are one level up — assembled-tree-relative by design.
    library = out / "library.html"
    library.write_text(
        render_library(
            site,
            records=(
                ("The Rev1 record", "../index.html"),
                ("The work record", "../work/library.html"),
            ),
        ),
        encoding="utf-8",
    )
    written.append(library)

    # Self-host the fonts beside the HTML so the module Library is zero-external-call (reused).
    worksurface._emit_fonts(out)

    return written
