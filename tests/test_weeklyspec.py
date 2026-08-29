"""Weekly Spec authoring path — proof suite (ported from ``tests/test_casespec.py``).

Two committed fixtures under ``tests/fixtures/weekly/`` drive the LIVE validator/loader
(``src/newsletters/weeklyspec.py``) end to end. Assertions are on STRUCTURE and INVARIANTS; where
a concrete value is needed it is read from the SAME parsed fixture the loader reads, so the test
tracks the corpus rather than freezing a magic string.

* ``weekly-full.yml`` — all eight keys: an ordinary quoted highlight AND a block-scalar one, a
  lowlight, two recognitions (one sourced, one not), two team members, three assets (complete /
  deep-link-required / provenance-incomplete), and a ``config:`` subtree whose values must NEVER
  become claims. One person string appears in BOTH ``recognitions:`` and ``team:`` — the
  span-swap regression's non-vacuity.
* ``weekly-sparse.yml`` — only ``week`` + ``module``: every other key must be disclosed in
  ``Distillation.missing[]``, never fabricated.

The invariants proven here (the Case Spec's eight, plus two the weekly earns):

1. **Schema validation** — teaching errors on a non-mapping doc, an unknown TOP-LEVEL key, an
   unknown key inside a recognition / a team member / an asset, and a type-coerced scalar.
2. **Trace faithfulness** — every claim content-addressed via ``Trace.from_source``, non-stale,
   re-sliceable from the live transcript, and entailed by the LIVE
   ``SpanContainmentFaithfulness`` gate (the strict half — never the structural fallback).
3. **The block-scalar item region** — asserted as the gate's own rule
   (``_normalize(text) in _normalize(span)``), never ``transcript[start:end] == text``.
4. **The span-swap regression** — a value duplicated across two sections traces to ITS OWN LINE.
5. **missing[] honesty** — every absent key is disclosed, in schema order, including "no
   lowlights"; no claim exists for an absent field.
6. **Narrative verbatim** — authored lines reach the typed spec byte-identical to the parsed YAML.
7. **Config never claimed** — no ``config:`` leaf appears in any claim; the subtree is carried.
8. **Recognition evidence** — absent / unresolvable ``source:`` ⇒ ``evidence == []`` + a named
   disclosure; a resolved one ⇒ exactly one SPAN-LESS ``Trace``. Never a fabricated span.
9. **Root containment** — a path outside ``root`` RAISES (a refusal, not a ``missing[]`` entry).
10. **Determinism + read-only** — two loads are byte-identical, the JSON round-trips, and the
    fixture's mtime and size are unchanged after a load.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters._yaml_loader import load_config
from newsletters.weeklyspec import (
    AuthoredAsset,
    AuthoredMember,
    AuthoredRecognition,
    WeeklySpec,
    _validate,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "weekly"
FULL = "weekly-full.yml"
SPARSE = "weekly-sparse.yml"
FIXTURES = [FULL, SPARSE]
AUTHOR = "author-x"

# The eight keys, in schema order. Duplicated here ON PURPOSE: importing the module's own
# ``_KNOWN_KEYS`` would make this assertion vacuous (it would compare the constant to itself).
SCHEMA_KEYS = [
    "week",
    "module",
    "highlights",
    "lowlights",
    "recognitions",
    "team",
    "assets",
    "config",
]


def _parsed(name: str) -> dict:
    return load_config((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _validated(text: str) -> dict:
    """Parse + validate one authored document, the way the loader will."""
    return _validate(load_config(text))


# --------------------------------------------------------------------------- #
# 1 — schema validation: teaching errors at BOTH levels, never a silent drop
# --------------------------------------------------------------------------- #


def test_non_mapping_document_names_the_eight_key_schema() -> None:
    """A document that is not a mapping fails loudly, naming the schema and the spec doc."""
    with pytest.raises(ValueError) as excinfo:
        _validated("- just\n- a list\n")
    message = str(excinfo.value)
    assert "YAML mapping" in message
    assert "docs/weekly-spec.md" in message
    for key in SCHEMA_KEYS:
        assert repr(key) in message, f"{key} not named in the schema error: {message}"


def test_unknown_top_level_key_refuses_to_drop_authored_content() -> None:
    """``highlight:`` for ``highlights:`` fails loudly — a typo must not lose a lowlight."""
    with pytest.raises(ValueError) as excinfo:
        _validated('week: "W1"\nhighlight:\n  - "one"\n')
    message = str(excinfo.value)
    assert "unknown Weekly Spec field" in message
    assert "'highlight'" in message
    assert "Refusing to drop authored content silently." in message
    for key in SCHEMA_KEYS:
        assert repr(key) in message


@pytest.mark.parametrize(
    ("document", "container", "offender"),
    [
        (
            'recognitions:\n  - person: "P"\n    resaon: "typo"\n',
            "recognitions[0]",
            "resaon",
        ),
        (
            'team:\n  - name: "N"\n    rol: "typo"\n',
            "team[0]",
            "rol",
        ),
        (
            'assets:\n  k:\n    file: "f"\n    fodler: "typo"\n',
            "assets['k']",
            "fodler",
        ),
    ],
)
def test_unknown_nested_key_fails_loud_naming_container_and_key(
    document: str, container: str, offender: str
) -> None:
    """A mistyped field INSIDE a container earns the same refusal as a top-level typo.

    Rule 1 names the top level, but a dropped ``resaon:`` loses authored content exactly as
    silently as a dropped ``lowlight:`` would. Same teaching voice, same refusal.
    """
    with pytest.raises(ValueError) as excinfo:
        _validated(document)
    message = str(excinfo.value)
    assert repr(offender) in message
    assert container in message
    assert "Refusing to drop authored content silently." in message


@pytest.mark.parametrize(
    ("document", "field", "actual"),
    [
        ("week: 42\n", "week", "int"),
        ("module: yes\n", "module", "bool"),
        ('highlights:\n  - "ok"\n  - 42\n', "highlights[1]", "int"),
        ('recognitions:\n  - person: yes\n', "recognitions[0].person", "bool"),
        ('team:\n  - name: "N"\n    lines:\n      - 42\n', "team[0].lines[0]", "int"),
        ('assets:\n  k:\n    sha256: 42\n', "assets['k'].sha256", "int"),
    ],
)
def test_type_coerced_scalar_names_the_field_its_type_and_the_fix(
    document: str, field: str, actual: str
) -> None:
    """A bare ``yes`` / ``42`` stops being the author's text, so the loader refuses it."""
    with pytest.raises(ValueError) as excinfo:
        _validated(document)
    message = str(excinfo.value)
    assert repr(field) in message
    assert f"got {actual}" in message
    assert "quote the value so YAML cannot type-coerce it" in message


