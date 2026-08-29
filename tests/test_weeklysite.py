"""WKLY-05 — the committed synthetic ``weekly`` corpus suite (Phase 4, plan 04-01).

STDLIB ONLY, ON PURPOSE. Nothing in this module imports ``python-pptx`` (not even indirectly:
``pptx_writer``'s module level is stdlib-only and only ``part_digest`` is used here), because this
module runs in the ``site-integrity`` CI job — which installs ``[test,config]`` and has NO
``0 skipped`` assertion. A ``[pptx]``-gated test placed here would skip forever and read as green:
that is W21, and this repo has already paid for it twice. The deck's fresh==committed drift check
is ``[pptx]``-gated and lives in ``tests/test_weekly_golden.py`` (plan 04-02) instead.

What this suite proves against ``weeklysite`` and the committed ``content/weekly/`` corpus:

* the committed corpus carries no real-looking nomenclature (the PROMOTED scanner in
  ``tests/_corpus_scan.py``, with ONE documented allowance and two planted arms proving the
  allowance is not over-broad);
* ``content/weekly/template.pptx`` is a byte-copy of the committed fixture template (P-06 — the
  template is copied, never regenerated, so neither copy can drift);
* the two loader-level planted absences (a recognition with no ``source:``, an asset with no
  ``folder:``) are DISCLOSED, located by the composer's own phrasing rather than by a
  hand-typed disclosure sentence;
* the built surface is a Draft ``Surface(REPORT)`` at ``EPOCH_ZERO`` at ``R-001``, every claim
  traced and content-addressed, and all THREE planted absences reach the rendered honesty panel;
* the corpus's ``config:`` values are bound as metadata and never claimed;
* the output auto-loads zero external resources, is byte-stable across two renders, and the
  committed ``site/`` equals a fresh build;
* the committed deck matches its ``.digest`` sidecar (tier 1, stdlib-only tamper check) and no
  ``.pptx`` exists anywhere under the published ``site/`` tree.

SHARED-LEDGER-PATH CAVEAT (inherited from ``test_modulesite.py``, and it is the same caveat):
``build_weekly_site`` loads and saves its ledger at the FIXED committed path
``content/weekly/ids.json`` (NOT ``out_dir``), so building into a ``tmp_path`` re-saves that
committed file. The committed ledger already holds R-001 and the save is byte-stable
(``sort_keys`` + trailing newline), so every rebuild is IDEMPOTENT — the tests below snapshot the
committed ledger and assert it is byte-unchanged rather than trusting that.
"""

from __future__ import annotations

import hashlib
import html
import re
import shlex
from collections.abc import Iterator
from pathlib import Path

# Sibling test helper (leading underscore == not collected by pytest). pytest's default
# "prepend" import mode puts tests/ on sys.path, so this resolves without a tests package.
from _corpus_scan import scan_real_looking
from pydantic import BaseModel
from typer.testing import CliRunner

from newsletters import weeklysite, weeklyspec
from newsletters.adapters._timestamps import EPOCH_ZERO
from newsletters.adapters.email_adapter import EmailAdapter
from newsletters.cli import app
from newsletters.compose import NO_KPIS
from newsletters.pptx_writer import part_digest
from newsletters.semantic import Claim, ClaimsBlock, Source, Surface, Trace
from newsletters.site import Ledger, Site
from newsletters.specspan import absent
from newsletters.templates import REPORT
from newsletters.weeklysite import build_weekly_site, build_weekly_surfaces
from newsletters.weeklyspec import load_weekly_spec

# The two module-private disclosure constants are reached through the MODULE rather than
# imported by name, so this file's imports stay one-per-line (DEF-15: isort and black disagree
# on every parenthesized multi-line import until isort gets a `profile = "black"`).
_ASSET_PROVENANCE_ABSENT = weeklyspec._ASSET_PROVENANCE_ABSENT
_RECOGNITIONS_KEY = weeklyspec._RECOGNITIONS_KEY

# The committed corpus lives under the repo root (mirror test_modulesite's anchor).
REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = REPO_ROOT / "content" / "weekly"

# RFC 6761 reserves ``.invalid`` — a domain that is guaranteed never to resolve, so an address
# there cannot belong to a real person. This is the ONE allowance the weekly scan takes, and it
# exists because the corpus commits an ``.eml``: the scanner treats an address SHAPE as its proxy
# for a real name, and every header of a synthetic message is a shape.
_RESERVED_DOMAIN = "@example.invalid"


def _scan_weekly(text: str) -> set[str]:
    """``scan_real_looking`` minus the documented RFC 6761 reserved-domain allowance.

    Subtracting ONLY hits that end in the reserved domain keeps the allowance as narrow as it can
    be: a real-looking NAME still trips, and so does an address at any other domain.
    """
    return {
        hit for hit in scan_real_looking(text) if not hit.endswith(_RESERVED_DOMAIN)
    }


def _corpus_files() -> list[Path]:
    """Every committed weekly file whose text a reader could publish, in a stable order."""
    files = sorted(CORPUS.glob("*.yml")) + sorted((CORPUS / "inbox").glob("*.eml"))
    ledger = CORPUS / "ids.json"
    if ledger.exists():  # written by plan 04-01 task 2; the scan must not wait for it
        files.append(ledger)
    files += sorted((CORPUS / "site").glob("*.html"))
    return files


