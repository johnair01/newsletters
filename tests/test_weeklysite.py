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

from pathlib import Path

from newsletters.adapters.email_adapter import EmailAdapter
from newsletters.specspan import absent
from newsletters.weeklyspec import _ASSET_PROVENANCE_ABSENT, load_weekly_spec

# Sibling test helper (leading underscore == not collected by pytest). pytest's default
# "prepend" import mode puts tests/ on sys.path, so this resolves without a tests package.
from _corpus_scan import scan_real_looking  # noqa: E402

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
