"""The Weekly Spec authoring path — a hand-authored weekly becomes a reviewed record.

A module lead writes a **Weekly Spec** (see ``docs/weekly-spec.md``) as YAML in a PR: the period
label (``week``), the module it is for (``module``), what went well and what did not in their own
words (``highlights`` / ``lowlights``), credit where it is owed (``recognitions``), who the module
is this week (``team``), the images and their provenance (``assets``), and the org-specific slots
(``config``). This module lifts that file through the existing zero-AI spine: content-addressed
``Source`` → span-traced ``Claim``s → ``Distillation``. No new spine concept; the review gate is
untouched.

THE WEEKLY SPEC IS A **SIBLING** OF THE CASE SPEC, NOT AN EXTENSION OF IT
(``docs/weekly-spec.md`` lines 11-17). The *mechanism* is reused verbatim — the promoted
``specspan.SpanMinter``, ``safe_load`` through the lazy ``[config]`` boundary, root containment,
``config:`` bound but never claimed. The *key set* is separate and lives here. Widening
``casespec._validate`` to accept weekly fields would make a Case Spec silently accept weekly keys
**and** a Weekly Spec silently accept case keys — destroying, in both directions, the
strict-schema guarantee that is the whole point of a teaching error.

The contract (mirrors ``casespec.py``):

* READ-ONLY / DETERMINISTIC. The only filesystem op is ``Path.read_text``; parsing is
  ``yaml.safe_load`` via the lazy ``[config]`` boundary (``_yaml_loader`` — no top-level
  ``import yaml`` anywhere here). ``Source.timestamp`` is ``EPOCH_ZERO``; fields are walked in
  FILE ORDER; two loads are byte-identical.
* FILE ORDER IS A CORRECTNESS CONDITION, NOT A STYLE. ``SpanMinter`` is a forward-only cursor, so
  every nested collection is iterated via its own ``.items()`` in the author's order rather than
  against a hardcoded field list. 03-RESEARCH proved by execution that minting a later field
  first silently SWAPS the spans of a value duplicated across two sections (a person named in
  both ``recognitions:`` and ``team:``) — and that both claims still pass the faithfulness gate,
  because the text is identical. No gate can catch that; only file order prevents it.
* FAITHFUL, NOT SUGGESTIVE. Authored narrative reaches the typed spec byte-verbatim: never
  summarised, never reordered by importance, never merged, never given connective prose
  (``docs/weekly-spec.md`` rule 3). Emphasis is the author's job.
* STRICT SCHEMA, AT BOTH LEVELS. An unknown key — top level *or* inside a recognition, a team
  member or an asset — fails LOUDLY. Rule 1 names the top level; the same reasoning applies one
  level down, because a mistyped ``resaon:`` inside a recognition would drop authored content
  just as silently as a mistyped ``lowlight:`` at the top.
* CONFIG IS NEVER A CLAIM. The ``config:`` subtree (system names, metrics, registries — org
  specifics) is carried on ``WeeklySpec.config`` for downstream binding, but no config value is
  ever minted into a claim or rendered into a block. Specifics stay config.
* EVERY ABSENCE IS DISCLOSED. Anything absent, empty or unlocatable lands in
  ``Distillation.missing[]`` — including *"no lowlights were authored"*, precisely the absence a
  weekly is tempted to hide (rule 4). Never fabricated, never silently dropped.

Load and placement are two different jobs, and this module is the LOAD half.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence, Union

from pydantic import BaseModel, Field

from ._yaml_loader import load_config as _parse_config
from .adapters._timestamps import EPOCH_ZERO
from .semantic import Claim, Distillation, Source, Trace
from .specspan import GATE, SpanMinter, absent

__all__ = [
    "AuthoredAsset",
    "AuthoredMember",
    "AuthoredRecognition",
    "WeeklySpec",
    "WeeklySpecLoad",
    "load_weekly_spec",
]

# The schema — GENERIC field names only (never an org/fixture value; LANE-03 discipline, policed
# by tests/test_abstraction_guard.py, which walks every *.py under src/newsletters/).
_WEEK_KEY = "week"
_MODULE_KEY = "module"
_HIGHLIGHTS_KEY = "highlights"
_LOWLIGHTS_KEY = "lowlights"
_RECOGNITIONS_KEY = "recognitions"
_TEAM_KEY = "team"
_ASSETS_KEY = "assets"
_CONFIG_KEY = "config"
_KNOWN_KEYS = (
    _WEEK_KEY,
    _MODULE_KEY,
    _HIGHLIGHTS_KEY,
    _LOWLIGHTS_KEY,
    _RECOGNITIONS_KEY,
    _TEAM_KEY,
    _ASSETS_KEY,
    _CONFIG_KEY,
)
# The two top-level narrative strings (the rest have their own shapes).
_STR_KEYS = (_WEEK_KEY, _MODULE_KEY)
# The two lists of authored narrative lines, one per NarrativeBlock tone.
_NARRATIVE_KEYS = (_HIGHLIGHTS_KEY, _LOWLIGHTS_KEY)

# Per-container allowed fields, in schema order. An unknown field in any of them is the same
# teaching refusal as an unknown top-level key: dropping it would lose what the author wrote.
_RECOGNITION_FIELDS = ("person", "reason", "source")
_MEMBER_FIELDS = ("name", "role", "lines", "photo")
_ASSET_FIELDS = (
    "file",
    "sha256",
    "folder",
    "date",
    "event",
    "link",
    "stands_in_for",
    "caption",
    "alt",
)
# The provenance minimum (decision D-02). Placement is plan 03-03's; the names live here because
# they are part of the schema this validator polices.
_PROVENANCE_MINIMUMS = ("folder", "date", "event")

_SPEC_DOC = "docs/weekly-spec.md"
_QUOTE_FIX = "quote the value so YAML cannot type-coerce it"

# The spec's own wording for an authored reference that names nothing (``docs/weekly-spec.md``
# §"The routing", last row). A ``source:`` that resolves to no known ``Source`` gets the
# ABSENT-source treatment — never a minted empty ``Trace`` and never a silent field drop, because
# either direction would fabricate or erase exactly what ``missing[]`` exists to surface. The one
# difference from a truly absent ``source:`` is this text, which names the id so the author can
# fix the typo.
_UNRESOLVABLE_SOURCE = (
    "recognition for {person!r}: source {source!r} does not resolve to a known Source "
    "— carried, with the unresolvable id disclosed"
)


class AuthoredRecognition(BaseModel):
    """Credit for one person, exactly as authored — permissive on purpose.

    Every field defaults to empty because an incomplete recognition must be REPRESENTABLE long
    enough to be disclosed: dropping it would erase credit (``docs/weekly-spec.md`` rule 6).
    ``evidence`` mirrors ``semantic.Recognition.evidence`` and may legitimately stay empty — a
    ``source:`` that is absent, or that resolves to no known ``Source``, yields ``[]`` plus a
    named disclosure, NEVER a fabricated ``Trace``. The author's own word is separately evidenced:
    ``person`` and ``reason`` are minted as gate-entailed claims at real spans of the spec file.
    """

    person: str = ""
    reason: str = ""
    source: str = ""
    evidence: list[Trace] = Field(default_factory=list)


class AuthoredMember(BaseModel):
    """One team member exactly as authored — permissive on purpose (absences are disclosed).

    ``photo`` holds an ``assets:`` KEY, never a file path, so a team photo goes through the same
    provenance routing as every other placed image instead of around it. Resolving that key
    against the *placed* assets is plan 03-03's second pass; here it is carried verbatim.
    """

    name: str = ""
    role: str = ""
    lines: list[str] = Field(default_factory=list)
    photo: str = ""


class AuthoredAsset(BaseModel):
    """One ``assets:`` entry exactly as authored — the LOAD side of the load/place seam.

    THE CONTRAST THAT MATTERS, and the reason this is not ``semantic.AssetRecord``:

    * ``AssetRecord``'s provenance minimums (``file`` / ``sha256`` / ``folder`` / ``date`` /
      ``event``) are NON-OPTIONAL, so "an asset without provenance reached a ``Surface``" is
      unrepresentable — the type-level half of decision D-02.
    * An *authored* asset, however, must be representable **while incomplete**, or the loader
      could not carry it far enough to disclose what is missing. A spec that refused to parse an
      incomplete asset would fail the whole weekly instead of naming the one absent field.

    So: permissive here, strict there. The seam between them is placement (plan 03-03), which
    checks the provenance minimums, the deep link, the root containment and the content address,
    and either mints an ``AssetRecord`` + ``AssetBlock`` or writes the spec's named disclosure to
    ``missing[]``. ``key`` carries the ``assets:`` mapping key so the record keeps its handle.
    """

    key: str = ""
    file: str = ""
    sha256: str = ""
    folder: str = ""
    date: str = ""
    event: str = ""
    link: str = ""
    stands_in_for: str = ""
    caption: str = ""
    alt: str = ""


class WeeklySpec(BaseModel):
    """The typed Weekly Spec — the parsed, validated authoring schema (values byte-verbatim).

    ``assets`` is a LIST rather than a mapping so the authored file order is carried explicitly:
    order is part of the determinism claim (media parts are numbered in add order), and an
    explicit sequence states that rather than leaning on dict insertion order surviving every
    round-trip. Each entry keeps its ``assets:`` key in ``AuthoredAsset.key``.
    """

    week: str = ""
    module: str = ""
    highlights: list[str] = Field(default_factory=list)
    lowlights: list[str] = Field(default_factory=list)
    recognitions: list[AuthoredRecognition] = Field(default_factory=list)
    team: list[AuthoredMember] = Field(default_factory=list)
    assets: list[AuthoredAsset] = Field(default_factory=list)
    # Org-specific slots. Carried for downstream binding; NEVER rendered into claims.
    config: dict[str, Any] = Field(default_factory=dict)


class WeeklySpecLoad(BaseModel):
    """One loaded Weekly Spec: the content-addressed ``Source``, the typed spec, the truth."""

    source: Source
    spec: WeeklySpec
    distillation: Distillation


def _require_str(value: object, where: str) -> None:
    """A narrative field must be a string — a bare ``yes`` or ``42`` stops being the author's text."""
    if value is not None and not isinstance(value, str):
        raise ValueError(
            f"Weekly Spec field {where!r} must be a string, got {type(value).__name__} "
            f"— {_QUOTE_FIX}."
        )


