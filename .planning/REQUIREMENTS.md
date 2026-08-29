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

- [x] **WKLY-02**: A weekly composes from new block kinds — `NarrativeBlock` (authored
  highlights/lowlights), `RecognitionsBlock`, `TeamBlock` (name, role, short lines, photo ref),
  `AssetBlock` — alongside the existing per-lane KPI strip + claims. Authored material arrives
  as a **Weekly Spec** YAML on the Case Spec mechanism: file text is the evidence, narrative
  carried byte-verbatim as the author's voice, absences → `missing[]`, org-specific `config:`
  bound but never claimed. The composer assembles and traces; it never editorializes.

### Evidence

- [x] **WKLY-03**: An asset (photo, screenshot) is a content-addressed file with required
  provenance — minimum: folder + date + event label; optional deep link. It enters a Surface
  only via an `AssetBlock` tracing to that record. An asset without provenance routes to
  `missing[]` — shown to the reviewer, never placed silently.

- [x] **WKLY-04**: BI values arrive as exported `.xlsx`/`.csv` fed to the existing ADAPT-03
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
| WKLY-02 | Phase 3 — Weekly compose | **Complete** (03-01 the block kinds · 03-02 the load half · 03-03 the composer). `build_weekly_report` assembles the four new kinds alongside the per-binding KPI strip + claims into a Draft `Surface(REPORT)` at `EPOCH_ZERO`, in a fixed asserted block order, byte-identical across two composes, with no gate-advancing call in the module. Authored narrative is carried byte-verbatim beside its own minted claim; `config:` is bound and never claimed; absences are disclosed rather than rendered as empty blocks. "It never editorializes" is ENFORCED: every block string is authored (compared through the faithfulness gate's own normal form) or one of eight declared connective constants, with the guard's firing observed on a planted paraphrase AND on a genuinely merging composer . **Closed end to end by 03-04:** `weekly_slots` derives the four `NL_` deck slots from the composed Surface and a full AND a sparse weekly render through Phase 2's writer to a deterministic, marked, Draft-watermarked deck — every property asserted by reopening the WRITTEN bytes, the Surface `model_dump()`-identical afterwards |
| WKLY-03 | Phase 3 — Weekly compose | **Complete** (03-01 the type-level half · 03-03 the routing). `AssetRecord`/`AssetBlock` make a provenance-less placement unrepresentable, and `load_weekly_spec` now routes every row of `docs/weekly-spec.md` §"The routing": the three provenance minimums in field order, the deep link required iff `stands_in_for: values`, the placement-time sha256 re-check (including the substitution case), the two `team[].photo` reference rows — each with the spec's exact disclosure string — and a root escape (direct or via symlink) that RAISES and contributes nothing to `missing[]`. The image is hashed, never decoded. 13 parametrized routing cases, every refusal paired with a well-formed asset that still places; the containment mutation was observed RED (and observed silently placing an out-of-root file) . **Scope recorded by 03-04:** a placed `AssetBlock` reaches the HTML surface (text-only: `figure.diagram` + caption, no `<img>`) and its caption can feed a text slot; the IMAGE does not reach the deck, because the writer has no `add_picture` path and no phase criterion budgets one. Written up in `docs/weekly-spec.md` as a round-two item |
| WKLY-04 | Phase 3 — Weekly compose | **Complete** (03-04). A synthetic `.xlsx` authored in-test goes through `resolve("excel")` — the REGISTERED ADAPT-03 backend — into `parse`/`distill`, and its claims reach a composed weekly's `KpiStripBlock` (delta derived by `compose.compute_delta` from two INDEPENDENTLY content-addressed endpoint cells, never a text match) and `ClaimsBlock`, each kept claim re-sliceable from the live transcript at its own offsets. The three absences WKLY-04 is really about are ASSERTED, not promised: the adapters directory gained no file, `powerbi_adapter.py`/`_tmdl.py`/`_pbir.py` are byte-unchanged against the milestone base, and `weeklyspec.py` contains no `openpyxl`/`xlsx`/`load_workbook` token — each resolving the base through the shared `milestone_base_ref` fixture, which FAILS rather than skips. Non-vacuity: an untraced and an un-addressed claim planted on the same binding are refused and disclosed by text. **Wording clarified, not scope-cut:** the live adapter is `.xlsx`-ONLY; a `.csv` path would need the new adapter module this requirement forbids, so values enter as `.xlsx` exports. **The `[excel]` extra now runs in CI** (the `weekly` job) — before this plan every excel test skipped itself |
| WKLY-05 | Phase 4 — Sample corpus + recipe | **In progress** (04-01 landed the first half). The committed `content/weekly/` corpus composes to a Draft `Surface(REPORT)` at `EPOCH_ZERO`/`R-001` and renders to HTML **and** to a `.pptx` deck, with all three honesty-path absences asserted in `surface.missing` AND `html.escape`d into the rendered panel — each located by the composer's own format string, never a retyped sentence. The deck lives OUTSIDE `site/` with a stdlib-checkable `part_digest` sidecar (tier 1, with a non-vacuity arm), and `newsletters weekly` is the one command that regenerates it. **Still open for 04-02:** `newsletters check --corpus weekly`, the publish layout + Records strips, and the `[pptx]`-gated tier-2 fresh==committed deck gate — i.e. "the carried gate set over ALL corpora" is not yet true, so this stays unchecked |
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
