---
title: "`.pptx` determinism, the generated-by marker, and the template contract: recorded decisions"
date: 2026-08-29
context: "v1.3 Phase 1 (Specify + de-risk) — the evidence-first decision gating WKLY-01"
status: decided
---

# `.pptx` determinism, the generated-by marker, and the template contract

This is the document the Phase 2 implementer reads. It is deliberately *not* a research summary:
`01-RESEARCH.md` records what was learned, this note records what was **decided**, with the reason
and the assertion that re-proves each decision. If Phase 2, 3 or 4 finds itself reopening
`01-RESEARCH.md` to settle a question, that is a bug in this note.

## The question

Phase 2 cannot start until three things stop being open:

1. **Is a `.pptx` byte-stable across renders?** ROADMAP Phase 1 criterion 2 allows two recorded
   outcomes — byte-stable, or content-stable (unzipped parts byte-identical under normalized zip
   metadata). Exactly ONE must be recorded, with committed evidence, before any renderer work.
2. **Where does the generated-by marker live** — OPC core properties or a notes slide — and how is
   it asserted by *reading a written file back* (ROADMAP Phase 1 criterion 3, Phase 2 criterion 3)?
3. **How does the renderer bind Surface content to an operator's template** without inventing
   layout (the Editor-in-Chief's locked decision **D-03**: named placeholders, fail loud)?

## The hinge

The whole determinism question came down to one line of somebody else's library.

`_ZipPkgWriter.write()` calls `self._zipf.writestr(pack_uri.membername, blob)` — it passes a
**`str`** arcname (`pptx/opc/serialized.py:234-242`). When `zipfile` is handed a string instead of
a `ZipInfo`, it manufactures the `ZipInfo` itself and stamps `date_time=time.localtime()[:6]`.
There is no python-pptx API to override that.

Everything else `Presentation.save()` does is already deterministic **by construction**, which is
the surprising and load-bearing half of the finding:

- part traversal is a DFS over insertion-ordered `dict`s (`visited` sets are membership-only, never
  iterated),
- `_Relationships.xml` serializes rels **sorted numerically by rId**, and `_next_rId` returns the
  first free `rIdN`,
- media parts are **content-deduplicated** and numbered in add order,
- core properties are **never auto-bumped on save** (the stock template's 2013 `created`/`modified`
  survived two saves untouched).

So the deck's *content* never moves. Only the container's clock does.

**The false-green trap, stated so nobody re-falls into it:** two writes inside a single wall-clock
second are **already byte-identical**. DOS timestamps in a ZIP have 2-second granularity. A spike
that rendered twice in a tight loop would have "proved" a byte-stability that does not exist, and
this note would have recorded a decision built on luck. The measurement therefore sleeps **3
seconds** between the two writes, and that sleep is load-bearing, not incidental.

## Decision

> **BYTE-STABLE, via a declared post-save zip normalization.** `Presentation.save()` into a
> `BytesIO`; rewrite every archive entry with `date_time=(1980,1,1,0,0,0)`, `create_system=0`,
> `compress_type=ZIP_DEFLATED`, each entry's `external_attr` preserved and the **emitted entry
> order** preserved; then one atomic write to disk. Part bytes are never touched — no XML is
> reformatted, no whitespace normalized, no attribute reordered.
> **Scoped, in writing, to a fixed (python-pptx, zlib) pair.** DEFLATE output is
> implementation-dependent, so the committed==fresh gate asserts the **part-content digest** —
> sha256 over sorted `(part name, sha256(part bytes))` — which is implementation-independent and
> strictly stronger than "the zips look the same". Neither assertion normalizes XML.

The stronger of the two allowed outcomes is recorded because the measurement supports it. The
scope sentence is not a hedge on the outcome; it is the boundary the outcome must not be carried
across.

### The measured evidence

Cited from `.planning/notes/2026-08-29-pptx-determinism-evidence.json` (committed by plan 01-01,
produced by a real double write 3 seconds apart, and re-verifiable with `--check`). These numbers
are **not** re-measured here:

| Key | Value | What it means |
|-----|-------|---------------|
| `raw_bytes_equal` | `false` | the negative control fired — un-normalized output across a time boundary really does differ |
| `varying_parts` | `[]` | every unzipped part was byte-identical: the deck's content is deterministic |
| `varying_zip_fields` | `["date_time"]` | the single non-determinism, exactly where the hinge predicted |
| `normalized_bytes_equal` | `true` | the recorded outcome |
| `part_digest_a` | `606c24642c74bed9a3514f053489067b7479a12b2212738338066c1cc2822ab9` | content identity, run A |
| `part_digest_b` | `606c24642c74bed9a3514f053489067b7479a12b2212738338066c1cc2822ab9` | identical to A — this is the cross-environment assertion |
| `python_pptx` | `1.0.2` | the exercised version — part of the claim's scope |
| `zlib` | `1.3` | the exercised zlib — the other half of the scope |
| `seconds_between_writes` | `3` | crosses the 2-second DOS boundary |

`raw_a_sha256` (`68eaa4d4…`) `!= raw_b_sha256` (`1d0d0eae…`) while
`normalized_a_sha256 == normalized_b_sha256` (`56fa2a61…`). That pair of facts *is* the finding.
The raw and normalized file hashes are recorded as evidence of what this machine measured; they
are **never** asserted across environments.

The module that re-proves all of this on every test run is **`tests/test_pptx_determinism.py`**.
Assertion **C** (the negative control) is what makes the green in **B** attributable to the
normalizer rather than to two writes landing in the same second.

## The three assertions Phases 2 and 4 inherit

| | Assertion | Where it runs | The failure it catches |
|---|-----------|---------------|------------------------|
| **A** | `part_digest(committed) == part_digest(fresh)` | Phase 4's committed==fresh gate | a real content regression, across machines and zlib implementations |
| **B** | `render(surface) == render(surface)` (full bytes, after normalization) | Phase 2's in-process double render | a clock, an unstable part order, or an unstable rel id leaking into the writer |
| **C** | an **un-normalized** double write across a time boundary is **NOT** byte-equal | Phase 2 / the spike test | a test that passes for the wrong reason — without C, B is green whenever both writes land in one second |

**The diagnostic signature to recognize (Pitfall 1):** identical part contents plus a different
file hash is a **zlib divergence, not a regression**. If assertion A is green and a full-file hash
comparison is red, the answer is that somebody asserted the wrong thing — not that the renderer
broke. This sentence exists so that failure costs a minute rather than an afternoon.

## The generated-by marker: OPC core properties, NOT a notes slide

| What | python-pptx attribute | OPC element | Value |
|------|----------------------|-------------|-------|
| generated-by marker | `core_properties.category` | `cp:category` | `"generated-by:newsletters"` |
| review-gate state | `core_properties.content_status` | `cp:contentStatus` | `"draft"` while `surface.review.state is not PUBLISHED` |
| determinism | `core_properties.created` / `.modified` | `dcterms:created` / `dcterms:modified` | `EPOCH_ZERO` (never a second epoch constant) |
| which Surface produced it | `core_properties.identifier` | `cp:identifier` | the Surface id (open question **Q4**) |

**Why core properties, not the notes slide.** Measured: writing a notes slide adds **four** parts
(`ppt/notesSlides/notesSlide1.xml` + its rels, `ppt/notesMasters/notesMaster1.xml` + its rels) to a
deck that had none. That is a structural mutation of every deck we touch, it is reader-visible in
presenter view, and an operator deletes it by accident. Core properties add **zero** parts, survive
a PowerPoint save round-trip, and a human can read them in File → Info with no tooling.

**Why not `dc:description` / `comments`.** It is free prose an operator may legitimately have
authored in their template, and the stock python-pptx template already writes
`"generated using python-pptx"` there. Overwriting it is the deck-level version of editorializing —
the same instinct the product forbids in the composer. `cp:category` is a purpose-built
classification slot; `cp:contentStatus` is documented as "completion status of the document, e.g.
'draft'", which is precisely the semantic the gate needs, and it keeps gate state out of prose.

**`cp:identifier` carries the Surface id** because it is nearly free, it round-trips, and it makes
a deck found on somebody's desktop self-locating: you can get from the file back to the reviewed
record it came from.

**Honest limit (accepted, not mitigated):** `cp:category` is operator-editable. The marker is
**provenance, not an authenticity control**. Nobody may later treat an unmarked deck as proof that
it was not generated, or a marked one as proof that it was.

### The stated read-back assertion

Phase 2 copies this verbatim. It reopens the **written file** — never the writer's return value:

```python
written = Presentation(str(out_path))          # reopen the FILE that was written
cp = written.core_properties
assert cp.category == "generated-by:newsletters", cp.category
assert cp.content_status == ("draft" if not surface.is_published else ""), cp.content_status
assert cp.created == EPOCH_ZERO.replace(tzinfo=None)   # dcterms reads back tz-NAIVE (Pitfall 5)
assert cp.identifier == surface.id, cp.identifier
assert any(sh.name == "NL_DRAFT_WATERMARK" for s in written.slides for sh in s.shapes)
```

The `replace(tzinfo=None)` is written here so Phase 2 copies it instead of rediscovering it:
`dcterms:created` serializes as W3CDTF `1970-01-01T00:00:00Z` but python-pptx reads it back
**tz-naive**, while the repo's `EPOCH_ZERO` is tz-aware UTC. A plain `==` fails. This is the same
class of mismatch `deterministic_timestamp()` already absorbs for openpyxl.

## The template contract: fill existing template slides, NOT `add_slide`

**Decision: the renderer fills shapes on slides that already exist in the operator's template. It
adds no slides.** The operator names shapes in PowerPoint's Selection Pane (`Alt+F10`); those names
are the single source of layout truth.

**The load-bearing reason.** `slides.add_slide(layout)` calls `clone_placeholder`, which computes
`name = self._next_ph_name(ph_type, id_, orient)` and injects it into a freshly parsed `<p:cNvPr>`.
The layout's placeholder name is **never copied**. Measured: a layout whose placeholders were named
`WEEKLY_LANE_TITLE` / `WEEKLY_LANE_BODY` produced a slide with `Title 1` / `Content Placeholder 2`.
A named-placeholder contract built on `add_slide` would therefore reject every one of the
operator's names on first contact with a real template — or, worse, fall back to position and
quietly fill the wrong boxes.

**The sanctioned escape hatch**, recorded so a variable-slide-count design has one blessed route
and does not invent one: `add_slide(layout)` followed immediately by restoring the layout's names
by `placeholder_format.idx`.

```python
def add_named_slide(prs, layout):
    """add_slide + restore the LAYOUT's placeholder names (python-pptx regenerates them)."""
    slide = prs.slides.add_slide(layout)
    layout_names = {p.placeholder_format.idx: p.name for p in layout.placeholders}
    for ph in slide.placeholders:
        if ph.placeholder_format.idx in layout_names:
            ph.name = layout_names[ph.placeholder_format.idx]
    return slide
```

(There is no slide copy/duplicate/delete API in python-pptx — `Slides` exposes only
`add_slide / element / get / index / parent / part` — so hand-rolled slide cloning is not an
option, and is a well-known source of corrupt decks anyway.)

**The `NL_` reserved prefix — decided, with its reason.** Only shapes whose name starts with `NL_`
are renderer slots. Without the prefix, direction (b) of the fail-loud contract ("a template shape
with no Surface content fails loud") rejects every operator logo, footer and page number, which
makes **D-03** unusable on any real deck. This is `01-RESEARCH` assumption **A4**, held at *medium*
confidence because no real operator deck was available to test against; it is flagged for
confirmation at the Phase 2 human-verify checkpoint.

**Duplicate shape names are LEGAL in OOXML** — python-pptx will happily write two shapes with the
same name, and copy-pasting a box in PowerPoint is how an operator creates one. A naive
`{sh.name: sh}` comprehension is last-wins, which silently drops a slot: exactly the failure the
fail-loud contract exists to prevent. **The binding map must raise on collision**, naming the
duplicated name and telling the operator to rename one in the Selection Pane.

**Bind over `slide.shapes`, not `slide.placeholders`.** The latter contains only real placeholders
keyed by `idx`; operator-added textboxes and pictures are absent from it (measured: 3 shapes, 2
placeholders).

**Testable consequence.** Phase 2 ships **two failing-direction tests**: Surface content bound to a
placeholder name the template does not contain, and an `NL_`-prefixed template slot with no
matching Surface content. Each must raise a teaching error that **names the offending placeholder**
and lists the names the template does contain.

## The Draft watermark

One textbox per slide, named `NL_DRAFT_WATERMARK`, added **last** so it sits at the top of
z-order: `rotation=315.0`, `Pt(96)`, bold, `RGBColor(0xD0, 0xD0, 0xD0)`, text `"DRAFT"`. Every
property is a fixed literal — no clock, no randomness — so the watermark contributes nothing to
non-determinism (confirmed: builds with the watermark were part-identical across time-separated
runs).

**Not true transparency.** python-pptx has no alpha/transparency API; a genuinely see-through
watermark needs raw `a:alpha` XML. A light-grey rotated run is visible, deterministic and
API-supported, and is not worth trading for that fragility. Recorded as the choice with its reason
so Phase 2 does not rediscover it.

**Not "an element in the operator's template, toggled off when published".** Removing a shape needs
the undocumented `el.getparent().remove(el)` lxml idiom, and the element would have to exist in the
operator's template — which makes correct gate behaviour depend on operator template content.
Adding is unconditional and testable.

## The three milestone decisions, with their testable consequence

**D-01 — the weekly reuses `Surface(REPORT)`.** The PPTX renderer is an *output format*, not a new
semantic kind. No new `Surface` kind, no `semantic.py` change.
*Consequence:* `git diff --exit-code -- src/newsletters/semantic.py` stays empty through Phases 2-4,
and the writer **reads** `surface.review.state` to choose the watermark and the `cp:contentStatus`
value and **never writes it**. There is no read-then-fix path, and therefore no auto-publish path.

**D-02 — asset provenance minimum = folder + date + event label**, with the deep link **REQUIRED**
iff the asset stands in for values (a BI screenshot, WKLY-04). No provenance → `missing[]`, shown
to the reviewer, never placed silently.
*Consequence:* the exact `missing[]` routing table, specified by **field name** in the new
`docs/weekly-spec.md` (plan 01-03), and `AssetBlock.asset` typed as **required** so a
provenance-less placement is *unrepresentable* rather than merely policed — the same move
`GlossaryTerm.definition: Claim` already makes in this codebase.

**D-03 — named placeholders, fail loud** on missing *and* unknown names; the renderer never invents
layout.
*Consequence:* the two failing-direction tests above, plus the duplicate-name raise, plus the `NL_`
prefix that makes the contract survive contact with a real deck.

## Other decisions

- **Q1 — where the schema lives:** a **new `docs/weekly-spec.md`**, with a one-line pointer from
  `docs/case-spec.md` ("the Weekly Spec extends this mechanism — see …") and a link from
  `docs/architecture.md` §1. Reason: ROADMAP SC-1 demands a document a reader can hand-author a
  valid spec from *alone*; folding it into the 70-line `case-spec.md` breaks that for both.
  `docs/weekly.md` stays reserved for the WKLY-06 operator recipe (Phase 4) — a different document
  for a different reader.
- **Q2 — one slide per lane, or one template the renderer fills:** answered above. Pattern 2a
  (fill existing template slides) is the contract; Pattern 2b (`add_slide` + name restore) is the
  sanctioned escape hatch.
- **Q3 — what the committed==fresh gate compares:** Phase 4 commits the `.pptx` **binary** *and*
  asserts the **part-content digest** against it. Full-file equality is never asserted across
  environments. This closes assumption A6; Phase 4 does not re-litigate it.
- **Q4 — should the marker record which Surface produced the deck:** yes. `cp:identifier` carries
  the Surface id.
- **Q5 — visual token vocabulary for the four new blocks:** `docs/weekly-spec.md` names the
  existing design-system classes each new block reuses, so Phase 3 has **no visual discretion**.
- **The Weekly Spec is a sibling loader (`weeklyspec.py`), not a widened `casespec._KNOWN_KEYS`.**
  Widening the Case Spec's exactly-eight-key tuple would make a Case Spec silently accept weekly
  fields and a Weekly Spec silently accept case fields — destroying the strict-schema guarantee in
  *both* directions. The **mechanism** is reused verbatim (`_yaml_loader.load_config` → `safe_load`
  only, `read_text` normalization, `Trace.from_source`, the `_SpanMinter` forward-only cursor, root
  containment, `config:` bound but never claimed); the *schema* is not.
- **ONE normalizer contract, two call sites.** `tests/fixtures/weekly/_determinism.normalize_opc_zip`
  is **canonical**; `tests/fixtures/pptx/_author_fixtures._normalize_zip` (the pre-existing ADAPT-06
  golden-corpus normalizer) is the same contract — rewrite every entry with a fixed `date_time`,
  preserve emitted entry order and `external_attr`, never touch part bytes — minus `create_system=0`
  and the explicit `compress_type`, plus a recursion that pins the chart fixture's embedded `.xlsx`
  core properties. Phase 2 moves the canonical one to `src/newsletters/_pptx_writer.py` behind the
  `[pptx]` extra, and `_author_fixtures._normalize_zip` delegates to it **then, not now**:
  delegating today would swap that file's `2026-01-01` entry constant for the canonical DOS epoch
  and rebuild all nine golden `.pptx` binaries — a corpus regeneration inside a spec phase. The
  argument for a single contract is the `EPOCH_ZERO` argument applied to normalizers: a second
  implementation of "make this deterministic" drifts from the first exactly as a second epoch
  sentinel would, and the drift is invisible until a gate that trusted both goes red.
- **Recommend a floor pin `python-pptx>=1.0.2` in Phase 2.** python-pptx makes no documented
  byte-output-stability promise across versions, and the `[pptx]` extra is currently unpinned.
  `tests/test_ai_optional.py::test_pptx_extra_declared` compares `_req_name(r)`, which strips
  version specifiers — so a pin *should* pass it, but that was reasoned from the test source, not
  executed (`01-RESEARCH` A7). Phase 2 **verifies rather than assumes**.
- **XXE is mitigated upstream.** python-pptx parses with
  `etree.XMLParser(remove_blank_text=True, resolve_entities=False)` (`pptx/oxml/__init__.py:21`).
  Phase 2 must not build a second XML parser without `resolve_entities=False`.
- **The normalizer never joins a path to the filesystem.** It reads with `ZipFile.read(name)` and
  writes with `ZipFile.writestr(ZipInfo, data)`, both in memory — no `open()`, no `Path` join, no
  `extract`. A malicious `../../etc/passwd` member in an operator-supplied template is carried
  through as an opaque *name string* and cannot reach disk. Zip-slip is closed by construction, not
  by validation.

## How it slots into the roadmap

- **Phase 2 (WKLY-01)** inherits the determinism definition, the marker fields and their read-back
  assertion, the template contract with its reserved prefix and duplicate-name rule, and the
  watermark shape — as **inputs**, not discoveries. `_determinism.py` moves to
  `src/newsletters/_pptx_writer.py` behind the `[pptx]` extra, mirroring the lazy-import discipline
  `adapters/_pptx_loader.py` already establishes.
- **Phase 3 (WKLY-02/03/04)** inherits the block and asset-record spec written in plan 01-03, and
  the `AssetBlock.asset`-is-required invariant.
- **Phase 4 (WKLY-05/06)** inherits **assertion A** for the committed==fresh gate.

**The one link that could NOT be verified in this environment.** No real `.pptx` consumer exists
here: `libreoffice-core` is installed without the Impress filters, so it cannot open *any* `.pptx`,
normalized or not. What *is* proven is that `ZipFile.testzip()` passes, `unzip -t` reports no
errors, `[Content_Types].xml` remains the first entry, and python-pptx reopens the normalized bytes
with shape names and core properties intact. "A normalized deck opens correctly in real PowerPoint"
remains **unproven** (`01-RESEARCH` A8) and is the **Phase 2 `checkpoint:human-verify`** — open one
normalized deck in real PowerPoint before the renderer is accepted.

## Truths checked (still honest)

- **No auto-publish, ever** — *preserved:* nothing in this decision touches `semantic.py`, and the
  writer is specified to **read** `surface.review.state` and never write it. `cp:contentStatus` is
  written *from* the gate state, not back into it; the read-back assertion reads the written FILE,
  so a writer that returned success without marking would be caught.
- **AI-optional core** — *preserved:* no column-0 `pptx` import under `src/`, `lint-imports`
  contracts stay KEPT, bare-install CI untouched. The writer shares the existing `[pptx]` extra;
  no new dependency enters this milestone.
- **Every published claim traces to evidence** — *extended:* this decision cites a **committed
  measurement** by path, with a `--check` mode that fails on drift, rather than restating
  remembered numbers. A decision without evidence is a vibe; so is a decision whose evidence ran
  once in a scratch shell.
- **Faithful, not suggestive** — *honored:* the marker is written to `cp:category`, a purpose-built
  classification slot, and never overwrites the operator's prose in `dc:description`. The
  fail-loud contract refuses to guess which slot content belongs in rather than filling by position.
- **Interactive until trusted** — *honored:* the one unverifiable link (a real PowerPoint open) is
  recorded as a human checkpoint in Phase 2, not quietly assumed away.