def _require_known_fields(
    item: dict[str, Any], allowed: tuple[str, ...], where: str
) -> None:
    """Nested strict-schema refusal — the same teaching voice as the top-level check.

    Rule 1 names the top level, but a mistyped field one level down (``resaon:`` inside a
    recognition) would drop authored content just as silently, so it earns the same refusal.
    """
    unknown = [k for k in item if k not in allowed]
    if unknown:
        raise ValueError(
            f"unknown field(s) {unknown!r} in {where!r} — the fields there are exactly "
            f"{list(allowed)!r}. Refusing to drop authored content silently."
        )


def _require_mapping_items(value: object, key: str) -> list[dict[str, Any]]:
    """``recognitions`` / ``team`` must be sequences of mappings; anything else fails loudly."""
    if not isinstance(value, list):
        raise ValueError(
            f"'{key}' must be a list of entries, got {type(value).__name__}. "
            f"See {_SPEC_DOC}."
        )
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(
                f"'{key}' entry {index} must be a mapping of its fields, "
                f"got {type(item).__name__}. See {_SPEC_DOC}."
            )
    return value


def _validate(parsed: object) -> dict[str, Any]:
    """Strict schema validation with teaching errors — a typo fails loudly, never silently.

    Three parts, mirroring ``casespec._validate``'s voice: (1) the document is a mapping of
    exactly the eight keys; (2) every value has the shape the schema declares; (3) every NESTED
    container carries exactly its own declared fields. Part (3) is the widening the weekly needs
    and the Case Spec does not — and it is a widening of THIS validator only. ``casespec``'s stays
    exactly eight case keys wide (``docs/weekly-spec.md`` lines 11-17).
    """
    if not isinstance(parsed, dict):
        raise ValueError(
            "a Weekly Spec must be a YAML mapping of the schema fields "
            f"{list(_KNOWN_KEYS)!r}; got {type(parsed).__name__!r}. See {_SPEC_DOC}."
        )
    unknown = [k for k in parsed if k not in _KNOWN_KEYS]
    if unknown:
        raise ValueError(
            f"unknown Weekly Spec field(s) {unknown!r} — the schema is exactly "
            f"{list(_KNOWN_KEYS)!r}. Refusing to drop authored content silently."
        )

    for key in _STR_KEYS:
        _require_str(parsed.get(key), key)

    for key in _NARRATIVE_KEYS:
        value = parsed.get(key)
        if value is None:
            continue
        if not isinstance(value, list):
            raise ValueError(
                f"'{key}' must be a list of authored lines, got {type(value).__name__}. "
                f"One line per entry — the composer never merges two lines into one. "
                f"See {_SPEC_DOC}."
            )
        for index, item in enumerate(value):
            _require_str(item, f"{key}[{index}]")

    recognitions = parsed.get(_RECOGNITIONS_KEY)
    if recognitions is not None:
        for index, item in enumerate(
            _require_mapping_items(recognitions, _RECOGNITIONS_KEY)
        ):
            where = f"{_RECOGNITIONS_KEY}[{index}]"
            _require_known_fields(item, _RECOGNITION_FIELDS, where)
            for field, value in item.items():
                _require_str(value, f"{where}.{field}")

    team = parsed.get(_TEAM_KEY)
    if team is not None:
        for index, item in enumerate(_require_mapping_items(team, _TEAM_KEY)):
            where = f"{_TEAM_KEY}[{index}]"
            _require_known_fields(item, _MEMBER_FIELDS, where)
            for field, value in item.items():
                if field == "lines":
                    if value is None:
                        continue
                    if not isinstance(value, list):
                        raise ValueError(
                            f"'{where}.lines' must be a list of short authored lines, "
                            f"got {type(value).__name__}. See {_SPEC_DOC}."
                        )
                    for line_index, line in enumerate(value):
                        _require_str(line, f"{where}.lines[{line_index}]")
                else:
                    _require_str(value, f"{where}.{field}")

    assets = parsed.get(_ASSETS_KEY)
    if assets is not None:
        if not isinstance(assets, dict):
            raise ValueError(
                f"'{_ASSETS_KEY}' must be a mapping of asset key → record, "
                f"got {type(assets).__name__}. The key is how 'photo:' and prose refer to "
                f"the asset. See {_SPEC_DOC}."
            )
        for asset_key, record in assets.items():
            where = f"{_ASSETS_KEY}[{asset_key!r}]"
            if not isinstance(record, dict):
                raise ValueError(
                    f"{where} must be a mapping of its provenance record, "
                    f"got {type(record).__name__}. The minimum is "
                    f"{list(_PROVENANCE_MINIMUMS)!r}. See {_SPEC_DOC}."
                )
            _require_known_fields(record, _ASSET_FIELDS, where)
            for field, value in record.items():
                _require_str(value, f"{where}.{field}")

    config = parsed.get(_CONFIG_KEY)
    if config is not None and not isinstance(config, dict):
        raise ValueError(
            f"'{_CONFIG_KEY}' must be a mapping of org-specific slots, "
            f"got {type(config).__name__}."
        )
    return parsed


