"""The Case Spec authoring path — a hand-authored YAML spec becomes a Draft Report.

An engineer writes a **Case Spec** (see ``docs/case-spec.md``) as YAML in a PR: the
work-content burden as a human problem (``problem``), how it is done today
(``current_state``), what better looks like (``imagined_state``), the design pattern
(``design``: inputs / reasoning / outputs / reusable_record), the author's thinking in
their own voice (``reasoning``), what travels (``portable``), and the org-specific slots
(``config``). This module lifts that file through the existing zero-AI spine:
content-addressed ``Source`` → span-traced ``Claim``s → ``Distillation`` → a **Draft**
``Surface(REPORT)``. No new spine concept; the review gate is untouched.

WHY the direct-builder path (sibling of ``swimlane.py``/``compose.py``, NOT
``capture.build_report``): capture mints bare-locator, un-addressed traces (no span, no
content hash), so span-containment faithfulness would pass only via the structural
fallback. Here every claim is minted via ``Trace.from_source`` — the sole pinning
constructor — so the strict half of ``SpanContainmentFaithfulness`` has teeth on every
emitted claim, enforced at load time (a claim the live gate rejects is routed to
``missing[]``, never emitted).

The contract (mirrors ``swimlane.py``):

* READ-ONLY / DETERMINISTIC. The only filesystem op is ``Path.read_text``; parsing is
  ``yaml.safe_load`` via the lazy ``[config]`` boundary (``_yaml_loader`` — no top-level
  ``import yaml`` anywhere here). ``Source.timestamp`` is ``EPOCH_ZERO``; fields are
  walked in FILE ORDER; two loads are byte-identical.
* FAITHFUL, NOT SUGGESTIVE. A field's value is located VERBATIM in the raw file text
  (forward-only cursor); a multi-line block scalar — whose logical value is not a verbatim
  substring — is traced to the field's RAW BLOCK REGION and kept only if the live
  span-containment gate entails it. Anything absent, empty, or unlocatable is disclosed in
  ``Distillation.missing[]`` — never fabricated, never silently dropped.
* REASONING IS FIRST-CLASS. The author's ``reasoning`` survives VERBATIM into the surface
  as a ``QuoteBlock`` — never summarized, never dropped.
* CONFIG IS NEVER A CLAIM. The ``config:`` subtree (system names, metrics — org
  specifics) is carried on ``CaseSpec.config`` for downstream binding but no config value
  is ever minted into a claim or rendered into a block. Specifics stay config
  (the abstraction guard's principle, applied to content).
* NO AUTO-PUBLISH. ``build_case_report`` ships ``Draft`` with the REPORT template's
  review policy; publishing still requires the recorded approval the gate demands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from ._yaml_loader import load_config as _parse_config
from .adapters._timestamps import EPOCH_ZERO
from .distill.faithfulness import SpanContainmentFaithfulness
from .semantic import (
    Claim,
    ClaimsBlock,
    Distillation,
    ProseBlock,
    QuoteBlock,
    Review,
    Source,
    Surface,
    Trace,
)
from .site import slugify
from .templates import REPORT

__all__ = ["CaseSpec", "CaseSpecLoad", "load_case_spec", "build_case_report"]

# The schema — GENERIC field names only (never an org/fixture value; LANE-03 discipline).
_CASE_KEY = "case"
_PROBLEM_KEY = "problem"
_CURRENT_KEY = "current_state"
_IMAGINED_KEY = "imagined_state"
_DESIGN_KEY = "design"
_REASONING_KEY = "reasoning"
_PORTABLE_KEY = "portable"
_CONFIG_KEY = "config"
_KNOWN_KEYS = (
    _CASE_KEY,
    _PROBLEM_KEY,
    _CURRENT_KEY,
    _IMAGINED_KEY,
    _DESIGN_KEY,
    _REASONING_KEY,
    _PORTABLE_KEY,
    _CONFIG_KEY,
)
# The single-string narrative fields (design/portable/config have their own shapes).
_STR_KEYS = (_CASE_KEY, _PROBLEM_KEY, _CURRENT_KEY, _IMAGINED_KEY, _REASONING_KEY)
# The design pattern's canonical slots: inputs → reasoning → outputs → reusable record.
_DESIGN_SLOTS = ("inputs", "reasoning", "outputs", "reusable_record")

# ONE definition of "faithful" — the live gate, reused, never reimplemented.
_GATE = SpanContainmentFaithfulness()


class CaseSpec(BaseModel):
    """The typed Case Spec — the parsed, validated authoring schema (values verbatim)."""

    case: str = ""
    problem: str = ""
    current_state: str = ""
    imagined_state: str = ""
    design: dict[str, str] = Field(default_factory=dict)
    reasoning: str = ""
    portable: list[str] = Field(default_factory=list)
    # Org-specific slots. Carried for downstream binding; NEVER rendered into claims.
    config: dict[str, Any] = Field(default_factory=dict)


class CaseSpecLoad(BaseModel):
    """One loaded Case Spec: the content-addressed ``Source``, the typed spec, the truth."""

    source: Source
    spec: CaseSpec
    distillation: Distillation


def _validate(parsed: object) -> dict[str, Any]:
    """Strict schema validation with teaching errors — a typo fails loudly, never silently."""
    if not isinstance(parsed, dict):
        raise ValueError(
            "a Case Spec must be a YAML mapping of the schema fields "
            f"{list(_KNOWN_KEYS)!r}; got {type(parsed).__name__!r}. See docs/case-spec.md."
        )
    unknown = [k for k in parsed if k not in _KNOWN_KEYS]
    if unknown:
        raise ValueError(
            f"unknown Case Spec field(s) {unknown!r} — the schema is exactly "
            f"{list(_KNOWN_KEYS)!r}. Refusing to drop authored content silently."
        )
    for key in _STR_KEYS:
        value = parsed.get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"Case Spec field {key!r} must be a string, got {type(value).__name__} "
                "— quote the value so YAML cannot type-coerce it."
            )
    design = parsed.get(_DESIGN_KEY)
    if design is not None:
        if not isinstance(design, dict):
            raise ValueError(
                f"'{_DESIGN_KEY}' must be a mapping of the pattern slots "
                f"{list(_DESIGN_SLOTS)!r}, got {type(design).__name__}."
            )
        bad_slots = [k for k in design if k not in _DESIGN_SLOTS]
        if bad_slots:
            raise ValueError(
                f"unknown design slot(s) {bad_slots!r} — the pattern is exactly "
                f"{list(_DESIGN_SLOTS)!r}."
            )
        for slot, value in design.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(
                    f"design slot {slot!r} must be a string, got {type(value).__name__}."
                )
    portable = parsed.get(_PORTABLE_KEY)
    if portable is not None and not isinstance(portable, (str, list)):
        raise ValueError(
            f"'{_PORTABLE_KEY}' must be a string or a list of strings, "
            f"got {type(portable).__name__}."
        )
    if isinstance(portable, list) and any(not isinstance(i, str) for i in portable):
        raise ValueError(f"every '{_PORTABLE_KEY}' item must be a string.")
    config = parsed.get(_CONFIG_KEY)
    if config is not None and not isinstance(config, dict):
        raise ValueError(
            f"'{_CONFIG_KEY}' must be a mapping of org-specific slots, "
            f"got {type(config).__name__}."
        )
    return parsed


class _SpanMinter:
    """Locate each authored value in the RAW file text and mint it — or disclose it.

    A forward-only cursor (the ``swimlane._Minter`` precedent) so duplicate values get
    distinct offsets. Two strategies, in order: (1) exact verbatim ``str.find`` — the span
    IS the value; (2) for a block scalar (whose folded value is not a verbatim substring),
    the field's raw BLOCK REGION located by a forward line scan — kept only if the live
    span-containment gate entails the claim against that region. A value neither strategy
    can honestly pin is returned as a disclosure string (verbatim, for ``missing[]``).
    """

    def __init__(self, source: Source) -> None:
        self._source = source
        self._raw = source.transcript
        self._cursor = 0
        self._lines = self._raw.splitlines(keepends=True)
        offsets, pos = [], 0
        for line in self._lines:
            offsets.append(pos)
            pos += len(line)
        self._line_offsets = offsets
        self._line_cursor = 0

    def mint(self, key: str, value: str, topic: str) -> Union[Claim, str]:
        idx = self._raw.find(value, self._cursor)
        if idx != -1:
            end = idx + len(value)
            claim = Claim(
                text=value,
                evidence=[Trace.from_source(self._source, idx, end)],
                topics=[topic],
            )
            self._advance(end)
            return claim
        region = self._field_region(key)
        if region is not None:
            start, end = region
            claim = Claim(
                text=value,
                evidence=[Trace.from_source(self._source, start, end)],
                topics=[topic],
            )
            if _GATE.entails(claim):
                self._advance(end)
                return claim
        return (
            f"field {topic!r} could not be located as a span of the authored file — "
            f"its text is disclosed here, never rendered as a traced claim: {value!r}"
        )

    def _advance(self, pos: int) -> None:
        """Move both cursors past ``pos`` (forward-only; duplicates stay distinct)."""
        self._cursor = max(self._cursor, pos)
        while (
            self._line_cursor + 1 < len(self._lines)
            and self._line_offsets[self._line_cursor + 1] <= self._cursor
        ):
            self._line_cursor += 1

    def _field_region(self, key: str) -> Optional[tuple[int, int]]:
        """The raw span of ``key:``'s value block: after the colon through deeper-indented lines."""
        needle = key + ":"
        for i in range(self._line_cursor, len(self._lines)):
            line = self._lines[i]
            stripped = line.lstrip()
            if not stripped.startswith(needle):
                continue
            indent = len(line) - len(stripped)
            start = self._line_offsets[i] + indent + len(needle)
            j = i + 1
            while j < len(self._lines):
                nxt = self._lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if len(nxt) - len(nxt.lstrip()) > indent:
                    j += 1
                    continue
                break
            end = self._line_offsets[j] if j < len(self._lines) else len(self._raw)
            return start, end
        return None