def test_committed_content_is_synthetic() -> None:
    """T-04-02: every committed content/weekly/ file carries only synthetic fabricated names.

    Scans the authored spec, the committed ``.eml``, the ledger and the rendered ``site/*.html``
    through the PROMOTED scanner, with the single ``@example.invalid`` allowance documented on
    :func:`_scan_weekly`. TWO planted arms keep the clean pass non-vacuous in both directions:
    a real-looking NAME still trips the scanner, and an address at a NON-reserved domain still
    trips it THROUGH the allowance — without that second arm the allowance could quietly widen
    into "ignore every address" and nobody would notice.
    """
    files = _corpus_files()
    assert files, "no committed weekly content to scan — the corpus is not populated"

    for f in files:
        text = f.read_text(encoding="utf-8")
        leaks = _scan_weekly(text)
        assert not leaks, (
            f"real-looking nomenclature in committed {f.relative_to(REPO_ROOT)}: {sorted(leaks)} "
            "— committed public content must be synthetic (T-04-02)"
        )

    # Non-vacuous, arm 1: the SAME scanner catches a planted real-looking name.
    planted_name = "owner: Jean-Luc Picard\n"
    assert "Jean-Luc Picard" in _scan_weekly(planted_name), _scan_weekly(planted_name)

    # Non-vacuous, arm 2: a NON-reserved address survives the allowance and still trips.
    planted_address = "contact: ops@starfleet.int\n"
    hits = _scan_weekly(planted_address)
    assert any(
        h.endswith("@starfleet.int") for h in hits
    ), f"the reserved-domain allowance is over-broad — it swallowed {planted_address!r}: {hits}"

    # ...and the allowance itself is real: a reserved-domain address is subtracted.
    assert not _scan_weekly(f"From: Rota Desk <rota-desk{_RESERVED_DOMAIN}>\n")


def test_template_is_byte_copy_of_fixture() -> None:
    """P-06: content/weekly/template.pptx is the committed fixture template, byte-for-byte.

    ``src/`` must not read from ``tests/`` and the recipe must be able to point an operator at a
    real template, so the corpus carries its own copy. P-06 ("the fixture template is NOT
    regenerated") therefore stands on BOTH copies, and this equality is what keeps them from
    drifting: if either is ever regenerated, this fails and names the decision.
    """
    corpus_template = CORPUS / "template.pptx"
    fixture_template = REPO_ROOT / "tests" / "fixtures" / "weekly" / "template.pptx"
    assert corpus_template.is_file(), "the corpus is missing its template.pptx copy"
    assert corpus_template.read_bytes() == fixture_template.read_bytes(), (
        "content/weekly/template.pptx has drifted from tests/fixtures/weekly/template.pptx — "
        "P-06: the template is COPIED, never regenerated (its part digests are committed "
        "determinism evidence)"
    )


def _committed_eml_source():
    """Parse the committed ``.eml`` into the ``Source`` a recognition's ``source:`` resolves to.

    ``EmailAdapter().parse(raw, path)`` makes ``Source.id`` the path STRING it is handed, so the
    repo-relative POSIX form is passed here for exactly the reason the builder passes it: that is
    the id the authored ``source:`` names, and an absolute path would bake this machine's
    directory layout into the record.
    """
    eml = sorted((CORPUS / "inbox").glob("*.eml"))[0]
    rel = eml.relative_to(REPO_ROOT).as_posix()
    source, _units, _unextracted = EmailAdapter().parse(eml.read_bytes(), rel)
    return source


def test_spec_absences_disclosed() -> None:
    """The two loader-level planted absences are DISCLOSED — and the resolvable one is not.

    Both disclosures are located by the composer's OWN phrasing (``specspan.absent`` and
    ``weeklyspec._ASSET_PROVENANCE_ABSENT``), never by a sentence typed into this test or into
    the fixture: one rule, one wording, and a test that would notice if the wording moved.

    The CONTRAST is what makes the absence row mean something. The first recognition names the
    committed ``.eml``, so it resolves to real evidence and NO unresolvable-source disclosure
    appears; the second names nothing, and that is the row the honesty panel carries.
    """
    spec_path = sorted(CORPUS.glob("*.yml"))[0]
    load = load_weekly_spec(
        spec_path, root=REPO_ROOT, known_sources=[_committed_eml_source()]
    )
    missing = load.distillation.missing

    # Planted absence #2 — a recognition with no source email.
    source_absences = [m for m in missing if m == absent("recognitions[1].source")]
    assert source_absences, (
        "fixture invariant: recognitions[1] must omit `source:` so the honesty panel carries "
        f"the absent-source disclosure. missing[] was: {missing}"
    )

    # Planted absence #3 — an asset with no provenance (the FIRST minimum field, in field order).
    provenance_phrase = _ASSET_PROVENANCE_ABSENT.split("{key!r}")[1].split("{field!r}")[
        0
    ]
    provenance_absences = [m for m in missing if provenance_phrase in m]
    assert provenance_absences, (
        "fixture invariant: one asset must omit a provenance minimum so the honesty panel "
        f"carries the provenance disclosure. missing[] was: {missing}"
    )

    # The contrast: the FIRST recognition resolved, so it carries real evidence...
    resolved = load.spec.recognitions[0]
    assert resolved.evidence, (
        "fixture invariant: recognitions[0].source must name the committed .eml so the absence "
        "row above has a resolvable sibling to contrast against"
    )
    # ...and nothing in the corpus is an unresolvable id (which would be a THIRD, different row).
    assert not [
        m for m in missing if "does not resolve to a known Source" in m
    ], f"an authored `source:` failed to resolve — fix the id, not the test. missing[]: {missing}"