def _resolve_recognition_evidence(
    recognitions: list[AuthoredRecognition], known_ids: set[str], missing: list[str]
) -> None:
    """Second pass: turn each authored ``source:`` into a POINTER, a disclosure, or both halves.

    Runs over ALREADY-MINTED data and never re-enters the minter — the forward cursor must only
    ever be walked in file order, so reference resolution is a separate pass by construction, not
    by convention.

    Three outcomes, one per row of ``docs/weekly-spec.md``:

    * ``source:`` absent → ``evidence == []`` plus the absence disclosure. The recognition is
      still carried: the author's word is the evidence, and ``person`` / ``reason`` are already
      minted as gate-entailed claims at real spans of the spec file (rule 6).
    * ``source:`` resolves to a known ``Source`` → exactly ONE span-less ``Trace`` to that id.
      No span: the loader has not read that source's text, and minting a span for text it has
      never seen would be fabrication.
    * ``source:`` resolves to nothing → ``evidence == []`` plus the unresolvable-id disclosure
      NAMING the id, so the author can fix the typo.
    """
    for index, recognition in enumerate(recognitions):
        if not recognition.source.strip():
            missing.append(absent(f"{_RECOGNITIONS_KEY}[{index}].source"))
        elif recognition.source in known_ids:
            recognition.evidence = [Trace(source_id=recognition.source)]
        else:
            missing.append(
                _UNRESOLVABLE_SOURCE.format(
                    person=recognition.person, source=recognition.source
                )
            )


