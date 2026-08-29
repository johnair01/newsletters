# Requirements: Newsletters — Milestone v1.3 (The Weekly, One Shot)

**Defined:** 2026-08-29 · **Count:** 6 (WKLY-01..06) · **Seed:** `.planning/seeds/v1.3-weekly-one-shot.md`
**Core Value:** Make work legible and trustworthy — every published claim traces to evidence;
nothing publishes without a human.

**Recorded decisions (the ONE discussion round, 2026-08-29 — binding for this build):**
reuse `Surface(REPORT)` for the weekly deck · asset provenance minimum = folder + date + event
label (deep link optional, but REQUIRED for a BI screenshot standing in for values) · template
contract = named placeholders, fail-loud on missing/unknown names.

## v1.3 Requirements

### Renderer

- [x] **WKLY-01**: A composed weekly `Surface(REPORT)` renders deterministically to `.pptx`
  through an operator-supplied template deck: python-pptx stays behind the `[pptx]` extra
  (writer and loader share it), core spine untouched, bare-install CI green. The determinism
  gate extends to `.pptx` — byte-stable double-render (fixed epoch per `EPOCH_ZERO`, sorted
  parts, stable rels) or a recorded content-stable definition with evidence, decided in Phase 1,
  not discovered in Validate. Every deck carries the generated-by marker in a durable field and
  renders visibly Draft-watermarked until the Surface is Published (the gate itself untouched).
  The renderer fills **named placeholders** only — it never invents layout; missing/unknown
  names fail loud. The repo ships a minimal synthetic template for the sample corpus and CI.

### Composition

- [ ] **WKLY-02**: A weekly composes from new block kinds — `NarrativeBlock` (authored
  highlights/lowlights), `RecognitionsBlock`, `TeamBlock` (name, role, short lines, photo ref),
  `AssetBlock` — alongside the existing per-lane KPI strip + claims. Authored material arrives
  as a **Weekly Spec** YAML on the Case Spec mechanism: file text is the evidence, narrative
  carried byte-verbatim as the author's voice, absences → `missing[]`, org-specific `config:`
  bound but never claimed. The composer assembles and traces; it never editorializes.

### Evidence

- [ ] **WKLY-03**: An asset (photo, screenshot) is a content-addressed file with required
  provenance — minimum: folder + date + event label; optional deep link. It enters a Surface
  only via an `AssetBlock` tracing to that record. An asset without provenance routes to
  `missing[]` — shown to the reviewer, never placed silently.

- [ ] **WKLY-04**: BI values arrive as exported `.xlsx`/`.csv` fed to the existing ADAPT-03
  excel adapter — no new adapter. Where export is unavailable, a screenshot **with a required
  deep link** enters via WKLY-03. ADAPT-05 remains the definition-side reader (extending it is
  out of scope this milestone).

### Proof

- [ ] **WKLY-05**: A synthetic sample weekly in the `content/module` lineage (fabricated
  everything; honesty-path coverage: a lane with no KPIs, a recognition with no source email,
  an asset with no provenance) composes and renders to `.pptx` under the carried gate set:
  pytest · lint-imports · `newsletters check` over all corpora · double-render stability
  (including `.pptx` per WKLY-01's recorded definition) · bare-install untouched ·
  mypy/black/isort no-new-failures.

- [ ] **WKLY-06**: `docs/weekly.md` lets an operator who is not the author point the adapters
  at a real workbook / template deck / `.eml` drop / photo folder (read-only, data stays local —
  the WORK-01 pattern), author the Weekly Spec, run compose + render, and review the result.

## Future Requirements

- **ADAPT-05 value-side extension** — live BI values from PBIP; deferred (WKLY-04 covers values
  via export this milestone).
- Everything in DEF-01..14 (see `.planning/ROADMAP.md` §Deferred).

## Out of Scope

| Feature | Reason |
|---------|--------|
| New Surface kind for weeklies | Recorded decision: the weekly reuses `REPORT`; a renderer is an output format, not a semantic kind |
| Extending ADAPT-05 to read data values | Definition-side reader stays as-is; values come via export (WKLY-04) |
| Per-asset deep link required for ordinary photos | Recorded decision: would push honest assets into `missing[]` for no trust gain; required only for BI screenshots standing in for values |
| Positional template mapping | Recorded decision: silently fragile to operator edits; named placeholders fail loud |
| AI anywhere in the render/compose path | AI-optional core is a hard rule; the renderer is deterministic code behind `[pptx]` |
| Auto-publish of the deck | Hard rule; the sample weekly ships Draft, watermarked |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| WKLY-01 | Phase 2 — Renderer | Complete (02-01 foundation · 02-02 the writer · 02-03 the proof + CI). All five phase SCs implemented and proved by tests that read the WRITTEN file back: SC-1 seven fail-loud/binding tests · SC-2 double render across a real 3s gap with its negative control and `part_digest` · SC-3 marker + watermark, asserted in both directions · SC-4 gate untouched, `semantic.py` byte-unchanged · SC-5 lazy `[pptx]` import + a `pptx` CI job whose exact command runs 117 passed / **0 skipped**. **Two confirmations remain for the PR review, recorded not hidden:** the new job's first observed CI green (no `gh` in the build environment) and the real-PowerPoint open (A8 — no `.pptx` consumer here) |
| WKLY-02 | Phase 3 — Weekly compose | **In progress** (03-01 · 03-02). 03-01: the four block kinds exist, round-trip by discriminator and each render to HTML from pre-existing design-system classes; `_block_html` can no longer swallow one. 03-02: the Weekly Spec YAML **load** path is met — `newsletters.weeklyspec.load_weekly_spec` lifts an authored file into a content-addressed `Source` with narrative carried byte-verbatim as gate-entailed claims at real spans of that file (a value duplicated across sections traces to its own line, proved by a mutation-tested line-number regression), `config:` bound-never-claimed, and every absence disclosed in `missing[]` in schema order including "no lowlights". **Not yet met:** the COMPOSE half — `build_weekly_report`, the fixed block order, and the KPI-strip/claims assembly that puts those blocks on a Draft `Surface(REPORT)`. That is plan 03-03's |
| WKLY-03 | Phase 3 — Weekly compose | **In progress** (03-01). The TYPE-LEVEL half is landed: `AssetRecord` carries the provenance minimums, and `AssetBlock.asset` (required, no default) + `evidence` (`min_length=1`) make a provenance-less placement unrepresentable rather than policed. **Not yet met:** the loader-side routing — the four `missing[]` conditions, the placement-time content-address check, and the root-containment refusal |
| WKLY-04 | Phase 3 — Weekly compose | Pending |
| WKLY-05 | Phase 4 — Sample corpus + recipe | Pending |
| WKLY-06 | Phase 4 — Sample corpus + recipe | Pending |

**Coverage:** v1.3 requirements: 6 total · Mapped to phases: 6 · Unmapped: 0 ✓

**Phase 1 (Specify + de-risk) carries no requirement of its own.** It de-risks WKLY-01 (the
`.pptx` determinism definition, the generated-by-marker mechanism, the named-placeholder contract)
and WKLY-02 (the Weekly Spec schema + the four new block kinds). Its outputs are spec text and a
recorded, evidence-backed determinism decision — the requirements themselves are satisfied in
Phases 2–4. See `.planning/ROADMAP.md`.

---
*Requirements defined: 2026-08-29 from the committed seed after verifying its current-state claims against the live repo.*
*Traceability mapped: 2026-08-29 when `.planning/ROADMAP.md` (4 phases) was created.*