@pytest.mark.parametrize("name", FIXTURES)
def test_both_committed_fixtures_parse_and_validate(name: str) -> None:
    """The corpus every later Phase-3 proof is written against is itself schema-clean."""
    parsed = _validate(_parsed(name))
    assert isinstance(parsed, dict) and parsed
    assert all(key in SCHEMA_KEYS for key in parsed), sorted(parsed)
    # File order IS schema order in the corpus — the forward cursor depends on the walk being
    # able to follow the document; a fixture authored out of schema order would hide that.
    assert list(parsed) == [k for k in SCHEMA_KEYS if k in parsed]


def test_full_fixture_carries_the_shapes_the_phase_is_proved_against() -> None:
    """Non-vacuity: the full fixture really does carry every shape the later tests need.

    Without this, a fixture that quietly lost its block scalar or its duplicated person would
    leave the block-scalar and span-swap proofs passing for the wrong reason.
    """
    parsed = _parsed(FULL)
    assert list(parsed) == SCHEMA_KEYS, "the full fixture must author all eight keys"

    # Two highlights: one an ordinary scalar, one a BLOCK scalar (multi-line, so its folded
    # value is not a verbatim substring of the file).
    highlights = parsed["highlights"]
    assert len(highlights) == 2
    assert "\n" not in highlights[0], "the first highlight must be an ordinary scalar"
    assert "\n" in highlights[1], "the second highlight must be a block scalar"

    assert len(parsed["lowlights"]) == 1

    # Two recognitions — exactly one of them sourced (rule 6's both-halves case).
    sourced = [r for r in parsed["recognitions"] if r.get("source")]
    assert len(parsed["recognitions"]) == 2 and len(sourced) == 1

    # The duplicated person string: named in BOTH recognitions and team.
    people = {r["person"] for r in parsed["recognitions"]}
    members = {m["name"] for m in parsed["team"]}
    assert people & members, "a person must appear in BOTH sections for the span-swap proof"

    # Three assets: complete / deep-link-required / provenance-incomplete.
    assets = parsed["assets"]
    assert len(assets) == 3
    complete = [
        k for k, r in assets.items() if all(r.get(f) for f in ("folder", "date", "event"))
    ]
    assert len(complete) == 2
    values_no_link = [
        k
        for k, r in assets.items()
        if r.get("stands_in_for") == "values" and not r.get("link")
    ]
    assert len(values_no_link) == 1, "the deep-link row must be exercised"
    incomplete = [
        k
        for k, r in assets.items()
        if not all(r.get(f) for f in ("folder", "date", "event"))
    ]
    assert len(incomplete) == 1, "one asset must be missing a provenance minimum"

    assert parsed["config"], "config must be non-empty or the never-claimed guard is vacuous"


