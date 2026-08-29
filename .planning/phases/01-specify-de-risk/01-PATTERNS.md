# Phase 1: Specify + de-risk - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 8 (new/modified)
**Analogs found:** 7 / 8

Phase 1 ships **spec text + a recorded decision with committed evidence** (no production
renderer/composer code). So most "files to create" are documents, one decision note, and a
spike that lands as a test fixture. The analogs below are all live on this branch.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/weekly-spec.md` (NEW) | doc — authored-schema spec | file-I/O (authored YAML → spine) | `docs/case-spec.md` | exact |
| `docs/architecture.md` (MODIFY §1, line 186-187) | doc — typed-model reference | — | itself (lines 178-197) | exact (in-file) |
| `docs/case-spec.md` (MODIFY — one-line pointer) | doc | — | itself | exact |
| `.planning/notes/2026-08-29-pptx-determinism-decision.md` (NEW) | decision record + evidence | — | `.planning/notes/a2-problem-lifecycle-decision.md` (shape) + `2026-07-09-casespec-implementation-notes.md` (voice) | exact |
| `tests/test_pptx_determinism.py` (NEW) | test — spike as durable fixture | batch / file-I/O | `tests/test_pptx_golden.py` | exact |
| `tests/fixtures/weekly/_author_template.py` (NEW) | test fixture generator | file-I/O | `tests/fixtures/pptx/_author_fixtures.py` | exact |
| `tests/fixtures/weekly/template.pptx` (NEW, generated) | binary fixture | — | `tests/fixtures/pptx/*.pptx` | exact |
| committed determinism evidence artifact (JSON) | evidence record | — | **none** | no analog |

Spec text *about* future code (the 4 block kinds, the Weekly Spec loader) must name real
classes/fields in the house style — the pattern sources for that prose are
`src/newsletters/semantic.py` (the `Block` union) and `src/newsletters/render.py` (dispatch).

---

## Pattern Assignments

### `docs/weekly-spec.md` (doc, authored-schema spec)

**Analog:** `docs/case-spec.md` (70 lines — the whole document is the template)

**Document skeleton to copy** (`docs/case-spec.md` lines 1-16, 38, 47-49, 60, 68-70):

```markdown
# Case Spec — hand-authored YAML into the reviewed record

How an engineer puts a **case** ... into the record by hand, in a PR, with zero AI. The spec
file is the source; the package lifts it through the existing spine
(`Source → Claim(+Trace) → Distillation → Surface`) into a **Draft Report** that moves through
the same review gate as everything else.

---

## Writing one

Author a YAML file (data, not code — parsed with `safe_load` only) and open a PR:

```yaml
...annotated schema, every key with an inline `<what goes here>` comment...
```

Rules the loader enforces (teaching errors, never silent drops):
- ...

## What happens to it
`newsletters.<mod>.load_*(path)` reads the file as **newline-normalized text** ...
```

Four structural moves this doc must copy verbatim in kind:

1. **Annotated YAML block as the schema** (lines 18-36) — inline `# comment` per key carrying
   the rule (`# NEVER rendered into claims — specifics stay config.`). This is what makes the
   doc hand-authorable from alone (SC-1).
2. **"Rules the loader enforces (teaching errors, never silent drops)"** (lines 38-45) — a
   4-bullet list: exact-key mapping / quote coercible scalars / sub-shape rules / absence is
   disclosed in `missing[]`, never fabricated. Weekly adds byte-verbatim narrative +
   `stands_in_for` explicitness + the recognition-without-source rule.
3. **"What happens to it"** (lines 47-66) — names the real function, the real normalization
   (`CRLF folds to LF; every span, offset, and hash addresses the same normalized text`),
   `Trace.from_source` as *the* pinning constructor, and the policing test by name
   (`tests/test_casespec.py::test_config_never_in_claims`).
4. **The closing determinism + extra sentence** (lines 68-70):

```markdown
Loads and builds are deterministic (`EPOCH_ZERO` timestamps, file-order iteration): the
same file always produces the byte-identical record. PyYAML lives behind the `[config]`
extra (`pip install '.[config]'`); the rest of the spine runs without it.
```

**Sibling-not-widening pointer:** add one line to `docs/case-spec.md` ("the Weekly Spec
extends this mechanism — see `docs/weekly-spec.md`") and link from `docs/architecture.md` §1.

---

### `docs/architecture.md` §1 block list (doc, MODIFY)

**Analog:** the same file, lines 186-187 — the exact sentence to edit:

```markdown
- **Surfaces compose from typed content `blocks`** (prose, claims, kpi, quote, chapters,
  items, prompt, fanout, rationale). The blocks *are* the slots.
```

**Already stale** — `diagram` and `glossary` exist in the live union and are missing here.
Fix the existing drift in the same edit, then add `narrative, recognitions, team, asset`.
Bullet voice to match (lines 183-197): bold lead-in, em-dash clause, file name in backticks.

---

### Spec prose about the four new block kinds (source of truth for the wording)

**Analog:** `src/newsletters/semantic.py` lines 400-464 — the live union idiom.

**Union declaration** (lines 449-464) — the spec must name this structure exactly:

```python
Block = Annotated[
    Union[
        ProseBlock, ClaimsBlock, KpiStripBlock, QuoteBlock, ChaptersBlock, ItemsBlock,
        PromptBlock, FanoutBlock, RationaleBlock, DiagramBlock, GlossaryBlock,
    ],
    Field(discriminator="kind"),
]
```

**Member idiom** (lines 412-418) — `kind: Literal[...]` default, `heading`/`title` optional,
`Field(default_factory=list)` for collections:

```python
class DiagramBlock(BaseModel):
    """An inline SVG diagram — renders the story visually, theming with the page."""

    kind: Literal["diagram"] = "diagram"
    title: Optional[str] = None
    svg: str = ""
    caption: Optional[str] = None
```

**The "unrepresentable, not policed" precedent** the `AssetBlock.asset` invariant must cite
(lines 421-434) — `GlossaryTerm.definition: Claim`, with its docstring reasoning:

```python
class GlossaryTerm(BaseModel):
    """A glossary entry: a term mapped to its DEFINING reviewed, traced ``Claim``.

    Faithfulness enforced *by the type*: ``definition`` is a ``Claim`` ... never a bare
    ``str``. ... A term with no traceable defining claim is NOT glossed here; the learning
    preset routes it to ``surface.missing[]`` (the honesty panel), never a fabricated string.
    """

    term: str
    definition: Claim
```

**The dispatch consequence to write down** — `src/newsletters/render.py` lines 616-620, the
fall-through the spec must require Phase 3 to close:

```python
    if isinstance(b, DiagramBlock):
        h = f'<div class="dh">{_e(b.title)}</div>' if b.title else ""
        cap = f"<figcaption>{_e(b.caption)}</figcaption>" if b.caption else ""
        return f'<div class="block"><figure class="diagram">{h}{b.svg}{cap}</figure></div>'
    return ""          # <-- line 620: the silent drop. Spec: every kind renders OR fails loud.
```

Class vocabulary to name per new block (from the live branches, lines 585-619): `block`,
`block-h`, `chapter` (`t` / `ti` / `bo`), `item` (`sg-tag cat` / `ti` / `bo`),
`figure.diagram` + `figcaption`, `sg-quote`.

---

### `.planning/notes/2026-08-29-pptx-determinism-decision.md` (decision record)

**Analog (shape):** `.planning/notes/a2-problem-lifecycle-decision.md`

**YAML frontmatter + heading pattern** (lines 1-8):

```markdown
---
title: "A2 — Problem Lifecycle Layer: routed decision"
date: 2026-06-17
context: "/gsd-explore design pass — the A1-vs-A2 lifecycle decision for Signals"
status: decided
---

# A2 — Problem Lifecycle Layer (routed decision)

## The question
```

**Section order to copy:** `## The question` → `## The hinge (why the decision came down to
one test)` → `## Decision` (with the scoping blockquote) → `## How it slots into the roadmap`
→ `## Truths checked (still honest)`.

**The blockquote-scoping move** (lines 42-51) — the decision plus the boundary it must not
cross, in one quoted paragraph:

```markdown
**A2 — scoped as a *legibility layer*, not an execution tracker.**

> Signals models the problem **lifecycle** as legible, queryable state — it does **not**
> execute the work. ... **No write-back** ...
```

For this phase: "**BYTE-STABLE, via a declared post-save zip normalization** — scoped to a
fixed (python-pptx, zlib) pair; the committed==fresh gate asserts the part-content digest."

**Truths-checked closing list** (lines 81-88) — bullet per load-bearing truth with `honored:`
/ `preserved:` / `extended:`. Phase 1's list: no auto-publish (`semantic.py` byte-unchanged),
AI-optional core (no column-0 `import pptx` under `src/`), every claim traces to evidence.

**Analog (voice for the "why not the alternative" paragraphs):**
`.planning/notes/2026-07-09-casespec-implementation-notes.md` — headed
`## Integration path chosen: X, NOT Y`, then `## The one genuinely new mechanism`, then
`## Other decisions` as a terse bullet list. Copy that framing for: core-properties marker NOT
notes-slide; zip rewrite NOT monkeypatching `_ZipPkgWriter`; sibling `weeklyspec.py` NOT a
widened `casespec._KNOWN_KEYS`.

---

### `tests/test_pptx_determinism.py` (test, batch/file-I/O)

**Analog:** `tests/test_pptx_golden.py`

**Module-level skip guard — copy verbatim** (lines 45-58); this is what keeps the bare-install
gate green and is the *only* sanctioned way to touch `pptx` from `tests/`:

```python
from __future__ import annotations

import importlib.util
import pathlib

import pytest

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("pptx") is None,
    reason="optional [pptx] extra (python-pptx) not installed",
)

from newsletters.distill import DistillationResult, assert_conforms  # noqa: E402
from newsletters.semantic import Source  # noqa: E402

FIXTURE_DIR = pathlib.Path(__file__).parent / "fixtures" / "pptx"
```

**Teaching module docstring** (lines 1-42) — numbered list of the load-bearing invariants,
each naming the threat/criterion it discharges. Phase 1's version enumerates: (A) part-content
digest equality, (B) full-byte equality after normalization, (C) the **negative control**.

**Determinism test idiom** (lines 216-229) — assertion message states the failure meaning:

```python
@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_determinism(name: str) -> None:
    """Parsing the same fixture twice yields an EQUAL result + a byte-identical Source (L5)."""
    s1, first = _distill(name)
    s2, second = _distill(name)
    assert first == second, f"{name}: non-deterministic distillation"
    assert s1.model_dump_json() == s2.model_dump_json(), (
        f"{name}: two parses of identical bytes produced non-identical Sources (L5 determinism)"
    )
```

**Corpus-is-exactly-N guard** (lines 131-141) — a test that the committed fixture set did not
silently shrink or grow; worth mirroring for the weekly template + evidence artifact.

**Note:** this analog's docstring (lines 21-27) records the *opposite* scope decision —
"determinism asserted on the PARSED Source, NOT on re-saved `.pptx` bytes ... immune to any
python-pptx re-save byte drift (risk A3)". Phase 1's decision is precisely the one that risk
was deferred to. The new note should say so explicitly and supersede it for the writer side.

---

### `tests/fixtures/weekly/_author_template.py` + `template.pptx` (fixture generator)

**Analog:** `tests/fixtures/pptx/_author_fixtures.py` — the closest thing in the repo to the
spike, and it **already contains a working zip normalizer**.

**The existing normalizer to extend, not reinvent** (lines 106-141):

```python
_FIXED = datetime(2026, 1, 1, 0, 0, 0)
_FIXED_ZIP_DATE_TIME = (2026, 1, 1, 0, 0, 0)
_FIXED_W3CDTF = "2026-01-01T00:00:00Z"

def _normalize_zip(raw: bytes) -> bytes:
    """Rewrite every ZIP entry's date_time to a fixed constant, preserving entry order + content."""
    zin = zipfile.ZipFile(io.BytesIO(raw))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():          # original entry order -> deterministic
            data = zin.read(item.filename)
            ...
            info = zipfile.ZipInfo(item.filename, date_time=_FIXED_ZIP_DATE_TIME)
```

RESEARCH Pattern 1's `normalize_opc_zip` is the same shape plus `create_system = 0`,
`compress_type`, and `external_attr` preservation. **Reconcile the two in the decision note**
(one epoch, one normalizer contract) rather than shipping a second, drifting copy — the
`EPOCH_ZERO` "a second sentinel would drift" argument applies to this too.

**Core-property pinning** (lines 151-152) — the Pitfall-6 scrub of `"Steve Canny"` /
`"generated using python-pptx"` belongs right here:

```python
    prs.core_properties.created = _FIXED
    prs.core_properties.modified = _FIXED
```

**Docstring conventions** (lines 1-45): a `THE CORPUS (N fixtures)` inventory, a
`BYTE-REPRODUCIBILITY (threat T-06-11)` section stating *why* it is stable, one ALL-CAPS
gotcha heading per surprise, and a literal run line:
`Run:  .venv/bin/python tests/fixtures/pptx/_author_fixtures.py`.

---

## Shared Patterns

### Deterministic timestamps — reuse `EPOCH_ZERO`, never mint a second epoch
**Source:** `src/newsletters/adapters/_timestamps.py` lines 39-61
**Apply to:** the decision note, `docs/weekly-spec.md`, the determinism test

```python
__all__ = ["EPOCH_ZERO", "deterministic_timestamp"]

# The deterministic "no intrinsic date" sentinel: tz-aware UTC 1970-01-01T00:00:00+00:00.
EPOCH_ZERO = datetime(1970, 1, 1, tzinfo=timezone.utc)

def deterministic_timestamp(intrinsic: datetime | None) -> datetime:
    if intrinsic is None:
        return EPOCH_ZERO
    if intrinsic.tzinfo is None:
        return intrinsic.replace(tzinfo=timezone.utc)   # openpyxl returns `created` tz-naive
    return intrinsic
```

Two things to lift: (1) the tz-naive coercion branch is *exactly* the Pitfall-5 fix for
`cp.created` read-back — the spec should route through `deterministic_timestamp()` or state
`EPOCH_ZERO.replace(tzinfo=None)`; (2) the module docstring's `WHY this exists / THE FIX /
CLAIMS ARE PROVABLY UNAFFECTED` structure is the house style for a determinism rationale —
copy it for the normalizer's docstring in Phase 2 and for the note's reasoning now.

### Absence is disclosed, never fabricated
**Source:** `docs/case-spec.md` lines 43-45 + 66
**Apply to:** `docs/weekly-spec.md`, the asset-record routing table

```markdown
- Every field is optional. An absent or empty field is **disclosed** in
  `Distillation.missing[]` (and the surface's honesty panel) — never fabricated.
...
- everything you left blank listed in `Surface.missing[]`, shown to the reviewer.
```

### Strict schema, teaching errors
**Source:** `.planning/notes/2026-07-09-casespec-implementation-notes.md` lines 35-38
**Apply to:** the Weekly Spec rules section, the fail-loud template contract

```markdown
- Strict schema (unknown field / unknown design slot / coerced scalar → teaching
  `ValueError`): this is an authoring format written by hand in PRs, so a typo must fail
  loudly, not silently drop authored content. Absence, by contrast, is honest and goes to
  `missing[]`.
```

The error *text* pattern (name the problem, name the fix, say what is being refused) is in
RESEARCH Pattern 2 and matches this voice — keep it.

### Optional-extra isolation
**Source:** `tests/test_pptx_golden.py` lines 45-58 (module `pytestmark` skip) and
`docs/case-spec.md` line 69-70 (the extra sentence)
**Apply to:** every Phase 1 artifact that touches `pptx`. No column-0 `import pptx` under
`src/newsletters/`; `tests/test_ai_optional.py` is the guard to re-run per commit.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| the committed determinism **evidence artifact** (e.g. `.planning/notes/pptx-determinism-evidence.json`) | evidence record | batch | No committed measurement artifact exists in the repo — golden fixtures encode expectations in Python (`EXPECTED` table, `test_pptx_golden.py` lines 96-118), not in a data file. Use RESEARCH §Code Examples' `evidence` dict as the schema (`python_pptx`, `zlib`, both raw hashes, `raw_bytes_equal`, `varying_parts`, `varying_zip_fields`, both normalized hashes, `part_digest_a/b`) and place it beside the note that cites it. The closest in-repo idea is the `EXPECTED` table's comment-per-row convention — carry that as a `"note"` field per row. |

## Metadata

**Analog search scope:** `docs/`, `.planning/notes/`, `src/newsletters/` (`semantic.py`,
`render.py`, `templates.py`, `adapters/_timestamps.py`), `tests/`, `tests/fixtures/pptx/`
**Files scanned:** 12 read; `tests/` (40 modules) and `docs/` (8) enumerated
**Pattern extraction date:** 2026-08-29