def _absent(field: str) -> str:
    return f"field {field!r} is absent or empty — disclosed, never fabricated"


def _disclose_gaps(parsed: dict[str, Any], spec: CaseSpec) -> list[str]:
    """Every absent/empty schema field, in schema order. ``config`` absence is not a gap
    (a spec with no org slots is simply fully portable)."""
    gaps: list[str] = []
    for key in (_CASE_KEY, _PROBLEM_KEY, _CURRENT_KEY, _IMAGINED_KEY):
        if not getattr(spec, key).strip():
            gaps.append(_absent(key))
    if parsed.get(_DESIGN_KEY) is None:
        gaps.append(_absent(_DESIGN_KEY))
    else:
        for slot in _DESIGN_SLOTS:
            if not spec.design.get(slot, "").strip():
                gaps.append(
                    f"design slot {slot!r} is absent or empty — disclosed, never fabricated"
                )
    if not spec.reasoning.strip():
        gaps.append(_absent(_REASONING_KEY))
    if not spec.portable:
        gaps.append(_absent(_PORTABLE_KEY))
    return gaps


def load_case_spec(path: Union[str, Path], *, root: Optional[Path] = None) -> CaseSpecLoad:
    """Load one hand-authored Case Spec YAML file into ``Source`` + spec + ``Distillation``.

    Read-only, deterministic, AI-free. Edge policy mirrors ``swimlane.load_swimlanes``:
    the path resolves under ``root`` (default ``Path.cwd()``; escaping it raises
    ``ValueError``), a missing file raises ``FileNotFoundError``, non-UTF-8 raises
    ``UnicodeDecodeError``. ``Source.transcript`` is the raw file text VERBATIM;
    ``Source.timestamp`` is ``EPOCH_ZERO``. Schema violations raise teaching
    ``ValueError``s (see :func:`_validate`); everything absent/empty/unlocatable lands in
    ``Distillation.missing[]``. Every emitted claim passes the LIVE span-containment gate
    — enforced here by construction (a violation raises ``RuntimeError``).
    """
    root_path = (root or Path.cwd()).resolve()
    candidate = Path(path)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(root_path).as_posix()  # ValueError if it escapes root
    transcript = resolved.read_text(encoding="utf-8")  # READ ONLY

    source = Source(
        id=rel,
        context=f"case-spec:{rel}",
        transcript=transcript,
        timestamp=EPOCH_ZERO,
    )
    parsed = _validate(_parse_config(transcript))

    minter = _SpanMinter(source)
    claims: list[Claim] = []
    missing: list[str] = []

    def _route(key: str, value: Optional[str], topic: str) -> Optional[str]:
        """Mint one non-empty value; return it for the spec (empty → None, disclosed later)."""
        if value is None or not value.strip():
            return None
        minted = minter.mint(key, value, topic)
        if isinstance(minted, Claim):
            claims.append(minted)
        else:
            missing.append(minted)
        return value

    spec_kwargs: dict[str, Any] = {}
    for key, value in parsed.items():  # FILE ORDER — determinism, forward cursor
        if key == _CONFIG_KEY:
            spec_kwargs[_CONFIG_KEY] = dict(value or {})  # carried; NEVER minted
        elif key in _STR_KEYS:
            kept = _route(key, value, key)
            if kept is not None:
                spec_kwargs[key] = kept
        elif key == _DESIGN_KEY and isinstance(value, dict):
            design: dict[str, str] = {}
            for slot, slot_value in value.items():  # file order within the mapping
                kept = _route(slot, slot_value, f"{_DESIGN_KEY}.{slot}")
                design[slot] = kept if kept is not None else ""
            spec_kwargs[_DESIGN_KEY] = design
        elif key == _PORTABLE_KEY and value is not None:
            items = [value] if isinstance(value, str) else list(value)
            kept_items = [
                item for item in items if _route(key, item, _PORTABLE_KEY) is not None
            ]
            spec_kwargs[_PORTABLE_KEY] = kept_items

    spec = CaseSpec(**spec_kwargs)
    missing.extend(_disclose_gaps(parsed, spec))

    # Enforced by construction: every emitted claim satisfies the LIVE gate.
    for claim in claims:
        if not _GATE.entails(claim):
            raise RuntimeError(
                f"case-spec faithfulness violated: claim {claim.text!r} does not pass "
                "span-containment against its own trace — refusing to emit it."
            )

    distillation = Distillation(
        narrative=(
            f"Case Spec {rel!r}: {len(claims)} claim(s) traced to spans of the authored "
            f"file; {len(missing)} gap(s) disclosed in missing[]."
        ),
        claims=claims,
        missing=missing,
        traces=[source],
    )
    return CaseSpecLoad(source=source, spec=spec, distillation=distillation)


