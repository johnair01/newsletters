# Phase 3: Weekly compose - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 8 (5 new, 3 modified)
**Analogs found:** 8 / 8 (all exact or role-match — this phase invents no new mechanism)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/newsletters/weeklyspec.py` (NEW) | loader + composer | file-I/O → transform | `src/newsletters/casespec.py` | exact |
| `src/newsletters/specspan.py` (NEW, recommended) | utility (promoted mechanism) | transform | `src/newsletters/pptx_writer.py` (promotion precedent) | role-match |
| `src/newsletters/semantic.py` (MOD, pure insertion) | model | — | `GlossaryTerm`/`GlossaryBlock` @ 421-446 | exact |
| `src/newsletters/render.py` (MOD, +4 branches, fall-through) | render | transform | `_block_html` ChaptersBlock/ItemsBlock/DiagramBlock branches | exact |
| asset record loading (inside `weeklyspec.py`) | loader | file-I/O (read-only hash) | `worksurface.capture_files` @ 66-119 | role-match |
| `tests/test_weeklyspec.py` (NEW) | test | — | `tests/test_casespec.py` (8-test shape) + `tests/test_compose.py` planted guards | exact |
| WKLY-04 values-via-export test (in `test_weeklyspec.py`) | test | file-I/O | `tests/test_excel_adapter.py` in-memory workbook idiom | exact |
| `.github/workflows/ci.yml` (MOD, +job) | config | — | `pptx` job @ ci.yml:145-174 | exact |
| `weekly_slots()` (inside `weeklyspec.py`) | utility | transform | `pptx_writer.render_surface_pptx` signature @ 678-684 | role-match |

---

## Pattern Assignments

### 1. `src/newsletters/weeklyspec.py` (loader/composer, file-I/O → transform)

**Analog:** `src/newsletters/casespec.py` (read in full this session). Copy its five-part
skeleton: module docstring contract → `_KNOWN_KEYS`/`_STR_KEYS` constants → `_validate` →
`load_*` → `build_*_report`.

**Imports pattern** (`casespec.py:43-68`) — copy verbatim, adding `hashlib`:
```python
from __future__ import annotations
from pathlib import Path
from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from ._yaml_loader import load_config as _parse_config     # NO column-0 `import yaml` (Pitfall 9)
from .adapters._timestamps import EPOCH_ZERO
from .distill.faithfulness import SpanContainmentFaithfulness
from .semantic import (Block, Claim, ClaimsBlock, Distillation, ProseBlock,
                       QuoteBlock, Review, Source, Surface, Trace)
from .site import slugify
from .templates import REPORT

__all__ = ["WeeklySpec", "WeeklySpecLoad", "load_weekly_spec", "build_weekly_report", "weekly_slots"]

_GATE = SpanContainmentFaithfulness()   # ONE definition of "faithful" — casespec.py:94-95
```

**Root containment + read-only read** (`casespec.py:331-343`) — copy these 6 lines verbatim,
changing only the `context=` prefix to `weekly-spec:{rel}`:
```python
root_path = (root or Path.cwd()).resolve()
candidate = Path(path)
absolute = candidate if candidate.is_absolute() else (root_path / candidate)
resolved = absolute.resolve()
rel = resolved.relative_to(root_path).as_posix()   # ValueError if it escapes root
transcript = resolved.read_text(encoding="utf-8")  # READ ONLY
source = Source(id=rel, context=f"weekly-spec:{rel}", transcript=transcript, timestamp=EPOCH_ZERO)
parsed = _validate(_parse_config(transcript))
```

**Strict-schema teaching-error idiom** (`casespec.py:120-139`) — the exact voice to mirror for the
eight weekly keys; note it must be a SEPARATE `_validate` (widening `casespec._validate` is
forbidden by `docs/weekly-spec.md:11-17`):
```python
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
```

**The `_SpanMinter` — PROMOTE, do not fork.** Exact reusable signatures (`casespec.py:175-288`),
to move verbatim into `specspan.py` (docstrings unchanged so the diff shows nothing was tidied):
```python
class _SpanMinter:
    def __init__(self, source: Source) -> None: ...
    def mint(self, key: str, value: str, topic: str, *, list_item: bool = False) -> Union[Claim, str]: ...
    def _advance(self, pos: int) -> None: ...
    def _field_region(self, key: str) -> Optional[tuple[int, int]]: ...
    def _item_region(self) -> Optional[tuple[int, int]]: ...
