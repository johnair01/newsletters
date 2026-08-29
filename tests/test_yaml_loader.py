"""The parse boundary refuses duplicate mapping keys — CR-01 (03-review), proven at every level.

``yaml.safe_load`` keeps only the LAST occurrence of a duplicated mapping key: a weekly authored
with ``highlights:`` twice loses its entire first list before any validator ever sees it — the
exact silent drop the strict spec schemas exist to refuse. The fix lives in ONE place
(``_yaml_loader.load_config``), so this module proves it at the boundary AND through all three
loaders that parse through it (``weeklyspec`` / ``casespec`` / ``swimlane``) — inheritance
asserted, never assumed.

Also proven: the refusal is a REFUSAL only of duplicates. Anchors/aliases, nested mappings and
the committed fixtures (which carry no duplicates) all still parse — the boundary stays
``SafeLoader``-only construction throughout.
"""

from __future__ import annotations

import pathlib

import pytest

from newsletters._yaml_loader import load_config
from newsletters.casespec import load_case_spec
from newsletters.swimlane import load_swimlanes
from newsletters.weeklyspec import load_weekly_spec

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"


# --------------------------------------------------------------------------- #
# The boundary itself — one implementation, teaching error, both line numbers
# --------------------------------------------------------------------------- #


def test_duplicate_top_level_key_is_refused_never_last_wins() -> None:
    """The CR-01 reproduction: the exact document the review proved silently drops a list."""
    text = (
        'week: "W1"\n'
        "highlights:\n"
        '  - "first block line"\n'
        "highlights:\n"
        '  - "second block line"\n'
    )
    with pytest.raises(ValueError, match="duplicate key 'highlights'") as excinfo:
        load_config(text)
    message = str(excinfo.value)
    # The teaching error names BOTH occurrences so the author can fix the right one.
    assert "at line 4" in message, message
    assert "first authored at line 2" in message, message
    assert "Refusing to drop authored content silently" in message, message


def test_duplicate_key_inside_a_nested_mapping_is_refused() -> None:
    """The same hole one level down (a duplicated field inside a record) is the same refusal."""
    text = (
        "assets:\n"
        "  chart-x:\n"
        '    folder: "Pack A"\n'
        '    folder: "Pack B"\n'
    )
    with pytest.raises(ValueError, match="duplicate key 'folder'"):
        load_config(text)


def test_unique_keys_and_aliases_still_parse() -> None:
    """Non-vacuity for the accept side: the refusal fires ONLY on duplicates."""
    parsed = load_config(
        "owner: &o owner-a\n"
        "sections:\n"
        "  - heading: One\n"
        "    owner: *o\n"
        "  - heading: Two\n"
    )
    assert parsed["owner"] == "owner-a"
    assert parsed["sections"][0]["owner"] == "owner-a"
    assert [s["heading"] for s in parsed["sections"]] == ["One", "Two"]


# --------------------------------------------------------------------------- #
# All three loaders inherit the refusal — through their own public entry points
# --------------------------------------------------------------------------- #


def _write(tmp_path: pathlib.Path, name: str, text: str) -> pathlib.Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_weekly_spec_loader_refuses_a_duplicated_key(tmp_path: pathlib.Path) -> None:
    path = _write(
        tmp_path,
        "weekly-dup.yml",
        'week: "W1"\nhighlights:\n  - "kept"\nhighlights:\n  - "shadowing"\n',
    )
    with pytest.raises(ValueError, match="duplicate key 'highlights'"):
        load_weekly_spec(path, root=tmp_path)


def test_case_spec_loader_refuses_a_duplicated_key(tmp_path: pathlib.Path) -> None:
    path = _write(tmp_path, "case-dup.yml", 'case: "First"\ncase: "Second"\n')
    with pytest.raises(ValueError, match="duplicate key 'case'"):
        load_case_spec(path, root=tmp_path)


def test_swimlane_loader_refuses_a_duplicated_key(tmp_path: pathlib.Path) -> None:
    path = _write(
        tmp_path, "module-dup.yml", "module: module-a\nmodule: module-b\nlanes: []\n"
    )
    with pytest.raises(ValueError, match="duplicate key 'module'"):
        load_swimlanes(path, root=tmp_path)


# --------------------------------------------------------------------------- #
# The committed corpora carry no duplicates — the fix disturbs nothing shipped
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "relative",
    [
        "weekly/weekly-full.yml",
        "weekly/weekly-sparse.yml",
        "weekly/weekly-editorial-bait.yml",
        "casespec/case-shuttle-turnaround.yml",
        "casespec/case-sparse.yml",
        "swimlane/module-x.yml",
        "swimlane/module-trap.yml",
    ],
)
def test_committed_fixtures_still_parse(relative: str) -> None:
    parsed = load_config((FIXTURES / relative).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict) and parsed
