"""WKLY-05 — the synthetic ``weekly`` corpus builder (Phase 4).

This module is the worked-example half of WKLY-05: it loads, composes and renders the committed
synthetic Weekly Spec under ``content/weekly/`` end-to-end (loader → composer → ledger → render →
Library) into a self-contained corpus with its OWN append-only ledger, and — on a THIRD, separate
entry point — renders the same composed record to a ``.pptx`` deck. It is deliberately a THIN seam
that MIRRORS :mod:`newsletters.modulesite` exactly, reusing the Phase-3 loader/composer and the
Phase-2 writer with ZERO edits to any existing module.

ABSTRACT EVERYTHING (LANE-03 / the abstraction guard): the concrete authored VALUES (the period
label, the module name, the crew names, the ``assets:`` keys, the ``config:`` slots) live ONLY in
the YAML + the rendered content, NEVER in this source. So this builder never hardcodes a corpus
filename: it DISCOVERS the single ``*.yml`` under each corpus dir (a generic, structural default),
and the surface slug/title are DERIVED by the composer from the authored identity at runtime.

WHY a new top-level module (a sibling of ``modulesite.py``, not code in ``compose.py``):
``compose.py`` is a LEAF (COMP contract: it must not import ``render``/``site``), so the
build-and-render seam cannot live there. Like ``modulesite.build_module_site``, this is a plain
corpus builder wiring a loader/composer to the renderer over committed, hand-authored content —
the honest fit is a sibling builder module, not a fork of the renderer.

WHERE THE BINDINGS COME FROM (recorded decision W0-1). The lane bindings are loaded from the
COMMITTED ``content/module/*.yml`` rather than from a second fabricated lane config, because this
IS the weekly for the module that lives in ``content/module`` — one fabricated module, one source
of truth, the repo's anti-duplication norm (``specspan.SpanMinter``, ``compose.compose_kpi_item``
and ``pptx_writer.normalize_opc_zip`` were each promoted for the same reason). The coupling is
bounded and LOUD: a change to the module config moves BOTH corpora's committed HTML and turns BOTH
committed==fresh gates red in the same run. It also supplies the sample's "a lane with no KPIs"
honesty row for free, from content that already exists rather than from content invented to make a
demo look honest.

A KNOWN LIMITATION, RECORDED RATHER THAN PATCHED (W0-4; Phase 3 source is frozen and reviewed).
``weeklyspec.build_weekly_report`` sets ``traces=[load.source]``, so claims contributed by the
bindings and by a resolved ``.eml`` recognition reference ``Source``s the ``Surface`` does not
carry. MEASURED consequence: no rendering break and no false STALE (``semantic.py`` skips a
``source_id`` absent from the lookup) and no ``href="None"`` in the rendered page. It would matter
only if this Draft sample were ever advanced to Published, where a lane-config drift would be
invisible to ``review.review_blockers`` — which is exactly why the sample ships Draft.

The four-property contract (mirrors ``modulesite.py`` / ``worksurface.py`` / ``compose.py``):

* READ-ONLY / NO NETWORK. The only writes are the ledger, the rendered output and (on the deck
  entry point) the caller-supplied ``out_path``; no network call anywhere (the fonts are
  self-hosted via the reused ``_emit_fonts``).
* CONTENT-ADDRESSED / FAITHFUL. Every rendered claim is content-addressed by the loader; an asset
  is placed only if it is root-contained, provenance-complete and still hashes to what its record
  says; everything else is a named disclosure in the honesty panel. This builder authors no text.
* DETERMINISTIC / BYTE-STABLE. Relies wholly on the loader/composer's ``EPOCH_ZERO`` + file order,
  sorted discovery, and the append-only ledger — no ``datetime.now()``, no ``set()``, no non-total
  sort — so the committed output equals a fresh build.
* AI-FREE / MINIMAL-CORE. Module level imports only stdlib + sibling core modules. NO ``yaml``, NO
  ``pptx``, NO ``openpyxl`` at module top level — importable on a bare, no-extras install; the
  ``[pptx]`` extra is reached lazily INSIDE :func:`build_weekly_deck` only, so rendering the HTML
  corpus never drags the optional extra into the ``site-integrity`` or deploy jobs.

THE GATE IS NEVER TOUCHED. Nothing here calls ``approve()``, ``open_pull_request()`` or
``publish()``: the composer returns ``Draft`` and that is the only state this builder produces.
"""

from __future__ import annotations

from pathlib import Path

from . import worksurface
from .adapters.email_adapter import EmailAdapter
from .render import render_library, render_surface
from .semantic import Source, Surface
from .site import Ledger, Site
from .swimlane import load_swimlanes
from .weeklyspec import WeeklySpecLoad, build_weekly_report, load_weekly_spec

