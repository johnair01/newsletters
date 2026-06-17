# Phase 6 — Context & Decisions (PowerPoint Adapter)

**Goal:** Extract slide/shape text from `.pptx` via python-pptx into `Claim(+Trace)` with slide/shape
locators, explicitly reporting shapes the high-level API cannot read (SmartArt, grouped shapes, charts,
images, media) in `unextracted[]` — so the reviewer sees the slide had content the extractor skipped.

**Requirements:** ADAPT-04 (+ ADAPT-06 golden tests). **Depends on:** Phase 4 (shared `normalize()`,
adapter/DistillPort pattern, Coverage/`unextracted[]`), Phase 5 (the hardened coverage carrier
`Source.extraction` + codec + round-trip parity matrix; the lazy-extra packaging precedent).

## Decisions

0. **FRONT FIX (carried from Phase-5 verifier) — deterministic adapter timestamp fallback, ALL
   adapters.** Today email/excel source `Source.timestamp` from the doc's intrinsic date (email `Date`,
   xlsx `properties.created`) but fall back to `now()` when absent → non-deterministic output that
   breaks the determinism/round-trip-parity property for real-world files. Fix the PATTERN before PPTX
   copies it: when no intrinsic timestamp exists, use a **deterministic** fallback (NOT `now()`) —
   research/planner pick the cleanest (recommended: a fixed sentinel/epoch, or derive deterministically
   from content; must be stable across repeated parses). Retrofit email + excel, apply to pptx, add a
   determinism test ("a doc with no intrinsic timestamp parses to byte-identical Sources twice").

1. **python-pptx behind a lazy `[pptx]` extra (Package-Legitimacy: PRE-APPROVED by spec).** ADAPT-04
   names python-pptx; it's MIT-licensed, mature, the standard. NOTE its transitive deps (lxml, Pillow,
   XlsxWriter, typing_extensions) include C-extensions (lxml, Pillow) — acceptable because they are
   widely-used, no-telemetry, and **sandboxed in the optional `[pptx]` extra**, never core. Add
   `pptx = ["python-pptx"]`; import LAZILY inside the adapter only (mirror `[excel]`); a clear
   ImportError→`pip install .[pptx]` if used without it. Bare install + AI-isolation + `lint-imports`
   must stay green WITHOUT `[pptx]` (no top-level pptx import reachable from `import newsletters`).
   python-pptx is NOT AI — forbid-ai contract unaffected — but verify.

2. **Reuse the shared `normalize()` + the Phase-5 coverage carrier.** The PPTX adapter produces a
   canonical text transcript + ordered verbatim units + its own `unextracted[]`; `normalize()`
   content-addresses the units; drops persist on `Source.extraction` (so round-trip parity holds — the
   adapter JOINS the existing parity matrix with one param). Adapter never calls `Trace.from_source`/`hashlib`.

3. **Extraction granularity (research the exact API).** Walk `prs.slides` in order; per slide walk
   `slide.shapes` in document order. Extract text from: title + body/placeholder text frames
   (`shape.has_text_frame` → `text_frame.paragraphs` → runs/`.text`), text boxes, table cells
   (`shape.has_table` → rows/cols/`cell.text`), and speaker notes (`slide.has_notes_slide` →
   `notes_slide.notes_text_frame`). Decide claim granularity (per-paragraph vs per-shape) — recommend
   per-paragraph for auditable atoms; research stable ordering.