def _disclose_gaps(spec: WeeklySpec) -> list[str]:
    """Every absent/empty schema key, in SCHEMA ORDER, plus each container's per-item absences.

    ``config`` absence is NOT a gap — a weekly with no org slots is simply fully portable (the
    Case Spec precedent). Two other absences are deliberately not disclosed here:

    * ``recognitions[].source`` — owned by :func:`_resolve_recognition_evidence`, so the absent
      and the unresolvable cases sit adjacent in ``missing[]`` and read as the one rule they are.
    * the ``assets[]`` provenance fields — owned by PLACEMENT (plan 03-03), which carries the
      spec's exact per-condition wording (``provenance field {field!r} is absent — the minimum is
      folder + date + event label``). Duplicating it here would give the reviewer the same gap
      twice in two different voices.

    Everything else reuses ``specspan.absent`` verbatim so the honesty panel reads consistently
    across both spec kinds.
    """
    gaps: list[str] = []
    for key in _KNOWN_KEYS:
        if key == _CONFIG_KEY:
            continue
        value = getattr(spec, key)
        if not value:
            gaps.append(absent(key))
            continue
        if key == _RECOGNITIONS_KEY:
            for index, recognition in enumerate(value):
                for field in ("person", "reason"):
                    if not getattr(recognition, field).strip():
                        gaps.append(absent(f"{key}[{index}].{field}"))
        elif key == _TEAM_KEY:
            for index, member in enumerate(value):
                for field in _MEMBER_FIELDS:
                    carried = getattr(member, field)
                    if not (carried.strip() if isinstance(carried, str) else carried):
                        gaps.append(absent(f"{key}[{index}].{field}"))
    return gaps


