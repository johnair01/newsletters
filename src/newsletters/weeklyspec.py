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

* AN ASSET IS PLACED ONLY BY ITS RECORD. An image reaches a ``Surface`` as an ``AssetBlock`` only
  when its authored record cleared folder + date + event, carried a deep link if it stands in for
  values, stayed inside the project root and still hashes to the ``sha256`` the record names. The
  image is HASHED, never decoded. Every other outcome is a named disclosure — except a path
  escaping the root, which is a REFUSAL and raises (``docs/weekly-spec.md`` §"The routing").
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from pydantic import BaseModel, Field

from ._yaml_loader import load_config as _parse_config
from .adapters._timestamps import EPOCH_ZERO

# The SHARED trust predicates and disclosure wording (WR-04, 03-review): `compose_kpi_item` is
# the ONE place the endpoint policy and its three disclosure strings live, exactly as `addressed`
# is the one traced-or-missing predicate. Re-declaring either here re-opens the two-copies drift
# this phase's own promotions (`specspan`, `addressed`) exist to prevent.
from .compose import NO_KPIS, addressed, compose_kpi_item

# The writer's reserved-prefix constant, IMPORTED rather than re-declared: `weekly_slots` builds
# the mapping `pptx_writer.bind_slots` validates, and two copies of the prefix drift exactly as
# two normalizers would. `pptx_writer`'s module level is stdlib-only (its `Surface` annotation is
# under TYPE_CHECKING and python-pptx is reached lazily inside the render function), so this edge
# adds NOTHING to the bare-install surface — see that module's AI-OPTIONAL banner.
from .pptx_writer import SLOT_PREFIX
from .semantic import (
    AssetBlock,
    AssetRecord,
    Block,
    Claim,
    ClaimsBlock,
    Distillation,
    KpiStripBlock,
    NarrativeBlock,
    NarrativeItem,
    ProseBlock,
    Recognition,
    RecognitionsBlock,
    Review,
    Source,
    Surface,
    TeamBlock,
    TeamMember,
    Trace,
)
from .site import slugify
from .specspan import GATE, SpanMinter, absent
from .swimlane import SectionBinding
from .templates import REPORT