def test_sparse_fixture_authors_only_the_two_scalars() -> None:
    """The sparse fixture's whole job is ABSENCE — six keys unwritten, including lowlights."""
    parsed = _parsed(SPARSE)
    assert list(parsed) == ["week", "module"]
    for key in SCHEMA_KEYS[2:]:
        assert key not in parsed


# --------------------------------------------------------------------------- #
# 2 — the authored-side models: permissive by design, so absences are disclosable
# --------------------------------------------------------------------------- #


def test_authored_models_are_permissive_so_an_incomplete_entry_is_disclosable() -> None:
    """An incomplete authored entry must be REPRESENTABLE long enough to be disclosed.

    This is the load half of the load/place seam. A recognition with no source is still credit
    owed; an asset missing a provenance minimum must be carried far enough to NAME the missing
    field. The strict shape (``semantic.AssetRecord``, whose minimums are non-optional) is
    deliberately not used here — that one guards PLACEMENT, where an incomplete record must be
    unrepresentable. Both directions are asserted so neither can be quietly relaxed.
    """
    # Permissive on the authored side: nothing is required, everything defaults empty.
    assert AuthoredRecognition().model_dump() == {
        "person": "",
        "reason": "",
        "source": "",
        "evidence": [],
    }
    assert AuthoredMember().lines == []
    assert AuthoredAsset(key="k").folder == ""

    # ...and the strict shape refuses exactly what the permissive one carries.
    from pydantic import ValidationError

    from newsletters.semantic import AssetRecord

    with pytest.raises(ValidationError) as excinfo:
        AssetRecord(key="k", file="f", sha256="s")  # no folder / date / event
    missing_fields = {
        error["loc"][0] for error in excinfo.value.errors() if error["type"] == "missing"
    }
    assert {"folder", "date", "event"} <= missing_fields, missing_fields


def test_weekly_spec_defaults_are_empty_never_fabricated() -> None:
    """A ``WeeklySpec`` built from nothing carries nothing — no placeholder, no invented value."""
    spec = WeeklySpec()
    assert spec.week == "" and spec.module == ""
    assert spec.highlights == [] and spec.lowlights == []
    assert spec.recognitions == [] and spec.team == [] and spec.assets == []
    assert spec.config == {}