def load_weekly_spec(
    path: Union[str, Path],
    *,
    root: Optional[Path] = None,
    known_sources: Sequence[Source] = (),
) -> WeeklySpecLoad:
    """Load one hand-authored Weekly Spec YAML file into ``Source`` + spec + ``Distillation``.

    Read-only, deterministic, AI-free. Edge policy mirrors ``casespec.load_case_spec`` exactly:
    the path resolves under ``root`` (default ``Path.cwd()``; escaping it raises ``ValueError`` —
    a REFUSAL, never a ``missing[]`` entry, per ``docs/weekly-spec.md`` rule 7), a missing file
    raises ``FileNotFoundError``, non-UTF-8 raises ``UnicodeDecodeError``. ``Source.transcript``
    is the newline-normalized file text (``read_text(encoding="utf-8")`` folds CRLF to LF;
    otherwise unaltered — and every span, offset and hash addresses that same normalized text);
    ``Source.timestamp`` is ``EPOCH_ZERO``. Schema violations raise teaching ``ValueError``s (see
    :func:`_validate`); everything absent, empty or unlocatable lands in
    ``Distillation.missing[]``. Every emitted claim passes the LIVE span-containment gate —
    enforced here by construction (a violation raises ``RuntimeError``).

    ``known_sources`` are the ``Source``s a recognition's ``source:`` id may resolve against, in
    addition to the spec file's own. An id that resolves to none of them is disclosed by name and
    never becomes a ``Trace``.

    THIS FUNCTION DOES NO PLACEMENT. It touches no file but the spec itself: no asset is hashed,
    no image is opened, no ``AssetBlock`` is minted. The ``assets:`` records are carried verbatim
    as ``AuthoredAsset``s and their provenance routing is plan 03-03's — the load/place seam.
    """
    root_path = (root or Path.cwd()).resolve()
    candidate = Path(path)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(root_path).as_posix()  # ValueError if it escapes root
    transcript = resolved.read_text(encoding="utf-8")  # READ ONLY

    source = Source(
        id=rel,
        context=f"weekly-spec:{rel}",
        transcript=transcript,
        timestamp=EPOCH_ZERO,
    )
    parsed = _validate(_parse_config(transcript))

    minter = SpanMinter(source)
    claims: list[Claim] = []
    missing: list[str] = []

    def _route(
        key: str, value: Optional[str], topic: str, *, list_item: bool = False
    ) -> Optional[str]:
        """Mint one non-empty value; return it for the spec (empty → None, disclosed later)."""
        if value is None or not value.strip():
            return None
        minted = minter.mint(key, value, topic, list_item=list_item)
        if isinstance(minted, Claim):
            claims.append(minted)
        else:
            missing.append(minted)
        return value

    spec_kwargs: dict[str, Any] = {}
    # FILE ORDER — the correctness condition, not a style preference. Every nested collection is
    # iterated via its OWN .items() rather than against a hardcoded field list, because the
    # author's field order IS the file's order and the cursor is forward-only.
    for key, value in parsed.items():
        if key == _CONFIG_KEY:
            spec_kwargs[_CONFIG_KEY] = dict(value or {})  # carried; NEVER minted
        elif key in _STR_KEYS:
            kept = _route(key, value, key)
            if kept is not None:
                spec_kwargs[key] = kept
        elif key in _NARRATIVE_KEYS and value is not None:
            spec_kwargs[key] = [
                item
                for item in value
                if _route(key, item, key, list_item=True) is not None
            ]
        elif key == _RECOGNITIONS_KEY and value is not None:
            recognitions: list[AuthoredRecognition] = []
            for item in value:
                fields: dict[str, str] = {}
                for field, field_value in item.items():  # file order within the mapping
                    kept = _route(field, field_value, f"{key}.{field}")
                    fields[field] = kept if kept is not None else ""
                recognitions.append(AuthoredRecognition(**fields))
            spec_kwargs[key] = recognitions
        elif key == _TEAM_KEY and value is not None:
            members: list[AuthoredMember] = []
            for item in value:
                fields = {}
                lines: list[str] = []
                for field, field_value in item.items():  # file order within the mapping
                    if field == "lines":
                        lines = [
                            line
                            for line in (field_value or [])
                            if _route(field, line, f"{key}.{field}", list_item=True)
                            is not None
                        ]
                        continue
                    kept = _route(field, field_value, f"{key}.{field}")
                    fields[field] = kept if kept is not None else ""
                members.append(AuthoredMember(lines=lines, **fields))
            spec_kwargs[key] = members
        elif key == _ASSETS_KEY and value is not None:
            assets: list[AuthoredAsset] = []
            for asset_key, record in value.items():  # file order within the mapping
                # The mapping KEY is the spec-local handle, not an authored narrative value, so
                # it is carried on the record rather than minted as a claim. Every record SCALAR
                # is routed — including the `sha256` hex, which is a literal substring of the
                # file and therefore traces verbatim like any other field.
                fields = {}
                for field, field_value in record.items():
                    kept = _route(field, field_value, f"{key}.{field}")
                    fields[field] = kept if kept is not None else ""
                assets.append(AuthoredAsset(key=asset_key, **fields))
            spec_kwargs[key] = assets

    spec = WeeklySpec(**spec_kwargs)

    # SECOND PASS over already-minted data — references only, never the minter.
    known_ids = {source.id} | {known.id for known in known_sources}
    _resolve_recognition_evidence(spec.recognitions, known_ids, missing)
    missing.extend(_disclose_gaps(spec))

    # Enforced by construction: every emitted claim satisfies the LIVE gate.
    for claim in claims:
        if not GATE.entails(claim):
            raise RuntimeError(
                f"weekly-spec faithfulness violated: claim {claim.text!r} does not pass "
                "span-containment against its own trace — refusing to emit it."
            )

    distillation = Distillation(
        narrative=(
            f"Weekly Spec {rel!r}: {len(claims)} claim(s) traced to spans of the authored "
            f"file; {len(missing)} gap(s) disclosed in missing[]."
        ),
        claims=claims,
        missing=missing,
        traces=[source],
    )
    return WeeklySpecLoad(source=source, spec=spec, distillation=distillation)
