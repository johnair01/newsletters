# Phase 1: Specify + de-risk - Research

**Researched:** 2026-08-29
**Domain:** OOXML/`.pptx` write determinism (python-pptx + OPC zip), authored-YAML schema design on the existing Case Spec mechanism, asset provenance/evidence modelling
**Confidence:** HIGH (determinism + python-pptx mechanics were measured, not read about) / MEDIUM (schema field-name recommendations — Claude's discretion, to be locked in the docs by this phase)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Binding decisions from the ONE discussion round (2026-08-29, Editor-in-Chief):**

1. The weekly deck **reuses `Surface(REPORT)`** — the PPTX renderer is an output format, not a
   new semantic kind. No `semantic.py` kind change.
2. Asset provenance minimum = **folder + date + event label**; deep link optional — EXCEPT a BI
   screenshot standing in for values (WKLY-04), where the deep link is REQUIRED. No provenance
   → `missing[]`, never placed silently.
3. Template contract = **named placeholders, fail-loud** on missing/unknown names. The renderer
   never invents layout.

### Claude's Discretion

**Remaining choices are Claude's discretion**, decided per the recorded recommendations and
reasoning (evidence-first, smallest change, fail-loud honesty) and logged — e.g. the
generated-by-marker mechanism (core properties vs. notes) is THIS phase's job to decide with a
stated reason and a stated read-back assertion.

### Deferred Ideas (OUT OF SCOPE)

None — scope is locked by the seed and the roadmap.

### Specific ideas carried from CONTEXT.md

- The determinism spike must run a REAL write twice and commit the evidence (hashes; varying
  parts/fields if any) — a decision without evidence is a vibe.
- Spike scratch code is deleted or lands as a test fixture — never an unguarded import in
  `src/newsletters/`.
- The Weekly Spec section must be complete enough that a reader can hand-author a valid spec
  from the doc alone.
</user_constraints>

<phase_requirements>
## Phase Requirements

Phase 1 carries **no WKLY requirement of its own** (`.planning/REQUIREMENTS.md` §Traceability).
It de-risks two requirements satisfied later. Mapping research support to what it de-risks:

| De-risks | What Phase 1 must settle | Research support in this document |
|----------|--------------------------|-----------------------------------|
| WKLY-01 (Phase 2) | `.pptx` determinism definition, backed by a real double-write with committed evidence | §Determinism Spike — Measured Results (E1–E8); §Pattern 1 (normalize-after-save); §Pitfall 1 (zlib cross-environment) |
| WKLY-01 (Phase 2) | generated-by marker mechanism + stated read-back assertion | §Pattern 3 (core properties, `cp:category` + `cp:contentStatus`); E5, E14 |
| WKLY-01 (Phase 2) | named-placeholder template contract (fail-loud both directions) | §Pattern 2; E9–E11 — **`add_slide()` destroys operator placeholder names** (load-bearing) |
| WKLY-01 (Phase 2) | Draft watermark, deterministic and visible | §Pattern 4; E12–E13 |
| WKLY-02 (Phase 3) | Weekly Spec YAML schema + 4 block kinds, field by field, in the `Block` union | §Pattern 5 (Weekly Spec on the Case Spec mechanism); §Pattern 6 (block-kind field shapes) |
| WKLY-03 (Phase 3) | asset-evidence record shape + `missing[]` routing | §Pattern 7 (the asset record IS the Source; the image is content-addressed inside it) |
</phase_requirements>

## Summary

The determinism question is **settled empirically and the answer is good news**. python-pptx
1.0.2's `Presentation.save()` has exactly **one** source of non-determinism: it calls
`zipfile.writestr(<str arcname>, blob)`, and passing a *string* arcname makes stdlib `zipfile`
stamp every entry with `time.localtime()`. Everything else the roadmap worried about is already
deterministic in the library: part traversal order is a DFS over insertion-ordered `dict`s (the
`visited` collections are sets used only for membership, never iterated), `_Relationships.xml`
serializes rels **sorted numerically by rId**, `_next_rId` deterministically returns the first
free `rIdN`, media parts are content-deduplicated and numbered in add-order, and core properties
are **never auto-bumped on save** (the stock template's 2013 `created`/`modified`/`revision`
survived two saves unchanged). Two writes 3 seconds apart differed **only** in zip `date_time`;
all 38 unzipped parts were byte-identical and in identical name order. A stdlib `zipfile`
re-write pass with fixed `date_time`, fixed `create_system`, and fixed compression makes the file
**byte-identical** across time-separated writes, is idempotent, passes `unzip -t`, and reopens in
python-pptx. Cross-process with `PYTHONHASHSEED` in {0, 1, 12345, random}: one distinct hash.

**Recommended recorded outcome: BYTE-STABLE**, achieved by a declared normalization step — not
the content-stable fallback. But the recorded definition must state its *scope*, because there is
one honest caveat the roadmap didn't anticipate: **DEFLATE output is implementation-dependent.**
reproducible-builds documented Fedora 40 (zlib-ng) and Debian (zlib) producing different
compressed bytes and CRCs for identical input. Byte-identity therefore holds for a fixed
(python-pptx, zlib) pair — which covers the in-process double-render test — but a *committed*
`.pptx` compared against a CI-fresh render crosses environments. The resolution is not to weaken
the definition: it is to make the **committed==fresh gate assert the content digest** (sorted
`(part name, sha256(part bytes))`), which is implementation-independent and strictly stronger
than "the zips look the same", while the double-render test asserts full byte identity. Both
assertions are cheap, and neither normalizes XML — the definition stays strict.

Two findings will change how the plan is written. First, **`slides.add_slide(layout)` regenerates
placeholder names** (`_next_ph_name(ph_type, id, orient)` → `"Title 1"`, `"Content Placeholder 2"`),
silently discarding whatever the operator named them in the Selection Pane. A named-placeholder
contract built on `add_slide` would fail on contact with a real operator template; the contract
must fill **shapes on slides that already exist in the template**, or restore names from the
layout by `placeholder_format.idx` immediately after cloning. Second, python-pptx has **no slide
copy, duplicate, or delete API** (`Slides` public surface is `add_slide / element / get / index /
parent / part`), so any "one slide per lane" design must be built from `add_slide` + name restore,
not from duplicating a prepared slide. Third, duplicate shape names are legal in the format, so
the by-name map must fail loud on collisions or it will silently drop a slot.

**Primary recommendation:** Record **byte-stable via a declared post-save zip normalization**
(fixed `date_time=(1980,1,1,0,0,0)`, `create_system=0`, `compress_type=ZIP_DEFLATED`, entry order
preserved as emitted), with the committed==fresh gate asserting the implementation-independent
part-content digest; put the generated-by marker in **core properties** (`cp:category` for the
marker, `cp:contentStatus` for the gate state) with a read-back-the-written-file assertion; and
specify the Weekly Spec as a **sibling loader of `casespec.py`** (`weeklyspec.py`), reusing the
Case Spec mechanism verbatim rather than widening the Case Spec's exactly-eight-field schema.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Weekly Spec schema definition (field names, types, absence rules) | Docs (`docs/architecture.md` + a new Weekly Spec section) | — | Spec-first is a CLAUDE.md hard rule; this phase ships spec text, not code |
| New block kinds (`Narrative/Recognitions/Team/Asset`) | Core spine (`semantic.py` `Block` union) | HTML renderer (`render.py` dispatch) | Blocks are typed core content; rendering is a consumer, added Phase 3 |
| `.pptx` byte production | Optional writer behind `[pptx]` | stdlib `zipfile` (normalization) | AI-optional/minimal-core: python-pptx must stay lazy-imported behind the extra |
| Determinism enforcement | stdlib `zipfile` normalization pass in the writer | test suite (double-render assertion) | python-pptx cannot be configured to fix zip timestamps; post-processing is the only API-level route |
| Generated-by marker + gate state | OPC core properties (`docProps/core.xml`) via python-pptx | — | Durable, survives PowerPoint round-trip, inspectable in File → Info, adds zero parts |
| Draft watermark | Writer (named shape added per slide) | Operator template (layout/theme) | Adding a named shape is deterministic and does not depend on operator template content |
| Asset provenance evidence | Core spine (`Source` + `Trace.from_source` over the record text) | Weekly Spec loader | An image cannot be a `Source` (transcript is `str`); the *record* is the Source |
| Asset binary identity | Content address (`sha256` hex) recorded in the asset record text | — | Keeps the span-containment gate strict: the hash is a real substring of the record |
| Review gate | `semantic.py` — **untouched** | — | Hard rule: no auto-publish; the renderer must never read-then-mutate review state |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `python-pptx` | 1.0.2 (latest; published 2024-08-07) | Read the operator template, fill named shapes, write the deck | Already the repo's `.pptx` dependency on the loader side (ADAPT-04); **the writer shares the existing `[pptx]` extra — no new dependency this milestone** [VERIFIED: pyproject.toml `pptx = ["python-pptx"]`; `pip index versions python-pptx` → LATEST 1.0.2] |
| `zipfile` (stdlib) | Python 3.12 | Post-save normalization of OPC zip metadata | Stdlib; python-pptx already writes through it; no new dependency, no core import edge |
| `hashlib` (stdlib) | Python 3.12 | Part-content digest (determinism assertion) + asset content-addressing | Already the repo's content-address primitive (`Source.content_hash`) |
| `PyYAML` (via `[config]`) | >=6.0.3 | Weekly Spec parsing through `_yaml_loader.load_config` (`safe_load` only) | Already the Case Spec parse path; the Weekly Spec must reuse it, not add a parser |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `io.BytesIO` (stdlib) | 3.12 | `prs.save(BytesIO)` → normalize in memory → one atomic file write | Recommended over save-to-temp-then-rewrite: no temp file, no partial artifact on failure [VERIFIED: spike4 — `Presentation.save()` accepts a file-like object] |
| `lxml` | transitive of python-pptx | XML parse/serialize inside python-pptx | Never imported directly; stays behind the `[pptx]` extra |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Post-save zip normalization | Monkeypatching `pptx.opc.serialized._ZipPkgWriter.write` to pass a fixed `ZipInfo` | Fewer bytes rewritten, but it reaches into a private class — it would break silently on a python-pptx upgrade and violates "diagnose the live object, not the repo's intent". **Rejected.** |
| `ZIP_DEFLATED` normalization | `ZIP_STORED` normalization | STORED is fully zlib-implementation-independent (byte-stable everywhere), but measured 100,666 B vs 28,244 B on the minimal template — a **3.6×** size increase on a repo-committed artifact. **Rejected**; the content-digest gate solves the same problem without the bloat. |
| Core-properties marker | Notes-slide marker | Measured: touching `notes_slide` adds 4 parts (`ppt/notesSlides/notesSlide1.xml`, its rels, `ppt/notesMasters/notesMaster1.xml`, its rels) to a deck that had none — a structural change to every deck, reader-visible in presenter view, and trivially deleted by an operator. **Rejected.** |
| `cp:category` marker field | `dc:description` (`comments`) | `comments` is free prose an operator may legitimately author in the template; overwriting it is the deck-level version of editorializing. (Note: the stock python-pptx template already writes `"generated using python-pptx"` there.) `cp:category` is a purpose-built classification slot. **`category` recommended.** |
| Fill existing template slides | `add_slide(layout)` per section | `add_slide` regenerates placeholder names (E9) — it discards the operator's naming. Usable only with an explicit name-restore step. See §Pattern 2. |

**Installation:** No new install. The writer shares the existing extra:

```bash
pip install '.[pptx]'     # python-pptx — already declared, loader and writer share it
```

**Version verification:** `pip index versions python-pptx` → `INSTALLED: 1.0.2 / LATEST: 1.0.2`.
Published 2024-08-07. MIT. `Requires: lxml, Pillow, typing-extensions, XlsxWriter`.
[VERIFIED: pypi via `pip index versions`, run 2026-08-29]

## Package Legitimacy Audit

> No package is *added* this milestone. This audit re-verifies the one external package the
> phase reasons about, per protocol.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `python-pptx` 1.0.2 | PyPI | released 2024-08-07 (~2 yrs) | unknown (PyPI API returns null) | github.com/scanny/python-pptx | `SUS` (reason: `unknown-downloads`) | **Approved — pre-existing dependency, no new install.** |

**Packages removed due to `SLOP` verdict:** none
**Packages flagged as suspicious `SUS`:** `python-pptx` — the *only* signal is
`unknown-downloads`, the known PyPI-API false positive already recorded and adjudicated in this
repo's `pyproject.toml` comment for the `[pptx]` extra ("the only SUS signal is
`unknown-downloads`, a known PyPI-API false positive"). It is not a new dependency, it is already
installed in CI via the extra, and it has a real source repo, an MIT licence, and no
`postinstall`. **No `checkpoint:human-verify` is required for this package**, because this phase
installs nothing — but the planner must not silently add any other package.

[VERIFIED: `gsd-tools query package-legitimacy check --ecosystem pypi python-pptx` → verdict SUS,
`exists: true`, `repoUrl: https://github.com/scanny/python-pptx`, `deprecated: false`,
`postinstall: null`]

## Architecture Patterns

### System Architecture Diagram

What Phase 1 *specifies* (dashed = built in Phases 2–3, not here):

```
  AUTHORED INPUT                       ADAPTER EVIDENCE
  weekly-spec.yaml                     .eml / .xlsx / .pptx / PBIP
        |                                      |
        | read_text (CRLF→LF)                  | existing adapters
        v                                      v
  Source(transcript = normalized file text)   Source(...)  [EPOCH_ZERO timestamps]
        |                                      |
        | Trace.from_source(start, end)        | normalize()
        | real spans, content-addressed        v
        v                                    Claim(+Trace)
  Claim(+Trace) ─── config: values bound, NEVER minted ───► CaseSpec.config-style carrier
        |                                      |
        +──────────────┬───────────────────────+
                       v
              Distillation(claims, missing[])
                       |
                       v
        Surface(REPORT, Draft)  ← reuse; NO new semantic kind
        blocks: [KpiStrip, Claims, Narrative, Recognitions, Team, Asset]
        missing[]: absences + provenance-less assets + link-less BI screenshots
                       |
        +──────────────┴───────────────────────+
        |                                      |
        v (Phase 3)                            v (Phase 2)  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
  render.py HTML dispatch            operator template.pptx (named shapes)
  (must fail loud, not return "")              |
                                               v
                                    fill by shape NAME (fail loud both ways)
                                               |
                            state != Published ─┤─► add NL_DRAFT_WATERMARK shape
                                               |
                                    set core props: cp:category (marker),
                                    cp:contentStatus (gate), dcterms:created/
                                    modified = EPOCH_ZERO
                                               |
                                    prs.save(BytesIO)   ← only nondeterminism enters here
                                               |
                                    normalize_opc_zip(bytes)  ← stdlib zipfile rewrite
                                               |
                                               v
                                    deck.pptx  ── read back ──► assert marker + watermark
                                               |
                                               v
                               DETERMINISM GATE (two assertions, no XML normalization)
                               A. content digest  sorted(name, sha256(part))   ← committed==fresh
                               B. full-file sha256 equality                    ← double-render
```

### Recommended Project Structure

Phase 1 writes **documentation only**. The structure below is what the spec must *describe*, so
Phases 2–3 have no discoveries left:

```
docs/
├── architecture.md          # §1 typed model — extend the block list + add the 4 kinds
├── case-spec.md             # unchanged (referenced as the mechanism being extended)
└── weekly-spec.md           # NEW (or a §Weekly Spec inside case-spec.md — see Open Q1)
                             # the hand-authorable schema, field by field

src/newsletters/             # NOTHING written this phase
├── semantic.py              # (Phase 3) 4 new Block classes + union entries
├── weeklyspec.py            # (Phase 3) sibling of casespec.py — NOT a widened casespec.py
├── render.py                # (Phase 3) 4 new dispatch branches; close the `return ""`
└── pptx_writer.py           # (Phase 2) lazy `[pptx]` import; normalize_opc_zip lives here

tests/fixtures/
└── weekly/                  # (Phase 2) minimal SYNTHETIC template.pptx
```

**Naming note:** the loader-side lazy boundary is `adapters/_pptx_loader.py`. A writer-side
boundary should mirror it (`_pptx_writer.py` or a `_load_pptx()` reuse) so the bare-install guard
in `tests/test_ai_optional.py` (column-0 import count == 0) extends by pattern, not by invention.

---

### Pattern 1: Save to memory, normalize the OPC zip, write once

**What:** python-pptx emits a zip whose only unstable field is per-entry `date_time`. Rewrite the
zip with stdlib `zipfile` using fixed metadata, then write the bytes to disk in one operation.

**When to use:** Every `.pptx` the renderer produces. This IS the recorded determinism mechanism.

**Why this and not "fix the timestamps in python-pptx":** `_ZipPkgWriter.write()` calls
`self._zipf.writestr(pack_uri.membername, blob)` — a **string** arcname. `zipfile` then builds a
`ZipInfo` with `date_time=time.localtime()[:6]`. There is no python-pptx API to override it.
[VERIFIED: `pptx/opc/serialized.py` lines 234–242 in the installed 1.0.2]

```python
# Source: measured in this session against python-pptx 1.0.2 (spike4/spike5)
import hashlib, io, zipfile

DOS_EPOCH = (1980, 1, 1, 0, 0, 0)   # earliest DOS-representable timestamp

def normalize_opc_zip(raw: bytes) -> bytes:
    """Rewrite an OPC package with FIXED zip metadata. Part BYTES are untouched."""
    with zipfile.ZipFile(io.BytesIO(raw)) as zin:
        infos = zin.infolist()
        names = [i.filename for i in infos]          # preserve emitted order (already stable)
        attrs = {i.filename: i.external_attr for i in infos}
        data = {n: zin.read(n) for n in names}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            zi = zipfile.ZipInfo(filename=n, date_time=DOS_EPOCH)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 0                     # 0 = MS-DOS; else platform-dependent (3 on unix)
            zi.external_attr = attrs[n]              # preserve python-pptx's value
            zout.writestr(zi, data[n])
    return buf.getvalue()

def part_digest(raw: bytes) -> str:
    """CONTENT identity: sorted (name, sha256(part bytes)). No zip metadata. No XML normalization."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        rows = sorted((n, hashlib.sha256(z.read(n)).hexdigest()) for n in z.namelist())
    h = hashlib.sha256()
    for n, d in rows:
        h.update(n.encode()); h.update(b"\0"); h.update(d.encode()); h.update(b"\n")
    return h.hexdigest()
```

**Measured variants** (all byte-stable across time-separated writes; all reopen in python-pptx;
all keep `[Content_Types].xml` as the first entry):

| Variant | Size | Stable | Note |
|---------|------|--------|------|
| preserve emitted order, deflate default | 28,244 B | ✓ | **recommended** — closest to what python-pptx emits |
| ASCII-sorted names, deflate default | 28,244 B | ✓ | also fine; `[` (0x5B) sorts before `_` and all lowercase, so the content-types stream stays first — but that is *incidental*, assert it explicitly if chosen |
| preserve order, `compresslevel=9` | 28,244 B | ✓ | no size win here; pins one more variable |
| preserve order, `ZIP_STORED` | 100,666 B | ✓ | zlib-independent but 3.6× bigger |

**Decision guidance for the planner:** preserve emitted order. python-pptx's order is already
deterministic (measured: identical name order across writes) *and* it is the order the OPC spec
convention expects (`[Content_Types].xml` first by construction, not by sort luck). Sorting adds
a second guarantee you have to defend; preserving adds none.

---

### Pattern 2: Fill by shape name on template slides — never trust `add_slide` to keep names

**What:** Build `{shape.name: shape}` over `slide.shapes` (not `slide.placeholders`) and fill by
name; fail loud in both directions.

**The load-bearing finding:** `slides.add_slide(layout)` calls
`_SlideShapes.clone_placeholder(...)`, which computes
`name = self._next_ph_name(ph_type, id_, orient)` and injects it into a freshly parsed
`<p:cNvPr id name>`. The **layout's placeholder name is not copied.** Measured: a layout whose
placeholders were renamed `WEEKLY_LANE_TITLE` / `WEEKLY_LANE_BODY` produced a slide with
`Title 1` / `Content Placeholder 2`. [VERIFIED: spike7 + `pptx/shapes/shapetree.py:111-116`,
`pptx/oxml/shapes/autoshape.py:348-368`]

Two viable contracts; the spec must pick one and say why:

**(a) Template-slide contract (recommended).** The operator's template deck contains the actual
slides, with shapes named in PowerPoint's Selection Pane (Home → Editing → Select → Selection
Pane, or `Alt+F10`). The renderer opens the template, fills existing named shapes, and adds no
slides. Simplest, honours "the renderer never invents layout" most literally, and needs no
name-restore machinery. Constraint: the deck's slide count is fixed by the template, so a
variable number of lanes must fit a fixed number of slides (e.g. one lanes-table slide) — which
is arguably the right constraint for a weekly anyway.

