# Phase 2: Renderer - Research

**Researched:** 2026-08-29
**Domain:** Deterministic template-driven `.pptx` writing (python-pptx 1.0.2 shape/text/media
mechanics), writer-module placement under the AI-optional-core discipline
**Confidence:** HIGH — every mechanical claim below was **executed** in this session against the
repo's own `.venv` (python-pptx 1.0.2, CPython 3.11.15, zlib 1.3) and the repo's own committed
`tests/fixtures/weekly/template.pptx`. Nothing here is recalled.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase 1's recorded decision note is BINDING input, not open questions:**
`.planning/notes/2026-08-29-pptx-determinism-decision.md` — read it first. It fixes:

1. **Determinism**: BYTE-STABLE via declared post-save OPC-zip normalization (fixed 1980
   date_time, create_system, compression pinned); scoped to the (python-pptx, zlib) pair;
   `part_digest` is the implementation-independent committed==fresh assertion; in-process
   double-render asserts full byte equality WITH a negative control.
2. **Marker**: OPC core properties — `cp:category` = generated-by marker, `cp:contentStatus` =
   "draft", `dcterms:created/modified` = EPOCH_ZERO, `cp:identifier` = Surface id — asserted by
   reading the WRITTEN file back (tz-naive comparison gotcha handled). Provenance, not
   authenticity.
3. **Template contract**: fill the operator's EXISTING slides — never `add_slide` (it
   regenerates placeholder names); `NL_` reserved shape-name prefix; duplicate `NL_` names
   raise; missing/unknown names fail loud in BOTH directions with teaching errors;
   `NL_DRAFT_WATERMARK` is the watermark slot shape.
4. Milestone decisions D-01/D-02/D-03 (reuse REPORT; provenance minimum; named placeholders).