def _stem(source_id: str) -> str:
    stem = source_id.rsplit("/", 1)[-1]
    return stem.rsplit(".", 1)[0] if "." in stem else stem


def build_case_report(
    load: CaseSpecLoad, *, author: str, surface_id: Optional[str] = None
) -> Surface:
    """Build the **Draft** ``Surface(REPORT)`` from a loaded Case Spec. No gate advance.

    The lead prose is connective only (numeral-free, no facts). The ``ClaimsBlock``
    carries every traced claim EXCEPT the reasoning claim; the author's ``reasoning`` is
    rendered VERBATIM as a ``QuoteBlock`` attributed to the author — first-class, never
    summarized. ``Distillation.missing[]`` flows to ``Surface.missing`` (the honesty
    panel). ``created=EPOCH_ZERO`` so two builds of the same load are byte-identical.
    """
    spec = load.spec
    blocks: list = [
        ProseBlock(
            heading="The case, as authored",
            text=(
                "A hand-authored case spec, lifted into the record without "
                "interpretation: every claim below traces to a span of the file the "
                "author wrote, the author's reasoning is carried in their own words, "
                "and anything the spec leaves blank is disclosed in the honesty panel "
                "— never filled in. Org-specific slots stay in config and are never "
                "rendered as claims."
            ),
        )
    ]
    body_claims = [
        c for c in load.distillation.claims if _REASONING_KEY not in c.topics
    ]
    blocks.append(
        ClaimsBlock(
            heading="The case — every claim traced to the authored file",
            claims=body_claims,
        )
    )
    if spec.reasoning:
        blocks.append(QuoteBlock(text=spec.reasoning, attr=author))

    return Surface(
        id=surface_id or f"case-{slugify(_stem(load.source.id)) or 'spec'}",
        template=REPORT,
        title=spec.case or _stem(load.source.id).replace("-", " ").title(),
        eyebrow="Report · case spec",
        blocks=blocks,
        traces=[load.source],
        missing=list(load.distillation.missing),
        byline=[author],
        review=Review(policy=REPORT.review_policy, author=author),
        created=EPOCH_ZERO,
    )