__all__ = ["build_weekly_deck", "build_weekly_site", "build_weekly_surfaces"]

# The committed synthetic corpus's fixed, GENERIC defaults (not user input, and not a
# content-specific filename — LANE-03). The spec, its inbox, its assets, its operator template, its
# OWN append-only ledger, the rendered site and the rendered deck all live self-contained under the
# corpus dir. ``_LANES_DIR`` is the ONE outward edge: the committed module corpus this weekly is
# the weekly FOR (see the module docstring).
_CORPUS_DIR = "content/weekly"
_LANES_DIR = "content/module"
_LEDGER_PATH = "content/weekly/ids.json"
_SITE_DIR = "content/weekly/site"
_DECK_DIR = "content/weekly/deck"
_TEMPLATE_NAME = "template.pptx"
_INBOX_GLOB = "inbox/*.eml"

# The authored ``config:`` key whose value becomes the weekly's byline. A config value BOUND as
# Surface metadata is what "bound, never claimed" means: it identifies who signed the record, and
# it is never minted as a Claim (the loader carries ``config:`` and never mints it).
_AUTHOR_KEY = "author"

_NO_AUTHOR = (
    "no byline for this weekly: pass author=... (the CLI's --author) or give the spec a "
    "'config: author:' value. Refusing to invent one — a fabricated byline would be an unsigned "
    "record wearing somebody's name, and the byline is what a reviewer is trusting."
)


def _discover_one_yml(root: Path | None, corpus_dir: str, what: str) -> Path:
    """Find the single committed ``*.yml`` under ``corpus_dir`` (generic, deterministic).

    Keeps the content-specific FILENAME out of source (LANE-03 abstraction guard): rather than
    hardcode the committed file, we discover it. Each corpus is self-contained with exactly one
    root-level config, so a SORTED glob is deterministic and byte-stable; the first entry is chosen
    so the result never depends on filesystem order. ``Path.glob`` is NON-recursive, so the
    corpus's ``inbox/``, ``assets/``, ``site/`` and ``deck/`` subdirectories never collide with it.
    Returned ABSOLUTE so it resolves cleanly under any ``root`` the loader is given.
    """
    corpus = (Path(root) if root is not None else Path.cwd()) / corpus_dir
    candidates = sorted(corpus.resolve().glob("*.yml"))
    if not candidates:
        raise FileNotFoundError(
            f"no {what} '*.yml' found under {corpus} — the corpus is not populated"
        )
    return candidates[0]


def _discover_spec(root: Path | None) -> Path:
    """The single committed Weekly Spec under the weekly corpus dir."""
    return _discover_one_yml(root, _CORPUS_DIR, "Weekly Spec")


def _discover_lanes(root: Path | None) -> Path:
    """The single committed lane config under the module corpus dir (the W0-1 lineage link)."""
    return _discover_one_yml(root, _LANES_DIR, "module-config")


def _load_inbox_sources(root: Path | None) -> list[Source]:
    """Parse every committed ``inbox/*.eml`` into a ``Source``, in sorted file order.

    ``EmailAdapter().parse(raw, path)`` makes ``Source.id`` the path STRING it is handed, and that
    id is exactly what a recognition's authored ``source:`` must name — so the REPO-RELATIVE POSIX
    form is passed, never an absolute path. An absolute path would bake the build machine's
    directory layout into the record's id and the sample would resolve on one machine and disclose
    an unresolvable id on another. Stdlib-only: ADAPT-02 pulls no optional extra.

    An inbox is OPTIONAL: a corpus with no ``inbox/`` returns ``[]`` and every authored ``source:``
    is then disclosed by name — the honest outcome, not an error.
    """
    root_path = (Path(root) if root is not None else Path.cwd()).resolve()
    corpus = root_path / _CORPUS_DIR
    adapter = EmailAdapter()
    sources: list[Source] = []
    for path in sorted(corpus.glob(_INBOX_GLOB)):
        rel = path.resolve().relative_to(root_path).as_posix()
        source, _units, _unextracted = adapter.parse(path.read_bytes(), rel)
        sources.append(source)
    return sources


def _resolve_author(spec_config: dict[str, object], author: str | None) -> str:
    """The byline: the explicit argument, else the spec's ``config: author:``, else refuse."""
    if author is not None and author.strip():
        return author
    configured = spec_config.get(_AUTHOR_KEY)
    if isinstance(configured, str) and configured.strip():
        return configured
    raise ValueError(_NO_AUTHOR)