```
Return contract: a `Claim` (minted, gate-entailed) or a `str` (a disclosure destined for
`missing[]`). Forward-only cursor — **walk `parsed.items()` and every nested collection in FILE
ORDER** (`casespec.py:364`), or duplicate values silently swap spans (RESEARCH Pitfall 1).

**Config binding — the exact short-circuit** (`casespec.py:365-366`):
```python
if key == _CONFIG_KEY:
    spec_kwargs[_CONFIG_KEY] = dict(value or {})  # carried; NEVER minted
```

**`_route` closure — missing[] routing** (`casespec.py:350-361`), re-implement (10 lines) closing
over the weekly's own `claims`/`missing`:
```python
def _route(key, value, topic, *, list_item=False) -> Optional[str]:
    """Mint one non-empty value; return it for the spec (empty → None, disclosed later)."""
    if value is None or not value.strip():
        return None
    minted = minter.mint(key, value, topic, list_item=list_item)
    if isinstance(minted, Claim):
        claims.append(minted)
    else:
        missing.append(minted)
    return value
```

**Absence wording** (`casespec.py:291-292`) — reuse verbatim so the honesty panel reads consistently:
```python
def _absent(field: str) -> str:
    return f"field {field!r} is absent or empty — disclosed, never fabricated"
```

**Enforced-by-construction gate sweep** (`casespec.py:390-396`) — copy; this is what makes "every
emitted claim passes the LIVE gate" a fact:
```python
for claim in claims:
    if not _GATE.entails(claim):
        raise RuntimeError(
            f"case-spec faithfulness violated: claim {claim.text!r} does not pass "
            "span-containment against its own trace — refusing to emit it."
        )