**Deferred-to-here from Phase 1 fixes (scheduled work, do not drop):**
- IN-02 second half: pin `create_system` in the normalizer promotion (the writer-side normalizer
  is promoted to `src/newsletters/` — e.g. `_pptx_writer.py` — the fixture normalizer delegates
  or is superseded per the decision note's one-contract rule).
- IN-03/IN-04: the promotion to `src/` resolves the fixture import-mechanism collision; consider
  consolidating `_FIXED` on EPOCH_ZERO only if it does not require regenerating golden binaries
  in this phase without cause.

**Remaining choices are Claude's discretion**, decided per the recorded reasoning
(evidence-first, smallest change, fail-loud) and logged.

### Claude's Discretion

Everything not fixed by the decision note above: writer module name and placement, the public
function signature, the text-fill primitive, group/nesting handling, the CI wiring, and the
disposition of IN-02/IN-03/IN-04.

### Deferred Ideas (OUT OF SCOPE)

None — scope locked by seed + roadmap; **Phase 3 owns the block kinds and composition.**
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **WKLY-01** | A composed weekly `Surface(REPORT)` renders deterministically to `.pptx` through an operator-supplied template deck: python-pptx stays behind the `[pptx]` extra (writer and loader share it), core spine untouched, bare-install CI green. The determinism gate extends to `.pptx`. Every deck carries the generated-by marker in a durable field and renders visibly Draft-watermarked until the Surface is Published (the gate itself untouched). | §Pattern 1 (module placement + lazy boundary reuse) · §Pattern 2 (the binding map, incl. **group recursion**, W17) · §Pattern 3 (**the clone-paragraph fill primitive**, W3–W6) · §Pattern 4 (watermark add/refuse, W12–W14) · §Pattern 5 (images, W15–W16, W18) · §Pattern 6 (normalizer promotion) · §Validation Architecture (the five assertions + the CI gap W21) |

Mapping to ROADMAP Phase 2's five success criteria:

| SC | Where this research answers it |
|----|-------------------------------|
| SC-1 fail-loud both directions | §Pattern 2 + Pitfalls 4/5 (the two *silent-drop* holes Phase 1 did not see: group nesting, non-text shapes) |
| SC-2 double render equal | §Pattern 6 + W-series (every writer operation measured deterministic across a 3-second gap) |
| SC-3 marker + watermark, read back | §Pattern 4, §Code Examples, W12/W20/W22 |
| SC-4 no auto-publish, `semantic.py` byte-unchanged | §Pattern 7 (the writer reads `review.state`, never writes) + §Validation Architecture |
| SC-5 lazy import, bare-install CI green, sample renders **in CI** | §Pattern 1 + **W21: no CI job installs `[pptx]` today — every pptx test is silently skipped in CI** |
</phase_requirements>

## Summary

Phase 1 settled the *container* (zip normalization, marker fields, "fill existing slides, never
`add_slide`"). What it did **not** measure is the part Phase 2 actually spends its code on: how you
put text and pictures into somebody else's shapes without destroying their formatting, and what
happens on the round trip. Nine new experiments answer that, and three of the answers change the
plan.

**First: the obvious fill API is the wrong one.** `text_frame.text = "..."` — the line the Phase 1
spike used, and the line every tutorial uses — **discards the operator's formatting**. Measured on a
box authored at 20pt bold with a `buChar` bullet: after `tf.text = "filled"` the run's font size
reads `None` and the bullet is gone (W3). `tf.clear()` is only half-safe: it keeps paragraph 0's
`pPr` (the bullet survives) but drops every run, and `add_paragraph()` returns a paragraph with no
`pPr` at all, so lines 2..n lose the level and the bullet (W4). The primitive that works — and the
one the plan should specify — is **reuse-and-clone**: keep paragraph 0's existing run as the
formatting carrier, set its `.text`, and `copy.deepcopy` the whole `<a:p>` for each additional line.
Measured: 18pt survives on all three lines, the bullet survives on all three, it round-trips through
a real write, and it is byte-identical across a 3-second gap (W5). python-pptx has **no bullet API**
at all (W6) — bullets can only be inherited, never synthesized, which makes this primitive the only
route to a bulleted highlights list that respects the operator's template.

**Second: the fail-loud contract has two silent-drop holes Phase 1's fixture cannot see.**
`slide.shapes` is **top-level only** — an `NL_`-named shape nested inside a group is invisible to a
`{sh.name: sh}` comprehension, so operator content bound to it is dropped with no error and the
unfilled-slot check never fires (W17). And a group shape (or a picture) has `has_text_frame ==
False`, so a naive `by_name[n].text_frame.text = ...` raises `AttributeError`, not a teaching error.
The binding map must **walk groups recursively** and the fill must check `has_text_frame` and raise
by name. This is exactly the failure class D-03 exists to prevent, and the current fixture template
(five flat textboxes) would never catch it.

**Third: open→save is not a fixed point, and part order is not template order.** Opening the
committed `template.pptx` and saving it unchanged produces a package whose `docProps/core.xml`
**differs** — the fixture's empty core properties were written as `<cp:keywords></cp:keywords>` and
come back as `<cp:keywords/>` (W1) — and whose part *emission order* moves `docProps/core.xml` from
index 2 to index 36 (W2), even though `_rels/.rels` is byte-identical. Neither is a
non-determinism: two independent open→saves 3 s apart are byte-equal after normalization and share a
`part_digest`. But it means **no assertion may compare a rendered deck's bytes, digest, or part
order against the template's**, and Phase 4's committed golden deck must be produced by the writer
itself, never by re-saving the template.

Everything else measured clean and deterministic across a 3-second gap: the watermark add (W12),
shape removal via the lxml idiom — which is not only deterministic but *exactly reversible* at the
part-content level (W13), image placement with content dedup and add-order numbering (W15),
`PicturePlaceholder.insert_picture()` **preserving** an operator-set name where `add_slide` destroys
it (W16), Unicode including emoji and XML metacharacters (W11), and an end-to-end miniature writer
(fill + watermark + marker + normalize) rendering byte-identically twice, three seconds apart, with
every read-back assertion green (F-series). Two open assumptions were closed by execution: the
`python-pptx>=1.0.2` floor pin **does** pass `test_pptx_extra_declared` (W19, closes A7), and
`core_properties.identifier` serializes as `dc:identifier`, not `cp:identifier` (W20 — a wording
correction for the decision note).

One gap is procedural, not technical, and it is the largest single risk to SC-5: **no CI job
installs the `[pptx]` extra**, so `test_pptx_determinism.py`, `test_pptx_golden.py`,
`test_pptx_adapter.py` and `test_pptx_loader.py` are all `importorskip`-skipped in CI today (W21).
"A sample Surface renders through it in CI" cannot be true until a job installs `.[test,pptx]`.

**Primary recommendation:** ship `src/newsletters/pptx_writer.py` — stdlib normalizer at module
level (bare-importable), python-pptx obtained lazily through the **existing**
`adapters._pptx_loader._load_pptx()` (one lazy boundary, two call sites, exactly the argument the
decision note made for normalizers) — exposing `render_surface_pptx_bytes(surface, *, template,
slots)` and a thin `render_surface_pptx(...)` that does one `Path.write_bytes`; bind over a
**group-recursive** name map that raises on duplicates, non-text slots, and both fail-loud
directions; fill with the **reuse-and-clone paragraph primitive**; add the watermark when
`not surface.is_published` and **refuse a template that already defines `NL_DRAFT_WATERMARK`**; and
add a `pptx` CI job so the sample render actually runs.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deck byte production (open template → fill → save) | `src/newsletters/pptx_writer.py` behind `[pptx]` | `adapters/_pptx_loader._load_pptx()` | The lazy boundary already exists and is already guarded by `tests/test_ai_optional.py`; a second boundary is a second contract that can drift |
| Zip determinism (normalize, digest, diff) | `pptx_writer.py`, **stdlib-only, module level** | — | Must stay importable on a bare install so the duplicate-member refusal and idempotence are testable without the extra (today they are not — W21) |
| Template slot binding + fail-loud | `pptx_writer.py` | operator's `.pptx` (Selection-Pane names are the layout truth) | D-03: the renderer never invents layout; the operator's names are the contract |
| Which Surface content goes in which slot | **the composer (Phase 3)** | `pptx_writer.py` accepts it as an explicit `slots` mapping | Only the composer knows the Weekly Spec's authored content; the writer owns the *deck*, not the editorial mapping. See Open Question 1 |
| Marker + gate state in the deck | OPC core properties via python-pptx | — | Phase 1 decision; zero extra parts, survives a PowerPoint round trip |
| Review gate | `semantic.py` — **untouched, byte-for-byte** | — | Hard rule. The writer *reads* `surface.review.state`; there is no write path |
| Draft watermark | `pptx_writer.py` (adds a named shape) | — | Adding is unconditional in mechanism, conditional on gate state; does not depend on operator template content |
| Image placement | `pptx_writer.py` (`add_picture` / `insert_picture`) | Phase 3's `AssetRecord` supplies path + provenance | Media naming/dedup is deterministic (W15); iteration order is the only variable and Phase 3 pins it to spec file order |
| Atomic-ish write to disk | `pathlib.Path.write_bytes` | — | Repo precedent (`publish.py`); one call with complete bytes, never a partially-normalized artifact |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `python-pptx` | **1.0.2** (latest; published 2024-08-07) | Open the operator template, bind shapes by name, fill text, place pictures, write core properties, save | Already the repo's `.pptx` dependency on the loader side (ADAPT-04); the writer **shares the existing `[pptx]` extra — no new dependency this milestone** [VERIFIED: `pyproject.toml` `pptx = ["python-pptx"]`; `.venv/bin/pip index versions python-pptx` → `python-pptx (1.0.2)`, run 2026-08-29] |
| `zipfile` (stdlib) | Python 3.11/3.12 | Post-save OPC normalization + part digest | Already the Phase 1 mechanism (`tests/fixtures/weekly/_determinism.py`); no new dependency, no core→extra edge |
| `hashlib` (stdlib) | 3.11/3.12 | `part_digest` rows | The repo's content-address primitive (`Source.content_hash`) |
| `copy` (stdlib) | 3.11/3.12 | `deepcopy` of `<a:p>` in the formatting-preserving fill primitive | The only way to clone paragraph formatting — python-pptx exposes no API for it (W6) |
| `lxml` | transitive of python-pptx | The element access the fill/remove primitives need (`p._p`, `sh._element`) | Never imported directly; stays behind the extra. python-pptx already parses with `resolve_entities=False` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `io.BytesIO` (stdlib) | 3.11/3.12 | `prs.save(BytesIO)` → normalize in memory → one `write_bytes` | Always. Never `prs.save(path)` then rewrite in place — a raised normalization leaves an un-normalized artifact on disk |
| `pathlib.Path` | 3.11/3.12 | The single disk write | `publish.py` precedent |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reuse-and-clone paragraph fill | `text_frame.text = "..."` | **Measured to destroy both run formatting (18pt → `None`) and paragraph formatting (bullet gone)** (W3). Correct only for a slot the writer fully owns — e.g. the watermark textbox it just created |
| Reuse-and-clone paragraph fill | `tf.clear()` + `add_paragraph()` | Keeps paragraph 0's `pPr`, loses every run's `rPr`, and gives lines 2..n no `pPr` at all (W4) — a half-preserved deck is worse than an obviously-wrong one |
| Reuse the existing `_load_pptx()` boundary | A second lazy import inside `pptx_writer.py` | Two implementations of "import the extra safely" drift exactly as two normalizers would. Reuse is the decision note's own one-contract argument |
| `Path.write_bytes` | tmpfile + `os.replace` | True POSIX atomicity is not what "one atomic write" in the decision note means (it means *one write of complete, already-normalized bytes*). `os.replace` is a reasonable hardening but is not repo precedent; call it out, don't smuggle it |
| Watermark **added** by the writer | Watermark toggled off in the operator's template | Measured: removal via `sh._element.getparent().remove(...)` IS deterministic and exactly reversible (W13) — so the *mechanism* objection in the decision note is now disproved. The remaining objection stands and is the binding one: a toggle makes correct gate behaviour depend on operator template content. **Keep adding.** |
| `add_picture` for team photos | `PicturePlaceholder.insert_picture()` | `insert_picture` **preserves** an operator-set placeholder name (W16) — unlike `add_slide`, which destroys names. Useful for Phase 3; not needed in Phase 2 |

**Installation:** No new install. The writer shares the existing extra:

```bash
pip install '.[pptx]'      # python-pptx — already declared; loader and writer share it
```

**Version verification:** `.venv/bin/pip index versions python-pptx` → `python-pptx (1.0.2)`;
available versions list confirms 1.0.2 is the newest. `.venv/bin/python -c "import pptx;
print(pptx.__version__)"` → `1.0.2`. [VERIFIED: PyPI index + installed module, run 2026-08-29]

**Floor pin — assumption A7 is now CLOSED by execution.** Importing the *real* `_req_name` from
`tests/test_ai_optional.py` and running it: `"python-pptx>=1.0.2"` → `"python-pptx"`, and
`"python-pptx>=1.0.2,<2.0"` → `"python-pptx"`. A floor pin therefore **passes**
`test_pptx_extra_declared` unchanged (W19). Phase 2 may add `python-pptx>=1.0.2` to the `[pptx]`
extra with no test edit. [VERIFIED: executed against the live test module]

## Package Legitimacy Audit

> **No package is added by this phase.** This is a re-verification of the one external package the
> writer uses, per protocol.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `python-pptx` 1.0.2 | PyPI | released 2024-08-07 (~2 yrs) | unknown (PyPI API returns `null`) | github.com/scanny/python-pptx | `SUS` (sole reason: `unknown-downloads`) | **Approved — pre-existing dependency, no new install, no new extra** |

**Packages removed due to `SLOP` verdict:** none.
**Packages flagged as suspicious `SUS`:** `python-pptx` — the only signal is `unknown-downloads`,
the known PyPI-API false positive already adjudicated in this repo's `pyproject.toml` comment for
the `[pptx]` extra and re-adjudicated in `01-RESEARCH`. `deprecated: false`, `postinstall: null`,
real source repo, MIT. **No `checkpoint:human-verify` is required for this package** because this
phase installs nothing new — but the planner must not silently add any other package (no
`python-pptx-interface`, no `pptx-templater`, no image-manipulation helper).

[VERIFIED: `gsd-tools query package-legitimacy check --ecosystem pypi python-pptx` → `verdict: SUS`,
`exists: true`, `repoUrl: https://github.com/scanny/python-pptx`, `deprecated: false`,
`postinstall: null`, run 2026-08-29]

## Architecture Patterns

### System Architecture Diagram

```
  Surface(REPORT, Draft)                 operator template.pptx
  ├ id            ──────────┐            (named shapes; NL_ = renderer slot)
  ├ review.state  ────┐     │                        │
  └ blocks             │     │                        │ Presentation(path)  [lazy _load_pptx()]
        │              │     │                        v
        │ (Phase 3)    │     │            ┌───────────────────────────┐
        v              │     │            │ BIND: group-RECURSIVE     │
  slots: {name -> lines}     │            │ {shape.name: shape}       │
        │              │     │            │  · duplicate name  -> RAISE
        └──────────────┼─────┼───────────>│  · content name not in map -> RAISE (direction a)
                       │     │            │  · NL_ slot not in content -> RAISE (direction b)
                       │     │            │  · slot has no text_frame  -> RAISE (W17)
                       │     │            │  · template defines NL_DRAFT_WATERMARK -> RAISE (W14)
                       │     │            └────────────┬──────────────┘
                       │     │                         │
                       │     │                         v
                       │     │            FILL: reuse paragraph 0's run as the
                       │     │            formatting carrier; deepcopy <a:p> per
                       │     │            extra line  (keeps rPr AND pPr — W5)
                       │     │                         │
      review.state ────┘     │        not PUBLISHED -> add NL_DRAFT_WATERMARK textbox
      (READ ONLY, never       │        (last => top of z-order; all literals — W12)
       written back)          │                        │
                              │                        v
                    surface.id│           core properties:
                              └──────────>  cp:category      = "generated-by:newsletters"
                                            cp:contentStatus = gate state
                                            dc:identifier    = surface.id      (W20)
                                            dcterms:created/modified = EPOCH_ZERO (tz-naive)
                                                         │
                                                         v
                                            prs.save(BytesIO)   <- the ONLY clock
                                                         │
                                                         v
                                            normalize_opc_zip(bytes)  [stdlib, in memory]
                                                         │
                        ┌────────────────────────────────┼────────────────────────────┐
                        v                                v                            v
              render() == render()            Path.write_bytes(once)          part_digest(bytes)
              (B: byte equality,              (never save-then-rewrite)       (A: committed==fresh,
               3s apart, with the                                              Phase 4, zlib-safe)
               C negative control)                       │
                                                         v
                                            REOPEN THE WRITTEN FILE and assert
                                            marker / gate / timestamps / shape names
                                            (never trust the writer's return value)
```

### Recommended Project Structure

```
src/newsletters/
├── pptx_writer.py          # NEW — the whole writer. NO column-0 `import pptx`.
│                           #   module level (STDLIB ONLY, bare-importable):
│                           #     DOS_EPOCH, normalize_opc_zip, part_digest,
│                           #     differing_parts, differing_zipinfo_fields   <- promoted from
│                           #     tests/fixtures/weekly/_determinism.py verbatim
│                           #     SLOT_PREFIX="NL_", WATERMARK_NAME, MARKER
│                           #   inside functions (lazy):
│                           #     from .adapters._pptx_loader import _load_pptx
│                           #     render_surface_pptx_bytes(...) -> bytes
│                           #     render_surface_pptx(...) -> Path
├── adapters/_pptx_loader.py   # UNCHANGED — the single lazy pptx boundary, reused
├── semantic.py                # UNCHANGED, byte-for-byte (git-diff gate)
└── render.py                  # UNCHANGED (HTML; Phase 3 touches it, not Phase 2)

tests/
├── test_pptx_writer.py        # NEW — the phase's proof (see §Validation Architecture)
├── test_pptx_determinism.py   # EDIT — import the normalizer from newsletters.pptx_writer;
│                              #        delete the sys.path.insert (closes IN-03)
└── fixtures/weekly/
    ├── _determinism.py        # DELETED (promoted) — or a 3-line re-export shim; prefer delete
    ├── _author_template.py    # EDIT — import from newsletters.pptx_writer; template gains
    │                          #        a group-nested slot + a non-text slot (see Wave 0)
    └── template.pptx          # REGENERATED (see IN-04 discussion — keep core props NON-epoch)

.github/workflows/ci.yml       # EDIT — a job that installs '.[test,pptx]' and runs the pptx
                               #        tests. Without it SC-5's "in CI" is not true (W21).
```

**Naming reconciliation (Claude's discretion, logged).** The decision note says `_determinism.py`
moves to `src/newsletters/_pptx_writer.py`; `01-RESEARCH`'s structure sketch says
`src/newsletters/pptx_writer.py`. They disagree only on the leading underscore. **Recommend
`pptx_writer.py` (no underscore)**, because this module carries the phase's *public* entry point
(`render_surface_pptx`) — `render.py`, `publish.py`, `casespec.py` are all public module names, and
`_pptx_loader.py` earns its underscore by being a boundary with no public surface. The note's
binding content — *the normalizer moves into `src/newsletters/` behind the `[pptx]` extra, mirroring
`adapters/_pptx_loader.py`'s lazy discipline* — is satisfied either way. If the planner prefers
literal compliance, `_pptx_writer.py` costs nothing but a less obvious import in Phase 3/4.

**Do NOT re-export from `src/newsletters/__init__.py`.** `__init__.py` eagerly imports `.render`,
`.capture`, `.problem`, `.site`, `.semantic`, `.templates`; `adapters` is deliberately absent.
Follow the `adapters` precedent: callers do `from newsletters.pptx_writer import
render_surface_pptx`. Adding it to `__init__` buys nothing and widens the bare-install blast radius
for zero benefit.

---

### Pattern 1: One lazy boundary, reused — not a second one

**What:** `pptx_writer.py` has no top-level `import pptx`. Inside the render function it calls the
loader's existing `_load_pptx()`.

**Why:** the decision note's own argument about normalizers applies verbatim to import boundaries —
"a second implementation of *make this safe* drifts from the first, and the drift is invisible until
a gate that trusted both goes red." `adapters/_pptx_loader._load_pptx()` already raises the teaching
`ImportError` naming `pip install '.[pptx]'`, is already exercised by
`test_pptx_loader_raises_teaching_error_without_pptx`, and `newsletters.adapters` is already proven
bare-importable by `test_adapters_package_imports_without_pptx`.

```python
# Source: src/newsletters/adapters/_pptx_loader.py (live, this branch)
def render_surface_pptx_bytes(surface, *, template, slots) -> bytes:
    from .adapters._pptx_loader import _load_pptx   # noqa: PLC0415 — lazy on purpose ([pptx] extra)

    pptx = _load_pptx()
    prs = pptx.Presentation(str(template))
    ...
```

**The guard this must satisfy**, copied from the existing pattern: a new test mirroring
`test_pptx_loader_has_no_toplevel_pptx_import` that reads `pptx_writer.py` and asserts **zero**
column-0 lines starting `import pptx` / `from pptx`. Indented (in-function) imports are invisible to
that check by design.

**The bare-install win.** Because `normalize_opc_zip` / `part_digest` sit at module level and touch
only `hashlib`, `io`, `zipfile`, `newsletters.pptx_writer` is importable **without** the extra. That
means the duplicate-member refusal, idempotence, and digest-collision tests can run on the bare CI
job — today they cannot, because they live behind `pytest.importorskip("pptx")` at module scope.

---

### Pattern 2: The binding map — group-recursive, and it refuses four kinds of ambiguity

**What:** build `{shape.name: shape}` over every slide, **descending into group shapes**, raising on
duplicates, then check both fail-loud directions and the shape's ability to hold text.

**The load-bearing new finding (W17):** `slide.shapes` yields **top-level shapes only**. Measured: a
slide with a group named `NL_GROUP` containing a textbox named `NL_INSIDE_GROUP`, plus a top-level
`NL_OUTSIDE`, reports `['NL_GROUP', 'NL_OUTSIDE']` — the inner slot is invisible. A contract that
promises "an `NL_` slot with no content fails loud" would say nothing at all about
`NL_INSIDE_GROUP`, and content bound to that name would be rejected as *unknown* even though the
operator can see the box in their Selection Pane. Grouping boxes is ordinary PowerPoint hygiene, so
this is not an exotic case.

**Second new finding:** a group shape has `has_text_frame == False` (measured). So does a picture.
`by_name[name].text_frame.text = ...` on such a shape raises `AttributeError` — a stack trace, not a
teaching error. The fill must check first.

```python
# Source: measured in this session (exp5/exp-group) against python-pptx 1.0.2
SLOT_PREFIX = "NL_"
WATERMARK_NAME = "NL_DRAFT_WATERMARK"


def _walk(shapes):
    """Every shape on a slide, DESCENDING into groups. `slide.shapes` is top-level only (W17)."""
    for shape in shapes:
        yield shape
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:   # from pptx.enum.shapes
            yield from _walk(shape.shapes)


def bind(prs, content: dict[str, list[str]]) -> dict[str, object]:
    by_name: dict[str, object] = {}
    for slide in prs.slides:
        for shape in _walk(slide.shapes):
            if shape.name in by_name:
                raise ValueError(
                    f"template has two shapes named {shape.name!r} — the name->shape binding is "
                    "ambiguous. Rename one in PowerPoint's Selection Pane (Alt+F10). Refusing to "
                    "guess which slot the content belongs in."
                )
            by_name[shape.name] = shape

    if WATERMARK_NAME in by_name:
        raise ValueError(
            f"the template already defines {WATERMARK_NAME!r}. That name is owned by the renderer, "
            "which adds the Draft watermark itself; leaving it in the template would produce two "
            "shapes with one name (measured: python-pptx writes both). Remove it from the template."
        )

    unknown = sorted(set(content) - set(by_name))
    if unknown:
        raise ValueError(
            f"Surface content is bound to placeholder name(s) {unknown!r} that this template does "
            f"not contain. Named shapes in this template: {sorted(by_name)!r}. The renderer never "
            "invents layout — add the shape to the template or fix the name."
        )

    unfilled = sorted(n for n in by_name if n.startswith(SLOT_PREFIX) and n not in content)
    if unfilled:
        raise ValueError(
            f"template placeholder(s) {unfilled!r} have no matching Surface content. A reserved-"
            "prefix slot left empty would ship a blank box to a reader — refusing. Either populate "
            "it or remove the NL_ prefix from the shape's name."
        )

    for name in content:
        shape = by_name[name]
        if not getattr(shape, "has_text_frame", False):
            raise ValueError(
                f"slot {name!r} is a {shape.shape_type} and cannot hold text (measured: group and "
                "picture shapes have has_text_frame == False). Point the slot at a text box, or "
                "place this content as an asset."
            )
    return by_name
```

**Why `slide.shapes` and not `slide.placeholders`** (Phase 1, still true): `placeholders` contains
only real placeholders keyed by `idx`; operator-added textboxes and pictures are absent entirely.

---

### Pattern 3: The fill primitive — reuse paragraph 0, clone it per extra line

**What:** never assign `text_frame.text`. Keep paragraph 0 and its first run as the *formatting
carriers*, write into that run, and `deepcopy` the whole `<a:p>` element for each additional line.

**The measurements that force this** (all on a box authored 20pt bold with a `buChar` bullet on
paragraph 0, level 1 on paragraph 1):

| Approach | paragraph props (`pPr` / bullet / level) | run props (`rPr` / size / bold) | paragraphs |
|----------|------------------------------------------|----------------------------------|-----------|
| `tf.text = "filled"` | **lost** (`bullet: None`) | **lost** (`size: None`, `bold: None`) | collapses to 1 |
| `tf.clear()` then `p.text=` / `add_paragraph()` | kept on p0 only; **lost** on every added paragraph | **lost** on all | as written |
| **reuse run 0 + `deepcopy(p0._p)`** | **kept on every line** (`bullet: buChar`) | **kept on every line** (`254000` = 20pt, `bold: True`) | as written |

Read back off the written file, the preserving variant reports
`[('one','254000',True), ('two','254000',True), ('three','254000',True)]` — the operator's
formatting survived a real save/reopen. Normalized bytes were identical across a 3-second gap.

```python
# Source: measured in this session (exp4 E3 / exp5 F) against python-pptx 1.0.2
import copy


def fill(text_frame, lines: list[str]) -> None:
    """Fill a template slot with N lines, PRESERVING the operator's paragraph and run formatting.

    python-pptx has no bullet API (measured: _Paragraph exposes only add_line_break, add_run,
    alignment, clear, font, level, line_spacing, runs, space_after, space_before, text), so a
    bullet can only be INHERITED. Paragraph 0 of the template slot is the formatting carrier;
    every additional line is a deep copy of it with its run's text replaced.
    """
    if not lines:
        raise ValueError("refusing to fill a slot with no lines — an empty slot ships a blank box")

    p0 = text_frame.paragraphs[0]
    for extra in list(text_frame.paragraphs)[1:]:
        extra._p.getparent().remove(extra._p)

    runs = p0.runs
    if not runs:
        raise ValueError(
            "template slot's first paragraph carries no run, so there is no formatting to inherit. "
            "Type one character of placeholder text into the shape in PowerPoint and re-save the "
            "template."
        )
    for extra in runs[1:]:
        extra._r.getparent().remove(extra._r)

    prev = p0._p
    for _ in lines[1:]:
        clone = copy.deepcopy(p0._p)
        prev.addnext(clone)
        prev = clone

    for paragraph, line in zip(text_frame.paragraphs, lines):
        paragraph.runs[0].text = line
```

**Two consequences the planner should carry into tasks.**

1. **The empty-run trap is real.** Setting a slot to `""` earlier in a pipeline leaves a paragraph
   with **zero runs** (measured: `('B_empty_paragraph_runs', 0, "''")`), and the next preserving fill
   then has nothing to inherit from. The teaching error above is not defensive padding — it is the
   observed failure.
2. **`tf.text = ...` is still correct for the watermark**, because the writer created that textbox
   itself and owns every property on it. Use the cheap API where you own the shape; use the
   preserving primitive where the operator does.

---

### Pattern 4: The Draft watermark — added, refused-if-present, absent when Published

**What:** while `not surface.is_published`, add one textbox per slide named `NL_DRAFT_WATERMARK`,
**last** (top of z-order). Every property is a fixed literal.

Measured (W12): normalized bytes identical across a 3-second gap; `part_digest` equal; the shape
reads back last in `slide.shapes` with `rotation == 315.0` and its name intact.

```python
# Source: measured in this session (exp3 C / exp5 F) — round-trips through a real write
tb = slide.shapes.add_textbox(Inches(1.5), Inches(2.5), Inches(7), Inches(2))
tb.name = "NL_DRAFT_WATERMARK"
tb.rotation = 315.0
tb.text_frame.text = "DRAFT"                    # the writer owns this shape — plain API is fine
run = tb.text_frame.paragraphs[0].runs[0]
run.font.size = Pt(96)
run.font.bold = True
run.font.color.rgb = RGBColor(0xD0, 0xD0, 0xD0)
```

**New: the template must not already contain the name (W14).** Measured — adding the watermark to a
deck that already had one produced **two** shapes named `NL_DRAFT_WATERMARK` with no error.
python-pptx permits duplicate names, so a "helpful" operator who copies the watermark into their
template silently defeats the binding map. The writer must check for `NL_DRAFT_WATERMARK` in the
bind pass and raise (Pattern 2).

**New: the toggle mechanism is sound, and is still not what we do (W13).** Removing a shape with
`sh._element.getparent().remove(sh._element)` is deterministic across a 3-second gap **and exactly
reversible**: a rendered deck with the watermark removed has a `part_digest` **equal** to an
untouched open→save of the template. So the decision note's *mechanical* objection ("needs the
undocumented lxml idiom") is now measured to be harmless. The note's other objection is the binding
one and still holds: a toggle makes correct gate behaviour depend on operator template content, and
"the watermark is missing" would then be a template bug rather than a renderer bug. **Keep adding.**
The measurement is recorded so nobody re-opens it, and because the same lxml idiom is what the
preserving fill primitive uses for paragraph/run pruning — one measured idiom, two call sites.

**Wording correction for the decision note (W20).** `core_properties.identifier` serializes as
**`dc:identifier`**, not `cp:identifier` — measured in `docProps/core.xml`:
`<dc:identifier>surface-1</dc:identifier>`. The python-pptx attribute name and the read-back
assertion in the note are both correct; only the OPC element name in the note's table is wrong. No
code consequence; fix the sentence when the note is next touched.

---

### Pattern 5: Images — deterministic, deduplicated, add-order-numbered

Phase 2 does not place assets (Phase 3 does), but the writer's shape is decided here, so the
mechanics are measured now.

| Measured | Result |
|----------|--------|
| Two distinct PNGs added in order | `ppt/media/image1.png`, `ppt/media/image2.png`; slide rels `rId2`, `rId3` in add order |
| Two **byte-identical** files (different paths) | **ONE** media part — python-pptx content-deduplicates |
| Reversed add order | same part names, **different `part_digest`** — add order IS a determinism variable |
| Same order, 3 s apart | normalized bytes identical |
| `[Content_Types].xml` | gains `Default Extension="png"` automatically |
| `PicturePlaceholder.insert_picture()` on a placeholder renamed `NL_TEAM_PHOTO` | returns a picture **still named `NL_TEAM_PHOTO`** — unlike `add_slide`, `insert_picture` does not regenerate names |
| Stock layouts with a `PICTURE` placeholder | exactly one: layout **8**, "Picture with Caption", `idx=1` |

**The one rule this creates:** iterate assets in a **pinned order** (Phase 3: Weekly Spec file
order). The writer should not sort or set-iterate images. Text fill order, by contrast, is **not** a
variable — filling slots in reverse name order produced byte-identical output (W18), because text
edits are in-place on existing elements while `add_picture` appends new parts.

---

### Pattern 6: Promote the normalizer, and treat the template as *not* a fixed point

**The promotion** is a verbatim move of `tests/fixtures/weekly/_determinism.py` (module docstring
included — it is the best explanation of the mechanism in the repo) into `pptx_writer.py` at module
level. It is stdlib-only, so it does not create a core→extra edge and stays bare-importable.

`tests/test_pptx_determinism.py` then imports `from newsletters.pptx_writer import
normalize_opc_zip, part_digest, ...` and **deletes its `sys.path.insert`** — which closes **IN-03**
exactly as the review predicted. `_author_template.py` and `_record_determinism_evidence.py` do the
same.

**The new constraint (W1, W2): a rendered deck can never be compared to the template.**

- **W1 — open→save is not a fixed point.** Opening the committed `template.pptx` and saving it with
  **no modification** produces a package whose `part_digest` differs; the sole differing part is
  `docProps/core.xml`. Cause: `_author_template.py` sets several core properties to `""`, which lxml
  serializes as `<cp:keywords></cp:keywords>`; on reload the element's text is `None` and it
  re-serializes as `<cp:keywords/>`. The *second* resave is stable, so this is a one-shot
  first-write asymmetry, not a non-determinism.
- **W2 — part emission order is a property of the input package, not of the content.** The committed
  template emits `docProps/core.xml` / `app.xml` at indices 2–3; a reopened-and-resaved copy emits
  them at 36–37 — while `_rels/.rels` is byte-identical between the two. python-pptx registers parts
  in a different order when loading from an archive than when building from its default template.
  Deterministic per input (two independent open→saves 3 s apart are byte-equal after normalization
  and share a `part_digest`), but not equal to the template's order.
- **The published deck writes `<cp:contentStatus></cp:contentStatus>`** when `content_status` is set
  to `""` (W22) — the same asymmetry, now in the writer's own output.

**Consequences for the plan:**

1. No test may assert `part_digest(rendered) == part_digest(template)` or compare part *order*
   between them.
2. Phase 4's committed golden `.pptx` must be produced **by the writer**, never by re-saving the
   template, and its committed==fresh gate must compare `part_digest(committed)` to
   `part_digest(writer(fresh))` — never to anything derived from the template.
3. `test_committed_template_is_scrubbed_and_normalized`'s existing assertion
   `normalize_opc_zip(committed) == committed` remains true and remains the right check: it asserts
   the *zip container* is a fixed point of the normalizer, not that the *package* is a fixed point of
   python-pptx.

**IN-02 / IN-04 — the delegation, and a caution the review did not anticipate.**

- `_author_fixtures._normalize_zip` (the nine ADAPT-06 golden decks) delegating to the canonical
  `normalize_opc_zip` swaps `_FIXED_ZIP_DATE_TIME` (2026-01-01) for `DOS_EPOCH` (1980-01-01) and
  gains the `create_system=0` pin — that is IN-02's second half. It **regenerates all nine
  binaries**. Verified safe: `tests/test_pptx_golden.py` asserts *extracted content* (claims,
  traces, coverage, JSON round-trip) and the corpus *file list* — **no test byte-compares those nine
  committed binaries**, and no test regenerates them. So the diff is nine binary files and zero
  assertion changes.
- **IN-04's literal fix is harmful and should be amended.** Consolidating `_author_template.py`'s
  `_FIXED = datetime(2026,1,1)` onto `EPOCH_ZERO` would set the *template's* `dcterms:created` to
  1970-01-01 — the exact value the writer is supposed to write. The read-back assertion
  `cp.created == EPOCH_ZERO.replace(tzinfo=None)` would then pass **even if the writer never set
  it**: a false green, in the phase whose whole discipline is "the agent says green ≠ green". The
  same argument applies to `category` and `content_status`, which the fixture correctly leaves `""`
  so the writer's write is observable. **Recommendation: apply IN-02's zip-metadata consolidation;
  keep the fixture template's core-property instant deliberately different from `EPOCH_ZERO`, with a
  comment naming it a falsifiability control rather than a second sentinel.** This is a deviation
  from the scheduled fix and needs the planner's explicit decision (Open Question 3).

---

### Pattern 7: The writer reads the gate and cannot write it

```python
watermark = not surface.is_published                 # a READ of a computed property
status = "draft" if not surface.is_published else ""  # the decision note's exact mapping
```

`Surface.is_published` is a `@property` over `review.state`; there is no assignment to
`surface.review`, `surface.review.state`, or any `Surface` field anywhere in the writer. `Surface`
carries `model_config = ConfigDict(validate_assignment=True)`, so an accidental assignment would be
validated — but the durable guard is the absence of the code path plus the test that renders a Draft
Surface and asserts `surface.review.state is ReviewState.DRAFT` and
`surface.model_dump() == before` afterwards.

### Anti-Patterns to Avoid

- **`text_frame.text = "..."` on an operator's shape.** Measured to erase both `rPr` and `pPr`
  (W3). The deck still *renders* — with the operator's 20pt bold bullets silently downgraded to
  theme defaults. A visual regression no automated check in this repo can see.
- **`{sh.name: sh for sh in slide.shapes}`.** Last-wins on duplicates (Phase 1) **and** blind to
  group-nested shapes (W17). Two independent silent-drop mechanisms in one comprehension.
- **`TextFrame.fit_text()`.** Its `_best_fit_font_size` path locates *a TrueType font file installed
  on the current system* — measured in the installed source. Output would depend on which fonts the
  machine has. It is the single most tempting non-determinism in the library. **Ban it by name in
  the plan.**
- **Assuming an autofit shape resizes.** `auto_size` is metadata for PowerPoint; python-pptx never
  recomputes geometry. Measured: 2000 words into a 6"×3" box leaves `width`/`height` unchanged and
  raises nothing (W8). Text overflow is a *silent, visual-only* failure.
- **`prs.save(path)` then rewriting the file in place.** A raised normalization leaves an
  un-normalized deck on disk. Save to `BytesIO`, normalize, `write_bytes` once.
- **Deriving `out_path` from `surface.id`.** A Surface id is authored content; joining it to a
  directory is a path-traversal primitive. The caller supplies the path.
- **Monkeypatching `pptx.opc.serialized._ZipPkgWriter`** (Phase 1; still rejected).
- **`add_slide()` in the writer** (Phase 1; regenerates placeholder names). The name-restore escape
  hatch exists in the decision note and is **not needed in Phase 2** — a fixed-slide template is the
  contract.
- **Re-exporting `pptx_writer` from `__init__.py`.** Follow `adapters`: submodule import only.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bulleted / levelled lists in a deck | Emitting `<a:buChar>` / `<a:buAutoNum>` XML yourself | Inherit them: `deepcopy` the template paragraph (Pattern 3) | python-pptx has **no** bullet API (W6). Hand-written bullet XML has to re-derive the operator's indent, colour, size and font-family from the master's list style — the exact "inventing layout" D-03 forbids |
| Preserving fonts across a fill | Reading `run.font.*` and re-applying it after `tf.text =` | `deepcopy` of `<a:p>` | Re-applying only copies the properties you thought to enumerate; the deep copy carries the whole `rPr`/`pPr` subtree including theme references and language tags |
| Deterministic zip output | A byte-level timestamp patcher | the promoted `normalize_opc_zip` | Timestamps live in both the local header and the central directory; a seek-and-patch fixes one and corrupts the other |
| Cross-environment artifact comparison | Full-file sha256 | `part_digest` | DEFLATE output is zlib-implementation-dependent (Phase 1 Pitfall 1) |
| Importing the optional extra | A second `try: import pptx` in the writer | `adapters._pptx_loader._load_pptx()` | One teaching message, one guard test, no drift |
| A fixed instant | A new epoch constant | `adapters._timestamps.EPOCH_ZERO` (tz-aware; `.replace(tzinfo=None)` at the OPC boundary) | Repo-wide sentinel; the tz strip is Pitfall 5, already written down |
| Text sizing / overflow prevention | `fit_text()`, or measuring strings | Nothing — leave it to PowerPoint, and make the template's boxes wrap | `fit_text` reads system fonts (machine-dependent). See Pitfall 3 for the honest mitigation |
| Slide duplication | An XML deep-copy of a slide + its rels | Don't: the template contract fixes the slide count | No copy API; hand-rolled slide cloning corrupts rels/media |

**Key insight:** every remaining non-trivial writer behaviour is *inheritance from the operator's
template*, not construction. The moment the writer starts building formatting, it has started
inventing layout — which is the one thing D-03 forbids. The `deepcopy` primitive is the mechanical
expression of that principle.

## Common Pitfalls

### Pitfall 1: The obvious fill API silently downgrades the operator's deck

**What goes wrong:** the deck renders, opens, passes every byte and digest assertion — and the
highlights list has lost its bullets and dropped from 20pt to the theme default.
**Why it happens:** `TextFrame.text`'s setter clears `<a:txBody>`'s content and appends a bare
paragraph; there is no `rPr` and no `pPr` to inherit from.
**How to avoid:** Pattern 3's preserving primitive.
**Warning signs:** a read-back test that asserts `run.font.size` returns `None`. **Make that an
explicit assertion** — it is the only automated way to see this failure.

---

### Pitfall 2: A slot nested inside a group is invisible, in both directions

**What goes wrong:** the operator groups their two narrative boxes, the renderer reports
`NL_HIGHLIGHTS` as an *unknown* name, and the fix that suggests itself (remove it from the content
map) ships a deck with an empty highlights box and no error.
**Why it happens:** `slide.shapes` does not recurse (W17).
**How to avoid:** the `_walk` recursion in Pattern 2.
**Warning signs:** an operator says "but the box is right there in the Selection Pane".

---

### Pitfall 3: Text overflow is invisible to every check this repo has

**What goes wrong:** four highlights fit; six run off the slide. Nothing raises; bytes are stable;
`unzip -t` is clean; the read-back assertions pass. The reviewer sees it, or doesn't.
**Why it happens:** python-pptx stores geometry and never measures text (W8). Worse, the current
fixture template's boxes are `auto_size = SHAPE_TO_FIT_TEXT` with `word_wrap = False` — python-pptx's
`add_textbox` defaults — which is the worst combination: no wrapping, and a stored size PowerPoint
will only fix when a human edits the box.
**How to avoid:** three honest, cheap moves, none of which is `fit_text`:
1. Author the fixture template with `word_wrap = True` and `auto_size = MSO_AUTO_SIZE.NONE`
   (measured to work), so overflow clips rather than escaping the slide.
2. Document the limit in the operator recipe (Phase 4): the template's box sizes are the operator's
   responsibility; the renderer never resizes anything.
3. Make the human-verify checkpoint (§Environment Availability) explicitly include "a
   deliberately-overfull slot looks acceptable", so the one human look covers it.

**Warning signs:** none automated. That is the point of recording it.

---

### Pitfall 4: An operator template that already contains `NL_DRAFT_WATERMARK`

**What goes wrong:** two shapes with one name; the binding map's duplicate check fires on the
*second* render (or, if the map is built before the add, never fires at all and the deck ships two
watermarks).
**Why it happens:** duplicate names are legal (Phase 1 E11) and the writer's add is unconditional
in mechanism (W14, measured: two shapes written, no error).
**How to avoid:** refuse the name at bind time (Pattern 2). Cheap, and it teaches the operator that
the name is reserved.

---

### Pitfall 5: Comparing a rendered deck to the template

**What goes wrong:** a plausible-looking assertion like "the render changed only the parts it
should" goes red on `docProps/core.xml` and on part order, for reasons that have nothing to do with
the writer (W1, W2).
**Why it happens:** the empty-element `<x></x>` → `<x/>` asymmetry on first reload, and python-pptx's
different part-registration order for loaded vs built packages.
**How to avoid:** assert render-vs-render, never render-vs-template. Phase 4's golden deck comes from
the writer.
**Warning signs:** a diff whose only entry is `docProps/core.xml`, or a part-order difference with a
byte-identical `_rels/.rels`. Both are this pitfall, not a regression.

---

### Pitfall 6: The empty-run slot

**What goes wrong:** `ValueError: template slot's first paragraph carries no run` on a slot the
operator "left blank on purpose".
**Why it happens:** a text box with no typed characters has a paragraph with **zero** runs (measured:
`('B_empty_paragraph_runs', 0, "''")`), so there is no formatting carrier.
**How to avoid:** the teaching error in Pattern 3 tells the operator to type one placeholder
character. Document it in the Phase 4 recipe.

---

### Pitfall 7: The pptx tests are skipped in CI, so "green" means "not run"

**What goes wrong:** the renderer is merged with a full local green and a CI green that never
imported python-pptx.
**Why it happens:** `.github/workflows/ci.yml` has four jobs (`bare-install`, `merge-block`,
`site-integrity`, `import-linter`); none installs `[pptx]`, and `site-integrity` runs a named subset
of test files that excludes every pptx module (W21). Each pptx test module skips itself via
`pytest.importorskip("pptx")`.
**How to avoid:** add a job that installs `.[test,pptx]` and runs `tests/test_pptx_*.py`. SC-5's
"a sample Surface renders through it in CI" is *false* without it.
**Warning signs:** a CI log with `s` where you expected `.`.

---

### Pitfall 8 (inherited, unchanged): the tz-naive core-properties comparison

`dcterms:created` reads back tz-**naive**; `EPOCH_ZERO` is tz-aware. Compare against
`EPOCH_ZERO.replace(tzinfo=None)`. Re-confirmed this session (`F_readback_created` →
`1970-01-01 00:00:00`, equality `True` only after the strip).

## Code Examples

### The writer, end to end (measured: two renders 3 s apart are byte-identical)

```python
# Source: measured in this session (exp5) against python-pptx 1.0.2 / zlib 1.3.
# Every assertion below the write reads the WRITTEN BYTES back.
def render_surface_pptx_bytes(surface, *, template, slots: dict[str, list[str]]) -> bytes:
    from .adapters._pptx_loader import _load_pptx        # noqa: PLC0415 — lazy ([pptx] extra)
    from .adapters._timestamps import EPOCH_ZERO

    pptx = _load_pptx()
    prs = pptx.Presentation(str(template))

    by_name = bind(prs, slots)                            # Pattern 2 — raises, never guesses
    for name in slots:                                    # fill order does not affect bytes (W18)
        fill(by_name[name].text_frame, slots[name])       # Pattern 3 — preserves rPr and pPr

    if not surface.is_published:                          # a READ of the gate. Never a write.
        for slide in prs.slides:
            _add_watermark(slide)                         # Pattern 4 — added last, top of z-order

    cp = prs.core_properties
    cp.category = "generated-by:newsletters"
    cp.content_status = "" if surface.is_published else "draft"
    cp.identifier = surface.id                            # serializes as dc:identifier (W20)
    cp.created = EPOCH_ZERO.replace(tzinfo=None)          # tz strip — Pitfall 8
    cp.modified = EPOCH_ZERO.replace(tzinfo=None)

    buf = io.BytesIO()
    prs.save(buf)                                         # the ONLY clock in the function
    return normalize_opc_zip(buf.getvalue())              # stdlib; part bytes untouched


def render_surface_pptx(surface, *, template, out_path) -> Path:
    raw = render_surface_pptx_bytes(surface, template=template, slots=...)
    out = Path(out_path)
    out.write_bytes(raw)                                  # ONE write of complete bytes
    return out
```

**Measured behaviour of exactly this shape** (`exp5`, template = the committed
`tests/fixtures/weekly/template.pptx`, four slots, two lines in `NL_HIGHLIGHTS`):

```
F_double_render_byte_identical_3s      True
F_partdigest_equal                     True
F_idempotent_normalize                 True
F_readback_category                    'generated-by:newsletters'
F_readback_content_status              'draft'
F_readback_identifier                  'surface-1'
F_readback_created                     1970-01-01 00:00:00   (== EPOCH_ZERO.replace(tzinfo=None))
F_readback_names                       ['Footer','NL_DRAFT_WATERMARK','NL_HIGHLIGHTS',
                                        'NL_LOWLIGHTS','NL_MODULE','NL_WEEK_TITLE']
F_readback_highlights                  [[('cut the checklist','228600')],
                                        [('second reviewer joined','228600')]]   # 18pt PRESERVED
F_published_names                      (no NL_DRAFT_WATERMARK)
F_published_content_status             ''
F_draft_vs_published_partdigest_differ True
F_failloud_unknown_name                "unknown slot(s): ['NL_NOPE']; template has [...]"
F_failloud_unfilled_slot               "unfilled reserved slot(s): ['NL_LOWLIGHTS']"
F_fill_order_affects_bytes             False
```

### The read-back assertion, verbatim from the decision note (now executed)

```python
written = Presentation(str(out_path))              # reopen the FILE that was written
cp = written.core_properties
assert cp.category == "generated-by:newsletters", cp.category
assert cp.content_status == ("draft" if not surface.is_published else ""), cp.content_status
assert cp.created == EPOCH_ZERO.replace(tzinfo=None)   # dcterms reads back tz-NAIVE (Pitfall 8)
assert cp.identifier == surface.id, cp.identifier
assert any(sh.name == "NL_DRAFT_WATERMARK" for s in written.slides for sh in s.shapes)
```

The last line must be **inverted** for the Published case — `assert not any(...)` — or SC-3's "while
the Surface is not Published" is only half-asserted.

## Measured Results — this session (W-series)

> Executed 2026-08-29 in the repo's own `.venv`: python-pptx **1.0.2**, CPython **3.11.15**, zlib
> **1.3**, Linux. Fixture: the committed `tests/fixtures/weekly/template.pptx` plus two synthetic
> decks built in the scratchpad (a "rich" template with real bullets/levels, and a group-nested
> deck). Scratch code was never written into the repo.

| # | Finding | Evidence |
|---|---------|----------|
| **W1** | **Open→save is not a fixed point.** Opening the committed template and saving it unchanged yields a different `part_digest`; the sole differing part is `docProps/core.xml`, because `""`-valued properties written as `<cp:keywords></cp:keywords>` come back as `<cp:keywords/>`. The **second** resave is stable. | exp1 A, exp2 |
| **W2** | **Part emission order differs between a built package and a reopened one.** Committed template: `docProps/core.xml`,`app.xml` at indices 2,3. Reopened+resaved: indices 36,37 — with `_rels/.rels` **byte-identical**. Order is deterministic per input (two open→saves 3 s apart: normalized-equal, digest-equal). | exp1 A/A2, exp2 |
| **W3** | **`text_frame.text = x` destroys run AND paragraph formatting.** 20pt bold + `buChar` → size `None`, bold `None`, bullet gone; collapses to one paragraph. | exp1 B, exp4 E1 |
| **W4** | **`tf.clear()` keeps paragraph 0's `pPr` (bullet survives) but drops ALL runs**; `add_paragraph()` returns a paragraph with no `pPr`, so lines 2..n lose bullet and level. | exp4 E2 |
| **W5** | **The reuse-and-clone primitive preserves everything.** Reuse p0's run 0, `deepcopy(p0._p)` per extra line → all three lines report `('…','254000',True)` with `bullet: buChar`; survives write+reopen; normalized-equal across a 3 s gap. | exp4 E3 |
| **W6** | **No bullet API.** `_Paragraph` public surface: `add_line_break, add_run, alignment, clear, font, level, line_spacing, part, runs, space_after, space_before, text`. `_Run`: `font, hyperlink, part, text`. | exp4 E4 |
| **W7** | **`TextFrame.fit_text()` is machine-dependent** — its docstring and `_best_fit_font_size` locate "a font file with matching `font_family`, `bold`, `italic` **installed on the current system**". | `inspect.getsource(TextFrame.fit_text)` |
| **W8** | **python-pptx never recomputes geometry.** 2000 words into a 6"×3" box: `width`/`height` unchanged, no exception. Fixture boxes are `auto_size=SHAPE_TO_FIT_TEXT`, `word_wrap=False` (the `add_textbox` default). | exp1 B, exp4 E0/E5 |
| **W9** | `tf.text = "one\ntwo\vthree"` → **2 paragraphs** (`\n` splits paragraphs, `\v` is a line break); text round-trips exactly. | exp1 B |
| **W10** | **Empty fill leaves zero runs** — `tf.text = ""` gives `len(paragraphs[0].runs) == 0`, so a later preserving fill has nothing to inherit. | exp1 B |
| **W11** | **Unicode round-trips exactly and deterministically** — `café — “smart” … 🎯 <&>` survives write+reopen byte-for-byte; XML declares UTF-8; normalized-equal across a 3 s gap. | exp1 B |
| **W12** | **Watermark add is deterministic** — normalized bytes equal and `part_digest` equal across a 3 s gap; reads back **last** in `slide.shapes` with `rotation == 315.0`. | exp3 C |
| **W13** | **Shape removal is deterministic and exactly reversible** — `sh._element.getparent().remove(...)` on the watermark yields a `part_digest` **equal to an untouched open→save of the template**; stable across a 3 s gap. | exp3 C2 |
| **W14** | **Adding a watermark to a deck that already has one writes TWO shapes with the same name**, silently. | exp3 C3 |
| **W15** | **Images:** two distinct PNGs → `image1.png`/`image2.png`, slide rels `rId2`/`rId3` in add order; two byte-identical files → **one** media part; reversed add order → **different `part_digest`**; same order 3 s apart → normalized-equal; `[Content_Types].xml` gains `Default Extension="png"`. | exp3 D |
| **W16** | **`PicturePlaceholder.insert_picture()` PRESERVES an operator-set name** (`NL_TEAM_PHOTO` survives), deterministic across a 3 s gap. Only stock layout with a `PICTURE` placeholder: layout 8 "Picture with Caption", `idx=1`. | exp3 D2 |
| **W17** | **`slide.shapes` is top-level only.** A textbox named `NL_INSIDE_GROUP` inside a group is absent from `[sh.name for sh in slide.shapes]`. Group shapes report `has_text_frame == False`. | exp-group |
| **W18** | **Text fill order does not affect output bytes** (reverse-order fill → byte-identical); image add order does (W15). | exp5 F |
| **W19** | **A7 CLOSED.** The live `_req_name` maps `"python-pptx>=1.0.2"` and `"python-pptx>=1.0.2,<2.0"` both to `"python-pptx"` — a floor pin passes `test_pptx_extra_declared` with no test change. | executed against `tests/test_ai_optional.py` |
| **W20** | **`core_properties.identifier` serializes as `dc:identifier`**, not `cp:identifier` (`<dc:identifier>surface-1</dc:identifier>`). | exp5 core.xml |
| **W21** | **No CI job installs `[pptx]`.** `ci.yml` jobs: `bare-install` (`.[test]`), `merge-block` (`.[test]` + `.[config]`), `site-integrity` (`.[test,config]`, named test files only), `import-linter` (`.[dev]`). Every pptx test module is `importorskip`-skipped in CI. | `.github/workflows/ci.yml`, grep |
| **W22** | Setting `content_status = ""` (the Published case) writes `<cp:contentStatus></cp:contentStatus>` — the W1 asymmetry, now in the writer's own output. Harmless within one writer; relevant to any future re-save. | exp5 F |
| **W23** | **The nine ADAPT-06 golden decks are content-asserted, not byte-asserted.** `test_pptx_golden.py` checks claims/traces/coverage/round-trip and the corpus file list; nothing byte-compares or regenerates the binaries. The IN-02 delegation is therefore a 9-binary diff with zero assertion changes. | `tests/test_pptx_golden.py`, grep |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| "Fill a deck with `shape.text_frame.text = value`" (every python-pptx tutorial, and the Phase 1 miniature writer in `test_pptx_determinism._render_bytes`) | Reuse-and-clone the template paragraph so `rPr`/`pPr` survive | measured this session | The spike's fill line is correct *for the spike* (its fixture has one run per box and asserts nothing about formatting) but must **not** be copied into the writer |
| `pptx/opc/pkgwriter.py`, `phys_pkg.py` (pre-1.0 module layout) | `pptx/opc/serialized.py` (`PackageWriter`, `_ZipPkgWriter`) | python-pptx 1.0.0, 2024 | Any advice referencing the old paths is stale; all references here are against 1.0.2 |
| "zips are inherently non-reproducible" | Fix mtimes/order/`create_system`; **and** know that DEFLATE itself varies by implementation (zlib vs zlib-ng) | zlib-ng in mainstream distros, 2024 | Byte claims are scoped; `part_digest` crosses environments |
| Wall-clock fallbacks | `EPOCH_ZERO` / `deterministic_timestamp()` | this repo, v1.1 | The writer extends it to `dcterms:created/modified`, with the tz strip |

**Deprecated/outdated:** python-pptx 0.6.x import paths. `strict_timestamps` is not the lever (it is
already `False` in `_ZipPkgWriter`; the `str` arcname is the cause).

## Project Constraints (from CLAUDE.md)

| CLAUDE.md directive | Consequence for Phase 2 |
|---|---|
| **AI-optional core** — extras lazy-imported, CI fails on a reachable core edge | `pptx_writer.py` has **zero** column-0 `import pptx`; it reuses `adapters._pptx_loader._load_pptx()`. New guard test mirroring `test_pptx_loader_has_no_toplevel_pptx_import`. `lint-imports` stays KEPT. **`bare-install` CI job must stay green and must be re-run independently.** |
| **No auto-publish, ever** | The writer *reads* `surface.is_published`; there is no assignment to any `Surface` field. `git diff --exit-code -- src/newsletters/semantic.py` stays empty. A test proves a Draft Surface is still Draft (and `model_dump()`-identical) after a render. |
| **Every published claim traces to evidence** | Not exercised by the writer (Phase 3 owns `missing[]`), but the writer must never *invent* slot content: an unfilled `NL_` slot raises rather than rendering a blank box. |
| **Faithful, not suggestive** | The writer never summarises, truncates, reflows or re-orders lines. Overflow is disclosed to a human (Pitfall 3), never "fixed" by shrinking the font (`fit_text` is banned). |
| **Interactive until trusted** | The human-verify checkpoint (open a normalized deck in real PowerPoint) is a phase gate, not an assumption. No installs that write config; no network. |
| **Secrets / private corpora** | The template shipped is **fabricated**; no operator deck is committed. The scrub guard (`test_committed_template_is_scrubbed_and_normalized`) must survive any template regeneration. |
| **Specs are the source of truth** | `docs/weekly-spec.md` §Determinism already points at the decision note. If Phase 2 amends the note (Open Questions 2/3), the note is edited in the same change with the reason. |
| **Typed everything** | Public writer signature fully annotated; `Surface` in, `bytes`/`Path` out; mypy no-new-failures against the 2026-07-02 baseline. |
| **Branch + PR only; atomic commits** | One task = one commit; the template regeneration (if any) is its own commit so the binary diff is legible. |
| **"The agent says green" ≠ green** | Every deck assertion reads the **written file** back. And re-run the gate set yourself — noting W21, a CI green today does not mean the pptx tests ran. |
| **Compass + RETRO per phase** | `WHERE-WE-ARE.md` updated; W21 (pptx never ran in CI) is a RETRO-worthy friction: a gate that silently did not run. |

## Runtime State Inventory

> Phase 2 includes a **promotion/refactor** (`_determinism.py` → `src/`) and a possible **fixture
> regeneration**, so this section is required.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | None. The writer reads a template and writes a deck; no database, no cache, no user-keyed store. Verified: no DB/datastore client anywhere under `src/newsletters/` (the repo's persistence is committed files under `content/`). | none |
| **Live service config** | None. No external service knows the module name `_determinism`. Verified: the only importers are `tests/test_pptx_determinism.py`, `tests/fixtures/weekly/_author_template.py`, `tests/fixtures/weekly/_record_determinism_evidence.py` (grep). | code edit in those three files only |
| **OS-registered state** | None — no scheduled tasks, no daemons, no CLI entry point added this phase. Verified: `pyproject` console scripts unchanged (`newsletters` only), no new command in `cli.py`. | none |
| **Secrets / env vars** | None. The writer takes no credentials and reads no environment. | none |
| **Build artifacts / committed binaries** | **(a)** `tests/fixtures/weekly/template.pptx` — regenerated if the fixture gains a group-nested slot / a non-text slot / wrap settings, and/or if `_FIXED` changes. **(b)** the nine `tests/fixtures/pptx/*.pptx` — regenerated **iff** `_author_fixtures._normalize_zip` delegates (IN-02 second half). **(c)** `__pycache__` under `tests/fixtures/weekly/` holds a compiled `_determinism` — stale after the promotion, harmless, but a stale `.pyc` plus a `sys.path.insert` is exactly the shadowing IN-03 warned about; deleting the `sys.path.insert` removes the mechanism. **(d)** `.planning/notes/2026-08-29-pptx-determinism-evidence.json` — unchanged; its `--check` mode must still pass after the promotion (the script imports `_determinism`). | regenerate (a)/(b) as deliberate, separately-committed steps; verify (d)'s `--check` still exits 0 |

**Data migration vs code edit:** every item above is a **code edit or an artifact regeneration** —
there is no stored record anywhere carrying the string `_determinism` that a code change would not
also update. The one thing that is *not* a code edit is the committed binaries, and those are
regenerated by running their author scripts, not migrated.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.11.15 (repo `.venv`); 3.12 in CI | — |
| `python-pptx` | the writer | ✓ **in `.venv`** | 1.0.2 | `pip install '.[pptx]'` — already declared |
| `zlib` | normalization | ✓ | 1.3 (runtime) | stdlib |
| `pytest` | the suite | ✓ | via `[test]`/`[dev]` | — |
| CI job with `[pptx]` | SC-5 "renders … in CI" | ✗ **MISSING** | — | **none — must be added this phase** (W21) |
| LibreOffice **Impress** | opening a normalized deck | ✗ | `libreoffice-core` only, no Impress filters | none in this environment |
| Microsoft PowerPoint | the definitive consumer check | ✗ | — | **human verification** |

**Missing dependencies with no fallback:**
- **A CI job that installs `[pptx]`.** Without it, ROADMAP SC-5's "a sample Surface renders through
  it in CI" is not satisfiable and the phase cannot honestly be called done. Add a job installing
  `.[test,pptx]` running `tests/test_pptx_writer.py tests/test_pptx_determinism.py
  tests/test_pptx_golden.py tests/test_pptx_adapter.py tests/test_pptx_loader.py`.
- **A real `.pptx` consumer.** Unchanged from Phase 1. `checkpoint:human-verify` (assumption A8,
  carried): open one normalized, watermarked Draft deck in real PowerPoint and confirm (i) it opens
  clean, (ii) the watermark is visible and legible, (iii) the operator's bullets/fonts survived the
  fill, (iv) a deliberately-overfull slot is acceptable (Pitfall 3), (v) the marker is readable in
  File → Info. This one look closes A8, A4 and Pitfall 3 together.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (`[test]` / `[dev]` extras); `pythonpath = ["src"]`, `testpaths = ["tests"]` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/test_pptx_writer.py tests/test_ai_optional.py -x -q` |
| Full suite command | `pytest -q` |
| Adjacent gates | `lint-imports` (contracts KEPT) · `newsletters check --corpus {rev1,work,module}` · committed==fresh double-render · mypy/black/isort no-NEW-failures vs the 2026-07-02 baseline · **bare-install CI** · **the new pptx CI job** |
| Optional-extra idiom | `pptx = pytest.importorskip("pptx", reason=...)` at module scope — a `pytestmark` skipif cannot guard a module-level import (the marker is evaluated after import). Copy from `tests/test_pptx_determinism.py`. |

### Phase Requirements → Test Map

| Req / SC | Behavior | Test Type | Automated Command | File Exists? |
|----------|----------|-----------|-------------------|--------------|
| SC-2 / WKLY-01 | **Double render byte equality** — `render(s) == render(s)`, the two writes separated by a real **3-second** sleep (module-scoped fixture) | integration | `pytest tests/test_pptx_writer.py::test_double_render_is_byte_identical -x -q` | ❌ Wave 0 |
| SC-2 | **Negative control** — an **un-normalized** double write across the DOS boundary is NOT byte-equal, all parts ARE identical, and the only differing zip field is `date_time`. Without this, byte-equality passes for free inside one wall-clock second | integration | `pytest tests/test_pptx_determinism.py -x -q` (exists; keep it, retarget its import) | ✅ retarget |
| SC-2 / Phase 4 | **`part_digest` gate** — digest equality across the two renders, asserted on the **un-normalized** bytes (implementation-independent; the assertion Phase 4 inherits) | unit | `pytest tests/test_pptx_writer.py::test_part_digest_stable -x -q` | ❌ Wave 0 |
| SC-2 | Normalizer **idempotence** + archive integrity (`testzip() is None`) + `[Content_Types].xml` first | unit | `pytest tests/test_pptx_writer.py::test_normalized_archive_valid -x -q` | ❌ Wave 0 |
| SC-3 | **Read-back marker assertions** — reopen the **written file**: `cp.category`, `cp.content_status`, `cp.created`/`.modified` (tz-stripped), `cp.identifier == surface.id` | integration | `pytest tests/test_pptx_writer.py::test_marker_reads_back_off_the_written_file -x -q` | ❌ Wave 0 |
| SC-3 | **Watermark present when Draft** — `NL_DRAFT_WATERMARK` found on every slide of the written file, last in z-order | integration | same module | ❌ Wave 0 |
| SC-3 | **Watermark ABSENT when Published**, and `content_status == ""` — the inverted half of the assertion | integration | `...::test_published_surface_has_no_watermark` | ❌ Wave 0 |
| SC-1 | **Fail loud direction (a)** — content bound to a name the template lacks raises, naming the offender **and listing the template's names** | unit | `...::test_unknown_slot_name_raises` | ❌ Wave 0 |
| SC-1 | **Fail loud direction (b)** — an `NL_` slot with no content raises, naming it | unit | `...::test_unfilled_reserved_slot_raises` | ❌ Wave 0 |
| SC-1 | **Duplicate shape name raises** (legal in OOXML; last-wins would silently drop a slot) | unit | `...::test_duplicate_shape_name_raises` | ❌ Wave 0 |
| SC-1 | **Group-nested `NL_` slot is bound, not dropped** (W17) — both directions exercised through a grouped slot | unit | `...::test_group_nested_slot_is_bound` | ❌ Wave 0 |
| SC-1 | **Non-text slot raises a teaching error** (W17) — a group/picture named `NL_*` in the content map | unit | `...::test_slot_without_text_frame_raises` | ❌ Wave 0 |
| SC-1 | **Template already defining `NL_DRAFT_WATERMARK` is refused** (W14) | unit | `...::test_template_owning_watermark_name_raises` | ❌ Wave 0 |
| WKLY-01 (fidelity) | **Formatting survives the fill** (W3/W5) — read back the written file and assert the slot's run `font.size` is the template's value and `pPr` still carries its bullet, on **every** filled line | integration | `...::test_fill_preserves_operator_formatting` | ❌ Wave 0 |
| WKLY-01 (fidelity) | **Unicode round-trips** through fill + write + normalize (W11) | unit | `...::test_unicode_roundtrips` | ❌ Wave 0 |
| SC-4 | **Draft stays Draft** — after rendering, `surface.review.state is ReviewState.DRAFT` and `surface.model_dump() == before` | unit | `...::test_render_does_not_touch_the_gate` | ❌ Wave 0 |
| SC-4 | **`semantic.py` byte-unchanged** | guard | `git diff --exit-code -- src/newsletters/semantic.py` | ✅ (git) |
| SC-5 | **No column-0 `import pptx` in the writer** | guard | `...::test_pptx_writer_has_no_toplevel_pptx_import` (mirror the loader's) | ❌ Wave 0 |
| SC-5 | **`newsletters.pptx_writer` imports on a bare install** (module-level is stdlib-only) — meta-path-blocked subprocess, mirroring `test_adapters_package_imports_without_pptx` | guard | `...::test_writer_module_imports_without_pptx` | ❌ Wave 0 |
| SC-5 | **`lint-imports` contracts KEPT** | static | `lint-imports` | ✅ `.importlinter` |
| SC-5 | **`[pptx]` extra still contains only python-pptx** (with the floor pin — W19) | guard | `pytest tests/test_ai_optional.py::test_pptx_extra_declared -x -q` | ✅ |
| SC-5 | **A sample Surface renders in CI** | CI | new job: `pip install ".[test,pptx]"` then `pytest tests/test_pptx_*.py -q` | ❌ Wave 0 (**W21 — no job installs `[pptx]` today**) |
| SC-5 | **Fixture corpus is exactly the committed template(s)** — no stray scratch deck | guard | `tests/test_pptx_determinism.py::test_weekly_fixture_corpus_is_exactly_the_committed_template` (update if the fixture set grows) | ✅ retarget |
| all | **Adapter golden tests still green after the IN-02 regeneration** (W23) | regression | `pytest tests/test_pptx_golden.py tests/test_pptx_adapter.py -q` | ✅ |
| all | **Determinism evidence `--check` still exits 0 after the promotion** | regression | `python tests/fixtures/weekly/_record_determinism_evidence.py --check` | ✅ |
| all | Full suite does not regress | regression | `pytest -q` | ✅ |

**The four assertion letters, mapped.** A = `part_digest` (row 3, and Phase 4's gate). B = full-byte
double render (row 1). C = the negative control (row 2 — *keep the existing module*; it is the only
thing that makes B meaningful, and it is the assertion most likely to be dropped as "redundant" once
the writer exists). D (new, this research) = **formatting fidelity** — the only automated way to see
Pitfall 1.

### Sampling Rate

- **Per task commit:** `pytest tests/test_pptx_writer.py tests/test_ai_optional.py -x -q` +
  `lint-imports`
- **Per wave merge:** `pytest -q` **plus** confirmation that the pptx modules ran (not `s`-skipped)
- **Phase gate:** the full enforced gate set from `.planning/ROADMAP.md` §Enforced gate set, re-run
  **independently**, once per check, before `/gsd-verify-work` — plus the
  `checkpoint:human-verify` PowerPoint open.

### Wave 0 Gaps

- [ ] `src/newsletters/pptx_writer.py` — the module itself (normalizer promoted verbatim; writer added)
- [ ] `tests/test_pptx_writer.py` — the phase's proof (rows above)
- [ ] **`.github/workflows/ci.yml`** — a job installing `.[test,pptx]`; without it SC-5 is unmet (W21)
- [ ] A **sample `Surface(REPORT)` fixture** for the CI render — built from existing block kinds
      (Phase 3 owns the four new ones); fabricated content, no org names in `src/`
- [ ] **Template fixture upgrade** — the current five flat textboxes cannot exercise W17 (group
      nesting), the non-text-slot error, or formatting preservation (the boxes carry a single 18pt
      run and no bullets). Add: one `NL_` slot **inside a group**, one non-text `NL_`-named shape
      for the teaching-error test, real bullet/level formatting on a narrative slot, and
      `word_wrap=True` / `auto_size=NONE` (Pitfall 3). Regeneration is a separate commit.
- [ ] Retarget `tests/test_pptx_determinism.py`, `_author_template.py`,
      `_record_determinism_evidence.py` to `from newsletters.pptx_writer import …` and **delete the
      three `sys.path.insert` lines** (closes IN-03)
- [ ] `_author_fixtures._normalize_zip` delegates to `normalize_opc_zip` (closes IN-02's second
      half) + regenerate the nine golden decks — **separate commit**, binary-only diff (W23)
- [ ] `python-pptx>=1.0.2` floor pin in `pyproject.toml` `[pptx]` (safe — W19)

*(Framework install: none needed — pytest is the framework and the suite is green.)*

## Security Domain

`security_enforcement: true`, `security_asvs_level: 1`. The writer consumes an **operator-supplied
binary** (a `.pptx` is a zip of XML) and writes a file to a caller-supplied path — a small but real
surface.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface, no network, no accounts |
| V3 Session Management | no | No sessions |
| V4 Access Control | **yes** | The **review gate** is this product's publication access control. The writer *reads* `review.state` and never writes it; `semantic.py` stays byte-unchanged; the gate state is mirrored into `cp:contentStatus` **from** the gate, never back into it |
| V5 Input Validation | **yes** | Operator-supplied shape *names* are untrusted strings used only as dict keys and in error messages — never as paths, never `eval`'d. Slot content is written as XML **text** via python-pptx (which escapes it — measured: `<&>` round-trips intact, W11). Fail-loud on unknown/unfilled/duplicate/non-text slots |
| V6 Cryptography | **yes (hashing only)** | `hashlib.sha256` for `part_digest`, matching `Source.content_hash()`. No keys, no signing |
| V12 File & Resource Handling | **yes** | Reading an operator `.pptx`; writing one file. See threats |
| V14 Configuration | **yes** | `[pptx]` stays an optional extra; the bare install stays extra-free and AI-free (`test_ai_optional` + `lint-imports` + the bare-install CI job) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XXE in an operator template | Information disclosure | **Mitigated upstream** — python-pptx parses with `etree.XMLParser(remove_blank_text=True, resolve_entities=False)`. **Phase 2 must not construct a second XML parser.** The `deepcopy`/`getparent().remove()` idioms operate on already-parsed trees and add no parser |
| Zip-slip via a template member named `../../etc/x` | Tampering | **Closed by construction** — the normalizer reads with `ZipFile.read(name)` and writes with `ZipFile.writestr(ZipInfo, data)`, entirely in memory. No `open()`, no `Path` join, no `extract`. Preserve this property verbatim in the promotion; a reviewer should diff the promoted module against the fixture original to confirm nothing was "tidied" |
| Duplicate **member** names in a crafted template | Tampering / spoofing | `_reject_duplicate_member_names` raises in all four functions (Phase 1, WR-01). Must survive the promotion **with its tests** |
| Duplicate **shape** names hiding a slot | Tampering | The binding map raises (Pattern 2) — now also across group boundaries |
| Decompression bomb in an operator template | DoS | Accepted: the operator supplies a deck about their own work, same trust level as their own files. `ZipInfo.file_size` is checkable if a limit is ever wanted |
| Path traversal via the output path | Tampering | `out_path` is **caller-supplied and never derived from Surface content**. Never join `surface.id` (authored data) to a directory. State this in the docstring |
| Marker forgery / removal | Spoofing / repudiation | **Accepted and recorded** — `cp:category` is operator-editable. The marker is **provenance, not authenticity**. Nobody may treat an unmarked deck as proof it was not generated |
| Silent publication of an unreviewed deck | Elevation of privilege | `cp:contentStatus` written from the gate + a visible watermark + the untouched gate + the Draft-stays-Draft test — all asserted by reading the written file back |
| Operator data leaking into the repo | Information disclosure | Fabricated template only; the scrub guard (`test_committed_template_is_scrubbed_and_normalized`) must survive any regeneration; scratch decks stay out of `tests/fixtures/weekly/` (the corpus guard enforces it) |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| **B1** | `pptx_writer.py` (no leading underscore) satisfies the decision note's `_pptx_writer.py` | §Project Structure | **Low** — cosmetic; the note's binding content is the destination package + lazy discipline. Flagged for the planner |
| **B2** | The writer takes an explicit `slots` mapping and the Surface→slots derivation lands in Phase 3 | §Responsibility Map, Open Q1 | **Medium** — if the planner reads SC-1 as requiring the derivation now, Phase 2 must invent slot names for block kinds that do not exist yet, which Phase 3 would then rewrite |
| **B3** | Keeping the fixture template's core-property instant ≠ `EPOCH_ZERO` (contra IN-04's literal fix) is right | §Pattern 6, Open Q3 | **Medium** — if wrong, the repo carries a second fixed-instant convention. If *not* done, the marker read-back assertion becomes a false green. Needs an explicit decision |
| **B4** | Upgrading the fixture template (group slot, non-text slot, bullets, wrap) is in scope for Phase 2 | Wave 0 | **Low-medium** — without it, three of the SC-1 tests cannot be written against a realistic deck. Cost is one regenerated binary |
| **B5** | Adding a CI job is in scope (SC-5 says "in CI") | §Environment Availability | **Low** — the criterion says it plainly; the only question is which job |
| **B6** | `MSO_SHAPE_TYPE.GROUP` is the right recursion predicate for all real templates | §Pattern 2 | **Low-medium** — measured on a python-pptx-authored group; a PowerPoint-authored group could conceivably present differently. Covered by the human-verify checkpoint if a real deck is available |
| **B7** | A floor pin is wanted (not a ceiling) | §Standard Stack | **Low** — a ceiling would also pass `_req_name`; the note recommends a floor |
| **A4** (carried) | The `NL_` reserved prefix survives contact with a real operator deck | Phase 1 | **Medium** — still untested against a real deck. Confirm at the human-verify checkpoint |
| **A8** (carried) | Normalized decks open correctly in real PowerPoint | Phase 1 | **Medium-high** — unverifiable here. `checkpoint:human-verify` |

## Open Questions

1. **Does Phase 2's writer derive slot content from the Surface, or accept it?**
   - What we know: the four weekly block kinds do not exist yet (Phase 3 adds them); the existing
     kinds (`ProseBlock`, `ClaimsBlock`, `KpiStripBlock`, …) carry no slot-name information; the
     operator's Selection-Pane names are the layout truth and only the composer knows which authored
     content belongs in which of them.
   - What's unclear: whether SC-1's "A weekly Surface renders to a `.pptx` by filling named
     placeholders" requires the derivation inside the writer.
   - **Recommendation:** the writer takes `slots: Mapping[str, Sequence[str]]` as a **required
     keyword argument** and owns the deck (binding, fail-loud, fill, watermark, marker,
     determinism); Phase 3 adds `weekly_slots(surface) -> dict[str, list[str]]` beside the composer.
     Phase 2's CI sample builds a real `Surface(REPORT)` and passes an explicit mapping, so SC-1 is
     proven end-to-end without inventing names for kinds that do not exist. Record the decision so
     Phase 3 does not re-litigate it.

2. **Should `cp:contentStatus` carry the actual gate state rather than a Draft/Published binary?**
   - What we know: the decision note fixes `"draft" if not surface.is_published else ""` and says
     Phase 2 copies it verbatim. `ReviewState` has **three** members (`draft`, `in_review`,
     `published`), so an IN_REVIEW deck is labelled `"draft"`. Measured: the `""` case writes
     `<cp:contentStatus></cp:contentStatus>` (W22), the one-shot empty-element asymmetry.
   - What's unclear: whether collapsing IN_REVIEW→"draft" is a deliberate simplification or an
     oversight; `cp:contentStatus` is documented free-form ("completion status … e.g. 'draft'"), so
     `surface.review.state.value` would be legal, more faithful, and would remove the empty-element
     case entirely.
   - **Recommendation:** implement the note **verbatim** (it is binding and its cost is small), and
     raise the amendment with the Editor-in-Chief as a one-line note change. Do **not** deviate
     silently — the assertion text is the thing Phases 2 and 4 both copy.

3. **IN-04: consolidate the fixture's `_FIXED` onto `EPOCH_ZERO`, or keep it deliberately
   different?**
   - What we know: consolidating would set the *template's* `dcterms:created` to the exact value the
     writer is supposed to write, so the marker read-back assertion would pass even if the writer
     never set it — a false green in the phase whose method is "green ≠ green".
   - What's unclear: whether the review's scheduled fix anticipated that the same fixture would
     later be the *input* to the assertion it is meant to falsify.
   - **Recommendation:** apply IN-02's zip-metadata consolidation (`DOS_EPOCH`, `create_system=0`)
     which is the substance of the finding; **keep** the fixture's core-property instant distinct
     from `EPOCH_ZERO` and add a comment naming it a *falsifiability control*, not a second
     sentinel. Record it as IN-04's resolution rather than leaving IN-04 open.

4. **Does the IN-02 delegation belong in this phase at all?**
   - What we know: it regenerates nine committed binaries; no test byte-compares or regenerates them
     (W23), so the risk is a large binary diff, not a broken gate. CONTEXT lists it as scheduled work
     that must not be dropped.
   - **Recommendation:** do it, as its **own task and own commit**, placed last in the phase so a
     revert is trivial and the diff never mixes with the writer's source changes.

5. **How many slides does the weekly template have?**
   - What we know: the contract fixes the slide count at the template's; the binding map and the
     watermark loop are already written to iterate `prs.slides`; the current fixture has one slide.
   - **Recommendation:** keep the writer multi-slide-correct (loop, never index `[0]`) and leave the
     fixture at one slide plus, if cheap, a second slide in the upgraded fixture so the
     "watermark on every slide" assertion is not vacuous.

## Sources

### Primary (HIGH confidence — executed in this session)

- **Six scratch experiments** against the repo `.venv` (python-pptx 1.0.2, CPython 3.11.15, zlib
  1.3), using the committed `tests/fixtures/weekly/template.pptx` and two synthetic decks:
  open→save round trip and core-property diff; text-fill variants (assign / clear / clone) with
  `pPr`+`rPr` inspection; watermark add / remove / duplicate; image placement, dedup, order,
  picture-placeholder insert; group nesting and `has_text_frame`; and an end-to-end miniature
  writer with full read-back. Results tabulated in §Measured Results (W1–W23) and §Code Examples.
  Scratch code lived in the session scratchpad and was never written into the repo.
- **python-pptx 1.0.2 installed source**, read directly: `pptx/text/text.py`
  (`TextFrame.fit_text`, `_Paragraph`, `_Run` public surfaces), `pptx/text/fonts.py` (`FontFiles`).
- **This repository, read directly on this branch:** `.planning/phases/02-renderer/02-CONTEXT.md`,
  `.planning/notes/2026-08-29-pptx-determinism-decision.md`,
  `.planning/phases/01-specify-de-risk/01-RESEARCH.md` + `01-REVIEW.md`, `.planning/ROADMAP.md`,
  `.planning/REQUIREMENTS.md`, `.planning/config.json`, `docs/weekly-spec.md`, `CLAUDE.md`,
  `src/newsletters/{semantic,render,publish,__init__}.py`,
  `src/newsletters/adapters/{_pptx_loader,_timestamps}.py`, `pyproject.toml`, `.importlinter`,
  `.github/workflows/ci.yml`, `tests/test_ai_optional.py` (incl. executing its `_req_name`),
  `tests/test_pptx_determinism.py`, `tests/test_pptx_golden.py`,
  `tests/fixtures/weekly/{_determinism,_author_template}.py`,
  `tests/fixtures/pptx/_author_fixtures.py`.
- `gsd-tools query package-legitimacy check --ecosystem pypi python-pptx`;
  `.venv/bin/pip index versions python-pptx` → 1.0.2 latest.

### Secondary (MEDIUM confidence)

- python-pptx API documentation for `CoreProperties` semantics (`content_status` = "completion
  status of the document, e.g. 'draft'"). [CITED:
  https://python-pptx.readthedocs.io/en/latest/api/presentation.html] — cross-checked against the
  installed library's actual round-trip behaviour, so the attribute claims are effectively verified.

### Tertiary (LOW confidence — carried from Phase 1, not re-measured)

- reproducible-builds guidance on archive metadata and the zlib/zlib-ng DEFLATE divergence.
  [CITED: https://reproducible-builds.org/docs/archives/] [CITED:
  https://lists.reproducible-builds.org/pipermail/rb-general/2024-September/003547.html] — only one
  zlib is available here; treated as a risk designed around (`part_digest`), never as a measured
  fact.

## Metadata

**Confidence breakdown:**

- **Writer mechanics** (fill primitives, formatting preservation, group nesting, watermark, images,
  round trip): **HIGH** — every claim was executed against the exact library version and the repo's
  own fixture; the two most consequential findings (formatting loss on `tf.text`, group invisibility)
  came from measurements that contradicted the obvious expectation.
- **Determinism of every new operation:** **HIGH** — each was re-measured across a real 3-second gap,
  the same discipline the Phase 1 evidence used.
- **Module placement / lazy-import plan:** **HIGH** — mirrors an existing, test-guarded boundary; the
  bare-import property follows from the promoted module being stdlib-only.
- **CI gap (W21):** **HIGH** — read from the live workflow file; four jobs, none installs `[pptx]`.
- **IN-02 blast radius (W23):** **HIGH** — read from the live golden test module.
- **API shape (`slots` explicit vs derived):** **MEDIUM** — a design recommendation with reasons, not
  a measurement. Open Question 1.
- **`cp:contentStatus` tri-state amendment / IN-04 falsifiability:** **MEDIUM** — the *facts* are
  measured (W22; the fixture's role as the assertion's input), the *recommendations* are judgement
  calls needing the Editor-in-Chief. Open Questions 2 and 3.
- **PowerPoint compatibility:** **MEDIUM-LOW** — unchanged from Phase 1; no consumer in this
  environment. `checkpoint:human-verify`.

**Research date:** 2026-08-29
**Valid until:** 2026-09-28 (30 days). Re-verify if python-pptx publishes a new release, or if the
repo's Python or zlib changes — the W-series is scoped to python-pptx 1.0.2 / CPython 3.11 / zlib 1.3.