def _load_and_compose(
    *,
    root: Path | None,
    spec_path: str | Path | None,
    lanes_path: str | Path | None,
    author: str | None,
) -> tuple[WeeklySpecLoad, Surface]:
    """The ONE load-and-compose sequence, shared by the surfaces and the deck entry points.

    Both entry points need the SAME load: ``weekly_slots(load, surface)`` checks its disclosure
    lines against ``surface.missing``, so a deck composed from a second, separately-built load
    would be checking one record's slides against another record's honesty panel. Two copies of
    this sequence would drift exactly as two normalizers would, so there is one.
    """
    spec = Path(spec_path) if spec_path is not None else _discover_spec(root)
    lanes = Path(lanes_path) if lanes_path is not None else _discover_lanes(root)
    load = load_weekly_spec(spec, root=root, known_sources=_load_inbox_sources(root))
    swim = load_swimlanes(lanes, root=root)
    surface = build_weekly_report(
        load,
        author=_resolve_author(load.spec.config, author),
        bindings=swim.bindings,
    )
    return load, surface


def build_weekly_surfaces(
    spec_path: str | Path | None = None,
    *,
    root: Path | None = None,
    lanes_path: str | Path | None = None,
    author: str | None = None,
) -> list[Surface]:
    """Load + compose the synthetic weekly corpus into one Draft REPORT Surface (WKLY-05).

    Mirrors :func:`newsletters.modulesite.build_module_surfaces` — the exact shape ``cli check``
    calls — over the Weekly Spec:

      1. Resolve the spec (``spec_path`` if given, else the single ``*.yml`` discovered under the
         corpus dir) and the lane config (the committed ``content/module`` one — W0-1).
      2. Parse the committed ``inbox/*.eml`` into ``Source``s and hand them to the loader as
         ``known_sources``, so a recognition's ``source:`` resolves to real evidence instead of
         being disclosed as an unresolvable id.
      3. ``load_weekly_spec(...)`` — the Phase-3 read-only, deterministic, content-addressed load.
         Asset PLACEMENT happens there (the content-address check needs the filesystem); every
         asset that is not root-contained + provenance-complete + correctly hashed is a named
         disclosure instead.
      4. ``build_weekly_report(load, author=..., bindings=swim.bindings)`` — the Phase-3 composer
         emits the fixed block order and routes every unprovable thing to the honesty panel. Like
         ``build_module_surfaces`` this does NOT touch the ledger.
      5. Return ``[surface]``.

    The surface ships ``Draft`` — there is no auto-publish path (the hard rule holds).

    Args:
        spec_path: an explicit Weekly Spec to build (default: discover the single ``*.yml``).
        root: the repo root the paths resolve against (default cwd).
        lanes_path: an explicit lane config to bind (default: discover the single ``*.yml``
            under the module corpus — the W0-1 lineage link).
        author: the byline. Defaults to the spec's ``config: author:``; a ``ValueError`` naming
            both that key and ``--author`` is raised if neither is given, because inventing a
            byline would put a name nobody chose on a record a human is meant to sign.
    """
    _load, surface = _load_and_compose(
        root=root, spec_path=spec_path, lanes_path=lanes_path, author=author
    )
    return [surface]


