# Roadmap: Newsletters — Milestone v1.3 (The Weekly, One Shot)

> **Fresh file for v1.3.** v1.2 (The Published Record) went live 2026-07-03 and closed 2026-08-29;
> it is archived at `.planning/milestones/v1.2-ROADMAP.md` / `v1.2-REQUIREMENTS.md`.
> **Phase numbering resets to 1–4 for this milestone** (repo precedent: prior phase dirs are
> archived under `.planning/milestones/v1.1-phases/` and `v1.2-phases/`; `.planning/phases/` is
> empty — no collision).

**Milestone:** v1.3 The Weekly, One Shot — the recurring module weekly becomes a product output
**Defined:** 2026-08-29
**Granularity:** fine (`.planning/config.json`)
**Phases:** 4 (locked by the approved seed's phase table)
**Coverage:** 6/6 v1.3 requirements mapped ✓ (WKLY-01..06 — see `.planning/REQUIREMENTS.md`)
**Seed:** `.planning/seeds/v1.3-weekly-one-shot.md` (current-state claims verified against the live repo)

## Overview

The spine already does the hard part: adapters mint `Source → Claim(+Trace)`, `swimlane.py` +
`compose.py` build a per-module `Surface(REPORT, Draft)` with an honest `missing[]`, the Case Spec
path carries an author's voice byte-verbatim, and one publish channel republishes exactly what a
human merged. What it cannot do is **ship the artifact a module actually sends every week**: a
deck. Surfaces render to HTML only; python-pptx exists on the *loader* side; images have no traced
route into a Surface; authored narrative, recognitions, and team blocks have no kinds.

This milestone adds **one output format and a few block kinds** — not a new spine. A weekly
composer assembles adapter evidence plus an authored **Weekly Spec** into one
`Surface(REPORT, Draft)`; a deterministic, template-driven PPTX renderer emits the deck through
the **untouched** review gate, visibly Draft-watermarked. The author writes the story; the engine
makes it traced, repeatable, and publishable-by-a-human.

**Recorded decisions (the ONE discussion round, 2026-08-29 — binding, no further questions):**

- **Reuse `Surface(REPORT)`.** The PPTX renderer is an output *format*, not a new semantic kind.
- **Asset provenance minimum = folder + date + event label.** Deep link optional — **except** a BI
  screenshot standing in for values (WKLY-04), where it is **required**. No provenance → `missing[]`.

- **Template contract = named placeholders, fail-loud** on missing/unknown names. The renderer
  never invents layout.

**Hard rules this milestone must not bend:** no auto-publish (the sample deck ships `Draft`,
watermarked; `semantic.py`'s gate untouched) · every claim traces or is disclosed in `missing[]` ·
AI-optional core (python-pptx stays behind the `[pptx]` extra, lazy-imported; **zero AI anywhere in
the compose/render path**) · faithful-not-suggestive (the composer assembles and traces; it never
editorializes) · branch + PR only, atomic commits, compass + RETRO per phase · proprietary
stripped / personal preserved (synthetic sample only; operator data never committed).

## Enforced gate set (definition of "green" for every phase — carried from v1.2/v1.1)

Re-run **independently** — *"the agent says green" ≠ green*. Run each gate once per check
(rapid re-runs throw transient errors); check every planning/executing subagent's claims against
the live repo before building on them.

1. **pytest** — full suite must not regress (639 green at v1.2 close, plus the Case Spec path
   added since) incl. each phase's new guard tests

2. **lint-imports** — contracts KEPT (AI-optional core; no-external-write). New `[pptx]` writer
   imports must not create a core→extra edge

3. **`newsletters check`** — over **ALL** corpora (`rev1`, `work`, `module`)
4. **byte-stable double-render** — committed == fresh for every corpus, **extended to `.pptx`**
   under Phase 1's recorded determinism definition (byte-stable, or content-stable = unzipped
   parts byte-identical under normalized zip metadata)

5. **bare-install CI** — untouched; stays the AI-free, extra-free source of truth
6. **mypy / black / isort** — no-NEW-failures vs the 2026-07-02 baseline (carried)

Plus the standing invariants: `content/*/ids.json` ledgers are **append-only** (any diff on
regenerate is a stop-the-line bug) and the abstraction guard stays green (no fixture/org-specific
name may leak into `src/`).

## Phases

- [x] **Phase 1: Specify + de-risk** — Weekly Spec schema + block kinds specified against `docs/architecture.md`; the `.pptx` determinism spike, decided on evidence up front (completed 2026-08-29)
- [x] **Phase 2: Renderer** (WKLY-01) — template-driven deterministic PPTX writer + generated-by marker + Draft watermark + gate wiring (completed 2026-08-29)
- [ ] **Phase 3: Weekly compose** (WKLY-02, WKLY-03, WKLY-04) — new block kinds, the Weekly Spec path, asset evidence, BI values via export
- [ ] **Phase 4: Sample corpus + recipe** (WKLY-05, WKLY-06) — CI-rendered synthetic weekly + `docs/weekly.md` operator recipe

## Phase Details

### Phase 1: Specify + de-risk

**Goal**: The two things that would be expensive to discover late are settled *before* any code
depends on them — the Weekly Spec schema and the new block kinds exist in the docs, and `.pptx`
determinism has a recorded definition backed by evidence from a real write. Nothing is discovered
in Validate.
**Depends on**: Nothing (first phase).
**Requirements**: **None of its own.** This phase carries no WKLY requirement — it **de-risks
WKLY-01** (determinism definition, marker mechanism, template contract) and **WKLY-02** (Weekly
Spec schema + block kinds). Its outputs are *spec text* and *a recorded decision with evidence*,
not shipped features. WKLY-01 is satisfied in Phase 2; WKLY-02 in Phase 3.
**Success Criteria** (what must be TRUE):

  1. The docs describe the weekly before it exists in `src/`: `docs/architecture.md` (§1 typed
     semantic model) plus a Weekly Spec section (extending the `docs/case-spec.md` mechanism)
     define the four new block kinds — `NarrativeBlock`, `RecognitionsBlock`, `TeamBlock`,
     `AssetBlock` — field by field, with their place in the discriminated `Block` union, and the
     Weekly Spec YAML schema (file text is the evidence; narrative byte-verbatim; absences →
     `missing[]`; `config:` bound but never claimed). A reader can hand-author a valid Weekly
     Spec from the doc alone.

  2. A determinism spike runs a **real** python-pptx write of a minimal template twice and records
     ONE outcome as a decision with committed evidence (the two runs' hashes, and — if they
     differ — exactly which parts/fields varied): **byte-stable** double-render (fixed epoch per
     the existing `EPOCH_ZERO` pattern, sorted parts, stable rel ids), **or** a **content-stable**
     definition (unzipped parts byte-identical under normalized zip metadata). No renderer work
     starts before this is recorded.

  3. The recorded milestone decisions are written down where the implementer will read them, with
     a testable consequence for each: reuse `Surface(REPORT)` (no new Surface kind, no
     `semantic.py` kind change); **named placeholders, fail-loud** on missing/unknown names; and
     the generated-by-marker mechanism (core properties vs. notes) chosen with a stated reason
     *and* a stated way to assert it by reading a written file back.

  4. The asset-evidence record shape is specified with the field names the composer and renderer
     will use: provenance minimum = folder + date + event label; deep link **required** for a BI
     screenshot standing in for values (WKLY-04); content-addressed file identity; and the exact
     `missing[]` routing when provenance is absent.

  5. The spike leaves no production surface behind: python-pptx stays behind the `[pptx]` extra
     (no new dependency, no core import edge), `lint-imports` contracts stay KEPT, bare-install CI
     is untouched, and any spike scratch code is deleted or lands as a test fixture — never as an
     unguarded import in `src/newsletters/`.
**Plans**: 3 plans (waves 1 -> 2 -> 3, strictly ordered: evidence, then decision, then spec)

- [x] `01-01-PLAN.md` — Determinism spike: real python-pptx double write across a time boundary, the spike as a durable test (part-digest / byte-equality / negative control), committed evidence, no production surface
- [x] `01-02-PLAN.md` — The recorded decision: byte-stable via a declared zip normalization (scoped), the core-properties marker with its read-back assertion, the fill-existing-slides template contract; supersedes the contradicting fixture docstring
- [x] `01-03-PLAN.md` — `docs/weekly-spec.md` (schema + the four block kinds field-by-field + the asset-evidence record and its `missing[]` routing); `docs/architecture.md` block-list drift fixed and pointers wired

### Phase 2: Renderer

**Goal**: A composed weekly `Surface(REPORT)` becomes a `.pptx` deck through an operator-supplied
template — deterministically, marked as generated, visibly `Draft` until a human publishes it, and
with the review gate itself untouched.
**Depends on**: Phase 1 (the recorded determinism definition, the marker mechanism, and the named-
placeholder contract are inputs, not discoveries).
**Requirements**: WKLY-01
**Success Criteria** (what must be TRUE):

  1. A weekly Surface renders to a `.pptx` by filling **named placeholders** in an operator-supplied
     template deck, and the renderer never invents layout: a placeholder name with no matching
     Surface content, and Surface content with no matching placeholder name, each **fail loud**
     with a teaching error naming the offending placeholder — proven by tests in both directions.

  2. Rendering the same Surface twice produces decks equal under Phase 1's recorded definition
     (byte-identical, or unzipped parts byte-identical under normalized zip metadata), asserted by
     a test that would fail if a wall-clock timestamp, part ordering, or unstable rel id leaked in.

  3. Every rendered deck carries the generated-by marker in the durable field chosen in Phase 1 and
     renders **visibly Draft-watermarked** while the Surface is not `Published` — both asserted by
     reading the written file back, never by trusting the writer's return value.

  4. No auto-publish path is created: the renderer never advances or inspects-then-mutates the
     review state, `semantic.py` is byte-unchanged, and a test proves rendering a `Draft` Surface
     leaves it `Draft`.

  5. python-pptx is lazy-imported **inside the writer only**, sharing the existing `[pptx]` extra
     with the loader; `lint-imports` stays KEPT and the bare-install CI job (no extras, no AI)
     stays green when run independently. A minimal **synthetic** template `.pptx` (fabricated, no
     operator data) ships in the repo and a sample Surface renders through it in CI.

**Plans**: 3 plans (waves 1 -> 2 -> 3, strictly ordered: foundation, then the writer, then the proof in CI)

- [x] `02-01-PLAN.md` — Foundation: promote the OPC normalizer into `src/newsletters/pptx_writer.py` (verbatim, stdlib-only, bare-importable) and retire the fixture copy (closes IN-03); the two AI-optional boundary guards + the `python-pptx>=1.0.2` floor pin; the in-test deck builders that make the fail-loud contract testable without regenerating the committed template
- [x] `02-02-PLAN.md` — The writer: group-recursive binding with five teaching refusals (SC-1), the reuse-and-clone fill primitive that inherits the operator's formatting, the Draft watermark + core-properties marker + the two public entry points, each landed with the tests that read the written file back (SC-3, SC-4)
- [x] `02-03-PLAN.md` — The proof in CI: double-render byte equality across a real 3-second gap with its negative control and `part_digest` (SC-2), a sample `Surface(REPORT)` rendered end to end through the committed synthetic template, and the first CI job that installs `[pptx]` so the pptx tests run instead of skipping (SC-5, W21)

### Phase 3: Weekly compose

**Goal**: A weekly `Surface(REPORT, Draft)` composes from authored voice plus adapter evidence —
new block kinds, the Weekly Spec path, content-addressed assets, and BI values via export — where
the composer assembles and traces and never editorializes.
**Depends on**: Phase 1 (schema + block-kind spec) and Phase 2 (the renderer is the consumer that
proves composed blocks actually reach a deck).
**Requirements**: WKLY-02, WKLY-03, WKLY-04
**Success Criteria** (what must be TRUE):

  1. Four new block kinds join the typed `Block` union per Phase 1's schema — `NarrativeBlock`,
     `RecognitionsBlock`, `TeamBlock`, `AssetBlock` — and **none of them can be silently dropped**:
     the HTML block dispatch in `render.py` renders each one using existing design-system tokens
     (`docs/design-system.md`, `--radius: 0`) or fails loud, so today's `return ""` fall-through can
     no longer swallow an unrecognized block (proven by test).

  2. A hand-authored **Weekly Spec** YAML composes through the Case Spec mechanism: the author's
     narrative appears in the Surface **byte-verbatim** with real-span `Trace`s to the spec file,
     `config:` values are bound but never minted as claims, and every declared-but-absent item
     lands in `Surface.missing[]` — no paraphrase, no invented emphasis, no summarization
     (proven by tests including a planted-editorialization guard).

  3. An asset enters a Surface **only** as a content-addressed file whose provenance meets the
     recorded minimum (folder + date + event label), carried by an `AssetBlock` whose `Trace`
     resolves to that record. An asset without provenance — and a BI screenshot standing in for
     values without its **required deep link** — routes to `missing[]`, is shown to the reviewer,
     and is never placed in the Surface (proven both ways by test).

  4. BI values reach the weekly through the **existing** ADAPT-03 excel adapter fed an exported
     `.xlsx`/`.csv`: no new adapter module exists, and the ADAPT-05 Power BI definition-side reader
     is unchanged (proven by test plus a clean diff on `adapters/powerbi*`).

  5. Composing the same inputs twice yields a byte-identical `Surface(REPORT, Draft)`
     (`created=EPOCH_ZERO`, sorted inputs, stable ids) that has never advanced the review gate, and
     it renders through Phase 2's writer to a deck that satisfies the recorded determinism
     definition.

**Plans**: 4 plans (waves 1 -> 2 -> 3 -> 4, strictly ordered: the types and the gate that guards
them, then the load, then the assets and the Surface, then the deck, the values and the CI job that
makes it all mean something)

- [ ] `03-01-PLAN.md` — Types + dispatch + the gate that guards them: the four block kinds join the
      union as a PURE INSERTION (zero deleted lines), each gets an HTML branch built from existing
      `_CSS` classes only, `_block_html`'s `return ""` fall-through becomes a teaching raise, and
      the review gate's working-tree-only protection is replaced by source-hash pins on the eight
      gate functions plus a zero-deleted-lines diff against `git merge-base HEAD origin/main`
      (SC-1, plus SC-3's type-level half)
- [ ] `03-02-PLAN.md` — The Weekly Spec lift: the span minter promoted to `specspan.py` so exactly
      one honest-span implementation exists, then `weeklyspec.py`'s strict eight-key schema and
      `load_weekly_spec` — file-order minting, `config:` bound never claimed, every absence
      disclosed, two committed fixtures + a tiny PNG (SC-2's mechanism)
- [ ] `03-03-PLAN.md` — Asset evidence + the composer: all seven routing rows with their exact
      disclosure strings (a path escape raises, an absence discloses, the two never collapse), and
      `build_weekly_report` — fixed block order, Draft at `EPOCH_ZERO`, byte-identical
      double-compose, and the planted-editorialization guard (SC-3, SC-5's composition half)
- [ ] `03-04-PLAN.md` — The deck, the values, and the job that makes the greens mean something:
      `weekly_slots` + an end-to-end render through Phase 2's writer (text-only; empty sections
      disclose on the slide), BI values through the **existing** ADAPT-03 adapter with ADAPT-05
      clean-diffed, and the `weekly` CI job installing `[excel]` with `0 skipped` asserted
      (SC-4, SC-5)

**UI hint**: yes — the new block kinds must render into the existing HTML surface under
`docs/design-system.md` / `docs/surfaces.md` tokens. No new web app work; the `web/` preview is
out of scope this milestone.

### Phase 4: Sample corpus + recipe

**Goal**: The weekly is proven and repeatable **by someone who is not the author** — a synthetic
sample weekly composes and renders in CI under the full gate set, and `docs/weekly.md` walks an
operator through the loop on their own data, read-only and local.
**Depends on**: Phase 3 (a composed weekly to render) and Phase 2 (the renderer).
**Requirements**: WKLY-05, WKLY-06
**Success Criteria** (what must be TRUE):

  1. A **synthetic** weekly in the `content/module` lineage (fabricated org, people, metrics — the
     abstraction guard stays green, no fixture-specific name in `src/`) composes and renders to
     `.pptx`, exercising the honesty path end to end: a lane with no KPIs, a recognition with no
     source email, and an asset with no provenance each appear in `missing[]` / the honesty panel
     and none is silently dropped.

  2. The full enforced gate set is green over **all** corpora when re-run independently: pytest ·
     lint-imports (contracts KEPT) · `newsletters check` (rev1, work, module) · committed == fresh
     double-render for every corpus **including the `.pptx`** per Phase 1's definition ·
     bare-install CI untouched · mypy/black/isort no-NEW-failures vs baseline. Every
     `content/*/ids.json` ledger is unchanged (append-only).

  3. The sample deck ships **`Draft` and watermarked**: no sample, script, or CI step publishes,
     advances the review gate, pushes to `main`, or makes an external call — proven by test and by
     reading the workflow diffs.

  4. `docs/weekly.md` takes an operator who is **not** the author from a real workbook / template
     deck / `.eml` drop / photo folder (read-only, data stays local — the WORK-01 pattern) through
     authoring the Weekly Spec, composing, rendering, and reviewing, with copy-pasteable commands
     that match the shipped CLI — verified by executing them against the synthetic corpus.

  5. Spec and compass stay honest: `docs/architecture.md` and `docs/surfaces.md` reflect the
     shipped block kinds and renderer, `WHERE-WE-ARE.md` is updated, and the milestone's friction
     is logged in `RETRO.md` with any durable fix encoded as a rule or guard test.

**Plans**: TBD

## Progress

**Execution Order:** 1 → 2 → 3 → 4 (strictly ordered; Phase 1 gates everything that follows).

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Specify + de-risk | 3/3 | Complete    | 2026-08-29 |
| 2. Renderer | 3/3 | Complete    | 2026-08-29 |
| 3. Weekly compose | 1/4 | Executing (plan 03-01 complete; 3 plans remain) | - |
| 4. Sample corpus + recipe | 0/0 | Not started | - |

Plans are created per phase by `/gsd-plan-phase`; `0/0` means "not yet planned", not "no work".

## Deferred — un-scheduled (carried at v1.2 close, unchanged)

- **DEF-01..DEF-12** — see `.planning/milestones/v1.1-ROADMAP.md` §Deferred (area roll-up,
  project/interview kinds, owner-audit, quarter-editorial, persona/leadership/learning re-cuts,
  MOR/IQ↔Problem, Kpi baseline, DistillPort AI backend, Problem Board).

- **DEF-13** — wire `web/` (the Signals Next.js app) to the real corpus data; until then it
  deploys only as the labeled `/web/` design preview.

- **DEF-14** — adopt the `actions/deploy-pages` environment channel iff the maintainer aligns
  the repo settings (Pages source + environment allowlist); until then gh-pages push is the one
  channel.

- **B1–B20 fix-batch** — maintainer-gated one-test guards
  (`.planning/reviews/2026-07-02-deep-review/07-tests-as-promises.md`).

Newly recorded as out of scope this milestone (see `.planning/REQUIREMENTS.md` §Out of Scope):
**ADAPT-05 value-side extension** — live BI values from PBIP; WKLY-04 covers values via export.

---
*Roadmap created: 2026-08-29 for milestone v1.3 from `.planning/seeds/v1.3-weekly-one-shot.md`.
v1.2 archived at `.planning/milestones/`. Current build state: `.planning/STATE.md`.*