# --------------------------------------------------------------------------- #
# Plan 04-01 Task 2 — the builder, the honesty path on the rendered page,
# determinism, ledger stability and committed==fresh over content/weekly/site/.
# --------------------------------------------------------------------------- #

# The composers' OWN phrasings, DERIVED from their format strings rather than retyped, and used
# only to LOCATE each disclosure inside surface.missing so the assertion reads the real entry text.
# Retyping a disclosure sentence here would create a second wording of the honesty rule, and the
# test would then pass while the reviewer read something else.
_NO_KPIS_PHRASE = NO_KPIS.split("{heading!r}")[1]
_ABSENT_PHRASE = absent("<field>").split("'<field>'")[1]
_PROVENANCE_PHRASE = _ASSET_PROVENANCE_ABSENT.split("{key!r}")[1].split("{field!r}")[0]


def _report_page_name() -> str:
    """The report page's filename, DERIVED from the composed surface identity (content-tracked).

    ``Site.from_surfaces`` uses ``surface.id`` as the slug for a slug-clean id and writes
    ``{slug}.html`` — so the report page name follows the authored identity, never a hardcode.
    """
    return f"{build_weekly_surfaces()[0].id}.html"


def _build_and_read_report(out: Path) -> str:
    """Build the weekly site into ``out`` and return the rendered report page HTML."""
    written = build_weekly_site(out)
    report = out / _report_page_name()
    assert report in written, "build_weekly_site did not emit the weekly report page"
    return report.read_text(encoding="utf-8")


def _iter_claims(obj: object) -> Iterator[Claim]:
    """Every ``Claim`` reachable from ``obj``, walked structurally rather than block-by-block.

    Walking the typed tree (instead of naming the block kinds that carry claims) means a future
    block kind cannot quietly escape the config-never-claimed guard below.
    """
    if isinstance(obj, Claim):
        yield obj
    elif isinstance(obj, BaseModel):
        for name in type(obj).model_fields:
            yield from _iter_claims(getattr(obj, name))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            yield from _iter_claims(item)