**(b) Clone-and-restore contract.** If a repeating section really needs N slides, `add_slide` then
immediately restore names from the layout by `placeholder_format.idx`:

```python
# Source: measured in this session (spike8) — deterministic across time-separated builds
def add_named_slide(prs, layout):
    """add_slide + restore the LAYOUT's placeholder names (python-pptx regenerates them)."""
    slide = prs.slides.add_slide(layout)
    layout_names = {p.placeholder_format.idx: p.name for p in layout.placeholders}
    for ph in slide.placeholders:
        idx = ph.placeholder_format.idx
        if idx in layout_names:
            ph.name = layout_names[idx]
    return slide
```

**Fail-loud, both directions (the locked decision), with a reserved prefix:**

```python
RESERVED = "NL_"   # only shapes under this prefix are renderer slots

def bind(slide, content: dict[str, str]) -> None:
    by_name: dict[str, object] = {}
    for sh in slide.shapes:
        if sh.name in by_name:                                    # duplicates are LEGAL in OOXML
            raise ValueError(
                f"template slide has two shapes named {sh.name!r} — the name→shape binding is "
                "ambiguous. Rename one in PowerPoint's Selection Pane (Alt+F10). "
                "Refusing to guess which slot the content belongs in."
            )
        by_name[sh.name] = sh
    unknown = sorted(set(content) - set(by_name))
    if unknown:
        raise ValueError(
            f"Surface content is bound to placeholder name(s) {unknown!r} that this template does "
            f"not contain. Named shapes on this slide: {sorted(by_name)!r}. "
            "The renderer never invents layout — add the shape to the template or fix the name."
        )
    unfilled = sorted(n for n in by_name if n.startswith(RESERVED) and n not in content)
    if unfilled:
        raise ValueError(
            f"template placeholder(s) {unfilled!r} have no matching Surface content. "
            "A reserved-prefix slot left empty would ship a blank box to a reader — refusing. "
            "Either populate it or remove it from the template."
        )
```