def build_weekly_site(
    out_dir: str | Path = _SITE_DIR,
    *,
    root: Path | None = None,
    spec_path: str | Path | None = None,
    author: str | None = None,
) -> list[Path]:
    """Render the weekly corpus to standalone HTML at ``out_dir``, mirroring build_module_site.

    Exactly mirrors :func:`newsletters.modulesite.build_module_site`, but over the weekly corpus
    and its OWN append-only ledger (``content/weekly/ids.json``, first ref ``R-001`` for the
    composed report slug), kept SEPARATE from the rev1 + work + module corpora:

      * ``Ledger.load("content/weekly/ids.json")`` → ``Site.from_surfaces(...)`` →
        ``ledger.save()`` — this builder is the SOLE ledger writer (compose only reads/assigns).
        The ledger path is the FIXED COMMITTED one, never ``out_dir``: the committed ledger is the
        contract, so a ``tmp_path`` build re-saves it idempotently and the tests snapshot its bytes
        and assert it did not move.
      * each page is written to ``out / page.href`` via ``render_surface`` — REUSING the PROV-03
        devices with NO new renderer (claim-beside-verbatim-trace spans + the populated honesty
        panel come for free);
      * a Library index (``library.html``) is rendered from the Site, declaring its three
        neighbours ASSEMBLED-TREE-relative (the weekly corpus lives at ``weekly/`` in the published
        tree, so its neighbours are one level up);
      * the self-hosted fonts are emitted via the REUSED ``worksurface._emit_fonts`` (zero-edit
        reuse, never re-vendored) — ZERO external call.

    The deck is deliberately NOT rendered here: see :func:`build_weekly_deck`.

    Returns:
        The written paths (every ``{slug}.html`` + ``library.html``), in write order.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_weekly_surfaces(spec_path, root=root, author=author)

    ledger = Ledger.load(_LEDGER_PATH)
    site = Site.from_surfaces(surfaces, ledger=ledger)
    ledger.save()

    written: list[Path] = []
    for page in site.pages():
        p = out / page.href
        # home_href climbs to the site root: the weekly corpus has NO index.html of its own.
        p.write_text(
            render_surface(
                page.surface, site=site, page=page, home_href="../index.html"
            ),
            encoding="utf-8",
        )
        written.append(p)

    library = out / "library.html"
    library.write_text(
        render_library(
            site,
            records=(
                ("The Rev1 record", "../index.html"),
                ("The work record", "../work/library.html"),
                ("The module record", "../module/library.html"),
            ),
            home_href="../index.html",
        ),
        encoding="utf-8",
    )
    written.append(library)

    worksurface._emit_fonts(out)

    return written


def build_weekly_deck(
    out_path: str | Path,
    *,
    root: Path | None = None,
    spec_path: str | Path | None = None,
    lanes_path: str | Path | None = None,
    template: str | Path | None = None,
    author: str | None = None,
) -> Path:
    """Render the composed weekly to a ``.pptx`` deck at ``out_path`` + write its digest sidecar.

    A THIRD, SEPARATE entry point, and that separation is the point: rendering the deck inside
    :func:`build_weekly_site` would drag ``python-pptx`` into the ``site-integrity`` CI job (which
    installs only ``[test,config]``) and into the deploy gate. HTML and deck stay on separate entry
    points, and the ``[pptx]`` import lives INSIDE this body — so a bare install still imports this
    module, and an operator without the extra gets the existing teaching ``ImportError`` naming
    ``pip install '.[pptx]'``.

    The load comes from the SAME :func:`_load_and_compose` sequence :func:`build_weekly_surfaces`
    uses, because ``weekly_slots(load, surface)`` must be given the SAME load the surface was
    composed from — the slot derivation checks its disclosure lines against ``surface.missing`` and
    refuses to emit a line that is neither the author's words nor the recorded disclosure.

    SECURITY (threat T-02-08, path traversal): ``out_path`` is **caller-supplied and never derived
    from Surface content** — the property ``render_surface_pptx``'s docstring states, preserved
    here. Joining ``surface.id`` (authored data) to a directory would be a traversal primitive.

    Never compared to the template, in any form — not bytes, not ``part_digest``, not part order:
    python-pptx's LOAD path re-serializes empty core properties and re-orders parts, so that
    comparison is guaranteed-wrong for reasons that have nothing to do with this record. The golden
    deck comes from the WRITER (02-03 decision).

    Args:
        out_path: where to write the deck. The caller's choice; the parent is created if absent.
        root: the repo root the paths resolve against (default cwd).
        spec_path: an explicit Weekly Spec (default: discover the single ``*.yml``).
        lanes_path: an explicit lane config (default: discover the single ``*.yml`` under the
            module corpus — the W0-1 lineage link).
        template: the operator's template deck (default: ``<corpus>/template.pptx``).
        author: the byline (see :func:`build_weekly_surfaces`).

    Returns:
        The written deck path. Its digest sidecar is ``<out_path>.digest``.
    """
    from .pptx_writer import part_digest, render_surface_pptx
    from .weeklyspec import weekly_slots

    root_path = (Path(root) if root is not None else Path.cwd()).resolve()
    load, surface = _load_and_compose(
        root=root, spec_path=spec_path, lanes_path=lanes_path, author=author
    )

    deck_template = (
        Path(template)
        if template is not None
        else root_path / _CORPUS_DIR / _TEMPLATE_NAME
    )
    if not deck_template.is_file():
        # Fail LOUD and whole, never partial: a missing template must not leave a half-written
        # deck on disk for the next reader to mistake for a rendered one.
        raise FileNotFoundError(
            f"no template deck at {deck_template} — point --template at a .pptx whose "
            "Selection-Pane shape names start with 'NL_', or restore the corpus copy"
        )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    render_surface_pptx(
        surface,
        template=deck_template,
        slots=weekly_slots(load, surface),
        out_path=out,
    )

    # The tier-1 tamper sidecar: ``part_digest`` is sorted, length-prefixed
    # ``(part name, sha256(part))`` rows, so it is independent of which zlib built the archive —
    # a full-file hash would be green locally and red on a runner with identical part content.
    digest = out.with_suffix(out.suffix + ".digest")
    digest.write_text(part_digest(out.read_bytes()) + "\n", encoding="utf-8")

    return out