def _config_leaves(value: object) -> list[str]:
    """Every string leaf of the authored ``config:`` subtree, at any nesting depth."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [leaf for v in value.values() for leaf in _config_leaves(v)]
    if isinstance(value, (list, tuple)):
        return [leaf for v in value for leaf in _config_leaves(v)]
    return []


def test_every_claim_traced_and_addressed() -> None:
    """Every claim on the weekly surface is traced AND content-addressed, at Draft/EPOCH_ZERO/R-001.

    The trust gate over the composed sample: every claim that survives onto a block is
    ``is_traced`` and every one of its traces ``is_addressed`` — anything unprovable was routed to
    ``surface.missing[]``, never left as a bare/untraced claim. Also asserts the body is real
    (≥1 kept claim) and the honesty panel is GENUINELY populated, so this is not an empty body
    dumped into ``missing[]``; that the surface is a Draft ``REPORT`` created at ``EPOCH_ZERO``
    (no wall clock is reachable through the build); and that a fresh ledger gives it ``R-001``.
    """
    surface = build_weekly_surfaces()[0]

    assert (
        surface.template is REPORT
    ), "the weekly reuses Surface(REPORT) — decision D-01"
    assert (
        not surface.is_published
    ), "the sample must ship Draft — there is no auto-publish path"
    assert (
        surface.created == EPOCH_ZERO
    ), "Surface.created must be EPOCH_ZERO (no datetime.now() in the weekly build)"
    for src in surface.traces:
        assert src.timestamp == EPOCH_ZERO, "the loader must not read the wall clock"

    claim_count = 0
    for claim in _iter_claims(surface.blocks):
        assert claim.is_traced, (
            f"claim {claim.text[:40]!r} is untraced — it should have been routed to "
            "missing[], never left on a block"
        )
        for trace in claim.evidence:
            assert (
                trace.is_addressed
            ), f"claim {claim.text[:40]!r} carries an un-addressed trace (Hole B free pass)"
        claim_count += 1

    assert claim_count >= 1, "no kept claim on any block — the body is empty"
    assert (
        surface.missing
    ), "the honesty panel is empty — the sample must disclose real gaps"


def test_honesty_panel_shows_all_three_planted_absences(tmp_path: Path) -> None:
    """SC-1: all THREE planted absences reach the RENDERED honesty panel, html-escaped.

    "in ``missing[]``" and "shown to the reviewer" are two different claims, and only the second
    one is the product's promise. So each disclosure is first located in ``surface.missing`` by its
    composer's own phrasing — the KPI-less lane via ``compose.NO_KPIS``, the source-less
    recognition via ``specspan.absent``, the provenance-incomplete asset via
    ``weeklyspec._ASSET_PROVENANCE_ABSENT`` — asserted non-empty as a fixture invariant, and then
    asserted ``html.escape``d into the built page. No disclosure sentence is typed into this test.
    """
    surface = build_weekly_surfaces()[0]

    no_kpis = [m for m in surface.missing if _NO_KPIS_PHRASE in m]
    assert no_kpis, (
        "fixture invariant: the bound module config must declare a lane with NO kpis so the "
        f"honesty panel carries the no-KPIs disclosure. missing[] was: {surface.missing}"
    )
    absent_source = [
        m
        for m in surface.missing
        if _ABSENT_PHRASE in m and m.startswith(f"field '{_RECOGNITIONS_KEY}")
    ]
    assert absent_source, (
        "fixture invariant: a recognition must omit `source:` so the honesty panel carries the "
        f"absent-source disclosure. missing[] was: {surface.missing}"
    )
    no_provenance = [m for m in surface.missing if _PROVENANCE_PHRASE in m]
    assert no_provenance, (
        "fixture invariant: an asset must omit a provenance minimum so the honesty panel carries "
        f"the provenance disclosure. missing[] was: {surface.missing}"
    )

    page = _build_and_read_report(tmp_path)
    assert 'class="honesty"' in page, "no honesty panel rendered on the weekly report"
    assert (
        'class="claim-span"' in page
    ), "no verbatim claim-span (claim-beside-trace) rendered"
    for entry in no_kpis + absent_source + no_provenance:
        assert (
            html.escape(entry) in page
        ), f"disclosure is not visible in the rendered honesty panel: {entry!r}"


def test_config_values_never_claimed() -> None:
    """The authored ``config:`` subtree is BOUND as metadata and never becomes a Claim.

    ``config:`` is org-specific by definition — registry names, metric names, the byline. The
    loader carries it and never mints it, and the corpus is authored so no config value is repeated
    in the narrative; this asserts the composed result. The subtree is asserted non-empty first, so
    the guard cannot pass by having nothing to check.
    """
    surface = build_weekly_surfaces()[0]
    spec_path = sorted(CORPUS.glob("*.yml"))[0]
    load = load_weekly_spec(
        spec_path, root=REPO_ROOT, known_sources=[_committed_eml_source()]
    )

    leaves = _config_leaves(load.spec.config)
    assert (
        leaves
    ), "fixture invariant: the corpus must declare a non-empty `config:` subtree"

    for claim in _iter_claims(surface.blocks):
        for leaf in leaves:
            assert leaf not in claim.text, (
                f"the config value {leaf!r} reached a Claim ({claim.text[:60]!r}) — `config:` is "
                "bound, never claimed"
            )
    assert (
        surface.byline
    ), "the config-bound author must reach the Surface byline as METADATA"


def test_no_external_calls(tmp_path: Path) -> None:
    """A2 / T-03-05: the weekly output auto-loads ZERO external resources (self-hosted fonts).

    Mirrors ``test_modulesite.test_no_external_calls`` over the weekly corpus: no Google-Fonts
    host, no ``@import url(http``, no ``src="http"``, no CSS ``url(http`` (@font-face), no
    ``<link href="http">`` — and the self-hosted ``fonts/*.woff2`` the relative @font-face urls
    reference must actually be present.
    """
    written = build_weekly_site(tmp_path)
    pages = sorted(p for p in written if p.suffix == ".html")
    assert pages, "build_weekly_site produced no HTML to scan"

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
    link_href_http = re.compile(
        r"<link\b[^>]*\bhref\s*=\s*['\"]https?://", re.IGNORECASE
    )

    for page in pages:
        text = page.read_text(encoding="utf-8")
        for needle in forbidden:
            assert (
                needle not in text
            ), f"{page.name} bakes an auto-loading external resource: {needle!r}"
        assert not css_url_fetch.search(
            text
        ), f"{page.name} has a CSS url(http...) fetch — weekly fonts must be self-hosted"
        assert not link_href_http.search(
            text
        ), f'{page.name} has a <link href="http..."> auto-loaded resource'

    fonts_dir = tmp_path / "fonts"
    assert (
        fonts_dir.is_dir()
    ), "build_weekly_site did not emit the self-hosted fonts/ dir"
    assert any(
        fonts_dir.glob("*.woff2")
    ), "no woff2 fonts in the weekly output fonts/ dir"


def test_byte_stable_double_render(tmp_path: Path) -> None:
    """The weekly build is byte-stable across two renders (no datetime.now(), no set()).

    Two independent builds into separate dirs must produce the IDENTICAL file set and
    byte-identical contents for EVERY file (HTML + self-hosted fonts). Shared-ledger caveat: both
    builds re-save the committed ``content/weekly/ids.json`` (idempotent — R-001 already recorded,
    append-only, byte-stable save), so the double render is stable and leaves it unchanged.
    """
    a, b = tmp_path / "a", tmp_path / "b"
    build_weekly_site(a)
    build_weekly_site(b)

    files_a = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    assert files_a == files_b, "the two weekly renders produced a different file set"
    for rel in files_a:
        assert (a / rel).read_bytes() == (
            b / rel
        ).read_bytes(), f"{rel} is not byte-identical across renders (nondeterminism in the weekly output)"


def test_r001_stable_across_rebuild(tmp_path: Path) -> None:
    """R-001 is stable across a rebuild — the append-only ledger never renumbers on re-sight.

    Uses a FRESH tmp ``ids.json`` (never the committed path) so nothing leaks: a fresh ledger
    assigns the first report ``R-001``; reloading that populated ledger and rebuilding returns the
    SAME ref. The stability is PROVEN by rebuild, not by asserting a literal twice.
    """
    ids = tmp_path / "ids.json"

    ledger = Ledger.load(ids)  # fresh / empty
    site = Site.from_surfaces(build_weekly_surfaces(), ledger=ledger)
    ledger.save()
    first_ref = site.pages()[0].ref
    assert (
        first_ref == "R-001"
    ), f"a fresh ledger must assign the first report ref R-001, got {first_ref!r}"

    reloaded = Ledger.load(ids)  # re-sight the same, now-populated, ledger
    site_again = Site.from_surfaces(build_weekly_surfaces(), ledger=reloaded)
    reloaded.save()
    assert (
        site_again.pages()[0].ref == first_ref
    ), "the append-only ledger renumbered R-001 on rebuild — it must be immutable on re-sight"


def test_committed_equals_fresh_build(tmp_path: Path) -> None:
    """The committed content/weekly/site/ == a fresh build (the committed==fresh-build norm).

    A fresh build into ``tmp_path`` must reproduce every committed file (HTML + fonts) BYTE-for-
    BYTE. Shared-ledger caveat (Pitfall 6): ``build_weekly_site`` writes its ledger to the FIXED
    committed ``content/weekly/ids.json``, NOT ``tmp_path`` — harmless only while the save is
    idempotent, so the committed ledger's bytes are snapshotted first and asserted UNCHANGED
    rather than assumed.
    """
    committed_site = CORPUS / "site"
    committed_ledger = CORPUS / "ids.json"
    assert committed_site.is_dir(), "committed content/weekly/site/ is missing"

    ledger_before = committed_ledger.read_bytes()
    build_weekly_site(tmp_path)
    assert (
        committed_ledger.read_bytes() == ledger_before
    ), "the fresh build mutated the committed ledger — the rebuild must be idempotent (R-001 held)"

    committed_files = sorted(p for p in committed_site.rglob("*") if p.is_file())
    assert committed_files, "no committed weekly site files to compare against"
    for src in committed_files:
        rel = src.relative_to(committed_site)
        built = tmp_path / rel
        assert built.exists(), f"fresh build is missing committed file {rel}"
        assert (
            built.read_bytes() == src.read_bytes()
        ), f"{rel} differs between the committed corpus and a fresh build"


# --------------------------------------------------------------------------- #
# Plan 04-01 Task 3 — the committed deck's TIER-1 integrity gate and the one
# command that regenerates it. Stdlib only: `part_digest` is `zipfile` + `hashlib`
# and `pptx_writer`'s module level imports no optional extra, so these run on a
# bare install and in the site-integrity job. The [pptx]-gated fresh==committed
# drift check (tier 2) lives in tests/test_weekly_golden.py.
# --------------------------------------------------------------------------- #

DECK_DIR = CORPUS / "deck"


def _committed_deck() -> Path:
    """The single committed deck, discovered rather than named (it tracks the authored week)."""
    decks = sorted(DECK_DIR.glob("*.pptx"))
    assert len(decks) == 1, f"expected exactly one committed deck, found {decks}"
    return decks[0]


def test_committed_deck_matches_its_digest() -> None:
    """TIER 1 (T-04-04): the committed deck's part_digest equals its committed .digest sidecar.

    A reader cannot diff a 28 KB zip by eye, so this is the check that says the binary in the repo
    is the binary the writer produced. ``part_digest`` is sorted, length-prefixed
    ``(part name, sha256(part))`` rows — implementation-INDEPENDENT, so it holds across zlib
    versions where a full-file hash would not — and it is stdlib-only, so this fires on EVERY
    install including a bare one.

    The non-vacuity arm digests a DIFFERENT committed ``.pptx`` (the corpus template) and asserts
    it does NOT match: without it, the assertion could be comparing a string to itself and nobody
    would know.
    """
    deck = _committed_deck()
    sidecar = deck.with_suffix(deck.suffix + ".digest")
    assert (
        sidecar.is_file()
    ), f"the committed deck has no digest sidecar at {sidecar.name}"

    recorded = sidecar.read_text(encoding="utf-8").strip()
    assert part_digest(deck.read_bytes()) == recorded, (
        f"{deck.name} does not match its recorded part_digest — the committed deck was "
        "hand-edited or substituted. Regenerate it with `newsletters weekly`, never by editing "
        "the binary or the sidecar."
    )

    # Non-vacuous: a different committed .pptx must NOT satisfy the same assertion.
    other = (CORPUS / "template.pptx").read_bytes()
    assert (
        part_digest(other) != recorded
    ), "the digest assertion does not discriminate — it matches an unrelated .pptx"


def test_deck_is_not_in_the_published_tree() -> None:
    """SC-3, the STRUCTURAL half of "nothing publishes": no deck can reach the published tree.

    ``publish.assemble_site`` copies ``content/*/site`` only, so a deck under ``deck/`` cannot be
    published by a discipline failure — the guarantee holds by layout rather than by care. It also
    keeps the binary out of ``test_publish.py``'s ``read_bytes()``-per-file committed==fresh loop,
    which would compare raw zip bytes across zlib implementations and go red on a runner for a
    reason that has nothing to do with the record's content.
    """
    assert DECK_DIR.is_dir(), "the committed deck dir is missing"
    strays = sorted((CORPUS / "site").rglob("*.pptx"))
    assert not strays, (
        f"a .pptx is inside the PUBLISHED weekly tree: {strays} — decks live in "
        "content/weekly/deck/ and are never served"
    )


def test_weekly_command_is_registered() -> None:
    """The `newsletters weekly` command exists on the shipped CLI, with all five options.

    The recipe (plan 04-03) documents this exact command, and the committed sample was produced by
    it — a renamed flag must turn this red rather than rot the doc. The deck-producing round trip
    itself needs ``[pptx]`` and lives in the extra-gated golden module; this asserts only the
    surface, so this file stays extra-free.
    """
    runner = CliRunner()

    top = runner.invoke(app, ["--help"])
    assert top.exit_code == 0, top.output
    assert "weekly" in top.output, top.output

    weekly_help = runner.invoke(app, ["weekly", "--help"])
    assert weekly_help.exit_code == 0, weekly_help.output
    for option in ("--spec", "--lanes", "--template", "--author", "--out"):
        assert option in weekly_help.output, f"{option} missing from `weekly --help`"


# --------------------------------------------------------------------------- #
# Plan 04-02 Task 1 — the `--corpus weekly` selector: `check` proven to FIRE,
# and `build` routed to the weekly builder.
#
# The shape mirrors tests/test_module_cli.py (the module corpus's own pair), and
# the mirroring is the point: a fourth corpus that reached the CLI without the
# blocking arm would be a fourth gate nobody had ever seen fire.
# --------------------------------------------------------------------------- #

CONTENT = REPO_ROOT / "content"


def _content_fingerprint() -> dict[str, str]:
    """A sha256 per committed file under ``content/`` — the git-free "nothing moved" witness.

    The blocking proof below plants a BLOCKED, PUBLISHED surface. That state must exist only
    inside ``monkeypatch``'s scope and must never touch a committed byte (T-04-10), so the
    assertion is made executable here rather than left to a reviewer running ``git status``.
    Hashing (rather than diffing bytes) keeps the check cheap over the corpora's vendored fonts,
    and a path-keyed map means a file that APPEARED or VANISHED fails too, not just an edit.
    """
    return {
        p.relative_to(REPO_ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(CONTENT.rglob("*"))
        if p.is_file()
    }


def _blocked_published_weekly_surface() -> Surface:
    """One PUBLISHED Report with an un-entailed claim — a single deterministic weekly blocker.

    Mirrors ``test_module_cli._blocked_published_module_surface``: an ADDRESSED trace over a
    transcript that does not contain the claim text. The trace is not stale (its hash matches the
    source), so ``review_blockers`` reports exactly ONE UNENTAILED blocker — enough to flip the
    exit code and prove the weekly corpus runs the same unforked gate. Built in memory only; the
    committed ``content/weekly/`` stays clean and Draft (T-03-07 / T-04-10).
    """
    transcript = "the weekly spec the composed record cites"
    src = Source(id="s-weekly-blocked", transcript=transcript)
    # Addressed (so it is not STALE), but the span omits the claim text — one UNENTAILED blocker.
    trace = Trace.from_source(src, 0, len(transcript))
    claim = Claim(text="the weekly corpus auto-published itself", evidence=[trace])
    surface = Surface(
        id="sfc-weekly-blocked",
        template=REPORT,
        title="Crafted blocked weekly surface",
        blocks=[ClaimsBlock(claims=[claim])],
        traces=[src],
    )
    surface.publish(reviewer="reviewer-w")
    assert surface.is_published
    return surface


def test_check_weekly_clean_exits_zero() -> None:
    """`newsletters check --corpus weekly` over the CLEAN committed corpus exits 0.

    Read this exit code for exactly what it is worth, which is the WIRING and nothing else. It is
    DRAFT-VACUOUS by design: ``review_blockers`` returns ``[]`` for any surface that is not
    Published, publication IS the trust boundary, and this sample ships Draft on purpose — so a
    corpus of pure nonsense would also exit 0 here. Two other tests carry the actual trust:
    ``test_check_weekly_blocks_on_planted_blocker`` below proves the gate can FIRE, and
    ``test_honesty_panel_shows_all_three_planted_absences`` proves this corpus discloses its real
    gaps to the reviewer. This one only proves the selector reaches the builder.
    """
    result = CliRunner().invoke(app, ["check", "--corpus", "weekly"])
    assert result.exit_code == 0, result.output
    assert "All published surfaces clean" in result.output


def test_check_weekly_blocks_on_planted_blocker(monkeypatch) -> None:
    """T-04-09: `check --corpus weekly` runs the SAME UNFORKED gate — proven BLOCKING.

    Inject ONE blocked PUBLISHED surface into the builder the command resolves, and assert the
    gate fires: nonzero exit plus a report naming the offending surface, ``BLOCK`` and ``merge
    blocked``. This only reaches the command because the ``check`` branch imports the MODULE
    OBJECT (``from . import weeklysite``) and resolves the attribute at CALL time — binding the
    function at import time would leave this ``setattr`` patching a name nobody reads, and the
    test would go green while the gate stayed unproven.

    T-04-10, asserted rather than assumed: the planted Published state lives only inside
    ``monkeypatch``'s scope, so every committed byte under ``content/`` is unchanged afterwards.
    """
    before = _content_fingerprint()

    monkeypatch.setattr(
        weeklysite,
        "build_weekly_surfaces",
        lambda *a, **k: [_blocked_published_weekly_surface()],
    )

    blocked = CliRunner().invoke(app, ["check", "--corpus", "weekly"])
    assert blocked.exit_code != 0, blocked.output
    assert "sfc-weekly-blocked" in blocked.output
    assert "BLOCK" in blocked.output
    assert "merge blocked" in blocked.output

    assert _content_fingerprint() == before, (
        "the blocking proof changed a committed file under content/ — a planted blocker must "
        "be a TEST fixture, never a dirty corpus (T-04-10)"
    )


def test_build_weekly_smoke(tmp_path: Path) -> None:
    """`newsletters build --corpus weekly` renders the weekly corpus to a chosen out dir.

    Routes to ``weeklysite.build_weekly_site`` — the report page + the Library — and NOT to the
    deck: the deck is a separate entry point (``newsletters weekly``) precisely so this command
    never needs the ``[pptx]`` extra. The committed corpus is fingerprinted across the build
    because ``build_weekly_site`` re-saves the FIXED committed ledger even for a ``tmp_path``
    build; idempotence is the property that makes that harmless, so it is asserted, not assumed.
    """
    before = _content_fingerprint()
    out = tmp_path / "weeklysite"

    result = CliRunner().invoke(app, ["build", "--corpus", "weekly", "--out", str(out)])

    assert result.exit_code == 0, result.output
    assert (out / _report_page_name()).exists()
    assert (out / "library.html").exists()
    assert not sorted(out.rglob("*.pptx")), "a deck reached the rendered site/ tree"
    assert _content_fingerprint() == before, (
        "a tmp_path weekly build moved a committed file under content/ — the ledger re-save "
        "must be idempotent"
    )


# --------------------------------------------------------------------------- #
# Plan 04-03 Task 1 — the two doc-contract tests over `docs/weekly.md`.
#
# WKLY-06's recipe teaches a human where to point tools at private material and
# which commands to run. Two things can rot it: the CLI can rename a flag under
# it (T-04-15), and an edit can quietly remove a trust statement (T-04-14). Each
# gets a test, and each test carries a NON-VACUITY arm — a doc-contract test that
# silently matches nothing passes forever and protects nothing.
# --------------------------------------------------------------------------- #

RECIPE = REPO_ROOT / "docs" / "weekly.md"

# Every long option token, as it appears in a Typer/Click `--help` body.
_OPTION_RE = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")


def _fenced_command_lines(text: str) -> list[str]:
    """Every fenced ``newsletters …`` line in the recipe, backslash-continuations joined.

    Only lines INSIDE a ``` fence count: prose that mentions a command in backticks is not a
    command an operator pastes, and holding prose to the CLI's option spelling would make the
    test a style police instead of a contract.
    """
    lines: list[str] = []
    buffer: str | None = None
    in_fence = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            buffer = None  # a fence must not swallow the next block
            continue
        if not in_fence:
            continue
        if buffer is None and not stripped.startswith("newsletters "):
            continue
        continued = stripped.endswith("\\")
        piece = stripped[:-1].strip() if continued else stripped
        buffer = piece if buffer is None else f"{buffer} {piece}"
        if not continued:
            lines.append(buffer)
            buffer = None
    return lines


def test_recipe_commands_match_the_shipped_cli() -> None:
    """Every fenced `newsletters …` line in docs/weekly.md runs on the LIVE Typer app (T-04-15).

    The expected command/option set is DRIVEN FROM THE APP — each line's command is invoked with
    ``--help`` and each ``--option`` it uses must appear in that command's own help body — never
    from a hand-written list here. So a renamed flag turns this suite RED instead of leaving the
    recipe teaching a wrong command with confidence.

    Two non-vacuity arms, because a regex that matches nothing would otherwise pass forever: a
    floor on how many command lines were found, and a proof that the check discriminates (an
    invented command and an invented option must both fail it).
    """
    runner = CliRunner()
    commands = _fenced_command_lines(RECIPE.read_text(encoding="utf-8"))

    assert len(commands) >= 4, (
        f"only {len(commands)} fenced `newsletters …` line(s) found in {RECIPE.name} — the "
        "recipe documents at least four, so either the doc lost its commands or this parser "
        "stopped matching them (a doc-contract test that matches nothing protects nothing)"
    )

    for line in commands:
        tokens = shlex.split(line)
        assert tokens[0] == "newsletters", line
        name = tokens[1]

        help_result = runner.invoke(app, [name, "--help"])
        assert help_result.exit_code == 0, (
            f"docs/weekly.md documents `newsletters {name}`, which the shipped app does not "
            f"expose:\n{help_result.output}"
        )
        exposed = set(_OPTION_RE.findall(help_result.output))
        for token in tokens[2:]:
            if not token.startswith("--"):
                continue
            option = token.split("=", 1)[0]
            assert option in exposed, (
                f"docs/weekly.md passes {option} to `newsletters {name}`, which does not expose "
                f"it. Exposed: {sorted(exposed)}"
            )

    # Non-vacuity: the same two checks must FAIL for something the app does not have.
    assert runner.invoke(app, ["weeklyy", "--help"]).exit_code != 0
    assert "--nonesuch" not in set(
        _OPTION_RE.findall(runner.invoke(app, ["weekly", "--help"]).output)
    )


def _prose_of(path: Path) -> str:
    """The document's PROSE: fenced code blocks and HTML comments removed, whitespace collapsed.

    Two reasons, both learned rather than assumed. (a) A document that legitimately QUOTES the
    wording this guard forbids — a code sample, a commented-out line — must not be able to
    self-invalidate the guard; strip that noise first, and if a document ever needs to quote the
    old wording in prose, scope the assertion to the section instead of loosening it. (b) These
    files are hard-wrapped, so ``three committed corpora`` spans a line break in the source: the
    phrase only exists after whitespace is collapsed, and a raw ``in`` check would pass on a
    document that still says it.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    return re.sub(r"\s+", " ", text)


# Per document: what must now be NAMED, and the exact wording this plan removed. Keeping the
# stale phrases here (rather than in a summary's one-off grep) is the point of the test — the
# NEXT corpus cannot make these four documents stale silently.
_FOUR_CORPORA_DOCS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "docs/architecture.md": (
        ("content/weekly/site", "four committed corpora", "weekly"),
        ("three committed corpora", "three corpora", "{rev1|work}"),
    ),
    "docs/surfaces.md": (
        ("four corpora", "/weekly/", "The weekly record"),
        ("three corpora",),
    ),
    "CLAUDE.md": (
        ("content/{rev1,work,module,weekly}/",),
        ("content/{rev1,work,module}/", "three corpora"),
    ),
    "content/README.md": (
        ("content/weekly", "weekly/", "four committed corpora"),
        ("Empty until then", "three corpora"),
    ),
}


def test_docs_describe_four_corpora() -> None:
    """No spec still describes three corpora or a two-value `--corpus` selector (T-04-18).

    A stale spec understates what publishes, and CLAUDE.md's own rule is that a spec the code
    outgrew gets fixed in the change that made it stale. Encoding that as a TEST rather than as a
    one-off grep in a plan summary is what makes it hold for the corpus AFTER this one: the fifth
    corpus will turn these four documents red the moment it lands.
    """
    for rel, (must_name, must_not_say) in _FOUR_CORPORA_DOCS.items():
        prose = _prose_of(REPO_ROOT / rel)
        for phrase in must_name:
            assert phrase in prose, f"{rel} stopped naming {phrase!r} (the weekly)"
        for phrase in must_not_say:
            assert phrase not in prose, (
                f"{rel} still says {phrase!r} — the repo ships FOUR committed corpora "
                "(rev1, work, module, weekly)"
            )


def test_recipe_carries_the_load_bearing_anchors() -> None:
    """The recipe's TRUST claims survive an edit (T-04-14) — not its prose style.

    This is a presence guard over the statements that make the recipe safe to follow: that the
    ingest is read-only and stays local, that nothing auto-publishes and the gate is named, the
    measured `word_wrap` overflow warning, the link to the ONE home of the authoring contract,
    the worked example, and the honest scope statement about what cannot read your numbers. Prose
    may be rewritten freely around these; deleting one of them is what turns this red.
    """
    text = RECIPE.read_text(encoding="utf-8")
    anchors = {
        "read-only": "read-only",
        "stays local": "on your machine",
        "no network call": "makes no network call",
        "nothing is committed": "commits nothing",
        "the review gate, named": "Draft › In Review › Published",
        "no command publishes": "publishes anything",
        "the measured autofit warning": "word_wrap",
        "the authoring contract's ONE home": "weekly-spec.md",
        "the worked example": "content/weekly",
        "no CSV reader": "no CSV reader",
        "no BI value reader": "no Power BI value reader",
    }
    for what, phrase in anchors.items():
        assert phrase in text, f"docs/weekly.md lost its {what} anchor ({phrase!r})"