The reserved prefix exists so an operator's logo, footer, page number, and decorative shapes are
not mistaken for unfilled slots. Without it, direction (b) of the fail-loud contract makes every
real template unusable. **This is a spec decision Phase 1 must record.**

---

### Pattern 3: Generated-by marker + gate state in OPC core properties

**Recommendation:**

| What | Field | OPC element | Value |
|------|-------|-------------|-------|
| generated-by marker | `core_properties.category` | `cp:category` | `"generated-by:newsletters"` (exact string is a spec decision) |
| review-gate state | `core_properties.content_status` | `cp:contentStatus` | `"draft"` while `surface.review.state is not PUBLISHED` |
| determinism | `core_properties.created` / `.modified` | `dcterms:created` / `dcterms:modified` | `EPOCH_ZERO` (1970-01-01T00:00:00Z) |

**Why core properties, not the notes slide:** measured — writing a notes slide adds four parts
(`ppt/notesSlides/notesSlide1.xml` + rels, `ppt/notesMasters/notesMaster1.xml` + rels) to a deck
that had none. That is a structural mutation of every deck, is reader-visible in presenter view,
and an operator deletes it by accident. Core properties add **zero** parts, survive a PowerPoint
save round-trip, and are inspectable by a human in File → Info without any tooling.

**Why `content_status` for the gate:** the python-pptx docs describe it as *"completion status of
the document, e.g. 'draft'"* — this is exactly the semantic we need, and it keeps the gate state
out of a free-prose field. [CITED: python-pptx.readthedocs.io/en/latest/api/presentation.html]

**Why not `comments` for the marker:** `dc:description` is free prose an operator may legitimately
have authored in the template deck; overwriting it silently is the deck-level version of
editorializing. (Also note: the stock python-pptx template already ships
`comments = "generated using python-pptx"`, so it is a contested slot.)

**The stated read-back assertion** (this is the wording Phase 1 must record, and Phase 2 must
implement as a test — it reads the *written file*, never the writer's return value):

```python
# Source: measured in this session (spike9) — both fields round-trip through a real write
written = Presentation(str(out_path))            # reopen the FILE that was written
cp = written.core_properties
assert cp.category == "generated-by:newsletters", cp.category
assert cp.content_status == ("draft" if not surface.is_published else ""), cp.content_status
assert cp.created == EPOCH_ZERO.replace(tzinfo=None)   # dcterms serialize as W3CDTF, naive on read
assert any(sh.name == "NL_DRAFT_WATERMARK" for s in written.slides for sh in s.shapes)
```

**Measured `docProps/core.xml` fragment after the write:**

```xml
<dcterms:created xsi:type="dcterms:W3CDTF">1970-01-01T00:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">1970-01-01T00:00:00Z</dcterms:modified>
<cp:category>generated-by:newsletters</cp:category>
<cp:contentStatus>draft</cp:contentStatus>
```

**Timezone gotcha:** `core_properties.created` reads back **tz-naive** (`datetime(1970,1,1,0,0)`),
while `EPOCH_ZERO` in `adapters/_timestamps.py` is **tz-aware** UTC. A naive `==` comparison in a
test will fail. Compare against `EPOCH_ZERO.replace(tzinfo=None)`, or normalize on read the way
`deterministic_timestamp()` already does for openpyxl.

---

### Pattern 4: Draft watermark as a named, added shape

**What:** While `surface.review.state is not PUBLISHED`, the writer adds one textbox per slide
named `NL_DRAFT_WATERMARK`, added **last** so it is top of z-order.

```python
# Source: measured in this session (spike6) — round-trips through a real write
tb = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(7), Inches(2))
tb.name = "NL_DRAFT_WATERMARK"
tb.rotation = 315.0                       # read back as 315.0
run = tb.text_frame.paragraphs[0].runs[0] # after tb.text_frame.text = "DRAFT"
run.font.size = Pt(96); run.font.bold = True
run.font.color.rgb = RGBColor(0xD0, 0xD0, 0xD0)
```

Every property above is a fixed literal — no clock, no randomness — so the watermark contributes
nothing to non-determinism (confirmed: builds with the watermark were part-identical across
time-separated runs).

**Why not "a template-layer element toggled off when published":** removing a shape requires the
undocumented lxml idiom `el.getparent().remove(el)` (python-pptx has no `shapes.remove`), and the
element must exist in the operator's template — which makes correct behaviour depend on operator
template content rather than on the renderer. Adding is unconditional and testable.

**True-transparency caveat:** python-pptx has no API for shape/fill transparency (`alpha`); a
genuinely see-through watermark needs raw `a:alpha` XML. Recommend **not** doing that in Phase 2 —
a light-grey rotated text run is visible, deterministic, and API-supported. Record it as the
choice with the reason, so Phase 2 doesn't rediscover it. [VERIFIED: `Shape` public API has no
transparency attribute; only `rotation`, `fill`, `line`, `text_frame`]

---

### Pattern 5: The Weekly Spec is a **sibling** of the Case Spec, not a widened Case Spec

**What:** `docs/weekly-spec.md` (or a §Weekly Spec section) describes a new YAML document; Phase 3
implements `src/newsletters/weeklyspec.py` next to `casespec.py`, reusing its mechanism verbatim.

**Why a sibling, not an extension:** `casespec._validate` rejects any key outside its exactly-eight
`_KNOWN_KEYS` with a teaching error ("Refusing to drop authored content silently"). Adding weekly
keys to that tuple would make a Case Spec silently accept weekly fields and vice versa — the
opposite of what the strict-schema decision buys. The **mechanism** to reuse is:

| Case Spec mechanism (`casespec.py`) | The Weekly Spec must reuse it verbatim |
|---|---|
| `_parse_config` (`_yaml_loader.load_config` → `yaml.safe_load` only, `[config]` extra, lazy) | ✓ config is data, never code |
| `read_text(encoding="utf-8")` — CRLF folds to LF; offsets/hashes/spans all address that same normalized text | ✓ file text IS the evidence |
| `Source(id=rel, context="weekly-spec:{rel}", transcript=<normalized text>, timestamp=EPOCH_ZERO)` | ✓ |
| `_SpanMinter` forward-only cursor: verbatim `str.find` first, then a raw block-region fallback kept only if `SpanContainmentFaithfulness().entails(claim)` | ✓ byte-verbatim narrative with real spans |
| Root containment: path resolves under `root`, escaping raises `ValueError` | ✓ read-only, data stays local (WORK-01) |
| `config:` carried on the typed spec, **never** minted into a claim (`test_config_never_in_claims` polices it) | ✓ org-specific slots stay config |
| Absent/empty/unlocatable → `Distillation.missing[]` with a disclosure string, never fabricated | ✓ |
| `build_*_report(...)` returns `Surface(REPORT, ...)` with `created=EPOCH_ZERO` and `Review(policy=REPORT.review_policy, author=...)` — **no gate advance** | ✓ reuses `Surface(REPORT)` per the locked decision |
| Every emitted claim re-checked against the live gate; a violation raises `RuntimeError` | ✓ enforced by construction |

**Proposed Weekly Spec schema** (Claude's discretion — the planner should treat these as the
recommended names and lock them in the doc; every field optional, absence → `missing[]`):

