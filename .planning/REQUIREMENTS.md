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

- [ ] **WKLY-01**: A composed weekly `Surface(REPORT)` renders deterministically to `.pptx`
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
| WKLY-01 | (roadmap pending) | Pending |
| WKLY-02 | (roadmap pending) | Pending |
| WKLY-03 | (roadmap pending) | Pending |
| WKLY-04 | (roadmap pending) | Pending |
| WKLY-05 | (roadmap pending) | Pending |
| WKLY-06 | (roadmap pending) | Pending |

**Coverage:** v1.3 requirements: 6 total · Mapped to phases: pending roadmap · Unmapped: 6 ⚠️

---
*Requirements defined: 2026-08-29 from the committed seed after verifying its current-state claims against the live repo.*