```

**Surface assembly template** (`casespec.py:427-466`) — `build_weekly_report` copies this shape:
connective numeral-free `ProseBlock` lead, blocks list built BEFORE construction (Pitfall 8:
`Surface.model_config` has `validate_assignment=True`), `missing` flowing to `Surface.missing`,
`Review(policy=REPORT.review_policy, author=author)`, `created=EPOCH_ZERO`, never advanced:
```python
return Surface(
    id=surface_id or f"case-{slug}",
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
```

**KPI-strip / claims composition** — analog `src/newsletters/compose.py:340-372`. The
traced-or-missing predicate and the per-section assembly to reuse (`compose.py:191-193`,
`340-362`):
```python
def _addressed(claim: Claim) -> bool:
    """True iff the claim is traced AND every trace is content-addressed (the trust gate)."""
    return claim.is_traced and all(trace.is_addressed for trace in claim.evidence)

# per binding, in FILE ORDER:
if binding.kpi_items:
    blocks.append(KpiStripBlock(heading=binding.heading, items=items))
else:
    missing.append(f"section {binding.heading!r} declares no KPIs — strip omitted")
kept: list[Claim] = []
for claim in binding.claims:
    if _addressed(claim):
        kept.append(claim)
    else:
        missing.append(claim.text)
blocks.append(ClaimsBlock(claims=kept))
```
`compute_delta` is public and in `__all__` (`compose.py:59,108`) — import it, never re-derive.
`compose_module_report` is a whole-Surface builder (its own id/Ledger/fanout), so the weekly
cannot call it — either extract `section_blocks(binding, missing) -> list[Block]` into
`compose.py` (not a protected file) or copy the four-line predicate above.

---

### 2. The four block-kind classes — `src/newsletters/semantic.py` (model)

**Analog:** the block sub-model + block-class + union idiom at `semantic.py:333-464`.

**Sub-model idiom** (`semantic.py:333-355`) — plain `BaseModel`, no `kind`, `Optional`/defaults:
```python
class KpiItem(BaseModel):
    label: str
    value: str
    delta: Optional[str] = None
    dir: Optional[Literal["up", "down"]] = None
```
Place `NarrativeItem`, `Recognition`, `TeamMember`, `AssetRecord` here, beside `KpiItem`/
`Chapter`/`LetterItem`/`FanoutLink` — every block sub-model in this repo lives in `semantic.py`.

**Block-class declaration idiom + discriminator literal** (`semantic.py:364-373`, `436-446`):
```python
class ClaimsBlock(BaseModel):
    kind: Literal["claims"] = "claims"
    heading: Optional[str] = "Findings — every claim traced"
    claims: list[Claim] = Field(default_factory=list)
```
Every member: `kind: Literal["<slug>"] = "<slug>"` first, then an `Optional[str]` heading with a
sentence-length default, then a `list[...] = Field(default_factory=list)` payload.

**"Unrepresentable" encoded in the type — `GlossaryTerm.definition: Claim`** (`semantic.py:421-446`)
is the precedent `AssetBlock` copies. The docstring carries the reasoning, not just the type:
```python
class GlossaryTerm(BaseModel):
    """A glossary entry: a term mapped to its DEFINING reviewed, traced ``Claim``.

    Faithfulness enforced *by the type*: ``definition`` is a ``Claim`` (carrying
    ``evidence: list[Trace]``), never a bare ``str``. ... A term with no traceable defining
    claim is NOT glossed here; the learning preset routes it to ``surface.missing[]`` ...
    """
    term: str
    definition: Claim
```
`AssetBlock` transposes this to `asset: AssetRecord` (required, no default) +
`evidence: list[Trace] = Field(..., min_length=1)` — provenance-less placement unrepresentable,
not policed. Deliberate contrast: `Recognition.evidence: list[Trace] = Field(default_factory=list)`
(empty legal by design, `docs/weekly-spec.md:193-199`).

**Union addition — PURE INSERTION** (`semantic.py:449-464`), append after `GlossaryBlock,`
(line 461); zero lines deleted:
```python
Block = Annotated[
    Union[
        ProseBlock, ClaimsBlock, KpiStripBlock, QuoteBlock, ChaptersBlock,
        ItemsBlock, PromptBlock, FanoutBlock, RationaleBlock, DiagramBlock,
        GlossaryBlock,
        NarrativeBlock, RecognitionsBlock, TeamBlock, AssetBlock,   # + 4, insertion only
    ],
    Field(discriminator="kind"),
]
```

**Count-pinning tests: THERE ARE NONE.** Re-verified this session — `grep -rn "get_args|__args__"
tests/` → zero hits. The "eleven members" phrasing lives only in prose:
`docs/architecture.md:31` and `docs/weekly-spec.md:204,211`. **Action:** update those two doc
locations to the shipped fifteen; no test count assertion needs changing.
`GlossaryBlock` is **not** re-exported from `__init__.py` — precedent says re-export is optional.

---

### 3. `render.py` — four `_block_html` branches + fail-loud fall-through (render, transform)

**Analog:** `_block_html` @ `render.py:544-620` (dispatch), `_CSS` @ `render.py:147-249`.
Only caller is `render_surface` @ `render.py:886`.

**Branch idiom** — `isinstance` test, build rows, optional heading, one f-string return; every
user-derived string through `_e()`:
```python
if isinstance(b, ChaptersBlock):                                    # render.py:585-592
    rows = "".join(
        f'<div class="chapter"><div class="t">{_e(c.time)}</div>'
        f'<div><div class="ti">{_e(c.title)}</div><div class="bo">{_e(c.body)}</div></div></div>'
        for c in b.chapters
    )
    h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
    return f'<div class="block">{h}{rows}</div>'
if isinstance(b, ItemsBlock):                                       # render.py:593-601
    rows = "".join(
        f'<div class="item">'
        + (f'<span class="sg-tag cat">{_e(i.tag)}</span>' if i.tag else "")
        + f'<div class="ti">{_e(i.title)}</div><div class="bo">{_e(i.body)}</div></div>'
        for i in b.items
    )
    h = f'<h3 class="block-h">{_e(b.heading)}</h3>' if b.heading else ""
    return f'<div class="block">{h}{rows}</div>'
if isinstance(b, RationaleBlock):                                   # render.py:613-615
    h = f'<div class="h">{_e(b.heading)}</div>' if b.heading else ""
    return f'<div class="block"><div class="rationale">{h}<div class="bo">{_e(b.text)}</div></div></div>'
if isinstance(b, DiagramBlock):                                     # render.py:616-619
    h = f'<div class="dh">{_e(b.title)}</div>' if b.title else ""
    cap = f"<figcaption>{_e(b.caption)}</figcaption>" if b.caption else ""
    return f'<div class="block"><figure class="diagram">{h}{b.svg}{cap}</figure></div>'
```
`KpiStripBlock` (`render.py:569-578`) is the strip precedent; `ClaimsBlock` (`549-552`) routes each
claim through `_claim_row(c, site, sources)` — the weekly's ClaimsBlock reuses it unchanged.

**Fall-through** — `return ""` at `render.py:620` becomes the teaching raise (RESEARCH Pattern 6).
Unreachable by construction: `Surface.blocks` is a discriminated `list[Block]`.

**Class map verified against `_CSS` — every class exists; ZERO new CSS is required:**

| Class | `_CSS` line | Class | `_CSS` line |
|---|---|---|---|
| `.block` | 201 | `.item .ti` | 232 |
| `.block-h` | 202 | `.item .bo` | 233 |
| `.sg-tag` / `.sg-tag.cat` | 147 / 148 | `.diagram` | 242 |
| `.item` | 231 | `.diagram .dh` | 244 |
| `.chapter` (grid `64px 1fr`) | 227 | `.diagram figcaption` | 245 |
| `.chapter .t` / `.ti` / `.bo` | 228 / 229 / 230 | | |

`TeamBlock` MUST mirror `ChaptersBlock`'s wrapper structure exactly (`div.t` + a wrapper `<div>`
holding `.ti`/`.bo`) because `.chapter` is a two-column grid (Pitfall 5). `AssetBlock` emits
`figure.diagram` + `div.dh` + `<figcaption>` — text only, no `<img>` this phase.
**Adding any `_CSS` rule breaks `test_publish.py::test_committed_{rev1,work}_equals_fresh_build`
(proven by experiment in research).**

---

### 4. Asset record loading (loader, read-only file-I/O + hashing)

**Analog:** `src/newsletters/worksurface.py:66-119` `capture_files` — the read-only file→`Source`
ingest with root containment. The exact loop body to mirror (`worksurface.py:100-115`):
```python
root_path = (root or Path.cwd()).resolve()
for raw in sorted(str(p) for p in paths):
    candidate = Path(raw)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(root_path).as_posix()  # raises ValueError if it escapes root
    sources.append(Source(id=rel, context=f"work-codebase:{rel}",
                          transcript=resolved.read_text(encoding="utf-8"),  # READ ONLY
                          timestamp=EPOCH_ZERO))
```
**The two deliberate divergences** for assets: (a) iterate in **file order**, not `sorted()` —
the weekly's asset order is the document's; (b) `read_bytes()` + `hashlib.sha256` instead of
`read_text` — the image is hashed, **never decoded** (no Pillow, no `imghdr`). Its docstring's
edge-case policy block (`worksurface.py:94-99`) is the model for documenting the four routing
conditions. Containment check runs **before** any filesystem call so `../../etc/passwd` never
reaches `read_bytes()`; a root escape **raises** (refusal), it does not go to `missing[]`.

---

### 5. Values-via-export test (test, file-I/O)

**Analog:** `tests/test_excel_adapter.py:1-60` — synthetic in-memory workbook, no committed binary:
```python
openpyxl = pytest.importorskip("openpyxl")  # skip cleanly without the [excel] extra

from newsletters.adapters.excel_adapter import SEP, ExcelAdapter, _cell_decision, value_to_str
from newsletters.distill import DistillationResult, assert_conforms, available, resolve

def _to_bytes(wb) -> bytes:
    """Serialize an openpyxl workbook to ``.xlsx`` bytes (so the adapter double-loads it)."""
    buf = io.BytesIO()
    wb.save(buf)
```
Note the module docstring's stated fixture policy ("tiny in-memory workbooks authored
programmatically with openpyxl and serialized via `io.BytesIO` — NOT committed fixtures") — the
weekly test follows it. **`importorskip` alone is not proof** (Pitfall 3 / RETRO W21): pair it
with the CI job in §7.
For the PNG fixture, reuse the 1×1 PNG byte literal at `tests/test_pptx_adapter.py:35-41`.

---

### 6. `tests/test_weeklyspec.py` (test)

**Analog:** `tests/test_casespec.py` — its 8-test shape ports almost name-for-name:

| `test_casespec.py` test | line | Weekly port |
|---|---|---|
| `test_schema_validation` | 79 | eight-key strict schema, unknown-key teaching error |
| `test_trace_faithfulness` | 119 | every claim gate-entailed on the STRICT branch |
| `test_portable_block_scalar_item_does_not_swallow_siblings` | 145 | block-scalar highlight + span-swap regression |
| `test_missing_honesty_for_absent_fields` | 189 | all 8 keys + per-item absences, incl. "no lowlights" |
| `test_reasoning_verbatim_into_surface` | 217 | narrative byte-verbatim into `NarrativeBlock` |
| `test_surface_is_draft_and_cannot_publish_without_gate` | 244 | copy directly |
| `test_config_never_in_claims` | 274 | copy directly (below) |
| `test_lossless_roundtrip_and_determinism` | 298 | double-load + double-compose byte-identical |

**Config-never-claimed guard, with its own non-vacuity arm** (`test_casespec.py:274-291`):
```python
leaves = _config_leaves(_parsed(FULL)["config"])
assert leaves, "fixture must declare config values for this guard to be non-vacuous"
for leaf in leaves:
    for text in claim_texts:
        assert leaf not in text, f"config value {leaf!r} leaked into claim {text!r}"
    for text in rendered:
        assert leaf not in text, f"config value {leaf!r} leaked into block {text!r}"
assert load.spec.config == _parsed(FULL)["config"]   # carried, not lost
```

**Double-load / double-compose byte-identity** (`test_casespec.py:298-320`):
```python
raw = (FIXTURE_DIR / name).read_text(encoding="utf-8")
first = _load(name); second = _load(name)
assert first.source.transcript == raw
assert first.model_dump_json() == second.model_dump_json()
dumped = first.model_dump_json()
assert CaseSpecLoad.model_validate_json(dumped).model_dump_json() == dumped
s1 = build_case_report(first, author=AUTHOR); s2 = build_case_report(second, author=AUTHOR)
assert s1.model_dump_json() == s2.model_dump_json()
assert s1.review.state is ReviewState.DRAFT
```
**Span assertion caveat:** for block scalars the span is the *item region*, not the folded value.
Assert `_normalize(text) in _normalize(span)` (the gate's own rule) plus
`transcript[start:end] == span` — never `transcript[start:end] == item.text` unconditionally.

**Planted-cheat precedent** — `tests/test_compose.py:216-235`
`test_untraced_and_unaddressed_claims_are_routed_to_missing`. This is the exact shape the
planted-editorialization guard copies (plant into a real load, re-compose, assert the planted text
is absent from the blocks AND present in `missing[]`):
```python
"""Hole B non-vacuity: a planted zero-trace AND a planted un-addressed claim go to missing[]."""
load, _ = _build_load()
untraced = Claim(text="planted untraced claim never sourced")            # zero evidence
unaddressed = Claim(text="planted claim on an un-addressed trace",
                    evidence=[Trace(source_id=load.source.id)])          # is_addressed False
load.bindings[0].claims.extend([untraced, unaddressed])
surface = _compose(load)
kept = {claim.text for claim in _claimsblock_claims(surface)}
assert untraced.text not in kept, "an untraced claim leaked onto a ClaimsBlock"
assert unaddressed.text not in kept, "an un-addressed claim leaked onto a ClaimsBlock"
assert untraced.text in surface.missing
```

**The gate-freeze test to REPLACE** — `tests/test_compose.py:534-556`. Note its list and message
voice, and that `git diff HEAD` makes it working-tree-only (vacuous in CI):
```python
gate_files = ["src/newsletters/distill/faithfulness.py", "src/newsletters/distill/coverage.py",
              "src/newsletters/semantic.py", "src/newsletters/templates.py", "src/newsletters/site.py"]
result = subprocess.run(["git", "diff", "HEAD", "--exit-code", "--", *gate_files],
                        cwd=repo_root, capture_output=True, text=True)
assert result.returncode == 0, (
    "a forbidden gate file was modified — a RED guard is fixed in the composer, "
    f"never by relaxing a gate:\n{result.stdout}")
```
Replacement (RESEARCH Pattern 2): `inspect.getsource` sha256 pins over the eight gate functions
(`Review.satisfied` 271-277, `Review._published_requires_satisfied_policy` 279-287,
`Surface._published_claims` 545-550, `Surface.open_pull_request` 552-564, `Surface.approve` 566-573,
`Surface.publish` 575-588, `Trace.from_source` 126-170, `Source.content_hash` 71-83) + a
zero-deleted-lines diff-shape assertion against `git merge-base HEAD origin/main`, not `HEAD`.

---

### 7. CI extension — `.github/workflows/ci.yml`

**Analog:** the `pptx` job @ `ci.yml:145-174` (the Phase-2 W21 precedent). Copy the whole shape
including the WHY comment — a separate job, never widening `bare-install` (PKG-03):
```yaml
  pptx:
    # WKLY-01 (v1.3, W21): the job that makes a pptx green MEAN something. Until this existed, NO
    # CI job installed the `[pptx]` extra, so all four pptx test modules `importorskip`-skipped
    # themselves on every run — a CI log with `s` where a `.` was expected, and a "green" that
    # meant "not run".
    #
    # Why a SEPARATE job rather than adding the extra above (the merge-block precedent): `[pptx]`
    # is a non-AI optional extra whose python-pptx never imports at module top level, so the
    # AI-optional property is untouched — and the `bare-install` job remains the canonical AI-free,
    # extra-free source of truth (PKG-03) and deliberately does NOT get this.
    name: pptx renderer + adapter (WKLY-01)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install with test + pptx extras (python-pptx — non-AI, lazy-imported)
        run: |
          python -m pip install --upgrade pip
          pip install ".[test,pptx]"
      - name: Run the renderer, determinism, golden, adapter and loader tests
        run: |
          python -m pytest tests/test_pptx_writer.py tests/test_pptx_determinism.py \
                           tests/test_pptx_golden.py tests/test_pptx_adapter.py \
                           tests/test_pptx_loader.py -q
```
Weekly job: `pip install ".[test,config,excel,pptx]"`, run
`tests/test_weeklyspec.py tests/test_casespec.py tests/test_compose.py tests/test_excel_adapter.py`,
and assert **0 skipped** (the header comment block at `ci.yml:15-20` also gets a one-line entry —
that per-job index is part of the file's convention).

---

### 8. Slots derivation — `weekly_slots()` (utility, transform)

**Analog:** `src/newsletters/pptx_writer.py:613-624` / `678-694` — the public API the composer feeds.
```python
def render_surface_pptx_bytes(surface, *, template: Union[str, Path],
                              slots: Mapping[str, Union[str, Sequence[str]]]) -> bytes: ...
def render_surface_pptx(surface, *, template, slots, out_path: Union[str, Path]) -> Path: ...
```
The docstring names Phase 3's obligation explicitly (`pptx_writer.py:622-624`):
> "The Surface→`slots` derivation belongs to the composer (Phase 3): only it knows which authored
> block belongs in which Selection-Pane name, so `slots` is a required keyword argument here (P-03)."

Contract the composer's pure function must satisfy: `NL_`-prefixed keys only
(`pptx_writer.py:441-448` refuses others); values are explicit `list[str]` (Pitfall 6 — a bare
`str` is a `Sequence[str]` of characters); **omit empty slots, never pad** (`fill_slot` raises on
`[]`/all-blank, `pptx_writer.py:538-544`); build the dict by iterating `surface.blocks` in order.
Images cannot reach the deck — there is no `add_picture` path in the writer (verified).
Cross-environment determinism claims use `part_digest` (`pptx_writer.py:85-92`), not raw bytes.

---

## Shared Patterns

### Determinism
**Source:** `adapters._timestamps.EPOCH_ZERO`, used at `casespec.py:342,466` and
`worksurface.py:113`.
**Apply to:** every `Source` and every `Surface` this phase constructs. One epoch sentinel; a
second one drifts.

### Root containment (V5 path-traversal bound)
**Source:** `casespec.py:335` / `worksurface.py:107` — identical idiom, identical comment.
```python
rel = resolved.relative_to(root_path).as_posix()  # raises ValueError if it escapes root
```
**Apply to:** the spec path AND every `assets[].file` path, before any filesystem call.
`Path.resolve()` follows symlinks first, so the resolved *target* is what is tested — assert that.

### The live faithfulness gate
**Source:** `casespec.py:94-95` + the sweep at `390-396`.
**Apply to:** every claim `weeklyspec.py` emits. Never re-implement "is this faithful".

### HTML escaping
**Source:** `render._e` — used in every one of the 14 existing `_block_html` branches.
**Apply to:** every user-derived interpolation in the four new branches. `DiagramBlock`'s raw
`{b.svg}` is the sole unescaped interpolation and is NOT a precedent for `AssetBlock`.

### Lazy optional-extra boundary
**Source:** `casespec.py:50` (`from ._yaml_loader import load_config as _parse_config`) and
`pptx_writer.py:638` (function-local `from .adapters._pptx_loader import _load_pptx`).
**Apply to:** `weeklyspec.py` — no column-0 `import yaml` / `openpyxl` / `pptx`, policed by
`tests/test_ai_optional.py` and `lint-imports`.

### Abstraction guard
**Source:** `tests/test_abstraction_guard.py` (walks every `*.py` under `src/newsletters/`);
`casespec.py:70` records the discipline inline ("GENERIC field names only — never an org/fixture
value; LANE-03 discipline").
**Apply to:** `weeklyspec.py` — no fixture key may appear in it. Add the weekly fixture's
identifiers to the guard's denylist beside `_CASESPEC_CONFIG_VALUES`.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| — | — | — | None. Every file this phase touches has a live in-repo analog; the phase's real work is schema, routing and disclosure, not mechanism. |

The only *capability* with no precedent is image placement into `.pptx` (`add_picture`) — verified
absent from `pptx_writer.py` and, per RESEARCH Open Question 1, out of scope this phase.

## Metadata

**Analog search scope:** `src/newsletters/` (casespec, semantic, compose, render, worksurface,
pptx_writer, swimlane), `tests/`, `.github/workflows/`
**Files scanned:** 11 read (targeted, non-overlapping ranges); 5 verification greps
**Pattern extraction date:** 2026-08-29