```yaml
week:            <the period label, e.g. "2026-W35">   # narrative string
module:          <the module/team this weekly is for>
highlights:                     # NarrativeBlock — authored, byte-verbatim
  - <one highlight, in the author's own words>
lowlights:                      # NarrativeBlock — authored, byte-verbatim
  - <one lowlight, honestly stated>
recognitions:                   # RecognitionsBlock
  - person: <who>
    reason: <what they did, in the author's words>
    source: <optional: an .eml message id / Source id that evidences it>
team:                           # TeamBlock
  - name: <person>
    role: <role>
    lines:                      # short lines, authored
      - <line>
    photo: <optional: an asset key from assets: below>
assets:                         # AssetBlock inputs — see Pattern 7 for the record shape
  <asset-key>:
    file:   <repo-relative path to the image>
    sha256: <content address of the file bytes>
    folder: <the folder it came from>          # provenance minimum 1/3
    date:   <YYYY-MM-DD>                        # provenance minimum 2/3
    event:  <the event label>                   # provenance minimum 3/3
    link:   <deep link; REQUIRED iff stands_in_for: values>
    stands_in_for: <omit | values>              # explicit, never inferred
    caption: <optional>
config:                         # org-specific slots — bound, NEVER claimed
  <key>: <value>
```

**Rules the doc must state explicitly** (mirroring `docs/case-spec.md`'s "Rules the loader
enforces"):

1. The document is a mapping of **exactly** these keys; an unknown key fails loud (a typo must
   never drop authored content).
2. Narrative fields are strings — quote values YAML would type-coerce (`42`, `yes`, `2026-W35`).
3. `highlights` / `lowlights` items are carried **byte-verbatim**; the composer never summarises,
   reorders by importance, or adds connective prose. (Phase 3 ships a planted-editorialization
   guard against this.)
4. Every absent or empty field is **disclosed** in `Surface.missing[]` — including "no lowlights
   were authored", which is exactly the kind of absence a weekly is tempted to hide.
5. `config:` values are bound for downstream use and **never** minted into a claim or rendered
   into a block.
6. A recognition with no `source` is still carried (the author's word is the evidence, traced to
   the spec file) **and** its missing evidence is disclosed — matching WKLY-05's honesty-path
   requirement ("a recognition with no source email").

---

### Pattern 6: The four new block kinds in the discriminated `Block` union

The union in `semantic.py` is `Annotated[Union[...], Field(discriminator="kind")]` with each
member carrying `kind: Literal["<name>"] = "<name>"`. The four new kinds must follow that idiom
exactly. Recommended shapes (field names are Claude's discretion; these are the recommendation):

```python
class NarrativeItem(BaseModel):
    text: str                                   # byte-verbatim authored line
    claim: Optional[Claim] = None               # the traced claim carrying that text

class NarrativeBlock(BaseModel):
    """Authored highlights / lowlights — the author's voice, never summarized."""
    kind: Literal["narrative"] = "narrative"
    heading: Optional[str] = None               # e.g. "Highlights" / "Lowlights"
    tone: Literal["highlight", "lowlight"] = "highlight"
    items: list[NarrativeItem] = Field(default_factory=list)

class Recognition(BaseModel):
    person: str
    reason: str
    evidence: list[Trace] = Field(default_factory=list)   # empty ⇒ disclosed in missing[]

class RecognitionsBlock(BaseModel):
    kind: Literal["recognitions"] = "recognitions"
    heading: Optional[str] = "Recognitions"
    recognitions: list[Recognition] = Field(default_factory=list)

class TeamMember(BaseModel):
    name: str
    role: str = ""
    lines: list[str] = Field(default_factory=list)
    photo: Optional[str] = None                 # an AssetRecord key, NOT a path

class TeamBlock(BaseModel):
    kind: Literal["team"] = "team"
    heading: Optional[str] = "The team"
    members: list[TeamMember] = Field(default_factory=list)

class AssetBlock(BaseModel):
    """One placed asset. It is here ONLY because its provenance record was complete."""
    kind: Literal["asset"] = "asset"
    heading: Optional[str] = None
    asset: "AssetRecord"                        # required — no AssetBlock without a record
    caption: Optional[str] = None
    evidence: list[Trace] = Field(default_factory=list)   # ≥1 by construction (Pattern 7)
```

**Invariant to state in the spec:** `AssetBlock.asset` is **required, not optional**, and
`evidence` is non-empty by construction. That makes "an asset without provenance can reach a
Surface" *unrepresentable* rather than merely policed — the same move `GlossaryTerm.definition:
Claim` already makes in this codebase ("faithfulness enforced by the type").

**The `render.py` consequence Phase 1 must anticipate** (CONTEXT §code_context flags it): the HTML
block dispatch ends at line 620 with a bare `return ""`. Four new kinds added to the union without
four new branches would be **silently swallowed**. The spec must state that each new kind renders
under `docs/design-system.md` tokens **or the dispatch raises** — and that the `return ""`
fall-through becomes a teaching `raise` naming the unhandled `block.kind`. Phase 3 owns the code;
Phase 1 owns writing the contract down.

---

### Pattern 7: The asset-evidence record — the record IS the Source, the image is addressed inside it

**The constraint that drives the design:** `Source.transcript` is a `str` and
`Source.content_hash()` hashes `transcript.encode("utf-8")`. **An image can never be a `Source`.**
Any design that tries to make the binary the evidence fights the spine.

**The design:** the *asset record text* (the `assets:` block of the Weekly Spec, or a sidecar YAML)
is the `Source`. The image's identity lives inside that text as a `sha256` hex string. Every
provenance claim then traces to a **real character span of the record** via `Trace.from_source` —
so the strict half of `SpanContainmentFaithfulness` has teeth, exactly as it does for the Case
Spec. The hash is a literal substring of the record, so it traces verbatim like any other field.

```python
class AssetRecord(BaseModel):
    """A content-addressed file plus its provenance. Absence of a minimum field ⇒ missing[]."""
    key: str                       # the spec-local handle (`assets:` mapping key)
    file: str                      # repo-relative path, root-contained
    sha256: str                    # content address of the FILE BYTES (hashlib.sha256)
    folder: str                    # provenance minimum 1/3  — locked decision
    date: str                      # provenance minimum 2/3  — ISO-8601 YYYY-MM-DD
    event: str                     # provenance minimum 3/3  — the event label
    link: Optional[str] = None     # REQUIRED iff stands_in_for == "values"
    stands_in_for: Optional[Literal["values"]] = None
    caption: Optional[str] = None
    alt: Optional[str] = None
```

**Exact `missing[]` routing (the spec must state these verbatim so Phase 3 has no discretion):**

| Condition | Outcome | Disclosure string shape |
|-----------|---------|-------------------------|
| any of `folder` / `date` / `event` absent or empty | asset **not placed**; no `AssetBlock` minted | `asset {key!r}: provenance field {field!r} is absent — the minimum is folder + date + event label; disclosed, never placed` |
| `stands_in_for == "values"` and `link` absent/empty | asset **not placed** | `asset {key!r}: a screenshot standing in for values requires a deep link to the report; disclosed, never placed` |
| `file` missing on disk, or its `sha256` ≠ the recorded value | asset **not placed** | `asset {key!r}: file {file!r} does not match its recorded content address — refusing to place a file that is not the one the record describes` |
| `file` path escapes `root` | `ValueError` (fail loud, not `missing[]`) | mirrors `casespec.load_case_spec` root containment |
| all minimums present and hash matches | `AssetBlock` minted with ≥1 `Trace` into the record | — |

**Why `stands_in_for` is explicit and never inferred:** deciding "is this a BI screenshot standing
in for values?" by looking at the filename or the image would be the composer forming an opinion
about content. Faithful-not-suggestive means the *author declares it* and the loader enforces the
consequence. This is the single most important design detail in WKLY-03/04 and it belongs in the
spec text, not in Phase 3's head.

**Determinism of the placed image** (measured): `add_picture` from a fixed file produces
`ppt/media/image1.png` deterministically; **two `add_picture` calls with byte-identical files
produce ONE media part** (python-pptx content-deduplicates images). Media parts are numbered in
add order, so iterating assets in **spec file order** keeps `image1..N` stable across renders.
[VERIFIED: spike3 + spike9]

### Anti-Patterns to Avoid

- **Normalizing XML to reach "content-stable".** Whitespace/attribute-order normalization would
  make the definition unfalsifiable — a renderer bug that reorders attributes would pass. The
  content-stable definition must mean *unzipped part bytes are byte-identical*, nothing softer.
  (Note: python-pptx parses with `remove_blank_text=True`, so it already normalizes insignificant
  whitespace **deterministically on load** — you get the benefit without weakening the assertion.)
- **`prs.save(path)` then re-writing the file in place.** Leaves a non-normalized artifact on disk
  if normalization raises. Save to `BytesIO`, normalize, write once.
- **Monkeypatching `pptx.opc.serialized._ZipPkgWriter`.** Private API; breaks silently on upgrade.
- **Using `slide.placeholders` as the binding map.** It contains *only* real placeholders keyed by
  `idx`; operator-added textboxes and pictures are absent (measured: 3 shapes, 2 placeholders).
  Bind over `slide.shapes`.
- **Widening `casespec._KNOWN_KEYS` with weekly fields.** Destroys the strict-schema guarantee in
  both directions.
- **Committing a rendered `.pptx` and asserting full-byte equality against a CI re-render.** See
  Pitfall 1 — that assertion is zlib-implementation-dependent.
- **Advancing or "checking-then-fixing" review state in the writer.** The gate is
  `semantic.py`-owned and must stay byte-unchanged. The writer *reads* `surface.review.state` to
  decide the watermark; it never writes it.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deterministic zip output | A custom zip writer, or a byte-level timestamp patcher that seeks into the local file headers | stdlib `zipfile` rewrite (Pattern 1) | Timestamps appear in **both** the local file header and the central directory; a seek-and-patch fixes one and corrupts the other. Rewriting is ~15 lines and provably correct (`unzip -t` OK, reopens). |
| `.pptx` reading/writing | Manual OOXML XML assembly | `python-pptx` 1.0.2 (already the repo's dep) | Content types, rels graph, rId allocation, media dedup, part naming — all handled, and all measured deterministic. |
| YAML parsing for the Weekly Spec | A new parser, or `yaml.load` | `newsletters._yaml_loader.load_config` | Existing lazy `[config]` boundary; `safe_load` **only** (config is data, not code — CLAUDE.md security rule). |
| Span-traced claims from authored text | A new minter | `casespec._SpanMinter` pattern + `Trace.from_source` | `Trace.from_source` is the sole content-address pinning constructor; the forward-only cursor already solves duplicate-value spans and block-scalar regions. |
| Faithfulness checking | A new "is this verbatim?" check | `SpanContainmentFaithfulness()` (the live gate) | One definition of faithful, reused, never reimplemented — the existing modules say so explicitly. |
| Deterministic timestamps | A new epoch constant | `adapters._timestamps.EPOCH_ZERO` / `deterministic_timestamp()` | Already the repo-wide sentinel; a second one would drift. |
| Content addressing | A new hashing scheme | `hashlib.sha256` hex, matching `Source.content_hash()` | Same primitive, same encoding, comparable across the codebase. |
| Slide duplication | An XML deep-copy of a slide + its rels | `add_slide(layout)` + name restore (Pattern 2b) | python-pptx has no copy API; hand-rolled slide cloning is a well-known source of corrupt decks (rels, media rIds, notes). |

**Key insight:** every deterministic behaviour this milestone needs already exists in the repo as
a named pattern (`EPOCH_ZERO`, `Trace.from_source`, `_SpanMinter`, the lazy-extra loader, the
strict-schema validator). The only genuinely *new* mechanism is the 15-line zip normalization —
and that is stdlib. If a plan proposes a new abstraction here, it is almost certainly duplicating
one of the seven rows above.

## Common Pitfalls

### Pitfall 1: DEFLATE output is implementation-dependent — byte-stability does not automatically survive a machine change

**What goes wrong:** A `.pptx` is committed from a developer machine; CI re-renders it and asserts
byte equality (the repo's existing `test_committed_equals_fresh_build` norm, extended to `.pptx`
by ROADMAP Phase 4 criterion 2). The bytes differ even though the deck is semantically identical.

**Why it happens:** the ZIP entries are DEFLATE-compressed, and different zlib implementations
produce different compressed streams for identical input. reproducible-builds documented exactly
this: a Python script deterministic under Debian's zlib produced different compressed data *and
different CRCs* on Fedora 40, which ships zlib-ng as system zlib.
[CITED: lists.reproducible-builds.org/pipermail/rb-general/2024-September/003547.html]
Compression *level* also changes the bytes — measured: level 6 and level 9 produce different
output for the same input (same length, different bytes).

**How to avoid:** two-level assertion, neither of which normalizes XML.
- **Level A — content digest** (`sorted (part name, sha256(part bytes))`): implementation-
  independent. **This is what the committed==fresh gate must assert for `.pptx`.**
- **Level B — full-file sha256** after normalization: asserted by the in-process double-render
  test, where the zlib implementation is by definition the same.

Also: pin the compression choice in the normalizer (`ZIP_DEFLATED`, one explicit level or the
documented default) so at least the *level* is never a variable. And consider a floor pin on
`python-pptx` in the `[pptx]` extra (currently unpinned) — see Pitfall 4.

**Warning signs:** the `.pptx` determinism test is green locally and red in CI, with identical
part contents but a different file hash. That symptom is *diagnostic* of this pitfall and of
nothing else.

---

### Pitfall 2: `add_slide()` silently discards the operator's placeholder names

**What goes wrong:** the operator carefully names layout placeholders in the Selection Pane, the
renderer calls `add_slide(layout)`, and every slot comes back as `"Title 1"` / `"Content
Placeholder 2"`. The fail-loud contract then rejects every one of the operator's names — or, worse,
a positional fallback quietly fills the wrong boxes.

**Why it happens:** `_SlideShapes.clone_placeholder()` computes
`name = self._next_ph_name(ph_type, id_, orient)` and writes that into the new `<p:cNvPr>`. The
layout name is never read.

**How to avoid:** Pattern 2 — either fill slides that already exist in the operator's template
(recommended), or restore names from the layout by `placeholder_format.idx` immediately after each
clone. Whichever is chosen, **the spec must say which**, because it determines what an operator is
told to do in `docs/weekly.md` (Phase 4).

**Warning signs:** a test that names layout placeholders and asserts them on an `add_slide`d slide
fails with `['Content Placeholder 2', 'Title 1']`. (That is the literal assertion failure this
research produced.)

---

### Pitfall 3: Duplicate shape names are legal, and a naive `{name: shape}` dict silently drops one

**What goes wrong:** `{sh.name: sh for sh in slide.shapes}` last-wins. Two shapes named
`NL_NARRATIVE_HIGHLIGHTS` (easy to create by copy-pasting a box in PowerPoint) means one is filled
and one ships blank — a silent drop, which is exactly what the fail-loud contract exists to prevent.

**Why it happens:** OOXML does not require unique `cNvPr/@name`; python-pptx happily wrote two
shapes with the same name in this session.

**How to avoid:** build the map with an explicit collision check that raises (Pattern 2 code).

**Warning signs:** `len({sh.name for sh in shapes}) != len(list(shapes))`.

---

### Pitfall 4: `python-pptx` is unpinned, and XML serialization is not a stability contract

**What goes wrong:** a `pip install '.[pptx]'` on a later python-pptx picks up a changed default
template, a changed attribute order, or a changed `_next_ph_name` scheme. Every committed
`.pptx`-adjacent digest goes red at once, with no code change.

**Why it happens:** `pyproject.toml` declares `pptx = ["python-pptx"]` — no floor, no ceiling.
python-pptx makes no documented byte-output-stability promise across versions.

**How to avoid:** record the exercised version in the determinism decision (**1.0.2**, latest as
of 2026-08-29) and recommend a floor pin (`python-pptx>=1.0.2`) in Phase 2. Note that
`tests/test_ai_optional.py::test_pptx_extra_declared` asserts the extra contains **exactly**
`{"python-pptx"}` by *name* — a version specifier is parsed out by `_req_name`, so adding a pin
does not break that guard, but the planner should verify rather than assume.

**Warning signs:** determinism tests fail immediately after a dependency refresh with no source
change.

---

### Pitfall 5: The core-properties timezone mismatch

**What goes wrong:** `assert prs.core_properties.created == EPOCH_ZERO` fails with
`datetime(1970,1,1,0,0) != datetime(1970,1,1,0,0,tzinfo=utc)`.

**Why it happens:** `dcterms:created` serializes as W3CDTF `1970-01-01T00:00:00Z` but python-pptx
reads it back **tz-naive**. The repo's `EPOCH_ZERO` is tz-aware. This is the same class of bug
`deterministic_timestamp()` was written to absorb for openpyxl.

**How to avoid:** compare against `EPOCH_ZERO.replace(tzinfo=None)`, or route the read-back through
`deterministic_timestamp()`. State the comparison in the recorded read-back assertion so Phase 2
copies it rather than rediscovering it.

---

### Pitfall 6: The stock python-pptx template carries someone else's name

**What goes wrong:** the minimal synthetic template Phase 2 ships is built from `Presentation()`,
whose default template has `last_modified_by = "Steve Canny"`, `comments = "generated using
python-pptx"`, and `created/modified = 2013-01-27`. Those ship in the repo.

**Why it happens:** `Presentation()` with no argument loads python-pptx's bundled default template.

**How to avoid:** the synthetic template's core properties must be scrubbed to fabricated/neutral
values as part of building it, and the abstraction guard's spirit ("no fixture-specific name leaks")
should be read as covering it. Cheap to fix, embarrassing to ship.

---

### Pitfall 7: Adding four block kinds without four dispatch branches

**What goes wrong:** `render.py`'s block dispatch falls through to `return ""` at line 620. A new
`AssetBlock` renders as the empty string — a silent drop, the exact failure mode the whole product
exists to prevent.

**Why it happens:** the union and the dispatch are in different files with no compile-time link.

**How to avoid:** Phase 1's spec must state the contract ("every block kind renders or fails
loud") so Phase 3's plan carries it as an explicit task; ROADMAP Phase 3 criterion 1 already
requires the proof. A `raise` on the fall-through, plus a test that constructs every member of the
`Block` union and asserts non-empty output, is the durable guard.

## Code Examples

### The determinism spike, as it should be committed

The spike must "run a REAL write twice and commit the evidence (hashes; varying parts/fields if
any)". A committed script + a committed evidence file is the shape:

```python
# Source: distilled from the measured spikes in this session (python-pptx 1.0.2)
import hashlib, io, json, time, zipfile
from pptx import Presentation

def render(template: str) -> bytes:
    prs = Presentation(template)
    prs.slides[0].shapes.title.text = "Weekly — Module A"
    cp = prs.core_properties
    cp.category = "generated-by:newsletters"
    cp.content_status = "draft"
    cp.created = cp.modified = datetime(1970, 1, 1)
    buf = io.BytesIO()
    prs.save(buf)                       # <-- the only nondeterminism enters here
    return buf.getvalue()

raw_a = render(TPL); time.sleep(3); raw_b = render(TPL)     # cross a DOS-time boundary

evidence = {
    "python_pptx": "1.0.2",
    "zlib": zlib.ZLIB_RUNTIME_VERSION,
    "raw_a_sha256": hashlib.sha256(raw_a).hexdigest(),
    "raw_b_sha256": hashlib.sha256(raw_b).hexdigest(),
    "raw_bytes_equal": raw_a == raw_b,                       # False — see varying_fields
    "varying_parts": _differing_parts(raw_a, raw_b),         # [] — all part bytes identical
    "varying_zip_fields": _differing_zipinfo(raw_a, raw_b),  # ["date_time"]
    "normalized_a_sha256": hashlib.sha256(normalize_opc_zip(raw_a)).hexdigest(),
    "normalized_b_sha256": hashlib.sha256(normalize_opc_zip(raw_b)).hexdigest(),
    "normalized_bytes_equal": normalize_opc_zip(raw_a) == normalize_opc_zip(raw_b),  # True
    "part_digest_a": part_digest(raw_a),
    "part_digest_b": part_digest(raw_b),
}
```

**Sleeping 3 seconds is load-bearing.** Two writes inside the same wall-clock second are already
byte-identical (measured: both `sha256[:16] == 646525cdefc453a0`) — a spike without a delay would
"prove" byte-stability that isn't there and record a false decision.

### The Weekly Spec loader skeleton (Phase 3 — shown so the spec can describe it precisely)

```python
# Source: the live casespec.py contract, applied to the weekly schema
def load_weekly_spec(path, *, root=None) -> WeeklySpecLoad:
    root_path = (root or Path.cwd()).resolve()
    resolved  = (Path(path) if Path(path).is_absolute() else root_path / path).resolve()
    rel       = resolved.relative_to(root_path).as_posix()      # ValueError if it escapes root
    transcript = resolved.read_text(encoding="utf-8")           # READ ONLY; CRLF folds to LF

    source = Source(id=rel, context=f"weekly-spec:{rel}",
                    transcript=transcript, timestamp=EPOCH_ZERO)
    parsed = _validate(_parse_config(transcript))               # safe_load; unknown key ⇒ raise
    minter = _SpanMinter(source)                                # forward-only cursor
    # ... walk parsed in FILE ORDER; mint or disclose; config carried, never minted ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pptx.api.Presentation` / older 0.6.x module layout | `pptx.Presentation`; OPC writer lives in `pptx/opc/serialized.py` (`PackageWriter`, `_ZipPkgWriter`) | python-pptx 1.0.0 (2024) | Any spike code or advice referencing `pptx/opc/pkgwriter.py` or `pptx/opc/phys_pkg.py` is pre-1.0 and stale. The measured line references in this document are against **1.0.2**. |
| "zips are inherently non-reproducible" | Reproducible-builds practice: fix mtimes (1980-01-01 floor), fix entry order, strip extras — plus the newer recognition that **DEFLATE itself varies by implementation** (zlib vs zlib-ng) | zlib-ng adoption in mainstream distros (Fedora 40, 2024) | Byte-identity claims must state their zlib scope. Content-level digests do not. [CITED: reproducible-builds.org/docs/archives/] |
| `datetime.now()` fallbacks in adapters | `EPOCH_ZERO` / `deterministic_timestamp()` | this repo, v1.1 (`adapters/_timestamps.py`) | The `.pptx` writer must extend this pattern to `dcterms:created` / `dcterms:modified`, not invent a second epoch. |

**Deprecated/outdated:**
- `python-pptx` 0.6.x import paths and internal module names — the writer internals moved in 1.0.
- Any advice to set `strict_timestamps` on python-pptx's own writer: it is already `False` in
  `_ZipPkgWriter._zipf`, which is why pre-1980 dates *could* be written — but the arcname is still
  a `str`, so `time.localtime()` still wins. The flag is not the lever.

## Determinism Spike — Measured Results

> Everything below was **run in this session** against `python-pptx 1.0.2`, CPython 3.11.15,
> `zlib 1.3` (runtime 1.3), Linux. These are observations, not recollections. The *committed*
> spike is Phase 1 execution work; this is the de-risking evidence that tells the planner what
> the spike will find and how to write it.

| # | Finding | Evidence |
|---|---------|----------|
| **E1** | The only non-determinism in `Presentation.save()` is the zip entry timestamp. `_ZipPkgWriter.write()` calls `self._zipf.writestr(pack_uri.membername, blob)` — a **str** arcname, so `zipfile` stamps `time.localtime()`. `ZipFile` is opened `"w", compression=ZIP_DEFLATED, strict_timestamps=False`. | `pptx/opc/serialized.py:234-242` |
| **E2** | Two writes **in the same second** → **byte-identical** (`sha256[:16] = 646525cdefc453a0`, 28,265 B both). Two writes **3 s apart** → different bytes; `date_time` `(2026,8,29,2,53,24)` vs `(2026,8,29,2,53,28)`; **all 38 unzipped parts byte-identical**; identical entry-name order; **0** other differing ZipInfo fields. | spike1, spike2 |
| **E3** | Part order and rIds are deterministic by construction: `iter_parts`/`iter_rels` DFS over `rels.values()` (insertion-ordered dict); `visited` sets are membership-only, never iterated; `_Relationships.xml` emits rels **sorted numerically by rId**; `_next_rId` returns the first free `rIdN`. | `pptx/opc/package.py:88-120, 595-661` |
| **E4** | Cross-process determinism holds: `PYTHONHASHSEED ∈ {0, 1, 12345, random}` → **1 distinct** normalized-output hash (`99b655bbf377724add39a46c520b2a29`). No hash-seed sensitivity. | spike4 |
| **E5** | Core properties are **not** auto-updated on save: the stock template's `created=2013-01-27T09:14:16`, `modified=2013-01-27T09:15:58`, `revision=1` survived two saves unchanged. | spike1 |
| **E6** | Normalization works. Fixed `date_time=(1980,1,1,0,0,0)`, `create_system=0`, fixed compress type → **byte-identical** across time-separated writes; **idempotent** (`normalize(normalize(x)) == normalize(x)`); `unzip -t` → "No errors detected"; reopens in python-pptx with title and core props intact; `[Content_Types].xml` remains the first entry. | spike2, spike4, spike5 |
| **E7** | `Presentation.save()` accepts a file-like object → in-memory save + normalize + one atomic write is available. | spike4 |
| **E8** | Multi-slide + image builds are deterministic: 3 added slides → `ppt/slides/slide1..4.xml`; all part digests equal across time-separated builds; two `add_picture` calls with identical bytes produce **one** `ppt/media/image1.png` (content dedup). | spike7/8, spike3, spike9 |
| **E9** | **`add_slide(layout)` regenerates placeholder names.** A layout renamed `WEEKLY_LANE_TITLE`/`WEEKLY_LANE_BODY` yields a slide with `Title 1`/`Content Placeholder 2`. Restoring names by `placeholder_format.idx` after the clone works and stays deterministic. | spike7 (assertion failure), spike8 (fix), `shapetree.py:111-116` |
| **E10** | No slide copy/duplicate/delete API. `Slides` public surface: `add_slide, element, get, index, parent, part`. Shape deletion requires the lxml idiom `el.getparent().remove(el)`. | spike6, spike8 |
| **E11** | **Duplicate shape names are permitted** — two shapes named `NEWSLETTERS_DRAFT_WATERMARK` coexisted on one slide. | spike6 |
| **E12** | A watermark textbox (`rotation=315.0`, `Pt(96)`, bold, `RGBColor(0xD0,0xD0,0xD0)`) round-trips through a real write; readable back by name. | spike6 |
| **E13** | Notes-slide marker costs 4 new parts including a `notesMaster1.xml`. Core-properties marker costs 0. | spike6 |
| **E14** | `category` → `cp:category` and `content_status` → `cp:contentStatus` both round-trip; `created/modified` serialize as `1970-01-01T00:00:00Z` and read back **tz-naive**. | spike9 |
| **E15** | Normalize variant sizes (all stable): preserve-order/deflate-default **28,244 B**; sorted/deflate-default **28,244 B**; deflate-9 **28,244 B**; `ZIP_STORED` **100,666 B**. | spike5 |
| **E16** | python-pptx parses with `etree.XMLParser(remove_blank_text=True, resolve_entities=False)` — entity expansion (XXE) is disabled; insignificant whitespace is stripped deterministically on load. | `pptx/oxml/__init__.py:21` |

## Project Constraints (from CLAUDE.md)

Directives the planner must honour; each has a checkable consequence for this phase.

| CLAUDE.md directive | Consequence for Phase 1 |
|---|---|
| **AI-optional core** — `core` imports only stdlib + Pydantic; AI/extra deps lazy-imported behind extras; CI fails on a reachable core edge | The spike must not leave any `import pptx` at column 0 under `src/newsletters/`. `tests/test_ai_optional.py` asserts column-0 import count 0 for the loader; the writer must mirror it. **`lint-imports` contracts stay KEPT; bare-install CI untouched.** (ROADMAP Phase 1 criterion 5.) |
| **No auto-publish, ever** | Nothing in this phase touches `semantic.py`. The spec must state that the writer *reads* `review.state` and never writes it. |
| **Every published claim traces to evidence** | The Weekly Spec and asset-record specs must define `missing[]` routing before any composer exists (Patterns 5, 7). |
| **Faithful, not suggestive** | `stands_in_for` is author-declared, never inferred; narrative is byte-verbatim; the composer never editorializes. |
| **Interactive until trusted** | The spike is read-only + writes to a scratch/tmp path; no installs that write config; no external calls. |
| **Secrets in git-ignored env files; private corpora local + encrypted** | The spike must use a **fabricated** template, never an operator deck. Any real deck used to explore must never be committed. |
| **Specs are the source of truth; never let code and spec drift silently** | `docs/architecture.md`'s block list (line 186: "prose, claims, kpi, quote, chapters, items, prompt, fanout, rationale") is **already stale** — it omits `diagram` and `glossary`, which exist in the union. Phase 1 adds four more; fix the existing drift in the same edit. |
| **Branch + PR only; never push to `main`; atomic commits** | One task = one commit; docs and evidence land on the phase branch. |
| **Compass + RETRO per phase** | `WHERE-WE-ARE.md` updated and any friction logged in `RETRO.md` at phase end. |
| **Visual fidelity is not optional** (`docs/design-system.md`, `--radius: 0`) | The four new block kinds' HTML rendering (Phase 3) must be specified against design-system tokens; Phase 1's spec should name the tokens each block uses so Phase 3 has no visual discretion. |
| **Typed everything** | The four block kinds are Pydantic models in the discriminated union, with `AssetBlock.asset` **required** so provenance-less placement is unrepresentable. |
| **"The agent says green" ≠ green** | Every determinism/marker assertion is stated as *read the written file back*, never *trust the writer's return value* (ROADMAP Phase 2 criterion 3 says this too). |

## Runtime State Inventory

**Not applicable** — Phase 1 is a greenfield specify-and-spike phase. It is not a rename,
refactor, or migration; it introduces no string rename, mutates no stored data, registers no OS
state, and changes no secret or env-var name. No inventory is required.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.12 in CI (`.github/workflows/ci.yml`, `ubuntu-latest`); 3.11.15 in the research venv | — |
| `python-pptx` | the determinism spike | ✗ **in the repo env** / ✓ in a scratch venv | 1.0.2 | `pip install '.[pptx]'` — the extra already exists; **the spike must install it, it is not present by default** |
| `zlib` | zip normalization | ✓ | 1.3 (runtime 1.3) | stdlib; version recorded in the evidence file |
| `unzip` | spike evidence (archive integrity check) | ✓ | system | `zipfile.ZipFile.testzip()` (used and passing) |
| PyYAML (`[config]`) | Weekly Spec examples in docs | ✓ declared | >=6.0.3 | `pip install '.[config]'` |
| LibreOffice **Impress** | opening a normalized deck in a real consumer | ✗ | only `libreoffice-core` is installed; no Impress filter | **none in this environment** — see below |
| Microsoft PowerPoint | the definitive consumer check | ✗ | — | human verification |

**Missing dependencies with no fallback:**
- **A real `.pptx` consumer.** `libreoffice` is on PATH but only `libreoffice-core` is installed
  (no `libreoffice-impress`); it fails to load **any** `.pptx`, including an un-normalized
  python-pptx output and python-pptx's own default template. So the "does a normalized deck still
  open in real software?" question could **not** be answered here. What *was* proven: `unzip -t`
  reports no errors, `ZipFile.testzip()` passes, and python-pptx reopens the normalized bytes with
  title, shape names, and core properties intact. **The planner should add a
  `checkpoint:human-verify` in Phase 2 — open the normalized deck once in real PowerPoint (and/or
  install `libreoffice-impress` in CI) before the renderer is accepted.** This is the single
  unverified link in the normalization chain, and it is cheap to close.

**Missing dependencies with fallback:**
- `python-pptx` is absent from the repo environment. The Phase 1 spike plan must include
  `pip install '.[pptx]'` as an explicit step (or run in a scratch venv), or the spike task will
  fail on `ModuleNotFoundError: No module named 'pptx'` at first contact.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (`[test]`/`[dev]` extras); `pythonpath = ["src"]`, `testpaths = ["tests"]` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_ai_optional.py -x -q` (the guard most likely to catch a spike leak) |
| Full suite command | `pytest -q` |
| Adjacent gates | `lint-imports` (contracts KEPT) · `newsletters check --corpus {rev1,work,module}` · `mypy` / `black` / `isort` no-NEW-failures vs the 2026-07-02 baseline · bare-install CI (`pip install '.[test]'`, no extras) |

### Phase Requirements → Test Map

Phase 1 ships **spec text + a recorded decision with evidence**, so most criteria are validated by
document/artifact inspection rather than by a new test. What Phase 1 *can and should* assert
automatically is (a) that the spike left no production surface behind, and (b) that the spec's
claims about the current code are true.

| Criterion | Behavior | Test Type | Automated Command | File Exists? |
|-----------|----------|-----------|-------------------|--------------|
| SC-1 | Spec documents the 4 block kinds + Weekly Spec schema, hand-authorable from the doc alone | manual-only (doc review) — *justification: prose completeness is not machine-checkable; the executable proof is Phase 3 composing a hand-authored spec* | — | — |
| SC-2 | Determinism spike ran a **real** double write and recorded ONE outcome with evidence | artifact | inspect the committed evidence file (hashes for both runs, varying fields, versions) | ❌ Wave 0 — the evidence file is a Phase 1 deliverable |
| SC-2 | The spike is reproducible, not a one-off | integration | `pytest tests/test_pptx_determinism.py -x -q` (spike lands as a **test fixture**, per CONTEXT: "deleted or lands as a test fixture") | ❌ Wave 0 |
| SC-3 | `semantic.py` unchanged (no new Surface kind) | unit/guard | `git diff --stat -- src/newsletters/semantic.py` → empty | ✅ (git) |
| SC-3 | The marker mechanism has a **stated** read-back assertion | doc + fixture | the recorded decision includes the exact `assert` lines (Pattern 3) that Phase 2 will copy | ❌ Wave 0 |
| SC-5 | No production surface left behind: no unguarded `import pptx` under `src/` | unit/guard | `pytest tests/test_ai_optional.py -x -q` (column-0 import guard, already exists) | ✅ `tests/test_ai_optional.py` |
| SC-5 | `lint-imports` contracts stay KEPT | static | `lint-imports` | ✅ `.importlinter` |
| SC-5 | Bare-install CI untouched | static | `git diff -- .github/workflows/ci.yml` → empty | ✅ (git) |
| SC-5 | No new dependency in the `[pptx]` extra | unit/guard | `pytest tests/test_ai_optional.py::test_pptx_extra_declared -x -q` | ✅ |
| all | Full suite does not regress | regression | `pytest -q` | ✅ |

### The determinism assertions later phases derive from the recorded definition

This is the concrete contract Phase 1 hands to Phases 2 and 4. Both assertions are on the
**written file**, and **neither normalizes XML**:

```python
# A. CONTENT identity — implementation-independent. Used by the committed==fresh gate (Phase 4),
#    because the committed artifact and the CI re-render may cross zlib implementations.
assert part_digest(committed_bytes) == part_digest(fresh_bytes), \
    "committed .pptx and a fresh render differ in part CONTENT — a real regression"

# B. BYTE identity — the recorded definition. Used by the in-process double-render test (Phase 2),
#    where the (python-pptx, zlib) pair is fixed by construction.
assert render(surface) == render(surface), \
    "two renders of the same Surface are not byte-identical — a clock, an unstable part order, " \
    "or an unstable rel id leaked into the writer"

# C. NEGATIVE control — the assertion must be able to FAIL. Phase 2 should prove it by asserting
#    that an un-normalized double write across a time boundary is NOT byte-equal, so the green
#    result in (B) is attributable to the normalizer and not to two writes landing in one second.
```

Assertion **C** is the one most likely to be omitted and most important to include: without it,
`render(s) == render(s)` passes trivially whenever both writes land in the same wall-clock second
(measured: they do, ~28,265 identical bytes) — a green test that proves nothing.

### Sampling Rate

- **Per task commit:** `pytest tests/test_ai_optional.py -x -q` (spike-leak guard) + `lint-imports`
- **Per wave merge:** `pytest -q`
- **Phase gate:** full enforced gate set from `.planning/ROADMAP.md` §Enforced gate set, re-run
  **independently** (once per check — rapid re-runs throw transient errors), before
  `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `pip install '.[pptx]'` (or a scratch venv) — **python-pptx is not installed in the repo
      environment**; every spike task fails at import without this
- [ ] `tests/test_pptx_determinism.py` — the spike as a durable fixture/test (covers SC-2), including
      the negative control (assertion C) and the 3-second delay between writes
- [ ] the committed evidence artifact (both runs' hashes, varying fields, `python-pptx` + `zlib`
      versions) — SC-2's "committed evidence"
- [ ] a **fabricated** minimal template `.pptx` with scrubbed core properties (Pitfall 6) — needed
      by the determinism test; Phase 2 also needs it

*(Framework install: not needed — `pytest` is already the framework and the suite is green.)*

## Security Domain

`security_enforcement: true`, `security_asvs_level: 1`. Phase 1 writes docs and runs a local
read-only spike, so the exposure is small — but the spec it writes determines Phase 2/3's exposure,
so the controls belong here.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface; no network, no accounts |
| V3 Session Management | no | No sessions |
| V4 Access Control | **yes (weakly)** | The **review gate** is this product's access control for publication. Phase 1's spec must state the writer never advances or mutates `review.state`; `semantic.py` stays byte-unchanged |
| V5 Input Validation | **yes** | Weekly Spec YAML parsed with `yaml.safe_load` **only** via `_yaml_loader.load_config` (never `yaml.load` — config is data, not code). Strict unknown-key rejection with a teaching error. Asset paths root-contained via `Path.resolve().relative_to(root)` — the `casespec.load_case_spec` precedent |
| V6 Cryptography | **yes (hashing only)** | `hashlib.sha256` for content addressing, matching `Source.content_hash()`. No key material, no signing, no custom crypto |
| V12 File & Resource Handling | **yes** | Reading an operator-supplied `.pptx` (a zip) and operator-supplied image files. See threats below |
| V14 Configuration | **yes** | `[pptx]` stays an optional extra; bare install must remain AI-free and extra-free (the existing `test_ai_optional` / `lint-imports` / bare-install-CI triad) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XXE / external entity expansion when parsing operator OOXML | Information disclosure | **Already mitigated upstream**: python-pptx parses with `etree.XMLParser(remove_blank_text=True, resolve_entities=False)` [VERIFIED: `pptx/oxml/__init__.py:21`]. Record it so Phase 2 does not build a second parser without it |
| Zip-slip (a template entry named `../../etc/x`) during normalization | Tampering | The normalizer **never writes entries to disk** — it reads with `ZipFile.read(name)` and rewrites into another `ZipFile`. No path is ever joined to the filesystem. State this property in the spec; it is why Pattern 1 is safe by construction |
| Decompression bomb in an operator template | DoS | The renderer reads a deck the operator supplies about their own machine — same trust level as their own files. Note as accepted; if a limit is ever wanted, `ZipInfo.file_size` is checkable before `read()` |
| Path traversal via an asset `file:` value in the Weekly Spec | Tampering / information disclosure | Root containment (`resolve().relative_to(root)` → `ValueError`) — the existing `casespec` edge policy, restated in the asset-record spec (Pattern 7 routing table) |
| Substituted asset (record says one image, a different one is on disk) | Tampering | `sha256` content address recorded in the asset record; mismatch ⇒ not placed, disclosed in `missing[]` |
| YAML deserialization RCE | Elevation of privilege | `safe_load` only — already a CLAUDE.md hard rule and enforced in `_yaml_loader` |
| Operator data leaking into the repo via the spike or the sample template | Information disclosure | Synthetic/fabricated template only; scrub core properties (Pitfall 6); abstraction guard stays green |
| Silent publication of an unreviewed deck | Elevation of privilege | `cp:contentStatus = "draft"` + a visible watermark + the untouched gate; asserted by reading the written file back |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The recommended Weekly Spec field names (`week`, `module`, `highlights`, `lowlights`, `recognitions`, `team`, `assets`, `config`) are a good schema | Pattern 5 | Low — explicitly Claude's discretion; Phase 1's job is to *choose and record*. Renaming later is a doc + loader edit before any corpus exists |
| A2 | The recommended block field names (`NarrativeItem.text`, `Recognition.person/reason`, `TeamMember.name/role/lines/photo`, `AssetBlock.asset`) are right | Pattern 6 | Low-medium — these enter the typed union in Phase 3 and would be a breaking change afterwards. Worth a deliberate decision in the doc, not a default |
| A3 | `"generated-by:newsletters"` is the right marker string, and `cp:category` the right field | Pattern 3 | Low — the *mechanism* (core properties, read-back asserted) is the load-bearing choice and is evidence-backed; the exact field/string is cosmetic and cheap to change before Phase 2 |
| A4 | A reserved shape-name prefix (`NL_`) is needed for the fail-loud contract to work on real templates | Pattern 2 | **Medium** — without it, "template shape with no Surface content fails loud" rejects every operator logo/footer, making the contract unusable. Not empirically tested against a real operator deck (none available). Should be confirmed at the Phase 2 human-verify checkpoint |
| A5 | Filling existing template slides (rather than `add_slide`ing them) fits the weekly's shape | Pattern 2a | Medium — depends on whether the weekly needs a variable slide count. If it does, Pattern 2b applies. **The spec must pick one; this research cannot pick for the operator** |
| A6 | Committing the rendered `.pptx` (vs. committing only a digest sidecar) is what Phase 4 intends | Pitfall 1 | Medium — ROADMAP Phase 4 says "committed == fresh double-render … including the `.pptx`", which reads as a committed binary. If instead only a digest is committed, Pitfall 1 evaporates. Worth an explicit sentence in Phase 1's recorded decision |
| A7 | A floor pin `python-pptx>=1.0.2` will not trip `test_pptx_extra_declared` | Pitfall 4 | Low — the test compares `_req_name(r)` values, which strip specifiers, but this was reasoned from the test source, not executed |
| A8 | Normalized decks open correctly in real PowerPoint | Pattern 1 / Environment | **Medium-high** — could not be verified here (no Impress filter, no PowerPoint). All available integrity checks pass (`unzip -t`, `testzip()`, python-pptx reopen). **The planner must gate this behind a human-verify checkpoint in Phase 2** |

## Open Questions

1. **Where does the Weekly Spec schema live — a new `docs/weekly-spec.md`, or a §Weekly Spec inside `docs/case-spec.md`?**
   - What we know: `docs/case-spec.md` is 70 lines and tightly scoped to one schema; ROADMAP SC-1 says "a Weekly Spec section (extending the `docs/case-spec.md` mechanism)"; `docs/weekly.md` is already reserved by WKLY-06 for the *operator recipe* (a different document).
   - What's unclear: whether "section" means literally inside `case-spec.md`.
   - **Recommendation:** a **new `docs/weekly-spec.md`**, with a one-line pointer from `docs/case-spec.md` ("the Weekly Spec extends this mechanism — see …") and a link from `docs/architecture.md` §1. Keeps each document hand-authorable-from-alone, which SC-1 explicitly demands, and keeps `docs/weekly.md` free for the Phase 4 recipe.

2. **One slide per lane, or one deck-shaped template the renderer fills?**
   - What we know: `add_slide` destroys operator names (E9), there is no slide copy or delete API (E10), and a name-restore helper works (Pattern 2b).
   - What's unclear: the actual shape of the weekly deck — nobody has shown one.
   - **Recommendation:** specify **Pattern 2a (fill existing template slides)** as the contract and note Pattern 2b as the sanctioned escape hatch with its exact helper. This makes the operator's Selection-Pane naming the single source of layout truth, which is the most literal reading of "the renderer never invents layout".

3. **Does the committed==fresh gate compare a committed `.pptx` binary, or a committed digest?**
   - What we know: Pitfall 1 makes full-byte equality across environments zlib-dependent; the part-content digest is not.
   - What's unclear: Phase 4's intent (see A6).
   - **Recommendation:** commit the `.pptx` **and** assert the part-content digest against it. That satisfies "committed == fresh" honestly, is immune to zlib/zlib-ng, and still catches every real regression. Say so in the recorded decision so Phase 4 doesn't have to re-litigate it.

4. **Should the marker also record *which* Surface produced the deck (id / content hash)?**
   - What we know: `cp:category` is a single string; `Provenance` and `Lineage` already exist on `Surface` and are unused by the deck.
   - What's unclear: whether a deck found on someone's desktop should be traceable back to its Surface.
   - **Recommendation:** yes, and it is nearly free — put the Surface id in `cp:identifier`
     (`dc:identifier`, documented as "an unambiguous reference to the resource within a given
     context"). Costs nothing, round-trips, and makes the deck self-locating. Record it as part of
     the marker decision or explicitly defer it.

5. **What visual token vocabulary do the four new blocks use in HTML (Phase 3)?**
   - What we know: `docs/design-system.md` is a non-negotiable visual contract; `render.py` uses classes like `block`, `block-h`, `sg-kpi`, `sg-quote`, `chapter`, `item`, `diagram`.
   - What's unclear: whether `TeamBlock`/`RecognitionsBlock` reuse `item`/`chapter` structures or need new ones.
   - **Recommendation:** Phase 1's spec should name the reused classes per block (e.g. Recognitions → the `item` row shape; Team → a `chapter`-style two-column row; Asset → the `diagram` `<figure>`/`<figcaption>` shape) so Phase 3 has no visual discretion. Cheap to decide now; expensive to argue about mid-implementation.

## Sources

### Primary (HIGH confidence — measured in this session)

- **`python-pptx` 1.0.2 installed source**, read directly:
  `pptx/opc/serialized.py` (`PackageWriter`, `_ZipPkgWriter.write`, `_zipf`),
  `pptx/opc/package.py` (`iter_parts`, `iter_rels`, `_Relationships.xml`, `_next_rId`, `_xml_rels`),
  `pptx/shapes/shapetree.py` (`clone_placeholder`, `_next_ph_name`),
  `pptx/oxml/shapes/autoshape.py` (`new_placeholder_sp`),
  `pptx/oxml/__init__.py` (`oxml_parser`).
- **Nine executed spikes** (double-write same-second and time-separated, zip metadata diffing,
  normalization variants, cross-process `PYTHONHASHSEED`, images + media dedup, watermark
  mechanics, layout-name propagation, multi-slide determinism, core-properties round-trip) —
  results tabulated in §Determinism Spike — Measured Results (E1–E16).
- **This repository, read directly:** `src/newsletters/semantic.py`, `templates.py`, `casespec.py`,
  `render.py` (dispatch, line 620 `return ""`), `locators.py`, `_yaml_loader.py`,
  `adapters/_timestamps.py`, `adapters/_pptx_loader.py`, `pyproject.toml`, `.importlinter`,
  `.github/workflows/ci.yml`, `tests/test_ai_optional.py`, `tests/test_modulesite.py`,
  `docs/architecture.md`, `docs/case-spec.md`, `.planning/{ROADMAP,REQUIREMENTS,STATE,config}`,
  `.planning/seeds/v1.3-weekly-one-shot.md`, `.planning/phases/01-specify-de-risk/01-CONTEXT.md`.
- `gsd-tools query package-legitimacy check --ecosystem pypi python-pptx`;
  `pip index versions python-pptx` (LATEST 1.0.2).

### Secondary (MEDIUM confidence)

- python-pptx API documentation — `CoreProperties` attribute list and `Presentation.save()`
  signature. [CITED: https://python-pptx.readthedocs.io/en/latest/api/presentation.html] —
  cross-checked against the installed library's actual behaviour (E14), so the attribute claims are
  effectively verified.

### Tertiary (LOW confidence — web only, flagged)

- Reproducible-builds guidance on archive metadata and the zlib/zlib-ng DEFLATE divergence.
  [CITED: https://lists.reproducible-builds.org/pipermail/rb-general/2024-September/003547.html]
  [CITED: https://reproducible-builds.org/docs/archives/]
  [CITED: https://github.com/drivendataorg/repro-zipfile]
  Not reproduced in this environment (only one zlib available: 1.3). Treated as a **risk to design
  around** (Pitfall 1), not as a proven failure in this repo.

## Metadata

**Confidence breakdown:**

- **Determinism mechanism:** HIGH — nine spikes against the exact library version; the single
  non-determinism source was located in the library source and confirmed by measurement; the fix
  was measured stable across time, processes, and hash seeds.
- **python-pptx API mechanics** (names, placeholders, markers, images, watermark): HIGH — every
  claim was executed, not recalled; the two most surprising findings (`add_slide` name
  regeneration, duplicate names allowed) came from an assertion actually failing.
- **Standard stack:** HIGH — no new dependency; the one package was version-verified on PyPI and
  run through the legitimacy seam.
- **Existing-repo constraints** (Case Spec mechanism, `Block` union, `render.py` fall-through,
  guards, gates): HIGH — read from the live files on this branch.
- **Cross-environment byte-stability risk:** MEDIUM — the mechanism is documented by
  reproducible-builds but was not reproduced here (single zlib available). Design-around
  recommended rather than asserted.
- **PowerPoint compatibility of the normalized deck:** MEDIUM-LOW — all available integrity checks
  pass, but no real `.pptx` consumer exists in this environment. **Flagged for human verify.**
- **Schema/field-name recommendations:** MEDIUM — these are Claude's discretion by design; the
  reasoning is grounded in the existing Case Spec contract, but they are choices, not findings.

**Research date:** 2026-08-29
**Valid until:** 2026-09-28 (30 days — python-pptx is stable, last release 2024-08-07; re-verify
if `python-pptx` publishes a new minor, or if the repo's Python or zlib changes)