__all__ = [
    "CONNECTIVE_CONSTANTS",
    "AuthoredAsset",
    "AuthoredMember",
    "AuthoredRecognition",
    "WeeklySpec",
    "WeeklySpecLoad",
    "build_weekly_report",
    "load_weekly_spec",
    "weekly_slots",
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
# The provenance minimum (decision D-02) — checked at placement in THIS field order, so the
# field a disclosure names is deterministic rather than dependent on dict iteration.
_PROVENANCE_MINIMUMS = ("folder", "date", "event")
# The ONE declared ``stands_in_for`` kind (``semantic.AssetRecord`` types it as
# ``Literal["values"]``). Author-declared, never inferred from a filename, a folder or the image.
_VALUES_STAND_IN = "values"

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

# ---------------------------------------------------------------------------- #
# The asset routing table (``docs/weekly-spec.md`` §"The routing"), verbatim.
#
# Four of its seven rows are disclosures and live here as constants so the wording the reviewer
# reads has exactly one source. The fifth row (the happy one) mints an ``AssetBlock``; the sixth
# is the ``team[].photo`` reference below; the seventh (an unresolvable recognition ``source:``)
# is ``_UNRESOLVABLE_SOURCE`` above. The escape row is NOT here: it is a refusal, and a refusal
# is raised, never disclosed.
# ---------------------------------------------------------------------------- #
_ASSET_PROVENANCE_ABSENT = (
    "asset {key!r}: provenance field {field!r} is absent — the minimum is folder + date "
    "+ event label; disclosed, never placed"
)
_ASSET_NEEDS_DEEP_LINK = (
    "asset {key!r}: a screenshot standing in for values requires a deep link to the "
    "report; disclosed, never placed"
)
_ASSET_CONTENT_ADDRESS = (
    "asset {key!r}: file {file!r} does not match its recorded content address — refusing "
    "to place a file that is not the one the record describes"
)
_PHOTO_NAMES_NO_PLACED_ASSET = (
    "team member {name!r}: photo key {key!r} names no placed asset — the member is "
    "carried, the photo is not"
)
# The ESCAPE row. A path that leaves the project root is refused in the teaching voice and
# contributes NOTHING to ``missing[]``: ``missing[]`` is for content that is absent, never for a
# request the loader will not serve (``docs/weekly-spec.md`` rule 7; threat T-03-02). Collapsing
# the two would let a future implementer "disclose" a path traversal.
_ASSET_ESCAPES_ROOT = (
    "asset {key!r}: file {file!r} resolves to {resolved!r}, which is OUTSIDE the project root "
    "{root!r} — REFUSING to read it. This is a refusal, not an absence: it is never routed to "
    "missing[], because missing[] is for content that is absent, never for a request the loader "
    "will not serve. Move the file inside the project, or fix the path."
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
    # The PLACED assets, in ``assets:`` file order — and only the placed ones. Placement happens
    # at LOAD time, not at compose time, because the content-address check needs the filesystem
    # and the composer must never read a file: an ``AssetBlock`` here is a file that was root
    # contained, provenance-complete and still hashing to what its record says. Every other
    # authored asset is a named disclosure in ``distillation.missing`` (see :func:`_place_assets`).
    assets: list[AssetBlock] = Field(default_factory=list)


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
            # ``stands_in_for`` is author-declared AND CLOSED. ``semantic.AssetRecord`` types it
            # as ``Literal["values"]``, so an unknown kind carried this far would surface at
            # PLACEMENT as a Pydantic ValidationError that names a type instead of the typo.
            # It earns the same teaching refusal every other typo gets, in the same place.
            stands_in_for = record.get("stands_in_for")
            if stands_in_for and stands_in_for != _VALUES_STAND_IN:
                raise ValueError(
                    f"{where}.stands_in_for must be {_VALUES_STAND_IN!r} — the one declared "
                    f"kind — or absent; got {stands_in_for!r}. It is AUTHOR-DECLARED and never "
                    f"inferred from a filename, a folder or the image itself. See {_SPEC_DOC}."
                )

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


def _record_evidence(record_claims: list[Claim]) -> list[Trace]:
    """The traces an ``AssetBlock`` stands on: the record's OWN provenance spans.

    The record is the evidence, never the image (``docs/weekly-spec.md`` §"Assets"): the
    ``sha256`` hex is a literal substring of the spec file, so the claim already minted for it is
    the natural trace — the block's evidence IS the provenance claim. Any other already-minted
    record claim is the fallback, so a record whose hash line could not be pinned still stands on
    a real span rather than on nothing.

    If this returns ``[]`` the caller passes it to ``AssetBlock`` anyway and Pydantic refuses the
    construction (``evidence`` carries ``min_length=1``). That is the TYPE doing its job — the
    D-02 guarantee that a picture nobody vouched for is unrepresentable — and it is deliberately
    not worked around here.
    """
    sha_topic = f"{_ASSETS_KEY}.sha256"
    for claim in record_claims:
        if claim.topics == [sha_topic]:
            return list(claim.evidence)
    return list(record_claims[0].evidence) if record_claims else []


def _place_assets(
    assets: list[AuthoredAsset],
    record_claims: dict[str, list[Claim]],
    root_path: Path,
    missing: list[str],
) -> list[AssetBlock]:
    """Route every authored asset: place it, disclose it, or REFUSE it. Document order.

    Placement happens at LOAD time because the content-address check needs the filesystem — the
    load/place seam is here, and this is the only function in the module that reads a file other
    than the spec itself.

    The order of the checks is the routing table's order and is load-bearing:

    1. **Containment first**, before any read: ``resolve()`` (which follows symlinks, so an
       in-root link pointing outside is caught by the same test) then ``relative_to(root)``. An
       escape RAISES — ``../../etc/passwd`` never reaches ``read_bytes()`` and never becomes a
       ``missing[]`` note (threats T-03-02 / T-03-03).
    2. The three provenance minimums **in field order**, so the field a disclosure names is
       deterministic. The FIRST absent one is named and the asset is dropped.
    3. The deep link, required iff the author declared ``stands_in_for: values``.
    4. Existence, then the content address: ``hashlib.sha256`` over the file BYTES, compared
       case-insensitively to the recorded hex. The image is HASHED, never DECODED: no imaging or
       image-sniffing library is imported or reached from here (threat T-03-10 — a decompression
       bomb is just bytes to a hash), and a test greps this module's source to keep it that way.
       ``read_bytes`` is guarded for ``OSError`` (a dangling path merely returns ``False`` from
       ``is_file()``, but a permission error would otherwise escape as a crash) and routes to the
       same content-address disclosure.

    The hash is re-checked at PLACEMENT, never trusted from authoring time: that is the whole
    substitution case (a record describing image A while image B sits on disk, threat T-03-05).
    """
    placed: list[AssetBlock] = []
    for asset in assets:
        candidate = Path(asset.file)
        absolute = candidate if candidate.is_absolute() else (root_path / candidate)
        resolved = absolute.resolve()  # follows symlinks BEFORE the containment test
        try:
            resolved.relative_to(root_path)
        except ValueError as exc:  # a REFUSAL — never a missing[] disclosure
            raise ValueError(
                _ASSET_ESCAPES_ROOT.format(
                    key=asset.key,
                    file=asset.file,
                    resolved=str(resolved),
                    root=str(root_path),
                )
            ) from exc

        gap = next(
            (
                field
                for field in _PROVENANCE_MINIMUMS
                if not getattr(asset, field).strip()
            ),
            None,
        )
        if gap is not None:
            missing.append(_ASSET_PROVENANCE_ABSENT.format(key=asset.key, field=gap))
            continue

        if asset.stands_in_for.strip() == _VALUES_STAND_IN and not asset.link.strip():
            missing.append(_ASSET_NEEDS_DEEP_LINK.format(key=asset.key))
            continue

        try:
            digest = (
                hashlib.sha256(resolved.read_bytes()).hexdigest()
                if resolved.is_file()
                else None
            )
        except OSError:  # unreadable is indistinguishable from unvouched-for: do not place
            digest = None
        if digest is None or digest.lower() != asset.sha256.strip().lower():
            missing.append(
                _ASSET_CONTENT_ADDRESS.format(key=asset.key, file=asset.file)
            )
            continue

        record = AssetRecord(
            key=asset.key,
            file=asset.file,
            sha256=asset.sha256,
            folder=asset.folder,
            date=asset.date,
            event=asset.event,
            link=asset.link or None,
            stands_in_for=asset.stands_in_for or None,
            caption=asset.caption or None,
            alt=asset.alt or None,
        )
        placed.append(
            AssetBlock(
                heading=asset.alt or None,
                asset=record,
                caption=asset.caption or None,
                evidence=_record_evidence(record_claims.get(asset.key, [])),
            )
        )
    return placed


def _resolve_team_photos(
    members: list[AuthoredMember], placed_keys: set[str], missing: list[str]
) -> None:
    """Second pass: a ``photo:`` key that names no PLACED asset is disclosed, never guessed.

    Runs after routing, because "was this asset placed?" is only answerable once every asset has
    been routed — and it never re-enters the span minter (file order stays intact by
    construction). The member and their lines are carried in every case: unlike a mistyped
    top-level key, nothing authored is at risk of being dropped, and inventing or guessing an
    image would be worse than disclosing its absence. The authored key stays on the spec
    verbatim; it is the COMPOSER that renders ``photo=None`` for an unplaced key.
    """
    for member in members:
        key = member.photo.strip()
        if key and key not in placed_keys:
            missing.append(
                _PHOTO_NAMES_NO_PLACED_ASSET.format(name=member.name, key=key)
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

    PLACEMENT HAPPENS HERE, and it is the ONE place this module reads a file other than the spec
    (:func:`_place_assets`). Each ``assets:`` entry is root-contained, provenance-checked,
    deep-link-checked and re-hashed against its recorded content address; a survivor becomes an
    ``AssetBlock`` on ``WeeklySpecLoad.assets`` and every other outcome is a named disclosure —
    except a path escaping ``root``, which RAISES. The image is hashed, never decoded. The
    composer (:func:`build_weekly_report`) therefore touches no filesystem at all.
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
    record_claims: dict[str, list[Claim]] = {}

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
            kept_lines: list[str] = []
            for index, item in enumerate(value):
                if _route(key, item, key, list_item=True) is not None:
                    kept_lines.append(item)
                else:
                    # WR-05 (03-review): a PRESENT-but-blank item ("" or ~) inside a non-empty
                    # list was dropped with NO disclosure — contradicting the banner's "anything
                    # absent, empty or unlocatable lands in missing[]" (rule 4). The author put
                    # a line at this position; its emptiness is disclosed, never silently eaten.
                    missing.append(absent(f"{key}[{index}]"))
            spec_kwargs[key] = kept_lines
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
            for member_index, item in enumerate(value):
                fields = {}
                lines: list[str] = []
                for field, field_value in item.items():  # file order within the mapping
                    if field == "lines":
                        for line_index, line in enumerate(field_value or []):
                            if (
                                _route(field, line, f"{key}.{field}", list_item=True)
                                is not None
                            ):
                                lines.append(line)
                            else:
                                # WR-05: a blank authored team line — same rule-4 disclosure
                                # as a blank narrative item, named by its authored position.
                                missing.append(
                                    absent(
                                        f"{key}[{member_index}].{field}[{line_index}]"
                                    )
                                )
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
                minted_before = len(claims)
                for field, field_value in record.items():
                    kept = _route(field, field_value, f"{key}.{field}")
                    fields[field] = kept if kept is not None else ""
                # Remember THIS record's own claims (by position, so a value duplicated across
                # two records still belongs to the record that minted it) — placement needs one
                # of them as the block's evidence.
                record_claims[asset_key] = claims[minted_before:]
                assets.append(AuthoredAsset(key=asset_key, **fields))
            spec_kwargs[key] = assets

    spec = WeeklySpec(**spec_kwargs)

    # SECOND PASS over already-minted data — references and placement, never the minter.
    known_ids = {source.id} | {known.id for known in known_sources}
    _resolve_recognition_evidence(spec.recognitions, known_ids, missing)
    placed = _place_assets(spec.assets, record_claims, root_path, missing)
    _resolve_team_photos(spec.team, {block.asset.key for block in placed}, missing)
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
    return WeeklySpecLoad(
        source=source, spec=spec, distillation=distillation, assets=placed
    )


# ---------------------------------------------------------------------------- #
# The composer: a loaded weekly becomes a Draft ``Surface(REPORT)``.
#
# THE CONNECTIVE CONSTANTS ARE THE ONLY TEXT THIS MODULE AUTHORS. Every other string on a
# composed surface is a substring of the author's own file. They are declared here — public, and
# collected in ``CONNECTIVE_CONSTANTS`` — so the editorialization guard has an allowlist to
# consult and a composer that starts writing prose has to change a declared constant to do it.
# Each carries NO numeral and NO fact: they name the record and label its sections, nothing more.
# ---------------------------------------------------------------------------- #
LEAD_HEADING = "The week, as authored"
LEAD_TEXT = (
    "This weekly was authored by hand and lifted into the reviewed record without "
    "interpretation: every line below is the author's own, traced to a span of the file they "
    "wrote, carried in their order and never summarised, merged or reordered. Anything the spec "
    "leaves blank — and every image whose provenance record was incomplete — is disclosed in the "
    "honesty panel rather than filled in. Org-specific slots stay in config and are never "
    "rendered as claims."
)
CLAIMS_HEADING = "Bound sections — every claim traced"
HIGHLIGHTS_HEADING = "What went well"
LOWLIGHTS_HEADING = "What did not"
RECOGNITIONS_HEADING = "Recognitions"
TEAM_HEADING = "The team"
# The eyebrow fallback, used only when the author named no module. A constant, never a join of
# the author's values: joining ``week`` and ``module`` would be composer-authored connective text
# dressed up as identity.
EYEBROW_FALLBACK = "Report · weekly"

CONNECTIVE_CONSTANTS = frozenset(
    {
        LEAD_HEADING,
        LEAD_TEXT,
        CLAIMS_HEADING,
        HIGHLIGHTS_HEADING,
        LOWLIGHTS_HEADING,
        RECOGNITIONS_HEADING,
        TEAM_HEADING,
        EYEBROW_FALLBACK,
    }
)

_NO_BINDINGS = (
    "no section bindings were supplied — no KPI strip and no claims block on this weekly"
)


class _MintedClaims:
    """Hand back the claim that was minted FOR a given authored line — once, in file order.

    A weekly may legitimately repeat a line across tones, so the lookup consumes: the first
    unused claim with the same topic and the identical text wins. Matching on text alone (or
    reusing one claim twice) would attach a rendered line to a span that belongs to a different
    occurrence — the span-swap failure, one layer up.
    """

    def __init__(self, claims: Sequence[Claim]) -> None:
        self._claims = list(claims)
        self._used: set[int] = set()

    def take(self, topic: str, text: str) -> Optional[Claim]:
        for index, claim in enumerate(self._claims):
            if index in self._used:
                continue
            if claim.topics == [topic] and claim.text == text:
                self._used.add(index)
                return claim
        return None


def build_weekly_report(
    load: WeeklySpecLoad,
    *,
    author: str,
    bindings: Sequence[SectionBinding] = (),
    surface_id: Optional[str] = None,
) -> Surface:
    """Assemble a loaded weekly into a **Draft** ``Surface(REPORT)`` at ``EPOCH_ZERO``.

    THE BLOCK ORDER IS FIXED AND ASSERTED BY TEST — it is part of the determinism claim, and a
    composer free to reorder blocks is a composer forming an opinion about what mattered this
    week::

        ProseBlock (the declared connective lead)
        KpiStripBlock*      (one per binding that declares KPIs, in binding order)
        ClaimsBlock         (every content-addressed binding claim, in binding order)
        NarrativeBlock      (highlights, in file order)
        NarrativeBlock      (lowlights, in file order)
        RecognitionsBlock
        TeamBlock
        AssetBlock*         (the PLACED assets, in ``assets:`` file order)

    An empty section produces NO block: a weekly with no lowlights gets no lowlight block, and
    the absence is already in ``missing[]`` where the reviewer sees it. An empty block would
    render an empty ``div.block`` and assert nothing.

    FAITHFUL, NOT SUGGESTIVE. Authored lines are carried byte-verbatim, one ``NarrativeItem`` per
    line, in the author's order, each beside the ``Claim`` minted for that same occurrence. The
    only text this function authors is the declared connective constants above.

    IDENTITY IS THE AUTHOR'S, NEVER A JOIN. ``title`` is ``week`` and ``eyebrow`` is ``module``,
    each carried whole; when one is absent the loader has already disclosed it and the fallback
    is the file stem (title) or a declared constant (eyebrow) — never the other value borrowed.

    THE GATE IS NOT TOUCHED. This function never calls ``approve()``, ``open_pull_request()`` or
    ``publish()``; it returns ``Draft`` and the recorded human review is the only way out
    (CLAIMS.md's first hard rule; threat T-03-09, asserted by a source grep in the test suite).

    ``bindings`` is the adapter seam (``swimlane.SectionBinding``): its KPIs become strips and its
    claims are filtered through the SHARED ``compose.addressed`` trust predicate — a claim that is
    untraced or whose trace is not content-addressed never reaches a block; its text is disclosed.
    """
    spec = load.spec
    missing: list[str] = list(load.distillation.missing)
    minted = _MintedClaims(load.distillation.claims)

    # Pitfall 8: ``Surface.model_config`` sets ``validate_assignment=True``. Build the whole list
    # first and pass it to the constructor; never mutate ``surface.blocks`` afterwards.
    blocks: list[Block] = [ProseBlock(heading=LEAD_HEADING, text=LEAD_TEXT)]

    strips: list[Block] = []
    kept_claims: list[Claim] = []
    for binding in bindings:  # BINDING ORDER — never a set, never a sort
        if binding.kpi_items:
            items = [
                compose_kpi_item(
                    kpi,
                    (
                        binding.kpi_endpoints[index]
                        if index < len(binding.kpi_endpoints)
                        else []
                    ),
                    missing,
                )
                for index, kpi in enumerate(binding.kpi_items)
            ]
            strips.append(KpiStripBlock(heading=binding.heading, items=items))
        else:
            missing.append(NO_KPIS.format(heading=binding.heading))
        for claim in binding.claims:  # traced-or-missing, via the SHARED predicate
            if addressed(claim):
                kept_claims.append(claim)
            else:
                missing.append(claim.text)
        missing.extend(binding.missing)
    if not bindings:
        missing.append(_NO_BINDINGS)
    blocks.extend(strips)
    if kept_claims:
        blocks.append(ClaimsBlock(heading=CLAIMS_HEADING, claims=kept_claims))

    for key, tone, heading in (
        (_HIGHLIGHTS_KEY, "highlight", HIGHLIGHTS_HEADING),
        (_LOWLIGHTS_KEY, "lowlight", LOWLIGHTS_HEADING),
    ):
        lines = getattr(spec, key)
        if not lines:
            continue  # the absence is already disclosed; an empty block asserts nothing
        blocks.append(
            NarrativeBlock(
                heading=heading,
                tone=tone,
                items=[
                    NarrativeItem(text=line, claim=minted.take(key, line))
                    for line in lines
                ],
            )
        )

    if spec.recognitions:
        blocks.append(
            RecognitionsBlock(
                heading=RECOGNITIONS_HEADING,
                recognitions=[
                    Recognition(
                        person=recognition.person,
                        reason=recognition.reason,
                        evidence=list(recognition.evidence),
                    )
                    for recognition in spec.recognitions
                ],
            )
        )

    placed_keys = {block.asset.key for block in load.assets}
    if spec.team:
        blocks.append(
            TeamBlock(
                heading=TEAM_HEADING,
                members=[
                    TeamMember(
                        name=member.name,
                        role=member.role,
                        lines=list(member.lines),
                        # A photo key that names no PLACED asset renders as no photo. The
                        # disclosure was written at load time; guessing an image would be worse
                        # than showing the reviewer that one is missing.
                        photo=(
                            member.photo if member.photo in placed_keys else None
                        ),
                    )
                    for member in spec.team
                ],
            )
        )

    blocks.extend(load.assets)  # already in ``assets:`` file order, already provenance-checked

    stem = Path(load.source.id).stem
    return Surface(
        id=surface_id or f"weekly-{slugify(stem).removeprefix('weekly-') or 'spec'}",
        template=REPORT,
        title=spec.week or stem.replace("-", " ").title(),
        eyebrow=spec.module or EYEBROW_FALLBACK,
        blocks=blocks,
        traces=[load.source],
        missing=missing,
        byline=[author],
        review=Review(policy=REPORT.review_policy, author=author),
        created=EPOCH_ZERO,
    )


# ---------------------------------------------------------------------------- #
# The deck slots: the Surface -> ``NL_`` derivation Phase 2 deliberately left open (D-03/P-03).
#
# The four names below are the ones the committed synthetic template declares. They are built from
# the WRITER's own ``SLOT_PREFIX`` rather than typed out, because the prefix is the contract
# ``bind_slots`` enforces in both directions (an unprefixed key is refused; an unfilled prefixed
# shape is refused) and a second spelling of it would drift.
# ---------------------------------------------------------------------------- #
WEEK_TITLE_SLOT = f"{SLOT_PREFIX}WEEK_TITLE"
MODULE_SLOT = f"{SLOT_PREFIX}MODULE"
HIGHLIGHTS_SLOT = f"{SLOT_PREFIX}HIGHLIGHTS"
LOWLIGHTS_SLOT = f"{SLOT_PREFIX}LOWLIGHTS"

# (slot name, authored key) in the FIXED emission order. Insertion order is the dict's order and
# is asserted by test: a composer free to reorder its slots is a composer forming an opinion.
_SLOT_SOURCES = (
    (WEEK_TITLE_SLOT, _WEEK_KEY),
    (MODULE_SLOT, _MODULE_KEY),
    (HIGHLIGHTS_SLOT, _HIGHLIGHTS_KEY),
    (LOWLIGHTS_SLOT, _LOWLIGHTS_KEY),
)

_INVENTED_SLOT_LINE = (
    "refusing to emit {line!r} into slot {slot!r}: section {key!r} is empty, so the ONLY line this "
    "composer may put on that slide is the surface's own disclosure of the absence — and that "
    "string is not in ``surface.missing``. A line that is neither the author's words nor the "
    "recorded disclosure is composer-invented content on an artifact a human will send. Compose "
    "the slots from the SAME load the surface was built from, or fix the loader so the absence is "
    "disclosed (docs/weekly-spec.md rule 4)."
)


def weekly_slots(load: WeeklySpecLoad, surface: Surface) -> dict[str, list[str]]:
    """Derive the ``NL_`` slot mapping :func:`pptx_writer.render_surface_pptx` requires.

    Pure and ordered: no filesystem, no clock, no gate call. Two calls on the same inputs return
    equal dicts with equal key order, which is half of why two renders of one reviewed record are
    the same deck.

    THE SHAPE. Exactly the four keys the committed template declares, in a fixed insertion order,
    every value an explicit ``list[str]`` — never a bare ``str``, which is itself a
    ``Sequence[str]`` of its characters and would ship one paragraph per letter (02-review WR-03;
    ``fill_slot`` now treats a bare string as one line, but building the right type here is the
    caller-side half of that fix).

    THE CONTENT. Every emitted line is either the author's own value, carried verbatim and in file
    order (one line per authored item — never joined, never sorted, never summarised), or the
    surface's own ``missing[]`` disclosure of that section's absence. There is no third source of
    text, and the disclosure branch PROVES it belongs to the second by checking membership in
    ``surface.missing`` before emitting and raising a teaching ``ValueError`` otherwise.

    WHY AN EMPTY SECTION STILL GETS A LINE — this SUPERSEDES the "omit empty slots" instinct
    (03-RESEARCH) for any slot the template DECLARES, and the reason is mechanical as well as
    editorial. Mechanically: ``bind_slots`` refuses an ``NL_``-prefixed shape with no matching
    content, so omitting ``NL_LOWLIGHTS`` would make a weekly with no lowlights fail to render at
    all. Editorially: "no lowlights" is the absence a weekly is most tempted to hide
    (``docs/weekly-spec.md`` rule 4), so the reviewer's slide is exactly where it belongs. Padding
    it with invented prose ("Nothing to report", an em dash) would be the composer editorializing
    on the most consequential line in the deck; the honest line already exists in ``missing[]``,
    so the slide carries THAT.

    Blank lines are impossible by construction rather than by filtering here: the loader drops
    blank list items — DISCLOSING each by its authored position in ``missing[]`` (rule 4;
    03-review WR-05) — and leaves a blank scalar empty, so an authored section is either
    non-empty real text or falsy and disclosed. Nothing authored is ever dropped in this
    function, and nothing dropped upstream went undisclosed.

    Args:
        load: the loaded weekly — the authored side, in file order.
        surface: the composed Draft ``Surface`` whose ``missing[]`` carries the disclosures. It is
            READ, never mutated: this function assigns to no ``Surface`` field and never touches
            the review gate.

    Raises:
        ValueError: if a disclosure line is not present in ``surface.missing`` — see above.
    """
    spec = load.spec
    disclosed = set(surface.missing)

    slots: dict[str, list[str]] = {}
    for slot, key in _SLOT_SOURCES:
        authored = getattr(spec, key)
        lines = [authored] if isinstance(authored, str) else list(authored)
        if any(line.strip() for line in lines):
            slots[slot] = lines
            continue
        disclosure = absent(key)
        if disclosure not in disclosed:
            raise ValueError(
                _INVENTED_SLOT_LINE.format(line=disclosure, slot=slot, key=key)
            )
        slots[slot] = [disclosure]
    return slots