4. **Transcript layout + locator.** Canonical text serialized deterministically (slide order, shape
   order); each emitted text unit a verbatim slice. Locator = `FreeLocator(text="Slide N / <shape>")`
   (no Trace/normalize schema change, mirroring Excel's `Sheet!A1`). Research a STABLE shape
   identifier (shape name? id? index?) that survives re-parse and reads well to a reviewer.

5. **`unextracted[]` enumeration (research).** Shapes the high-level text API cannot read → reported,
   never silently skipped: SmartArt/diagrams (`graphicFrame`), charts, pictures/images, media
   (audio/video), grouped shapes (`GROUP` — decide: recurse into members vs report the group; research
   what python-pptx exposes), OLE/embedded objects, WordArt, and any shape with no readable text frame.
   Decide how a partially-readable group is handled faithfully. "Zero silent drops": every shape is a
   claim-source OR an `unextracted[]` entry.

6. **Golden fixtures (ADAPT-06).** `.pptx` fixtures authored programmatically (byte-reproducible
   generator, mirror Phase-4/5). MUST include SmartArt and grouped shapes (ROADMAP criterion 3), plus:
   title+body, text box, table, speaker notes, chart, image, an empty slide. Assert zero-silent-drops
   identity, verbatim + content-addressed claims, conformance, determinism, AND round-trip coverage parity.

## Research-locked choices (06-RESEARCH.md accepted 2026-06-17, HIGH confidence, verified vs pptx 1.0.2 source)

- **L1 — Timestamp fix:** shared `adapters/_timestamps.py` with `EPOCH_ZERO =
  datetime(1970,1,1,tzinfo=utc)` + `deterministic_timestamp(intrinsic) -> intrinsic or EPOCH_ZERO`
  (NEVER `now()`). Retrofit email (`Date`-or-None) + excel (`properties.created`-or-None), apply to
  pptx (`core_properties.created`-or-None); all three pass `timestamp=` explicitly. Claims unaffected
  (content_hash hashes transcript only). Determinism test parametrized across all 3 adapters.
- **L2 — SmartArt detection:** `shape_type` is `None` for SmartArt; detect via graphic-frame
  `graphicData @uri == ".../drawingml/2006/diagram"` with an lxml `@uri` fallback so any unknown
  graphicFrame is reported, never dropped. (Risk A1: the accessor is internal — use the lxml fallback.)
- **L3 — Groups:** recurse into `GroupShape.shapes`; extract members' text; report only unreadable
  MEMBERS, not the whole group. Nested accounting: `leaf_shapes == producers + skipped_empty +
  unextracted_from_shapes`; a GROUP node itself contributes nothing to the count.
- **L4 — Fixtures:** Pillow is a hard (auto-installed) dep of python-pptx — embed a constant 1×1 PNG
  byte literal (don't call Pillow). `add_group_shape` MOVES shapes (author members first, then group;
  nested = group an inner group). SmartArt has no authoring API → XML-inject a diagram graphicFrame
  (dedicated task). Set `core_properties.created` for determinism.
- **L5 — Determinism assertion (risk A3):** python-pptx re-save may not be byte-reproducible; assert
  determinism on the parsed **Source** (identical bytes → byte-identical `model_dump_json`), NOT on
  re-saved `.pptx` bytes — that is the property ADAPT-06 actually needs.
- **Deps:** python-pptx 1.0.2 (MIT) + transitive lxml/Pillow (C-ext, OK behind `[pptx]`),
  XlsxWriter/typing_extensions (pure-Py). No other new direct dep. Pkg-legitimacy SUS = `unknown-downloads`
  artifact only; pre-approved, no checkpoint.

## Hard rules in play
- **Faithful, not suggestive** — only verbatim shape text becomes claims; unreadable shapes →
  `unextracted[]`, never paraphrased or fabricated.
- **No silent drops** (incl. across persistence, via the Phase-5 carrier).
- **AI-optional / minimal core** — python-pptx (+ its C-ext transitive deps) behind `[pptx]`, lazy;
  bare-install + `lint-imports` stay green.
- **Every claim traces to evidence** — shape claims content-addressed via the shared normalize().
- **Determinism** — same `.pptx` → identical claims/coverage (the front-fix makes this hold even
  without an intrinsic timestamp).

## Research note (dispatch BEFORE planning)
Best-known python-pptx methods: `Presentation(path_or_filelike)`, slide/shape iteration, `shape.shape_type`
(MSO_SHAPE_TYPE: GROUP, PICTURE, CHART, MEDIA, EMBEDDED_OLE_OBJECT, etc.), `has_text_frame`/`has_table`/
`has_chart`, group-shape member access, SmartArt/diagram detection (graphicFrame XML), notes slides,
stable shape identity, and how to author SmartArt + grouped + chart + image fixtures programmatically.
Also: the deterministic-timestamp fallback design (front-fix), and confirm python-pptx is the right lib
+ enumerate its transitive deps + licenses. Cite python-pptx docs + python docs. Record in 06-RESEARCH.md.
